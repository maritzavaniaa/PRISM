# Rencana Harian Menuju 11 November 2026

**Target 11 Nov:** prototipe awal (CLI scanner + workflow GitHub Actions yang gagal saat ada temuan) dan draf bab Introduction + Metodologi.

**Pola:**
- 2-7 Nov (expo matkul lain): tugas ringan, 30-60 menit per hari, bisa dikerjakan di sela waktu.
- 8-10 Nov: hari kerja utama (coding dan menulis).
- 11 Nov: rapikan dan kumpulkan.

Estimasi waktu ada di kurung. Kalau satu hari terlewat, geser tugasnya ke hari berikutnya dan jangan menumpuk di 8-10 Nov. Tugas bertanda ⭐ boleh dilewati kalau waktu mepet.

---

## Senin, 2 Nov (hari ini)

- [ ] Tentukan 10 keputusan cakupan (30 mnt). Tulis jawabannya di `docs/planning/scope-prototipe.md`, satu baris per keputusan:
  - bahasa: Python
  - objek pindai: working tree saja, riwayat git di luar cakupan
  - S3: pindai berkas log
  - laporan: masking 4 karakter terakhir
  - severity: semua temuan menggagalkan pipeline
  - kredensial: kategori terpisah
  - threat fokus: T3 dan T5
  - FR-07 dan FR-08 ditunda
  - Jenkins dan package Action di luar cakupan
  - kolom tak terenkripsi di luar cakupan
- [ ] Tulis rumusan masalah (2-3 kalimat), tujuan, dan manfaat di `docs/report/01-introduction.md` (20 mnt).

## Selasa, 3 Nov

- [ ] Tulis 3-4 alasan kenapa scanner dibuat dari nol (15 mnt), sebagai bahan research gap:
  - Gitleaks fokus secret, bukan PII Indonesia
  - Presidio butuh runtime Python/NER dan tidak dirancang untuk CI/CD
  - tidak ada rule NIK/NPWP bawaan
  - verifikasi tiap poin ke dokumentasi
- [ ] Isi tabel perbandingan tool di bagian 9.1 (45 mnt), dengan kolom: jenis deteksi, dukungan PII Indonesia, cara jalan di CI/CD, lisensi, kelebihan, kekurangan. Betterleaks dicek singkat, lalu putuskan dipakai atau dibuang.

## Rabu, 4 Nov

- [ ] Riset format NIK (45 mnt): struktur 16 digit, tanggal lahir (+40 untuk perempuan), kode wilayah, dan aturan validasi yang bisa dipakai. Catat sumber resminya.
- [ ] Riset NPWP (15 mnt): format 15 digit lama dan 16 digit baru (sama dengan NIK).

## Kamis, 5 Nov

- [ ] Riset format nomor HP Indonesia (20 mnt): awalan +62 dan 08, panjang, dan prefiks operator.
- [ ] Tulis daftar pola regex v1 (30 mnt) untuk NIK, NPWP, HP, email, dan token. Cukup di catatan, belum perlu kode.
- [ ] Putuskan satu aturan validasi tambahan untuk menurunkan false positive, misalnya cek tanggal lahir valid pada NIK (10 mnt).

## Jumat, 6 Nov

- [ ] Cari 5-8 paper related work (45 mnt). Topik yang dicari:
  - secret leakage di GitHub
  - deteksi PII di kode dan log
  - evaluasi scanner secret
  - Simpan judul, tahun, dan satu kalimat inti tiap paper di `docs/research/related-work.md`. Verifikasi bahwa paper benar-benar ada sebelum dikutip.
- [ ] ⭐ Baca abstrak dan kesimpulan 3 paper terpenting (30 mnt).

## Sabtu, 7 Nov

- [ ] Ringkas pasal UU PDP yang dipakai (45 mnt): Pasal 1 ayat 1, Pasal 4, Pasal 16 ayat 2, dan Pasal 35-39. Isi bagian 6.4, 2-3 kalimat per pasal.
- [ ] Putuskan nama metode penelitian (10 mnt), misalnya Design Science Research, dan tulis daftar tahapnya (identifikasi masalah, desain, implementasi, evaluasi).
- [ ] Buat kerangka bab Introduction dan Metodologi berupa poin-poin judul subbab (20 mnt).

---

## Minggu, 8 Nov (hari kerja utama 1: coding)

- [ ] Buat kerangka CLI Python: terima argumen path dan mode (`repo` atau `log`), lalu atur exit code 0, 1, dan 2 (error) (1 jam).
- [ ] Implementasi regex v1 dan fungsi masking (2 jam).
- [ ] Tambahkan validasi tambahan, misalnya tanggal lahir NIK (30 mnt).
- [ ] Buat data uji sintetis kecil dengan Faker `id_ID` dan contoh token palsu (45 mnt). Simpan label ground truth dalam CSV atau JSON.

## Senin, 9 Nov (hari kerja utama 2: integrasi dan Introduction)

- [ ] Buat aplikasi contoh kecil yang menulis log berisi PII sintetis (45 mnt), sebagai bahan S3.
- [ ] Buat workflow `.github/workflows/privacy-scan.yml` yang menjalankan CLI lewat step `run` (45 mnt).
- [ ] Push ke GitHub, lalu cek bahwa job gagal saat ada temuan dan lolos saat bersih. Ambil screenshot untuk laporan (30 mnt).
- [ ] Tulis draf Introduction (2 jam):
  1. latar belakang dan UU PDP
  2. DFD dan LINDDUN ringkas
  3. research gap
  4. rumusan masalah, tujuan, kontribusi
  5. batasan

## Selasa, 10 Nov (hari kerja utama 3: Metodologi)

- [ ] Tulis draf Metodologi (2-3 jam):
  1. metode penelitian
  2. tahapan
  3. desain scanner (alur 10.3)
  4. pola PII dan validasi
  5. rancangan evaluasi: dataset sintetis, precision/recall/FPR, waktu, baseline Gitleaks
- [ ] Jalankan CLI di data uji dan hitung precision/recall awal. Cukup angka kasar (45 mnt).
- [ ] ⭐ Jalankan Gitleaks pada data uji yang sama sebagai pembanding awal (30 mnt).
- [ ] Rapikan DFD dan matriks LINDDUN agar masuk ke bab (30 mnt).

## Rabu, 11 Nov (finalisasi)

- [ ] Baca ulang Introduction dan Metodologi, cek konsistensi istilah dan sitasi (45 mnt).
- [ ] Pastikan repo berisi README singkat, cara menjalankan CLI, dan workflow yang jalan (30 mnt).
- [ ] Kumpulkan: tautan repo, draf bab, dan daftar pertanyaan untuk dosen (15 mnt).

---

## Ditunda sampai setelah 11 Nov

- Package atau GitHub Action yang bisa dipakai ulang
- Uji di repositori publik lain
- Mekanisme pengecualian (FR-08) dan konfigurasi (FR-07)
- Evaluasi NFR selain NFR-02, NFR-03, dan NFR-04
- Bab Results dan Conclusion
