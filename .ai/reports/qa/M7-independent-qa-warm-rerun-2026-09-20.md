# M7 Independent QA Warm-Provider Rerun — 2026-09-20

## Verdict

`FAIL` for the current warm-provider Telegram Q&A path. QA independently warmed the local provider from inside the n8n container and verified successful native provider responses, but the first approved Telegram item still returned the service-unavailable fallback. The current-candidate ledger classified the delivery as `provider_or_runtime_failure`. The remaining 14 items were not sent.

The Engineer warm-session report is treated as scoped implementer evidence, not as independent QA evidence.

## Scope and candidate

- Candidate: `m6-local-gemma-bounded-2026-09-20-v4`.
- Chat model: `gemma4:e2b-it-qat`.
- Embedding model: `embeddinggemma:300m-qat-q4_0`.
- Embedding dimension: `768`.
- Online timeout: `4000 ms`.
- Business deadline: `5000 ms`.
- Telegram reserve: `1000 ms`.
- Active corpus hash prefix: `sha256:61b730...6d109`.
- Approved dataset: synthetic `12 supported + 3 unsupported`.
- Target: authorized Telegram sandbox; identifier omitted.

No credential, workflow, runtime setting, database data, corpus file, or application source was changed by QA.

## Independent preflight

| Check | Result |
|---|---|
| n8n | `n8nio/n8n:1.123.81`, healthy |
| PostgreSQL | `pgvector/pgvector:pg16`, healthy |
| Temporary tunnel | running |
| Webhook gateway | running |
| n8n health/readiness | both HTTP 200 |
| Runtime revision | `m6-local-gemma-bounded-2026-09-20-v4` |
| Baseline current-candidate ledger rows | `9`, latest status `delivered` |

Telegram Web was already authenticated and used for the authorized sandbox conversation. Native Telegram Desktop was not exposed to the computer-use surface in this environment; the browser session represented the same logged-in account.

## Independent warm-up

Immediately before the Telegram send, QA ran synthetic, non-user, non-corpus requests from inside `rag-n8n-local` to the configured native Ollama endpoints with `keep_alive=10m`:

```text
embed_rc=0|bytes=9672|elapsed_ms=3
chat_rc=0|bytes=340|elapsed_ms=26
```

Only return code, response size, and duration were retained; generated content was not persisted. This proves provider endpoint reachability at warm-up time, not workflow-level Q&A success.

## Independent item 1 run

1. QA submitted the first approved synthetic item once after the warm-up.
2. Telegram showed the outgoing message and a bot response.
3. The response was the service-unavailable fallback, not a grounded answer and not the approved unsupported abstention response.
4. The current-candidate ledger received one new row with status `delivered`.
5. Sanitized telemetry for the new row was:

```text
telegram_updates: status=delivered|error_category=provider_or_runtime_failure|duration_ms=4907
safe_events: workflow=02-telegram-grounded-qa|stage=delivery|status=success|duration_ms=4941|error_category=provider_or_runtime_failure
```

The duration is nominally below the 5-second budget, but a delivery-time budget pass cannot compensate for a provider/runtime failure and missing grounded answer.

## Separate oracle/corpus integrity finding

The approved dataset oracle for item 1 expects an `08:00` answer and source `09_FAQ_Jam_Operasional_dan_Lokasi.md`. The persisted corpus documents `09_FAQ_Jam_Operasional_dan_Lokasi.md` and `21_Kebijakan_Jadwal_Shift_Kerja.md` both state `07.00–21.00`. The Engineer history response cited source `21` and aligned with the corpus rather than the dataset oracle.

This is an unresolved evaluation-oracle conflict, separate from the observed provider/runtime failure. QA does not silently rewrite the approved oracle during this run. The dataset/corpus conflict must be reconciled by the Human/Architect before final semantic scoring.

## Result matrix

| Item | Warm-up before send | Telegram receipt | Grounded answer/source | Latency | Result |
|---:|---|---|---|---:|---|
| 1 | Independently passed | `delivered` | Failed; provider/runtime fallback; oracle conflict also exists | `4907 ms` ledger / `4941 ms` event | `FAIL` |
| 2–15 | Not run | Not run | Not assessable | Not assessable | `NOT_RUN` |

## Gate impact

- Native provider warm-up: `PASS`.
- Telegram receipt/delivery: `PASS` for the single observed row.
- Supported grounded-answer acceptance: `FAIL`.
- Full 12+3 semantic/source/abstention run: `NOT_COMPLETED`.
- Full 15-item latency run: `NOT_COMPLETED`.
- Live invalid/provider/5xx/timeout/database/duplicate/concurrency matrix: `NOT_VERIFIED`.
- Clean-instance import/rebind, Security, release, and cleanup: `NOT_VERIFIED`/`NOT_STARTED`.

## QA conclusion

The warm-provider precondition did not make the current candidate pass item 1. The provider endpoints themselves responded to synthetic warm-up, but the real workflow still emitted a provider/runtime failure fallback. The candidate is not proven usable and is not release-ready.

## Required next action

Engineer should inspect the workflow-level provider request and failure classification after the independent warm-up, preserving sanitized evidence for model binding, request body, timeout budget, and response/error handling. The dataset/corpus oracle conflict must also be resolved before final semantic scoring. QA should rerun item 1 alone after both issues are addressed, then continue the 12+3 sequence only if item 1 produces a grounded answer with a reconciled allowed source.

## Integrity and change boundary

- QA did not modify application code, workflow exports, credentials, runtime settings, Docker configuration, database data, or corpus data.
- No raw answer transcript, message payload, chat identifier, credential value, or restricted record was persisted in this report.
