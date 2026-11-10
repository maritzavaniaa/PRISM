# Persiapan Sebelum Implementasi

Kerjakan berurutan. Jangan loncat. Tiap langkah punya **hasil** yang harus ada sebelum lanjut.

Total: sekitar 4 jam. Boleh dipecah.

---

## Bagian A. Putuskan dulu (20 menit, tanpa riset)

Semua pilihan sudah ada isinya. Tinggal setuju atau ganti. Salin ke `docs/planning/scope-prototipe.md`.

| No | Hal | Keputusan awal |
|----|-----|----------------|
| 1 | Bahasa | Python |
| 2 | Yang dipindai | Berkas teks di folder repo (bukan riwayat git) |
| 3 | Jenis data yang dideteksi | NIK, NPWP, nomor HP, email, token |
| 4 | Skenario | S1 (PII di berkas), S2 (token di berkas), S3 (PII di berkas log) |
| 5 | Cara scanner baca log (S3) | Berkas log diberikan lewat argumen. Tidak membaca log GitHub langsung |
| 6 | Isi laporan | Tampilkan jenis, berkas, nomor baris, dan nilai yang disamarkan (contoh `************3456`). Jangan tampilkan nilai utuh |
| 7 | Kapan pipeline gagal | Jika ada satu temuan apa pun. Exit code 1 |
| 8 | Data uji | Data buatan (sintetis). Jangan pakai data asli orang |

**Hasil:** file `scope-prototipe.md` berisi 8 baris di atas.

**Kenapa ini penting:** kalau tidak diputuskan, kamu akan berhenti dan bingung di tengah coding.

---

## Bagian B. Pelajari 3 hal kecil (±2 jam)

Tiap hal punya pertanyaan. Jawab pakai kalimatmu sendiri di catatan. Kalau belum bisa menjawab, baca lagi.

### B1. Format NIK, NPWP, dan nomor HP (60 menit)

Cari dan baca: aturan format NIK, format NPWP (termasuk perubahan 2024), dan format nomor HP Indonesia. Cek ke sumber resmi (misalnya situs Dirjen Pajak atau Dukcapil), jangan hanya blog.

Pegangan awal (**cek ulang** ke sumber resmi sebelum dipakai):
- NIK: 16 digit. Digit 1-6 kode wilayah. Digit 7-12 tanggal lahir (tanggal ditambah 40 untuk perempuan). Digit 13-16 nomor urut.
- NPWP: format lama 15 digit. Format baru 16 digit (sama dengan NIK untuk orang pribadi).
- HP: diawali `08` atau `+62`.

Pertanyaan:
1. Dari 16 digit NIK, bagian mana yang bisa dicek valid atau tidak?
2. Apa bedanya NPWP 15 dan 16 digit?
3. Tulis 3 contoh nomor HP yang valid dan 3 yang tidak valid.

**Hasil:** satu tabel kecil di `docs/research/format-pii-indonesia.md`: jenis, format, contoh sintetis, dan aturan validasi.

### B2. Cara kerja regex (45 menit)

Belajar dasar saja dengan situs interaktif (misalnya regex101.com, pilih flavor Python):
- `\d`, `{16}`, `[0-9]`, `|`, `\b`

Latihan:
1. Tulis regex untuk 16 digit angka.
2. Pastikan tidak cocok dengan angka 17 digit (pakai `\b`).
3. Tulis regex untuk nomor HP `08` + 8 sampai 11 digit.

**Hasil:** 3 regex yang jalan di regex101, disalin ke catatan.

### B3. Cara GitHub Actions menggagalkan job (45 menit)

Ini inti prototipe: sebuah step gagal kalau programnya keluar dengan kode selain 0.

Latihan:
1. Buat repo kecil di GitHub (privat tidak apa-apa).
2. Buat `.github/workflows/test.yml` dengan satu step `run: exit 1`.
3. Push. Lihat job jadi merah.
4. Ubah jadi `exit 0`. Push. Lihat job jadi hijau.

Pertanyaan: apa yang membuat job merah?

**Hasil:** screenshot job merah dan hijau. Ini juga bahan laporan.

---

## Bagian C. Coba satu eksperimen pembanding (30 menit)

Tujuannya membuktikan alasan membuat scanner sendiri.

1. Install Gitleaks (`brew install gitleaks`).
2. Buat berkas dengan 1 NIK palsu, 1 nomor HP palsu, dan 1 token palsu bentuk `ghp_` diikuti 36 karakter acak.
3. Jalankan `gitleaks dir <folder> -v`.
4. Catat mana yang terdeteksi dan mana yang tidak.

Dugaan: token terdeteksi, NIK dan HP tidak. Kalau hasilnya berbeda, catat juga, itu temuan.

**Hasil:** satu tabel "yang terdeteksi vs tidak" di `docs/research/tool-gitleaks.md`.

---

## Bagian D. Baru mulai implementasi

Kalau A, B, dan C sudah ada hasilnya, kamu siap. Urutannya:

1. Buat CLI kosong yang membaca satu berkas dan menampilkan jumlah barisnya.
2. Tambahkan satu regex (NIK). Cetak nomor baris yang cocok.
3. Tambahkan masking dan exit code 1.
4. Tambahkan jenis lain satu per satu: NPWP, HP, email, token.
5. Hubungkan ke workflow yang sudah kamu buat di B3.

Jangan menambah fitur lain sebelum langkah 5 jalan.

---

## Jangan dikerjakan dulu

- Riwayat git, severity, pengecualian, dan konfigurasi.
- Package atau GitHub Action yang bisa dipakai ulang.
- Membaca semua isi dokumen riset lama.
