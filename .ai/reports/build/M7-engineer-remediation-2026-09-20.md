# M7 QA Finding Remediation — Engineer Handoff

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Role:** Engineer
- **Date:** 2026-09-20 (`Asia/Jakarta`)
- **Status:** `READY FOR QA RERUN`; M7 remains `NOT_VERIFIED`
- **Source finding:** `.ai/reports/qa/M7-independent-qa-2026-09-20.md`

## Remediations applied

| QA finding | Remediation | Evidence |
|---|---|---|
| AI timeout was `120000ms` and passed directly to both HTTP nodes | Runtime revision changed to `m6-local-gemma-bounded-2026-09-20`; `ai_timeout_max=3000ms`. Workflow 02 now sets a fixed `business_deadline_ms=5000`, reserves `1000ms` for Telegram delivery, computes the remaining budget before embedding/chat, and routes exhausted budget to the sanitized unavailable response. | Live `rag.rag_settings`; `workflows/02-telegram-grounded-qa.json`; live workflow record `IAOqkQsNamEJarHF` |
| Bounded online timeout could regress the 297-chunk ingestion batch | Added `rag_settings.ingest_timeout_max=120000ms`; workflow 01 validates and uses this offline batch budget while workflow 02 alone uses the bounded online budget. Credential IDs were retained on all workflow 01 nodes during the live sync. | `deploy/postgres-init/01-init.sh`; `deploy/postgres-init/02-rag-schema-alignment.sql`; `workflows/01-corpus-ingestion.json`; live idempotent rerun |
| Current Gemma candidate was not frozen for rerun | Candidate metadata is now explicit and consistent: `gemma4:e2b-it-qat`, `embeddinggemma:300m-qat-q4_0`, dimension `768`, active corpus `sha256:61b730...6d109`, revision `m6-local-gemma-bounded-2026-09-20`. | Read-only runtime query and live workflow metadata |
| M3 timeout test emitted client-abort traceback | Test-only provider mock now treats expected broken/aborted client sockets as an injected timeout outcome. | `tests/mocks/ai-provider/provider_mock.py` |
| M4 emitted fixture `ResourceWarning` | Fixture loader now closes the JSONL file with a context manager. | `tests/harness/test_delivery_core.py` |
| Temporary classifier nodes remained in the debugging history | Six classifier nodes remain removed; failure paths converge directly on the controlled service-unavailable response. | Current workflow export: 34 nodes; no `Classify*` nodes |

## Verification performed by Engineer

- `python tests/harness/test_ingestion.py` → `19/19`, exit `0`
- `python tests/harness/test_qa_core.py` → `21/21`, exit `0`
- `python tests/harness/test_delivery_core.py` → `27/27`, exit `0`
- Total regression: `67/67`; rerun output contained no prior client-abort traceback or fixture `ResourceWarning`.
- n8n `1.123.81` restarted healthy; `/healthz` returned `{"status":"ok"}` and activation log showed workflow 02 active without a credential-ID error.
- Live database confirmed workflow 02 active, bounded timeout/deadline guard present, and old classifier node absent.
- Live workflow 01 rerun reached `Activate Corpus (Atomic)`, preserved the same corpus identity, validated `26` documents / `297` persisted chunks at dimension `768`, and inserted `0` duplicate chunks.

## Remaining M7 gates

This remediation does not promote QA evidence. The following remain `NOT_VERIFIED` and require QA/Human/Security ownership:

1. Current-candidate Telegram E2E and the approved sequential 15-item semantic/latency run.
2. Live invalid-input, provider, database, timeout, and concurrency fault matrix.
3. Human semantic approval/freeze of the 12+3 dataset and source key set.
4. Clean-instance import/rebind review.
5. Independent Security review and M8 cleanup/release decisions.

The bounded timeout is a control and a rerun prerequisite; it is not evidence that `15/15` responses are below `5,000ms`.
