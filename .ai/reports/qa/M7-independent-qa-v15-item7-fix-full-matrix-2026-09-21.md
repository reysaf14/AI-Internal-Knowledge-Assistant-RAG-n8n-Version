# M7 Independent QA v15 — Item-7 Fix Full Matrix

Date: 2026-09-21  
Timezone: Asia/Jakarta  
Project/lane: Asisten Pengetahuan Internal Toko Makmur Jaya / PROFESSIONAL  
Executor: QA, independent of Engineer implementation and targeted self-test  
Candidate: runtime v9 / Engineer item-7 supported-answer fix  
Verdict: FAIL — NOT RELEASE READY

## Objective and evidence rule

This run independently reruns the approved 12 supported + 3 unsupported Telegram matrix after the Engineer reported the item-7 fix and a warm targeted self-test. The Engineer report and self-test are used only to identify the candidate and intended remediation; they are not QA proof. The verdict is based on the fresh Telegram Web interaction, active workflow/runtime, and newly persisted PostgreSQL evidence.

No credentials, raw Telegram payloads, provider bodies, or production records were read or stored. The per-item artifact is sanitized.

## Candidate freeze

| Artifact/runtime | Observed evidence |
|---|---|
| Workflow | ID `IAOqkQsNamEJarHF`; local export parses with 37 nodes |
| Workflow export SHA-256 | `F726285D023CDB14D344C819FA42E0E758FD858BFF3F4295F62981A9FD9BDD88` |
| Dataset SHA-256 | `6B4587A7DCB7EB04630801D7073F7424ED8274D7245746A3C82CD658DFF60614` |
| Evaluation README SHA-256 | `FD9BDAE3F1B0CB9D7C51D1F40F1A06AA95850AA674EB95DD07029A5CA56259EC` |
| Runtime revision | `cloud-chat-local-embedding-2026-09-21-v9` |
| Chat | DeepSeek `deepseek-flash` |
| Embedding | local `embeddinggemma:300m-qat-q4_0`, profile dimension 768 |
| Retrieval | limit 5; minimum similarity 0.25 |
| Bounds | context 6500; output 256; AI timeout 4000 ms |
| Active corpus | `sha256:61b7301108de25c111d815812e8695f150e4e958dbbd9c40dd03dfd1baa6d109`; 26 documents, 297 chunks |

## Preconditions and execution

- `rag-n8n-local` and `rag-postgres-local` were healthy before execution.
- Telegram Web was logged in to the `AgnesTachyon` bot chat.
- The 15 dataset questions were entered sequentially in the visible Telegram Web session. The UI showed 15/15 question/answer pairs; current fresh messages were timestamped approximately 19:41–19:43 Asia/Jakarta.
- Manual UI exit code: `NOT_APPLICABLE` because acceptance evidence is visual UI observation plus persisted receipts/events, not a process exit code.
- The Engineer targeted warm self-test and its earlier post-restart failure were excluded from this run's acceptance count.

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
| `rag.telegram_updates` | 257 | 272 | +15 |
| `rag.safe_events` | 351 | 381 | +30 |

New receipt rows were IDs `259–273`; all 15 were `delivered`, used runtime v9, and had empty error categories. New safe events were IDs `398–427`: 15 `grounding_diagnostic` events and 15 `delivery` events, all `status=success`. Delivery durations were `1,292–3,318 ms`; all were below the 5,000 ms target.

## Independent matrix

The approved rubric requires all supported mandatory facts, no contradiction or unsupported policy claim, and a relevant source. Unsupported questions must abstain without citation. The exact sanitized per-item record is in `evaluation/run_v15-item7-fix-full-matrix-2026-09-21.jsonl`.

| Item | Observed result | Diagnostic / delivery | Verdict |
|---:|---|---|---|
| 1 | Monday hours `07.00–21.00`, source 09; fresh-run pass | 398 / 399; 1,310 / 2,231 ms | PASS, source-label nuance |
| 2 | Parking answer includes approximately 10 motorbikes, 5 cars, free; source 09 | 400 / 401; 1,100 / 2,017 ms | PASS |
| 3 | Return/exchange boundary grounded in source 11 | 402 / 403; 1,844 / 2,789 ms | PASS |
| 4 | Opening SOP complete; deterministic rescue; source 01 | 404 / 405; 1,889 / 2,745 ms | PASS |
| 5 | Cash SOP includes 20.55 count, evidence, QRIS/debit, reconciliation, cash float, safe, setoran, logs; source 03 | 406 / 407; 1,905 / 2,795 ms | PASS |
| 6 | Closing SOP includes customer-flow boundary, active checkout, two-witness count, QRIS/debit, AC/lamp/music/POS shutdown, alarm/locks/log; source 02 | 408 / 409; 2,054 / 2,955 ms | PASS |
| 7 | Fresh full-matrix answer still includes the source-16 procedure plus the `hari ini` versus `≤3 hari` conflict and `Informasi tidak ditemukan di dokumen resmi.` | 410 / 411; 1,489 / 2,389 ms | **FAIL** |
| 8 | Late-delivery procedure grounded in source 18 | 412 / 413; 1,672 / 2,632 ms | PASS |
| 9 | 12 annual-leave days; source 20 | 414 / 415; 1,745 / 2,731 ms | PASS |
| 10 | Sick-leave boundary: up to 2 days without letter; over 2 days with doctor letter; source 20 | 416 / 417; 1,466 / 3,318 ms | PASS |
| 11 | K3 APAR and evacuation-route answer complete; source 25 | 418 / 419; 1,399 / 2,338 ms | PASS |
| 12 | Address correct; source 09 is relevant, with known CSV canonical-label nuance | 420 / 421; 1,098 / 2,002 ms | PASS, source-label nuance |
| 13 | Exact official-document abstention; no citation | 422 / 423; 1,369 / 2,268 ms | PASS |
| 14 | Exact official-document abstention; no citation | 424 / 425; 986 / 1,996 ms | PASS |
| 15 | Exact official-document abstention; no citation; support-gate stage | 426 / 427; 300 / 1,292 ms | PASS |

## Aggregate gates

- Content/abstention: **14/15**.
- Supported: **11/12**; item 7 fails again.
- Unsupported: **3/3**.
- Delivery: **15/15** persisted as delivered.
- Latency: **15/15** under 5,000 ms; range **1,292–3,318 ms**.
- Diagnostic persistence: **15/15** new diagnostic rows, all success.
- Deterministic regression: **67/67** pass.
- Source relevance: **12/12** supported answers cite a semantically relevant active-corpus source. Exact dataset-label parity is **10/12** because item 1 cites source 09 instead of CSV canonical 21 and item 12 cites source 09 instead of CSV canonical 00; these remain traceability nuances carried from the approved corpus-backed interpretation.

The required content gate is 15/15 and is not met. Therefore the independent live matrix is **FAIL / NOT_VERIFIED**. Successful delivery, sub-five-second latency, and complete diagnostics do not override the item-7 failure.

## Findings

### P1 — Engineer item-7 fix is not repeatable in the fresh full matrix

The targeted Engineer warm self-test reported a corrected item-7 answer. In this independent full matrix, the new Telegram response at approximately 19:42 again contained both valid scenarios but also exposed the unresolved `hari ini` versus `≤3 hari` facts and appended `Informasi tidak ditemukan di dokumen resmi.`. This violates the supported-answer rubric.

Persisted evidence for the same item is internally noteworthy: diagnostic event `410` is `grounding_diagnostic`, `success`, and labels the model stage `deterministic_completeness_rescue`; delivery event `411` is `success` at `2,389 ms`. The visible content still fails, so the deterministic stage label does not prove the answer content is correct.

Required owner: Engineer. Reproduce why the targeted warm path emits the corrected source-16 answer while the full-matrix item emits the older mixed answer. QA must rerun the complete matrix after the fix is made repeatable; no one-item warm self-test may replace the failed full-matrix evidence.

### P2 — Item 1 is not the current content blocker

The fresh run passed item 1 with source 09 and persisted diagnostic `398` at `1,310 ms` plus delivery `399` at `2,231 ms`. Cold/idle repeatability remains an operational risk because the Engineer observed a separate post-restart transient, but item 1 is not a failure in this matrix.

### P2 — v12 cash/closing fix remains closed for content completeness

Items 5 and 6 independently pass the mandatory checks in the actual Telegram UI, including the 20.55 cash count and the closing customer-flow/AC/lamp/music/POS facts.

## Coverage boundary

Still unverified: live fault injection beyond observed paths, provider/database fault matrix, duplicate/concurrency behavior on current v9, clean-instance import/rebind, Security audit, Human quality approval, release, and cleanup/revocation. This report does not authorize release.

## Status and handoff

M7 remains **FAIL / NOT_VERIFIED**. The next owner is **Engineer** to make the item-7 source-16 rescue deterministic/repeatable across the full matrix; QA then reruns the full 15-item matrix. The Engineer targeted self-test is preserved as implementer evidence only and does not replace this failed QA run.

Artifacts:

- `evaluation/run_v15-item7-fix-full-matrix-2026-09-21.jsonl`
- `evaluation/run_v15-item7-fix-full-matrix-2026-09-21_config.json`
- `evaluation/run_v15-item7-fix-full-matrix-2026-09-21_summary.md`
- `.ai/project-state.md`
