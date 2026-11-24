# Skema Evaluasi PRISM (1 minggu)

> Dibuat 18 Nov 2026. Mengisi "desain evaluasi 1 halaman" di [cek-dan-belajar.md](cek-dan-belajar.md) dan memperinci langkah 10, 11, 13 di [mvp-t5.md](mvp-t5.md) Lampiran B.
> Dasar pilihan ada di [pengujian-tool-lain-dan-data-uji.md](../research/pengujian-tool-lain-dan-data-uji.md). Sumber bernomor ada di [referensi.md](../research/referensi.md).
> ⚠️ = belum diputuskan, belum dibuktikan, atau perkiraan saya.
> Angka jam adalah **perkiraan saya**, belum diukur. Yang dari dokumen rencana ditandai "(rencana)".

## 1. Yang harus dibuktikan

| Klaim | Bukti | Kebutuhan |
|---|---|---|
| Deteksi NIK, HP, email bekerja dalam cakupannya | Precision, recall, F1, FPR pada data berlabel yang belum dipakai untuk menyetel | KN-03 |
| Tingkat bukti (`high`, `medium`, `low`) berguna | Precision per tingkat naik dari `low` ke `high` | KF-11, U5 |
| Ambang bawaan `medium` dan aturan "konteks naik satu tingkat" beralasan | Dibandingkan pada **data kalibrasi**, bukan data uji | U5 |
| NPWP orang pribadi dan KK ikut dilaporkan sebagai `nik` | Sampel berlabel `asal_sampel` = `npwp_op` dan `kk` terdeteksi | KF-10 |
| Hasil bisa diulang | Menjalankan dua kali menghasilkan angka sama | KN-06 |
| Waktu pindai wajar | Waktu pindai dicatat | KN-02 |

Yang **tidak** diklaim: recall pada repo nyata. Repo publik hanya dipakai untuk precision.

## 2. Data

Empat sumber, dari yang paling wajib.

| No | Sumber | Isi | Label | Dipakai untuk | Wajib? | Perkiraan |
|---|---|---|---|---|---|---|
| D1 | **Repo tiruan** di `data/synthetic/<tema>/` | Tema kesehatan, keuangan, kepegawaian, layanan publik. CSV, YAML, Markdown, kode, log. Positif (NIK tiap tingkat, HP, email, NPWP orang pribadi, KK) dan pengecoh (16 digit acak, rekening, ID transaksi, timestamp, UUID) | Pasti, dari pembuatnya | Recall, FPR, precision per tingkat | **Ya** | 105 mnt (rencana) |
| D2 | **Kasus tulisan tangan** `data/synthetic/tulis_tangan/` | 30 kasus: NIK dengan spasi atau tanda hubung, NIK di CSV ekspor, angka 16 digit di log, NIK di tengah kalimat, NIK bersebelahan | Pasti, ditulis sendiri **tanpa melihat kode rule** | Recall pada kasus yang tidak dibuat dengan aturan PRISM | **Ya** | 60 mnt |
| D3 | **Pembanding independen**: python-stdnum [69] | Hanya dijalankan pada NIK dari D1 dan D2 | - | Selisih dengan `assess_nik` | Ya (murah) | 45 mnt |
| D4 | **Repo publik** | 10–15 repo yang berpotensi memuat angka 16 digit | Manual, per temuan | **Hanya precision** di dunia nyata | **Opsional** | 120 mnt |

Catatan D1 dan D2:
- Tema (kesehatan dan seterusnya) hanya cara membuat konteks yang realistis. Bukan kolom hasil, karena NIK yang sama muncul lintas bidang.
- NIK positif dibuat dengan generator sendiri yang mengikuti aturan langkah 6. Faker tidak punya generator NIK Indonesia [70].
- Nilai sintetis tidak diambil dari orang nyata. Tidak boleh ada NIK yang diketahui milik seseorang.

Catatan D3: python-stdnum hanya dipasang untuk evaluasi, bukan untuk PRISM. PRISM sendiri tetap hanya memakai pustaka bawaan Python ([library-bawaan-python.md](../research/library-bawaan-python.md)).

### Kolom `ground_truth.csv`

Menggantikan usulan kolom di langkah 10 (belum diubah di mvp-t5.md).

```csv
berkas,baris,jenis,label,level_diharapkan,asal_sampel,kata_konteks,jenis_berkas,split
```

| Kolom | Isi |
|---|---|
| `jenis` | Yang diharapkan dilaporkan PRISM: `nik`, `hp`, `email` |
| `label` | `positif` atau `negatif` |
| `level_diharapkan` | `high`, `medium`, `low` (untuk NIK) |
| `asal_sampel` | `nik`, `npwp_op`, `kk`, `hp`, `email`, atau jenis pengecoh |
| `kata_konteks` | Kata petunjuk di baris yang sama (`nik`, `npwp`, `kk`, ...) atau kosong |
| `jenis_berkas` | `csv`, `yaml`, `md`, `kode`, `log` |
| `split` | `kalibrasi` atau `uji` |

## 3. Pembagian data

- Bagi per **berkas**, bukan per baris. Satu templat yang dipakai di dua sisi membuat hasil terlalu bagus (pelajaran dari presidio-research [59]).
- Kalibrasi: sekitar sepertiga berkas D1. Uji: sisanya ditambah seluruh D2.
- **Aturan beku:** keputusan ambang dan aturan konteks dibuat dari data kalibrasi, ditulis, lalu dibekukan. Data uji dijalankan **sekali** setelah itu. Bila hasil uji mengecewakan, boleh diperbaiki, tetapi laporan harus menyebut bahwa data uji sudah terlihat.

## 4. Pengukuran

### 4.1 Metrik

| Metrik | Hitung | Dilaporkan |
|---|---|---|
| Precision | TP / (TP + FP) | Per ambang (`low`, `medium`, `high`), dan per tingkat |
| Recall | TP / (TP + FN) | Per ambang, dan per `jenis_berkas` serta `kata_konteks` |
| F1 | 2PR / (P + R) | Per ambang |
| FPR | pengecoh yang terdeteksi / jumlah pengecoh | Per ambang |
| Waktu pindai | detik, ukur 3 kali, laporkan median | Satu angka |

- Pencocokan temuan: per (berkas, baris, jenis).
- ⚠️ Definisi precision, recall, F1, dan FPR belum dikutip dari sumber. Cari sebelum masuk laporan.
- Laporkan jumlah sampel di tiap sel tabel. Dengan data kecil, selisih kecil bisa kebetulan.
- ⚠️ Interval kepercayaan belum diputuskan. Bila ditambahkan, cari sumber metodenya.

### 4.2 Pembanding

| Pembanding | Fungsi | Wajib? |
|---|---|---|
| Baseline `\d{16}` polos | Menunjukkan apa yang ditambah validasi dan tingkat bukti | **Ya** |
| python-stdnum `is_valid` [69] | Selisih dengan `assess_nik`. Tiap selisih diperiksa: salah di PRISM, salah di stdnum, atau beda tahun daftar wilayah | **Ya** |
| Presidio (U1) | Sesuai rencana di implementasi.md bagian 8 | **Opsional**, paling dulu dipotong |

## 5. Tes otomatis (langkah 11)

Meniru pola Presidio [60]: satu tabel `(teks, hasil yang diharapkan)` per rule, termasuk contoh valid, tidak valid, dan variasi pemisah.

| Teks (sintetis) | Diharapkan | Alasan |
|---|---|---|
| `3171011503900001` | `high` | Jakarta Pusat, Gambir, laki-laki |
| `3171015503900002` | `high` | Perempuan (hari 55 = 15 + 40) |
| `3171991503900001` | `medium` | Kecamatan 99 tidak ada |
| `4171011503900001` | `low` | Provinsi 41 tidak ada |
| `3171011513900001` | `low` | Bulan 13 |
| `1234567890123456` | `low` | Hanya 16 digit |
| `NIK: 3171011503900001 tercatat` | `high` | Di tengah kalimat |
| `3171 0115 0390 0001` | ⚠️ keputusan | Tanpa dukungan pemisah, 0 temuan |
| `3171-0115-0390-0001` | ⚠️ keputusan | Idem |

- **Keputusan yang dibutuhkan:** apakah MVP mendukung pemisah. Bila tidak, tulis di batasan dan buat tes yang **memastikan 0 temuan**, supaya batasannya terdokumentasi. Bila ya, itu perubahan di regex (langkah 5) dan tidak masuk jadwal minggu ini.
- Tes tiap rule juga mencakup `fps` eksplisit seperti Gitleaks dan TruffleHog [62]–[64]: nilai yang tidak boleh terdeteksi (UUID, timestamp, nomor rekening).
- `pytest` dijalankan lokal. Folder `tests/` dikecualikan di CI (KF-24), jadi nilai uji sintetis boleh ditulis langsung.

## 6. Jadwal 1 minggu

**Prasyarat:** kode PRISM sampai langkah 9 selesai (CLI, rule NIK, HP, email, laporan JSON). Per 18 Nov 2026 `src/prism/` masih kosong. Kalau belum selesai, minggu evaluasi bergeser.

Satu hari = ±1,5–2 jam ⚠️ (asumsi, sesuaikan dengan waktumu). Total paket minimum ±10,5–11 jam (H1–H5 dan H7), paket penuh ±13–14 jam (ditambah H6) ⚠️. Jam di atas sudah dijumlahkan dari tabel di bawah, tetapi tiap angkanya perkiraan.

| Hari | Kerjakan | Hasil | Jam | Paket |
|---|---|---|---|---|
| H1 | **D1**: generator NIK sendiri, `make_dataset.py`, `ground_truth.csv` dengan kolom baru, bagi `split` | `data/synthetic/` terisi, jumlah positif dan negatif tercatat | 2 | Minimum |
| H2 | **D2**: 30 kasus tulisan tangan (tulis dulu, **baru** jalankan PRISM). **Langkah 11**: tes `pytest` bentuk tabel | `pytest` hijau, kasus pemisah terdokumentasi | 2 | Minimum |
| H3 | `evaluate.py`: cocokkan dengan label, hitung metrik per ambang. Baseline `\d{16}`. **D3**: selisih dengan python-stdnum | Tabel metrik pada data kalibrasi, daftar selisih | 2 | Minimum |
| H4 | **Kalibrasi (U5)**: bandingkan ambang dan aturan konteks pada data kalibrasi. Periksa tiap selisih stdnum. Tetapkan dan **bekukan** keputusan | Catatan keputusan beserta alasan | 1,5 | Minimum |
| H5 | Jalankan pada data uji **sekali**. Ulang untuk cek keterulangan. Ukur waktu 3 kali | Angka akhir di `evaluation/results/` | 1,5 | Minimum |
| H6 | **D4** (opsional): pindai 10–15 repo publik, periksa tiap temuan, hitung precision. Presidio U1 bila masih ada waktu | Tabel precision di dunia nyata | 2–3 | Penuh |
| H7 | Tulis hasil: tabel, batasan, jumlah sampel. Cadangan untuk hari yang meleset | Bab hasil evaluasi | 1,5–2 | Minimum |

### Urutan pemotongan bila waktu mepet

1. Potong **Presidio U1**.
2. Potong **D4** (repo publik). Klaim precision hanya dari data sintetis dan tulisan tangan, dan sebutkan itu sebagai batasan.
3. Potong rincian per `jenis_berkas` dan `kata_konteks`. Tetap laporkan per ambang.
4. Jangan dipotong: pembagian kalibrasi dan uji, baseline, D2 tulisan tangan, tes `pytest`, pengulangan untuk keterulangan.

## 7. Risiko

| Risiko | Penanganan |
|---|---|
| Data D1 dibuat dengan aturan yang sama dengan yang diuji, hasil terlalu bagus | D2 ditulis tanpa melihat rule. D3 memakai implementasi lain. Dicatat sebagai batasan |
| Daftar wilayah python-stdnum beda tahun dengan daftar kita | Selisih akibat itu dipisah dari selisih akibat salah logika. Isi `loc.dat` belum dibandingkan ⚠️ |
| Sampel kecil | Laporkan jumlah di tiap sel. Jangan klaim selisih kecil sebagai nyata |
| NIK asli ditolak karena kode wilayah lama (pemekaran) | Dicatat sebagai batasan. D4 bisa menunjukkan seberapa sering |
| Repo publik berisi data asli orang | Laporan hanya memuat jumlah dan jenis. Nilai tidak disalin ke dokumen. Pilih repo dengan data uji yang jelas bertanda sintetis atau contoh |
| Kode belum selesai saat minggu evaluasi dimulai | Lihat prasyarat. Mulai H1 (data) boleh dikerjakan paralel dengan langkah 7–9 |

## 8. Keluaran

- `data/synthetic/`, `data/labels/ground_truth.csv`
- `evaluation/scripts/make_dataset.py`, `evaluate.py`
- `evaluation/results/`: angka per ambang, tabel per tingkat, daftar selisih stdnum, waktu pindai
- `tests/`: tes `pytest` bentuk tabel
- Catatan keputusan kalibrasi (tanggal, alasan, data apa yang dipakai)
- Bagian batasan, untuk laporan

## 9. Belum diputuskan

- Dukungan pemisah pada NIK (bagian 5).
- Cara menghitung interval kepercayaan, bila dipakai.
- Definisi metrik yang bisa dikutip.
- Daftar 10–15 repo untuk D4 dan cara memilihnya tanpa bias.
- Apakah mvp-t5.md langkah 10 dan KF-25 diperbarui dengan kolom `ground_truth.csv` baru.
