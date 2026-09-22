# M7 Independent QA Recovery Rerun — 2026-09-20

## Verdict

`FAIL` for the recovered current-candidate Telegram Q&A path. The webhook recovery was independently observed to restore receipt and Telegram response delivery, but the first clean post-recovery synthetic item returned the service-unavailable fallback and produced a sanitized `provider_or_runtime_failure`. The remaining 14 items were not sent because the handoff requires item 1 to pass before continuing.

This report is independent QA evidence; the Engineer recovery report is treated as a claim to verify, not as a pass.

## Scope and authorization

- Candidate: `m6-local-gemma-bounded-2026-09-20`.
- Scope: one clean post-recovery run of approved dataset item 1, followed by continuation only if item 1 passed.
- Dataset authorization: synthetic `12 supported + 3 unsupported` from `evaluation/qa-dataset.csv`.
- Telegram target: the authorized sandbox target from the Human handoff; identifier omitted here.
- No credential, workflow export, database row, runtime setting, corpus file, or Docker configuration was changed by QA.

## Preflight independently observed

| Check | Result |
|---|---|
| n8n container | `n8nio/n8n:1.123.81`, healthy |
| PostgreSQL container | `pgvector/pgvector:pg16`, healthy |
| Temporary tunnel | running |
| Webhook gateway | running |
| n8n `/healthz` | `HTTP 200`, `status=ok` |
| n8n readiness | `HTTP 200`, `status=ok` |
| Config revision | `m6-local-gemma-bounded-2026-09-20` |
| Online AI timeout | `3000 ms` |
| Ingestion timeout | `120000 ms` |
| Active corpus | hash prefix `sha256:61b730...6d109` |

The Telegram Web session was already authenticated. Native Telegram Desktop was not exposed to the computer-use surface, so the same authenticated Telegram account was used through Telegram Web; this is functionally the same sandbox account and target.

## Execution evidence

### Baseline

Immediately before the clean send, the sanitized ledger query returned:

```text
current-candidate rows = 1
latest current-candidate status = delivered
latest prior current-candidate claimed_at = 06:22:30.083 UTC
```

The prior row was the delayed processing of the earlier pre-recovery message and was not counted as the clean rerun.

### Item 1

1. The first approved synthetic dataset item was submitted once through the authenticated Telegram sandbox chat.
2. Telegram Web showed the outgoing message and then a bot response.
3. The bot response was the service-unavailable fallback, not a grounded answer and not an abstention response for an unsupported question.
4. The sanitized PostgreSQL ledger showed a new `delivered` row.
5. The sanitized workflow event showed:

```text
workflow=02-telegram-grounded-qa
stage=delivery
status=success
duration_ms=4027
error_category=provider_or_runtime_failure
```

The ledger-derived duration from claim to delivery success was `3980 ms`, within the nominal `<5000 ms` budget, but latency alone does not pass the Q&A acceptance when the answer is a runtime failure fallback.

## Result matrix

| Item | Telegram receipt | Delivery latency | Grounded answer/source | Result |
|---:|---|---:|---|---|
| 1 | Observed; `delivered` | `3980 ms` ledger / `4027 ms` event | Failed; provider/runtime fallback; source not assessable | `FAIL` |
| 2–15 | Not run | Not run | Not assessable | `NOT_RUN` |

## Gate impact

- Webhook/tunnel receipt path after recovery: `PASS` for this one observed receipt.
- Telegram delivery timing for item 1: `PASS` against the nominal 5-second budget, with a provider/runtime failure category.
- Grounded supported-answer acceptance: `FAIL`.
- 12+3 semantic/source/abstention run: `NOT_COMPLETED`.
- Provider/auth/5xx/timeout/database/duplicate/concurrency matrix: `NOT_VERIFIED`.
- Security, clean-instance portability, release, and cleanup: unchanged and still `NOT_VERIFIED`/`NOT_STARTED`.

## QA conclusion

The recovery fixed the previously observed missing webhook receipt, but it did not establish a usable end-to-end Q&A path. The system now receives the test and sends a response, yet the response is a provider/runtime failure fallback for a supported item. The candidate is not proven usable and is not release-ready.

Do not treat the Engineer's recovery validation, the previous 67/67 harness result, live ingestion, or the single sub-five-second delivery duration as a semantic QA pass.

## Required next action

Engineer should investigate the provider/runtime failure using sanitized execution evidence, including provider reachability from n8n, model binding, and failure-path classification. QA should rerun item 1 alone after remediation; only a grounded answer with the expected source can unlock the remaining 14 sequential items.

## Integrity and change boundary

- QA did not modify application code, workflow exports, credentials, runtime settings, Docker configuration, database data, or corpus data.
- No answer transcript, message payload, chat identifier, credential value, or restricted record was persisted in this report.
