# M7 Independent QA v5 Post-Refresh Rerun — 2026-09-20

## Verdict

`PASS` for the newly requested post-refresh item-1 rerun. The n8n runtime was verified at v5, the provider was warmed independently, and one Telegram item produced a grounded corpus-backed answer with no telemetry error. This is an item-level result only; the M7 aggregate remains `NOT_VERIFIED`.

## Precondition and runtime

- Human requested a new rerun after the n8n page/runtime refresh.
- Candidate observed in PostgreSQL: `m6-local-gemma-bounded-2026-09-20-v5`.
- `output_bound=192`; online timeout `4000 ms`; business deadline `5000 ms`; Telegram reserve `1000 ms`.
- n8n health/readiness: HTTP 200.
- n8n, PostgreSQL, gateway, and tunnel containers: running/healthy as applicable.
- Active corpus hash prefix: `sha256:61b730...6d109`.

## Independent warm-up

Immediately before the send, QA ran synthetic provider probes from inside `rag-n8n-local` with `keep_alive=10m`:

```text
embed_rc=0|bytes=9668|elapsed_ms=0
chat_rc=0|bytes=346|elapsed_ms=1
```

No Telegram payload, user message, or corpus answer was used in the warm-up.

## Telegram item-1 result

- Item: approved synthetic dataset item 1.
- Submission: one new message through the authenticated Telegram sandbox after the refresh and warm-up.
- UI result: grounded answer with corpus citation/source `21_Kebijakan_Jadwal_Shift_Kerja.md`.
- Ledger result: `status=delivered`, empty error category, `1814 ms` claim-to-delivery duration.
- Safe event: `workflow=02-telegram-grounded-qa`, `stage=delivery`, `status=success`, empty error category, `1863 ms`.

This is the second valid post-refresh item-1 pass: the prior post-refresh retry recorded `1911 ms` ledger / `1965 ms` event with no error category. The earlier fallback attempt remains excluded as `INVALID_PRECONDITION` because it occurred before the n8n refresh.

## Gate impact

- Post-refresh item 1: `PASS`, two valid observations after refresh.
- Full 12+3 semantic/source/abstention matrix: `NOT_RUN`.
- Full 15-item latency coverage: `NOT_VERIFIED`.
- Live provider/budget/timeout/database/duplicate/concurrency matrix: `NOT_VERIFIED`.
- Security, clean-instance import/rebind, release, and cleanup: `NOT_VERIFIED`/`NOT_STARTED`.

## Oracle conflict remains open

The dataset oracle still expects `08:00` and source `09_FAQ_Jam_Operasional_dan_Lokasi.md`, while persisted corpus documents `09` and `21` state `07.00–21.00`. The two valid post-refresh observations follow the corpus-backed interpretation and cite source `21`; this does not resolve the approved oracle conflict. Human/Architect must decide the expected answer/source before final semantic scoring.

## QA conclusion

The refresh-sensitive item-1 path now has two valid post-refresh passes with sub-two-second delivery telemetry. This removes the pre-refresh stale-session observation from the valid v5 result set, but it does not establish M7 completion. QA will not send items 2–15 until the approved oracle is reconciled.

## Integrity and change boundary

- QA did not modify application code, workflow exports, credentials, runtime settings, Docker configuration, database data, or corpus data.
- No raw answer transcript, message payload, chat identifier, credential value, or restricted record was persisted here.
