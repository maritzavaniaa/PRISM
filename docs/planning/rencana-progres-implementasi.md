# Rencana Progres Implementasi PRISM MVP T5

> Dibuat 24 Nov 2026. Turunan dari [mvp-t5.md](mvp-t5.md) (Lampiran B, [B.2 Langkah implementasi](mvp-t5.md#b2-langkah-implementasi)). Tujuan: memberi gambaran **urutan kerja dan tes yang menandai tiap langkah selesai**.
> Dokumen ini tidak menambah fitur. Yang berubah dari mvp-t5 hanya **kapan tes ditulis**, yaitu tes ditulis bersamaan dengan tiap langkah (lihat bagian 2, ⚠️ Usulan).
> ⚠️ = belum diverifikasi, belum diputuskan, atau perkiraan saya.

**Cara membaca:**
- Setiap `[KF-xx]`, `[KN-xx]`, dan `[Langkah n]` adalah tautan ke baris di [mvp-t5.md](mvp-t5.md). Tautan memakai nomor baris, jadi bila mvp-t5 bertambah panjang, nomornya bergeser. Perbarui bila perlu.
- Persen adalah **bagian dari perkiraan waktu** (±950 menit dari tabel [B.3](mvp-t5.md#b3-ringkasan-urutan-dan-waktu)), bukan ukuran hasil. Angka waktunya sendiri perkiraan.

---

## 1. Gambaran: 14 langkah, 5 gerbang

| Langkah | Hasil | KF / KN | Tes penanda selesai | Waktu | Kumulatif |
|---|---|---|---|---|---|
| [1](#langkah-1-verifikasi-format-pii) ✅ | Format PII bersumber resmi | KF-07 sampai 09 (dasar) | Tiap angka punya sumber (cek dokumen) | 75 mnt | 8% |
| [2](#langkah-2-workflow-merah-dan-hijau) ✅ | Workflow merah lalu hijau | KF-22, KF-23 (kerangka) | Manual: tangkapan layar | 45 mnt | 13% |
| [3](#langkah-3-kerangka-cli) ✅ | `prism scan` + exit code | KF-01, KF-02 | pytest CLI | 60 mnt | 19% |
| [4](#langkah-4-telusuri-folder-dan-prefilter) | Telusur + prefilter | KF-03 sampai 06 | pytest folder sementara | 75 mnt | 27% |
| [5](#langkah-5-rule-nik-dengan-regex) | Deteksi NIK pertama | KF-07, awal KF-20 & 21 | pytest rule + CLI | 45 mnt | 32% |
| [6](#langkah-6-penilaian-bukti-nik) | Tingkat bukti NIK | KF-11, KF-10 | pytest tabel (`high`/`medium`/`low`) | 75 mnt | 39% |
| | **Gerbang 1: NIK end-to-end** | | | | |
| [7](#langkah-7-rule-hp-dan-email) | Rule HP dan email | KF-08, 09, 12, 13 | pytest tabel HP dan email | 75 mnt | 47% |
| [8](#langkah-8-konteks-ambang-dan-dedup) | Konteks, ambang, dedup | KF-14, 15, 16 | pytest tabel konteks, ambang, dedup | 75 mnt | 55% |
| [9](#langkah-9-laporan-dan-exit-code-final) | Teks, JSON, mask, exit code | KF-17 sampai 21, KN-04 sampai 06 | pytest mask, JSON, "nilai utuh tidak muncul", exit code | 75 mnt | 63% |
| | **Gerbang 2: MVP lokal selesai** | | | | |
| [10](#langkah-10-data-uji-sintetis-dan-label) | `data/synthetic/` + label | KF-25 | Skrip konsistensi data | 105 mnt | 74% |
| [11](#langkah-11-melengkapi-tes-otomatis) | `pytest` lengkap | KF-27 | Matriks KF → tes tanpa lubang | 60 mnt | 81% |
| | **Gerbang 3: data dan tes siap** | | | | |
| [12](#langkah-12-workflow-nyata) | Job CI merah dan hijau | KF-22 sampai 24, KN-01, KN-08 | Pindai lokal = perintah CI, lalu run nyata | 50 mnt | 86% |
| | **Gerbang 4: MVP CI selesai** | | | | |
| [13](#langkah-13-evaluasi) | Angka evaluasi | KF-26, KN-02, 03, 06 | Tes `evaluate.py` + ulang dua kali | 90 mnt | 95% |
| [14](#langkah-14-dokumentasi-dan-demo) | README dan bukti | Kriteria MVP [1.3](mvp-t5.md#13-kriteria-mvp-selesai) | Orang lain menjalankan dari README | 45 mnt | 100% |
| | **Gerbang 5: MVP selesai** | | | | |

⚠️ **Waktu langkah 10, 11, 13 belum sesuai dengan skema-evaluasi.** Tabel di atas mengikuti [B.3 mvp-t5](mvp-t5.md#b3-ringkasan-urutan-dan-waktu) (±950 menit, ±16 jam). Namun [skema-evaluasi.md](skema-evaluasi.md) bagian 6 memperinci ketiga langkah itu menjadi ±10,5–11 jam (minimum), bukan 255 menit. Dengan angka itu total sekitar **22–23 jam (minimum)**, dan persen kumulatif di kolom terakhir bergeser: langkah 1 sampai 9 menjadi sekitar 45% saja, bukan 63%. Putuskan angka mana yang dipakai sebelum persen ini dijadikan patokan.


---

## 2. Cara menguji progres

### 2.1 Tiga jenis tes

| Jenis | Isi | Dipakai di langkah |
|---|---|---|
| **Tes unit** (`pytest`) | Tabel `(teks, hasil yang diharapkan)` per rule, bergaya Presidio (). Termasuk contoh yang **tidak boleh** terdeteksi | 3 sampai 9 |
| **Tes CLI** (`pytest` + `subprocess`) | Menjalankan `python -m prism scan ...` sungguhan, memeriksa exit code, stdout, stderr | 3, 5, 9, 12 (lokal) |
| **Bukti manual** | Tangkapan layar job merah dan hijau di GitHub, README dijalankan orang lain | 2, 12, 14 |

Evaluasi (precision, recall, F1, FPR di langkah 13) **bukan** tes progres. Itu pembuktian klaim dan aturannya lebih ketat (bagian 2.3).

### 2.2 Aturan tes progres

1. **Tes ditulis bersamaan dengan langkahnya, bukan setelah semua kode selesai.** Di mvp-t5, tes baru dilengkapi di [Langkah 11](mvp-t5.md#L1196). Terlalu telat: bug di rule NIK baru ketahuan setelah HP, laporan, dan CI dibangun di atasnya. Langkah 11 menjadi **pelengkap dan pemeriksa celah**, bukan awal penulisan tes. Dicatat sebagai  (Usulan).
2. **Satu langkah selesai bila tes langkah itu hijau dan seluruh `pytest` lama tetap hijau.** Jalankan seluruhnya, bukan hanya tes baru, supaya tahu langkah baru tidak merusak yang lama.
3. **Tes ditulis dari tabel di SRS, bukan dari keluaran kodenya.** Bila tes disalin dari apa yang dikeluarkan program, tes pasti lulus walau programnya salah.
4. **Nilai uji sintetis boleh ditulis langsung di berkas tes** (folder `tests/` dikecualikan di CI, [KF-24](mvp-t5.md#L572)).
5. **`pytest` hanya alat pengembangan.** Ia bukan pustaka standar. Aturan "hanya pustaka standar" berlaku untuk kode PRISM di `src/`, jadi `pytest` boleh dipasang di mesin lokal, tetapi tidak boleh di-`import` dari `src/` dan tidak dipasang di workflow ([Langkah 11](mvp-t5.md#L1196) menyebut tes dijalankan lokal).
6. **Langkah gagal = jangan lanjut.** Perbaiki dulu. Keputusan baru yang muncul dicatat di [mvp-t5.md](mvp-t5.md) pada hari yang sama (satu-satunya sumber spesifikasi).

### 2.3 Batas antara tes progres dan evaluasi

Aturan beku : data uji dijalankan **sekali** setelah ambang dibekukan.

- Tes progres memakai **contoh kecil tulisan tangan** di dalam berkas tes. **Jangan** menjalankan PRISM pada `data/synthetic/` bagian `uji` sambil menyetel rule. Itu membuat data uji sudah "terlihat" dan klaim tidak sirkular hilang.
- Data kalibrasi (sepertiga berkas D1) boleh dipakai untuk menyetel di langkah 8 dan 13, tetapi **setelah** langkah 10.
- Tes lulus **tidak membuktikan rule benar**. Ia hanya membuktikan kode sesuai harapanmu. Apakah harapannya benar adalah urusan sumber resmi ([Langkah 1](mvp-t5.md#L1052)) dan evaluasi.

### 2.4 Bila tes gagal

| Gejala | Tindakan |
|---|---|
| Tes baru gagal | Perbaiki kode. Bila ternyata **harapan** di SRS yang salah, ubah SRS **dan** catat di log (status "Diganti") |
| Tes lama gagal setelah langkah baru | Regresi. Perbaiki sebelum lanjut |
| Tes sulit ditulis | Biasanya tanda spesifikasi belum jelas. Putuskan dulu (lihat "Putuskan di sini" tiap langkah) |

---

## 3. Rincian per langkah

Format tiap langkah: **Kebutuhan** (KF/KN), **Tes progres**, **Selesai bila**, **Putuskan di sini** (butir terbuka dari [5.2](mvp-t5.md#52-hal-yang-belum-diputuskan-atau-diuji) yang paling pas diputuskan saat sampai di langkah ini).

### Fase A. Persiapan

#### Langkah 1. Verifikasi format PII
[Langkah 1](mvp-t5.md#L1052) · ±75 mnt · kumulatif 8%

**Status: ✅ selesai 24 Nov 2026.** Sisa ⚠️ di dokumen format PII tidak menghalangi (batas panjang HP, keputusan wilayah setelah 2025).

- **Kebutuhan:** dasar [KF-07](mvp-t5.md#L432), [KF-08](mvp-t5.md#L433), [KF-09](mvp-t5.md#L434).
- **Tes progres:** bukan kode. Ceklis dokumen [format-pii-indonesia.md](../research/format-pii-indonesia.md):
  - setiap angka dan aturan punya sumber bernomor di [referensi.md](../research/referensi.md)
  - ada contoh sintetis valid **dan** tidak valid untuk NIK, HP, email
  - daftar provinsi di dokumen sama dengan `data/reference/kode-wilayah/provinsi.csv` (38 kode)
- **Selesai bila:** ceklis terpenuhi.
- **Sudah dicek (24 Nov 2026), hasilnya di [mvp-t5.md](mvp-t5.md):** PP 40/2019 Pasal 31 ayat (2) tidak menyebut pemisah (bagian [5.2](mvp-t5.md#52-hal-yang-belum-diputuskan-atau-diuji)). Permenkominfo 14/2018 hanya memuat struktur NDC `08XY`, bukan tabel per operator (rincian di [KF-08, pola regex](mvp-t5.md#b-pencarian-kandidat)). Batas panjang HP tetap hipotesis dari libphonenumber.
- ⚠️ Dokumen sudah ada di `docs/research/`. Sisa pekerjaannya hanya butir di atas, jadi langkah ini bisa lebih singkat dari 75 menit.

#### Langkah 2. Workflow merah dan hijau
[Langkah 2](mvp-t5.md#L1066) · ±45 mnt · kumulatif 13%

**Status: ✅ selesai 24 Nov 2026.** Merah dan hijau sudah terlihat, tangkapan layar diambil.

- **Kebutuhan:** kerangka [KF-22](mvp-t5.md#L570), [KF-23](mvp-t5.md#L571).
- **Tes progres (manual):**

| Tes | Lulus bila |
|---|---|
| Push dengan `exit 1` | Job merah di tab Actions |
| Ganti ke `exit 0`, push | Job hijau |
| Lihat riwayat commit | Commit tetap masuk walau job merah |
| Tanya diri sendiri: "apa yang membuat job merah?" | Jawab: exit code selain 0 |

- **Selesai bila:** dua tangkapan layar (merah, hijau) tersimpan.
- **Putuskan di sini:** apakah *required status checks* aktif sehingga merge PR benar-benar terblokir ([5.2](mvp-t5.md#52-hal-yang-belum-diputuskan-atau-diuji), perlu dicek ke dokumentasi GitHub).

### Fase B. CLI inti

#### Langkah 3. Kerangka CLI
[Langkah 3](mvp-t5.md#L1082) · ±60 mnt · kumulatif 19%

**Status: ✅ selesai 24 Nov 2026.** 9 tes hijau di Python 3.13 (`.venv`). Jalankan: `PYTHONPATH=src .venv/bin/python -m pytest -q`.

- **Kebutuhan:** [KF-01](mvp-t5.md#L421), [KF-02](mvp-t5.md#L422), [KN-08](mvp-t5.md#L739).
- **Tes progres** (`tests/test_cli.py`):

| Tes | Lulus bila |
|---|---|
| `scan <berkas ada>` | exit 0, mencetak jumlah baris |
| `scan <path tidak ada>` | exit 2, pesan di **stderr**, stdout kosong |
| `scan` tanpa argumen | exit 2 (kesalahan argumen `argparse`) |
| `python --version` di lokal | 3.13 (sama dengan CI, KN-08) |

- **Selesai bila:** `pytest` hijau dan `PYTHONPATH=src python -m prism scan sample.txt; echo $?` mencetak 0.
- **Sudah dikerjakan:** `pytest` dipasang di `.venv` (Python 3.13, folder `.venv` sudah diabaikan git). `python3` bawaan shell masih 3.9.6, jadi selalu pakai `.venv/bin/python`. Tes `test_python_yang_dipakai_adalah_3_13` sengaja gagal bila dijalankan dengan Python lain.

#### Langkah 4. Telusuri folder dan prefilter
[Langkah 4](mvp-t5.md#L1095) · ±75 mnt · kumulatif 27%

**Status: ✅ selesai 25 Nov 2026.** 44 tes hijau seluruhnya (`tests/test_scanner.py` baru). Keputusan: tepat 1.000.000 byte masih dipindai; symlink tidak diikuti (dihitung dilewati); `--exclude` dicocokkan sebagai path, bukan nama folder di mana saja; ringkasan mencetak lima angka (baris dibaca dan baris lolos prefilter dipisah); exit 2 bila ada berkas error.

- **Kebutuhan:** [KF-03](mvp-t5.md#L423), [KF-04](mvp-t5.md#L424), [KF-05](mvp-t5.md#L425), [KF-06](mvp-t5.md#L426).
- **Tes progres** (`tests/test_scanner.py` ⚠️ tidak ada di [B.1](mvp-t5.md#b1-struktur-file-target), tambahkan; memakai `tmp_path` pytest):

| Tes | Lulus bila |
|---|---|
| Folder dengan subfolder bersarang | Jumlah berkas diperiksa = hitungan manual |
| Ada folder `.git`, folder `--exclude` (diulang dua kali) | Isinya dilewati dan terhitung di "dilewati" |
| Berkas biner (ekstensi umum) dan berkas dengan byte nol | Dilewati |
| Berkas > 1 MB, dan tepat 1 MB | Yang di atas batas dilewati. Perilaku tepat di batas **ditetapkan dan diuji** |
| Berkas non-UTF-8 | Terbaca (`errors="replace"`), tidak error |
| Berkas tanpa izin baca | error = 1, pindai lanjut ke berkas lain |
| Prefilter: `0812-3456-7890`, `+62 812 3456 7890`, `01.234.567.8-901.000` | **Lolos** |
| Prefilter: baris tanpa digit ≥ 8 dan tanpa `@` | **Tidak lolos** |
| Prefilter: baris dengan `@` | Lolos |

- **Selesai bila:** angka ringkasan (diperiksa, dilewati, error, baris) sesuai hitungan manual pada folder uji kecil.
- **Putuskan di sini:** batas 1 MB (belum diuji, [5.2](mvp-t5.md#52-hal-yang-belum-diputuskan-atau-diuji)), dasar angkanya belum bersumber. Urutan berkas ditelusuri (`os.walk` urutannya tidak dijamin, **urutkan** supaya hasil bisa diulang, KN-06).
- **Batas yang diterima:** NIK di riwayat git tidak dipindai (hanya folder kerja).

#### Langkah 5. Rule NIK dengan regex
[Langkah 5](mvp-t5.md#L1111) · ±45 mnt · kumulatif 32%

**Status: ✅ selesai 25 Nov 2026.** 76 tes hijau seluruhnya. Keputusan: kolom mulai 1; huruf di sekitar 16 digit tidak menghalangi (hanya digit yang menolak); NIK berpemisah tidak terdeteksi (didokumentasikan lewat tes); `assess_nik` sementara `low` untuk semua. Penilaian bukti KF-11 baru di Langkah 6.

- **Kebutuhan:** [KF-07](mvp-t5.md#L432), awal [KF-20](mvp-t5.md#L550) dan [KF-21](mvp-t5.md#L551).
- **Tes progres** (`tests/test_rules.py`, `test_engine.py`, `test_cli.py`):

| Teks (sintetis) | Diharapkan |
|---|---|
| `3171011503900001` | 1 kandidat |
| 15 digit | 0 |
| 17 digit | 0 (diapit digit lain) |
| `3171 0115 0390 0001`, `3171-0115-0390-0001` | **0** (batasan NIK tanpa pemisah didokumentasikan lewat tes) |
| `abc3171011503900001` | ⚠️ tetapkan: `(?<!\d)` hanya melihat digit, huruf di depan tetap cocok. Tulis tesnya sesuai keputusan |
| Baris 3 kolom 10 | `berkas:3:10` benar (diperiksa angka, bukan hanya "ada") |
| `mask("3171011503900001")` | `************0001` |
| Berkas berisi 1 angka 16 digit | exit 1, nilai utuh **tidak** ada di stdout |
| Berkas bersih | exit 0 |

- **Selesai bila:** semua tes hijau, dan tes "nilai utuh tidak muncul" sudah ada sejak langkah ini.
- **Putuskan di sini:** kolom dihitung mulai 1 atau 0 (tetapkan sekali, dipakai di laporan, [3.2.2](mvp-t5.md#322-keluaran-teks-di-log-job)).

#### Langkah 6. Penilaian bukti NIK
[Langkah 6](mvp-t5.md#L1125) · ±75 mnt · kumulatif 39%

- **Kebutuhan:** [KF-11](mvp-t5.md#L445), [KF-10](mvp-t5.md#L435).
- **Tes progres** (`tests/test_rules.py`, tabel satu baris satu kasus):

| Teks (sintetis) | Diharapkan | Alasan |
|---|---|---|
| `3171011503900001` | `high` | Jakarta Pusat, Gambir, laki-laki |
| `3171015503900002` | `high` | Perempuan (hari 55 = 15 + 40) |
| `3171991503900001` | `medium` | Kecamatan 99 tidak ada |
| `4171011503900001` | `low` | Provinsi 41 tidak ada |
| `3171011513900001` | `low` | Bulan 13 |
| `1234567890123456` | `low` | Hanya 16 digit |
| Hari `00`, `32`, `72` | `low` | Di luar 01–31 dan 41–71 |
| 31 April, 30 Februari | `low` | Jumlah hari tidak sesuai bulan |
| 29 Februari | tidak ditolak | Tahun tidak dicek (KF-11) |
| NIK berawalan `99` | `low` | Belum ditangani, didokumentasikan lewat tes |
| NPWP orang pribadi (16 digit) | dilaporkan sebagai `nik` | KF-10 |

  Tambahan: jumlah kode di `provinsi.csv` = 38, `kecamatan.csv` = 7.285, dimuat **sekali** per pindai (bukan per baris).
- **Selesai bila:** semua baris tabel hijau, dan setiap contoh valid dicek **tangan** terhadap sumber resmi (bukan hanya terhadap kode).
- **Gerbang 1 (NIK end-to-end):** `prism scan` pada satu berkas berisi NIK sintetis mencetak lokasi, tingkat benar, nilai di-mask, exit 1. Ini titik aman pertama, dan kamu sudah bisa memperlihatkan sesuatu yang bekerja.
- **Batas yang diterima:** NIK asli dengan kode wilayah lama jatuh ke `medium` atau `low`.

### Gerbang 1 → lanjut ke HP dan email

#### Langkah 7. Rule HP dan email
[Langkah 7](mvp-t5.md#L1139) · ±75 mnt · kumulatif 47%

- **Kebutuhan:** [KF-08](mvp-t5.md#L433), [KF-09](mvp-t5.md#L434), [KF-12](mvp-t5.md#L464), [KF-13](mvp-t5.md#L473).
- **Tes progres:**

| Jenis | Tes | Diharapkan |
|---|---|---|
| HP | Enam bentuk [KF-08](mvp-t5.md#L433): `081234567890`, `81234567890`, `0812-3456-7890`, `812-3456-7890`, `+6281234567890`, `+62 812-3456-7890` | Semua terdeteksi sebagai kandidat |
| HP | Tingkat tiap baris [KF-12](mvp-t5.md#L464) | `+62…` dan `0` berpemisah `high`; `08…`/`62…` polos `medium`; `812-3456-7890` `medium`; `81234567890` `low` |
| HP | Pengecoh: 7 digit, 14 digit, digit kedua `0`, diapit digit lain | 0 kandidat |
| Email | Bentuk sah, local-part 65 karakter, TLD 1 huruf | Sah terdeteksi, dua lainnya tidak |
| Email | `budi@gmail.com` | `medium` |
| Email | `budi@example.com`, `git@github.com:user/repo.git`, `info@pt-abc.co.id` | `low` |
| Email | Daftar domain dibaca dari **berkas data** di `data/reference/` | Menambah satu domain di berkas mengubah hasil **tanpa** mengubah kode |

- **Selesai bila:** satu berkas uji berisi ketiga jenis terdeteksi dengan jenis dan tingkat benar, dan seluruh `pytest` hijau.
- **Putuskan di sini:** pilihan (b)/(c) untuk `81234567890` polos (saat ini pilihan (a): tidak dilaporkan tanpa konteks). Tambahan domain pribadi dicatat di mvp-t5 (KF-13).
- ⚠️ Tingkat HP dan email adalah **hipotesis** (disetujui 24 Nov). Jangan mengubahnya berdasarkan intuisi di sini. Diuji di langkah 13.
- ⚠️ Bila HP dan email terasa menyita waktu, ingat urutan pemotongan di [B.3](mvp-t5.md#b3-ringkasan-urutan-dan-waktu): langkah 1 sampai 6, 9, 12 dulu.

#### Langkah 8. Konteks, ambang, dan dedup
[Langkah 8](mvp-t5.md#L1149) · ±75 mnt · kumulatif 55%

- **Kebutuhan:** [KF-14](mvp-t5.md#L482), [KF-15](mvp-t5.md#L483), [KF-16](mvp-t5.md#L484).
- **Tes progres** (`tests/test_engine.py`; tabel dari [KF-14 sampai KF-16](mvp-t5.md#L482)):

| Aspek | Tes | Diharapkan |
|---|---|---|
| Konteks | `nik: 3171011503900001` | `high` (sudah `high`, tetap) |
| Konteks | `nik: 1234567890123456` | `low` → `medium`, dilaporkan |
| Konteks | `ref: 1234567890123456` | `low`, dibuang, `suppressed_low` = 1 |
| Konteks | Kata `NIK` huruf besar | Tetap menaikkan (tanpa membedakan huruf) |
| Konteks | Kata 40 karakter dari kandidat, lalu 41 karakter | Batas ±40 diuji di kedua sisi |
| Ambang | Tiga kandidat A `high`, B `medium`, C `low` | `medium`: A, B (supp. 1). `low`: A, B, C (supp. 0). `high`: A (supp. 1) |
| Ambang | Hanya kandidat yang **dilaporkan** yang membuat exit 1 | Berkas berisi hanya `low` pada ambang bawaan → exit 0 |
| Dedup | `hp: 08123456789, email: budi@gmail.com` | 2 temuan (tidak beririsan) |
| Dedup | `kontak: 08123456789@gmail.com` | 1 temuan (email, lebih panjang) |
| Dedup | `kontak: +6281234567890@gmail.com` | HP menang (tingkat didahulukan) ⚠️ lihat apakah wajar |

- **Selesai bila:** semua baris hijau, dan urutan proses benar: penilaian bukti → konteks → ambang → dedup (tes yang gagal bila urutannya terbalik, misalnya ambang sebelum konteks).
- **Putuskan di sini:**
  - apakah konteks `email` berlaku untuk domain di luar daftar, 
  - apakah `medium` yang dibuang pada `--min-level high` ikut dihitung di ringkasan ([5.2](mvp-t5.md#52-hal-yang-belum-diputuskan-atau-diuji))
  - konteks per baris tidak menjangkau judul kolom CSV: cukup dicatat sebagai batasan, diukur di langkah 13
- ⚠️ Aturan "naik satu tingkat" dan ±40 karakter adalah hipotesis tanpa dasar teori. Tes di sini hanya memastikan **kode sesuai hipotesis**, bukan hipotesisnya benar.

#### Langkah 9. Laporan dan exit code final
[Langkah 9](mvp-t5.md#L1159) · ±75 mnt · kumulatif 63%

- **Kebutuhan:** [KF-17](mvp-t5.md#L547), [KF-18](mvp-t5.md#L548), [KF-19](mvp-t5.md#L549), [KF-20](mvp-t5.md#L550), [KF-21](mvp-t5.md#L551), [KN-04](mvp-t5.md#L735), [KN-05](mvp-t5.md#L736), [KN-06](mvp-t5.md#L737).
- **Tes progres** (`tests/test_report.py`, `test_cli.py`):

| Aspek | Tes | Diharapkan |
|---|---|---|
| Mask | `3171011503900001` | `************0001` |
| Mask | `081234567890` | `********7890` |
| Mask | `budi@example.com` | `****@example.com` |
| Mask | nilai ≤ 4 karakter | Semua `*` |
| Mask | email tanpa `@` | Memakai aturan NIK/HP |
| Teks | Satu temuan | Cocok pola `berkas:baris:kolom  rule  tingkat  nilai-mask`, lalu satu baris ringkasan |
| JSON | `--json --output x.json` | Kunci `schema_version`, `findings`, `scan` ada. Tiap temuan punya `level` (bukan `score`) |
| Ringkasan | Folder uji | Diperiksa, dilewati, error, baris, temuan per jenis, `suppressed_low` benar |
| **Nilai utuh** | Berkas berisi NIK, HP, email utuh | Nilai utuh **tidak** ada di stdout, stderr, JSON, maupun pesan error (termasuk error baca berkas) |
| Exit code | Bersih / ada temuan / error | 0 / 1 / 2 |
| Exit code | Ada temuan **dan** error | **2** (didahulukan) |
| Keterulangan | Dua kali jalan pada folder sama | Keluaran identik (urutan temuan tetap) |
| Tanpa jaringan | Cari `socket`, `urllib`, `http`, `requests` di `src/` | Tidak ada (KN-04) |

- **Selesai bila:** semua baris hijau.
- **Gerbang 2 (MVP lokal selesai):** `prism scan .` pada folder campuran memberi laporan yang benar dan aman. Ini titik aman kedua. Bila waktu habis, **berhenti di sini**, lalu lompat ke langkah 12 (urutan prioritas B.3), dan klaim MVP tetap berdiri.
- **Putuskan di sini:** perilaku `--json` tanpa `--output` ([5.2](mvp-t5.md#52-hal-yang-belum-diputuskan-atau-diuji)), urutan temuan di log (usulan: berkas, baris, kolom), rujukan untuk masking parsial.

### Fase C. Data uji dan tes

#### Langkah 10. Data uji sintetis dan label
[Langkah 10](mvp-t5.md#L1176) · ±105 mnt · kumulatif 74%

- **Kebutuhan:** [KF-25](mvp-t5.md#L578).
- **Tes progres** (skrip pemeriksa kecil, atau `tests/test_dataset.py`):

| Tes | Lulus bila |
|---|---|
| `assess_nik` pada semua NIK positif | Sama dengan `level_diharapkan` |
| Jumlah positif dan negatif | Tercatat |
| Kolom `ground_truth.csv` | `berkas, baris, jenis, label, level_diharapkan, asal_sampel, kata_konteks, jenis_berkas, split` ([skema-evaluasi](skema-evaluasi.md#kolom-ground_truthcsv)) |
| Pembagian `split` | **Per berkas**: tidak ada berkas yang punya baris di dua split |
| Tiap baris label | Menunjuk berkas dan baris yang ada |
| Data | Tidak ada NIK/HP/email asli. Generator buatan sendiri, bukan Faker (Faker tak punya NIK Indonesia) |

- **Selesai bila:** semua tes pemeriksa hijau dan angka positif/negatif tercatat.
- **Putuskan di sini:** bidang untuk tahap pertama. Sinkronkan mvp-t5 langkah 10 dan KF-25 dengan kolom baru. Kasus tulisan tangan D2 (30 kasus) **ditulis sebelum menjalankan PRISM padanya**, lihat [skema-evaluasi.md](skema-evaluasi.md) H2.
- Boleh dikerjakan **paralel** dengan langkah 7 sampai 9 ([B.3](mvp-t5.md#b3-ringkasan-urutan-dan-waktu)). Tapi data tetap tidak dipakai menyetel (bagian 2.3).

#### Langkah 11. Melengkapi tes otomatis
[Langkah 11](mvp-t5.md#L1196) · ±60 mnt · kumulatif 81%

- **Kebutuhan:** [KF-27](mvp-t5.md#L580).
- **Isi:** karena tes sudah ditulis tiap langkah, pekerjaannya **menutup lubang**, bukan menulis dari nol.
- **Tes progres:**

| Pemeriksaan | Lulus bila |
|---|---|
| **Matriks KF → tes** | Tiap KF-01 sampai KF-24 menunjuk paling sedikit satu tes. KF tanpa tes ditandai dan ditulis tesnya |
| Pengecoh (`fps`) | UUID, timestamp, nomor rekening, ID transaksi **tidak** terdeteksi (gaya Gitleaks/TruffleHog) |
| Bersih dari awal | `pytest` hijau di lingkungan baru (venv kosong, clone baru) |
| Keterulangan | `pytest` dijalankan dua kali, hasil sama |

- **Selesai bila:** `PYTHONPATH=src pytest` hijau dan matriks KF → tes tidak punya baris kosong.
- **Gerbang 3 (data dan tes siap):** kode, data, dan tes siap untuk dipasang ke CI dan dievaluasi.

### Fase D. CI

#### Langkah 12. Workflow nyata
[Langkah 12](mvp-t5.md#L1208) · ±50 mnt · kumulatif 86%

- **Kebutuhan:** [KF-22](mvp-t5.md#L570), [KF-23](mvp-t5.md#L571), [KF-24](mvp-t5.md#L572), [KN-01](mvp-t5.md#L732), [KN-08](mvp-t5.md#L739).
- **Tes progres:**

| Urutan | Tes | Lulus bila |
|---|---|---|
| 1 | **Lokal dulu**: jalankan perintah CI persis (`--exclude data/synthetic --exclude tests --exclude evaluation/results --json --output prism-report.json`) | exit 0. Dokumen di `docs/` yang memuat angka 16 digit tidak jadi temuan (tambah `--exclude docs` bila perlu) |
| 2 | Push berkas bersih | Job **hijau** |
| 3 | Cabang percobaan + satu berkas berisi NIK sintetis | Job **merah**, lokasi tampil di log, nilai di-mask, `prism-report.json` ada di artifact |
| 4 | Hapus berkas percobaan | Job **hijau** lagi |
| 5 | Versi Python di workflow | Sama dengan lokal (3.13) |
| 6 | Tangkapan layar merah dan hijau | Tersimpan sebagai bukti |

- **Selesai bila:** urutan 1 sampai 6 terpenuhi.
- **Gerbang 4 (MVP CI selesai):** kriteria MVP 1 sampai 5 dan 7 di [1.3](mvp-t5.md#13-kriteria-mvp-selesai) terpenuhi. Tinggal angka evaluasi dan dokumentasi.
- **Putuskan di sini:** pin versi `checkout`, `setup-python`, `upload-artifact` (cek dokumentasi resmi, [5.2](mvp-t5.md#52-hal-yang-belum-diputuskan-atau-diuji)). `if: always()` atau `if: failure()` untuk artifact. Aktifkan *required status checks* bila ingin merge benar-benar terblokir.
- **Batas yang diterima:** CI hanya mendeteksi. PII yang sudah di-push tetap ada di riwayat git ([5.1](mvp-t5.md#51-risiko-dan-penanganan)).

### Fase E. Evaluasi dan dokumentasi

#### Langkah 13. Evaluasi
[Langkah 13](mvp-t5.md#L1228) · ±90 mnt · kumulatif 95%

- **Kebutuhan:** [KF-26](mvp-t5.md#L579), [KN-02](mvp-t5.md#L733), [KN-03](mvp-t5.md#L734), [KN-06](mvp-t5.md#L737).
- Rincian jadwal H1 sampai H7 ada di [skema-evaluasi.md](skema-evaluasi.md) bagian 6. Langkah ini memadatkannya.
- **Tes progres:** yang diuji di sini adalah **skrip evaluasinya**, sebelum dipercaya.

| Tes | Lulus bila |
|---|---|
| `evaluate.py` pada contoh kecil dengan hasil hitungan tangan (TP, FP, FN diketahui) | Precision, recall, F1, FPR sama dengan hitungan tangan |
| Baseline `\d{16}` polos | Dijalankan pada data yang sama, sebagai pembanding |
| python-stdnum (hanya untuk evaluasi, tidak dipasang di PRISM) | Tiap selisih dengan `assess_nik` diperiksa: salah di PRISM, salah di stdnum, atau beda tahun wilayah |
| Evaluasi diulang dua kali | Angka **sama** (KN-06) |
| Waktu pindai | Tiga kali, laporkan median |

- **Urutan wajib:** kalibrasi → tulis keputusan → **bekukan** → jalankan data uji **sekali**.
- **Putuskan sebelum menjalankan data uji:** kriteria "hasil kurang" yang memicu perluasan ke banyak bidang. Bila ditulis setelah melihat hasil, kriterianya tidak sahih.
- **Selesai bila:** angka per ambang tersimpan di `evaluation/results/` dengan tanggal dan `--min-level`, plus jumlah sampel tiap sel.
- Bila waktu mepet, urutan pemotongan di [skema-evaluasi.md](skema-evaluasi.md) bagian 6: Presidio, lalu repo publik. **Jangan** potong pembagian kalibrasi-uji, baseline, D2, dan pytest.

#### Langkah 14. Dokumentasi dan demo
[Langkah 14](mvp-t5.md#L1243) · ±45 mnt · kumulatif 100%

- **Kebutuhan:** [kriteria MVP 1.3](mvp-t5.md#13-kriteria-mvp-selesai), [KN-05](mvp-t5.md#L736).
- **Tes progres (manual):**

| Tes | Lulus bila |
|---|---|
| Clone repo ke folder baru, ikuti README dari atas | Berhasil menjalankan `prism scan` **tanpa bertanya** |
| Orang lain mencoba (teman, bukan penulis) | Sama, atau catat bagian yang membingungkan |
| README memuat | Cara jalan lokal, cara kerja CI, contoh keluaran, batasan |
| Tangkapan layar merah dan hijau | Ada |

- **Gerbang 5 (MVP selesai):** semua baris tabel bagian 4 terpenuhi.

---

## 4. Kriteria MVP selesai → langkah dan bukti

Dari [1.3](mvp-t5.md#13-kriteria-mvp-selesai).

| No | MVP selesai bila | Langkah | Bukti |
|---|---|---|---|
| 1 | `prism scan` mendeteksi NIK, HP, email | 5, 6, 7 | `pytest` tabel rule hijau |
| 2 | Nilai PII tidak pernah utuh di laporan | 5, 9 | Tes "nilai utuh tidak muncul" |
| 3 | Exit code 0/1/2 benar | 3, 9 | Tes CLI tiga exit code |
| 4 | Workflow jalan, merah bila ada temuan | 2, 12 | Tangkapan layar |
| 5 | Laporan JSON jadi artifact | 9, 12 | Artifact di run CI |
| 6 | Data uji berlabel, metrik dan waktu tercatat | 10, 13 | `evaluation/results/` |
| 7 | Tes otomatis lulus | 3 sampai 11 | `PYTHONPATH=src pytest` hijau |

---

## 5. Di luar MVP tapi dibutuhkan sidang ⚠️

Tidak ada di mvp-t5, jadi belum punya langkah, K, atau tes. Muncul karena keluaran akhir adalah draf jurnal dan video 3 menit:

| Hal | Status | Yang perlu ditetapkan |
|---|---|---|
| Draf jurnal | Bahan ada di mvp-t5.md (keputusan, batasan, dan butir terbuka) | Template dan format dari dosen/kampus, kerangka bab |
| Video 3 menit | Belum ada rencana | Skenario: masalah → demo job merah lalu hijau → satu angka hasil. Siapkan rekaman cadangan, jangan bergantung pada demo langsung |
| Persiapan tanya-jawab | Belum ada | Daftar keterbatasan dari mvp-t5.md (NIK tanpa pemisah, kode wilayah lama, email per domain, hipotesis tanpa dasar) sebagai bahan jawaban |

---

## 6. Rangkuman: apa yang paling mungkin berubah

Bukan tanda rencana gagal. Ini bagian yang paling mungkin diputuskan ulang saat kode jalan, jadi **catat di log pada hari yang sama**.

| Langkah | Yang mungkin berubah | Dampak ke tes |
|---|---|---|
| 4 | Batas 1 MB, urutan telusur | Tes batas |
| 7 | Bentuk regex HP, tingkat HP tanpa awalan | Tabel HP |
| 8 | Konteks untuk email di luar daftar, hitungan `suppressed` | Tabel konteks, ambang |
| 9 | Perilaku `--json` tanpa `--output`, urutan temuan | Tes JSON, keterulangan |
| 10 | Kolom label, bidang pertama | Skrip pemeriksa data |

**Yang tidak boleh berubah diam-diam setelah data dibuat:** cakupan jenis data (NIK, HP, email per domain), dan aturan beku setelah data uji dijalankan.
