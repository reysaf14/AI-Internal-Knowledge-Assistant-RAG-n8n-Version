# Project State

## Identity

- Project: `Asisten Pengetahuan Internal Toko Makmur Jaya`
- Workspace-relative project path: `projects/active/AI Internal Knowledge Assistant (RAG) — n8n Version`
- Lifecycle: `ACTIVE`
- Delivery lane: `PROFESSIONAL`
- Lane decision and reason: Disetujui Human `2026-09-13`; kebijakan internal/ketenagakerjaan, kanal pesan pihak ketiga, dan keluaran AI probabilistik memerlukan design serta review independen yang proporsional.
- Last updated: `2026-09-19`
- Current stage: `ENGINEER (M6 runtime split identified; ingestion not verified)`
- Next owner: `Human/QA` (`M6 — use the project Docker n8n instance and rebind credentials`; host n8n and project Docker n8n are separate runtimes)
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
| Engineer handoff | `workflows/01-corpus-ingestion.json` (m6-aligned-v1), `workflows/02-telegram-grounded-qa.json` (m6-aligned-v1), `tests/harness/*`, `tests/mocks/ai-provider/*`, `tests/fixtures/*`, `evaluation/qa-dataset.csv` (12+3), `README.md`, `.ai/reports/build/M5-final-traceability.md`, `.ai/reports/build/M6-workflow-schema-credential-branching-alignment-report.md`, `.ai/reports/build/M6-local-ollama-provider-readiness-report.md` | `M0-M6 local provider / 2026-09-19` | `VERIFIED BY IMPLEMENTER` | M0-M5 regression remains 67/67; M6 alignment plus host-level Ollama `/v1` contract pass. Workflow exports remain DRAFT unpublished; container binding/import NOT_VERIFIED |
| DevOps handoff | `deploy/compose.yaml`, `deploy/postgres-init/01-init.sh`, `deploy/start-local.sh`, `deploy/stop-local.sh`, `.env.test`, `deploy/WORKFLOW-IMPORT-GUIDE.md` | `M6 / 2026-09-19` | `VERIFIED BY IMPLEMENTER` | local-isolated profile: n8n 1.62.1 + pgvector pg16 BOTH healthy; existing-volume alignment migration applied; local `rag_settings` populated for Ollama tester; active corpus and live ingestion remain unverified |
| Build / self-test evidence | `.ai/reports/build/M1-safe-isolated-foundation-exit-report.md`, `M2-atomic-corpus-ingestion-exit-report.md`, `M3-grounded-answer-core-exit-report.md`, `M4-telegram-delivery-deadline-exit-report.md`, `M5-portable-delivery-bundle-exit-report.md`, `M6-local-isolated-deployment-exit-report.md`, `M6-workflow-schema-credential-branching-alignment-report.md`, `M6-local-ollama-provider-readiness-report.md` | `2026-09-19` | `VERIFIED BY IMPLEMENTER` | M1 foundation; M2 19/19; M3 21/21; M4 27/27; M5 67/67; M6 deployment/alignment and host-level Ollama provider contract pass. Container binding, import, QA, and Security remain unverified |
| QA evidence | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Belum ada kandidat |
| Security evidence | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Belum ada kandidat |
| LLM routing / usage evidence | `NOT_AVAILABLE` | `NOT_AVAILABLE` | `NOT_AVAILABLE` | Telemetry belum menjadi requirement approved |
| Evaluation dataset candidate | `D:\QA_Dataset_15_Pasangan.csv` | `received 2026-09-13; SHA-256 4AA92047...46EEC` | `DRAFT` | Human confirmed synthetic; 15 rows; 4 source references are outside corpus; working copy `evaluation/qa-dataset.csv` corrected in M5: 12+3 per approved distribution (3 SOP / 3 FAQ / 2 Panduan / 3 Kebijakan / 1 Profil / 3 Unsupported). Semantic validation pending real embedding model (M7) |
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
| `2026-09-14` | Engineer menyelesaikan M0–M4 dengan self-test (M2 19/19, M3 21/21, M4 27/27) | Engineer; dicatat Engineer | All harness self-tests `VERIFIED BY IMPLEMENTER`; workflow exports draft unpublished; imports `NOT_VERIFIED` until M6 (DevOps) |
| `2026-09-14` | Engineer menyelesaikan M5: portable delivery bundle (67/67 pass), dataset corrected 12+3, README, static validation clean | Engineer; dicatat Engineer | Stage → `HANDOFF_TO_DEVOPS`; next owner DevOps (M6); Engineer scope M0–M5 complete |
| `2026-09-14` | DevOps menyelesaikan M6 local-isolated: compose.yaml (n8n 1.62.1 + pgvector pg16), DB init script (roles/schema/grants), launcher, WORKFLOW-IMPORT-GUIDE | DevOps; dicatat DevOps | Stack up & BOTH healthy; DB init + permission matrix verified; loopback-only verified; workflow import `NOT_YET` (butuh credential/owner) |
| `2026-09-14` | Init script dikonversi .sql → .sh (butuh env vars container); urutan diperbaiki: extension → roles → DB grants → schemas → grants → tables | DevOps; dicatat DevOps | Fix `role does not exist` (schema before role), `permission denied database` (missing CONNECT), missing default privileges (rag_runtime SELECT on future tables) |
| `2026-09-15` | Engineer menyelaraskan workflow–schema–credential–branching sebelum QA | Engineer; dicatat Engineer | Exports naik ke `m6-aligned-v1`; schema alignment migration ditambah; credential references pindah ke n8n store; Telegram Trigger dinaikkan ke `typeVersion 1.2` untuk secret-token verification; invalid/duplicate/abstention/failure/delivery branches tersambung; timing/state delivery diperbaiki; static contract PASS dan regresi 67/67 PASS |
| `2026-09-19` | Human menyediakan Ollama lokal sebagai tester dan Engineer memverifikasi provider contract | Human + Engineer | Ollama `/v1` host contract PASS: Qwen chat, Gemma chat, EmbeddingGemma 768-dim; workflow menonaktifkan reasoning Qwen untuk tester; next blocker adalah host-reachable binding, n8n credentials/settings, import, dan ingestion |
| `2026-09-19` | Human meminta Engineer menjalankan pengisian runtime settings lokal dengan chat ID `5578891856` | Human + Engineer | Existing-volume schema alignment migration applied; `rag.rag_settings` updated with Qwen, EmbeddingGemma 768-dim, tester bounds, timeout, and Telegram allowlist; `active_corpus_version` remains empty until ingestion succeeds |

## Latest handoff

- From stage / owner: `Engineer (M6 local Ollama provider wiring)` / `M6 — local provider binding & workflow runtime integration`
- Changed or produced artifacts: `workflows/01-corpus-ingestion.json` (`m6-aligned-v1`), `workflows/02-telegram-grounded-qa.json` (`m6-aligned-v1`), `deploy/postgres-init/01-init.sh`, `deploy/postgres-init/02-rag-schema-alignment.sql`, `deploy/postgres-init/README.md`, `deploy/WORKFLOW-IMPORT-GUIDE.md`, `README.md`, `evaluation/README.md`, `.ai/reports/build/M6-workflow-schema-credential-branching-alignment-report.md`, `.ai/reports/build/M6-local-ollama-provider-readiness-report.md`.
- Evidence and result: Ollama `0.34.0` host probes pass for `/v1/models`, `/v1/embeddings` (768 dim), Qwen `/v1/chat/completions` with `reasoning_effort=none`, and Gemma chat; n8n health is 200; existing-volume schema alignment migration and local `rag.rag_settings` update completed; Docker host gateway port 11434, live workflow execution, and active corpus remain unverified.
- Bugs fixed: (1) workflow/schema legacy column mismatch; (2) missing existing-volume schema migration; (3) `$env` credential boundary conflict; (4) missing input/dedup/abstention/failure/delivery stop branches; (5) activation could supersede the active corpus before confirming a candidate; (6) delivery timing/state fields were not populated; (7) stale import/evaluation instructions; (8) ingestion manifest reader used `json.fileName` although n8n `Read Binary Files` exposes `binary.data.fileName`; (9) failure sink discarded the upstream error message, now propagates a bounded failure reason for diagnosis; (10) settings preflight now reports the exact missing/invalid field instead of only `rag_settings_incomplete`.
- Assumptions / untested items: workflow import into n8n (AC-025) NOT yet done — waits for owner account + named credentials; container-to-Ollama reachability, Telegram webhook/send, provider profiling, live DB transaction behavior, and QA remain untested; demo-vps profile requires Human provisioning.
- Required next action: Human/QA — open the project n8n through `http://127.0.0.1:5678`, complete its owner setup if shown, import/rebind the workflows there, and use container bindings (`postgres`, `/files/docs`, `host.docker.internal:11434/v1`). M7/M8 remain out of scope for this handoff.
