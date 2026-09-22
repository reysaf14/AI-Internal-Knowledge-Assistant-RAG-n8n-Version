# M7 — Independent QA Execution Report

## Objective and scope

- Project: Asisten Pengetahuan Internal Toko Makmur Jaya
- Lane: `PROFESSIONAL`; Architecture `1.2`; Acceptance Matrix `1.0`
- Candidate reference: git `6cc818e26220759a478f095ad3d84ae59c34f9fb`; working tree has pre-existing untracked `.ai/` artifacts
- Tested artifact hashes: workflow 01 `601C0398869972E2E52861E5E43131006B484EDC496755074F9939FB9ED314F1`; workflow 02 `BCDAB6A09BBA9DDCE7D7A51906E741D6D911A8FFB22DD7168BAE4C77F588CE79`; dataset `B5FCAA7C40D8C6A56F09691B50BCAB8631910179C519A98CC83ABBE3539B1882`
- Executor: QA independen; bukan implementer laporan M0–M6
- Timestamp utama: `2026-09-20T11:29:20+07:00` (`Asia/Jakarta`)
- Shell/cwd: PowerShell; `C:\Freelance-Workspace\projects\active\AI Internal Knowledge Assistant (RAG) — n8n Version`
- Runtime: Python `3.11.15`; n8n `1.123.81`; PostgreSQL/pgvector `pg16`
- In scope: AC-001–AC-027, synthetic fixtures, local-isolated runtime, current Gemma-bound settings
- Excluded: Security audit, production/demo-vps, real Telegram message send, destructive cleanup/revocation; tidak ada otorisasi Human untuk aksi tersebut

## Evidence executed

| Check | Exact command / observation | Expected → observed | Exit / status |
|---|---|---|---|
| M2 regression | `python tests/harness/test_ingestion.py` | 19 tests → 19 passed | `0`, PASS at mock/contract level |
| M3 regression | `python tests/harness/test_qa_core.py` | 21 tests → 21 passed | `0`, PASS at mock/contract level |
| M4 regression | `python tests/harness/test_delivery_core.py` | 27 tests → 27 passed | `0`, PASS at mock/contract level |
| Runtime health | `GET /healthz`, `GET /healthz/readiness` on `127.0.0.1:5678` | HTTP 200 `{"status":"ok"}` → observed | PASS readiness only |
| Container target | `docker ps --format '{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}'` | n8n and PostgreSQL healthy → observed; both loopback-bound | `0`, PASS target readiness |
| Live ingestion | `docker exec rag-n8n-local sh -c 'n8n execute --id=5E9eQbknShf6iskV --rawOutput >/dev/null 2>/dev/null; rc=$?; printf "workflow=01|n8n_exit=%s\\n" "$rc"; exit 0'` | valid rerun → `n8n_exit=0` | `0`, PASS happy path |
| Live ingestion state | Sanitized PostgreSQL aggregate query before/after rerun | one active version; 26 docs; 297 chunks; 26 sources; dimensions 768..768; no staging/failed version → observed unchanged | PASS valid + sequential idempotency boundary |
| Invalid webhook boundary | `curl.exe -sS --max-time 10 -D - -X POST http://127.0.0.1:5678/webhook/e07e1904-256f-4192-a2e1-17c14c4caee4/webhook ...` without Telegram secret | invalid secret → HTTP 403 `Provided secret is not valid` | `0`, PASS only for bad-secret branch |
| Dataset shape | non-comment CSV lines through `ConvertFrom-Csv` | 15 rows; 12 `TRUE`, 3 `FALSE`; 0 supported source missing → observed | PASS structural only; semantic approval missing |
| Workflow graph | PowerShell JSON parse and edge validation for both exports | 20/34 nodes; 0 unresolved edges → observed | `0`, PASS static only |

The mock suite is intentionally not promoted to live QA evidence. It uses an in-process deterministic provider and mock Telegram sender; it does not prove n8n node execution, current provider behavior, PostgreSQL workflow permissions, Telegram delivery, or model quality.

## Requirement / AC results

| AC / requirement / test | Level | Expected → observed | Verdict | Evidence |
|---|---|---|---|---|
| `AC-001 / REQ-001 / T-QA-001` | live isolated | 26-document valid ingest activates one complete corpus → 26 docs, 297 chunks, 26 sources, vector dimension 768, one active version | `PASS` within valid happy path | live rerun + sanitized DB aggregate |
| `AC-002, AC-004, AC-005 / REQ-001 / T-QA-002` | required fault integration | invalid corpus, mid-ingest timeout, provider/auth/5xx/dimension/DB failure preserve old active version → only mock harness passed; no current n8n fault injection run | `NOT_VERIFIED` | M2 `19/19` is mock/contract only |
| `AC-003 / REQ-001 / T-QA-003` | isolated concurrency | sequential and near-concurrent duplicate trigger produce one identity/no duplicate chunks → sequential rerun stayed at 297 chunks and one active version; concurrent case not run live | `PASS_WITH_LIMITATIONS` | live sequential rerun; concurrency gap |
| `AC-006 / REQ-002 / T-QA-004` | approved demo E2E | valid allowed Telegram update receives exactly one readable response and is delivered → no valid current-candidate Telegram message was sent by QA | `NOT_VERIFIED` | only invalid-secret route was exercised |
| `AC-007 / REQ-002 / T-QA-005` | sandbox integration | bad secret, wrong chat, non-message, and empty text stop before retrieval/send → bad-secret 403 observed; other branches only mock-tested | `NOT_VERIFIED` | local webhook 403; M4 mock |
| `AC-008–AC-010 / REQ-002 / T-QA-006` | fault/concurrency integration | duplicate claim, send timeout/ambiguity, auth/rate-limit/5xx have bounded non-duplicate behavior → no live fault or concurrency injection | `NOT_VERIFIED` | M4 `27/27` mock only; current DB has 23 delivered and 8 `delivery_unknown` records without frozen eval mapping |
| `AC-011–AC-020 / REQ-003–REQ-005 / T-QA-007` | approved demo E2E + rubric | current real model answers 12/15, sources 12/12, unsupported 3/3, safe injection/failure behavior → no current-candidate 15-item E2E or semantic rubric run; working CSV remains `DRAFT` | `NOT_VERIFIED` | dataset shape PASS only; M3 `21/21` mock only |
| `AC-021 / REQ-006 / T-QA-008` | required 15-item E2E | all 15 current-candidate responses individually `<5,000 ms` → not run | `NOT_VERIFIED` | no `m6-local-gemma-2026-09-20` 15-item evidence |
| `AC-022–AC-024 / REQ-006 / T-QA-009` | fault E2E / exploratory | timeout/provider failure stays within deadline; cold/warm behavior is separately recorded → mock PASS; live fault not run; prior cold/warm telemetry is not current QA proof | `NOT_VERIFIED` | M4 mock; stale Engineer telemetry |
| `AC-025–AC-026 / REQ-007 / T-QA-010` | clean-instance import + config | both exports import/rebind cleanly with required artifacts and fail closed on missing config → current runtime metadata has workflow 01 inactive, workflow 02 active plus inactive duplicate; clean-instance import/rebind and full preflight not independently executed | `NOT_VERIFIED` | graph/static PASS; live inventory partial |
| `AC-027 / REQ-007 / T-QA-011` | scoped cleanup | authorized cleanup/revocation removes only exact demo target → not run; no cleanup authorization in scope | `NOT_VERIFIED` | Human/DevOps gate required |

### Coverage summary

- Mock/contract tests: `67/67` passed (`19 + 21 + 27`), all with exit code `0`.
- Current live complete required behavior: `AC-001` valid ingestion only.
- Current live partial behavior: sequential portion of `AC-003`; bad-secret branch of `AC-007`.
- Required live/fault/E2E proof missing: `AC-002`, `AC-004`–`AC-023`, `AC-025`–`AC-027` except the partial boundaries above.
- Optional `AC-024`: not proven for the current candidate.
- Dataset structure is `15 = 12 supported + 3 unsupported`, but `evaluation/README.md` still marks it `DRAFT`; Human semantic approval/frozen keys are not recorded.

## Findings, risks, and evidence limitations

1. **Current-candidate evidence gap.** `rag.rag_settings` is `m6-local-gemma-2026-09-20`, while existing delivery telemetry is `m6-local-ollama-2026-09-19`. The old telemetry records 20 successful deliveries with `max=61,461 ms`, `avg=18,746 ms`, plus 3 failed deliveries. It is stale for the current candidate and cannot be used as a current PASS or silently carried forward. It does establish that the `<5s` risk is material and requires a fresh 15-item run.
2. **Required semantic gate is absent.** The draft CSV structure is correct, but no current real-model output was scored against `Jawaban_Benar`, source relevance, and unsupported abstention. The mock provider's deterministic outputs are not semantic acceptance evidence.
3. **Runtime timeout remains unbounded relative to the business gate.** The current DB setting reports `ai_timeout_max=120000`; both workflow HTTP Request nodes pass that value directly. Architecture requires profiling and a bounded budget that leaves headroom under `<5,000 ms`. This is an unverified configuration risk, not a claimed live failure without a current fault run.
4. **Live delivery state needs a fresh frozen run.** The current local ledger contains `23 delivered` and `8 delivery_unknown`, but these records are not mapped to the approved 15-item dataset/config revision. They cannot satisfy REQ-002 or REQ-006.
5. **Evidence hygiene.** The independent local run passed, but M3 emitted the expected client-abort traceback during timeout testing and M4 emitted a pre-existing fixture `ResourceWarning` for an unclosed JSONL file. They did not change runner exit codes, but the Engineer should clean them before using console output as polished evidence.

No secrets, raw Telegram payloads, question/answer transcripts, chat IDs, or credential values were included in this report.

## Status and gate

**Overall QA verdict: `NOT_VERIFIED`.**

No observed current-candidate requirement failure is asserted from the stale telemetry, but required live fault coverage, approved semantic evaluation, current 15-item latency proof, clean-instance portability, and cleanup evidence are missing. The mock suite and readiness checks do not change that verdict. This is a QA verification status, not a release approval.

## Next owner / action

1. Engineer/DevOps must freeze and record the current Gemma runtime configuration, resolve the timeout budget against the `<5s` requirement, and provide a reproducible current-candidate test target.
2. QA must rerun AC-002–AC-024 as applicable, then execute the approved sequential 15-item E2E with per-item answer/source/latency/delivery evidence.
3. Human must approve the semantic 12+3 key/source set before it becomes the acceptance dataset.
4. Security remains a separate independent M7 gate; Human selects that handoff after QA evidence is complete.
