# M7 v9 Diagnostic Persistence Independent QA Rerun

Date: `2026-09-20`  
Scope: frozen synthetic matrix items `1–15`, active Telegram sandbox, workflow revision `m7-support-gate-trace-2026-09-20-v9`.

## Result

- Final matrix attempts: `15/15` delivered.
- Final response latency: `1,158–2,724 ms`; `15/15` under the `<5,000 ms` budget.
- One transient first attempt for item 1 returned the service-unavailable fallback at `5,013 ms` with `provider_or_runtime_failure`; a controlled retry answered in `2,015 ms`.
- Raw content/abstention: `9/15` pass; supported `6/12`; unsupported `3/3`.
- Accepted only as local Gemma proof-of-wiring: items `4,5,6,11` (partial but source-grounded).
- Still open: items `9,10` (supported questions abstained and the failing stage is not proven).

## Diagnostic persistence gate

The v9 remediation did not pass its acceptance gate. Before the run the database had `104` safe events and `0` diagnostic rows. After the final matrix plus the item-1 retry it had `120` safe events, including `16` v9 `delivery` rows, but `0` rows with `stage='grounding_diagnostic'`. This is true for the successful answered path and the abstained paths. The active workflow export contains the diagnostic node and plain `INSERT`, so the remaining defect is live execution/persistence, not static marker presence.

## Deterministic regression

The independent rerun passed `19/19` ingestion, `21/21` QA-core, and `27/27` delivery tests (`67/67`). These are mock/contract evidence and do not override live semantic or telemetry failures.

## Verdict

`FAIL — NOT RELEASE READY` for the approved M7 semantic/observability gate. The scoped local-provider proof remains `PASS WITH LIMITATIONS` for the paths that answered and for the accepted Gemma limitations, but items `9/10` and the missing diagnostic persistence remain engineering blockers.
