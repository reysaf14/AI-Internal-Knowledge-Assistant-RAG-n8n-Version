# Asisten Pengetahuan Internal Toko Makmur Jaya

> n8n-based Telegram RAG assistant — answer internal knowledge questions from approved document corpus only.

---

## Architecture

```
Telegram → n8n Webhook → [Embedding] → [pgvector Similarity]
         → [AI Chat (grounded)] → Telegram Response
         → [Postgres dedup/state/timing]
```

| Layer | Technology | Version |
|-------|-----------|---------|
| Orchestration | n8n (self-hosted) | latest stable |
| Vector DB | pgvector (PostgreSQL) | latest |
| AI Provider | OpenAI-compatible (any provider) | configurable |
| Channel | Telegram Bot API | — |

See [architecture.md](.ai/knowledge/architecture.md) for full spec (v1.2, 8 milestones, acceptance matrix).

---

## Quick Start (local-isolated)

### Prerequisites

- Docker Desktop / Docker Engine + Compose v2
- `deploy/compose.yaml` (buatan DevOps, M6) + `.env.test` (dummy local)

### 1. Configure

```bash
cp .env.example .env.test
# Fill in test-only values (see .env.test for the dummy defaults)
# NEVER use production secrets in .env.test
```

### 2. Start stack

```bash
bash deploy/start-local.sh
```

Launcher akan:
1. Validasi compose config (quiet)
2. `docker compose up -d` dengan project `rag-local` + `.env.test`
3. Menunggu healthcheck

Services:
| Service | Port | Purpose |
|---------|------|---------|
| n8n | 127.0.0.1:5678 (loopback only) | Workflow UI + webhook |
| PostgreSQL + pgvector | internal (no host port) | Vector store + dedup + state |

### 3. Stop stack

```bash
bash deploy/stop-local.sh
# Volumes preserved. To also remove volumes:
#   docker compose -f deploy/compose.yaml --project-name rag-local --env-file .env.test down -v
```

### 4. Import workflows

See `deploy/WORKFLOW-IMPORT-GUIDE.md` — three options (CLI, API, UI).

1. Open n8n UI at `http://127.0.0.1:5678`
2. Import `workflows/01-corpus-ingestion.json`
3. Import `workflows/02-telegram-grounded-qa.json`
4. Configure credential `ai-provider` with the approved cloud chat API key; the non-secret OpenAI-compatible chat endpoint and model binding are stored in `rag.rag_settings`, while EmbeddingGemma remains local
5. Configure Telegram bot credential `telegram-demo-bot` (BotFather token) for workflow 02
6. Populate `rag.rag_settings`, including `chat_base_url`, `chat_api_path`, the cloud `chat_model`, allowed Telegram chat ID, and existing embedding profile values; run the alignment migration for an existing database volume
7. Activate only after workflow credentials, runtime settings, and an active corpus are ready. For the cloud-chat/local-embedding profile, follow `deploy/CLOUD-CHAT-SETUP-GUIDE.md` and `deploy/WORKFLOW-IMPORT-GUIDE.md`.

### 5. Ingest corpus

1. Run workflow 01 (Manual Trigger)
2. Documents from `docs/` (mounted read-only) are embedded and stored in pgvector
3. Verify: query `SELECT count(*) FROM rag.documents WHERE corpus_version = (SELECT active_corpus_version FROM rag.rag_settings)`

### 6. Ask questions

**local-isolated**: validate import, graph, AI, and database contracts; live Telegram requires a reachable approved webhook endpoint.
**demo-vps**: after credential binding, settings, and corpus activation, send a message to the Telegram bot and verify the grounded response and delivery state.

---

## Corpus Management

### Source documents

26 Markdown files in `docs/` covering:

| Category | Count | Files |
|----------|-------|-------|
| Company Profile | 1 | `00_Company_Profile_Toko_Makmur_Jaya.md` |
| SOP | 8 | `01` – `08` |
| FAQ | 15 | `09` – `23` |
| Kebijakan Internal | 2 | `24`, `25` |

**All source files must be in `docs/`.** Files outside this folder are never ingested.

### Update a document

1. Edit the `.md` file in `docs/`
2. Re-run workflow 01
3. Old version is replaced (idempotent upsert by filename)

### Add a new document

1. Add a new `.md` file to `docs/` following the naming convention: `NN_Category_Name.md`
2. Assign the next sequential number (currently 00–25 → next is 26)
3. Re-run workflow 01
4. Update `evaluation/qa-dataset.csv` with new test questions for the new document

### Evaluation Dataset

`evaluation/qa-dataset.csv` — 15 questions (12 supported + 3 unsupported):

| Category | Supported Questions |
|----------|-------------------|
| SOP | 3 |
| FAQ | 3 |
| Panduan | 2 |
| Kebijakan Internal | 3 |
| Profil Perusahaan | 1 |
| Unsupported (outside corpus) | 3 |

**Supported** = answer exists in an approved corpus document.  
**Unsupported** = question cannot be answered from the corpus; system responds with "Informasi tidak ditemukan di dokumen resmi."

---

## Environment Variables

All variables are defined in `.env.example` with full documentation. Key categories:

| Category | Variables | Provisioned by |
|----------|-----------|---------------|
| Container images | `N8N_IMAGE`, `PGVECTOR_IMAGE` | DevOps |
| Secrets | `N8N_ENCRYPTION_KEY`, `POSTGRES_PASSWORD`, DB passwords | Human |
| Hostname/TLS | `PUBLIC_HOSTNAME`, `ACME_EMAIL` | DevOps |
| Timezone | `GENERIC_TIMEZONE` | Human |
| AI config | AI_TIMEOUT_MAX, embedding dim | Engineer (after profiling) |

**NEVER** commit `.env`, `.env.test`, or any file containing real secrets.

---

## Testing (local-isolated, no network)

Engineer self-tests verify each milestone independently:

```bash
# M2 — Corpus Ingestion (AC-001..005) — 19 tests
python tests/harness/test_ingestion.py

# M3 — Grounded QA (AC-011..020) — 21 tests
python tests/harness/test_qa_core.py

# M4 — Delivery & Deadline (AC-006..010, 022..024) — 27 tests
python tests/harness/test_delivery_core.py
```

**All tests use stdlib + mock AI provider only** — no real API keys, no network, no real Telegram.  
Tests run on any OS with Python 3.10+. No pip install required.

### What the tests verify

| Milestone | AC | Coverage |
|-----------|-----|---------|
| M2 | 001–005 | Ingestion, upsert, validation, idempotency |
| M3 | 011–020 | Retrieval, citation, grounding, unsupported, injection, boundary |
| M4 | 006–010, 022–024 | Webhook validation, dedup, timeout, provider failure, deadline |

---

## Project Structure

```
.
├── docs/                          # 26 approved corpus documents
├── workflows/
│   ├── 01-corpus-ingestion.json   # n8n workflow: embed + store documents
│   └── 02-telegram-grounded-qa.json # n8n workflow: webhook → QA → Telegram
├── tests/
│   ├── harness/                   # Test harness + self-tests
│   │   ├── rag_ingest_core.py     # Ingestion pipeline (pure Python)
│   │   ├── rag_qa_core.py         # QA pipeline (pure Python)
│   │   ├── telegram_delivery_core.py # Delivery pipeline + state
│   │   ├── test_ingestion.py      # M2 self-test (19 tests)
│   │   ├── test_qa_core.py        # M3 self-test (21 tests)
│   │   └── test_delivery_core.py  # M4 self-test (27 tests)
│   ├── mocks/
│   │   └── ai-provider/
│   │       └── provider_mock.py   # OpenAI-compatible mock server
│   └── fixtures/
│       ├── corpus/
│       │   └── synthetic_corpus.md # Test corpus fixture
│       └── telegram/
│           └── synthetic_updates.jsonl # 10 Telegram update fixtures
├── evaluation/
│   └── qa-dataset.csv             # 15-question eval dataset (12+3)
├── .ai/
│   ├── knowledge/
│   │   └── architecture.md        # Architecture spec v1.2
│   ├── reports/
│   │   └── build/                 # Milestone exit reports
│   └── project-state.md           # Current project state
├── .env.example                   # Canonical env schema v1.1
├── .gitignore                     # Excludes .env, secrets, artifacts
├── README.md                      # This file
└── DESIGN.md                      # Design tokens (n8n UI theming)
```

---

## Data Limitations

| Limit | Value | Reason |
|-------|-------|--------|
| Embedding dimension | Depends on model | Set via `RAG_EMBEDDING_DIMENSION` after model selection |
| Similarity threshold | Unknown until profiling | TEST-ONLY value 0.25 in self-tests; runtime needs real model profiling |
| Corpus size | 26 documents | Toko Makmur Jaya internal docs |
| Eval dataset | 15 questions | Synthetic; needs human review for production |
| Max retrieval | Configurable | Set in `rag_settings` table |
| Timeout budget | Unknown until profiling | Must leave headroom for Telegram send (< 5s total) |

---

## Teardown

```bash
docker compose down -v  # stop + remove volumes
rm -f .env              # remove secrets
```

---

## License

Internal use only — Toko Makmur Jaya.
