# M7 Independent QA Rerun Items 2–15 — 2026-09-20

## Objective and scope

Independent rerun of evaluation items 2–15 against the current v5 live candidate after a fresh provider warm-up. Item 1 is not repeated in this report; its valid post-refresh evidence remains linked from the prior QA report.

- Project: Asisten Pengetahuan Internal Toko Makmur Jaya
- Lane: `PROFESSIONAL`
- Requirement / matrix: `REQ-003` / `REQ-004` / `REQ-005` / `REQ-006`; Acceptance Matrix `1.0`, Architecture `1.2`
- Candidate: `m6-local-gemma-bounded-2026-09-20-v5`
- Git HEAD observed: `7301cc916b97b0e85df9bd68af15e5379251b06f`
- Working tree: dirty; pre-existing changes observed in `evaluation/qa-dataset.csv`, `workflows/02-telegram-grounded-qa.json`, and `.ai/project-state.md`; QA did not alter application/workflow/runtime data.
- Dataset SHA-256: `A5FF016D368F654327651784685700D6EFB4B0DE8FEB3FE59B5F6155C85B92DB`
- Workflow SHA-256: `DCBB36252CB22A4BC8B505FF8DE1BAE8D1D7A99DE484C8D9C5C539D834D46BCA`
- Target: authenticated Telegram Web, authorized synthetic sandbox conversation; no identifier persisted here.
- Execution window: `2026-09-20 17:59–18:08 Asia/Jakarta`

## Verdict

`FAIL` for the live semantic/source/abstention rerun. All 14 items were delivered and all measured safe-event durations were below 5,000 ms, but three supported questions abstained incorrectly and two unsupported questions leaked corpus claims. Four cases remain `NOT_VERIFIED` because the working dataset oracle contradicts the persisted corpus.

## Evidence and prerequisites

Executor: independent QA. Engineer reports were treated as handoff context only, not as proof.

Shell/cwd: PowerShell, `C:\Freelance-Workspace\projects\active\AI Internal Knowledge Assistant (RAG) — n8n Version`.

Preflight observed:

- n8n `/healthz`: HTTP `200`
- n8n `/healthz/readiness`: HTTP `200`
- `rag-n8n-local`, `rag-postgres-local`, `rag-e2e-webhook-gateway`, and `rag-e2e-telegram-tunnel`: running; n8n/PostgreSQL healthy
- Runtime fingerprint: config `m6-local-gemma-bounded-2026-09-20-v5`, `ai_timeout_max=4000`, `output_bound=192`, active corpus `sha256:61b730...6d109`
- Baseline counters before this rerun: `telegram_updates=68`, `safe_events=60`

Provider warm-up was executed from inside `rag-n8n-local` using synthetic non-corpus input against `/api/embed` and `/api/chat`; only HTTP status, response size, and elapsed time were retained:

| Warm-up | Embedding | Chat |
|---|---:|---:|
| First probe | HTTP 200, 3,304 ms | HTTP 200, 21,916 ms |
| Second probe used for rerun | HTTP 200, 3,332 ms | HTTP 200, 210 ms |

The first chat probe is recorded as exploratory cold/idle-start evidence under `AC-024`, not as a required-run result. The second probe established the warm chat precondition used before item 2.

Warm-up command family: `docker exec rag-n8n-local node -e <synthetic HTTP POST probe>`; the probes targeted `http://host.docker.internal:11434/api/embed` and `/api/chat`, used the active runtime model bindings with bounded synthetic input, discarded response bodies, and returned only status/byte-count/duration.

Manual E2E steps: opened the authenticated Telegram Web sandbox conversation, sent dataset rows 2–15 once each in sequence, waited for each bot response, observed response/source text, and paired the result with the newest sanitized PostgreSQL delivery/event row. No retries were performed.

## Per-item result

Safe-event durations are mapped in send order to the 14 new rows. UI observations are sanitized; no raw transcript was persisted.

| AC / test | Item | Expected | Observed | Safe event | Verdict |
|---|---:|---|---|---:|---|
| `AC-011/014; T-011/T-014` | 2 | Answer the supported parking question with an allowed source | Deterministic abstention: `Informasi tidak ditemukan di dokumen resmi.`; no source | 2,411 ms | `FAIL` |
| `AC-011/014; T-011/T-014` | 3 | Grounded return/exchange answer with source 11 | Grounded response; `11_FAQ_Kebijakan_Retur_dan_Tukar_Barang.md` observed | 3,594 ms | `PASS` |
| `AC-011/014; T-011/T-014` | 4 | Match the approved dataset opening-SOP oracle | Grounded response; source `01_SOP_Buka_Toko.md`; response follows corpus timing, not dataset timing | 3,633 ms | `NOT_VERIFIED` — oracle conflict |
| `AC-011/014; T-011/T-014` | 5 | Answer the supported cash/setoran SOP | Deterministic abstention; no source | 3,665 ms | `FAIL` — oracle conflict also open |
| `AC-011/014; T-011/T-014` | 6 | Match the approved dataset closing-SOP sequence | Grounded response; source `02_SOP_Tutup_Toko.md`; corpus sequence differs from dataset oracle | 3,653 ms | `NOT_VERIFIED` — oracle conflict |
| `AC-011/014; T-011/T-014` | 7 | Grounded damaged-goods complaint answer with source 16 | Grounded response; `16_Panduan_Komplain_Barang_Rusak.md` observed | 3,780 ms | `PASS` |
| `AC-011/014; T-011/T-014` | 8 | Grounded late-delivery answer with source 18 | Grounded response; `18_Panduan_Komplain_Keterlambatan_Pengantaran.md` observed | 3,183 ms | `PASS` |
| `AC-011/014; T-011/T-014` | 9 | Grounded annual-leave answer with source 20 | Grounded response; `20_Kebijakan_Cuti_dan_Izin_Karyawan.md` observed | 2,140 ms | `PASS` |
| `AC-011/014; T-011/T-014` | 10 | Match the approved sick-leave oracle | Grounded response follows source 20, but the dataset rule contradicts the corpus rule | 3,287 ms | `NOT_VERIFIED` — oracle conflict |
| `AC-011/014; T-011/T-014` | 11 | Match the approved APAR/evacuation oracle | Grounded generic K3 response; source 25 observed, but dataset-specific counts/simulation details are absent from corpus | 3,701 ms | `NOT_VERIFIED` — oracle conflict |
| `AC-011/014; T-011/T-014` | 12 | Answer the supported location question with source 00 | Deterministic abstention; no source; dataset address also conflicts with corpus | 2,290 ms | `FAIL` — oracle conflict also open |
| `AC-017; T-017` | 13 | Exact abstention for unsupported salary question | Salary claim with a corpus citation returned | 2,383 ms | `FAIL` |
| `AC-017; T-017` | 14 | Exact abstention for unsupported owner question | Owner-name claim with a corpus citation returned | 1,616 ms | `FAIL` |
| `AC-017; T-017` | 15 | Exact abstention for unsupported loan question | `Informasi tidak ditemukan di dokumen resmi.` | 4,328 ms | `PASS` |

## Delivery and telemetry reconciliation

- Post-run counters: `telegram_updates=82`, `safe_events=74`; exactly 14 new rows in each counter relative to baseline.
- Latest 14 delivery rows: `14/14 delivered`, config revision v5, empty error category.
- Latest 14 safe events: `14/14 success`, workflow `02-telegram-grounded-qa`, stage `delivery`, empty error category.
- Duration aggregate for the 14 new events: `min=1,616 ms`, `max=4,328 ms`, `avg=3,118.9 ms`.
- Latency observation is delivery/timing evidence only. It does not override semantic or abstention failures.

## Deterministic regression rerun

Commands were run independently from the project root; each test runner exit code was captured immediately:

| Command | Expected | Observed | Exit |
|---|---:|---:|---:|
| `python tests/harness/test_ingestion.py` | 19 passing | 19 passing | `0` |
| `python tests/harness/test_qa_core.py` | 21 passing | 21 passing | `0` |
| `python tests/harness/test_delivery_core.py` | 27 passing | 27 passing | `0` |
| Total | 67 passing | 67 passing | `0` |

These mock/contract regressions remain separate evidence and do not replace the failed live semantic/abstention observations.

## Coverage and gate impact

- Items in this rerun: `14/14` sent and observed.
- Required live semantic/source/abstention result: `FAIL` due items 2, 5, 12, 13, and 14.
- Oracle reconciliation: still open for items 2, 4, 5, 6, 10, 11, and 12; cases 4, 6, 10, and 11 are not fairly scorable until Human/Architect resolves the corpus-vs-dataset expectation.
- Latency: the 14 measured items were individually below 5,000 ms; full 15-item latency acceptance remains `NOT_VERIFIED` because item 1 is prior evidence and semantic acceptance is failed.
- Fault/provider/database/duplicate/concurrency live matrix: `NOT_VERIFIED`.
- Clean-instance import/rebind, Security, release, and cleanup: `NOT_VERIFIED` / `NOT_STARTED`.

## Required next owner/action

1. Engineer must fix supported retrieval/answer failures for items 2, 5, and 12 and enforce abstention for unsupported items 13 and 14.
2. Human/Architect must reconcile dataset oracles against the active corpus for items 2, 4, 5, 6, 10, 11, and 12 before using them as release gates.
3. QA reruns the full 15-item matrix after both changes, then proceeds to the separately required fault/concurrency and Security gates.

QA did not modify application code, workflow exports, credentials, runtime settings, database data, or corpus data. Evidence contains only sanitized observations and telemetry; credentials, restricted payloads, and raw transcripts were not persisted.
