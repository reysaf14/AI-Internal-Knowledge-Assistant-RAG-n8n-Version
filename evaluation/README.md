# Evaluation Dataset & Rubric — Asisten Pengetahuan Internal Toko Makmur Jaya
# Architecture version: 1.2 | Environment Schema version: 1.1
# =============================================================================
# This document describes the approved eval dataset, rubric, config revision,
# model/corpus identity, and rerun rules.
# =============================================================================

## 1. Dataset Composition (Approved 12 Supported + 3 Unsupported)

| # | Pertanyaan | Kategori | Supported | Dokumen Sumber |
|---|------------|----------|-----------|----------------|
| 1 | Jam berapa toko buka hari Senin? | FAQ | TRUE | 09_FAQ_Jam_Operasional_dan_Lokasi.md |
| 2 | Bagaimana prosedur membuka toko menurut SOP? | SOP | TRUE | 01_SOP_Buka_Toko.md |
| 3 | Apa saja isi SOP Penanganan Kas dan Setoran Harian? | SOP | TRUE | 03_SOP_Penanganan_Kas_dan_Setoran_Harian.md |
| 4 | Berapa hari cuti tahunan karyawan setelah 1 tahun kerja? | Kebijakan Internal | TRUE | 20_Kebijakan_Cuti_dan_Izin_Karyawan.md |
| 5 | Bagaimana ketentuan izin sakit kurang dari 3 hari? | Kebijakan Internal | TRUE | 20_Kebijakan_Cuti_dan_Izin_Karyawan.md |
| 6 | Berapa bonus bulanan jika pencapaian penjualan 115%? | Kebijakan Internal | TRUE | 24_Kebijakan_Bonus_dan_Insentif_Penjualan.md |
| 7 | Apakah toko menyediakan parkir untuk pelanggan? | FAQ | TRUE | 09_FAQ_Jam_Operasional_dan_Lokasi.md |
| 8 | Apa prosedur tutup toko pada pukul 21:00? | SOP | TRUE | 02_SOP_Tutup_Toko.md |
| 9 | Bagaimana kebijakan K3 terkait APAR dan jalur evakuasi? | Kebijakan Internal | TRUE | 25_Kebijakan_Keselamatan_Kerja_K3_Sederhana.md |
| 10 | Di mana lokasi Toko Makmur Jaya? | Profil Perusahaan | TRUE | 00_Company_Profile_Toko_Makmur_Jaya.md |
| 11 | Apa syarat mendapatkan bonus tahunan (THR + Performance)? | Kebijakan Internal | TRUE | 24_Kebijakan_Bonus_dan_Insentif_Penjualan.md |
| 12 | Berapa lama cuti melahirkan yang diberikan? | Kebijakan Internal | TRUE | 20_Kebijakan_Cuti_dan_Izin_Karyawan.md |
| 13 | Apa yang harus dilakukan jika lantai basah di area kerja? | Kebijakan Internal | TRUE | 25_Kebijakan_Keselamatan_Kerja_K3_Sederhana.md |
| 14 | Berapa nominal gaji pokok karyawan baru? | — | FALSE | (none) |
| 15 | Siapa nama pemilik toko? | — | FALSE | (none) |
| 16 | Bagaimana cara mengajukan pinjaman ke manajer? | — | FALSE | (none) |

**Category Distribution (Supported):**
- SOP Operasional: 3 (items 2, 3, 8)
- FAQ Pelanggan: 2 (items 1, 7) — *Note: PRD specifies 3 FAQ; this working copy has 2. Awaiting Human approval to adjust.*
- Panduan Komplain: 0 — *Note: PRD specifies 2. Awaiting Human approval.*
- Kebijakan Internal: 6 (items 4, 5, 6, 9, 11, 12, 13) — *Note: PRD specifies 3. This working copy has 7. Awaiting Human approval.*
- Profil Perusahaan: 1 (item 10)

**Unsupported (3):** Items 14, 15, 16 — verified semantically against entire corpus; no document contains answers.

> **STATUS: DRAFT — REQUIRES HUMAN APPROVAL** after corpus-wide semantic verification.
> Source candidate CSV has 4 rows referencing docs 26/27/29 (outside corpus 00-25).
> This working copy adjusts to 12+3 with synthetic corpus subset.
> Human must approve final composition before QA.

## 2. Rubric (Binary Per-Question)

### Supported Questions (12 items)
**PASS** if ALL of:
- All mandatory facts from `Jawaban_Benar` are conveyed
- No contradiction with source document
- No unsupported policy claims added
- At least one correct `source_name` cited (exact filename match)
- Any additional sources cited are relevant

**FAIL** if ANY:
- Missing mandatory fact
- Contradicts source document
- Adds unsupported policy claim
- No source cited OR incorrect source cited

### Unsupported Questions (3 items)
**PASS** only if:
- Clearly states "informasi tidak ditemukan" / "tidak diketahui" / equivalent
- Does NOT guess or speculate
- Does NOT cite any source (or explicitly states "tidak ada sumber")

**FAIL** if ANY:
- Provides a policy claim/answer
- Cites a fake source
- Ambiguous/hedging without clear abstention

### Source Accuracy (Separate Gate)
- **12/12** supported questions MUST cite at least one correct `source_name`
- Every additional source cited must be relevant
- Unsupported questions MUST NOT cite sources

### Latency Gate (Hard)
- **15/15** questions MUST complete < 5,000 ms each
- Measured from workflow receive → Telegram send success
- Individual measurement (not average)
- Failed/send_unknown items do NOT count as pass

## 3. Frozen Configuration (Must Be Identical for All Runs)

| Parameter | Value | Source |
|-----------|-------|--------|
| `config_revision` | `2026-09-14-v1` | Engineer sets after calibration |
| `chat_model` | `provider:model-id@version` | Human + Engineer / provider inventory |
| `embedding_model` | `provider:model-id@version` | Human + Engineer / provider inventory |
| `embedding_profile_id` | `hash(embedding_model + norm + dim)` | Engineer |
| `embedding_dimension` | `INTEGER` | Engineer / `RAG_EMBEDDING_DIMENSION` |
| `retrieval_limit` | `5` | Engineer calibrated |
| `minimum_similarity` | `0.75` | Engineer calibrated |
| `context_bound` | `3000` | Engineer calibrated |
| `output_bound` | `500` | Engineer calibrated |
| `N8N_AI_TIMEOUT_MAX` | `INTEGER ms` | Engineer + DevOps profiled |
| Corpus version | `manifest_hash` | From ingestion run |
| Question order | As listed in qa-dataset.csv | Fixed |
| Temperature | Minimum supported by runtime | Fixed |

## 4. Rerun Rules

1. **First declared run** = primary evidence (must be explicitly declared before execution)
2. **Reruns** must be labeled (e.g., `rerun-1`, `rerun-2`) with reason documented
3. Reruns do NOT replace primary evidence without documented reason + impact record
4. All runs use same frozen config (no parameter changes between runs)
5. Sequential execution (single user simulation); no parallel requests
6. Warm-up: provider/model readiness check documented before required run
7. Cold/idle starts recorded separately as exploratory (not required)

## 5. Evidence Artifacts (Per Run)

Each run must produce sanitized evidence:
- `run_<label>_timestamp.jsonl` — per-question: question, answer, sources, latency_ms, pass/fail per rubric
- `run_<label>_summary.md` — aggregate: content accuracy (X/15), source accuracy (Y/12), abstention (Z/3), latency (15/15 < 5000ms)
- `run_<label>_config.json` — frozen config used
- No raw payloads, credentials, PII, or execution bodies

## 6. Approval Chain

1. Engineer prepares working copy (this document + qa-dataset.csv)
2. Human performs corpus-wide semantic verification → approves 12+3 composition
3. Engineer freezes config_revision after calibration (M2/M3)
4. QA executes on approved dataset + frozen config
5. Security audits same candidate + deployment config
6. Human quality gate → release/deploy decision