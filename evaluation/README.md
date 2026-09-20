# Evaluation Dataset & Rubric — Asisten Pengetahuan Internal Toko Makmur Jaya

Architecture version: 1.2
Dataset: `evaluation/qa-dataset.csv`
Composition: 12 supported + 3 unsupported
Status: APPROVED FOR V7 QA RERUN — corpus-backed oracle reconciliation and item-14 replacement approved by Human on 2026-09-20; execution and verdict remain QA-owned

## Dataset contract

The CSV is authoritative. It contains 15 data rows after the commented metadata and header:

- 12 supported questions: 3 FAQ, 3 SOP, 2 Panduan, 3 Kebijakan Internal, 1 Profil Perusahaan.
- 3 unsupported questions: no approved source and expected abstention.
- Every supported source label must match one of the 26 files in `docs/`.

Human approved the corpus-backed interpretation for items 1, 2, 4, 5, 6, 10, 11, and 12. The working oracle now follows the active corpus for those items, including the replacement of item 14 with the corpus-absent question `Bagaimana prosedur klaim biaya perjalanan dinas?`. Synthetic data and sanitized evidence only; no production records, credentials, or raw Telegram payloads. QA must still verify the responses, citations, abstentions, delivery, and latency independently.

## Rubric

### Supported questions

PASS requires all of:

- mandatory facts from `Jawaban_Benar` are conveyed;
- no contradiction or unsupported policy claim;
- at least one exact, relevant `source_name` is cited.

FAIL if a mandatory fact is missing, the answer contradicts the source, or the citation is absent/incorrect.

### Unsupported questions

PASS only if the response clearly states that the information was not found in the official documents and does not guess, speculate, or cite a source.

### Aggregate gates

- Content: 15/15 questions pass the applicable rubric.
- Source accuracy: 12/12 supported questions cite a correct source; unsupported questions cite none.
- Latency: 15/15 complete under 5,000 ms from workflow receive to Telegram send success.
- Delivery failures or `delivery_unknown` do not count as passing latency/content evidence.

## Frozen run configuration

The primary QA run must record the exact values used for:

| Parameter | Source |
|---|---|
| `config_revision` | `rag.rag_settings` |
| `chat_model` | `rag.rag_settings` / provider inventory |
| `embedding_model` | `rag.rag_settings` / provider inventory |
| `embedding_profile_id` | `rag.rag_settings` |
| `embedding_dimension` | `rag.rag_settings` |
| `retrieval_limit`, `minimum_similarity` | `rag.rag_settings` after calibration |
| `context_bound`, `output_bound` | `rag.rag_settings` |
| `ai_timeout_max` | `rag.rag_settings` after provider profiling |
| `corpus_version` | active corpus selected by ingestion |
| temperature | workflow contract; currently `0` for provider requests |

No parameter may change between questions in a primary run.

## Rerun rules

1. Declare the first run as the primary run before execution.
2. Label any rerun (`rerun-1`, `rerun-2`) and record the reason and impact.
3. Do not replace primary evidence without a documented reason.
4. Run questions sequentially with the same frozen configuration.
5. Record provider readiness/warm-up separately from required evidence.

## Evidence artifacts

Each run produces sanitized artifacts only:

- `run_<label>_timestamp.jsonl`: question, answer, sources, latency, and per-question result;
- `run_<label>_summary.md`: content, source, abstention, latency, and delivery aggregates;
- `run_<label>_config.json`: frozen runtime configuration.

Do not store credentials, raw provider bodies, raw Telegram payloads, or PII.

## Approval chain

1. Engineer prepares this working copy and the CSV.
2. Human approves the 12+3 composition and source semantics.
3. Engineer freezes runtime values after M7 calibration.
4. QA executes against the approved dataset.
5. Security audits the same candidate and deployment configuration.
6. Human makes the quality/release decision.
