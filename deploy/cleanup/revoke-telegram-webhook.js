#!/usr/bin/env node
'use strict';

/**
 * Project-scoped demo cleanup: remove the Telegram webhook without exposing
 * the bot token. The token is decrypted only in memory with n8n's own cipher,
 * sent through the fixed internal egress route, and never printed.
 *
 * Run inside rag-n8n-local while the project credential still exists.
 */

const { Client } = require('pg');
const { Cipher } = require('n8n-core/dist/encryption/cipher');

const credentialName = process.env.TELEGRAM_CREDENTIAL_NAME || 'telegram-demo-bot';
const credentialType = 'telegramApi';

async function main() {
  const required = [
    'N8N_ENCRYPTION_KEY',
    'DB_POSTGRESDB_HOST',
    'DB_POSTGRESDB_DATABASE',
    'DB_POSTGRESDB_USER',
    'DB_POSTGRESDB_PASSWORD',
  ];
  for (const name of required) {
    if (!process.env[name]) throw new Error(`${name} is unavailable`);
  }

  const client = new Client({
    host: process.env.DB_POSTGRESDB_HOST,
    port: Number(process.env.DB_POSTGRESDB_PORT || '5432'),
    database: process.env.DB_POSTGRESDB_DATABASE,
    user: process.env.DB_POSTGRESDB_USER,
    password: process.env.DB_POSTGRESDB_PASSWORD,
  });

  await client.connect();
  try {
    const result = await client.query(
      'SELECT data FROM n8n.credentials_entity WHERE name = $1 AND type = $2',
      [credentialName, credentialType],
    );
    if (result.rowCount !== 1) throw new Error('expected exactly one Telegram credential match');

    const cipher = new Cipher({ encryptionKey: process.env.N8N_ENCRYPTION_KEY });
    const values = JSON.parse(cipher.decrypt(result.rows[0].data));
    if (typeof values.accessToken !== 'string' || values.accessToken.length === 0) {
      throw new Error('credential has no Telegram access token');
    }

    const url = `http://egress-gateway:8080/telegram/bot${values.accessToken}/deleteWebhook?drop_pending_updates=true`;
    const response = await fetch(url, { method: 'POST', redirect: 'error' });
    const body = await response.json();
    if (!response.ok || body.ok !== true) throw new Error('Telegram deleteWebhook was rejected');
    console.log(`VERIFIED: Telegram webhook removed for ${credentialType}/${credentialName}`);
  } finally {
    await client.end();
  }
}

main().catch((error) => {
  console.error(`FAILED: ${error.message}`);
  process.exitCode = 1;
});
