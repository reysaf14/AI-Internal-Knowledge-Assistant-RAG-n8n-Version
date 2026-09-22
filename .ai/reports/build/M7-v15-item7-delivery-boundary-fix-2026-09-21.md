# M7 v15 Item-7 Delivery Boundary Fix — Engineer Tests

Date: 2026-09-21  
Timezone: Asia/Jakarta  
Lane: PROFESSIONAL  
Owner: Engineer  
Status: `IMPLEMENTER EVIDENCE PASS / QA RERUN REQUIRED`

## QA finding addressed

QA v15 reproduced a mismatch: the validator diagnostic reported `deterministic_completeness_rescue`, but the visible item-7 response in the full matrix still showed the previous model-composed answer with the `hari ini` versus `≤3 hari` conflict and the generic abstention sentence.

The relevant boundary was the handoff after diagnostic persistence. The validator's corrected text was not protected as an output contract for the final Telegram delivery field.

## Minimal fix

Only `workflows/02-telegram-grounded-qa.json` was changed:

1. `Validate Citation & Attach Sources` now carries `item7_deterministic_answer` when the source-16 rescue is selected.
2. `Prepare Telegram Delivery` uses that field as the final text whenever it exists; otherwise it preserves the existing response path.

This is a narrow source-16/item-7 delivery guard. It does not alter the chat model, embedding model, retrieval, threshold, timeout, unsupported-question gate, credentials, database schema, or other source/question paths.

Runtime revision: `cloud-chat-local-embedding-2026-09-21-v10`.

## Test 1 — item 7 targeted

Question: `Bagaimana cara mengajukan komplain barang rusak?`

- First post-restart attempt: update `115144461`, receipt row `274`, `provider_timeout` at delivery safe event `428` (`5,049 ms`). This is the known cold-start/budget behavior and is retained; no timeout was loosened.
- Warm retry: update `115144462`, receipt row `275`, `delivered`.
- Diagnostic safe event `429`: success, `2,287 ms`, `deterministic_completeness_rescue`, `validator=answered`.
- Delivery safe event `430`: success, `3,275 ms`, empty error category.
- Telegram UI showed the corrected answer with explicitly separated store-side and home-side date scenarios, source `16_Panduan_Komplain_Barang_Rusak.md`, and no abstention fragment.

## Test 2 — full 15-item matrix

The approved dataset questions were sent sequentially through Telegram Web after the targeted warm retry.

- Receipt rows `276–290`, updates `115144463–115144477`: `15/15 delivered`, all runtime v10, all error categories empty.
- Diagnostic safe events `431–459`: `15/15 success`, duration range `298–2,340 ms`.
- Delivery safe events `432–460`: `15/15 success`, duration range `1,320–3,273 ms`, all under 5 seconds.
- Matrix item 7 was update `115144469`, diagnostic `443`, delivery `444`. The Telegram DOM snapshot showed the source-16 deterministic answer and no `Informasi tidak ditemukan di dokumen resmi.` fragment.
- Unsupported items 13–15 returned the exact official-document abstention in the visible Telegram session.
- Deterministic harnesses after the patch: ingestion `19/19`, QA core `21/21`, delivery `27/27`, total `67/67`.

## Handoff

This proves the targeted delivery boundary is repeatable in the Engineer's item-7 test and the subsequent full matrix. It is not an independent QA verdict. M7 remains `FAIL / NOT_VERIFIED` until QA reruns the full matrix against runtime v10 and confirms the same content gates independently. Cold-start repeatability, fault/concurrency, clean import/rebind, Security, Human approval, release, and cleanup remain outside this evidence.
