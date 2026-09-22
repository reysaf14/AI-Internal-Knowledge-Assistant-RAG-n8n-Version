# M7 Independent QA Primary Telegram Run — 2026-09-20

## Verdict

`FAIL` for the current-candidate Telegram E2E path. The first authorized synthetic message was visibly sent by Telegram Web, but the candidate produced no Telegram response, no `rag.telegram_updates` receipt, and no new `rag.safe_events` record after approximately ten seconds. The remaining 14 items were intentionally not sent after this blocking failure.

This is an independent QA result. Engineer self-test reports and the prior QA rerun remain separate evidence classes.

## Scope and authorization

- Scope: current frozen M7 candidate, real Telegram sandbox, one sequential primary-run attempt.
- Human approval: `.ai/reports/build/M7-human-approval-qa-handoff-2026-09-20.md`.
- Dataset: approved synthetic `12 supported + 3 unsupported` working copy at `evaluation/qa-dataset.csv`.
- Target: the authorized Telegram sandbox target from the handoff; identifier intentionally omitted from this report.
- Data handling: synthetic test input only; no credentials, payloads, chat identifiers, answer transcripts, or restricted records persisted here.

## Frozen candidate checked before execution

| Setting | Observed value |
|---|---|
| `config_revision` | `m6-local-gemma-bounded-2026-09-20` |
| Chat model | `gemma4:e2b-it-qat` |
| Embedding model | `embeddinggemma:300m-qat-q4_0` |
| Embedding dimension | `768` |
| Online AI timeout | `3000 ms` |
| Offline ingestion timeout | `120000 ms` |
| Workflow 02 | `IAOqkQsNamEJarHF` (active in prior independent rerun) |

The pre-run PostgreSQL settings query returned the frozen candidate revision and timeout values. No QA change was made to the runtime, workflow, credentials, or corpus.

## Execution evidence

### Procedure

1. Telegram Web was opened and manually confirmed logged in; no login, OTP, or credential automation was performed.
2. The authorized sandbox bot chat was opened.
3. Synthetic dataset item 1 was entered and submitted once through the Telegram Web composer.
4. The UI showed the outgoing message in the chat at `13:08:35` local time with a sent state.
5. The UI was observed for approximately `2.5 s`, then an additional `8 s`; no bot response appeared.
6. The primary run was stopped to avoid generating 14 uncorrelated messages after the first blocking failure.

### Sanitized telemetry checks

Baseline before sending:

```text
current candidate telegram_updates = 0
latest current-candidate claimed_at = none
```

After the wait:

```text
current candidate telegram_updates = 0
safe_events created in the last 15 minutes = 0
all historical telegram_updates = 31
latest historical config_revision = m6-local-ollama-2026-09-19
```

The database checks selected only counts, status/duration fields, revision labels, and timestamps. Update IDs, chat IDs, message text, answers, and payloads were not selected.

## Primary-run result

| Item | Input submission | Candidate receipt | Telegram response | Source/answer rubric | `<5000 ms` latency | Result |
|---:|---|---|---|---|---|---|
| 1 | Sent once; UI-confirmed | No receipt observed | No response observed | Not assessable | Not assessable | `FAIL` |
| 2–15 | Not run | Not run | Not run | Not assessable | Not assessable | `NOT_RUN` |

The single observed failure is sufficient to fail the current primary E2E path. It is not evidence that the remaining dataset items would pass.

## Gate impact

- Valid Telegram E2E: `FAIL`.
- Current 15-item semantic/source/latency run: `NOT_COMPLETED`; blocked by the first E2E failure.
- Delivery latency acceptance: `NOT_VERIFIED`; no candidate delivery timestamp exists for item 1.
- Live provider/auth/5xx/timeout/database/duplicate/concurrency matrix: `NOT_VERIFIED`; not attempted after the blocking failure and no fault injection was authorized.
- Security, clean-instance portability, release, and cleanup gates: unchanged and still `NOT_VERIFIED`/`NOT_STARTED`.

## QA conclusion

The current candidate is not proven usable through its authorized Telegram path. The observed failure is upstream of semantic scoring: the submitted message did not produce a candidate workflow receipt or response. Do not treat the prior 67/67 mock regression, live ingestion, or invalid-secret result as a substitute for this failed functional E2E gate.

## Required next action

Engineer should inspect Telegram webhook registration/routing and the active workflow trigger using sanitized operational evidence. QA should rerun item 1 alone first; only after a receipt and response are observed should the 12+3 sequential run resume. No release, Security sign-off, or cleanup decision is authorized by this report.

## Integrity and change boundary

- QA did not modify application code, workflow exports, credentials, Docker configuration, database rows, or corpus data.
- This report is a new QA artifact; prior reports remain immutable evidence.
