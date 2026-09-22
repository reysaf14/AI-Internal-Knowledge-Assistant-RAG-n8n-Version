# M7 — Independent QA Re-test Report

## Objective and scope

- Project: Asisten Pengetahuan Internal Toko Makmur Jaya
- Lane: `PROFESSIONAL`; Architecture `1.2`; Acceptance Matrix `1.0`
- Source finding: `.ai/reports/qa/M7-independent-qa-2026-09-20.md`
- Remediation assessed: `.ai/reports/build/M7-engineer-remediation-2026-09-20.md`
- Candidate: uncommitted remediation working tree; workflow 01 SHA-256 `44B96B9D3CA8710C37DE9C0496FB1D191D4D7398EA36AB91182E88FB948590D3`; workflow 02 SHA-256 `B7595B85FF5BBB2EDDF0582E65A1360876C824572EFC11062683D5593F1C490A`; dataset unchanged SHA-256 `B5FCAA7C40D8C6A56F09691B50BCAB8631910179C519A98CC83ABBE3539B1882`
- Executor: QA independen; Engineer remediation report tidak diperlakukan sebagai bukti QA
- Timestamp: `2026-09-20` (`Asia/Jakarta`); shell/cwd: PowerShell; project root
- Runtime: Python `3.11.15`; n8n `1.123.81`; PostgreSQL/pgvector `pg16`
- Re-test scope: AC-001–AC-024 dan regresi connected setelah bounded-timeout, ingestion-budget, workflow-sync, dan test-harness changes
- Excluded: Security, production/demo-vps, real Telegram message send, destructive cleanup/revocation

## Independent execution evidence

| Check | Exact command / observation | Expected → observed | Exit / status |
|---|---|---|---|
| M2 regression | `python tests/harness/test_ingestion.py` | 19 tests → 19 passed | `0`, PASS at mock/contract level |
| M3 regression | `python tests/harness/test_qa_core.py` | 21 tests → 21 passed | `0`, PASS at mock/contract level |
| M4 regression | `python tests/harness/test_delivery_core.py` | 27 tests → 27 passed; no prior traceback/resource warning | `0`, PASS at mock/contract level |
| Runtime health | `curl.exe ... /healthz` and `/healthz/readiness` | HTTP 200 `{"status":"ok"}` → observed | PASS readiness only |
| Runtime containers | `docker ps --format '{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}'` | n8n/PostgreSQL healthy, loopback-bound → observed | `0`, PASS target readiness |
| Candidate settings | Sanitized PostgreSQL query | revision `m6-local-gemma-bounded-2026-09-20`; chat `gemma4:e2b-it-qat`; embedding dimension `768`; online timeout `3000ms`; ingest timeout `120000ms` → observed | PASS configuration presence |
| Active workflow metadata | Sanitized `n8n.workflow_entity` query | workflow 02 original `active=true`, 34 nodes, bounded deadline markers present; duplicate inactive → observed | PASS active remediation marker |
| Live ingestion | `docker exec rag-n8n-local sh -c 'n8n execute --id=5E9eQbknShf6iskV --rawOutput >/dev/null 2>/dev/null; rc=$?; printf ...'` | n8n exit `0` → observed | PASS valid rerun |
| Live corpus post-check | Sanitized PostgreSQL aggregate query | one active version; 26 docs; 297 chunks; 26 sources; dimension 768..768; staging/failed `0` → observed | PASS valid/idempotent boundary |
| Invalid webhook boundary | POST to registered local route without Telegram secret | HTTP 403 `Provided secret is not valid` → observed | PASS bad-secret branch only |

No secrets, raw Telegram payloads, questions/answers, chat IDs, or credential values were included in this report.

## Requirement / AC re-test results

| AC / requirement / test | Level | Expected → observed | Verdict | Evidence |
|---|---|---|---|---|
| `AC-001 / REQ-001 / T-RERUN-001` | live isolated | valid ingest activates complete corpus → exit 0; one active version; 26 docs; 297 chunks; 26 sources; dimension 768 | `PASS` within valid happy path | live rerun + sanitized DB post-check |
| `AC-002, AC-004, AC-005 / REQ-001 / T-RERUN-002` | required fault integration | invalid corpus, timeout, provider/auth/5xx/dimension/DB failure preserve old corpus → mock cases pass; current n8n fault injection not executed | `NOT_VERIFIED` | M2 `19/19` mock only |
| `AC-003 / REQ-001 / T-RERUN-003` | isolated concurrency | sequential and near-concurrent duplicate triggers are safe → sequential rerun remained 297 chunks/one active version; live concurrency not executed | `PASS_WITH_LIMITATIONS` | live sequential boundary; concurrency gap |
| `AC-006 / REQ-002 / T-RERUN-004` | approved Telegram E2E | valid allowed update produces one readable response and delivered state → no valid current-candidate Telegram message sent | `NOT_VERIFIED` | invalid-secret only |
| `AC-007 / REQ-002 / T-RERUN-005` | sandbox integration | all invalid branches stop before retrieval/send → bad-secret 403 observed; wrong-chat/non-message/empty-text only mock-tested | `NOT_VERIFIED` | live route + M4 mock |
| `AC-008–AC-010 / REQ-002 / T-RERUN-006` | fault/concurrency integration | dedup, timeout/ambiguity, auth/rate-limit/5xx remain bounded and non-duplicating → regression mock passes; live matrix not executed; existing ledger remains 23 delivered/8 unknown without frozen-run mapping | `NOT_VERIFIED` | M4 `27/27` mock; sanitized ledger aggregate |
| `AC-011–AC-020 / REQ-003–REQ-005 / T-RERUN-007` | approved real-model E2E + rubric | 12/15 content, 12/12 sources, 3/3 abstention, injection/failure safety → no current real-model 15-item semantic run; CSV remains `DRAFT` pending Human semantic approval | `NOT_VERIFIED` | M3 `21/21` mock only |
| `AC-021 / REQ-006 / T-RERUN-008` | required 15-item E2E | every item `<5,000ms` from receive to Telegram success → not executed | `NOT_VERIFIED` | bounded control is not latency evidence |
| `AC-022–AC-024 / REQ-006 / T-RERUN-009` | fault E2E / exploratory | bounded AI failure behavior and cold/warm evidence → bounded code/config and mock timeout pass; live fault/current-candidate benchmark not executed | `NOT_VERIFIED` | workflow markers + M4 mock |
| `AC-025–AC-026 / REQ-007 / T-RERUN-010` | clean import/config | clean instance imports/rebinds and fails closed → current active workflow metadata is coherent; clean-instance import/rebind not independently executed | `NOT_VERIFIED` | static/live metadata partial |
| `AC-027 / REQ-007 / T-RERUN-011` | scoped cleanup | exact authorized target is unpublished/revoked/removed → not run; no cleanup authorization | `NOT_VERIFIED` | Human/DevOps gate |

## Remediation assessment

- The timeout-remediation control is independently observed in source and active runtime metadata: online `3000ms`, business deadline `5000ms`, delivery reserve `1000ms`, and remaining-budget calculation before embedding/chat.
- Ingestion uses a separate `120000ms` batch budget, and the live rerun preserved the active corpus without duplicate chunks.
- Test harness hygiene remediation is confirmed by the independent clean regression output: no prior client-abort traceback or fixture `ResourceWarning` appeared.
- These results verify remediation controls and regression behavior, not the required Telegram E2E or semantic/latency acceptance gates.

## Coverage and remaining gaps

- Mock/contract regression: `67/67` passed with exit code `0`.
- Current live complete required behavior: `AC-001` valid ingestion only.
- Current live partial behavior: sequential portion of `AC-003`; bad-secret portion of `AC-007`.
- Required current-candidate live/fault/E2E proof remains missing for `AC-002`, `AC-004`–`AC-023`, and `AC-025`–`AC-027` except the partial boundaries above.
- The evaluation file has the correct structural `12 supported + 3 unsupported` shape, but `evaluation/README.md` still marks it `DRAFT`; Human approval/freeze of semantic keys and sources is absent.
- Existing `delivery_unknown` records are not mapped to this frozen bounded candidate and cannot be counted as a current 15-item result.

## Status and gate

**Overall QA re-test verdict: `NOT_VERIFIED`.**

The remediation is verified at the control, regression, and live ingestion boundaries. Required real Telegram delivery, semantic scoring, current 15-item latency, live fault/concurrency cases, and clean-instance portability are still unproven. This status is not release approval.

## Next owner / action

1. Human approves/freezes the synthetic 12+3 semantic key/source set and authorizes the exact Telegram sandbox target for valid-message testing.
2. QA executes the current sequential 15-item E2E and live fault/concurrency matrix against revision `m6-local-gemma-bounded-2026-09-20`.
3. QA reruns affected ACs after any failure; Security remains a separate independent gate.
