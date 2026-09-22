# M7 Independent QA v12 — Deterministic Completeness Rescue Full Matrix

Date: 2026-09-21  
Timezone: Asia/Jakarta  
Project/lane: Asisten Pengetahuan Internal Toko Makmur Jaya / PROFESSIONAL  
Executor: QA, independent of Engineer implementation and report  
Verdict: FAIL — NOT RELEASE READY

## Objective and evidence rule

This run independently verifies the Engineer's v11 deterministic completeness rescue against the approved 12 supported + 3 unsupported evaluation dataset. The Engineer report was used only to identify the candidate and intended remediation scope. The verdict is based on the current Telegram Web UI, the current active workflow/runtime, and newly persisted PostgreSQL evidence.

No credentials, raw Telegram payloads, provider bodies, or production data were read or stored. The result is persisted in the per-item JSONL and this report.

## Candidate freeze

| Artifact/runtime | Observed evidence |
|---|---|
| Workflow | ID IAOqkQsNamEJarHF; local export parses with 37 nodes |
| Workflow export SHA-256 | 8945D3D92C0DC9A75FA60DDFB4BBC21C1907B342BCFB6A10DF0156455A5818F3 |
| Dataset SHA-256 | 6B4587A7DCB7EB04630801D7073F7424ED8274D7245746A3C82CD658DFF60614 |
| Evaluation README SHA-256 | FD9BDAE3F1B0CB9D7C51D1F40F1A06AA95850AA674EB95DD07029A5CA56259EC |
| Runtime revision | cloud-chat-local-embedding-2026-09-21-v7 |
| Chat | DeepSeek deepseek-flash |
| Embedding | local embeddinggemma:300m-qat-q4_0, profile dimension 768 |
| Retrieval | limit 5; minimum similarity 0.25 |
| Bounds | context 6500; output 256; AI timeout 4000 ms |
| Active corpus | sha256:61b7301108de25c111d815812e8695f150e4e958dbbd9c40dd03dfd1baa6d109; 26 documents, 297 chunks |
| Temperature | 0 |

## Preconditions and execution

- rag-n8n-local was healthy; n8n healthz HTTP 200 and readiness HTTP 200.
- rag-postgres-local was healthy and available for persisted evidence.
- Telegram Web was authenticated in the AgnesTachyon chat.
- A fresh browser tab was used for the actual matrix. All 15 questions were sent sequentially and all 15 answer pairs were visible in the UI.
- The UI has no process exit code; persisted receipt, diagnostic, and delivery rows are the acceptance evidence.
- The run was performed after the current n8n/browser refresh condition. No Engineer report is treated as proof of semantic correctness.

Independent deterministic regression:

| Command | Expected | Observed | Exit |
|---|---:|---:|---:|
| python tests/harness/test_ingestion.py | 19 | 19/19 | 0 |
| python tests/harness/test_qa_core.py | 21 | 21/21 | 0 |
| python tests/harness/test_delivery_core.py | 27 | 27/27 | 0 |
| Total | 67 | 67/67 | 0 |

## Persisted before/after evidence

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| rag.telegram_updates | 208 | 223 | +15 |
| rag.safe_events | 255 | 285 | +30 |

New telegram_updates IDs were 210–224. All 15 were delivered, had an empty error category, and used runtime revision `cloud-chat-local-embedding-2026-09-21-v7`.

New safe_events IDs were 302–331:

- grounding diagnostics: 302, 304, 306, 308, 310, 312, 314, 316, 318, 320, 322, 324, 326, 328, 330 — 15/15 `success`;
- delivery events: 303, 305, 307, 309, 311, 313, 315, 317, 319, 321, 323, 325, 327, 329, 331 — 15/15 `success`.

Diagnostic durations were 251–3,996 ms. Delivery durations were 1,352–4,891 ms. Every delivery was below the 5,000 ms target.

## Independent matrix

The CSV rubric requires all mandatory supported facts, no contradiction, and a relevant source. Unsupported questions must abstain without citation. The exact sanitized per-item record is in `evaluation/run_v12-deterministic-completeness-rescue-2026-09-21.jsonl`.

| Item | Required result and observed result | Diagnostic / delivery | Verdict |
|---:|---|---|---|
| 1 | Monday 07.00–21.00 answered correctly; relevant source 09, with the known CSV canonical-label nuance | 302 / 303; 3,996 / 4,891 ms | PASS |
| 2 | Parking: 10 motor, 5 mobil, free; source 09 | 304 / 305; 980 / 1,895 ms | PASS |
| 3 | Return/exchange policy grounded in source 11 | 306 / 307; 1,726 / 2,716 ms | PASS |
| 4 | Opening SOP rescue includes 06.30–07.00, alarm/security, sales area, POS/printer, QRIS/card reader, AC, and cash float; source 01 | 308 / 309; 1,713 / 2,598 ms | PASS |
| 5 | Cash/setoran rescue covers schedule, expense proof, QRIS/debit, reconciliation, cash float, safe, forms/logs, but omits the mandatory explicit cash count at 20.55 | 310 / 311; 1,892 / 2,893 ms | FAIL |
| 6 | Closing rescue covers timing, patrol/cleaning, two-witness count, payment reconciliation, alarm, locks, and documentation, but omits explicit stop-new-customer/serve-checkout flow and lamp/music/POS shutdown | 312 / 313; 2,196 / 3,080 ms | FAIL |
| 7 | Damaged-goods complaint procedure grounded in source 16 | 314 / 315; 2,160 / 3,079 ms | PASS |
| 8 | Late-delivery escalation grounded in source 18 | 316 / 317; 998 / 1,905 ms | PASS |
| 9 | 12 annual-leave days after one year; source 20 | 318 / 319; 1,744 / 2,622 ms | PASS |
| 10 | Sick-leave boundary: up to 2 days without letter; over 2 days requires doctor letter; source 20 | 320 / 321; 1,104 / 1,993 ms | PASS |
| 11 | K3 rescue includes APAR access/placement, clear emergency route, and team awareness; source 25 | 322 / 323; 1,046 / 1,889 ms | PASS |
| 12 | Address answered correctly; relevant source 09, with the known CSV canonical-label nuance | 324 / 325; 1,035 / 1,983 ms | PASS |
| 13 | Unsupported salary question returns exact official-document abstention with no citation | 326 / 327; 1,238 / 2,213 ms | PASS |
| 14 | Unsupported travel-claim question returns exact official-document abstention with no citation | 328 / 329; 1,059 / 1,937 ms | PASS |
| 15 | Unsupported manager-loan question returns exact official-document abstention with no citation | 330 / 331; 251 / 1,352 ms | PASS |

## Aggregate gates

- Content/abstention: 13/15 pass.
- Supported: 10/12 pass; failures are items 5 and 6.
- Unsupported: 3/3 pass.
- Relevant source citation: 12/12 supported cases cite a relevant active source. Items 1 and 12 retain the previously recorded CSV canonical-label nuance.
- Delivery: 15/15 pass.
- Latency: 15/15 pass under 5,000 ms; delivery range 1,352–4,891 ms.
- Diagnostic persistence: 15/15 pass.
- Deterministic regression: 67/67 pass.

The required semantic content gate is 15/15. Therefore the independent live matrix is FAIL. Delivery, latency, diagnostics, and deterministic harness results do not override the two content failures.

## Findings

### P1 — Item 5 remains incomplete despite deterministic rescue

The current answer is source-grounded and includes the main cash/setoran sections, but it does not explicitly state the mandatory fact that cash is counted at 20.55. This is a content-completeness failure, not a Telegram delivery or diagnostic-persistence failure.

Engineer action required: update the deterministic rescue or equivalent response path so the observed answer explicitly contains the 20.55 cash-count fact, then rerun item 5 and the full matrix.

### P1 — Item 6 remains incomplete despite deterministic rescue

The current answer is source-grounded and includes closing activities, but it does not explicitly state:

- stop accepting new customers and serve customers already in checkout;
- switch off the lamp, music, and POS as required by the approved oracle.

This is a content-completeness failure, not a Telegram delivery or diagnostic-persistence failure.

Engineer action required: update the deterministic rescue or equivalent response path so the observed answer explicitly contains the customer-flow and shutdown-device facts, then rerun item 6 and the full matrix.

### P2 — Source-label nuance remains

Items 1 and 12 cite the relevant active source 09 while the CSV retains canonical labels 21 and 00. The cited source contains the observed facts, so this remains a traceability nuance rather than a new blocker.

## Coverage boundary

Still unverified: live fault injection, provider/database fault paths, duplicate/concurrency on the current candidate, clean-instance import/rebind, Security, Human quality approval, release, and cleanup/revocation. This report does not authorize release.

## Handoff

Engineer owns fixes for items 5 and 6. After the shared workflow change, QA must rerun item 5, item 6, and the complete 15-item matrix, checking content, citation/source relevance, delivery, latency, and diagnostic persistence. M7 remains FAIL / NOT_VERIFIED until the full content gate reaches 15/15 and the separate remaining gates are addressed.

Artifacts:

- `evaluation/run_v12-deterministic-completeness-rescue-2026-09-21.jsonl`
- `evaluation/run_v12-deterministic-completeness-rescue-2026-09-21_config.json`
- `evaluation/run_v12-deterministic-completeness-rescue-2026-09-21_summary.md`
- `.ai/reports/build/M7-v11-deterministic-completeness-rescue-2026-09-21.md`

