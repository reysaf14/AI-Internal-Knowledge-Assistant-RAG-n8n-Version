# ADR-002 — Provider-Neutral AI Boundary

- Status: `ACCEPTED`
- Tanggal keputusan Human: `2026-09-14`
- Dicatat oleh Architect: `2026-09-14`
- Architecture terkait: `.ai/knowledge/architecture.md` version `1.1`
- Menggantikan keputusan: `ADR-001 — Split Runtime VPS dan Local LLM melalui WireGuard`

## Konteks

Project harus layak dipublikasikan sebagai portfolio profesional dan menunjukkan deployment Docker pada VPS, tetapi repository tidak boleh terlihat bergantung pada satu runtime lokal, vendor, model, host, accelerator, atau teknologi tunnel. Human meminta bagian AI lokal dibuat general. Core workload VPS tetap ringan: Caddy, n8n, dan PostgreSQL/pgvector; inference berada di luar core stack.

Corpus pada PRD masih berstatus `Confidential`. Karena itu, kemampuan memakai hosted provider tidak otomatis menjadi izin mengirim corpus atau pertanyaan ke pihak ketiga. Deployment hosted memerlukan persetujuan Human terpisah atas provider, tujuan pemrosesan, retention, dan region.

## Keputusan

1. Core architecture bergantung pada kapabilitas AI, bukan lokasi atau merek provider: satu operasi chat dan satu operasi embeddings.
2. Adapter awal memakai kontrak HTTP OpenAI-compatible. Base URL, autentikasi, chat model identity, embedding profile, dimensi, dan parameter menjadi runtime binding, bukan konstanta repository.
3. Contract test sebelum ingest/E2E memverifikasi health/reachability, autentikasi, model identity, bentuk respons chat, bentuk serta dimensi embedding, timeout, dan kategori error yang aman.
4. Indexing dan querying wajib memakai embedding profile identik. Pergantian provider atau model embedding membuat corpus lama tidak kompatibel dan mewajibkan full re-ingest sebelum aktivasi.
5. Endpoint private/self-hosted memakai route dan firewall privat yang disetujui; teknologi network dipilih saat provisioning dan tidak ditetapkan oleh repository. Endpoint tersebut tidak menjadi public ingress.
6. Endpoint hosted memakai HTTPS, exact-origin egress restriction, dan credential least-privilege, tetapi profile tetap disabled sampai Human menyetujui data-processing boundary.
7. Provider dengan API non-compatible memerlukan adapter terisolasi serta rerun acceptance yang terdampak; requirement bisnis dan alur retrieval-grounding tidak berubah.

## Alternatif yang Dipertimbangkan

| Alternatif | Keputusan | Alasan |
|---|---|---|
| Mempertahankan topologi Ollama + WireGuard sebagai fondasi | Digantikan | Cocok sebagai satu deployment profile, tetapi terlalu spesifik untuk repository portfolio yang harus menunjukkan portabilitas. |
| Cabang workflow berbeda untuk setiap vendor | Ditolak | Menduplicasi alur retrieval, guard, failure handling, dan acceptance surface. |
| Custom AI gateway di dalam project | Ditunda | Menambah service, maintenance, dan konsumsi RAM pada VPS 2 GB tanpa kebutuhan approved saat ini. |
| Hanya hosted provider | Ditolak | Mengubah data boundary dan menghilangkan opsi private/self-hosted tanpa kebutuhan bisnis. |
| Hanya provider lokal | Ditolak | Mengikat desain pada lokasi runtime dan membatasi portability yang diminta Human. |

## Konsekuensi

### Positif

- Repository menampilkan pola deployment yang dapat dipindah antara endpoint private/self-hosted dan hosted approved tanpa mengubah alur bisnis.
- Identitas model dan provider tetap dapat direproduksi melalui config revision serta evidence yang disanitasi.
- Risiko perubahan embedding dikendalikan oleh profile identity dan full re-ingest.
- Teknologi jaringan lokal tidak bocor menjadi asumsi wajib bagi pengguna repository.

### Negatif dan mitigasi

- Tidak semua provider menyajikan detail API dan error yang identik walau mengklaim compatibility. Contract tests dan adapter boundary wajib membuktikan perilaku aktual.
- Latency `<5,0 detik` tetap bergantung pada provider, model, lokasi, warm state, dan jaringan terpilih; benchmark 15/15 tetap hard gate.
- Hosted endpoint memperluas subprocessor/data boundary. Profile tidak boleh diaktifkan tanpa approval Human dan verifikasi retention/region.
- Endpoint private tetap memiliki risiko availability host/uplink. Readiness check diwajibkan dan tidak ada klaim high availability.

## Batas Keputusan

ADR ini menyetujui generalisasi boundary AI pada desain saja. ADR ini tidak menyetujui provider tertentu, pengiriman data ke hosted provider, credential, domain, deploy, public GitHub push, atau implementasi. Architecture version `1.1` tetap memerlukan persetujuan Human sebelum Engineer memulai.
