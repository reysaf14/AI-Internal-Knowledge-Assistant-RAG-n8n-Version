# M7 Independent QA v11 — Content-Completeness Full Matrix

Date: 2026-09-21  
Timezone: Asia/Jakarta  
Project/lane: Asisten Pengetahuan Internal Toko Makmur Jaya / PROFESSIONAL  
Executor: QA, independent of Engineer implementation and report  
Verdict: FAIL — NOT RELEASE READY

## Objective and evidence rule

This rerun independently tests the Engineer content-completeness remediation against the approved 12 supported + 3 unsupported evaluation dataset. Engineer evidence was used only to identify the intended candidate and remediation scope. The verdict is based on the current Telegram UI, the current workflow/runtime, and newly persisted PostgreSQL telemetry.

No credentials, raw Telegram payloads, provider bodies, or production data were read or stored.

## Candidate freeze

| Artifact/runtime | Observed evidence |
|---|---|
| Workflow | ID IAOqkQsNamEJarHF; local export parses with 37 nodes |
| Workflow export SHA-256 | 81233BBFCE9684BEACF94F81D3AD1FEA90D2408F25A1A5A81525A5C47C5BA440 |
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

- rag-n8n-local: healthy; n8n healthz HTTP 200 and readiness HTTP 200.
- rag-postgres-local: healthy; PostgreSQL/pgvector runtime available.
- Regression commands were executed independently:

| Command | Expected | Observed | Exit |
|---|---:|---:|---:|
| python tests/harness/test_ingestion.py | 19 | 19/19 | 0 |
| python tests/harness/test_qa_core.py | 21 | 21/21 | 0 |
| python tests/harness/test_delivery_core.py | 27 | 27/27 | 0 |
| Total | 67 | 67/67 | 0 |

Telegram Web was already authenticated. A fresh browser tab was used for the actual run. A stale-tab/input preparation error occurred before the first message and sent no text; after the fresh tab loaded, item 1 was sent once and items 2–15 were sent sequentially. UI observation confirmed all 15 question/answer pairs. The UI has no process exit code; persisted receipt and delivery rows are the acceptance evidence.

## Persisted before/after evidence

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| rag.telegram_updates | 187 | 202 | +15 |
| rag.safe_events | 214 | 244 | +30 |

New telegram_updates IDs were 189–203: 15/15 delivered, empty error category, v7 revision.

New safe_events were:

- diagnostics 261, 263, 265, 267, 269, 271, 273, 275, 277, 279, 281, 283, 285, 287, 289: 15/15 grounding_diagnostic/success;
- delivery 262, 264, 266, 268, 270, 272, 274, 276, 278, 280, 282, 284, 286, 288, 290: 15/15 delivery/success.

Diagnostic durations were 269–4,026 ms. Delivery durations were 1,148–4,901 ms. Every delivery was below the 5,000 ms acceptance target.

## Independent matrix

The CSV rubric requires all mandatory supported facts, no contradiction, and a relevant source. Unsupported questions must abstain without citation. The exact per-item sanitized record is in the JSONL artifact.

| Item | Expected → observed | Diagnostic / delivery | Verdict |
|---:|---|---:|---|
| 1 | 07.00–21.00 Monday → correct; source 09 relevant, CSV label nuance | 261 / 262; 4026 / 4901 ms | PASS |
| 2 | 10 motor, 5 mobil, free → all present; source 09 | 263 / 264; 1373 / 2413 ms | PASS |
| 3 | Return/exchange policy → grounded policy answer; source 11 | 265 / 266; 1561 / 2437 ms | PASS |
| 4 | Opening SOP requires alarm deactivation and sales-area check → answer did not state either explicitly | 267 / 268; 2140 / 3085 ms | FAIL |
| 5 | Cash SOP requires expense-proof records and QRIS/debit verification → answer mentioned related channels but did not state those mandatory facts explicitly; forms/log tail incomplete | 269 / 270; 2085 / 2990 ms | FAIL |
| 6 | Closing SOP requires cleaning → answer omitted explicit cleaning/housekeeping | 271 / 272; 2068 / 2965 ms | FAIL |
| 7 | Damaged-goods complaint procedure → grounded procedure; source 16 | 273 / 274; 1786 / 2679 ms | PASS |
| 8 | Late-delivery procedure → grounded third-party escalation; source 18 | 275 / 276; 1507 / 2412 ms | PASS |
| 9 | 12 annual-leave days → correct; source 20 | 277 / 278; 1685 / 2558 ms | PASS |
| 10 | Both sick-leave boundaries → both present; source 20 | 279 / 280; 1577 / 2615 ms | PASS |
| 11 | K3 APAR/route facts → UI returned official-document abstention although source 25 appeared in retrieval candidates | 281 / 282; 880 / 1735 ms | FAIL |
| 12 | Full address → correct; source 09 relevant, CSV label nuance | 283 / 284; 1122 / 2001 ms | PASS |
| 13 | Unsupported salary → exact abstention, no citation | 285 / 286; 876 / 1812 ms | PASS |
| 14 | Unsupported travel claim → exact abstention, no citation | 287 / 288; 1178 / 2053 ms | PASS |
| 15 | Unsupported manager loan → exact abstention, no citation; support gate | 289 / 290; 269 / 1148 ms | PASS |

## Aggregate gates

- Content/abstention: 11/15 pass.
- Supported: 8/12 pass; failures 4, 5, 6, 11.
- Unsupported: 3/3 pass.
- Relevant source citation: 11/12 supported cases; items 1 and 12 have relevant active-source citations but canonical-label differences.
- Delivery: 15/15 pass.
- Latency: 15/15 pass under 5,000 ms.
- Diagnostic persistence: 15/15 pass.
- Deterministic regression: 67/67 pass.

Because the required content gate is 15/15, the independent live matrix is FAIL. Delivery, latency, diagnostics, and deterministic harness are not sufficient to override the content failures.

## Findings

### P1 — Opening, cash/setoran, and closing answers still fail completeness

The current live answers for items 4–6 cite the correct SOPs and persist answered diagnostics, but the observed text omits mandatory facts from the approved oracle:

- item 4: explicit alarm deactivation and explicit sales-area check;
- item 5: expense records with proof and QRIS/debit verification; forms/log section is incomplete;
- item 6: explicit area cleaning/housekeeping.

This disproves the Engineer targeted claim as a full acceptance proof. The remaining issue is answer completeness, not Telegram receipt or telemetry persistence.

### P1 — Supported K3 question abstains

Item 11 returned Informasi tidak ditemukan di dokumen resmi. The diagnostic metadata shows K3 source candidates including 25_Kebijakan_Keselamatan_Kerja_K3_Sederhana.md, filtered=10, prompt=10, gate=pass, then model=model_abstention_text, validator=no_valid_citation, response=abstained. This is a supported-answer failure, not a valid unsupported-boundary result.

### P2 — Canonical source-label nuance remains

Items 1 and 12 cite active source 09 while the CSV labels remain 21 and 00. The cited source is relevant and contains the observed facts, so QA records this as a traceability nuance rather than silently rewriting the dataset.

## Coverage boundary

Still unverified: live fault injection, provider/database fault paths, duplicate/concurrency on the current DeepSeek candidate, clean-instance import/rebind, Security, Human quality approval, release, and cleanup/revocation. M7 remains FAIL / NOT_VERIFIED; this run does not authorize release.

## Handoff

Engineer owns fixes for items 4–6 and 11. After any shared prompt/retrieval/provider change, QA must rerun the affected items and the full 15-item matrix. Security and Human release gates remain separate.

Artifacts:

- evaluation/run_v11-content-completeness-2026-09-21.jsonl
- evaluation/run_v11-content-completeness-2026-09-21_config.json
- evaluation/run_v11-content-completeness-2026-09-21_summary.md
- .ai/reports/build/M7-content-completeness-remediation-2026-09-21.md
