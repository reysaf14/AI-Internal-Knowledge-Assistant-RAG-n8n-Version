# Project State

## Identity

- Project: `Asisten Pengetahuan Internal Toko Makmur Jaya`
- Workspace-relative project path: `projects/active/AI Internal Knowledge Assistant (RAG) — n8n Version`
- Lifecycle: `ACTIVE`
- Delivery lane: `PROFESSIONAL`
- Lane decision and reason: Disetujui Human `2026-09-13`; kebijakan internal/ketenagakerjaan, kanal pesan pihak ketiga, dan keluaran AI probabilistik memerlukan design serta review independen yang proporsional.
- Last updated: `2026-09-20`
- Current stage: `ENGINEER (M6 runtime smoke partially observed; functional delivery is intermittent and semantic QA remains open)`
- Next owner: `Engineer` (`next session: close M6 evidence and prepare an explicit handoff decision; M7/M8 remain outside Engineer scope`)
- Current release candidate: `NOT_AVAILABLE`
- DoD aggregate: `NOT_APPLICABLE`

## Milestone status as of 2026-09-20

| Milestone | Current verdict | Evidence / blocker |
|---|---|---|
| M0 — Contract & traceability baseline | `VERIFIED BY IMPLEMENTER` | Traceability baseline and planned AC ownership recorded. No known implementation blocker. |
| M1 — Safe isolated foundation | `VERIFIED BY IMPLEMENTER` | Static/config/data-boundary self-tests and isolated launcher evidence in `M1-safe-isolated-foundation-exit-report.md`. Independent QA/Security not performed. |
| M2 — Atomic corpus ingestion | `VERIFIED BY IMPLEMENTER` | Regression `19/19`; live workflow 01 produced 26 documents/297 chunks and identical rerun inserted 0 duplicates. Independent QA and live fault matrix remain open. |
| M3 — Grounded answer core | `VERIFIED BY IMPLEMENTER` for self-test; live semantic quality `NOT_VERIFIED` | Regression `21/21`; local provider HTTP path works. No M7 semantic evaluation of the real model/corpus yet. |
| M4 — Telegram delivery & deadline | `VERIFIED BY IMPLEMENTER` for harness; runtime `PARTIAL` | Regression `27/27`; real Telegram delivery was observed, but recent ledger shows 19 delivery successes and 3 `delivery_unknown` results. The `<5s`/15-item deadline is not met or verified. |
| M5 — Portable delivery bundle | `VERIFIED BY IMPLEMENTER` | Portable bundle, 12+3 working dataset, README, and `67/67` self-test evidence exist. Corpus-wide semantic dataset review remains open before QA. |
| M6 — Runtime & test-target readiness | `PARTIAL — READY FOR QA, NOT COMPLETE` | n8n/PostgreSQL/Ollama binding, live ingestion, webhook route, and temporary HTTPS path are operational. Functional Telegram delivery is intermittent; temporary tunnel cleanup and final M6 evidence remain open. |
| M7 — Independent quality & security | `NOT_STARTED / NOT_VERIFIED` | No independent QA or Security evidence exists. This is outside the current Engineer scope. |
| M8 — Human gates, demo & cleanup | `NOT_STARTED / NOT_VERIFIED` | No Human quality/release decision or authorized cleanup/revocation record exists. |

## Artifact registry

| Artifact | Path | Version / date | Status | Notes |
|---|---|---|---|---|
| Brief / Scope Card | `.ai/knowledge/project-brief.md` | `0.3 / 2026-09-13` | `APPROVED` | Professional Lane, corpus, dan rubric 12 supported + 3 unsupported disetujui Human |
| PRD | `.ai/knowledge/prd.md` | `1.0 / 2026-09-13` | `APPROVED` | Approved by Human melalui chat pada `2026-09-13` |
| Architecture / Fast technical note | `.ai/knowledge/architecture.md` | `1.2 / 2026-09-14` | `APPROVED` | Disetujui Human `2026-09-14`; milestone `M0`–`M8`, quality checkpoint, topology, dan requirement menjadi handoff aktif; belum diimplementasi/diuji |
| Acceptance & Failure Scenarios | `.ai/knowledge/architecture.md#7-acceptance--failure-scenarios` | `matrix 1.0 / 2026-09-14` | `APPROVED` | Disetujui Human `2026-09-14`; `AC-001`–`AC-027`; planned levels, bukan execution evidence |
| Environment schema | `.ai/knowledge/environment-schema.md` | `1.1 / 2026-09-14` | `APPROVED` | Disetujui Human `2026-09-14`; canonical root `.env.example`, credential binding, dan provider contract masih planned |
| ADRs | `.ai/decisions/` | `ADR-001 SUPERSEDED; ADR-002 recorded 2026-09-14` | `APPROVED` | Keputusan Human terbaru: AI boundary provider-neutral; private/self-hosted atau hosted-approved menjadi deployment profile |
| Engineer handoff | `workflows/01-corpus-ingestion.json` (m6-live-ingestion-v2), `workflows/02-telegram-grounded-qa.json` (m6-aligned-v1), `tests/harness/*`, `tests/mocks/ai-provider/*`, `tests/fixtures/*`, `evaluation/qa-dataset.csv` (12+3), `README.md`, `.ai/reports/build/M5-final-traceability.md`, `.ai/reports/build/M6-workflow-schema-credential-branching-alignment-report.md`, `.ai/reports/build/M6-local-ollama-provider-readiness-report.md`, `.ai/reports/build/M6-live-corpus-ingestion-runtime-fix-report.md` | `M0-M6 local provider / 2026-09-19` | `VERIFIED BY IMPLEMENTER` | Workflow 01 live path now reaches atomic activation: 26 documents, 297 persisted chunks, dimension 768; identical rerun inserts 0 duplicate rows. Workflow 02 runtime path remains NOT_VERIFIED |
| DevOps handoff | `deploy/compose.yaml`, `deploy/postgres-init/01-init.sh`, `deploy/start-local.sh`, `deploy/stop-local.sh`, `.env.test`, `deploy/WORKFLOW-IMPORT-GUIDE.md` | `M6 / 2026-09-19` | `VERIFIED BY IMPLEMENTER` | local-isolated profile: n8n 1.123.81 + pgvector pg16 healthy; runtime settings populated; corpus is active. Workflow 02 is imported with all four runtime credentials; temporary HTTPS route is active for test only |
| Build / self-test evidence | `.ai/reports/build/M1-safe-isolated-foundation-exit-report.md`, `M2-atomic-corpus-ingestion-exit-report.md`, `M3-grounded-answer-core-exit-report.md`, `M4-telegram-delivery-deadline-exit-report.md`, `M5-portable-delivery-bundle-exit-report.md`, `M6-local-isolated-deployment-exit-report.md`, `M6-workflow-schema-credential-branching-alignment-report.md`, `M6-local-ollama-provider-readiness-report.md`, `M6-live-corpus-ingestion-runtime-fix-report.md`, `M6-temporary-telegram-e2e-readiness-report.md` | `2026-09-20` | `VERIFIED BY IMPLEMENTER` | M2 19/19, M3 21/21, M4 27/27; live workflow 01 ingest/idempotent rerun pass; 22 runtime safe events show 19 delivery successes and 3 `delivery_unknown`; semantic Telegram quality, QA, Security, and release remain NOT_VERIFIED |
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
- Domain/DNS/TLS produksi belum tersedia; untuk test sementara digunakan Cloudflare Quick Tunnel dengan hostname ephemeral, dan hanya `/webhook/*` yang diteruskan ke n8n. `postgres-rag-runtime` dan `telegram-demo-bot` sudah tersedia pada project Docker n8n yang sedang diuji. Public GitHub push tetap menunggu sanitization/reclassification karena PRD masih menandai corpus `Confidential`.
- Temporary E2E boundary: `rag-e2e-webhook-gateway` (Caddy `2.11.4`) dan `rag-e2e-telegram-tunnel` (cloudflared `2026.9.1`) berjalan di network internal Docker; UI n8n/PostgreSQL tidak dipublikasikan. Quick Tunnel bersifat testing-only dan harus dihentikan setelah smoke test.

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
| `2026-09-19` | Human meminta Engineer menjalankan pengisian runtime settings lokal dengan Telegram allowlist runtime | Human + Engineer | Existing-volume schema alignment migration applied; `rag.rag_settings` updated with Qwen, EmbeddingGemma 768-dim, tester bounds, timeout, and Telegram allowlist; `active_corpus_version` remains empty until ingestion succeeds |
| `2026-09-19` | Engineer memperbaiki dan menjalankan live workflow 01 pada n8n Docker `1.123.81` | Engineer; `VERIFIED BY IMPLEMENTER` | Raw request construction, dropped batch state, DB-backed candidate validation, query-parameter coercion, dan idempotent empty-return diperbaiki. Corpus aktif berisi 26 dokumen/297 chunk berdimensi 768; rerun memasukkan 0 baris baru. Complete M6 tetap `NOT_VERIFIED` sampai workflow 02 beserta credential dan webhook tersedia |
| `2026-09-19` | Human meminta jalur test sementara untuk Telegram E2E | Human + Engineer | Workflow 02 diaktifkan; `WEBHOOK_URL` n8n dioverride ke Quick Tunnel HTTPS ephemeral; Caddy hanya meneruskan `/webhook/*`; synthetic POST ke registered Telegram route mencapai n8n dan ditolak dengan `403 Provided secret is not valid`, membuktikan route hidup. Functional Telegram message test masih pending |
| `2026-09-19` | Engineer menelusuri fallback 22:17 dan status `processing` yang tidak selesai | Engineer; `VERIFIED BY IMPLEMENTER` | Root cause delivery bookkeeping: `Telegram Send` mengganti item dengan respons API sehingga `updateId`, `bot_scope_hash`, `config_revision`, dan `active_corpus_version` hilang sebelum `Mark Delivered`. Context-preserving node ditambahkan, workflow lama diperbarui dan diaktifkan kembali; regresi M4 27/27 PASS. Pesan Telegram nyata setelah perbaikan masih pending |
| `2026-09-19` | Engineer menelusuri tidak adanya respons setelah workflow diaktifkan ulang | Engineer; `VERIFIED BY IMPLEMENTER` | Direct workflow patch sempat menghilangkan credential IDs karena source export hanya memuat nama; n8n log menunjukkan `Found credential with no ID` dan update baru tidak masuk ledger. Credential IDs dipasang kembali pada 12 binding node, workflow direstart, log aktivasi bersih, dan health check PASS. Functional Telegram message test masih pending |
| `2026-09-19` | Engineer menelusuri fallback setelah trigger dan delivery kembali normal | Engineer; `VERIFIED BY IMPLEMENTER` | Ollama embedding/chat dan reproduksi query pgvector lulus independen. Workflow 02 dinormalisasi agar vector embedding dibawa sebagai scalar item sebelum PostgreSQL retrieval; context event dipulihkan setelah node SQL yang dapat mengosongkan output. Workflow aktif direstart tanpa error; functional Telegram answer masih pending |
| `2026-09-19` | Engineer menelusuri pesan terakhir yang tidak terlihat di Telegram | Engineer; `VERIFIED BY IMPLEMENTER` | Ledger menunjukkan update masuk dan berakhir `delivery_unknown`/`telegram_send_ambiguous` setelah sekitar 15,8 detik; kegagalan terbaru terlokalisasi di `Telegram Send`, bukan provider RAG. `Delivery Failure` dipatch untuk merekam detail error Telegram yang disanitasi; workflow aktif direstart. Satu uji manusia diperlukan untuk membaca penyebab API/network tanpa retry otomatis |
| `2026-09-20` | Human meminta sesi dihentikan dan status milestone ditutup sementara | Human + Engineer | Status persisten diperbarui: M0–M5 self-test `VERIFIED BY IMPLEMENTER`, M6 `PARTIAL / READY FOR QA`, M7–M8 `NOT_STARTED / NOT_VERIFIED`. TODO sesi berikutnya dibuat; tidak ada perubahan runtime baru. |

## Latest handoff

- From stage / owner: `Engineer (M6 live ingestion runtime fix)` / `M6 — local provider and workflow runtime integration`
- Changed or produced artifacts: `workflows/01-corpus-ingestion.json` (`m6-live-ingestion-v2`), `workflows/02-telegram-grounded-qa.json` (`m6-telegram-context-v2`), live workflows `01 — Corpus Ingestion` / `02 — Telegram Grounded Q&A`, `deploy/compose.yaml` (runtime webhook overrides parameterized), `deploy/e2e-temp/Caddyfile` (temporary), `deploy/WORKFLOW-IMPORT-GUIDE.md`, and `.ai/reports/build/M6-live-corpus-ingestion-runtime-fix-report.md` / `M6-temporary-telegram-e2e-readiness-report.md`.
- Evidence and result: n8n `1.123.81` and PostgreSQL/pgvector are healthy; container-to-Ollama embedding succeeds; active corpus has 26 distinct sources, 297 chunks, and dimension 768; identical rerun inserts 0 rows and leaves counts unchanged. Workflow 02 original ID is active, its Telegram POST route is registered, the imported duplicate is inactive, and the synthetic public request reaches n8n and receives the expected invalid-secret rejection. M2/M3/M4 regressions pass 19/19, 21/21, and 27/27. Recent runtime safe events show 19 delivery successes and 3 ambiguous delivery failures; evidence is `VERIFIED BY IMPLEMENTER`, while semantic answer quality and deadline acceptance remain unverified.
- Bugs fixed: (1) large inline embedding request produced invalid/empty transport body; (2) PostgreSQL version-upsert dropped the batch before insert; (3) candidate validation trusted in-memory counts instead of persisted rows; (4) cross-node parameter arrays were coerced to an unsupported type; (5) all-conflict rerun returned no identity for downstream validation; (6) Telegram delivery bookkeeping lost context after the send node; (7) live workflow bindings lost n8n credential IDs during direct node replacement; (8) retrieval vector crossed the n8n Postgres boundary through a fragile cross-node expression; (9) SQL bookkeeping nodes could drop event context before safe-event recording.
- Assumptions / untested items: live invalid/timeout/provider/database/concurrency faults were not rerun; Telegram delivery is only partially reliable (19 successes, 3 `delivery_unknown`) and grounded answer/source quality was not independently scored; the Quick Tunnel is not production infrastructure; QA, Security, latency 15/15, demo-vps, M7, and M8 remain untested/out of scope.
- Required next action: On the next session, Engineer reconciles the M6 runtime evidence and the Qwen context/latency mismatch, then prepares the M6-to-QA handoff decision. Do not start M7/M8 automatically; Human selects the next owner and exact QA target.
