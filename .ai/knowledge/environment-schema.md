# Environment Schema — Asisten Pengetahuan Internal Toko Makmur Jaya

- Schema version: `1.1`
- Tanggal: `2026-09-14`
- Status: `APPROVED`
- Architecture: `.ai/knowledge/architecture.md` version `1.2`; schema content tetap version `1.1`

Schema ini merencanakan satu template canonical `.env.example` di root project. Template dan consumer belum dibuat pada tahap Architect. Nilai actual `.env`, `.env.test`, credential n8n, token, password, private key, dan konfigurasi host tidak boleh dibaca, ditampilkan, atau disimpan dalam artefak agent.

## 1. Variabel input operator untuk `.env.example`

Nilai kosong adalah aman untuk template tetapi membuat profile terkait belum runnable. `UNKNOWN` di kolom contoh berarti keputusan teknis belum boleh ditebak; template menggunakan nilai kosong dan preflight harus berhenti sampai owner mengisinya.

| Name | Purpose / type | Required / condition | Environment | Safe example | Owner / source | Secret? | Consumer / validation |
|---|---|---|---|---|---|---|---|
| `N8N_IMAGE` | Exact n8n image reference; string tag/digest | Required | local-isolated, demo-vps | `N8N_IMAGE=` | DevOps / verified registry release | No | Compose `n8n.image`; reject empty, placeholder, dan floating `latest` |
| `PGVECTOR_IMAGE` | Exact PostgreSQL+pgvector image reference; string tag/digest | Required | local-isolated, demo-vps | `PGVECTOR_IMAGE=` | DevOps / verified registry release | No | Compose `postgres.image`; reject empty, placeholder, `latest`, atau incompatibility |
| `CADDY_IMAGE` | Exact Caddy image reference; string tag/digest | Required hanya demo-vps | demo-vps | `CADDY_IMAGE=` | DevOps / verified registry release | No | Compose `caddy.image`; reject empty, placeholder, dan `latest` |
| `PUBLIC_HOSTNAME` | Public FQDN untuk webhook; hostname | Required hanya demo-vps/live Telegram | demo-vps | `n8n.example.invalid` | Human / DNS yang dikelola Human | No | Compose/Caddy/n8n derived vars; reject IP, scheme/path, `.invalid`, atau DNS yang tidak mengarah ke exact VPS saat live |
| `ACME_EMAIL` | Kontak sertifikat; email | Required hanya automatic public TLS | demo-vps | `ops@example.invalid` | Human / mailbox operasional | No; nilai nyata minimal Confidential | Caddy; valid email dan bukan `.invalid` saat live |
| `GENERIC_TIMEZONE` | Zona waktu IANA | Required | local-isolated, demo-vps | `Asia/Jakarta` | Human / target operasi | No | n8n `GENERIC_TIMEZONE` dan `TZ`; reject timezone tidak dikenal |
| `N8N_ENCRYPTION_KEY` | Master key credential encryption; string acak kuat | Required | local-isolated, demo-vps | `N8N_ENCRYPTION_KEY=` | Human / approved local secret source | Yes | n8n; nonempty/non-placeholder, konsisten selama lifecycle, tidak pernah dicetak |
| `POSTGRES_DB` | Nama database cluster aplikasi; identifier | Required | local-isolated, demo-vps | `automation` | Architect / project schema | No | Postgres/init/n8n; identifier tervalidasi, bukan database shared/production |
| `POSTGRES_USER` | Bootstrap/admin database role; identifier | Required hanya initialization/maintenance | local-isolated, demo-vps | `cluster_admin` | DevOps / project initialization | No | Postgres container; tidak menjadi credential workflow |
| `POSTGRES_PASSWORD` | Bootstrap/admin database password | Required | local-isolated, demo-vps | `POSTGRES_PASSWORD=` | Human / approved local secret source | Yes | Postgres initialization/maintenance; nonempty/non-placeholder, tidak diteruskan ke n8n workflow |
| `N8N_DB_USER` | Least-privilege role untuk schema n8n | Required | local-isolated, demo-vps | `n8n_app` | Architect / project initialization | No | Postgres init dan derived n8n DB config; identifier tervalidasi |
| `N8N_DB_PASSWORD` | Password role n8n | Required | local-isolated, demo-vps | `N8N_DB_PASSWORD=` | Human / approved local secret source | Yes | Postgres init + n8n DB connection; nonempty/non-placeholder |
| `RAG_INGEST_DB_USER` | Role write corpus/staging | Required | local-isolated, demo-vps | `rag_ingest` | Architect / project initialization | No | Postgres init + n8n credential reference; hanya grant schema RAG yang diperlukan |
| `RAG_INGEST_DB_PASSWORD` | Password role ingest | Required | local-isolated, demo-vps | `RAG_INGEST_DB_PASSWORD=` | Human / approved local secret source | Yes | Postgres init dan credential n8n; nonempty/non-placeholder |
| `RAG_RUNTIME_DB_USER` | Role read corpus + write dedup/safe event | Required | local-isolated, demo-vps | `rag_runtime` | Architect / project initialization | No | Postgres init + n8n credential reference; tidak boleh mengubah active corpus/content |
| `RAG_RUNTIME_DB_PASSWORD` | Password role runtime | Required | local-isolated, demo-vps | `RAG_RUNTIME_DB_PASSWORD=` | Human / approved local secret source | Yes | Postgres init dan credential n8n; nonempty/non-placeholder |
| `RAG_EMBEDDING_DIMENSION` | Dimensi vector untuk schema; positive integer | Required sebelum DB init/ingest | local-isolated, demo-vps | `RAG_EMBEDDING_DIMENSION=` | Engineer / metadata model embedding yang dipilih | No | Postgres init + workflow preflight; harus cocok dengan output aktual dan embedding profile active |
| `N8N_AI_TIMEOUT_MAX` | Batas maksimum AI node; integer milliseconds | Required sebelum integration/E2E | local-isolated, demo-vps | `N8N_AI_TIMEOUT_MAX=` (`UNKNOWN` sampai profiling) | Engineer + DevOps / measured latency budget | No | n8n AI nodes; positive integer dan cukup kecil agar final Telegram send masih dapat selesai sebelum `<5.000 ms` |
| `EXECUTIONS_DATA_MAX_AGE` | Retention metadata eksekusi; integer hours | Required | local-isolated, demo-vps | `24` | Architect / temporary demo lifecycle | No | n8n pruning; positive integer; bukan izin menyimpan payload |

## 2. Variabel runtime yang fixed atau diturunkan

Variabel di bagian ini tetap harus di-audit sebagai consumer configuration, tetapi tidak diduplikasi sebagai input bebas di `.env.example`. Compose membentuknya dari input operator atau menetapkan nilai desain berikut.

| Name | Purpose / type | Required / condition | Environment | Safe example | Owner / source | Secret? | Consumer / validation |
|---|---|---|---|---|---|---|---|
| `DB_TYPE` | Backend n8n database; enum | Required | local-isolated, demo-vps | `postgresdb` | Architect / fixed design | No | n8n; hanya `postgresdb` |
| `DB_POSTGRESDB_HOST` | Internal DB service host | Required | local-isolated, demo-vps | `postgres` | DevOps / Compose service name | No | n8n; harus resolve hanya pada private Compose network |
| `DB_POSTGRESDB_PORT` | Internal DB port; integer | Required | local-isolated, demo-vps | `5432` | DevOps / Postgres service | No | n8n; tidak dipublish ke host |
| `DB_POSTGRESDB_DATABASE` | n8n database name | Required | local-isolated, demo-vps | Diturunkan dari `POSTGRES_DB` | DevOps / Compose interpolation | No | n8n; exact match bootstrap database |
| `DB_POSTGRESDB_USER` | n8n DB role | Required | local-isolated, demo-vps | Diturunkan dari `N8N_DB_USER` | DevOps / Compose interpolation | No | n8n; role hanya schema `n8n` |
| `DB_POSTGRESDB_PASSWORD` | n8n DB role password | Required | local-isolated, demo-vps | Kosong pada template; diturunkan dari `N8N_DB_PASSWORD` | Human/DevOps / injected runtime | Yes | n8n; tidak dicetak atau masuk render config evidence |
| `DB_POSTGRESDB_SCHEMA` | n8n-owned schema | Required | local-isolated, demo-vps | `n8n` | Architect / fixed design | No | n8n; exact schema, berbeda dari `rag` |
| `N8N_HOST` | Hostname publik yang diketahui n8n | Required demo-vps | demo-vps | Diturunkan dari `PUBLIC_HOSTNAME` | DevOps / Compose interpolation | No | n8n; hostname saja |
| `N8N_PORT` | Internal n8n port; integer | Required | local-isolated, demo-vps | `5678` | Architect / fixed design | No | n8n/Caddy; tidak dipublish langsung |
| `N8N_PROTOCOL` | Public URL scheme; enum | Required demo-vps | demo-vps | `https` | Architect / fixed design | No | n8n URL generation; hanya `https` untuk live Telegram |
| `WEBHOOK_URL` | Canonical public webhook base URL | Required live Telegram | demo-vps | `https://n8n.example.invalid/` | DevOps / derived from `PUBLIC_HOSTNAME` | No | n8n Telegram Trigger; exact HTTPS origin, trailing slash konsisten |
| `N8N_PROXY_HOPS` | Trusted reverse-proxy hop count; integer | Required demo-vps | demo-vps | `1` | Architect / one Caddy hop | No | n8n; harus sama dengan topology aktual |
| `TZ` | Container/system timezone | Required | local-isolated, demo-vps | Diturunkan dari `GENERIC_TIMEZONE` | DevOps | No | n8n container; exact match |
| `EXECUTIONS_MODE` | n8n execution mode; enum | Required | local-isolated, demo-vps | `regular` | Architect / fixed design | No | n8n; queue mode ditolak untuk scope ini |
| `N8N_CONCURRENCY_PRODUCTION_LIMIT` | Max production workflow executions; integer | Required demo-vps | demo-vps | `1` | Architect / single-user provider-capacity boundary | No | n8n; exact `1` sampai capacity review |
| `EXECUTIONS_DATA_SAVE_ON_SUCCESS` | Save execution payload on success; enum | Required | local-isolated, demo-vps | `none` | Architect / data minimization | No | n8n; exact `none` |
| `EXECUTIONS_DATA_SAVE_ON_ERROR` | Save execution payload on error; enum | Required | local-isolated, demo-vps | `none` | Architect / data minimization | No | n8n; exact `none`; safe event disimpan terpisah |
| `EXECUTIONS_DATA_SAVE_ON_PROGRESS` | Persist per-node progress payload; boolean | Required | local-isolated, demo-vps | `false` | Architect / data minimization | No | n8n; exact `false` |
| `EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS` | Save manual execution payload; boolean | Required | local-isolated, demo-vps | `false` | Architect / data minimization | No | n8n; exact `false`; evidence dibuat oleh test harness/report tersanitasi |
| `EXECUTIONS_DATA_PRUNE` | Enable rolling pruning; boolean | Required | local-isolated, demo-vps | `true` | Architect / temporary lifecycle | No | n8n; exact `true` |
| `N8N_BLOCK_ENV_ACCESS_IN_NODE` | Block workflow node access to process env; boolean | Required | local-isolated, demo-vps | `true` | Architect / secret boundary | No | n8n; exact `true` |
| `N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS` | Enforce settings permissions; boolean | Required on Linux containers | local-isolated, demo-vps | `true` | Architect / security baseline | No | n8n; exact `true`, compatibility verified on selected image |
| `N8N_RESTRICT_FILE_ACCESS_TO` | Allowed file-node root; absolute container path | Required | local-isolated, demo-vps | `/files/docs` | Architect / read-only corpus mount | No | n8n; resolved path must stay inside corpus mount |
| `N8N_DIAGNOSTICS_ENABLED` | n8n diagnostics telemetry; boolean | Required | local-isolated, demo-vps | `false` | Architect / data minimization | No | n8n; exact `false` |
| `N8N_PERSONALIZATION_ENABLED` | n8n personalization prompts; boolean | Required | local-isolated, demo-vps | `false` | Architect / minimal instance | No | n8n; exact `false` |

## 3. Kontrak AI Provider

Konfigurasi AI tidak dimasukkan sebagai sekumpulan variabel vendor-spesifik di `.env.example`. Adapter awal memakai HTTP OpenAI-compatible untuk operasi chat dan embeddings; binding aktual disimpan di credential store dan `rag_settings` agar deployment dapat memakai endpoint private/self-hosted atau hosted yang telah disetujui tanpa mengubah alur RAG.

| Binding | Required / condition | Owner / source | Secret? | Consumer / validation |
|---|---|---|---|---|
| Provider Base URL | Required sebelum ingest/integration/E2E | Human / endpoint yang dipilih | Internal; dapat sensitif | n8n credential; exact HTTPS origin atau private endpoint yang disetujui, health dan contract test harus lulus |
| Provider authentication | Sesuai provider; tetap explicit walau endpoint tidak memerlukan token | Human / approved secret source | Yes bila berupa key/token | n8n credential store; tidak ada fallback ke workflow JSON, environment umum, atau URL berisi secret |
| Chat model identity | Required sebelum Q&A E2E | Human + Engineer / provider model inventory | No; dapat Internal | `rag_settings`; exact ID/version/digest bila tersedia, output contract dan parameter generation tervalidasi |
| Embedding profile | Required sebelum DB init/ingest | Human + Engineer / provider model inventory | No; dapat Internal | `rag_settings`; provider + model identity + normalization + dimension; wajib identik untuk indexing dan querying |
| Provider transport profile | Required untuk demo-vps | Human + DevOps / approved topology | Private key/token adalah Restricted | Hosted memakai HTTPS dan egress allowlist; private/self-hosted memakai route/firewall privat yang disetujui; tidak ada public ingress ke endpoint private |

Key atau konfigurasi jaringan privat bukan project environment variables. Material rahasia berada di credential/secret store OS dengan permission ketat; evidence hanya mencatat profile dan hasil validasi tersanitasi.

## 4. Credential-store dan runtime binding non-environment

| Safe reference | Consumer | Owner / provisioning | Boundary dan validation |
|---|---|---|---|
| `telegram-demo-bot` | Telegram Trigger dan Telegram send node pada workflow Q&A | Human memasukkan bot token di n8n credential store | Bot khusus demo; token Restricted; connection test tanpa menampilkan token; revoke setelah demo |
| `ai-provider` | Adapter chat dan embeddings OpenAI-compatible | Human memasukkan Base URL dan autentikasi, bila diperlukan, di n8n credential store | Endpoint harus exact target yang disetujui; health, model identity, chat, embeddings, output shape, dan dimension diverifikasi tanpa menyalin prompt. Hosted profile memerlukan approval data-processing Human terlebih dahulu |
| `postgres-rag-ingest` | Workflow ingest | Human/DevOps memasukkan role `rag_ingest` di n8n credential store | Hanya schema RAG dan grant write/activate yang diperlukan; bukan admin DB |
| `postgres-rag-runtime` | Workflow Q&A | Human/DevOps memasukkan role `rag_runtime` di n8n credential store | Read corpus/settings + write dedup/safe event saja; tidak dapat mengubah corpus active |
| n8n owner account | Editor/admin UI | Human membuat owner pertama melalui UI privat | Password/MFA material Restricted; tidak masuk `.env.example` atau export |
| Telegram allowed chat/group ID | Telegram Trigger runtime field | Human mengisi setelah import | Minimal Confidential; tidak ada pada export publik; workflow tidak boleh dipublish ketika kosong/placeholder |
| RAG runtime settings | `rag_settings` dibaca kedua workflow | Engineer membuat schema; Human/Engineer mengisi nilai non-secret yang telah dikalibrasi | `chat_model`, `embedding_model`, `embedding_profile_id`, retrieval limit, minimum similarity, context/output bounds, config revision; required kosong → fail-closed |

Nama vendor, lokasi provider, dan nama model tidak di-hard-code di repository. Export publik memakai binding generik/unbound, sedangkan evidence mencatat provider profile serta model ID/version/digest aktual secara tersanitasi agar hasil dapat direproduksi.

## 5. Runtime Profiles dan Source Precedence

### `local-isolated`

- Target: Docker Compose terisolasi pada PC/development host; n8n hanya bind ke loopback, PostgreSQL private, Caddy tidak diperlukan, Telegram dan provider-failure tests memakai synthetic mock kecuali Human mengizinkan sandbox bot.
- Working directory: root project. Launcher yang dibuat Engineer/DevOps wajib memilih `deploy/compose.yaml`, profile local, project name khusus test, dan `--env-file .env.test` secara eksplisit.
- Source precedence: launcher allowlist → `.env.test` untuk Compose interpolation → explicit service `environment`. Inherited process variables yang namanya bertabrakan menyebabkan preflight stop; tidak ada fallback ke `.env`.
- Credential/runtime: dummy/mock account milik project test; `/docs` atau fixture corpus synthetic di-mount read-only; named volumes memiliki project name test unik.
- Cleanup: down memakai file/profile/project name yang sama. Volume tidak dihapus otomatis kecuali exact test volume disetujui sebagai disposable.

### `demo-vps`

- Target: VPS Ubuntu 24.04 milik Human; Caddy+n8n+PostgreSQL/pgvector di Compose, satu AI provider terpilih di luar core stack, dan satu Telegram bot/chat milik Human. Side effect hanya pesan ke chat demo, call ke endpoint AI yang disetujui, dan write ke database/volume project.
- Working directory: root project checkout di VPS. Launcher memakai `deploy/compose.yaml`, project name demo tetap, dan `--env-file .env` eksplisit.
- Source precedence: preflight-validated `.env` → explicit Compose interpolation → explicit per-service `environment`. Tidak memakai service-level `env_file`, tidak mewarisi target dari shell, dan tidak merender secret ke output.
- Credential precedence: n8n credential store adalah satu-satunya sumber credential workflow; tidak ada fallback ke env/workflow JSON. `rag_settings` adalah satu-satunya sumber model/retrieval config runtime.
- Missing domain/TLS/provider transport/model/credential/settings membuat workflow tetap unpublished atau readiness gagal sebelum provider call/write.
- Cleanup setelah gate Human: backup/export aman terlebih dahulu, lalu unpublish/revoke/down secara project-scoped; tidak ada global Docker prune.

### `portfolio-distribution`

- Target: repository GitHub tanpa runtime aktif.
- Hanya `.env.example`, workflow exports tersanitasi dan unpublished, corpus/eval/demo yang telah disetujui Public/synthetic, serta dokumentasi/evidence tersanitasi yang boleh hadir.
- `.env`, `.env.test`, n8n data, database dump, ACME state, private-network config/key, credential export, raw execution data, dan screenshot dengan identifier dilarang.
- Importer wajib melakukan provisioning sendiri; repository tidak boleh tampak runnable bila required binding masih kosong.

## 6. Missing-Value dan Wrong-Target Behavior

1. Required value kosong, placeholder, malformed, `latest`, atau `UNKNOWN` menghentikan validation sebelum pull/start/network/write sesuai consumer stage.
2. `RAG_EMBEDDING_DIMENSION` atau embedding profile mismatch menghentikan ingest/query; sistem tidak mencampur vector berbeda.
3. `PUBLIC_HOSTNAME` yang tidak resolve ke exact VPS, HTTPS tidak trusted, atau `WEBHOOK_URL` mismatch mencegah publish Telegram workflow.
4. AI provider Base URL harus resolve/rute ke exact approved endpoint. Origin publik yang tidak disetujui, loopback container yang salah, downgrade TLS, atau health/model/contract mismatch ditolak.
5. Chat restriction/Telegram secret/credential/model setting kosong membuat Q&A workflow fail-closed dan unpublished.
6. Profile test tanpa `.env.test` berhenti; tidak pernah fallback ke `.env`, shell target, credential, network, atau volume demo.
7. Compose hanya menerima explicit allowlist environment. Validasi memakai mode quiet dan evidence hanya mencatat command/exit/error category yang aman, bukan rendered config.

## 7. Ignore dan Secret Lifecycle

Engineer merencanakan root `.gitignore` minimal dengan pola `.env*` dan exception hanya untuk `/.env.example`. Semua nested environment, private-network config/key, credential export, n8n data, database dump, ACME state, dan raw screenshot/evidence sensitif ditambahkan secara eksplisit berdasarkan inventory.

Setiap actual Docker build context memiliki `.dockerignore` yang mengecualikan `.env*`, nested env, `.git`, n8n state, database dump, key/certificate, dan credential files. Compose memakai prebuilt exact images sehingga repository tidak memerlukan custom application image kecuali perubahan architecture disetujui.

Human adalah owner seluruh secret. Rotation/revocation dilakukan bila nilai terekspos dan pada akhir demo. State hanya mencatat status/reference, tidak pernah nilai.

## 8. Riwayat Perubahan

| Versi | Tanggal | Perubahan |
|---|---|---|
| `1.0` | `2026-09-14` | Schema awal untuk local-isolated, demo-vps, portfolio distribution, Docker/n8n/PostgreSQL, Ollama host, credential store, dan fail-closed behavior |
| `1.1` | `2026-09-14` | Binding AI digeneralisasi menjadi provider-neutral: OpenAI-compatible adapter awal, endpoint/credential di credential store, model profile di `rag_settings`, dan transport private/hosted bersyarat |
