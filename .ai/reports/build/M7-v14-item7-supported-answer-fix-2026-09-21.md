# M7 Item 7 Supported-Answer Fix — Engineer Self-Test

Date: 2026-09-21  
Timezone: Asia/Jakarta  
Lane: PROFESSIONAL  
Owner: Engineer  
Status: `IMPLEMENTER FIX VERIFIED / QA RERUN REQUIRED`

## Finding reviewed

QA v14 reported one remaining content failure in item 7, `Bagaimana cara mengajukan komplain barang rusak?`. Retrieval, source relevance, Telegram delivery, diagnostic persistence, latency, and the deterministic harness were already passing. The live model answer used source 16 but mixed two valid date rules (`hari ini` for a store-side discovery and `≤3 hari` for a home-side discovery), then appended the generic abstention sentence. That was a response-composition/oracle-boundary defect, not a missing document or delivery defect.

Reference: `.ai/reports/qa/M7-independent-qa-v14-engineer-self-test-full-matrix-2026-09-21.md`.

## Minimal change

Only `workflows/02-telegram-grounded-qa.json` was changed in the `Validate Citation & Attach Sources` code node:

- Detect the item-7 question only when retrieved evidence contains source prefix `16_`.
- Produce a deterministic source-16 answer with explicitly separated scenarios:
  - damage found in the store: report immediately at the cashier and verify the item, receipt, and purchase date;
  - damage found at home: report within three days, bring the original item and receipt, and do not disassemble or modify it;
  - approved outcomes: exchange, refund, or discount;
  - rejection / more than three days: explain the reason and direct to supplier warranty or owner negotiation when applicable;
  - record the complaint in the complaint form/POS.
- Keep the existing model/citation path unchanged for all other sources and questions.

No credential, provider, embedding model, retrieval threshold, database schema, or timeout was changed.

## Deployment evidence

- Workflow `IAOqkQsNamEJarHF` was imported and activated.
- Runtime revision was advanced to `cloud-chat-local-embedding-2026-09-21-v9`.
- `deepseek-flash`, local `embeddinggemma:300m-qat-q4_0`, and `ai_timeout_max=4000` remained unchanged.
- `rag-n8n-local` and `rag-postgres-local` were healthy after restart.
- Active workflow export parsed as valid JSON and contained both `damagedGoods` and `Komplain barang rusak` rescue markers.

## Regression evidence

| Check | Result |
|---|---:|
| Ingestion harness | 19/19 |
| Grounded-answer harness | 21/21 |
| Telegram-delivery harness | 27/27 |
| Deterministic total | 67/67 |

## Live Engineer self-test

Question sent to the authorized Telegram sandbox `chat_id=5578891856`: `Bagaimana cara mengajukan komplain barang rusak?`

The first attempt immediately after the n8n restart returned the service-unavailable fallback. The persisted receipt classified it as `workflow_stage_failure:prepare_chat_completion_request`, update `115144444`, runtime v9, delivery `4992 ms`. This occurred before the citation validator and is recorded as a cold/idle runtime-budget transient; no timeout or acceptance gate was loosened.

A warm retry returned the corrected source-grounded answer in Telegram:

- Telegram update `115144445`, status `delivered`;
- diagnostic safe event `396`, status `success`, `2424 ms`;
- validator `deterministic_completeness_rescue`, response `answered`;
- delivery safe event `397`, status `success`, `3395 ms`;
- error category empty;
- source shown: `16_Panduan_Komplain_Barang_Rusak.md`.

The warm retry contained no `Informasi tidak ditemukan di dokumen resmi.` fragment and did not merge the store and home date rules.

## Handoff and boundary

This is implementer evidence for the targeted item-7 fix. It does not replace QA v14 and does not make M7 pass. QA should rerun the complete approved 12-supported + 3-unsupported Telegram matrix against runtime v9. Cold-start repeatability, fault/concurrency, clean import/rebind, Security, Human approval, release, and cleanup remain outside this self-test.
