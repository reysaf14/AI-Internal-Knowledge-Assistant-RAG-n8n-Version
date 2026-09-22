# M7 Engineer Runtime-Budget Remediation — 2026-09-20

## Objective and scope

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Role / executor:** Engineer
- **Candidate before fix:** `m6-local-gemma-bounded-2026-09-20-v4`
- **Candidate after fix:** `m6-local-gemma-bounded-2026-09-20-v5`
- **Verification boundary:** workflow 02 warm local-provider Telegram E2E and sanitized runtime telemetry
- **Included:** root-cause isolation, bounded output adjustment, failure-category correction, workflow reactivation, and three supported E2E checks
- **Excluded:** independent QA verdict, full `12 supported + 3 unsupported` matrix, Security, release, and cleanup

This report addresses QA finding `.ai/reports/qa/M7-independent-qa-warm-rerun-2026-09-20.md`. It is implementer evidence and does not replace the QA rerun.

## Finding and root cause

QA warm-up proved that the Ollama endpoints were reachable, but the first real Telegram item still returned the service-unavailable fallback at `4907 ms` ledger / `4941 ms` event time. The workflow uses a total business deadline of `5000 ms` with a `1000 ms` Telegram delivery reserve. The online guard subtracts elapsed workflow time and the reserve before the chat request. With `output_bound=500`, Gemma could consume the remaining generation budget after embedding, retrieval, and n8n overhead, causing the bounded path to fail closed.

The failure response also classified `ai_budget_exhausted` as generic `provider_or_runtime_failure`, which hid the actual budget signal from QA telemetry.

The controlled same-query comparison confirms the diagnosis: after reducing the generation bound, the previously failing supported item completed with a grounded response in `1974 ms` under the new candidate.

## Changes applied

1. **Runtime bound:** updated `rag.rag_settings.output_bound` from `500` to `192` and advanced the non-secret revision to `m6-local-gemma-bounded-2026-09-20-v5`.
2. **Failure classification:** updated `Build Service-Unavailable Response` in `workflows/02-telegram-grounded-qa.json` to classify `ai_budget_exhausted` as `ai_budget_exhausted` and timeout signals as `provider_timeout`, before the generic provider category.
3. **Activation:** re-imported workflow `02 — Telegram Grounded Q&A`, kept workflow ID `IAOqkQsNamEJarHF`, reactivated it, and restarted n8n. The workflow remained 34 nodes and active.

No credential, corpus, schema, embedding profile, Telegram route, or ingestion workflow was changed.

## Verification evidence

- **Date/time:** `2026-09-20`, approximately `16:41–16:43 Asia/Jakarta` (`09:41–09:43 UTC`)
- **Shell/cwd:** PowerShell; `C:\Freelance-Workspace\projects\active\AI Internal Knowledge Assistant (RAG) — n8n Version`
- **Runtime:** n8n `1.123.81`, PostgreSQL/pgvector, temporary HTTPS Telegram route, Ollama local provider
- **Static workflow check:** JSON parse `PASS`; 34 nodes; active `true`; budget classifier present `PASS`
- **Provider warm-up:** native embedding HTTP `200`, dimension `768`, `208 ms`; native chat HTTP `200`, completed, `406 ms`
- **Telemetry boundary:** only sanitized correlation/status/duration/error-category/config metadata was inspected

| Test | Expected | Observed | Status |
|---|---|---|---|
| QA item 1: Monday opening hours | Grounded answer with a valid source, no service-unavailable fallback, under 5000 ms | Grounded Telegram response citing `21_Kebijakan_Jadwal_Shift_Kerja.md`; v5 safe event `success`, `1974 ms`, empty error category | `PASS` |
| Supported expired-goods question | Grounded answer with a valid source, no service-unavailable fallback, under 5000 ms | Grounded Telegram response citing `08_SOP_Penanganan_Barang_Rusak_dan_Kadaluarsa.md`; v5 safe event `success`, `3838 ms`, empty error category | `PASS` |
| Supported returns/exchanges question | Grounded answer with a valid source, no service-unavailable fallback, under 5000 ms | Grounded Telegram response citing `11_FAQ_Kebijakan_Retur_dan_Tukar_Barang.md`; v5 safe event `success`, `3868 ms`, empty error category | `PASS` |

The first test is the same supported topic that failed under v4 after QA's independent warm-up. The v5 result is a scoped regression proof, not a full QA pass.

## Separate oracle/corpus conflict

QA also found that `evaluation/qa-dataset.csv` expects item 1 to say `08:00` and names `09_FAQ_Jam_Operasional_dan_Lokasi.md`, while the persisted corpus says `07.00–21.00` in both `09_FAQ_Jam_Operasional_dan_Lokasi.md` and `21_Kebijakan_Jadwal_Shift_Kerja.md`.

This is not changed by the runtime fix. The corpus-backed v5 answer is consistent with the current corpus, but the approved evaluation oracle is inconsistent. Human/Architect must reconcile that expected result before QA can score item 1 definitively. Engineer did not silently alter the evaluation oracle or approved expected result.

## Traceability and impact

| Requirement / AC | Affected implementation | Evidence | Result |
|---|---|---|---|
| `REQ-002 / AC-006` | Workflow 02 bounded Q&A and Telegram delivery | Three v5 Telegram responses delivered to the authorized sandbox | Scoped `PASS` |
| `REQ-003 / AC-011` | `Prepare Chat Completion Request`, `Chat Completion`, citation guard | Three supported responses were grounded; full semantic rubric not run | Scoped `PASS`; aggregate `NOT_VERIFIED` |
| `REQ-004 / AC-014` | `Validate Citation & Attach Sources` | Three responses named approved sources | Scoped `PASS`; `12/12` remains `NOT_VERIFIED` |
| `REQ-006 / AC-021` | Total budget guard and output bound | Three v5 durations were below 5000 ms | Scoped `PASS`; `15/15` remains `NOT_VERIFIED` |
| `AC-013 / AC-022` | Failure branch and budget classification | v4 failure remained fail-closed; v5 now exposes budget/timeout category when applicable | Implementer fix verified; full fault matrix open |

Workflow 01 ingestion and M0–M6 implementation evidence are unaffected by this online Q&A-only change. The candidate revision changed, so QA must rerun affected M7 cases against v5 rather than carry forward v4 evidence.

## Regression verification

The available deterministic harnesses were rerun from the project cwd after the patch:

| Command | Result | Exit code |
|---|---:|---:|
| `python tests/harness/test_ingestion.py` | `19/19` passed | `0` |
| `python tests/harness/test_qa_core.py` | `21/21` passed | `0` |
| `python tests/harness/test_delivery_core.py` | `27/27` passed | `0` |
| Total | `67/67` passed | `0` |

These harnesses verify deterministic contract logic and failure branches; they do not replace the required independent Telegram E2E matrix.

## Status and gate

- **Engineer verification:** `VERIFIED BY IMPLEMENTER — SCOPED FIX VERIFIED`
- **M7 aggregate:** `NOT_VERIFIED` until QA reruns item 1 and the remaining approved matrix against v5
- **Security:** `NOT_STARTED`
- **Release / Human quality gate:** unchanged and not approved

## QA handoff

1. Re-run item 1 against `m6-local-gemma-bounded-2026-09-20-v5` after the documented synthetic warm-up.
2. Use the reconciled corpus/oracle expectation; do not count the item as semantically passed until Human/Architect resolves the `08:00` versus `07.00–21.00` conflict.
3. If item 1 passes the reconciled source/content check, continue the remaining 14 items sequentially and record individual latency.
4. Retest the provider/budget failure cases and confirm that telemetry distinguishes `ai_budget_exhausted` or `provider_timeout` from generic provider failure.

## Next owner and required Human input

- **Next owner:** QA for the v5 rerun; Human/Architect for the evaluation oracle decision.
- **Human input required:** confirm whether the approved answer for item 1 should follow the persisted corpus (`07.00–21.00`, source `09`/`21`) or whether the corpus itself is intended to be changed. No corpus/oracle edit was made by Engineer.
