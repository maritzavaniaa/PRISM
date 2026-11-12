---
name: riset-referensi
description: Aturan untuk setiap riset di proyek PRISM. Semua sumber dan referensi dikumpulkan di satu dokumen markdown (docs/research/referensi.md) dengan format sitasi IEEE. Pakai skill ini setiap kali melakukan riset, menulis atau mengubah dokumen di docs/research/, atau menambahkan sumber baru.
---

# Riset: satu dokumen referensi, format IEEE

Berlaku untuk semua riset baru mulai 11 November 2026. Riset lama belum dipindahkan.

## Aturan

1. Semua sumber dikumpulkan di **satu dokumen**: `docs/research/referensi.md`. Jangan membuat daftar sumber terpisah di dokumen riset.
2. Setiap sumber ditulis dalam **format IEEE** dan diberi nomor `[n]`.
3. Dokumen riset memakai sitasi di dalam teks, misalnya `[3]`, dan tidak mengulang URL atau judul lengkap. Sumber yang sama selalu memakai nomor yang sama.
4. Nomor berurutan tanpa celah. Sumber baru ditambahkan di akhir. Menghapus sumber yang tidak penting boleh, asalkan nomor sesudahnya digeser dan semua sitasi `[n]` di dokumen riset diperbarui pada saat yang sama (cek dengan grep).
5. Setiap sumber diberi **bagian riset** (misalnya "Format PII Indonesia") dan **tingkat keandalan**:
   - **Resmi**: peraturan, keputusan, dokumentasi vendor, makalah.
   - **Data**: dataset atau repositori.
   - **Tidak resmi**: berita, blog, forum. Jangan jadi satu-satunya dasar sebuah klaim.
6. Tulis hanya sumber yang **benar-benar dibaca**. Sumber yang hanya muncul di hasil pencarian diberi tanda ⚠️ dan keterangan "belum dibaca langsung".
7. Sumber yang asalnya tidak diketahui (misalnya teks yang ditempel pengguna) tetap dicatat, ditandai "sumber asli belum dicatat", bukan dikarang.
8. Jangan menebak judul, penulis, tahun, atau nomor halaman. Kalau tidak diketahui, tulis apa adanya dan jangan diisi.

## Format IEEE yang dipakai

Tanggal ditulis singkatan bahasa Inggris ala IEEE (Jan., Feb., Mar., Apr., May, Jun., Jul., Aug., Sep., Oct., Nov., Dec.). Judul yang diterjemahkan tidak diubah, tetap sesuai aslinya.

| Jenis | Pola |
|---|---|
| Peraturan atau keputusan | `[n] Penerbit, "Judul lengkap," Jenis dan nomor, Kota, Negara, Tgl. Bulan Tahun. [Online]. Available: URL. Accessed: Bulan Tgl., Tahun.` |
| Berita atau artikel web | `[n] Penulis (jika ada), "Judul," Nama Situs, Tgl. Bulan Tahun. [Online]. Available: URL. Accessed: Bulan Tgl., Tahun.` |
| Repositori atau dataset | `[n] Penulis/Organisasi, "Nama," GitHub repository, Tahun. [Online]. Available: URL. Accessed: Bulan Tgl., Tahun.` |
| Dokumentasi atau halaman vendor | `[n] Organisasi, "Judul halaman," Nama produk/situs. [Online]. Available: URL. Accessed: Bulan Tgl., Tahun.` |
| Makalah jurnal | `[n] A. Penulis, B. Penulis, and C. Penulis, "Judul," Nama Jurnal, vol. x, no. y, pp. xx–yy, Bulan Tahun, doi: ...` |
| Makalah konferensi | `[n] A. Penulis and B. Penulis, "Judul," in Proc. Nama Konferensi, Kota, Negara, Tahun, pp. xx–yy.` |
| Buku | `[n] A. Penulis, Judul Buku, edisi ke-x. Kota, Negara: Penerbit, Tahun.` |
| Standar | `[n] Organisasi, Judul Standar, Nomor, Tahun.` |
| Sumber tanpa asal | `[n] Teks yang ditempel pengguna pada riset "X", tanpa sumber asli (belum dicatat).` |

Aturan penulisan:
- Nama penulis: inisial lalu nama belakang (`A. Penulis`). Maksimal enam penulis, lebih dari itu `A. Penulis et al.`.
- Untuk sumber online, selalu ada `[Online]. Available:` dan `Accessed:`. Tanggal akses adalah hari sumber dibaca.
- Satu entri satu paragraf, tanpa daftar bersarang.

## Struktur `docs/research/referensi.md`

```markdown
# Referensi riset PRISM

Format IEEE. Nomor tetap, sumber baru ditambahkan di akhir.

## Daftar

[1] ...
[2] ...

## Peta sumber

| No | Bagian riset | Jenis | Dibaca | Catatan |
|---|---|---|---|---|
| [1] | Format PII Indonesia | Resmi | Halaman 1–6 | ... |
```

- **Daftar** memuat entri IEEE saja, berurutan.
- **Peta sumber** menunjukkan bagian riset, jenis, bagian yang dibaca, dan catatan keandalan. Tabel ini yang dicek saat memverifikasi.

## Langkah setiap riset

1. Sebelum menulis sumber, baca `docs/research/referensi.md` dan pakai ulang nomor jika sumber sudah ada.
2. Tambahkan sumber baru di akhir daftar dan peta sumber.
3. Di dokumen riset, ganti URL atau judul sumber dengan sitasi `[n]`.
4. Sebelum selesai, cek bahwa setiap `[n]` di dokumen riset ada di daftar, dan setiap entri daftar dipakai minimal satu kali.
5. Di laporan akhir ke pengguna, sebutkan sumber mana yang resmi, mana yang tidak resmi, dan mana yang belum dibaca langsung.
