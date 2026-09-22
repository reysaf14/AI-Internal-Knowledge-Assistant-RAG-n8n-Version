# M7 Independent QA v8 Support-Boundary Full Matrix — 2026-09-20

## Objective and scope

Independent rerun of the frozen 15-item Telegram matrix against the Engineer's v8 support-boundary and diagnostic remediation. The rerun specifically verifies items 9, 10, and 15 first in the same sequential matrix, while retaining the five locally accepted Gemma limitation cases as regression cases.

- Project: `Asisten Pengetahuan Internal Toko Makmur Jaya`
- Lane: `PROFESSIONAL`
- Matrix: Acceptance Matrix `1.0`, Architecture `1.2`
- Candidate: `m7-support-gate-trace-2026-09-20-v8`
- Chat model: `gemma4:e2b-it-qat`
- Target: authenticated Telegram Web, authorized synthetic sandbox bot conversation
- Dataset: `evaluation/qa-dataset.csv`, unchanged from v7
- Engineer remediation: `.ai/reports/build/M7-support-boundary-and-diagnostic-remediation-2026-09-20.md`
- Execution date/time: `2026-09-20`, Asia/Jakarta
- Executor: independent QA

Persisted artifact hashes:

- Sanitized JSONL: `5139FC9624583AC2057754EF199B8D01DD102114C679312DC8724749FC07B34A`
- Run summary: `67590DB3B31FAE64AD38E42A066CABC11EE27981374B1E9B8639EED926E32AE8`
- Run config: `1BB2C1092695CA050ECC9C10A75B7EA32C903FBC6724F889A9F8C4168CB4CAF2`
- Engineer remediation: `5B5B3D5D09B40796F433E7613300658A59FEF96796787F43ABA3D70022F96BF6`
- Active workflow export: `F36AC74779B99D7EFA7AD74A69056117798BC200944F75DF20E357CCA6CC94F8`

## Verdict

`FAIL` under the approved semantic/source/abstention contract.

The v8 behavior improved the unsupported boundary: item 15 now returned exact abstention with no source. The raw live matrix passed `9/15` content/abstention cases: supported `6/12`, unsupported `3/3`. Items 4, 5, 6, and 11 remain accepted only as local-Gemma limitations for the narrower proof-of-wiring scope. Items 9 and 10 still abstained despite being supported and remain open.

Scoped Human-requested local proof-of-wiring disposition: `PASS WITH LIMITATIONS` for runtime/integration, with `2` semantic cases still unverified and diagnostic telemetry missing.

## Preconditions and environment

Shell/cwd: PowerShell, `C:\Freelance-Workspace\projects\active\AI Internal Knowledge Assistant (RAG) — n8n Version`.

Observed before sending:

- `rag-n8n-local`: running/healthy, n8n `1.123.81`;
- `rag-postgres-local`: running/healthy, pgvector PostgreSQL `16`;
- `rag-e2e-telegram-tunnel`: running;
- `rag-e2e-webhook-gateway`: running;
- n8n `/healthz`: `HTTP 200`, `{"status":"ok"}`;
- n8n `/healthz/readiness`: `HTTP 200`, `{"status":"ok"}`;
- active DB config: `m7-support-gate-trace-2026-09-20-v8`;
- active model: `gemma4:e2b-it-qat`;
- embedding profile: `ollama:embeddinggemma:300m-qat-q4_0:768`;
- retrieval limit `5`, minimum similarity `0.25`, context bound `3000`, output bound `192`, AI timeout `4000 ms`;
- active corpus: `sha256:61b7301108de25c111d815812e8695f150e4e958dbbd9c40dd03dfd1baa6d109`;
- baseline counters: `telegram_updates=97`, `safe_events=89`.

Synthetic provider warm-up from inside `rag-n8n-local` succeeded:

| Operation | HTTP | Elapsed |
|---|---:|---:|
| Embedding | 200 | 192 ms |
| Chat | 200 | 477 ms |

No provider response body, credential, Telegram payload, or raw transcript was persisted.

## Manual E2E steps

1. Reopened authenticated Telegram Web and selected the authorized `AgnesTachyon bot` conversation.
2. Sent item 1 after explicit user confirmation.
3. Sent items 2–8 sequentially, waiting for the response after each message.
4. Sent items 9–15 sequentially, waiting for the response after each message.
5. Reconciled the visible question/answer/source or abstention classification with the newest sanitized PostgreSQL delivery event.
6. Read sanitized counters and stage values from `rag.telegram_updates` and `rag.safe_events`.

The rerun created exactly 15 new update rows (`id=99–113`) and 15 new delivery event rows (`id=101–129`).

## Per-item evidence

The table records sanitized observations, not raw Telegram transcripts.

| Item | Expected class | Observed result | Source observed | Duration | Raw verdict | Scoped disposition |
|---:|---|---|---|---:|---|---|
| 1 | Supported hours | 07.00–21.00 Monday answer | `09_FAQ_Jam_Operasional_dan_Lokasi.md` | 2,548 ms | `PASS` | `PASS` |
| 2 | Supported parking facts | About 10 motor, 5 cars, free | `09_FAQ_Jam_Operasional_dan_Lokasi.md` | 2,122 ms | `PASS` | `PASS` |
| 3 | Supported return/exchange | Grounded policy answer | `11_FAQ_Kebijakan_Retur_dan_Tukar_Barang.md` | 2,603 ms | `PASS` | `PASS` |
| 4 | Supported opening SOP | Relevant source, multiple mandatory steps omitted | `01_SOP_Buka_Toko.md` | 2,313 ms | `FAIL` | `ACCEPTED LOCAL-MODEL LIMITATION` |
| 5 | Supported cash SOP | Relevant source, mandatory details omitted | `03_SOP_Penanganan_Kas_dan_Setoran_Harian.md` | 2,618 ms | `FAIL` | `ACCEPTED LOCAL-MODEL LIMITATION` |
| 6 | Supported closing SOP | Relevant source, mandatory details omitted | `02_SOP_Tutup_Toko.md` | 2,170 ms | `FAIL` | `ACCEPTED LOCAL-MODEL LIMITATION` |
| 7 | Supported damaged-goods complaint | Grounded procedure and evidence handling | `16_Panduan_Komplain_Barang_Rusak.md` | 2,262 ms | `PASS` | `PASS` |
| 8 | Supported late delivery | Grounded escalation paths | `18_Panduan_Komplain_Keterlambatan_Pengantaran.md` | 2,567 ms | `PASS` | `PASS` |
| 9 | Supported annual leave | Deterministic abstention; no source in final response | none | 2,094 ms | `FAIL` | `OPEN ROOT CAUSE — NOT VERIFIED` |
| 10 | Supported sick leave | Deterministic abstention; no source in final response | none | 1,786 ms | `FAIL` | `OPEN ROOT CAUSE — NOT VERIFIED` |
| 11 | Supported K3 | Relevant source, accessible-fire-extinguisher fact omitted | `25_Kebijakan_Keselamatan_Kerja_K3_Sederhana.md` | 2,556 ms | `FAIL` | `ACCEPTED LOCAL-MODEL LIMITATION` |
| 12 | Supported address | Correct corpus-backed address | `09_FAQ_Jam_Operasional_dan_Lokasi.md` | 2,191 ms | `PASS` | `PASS` |
| 13 | Unsupported salary | Exact abstention | none | 2,933 ms | `PASS` | `PASS` |
| 14 | Unsupported travel claim | Exact abstention | none | 1,638 ms | `PASS` | `PASS` |
| 15 | Unsupported loan | Exact abstention; no related escalation source cited | none | 1,160 ms | `PASS` | `PASS` |

## Delivery and latency reconciliation

- Post-run counters: `telegram_updates=112`, `safe_events=104`.
- Delta from baseline: exactly `+15` updates and `+15` safe events.
- Delivery: `15/15` rows status `delivered`.
- Delivery safe events: `15/15` status `success`.
- Delivery duration: minimum `1,160 ms`, maximum `2,933 ms`, average `2,237.4 ms`.
- Delivery error category: empty for all 15 new delivery events.
- All 15 items were below the `5,000 ms` latency requirement.

## Diagnostic telemetry result

The remediation report promised one sanitized `grounding_diagnostic` safe event per processed answer. The v8 rerun produced:

- `grounding_diagnostic` rows: `0`;
- only `delivery` safe events were persisted;
- no persisted stage evidence for `retrieved_candidate_count`, `prompt_evidence_count`, query-term overlap, model response class, or validator result.

This is an observed evidence failure. It prevents QA from proving whether items 9 and 10 fail in retrieval, evidence assembly, model response, or citation validation. Their prior read-only nearest-neighbor evidence shows source-20 candidates exist, but that does not identify the live E2E failing stage.

Item 15 itself is behaviorally repaired in this run: the related escalation document was no longer surfaced as a source and the response was exact abstention. The missing diagnostic row means the internal gate reason is not independently persisted, but the externally required unsupported behavior passed.

## Deterministic regression rerun

Commands were run independently from the project root; each runner completed with exit code `0`:

| Command | Result | Exit |
|---|---:|---:|
| `python tests/harness/test_ingestion.py` | `19/19` passed | `0` |
| `python tests/harness/test_qa_core.py` | `21/21` passed | `0` |
| `python tests/harness/test_delivery_core.py` | `27/27` passed | `0` |
| Total | `67/67` passed | `0` |

The deterministic harness remains separate evidence and does not override the two live supported abstentions or missing diagnostic telemetry.

## Gate summary

| Gate | Result | Evidence |
|---|---|---|
| Runtime/container readiness | `PASS` | Healthy containers and n8n health/readiness HTTP 200 |
| Provider reachability from n8n container | `PASS` | Synthetic embedding/chat HTTP 200 |
| Telegram delivery | `PASS` | 15/15 new rows delivered |
| Latency | `PASS` | 15/15 under 5 seconds |
| Raw supported semantic content | `FAIL` | 6/12; items 4,5,6,9,10,11 incomplete/abstained |
| Raw unsupported abstention | `PASS` | 3/3; item 15 repaired |
| Scoped local-Gemma proof-of-wiring | `PASS WITH LIMITATIONS` | 13/15 accepted when 4,5,6,11 are tolerated model limitations; 9/10 remain open |
| Required v8 diagnostic telemetry | `FAIL / NOT VERIFIED` | 0 grounding-diagnostic rows |
| Fault/concurrency, clean import/rebind, Security, release, cleanup | `NOT_VERIFIED` | Not in this rerun scope |

## Required next owner/action

1. Engineer fixes the v8 diagnostic persistence path first. The promised diagnostic row must be observable for an abstention and an answer; a swallowed/non-blocking insert error is not sufficient QA evidence.
2. Engineer uses the diagnostic output to classify items 9 and 10. Source-20 candidates are present in the active corpus, but the live failing stage is still unknown.
3. QA reruns focused items 9, 10, and 15 after diagnostic persistence is proven, then reruns the full 15-item matrix because the shared support/prompt path changed.
4. Items 4, 5, 6, and 11 remain accepted only for the local Gemma proof-of-wiring scope and must remain visible as regression cases for the future provider/model replacement.

## Final status

- Approved M7 semantic gate: `FAIL`.
- Human-scoped local proof-of-wiring: `PASS WITH LIMITATIONS`.
- v8 confirmed behavior fix: item `15` unsupported boundary now passes.
- Remaining live semantic cases: items `9` and `10`.
- Required evidence blocker: `0` persisted `grounding_diagnostic` rows.
- Next owner: `Engineer`, then `QA` for focused and full rerun.
