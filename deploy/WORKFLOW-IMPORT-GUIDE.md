# Workflow Import Guide — Asisten Pengetahuan Internal Toko Makmur Jaya

- Profile: local-isolated
- Created: 2026-09-14
- Architecture version: 1.2

## Overview

Workflow files in `workflows/` are DRAFT exports (current workflow 02 version `m7-cloud-chat-local-embedding-v1`), unpublished. The local working export contains environment-specific credential metadata for the current n8n instance; a clean instance still requires credential rebinding before activation.

**Workflow JSON on disk ≠ imported or active workflow.** This guide documents the import mechanism for the actual n8n instance.

## Prerequisites

- n8n container running and healthy (`http://127.0.0.1:5678` accessible)
- n8n owner account created via UI (first-run setup)
- DeepSeek credential configured in n8n credential store (`DeepSeek account`) with the approved API key
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

The init directory runs only when PostgreSQL initializes an empty volume. For an existing volume, use the guarded migration runner so alignment and security hardening are applied together:

```bash
bash deploy/apply-existing-volume-migrations.sh .env.test
```

On Windows PowerShell use
`.\deploy\apply-existing-volume-migrations.ps1 -EnvFile .env.test`.
The runner applies `02-rag-schema-alignment.sql` and
`03-rag-security-hardening.sql`, then verifies the
`rag-security-hardening-v1|4` marker. PostgreSQL health and n8n startup fail
closed until that marker exists. Do not put database passwords in the command
line or commit them to the repository.

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
| Embedding Request | None | Existing local EmbeddingGemma route; no cloud credential is sent |

For the project Compose n8n container, use PostgreSQL host `postgres`. If n8n runs as a separate Windows/host instance, PostgreSQL is published only on loopback by `compose.yaml`; use host `127.0.0.1` and port `5432` instead. Do not use `localhost`/`127.0.0.1` from a container that is not the host, and do not expose PostgreSQL on a public interface.

### Workflow 02 — Telegram Grounded Q&A

| Node | Credential Required | Type |
|------|-------------------|------|
| Telegram Trigger and Telegram Send | `telegram-demo-bot` | Bot token from BotFather |
| Query Embedding | None | Existing local EmbeddingGemma route; no cloud embedding call |
| Chat Completion | `DeepSeek account` | DeepSeek API key; current credentialed route is fixed to `https://api.deepseek.com/chat/completions` |
| PostgreSQL nodes | `postgres-rag-runtime` | Connection to `rag` schema (role: `rag_runtime`) |
| Telegram Send | `telegram-demo-bot` | Same bot token |

### Current DeepSeek OpenAI-compatible provider profile

The exported workflow uses the OpenAI-compatible chat contract with the current approved DeepSeek route fixed in the credentialed HTTP node. `rag_settings.chat_base_url` and `chat_api_path` are consistency metadata and are validated fail-closed; they are not used to construct a credentialed destination. Embeddings intentionally remain on the local EmbeddingGemma tester, so the current corpus and vector dimension are preserved.

The key alone cannot identify a provider's endpoint or chat model. Those two non-secret values must be entered once in `rag.rag_settings` from the chosen provider's model inventory. The embedding model/profile/dimension stays unchanged:

```sql
UPDATE rag.rag_settings
SET config_revision = 'cloud-chat-local-embedding-<date>',
    chat_base_url = 'https://api.deepseek.com',
    chat_api_path = '/chat/completions',
    chat_model = 'deepseek-flash',
    ai_timeout_max = <measured-online-budget-ms>,
    ingest_timeout_max = <measured-ingest-budget-ms>,
    updated_at = now()
WHERE id = 1;
```

The current workflow validates the exact HTTPS origin `https://api.deepseek.com` and sends only to `/chat/completions`. The credentialed HTTP node disables both ordinary and all-redirect following; a non-2xx/3xx response is handled as a provider failure rather than followed to another origin. A provider with a different origin or native non-compatible API needs a separate reviewed adapter/workflow and Security re-audit; editing `rag_settings` alone cannot redirect the credentialed request.

Changing only `chat_model` or the chat endpoint does not require re-ingestion. Do not send retrieved confidential corpus excerpts or questions to a hosted provider until the Human data-processing approval for that provider, retention, and region is recorded.

### Local Ollama tester profile (M6 only)

Use this profile only for local runtime readiness and provider-contract testing. It is not a quality or release verdict.

| Binding | Value |
|---|---|
| `rag_settings.chat_base_url` | `http://host.docker.internal:11434` (historical local-chat tester profile only) |
| `ai-provider` API key | Any local-only non-secret placeholder if the n8n credential form requires one; Ollama does not use it for local auth |
| `rag_settings.chat_api_path` | `/v1/chat/completions` |
| `rag_settings.chat_model` | `gemma4:e2b-it-qat` (current local tester binding; runtime-selectable) |
| `rag_settings.embedding_model` | `embeddinggemma:300m-qat-q4_0` |
| `rag_settings.embedding_dimension` | `768` |
| `rag_settings.config_revision` | `m6-local-gemma-bounded-2026-09-20` |
| `rag_settings.ai_timeout_max` | `3000` ms; workflow 02 dynamically reduces this against the fixed `<5000` ms business deadline and reserves `1000` ms for Telegram delivery |
| `rag_settings.ingest_timeout_max` | `120000` ms; offline workflow 01 batch budget, separate from the online Telegram SLA |
| Optional alternative chat/vision model | `qwen3-8b-2k:latest` |

The n8n container must be able to reach Ollama through `host.docker.internal`; `127.0.0.1` inside the container is not the Windows host. This local-chat profile is retained as historical tester documentation only; the current export is fixed to DeepSeek and requires an adapter change before Ollama chat can be used. EmbeddingGemma remains on the existing local embedding route.

Workflow 02 carries `start_ts` from the trigger. Before each AI call it computes the remaining deadline budget; an exhausted budget follows the sanitized service-unavailable branch. This bounded control is ready for QA profiling but does not itself prove the required `15/15` responses below `5,000ms`.

The exported workflow sends chat only to `https://api.deepseek.com/chat/completions`. A provider change requires a reviewed adapter/workflow change and Security re-audit; changing database URL metadata alone cannot redirect the credentialed request. The embedding nodes retain their local tester endpoint.

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
