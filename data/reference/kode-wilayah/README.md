# Kode wilayah: provinsi, kabupaten/kota, kecamatan

Daftar ini dipakai untuk memeriksa 6 digit pertama NIK (kode wilayah). Isinya data wilayah administrasi, **bukan data pribadi**.

## Isi

| Berkas | Kode | Jumlah | Contoh |
|---|---|---|---|
| `provinsi.csv` | 2 digit | 38 | `31,Daerah Khusus Ibukota Jakarta` |
| `kabkota.csv` | 4 digit (provinsi + kab/kota) | 514 (416 kabupaten, 98 kota) | `3171,Kota Administrasi Jakarta Pusat` |
| `kecamatan.csv` | 6 digit (provinsi + kab/kota + kecamatan) | 7.285 | `317101,Gambir` |
| `build_from_sql.py` | - | - | Skrip pembuat ketiga berkas CSV |

- Kolom: `kode`, `nama`.
- Kode ditulis tanpa titik, sesuai bentuknya di NIK.
- Desa dan kelurahan tidak diambil.

## Sumber dan versi

| Hal | Isi |
|---|---|
| Dataset | [cahyadsn/wilayah](https://github.com/cahyadsn/wilayah), berkas `db/wilayah.sql`, branch `master` |
| Lisensi dataset | MIT. Hak cipta 2025 cahya dsn |
| Diunduh | 10 November 2026 |
| SHA-256 `wilayah.sql` | `c4c3396d9380d4edee072af1d9dff83573b574d7cd00a6562cf82e200e954031` |
| Dasar hukum menurut dataset | Kepmendagri Nomor 300.2.2-2138 Tahun 2025 (komentar di kepala berkas, terakhir diubah 2026-02-13) dan 300.2.2-2430 Tahun 2025 (README repositori) |
| Pembersihan | Spasi di awal atau akhir nama dihapus (ada satu kasus di `kabkota.csv`) |

## Dasar hukum (dari dokumen resmi)

- Permendagri Nomor 58 Tahun 2021 tentang Kode, Data Wilayah Administrasi Pemerintahan, dan Pulau.
- Kepmendagri Nomor 300.2.2-2138 Tahun 2025 tentang Pemberian dan Pemutakhiran Kode, Data Wilayah Administrasi Pemerintahan, dan Pulau.
- Kepmendagri Nomor 300.2.2-2430 Tahun 2025 (ditetapkan di Jakarta, 23 Juni 2025) mengubah lampiran 2138 **hanya untuk Aceh dan Sumatera Utara** (rekapitulasi dan rincian pulau). Selebihnya 2138 tetap berlaku.
- Salinan 2430 dibaca dari JDIH Sumatera Utara (SHA-256 berkas cocok dengan yang tercantum di halaman JDIH). Salinan dari situs Kemendagri sendiri belum ditemukan.

## Verifikasi

- Tabel "A. Rekapitulasi ... Per Provinsi" di lampiran 2430 dibaca langsung. Berkas itu berupa pindaian, jadi angkanya dibaca dari gambar.
- **Cocok:** 38 kode provinsi, serta jumlah kabupaten, kota, dan kecamatan di setiap provinsi. Total 416 kabupaten, 98 kota, 7.285 kecamatan.
- **Cocok:** hierarki lengkap (setiap kabupaten/kota punya provinsi, setiap kecamatan punya kabupaten/kota).
- **Belum:** kode dan nama kabupaten/kota/kecamatan **satu per satu** belum dibandingkan dengan Lampiran B dan C Kepmendagri 2138, karena lampiran itu tidak diperoleh.
- ⚠️ Belum dicek apakah ada keputusan menteri yang lebih baru dari 2025.

## Catatan pemakaian

- Kode di NIK adalah wilayah **tempat tinggal pada saat mendaftar** (PP 40/2019 Pasal 31) dan tidak berubah saat pemilik pindah. NIK lama bisa memuat kode yang tidak ada di daftar ini (misalnya sebelum pemekaran). ⚠️ Perlu diuji.
- NIK WNI di luar negeri diawali `99` (PP 40/2019 Pasal 32) dan **tidak ada** di daftar ini. Belum ditangani di MVP (lihat `docs/research/format-pii-parkir.md`, bagian P4).
- Kode wilayah Kemendagri ini yang dipakai NIK. Kode BPS bisa berbeda, jangan dicampur.

## Membuat ulang

```bash
python3 -I build_from_sql.py <wilayah.sql> <folder-keluaran>
```

Hanya library standar Python. Berkas `wilayah.sql` diperlakukan sebagai data dan tidak dijalankan.
