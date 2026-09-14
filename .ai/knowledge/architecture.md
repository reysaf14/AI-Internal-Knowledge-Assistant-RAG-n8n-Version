# Arsitektur — Asisten Pengetahuan Internal Toko Makmur Jaya

- Delivery lane: `PROFESSIONAL`
- Architecture version: `1.2`
- Matrix version: `1.0`
- Tanggal: `2026-09-14`
- Status: `APPROVED`
- Input approved: `.ai/knowledge/prd.md` version `1.0`
- Keputusan terkait: `.ai/decisions/adr-002-provider-neutral-ai-boundary.md` (menggantikan `ADR-001`)

Dokumen ini adalah desain, bukan bukti implementasi. Workflow, container, fixture, credential, deployment, dan pengujian yang disebutkan di bawah belum dibuat atau dijalankan.

## 1. Pendekatan Utama dan Alasan

### Ringkasan keputusan

Arsitektur menggunakan dua workflow n8n dan satu stack Docker Compose ringan pada VPS Ubuntu 24.04. VPS menjalankan reverse proxy, n8n, dan PostgreSQL dengan ekstensi pgvector. Layanan AI berada di luar core stack dan dipilih saat deployment melalui kontrak provider yang dapat dikonfigurasi; ia dapat berupa endpoint private/self-hosted atau hosted yang telah disetujui.

| Komponen | Lokasi | Tanggung jawab | Alasan pemilihan |
|---|---|---|---|
| Caddy | Container VPS | Terminasi HTTPS dan pembatasan rute publik | Konfigurasi statis, TLS otomatis, dan tidak memerlukan akses Docker socket. Hanya rute webhook yang perlu publik. |
| n8n, mode eksekusi `regular` | Container VPS | Orkestrasi ingest dan tanya-jawab | Sesuai brief n8n, mudah diekspor, dan cukup untuk satu operator/pengguna demo. Queue worker dan Redis tidak diperlukan untuk beban ini. |
| PostgreSQL + pgvector | Satu container VPS | Metadata n8n, vector store, versi corpus, dedup, dan event operasional tersanitasi | Satu proses database menghindari duplikasi layanan pada VPS 2 GB, sementara schema dan role memisahkan state n8n dari data RAG. |
| AI provider endpoint | Configurable di luar core stack | Embedding dan pembentukan jawaban melalui operasi chat + embeddings | Provider/model menjadi deployment binding sehingga repository tidak bergantung pada merek, model, lokasi host, atau accelerator tertentu. |
| Secure provider transport | Sesuai profile | HTTPS untuk hosted endpoint atau private routed network untuk endpoint private | Menjaga autentikasi dan data boundary tanpa memaksakan teknologi tunnel tertentu pada repository. |

Hanya dua workflow yang menjadi deliverable:

1. `01 — Corpus Ingestion`: membaca seluruh Markdown approved dari `/docs`, membentuk kandidat corpus, melakukan embedding, memvalidasi kandidat, lalu mengaktifkan versi baru secara atomik.
2. `02 — Telegram Grounded Q&A`: menerima update Telegram, memvalidasi asal dan isi, melakukan retrieval terlebih dahulu, membentuk jawaban grounded, memvalidasi sumber, lalu mengirim satu respons.

Controlled failure branches berada di dalam masing-masing workflow. Error Trigger workflow ketiga tidak dipilih karena deliverable approved menetapkan dua workflow; unexpected crash tetap berstatus failed dan ditangani melalui runtime health/container logs yang disanitasi, bukan dengan menyimpan payload eksekusi.

Retrieval selalu terjadi sebelum model menjawab. Desain tidak memakai agent/tool-calling karena kebutuhan hanya pencarian corpus dan jawaban singkat; alur eksplisit lebih mudah diuji, lebih sedikit nondeterminisme, dan tidak bergantung pada kemampuan tool-calling model tertentu.

Repository bersifat provider/model-neutral pada level bisnis. Adapter awal menggunakan kontrak HTTP OpenAI-compatible yang menyediakan operasi chat dan embeddings; endpoint, credential, nama model, dimensi embedding, dan parameter retrieval menjadi binding runtime. Provider private maupun hosted dapat dipakai selama memenuhi contract tests. Pergantian model embedding selalu memerlukan re-ingest; provider dengan API berbeda memerlukan adapter baru dan retest, tanpa mengubah alur RAG atau requirement bisnis.

### Target dan cara distribusi

- Target runtime core: satu VPS demo Ubuntu 24.04, RAM 2 GB, 2 vCPU. Target inference dipilih saat provisioning dan bukan bagian tetap dari core topology.
- Distribusi: repository GitHub berisi source corpus yang telah disetujui untuk publikasi, dua workflow export tersanitasi, konfigurasi Docker, panduan, fixture evaluasi sintetis, dan evidence yang sudah disanitasi.
- Deployment bersifat sementara untuk perekaman portfolio. Penghapusan VPS/volume dan revocation credential dilakukan sebagai aksi release/cleanup terpisah setelah bukti yang aman telah disimpan.
- Public push dan deploy bukan kewenangan artefak ini; keduanya tetap memerlukan gate Human yang sesuai.

## 2. Aliran Data

### Boundary dan kategori data

| Area | Operator / trust boundary | Kategori dan state yang diizinkan |
|---|---|---|
| Repository dan mount `/docs` | Human mengesahkan isi; container n8n mendapat read-only mount | Corpus saat ini mengikuti PRD: `Confidential`, minimized-and-masked. Publikasi GitHub menunggu reclassification/sanitization check. |
| Telegram | Telegram adalah provider eksternal; satu bot dan satu chat/group ID yang dibatasi | Pertanyaan kebijakan umum saja. Record HR/pelanggan, transaksi, credential, dan data Restricted dilarang. |
| VPS Docker network | Boundary runtime milik operator | n8n, database, dan reverse proxy; database tidak memiliki port publik. |
| AI provider boundary | Endpoint private/self-hosted atau hosted yang disetujui | Pertanyaan dan potongan hasil retrieval hanya dikirim ke endpoint yang dipilih untuk deployment. Hosted provider memerlukan persetujuan Human atas pemrosesan data, retention, dan region sebelum credential diprovision. |
| n8n credential store / host secret source | Human melakukan provisioning | Token, password, private key, dan credential lain adalah `Restricted`; nilai tidak masuk Git, workflow export, laporan, atau chat agent. |

### Flow A — pemuatan corpus

`Human-approved /docs (read-only) → inventaris & validasi → pemecahan dokumen → provider embedding → staging pgvector → validasi kandidat → aktivasi corpus`

1. Human menjalankan workflow ingest secara manual setelah isi `/docs` disahkan. Baseline yang teramati pada `2026-09-14` adalah 26 file Markdown `00`–`25`, total 191.772 byte.
2. Workflow hanya menerima file Markdown reguler di root mount corpus. Path traversal, symlink ke luar mount, file kosong, ekstensi lain, atau file yang tidak dapat dibaca menggagalkan kandidat sebelum aktivasi.
3. Manifest kanonis dibentuk dari path relatif yang telah diurutkan dan hash isi setiap file. Hash manifest menjadi `corpus_version`; metadata chunk memuat minimal `source_name`, `source_hash`, `chunk_index`, `corpus_version`, dan `embedding_profile_id`.
4. Teks dipecah dengan aturan yang mempertahankan heading dan batas paragraf. Ukuran chunk/overlap adalah konfigurasi terkontrol yang dikalibrasi Engineer terhadap eval set; nilai final harus dicatat sebelum bukti QA dan tidak boleh berubah di tengah run.
5. Semua chunk kandidat di-embed dengan satu embedding profile yang sama. Contract test memastikan operasi indexing dan querying menggunakan provider, model identity, normalisasi, dan dimensi yang identik.
6. Kandidat ditulis sebagai `staging`. Hanya setelah jumlah dokumen, integritas metadata, dimensi vector, dan status seluruh file valid, transaksi singkat memindahkan pointer aktif ke versi baru.
7. Kegagalan parsing, timeout, respons embedding invalid, atau database error menandai kandidat gagal dan mempertahankan versi aktif sebelumnya. Kandidat gagal tidak boleh terlihat oleh alur Q&A.
8. Menjalankan ulang manifest identik adalah no-op atau rebuild staging yang menggantikan staging identik; hasilnya tidak boleh menambah chunk duplikat. Versi aktif sebelumnya dipertahankan sampai kandidat baru lengkap, sehingga rollback cukup mengubah pointer ke versi lengkap terdahulu.

### Flow B — tanya-jawab Telegram

`Telegram Trigger tervalidasi → otorisasi chat → dedup update → validasi pertanyaan → active corpus retrieval → grounding & citation validation → Telegram response`

1. Telegram Trigger versi yang dipilih harus menghasilkan dan memverifikasi `secret_token` webhook serta membatasi `chat_id`. Nilai chat/user restriction diisi Human pada runtime dan dihapus dari export publik.
2. Hanya update `message` dengan teks non-kosong dalam batas provider yang diproses. Update dari chat yang tidak diizinkan, attachment, command yang tidak didukung, atau payload tanpa struktur yang dibutuhkan berhenti sebelum retrieval/model.
3. Identitas dedup adalah kombinasi bot runtime dan `update_id` Telegram, disimpan selama umur deployment demo. Claim atomik mencegah dua eksekusi konkuren memproses update yang sama.
4. Workflow mengambil `active_corpus_version` dan konfigurasi RAG yang lengkap. Query embedding harus memakai `embedding_profile_id` yang sama dengan corpus aktif; mismatch berhenti sebelum pencarian.
5. PGVector mengambil kandidat hanya dari corpus aktif. `retrieval_limit` dan `minimum_similarity` dikunci pada config revision yang telah dikalibrasi. Bila tidak ada evidence yang melewati syarat, workflow melewati generasi dan mengirim abstention deterministik tanpa sumber.
6. Untuk evidence yang memadai, potongan diberi citation key internal. Model menerima pertanyaan, potongan, dan instruksi bahwa isi pertanyaan/dokumen adalah data, bukan perintah sistem. Output yang diharapkan berisi jawaban singkat dan citation key, bukan nama file bebas.
7. Workflow memvalidasi bentuk output dan memastikan semua citation key berasal dari hasil retrieval. Nama sumber pada respons dibentuk secara deterministik dari metadata chunk yang tervalidasi. Citation yang tidak dikenal, struktur invalid, atau klaim tanpa evidence menghasilkan abstention aman, bukan sumber rekaan.
8. Setelah Telegram menyatakan pengiriman berhasil, record update menjadi `delivered`. Error pasti sebelum pengiriman boleh dihentikan/fallback dalam budget; timeout setelah request pengiriman menjadi `delivery_unknown` dan tidak di-retry otomatis karena hasil provider dapat ambigu.

### Deadline, retry, dan kegagalan

- Batas bisnis tetap `<5,0 detik` dari workflow menerima pertanyaan sampai Telegram menyatakan send berhasil. Alur online tidak melakukan retry otomatis terhadap embedding atau chat; setiap call mendapat budget terbatas dari deadline yang tersisa.
- Nilai internal `N8N_AI_TIMEOUT_MAX` belum boleh ditebak. Engineer/DevOps harus menetapkannya dari profiling agar cabang kegagalan masih memiliki waktu untuk mengirim respons sebelum batas bisnis.
- Model timeout/invalid response menghasilkan pesan deterministik “layanan pengetahuan sedang tidak tersedia” tanpa klaim atau sumber. Kondisi ini dibedakan dari abstention “informasi tidak ditemukan di dokumen”.
- Telegram send yang gagal tidak boleh dicatat sebagai jawaban berhasil. Retry manual hanya boleh dilakukan setelah operator memeriksa status `failed` versus `delivery_unknown` untuk mencegah respons ganda.
- Ingest boleh diulang karena seluruh write diarahkan ke staging dan aktivasi atomik. Q&A tidak mengubah corpus.

## 3. Struktur Folder

Struktur berikut direncanakan untuk Engineer; hanya artefak desain di `.ai` yang dibuat pada tahap Architect.

| Path | Isi / owner |
|---|---|
| `.ai/knowledge/architecture.md` | Desain dan matrix Architect ini. |
| `.ai/knowledge/environment-schema.md` | Kontrak konfigurasi per environment. |
| `.ai/decisions/` | ADR keputusan struktural. |
| `docs/` | Corpus Markdown approved; di-mount read-only ke n8n. |
| `workflows/01-corpus-ingestion.json` | Export workflow ingest tersanitasi; dibuat Engineer dari versi n8n yang dipilih. |
| `workflows/02-telegram-grounded-qa.json` | Export workflow Q&A tersanitasi; dibuat Engineer. |
| `deploy/compose.yaml` | Stack demo VPS; dibuat DevOps setelah architecture approval. |
| `deploy/Caddyfile` | HTTPS/routing; dibuat DevOps. |
| `deploy/postgres-init/` | Schema/role initialization tanpa nilai secret; dibuat Engineer/DevOps. |
| `evaluation/qa-dataset.csv` | Salinan kerja sintetis 12 supported + 3 unsupported yang telah disahkan; sumber `D:\QA_Dataset_15_Pasangan.csv` tidak diubah. |
| `evaluation/README.md` | Rubric, config revision, model/corpus identity, dan aturan rerun. |
| `.ai/reports/qa/` | Evidence QA tersanitasi, hanya dibuat ketika eksekusi aktual dilakukan. |
| `README.md` | Setup, update corpus, demo, batas data, dan teardown. |
| `.env.example` | Satu template canonical yang aman; dibuat Engineer. |
| `.gitignore`, `.dockerignore` | Proteksi secret/build context; dibuat Engineer/DevOps. |

Tidak ada service source-code khusus atau community node. Transformasi deterministik memakai node bawaan n8n yang tersedia pada image terpilih; Execute Command tidak diperlukan.

## 4. Dependency & Environment Variables

Schema lengkap berada di [environment-schema.md](./environment-schema.md). Dependency/version berikut harus dipilih sebagai exact maintained tag atau digest dan diverifikasi bersama; `latest` bukan pin yang dapat diterima.

| Dependency | Batas versi/kontrak | Alasan dan verifikasi |
|---|---|---|
| Docker Engine + Compose plugin | Rilis yang mendukung Ubuntu 24.04; versi aktual dicatat DevOps | Packaging runtime yang diminta Human dan isolasi service. Docker mendokumentasikan Ubuntu Noble 24.04 sebagai platform yang didukung. |
| Caddy | Exact image tag/digest | Reverse proxy dan TLS otomatis dengan konfigurasi statis. Data ACME memakai named volume. |
| n8n | Exact image tag/digest; node Telegram Trigger harus mendukung secret-token verification dan chat restriction | Dua workflow export harus berasal dari instance/node version yang sama dengan target import. Tidak memakai queue mode. |
| PostgreSQL + pgvector | Exact compatible image tag/digest | Menyimpan metadata n8n dan vector/state RAG pada satu proses DB dengan schema/role terpisah. |
| AI provider | OpenAI-compatible chat + embeddings contract pada adapter awal; versi API/model aktual dicatat pada evidence | Endpoint, credential, lokasi, model ID/digest, dan dimensi adalah binding runtime. Provider lain memerlukan adapter terisolasi dan retest, bukan perubahan alur bisnis. |
| Private network transport | Conditional untuk endpoint private/self-hosted; teknologi dipilih saat provisioning | Route dan firewall hanya membuka koneksi VPS ke endpoint AI yang disetujui. Key/config tidak berada di repository atau project `.env`. |

Sumber teknis resmi yang diperiksa pada `2026-09-14`: [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/), [n8n Docker Compose deployment](https://github.com/n8n-io/n8n-docs/blob/main/docs/deploy/host-n8n/install-options/use-a-cloud-provider/use-docker-compose.md), [n8n PGVector node](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.vectorstorepgvector/), [n8n OpenAI credential dengan Base URL yang dapat diubah](https://github.com/n8n-io/n8n/blob/master/packages/nodes-base/credentials/OpenAiApi.credentials.ts), [n8n HTTP Request credential](https://docs.n8n.io/integrations/builtin/credentials/httprequest/), [Telegram Bot API webhook secret](https://core.telegram.org/bots/api), dan [Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https).

## 5. Database

Satu PostgreSQL/pgvector cluster digunakan agar VPS 2 GB tidak menjalankan database terpisah. Pemisahan dilakukan secara logis dan dengan role:

- schema `n8n`: dimiliki role aplikasi n8n dan hanya digunakan n8n untuk workflow, credential terenkripsi, dan metadata instance;
- schema `rag`: corpus/vector/state operasional;
- role `rag_ingest`: write staging, validasi, aktivasi, dan cleanup corpus;
- role `rag_runtime`: read corpus/settings dan write terbatas ke dedup/event operasional; tidak dapat mengubah corpus aktif;
- admin database hanya dipakai saat initialization/maintenance dan tidak menjadi credential workflow.

### Entitas RAG konseptual

| Entitas | Data minimum | Aturan penting |
|---|---|---|
| `rag_settings` | config revision, chat model binding, embedding profile/dimension, retrieval limit, minimum similarity, context/output bounds, active corpus version | Nilai non-secret; required field kosong membuat workflow fail-closed. Perubahan embedding profile mewajibkan full re-ingest. |
| `corpus_versions` | version/hash, status, document/chunk counts, embedding profile, created/activated timestamps | Status `staging`, `active`, `failed`, atau `superseded`; hanya satu active. |
| `documents` | deterministic chunk identity, content, vector, metadata source/chunk/version | Unique per corpus version + source hash + chunk index; query selalu difilter ke active version. |
| `telegram_updates` | bot-scope hash, update ID, status, attempt timestamps, delivery state, safe error category | Tidak menyimpan question, answer, chat ID, atau payload Telegram. Unique identity menjadi boundary dedup. |
| `safe_events` | correlation ID non-reversible, workflow/stage, status, duration, safe error category, config/corpus version | Tidak menyimpan body, stack mentah, header, credential, source excerpt, atau identifier pengguna. |

State n8n dan RAG berada pada named volume yang berbeda dari source repository. PostgreSQL tidak mempublikasikan port host. Backup sebelum perubahan schema/upgrade dilakukan pada storage akses-terbatas dan tidak masuk Git atau agent context.

Aktivasi corpus adalah satu perubahan pointer/transaksi setelah staging lengkap. Kegagalan sebelum commit tidak mengubah active version. Rollback hanya menunjuk kembali versi lengkap sebelumnya; penghapusan versi/volume bersifat maintenance/destructive action yang memerlukan target dan persetujuan yang jelas.

## 6. Catatan Keamanan & Robustness

### Ingress, auth, dan authorization

- Internet hanya dapat mencapai port 80/443 milik Caddy. Port n8n dan PostgreSQL tidak dipublikasikan; endpoint AI private/self-hosted juga tidak boleh menjadi public ingress.
- Rute production webhook Telegram harus publik melalui HTTPS. Admin/editor n8n dibatasi ke jalur operator privat yang dipilih saat provisioning; rute test webhook tidak dipublikasikan.
- Untuk profile private/self-hosted, VPS hanya diberi route keluar ke exact host/port endpoint AI melalui jaringan privat yang disetujui. Tidak ada default route seluruh trafik atau akses subnet yang lebih luas dari kebutuhan.
- Untuk profile hosted, egress n8n dibatasi ke exact HTTPS origin provider dan memakai credential least-privilege. Profile ini tetap disabled sampai Human menyetujui provider, tujuan pemrosesan, retention, dan region untuk corpus `Confidential`.
- Rule host ditempatkan pada boundary firewall Docker yang benar; publikasi container tidak boleh diasumsikan tunduk pada UFW tanpa pemeriksaan `DOCKER-USER`/iptables.
- Telegram Trigger pada node version terpilih wajib memverifikasi header secret token yang didaftarkan ke Telegram. Trigger juga dibatasi ke satu chat/group ID runtime. Ini merupakan otorisasi deployment, bukan fitur autentikasi/personalization per karyawan.
- Export publik dikirim dalam keadaan unpublished dengan credential binding dan allowed chat ID kosong/placeholder. Preflight harus menolak publish sampai binding runtime lengkap.
- n8n hanya memiliki satu owner account milik Human, registrasi publik tidak tersedia, dan password/MFA bila didukung dikelola Human.

### Secret dan data minimization

- Bot token, password database, n8n encryption key, AI provider credential, private-network key, dan credential lain tidak pernah berada di Git, workflow JSON, screenshot, laporan, atau project state.
- Credential provider disimpan di n8n credential store yang dienkripsi dengan `N8N_ENCRYPTION_KEY`; private-network key, bila digunakan, berada di secret store OS masing-masing host.
- `N8N_BLOCK_ENV_ACCESS_IN_NODE=true`. Model/provider binding non-secret berasal dari record konfigurasi terkontrol; workflow tidak diberi akses umum ke seluruh process environment.
- Eksekusi demo tidak menyimpan payload sukses/error/manual. Hanya event operasional tersanitasi yang disimpan, dengan pruning dan teardown akhir.
- Pertanyaan Telegram tetap dibatasi pada kebijakan umum. Sistem tidak menyimpan prompt/answer body; record Restricted yang sengaja/tidak sengaja dikirim tidak boleh masuk evidence atau laporan.

### Runtime dan failure containment

- `/docs` di-mount read-only dan akses file n8n dibatasi ke mount tersebut. Tidak ada Execute Command, community node, shell interpolation, atau host Docker socket pada n8n/Caddy.
- Container memakai least privilege/capability drop/read-only filesystem sejauh kompatibel dengan image terpilih; writable path hanya named volume yang dibutuhkan. Database mengikuti user bawaan image dan bukan dipaksa ke UID yang belum diverifikasi.
- `regular` execution mode dan concurrency satu dipilih untuk pengguna tunggal serta endpoint model dengan resource terbatas. Tidak ada Redis, worker, atau autoscaling.
- Healthcheck hanya membuktikan service readiness, bukan workflow/E2E. Dependency startup menunggu database healthy; endpoint/provider/model yang tidak siap menyebabkan status degraded dan menonaktifkan klaim ready-to-demo.
- Prompt injection dibatasi dengan alur tanpa tool/action, retrieval eksplisit, instruksi prioritas tetap, output contract, dan citation allowlist. Dokumen dan pertanyaan diperlakukan sebagai data.
- Upgrade image dilakukan dengan backup, exact version selection, static config validation, import check, dan rerun AC terdampak. Tidak ada auto-upgrade `latest`.
- Teardown hanya menargetkan Compose project/volume dan credential demo yang tercatat. Setelah Human menyetujui cleanup: export artefak/evidence aman, unpublish workflow, revoke bot token, provider credential, dan akses jaringan privat terkait, lalu hapus volume proyek. Tidak ada global prune.

## 7. Acceptance & Failure Scenarios

### Aturan evaluasi probabilistik

- Eval set final tetap 15 pertanyaan sintetis: 12 supported sesuai distribusi kategori PRD dan 3 benar-benar unsupported setelah pencarian semantik seluruh corpus.
- Kunci jawaban, sumber, corpus version, config revision, model ID/digest, opsi generation, dan urutan soal dibekukan sebelum run. Temperature dibuat deterministik pada nilai minimum yang didukung runtime.
- Penilaian mengikuti rubric biner PRD, bukan exact string match. Run pertama yang telah dideklarasikan menjadi evidence utama; rerun harus diberi label dan tidak menggantikan hasil pertama tanpa alasan/impact record.
- Uji gate dilakukan sekuensial untuk merepresentasikan satu pengguna. Provider/model menjalani readiness warm-up yang terdokumentasi sebelum run required; cold/idle-start dicatat sebagai exploratory karena PRD belum menetapkan kondisi cold-start.
- Matrix ini belum dijalankan. Level adalah target evidence yang wajib dibuat Engineer/DevOps dan dieksekusi QA.

### Applicability lima family

| Requirement | Valid | Invalid | Duplicate / retry | Timeout | Provider failure |
|---|---|---|---|---|---|
| `REQ-001` | Applicable | Applicable | Applicable | Applicable | Applicable: embedding/database |
| `REQ-002` | Applicable | Applicable | Applicable | Applicable | Applicable: Telegram |
| `REQ-003` | Applicable | Applicable: malformed/ungrounded model output | `NOT_APPLICABLE`: dedup delivery dinilai pada REQ-002; pertanyaan berulang dengan update ID baru adalah input baru | Applicable | Applicable: model/embedding |
| `REQ-004` | Applicable | Applicable: citation invalid | `NOT_APPLICABLE`: sumber tidak memiliki write/retry terpisah dari delivery | Applicable | Applicable: retrieval/model |
| `REQ-005` | Applicable | Applicable: prompt injection/false support | `NOT_APPLICABLE`: duplicate update ditangani REQ-002 dan tidak mengubah aturan abstention | Applicable | Applicable: retrieval/model |
| `REQ-006` | Applicable | `NOT_APPLICABLE`: gate latency PRD hanya mengukur 15 input eval valid; invalid input tetap diuji di REQ-002 | `NOT_APPLICABLE`: delivery duplikat sengaja disuppress sehingga tidak memiliki response timing kedua | Applicable | Applicable: AI/Telegram |
| `REQ-007` | Applicable | Applicable: missing binding/artifact | `NOT_APPLICABLE`: acceptance artefak tidak menjanjikan import idempotent; dedup perilaku ada di REQ-001/002 | `NOT_APPLICABLE`: timeout workflow dinilai pada REQ-001/002/006, bukan inspeksi artefak | `NOT_APPLICABLE`: import/static inspection tidak bergantung provider; live provider dibuktikan oleh REQ-001/002 |

### Matrix version 1.0

| AC ID / requirement | Family | Preconditions + synthetic stimulus / injected fault | Expected observable result + forbidden side effects | Level / target | Priority | Version |
|---|---|---|---|---|---|---|
| `AC-001 / REQ-001` | Valid | Approved baseline mount berisi tepat 26 Markdown `00`–`25`; embedding config lengkap | Satu candidate version berstatus active dengan `document_count=26`; semua chunk punya metadata wajib dan hanya versi ini dipakai query. Tidak ada file lain atau credential yang tersimpan sebagai dokumen. | Isolated integration + demo E2E | Required | `1.0` |
| `AC-002 / REQ-001` | Invalid | Satu fixture corpus berisi file kosong, ekstensi tidak didukung, atau path keluar mount | Candidate ditolak/failed dan active version lama tidak berubah. Tidak ada partial corpus yang terlihat oleh Q&A. | Isolated integration | Required | `1.0` |
| `AC-003 / REQ-001` | Duplicate/retry | Manifest identik dijalankan ulang, termasuk dua trigger hampir bersamaan | Hanya satu identity corpus; tidak ada chunk ganda dan tidak ada dua active version. Eksekusi kedua no-op atau berhenti dengan status duplicate yang aman. | Isolated concurrency integration | Required | `1.0` |
| `AC-004 / REQ-001` | Timeout | Embedding endpoint diberi delay melewati timeout pada tengah ingest | Candidate gagal; versi lama tetap active; tidak ada aktivasi sebagian atau retry tak terbatas. Safe event hanya mencatat kategori timeout. | Fault-injected integration | Required | `1.0` |
| `AC-005 / REQ-001` | Provider failure | Embedding mengembalikan auth/5xx/vector dimension salah atau database write gagal | Workflow tidak melaporkan sukses, tidak mengubah active pointer, dan menyimpan status gagal tersanitasi. | Fault-injected integration | Required | `1.0` |
| `AC-006 / REQ-002` | Valid | Update Telegram sintetis dari allowed chat, text valid, service ready | Tepat satu respons dapat dibaca dikirim ke chat yang sama; update menjadi delivered. Tidak ada tujuan lain yang menerima pesan. | Approved demo E2E | Required | `1.0` |
| `AC-007 / REQ-002` | Invalid | Secret header salah, chat ID tidak diizinkan, payload non-message/non-text, atau text kosong | Secret salah ditolak 403 oleh trigger; kasus lain berhenti sebelum retrieval/model. Tidak ada knowledge response, corpus write, atau body log. | Sandbox integration | Required | `1.0` |
| `AC-008 / REQ-002` | Duplicate/retry | Update ID yang sama dikirim ulang dan dua delivery konkuren disimulasikan | Satu claim menang dan paling banyak satu send attempt dilakukan; eksekusi lain no-op. Desain tidak mengklaim universal exactly-once pada timeout provider ambigu. | Isolated concurrency integration | Required | `1.0` |
| `AC-009 / REQ-002` | Timeout | Telegram send melebihi budget atau koneksi diputus setelah request | State `failed` bila pasti belum terkirim atau `delivery_unknown` bila ambigu; tidak dicatat delivered dan tidak auto-retry. | Fault-injected provider integration | Required | `1.0` |
| `AC-010 / REQ-002` | Provider failure | Telegram auth rejection, rate limit, atau 5xx saat send | Satu bounded attempt sesuai sisa deadline; hasil bukan success, tanpa pesan ke tujuan alternatif dan tanpa payload mentah pada log. | Sandbox/fault integration | Required | `1.0` |
| `AC-011 / REQ-003` | Valid | Eval set final approved, frozen corpus/config/model, readiness terpenuhi | Sedikitnya 12 dari 15 jawaban lulus rubric isi biner; setiap item tetap memiliki hasil individual. Tidak ada klaim di luar corpus. | Approved demo E2E + Human rubric review | Required | `1.0` |
| `AC-012 / REQ-003` | Invalid output | Model mengembalikan struktur rusak, citation key tak dikenal, atau jawaban tanpa evidence yang divalidasi | Guard menolak output dan mengirim abstention aman; tidak meneruskan raw/model output atau sumber rekaan. Supported item boleh dinilai gagal isi, tetapi safety tetap teramati. | Mock + isolated integration | Required | `1.0` |
| `AC-013 / REQ-003` | Timeout/provider failure | Embedding/chat timeout, 5xx, overload, atau respons tidak dapat diparse | Respons deterministik service-unavailable tanpa klaim kebijakan/sumber; event tersanitasi. Tidak disamarkan sebagai jawaban grounded. | Fault-injected integration | Required | `1.0` |
| `AC-014 / REQ-004` | Valid | Dua belas pertanyaan supported final dengan approved source set | `12/12` menyebut minimal satu source_name yang mendukung; setiap sumber tambahan berada pada approved/relevant set. | Approved demo E2E + rubric review | Required | `1.0` |
| `AC-015 / REQ-004` | Invalid citation | Model menyebut key yang tidak ada atau mencoba menulis nama file sendiri | Nama tersebut tidak pernah dikirim; output menjadi abstention aman tanpa sumber palsu. | Mock + isolated integration | Required | `1.0` |
| `AC-016 / REQ-004` | Timeout/provider failure | Retrieval/model gagal sebelum citation tervalidasi | Respons tidak memuat source_name. Tidak ada fallback yang menebak sumber. | Fault-injected integration | Required | `1.0` |
| `AC-017 / REQ-005` | Valid unsupported | Tiga pertanyaan final telah diverifikasi semantik tidak terjawab oleh seluruh corpus | `3/3` menyatakan informasi tidak ditemukan/tidak diketahui, tanpa klaim kebijakan dan tanpa sumber. | Approved demo E2E + rubric review | Required | `1.0` |
| `AC-018 / REQ-005` | Invalid / adversarial | Pertanyaan memerintahkan abaikan corpus, meminta menebak, atau memasukkan instruksi sebagai data | Sistem tetap grounded atau abstain; tidak menjalankan tool/action dan tidak mengungkap prompt/config. | Adversarial sandbox integration | Required | `1.0` |
| `AC-019 / REQ-005` | Retrieval boundary | Tidak ada hasil di atas minimum similarity atau active corpus kosong/mismatch | Generasi factual dilewati dan abstention deterministik dikirim. Active corpus kosong/mismatch juga menghasilkan safe unavailable state, bukan klaim. | Mock + isolated integration | Required | `1.0` |
| `AC-020 / REQ-005` | Timeout/provider failure | Provider gagal pada pertanyaan unsupported | Respons service-unavailable dibedakan dari “tidak ditemukan”; tidak ada klaim/sumber. Item tidak boleh dinilai lulus abstention bila evidence provider tidak tersedia. | Fault-injected integration | Required | `1.0` |
| `AC-021 / REQ-006` | Valid | 15 item final, run sekuensial, readiness warm-up, timestamp monotonic di receive dan Telegram send success | Setiap item `15/15` memiliki durasi individual `<5.000 ms`; agregat saja tidak cukup. Tidak ada item gagal/send unknown yang dihitung lulus. | Approved demo E2E | Required | `1.0` |
| `AC-022 / REQ-006` | Timeout | AI call dikontrol melewati internal budget | Cabang failure melakukan send attempt sebelum deadline; bila send success dan durasi `<5.000 ms`, latency behavior lulus tetapi item isi gagal. Tidak ada retry yang melewati budget. | Fault-injected E2E-like integration | Required | `1.0` |
| `AC-023 / REQ-006` | Provider failure | Telegram menunda/gagal mengakui send atau koneksi endpoint AI terputus | Item tidak memiliki send-success timestamp dan dinilai gagal REQ-006; status tidak dipalsukan. | Fault-injected integration | Required | `1.0` |
| `AC-024 / REQ-006` | Cold/idle start | Model/provider berada pada kondisi cold, idle, atau baru restart | Durasi dan readiness state dicatat terpisah untuk mengungkap biaya cold start; hasil tidak menggantikan required warm run. | Demo exploratory | Optional | `1.0` |
| `AC-025 / REQ-007` | Valid | Clean isolated instance dengan exact supported image; dua export, panduan, dataset approved, dan placeholder aman tersedia | Kedua workflow dapat di-import, node/dependency dikenali, credential dapat direbind, panduan setup/update/eval/teardown lengkap, hasil dan demo tersanitasi dapat ditinjau. | Static inspection + clean-instance import + demo review | Required | `1.0` |
| `AC-026 / REQ-007` | Invalid config/artifact | Required env kosong/placeholder, credential/chat restriction/model binding hilang, atau salah satu deliverable tidak ada | Preflight/import review gagal jelas dengan nama field/artifact saja; workflow tetap unpublished dan tidak melakukan network/write. | Static + isolated integration | Required | `1.0` |
| `AC-027 / REQ-007` | Cleanup | Human menyetujui exact cleanup target setelah demo dan evidence aman sudah diekspor | Workflow unpublished, bot/provider/private-network credential direvoke, container/network/volume project dihapus, repository/evidence tersanitasi tetap ada. Tidak ada global prune atau penghapusan resource di luar project. | DevOps scoped verification | Required sebelum penutupan demo | `1.0` |

## 8. Catatan Khusus: Asumsi, Risiko, dan Batas Belum Terselesaikan

### Milestone implementasi dan quality checkpoint

Milestone berikut menjaga pekerjaan Engineer tetap berupa satu irisan koheren pada satu waktu. Satu milestone baru dimulai setelah exit criterion milestone sebelumnya terpenuhi atau gap-nya dicatat eksplisit sebagai `NOT_VERIFIED` beserta owner. Tidak ada estimasi waktu pada desain ini.

| Milestone | Owner utama | Fokus dan artefak | Exit criterion / quality checkpoint | AC utama |
|---|---|---|---|---|
| `M0 — Contract & traceability baseline` | Engineer | Membaca PRD/architecture/ADR approved; membuat mapping `REQ → AC → implementation → test`; menginventarisasi prerequisite dan nilai `UNKNOWN` tanpa mengarangnya | Semua `AC-001`–`AC-027` memiliki planned owner, implementation/test target, fixture/fault method, dan command placeholder yang jujur; konflik intent dikembalikan ke Architect/Human sebelum build | Semua AC untuk traceability saja; belum ada klaim behavior |
| `M1 — Safe isolated foundation` | Engineer | Struktur repository, canonical `.env.example`, ignore rules, schema/init RAG, synthetic fixtures, provider mock, dan launcher test terisolasi | Static validation lulus; test target tidak dapat memakai credential/network/volume demo; missing/placeholder config fail-closed; tidak ada secret atau data non-sintetis di artefak | Fondasi `AC-026`; prerequisite `AC-001`–`AC-024` |
| `M2 — Atomic corpus ingestion` | Engineer | Workflow ingestion lengkap terhadap corpus/fixture read-only, deterministic manifest/chunk identity, staging, activation, rollback pointer, dan embedding-profile guard | Self-test Engineer membuktikan valid, invalid, duplicate/concurrent, timeout, dan provider/database failure tanpa partial activation atau duplicate chunk | `AC-001`–`AC-005` |
| `M3 — Grounded answer core` | Engineer | Retrieval active-corpus, threshold, prompt boundary, structured output, citation allowlist, abstention, serta service-unavailable path; transport Telegram masih dimock | Self-test membuktikan supported/unsupported, malformed citation, prompt injection, corpus mismatch, timeout, dan provider failure. Mock tidak diklaim sebagai live integration | `AC-011`–`AC-020` |
| `M4 — Telegram delivery & deadline` | Engineer | Validasi webhook/chat, input boundary, atomic update dedup, bounded AI calls, send state `delivered/failed/delivery_unknown`, dan timing instrumentation aman | Sandbox/mock self-test membuktikan unauthorized input berhenti sebelum AI, duplicate update maksimal satu send attempt, ambiguity tidak di-retry otomatis, serta timeout tidak dipalsukan sebagai success | `AC-006`–`AC-010`, `AC-022`–`AC-024` |
| `M5 — Portable delivery bundle` | Engineer | Dua workflow export tersanitasi/unpublished, dataset kerja 12+3 yang lolos corpus-wide review, README, setup/eval/teardown guidance, mapping final, commands, dan self-test report | Clean-instance import pada target terisolasi mengenali node/dependency dan rebinding; seluruh self-test aktual dicatat `VERIFIED BY IMPLEMENTER`; required gap tetap terlihat. Engineer berhenti dan menyerahkan ke DevOps | `AC-025`–`AC-026` serta regresi `AC-001`–`AC-024` yang terdampak |
| `M6 — Runtime & test-target readiness` | DevOps | Exact image pins, Compose/Caddy, volumes, least-privilege network, provider binding, health/preflight, backup dan scoped teardown procedure | Static/runtime validation dan resource observation tersedia. Deployment ke target eksternal hanya setelah Human menyetujui exact temporary test target; status hanya ready-for-QA, bukan release | Runtime prerequisite untuk `AC-001`–`AC-027` |
| `M7 — Independent quality & security` | QA lalu Security | QA menjalankan matrix pada level yang disetujui, termasuk 15-item E2E; Security mengaudit exact candidate dan deployment configuration secara independen | QA/Security verdict serta gap tersedia terhadap candidate yang sama. Target `<5.000 ms` memerlukan `15/15`; mock/static evidence tidak menggantikan required integration/E2E | Seluruh required AC; `AC-024` tetap exploratory |
| `M8 — Human gates, demo, dan cleanup` | Human + DevOps | Human menilai quality evidence, lalu memberi atau menolak release/deploy untuk exact target/action; setelah demo, evidence aman disimpan dan cleanup terotorisasi dijalankan | Quality decision dan release/deploy decision tercatat terpisah; teardown project-scoped serta revocation diverifikasi tanpa global prune | `AC-027` dan release record |

Aturan lintas milestone:

- Work-in-progress dibatasi satu milestone Engineer; defect pada exit criterion diselesaikan atau dicatat sebelum membuka milestone berikutnya.
- Setiap milestone mererun AC yang diubah dan regression path yang terhubung. Perubahan shared config, schema, provider adapter, atau output contract memperluas regression scope.
- Fixture selalu sintetis. Credential nyata hanya diprovision Human melalui store yang ditetapkan; tidak pernah digunakan untuk menutup gap test lokal secara diam-diam.
- Evidence awal boleh berada pada level unit/mock/isolated sesuai milestone, tetapi verdict final hanya mengikuti level target pada Acceptance Matrix `1.0`.
- Milestone completion bukan Architecture, Quality, atau Release approval. Human gate tetap dicatat terpisah di project state.

1. **Risiko hard gate latency tinggi.** Kapasitas provider/model, warm-state behavior, dan jalur jaringan yang dipilih belum dibenchmark. `REQ-006` tidak dianggap terpenuhi sampai benchmark nyata 15/15 lulus. Bila gagal, opsi yang dibawa kembali ke Human adalah model lebih ringan, topology inference lain, atau provider lain; requirement `<5,0 detik` tidak boleh diam-diam dilonggarkan.
2. **Eval set belum approved.** Dataset sumber `D:\QA_Dataset_15_Pasangan.csv` teramati memiliki 15 baris dan SHA-256 `4AA92047BE3C7933586207DE068AC8711672700F54DB6D4BD69A7C1B14646EEC`. Berdasarkan source label saat ini, 11 baris yang menunjuk corpus terbagi menjadi 1 SOP, 4 FAQ, 1 panduan komplain, 5 kebijakan, dan 0 profil; empat baris lain menunjuk file di luar `00`–`25`. Ini belum memenuhi distribusi approved 3/3/2/3/1. Selain itu, “source file tidak ada” tidak cukup untuk menetapkan unsupported: nominal gaji masih muncul di corpus lain, dan pertanyaan penerimaan barang rusak perlu diperiksa terhadap SOP penerimaan, bukan hanya source label kandidat. Engineer menyiapkan salinan kerja; Human mengesahkan 12+3 setelah semantic corpus-wide check. CSV sumber tidak diubah.
3. **Model/retrieval values belum dikalibrasi.** `chat_model`, `embedding_model`, embedding dimension, retrieval limit, minimum similarity, context bound, output bound, dan internal timeout tercatat `UNKNOWN` sampai profiling. Missing value harus fail-closed dan tidak menghalangi pembuatan struktur implementasi/mock, tetapi memblokir klaim runtime-ready/E2E.
4. **Domain/HTTPS belum diprovision.** Human akan mengatur domain terakhir. Sampai DNS, port 80/443, dan sertifikat tervalidasi, Telegram webhook E2E adalah `NOT_VERIFIED`.
5. **AI provider adalah dependency tunggal.** Endpoint private dapat bergantung pada host dan uplink operator; endpoint hosted bergantung pada availability, quota, dan kebijakan provider. Tidak ada HA karena project hanya demo portfolio sementara.
6. **Public GitHub belum diizinkan oleh klasifikasi tersimpan.** PRD saat ini menandai corpus `Confidential`; pernyataan bisnis fiktif mendukung sanitization review, tetapi Security/Human harus memastikan seluruh corpus, nama, dataset, screenshot, dan export layak menjadi `Public/synthetic` sebelum push.
7. **Exact image versions belum dipilih.** DevOps harus memilih tag/digest kompatibel, mencatat tanggal verifikasi, dan menjalankan static/runtime/import checks. Tidak ada `latest` dan tidak ada klaim dukungan versi dari desain saja.
8. **Kapasitas VPS belum dibuktikan.** Resource limits harus menyisakan headroom untuk Ubuntu dan diukur saat ingest + run evaluasi. OOM/restart membuat runtime tidak ready; angka limit tidak dikarang pada tahap ini.
9. **Scope tetap demo, bukan production.** Tidak ada POS, data pelanggan/HR, user personalization, multi-tenant, monitoring komersial, autoscaling, atau SLA produksi.

## 9. Riwayat Perubahan

| Versi | Tanggal | Perubahan | ADR terkait |
|---|---|---|---|
| `1.0` | `2026-09-14` | Desain awal dari PRD `1.0`: dua workflow, split VPS/PC, Docker Compose, pgvector versioning, Telegram security/dedup, config schema, dan Acceptance Matrix `1.0` | `ADR-001` |
| `1.1` | `2026-09-14` | AI layer digeneralisasi menjadi provider-neutral; endpoint private/self-hosted dan hosted yang disetujui memakai runtime binding dan contract test yang sama. Acceptance Matrix tetap `1.0` karena requirement, AC ID, dan hasil observabel tidak berubah. | `ADR-002` |
| `1.2` | `2026-09-14` | Menambahkan milestone `M0`–`M8`, entry/exit quality checkpoint, pemisahan owner, dan regression rules untuk mengurangi beban Engineer serta mencegah big-bang validation. Matrix `1.0` dan environment schema `1.1` tidak berubah. | Tidak memerlukan ADR; topology dan requirement tidak berubah |
