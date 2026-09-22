# M7 Independent QA Full Matrix — 2026-09-20

## Verdict

`FAIL` for the current v5 candidate's full semantic/abstention matrix. Items 2–15 were sent once sequentially after an independent provider warm-up. All 14 messages reached Telegram delivery, but the matrix contains supported-question fallbacks, incomplete/incorrect supported answers, and unsupported-question leakage. Several dataset oracles also conflict with the persisted corpus and are marked `BLOCKED_ORACLE` rather than silently scored.

M7 remains not release-ready. This report is independent QA evidence; Engineer smoke reports and deterministic harness results remain separate evidence classes.

## Candidate and preconditions

- Candidate: `m6-local-gemma-bounded-2026-09-20-v5`.
- Chat model: `gemma4:e2b-it-qat`.
- Embedding model: `embeddinggemma:300m-qat-q4_0`.
- Online timeout: `4000 ms`; business deadline: `5000 ms`; Telegram reserve: `1000 ms`.
- Output bound: `192`.
- Active corpus hash prefix: `sha256:61b730...6d109`.
- Dataset: Human-reconciled synthetic 12 supported + 3 unsupported.
- Telegram target: authorized sandbox; identifier omitted.

Preflight observed n8n health/readiness HTTP 200, healthy n8n/PostgreSQL containers, and running gateway/tunnel containers. QA performed a synthetic provider warm-up from inside `rag-n8n-local` immediately before item 2:

```text
embed_rc=0|elapsed_ms=3
chat_rc=0|elapsed_ms=26
```

No credentials, payloads, transcripts, or restricted data were persisted.

## Execution boundary

- Item 1 had already passed twice under the valid post-refresh precondition, with the reconciled corpus-backed oracle.
- Items 2–15 were submitted once each, sequentially, through the authenticated Telegram sandbox.
- UI response classification and source observation were paired with the newest sanitized current-candidate ledger row and safe event after each send.
- No automatic retries were performed for items 2–15.

## Per-item result matrix

Latency is shown as `ledger claim→delivery / safe-event duration`.

| Item | Dataset class | Delivery | Source observed | Semantic / abstention result | Latency | Verdict |
|---:|---|---|---|---|---:|---|
| 1 | Supported | Delivered; valid post-refresh runs 2/2 | `21_Kebijakan_Jadwal_Shift_Kerja.md` | Grounded answer; reconciled oracle pass | `1814 / 1863 ms` latest | `PASS` |
| 2 | Supported | Delivered | None; service-unavailable fallback | Supported question failed; dataset parking oracle also conflicts with corpus | `4950 / 4996 ms` | `FAIL` |
| 3 | Supported | Delivered | `11_FAQ_Kebijakan_Retur_dan_Tukar_Barang.md` | Grounded answer with allowed source | `3748 / 3800 ms` | `PASS` |
| 4 | Supported | Delivered | `01_SOP_Buka_Toko.md` | Grounded response, but dataset timing/steps conflict with persisted source; not fairly scorable | `3672 / 3767 ms` | `BLOCKED_ORACLE` |
| 5 | Supported | Delivered | None; service-unavailable fallback | Supported question failed; dataset expected content also conflicts with persisted SOP | `3617 / 3670 ms` | `FAIL` |
| 6 | Supported | Delivered | `02_SOP_Tutup_Toko.md` | Grounded response, but dataset timing sequence conflicts with persisted SOP | `3657 / 3707 ms` | `BLOCKED_ORACLE` |
| 7 | Supported | Delivered | `16_Panduan_Komplain_Barang_Rusak.md` | Grounded answer with allowed source | `3703 / 3757 ms` | `PASS` |
| 8 | Supported | Delivered | `18_Panduan_Komplain_Keterlambatan_Pengantaran.md` | Grounded answer with allowed source | `3220 / 3262 ms` | `PASS` |
| 9 | Supported | Delivered | `20_Kebijakan_Cuti_dan_Izin_Karyawan.md` | Grounded answer with allowed source | `2133 / 2177 ms` | `PASS` |
| 10 | Supported | Delivered | `20_Kebijakan_Cuti_dan_Izin_Karyawan.md` | Response follows corpus, but dataset requires a contradictory sick-leave rule | `3182 / 3231 ms` | `BLOCKED_ORACLE` |
| 11 | Supported | Delivered | `25_Kebijakan_Keselamatan_Kerja_K3_Sederhana.md` | Source valid, but dataset's APAR counts/simulation details are not supported by persisted source; not fairly scorable | `3575 / 3624 ms` | `BLOCKED_ORACLE` |
| 12 | Supported | Delivered | None; service-unavailable fallback | Supported location question failed; dataset address also conflicts with corpus | `2271 / 2319 ms` | `FAIL` |
| 13 | Unsupported | Delivered | A corpus source was cited | Leaked a salary claim instead of exact abstention | `2296 / 2366 ms` | `FAIL` |
| 14 | Unsupported | Delivered | A corpus source was cited | Leaked an owner-name claim instead of exact abstention | `1978 / 2025 ms` | `FAIL` |
| 15 | Unsupported | Delivered | None | Correct abstention: information not found in official documents | `3001 / 3044 ms` | `PASS` |

## Aggregate observations

- Items sent in this matrix: `14/14`.
- Current-candidate delivery rows after baseline: `14/14 delivered`.
- Safe-event durations: all observed under the nominal `5000 ms` business deadline; item 2 was near the boundary and carried `provider_or_runtime_failure`.
- Semantic/source/abstention direct results: `6 PASS`, `5 FAIL`, `4 BLOCKED_ORACLE` when item 1 is included.
- Explicit failures: item 2 fallback, item 5 fallback, item 12 fallback, item 13 unsupported leakage, item 14 unsupported leakage.
- Oracle conflicts: items 2, 4, 5, 6, 10, 11, and 12 have expected answers/details that do not match the persisted corpus source content. Item 1 was reconciled separately and is not in this conflict count.

## Deterministic regression rerun

| Command | Result | Exit code |
|---|---:|---:|
| `python tests/harness/test_ingestion.py` | `19/19` passed | `0` |
| `python tests/harness/test_qa_core.py` | `21/21` passed | `0` |
| `python tests/harness/test_delivery_core.py` | `27/27` passed | `0` |
| Total | `67/67` passed | `0` |

These deterministic tests do not override the observed live Telegram semantic and abstention failures.

## Gate impact

- Telegram delivery/receipt for items 2–15: `PASS` for delivery bookkeeping only.
- 15-item latency: observed all under 5 seconds, but overall latency acceptance is `NOT_VERIFIED` because semantic acceptance failed and item 2 was near the boundary.
- Supported grounding/source: `FAIL` for explicit fallback items; several additional items `BLOCKED_ORACLE`.
- Unsupported abstention: `FAIL` because items 13 and 14 leaked answers; item 15 passed.
- Full live fault/provider/database/duplicate/concurrency matrix: `NOT_VERIFIED`.
- Clean-instance import/rebind, Security, release, and cleanup: `NOT_VERIFIED`/`NOT_STARTED`.

## QA conclusion

The current candidate is not proven usable. The live path can deliver responses within budget, but it fails required supported questions and violates the unsupported-information boundary by returning restricted-to-corpus claims for items 13 and 14. The dataset also contains multiple unresolved oracle/corpus contradictions beyond item 1, so a clean semantic score cannot be claimed until those oracles are reconciled.

## Required next action

1. Engineer fixes supported-question retrieval/provider failure behavior and the unsupported-question abstention boundary.
2. Human/Architect reconciles dataset items 2, 4, 5, 6, 10, 11, and 12 against the corpus before using them as release gates.
3. QA reruns the full 12+3 matrix after remediation and oracle reconciliation, then executes the separate live fault/concurrency and Security gates.
