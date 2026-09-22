#!/usr/bin/env node
'use strict';

/**
 * Narrow, one-purpose migration for the locally stored n8n Telegram credential.
 *
 * It keeps the encrypted token in memory only, updates only `baseUrl`, and uses
 * n8n's own credential cipher. It never logs credential values.
 *
 * Run from the n8n container with NODE_PATH pointing at n8n's node_modules.
 * The default is a read-only validation. Add --apply to persist the change.
 */

const { Client } = require('pg');
const { Cipher } = require('n8n-core/dist/encryption/cipher');

const credentialName = process.env.TELEGRAM_CREDENTIAL_NAME || 'telegram-demo-bot';
const credentialType = 'telegramApi';
const targetBaseUrl = 'http://egress-gateway:8080/telegram';
const shouldApply = process.argv.includes('--apply');
async function main() {
  if (!process.env.N8N_ENCRYPTION_KEY) {
    throw new Error('N8N_ENCRYPTION_KEY is unavailable');
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
    await client.query('BEGIN');
    const result = await client.query(
      'SELECT id, name, type, data FROM n8n.credentials_entity WHERE name = $1 AND type = $2 FOR UPDATE',
      [credentialName, credentialType],
    );
    if (result.rowCount !== 1) {
      throw new Error('expected exactly one Telegram credential match');
    }

    const row = result.rows[0];
    const cipher = new Cipher({ encryptionKey: process.env.N8N_ENCRYPTION_KEY });
    const values = JSON.parse(cipher.decrypt(row.data));
    if (typeof values.accessToken !== 'string' || values.accessToken.length === 0) {
      throw new Error('credential has no Telegram access token');
    }

    if (!shouldApply) {
      await client.query('ROLLBACK');
      if (values.baseUrl === targetBaseUrl) {
        console.log(`VERIFIED: ${credentialType}/${credentialName} uses the egress gateway`);
      } else {
        console.log(`VALIDATED: ${credentialType}/${credentialName} can be rewritten to the egress gateway`);
      }
      return;
    }

    values.baseUrl = targetBaseUrl;
    const encrypted = cipher.encrypt(values);
    await client.query(
      'UPDATE n8n.credentials_entity SET data = $1, "updatedAt" = NOW() WHERE id = $2',
      [encrypted, row.id],
    );
    await client.query('COMMIT');
    console.log(`UPDATED: ${credentialType}/${credentialName} base URL now uses the egress gateway`);
  } catch (error) {
    await client.query('ROLLBACK').catch(() => undefined);
    throw error;
  } finally {
    await client.end();
  }
}

main().catch((error) => {
  console.error(`FAILED: ${error.message}`);
  process.exitCode = 1;
});
