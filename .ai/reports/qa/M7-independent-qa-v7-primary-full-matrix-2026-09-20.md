# M7 Independent QA v7 Primary Full Matrix — 2026-09-20

## Objective and scope

Independent primary QA run of the updated 15-item dataset against the active v7 candidate after Engineer citation/grounding remediation and Human oracle reconciliation.

- Project: Asisten Pengetahuan Internal Toko Makmur Jaya
- Lane: `PROFESSIONAL`
- Matrix: Acceptance Matrix `1.0`, Architecture `1.2`
- Requirements: `REQ-003`, `REQ-004`, `REQ-005`, `REQ-006`
- Candidate: `m7-citation-contract-2026-09-20-v7`
- Git HEAD: `7301cc916b97b0e85df9bd68af15e5379251b06f`
- Dataset SHA-256: `6B4587A7DCB7EB04630801D7073F7424ED8274D7245746A3C82CD658DFF60614`
- Evaluation README SHA-256: `FD9BDAE3F1B0CB9D7C51D1F40F1A06AA95850AA674EB95DD07029A5CA56259EC`
- Workflow SHA-256: `592CD31522A698178A2BE7D94D69B5F6C843AFAA2F3872062D21C8F8F832D119`
- Engineer remediation report SHA-256: `FE35F92388CF58E01A46BA8F6EDEA00763A136997012D50CF50E51263FB1B389`
- Target: authenticated Telegram Web, authorized synthetic sandbox conversation
- Execution window: `2026-09-20 18:58–19:07 Asia/Jakarta`

This is the first independent Telegram run against v7 and the updated oracle, so it is labeled the primary v7 run. Earlier v5 reports remain historical evidence and were not overwritten.

## Verdict

`FAIL` for the live semantic/source/abstention matrix. The transport and latency path passed, but only 7/15 items passed the content/abstention rubric. Eight required item outcomes failed.

## Engineer handoff assessment

The latest Engineer report, `.ai/reports/build/M7-citation-grounding-remediation-2026-09-20.md`, was read as implementer evidence only. It correctly identified the v5 citation-boundary defect and reported local repairs for items 2, 5, 12, 13, and 14. QA did not accept those local checks as E2E proof; the following Telegram run independently tested the active workflow.

## Preconditions and environment

Shell/cwd: PowerShell, `C:\Freelance-Workspace\projects\active\AI Internal Knowledge Assistant (RAG) — n8n Version`.

Observed before sending:

- n8n `/healthz`: HTTP `200`
- n8n `/healthz/readiness`: HTTP `200`
- `rag-n8n-local` and `rag-postgres-local`: running/healthy
- gateway and Telegram tunnel: running
- baseline counters: `telegram_updates=82`, `safe_events=74`
- runtime revision: `m7-citation-contract-2026-09-20-v7`
- `embedding_profile_id=ollama:embeddinggemma:300m-qat-q4_0:768`
- `embedding_dimension=768`, `retrieval_limit=5`, `minimum_similarity=0.25`
- `context_bound=3000`, `output_bound=192`, `ai_timeout_max=4000 ms`
- active corpus: `sha256:61b730...6d109`

Provider warm-up was run from inside `rag-n8n-local` with synthetic-only requests to `/api/embed` and `/api/chat`; response bodies were discarded and only status/size/time were retained:

| Pass | Embedding | Chat | Use |
|---|---:|---:|---|
| 1 | HTTP 200 / 2,932 ms | HTTP 200 / 19,124 ms | Exploratory cold/idle-start (`AC-024`) |
| 2 | HTTP 200 / 2,064 ms | HTTP 200 / 236 ms | Warm precondition for required run |

Manual steps: opened authenticated Telegram Web, selected the authorized bot conversation, sent dataset items 1–15 exactly once and sequentially, waited for each response, observed answer/source or abstention, and paired the result with the newest sanitized delivery/event row. No retries were performed.

## Per-item evidence

Safe-event durations are mapped in send order to the 15 new rows. Raw Telegram transcripts and payloads were not persisted.

| AC / test | Item | Expected → observed | Source observed | Duration | Verdict |
|---|---:|---|---|---:|---|
| `AC-011/014; T-011/T-014` | 1 | 07.00–21.00 Monday answer → correct answer | `09_FAQ_Jam_Operasional_dan_Lokasi.md` (relevant corroborating source; dataset canonical is 21) | 2,332 ms | `PASS` |
| `AC-011/014; T-011/T-014` | 2 | Include about 10 motor, 5 cars, free → 5 cars/free only; motor capacity missing | `09_FAQ_Jam_Operasional_dan_Lokasi.md` | 1,937 ms | `FAIL` |
| `AC-011/014; T-011/T-014` | 3 | Grounded return/exchange policy → grounded response | `11_FAQ_Kebijakan_Retur_dan_Tukar_Barang.md` | 2,144 ms | `PASS` |
| `AC-011/014; T-011/T-014` | 4 | Full 06.30–07.00 opening checklist → only security/timing subset | `01_SOP_Buka_Toko.md` | 2,342 ms | `FAIL` |
| `AC-011/014; T-011/T-014` | 5 | Cash time, QRIS/card, float, safe, bank schedule, documentation → partial cash procedure; mandatory details missing | `03_SOP_Penanganan_Kas_dan_Setoran_Harian.md` | 3,573 ms | `FAIL` |
| `AC-011/014; T-011/T-014` | 6 | Full closing checklist → only announcement and shutdown subset | `02_SOP_Tutup_Toko.md` | 2,522 ms | `FAIL` |
| `AC-011/014; T-011/T-014` | 7 | Damaged-goods complaint procedure/evidence → grounded procedure and evidence handling | `16_Panduan_Komplain_Barang_Rusak.md` | 2,438 ms | `PASS` |
| `AC-011/014; T-011/T-014` | 8 | Late-delivery procedure → grounded escalation paths | `18_Panduan_Komplain_Keterlambatan_Pengantaran.md` | 2,569 ms | `PASS` |
| `AC-011/014; T-011/T-014` | 9 | 12 annual-leave days → deterministic abstention | none | 1,961 ms | `FAIL` |
| `AC-011/014; T-011/T-014` | 10 | Max 2 sick days without letter, >2 requires letter → deterministic abstention | none | 2,413 ms | `FAIL` |
| `AC-011/014; T-011/T-014` | 11 | Accessible fire extinguisher + clear exits/routes → clear exits/routes only; APAR fact missing | `25_Kebijakan_Keselamatan_Kerja_K3_Sederhana.md` | 2,284 ms | `FAIL` |
| `AC-011/014; T-011/T-014` | 12 | Corpus-backed address → correct address | `09_FAQ_Jam_Operasional_dan_Lokasi.md` (relevant corroborating source; dataset canonical is 00) | 2,157 ms | `PASS` |
| `AC-017; T-017` | 13 | Exact unsupported abstention → exact abstention | none | 2,085 ms | `PASS` |
| `AC-017; T-017` | 14 | Exact unsupported abstention for travel-claim question → exact abstention | none | 1,558 ms | `PASS` |
| `AC-017; T-017` | 15 | Exact unsupported abstention → cited escalation/contact claim returned | `19_Panduan_Eskalasi_Komplain_ke_Manajer.md` | 2,692 ms | `FAIL` |

## Delivery and telemetry reconciliation

- Post-run counters: `telegram_updates=97`, `safe_events=89`; exactly 15 new rows relative to baseline.
- Latest 15 delivery rows: `15/15 delivered`, all v7, empty error category.
- Latest 15 safe events: `15/15 success`, workflow `02-telegram-grounded-qa`, stage `delivery`, empty error category.
- Duration aggregate: `min=1,558 ms`, `max=3,573 ms`, `avg=2,333.8 ms`.
- Delivery and timing pass does not override the content/abstention failures.

## Deterministic regression rerun

Commands were run independently from the project root and each runner exit code was captured immediately:

| Command | Expected → observed | Exit |
|---|---|---:|
| `python tests/harness/test_ingestion.py` | 19 → 19 passed | `0` |
| `python tests/harness/test_qa_core.py` | 21 → 21 passed | `0` |
| `python tests/harness/test_delivery_core.py` | 27 → 27 passed | `0` |
| Total | 67 → 67 passed | `0` |

These mock/contract tests remain separate evidence and do not replace the live semantic failures.

## Coverage and gate impact

- Content/abstention: `7/15 pass`; required aggregate is `15/15`.
- Supported content: `5/12 pass`; failures are items 2, 4, 5, 6, 9, 10, and 11.
- Supported relevant source observed: `10/12`; items 9 and 10 had no source because they abstained.
- Unsupported abstention: `2/3 pass`; item 15 leaked a cited claim.
- Delivery: `15/15 delivered`.
- Latency: `15/15` individually below 5,000 ms.
- Live fault/provider/database/duplicate/concurrency matrix: `NOT_VERIFIED`.
- Clean-instance import/rebind, Security, release, and cleanup: `NOT_VERIFIED` / `NOT_STARTED`.

## Required next owner/action

1. Engineer investigates the remaining semantic failures: retrieval/generation completeness for items 2, 4, 5, 6, 9, 10, 11, and the unsupported-boundary leakage for item 15.
2. QA preserves this v7 primary evidence and reruns the full matrix after a new remediation; no prior pass is carried forward for failed items.
3. Fault/concurrency, clean-instance, Security, release, and cleanup gates remain separate and unverified.

QA did not modify application code, workflow exports, credentials, runtime settings, database data, or corpus data. Persisted artifacts contain sanitized classifications/telemetry only; no credentials, raw Telegram payloads, or raw answer transcripts were written.
