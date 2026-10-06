# Internal Knowledge Assistant for Toko Makmur Jaya

> A Telegram based knowledge assistant that answers internal business questions from approved company documents.

## Project Overview

### The Problem

Business information was spread across company profiles, SOPs, policies, and FAQs. Employees had to search these documents manually, which slowed down routine decisions and increased the risk of inconsistent answers.

The assistant also needed to avoid inventing information when an answer was not available in the approved document collection.

### The Solution

This project turns the approved document library into a searchable knowledge service inside Telegram. Users can ask questions in natural language and receive a grounded answer with supporting sources. When the information cannot be verified, the assistant clearly abstains.

The project was completed as a local portfolio demo. The runtime is currently stopped and project credentials were removed after the demo, while the source workflows, corpus volumes, and restore documentation remain available.

### Business Value

- Faster access to internal procedures and policies
- More consistent answers for routine operational questions
- Clear handling of questions outside the approved knowledge scope
- A maintainable workflow for updating company documents
- Traceable delivery and failure states for operational review

## How It Works

```text
Approved Markdown documents
          │
          ▼
Corpus ingestion → embeddings → PostgreSQL/pgvector
                                      │
Telegram question → retrieval → grounded answer → Telegram response
                                      │
                         citations, abstention, and delivery state
```

The project uses two n8n workflows:

1. `01 — Corpus Ingestion` validates documents, creates a content based version, splits documents into chunks, generates embeddings, writes a candidate corpus, and activates it atomically.
2. `02 — Telegram Grounded Q&A` validates the incoming update, prevents duplicate processing, retrieves relevant evidence, generates a grounded answer, validates citations, records sanitized diagnostics, and tracks delivery status.

## Architecture

| Layer | Technology | Responsibility |
|---|---|---|
| Orchestration | n8n self hosted | Workflow execution and branching |
| Document source | Markdown files | Approved internal knowledge corpus |
| Vector search | PostgreSQL with pgvector | Embedding storage and similarity retrieval |
| Chat generation | DeepSeek chat route | Grounded answer generation |
| Embeddings | Local EmbeddingGemma | Local embedding generation for the demo |
| User channel | Telegram Bot API | Staff question and answer interface |
| Network boundary | Caddy egress gateway | Fixed routes to approved external services and host local Ollama |
| Runtime | Docker Compose | Local isolation and repeatable startup |

See [architecture.md](.ai/knowledge/architecture.md) for the approved architecture and acceptance matrix.

## Quick Start — Restore the Local Demo

### Prerequisites

- Docker Desktop or Docker Engine with Compose v2
- Python 3.10+ for the deterministic test harness
- A local `.env.test` file based on `.env.example`
- Credentials entered into the n8n credential store

After the M8 cleanup, the named n8n and PostgreSQL volumes are preserved, but the five project credentials were removed. A future demo therefore requires credential recreation and workflow rebinding.

### 1. Configure the local profile

Create `.env.test` from `.env.example` for a new checkout and fill it with test only values. Never use production secrets in `.env.test`.

```powershell
Copy-Item .env.example .env.test
```

### 2. Start the stack

```powershell
docker compose -f deploy/compose.yaml --project-name rag-local --env-file .env.test up -d
```

Or use the launcher on a Bash compatible shell:

```bash
bash deploy/start-local.sh
```

| Service | Exposure | Purpose |
|---|---|---|
| n8n | `127.0.0.1:5678` | Workflow editor and runtime |
| PostgreSQL + pgvector | Internal Docker network | Vector store, corpus state, and delivery state |
| Egress gateway | Internal Docker network | Fixed Telegram, DeepSeek, and Ollama routes |

### 3. Bind credentials

Use the exact credential names below when restoring the existing workflows:

| Credential | Type | Main consumer |
|---|---|---|
| `postgres-rag-ingest` | PostgreSQL | Workflow 01 |
| `postgres-rag-runtime` | PostgreSQL | Workflow 02 |
| `DeepSeek account` | DeepSeek API | `Chat Completion` |
| `telegram-demo-bot` | Telegram API | `TelegramTrigger` and `Telegram Send` |

For PostgreSQL credentials, use the container host `postgres`, not `localhost`. The database and passwords come from the local test configuration and must never be placed in workflow JSON or reports.

For the Telegram credential, set the Base URL to:

```text
http://egress-gateway:8080/telegram
```

For a new n8n instance, import both files from `workflows/` and rebind credentials after import. For the preserved local instance, reopen the existing workflows and select the recreated credentials on nodes showing a missing credential. See [WORKFLOW-IMPORT-GUIDE.md](deploy/WORKFLOW-IMPORT-GUIDE.md) for the import options.

### 4. Prepare runtime settings and corpus

The `rag.rag_settings` row must contain the approved chat metadata, embedding profile, embedding dimension, retrieval limits, timeout values, allowed Telegram chat ID, and configuration revision. See [CLOUD-CHAT-SETUP-GUIDE.md](deploy/CLOUD-CHAT-SETUP-GUIDE.md) for the provider binding details.

The preserved demo corpus contains 26 Markdown documents and 297 indexed chunks with 768 dimensional embeddings. Run workflow 01 with its Manual Trigger only when the corpus needs to be rebuilt.

### 5. Enable Telegram E2E

Telegram requires a reachable HTTPS webhook. A loopback URL such as `127.0.0.1` cannot register a live Telegram webhook.

1. Provide an approved HTTPS `WEBHOOK_URL` before recreating n8n.
2. Confirm all credentials, runtime settings, and the active corpus.
3. Activate workflow 02 only after webhook registration succeeds.
4. Test supported and unsupported questions from an allowed Telegram chat.

For local graph, provider, and database checks without Telegram, keep workflow 02 inactive.

The complete restore and post demo cleanup procedure is documented in [LOCAL-DEMO-USER-GUIDE.md](deploy/LOCAL-DEMO-USER-GUIDE.md).

## Corpus Management

All source files must be stored in `docs/`. Files outside that directory are not ingested.

| Category | Count | Files |
|---|---:|---|
| Company profile | 1 | `00_Company_Profile_Toko_Makmur_Jaya.md` |
| SOP | 8 | `01`–`08` |
| FAQ | 15 | `09`–`23` |
| Internal policy | 2 | `24`–`25` |

### Update an existing document

1. Edit the Markdown file in `docs/`.
2. Run workflow 01.
3. Confirm that the new corpus version becomes active.

The ingestion workflow uses content hashes and idempotent upserts, so an identical rerun does not create duplicate chunks.

### Add a document

1. Add a file using the `NN_Category_Name.md` naming convention.
2. Continue the sequence after `00`–`25`.
3. Run workflow 01.
4. Add evaluation questions to `evaluation/qa-dataset.csv` when the new content changes the expected knowledge scope.

## Evaluation Dataset and Testing

`evaluation/qa-dataset.csv` contains 15 questions:

- 12 supported questions with answers in the approved corpus
- 3 unsupported questions that should produce a clear abstention

The deterministic local harness uses only Python standard library components and a mock AI provider. It does not use real API keys, real Telegram traffic, or production data.

```bash
# M2 — Corpus ingestion: 19 tests
python tests/harness/test_ingestion.py

# M3 — Grounded QA: 21 tests
python tests/harness/test_qa_core.py

# M4 — Delivery and deadline behavior: 27 tests
python tests/harness/test_delivery_core.py
```

The recorded implementer regression is `67/67` passed. The latest independent semantic demo matrix also recorded `15/15` delivered answers, with supported and unsupported behavior validated under the agreed local demo scope. These results are evidence for the documented candidate and do not represent a production guarantee.

## Security and Operational Boundaries

- Workflow credentials are stored in n8n and are not committed to exports or documentation.
- PostgreSQL uses separate ingest and runtime roles.
- The application network is internal; external calls pass through fixed egress routes.
- Configuration errors fail closed before provider calls or database writes.
- The assistant abstains when evidence is missing or unsupported.
- Runtime diagnostics are sanitized and do not store raw prompts, provider payloads, or secrets.
- Live Telegram use requires an approved HTTPS endpoint.
- The project is scoped as a local portfolio demo. Public publication, client handoff, production use, and release claims require a new review.

## Project Structure

```text
.
├── docs/                              # Approved business knowledge documents
├── workflows/
│   ├── 01-corpus-ingestion.json      # Ingest, embed, stage, and activate corpus
│   └── 02-telegram-grounded-qa.json  # Telegram question and answer workflow
├── tests/
│   ├── harness/                       # Deterministic contract tests
│   ├── mocks/ai-provider/             # Local mock provider
│   └── fixtures/                      # Synthetic corpus and Telegram updates
├── evaluation/qa-dataset.csv          # 15 question evaluation set
├── deploy/
│   ├── compose.yaml                   # Local isolated stack
│   ├── postgres-init/                 # Schema and security migrations
│   ├── egress-gateway/                # Fixed outbound routes
│   ├── cleanup/                       # Scoped cleanup helpers
│   └── LOCAL-DEMO-USER-GUIDE.md       # Restore, run, and cleanup guide
├── .ai/
│   ├── knowledge/                     # PRD, architecture, and environment contract
│   ├── reports/                       # Build, QA, and Security evidence
│   └── project-state.md               # Current milestone state
├── .env.example                       # Canonical environment template
└── README.md                          # This overview
```

## Stop and Cleanup

To stop the demo while preserving the named volumes:

```powershell
docker compose -f deploy/compose.yaml --project-name rag-local --env-file .env.test stop
```

Do not use `down -v` unless the demo database and n8n state are disposable. Full post demo cleanup, credential removal, webhook removal, and restoration instructions are in [LOCAL-DEMO-USER-GUIDE.md](deploy/LOCAL-DEMO-USER-GUIDE.md).

## License

Internal use and local portfolio demonstration only — Toko Makmur Jaya.
