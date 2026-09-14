# Synthetic Corpus Fixture — Asisten Pengetahuan Internal Toko Makmur Jaya
# Architecture version: 1.2 | For local-isolated testing only
# =============================================================================
# This is a SYNTHETIC subset of the 26 official documents (00-25).
# Used for local-isolated testing only. Does NOT contain real confidential data.
# Real corpus lives in /docs (mounted read-only at runtime).
# =============================================================================

# File: 00_Company_Profile_Toko_Makmur_Jaya.md
---
source_name: 00_Company_Profile_Toko_Makmur_Jaya.md
source_hash: synthetic_hash_001
---
# Profil Perusahaan Toko Makmur Jaya

Toko Makmur Jaya adalah usaha ritel yang beroperasi sejak 2010, berlokasi di Jalan Merdeka No. 123, Jakarta Pusat. Kami menjual kebutuhan sehari-hari, elektronik ringan, dan pakaian.

**Jam Operasional:**
- Senin - Sabtu: 08:00 - 21:00
- Minggu: 09:00 - 20:00

**Kontak:**
- Telepon: 021-5550123
- Email: info@tokomakmurjaya.example

**Visi:** Menjadi toko kepercayaan utama masyarakat setempat.
**Misi:** Menyediakan produk berkualitas dengan pelayanan ramah dan harga kompetitif.

---

# File: 01_SOP_Buka_Toko.md
---
source_name: 01_SOP_Buka_Toko.md
source_hash: synthetic_hash_002
---
# SOP Buka Toko

**Tujuan:** Memastikan toko siap melayani pelanggan tepat waktu.

**Prosedur:**
1. **07:30** - Manajer/Shift Leader tiba, membuka kunci utama dan alarm.
2. **07:35** - Nyala lamputeras, AC, dan sistem kasir (POS).
3. **07:40** - Cek ketersediaan uang kembalian di kasir (minimal Rp 500.000 pecahan kecil).
4. **07:45** - Inspeksi kebersihan area jual, kasir, dan gudang.
5. **07:50** - Pastikan harga di etalase sesuai sistem.
6. **07:55** - Briefing singkat tim: target hari ini, promo aktif, stok kritis.
7. **08:00** - Buka pintu untuk pelanggan.

**Catatan:** Jika manajer tidak hadir, Shift Leader bertanggung jawab penuh.

---

# File: 02_SOP_Tutup_Toko.md
---
source_name: 02_SOP_Tutup_Toko.md
source_hash: synthetic_hash_003
---
# SOP Tutup Toko

**Tujuan:** Menutup toko dengan aman dan tercatat.

**Prosedur:**
1. **20:45** - Umumkan penutupan 15 menit lagi via音响.
2. **21:00** - Tutup pintu masuk; layani pelanggan yang sudah di dalam.
3. **21:15** - Tutup kasir: hitung kas, catat di buku kas harian, setor ke manajer.
4. **21:25** - Matikan POS, AC, lamputeras (kecuali lampu keamanan).
5. **21:30** - Cek kembali kebersihan, kunci pintu gudang dan kantor.
6. **21:35** - Aktifkan alarm, kunci pintu utama.
7. **21:40** - Manajer/Shift Leader terakhir berangkat.

**Catatan:** Setoran harian wajib diserahkan ke manajer sebelum pulang.

---

# File: 03_SOP_Penanganan_Kas_dan_Setoran_Harian.md
---
source_name: 03_SOP_Penanganan_Kas_dan_Setoran_Harian.md
source_hash: synthetic_hash_004
---
# SOP Penanganan Kas dan Setoran Harian

**Tujuan:** Mengelola kas harian dengan akurat dan transparan.

**Prosedur:**
1. **Awal hari:** Kasir terima uang kembalian dari manajer, catat nominal.
2. **Selama operasional:** Setiap transaksi dicatat otomatis POS; transaksi manual dicatat di buku kas.
3. **Setiap 2 jam:** Kasir cek fisik kas vs POS; selisih > Rp 50.000 dilaporkan ke manajer.
4. **Akhir hari (SOP Tutup Toko):**
   - Hitung total kas fisik (tunai + non-tunai QRIS/transfer).
   - Bandingkan dengan laporan POS.
   - Isi formulir setoran harian: tanggal, total penjualan, total kas, selisih, tanda tangan kasir & manajer.
5. **Setoran:** Uang diserahkan ke manajer; manajer simpan di safe/bringing ke bank.

**Batasan:** Selisih kas > Rp 100.000 wajib investigasi sebelum setoran.

---

# File: 09_FAQ_Jam_Operasional_dan_Lokasi.md
---
source_name: 09_FAQ_Jam_Operasional_dan_Lokasi.md
source_hash: synthetic_hash_005
---
# FAQ Jam Operasional dan Lokasi

**Q: Jam berapa toko buka?**
A: Senin-Sabtu 08:00-21:00, Minggu 09:00-20:00.

**Q: Di mana lokasi toko?**
A: Jalan Merdeka No. 123, Jakarta Pusat (dekat Stasiun Merdeka).

**Q: Apakah buka hari libur nasional?**
A: Tutup pada hari libur nasional besar (Idul Fitri, Natal, Tahun Baru). Libur lainnya buka normal.

**Q: Apakah ada parkir?**
A: Tersedia parkir motor 20 unit dan mobil 5 unit di depan toko (gratis 2 jam pertama).

---

# File: 20_Kebijakan_Cuti_dan_Izin_Karyawan.md
---
source_name: 20_Kebijakan_Cuti_dan_Izin_Karyawan.md
source_hash: synthetic_hash_006
---
# Kebijakan Cuti dan Izin Karyawan

**Cuti Tahunan:**
- Hak cuti: 12 hari/tahun setelah bekerja 1 tahun penuh.
- Pengajuan minimal 2 minggu sebelum cuti via formulir HR.
- Persetujuan manajer wajib; tidak boleh bertabrakan dengan jadwal shift kritis.

**Izin Sakit:**
- Izin sakit < 3 hari: surat keterangan dokter/puskesmas.
- Izin sakit ≥ 3 hari: surat keterangan rumah sakit.
- Gaji dibayar penuh selama izin sakit dengan surat valid.

**Izin Penting (Menikah, Khitanan, Duka Cita):**
- Menikah: 3 hari (karyawan), 1 hari (anak menikah).
- Khitanan: 2 hari.
- Duka cita: 2 hari (orang tua/istri/suami/anak), 1 hari (saudara).

**Cuti Melahirkan:** 3 bulan (1,5 bulan sebelum & 1,5 bulan setelah) sesuai UU.

**Tanpa Keterangan (Alpha):**
- 1 hari: peringatan lisan.
- 2 hari berturut: peringatan tertulis.
- 3 hari berturut: PHK.

---

# File: 24_Kebijakan_Bonus_dan_Insentif_Penjualan.md
---
source_name: 24_Kebijakan_Bonus_dan_Insentif_Penjualan.md
source_hash: synthetic_hash_007
---
# Kebijakan Bonus dan Insentif Penjualan

**Insentif Bulanan:**
- Target penjualan personal: Rp 50.000.000/bulan.
- Pencapaian 100-110%: Bonus Rp 500.000.
- Pencapaian 111-120%: Bonus Rp 1.000.000.
- Pencapaian >120%: Bonus Rp 2.000.000 + hadiah spesial.

**Insentif Tim:**
- Jika total toko > Rp 500.000.000/bulan: seluruh tim dapat bonus Rp 250.000/orang.

**Bonus Tahunan (THR + Performance):**
- THR: 1x gaji pokok (dibayar menjelang lebaran).
- Performance bonus: 0.5-2x gaji pokok berdasarkan appraisal tahunan.

**Syarat:** Karyawan status tetap, minimal 6 bulan kerja, tidak ada sanksi berat tahun berjalan.

---

# File: 25_Kebijakan_Keselamatan_Kerja_K3_Sederhana.md
---
source_name: 25_Kebijakan_Keselamatan_Kerja_K3_Sederhana.md
source_hash: synthetic_hash_008
---
# Kebijakan Keselamatan Kerja (K3) Sederhana

**Umum:**
- Semua karyawan wajib mengikuti pelatihan K3 dasar saat onboarding.
- Laporan insiden/kecelakaan wajib ke manajer maksimal 1x24 jam.

**Kebakaran:**
- APAR tersedia di: kasir (1), gudang (2), kantor (1).
- Jalur evakuasi: pintu depan & pintu belakang gudang.
- Simulasi kebakaran: 2x/tahun.

**Ergonomik & Penanganan Barang:**
- Angkat barang > 20 kg: minta bantuan/gunakan trolly.
- Gunakan sarung tangan saat menangani barang tajam/berbahaya.

**Kebersihan:**
- Lantai basah: tanda "Hati-hati Lantai Licin" wajib dipasang.
- Sampah dibuang ke tempatnya; tidak menumpuk di area kerja.

**P3K:** Kotak P3K di kasir & gudang; minimal 1 orang per shift sertifikat P3K.