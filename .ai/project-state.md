# Project State

## Identity

- Project: `Asisten Pengetahuan Internal Toko Makmur Jaya`
- Workspace-relative project path: `projects/active/AI Internal Knowledge Assistant (RAG) — n8n Version`
- Lifecycle: `ACTIVE`
- Delivery lane: `PROFESSIONAL`
- Lane decision and reason: Disetujui Human `2026-09-13`; kebijakan internal/ketenagakerjaan, kanal pesan pihak ketiga, dan keluaran AI probabilistik memerlukan design serta review independen yang proporsional.
- Last updated: `2026-09-14`
- Current stage: `ARCHITECT`
- Next owner: `Engineer` (`M0 — Contract & traceability baseline`; belum dimulai)
- Current release candidate: `NOT_AVAILABLE`
- DoD aggregate: `NOT_APPLICABLE`

## Artifact registry

| Artifact | Path | Version / date | Status | Notes |
|---|---|---|---|---|
| Brief / Scope Card | `.ai/knowledge/project-brief.md` | `0.3 / 2026-09-13` | `APPROVED` | Professional Lane, corpus, dan rubric 12 supported + 3 unsupported disetujui Human |
| PRD | `.ai/knowledge/prd.md` | `1.0 / 2026-09-13` | `APPROVED` | Approved by Human melalui chat pada `2026-09-13` |
| Architecture / Fast technical note | `.ai/knowledge/architecture.md` | `1.2 / 2026-09-14` | `APPROVED` | Disetujui Human `2026-09-14`; milestone `M0`–`M8`, quality checkpoint, topology, dan requirement menjadi handoff aktif; belum diimplementasi/diuji |
| Acceptance & Failure Scenarios | `.ai/knowledge/architecture.md#7-acceptance--failure-scenarios` | `matrix 1.0 / 2026-09-14` | `APPROVED` | Disetujui Human `2026-09-14`; `AC-001`–`AC-027`; planned levels, bukan execution evidence |
| Environment schema | `.ai/knowledge/environment-schema.md` | `1.1 / 2026-09-14` | `APPROVED` | Disetujui Human `2026-09-14`; canonical root `.env.example`, credential binding, dan provider contract masih planned |
| ADRs | `.ai/decisions/` | `ADR-001 SUPERSEDED; ADR-002 recorded 2026-09-14` | `APPROVED` | Keputusan Human terbaru: AI boundary provider-neutral; private/self-hosted atau hosted-approved menjadi deployment profile |
| Engineer handoff | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Belum masuk tahap implementasi |
| DevOps handoff | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Belum dinilai |
| Build / self-test evidence | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Belum ada kandidat |
| QA evidence | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Belum ada kandidat |
| Security evidence | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Belum ada kandidat |
| LLM routing / usage evidence | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Telemetry belum menjadi requirement approved |
| Evaluation dataset candidate | `D:\QA_Dataset_15_Pasangan.csv` | `received 2026-09-13; SHA-256 4AA92047...46EEC` | `DRAFT` | Human confirmed synthetic; 15 rows; 4 source references are outside corpus; category distribution and corpus-wide semantic support still require 12+3 working-copy adjustment before approval |
| Definition of Done assessment | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_APPLICABLE` | Belum ada kandidat |
| Release packet | `.ai/release-packet.md` | `NOT_AVAILABLE` | `NOT_APPLICABLE` | Dibuat mendekati quality/release gate |

## Human gates

| Gate | Artifact / scope | Decision | Approved by | Date | Source / note |
|---|---|---|---|---|---|
| Scope & lane | Scope Card `0.3`; lane `PROFESSIONAL`; corpus seluruh `/docs`; rubric 12 supported + 3 unsupported | `APPROVED` | Human | `2026-09-13` | Persetujuan bertahap melalui chat: lane/scope, corpus, lalu komposisi rubric |
| PRD | `.ai/knowledge/prd.md` version `1.0` | `APPROVED` | Human | `2026-09-13` | Approval eksplisit melalui chat |
| Architecture | `.ai/knowledge/architecture.md` version `1.2`; matrix `1.0`; environment schema `1.1` | `APPROVED` | Human | `2026-09-14` | Approval eksplisit melalui chat untuk milestone `M0`–`M8`; Engineer dapat mulai dari `M0`, tanpa izin deploy atau public push |
| Quality | `NOT_AVAILABLE` | `NOT_AVAILABLE` | | | Belum ada kandidat/evidence |
| Release / deploy | `NOT_AVAILABLE` | `NOT_AVAILABLE` | | | Belum ada kandidat/release packet |

## Current scope and risk notes

- Business outcome: jawaban karyawan lebih konsisten dan interupsi repetitif kepada manajer berkurang, dengan jawaban dibatasi pada SOP/kebijakan resmi.
- Data classification and allowed agent/artifact representation: dokumen kebijakan awalnya `Confidential` dan hanya `minimized-and-masked`; artefak/test memakai `synthetic`; credential, record HR/pelanggan, transaksi, dan payload produksi adalah `Restricted` serta `blocked`.
- In scope: seluruh isi `/docs` dengan baseline 26 dokumen Markdown `00`–`25`, tanya-jawab internal via bot Telegram bersama, sumber jawaban, abstention, pemuatan ulang, panduan, evaluasi, dan demo tersanitasi.
- Out of scope: akses pelanggan langsung, POS/stok real-time, autentikasi/personalization per karyawan, topik di luar dokumen, record individual/Restricted.
- Approved runtime direction recorded by Architect: Docker Compose pada VPS Ubuntu 24.04 (RAM 2 GB, 2 vCPU); AI provider berada di luar core stack dan dipilih saat provisioning melalui binding generik. Endpoint dapat private/self-hosted atau hosted yang disetujui; tidak ada vendor, model, host, accelerator, atau teknologi tunnel yang di-hard-code di repository.
- Planned runtime: Caddy + n8n regular mode + satu PostgreSQL/pgvector cluster di VPS; tepat dua workflow export; no Redis/worker/community node/custom service.
- Known limitations / blockers: kandidat eval set dikonfirmasi sintetis, tetapi empat source reference di luar corpus tidak otomatis berarti unsupported. Corpus lain memuat sebagian fakta terkait, dan distribusi kategori kandidat belum sesuai rubric 12+3. Salinan kerja harus diverifikasi semantik terhadap seluruh corpus dan disahkan Human sebelum QA.
- Hard technical risk: target `<5,0 detik` belum dibuktikan pada provider/model/topology yang akan dipilih. Internal timeout, warm-state behavior, dan retrieval values tetap `UNKNOWN` sampai profiling; requirement tidak dilonggarkan.
- Domain/DNS/TLS dan credential belum diprovision oleh Human. Public GitHub push juga menunggu sanitization/reclassification karena PRD masih menandai corpus `Confidential`.

## Decision log

| Date | Decision | Human / source | Effect |
|---|---|---|---|
| `2026-09-13` | Professional Lane dan arah scope version `0.1` disetujui | Human, chat | Lane dikunci `PROFESSIONAL`; data handling pada Scope Card tetap berlaku |
| `2026-09-13` | Corpus mencakup seluruh isi folder `/docs` | Human, chat | Scope direvisi menjadi version `0.2`; baseline 26 file Markdown `00`–`25` |
| `2026-09-13` | Komposisi evaluasi dipertahankan pada 12 supported + 3 unsupported | Human, chat | Scope Card `0.3` dan Scope & Lane gate menjadi `APPROVED`; PRD dapat disusun |
| `2026-09-13` | Seluruh isi kandidat eval set dikonfirmasi sintetis | Human, chat | Data class menjadi `Internal / synthetic`; blokir klasifikasi dicabut, penyesuaian struktur tetap diperlukan |
| `2026-09-13` | PRD version `1.0` disetujui | Human, chat | PRD gate menjadi `APPROVED`; project siap diserahkan ke Architect |
| `2026-09-14` | Keputusan runtime Human dipersist: VPS Ubuntu 24.04 2 GB/2 vCPU menjalankan Docker; Ollama tetap di PC 16 GB/RTX 2060 6 GB; domain disiapkan Human terakhir | Human, chat; dicatat Architect | Menjadi dasar `ADR-001` dan architecture `1.0` |
| `2026-09-14` | Repository harus model-neutral walau demo awal memakai dua model lokal yang dipilih Human | Human, chat; dicatat Architect | Model ID/digest menjadi runtime binding dan evidence, bukan konstanta repository |
| `2026-09-14` | Architecture `1.0`, environment schema `1.0`, dan Acceptance Matrix `1.0` selesai sebagai draft | Architect | Gate Architecture menjadi `AWAITING_HUMAN_APPROVAL`; tidak ada implementasi/deploy/test yang diotorisasi |
| `2026-09-14` | Human meminta bagian LLM lokal dibuat general | Human, chat; dicatat Architect | `ADR-001` digantikan `ADR-002`; architecture/environment schema naik ke `1.1` dengan provider-neutral AI boundary. Matrix tetap `1.0` karena requirement dan AC tidak berubah |
| `2026-09-14` | Architecture `1.1`, Acceptance Matrix `1.0`, dan Environment Schema `1.1` disetujui | Human, chat; dicatat Architect | Gate Architecture menjadi `APPROVED`; project siap untuk handoff ke Engineer tanpa memberi izin deploy atau public push |
| `2026-09-14` | Human meminta tahap/milestone untuk meringankan beban Engineer dan menjaga kualitas sejak awal | Human, chat; dicatat Architect | Architecture naik ke `1.2` dengan milestone `M0`–`M8`; gate dibuka ulang. Matrix `1.0`, environment schema `1.1`, topology, dan requirement tidak berubah |
| `2026-09-14` | Architecture `1.2` beserta milestone `M0`–`M8` disetujui | Human, chat; dicatat Architect | Gate Architecture kembali `APPROVED`; next owner Engineer dan titik mulai dibatasi pada `M0` |

## Latest handoff

- From stage / owner: `Architect` / Professional Lane
- Changed or produced artifacts: `.ai/knowledge/architecture.md` version `1.2` dengan milestone `M0`–`M8`; Acceptance Matrix `1.0` (`AC-001`–`AC-027`, unchanged); `.ai/knowledge/environment-schema.md` content version `1.1` hanya diperbarui cross-reference; state updated `2026-09-14`.
- Evidence and result: Human menyetujui architecture `1.2` melalui chat pada `2026-09-14`; Acceptance Matrix `1.0` dan environment schema `1.1` tetap berlaku. Delivery terbagi menjadi Engineer `M0`–`M5`, DevOps `M6`, QA/Security `M7`, dan Human/DevOps `M8`, masing-masing dengan exit criterion. Approval desain bukan implementation atau test evidence.
- Assumptions / untested items: no workflow/config/template/container/credential exists; no provider/model/network/Telegram/runtime test has run. Exact image versions, AI provider binding, internal timeout, chunk/retrieval parameters, and final eval working copy remain unresolved by their assigned owners. Latency `<5,0 detik`, public sanitization, and VPS capacity remain unverified risks.
- Required next action and gate: Engineer mulai hanya dari `M0 — Contract & traceability baseline`, menghasilkan mapping `REQ → AC → implementation → test` serta inventory prerequisite/`UNKNOWN`, lalu berhenti pada checkpoint `M0` sebelum `M1`. Provider selection/provisioning tetap milik Human/DevOps; deployment dan public push memerlukan gate Human terpisah.
