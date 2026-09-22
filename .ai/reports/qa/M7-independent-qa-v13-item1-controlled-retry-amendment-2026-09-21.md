# M7 QA v13 Item 1 Controlled Retry Amendment

Date: 2026-09-21  
Timezone: Asia/Jakarta  
Executor: QA  
Candidate: Engineer v12 / runtime v8  
Scope: controlled single-item retry after the v13 full matrix  
Result: RETRY PASS; REPEATABILITY FAIL / NOT_VERIFIED

## Purpose

This amendment tests whether the v13 item-1 failure was simply a provider warm-up condition. It is an additional controlled retry and does not replace or erase the original full-matrix result.

The prior full-matrix attempt returned the service-unavailable fallback with `chat_completion_failure`, delivery event 332 at 4,985 ms, and no grounding diagnostic. No claim is made that the prior attempt was cold; the runtime warm/cold state was not independently instrumented for this test.

## Controlled retry evidence

| Evidence | Observed |
|---|---|
| Question | Jam berapa toko buka hari Senin? |
| Telegram UI answer | Senin buka pukul 07.00–21.00. Sumber: 09_FAQ_Jam_Operasional_dan_Lokasi.md |
| Telegram update | ID 240, status `delivered`, empty error category |
| Grounding diagnostic | Safe event 361, `success`, 3,986 ms; model text received; validator answered |
| Delivery event | Safe event 362, `success`, 4,940 ms; empty error category |
| Runtime | cloud-chat-local-embedding-2026-09-21-v8 |
| Persisted delta | +1 Telegram update; +2 safe events |

## Interpretation

The retry passes both semantic and operational checks for item 1. However, the adjacent sequence is divergent:

- Attempt A: fallback, `chat_completion_failure`, no grounding diagnostic, delivery 4,985 ms.
- Attempt B: grounded answer with source 09, diagnostic 3,986 ms, delivery 4,940 ms.

Therefore:

- item-1 retry: PASS;
- item-1 repeatability: FAIL / NOT_VERIFIED;
- “the first failure was only because the model was not warm”: NOT_PROVEN.

The persisted evidence establishes intermittent behavior in the current chat-completion/runtime path. It does not distinguish cold-start, transient provider failure, budget/timing sensitivity, or another runtime condition. More instrumentation or a controlled warm/cold experiment is required before assigning the root cause.

## Verdict impact

The original v13 full matrix remains unchanged:

- content 14/15;
- supported 11/12;
- unsupported 3/3;
- delivery 15/15;
- latency 15/15 under 5 seconds;
- diagnostic persistence 14/15;
- deterministic harness 67/67;
- overall M7: FAIL / NOT_VERIFIED.

This retry is evidence that the v8 path can pass item 1, not evidence of release readiness or repeatable acceptance.

## Handoff

Engineer should investigate the intermittent `chat_completion_failure` and expose enough sanitized stage/timing evidence to distinguish warm-state, provider, and budget behavior. QA should rerun the complete 15-item matrix after that investigation/fix; the controlled retry must remain linked as a separate attempt, not substituted for the failed full-matrix item.

Artifacts:

- `evaluation/run_v13-item1-controlled-retry-2026-09-21.jsonl`
- `evaluation/run_v13-item1-controlled-retry-2026-09-21_config.json`
- `evaluation/run_v13-item1-controlled-retry-2026-09-21_summary.md`
- `.ai/reports/qa/M7-independent-qa-v13-engineer-v12-cash-closing-fix-full-matrix-2026-09-21.md`

