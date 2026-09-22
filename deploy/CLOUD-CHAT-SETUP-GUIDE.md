# Cloud Chat Setup — Local EmbeddingGemma

Guide ini mengganti **chat model lokal Gemma 4 E2B** dengan provider cloud yang menyediakan kontrak OpenAI-compatible. **EmbeddingGemma tetap lokal** dan corpus aktif tidak perlu di-ingest ulang.

## Status runtime saat ini

- Workflow aktif: `02 — Telegram Grounded Q&A`
- Workflow ID: `IAOqkQsNamEJarHF`
- Chat node: current candidate is pinned to the approved DeepSeek route
- Query embedding: lokal, `http://host.docker.internal:11434/api/embed`
- Ingestion embedding: lokal, `http://host.docker.internal:11434/v1/embeddings`
- Cloud credential `DeepSeek account` bertipe `deepSeekApi` dan dipakai hanya oleh node `Chat Completion`
- `chat_base_url` dan `chat_api_path` remain consistency metadata in `rag.rag_settings`; the credentialed HTTP node does not build a destination from database values

## Yang perlu disiapkan

Untuk current candidate, gunakan DeepSeek yang sudah dipasang pada credential. Penggantian provider bukan lagi perubahan URL/database-only: perlu adapter/workflow review dan Security re-audit.

Provider cloud yang disetujui harus memenuhi semua syarat berikut:

1. Menyediakan HTTPS endpoint OpenAI-compatible.
2. Memiliki route chat `/chat/completions` atau route setara yang didokumentasikan.
3. Menghasilkan respons `choices[0].message.content`.
4. Memiliki model chat yang boleh digunakan untuk pertanyaan dan potongan corpus Confidential.
5. Human sudah menyetujui provider, retention, region, dan batas pemrosesan data.

API key adalah satu-satunya secret. Endpoint dan model chat bukan secret, tetapi tetap harus diisi karena tidak dapat ditentukan dari API key saja.

## Langkah konfigurasi

### 1. Credential cloud

Credential `DeepSeek account` sudah tersedia di runtime dan bertipe `deepSeekApi`. Engineer tidak mengubah API key atau isi credential tersebut.

Jika perlu mengganti API key, buka `http://127.0.0.1:5678` → **Credentials** → `DeepSeek account`, isi/simpan API key DeepSeek, lalu gunakan tombol test credential bila tersedia. Jangan menaruh API key di workflow JSON, SQL, screenshot, atau report.

Credential ini digunakan oleh node **Chat Completion** saja. Node embedding lokal tidak mengirim API key ke Ollama.

### 2. Pastikan binding metadata chat

Node sementara untuk mengubah `rag_settings` sudah dihapus dari workflow ingestion. Ini disengaja: credential ingest tidak boleh menjadi admin/settings writer.

Jika binding metadata perlu diubah oleh operator yang berwenang, lakukan melalui sesi maintenance memakai role bootstrap/admin, bukan credential workflow:

```sql
UPDATE rag.rag_settings
SET config_revision = 'cloud-chat-local-embedding-2026-09-21',
      chat_base_url = 'https://api.deepseek.com',
      chat_api_path = '/chat/completions',
      chat_model = 'deepseek-flash',
      updated_at = now()
WHERE id = 1;
```

Jangan mengubah field berikut untuk pergantian chat saja:

- `embedding_model`
- `embedding_profile_id`
- `embedding_dimension`
- `active_corpus_version`

Batas `ai_timeout_max` harus tetap integer positif dan tidak lebih dari `4000` ms pada konfigurasi online saat ini, karena alur menyisakan waktu untuk pengiriman Telegram.

### 3. Pastikan workflow aktif

Workflow aktif sudah disinkronkan oleh Engineer. Setelah perubahan credential dan `rag_settings`, tidak perlu import ulang workflow.

Jika status di UI tidak langsung berubah setelah restart Docker, buka workflow `02 — Telegram Grounded Q&A`, pastikan credential `DeepSeek account` terpasang pada **Chat Completion**, lalu simpan tanpa mengubah URL manual.

### 4. Tes manual

Kirim satu pertanyaan yang jelas-jelas didukung corpus, lalu satu pertanyaan unsupported. Amati:

- supported → jawaban dengan citation/source yang valid;
- unsupported → `Informasi tidak ditemukan di dokumen resmi.`;
- provider gagal/timeout → pesan layanan tidak tersedia;
- embedding gagal → periksa Ollama lokal, bukan API key cloud.

Jangan menjalankan workflow ingestion hanya karena chat model berubah. Ingestion ulang hanya diperlukan bila embedding model, embedding profile, dimensi, atau endpoint embedding berubah.

## Diagnosis cepat

| Gejala | Pemeriksaan pertama |
|---|---|
| `runtime_settings_incomplete` | `chat_base_url`, `chat_api_path`, atau `chat_model` masih kosong/placeholder |
| `chat_endpoint_invalid` | Metadata bukan persis `https://api.deepseek.com` + `/chat/completions`; endpoint lain ditolak fail-closed |
| HTTP `401/403` | API key pada `DeepSeek account` salah, kosong, expired, atau tidak berhak memakai model |
| HTTP `404` | Base URL sudah mengandung path yang salah atau `chat_api_path` tidak sesuai dokumentasi provider |
| HTTP `400` | Model ID atau parameter OpenAI-compatible provider tidak sesuai |
| `embedding_dimension_mismatch` | Jangan ubah corpus; pastikan Ollama masih menjalankan EmbeddingGemma 768-dim |
| service unavailable/timeout | Profil latency cloud terlalu lambat atau `ai_timeout_max` terlalu rendah |

## Perubahan provider / rollback

Jangan mengubah `chat_base_url` ke Ollama atau provider lain sebagai rollback binding-only. Node credentialed saat ini memakai route DeepSeek yang fixed; perubahan provider memerlukan adapter/workflow yang direview, credential yang sesuai, dan Security re-audit. EmbeddingGemma dan corpus tetap terpisah.

## Batas verifikasi

Engineer sudah memverifikasi wiring statis, migration SQL, JSON workflow, dan pembersihan node sementara. Runtime Docker sedang tidak tersedia pada sesi remediation ini, sehingga penerapan migration ke volume aktif dan health/E2E belum diklaim. QA/Security tetap harus menilai candidate post-fix secara independen.
