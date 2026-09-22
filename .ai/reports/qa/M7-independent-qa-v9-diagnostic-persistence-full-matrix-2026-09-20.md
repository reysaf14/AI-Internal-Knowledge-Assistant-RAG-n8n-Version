# M7 Independent QA — v9 Diagnostic Persistence Full Matrix

Date: `2026-09-20`  
QA mode: independent rerun against the active local deployment; Engineer report was treated as a hypothesis, not as execution evidence.  
Scope: frozen synthetic dataset items `1–15`, Telegram sandbox, active n8n workflow `IAOqkQsNamEJarHF`.

## Executive verdict

`FAIL — NOT RELEASE READY`.

The v9 candidate delivered the final 15-case matrix and met the final latency budget, but the remediation acceptance condition failed in live execution: `0` persisted `grounding_diagnostic` rows were written for `16` v9 safe events. The successful answered path and the abstained paths therefore remain without the promised stage-level evidence. Items `9` and `10` still abstained, and their failing stage cannot be proven.

The local Gemma limitation is accepted only where the answer was source-grounded but incomplete (`4,5,6,11`). That scoped allowance does not waive the telemetry persistence blocker or allow unsupported classification of items `9` and `10`.

## Preconditions and evidence freeze

| Check | Observed evidence | Result |
|---|---|---|
| n8n | container `rag-n8n-local`, healthy, version `1.123.81` | PASS |
| PostgreSQL | container `rag-postgres-local`, healthy, pgvector/PostgreSQL 16 | PASS |
| n8n health | `/healthz` and `/healthz/readiness` returned `status=ok` | PASS |
| Provider preflight | embedding HTTP `200`; chat HTTP `200` from inside n8n container | PASS, timing exploratory |
| Ollama models | `gemma4:e2b-it-qat` and `embeddinggemma:300m-qat-q4_0` loaded on GPU during retry | OBSERVED |
| Workflow | active workflow ID `IAOqkQsNamEJarHF`, 37 nodes, revision v9 | PASS static/live metadata |
| Dataset | SHA-256 `6B4587A7DCB7EB04630801D7073F7424ED8274D7245746A3C82CD658DFF60614` | FROZEN |
| Workflow export | SHA-256 `18E4D163F2D410A31F2135B53BE3A93C45E137E0924A0234755D11235A31ECC0` | FROZEN |

Persisted runtime configuration at execution time:

```text
revision=m7-support-gate-trace-2026-09-20-v9
chat_model=gemma4:e2b-it-qat
embedding_model=embeddinggemma:300m-qat-q4_0
embedding_dimension=768
retrieval_limit=5
minimum_similarity=0.25
ai_timeout_max=4000ms
context_bound=3000
output_bound=192
active_corpus=sha256:61b7301108de25c111d815812e8695f150e4e958dbbd9c40dd03dfd1baa6d109
```

## Live matrix evidence

The first item-1 attempt was independently sent and delivered the service-unavailable fallback at `5,013 ms`, with persisted `provider_or_runtime_failure`. A retry of the same synthetic question then produced the grounded answer at `2,015 ms`; the retry is the valid final item-1 result below. Items `2–15` were sent sequentially after that retry.

| Item | Final delivery | Event ms | Observed class | Source / boundary | Raw rubric | Scoped disposition |
|---:|---|---:|---|---|---|---|
| 1 | delivered | 2,015 | answered, 07.00–21.00 | active corpus source 09; dataset label remains source 21 | PASS | PASS |
| 2 | delivered | 2,143 | answered, 10 motor / 5 mobil / gratis | source 09 | PASS | PASS |
| 3 | delivered | 2,724 | answered | source 11 | PASS | PASS |
| 4 | delivered | 2,473 | answered, incomplete opening SOP | source 01 | FAIL | accepted local Gemma limitation |
| 5 | delivered | 2,692 | answered, incomplete cash SOP | source 03 | FAIL | accepted local Gemma limitation |
| 6 | delivered | 2,200 | answered, incomplete closing SOP | source 02 | FAIL | accepted local Gemma limitation |
| 7 | delivered | 2,281 | answered | source 16 | PASS | PASS |
| 8 | delivered | 2,578 | answered | source 18 | PASS | PASS |
| 9 | delivered | 1,868 | deterministic abstention | no source observed | FAIL | OPEN — root cause not verified |
| 10 | delivered | 2,015 | deterministic abstention | no source observed | FAIL | OPEN — root cause not verified |
| 11 | delivered | 2,486 | answered, incomplete K3/APAR detail | source 25 | FAIL | accepted local Gemma limitation |
| 12 | delivered | 2,183 | answered | source 09 | PASS | PASS |
| 13 | delivered | 1,981 | exact unsupported abstention | unsupported boundary | PASS | PASS |
| 14 | delivered | 1,685 | exact unsupported abstention | unsupported boundary | PASS | PASS |
| 15 | delivered | 1,158 | exact unsupported abstention | unsupported boundary | PASS | PASS |

Aggregates for the final matrix: delivery `15/15`, final latency `<5s` `15/15`, raw content/abstention `9/15`, supported `6/12`, unsupported `3/3`. The additional first item-1 attempt is retained as a reliability observation and is not silently counted as the final matrix attempt.

## Diagnostic persistence acceptance test

The remediation report required one diagnostic row for a successful answer and one for an abstention. The persisted database evidence was:

| Persisted metric | Before run | After run |
|---|---:|---:|
| `rag.telegram_updates` | 112 | 128 |
| `rag.safe_events` | 104 | 120 |
| v9 `delivery` rows | 0 | 16 |
| v9 `grounding_diagnostic` rows | 0 | 0 |

The 16 v9 delivery rows comprise the first failed item-1 attempt, the successful retry, and the final items `2–15`. No `grounding_diagnostic` row was present for the successful item-1 retry, items `2–8`, item `9`, or items `10–15`.

The active export does contain the expected static node and query:

- `Prepare Grounding Diagnostic`
- `Record Grounding Diagnostic`
- `Restore Grounding Diagnostic Context`
- plain `INSERT INTO rag.safe_events (...)` with stage `grounding_diagnostic`
- no `RETURNING id` in that diagnostic query

Static presence is not live persistence. The node is configured as non-blocking (`onError=continueRegularOutput`), so a runtime/query failure can be hidden while Telegram delivery still succeeds. The current persisted evidence proves that this path is not writing rows, but does not yet identify whether the node is skipped or the insert errors.

## Deterministic regression

Independent rerun from the project checkout:

| Suite | Result |
|---|---:|
| `python tests/harness/test_ingestion.py` | `19/19` |
| `python tests/harness/test_qa_core.py` | `21/21` |
| `python tests/harness/test_delivery_core.py` | `27/27` |
| Total | `67/67` |

These tests use deterministic/mock providers and are contract evidence only. They do not override live Telegram semantic results or the missing v9 diagnostic rows.

## Findings for Engineer

1. **P0 / M7 blocker — diagnostic persistence still fails live.** The remediation changed the SQL text and reactivated v9, but live `grounding_diagnostic` count remains `0` after both answered and abstained cases. Make the write failure observable during QA and verify the actual active execution path. Do not rely on static workflow markers.
2. **P1 — items 9 and 10 remain unresolved.** Both supported policy questions abstain. Without diagnostic rows, retrieval, evidence filtering, prompt assembly, model output, and citation validation cannot be separated. Fix persistence first, then rerun items `9,10,15` and the full matrix.
3. **P1 — transient provider/runtime instability remains observable.** Identical item 1 first returned `provider_or_runtime_failure` at `5,013 ms`, then succeeded at `2,015 ms`. Investigate repeatability and preserve sanitized timing/error evidence; do not treat the successful retry as proof of deterministic reliability.
4. **P2 — local Gemma limitations remain scoped, not release acceptance.** Items `4,5,6,11` are source-grounded but incomplete. The user-approved local-model allowance can keep them out of the immediate blocker set, but the approved raw semantic rubric remains `FAIL`.

## Required next gate

Engineer must produce persisted diagnostic rows for at least one successful answer and one abstention, with sanitized metadata, then QA must rerun focused items `9,10,15` and the complete `1–15` matrix. Until that evidence exists, M7 remains `FAIL / NOT_VERIFIED` and the release candidate is unavailable.

Artifacts:

- [Sanitized per-item results](../../../evaluation/run_v9-diagnostic-persistence-2026-09-20.jsonl)
- [Frozen run configuration](../../../evaluation/run_v9-diagnostic-persistence-2026-09-20_config.json)
- [Run summary](../../../evaluation/run_v9-diagnostic-persistence-2026-09-20_summary.md)
- [Latest remediation report](../../build/M7-diagnostic-persistence-remediation-2026-09-20.md)
