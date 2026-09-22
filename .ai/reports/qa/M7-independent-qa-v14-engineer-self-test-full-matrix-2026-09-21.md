# M7 Independent QA v14 — Engineer Self-Test Follow-up Full Matrix

Date: 2026-09-21  
Timezone: Asia/Jakarta  
Project/lane: Asisten Pengetahuan Internal Toko Makmur Jaya / PROFESSIONAL  
Executor: QA, independent of Engineer implementation and self-test  
Candidate: runtime v8 / Engineer v12 cash-closing remediation  
Verdict: FAIL — NOT RELEASE READY

## Objective and evidence rule

This run independently reruns the approved 12 supported + 3 unsupported Telegram matrix after the Engineer reported a self-test and updated project state. The Engineer self-test is treated as setup/context only, not as QA evidence. The verdict below is based on this fresh Telegram Web interaction, the current active workflow/runtime, and the newly persisted PostgreSQL counters/events.

No credentials, raw Telegram payloads, provider bodies, or production records were read or stored. The per-item artifact is sanitized.

## Candidate freeze

| Artifact/runtime | Observed evidence |
|---|---|
| Workflow | ID `IAOqkQsNamEJarHF`; local export parses with 37 nodes |
| Workflow export SHA-256 | `7ED4468C13E8BC8DF82780CC55D516BCEB5F05BB01206121F70A3D14907B767B` |
| Dataset SHA-256 | `6B4587A7DCB7EB04630801D7073F7424ED8274D7245746A3C82CD658DFF60614` |
| Evaluation README SHA-256 | `FD9BDAE3F1B0CB9D7C51D1F40F1A06AA95850AA674EB95DD07029A5CA56259EC` |
| Runtime revision | `cloud-chat-local-embedding-2026-09-21-v8` |
| Chat | DeepSeek `deepseek-flash` |
| Embedding | local `embeddinggemma:300m-qat-q4_0`, profile dimension 768 |
| Retrieval | limit 5; minimum similarity 0.25 |
| Bounds | context 6500; output 256; AI timeout 4000 ms |
| Active corpus | `sha256:61b7301108de25c111d815812e8695f150e4e958dbbd9c40dd03dfd1baa6d109`; 26 documents, 297 chunks |
| Temperature | 0 |

## Preconditions and execution

- `rag-n8n-local` and `rag-postgres-local` were healthy before execution.
- Telegram Web was logged in to the `AgnesTachyon` bot chat.
- The 15 dataset questions were entered sequentially in the visible Telegram Web session. The UI showed 15/15 question/answer pairs.
- Manual UI exit code: `NOT_APPLICABLE` because the acceptance evidence is visual UI observation plus persisted receipts/events, not a process exit code.
- Execution window observed in the UI: approximately 18:55–18:57 Asia/Jakarta on 2026-09-21; report authored at 19:05 Asia/Jakarta.
- Engineer's item-1 self-test (update 241 / diagnostic 363 / delivery 364) is outside this run and is not counted.

Independent deterministic regression was rerun before the Telegram matrix:

| Command | Expected | Observed | Exit |
|---|---:|---:|---:|
| `python tests/harness/test_ingestion.py` | 19 | 19/19 | 0 |
| `python tests/harness/test_qa_core.py` | 21 | 21/21 | 0 |
| `python tests/harness/test_delivery_core.py` | 27 | 27/27 | 0 |
| Total | 67 | 67/67 | 0 |

## Persisted before/after evidence

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| `rag.telegram_updates` | 240 | 255 | +15 |
| `rag.safe_events` | 318 | 348 | +30 |

New Telegram receipt rows were IDs `242–256`; all 15 were delivered with no persisted delivery failure category. New safe events were IDs `365–394`: 15 `grounding_diagnostic` events and 15 `delivery` events, all `status=success`. Delivery durations were `1,159–3,785 ms`; all were below the 5,000 ms target.

## Independent matrix

The approved rubric requires all supported mandatory facts, no contradiction or unsupported policy claim, and a relevant source. Unsupported questions must abstain without citation. The exact sanitized per-item record is in `evaluation/run_v14-engineer-self-test-full-matrix-2026-09-21.jsonl`.

| Item | Observed result | Diagnostic / delivery | Verdict |
|---:|---|---|---|
| 1 | Monday hours answer `07.00–21.00`, source 09; fresh-run pass | 365 / 366; 1,384 / 2,360 ms | PASS, source-label nuance |
| 2 | Parking answer includes approximately 10 motorbikes, 5 cars, free; source 09 | 367 / 368; 1,467 / 2,336 ms | PASS |
| 3 | Return/exchange answer grounded in source 11 | 369 / 370; 2,322 / 3,228 ms | PASS |
| 4 | Opening SOP complete; deterministic rescue; source 01 | 371 / 372; 2,097 / 2,993 ms | PASS |
| 5 | Cash SOP includes 20.55 count, evidence, QRIS/debit, reconciliation, cash float, safe, setoran, logs; source 03 | 373 / 374; 2,246 / 3,123 ms | PASS |
| 6 | Closing SOP includes customer-flow boundary, active checkout, two-witness count, QRIS/debit, AC/lamp/music/POS shutdown, alarm/locks/log; source 02 | 375 / 376; 2,071 / 2,967 ms | PASS |
| 7 | Procedure and source 16 are present, but answer also says information was not found and exposes `hari ini` versus `≤3 hari` conflict | 377 / 378; 2,866 / 3,785 ms | **FAIL** |
| 8 | Late-delivery procedure grounded in source 18 | 379 / 380; 1,518 / 2,432 ms | PASS |
| 9 | 12 annual-leave days; source 20 | 381 / 382; 1,662 / 2,539 ms | PASS |
| 10 | Sick-leave boundary: up to 2 days without letter; over 2 days with doctor letter; source 20 | 383 / 384; 1,474 / 2,401 ms | PASS |
| 11 | K3 APAR and evacuation-route answer complete; deterministic rescue; source 25 | 385 / 386; 1,669 / 2,549 ms | PASS |
| 12 | Address correct; source 09 is relevant, with known CSV canonical-label nuance | 387 / 388; 1,349 / 2,336 ms | PASS, source-label nuance |
| 13 | Exact official-document abstention; no citation | 389 / 390; 1,356 / 2,238 ms | PASS |
| 14 | Exact official-document abstention; no citation | 391 / 392; 1,018 / 1,957 ms | PASS |
| 15 | Exact official-document abstention; no citation; support-gate stage | 393 / 394; 250 / 1,159 ms | PASS |

## Aggregate gates

- Content/abstention: **14/15**.
- Supported: **11/12**; item 7 fails.
- Unsupported: **3/3**.
- Delivery: **15/15** persisted as delivered.
- Latency: **15/15** under 5,000 ms; range **1,159–3,785 ms**.
- Diagnostic persistence: **15/15** new diagnostic rows, all success.
- Deterministic regression: **67/67** pass.
- Source relevance: **12/12** supported answers cite a semantically relevant active-corpus source. Exact dataset-label parity is **10/12** because item 1 cites source 09 instead of CSV canonical 21 and item 12 cites source 09 instead of CSV canonical 00; these remain traceability nuances carried from the approved corpus-backed interpretation.

The required content gate is 15/15 and is not met. Therefore the independent live matrix is **FAIL / NOT_VERIFIED**. Successful delivery, sub-five-second latency, and complete diagnostics do not override the item-7 supported-answer failure.

## Findings

### P1 — Item 7 mixes a supported answer with abstention and unresolved policy conflict

The UI answer contains the expected complaint procedure and cites source 16, but it also appends `Informasi tidak ditemukan di dokumen resmi.` and explicitly reports conflicting date facts from retrieved chunks (`hari ini` versus `≤3 hari`). Under the approved supported-question rubric, a supported answer must convey the required facts without contradiction or unsupported policy claims. This is a live behavioral failure, not a missing Telegram delivery or a deterministic-harness gap.

Required owner: Engineer. The response boundary/source-oracle handling for source 16 must produce one grounded, non-contradictory policy answer or a clean supported abstention only when the approved oracle says the fact is unavailable. QA must rerun the complete matrix after the fix.

### P2 — Item 1 is not currently failing on warm-up evidence

The fresh independent run passed item 1 with a grounded answer, persisted diagnostic `365` at `1,384 ms`, and persisted delivery `366` at `2,360 ms`. This does not prove cold-start behavior or repeatability across idle windows, but it does remove item 1 as the current observed content blocker in this run. The Engineer self-test was excluded from the count.

### P2 — v12 cash/closing fix remains closed for content completeness

Items 5 and 6 independently pass the mandatory checks in the actual Telegram UI, including the 20.55 cash count and the closing customer-flow/AC/lamp/music/POS facts.

## Coverage boundary

Still unverified: live fault injection beyond the observed paths, provider/database fault matrix, duplicate/concurrency behavior on current v8, clean-instance import/rebind, Security audit, Human quality approval, release, and cleanup/revocation. This report does not authorize release.

## Status and handoff

M7 remains **FAIL / NOT_VERIFIED**. The next owner is **Engineer** for item-7 response/oracle remediation; QA then reruns the full 15-item matrix. No Engineer self-test or prior pass silently replaces this failed current matrix.

Artifacts:

- `evaluation/run_v14-engineer-self-test-full-matrix-2026-09-21.jsonl`
- `evaluation/run_v14-engineer-self-test-full-matrix-2026-09-21_config.json`
- `evaluation/run_v14-engineer-self-test-full-matrix-2026-09-21_summary.md`
- `.ai/project-state.md`
