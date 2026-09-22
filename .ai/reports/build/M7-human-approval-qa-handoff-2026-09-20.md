# M7 Human Approval — QA Execution Handoff

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Role:** Engineer handoff to independent QA
- **Date:** 2026-09-20 (`Asia/Jakarta`)
- **Status:** `APPROVED FOR QA EXECUTION`; M7 verdict remains `NOT_VERIFIED`
- **Related QA report:** `.ai/reports/qa/M7-independent-qa-rerun-2026-09-20.md`
- **Related remediation:** `.ai/reports/build/M7-engineer-remediation-2026-09-20.md`

## Human confirmation recorded

The Human confirmed in the current task that:

1. The synthetic evaluation set with `12 supported + 3 unsupported` items is approved for the semantic QA run.
2. The exact Telegram sandbox target is authorized for testing: `chat_id=5578891856`.
3. QA may run the current candidate against that sandbox target.

This is authorization to execute the QA test only. It is not a release approval, production authorization, Security approval, or cleanup authorization.

## Frozen QA candidate

| Parameter | Frozen value |
|---|---|
| `config_revision` | `m6-local-gemma-bounded-2026-09-20` |
| `chat_model` | `gemma4:e2b-it-qat` |
| `embedding_model` | `embeddinggemma:300m-qat-q4_0` |
| `embedding_dimension` | `768` |
| `ai_timeout_max` | `3000ms` |
| `ingest_timeout_max` | `120000ms` (offline ingestion only) |
| `business_deadline_ms` | `5000ms` |
| `delivery_reserve_ms` | `1000ms` |
| `active_corpus_version` | `sha256:61b7301108de25c111d815812e8695f150e4e958dbbd9c40dd03dfd1baa6d109` |
| Workflow 01 | `5E9eQbknShf6iskV` |
| Workflow 02 | `IAOqkQsNamEJarHF` |

The configuration must remain unchanged for the primary 15-item run. Any change requires a new run label and frozen configuration record.

## QA execution requested

QA may now execute the following against the authorized sandbox:

1. Sequential 15-item run: 12 supported questions and 3 unsupported questions.
2. Content and source rubric: supported answers `12/12`, source citations `12/12`, unsupported abstention `3/3`.
3. End-to-end latency: each completed item from workflow receive to Telegram send success under `5000ms`.
4. Live invalid-input, provider/auth/5xx, timeout, database, duplicate, and concurrency cases.
5. Sanitized evidence only: no credentials, raw Telegram payloads, or unnecessary message content in the report.

The existing engineer and mock-regression evidence must not be promoted to independent QA evidence. The previous QA verdict remains `NOT_VERIFIED` until this run produces the required results.

## Explicitly out of this authorization

- Production or demo-VPS testing.
- Credential rotation or disclosure.
- Workflow/database cleanup, revocation, or destructive teardown.
- Security sign-off.
- Human release decision.

## Handoff result

The Human approval blocker for the 12+3 dataset and Telegram sandbox target is cleared for QA execution. Remaining gates are owned by QA and Security; M8 human release/cleanup decisions remain open.
