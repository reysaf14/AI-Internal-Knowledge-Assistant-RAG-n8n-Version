# M7 Citation and Grounding Remediation — 2026-09-20

## Finding and scope

This implementer remediation addresses the engineering findings in `.ai/reports/qa/M7-independent-qa-items-2-15-rerun-2026-09-20.md` for candidate v5:

- supported items 2, 5, and 12 reached delivery but became deterministic abstentions;
- item 13 required a no-inference check for a requested nominal not explicitly present in the retrieved evidence.

The separate dataset/corpus conflicts were resolved by Human confirmation after the engineering remediation: the active corpus is the source of truth for items 2, 4, 5, 6, 10, 11, and 12, and item 14 is replaced with a corpus-absent unsupported question. These are evaluation-oracle changes only; the corpus and runtime were not changed.

## Root cause

Retrieval was not empty. Read-only calibration against the active corpus found nearest distances `0.3392` (item 2), `0.3475` (item 5), and `0.2732` (item 12), each inside the active `minimum_similarity=0.25` acceptance boundary (distance `<= 0.75`).

The defect was in the generation/citation boundary:

1. `Validate Citation & Attach Sources` accepted only the literal `[CITATION:n]` form. The local model can return a semantically equivalent `CITATION: n` form, so a grounded answer was converted to abstention.
2. The validator used all retrieved rows even when `context_bound` meant only a subset had been shown to the model. This could attach a source that was not in the prompt.
3. The prompt did not explicitly prohibit inference of a requested specific nominal from partial compensation facts.

## Changes applied

`workflows/02-telegram-grounded-qa.json` remains a 34-node workflow. Only `Build Prompt` and `Validate Citation & Attach Sources` changed.

- The prompt now requires a citation key first, in the exact internal form `[CITATION:n]`, followed by at most two concise answer sentences.
- The model receives chunks from only the nearest source document. PostgreSQL retrieval still selects and ranks five active-corpus candidates; this is a model-context control, not a retrieval bypass.
- `prompt_evidence` records exactly the chunks delivered to the model.
- Citation validation accepts harmless bracket/spacing variants, but validates every parsed key against `prompt_evidence` only. Unknown or unprompted keys remain fail-closed to deterministic abstention.
- Internal citation tokens are removed before the readable Telegram response; source names are attached deterministically from validated metadata.
- The prompt explicitly prohibits inferring a specific nominal, identity, or policy from partial facts.

No credential, corpus document, database schema, embedding profile, retrieval threshold, or ingestion workflow was changed.

## Candidate activation

- Workflow: `02 — Telegram Grounded Q&A`, ID `IAOqkQsNamEJarHF`
- Runtime revision: `m7-citation-contract-2026-09-20-v7`
- Bounds unchanged: `output_bound=192`, `ai_timeout_max=4000 ms`
- n8n after import/restart: active, 34 nodes, healthy

## Implementer verification

All checks used synthetic questions and retained only source/citation/status metadata; no raw Telegram payload, answer body, credential, or corpus excerpt was persisted.

| Case | Local active-corpus/model result | Implementer result |
|---|---|---|
| Item 2, parking | answered; primary source `09_FAQ_Jam_Operasional_dan_Lokasi.md`; valid key | `PASS` for repaired citation path |
| Item 5, cash/setoran | answered; primary source `03_SOP_Penanganan_Kas_dan_Setoran_Harian.md`; valid keys | `PASS` for repaired citation path |
| Item 12, location | answered; primary source `09_FAQ_Jam_Operasional_dan_Lokasi.md`; valid key | Citation path `PASS`; corpus-backed oracle now applied |
| Item 13, exact base-salary nominal | no valid citation; final workflow outcome would be deterministic abstention | `PASS` for no-inference guard, pending Telegram E2E |
| Item 14, replacement travel-claim question | no corpus match; final workflow outcome should be deterministic abstention | Oracle replacement applied; pending Telegram E2E |

- Static workflow contract: JSON valid; 34 nodes; `primarySource`, `prompt_evidence`, and normalized citation guard present.
- Active-runtime verification: workflow active with all three controls present; n8n healthy.
- Regression: `python tests/harness/test_ingestion.py`, `test_qa_core.py`, and `test_delivery_core.py` passed `19/19`, `21/21`, and `27/27` respectively (`67/67`).

## Human confirmation applied

- Human confirmed that the active corpus is the source of truth for items 2, 4, 5, 6, 10, 11, and 12. `evaluation/qa-dataset.csv` now reflects the exact corpus-backed facts: parking capacity/free status, opening procedure, cash/setoran controls, closing procedure, sick-leave threshold, generic fire-extinguisher/escape-route guidance, and the actual address.
- Human confirmed replacing item 14 (`Siapa nama pemilik toko?`) with `Bagaimana prosedur klaim biaya perjalanan dinas?`, which has no approved corpus match and remains `Unsupported,FALSE`.
- No corpus re-ingestion is needed because only the evaluation oracle changed. No workflow, credential, schema, threshold, or runtime setting changed in this step.

## QA handoff

QA may now warm the local provider using its existing synthetic-only preflight and run the full 15-item matrix against runtime revision v7. No Engineer Telegram self-test was performed in this step, per Human instruction; the user and QA own the E2E execution. The required fault/concurrency, clean-instance, Security, release, and cleanup gates remain untouched.

## Verdict

`VERIFIED BY IMPLEMENTER — SCOPED CITATION/GROUNDING REMEDIATION; M7 AGGREGATE REMAINS NOT_VERIFIED`
