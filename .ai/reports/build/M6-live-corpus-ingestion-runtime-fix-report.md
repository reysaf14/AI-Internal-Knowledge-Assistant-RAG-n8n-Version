# M6 — Live Corpus Ingestion Runtime Fix Report

## Objective and scope

- Project: `Asisten Pengetahuan Internal Toko Makmur Jaya`
- Lane / matrix: `PROFESSIONAL`; Architecture `1.2`; Acceptance Matrix `1.0`
- Executor / independence: Engineer — `VERIFIED BY IMPLEMENTER`, bukan QA independen
- Timestamp: `2026-09-19T21:25:24+07:00` (`Asia/Jakarta`)
- Candidate artifact: `workflows/01-corpus-ingestion.json` version `m6-live-ingestion-v2`; SHA-256 `601C0398869972E2E52861E5E43131006B484EDC496755074F9939FB9ED314F1`
- Included: live local-isolated ingestion melalui n8n Docker, Ollama host endpoint, PostgreSQL/pgvector persistence, atomic activation, dan identical rerun.
- Excluded: workflow 02, Telegram webhook/send, 15-item quality evaluation, independent QA/Security, demo-vps, M7, dan M8.

## Findings and changes

| Finding | Root cause | Minimal correction | Location |
|---|---|---|---|
| `F-M6-ING-001` — embedding request returned `EOF` / invalid JSON | n8n `1.123.81` did not reliably serialize the large 297-input body when the HTTP Request node constructed it inline. Direct Ollama execution of the same 297 texts succeeded, isolating the defect to workflow body construction. | `Prepare Embedding Request` serializes one `request_body`; HTTP Request uses Raw `application/json`, one input item, and `Execute Once`. | `workflows/01-corpus-ingestion.json` — `Prepare Embedding Request`, `Embedding Request` |
| `F-M6-ING-002` — green activation could coexist with zero persisted rows | `Staging: Create Version` replaced the current item, so the following insert no longer received `chunks`. Candidate validation checked the in-memory batch rather than persisted DB counts. | Explicitly restore the batch, insert through a CTE, load persisted evidence, compare exact document/chunk counts, and guard every activation update with DB count predicates. | `Restore Ingest Batch`, `Staging: Insert Chunks`, `Load Candidate Evidence`, `Validate Candidate`, `Activate Corpus (Atomic)` |
| `F-M6-ING-003` — PostgreSQL query-parameter type rejected | An array containing cross-node `$()` expressions was coerced to an unsupported value type by the PostgreSQL v2.6 node. | Parameter arrays now use current-item `$json` values only; the preceding node carries the required identity forward. | `Staging: Insert Chunks`, `Load Candidate Evidence` |
| `F-M6-ING-004` — rerun could provide no insert output | `ON CONFLICT DO NOTHING RETURNING id` returns no row when every chunk already exists. | The insert CTE always emits corpus/profile identity plus `inserted_chunk_count`, including zero. | `Staging: Insert Chunks` |

The active n8n workflow `5E9eQbknShf6iskV` was updated to the same runtime behavior. Temporary SQL patches, the debug workflow, and raw execution files were removed after extracting minimized evidence.

## Evidence

### Environment

- Shell / cwd: PowerShell; project root
- n8n: `n8nio/n8n:1.123.81`; runtime reports `1.123.81`; container healthy
- PostgreSQL: `pgvector/pgvector:pg16`; pgvector `0.8.6`; container healthy
- Python: `3.11.15`
- Provider binding: local Ollama through `host.docker.internal:11434`; embedding profile `ollama:embeddinggemma:300m-qat-q4_0:768`

### Commands and observed assertions

| AC / check | Command / target | Expected → observed | Result |
|---|---|---|---|
| `AC-001` live valid ingest | `docker exec rag-n8n-local sh -c "n8n execute --id=5E9eQbknShf6iskV --rawOutput >..."` | End at atomic activation; 26 documents; non-empty persisted candidate → last node `Activate Corpus (Atomic)`; 26 distinct sources; 297 chunks; every vector dimension 768; active pointer equals the generated corpus hash | `PASS` within live happy-path boundary |
| `AC-003` identical rerun | Same workflow command, second run | No duplicate row and same active identity → `inserted_chunk_count=0`; persisted rows remain 297 and distinct sources remain 26 | `PASS` within sequential rerun boundary |
| Finding-specific DB fail-closed guard | Diagnostic run before final correction | Failed insert must not activate → `Validate Candidate` emitted `candidate_validation_failed`; activation node was not executed | `PASS` for this injected parameter failure; not a substitute for all `AC-005` live faults |
| Persisted DB evidence | Read-only query as `rag_ingest` | Metadata equals physical rows → `document_count=26`, `chunk_count=297`, persisted `26/297`, dimensions `768..768`, status `active`, no failure reason | `PASS` |
| Compose configuration | `docker compose --file deploy/compose.yaml --project-name rag-local --env-file .env.test config --quiet` | Valid configuration with no rendered output → exit 0 | `PASS` |
| Workflow graph/static | PowerShell JSON/edge validator | Both exports parse; every source/target exists → workflow 01: 20 nodes; workflow 02: 28 nodes; total 48 | `PASS` |
| `AC-001`–`AC-005` regression | `python tests\harness\test_ingestion.py` | 19 tests, exit 0 → 19/19 | `PASS` — mock/contract level |
| `AC-011`–`AC-020` regression | `python tests\harness\test_qa_core.py` | 21 tests, exit 0 → 21/21; expected client-abort trace occurred in timeout case | `PASS` — mock/contract level |
| `AC-006`–`AC-010`, `AC-022`–`AC-024` regression | `python tests\harness\test_delivery_core.py` | 27 tests, exit 0 → 27/27; pre-existing fixture `ResourceWarning` remains non-failing | `PASS` — mock/contract level |
| `AC-025` runtime portability | Current Docker n8n inventory | Workflow 01 imported, rebound, and executes; workflow 02 and its two required credentials are not present in this n8n project | `NOT_VERIFIED` overall |

Active corpus identity: `sha256:61b7301108de25c111d815812e8695f150e4e958dbbd9c40dd03dfd1baa6d109`.

## Risk and limitations

- The live ingestion happy path and identical rerun are proven; live invalid-corpus, timeout, provider-auth/5xx, dimension-mismatch, concurrent-run, and database-failure scenarios were not rerun against this runtime. Existing 19/19 evidence for those families remains mock/contract-level only.
- Workflow 02 is not imported in the current Docker n8n project. The current credential inventory contains `ai-provider` and `postgres-rag-ingest`, but not `postgres-rag-runtime` or `telegram-demo-bot`.
- Live Telegram still requires an approved externally reachable HTTPS webhook target. Local loopback cannot prove Telegram Trigger E2E.
- No QA, Security, latency `15/15`, release, or deployment verdict is claimed.
- Raw n8n execution output contained corpus text and embeddings, so it was used only transiently and deleted after minimized assertions were recorded here.

## Status and gate

- Runtime finding result: `F-M6-ING-001` through `F-M6-ING-004` resolved and verified by implementer.
- Complete M6 / candidate status: `NOT_VERIFIED` because workflow 02, runtime/Telegram credentials, public webhook, and its integration path remain unavailable in the current Docker n8n project.
- Release/deploy approval: `NOT_AVAILABLE`.

## Next owner/action

Human provisions `postgres-rag-runtime` and `telegram-demo-bot` in this same Docker n8n project and supplies an approved HTTPS webhook target. Engineer may then import/rebind workflow 02 and perform the remaining M6 smoke verification. M7/M8 do not start automatically.
