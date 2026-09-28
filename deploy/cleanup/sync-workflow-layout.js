#!/usr/bin/env node
'use strict';

/**
 * Behavior-neutral layout sync for the two known local-demo workflows.
 * Only node positions are copied from the checked-in exports into the exact
 * inactive runtime records; parameters, credentials, connections, and IDs
 * are not replaced.
 */

const fs = require('fs');
const { Client } = require('pg');

const workflows = [
  { id: '5E9eQbknShf6iskV', path: '/import-workflows/01-corpus-ingestion.json' },
  { id: 'IAOqkQsNamEJarHF', path: '/import-workflows/02-telegram-grounded-qa.json' },
];

async function main() {
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
    for (const item of workflows) {
      const result = await client.query(
        'SELECT id, name, active, nodes FROM n8n.workflow_entity WHERE id = $1 FOR UPDATE',
        [item.id],
      );
      if (result.rowCount !== 1) throw new Error(`workflow ${item.id} not found`);
      const runtime = result.rows[0];
      if (runtime.active) throw new Error(`workflow ${item.id} must be inactive before layout sync`);

      const source = JSON.parse(fs.readFileSync(item.path, 'utf8'));
      const runtimeNodes = typeof runtime.nodes === 'string' ? JSON.parse(runtime.nodes) : runtime.nodes;
      const sourceById = new Map(source.nodes.map((node) => [node.id, node]));
      if (runtimeNodes.length !== source.nodes.length) {
        throw new Error(`workflow ${item.id} node count differs from source`);
      }
      for (const node of runtimeNodes) {
        const sourceNode = sourceById.get(node.id);
        if (!sourceNode || sourceNode.name !== node.name) {
          throw new Error(`workflow ${item.id} node identity differs from source`);
        }
        node.position = sourceNode.position;
      }

      await client.query(
        'UPDATE n8n.workflow_entity SET nodes = $1, "updatedAt" = NOW() WHERE id = $2',
        [JSON.stringify(runtimeNodes), item.id],
      );
      console.log(`UPDATED: ${runtime.name} (${runtimeNodes.length} node positions)`);
    }
    await client.query('COMMIT');
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
