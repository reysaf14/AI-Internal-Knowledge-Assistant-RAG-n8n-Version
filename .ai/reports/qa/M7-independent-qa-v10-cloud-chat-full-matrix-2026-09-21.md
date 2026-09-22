# M7 Independent QA — v10 Cloud-Chat Full Matrix

Date: `2026-09-21`  
Timezone: `Asia/Jakarta`  
Project/lane: `Asisten Pengetahuan Internal Toko Makmur Jaya` / `PROFESSIONAL`  
Executor: `QA`, independent of Engineer implementation and report  
Scope: approved synthetic `12 supported + 3 unsupported` dataset, active Telegram sandbox, DeepSeek cloud chat, local EmbeddingGemma retrieval.

## Status

`FAIL — NOT RELEASE READY`.

The cloud-chat change is behaviorally better than the prior Gemma candidate: all 15 final messages were delivered under the latency budget, all 15 diagnostic rows persisted successfully, and items 9 and 10 reached the model instead of deterministic abstention. However, four supported answers still fail the approved content rubric because mandatory facts are missing. This is now a content-quality failure, not a diagnostic-persistence failure.

## Candidate and evidence freeze

| Artifact/runtime | Evidence |
|---|---|
| Workflow | `IAOqkQsNamEJarHF`, active, 37 nodes |
| Revision | `cloud-chat-local-embedding-2026-09-21-v2` |
| Workflow export SHA-256 | `C70696EC083FE088D61B75BC6B06F1FB72A739418972FB0E241A333D97A16FBA` |
| Dataset SHA-256 | `6B4587A7DCB7EB04630801D7073F7424ED8274D7245746A3C82CD658DFF60614` |
| Evaluation README SHA-256 | `FD9BDAE3F1B0CB9D7C51D1F40F1A06AA95850AA674EB95DD07029A5CA56259EC` |
| Chat provider | `https://api.deepseek.com`, model `deepseek-flash` |
| Embedding provider | local Ollama `embeddinggemma:300m-qat-q4_0`, profile dimension `768` |
| RAG settings | retrieval `5`; minimum similarity `0.25`; context `3000`; output `192`; AI timeout `4000 ms` |
| Active corpus | `sha256:61b7301108de25c111d815812e8695f150e4e958dbbd9c40dd03dfd1baa6d109` |

No credential value was read or recorded. The DeepSeek key remained inside the n8n credential store.

## Preconditions and execution evidence

### Runtime checks

- `rag-n8n-local`: healthy, n8n `1.123.81`.
- `rag-postgres-local`: healthy, pgvector/PostgreSQL 16.
- `/healthz`: HTTP `200`, `{"status":"ok"}`.
- `/healthz/readiness`: HTTP `200`, `{"status":"ok"}`.
- Embedding readiness probe executed from inside n8n against local Ollama: HTTP `200`, `4,971 ms`; readiness evidence only, not the matrix latency result.
- Active runtime query confirmed DeepSeek chat and EmbeddingGemma embedding values above.

### Manual Telegram steps

Computer Use opened Telegram Web, selected `AgnesTachyon bot`, and sequentially entered the 15 CSV questions. Each message was submitted with `Enter`; the UI was re-observed after each batch. Three batches were used: items `1–5`, `6–10`, and `11–15`. A tab-load retry occurred before batch `6–10`; no message was sent during the failed input attempt.

UI/manual exit code: `NOT_APPLICABLE` — the approved E2E assertion is the visible Telegram delivery/response plus persisted database evidence, not a process exit code.

### Persisted counts

| Metric | Before run | After run |
|---|---:|---:|
| `rag.telegram_updates` | 156 | 171 |
| `rag.safe_events` | 153 | 183 |
| v2 safe events | 16 | 46 |
| New delivery events | — | 15 `success` |
| New grounding diagnostics | — | 15 `success` |

The 15 newest Telegram ledger rows (`update_id` values `158–172`) were all `delivered` with empty `error_category`. New safe-event rows were `200–229`: 15 diagnostic rows followed by 15 delivery rows. Diagnostic metadata included answered paths, abstention paths, and `support_gate_abstention` for item 15.

## Matrix result

Rubric: supported items require mandatory facts, no contradiction, and a relevant source; unsupported items require exact official-document abstention without guessing or citation.

| Item | AC/test family | Expected → observed | Delivery/event ms | Diagnostic | Verdict |
|---:|---|---|---:|---|---|
| 1 | AC-011/014 supported answer/source | 07.00–21.00 Monday + relevant source → answered with source 09 | 2,386 | `answered`, `validator=answered` | PASS |
| 2 | AC-011/014 supported answer/source | 10 motor, 5 mobil, gratis → all present with source | 2,190 | `answered` | PASS |
| 3 | AC-011/014 supported answer/source | Retur/tukar policy → grounded policy answer | 2,276 | `answered` | PASS |
| 4 | AC-011/014 supported SOP completeness | Full opening SOP → answer omits printer, QRIS/card reader, AC, and inside-security details | 2,528 | `answered` | FAIL |
| 5 | AC-011/014 supported SOP completeness | Full cash/setoran SOP → omits cash-float amount, bank schedule, and complete reconciliation | 2,400 | `answered` | FAIL |
| 6 | AC-011/014 supported SOP completeness | Full closing SOP → omits 20.45 start, customer/checkout flow, two-witness cash count, cleaning, documentation | 2,579 | `answered` | FAIL |
| 7 | AC-011/014 supported answer/source | Damaged-goods complaint procedure → source-grounded complaint and verification steps | 2,204 | `answered` | PASS |
| 8 | AC-011/014 supported answer/source | Late-delivery procedure → third-party courier escalation grounded | 2,134 | `answered` | PASS |
| 9 | AC-011/014 supported policy fact | 12 annual-leave days → `12 hari per tahun` with source 20 | 2,156 | `answered` | PASS |
| 10 | AC-011/014 supported policy completeness | Max 2 sick days without letter; `>2` requires doctor letter → only first half answered | 2,042 | `answered`, `validator=answered` | FAIL |
| 11 | AC-011/014 supported safety/source | APAR accessible; routes clear; everyone knows route → all core facts answered | 2,561 | `answered` | PASS |
| 12 | AC-011/014 supported answer/source | Full store address → address answered with relevant source 09 | 1,992 | `answered` | PASS |
| 13 | AC-017 unsupported boundary | No official salary information; no source → exact abstention | 1,979 | `model_abstention_text`, no valid citation | PASS |
| 14 | AC-017 unsupported boundary | No official travel-claim information; no source → exact abstention | 1,653 | `model_abstention_text`, no valid citation | PASS |
| 15 | AC-017 unsupported boundary | No official manager-loan information; no source → exact abstention | 1,100 | `support_gate_abstention`, no valid citation | PASS |

### Aggregates

- Content/source/abstention raw result: `11/15`.
- Supported: `8/12`.
- Unsupported: `3/3`.
- Delivery: `15/15`.
- Latency: `15/15` under `<5,000 ms`; observed `1,100–2,579 ms`.
- Diagnostic persistence: `15/15` new rows, all `success`.

Items 1 and 12 cite active-corpus source 09, while the CSV source labels are 21 and 00 respectively. The cited source is relevant and contains the observed facts; this is recorded as a source-label/oracle nuance, not silently rewritten.

## Regression evidence

Commands were run from PowerShell in:
`C:\Freelance-Workspace\projects\active\AI Internal Knowledge Assistant (RAG) — n8n Version`

| Command | Level | Expected → observed | Exit code | Verdict |
|---|---|---|---:|---|
| `python tests/harness/test_ingestion.py` | mock/contract | 19 tests → `19/19` | 0 | PASS at harness level |
| `python tests/harness/test_qa_core.py` | mock/contract | 21 tests → `21/21` | 0 | PASS at harness level |
| `python tests/harness/test_delivery_core.py` | mock/contract | 27 tests → `27/27` | 0 | PASS at harness level |
| Total | mock/contract | 67 tests → `67/67` | 0 | PASS at harness level |

The deterministic harness does not override the four live DeepSeek content failures.

## Findings and owner

1. **P1 — items 4, 5, and 6 are still incomplete against the approved SOP oracle.** The model cites the correct sources but drops mandatory operational details. Owner: Engineer; improve evidence selection/prompt/output completeness or add a deterministic completeness guard.
2. **P1 — item 10 is incomplete.** DeepSeek answers the `≤2 days without letter` half but omits the explicit `>2 days requires a doctor letter` rule. Owner: Engineer; add a required-fact check for policy answers and rerun item 10.
3. **P2 — source-label/oracle nuance.** Items 1 and 12 answer from relevant active source 09 while the CSV labels point to sources 21 and 00. Owner: Human/Architect if exact canonical source identity is required; otherwise keep the corpus-backed relevant-source rule explicit.
4. **Telemetry remediation status:** PASS for the tested v2 paths. The prior zero-row blocker is not reproduced: all 15 new diagnostics persisted successfully.

## Coverage and untested scope

Required live semantic matrix coverage is complete: `15/15`. Required live latency and delivery coverage is complete for this run. Diagnostic persistence coverage is complete for answered and abstained paths.

Still unverified and not silently treated as N/A:

- live provider/database/Telegram fault injection;
- duplicate/concurrency behavior on the current DeepSeek candidate;
- clean-instance import/rebind;
- Security audit and candidate-bound coverage;
- Human quality/release decision and cleanup/revocation.

## Next gate

Engineer must remediate the four content failures (`4,5,6,10`) or obtain a separate Human-approved oracle/scope decision. QA then reruns those affected cases plus the full matrix because the prompt/provider/config path is shared. M7 remains `FAIL / NOT_VERIFIED` for release purposes.

Artifacts:

- [Sanitized per-item results](../../../evaluation/run_v10-cloud-chat-2026-09-21.jsonl)
- [Frozen runtime configuration](../../../evaluation/run_v10-cloud-chat-2026-09-21_config.json)
- [Run summary](../../../evaluation/run_v10-cloud-chat-2026-09-21_summary.md)
- [Engineer remediation report](../../build/M7-cloud-chat-e2e-remediation-2026-09-21.md)
