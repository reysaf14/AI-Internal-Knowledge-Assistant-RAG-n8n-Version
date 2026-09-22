# M7 Independent QA v13 — Engineer v12 Cash/Closing Fix Full Matrix

Date: 2026-09-21  
Timezone: Asia/Jakarta  
Project/lane: Asisten Pengetahuan Internal Toko Makmur Jaya / PROFESSIONAL  
Executor: QA, independent of Engineer implementation and report  
Candidate: Engineer v12 / runtime v8  
Verdict: FAIL — NOT RELEASE READY

## Objective and evidence rule

This run independently verifies the Engineer v12 cash/closing completeness fix against the approved 12 supported + 3 unsupported evaluation dataset. The Engineer report was used only to identify the candidate and intended remediation scope. The verdict is based on the current Telegram Web UI, the current active workflow/runtime, and newly persisted PostgreSQL evidence.

No credentials, raw Telegram payloads, provider bodies, or production data were read or stored. The sanitized per-item record is persisted in the v13 JSONL artifact.

## Candidate freeze

| Artifact/runtime | Observed evidence |
|---|---|
| Workflow | ID IAOqkQsNamEJarHF; local export parses with 37 nodes |
| Workflow export SHA-256 | 7ED4468C13E8BC8DF82780CC55D516BCEB5F05BB01206121F70A3D14907B767B |
| Dataset SHA-256 | 6B4587A7DCB7EB04630801D7073F7424ED8274D7245746A3C82CD658DFF60614 |
| Evaluation README SHA-256 | FD9BDAE3F1B0CB9D7C51D1F40F1A06AA95850AA674EB95DD07029A5CA56259EC |
| Runtime revision | cloud-chat-local-embedding-2026-09-21-v8 |
| Chat | DeepSeek deepseek-flash |
| Embedding | local embeddinggemma:300m-qat-q4_0, profile dimension 768 |
| Retrieval | limit 5; minimum similarity 0.25 |
| Bounds | context 6500; output 256; AI timeout 4000 ms |
| Active corpus | sha256:61b7301108de25c111d815812e8695f150e4e958dbbd9c40dd03dfd1baa6d109; 26 documents, 297 chunks |
| Temperature | 0 |

## Preconditions and execution

- rag-n8n-local was healthy; rag-postgres-local was healthy.
- Telegram Web was authenticated in the AgnesTachyon bot chat.
- All 15 questions were sent sequentially in a fresh visible Telegram Web tab, and all 15 question/answer pairs were visible in the UI.
- Item 1 returned the service-unavailable fallback. The run was not silently retried; its failure is retained as part of this matrix.
- The UI has no process exit code; persisted receipt, diagnostic, and delivery rows are the acceptance evidence.

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
| rag.telegram_updates | 223 | 238 | +15 |
| rag.safe_events | 285 | 314 | +29 |

New Telegram receipt rows were IDs 225–239. All 15 have status `delivered`; item 1 retains error category `chat_completion_failure`, while items 2–15 have an empty error category.

New safe events were IDs 332–360:

- delivery events: 332, 334, 336, 338, 340, 342, 344, 346, 348, 350, 352, 354, 356, 358, 360 — 15/15 persisted with status `success`;
- grounding diagnostics: 333, 335, 337, 339, 341, 343, 345, 347, 349, 351, 353, 355, 357, 359 — 14/15 persisted with status `success`;
- item 1 has no persisted `grounding_diagnostic` row in this run. Its delivery event 332 is `success` at 4,985 ms but retains `chat_completion_failure`.

Delivery durations were 1,174–4,985 ms. All 15 delivery events were below the 5,000 ms target.

## Independent matrix

The CSV rubric requires all mandatory supported facts, no contradiction, and a relevant source. Unsupported questions must abstain without citation. The exact sanitized per-item record is in `evaluation/run_v13-engineer-v12-cash-closing-fix-2026-09-21.jsonl`.

| Item | Observed result | Diagnostic / delivery | Verdict |
|---:|---|---|---|
| 1 | Service-unavailable fallback; no answer, no source, persisted `chat_completion_failure` | missing / 332; — / 4,985 ms | FAIL |
| 2 | Parking answer includes 10 motor, 5 mobil, free; source 09 | 333 / 334; 994 / 1,943 ms | PASS |
| 3 | Return/exchange policy grounded in source 11 | 335 / 336; 1,781 / 2,681 ms | PASS |
| 4 | Opening SOP complete with alarm, sales-area check, POS/printer, QRIS/card reader, AC, cash float; source 01 | 337 / 338; 1,911 / 2,825 ms | PASS |
| 5 | Explicitly includes cash count at 20.55, expense proof, QRIS/debit, reconciliation, cash float, safe, forms/logs; source 03 | 339 / 340; 2,121 / 3,012 ms | PASS |
| 6 | Explicitly includes stop-new-customer at 20.50, complete checkout, cleaning, and 21.00 AC/lamp/music/POS shutdown; source 02 | 341 / 342; 1,849 / 2,747 ms | PASS |
| 7 | Damaged-goods complaint procedure grounded in source 16 | 343 / 344; 2,014 / 2,926 ms | PASS |
| 8 | Late-delivery escalation grounded in source 18 | 345 / 346; 1,466 / 2,370 ms | PASS |
| 9 | 12 annual-leave days after one year; source 20 | 347 / 348; 1,292 / 2,129 ms | PASS |
| 10 | Sick-leave boundary includes up to 2 days without letter and over 2 days with doctor letter; source 20 | 349 / 350; 1,282 / 2,257 ms | PASS |
| 11 | K3 APAR and evacuation-route answer grounded in source 25 | 351 / 352; 1,048 / 1,938 ms | PASS |
| 12 | Address correct; relevant source 09, with known CSV canonical-label nuance | 353 / 354; 1,084 / 1,942 ms | PASS |
| 13 | Unsupported salary returns exact official-document abstention with no citation | 355 / 356; 1,101 / 2,164 ms | PASS |
| 14 | Unsupported travel-claim question returns exact official-document abstention with no citation | 357 / 358; 1,023 / 1,935 ms | PASS |
| 15 | Unsupported manager-loan question returns exact official-document abstention with no citation | 359 / 360; 257 / 1,174 ms | PASS |

## Aggregate gates

- Content/abstention: 14/15 pass.
- Supported: 11/12 pass; item 1 fails.
- Unsupported: 3/3 pass.
- Relevant source citation: 11/12 supported cases pass; item 1 has no citation, and item 12 retains the known source-label nuance.
- Delivery: 15/15 persisted as delivered.
- Latency: 15/15 under 5,000 ms; range 1,174–4,985 ms.
- Diagnostic persistence: 14/15; item 1 missing.
- Deterministic regression: 67/67 pass.

The required semantic content gate is 15/15 and the diagnostic persistence gate is also incomplete. Therefore the independent live matrix is FAIL. Successful Telegram delivery and sub-five-second latency do not make the fallback answer acceptable.

## Findings

### P1 — Current v8 chat-completion failure remains on item 1

The first supported question returned `Layanan pengetahuan sedang tidak tersedia. Silakan coba lagi nanti.` instead of the grounded Monday-hours answer. Persisted evidence records:

- Telegram update 225: `delivered`, error category `chat_completion_failure`;
- delivery safe event 332: `success`, 4,985 ms, error category `chat_completion_failure`;
- no corresponding `grounding_diagnostic` row for item 1.

This is a current provider/runtime chat-completion failure path, not an oracle mismatch and not a model-quality omission. It blocks repeatable full-matrix acceptance. The prior v12 item-1 failure pattern means a single later success would not silently erase this failed attempt; repeatability still needs evidence.

### P1 — v12 cash/closing content fix is independently confirmed

Items 5 and 6 now pass the approved mandatory content checks in the actual Telegram UI:

- item 5 includes the explicit 20.55 cash-count requirement;
- item 6 includes stopping new customers, completing active checkout, and switching off AC, sales lamps, background music, and POS at 21.00.

This finding is therefore closed for content completeness on this run.

### P2 — Source-label nuance remains

Item 12 cites relevant active source 09 while the CSV retains the previously recorded canonical-label difference. The source is relevant and contains the observed address, so this remains a traceability nuance rather than a new blocker.

## Coverage boundary

Still unverified: live fault injection beyond this observed chat-completion failure, provider/database fault matrix, duplicate/concurrency on the current v8 candidate, clean-instance import/rebind, Security, Human quality approval, release, and cleanup/revocation. This report does not authorize release.

## Handoff

Engineer owns investigation of the current v8 `chat_completion_failure` path and diagnostic omission for item 1. QA should rerun the complete 15-item matrix after the shared runtime/provider fix, with no silent substitution of this failed attempt. M7 remains FAIL / NOT_VERIFIED until the semantic content and diagnostic-persistence gates pass consistently.

Artifacts:

- `evaluation/run_v13-engineer-v12-cash-closing-fix-2026-09-21.jsonl`
- `evaluation/run_v13-engineer-v12-cash-closing-fix-2026-09-21_config.json`
- `evaluation/run_v13-engineer-v12-cash-closing-fix-2026-09-21_summary.md`
- `.ai/reports/build/M7-v12-cash-closing-completeness-fix-2026-09-21.md`

