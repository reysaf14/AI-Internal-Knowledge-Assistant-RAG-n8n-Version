# M7 Independent QA v16 — Item-7 Delivery Contract Full Matrix

Date: 2026-09-21  
Timezone: Asia/Jakarta  
Project/lane: Asisten Pengetahuan Internal Toko Makmur Jaya / PROFESSIONAL  
Executor: QA, independent of Engineer targeted and full-matrix self-tests  
Candidate: runtime v10 / Engineer item-7 delivery-contract fix  
Semantic matrix verdict: PASS  
Overall M7 status: NOT_VERIFIED — broader required gates remain open

## Objective and evidence rule

This run independently reruns the approved 12 supported + 3 unsupported Telegram matrix after the Engineer reported a strict item-7 delivery contract and runtime v10 self-tests. Engineer evidence is context only and is not counted as QA proof. The semantic verdict below is based on the fresh Telegram Web interaction, active workflow/runtime, and newly persisted PostgreSQL evidence.

No credentials, raw Telegram payloads, provider bodies, or production records were read or stored. The per-item artifact is sanitized.

## Candidate freeze

| Artifact/runtime | Observed evidence |
|---|---|
| Workflow | ID `IAOqkQsNamEJarHF`; local export parses with 37 nodes |
| Workflow export SHA-256 | `6F12DA416F362A9E602C4872878BCCF7BC8516FDCB73AC82F08697DEDB388E14` |
| Dataset SHA-256 | `6B4587A7DCB7EB04630801D7073F7424ED8274D7245746A3C82CD658DFF60614` |
| Evaluation README SHA-256 | `FD9BDAE3F1B0CB9D7C51D1F40F1A06AA95850AA674EB95DD07029A5CA56259EC` |
| Runtime revision | `cloud-chat-local-embedding-2026-09-21-v10` |
| Chat | DeepSeek `deepseek-flash` |
| Embedding | local `embeddinggemma:300m-qat-q4_0`, profile dimension 768 |
| Retrieval | limit 5; minimum similarity 0.25 |
| Bounds | context 6500; output 256; AI timeout 4000 ms |
| Active corpus | `sha256:61b7301108de25c111d815812e8695f150e4e958dbbd9c40dd03dfd1baa6d109`; 26 documents, 297 chunks |

## Preconditions and execution

- `rag-n8n-local` and `rag-postgres-local` were healthy before execution.
- Telegram Web was logged in to the `AgnesTachyon` bot chat.
- The 15 dataset questions were entered sequentially in the visible Telegram Web session. The UI showed 15/15 question/answer pairs; current fresh messages were timestamped approximately 20:15–20:17 Asia/Jakarta.
- Manual UI exit code: `NOT_APPLICABLE` because acceptance evidence is visual UI observation plus persisted receipts/events, not a process exit code.
- Engineer targeted/full-matrix self-tests and the prior cold timeout were excluded from this run's acceptance count.

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
| `rag.telegram_updates` | 289 | 304 | +15 |
| `rag.safe_events` | 414 | 444 | +30 |

New receipt rows were IDs `291–305`; all 15 were `delivered`, used runtime v10, and had empty error categories. New safe events were IDs `461–490`: 15 `grounding_diagnostic` events and 15 `delivery` events, all `status=success`. Delivery durations were `1,226–3,682 ms`; all were below the 5,000 ms target.

## Independent matrix

The approved rubric requires all supported mandatory facts, no contradiction or unsupported policy claim, and a relevant source. Unsupported questions must abstain without citation. The exact sanitized per-item record is in `evaluation/run_v16-item7-delivery-contract-full-matrix-2026-09-21.jsonl`.

| Item | Observed result | Diagnostic / delivery | Verdict |
|---:|---|---|---|
| 1 | Monday hours `07.00–21.00`, source 09; fresh-run pass | 461 / 462; 1,040 / 2,059 ms | PASS, source-label nuance |
| 2 | Parking answer includes approximately 10 motorbikes, 5 cars, free; source 09 | 463 / 464; 1,263 / 2,195 ms | PASS |
| 3 | Return/exchange boundary grounded in source 11 | 465 / 466; 1,826 / 2,807 ms | PASS |
| 4 | Opening SOP complete; deterministic rescue; source 01 | 467 / 468; 2,113 / 3,154 ms | PASS |
| 5 | Cash SOP includes 20.55 count, evidence, QRIS/debit, reconciliation, cash float, safe, setoran, logs; source 03 | 469 / 470; 2,009 / 3,682 ms | PASS |
| 6 | Closing SOP includes customer-flow boundary, active checkout, two-witness count, QRIS/debit, AC/lamp/music/POS shutdown, alarm/locks/log; source 02 | 471 / 472; 2,152 / 3,075 ms | PASS |
| 7 | Separate store-side and home-side date scenarios, source 16, no false abstention or unresolved date mix | 473 / 474; 1,755 / 2,767 ms | PASS |
| 8 | Late-delivery procedure grounded in source 18 | 475 / 476; 1,768 / 2,363 ms | PASS |
| 9 | 12 annual-leave days; source 20 | 477 / 478; 1,395 / 2,374 ms | PASS |
| 10 | Sick-leave boundary: up to 2 days without letter; over 2 days with doctor letter; source 20 | 479 / 480; 1,413 / 2,464 ms | PASS |
| 11 | K3 APAR and evacuation-route answer complete; source 25 | 481 / 482; 1,559 / 2,353 ms | PASS |
| 12 | Address correct; source 09 is relevant, with known CSV canonical-label nuance | 483 / 484; 1,340 / 2,065 ms | PASS, source-label nuance |
| 13 | Exact official-document abstention; no citation | 485 / 486; 1,158 / 2,014 ms | PASS |
| 14 | Exact official-document abstention; no citation | 487 / 488; 912 / 1,226 ms | PASS |
| 15 | Exact official-document abstention; no citation; support-gate stage | 489 / 490; 273 / 1,292 ms | PASS |

## Aggregate gates

- Content/abstention: **15/15**.
- Supported: **12/12**.
- Unsupported: **3/3**.
- Delivery: **15/15** persisted as delivered.
- Latency: **15/15** under 5,000 ms; range **1,226–3,682 ms**.
- Diagnostic persistence: **15/15** new diagnostic rows, all success.
- Deterministic regression: **67/67** pass.
- Source relevance: **12/12** supported answers cite a semantically relevant active-corpus source. Exact dataset-label parity is **10/12** because item 1 cites source 09 instead of CSV canonical 21 and item 12 cites source 09 instead of CSV canonical 00; these remain traceability nuances carried from the approved corpus-backed interpretation.

The approved live semantic Telegram matrix is **PASS**. This does not authorize release or close M7 overall: required broader evidence is still missing.

## Findings

### P1 — None observed in the approved 15-item semantic matrix

Item 7 is independently fixed in the full matrix. The visible answer uses the source-16 delivery contract, separates store-side and home-side rules, and contains neither the old date-conflict composition nor the generic abstention sentence. Persisted diagnostic `473` and delivery `474` are successful; delivery is `2,767 ms`.

### P2 — Source-label traceability nuance remains

Items 1 and 12 cite relevant source 09 while the CSV retains different canonical source labels. This is not a new behavioral failure and is retained for traceability review.

### P2 — Cold/idle provider behavior remains outside this passing matrix

Engineer observed a separate post-restart timeout before its warm self-test. This fresh matrix had no delivery failure and all items met the latency gate, but it does not prove cold-start repeatability.

## Coverage boundary

Overall M7 remains **NOT_VERIFIED** for this lane because the following are still untested or separately owned: live fault injection beyond observed paths, provider/database fault matrix, duplicate/concurrency behavior on current v10, clean-instance import/rebind, Security audit, Human quality/release approval, and cleanup/revocation. This report does not authorize release.

## Status and handoff

Semantic 15-item acceptance is **PASS**. Overall M7 is **NOT_VERIFIED** pending the broader required gates. Next owner: Human decides the next gate (Security / further operational validation); no release decision is implied. QA evidence is complete for this semantic matrix.

Artifacts:

- `evaluation/run_v16-item7-delivery-contract-full-matrix-2026-09-21.jsonl`
- `evaluation/run_v16-item7-delivery-contract-full-matrix-2026-09-21_config.json`
- `evaluation/run_v16-item7-delivery-contract-full-matrix-2026-09-21_summary.md`
- `.ai/project-state.md`
