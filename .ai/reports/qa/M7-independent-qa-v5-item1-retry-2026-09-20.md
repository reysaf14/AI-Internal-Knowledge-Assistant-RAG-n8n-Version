# M7 Independent QA v5 Item-1 Retry — 2026-09-20

## Verdict

`FAIL / NOT_VERIFIED` for item-1 repeatability on candidate v5. A first independent warm-provider attempt returned the service-unavailable fallback with `provider_or_runtime_failure`; after a second independent warm-up, one retry of the same item returned a grounded answer with an approved corpus source. The contradictory outcomes show that the candidate is not yet stable enough to unlock the remaining 14 items.

No full 12+3 run was claimed or completed.

## Candidate and boundary

- Candidate: `m6-local-gemma-bounded-2026-09-20-v5`.
- Chat model: `gemma4:e2b-it-qat`.
- Embedding model: `embeddinggemma:300m-qat-q4_0`.
- Online timeout: `4000 ms`; business deadline `5000 ms`; Telegram reserve `1000 ms`.
- Active corpus hash prefix: `sha256:61b730...6d109`.
- Target: authorized Telegram sandbox; identifier omitted.
- Dataset: approved synthetic `12 supported + 3 unsupported`.

The Engineer v5 report was read as implementer evidence only. QA did not modify code, workflow, credentials, runtime settings, database data, or corpus data.

## Preflight and warm-up

QA independently observed healthy n8n, PostgreSQL, gateway, and tunnel containers; n8n health and readiness both returned HTTP 200. PostgreSQL reported revision v5 and `output_bound=192`.

Two separate synthetic warm-ups were performed from inside `rag-n8n-local`, with no Telegram payload or corpus content:

| Attempt | Embedding | Chat |
|---|---:|---:|
| First v5 run | `rc=0`, `3 ms` | `rc=0`, `25 ms` |
| Retry run | `rc=0`, `0 ms` | `rc=0`, `1 ms` |

Only return codes, response sizes, and durations were retained.

## Item-1 observations

### Attempt A — first v5 QA run

- Telegram message submitted once after independent warm-up.
- Telegram response: service-unavailable fallback.
- Current-candidate ledger: `delivered`, `provider_or_runtime_failure`, `4940 ms`.
- Safe event: `success`, `provider_or_runtime_failure`, `4987 ms`.
- Result: `FAIL`.

### Attempt B — controlled retry after a second warm-up

- The same approved item was submitted once more after the second independent warm-up.
- Telegram response: grounded corpus-backed answer with a citation/source for `21_Kebijakan_Jadwal_Shift_Kerja.md`.
- Current-candidate ledger: `delivered`, empty error category, `1911 ms`.
- Safe event: `success`, empty error category, `1965 ms`.
- Result: `PASS` for this single attempt against the corpus-backed interpretation.

## Repeatability result

| Item | Attempt A | Attempt B | Repeatability |
|---:|---|---|---|
| 1 | Fallback / provider-runtime failure at `4940/4987 ms` | Grounded answer / source observed at `1911/1965 ms` | `FAIL / NOT_VERIFIED` |

The second result does not erase the first observed failure. The item is not considered stable under the same approved warm precondition.

## Oracle/corpus conflict remains open

The dataset oracle for item 1 expects `08:00` and source `09_FAQ_Jam_Operasional_dan_Lokasi.md`. Persisted corpus documents `09` and `21` state `07.00–21.00`. The successful retry followed the corpus-backed interpretation and cited source `21`; Human/Architect has not yet reconciled the expected answer/source.

This prevents final semantic scoring even for the successful retry. QA did not alter the oracle or corpus.

## Gate impact

- v5 workflow receipt/delivery: observed on both attempts.
- v5 latency: one failing near-deadline attempt and one successful sub-two-second attempt; full latency acceptance not established.
- Item-1 grounded-answer stability: `FAIL / NOT_VERIFIED`.
- Full 12+3 semantic/source/abstention matrix: `NOT_RUN`.
- Live provider/budget/timeout/database/duplicate/concurrency matrix: `NOT_VERIFIED`.
- Clean-instance portability, Security, release, and cleanup: `NOT_VERIFIED`/`NOT_STARTED`.

## QA conclusion

The v5 runtime-budget remediation improves one retry result but does not yet prove deterministic, repeatable behavior. The candidate remains unsuitable for a release decision. Engineer should investigate the intermittent provider/runtime failure and preserve enough sanitized timing/error evidence to explain why identical warm attempts diverge.

## Required next action

1. Engineer isolates the v5 intermittent failure path, including remaining-budget calculation, provider response timing, and failure classification.
2. Human/Architect reconciles the item-1 dataset oracle with the persisted corpus.
3. QA reruns item 1 until the reconciled grounding/source result is repeatable; only then should the 14 remaining items be sent sequentially.
