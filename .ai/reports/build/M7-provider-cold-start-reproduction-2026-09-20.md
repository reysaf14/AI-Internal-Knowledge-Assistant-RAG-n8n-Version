# M7 Provider Cold-Start Reproduction — Engineer Handoff

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Role:** Engineer remediation / controlled QA preparation
- **Date:** 2026-09-20 (`Asia/Jakarta`)
- **Status:** `READY FOR HUMAN-CONTROLLED QA RERUN`; M7 remains `NOT_VERIFIED`
- **QA finding:** `.ai/reports/qa/M7-independent-qa-recovery-rerun-2026-09-20.md`

## Finding

The recovery rerun proved that Telegram receipt and delivery work, but the first clean item returned `provider_or_runtime_failure`. A sanitized provider probe from inside the n8n container reproduced a cold-start dependency:

| Probe | Cold | Warm |
|---|---:|---:|
| `embeddinggemma:300m-qat-q4_0` via `/v1/embeddings` | ~`3,017ms` | ~`209ms` |
| `gemma4:e2b-it-qat` via native `/api/chat`, `think:false` | ~`15,542ms` | ~`567ms` |

Container-to-Ollama reachability itself passed for both API surfaces. The current online budget is `5,000ms` with `1,000ms` reserved for Telegram delivery and `ai_timeout_max=3,000ms`. Therefore a cold provider call can exhaust the bounded path before a grounded answer is produced, while the warm path matches the successful late-night behavior.

This evidence identifies cold-start timing as the leading provider/runtime cause. The exact failing node for the QA item is not promoted to a QA claim until a clean rerun records it independently.

## Controlled test preparation

The models were warmed with synthetic probes only; no user message or Telegram payload was used for warm-up. The current runtime remains:

- `config_revision=m6-local-gemma-bounded-2026-09-20`
- `chat_model=gemma4:e2b-it-qat`
- `embedding_model=embeddinggemma:300m-qat-q4_0`
- n8n/PostgreSQL/tunnel/gateway healthy
- no workflow source, credential, corpus, or database configuration change

## Human-controlled QA procedure

1. Keep the current n8n and temporary HTTPS tunnel running.
2. Use the already authorized Telegram sandbox target.
3. Send exactly one approved supported item: `Jam berapa toko buka hari Senin?`
4. Send it within the warm window after the synthetic warm-up; do not send duplicates.
5. Confirm that the response is grounded and contains the expected source, not the service-unavailable fallback.
6. If item 1 passes, QA may continue the remaining 14 items sequentially with the same frozen configuration.

Warm-up/readiness timing must be recorded separately from the required end-to-end item latency. M7 remains `NOT_VERIFIED` until QA independently records the grounded response and completes its acceptance scope.
