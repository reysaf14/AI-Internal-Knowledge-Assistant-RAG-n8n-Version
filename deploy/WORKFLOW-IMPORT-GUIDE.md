# Workflow Import Guide — Asisten Pengetahuan Internal Toko Makmur Jaya

- Profile: local-isolated
- Created: 2026-09-14
- Architecture version: 1.2

## Overview

Workflow files in `workflows/` are DRAFT exports (m6-aligned-v1), unpublished and without credential bindings. They must be imported into a running n8n instance before they can execute.

**Workflow JSON on disk ≠ imported or active workflow.** This guide documents the import mechanism for the actual n8n instance.

## Prerequisites

- n8n container running and healthy (`http://127.0.0.1:5678` accessible)
- n8n owner account created via UI (first-run setup)
- AI provider credential configured in n8n credential store (`ai-provider`)
- Telegram bot credential configured in n8n (`telegram-demo-bot`) for workflow 02
- Database roles provisioned (handled by `postgres-init/01-init.sh`)
- Existing database volume aligned with `postgres-init/02-rag-schema-alignment.sql`

## Import Mechanism

### Option A: n8n CLI (recommended for local-isolated)

```bash
# Import workflow 01 — Corpus Ingestion
docker exec rag-n8n-local n8n import:workflow \
  --input=/import-workflows/01-corpus-ingestion.json

# Import workflow 02 — Telegram Grounded Q&A
docker exec rag-n8n-local n8n import:workflow \
  --input=/import-workflows/02-telegram-grounded-qa.json
```

The `/import-workflows` path is mounted read-only from `workflows/` in `deploy/compose.yaml`.

### Existing-volume schema alignment

The init directory runs only when PostgreSQL initializes an empty volume. For an existing volume, apply the idempotent alignment migration once using an approved database-admin connection:

```bash
docker exec -i rag-postgres-local psql -U <db-admin-role> -d <db-name> \
  < deploy/postgres-init/02-rag-schema-alignment.sql
```

Do not put database passwords in the command line or commit them to the repository.

### Option B: n8n REST API

```bash
# Import workflow 01
curl -X POST http://127.0.0.1:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: <owner-api-key>" \
  -d @workflows/01-corpus-ingestion.json

# Import workflow 02
curl -X POST http://127.0.0.1:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: <owner-api-key>" \
  -d @workflows/02-telegram-grounded-qa.json
```

### Option C: n8n UI (manual)

1. Open `http://127.0.0.1:5678`
2. Login with owner account
3. Click **Workflows** → **Import from File**
4. Select `workflows/01-corpus-ingestion.json`
5. Repeat for `02-telegram-grounded-qa.json`
6. **Do NOT activate (publish) yet** — credential binding must be configured first

## Post-Import Configuration

After import, each workflow needs credential rebinding in n8n UI:

### Workflow 01 — Corpus Ingestion

| Node | Credential Required | Type |
|------|-------------------|------|
| Load RAG Settings, staging/failure PostgreSQL nodes | `postgres-rag-ingest` | Connection to `rag` schema (role: `rag_ingest`) |
| Embedding Request | `ai-provider` | OpenAI-compatible base URL + API key |

For the project Compose n8n container, use PostgreSQL host `postgres`. If n8n runs as a separate Windows/host instance, PostgreSQL is published only on loopback by `compose.yaml`; use host `127.0.0.1` and port `5432` instead. Do not use `localhost`/`127.0.0.1` from a container that is not the host, and do not expose PostgreSQL on a public interface.

### Workflow 02 — Telegram Grounded Q&A

| Node | Credential Required | Type |
|------|-------------------|------|
| Telegram Trigger and Telegram Send | `telegram-demo-bot` | Bot token from BotFather |
| Query Embedding and Chat Completion | `ai-provider` | Same OpenAI-compatible endpoint |
| PostgreSQL nodes | `postgres-rag-runtime` | Connection to `rag` schema (role: `rag_runtime`) |
| Telegram Send | `telegram-demo-bot` | Same bot token |

### Local Ollama tester profile (M6 only)

Use this profile only for local runtime readiness and provider-contract testing. It is not a quality or release verdict.

| Binding | Value |
|---|---|
| `ai-provider` base URL | `http://host.docker.internal:11434/v1` |
| `ai-provider` API key | Any local-only non-secret placeholder if the n8n credential form requires one; Ollama does not use it for local auth |
| `rag_settings.chat_model` | `qwen3-8b-2k:latest` |
| `rag_settings.embedding_model` | `embeddinggemma:300m-qat-q4_0` |
| `rag_settings.embedding_dimension` | `768` |
| Optional alternative chat/vision model | `gemma4:e2b-it-qat` |

The n8n container must be able to reach Ollama through `host.docker.internal`; `127.0.0.1` inside the container is not the Windows host. Configure Ollama to listen on a host-reachable interface before testing. The Qwen workflow request sets `reasoning_effort: 'none'` to avoid spending the short tester budget on hidden reasoning; this is a runtime test setting, not a quality claim.

The exported workflows use explicit Docker-local endpoint paths (`/v1/embeddings` and `/v1/chat/completions`). The `ai-provider` credential supplies the OpenAI-compatible authentication fields; its Base URL is retained for credential testing, but is not interpolated into the HTTP Request node URL because credential fields are not available there as workflow expressions.

The HTTP Request nodes use `Raw` body mode with `Content-Type: application/json`. Ingestion builds the 297-input payload once in `Prepare Embedding Request`, then sends the resulting `request_body` string from a single input item. This avoids both the `Using JSON` coercion issue and the unreliable large inline expression in n8n `1.123.81`. `Embedding Request` also retains `Execute Once` as a defensive guard against repeated batch requests.

For PostgreSQL nodes on n8n `1.123.81`, query-parameter arrays are built only from the current item (`$json`). `Restore Ingest Batch` explicitly restores the batch after the version-upsert node, and `Staging: Insert Chunks` returns the corpus/profile identity even when an idempotent rerun inserts zero rows. Do not replace these with cross-node `$()` expressions inside the parameter array: that form is coerced to an unsupported value type by this node version.

### Environment-Specific Settings (in n8n UI)

| Setting | Value | Location |
|---------|-------|----------|
| Telegram allowed chat ID | `<fill at runtime>` | `rag.rag_settings.telegram_allowed_chat_id` |
| RAG settings | `<fill at runtime>` | `rag.rag_settings` before activation |
| Active corpus | `<fill at runtime>` | Set by successful workflow 01 activation |

The Telegram Trigger export uses node version `1.2`, so n8n performs its generated webhook secret-token verification when the workflow is activated. The allowed chat ID remains a runtime database setting and is checked again by `Validate Input`; it is not embedded in the export.

## Activation (Publishing)

After all credentials are bound, `rag.rag_settings` is complete, and a corpus is active:

1. Open each workflow in n8n UI
2. Click **Active** toggle to enable
3. n8n manages the Telegram webhook when workflow 02 is activated. The target n8n URL must be reachable by Telegram; local-isolated cannot complete live Telegram E2E without an approved externally reachable endpoint.

## Verification

```bash
# Check n8n health
curl -s http://127.0.0.1:5678/healthz

# Check workflows are imported (API)
curl -s http://127.0.0.1:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: <key>" | python -m json.tool

# Check database connection
docker exec rag-postgres-local psql -U cluster_admin -d automation -c "\dn"
# Expected: n8n, rag schemas visible
```

## Limitations

- **local-isolated**: database, AI, import, and static validation are possible; the Telegram Trigger still requires an externally reachable approved endpoint for live E2E
- **demo-vps**: Requires domain, TLS, DNS, and the Telegram credential before webhook registration
- Workflow exports are DRAFT — they will show as "needs configuration" until credentials and runtime settings are bound
- AI provider must be healthy and accessible from n8n container network
