# M7 Independent QA v5 Item-1 Retry Amendment — 2026-09-20

## Purpose

This amendment records the Human clarification received after `.ai/reports/qa/M7-independent-qa-v5-item1-retry-2026-09-20.md`: the first attempt occurred before the n8n page in Microsoft Edge was refreshed; the second retry occurred after the refresh.

The prior report remains immutable historical evidence. This amendment corrects the comparability classification; it does not delete the first observation.

## Corrected classification

| Attempt | Page/runtime context | Observed result | QA classification |
|---|---|---|---|
| A | n8n Edge page had not yet been refreshed after the Engineer remediation | Service-unavailable fallback; `provider_or_runtime_failure`; `4940 ms` ledger / `4987 ms` safe event | `INVALID_PRECONDITION`; excluded from current-candidate pass/fail scoring |
| B | After Human refreshed the n8n Edge page and QA retried after warm-up | Grounded corpus-backed response; source `21_Kebijakan_Jadwal_Shift_Kerja.md`; no error category; `1911 ms` ledger / `1965 ms` safe event | `PASS` for one valid post-refresh item-1 observation |

The first attempt is retained as operational history but is not treated as a valid v5 comparison because the stated refresh precondition was absent. The valid retry demonstrates one successful post-refresh item-1 path; it does not establish repeatability or complete M7.

## Remaining gates

- Valid item 1 post-refresh: `PASS` for one observation.
- Full 12+3 semantic/source/abstention matrix: `NOT_VERIFIED` and not run.
- Full 15-item latency coverage: `NOT_VERIFIED` and not run.
- Item-1 oracle conflict: still open. The dataset expects `08:00`/source `09`, while persisted corpus documents `09` and `21` state `07.00–21.00`.
- Live provider/budget/timeout/database/duplicate/concurrency matrix: `NOT_VERIFIED`.
- Security, clean-instance import/rebind, release, and cleanup: `NOT_VERIFIED`/`NOT_STARTED`.

## QA conclusion

After excluding the pre-refresh attempt, the corrected evidence is one valid post-refresh pass for item 1. M7 remains `NOT_VERIFIED` because the approved oracle is unresolved and the required remaining matrix and independent fault/security gates are incomplete.

## Required next action

Human/Architect must reconcile the item-1 dataset oracle with the persisted corpus. After that decision, QA can continue the approved 12+3 sequence from item 2 using the refreshed/current v5 runtime, while recording each item and latency independently.
