# ADR-001 — Split Runtime VPS dan Local LLM melalui WireGuard

- Status: `SUPERSEDED`
- Tanggal keputusan Human: `2026-09-13`
- Dicatat oleh Architect: `2026-09-14`
- Architecture terkait: `.ai/knowledge/architecture.md` version `1.0`
- Menggantikan keputusan: `Tidak ada`
- Digantikan oleh: `.ai/decisions/adr-002-provider-neutral-ai-boundary.md`

## Konteks

Project adalah demo portfolio sementara yang harus menunjukkan kemampuan deployment. Human telah memiliki VPS kosong Ubuntu 24.04 dengan RAM 2 GB dan 2 vCPU, serta PC dengan RAM 16 GB dan RTX 2060 6 GB. Human memilih Ollama dan akan menyediakan model chat serta embedding sendiri. Repository harus tetap generik dan tidak mengikat implementasi pada nama model tertentu.

VPS perlu menerima webhook Telegram melalui HTTPS dan menjalankan orkestrasi secara stabil, tetapi kapasitasnya tidak memadai untuk inference model 8B. Membuka Ollama PC langsung ke internet akan menambah exposure yang tidak diperlukan.

## Keputusan

1. VPS menjalankan stack Docker Compose berisi Caddy, n8n, dan PostgreSQL/pgvector.
2. Ollama tetap berjalan pada PC operator, bukan di VPS dan bukan sebagai container project.
3. VPS mengakses Ollama hanya melalui tunnel WireGuard host-to-host. Port Ollama tidak dipublikasikan ke internet.
4. Repository menyimpan kontrak dan placeholder runtime generik. Nama/digest model chat dan embedding dicatat saat provisioning/evidence, bukan di-hard-code ke workflow publik.
5. Mode n8n tetap single-main/`regular`; Redis, worker, dan autoscaling tidak ditambahkan.

## Alternatif yang Dipertimbangkan

| Alternatif | Keputusan | Alasan |
|---|---|---|
| Menjalankan model di VPS 2 GB/2 vCPU | Ditolak | Kapasitas tidak proporsional untuk model yang dipilih dan akan bersaing dengan n8n/database. |
| Membuka port Ollama PC ke internet | Ditolak | Menambah public attack surface dan tidak diperlukan untuk satu VPS/PC. |
| Cloud LLM API | Ditunda | Human memilih local AI sementara; cloud menambah credential/provider/data boundary. Dapat dipertimbangkan lewat revisi bila latency lokal gagal. |
| Tailscale/mesh VPN terkelola | Tidak dipilih | Lebih mudah untuk NAT, tetapi menambah akun dan control plane pihak ketiga. WireGuard cukup untuk dua peer dan VPS publik. |
| Menjalankan seluruh stack pada PC | Ditolak untuk demo target | Tidak menunjukkan deployment VPS publik yang diminta dan webhook bergantung pada workstation sebagai ingress. |
| Queue-mode n8n + Redis/worker | Ditolak | Pengguna tunggal, corpus kecil, dan VPS 2 GB tidak membutuhkan overhead atau kompleksitas ini. |

## Konsekuensi

### Positif

- Demo memperlihatkan deployment HTTPS/Docker pada VPS tanpa menaruh inference berat di host kecil.
- Prompt dan context model tetap pada perangkat lokal Human, melewati tunnel privat.
- Model dapat diganti melalui binding/config revision tanpa mengganti requirement atau alur bisnis.
- Jumlah service dan biaya maintenance tetap proporsional.

### Negatif dan mitigasi

- PC, Ollama, WireGuard, dan uplink rumah menjadi single point of failure. Readiness check wajib sebelum demo; tidak ada klaim high availability.
- Dua model yang tidak muat bersamaan pada VRAM dapat di-queue/unload/reload dan mengancam target `<5,0 detik`. Benchmark `REQ-006` tetap hard gate; model/topology dibawa kembali ke Human bila gagal.
- Konfigurasi WireGuard dan firewall harus dikelola pada dua host. Private key tetap di OS store, dan peer dicabut setelah demo.
- Perubahan provider dengan API non-Ollama-compatible memerlukan perubahan adapter node/credential serta retest, walau alur retrieval dan acceptance tetap sama.

## Batas Keputusan

ADR ini dipertahankan sebagai histori keputusan architecture version `1.0`. Topologi AI lokal spesifik di dalamnya tidak lagi menjadi keputusan aktif setelah `ADR-002`; domain, credential, deploy, public GitHub push, dan implementasi tetap memerlukan gate masing-masing.
