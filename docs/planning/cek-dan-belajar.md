# Cek dan Belajar: Metode, Tool, Testing

**Tujuan:** memahami dan mengecek ulang pemilihan metode, tool, dan testing sebelum presentasi rencana implementasi ke dosen pembimbing.

**Presentasi:** Selasa, 18 Nov 2026 menurut catatanmu. ⚠️ Menurut kalender 2026 (2 Nov = Senin), **18 Nov jatuh pada Rabu dan Selasa adalah 17 Nov.** Rencana di bawah dibuat agar bahan selesai **Senin malam 16 Nov**, jadi aman untuk dua tanggal itu. Konfirmasi tanggalnya.

**Waktu yang ada:** Kamis 12 (sisa hari), Jumat 13, Senin 16, Selasa 17. Sabtu 14 dan Minggu 15 libur (acara keluarga), tidak ada tugas wajib.

**Fokus:** metode, tool, testing. Pengecekan format PII hanya diisi di waktu senggang (bagian 4).

**Prioritas bila waktu mepet:** metode, lalu testing, lalu tool.

---

## 1. Rencana per hari

### Kamis 12 Nov (sisa hari, ±1 jam)

Tujuan: paham gambaran besar, tanpa beban baru.

- [ ] Baca `docs/planning/mvp-t5.md` bagian 1, 2, 3, dan 4 (40 mnt). Dokumen ini sekarang berbentuk SRS. Bagian 2 berisi diagram alur, bagian 3 daftar kebutuhan (KF dan KN), bagian 4 keputusan MVP.
- [ ] Jawab pertanyaan 4 dan 8 di bagian 3, masing-masing 2 kalimat (15 mnt).
- [ ] Commit dokumen yang belum ter-commit (10 mnt): `docs/research/`, `docs/planning/`, `src/prism/data/`, `.claude/`.

**Hasil:** jawaban 4 dan 8 tertulis, dan semua dokumen ter-commit.

### Jumat 13 Nov (±3 jam): METODE

Tujuan: bisa menjelaskan mengapa memilih regex dengan validasi dan tingkat bukti.

- [ ] Baca `riset-privacy-scanner-cicd.md` bagian 9 dan 10, lalu `implementasi.md` bagian 3 (45 mnt).
- [ ] Tulis 5 kalimat: mengapa regex, bukan ML (30 mnt). Jangan memakai alasan "F1 lebih baik" tanpa bukti.
- [ ] Baca `format-pii-indonesia.md` bagian 1.3, 2.3, dan Lampiran B (45 mnt). Jawab pertanyaan 1, 2, 7.
- [ ] Putuskan nama metode penelitian dan tulis tahapnya (30 mnt). Kandidat: Design Science Research. Tahap contoh: identifikasi masalah, desain, implementasi, evaluasi.
- [ ] Cari rujukan metode (30 mnt).

**Yang perlu dicari:**
- Rujukan untuk Design Science Research. Kandidat yang saya ingat: Hevner dkk. (2004, MIS Quarterly) dan Peffers dkk. (2007). **Verifikasi dulu bahwa keduanya ada dan isinya sesuai** sebelum dikutip.
- 2–3 sumber yang membandingkan pendekatan berbasis aturan dengan ML untuk deteksi PII, bila ada.
- Satu kalimat yang bisa dikutip tentang mengapa format yang jelas cocok untuk regex.

**Hasil:** (1) 5 kalimat alasan memilih regex, (2) paragraf "mengapa tingkat bukti, bukan skor angka", (3) nama metode dan 4–6 tahapnya, (4) 2–4 rujukan terverifikasi. Tambahkan rujukan ke `docs/research/referensi.md` dalam format IEEE.

### Sabtu 14 dan Minggu 15 Nov: libur

Tidak ada tugas wajib. Kalau ada 15 menit senggang, baca ulang jawaban pertanyaan 1 sampai 8. Jangan menambah pekerjaan.

### Senin 16 Nov (±4 jam): TOOL dan TESTING

Tujuan: tabel tool yang bisa dibela, dan rencana evaluasi yang tidak sirkular.

**Tool (±2 jam)**
- [ ] Isi tabel perbandingan di `riset-privacy-scanner-cicd.md` bagian 9.1 dengan isi dari `tool-betterleaks.md`, `tool-presidio.md`, `tool-github-secret-scanning.md`, dan `perbandingan-betterleaks-presidio.md` (45 mnt). Kolom: jenis deteksi, dukungan PII Indonesia, cara jalan di CI, lisensi, kelebihan, kekurangan.
- [ ] Gitleaks belum punya dokumen sendiri. Tulis 1 paragraf dari percobaan yang pernah kamu jalankan (20 mnt).
- [ ] Cek 3 klaim terpenting tiap tool ke dokumentasi resmi (45 mnt). Pilih klaim yang kamu pakai sebagai alasan membuat scanner sendiri.
- [ ] Tulis 3 celah yang menjadi alasan PRISM ada (10 mnt).

**Yang perlu dicari:**
- Apakah tiap tool punya aturan bawaan untuk NIK, NPWP, atau nomor HP Indonesia (jawaban per tool: ya atau tidak, beserta tautan dokumennya).
- Apakah tiap tool bisa menggagalkan job CI lewat exit code.
- Lisensi tiap tool.

**Testing (±2 jam)**
- [ ] Tulis desain evaluasi 1 halaman (60 mnt). Isi: dataset, metrik, pembagian data, baseline, ulang uji.
- [ ] Cari definisi precision, recall, F1, dan FPR dari sumber yang bisa dikutip (30 mnt). Contoh tempat mencari: dokumentasi scikit-learn tentang metrik klasifikasi atau buku teks.
- [ ] Tulis ulang uji kesesuaian U1–U6 di `implementasi.md` bagian 8 agar memakai tingkat bukti, bukan skor angka (30 mnt).

**Yang perlu dicari:**
- Definisi dan rumus precision, recall, F1, FPR yang bersumber.
- Cara memisahkan data kalibrasi dari data uji, dari sumber yang bisa dikutip.
- Penjelasan sederhana tentang bahaya data uji yang dibuat dengan aturan yang sama dengan sistem yang diuji.

**Hasil:** tabel tool lengkap dengan 3 celah, dokumen desain evaluasi 1 halaman, tabel U1–U6 versi tingkat bukti, dan rujukan baru di referensi.md.

### Senin malam 16 Nov (±1 jam): outline slide

- [ ] Buat outline 6–8 slide (lihat bagian 2).
- [ ] Tulis 5 pertanyaan yang mungkin diajukan dosen beserta jawabanmu. Pakai pertanyaan 1 sampai 8 dan butir 12.1 di riset utama.

### Selasa 17 Nov (±2 jam): latihan dan cadangan

- [ ] Latihan presentasi 10 menit, dua kali.
- [ ] Rapikan outline dan perbaiki jawaban yang masih goyah.
- [ ] Kalau presentasi ternyata Rabu 18, hari ini juga untuk mengecek format di bagian 4.

---

## 2. Outline presentasi (usulan, 6–8 slide)

| Slide | Isi | Sumber di repo |
|---|---|---|
| 1 | Masalah dan tujuan: PII Indonesia bocor lewat repositori dan log CI | `riset-privacy-scanner-cicd.md` bagian 1, 5 |
| 2 | Ancaman fokus: T5 dulu (PII di berkas repositori), T3 (log) sesudahnya | bagian 7.5, `mvp-t5.md` bagian 1 dan 2 |
| 3 | Cakupan data: NIK (+NPWP orang pribadi, +KK), HP, email. Dasar: UU PDP Pasal 4 | `dasar-hukum-uu-pdp.md` |
| 4 | Metode: regex, validasi, kata konteks, tingkat bukti (`high`, `medium`, `low`) | `format-pii-indonesia.md` bagian 1.3, 2.3 |
| 5 | Tool pembanding dan alasan membuat scanner sendiri | tabel di bagian 9.1 |
| 6 | Rencana pengujian: dataset, metrik, baseline, pembagian data | dokumen desain evaluasi |
| 7 | Rencana implementasi: langkah 2–14, ±15 jam | `mvp-t5.md` Lampiran B |
| 8 | Pertanyaan untuk dosen: butir 12.1, termasuk cakupan PII saja dan T3 ditunda | bagian 12.1 |

---

## 3. Cek pemahaman

Jawab dengan kalimatmu sendiri. Tulis di bawah pertanyaan. Setelah itu minta saya mengoreksi.

1. Mengapa peluang 0,053% untuk `high` NIK belum berarti 99,947% temuan `high` itu benar-benar NIK?
2. Mengapa NIK dengan bulan 13 dan kecamatan terdaftar jatuh ke `low`? Apa untung ruginya?
3. Mengapa NPWP badan dikeluarkan dari cakupan?
4. Apa bedanya tes unit di langkah 11 dengan evaluasi di langkah 13?
5. Mengapa data uji sintetis buatan sendiri bisa menghasilkan precision yang terlalu bagus?
6. Mengapa data untuk memilih ambang tidak boleh sama dengan data untuk melaporkan hasil?
7. Apa yang berubah pada klaim "hasilnya mirip Presidio" setelah skor angka diganti tingkat bukti?
8. Mengapa job CI merah tidak berarti push ditolak?

---

## 4. Pengecekan format PII (waktu senggang)

Kerjakan satu per satu kapan saja, 10–15 menit masing-masing. Urutan dari yang paling berpengaruh.

| No | Cek | Buka | Halaman |
|---|---|---|---|
| 1 | Struktur NIK, +40 perempuan, awalan `99` | PP 40/2019 [5], peraturan.bpk.go.id | PDF hlm 26–28 |
| 2 | HP dan IP disebut eksplisit, email tidak | UU 27/2022 [31] | PDF hlm 5, dan hlm 39 (Penjelasan) |
| 3 | NDC seluler `08XY`, 0804 dan 0809 bukan nomor pribadi | Permenkominfo 14/2018 [25] | PDF hlm 37–38, 46 |
| 4 | NPWP orang pribadi = NIK | PMK 112/2022 [6] Pasal 2, PMK 81/2024 [8] Pasal 16 | pasal yang disebut |
| 5 | Ulang hitungan Lampiran B dengan kalkulator | `format-pii-indonesia.md` Lampiran B | - |
| 6 | Cocokkan jumlah provinsi, kabupaten, dan kecamatan dengan tabel resmi | Kepmendagri 2430 [1] vs `src/prism/data/kode-wilayah/` | tabel A di lampiran |
| 7 | Sumber yang saya baca lewat ringkasan alat fetch | [9], [10], [18], [19], [32], [36], [37]–[39], [43]–[45] | buka tautan di `referensi.md` |

**Paling lemah, periksa dengan curiga:**
- Struktur nomor KK, hanya dari Perbup Gresik [14], [21].
- Daftar nama peran email (`info`, `admin`, dan seterusnya), saya susun sendiri.
- Tingkat bukti HP `high` untuk `+62`, berdasarkan penilaian, bukan hitungan.
- Aturan "kata konteks menaikkan satu tingkat", belum punya dasar.
- Tabel wilayah di Kepmendagri 2430 saya baca dari gambar pindaian.

---

## 5. Catatan

- Rencana ini sengaja ringan karena waktumu terbatas. Tugas yang tidak selesai digeser ke hari berikutnya, jangan ditumpuk.
- Dokumen lama masih belum sinkron dengan keputusan terbaru: `implementasi.md` (skor angka, cakupan secret, bug prefilter), `riset-privacy-scanner-cicd.md` (target luaran 1, flavor regex, hash vs masking), README, dan `rencana-harian-11-nov.md`. Sinkronisasinya dikerjakan setelah presentasi, kecuali bagian yang kamu butuhkan untuk slide.
- Rujukan baru wajib masuk `docs/research/referensi.md` dalam format IEEE (skill `riset-referensi`).
