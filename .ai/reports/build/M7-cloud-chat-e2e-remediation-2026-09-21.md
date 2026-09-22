# M7 Engineer Cloud-Chat E2E Remediation

Date: `2026-09-21`  
Owner: `Engineer`  
Workflow: `02 — Telegram Grounded Q&A` (`IAOqkQsNamEJarHF`)  
Target chat: approved Telegram sandbox `5578891856`

## Executive result

`TARGETED E2E PASS / M7 FULL MATRIX NOT_VERIFIED`

The runtime now uses a hosted DeepSeek chat binding with the existing local EmbeddingGemma retrieval path. A supported question produced a grounded answer with a source, and an unsupported question produced the exact official-document abstention. Both messages were delivered and both now persist a `grounding_diagnostic` row.

This is targeted Engineer evidence only. It does not replace the independent M7 1–15 matrix, live fault/concurrency checks, Security, or release approval.

## Operator confirmation

The operator confirmed that the DeepSeek API key had been entered in n8n. The key value was not read, copied, or recorded in this report.

## Changes applied

1. `Query Embedding` and `Chat Completion` explicitly send `Content-Type: application/json` through n8n raw request mode. This removes the prior empty-content-type/HTTP 415 path.
2. `Prepare Chat Completion Request` now sends DeepSeek with `thinking: { type: 'disabled' }` and `reasoning_effort: 'none'`, so the reasoning budget cannot consume the entire bounded answer budget. DeepSeek documents thinking mode as enabled by default and supports disabling it through these request controls.
3. `Normalize Update` now creates `correlation_id` before retrieval and diagnostic persistence. The diagnostic node executes before Telegram delivery, so creating the ID only in `Delivery Success` was too late.
4. `Record Grounding Diagnostic` now uses `status='success'`. PostgreSQL `rag.safe_events.status` accepts `started`, `success`, `failed`, `timeout`, and `aborted`; the former `observed` value was rejected by the check constraint and the node was configured to continue on error.
5. Two temporary `TEMP — DeepSeek Provider Probe` workflows and their internal n8n references were removed after diagnosis. The local probe JSON was also removed. The four real workflow records remain intact.

## Runtime binding

```text
chat_base_url=https://api.deepseek.com
chat_api_path=/chat/completions
chat_model=deepseek-flash
chat credential=DeepSeek account (n8n deepSeekApi)
embedding_model=embeddinggemma:300m-qat-q4_0
embedding_profile_id=ollama:embeddinggemma:300m-qat-q4_0:768
embedding_dimension=768
config_revision=cloud-chat-local-embedding-2026-09-21-v2
```

No API key, Telegram token, database password, raw prompt, or full transcript is included here.

## Telegram E2E evidence

| Path | Update ID | Telegram result | Persisted diagnostic | Key evidence |
|---|---:|---|---|---|
| Supported | `115144343` | `delivered`, `3068 ms` | `safe_events.id=196`, `success`, `2110 ms` | `gate=pass; model=model_text_received; validator=answered; response=answered; sources=1` |
| Unsupported | `115144344` | `delivered`, `2116 ms` | `safe_events.id=198`, `success`, `1245 ms` | `model=model_abstention_text; validator=no_valid_citation; response=abstained` |

Observed Telegram responses:

- Supported: grounded SOP summary followed by `Sumber: 03_SOP_Penanganan_Kas_dan_Setoran_Harian.md`.
- Unsupported: `Informasi tidak ditemukan di dokumen resmi.`

Persisted delivery rows are `rag.telegram_updates.id=156` and `157`, both `status=delivered` with empty `error_category`. Corresponding delivery safe events are `197` and `199`, both `status=success`.

## QA handoff

QA can now rerun the focused cases that were previously blocked by the local Gemma behavior, especially supported items `9` and `10`, using the current cloud-chat binding. The old v9 Gemma semantic outcomes must not be treated as current cloud-chat results.

Remaining gates:

- independent full 12+3 semantic matrix;
- item-oracle confirmation against the active corpus;
- live fault, duplicate, concurrency, and clean-import/rebind checks;
- Security and release decision.

Until those are independently rerun and accepted, M7 remains `NOT_VERIFIED` and no release candidate is declared.

## References

- [DeepSeek Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/)
- [DeepSeek Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion/)
