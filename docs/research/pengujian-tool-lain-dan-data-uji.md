# Cara tool lain menguji dirinya, dan data uji PII Indonesia

> Dibuat 18 Nov 2026 untuk memutuskan skema evaluasi PRISM: membuat repo sendiri atau memakai repo publik.
> Sumber ada di [referensi.md](referensi.md) bagian [59]–[75].
> ⚠️ = belum diverifikasi, belum dibaca langsung, atau kesimpulan saya sendiri.
> Pencarian terbatas: satu mesin pencari dan GitHub API. "Tidak ditemukan" berarti tidak ketemu di sini, bukan terbukti tidak ada.

## 1. Ringkasan

- Tool yang saya periksa (Gitleaks, TruffleHog, Presidio) menguji **aturan** dengan unit test berisi contoh yang harus terdeteksi dan contoh yang tidak boleh terdeteksi [60], [62]–[64]. Itu bukan pengukuran precision dan recall.
- Pengukuran precision dan recall muncul di dua tempat lain: dataset acuan dari repo publik yang dilabeli manual (SecretBench) [66], dan data sintetis berbasis templat (presidio-research) [59].
- **Tidak ada dataset atau repo publik berlabel untuk NIK atau NPWP Indonesia** yang saya temukan. Yang ada hanya generator, validator, dan dataset sintetis multibahasa yang tidak berfokus pada format Indonesia.
- Karena itu usulan tiga lapis (repo tiruan, kasus tulisan tangan, pindai repo publik untuk precision) tetap masuk akal, ditambah satu pembanding independen: python-stdnum [69].

## 2. Cara tool lain menguji

| Tool | Cara menguji | Bukti |
|---|---|---|
| **Gitleaks** | Tiap rule punya daftar contoh yang harus terdeteksi (`tps`) dan yang tidak (`fps`). Fungsi `Validate` menghentikan proses bila salah satu gagal. Contoh sebagian dibuat acak dengan pola rule, sebagian string tetap yang diberi komentar `gitleaks:allow` (keaslian string itu tidak diperiksa) | [62], [63] |
| **TruffleHog** | Dua lapis: unit test pola (satu contoh valid, satu tidak valid, dengan kata kunci) dan *integration test* yang memakai kredensial nyata dari penyimpanan rahasia. Dokumen kontributor melarang menaruh kredensial uji di kode | [64], [65] ⚠️ [65] dibaca sebagian |
| **Presidio (analyzer)** | Tes `pytest` per recognizer dalam satu tabel `(teks, jumlah temuan, posisi, skor)`. Contoh Aadhaar mencakup nomor valid dan tidak valid, pemisah spasi, tanda hubung, dan titik dua, serta nomor di tengah kalimat | [60] |
| **presidio-research** | Evaluasi terpisah. Data dibuat dari templat (`My name is {{name}}`) dan identitas palsu, lalu diberi tag otomatis. Pemisahan latih dan uji dilakukan per templat agar pola yang sama tidak bocor ke dua sisi, dan README menyebut cara ini hanya berlaku untuk data sintetis | [59] |
| **Betterleaks** | Fixture `[[rules.tests]]` dijalankan lewat `config check`. Sudah dicatat di [tool-betterleaks.md](tool-betterleaks.md) (riset sebelum sistem sitasi baru) | tidak dikutip ulang |
| **SecretBench** (dataset, bukan tool) | 818 repo GitHub dipilih dari 2,23 juta repo yang cocok dengan 761 pola. Kandidat diambil dengan TruffleHog dan Gitleaks (97.479), lalu dua orang melabeli tiap kandidat secara terpisah. Kesepakatan Cohen's Kappa 0,86, hasil 15.084 rahasia sungguhan. Keterbatasan yang ditulis: hanya GitHub | [66] |

**Yang bisa ditiru PRISM:**
- Tabel tes per rule berisi variasi pemisah seperti Presidio [60]. PRISM sekarang hanya mencari `\d{16}` (mvp-t5.md bagian 2.2 dan bagian 6 di format-pii-indonesia.md), jadi `3171 0115 0390 0001` dan `3171-0115-0390-0001` belum tertangkap.
- Satu contoh valid dan satu tidak valid per rule, plus fps eksplisit, seperti Gitleaks dan TruffleHog [62]–[64]. Ini sama dengan langkah 11 (tes otomatis).
- Pemisahan per templat seperti presidio-research [59]. Bila data sintetis dibuat dari templat, bagi data uji dan kalibrasi per templat atau per berkas, bukan per baris.
- Dua pelabel untuk repo publik seperti SecretBench [66], bila memungkinkan. Satu pelabel tetap boleh, dicatat sebagai keterbatasan.

**Yang tidak berlaku bagi PRISM:**
- *Integration test* dengan kredensial nyata [65]. PII tidak punya "kunci" yang bisa diverifikasi ke penyedia.

**Kesimpulan terbatas:** dari tiga tool yang saya baca kodenya, pengujian aturan berupa unit test, bukan metrik. Ini tidak berarti tool lain tidak punya evaluasi. Repo tool yang tidak saya baca tidak diperiksa.

⚠️ Pengamatan saya, bukan klaim [66]: kandidat SecretBench berasal dari dua tool, jadi rahasia yang lolos dari keduanya tidak ada di dataset. Dataset itu cocok untuk menilai false positive, tetapi lemah untuk mengukur recall. Hal yang sama berlaku bila PRISM memindai repo publik.

## 3. Repo dan data publik untuk PII Indonesia

### 3.1 Yang tidak ada

- **Presidio** tidak punya recognizer khusus Indonesia. Folder `country_specific` memuat: australia, canada, finland, germany, india, italy, korea, nigeria, philippines, poland, singapore, south_africa, spain, sweden, thai, turkey, uk, us [61]. ⚠️ Daftar ini tanpa pengecekan versi rilis.
- **Faker** tidak punya provider `ssn` untuk `id_ID` [70], dan di provider `person/id_ID` tidak ada kata `nik`. Jadi catatan di mvp-t5.md langkah 10, bahwa generator NIK perlu dibuat sendiri, **terkonfirmasi**.
- Tidak ada dataset NER Indonesia berlabel NIK atau NPWP. Hasil pencarian hanya menunjukkan korpus NER umum (IndoNLU dan sejenisnya) berlabel orang, tempat, dan organisasi. ⚠️ Hanya dari hasil pencarian, tidak dibaca.

### 3.2 Yang ada, dan batasnya

| Kandidat | Isi | Cocok untuk | Batas |
|---|---|---|---|
| **ai4privacy `pii-masking-openpii-1.5m`** [67], contoh kecilnya `nano-1k` [68] | Sintetis, 30 bahasa termasuk Indonesia. Label: IDCARDNUM, TAXNUM, TELEPHONENUM, EMAIL, dan lain-lain. CC-BY-4.0 menurut kartu dataset | Variasi penulisan nomor HP dan email di kalimat Indonesia. Teks pengecoh | Berupa kalimat, bukan berkas repo. Label bukan NIK atau NPWP (lihat di bawah). Cara label dibuat tidak dibaca |
| **python-stdnum** `id/nik.py` [69] (LGPL-2.1) | Validator NIK: 16 digit, pemisah ` -.` dibuang, tanggal lahir (hari mod 40), cek kode provinsi dan kab/kota (4 digit pertama) dari datanya sendiri. **Tidak ada checksum** | **Pembanding independen** untuk `assess_nik`. Karena kode wilayahnya dari sumber berbeda, cek ini tidak sirkular | Hanya sampai kab/kota, tidak sampai kecamatan. Daftar `loc.dat` tidak dibaca dan belum dibandingkan dengan Kepmendagri |
| **nusakit-api** [71] (MIT) | Validator dan generator dummy NIK, NPWP (15 dan 16 digit), dan HP | Membandingkan hasil generator dengan generator sendiri | Struktur angka generator tidak dijelaskan di README, kode tidak dibaca. Validasi hanya struktural |
| **indonesian-id-card-identification** [75] (tanpa lisensi) | API Flask yang menerima daftar NIK dari pemanggil, lalu memeriksa panjang 16, kode wilayah 6 digit, tanggal lahir (+40 perempuan), digit gender, dan 4 digit terakhir | Bahan banding desain: strukturnya sama dengan penilaian NIK PRISM | **Bukan pemindai** (tidak mencari NIK di teks). Tanpa lisensi sehingga kode dan CSV tidak boleh disalin. Ada dua cacat (bagian 3.4). Data wilayah tahun 2021, sumber tidak disebut |
| ⚠️ randktpkkv1 [72], nik-generator-id [73], pii-shield [74] | Generator NIK dan KK, validator NIK dan NPWP | - | Hanya dari hasil pencarian, tidak dibaca |

### 3.3 Hasil periksa contoh Indonesia di ai4privacy

Dari **30 baris** Indonesia di `nano-1k` [68]. Sampel sangat kecil, jangan digeneralisasi.

| Label | Isi contoh | Pengamatan |
|---|---|---|
| IDCARDNUM (10 nilai) | `KH9UF035EP`, `2E90BNX333` | Alfanumerik 10 karakter. **Bukan** bentuk NIK |
| TAXNUM (7 nilai) | `6116872611379991`, `1307532508769999` | 16 digit. Saya cek 6 dari 7 nilai ke daftar provinsi kita: 4 berkode provinsi valid, 2 (`90`, `37`) tidak. Keenamnya punya tanggal dan bulan wajar dan berakhiran `999x`. Nilai ketujuh tidak dicek |
| TELEPHONENUM (16 nilai) | `+62360.533 0057`, `+62.86-676 4371` | Banyak variasi pemisah |
| EMAIL (18 nilai) | `K@outlook.com`, `D2004@hotmail.com` | Domain umum |

Artinya: dataset ini tidak memodelkan NIK Indonesia secara tepat, dan label TAXNUM-nya bukan NPWP atau NIK yang valid. Ia tidak layak jadi ground truth NIK. Ia berguna untuk menguji kekokohan pada variasi HP dan email, serta sebagai teks pengecoh.

### 3.4 Hasil periksa indonesian-id-card-identification [75]

Dibaca 24 Nov 2026: README, `app.py`, `validator.py`, `helper.py`, dan tabel wilayah. Notebook tidak dibaca. Kode tidak dijalankan. Logika yang diuji ditulis ulang di skrip sendiri.

| Pengamatan | Isi |
|---|---|
| Jenis | API validasi. NIK dikirim pemanggil lewat POST `/api/nik`, bukan dicari di berkas. Tidak ada pemindaian teks, regex, atau integrasi CI |
| Pemeriksaan | Panjang = 16, 6 digit pertama ada di tabel wilayah, tanggal lahir sah (+400000 untuk perempuan), digit ke-7 antara 0–7, 4 digit terakhir. Umur harus ≥ 17 tahun agar dianggap sah |
| Cacat 1 | `checkDOB` mengubah 6 digit tanggal menjadi `int` sehingga nol di depan hilang. Hasil tulis ulang: `010190` terbaca 10-01-1990 dan `010100` terbaca 10-01-2000. Hari 01–09 terbaca salah |
| Cacat 2 | `checkComputerizedNumber` membandingkan `status` (bool) dengan `'0000'`, jadi selalu valid. Empat digit terakhir tidak pernah ditolak |
| Tabel wilayah | 6.983 kecamatan dan 33 provinsi. Punya PRISM: 7.285 dan 38. Kode sama: 6.332. Hanya di tabel mereka: 651. Hanya di PRISM: 953. Provinsi 65 dan 93–96 tidak ada di tabel mereka. Mana yang benar untuk NIK tertentu tidak diketahui ⚠️ |
| Lisensi | Tidak ada. Tanpa izin, kode dan CSV tidak boleh disalin |

Artinya: dua daftar kode wilayah dari waktu berbeda berselisih sekitar 9–13%. Itu menguatkan batasan di keputusan K-12 (NIK asli dengan kode wilayah lama). Repo ini tidak dipakai sebagai pembanding D3. python-stdnum [69] tetap pilihan utama.

## 4. Generate repo atau pakai repo publik

| Kriteria | Repo tiruan (generate) | Repo publik |
|---|---|---|
| Label pasti | Ya, karena dibuat sendiri | Tidak, harus dilabeli manual [66] |
| Recall bisa dihitung | Ya | **Tidak** ⚠️ (lihat pengamatan di bagian 2) |
| Precision bisa dihitung | Ya, tapi bisa terlalu bagus karena sirkular | **Ya**, lewat pemeriksaan temuan satu per satu |
| Realistis | Tergantung seberapa baik dibuat | Ya |
| Ada PII Indonesia | Ya, sintetis | Tidak diketahui, kemungkinan jarang ⚠️ |
| Risiko data asli | Tidak ada | Mungkin menemukan data asli orang. PRISM sudah menyamarkan nilai, laporan sebaiknya hanya jumlah dan jenis |

**Usulan:** gabungkan, bukan pilih salah satu.

1. **Generate** untuk recall, FPR, dan keterulangan. Buat NIK dengan generator sendiri (tidak ada di Faker [70]).
2. **Tulisan tangan** 30–50 kasus sulit, termasuk variasi pemisah seperti tes Presidio [60].
3. **Pembanding independen:** jalankan python-stdnum [69] pada semua NIK yang diuji, lalu hitung selisihnya dengan `assess_nik`. Selisih menunjukkan salah satu dari dua implementasi keliru, dan itu bahan yang kuat untuk dibahas.
4. **Repo publik** hanya untuk precision di dunia nyata. Pilih repo yang berpotensi memuat angka 16 digit (log, data, dump), dan periksa temuan satu per satu.
5. **Data ai4privacy** [67] opsional, sebagai uji variasi HP dan email di teks bahasa Indonesia.

## 5. Belum diketahui

- Isi `loc.dat` python-stdnum dibandingkan dengan Kepmendagri 2430/2025 [1]. Bila daftarnya lama, selisih dengan PRISM bisa berasal dari tahun daftar, bukan salah logika.
- Bagaimana label ai4privacy dibuat dan seberapa representatif format Indonesia di seluruh 1,5 juta barisnya.
- Apakah ada repo publik yang memang memuat NIK sintetis atau uji Indonesia (misalnya tes dari proyek validator [73], [74]). Belum dibaca.
- Berapa repo publik yang cukup untuk memperkirakan precision. Perlu dasar statistik yang bisa dikutip.
- Venue SecretBench di MSR 2023 baru dari hasil pencarian [66].
