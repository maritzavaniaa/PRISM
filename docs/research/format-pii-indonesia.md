# Format PII Indonesia

> Keluaran langkah 1 di [mvp-t5.md](../planning/mvp-t5.md). **Fokus MVP: NIK (termasuk NPWP orang pribadi dan nomor KK), nomor HP, dan email.**
> Bagian yang diparkir ada di [format-pii-parkir.md](format-pii-parkir.md).
> Dasar hukum cakupan: [dasar-hukum-uu-pdp.md](dasar-hukum-uu-pdp.md). Semua sumber: [referensi.md](referensi.md).
> Data kode wilayah: [data/reference/kode-wilayah/](../../data/reference/kode-wilayah/README.md).
> ⚠️ = belum diverifikasi atau belum diuji. `[n]` = nomor sumber di referensi.md.
> **Diperbarui:** 12 Nov 2026.

## 1. Ringkasan

### 1.1 Jenis data dan statusnya

| Jenis | Bentuk | Status | Bagian |
|---|---|---|---|
| **NIK** (juga NPWP orang pribadi dan nomor KK) | 16 digit | Selesai. Tingkat bukti sudah diputuskan | 2, 4, 5 |
| **Nomor HP** | `+62`, `62`, atau `0` lalu `8` | Selesai. Tingkat bukti diusulkan di mvp-t5.md langkah 7 | 6 |
| **Email** | `local@domain` | Selesai. Tingkat bukti diusulkan di mvp-t5.md langkah 7 | 7 |

Jenis lain (NPWP 15 digit, kartu kredit dan debit, rekening, paspor, dan sebagainya) ada di [format-pii-parkir.md](format-pii-parkir.md).

### 1.2 Keputusan yang sudah diambil

- **Label `nik` mencakup tiga jenis:** NIK, NPWP orang pribadi (sama dengan NIK), dan nomor KK. Ketiganya berbentuk sama dan tidak bisa dibedakan dari angkanya. Yang penting adalah terdeteksi sebagai PII.
- **Kode wilayah:** cukup memeriksa apakah 6 digit awal ada di daftar wilayah saat ini. NIK dengan kode lama yang tidak ada di daftar diterima sebagai batasan, tidak diukur.
- **Pemeriksaan tanggal tetap dipakai.** Tanggal lahir adalah data yang rawan, jadi format tanggal sah bersama kecamatan terdaftar menjadi syarat tingkat `high`.
- **Fokus MVP hanya NIK, HP, dan email.** Sisanya diparkir.

### 1.3 Tingkat bukti

Tidak ada skor angka. Tingkat mengurutkan bukti: makin kecil peluang lolos kebetulan, makin tinggi tingkatnya. Pada ambang bawaan hanya `medium` dan `high` yang dilaporkan. Kata konteks di baris yang sama menaikkan satu tingkat (hipotesis ⚠️). Rincian dan alasan ada di [mvp-t5.md](../planning/mvp-t5.md) bagian 4. Cara menghitung peluang kebetulan ada di Lampiran B.

## 2. NIK

### 2.1 Struktur

NIK terdiri dari 16 digit [5].

| Posisi | Isi | Keterangan |
|---|---|---|
| 1–2 | Kode provinsi | Tempat tinggal pada saat mendaftar |
| 3–4 | Kode kabupaten/kota | Idem |
| 5–6 | Kode kecamatan | Idem |
| 7–8 | Tanggal lahir (DD) | 01–31. **Perempuan: ditambah 40** (tanggal 10 menjadi 50) |
| 9–10 | Bulan lahir (MM) | 01–12 |
| 11–12 | Tahun lahir (YY) | 2 digit terakhir tahun lahir |
| 13–16 | Nomor urut | Nomor urut penerbitan NIK, diproses otomatis dengan SIAK |

**Sumber:**
- **Dasar hukum (resmi): PP 40/2019 Pasal 30–32 [5].** Dibaca langsung dari PDF BPK.
- [5] menulis "tempat tinggal **pada saat mendaftar**". Situs Disdukcapil Klaten [4] dan Kompas TV [3] menulis "tempat pertama kali didaftarkan". Bayi yang lahir di luar domisili memakai Dinas tempat domisili orang tua (Pasal 31 ayat 5). NIK tidak berubah saat pindah domisili (Pasal 30 ayat 2).
- Situs Klaten [4] dan Kompas TV [3] sejalan dengan [5] untuk struktur. Frasa "nomor urut mulai dari 0001" hanya ada di [4], tidak ada di [5], dan **tidak dipakai**.
- ⚠️ Kompas TV [3] memakai contoh `3602041211870001` dan menyebut 3602 sebagai Kabupaten Serang. Di daftar wilayah [1], [2], **3602 adalah Kabupaten Lebak dan 3604 adalah Kabupaten Serang**. Artikel media tidak cukup sebagai satu-satunya sumber.

### 2.2 Yang bisa dan tidak bisa diperiksa

| Bagian | Bisa dicek? | Cara |
|---|---|---|
| Provinsi | Ya | Ada di daftar 38 provinsi |
| Kabupaten/kota | Ya | Ada di daftar 514 kabupaten/kota |
| Kecamatan | Ya | Ada di daftar 7.285 kecamatan |
| Tanggal (DD) | Ya | 01–31, atau 41–71 untuk perempuan, sesuai jumlah hari bulan itu. 29 Februari diterima karena tahunnya tidak diketahui |
| Bulan (MM) | Ya | 01–12 |
| Tahun (YY) | Tidak | Dua digit, abad tidak diketahui |
| Nomor urut | Tidak | Tidak ada aturan di [5] |
| Checksum | **Tidak ada** | Tidak ada digit pemeriksa yang dikenal ⚠️ |

"Format sah" di dokumen ini berarti digit 7–12 bisa terbaca sebagai tanggal dan bulan. Itu bukan berarti tanggalnya benar milik seseorang.

### 2.3 Peluang lolos kebetulan dan tingkat bukti

Persentase di bawah adalah **peluang sebuah angka 16 digit acak lolos pemeriksaan**, dengan asumsi tiap digit merata dan bebas. Itu hanya gambaran, bukan peluang bahwa sebuah temuan benar-benar NIK. Cara menghitungnya ada di Lampiran B. Angka sebenarnya diukur di uji U5.

| Pemeriksaan | Kode valid | Lolos pada digit acak | Digabung dengan tanggal valid (7,3%) |
|---|---|---|---|
| Tanpa cek wilayah | - | 100% | 7,3% |
| Provinsi | 38 dari 100 | 38% | ±2,8% |
| Kabupaten/kota | 514 dari 10.000 | 5,14% | ±0,38% |
| Kecamatan | 7.285 dari 1.000.000 | 0,73% | ±0,053% |

| Tingkat | Syarat | Peluang kebetulan |
|---|---|---|
| `high` | Format sah **dan** kecamatan (6 digit pertama) terdaftar | ±0,053% |
| `medium` | Format sah dan provinsi terdaftar, kecamatan tidak ditemukan | ±2,73% |
| `low` | Selainnya, termasuk hanya 16 digit. Tidak dilaporkan | - |

- NIK asli dengan bulan atau hari salah menjadi `low`, walau kecamatannya terdaftar.
- NIK asli dengan kode wilayah lama jatuh ke `medium` bila provinsinya terdaftar. **Diterima sebagai batasan** (keputusan 12 Nov 2026).
- Nomor urut tidak dicek.

### 2.4 Contoh sintetis

Semua nilai rekaan. Tingkat dihitung tanpa kata konteks.

| NIK | Tingkat | Alasan |
|---|---|---|
| `3171011503900001` | `high` | Jakarta Pusat, Gambir, laki-laki, 15-03-90 |
| `3171015503900002` | `high` | Sama, perempuan (55 = 15 + 40) |
| `3171991503900001` | `medium` | Format sah dan provinsi terdaftar, kecamatan 99 tidak ada di Jakarta Pusat |
| `3171011513900001` | `low` | Kecamatan terdaftar, tetapi bulan 13 tidak sah |
| `3171013203900001` | `low` | Kecamatan terdaftar, tetapi hari 32 tidak sah |
| `3171010003900001` | `low` | Kecamatan terdaftar, tetapi hari 00 tidak sah |
| `4171011503900001` | `low` | Provinsi 41 tidak ada |
| `1234567890123456` | `low` | Hanya 16 digit |

## 3. Kode wilayah

### 3.1 Dasar hukum

Kode wilayah mengikuti Kepmendagri 300.2.2-2138 Tahun 2025, diubah oleh Kepmendagri 300.2.2-2430 Tahun 2025 (ditetapkan 23 Juni 2025) [1]. Perubahan itu hanya menyangkut lampiran Aceh dan Sumatera Utara. Dokumen [1] menyebut Permendagri 58 Tahun 2021 sebagai dasarnya.

### 3.2 Aturan penomoran (hasil pengamatan pada data [2])

| Tingkat | Bentuk | Pengamatan |
|---|---|---|
| Provinsi | 2 digit | 38 kode, dari 11 sampai 96, tidak berurutan penuh |
| Kabupaten/kota | 4 digit | Kabupaten bernomor **01 sampai 29**, kota **71 sampai 79**, di setiap provinsi |
| Kecamatan | 6 digit | Nomor urut kecamatan di dalam kabupaten/kota |

- Contoh: `3171` = Kota Administrasi Jakarta Pusat, `317101` = Gambir. Urutan Jakarta: 3171 Pusat, 3172 Utara, 3173 Barat, 3174 Selatan, 3175 Timur.
- Sebuah paket pihak ketiga menyatakan kabupaten 01–69 dan kota 71–99. Itu belum diverifikasi, data memakai rentang yang lebih sempit.

### 3.3 Berkas data dan tingkat kepercayaan

| Berkas | Isi |
|---|---|
| [provinsi.csv](../../data/reference/kode-wilayah/provinsi.csv) | 38 baris |
| [kabkota.csv](../../data/reference/kode-wilayah/kabkota.csv) | 514 baris |
| [kecamatan.csv](../../data/reference/kode-wilayah/kecamatan.csv) | 7.285 baris |

- **Terverifikasi** ke dokumen resmi [1]: 38 kode provinsi, serta jumlah kabupaten, kota, dan kecamatan per provinsi (Lampiran A).
- **Belum** terverifikasi satu per satu: kode dan nama kabupaten/kota/kecamatan. Lampiran B dan C Kepmendagri 2138 tidak diperoleh.
- ⚠️ Belum dicek apakah ada keputusan yang lebih baru dari 2025. Daftar diperbarui bila ada keputusan baru.

## 4. NPWP orang pribadi

### 4.1 Dasar hukum

Semua peraturan di bawah dibaca langsung dari sumber resmi.

| Aturan | Isi yang relevan |
|---|---|
| PMK 112/PMK.03/2022, ditetapkan 8 Juli 2022 [6] | Mulai 14 Juli 2022, orang pribadi penduduk memakai **NIK** sebagai NPWP (Pasal 2 ayat 1 huruf a). Bagi yang sudah punya NPWP 15 digit, versi 16 digit dibuat dengan menambahkan angka `0` di depan (Pasal 7 ayat 2) |
| PMK 136/2023, berlaku 12 Des. 2023 [7] | Mengubah batas transisi dari 31 Des. 2023 menjadi **30 Juni 2024** (Pasal 2 ayat 6 dan Pasal 6, 9, 10). Mulai **1 Juli 2024**, NIK dan NPWP 16 digit dipakai di semua layanan DJP dan pihak lain (Pasal 11 ayat 1). Dokumen yang mencantumkan NPWP 15 digit dan terbit sebelum 1 Juli 2024 **tetap berlaku** (Pasal 13) |
| PMK 81/2024, berlaku 1 Jan. 2025 [8] | Pasal 16 ayat 2: NPWP orang pribadi penduduk = NIK yang diaktivasi. Tidak mencabut PMK 112 dan 136 |

### 4.2 Akibat untuk PRISM

- NPWP orang pribadi yang berstatus penduduk adalah **NIK** [6] Pasal 2, [8] Pasal 16. Jadi ia dideteksi oleh rule NIK dan tidak bisa dibedakan dari NIK. Yang penting ia terdeteksi sebagai PII.
- Format NPWP lama 15 digit, NPWP badan, dan kasus kebocoran NPWP ada di [format-pii-parkir.md](format-pii-parkir.md).

## 5. Nomor Kartu Keluarga (KK)

### 5.1 Struktur (hanya dari aturan daerah ⚠️)

| Posisi | Isi | Keterangan |
|---|---|---|
| 1–2 | Kode provinsi | Contoh di aturan Gresik: 35 (Jawa Timur) |
| 3–4 | Kode kabupaten/kota | Contoh: 25 (Kabupaten Gresik) |
| 5–6 | Kode kecamatan | - |
| 7–8 | Hari **perekaman** data KK | Bukan tanggal lahir. Tidak ada tambahan 40 |
| 9–10 | Bulan perekaman | - |
| 11–12 | 2 digit terakhir tahun perekaman | - |
| 13–16 | Urutan proses perekaman KK pada wilayah dan tanggal yang sama | Teks menulis "digit terakhir" (tunggal) tanpa posisi. Empat digit disimpulkan dari total 16 ⚠️ |

- Sumber: Perbup Gresik 32/2016 Pasal 11 [14] dan 51/2013 Pasal 11 [21], isinya sama. Nomor KK diterbitkan terpusat oleh Dinas, setelah biodata kepala keluarga direkam di SIAK.
- **Aturan nasional belum ditemukan.** Sudah dicari: PP 40/2019 [5] (tidak ada struktur KK), Permendagri 19/2010 [24] (hanya formulir), Perbup Kebumen 15/2024 [22] dan Perda Bekasi 7/2011 [23] (menyebut nomor KK tanpa susunan digit). Kesamaan dengan daerah lain adalah asumsi.
- Perda Bekasi Pasal 46 ayat 1 huruf a mencantumkan Nomor KK sebagai Data Pribadi Penduduk yang harus dilindungi [23]. Itu aturan daerah dan mendukung KK dilaporkan sebagai PII.
- Nomor KK bisa berganti bila kepala keluarga pindah sendirian [22] Pasal 8 ⚠️ (halaman sumber belum ditinjau).

### 5.2 Beda dengan NIK

| Aspek | NIK | Nomor KK |
|---|---|---|
| 6 digit pertama | Wilayah tempat tinggal saat mendaftar | Kode wilayah, jenisnya sama |
| Digit 7–12 | Tanggal lahir, perempuan +40 | Tanggal perekaman data KK, tanpa +40 |
| Hari | 01–31 atau 41–71 | 01–31 |
| Digit 13–16 | Nomor urut penerbitan NIK | Urutan perekaman KK |

### 5.3 Akibat untuk PRISM

- Nomor KK dengan kecamatan terdaftar dan hari 01–31 memenuhi syarat `high` NIK. KK terdeteksi, menggagalkan job, dan berlabel `nik`.
- Hari 41–71 pasti bukan KK. Hari 01–31 bisa NIK laki-laki atau KK, tidak bisa dibedakan dari angkanya.
- **Keputusan:** tidak ada rule terpisah. Pembeda `nik` dan `kk` lewat kata konteks (`kk`, `kartu keluarga`) masuk tahap 2.
- Contoh sintetis: `3171010112200001` = Jakarta Pusat, Gambir, direkam 01-12-20. Hasil: `high`, berjenis `nik`.

### 5.4 Belum diketahui (⚠️)

- Aturan nasional untuk susunan nomor KK, dan apakah semua daerah sama.
- Posisi dan panjang bagian urutan secara resmi.
- Rentang tahun perekaman yang lazim. Tidak dijadikan aturan.

### 5.5 Apakah nomor KK bisa sama dengan NIK seseorang? (dicari 12 Nov. 2026)

**Tidak ditemukan kasus.** Tidak ada sumber yang menyebut nomor KK pernah sama dengan NIK seseorang, dan tidak ada sumber yang menyatakan sistem menjamin hal itu tidak akan terjadi.

| Sumber | Yang dikatakan | Keterbatasan |
|---|---|---|
| Dirjen Dukcapil Zudan Arif Fakrulloh, lewat detikNews 21 Okt. 2020 [43] | NIK tidak berubah saat pindah domisili, nomor KK bisa berganti saat pindah alamat atau perubahan status | Tidak membahas apakah keduanya bisa bernilai sama, dan tidak membahas keunikan atau pembentukan nomor KK |
| IndonesiaBaik.ID [44] | NIK permanen, nomor KK terikat rumah tangga dan alamat sehingga bisa berubah | Tanggal tidak tertera. Tidak menyatakan apakah keduanya bisa identik |
| Kompas TV, 19 Jan. 2024 [45] | NIK di KTP sama dengan NIK di KK. Nomor KK disebut "nomor unik yang sedikit berbeda dengan NIK masing-masing anggota keluarga" | Tidak mengutip pejabat untuk bagian KK. Kata "sedikit berbeda" bukan jaminan tidak pernah sama |

- **Yang perlu dibedakan:** NIK **di dalam** KK adalah NIK tiap anggota, sama dengan NIK di KTP-nya. Itu bukan nomor KK itu sendiri.
- **Dari struktur** (bagian 5.1 dan 5.2): keduanya 16 digit dengan susunan wilayah, tanggal, lalu nomor urut. Nomor KK dengan hari 01–31 secara bentuk bisa persis sama dengan NIK laki-laki. Apakah sistem mencegah bentrokan itu tidak diketahui ⚠️. Peluang kebetulannya sangat kecil karena tanggalnya berbeda arti (tanggal lahir dan tanggal perekaman), tetapi tidak saya hitung ⚠️.
- **Jangan tertukar dengan "NIK ganda".** Menurut ringkasan hasil pencarian (artikel tidak dibaca ⚠️), istilah itu berarti **satu orang** punya lebih dari satu NIK, bukan dua orang berbagi satu NIK. Dukcapil disebut menyatakan masalah itu sudah lama diselesaikan.
- **Dampak untuk PRISM: tidak ada.** Kalau sebuah nomor kebetulan sama dengan NIK seseorang, ia tetap PII dan tetap terdeteksi sebagai `nik`. Tidak perlu penanganan khusus.

## 6. Nomor HP

### 6.1 Yang ditetapkan peraturan (Permenkominfo 14/2018 [25])

- Nomor seluler internasional (MSISDN) = kode negara **62** + N(S)N-Mobil. N(S)N-Mobil = kode tujuan nasional (NDC) **3 digit** + nomor pelanggan (hlm. 37).
- NDC seluler dialokasikan pada kelompok nomor **A = 8**, bentuknya `8BC` (hlm. 38).
- Panjang nomor pelanggan diatur masing-masing penyelenggara, dengan batas panjang maksimum N(S)N-Mobil (hlm. 38).
- Batas dari ITU-T E.164: nomor internasional maksimum 15 digit, kode negara Indonesia 2 digit, jadi N(S)N sampai 13 digit (hlm. 19).
- **Tidak ditetapkan:** jumlah digit nomor pelanggan yang pasti dan prefiks per operator. Alokasi NDC per operator belum saya baca ⚠️ dan bisa berubah.

Ikhtisar Peruntukan Nomor [25] (hlm. 40 dokumen):

| Kombinasi | Peruntukan |
|---|---|
| `0` | Prefiks nasional |
| `08XY` | NDC jaringan. X ≠ 0 dan 6, Y = 0–9 |
| `086X` | NDC jaringan. X ≠ 1 |
| `0800` sampai `0809` | Layanan Intelligent Network. `0804` biaya terbagi, `0809` premium. `0801`–`0803` dan `0805` belum dialokasikan |
| `08611XY`, `08612XY` | Kode akses jaringan data paket |

### 6.2 Pola teknis (metadata libphonenumber [26], bukan sumber pemerintah)

| Hal | Isi |
|---|---|
| Kode negara dan prefiks nasional | 62 dan 0 |
| Pola seluler (tanpa 0 di depan) | `8[1-35-9]\d{7,10}`, panjang **9–12 digit** |
| Pola tampilan | `812-3456-7890` (3-4-4), variasi 3-3-3 dan 3-4-5 |
| Bukan nomor pribadi | 804 (biaya terbagi) dan 809 (premium) |

- **Cocok dengan [25]:** 804 dan 809 memang bukan nomor seluler pribadi.
- **Berbeda dengan [25]:** peraturan mengizinkan NDC `084Y`, metadata mengecualikan 84. Karena PRISM alat privasi (melewatkan nomor lebih buruk daripada satu temuan palsu), MVP mengikuti peraturan: digit kedua `1`–`9`.

### 6.3 Bentuk yang perlu dikenali PRISM

| Bentuk | Contoh | Panjang digit |
|---|---|---|
| Nasional | `0812-3456-7890`, `081234567890` | 10–13 (0 + 9–12) |
| Internasional dengan `+` | `+62 812-3456-7890` | 11–14 setelah `+` |
| Internasional tanpa `+` | `6281234567890` | 11–14 |
| Tanpa angka nol (nol hilang di spreadsheet) | `81234567890` | **Terlalu ambigu, tidak dideteksi** |
| Kesalahan penulisan umum ⚠️ | `+62 0812 ...` | Perlu diputuskan |

- Pemisah yang lazim: spasi, strip, titik, tanda kurung. Daftar ini disusun dari [25], [26], dan pola Faker [27], **bukan dari statistik database Indonesia** (tidak ditemukan sumber yang dapat dipercaya).
- Rule MVP: `(?:\+62|62|0)8[1-9]\d{7,10}`.
- Nomor telepon tetap (`(021) 1234 5678`) tidak dicakup. UU PDP menyebut nomor telepon **seluler** [31].

### 6.4 Status sebagai data pribadi

- Disebut eksplisit di UU PDP [31].
- NIST [35] hlm. 14: "Telephone numbers, including mobile, business, and personal numbers". NIST hlm. 17: nomor kantor yang sengaja dipublikasikan tidak perlu dilindungi. Jadi kecocokan pola belum tentu kebocoran, dan pembedanya konteks.

### 6.5 Data uji dan hal yang belum diketahui

- Pola Faker id_ID [27] tidak cocok untuk data uji HP. Beberapa polanya (`+62-0##-###-####`, `08# ### ####`) bisa menghasilkan nomor yang tidak sah menurut [26]. Buat generator sendiri.
- ⚠️ Isi tabel alokasi NDC per operator [25] dan status perubahannya sesudah 2018.
- ⚠️ Panjang nomor pelanggan resmi. Batas atasnya mungkin lebih ketat daripada 13 digit.
- ⚠️ Sebaran bentuk HP di database nyata Indonesia.

## 7. Email

### 7.1 Aturan baku

- Bentuk `local-part "@" domain` (RFC 5322 bagian 3.4.1 [29]). Local-part berupa `dot-atom` atau `quoted-string`.
- Karakter `atext` di `dot-atom`: huruf, angka, dan `! # $ % & ' * + - / = ? ^ _ \` { | } ~` (RFC 5322 bagian 3.2.3 [29]). Titik hanya di antara dua karakter `atext`.
- Domain berupa `dot-atom` atau `domain-literal` (alamat IP dalam kurung siku).
- Batas panjang (RFC 5321 bagian 4.5.3.1 [28]): local-part **64 oktet**, domain **255 oktet**, alamat lengkap dengan tanda pemisah **256 oktet**.
- Domain yang dicadangkan untuk contoh dan uji (RFC 2606 [30]): `.test`, `.example`, `.invalid`, `.localhost`, serta `example.com`, `example.net`, `example.org`.

### 7.2 Format khusus Indonesia

- Tidak ada sintaks email khusus Indonesia yang ditemukan. Yang khas hanya akhiran domain (`.id`, `.co.id`, `.ac.id`, `.go.id`, `.sch.id`). Daftar resmi domain tingkat kedua `.id` tidak ditemukan, jadi **tidak dipakai**. Rule generik tidak bergantung pada akhiran.
- Statistik domain email yang paling sering di database Indonesia tidak ditemukan dari sumber yang dapat dipercaya, dan tidak diperlukan.

### 7.3 Usulan pola MVP (subset praktis, bukan seluruh RFC)

- Local-part: huruf, angka, dan `. _ % + -`, titik tidak di awal, akhir, atau berurutan, maksimum 64 karakter.
- Domain: label huruf, angka, atau strip yang dipisah titik, minimal satu titik, TLD minimal 2 huruf, maksimum 255 karakter.
- Tidak didukung (batasan): `quoted-string`, `domain-literal`, karakter `! # $ & ' * / = ? ^ \` { | } ~` di local-part, dan domain internasional (IDN).
- Sumber temuan palsu yang perlu diuji ⚠️: alamat SSH `git@github.com:user/repo.git`.

### 7.4 Status sebagai data pribadi dan usulan tingkat rendah

- **UU PDP [31] tidak menyebut email.** Beberapa tulisan sekunder menyatakan UU "secara tegas" memuat email. Itu **tidak cocok** dengan teks resmi ⚠️, jangan dikutip.
- NIST [35] hlm. 14: contoh PII mencakup "Address information, such as street address or email address".
- European Commission [36]: `name.surname@company.com` adalah data pribadi, `info@company.com` **bukan**.
- **Usulan tingkat `low` (hipotesis ⚠️):** (1) domain yang dicadangkan RFC 2606, (2) local-part berupa nama peran generik (`info`, `admin`, `support`, `noreply`, `contact`, `sales`). Daftar nama peran saya susun sendiri, tidak bersumber.
- Sumber Indonesia yang menyebut email sebagai data pribadi tidak ditemukan. Permenkominfo 20/2016 tidak dibaca.

### 7.5 Belum diketahui (⚠️)

- Seberapa sering alamat SSH, pengenal paket, dan contoh dokumentasi cocok dengan pola di repo nyata.
- Apakah email milik badan (`info@perusahaan.co.id`) perlu dilaporkan. UU PDP melindungi orang perseorangan, jadi belum tentu.

## 8. Kekurangan riset yang masih penting untuk MVP

| No | Kekurangan | Mengapa penting | Cara mengisinya |
|---|---|---|---|
| 1 | **Bentuk NIK di berkas nyata.** Regex hanya `\d{16}` | NIK yang ditulis `3171 0115 0390 0001`, `3171-0115-0390-0001`, atau dari ekspor spreadsheet tidak ketangkap. Dugaan: spreadsheet hanya menyimpan 15 digit signifikan sehingga digit terakhir bisa `0` ⚠️ | Cari contoh bentuk di ekspor Excel, Google Sheets, JSON. Putuskan pemisah yang ditoleransi |
| 2 | **Peluang angka biasa lolos tiap tingkat.** Angka di bagian 2.3 mengandaikan digit acak merata | Angka asli di repo (timestamp, ID) tidak merata. Menentukan apakah `medium` aman dilaporkan bawaan | Pindai beberapa repo publik, hitung berapa angka 16 digit yang lolos tiap tingkat |
| 3 | **Aturan "kata konteks menaikkan satu tingkat" tidak punya dasar** | Ia yang mengubah `low` menjadi `medium` sehingga dilaporkan | Diukur di uji U5 dengan dan tanpa aturan ini |

## Lampiran A. Daftar provinsi

Kode dan jumlah dibaca dari tabel resmi "A. Rekapitulasi" di lampiran Kepmendagri 2430/2025 [1], lalu dicocokkan dengan data [2].

| Kode | Provinsi | Kabupaten | Kota | Kecamatan |
|---|---|---|---|---|
| 11 | Aceh | 18 | 5 | 290 |
| 12 | Sumatera Utara | 25 | 8 | 455 |
| 13 | Sumatera Barat | 12 | 7 | 179 |
| 14 | Riau | 10 | 2 | 172 |
| 15 | Jambi | 9 | 2 | 144 |
| 16 | Sumatera Selatan | 13 | 4 | 241 |
| 17 | Bengkulu | 9 | 1 | 129 |
| 18 | Lampung | 13 | 2 | 229 |
| 19 | Kepulauan Bangka Belitung | 6 | 1 | 47 |
| 21 | Kepulauan Riau | 5 | 2 | 80 |
| 31 | Daerah Khusus Ibukota Jakarta | 1 | 5 | 44 |
| 32 | Jawa Barat | 18 | 9 | 627 |
| 33 | Jawa Tengah | 29 | 6 | 576 |
| 34 | Daerah Istimewa Yogyakarta | 4 | 1 | 78 |
| 35 | Jawa Timur | 29 | 9 | 666 |
| 36 | Banten | 4 | 4 | 155 |
| 51 | Bali | 8 | 1 | 57 |
| 52 | Nusa Tenggara Barat | 8 | 2 | 117 |
| 53 | Nusa Tenggara Timur | 21 | 1 | 315 |
| 61 | Kalimantan Barat | 12 | 2 | 174 |
| 62 | Kalimantan Tengah | 13 | 1 | 136 |
| 63 | Kalimantan Selatan | 11 | 2 | 156 |
| 64 | Kalimantan Timur | 7 | 3 | 105 |
| 65 | Kalimantan Utara | 4 | 1 | 55 |
| 71 | Sulawesi Utara | 11 | 4 | 171 |
| 72 | Sulawesi Tengah | 12 | 1 | 177 |
| 73 | Sulawesi Selatan | 21 | 3 | 313 |
| 74 | Sulawesi Tenggara | 15 | 2 | 221 |
| 75 | Gorontalo | 5 | 1 | 77 |
| 76 | Sulawesi Barat | 6 | 0 | 69 |
| 81 | Maluku | 9 | 2 | 119 |
| 82 | Maluku Utara | 8 | 2 | 118 |
| 91 | Papua | 8 | 1 | 105 |
| 92 | Papua Barat | 7 | 0 | 91 |
| 93 | Papua Selatan | 4 | 0 | 82 |
| 94 | Papua Tengah | 8 | 0 | 131 |
| 95 | Papua Pegunungan | 8 | 0 | 252 |
| 96 | Papua Barat Daya | 5 | 1 | 132 |
| | **Total** | **416** | **98** | **7.285** |

## Lampiran B. Cara menghitung peluang lolos kebetulan

### B.1 Apa yang dihitung dan asumsinya

- **Yang dihitung:** peluang sebuah angka yang **dibuat acak** lolos suatu pemeriksaan. Ini laju temuan palsu bila PRISM bertemu angka acak. Ia **bukan** peluang bahwa sebuah temuan benar-benar NIK (itu bergantung pada seberapa sering NIK asli ada di repo, yang tidak kita ketahui).
- **Model acak (asumsi):** tiap digit 0–9 muncul dengan peluang sama, 1/10, dan tiap digit tidak memengaruhi digit lain.
- Asumsi itu **tidak berlaku di data nyata**. Timestamp, ID, dan nomor urut punya sebaran digit yang miring (misalnya banyak yang berawalan `1`). Karena itu angka di sini dipakai untuk **membandingkan kekuatan bukti antar pemeriksaan**, bukan sebagai laju temuan palsu sebenarnya. Laju sebenarnya diukur di uji U5 (kekurangan riset nomor 2).

### B.2 Tiga rumus yang dipakai [42]

| Rumus | Bunyi | Sumber di [42] |
|---|---|---|
| **Peluang klasik (distribusi seragam)** | Bila semua hasil sama mungkin, peluang kejadian A = banyak hasil di A dibagi banyak semua hasil: P(A) = \|A\| / \|Ω\| | Definisi 1.3 |
| **Aturan kali untuk kejadian bebas** | Bila A dan B bebas, P(A dan B) = P(A) × P(B) | Teorema 4.1 |
| **Komplemen dan himpunan bagian** | P(bukan A) = 1 − P(A). Bila B termasuk di dalam A, P(A tetapi bukan B) = P(A) − P(B) | Teorema 1.1 (sifat peluang) |

### B.3 NIK

**Langkah 1. Peluang tiap pemeriksaan wilayah** (rumus peluang klasik: kode yang ada dibagi kode yang mungkin):

| Pemeriksaan | Kode yang ada [1], [2] | Kode yang mungkin | Peluang |
|---|---|---|---|
| Provinsi (2 digit) | 38 | 10² = 100 | 38/100 = **38%** |
| Kabupaten/kota (4 digit) | 514 | 10⁴ = 10.000 | 514/10.000 = **5,14%** |
| Kecamatan (6 digit) | 7.285 | 10⁶ = 1.000.000 | 7.285/1.000.000 = **0,7285%** |

Kode kecamatan sudah memuat kode provinsi dan kabupaten/kota di depannya, jadi 0,7285% **tidak** dikalikan lagi dengan 38% atau 5,14%.

**Langkah 2. Peluang tanggal sah** (digit 7–12, rumus peluang klasik):
- Kombinasi hari-dan-bulan yang mungkin = 100 (nilai hari 00–99) × 100 (nilai bulan 00–99) = 10.000.
- Kombinasi yang sah: tiap hari dalam setahun dihitung dua kali (laki-laki dan perempuan dengan tambahan 40). Jumlah hari = 31+29+31+30+31+30+31+31+30+31+30+31 = 366 (29 Februari ikut karena tahunnya tidak diketahui). 2 × 366 = **732**.
- Peluang = 732/10.000 = **7,32%**. Tahun (digit 11–12) bebas, tidak memengaruhi hasil.

**Langkah 3. Menggabungkan** (aturan kali, karena digit 1–6 dan digit 7–12 saling lepas):

| Pemeriksaan | Perhitungan | Hasil |
|---|---|---|
| Provinsi + tanggal | 38% × 7,32% | 2,78% |
| Kabupaten/kota + tanggal | 5,14% × 7,32% | 0,376% |
| Kecamatan + tanggal | 0,7285% × 7,32% | 0,0533% |

**Langkah 4. Tingkat bukti NIK:**

| Tingkat | Perhitungan | Hasil |
|---|---|---|
| `high` (tanggal sah dan kecamatan terdaftar) | 7,32% × 0,7285% | **0,0533%** |
| `medium` (tanggal sah dan provinsi terdaftar, kecamatan tidak) | 7,32% × (38% − 0,7285%) | **2,73%** |

Pada `medium`, pengurangan dipakai karena kode kecamatan yang terdaftar adalah bagian dari kode provinsi yang terdaftar (himpunan bagian).

**Pemeriksaan dengan simulasi** (12 Nov. 2026, 2.000.000 angka 16 digit acak, data wilayah dari [2]): tanggal sah 7,32%, `high` 0,054%, `medium` 2,73%. Cocok dengan rumus.

### B.4 Nomor HP

Peluang bahwa **sebuah angka digit-polos** dengan panjang yang sesuai memenuhi awalan HP, memakai aturan kali untuk digit yang bebas:

| Bentuk | Perhitungan | Hasil | Syarat panjang |
|---|---|---|---|
| `08` + digit 1–9 (nasional, polos) | 1/10 × 1/10 × 9/10 | **0,9%** | Angka 10–13 digit |
| `62` + `8` + digit 1–9 (internasional tanpa `+`, polos) | 1/10 × 1/10 × 1/10 × 9/10 | **0,09%** | Angka 11–14 digit |

- Hasil di atas **bersyarat**: berlaku untuk angka yang panjangnya sudah berada di jendela itu. Peluang sebuah angka acak kebetulan berpanjang segitu tidak dihitung karena bergantung pada data.
- Bentuk `+62` dan bentuk berpemisah (`0812-3456-7890`) **tidak dihitung**. Tanda `+` dan pemisah bukan digit, jadi model digit acak tidak berlaku. Alasan tingkat `high` untuk dua bentuk itu adalah penilaian, bukan hitungan ⚠️.


### B.5 Email

Tidak dihitung. Email bukan deretan digit, jadi model digit acak tidak berlaku. Tingkat `low` untuk domain cadangan dan nama peran berasal dari RFC 2606 [30] dan European Commission [36], bukan dari peluang.

## Sumber

Semua sumber ada di [referensi.md](referensi.md).

| Kelompok | Nomor |
|---|---|
| Dibaca langsung (dokumen resmi dan standar) | [1], [4], [5], [6], [7], [8], [28], [29], [30], [31], [35] |
| Resmi, dibaca lewat ringkasan alat fetch | [36] |
| Resmi, hanya dicari lewat kata kunci pada teks | [24], [25] |
| Aturan daerah, lewat agregator pasal.id | [14], [21], [22], [23] |
| Data komunitas | [2], [26], [27] |
| Buku teks (dasar hitungan peluang) | [42] |
| Tidak resmi (media dan opini) | [3], [43], [44], [45] |
