# Project State

## Identity

- Project: `Asisten Pengetahuan Internal Toko Makmur Jaya`
- Workspace-relative project path: `projects/active/AI Internal Knowledge Assistant (RAG) — n8n Version`
- Lifecycle: `ACTIVE`
- Delivery lane: `PROFESSIONAL`
- Lane decision and reason: Disetujui Human `2026-09-13`; kebijakan internal/ketenagakerjaan, kanal pesan pihak ketiga, dan keluaran AI probabilistik memerlukan design serta review independen yang proporsional.
- Last updated: `2026-09-13`
- Current stage: `PM`
- Next owner: `Architect`
- Current release candidate: `NOT_AVAILABLE`
- DoD aggregate: `NOT_APPLICABLE`

## Artifact registry

| Artifact | Path | Version / date | Status | Notes |
|---|---|---|---|---|
| Brief / Scope Card | `.ai/knowledge/project-brief.md` | `0.3 / 2026-09-13` | `APPROVED` | Professional Lane, corpus, dan rubric 12 supported + 3 unsupported disetujui Human |
| PRD | `.ai/knowledge/prd.md` | `1.0 / 2026-09-13` | `APPROVED` | Approved by Human melalui chat pada `2026-09-13` |
| Architecture / Fast technical note | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | PRD approved; next owner Architect |
| Acceptance & Failure Scenarios | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Akan diturunkan dari requirement approved |
| Environment schema | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Bukan output tahap PM |
| ADRs | `.ai/decisions/` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Tidak ada keputusan teknis yang dicatat pada intake |
| Engineer handoff | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Belum masuk tahap implementasi |
| DevOps handoff | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Belum dinilai |
| Build / self-test evidence | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Belum ada kandidat |
| QA evidence | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Belum ada kandidat |
| Security evidence | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Belum ada kandidat |
| LLM routing / usage evidence | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Telemetry belum menjadi requirement approved |
| Evaluation dataset candidate | `D:\QA_Dataset_15_Pasangan.csv` | `received 2026-09-13` | `DRAFT` | Human confirmed synthetic; 15 rows; 4 source references are outside corpus; requires 12+3 working-copy adjustment before approval |
| Definition of Done assessment | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_APPLICABLE` | Belum ada kandidat |
| Release packet | `.ai/release-packet.md` | `NOT_AVAILABLE` | `NOT_APPLICABLE` | Dibuat mendekati quality/release gate |

## Human gates

| Gate | Artifact / scope | Decision | Approved by | Date | Source / note |
|---|---|---|---|---|---|
| Scope & lane | Scope Card `0.3`; lane `PROFESSIONAL`; corpus seluruh `/docs`; rubric 12 supported + 3 unsupported | `APPROVED` | Human | `2026-09-13` | Persetujuan bertahap melalui chat: lane/scope, corpus, lalu komposisi rubric |
| PRD | `.ai/knowledge/prd.md` version `1.0` | `APPROVED` | Human | `2026-09-13` | Approval eksplisit melalui chat |
| Architecture | `NOT_AVAILABLE` | `NOT_AVAILABLE` | | | Next gate; Architect dapat mulai dari PRD approved |
| Quality | `NOT_AVAILABLE` | `NOT_AVAILABLE` | | | Belum ada kandidat/evidence |
| Release / deploy | `NOT_AVAILABLE` | `NOT_AVAILABLE` | | | Belum ada kandidat/release packet |

## Current scope and risk notes

- Business outcome: jawaban karyawan lebih konsisten dan interupsi repetitif kepada manajer berkurang, dengan jawaban dibatasi pada SOP/kebijakan resmi.
- Data classification and allowed agent/artifact representation: dokumen kebijakan awalnya `Confidential` dan hanya `minimized-and-masked`; artefak/test memakai `synthetic`; credential, record HR/pelanggan, transaksi, dan payload produksi adalah `Restricted` serta `blocked`.
- In scope: seluruh isi `/docs` dengan baseline 26 dokumen Markdown `00`–`25`, tanya-jawab internal via bot Telegram bersama, sumber jawaban, abstention, pemuatan ulang, panduan, evaluasi, dan demo tersanitasi.
- Out of scope: akses pelanggan langsung, POS/stok real-time, autentikasi/personalization per karyawan, topik di luar dokumen, record individual/Restricted.
- Known limitations / blockers: kandidat eval set dikonfirmasi sintetis dan tidak lagi diblokir oleh klasifikasi data, tetapi masih memuat 4 referensi sumber di luar corpus dan memerlukan penyesuaian salinan kerja menjadi 12 supported + 3 unsupported. Detail sumber pemuatan dan retensi percakapan menunggu tahap desain. Pemilik/manajer diasumsikan sebagai pengesah corpus dan owner operasi sementara.

## Decision log

| Date | Decision | Human / source | Effect |
|---|---|---|---|
| `2026-09-13` | Professional Lane dan arah scope version `0.1` disetujui | Human, chat | Lane dikunci `PROFESSIONAL`; data handling pada Scope Card tetap berlaku |
| `2026-09-13` | Corpus mencakup seluruh isi folder `/docs` | Human, chat | Scope direvisi menjadi version `0.2`; baseline 26 file Markdown `00`–`25` |
| `2026-09-13` | Komposisi evaluasi dipertahankan pada 12 supported + 3 unsupported | Human, chat | Scope Card `0.3` dan Scope & Lane gate menjadi `APPROVED`; PRD dapat disusun |
| `2026-09-13` | Seluruh isi kandidat eval set dikonfirmasi sintetis | Human, chat | Data class menjadi `Internal / synthetic`; blokir klasifikasi dicabut, penyesuaian struktur tetap diperlukan |
| `2026-09-13` | PRD version `1.0` disetujui | Human, chat | PRD gate menjadi `APPROVED`; project siap diserahkan ke Architect |

## Latest handoff

- From stage / owner: `PM`
- Changed or produced artifacts: Scope Card `.ai/knowledge/project-brief.md` version `0.3` approved; PRD `.ai/knowledge/prd.md` version `1.0` created; `.ai/project-state.md` updated `2026-09-13`.
- Evidence and result: Scope & Lane gate `APPROVED`; PRD version `1.0` `APPROVED` oleh Human pada `2026-09-13`. Human mengonfirmasi kandidat eval set sepenuhnya sintetis; statusnya `DRAFT` karena masih memerlukan penyesuaian 12+3.
- Assumptions / untested items: kesesuaian semantik jawaban kandidat dataset terhadap corpus belum diverifikasi; salinan kerja 12+3 belum dibuat; tidak ada runtime atau integrasi yang diuji; pemilik/manajer masih diasumsikan sebagai owner operasi awal.
- Required next action and gate: handoff ke Architect untuk menyusun desain berdasarkan PRD version `1.0`. Human harus menyetujui architecture sebelum Engineer mulai. Penyesuaian eval set dilakukan pada salinan kerja di tahap berikutnya; file sumber tetap dipertahankan.
