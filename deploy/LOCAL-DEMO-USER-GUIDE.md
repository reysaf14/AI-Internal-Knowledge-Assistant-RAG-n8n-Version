# User Guide — Local Demo

## Scope

Panduan ini untuk menjalankan ulang demo lokal setelah sesi demo ditutup. Demo tetap menggunakan dua workflow sumber yang sama:

- `workflows/01-corpus-ingestion.json` — ingest corpus dan aktivasi versi corpus secara atomic.
- `workflows/02-telegram-grounded-qa.json` — Telegram update → claim/dedup → embedding → pgvector retrieval → grounded answer → diagnostic → delivery receipt.

Cleanup M8 sudah menonaktifkan runtime dan menghapus credential dari n8n. Volume PostgreSQL dan n8n tetap dipertahankan, sehingga corpus dan state tidak ikut dihapus.

## Status setelah cleanup

- Container `rag-n8n-local`, `rag-postgres-local`, dan `rag-egress-gateway-local`: stopped.
- Workflow runtime: tetap ada, tetapi inactive.
- Telegram webhook: sudah dihapus melalui Bot API.
- Credential n8n project-scoped: sudah dihapus (`telegram-demo-bot`, `DeepSeek account`, `postgres-rag-ingest`, `postgres-rag-runtime`, dan credential tester lama `ai-provider`).
- File ingress sementara `deploy/e2e-temp/Caddyfile`: sudah dihapus karena bukan jalur demo yang dipertahankan.
- Volume: tetap ada; jangan gunakan `down -v` kecuali memang ingin membuang state demo.

## Menyalakan ulang demo

Jalankan dari root project:

```powershell
docker compose -f deploy/compose.yaml --project-name rag-local --env-file .env.test up -d
```

Tunggu healthcheck, lalu buka `http://127.0.0.1:5678`.

### Bind credential PostgreSQL

Buat dua credential PostgreSQL dengan nama persis berikut. Host harus `postgres`, bukan `localhost` atau `127.0.0.1` karena n8n berjalan di container.

| Credential | User | Dipakai oleh |
|---|---|---|
| `postgres-rag-ingest` | `rag_ingest` | Workflow 01 |
| `postgres-rag-runtime` | `rag_runtime` | Workflow 02 |

Database, password, dan port mengikuti `.env.test`; jangan menyalin password ke workflow JSON, screenshot, atau report.

### Bind chat provider

Buat `DeepSeek account` bertipe `deepSeekApi`, lalu masukkan API key pada credential store n8n. Pasang credential itu hanya pada node `Chat Completion` workflow 02.

Node tersebut tetap memanggil route internal `http://egress-gateway:8080/deepseek/chat/completions`. Gateway meneruskan ke origin provider yang direview; jangan mengganti URL node menjadi URL bebas atau membangun URL dari input/database.

### Bind Telegram

Buat `telegram-demo-bot` bertipe Telegram API. Gunakan token baru atau token yang sudah direvoke melalui BotFather. Pada field **Base URL**, isi:

```text
http://egress-gateway:8080/telegram
```

Pasang credential pada `TelegramTrigger` dan `Telegram Send` workflow 02.

### Rebind workflow yang sudah ada

Workflow runtime tidak dihapus. Setelah credential dibuat, pilih credential baru pada node-node yang menampilkan credential missing:

1. Workflow 01: semua node PostgreSQL memakai `postgres-rag-ingest`.
2. Workflow 02: `Settings Query`, `Claim Update`, `PGVector Retrieval`, diagnostic, dan event nodes memakai `postgres-rag-runtime`.
3. Workflow 02: `TelegramTrigger` dan `Telegram Send` memakai `telegram-demo-bot`.
4. Workflow 02: `Chat Completion` memakai `DeepSeek account`.

Jika memilih import ulang export JSON, tetap lakukan rebind di UI setelah import; ID credential lama sengaja sudah tidak valid setelah cleanup.

## Menyiapkan corpus dan settings

1. Pastikan `rag.rag_settings` masih memiliki `embedding_model`, `embedding_profile_id`, `embedding_dimension=768`, model chat, timeout, retrieval limit, dan allowed Telegram chat ID.
2. Pastikan database masih memiliki active corpus. Volume tidak dihapus oleh cleanup, jadi biasanya tidak perlu ingest ulang.
3. Jika corpus memang perlu dibuat ulang, jalankan workflow 01 dengan **Manual Trigger** dan pastikan alurnya mencapai `Activate Corpus (Atomic)`.
4. Jangan mengubah `chat_base_url`, `chat_api_path`, atau embedding dimension hanya untuk mengatasi credential error. Ikuti setup guide provider bila mengganti provider.

## Telegram E2E

Telegram tidak menerima webhook loopback HTTP. Untuk E2E nyata:

1. Sediakan approved HTTPS `WEBHOOK_URL` yang aktif dan dapat dijangkau Telegram.
2. Set environment itu sebelum recreate n8n.
3. Pastikan credential Telegram sudah terpasang dan workflow 02 masih inactive sebelum readiness check.
4. Aktifkan workflow 02 hanya setelah webhook registration berhasil.
5. Kirim pertanyaan supported dan unsupported dari chat yang diizinkan; periksa jawaban, citation, safe event, dan delivery receipt.

Untuk validasi graph/provider/database lokal tanpa Telegram, workflow 02 boleh tetap inactive.

## Menutup demo kembali

```powershell
docker compose -f deploy/compose.yaml --project-name rag-local --env-file .env.test stop
```

Perintah tersebut menghentikan container tetapi mempertahankan volume. Jangan memakai `down -v` pada demo yang masih ingin dipulihkan.

Untuk revocation penuh token Telegram, buka BotFather dan gunakan `/revoke` pada bot demo. Menghapus webhook saja menghentikan delivery, tetapi tidak mencabut token di sisi Telegram. Setelah itu hapus atau rotasi material lokal yang tidak lagi diperlukan.

## Batasan

Dokumen ini adalah runbook local portfolio/demo, bukan runbook production. M7 semantic QA dan Security scoped local-demo tetap merupakan evidence terpisah. Public portfolio publication, client handoff, production use, atau release claim memerlukan Security scope/re-audit baru.
