# Log Keputusan PRISM

> Dibuat 18 Nov 2026, setelah dosen pembimbing menyetujui implementasi. Keluaran akhir proyek adalah **draf jurnal**, jadi tiap keputusan dicatat di sini beserta alasan, alternatif, dan buktinya.
> Isi awal disusun dari dokumen yang sudah ada ([mvp-t5.md](mvp-t5.md), [skema-evaluasi.md](skema-evaluasi.md), [implementasi.md](implementasi.md), riset di `docs/research/`). Tanggal hanya ditulis bila tercatat di dokumen asal. Selebihnya tertulis "tidak tercatat".
> ⚠️ = belum diverifikasi atau belum disetujui. Sumber ditulis dengan nomor IEEE di [referensi.md](../research/referensi.md).

## Aturan pakai

- **Satu keputusan, satu ID** (`K-nn`). ID tidak dipakai ulang. Keputusan yang berubah **tidak dihapus**: statusnya menjadi "Diganti oleh K-xx" dan keputusan baru ditulis di bawahnya. Jurnal perlu riwayat ini.
- **Status:** `Diputuskan` (sudah disetujui, atau sudah dipakai di SRS), `Usulan` (belum disetujui), `Ditunda`, `Diganti`.
- Setiap entri berisi: **Keputusan**, **Alternatif**, **Alasan**, **Bukti** (sumber, hitungan, atau percobaan), **Batas** (kelemahan yang diterima), **Jurnal** (bagian tempat dipakai).
- Keputusan yang muncul saat implementasi (nama modul, struktur data, perilaku yang tidak ada di SRS) ditambahkan **pada hari yang sama**, termasuk perubahan kecil yang mengubah hasil pindai.
- Hasil percobaan yang memengaruhi keputusan (misalnya hasil kalibrasi U5) dicatat sebagai keputusan baru dengan data yang dipakai.

## Persetujuan

| Tanggal | Pihak | Hal |
|---|---|---|
| 18 Nov 2026 | Dosen pembimbing (Warsun Najib) | Rencana implementasi disetujui. Menurut penyusun, ⚠️ catatan rinci tentang apa yang disetujui (cakupan, metode, evaluasi) belum ditulis. Tambahkan bila ada koreksi atau syarat dari dosen |
| 18 Nov 2026 | Dosen pembimbing (Warsun Najib) | **Saran evaluasi:** mulai dari **satu bidang** dulu. Bila hasilnya dirasa kurang, baru diperluas ke banyak bidang. Dicatat sebagai K-23 |

---

## A. Cakupan

### K-01 Ancaman yang dikerjakan: T5 dulu, T3 setelah MVP
- **Status:** Diputuskan. Tanggal tidak tercatat.
- **Keputusan:** MVP hanya memindai PII di berkas repositori (T5). PII di log keluaran tes (T3) dikerjakan setelah MVP.
- **Alternatif:** mengerjakan T3 bersamaan (rencana awal di [sebelum-implementasi.md](sebelum-implementasi.md) memuat S3 log).
- **Alasan:** waktu terbatas, dan T5 sudah cukup untuk membuktikan alur pindai sampai job CI gagal. ⚠️ Alasan tertulis lebih rinci tidak ditemukan.
- **Jurnal:** Pendahuluan (batasan masalah), Saran.

### K-02 Yang dipindai: berkas teks di folder kerja, bukan riwayat git
- **Status:** Diputuskan. Tanggal tidak tercatat.
- **Alternatif:** memindai riwayat commit.
- **Alasan:** [implementasi.md](implementasi.md) mencatatnya sebagai "keputusan cakupan: working tree saja". PII yang pernah di-commit lalu dihapus tidak terdeteksi.
- **Batas:** NIK yang sudah masuk riwayat git tetap terbuka. Dicatat sebagai keterbatasan.
- **Jurnal:** Batasan, Keterbatasan.

### K-03 Jenis data yang dideteksi: NIK (termasuk NPWP orang pribadi dan KK), HP, email
- **Status:** Diputuskan, 12 Nov 2026 ([mvp-t5.md](mvp-t5.md) bagian 1.2). **Diubah 24 Nov 2026: email sempat dikeluarkan (K-33), lalu dimasukkan kembali hanya untuk penyedia email pribadi (K-34).** Isi di bawah adalah keputusan 12 Nov apa adanya.
- **Alternatif:** menambah secret/token (rencana awal), IP address, nama dan data umum butir a–e.
- **Alasan:** dasar hukum Pasal 4 ayat (3) huruf f UU PDP. Hanya nomor HP yang disebut eksplisit dalam Penjelasan. NIK, NPWP orang pribadi, KK, dan email adalah **tafsiran** dari Pasal 1 butir 1.
- **Bukti:** [dasar-hukum-uu-pdp.md](../research/dasar-hukum-uu-pdp.md). NPWP orang pribadi sama dengan NIK menurut PMK 112/2022 [6] dan PMK 81/2024 [8].
- **Batas:** tafsiran hukum ini perlu dinyatakan sebagai tafsiran di jurnal.
- **Jurnal:** Dasar teori (UU PDP), Metode (cakupan data).

### K-04 IP address tidak dikerjakan dulu
- **Status:** Diputuskan, 11 Nov 2026.
- **Alasan:** disebut eksplisit di Penjelasan Pasal 4 ayat (3) huruf f, tetapi risiko temuan palsu tinggi (nomor versi, alamat dalam contoh dokumentasi).
- **Jurnal:** Keterbatasan.

### K-05 Secret/token tidak dicakup
- **Status:** Diputuskan, tercantum di [mvp-t5.md](mvp-t5.md) bagian 1.2 ("Secret dan token juga tidak dicakup"). ⚠️ Berbeda dengan rencana awal di [sebelum-implementasi.md](sebelum-implementasi.md) yang memuat token. Tanggal perubahan tidak tercatat.
- **Alasan:** ⚠️ alasan tertulis tidak ditemukan. Dugaan: deteksi secret sudah dilayani tool lain (Gitleaks, secret scanning GitHub) dan celah yang dikerjakan PRISM adalah PII Indonesia. Konfirmasi ke penyusun. Bahan perbandingan: [perbandingan-betterleaks-presidio.md](../research/perbandingan-betterleaks-presidio.md), [tool-github-secret-scanning.md](../research/tool-github-secret-scanning.md).
- **Jurnal:** Pendahuluan (celah penelitian), Pembahasan tool pembanding.

### K-06 NPWP badan/instansi di luar cakupan
- **Status:** Diputuskan. Tanggal tidak tercatat. Bukti tambahan diperoleh 18 Nov 2026.
- **Alasan:** polanya belum diketahui. ⚠️ Alasan hukum (NPWP badan bukan data pribadi orang) adalah dugaan saya, belum diverifikasi. Badan lama berbentuk "0" + 15 digit [16]–[20]. Untuk badan baru, sumber resmi hanya menyatakan 16 digit yang dibuat sistem. Tidak ada sumber yang menyebut "acak", dan tidak ada yang menyebut pola.
- **Batas:** ⚠️ pola NPWP badan setelah Coretax 2025 tidak diketahui. Jangan menulis "acak" di jurnal.
- **Jurnal:** Batasan, Keterbatasan.

### K-07 NIK dikenali hanya sebagai 16 digit berurutan, tanpa pemisah
- **Status:** Diputuskan, 24 Nov 2026, atas masukan penyusun.
- **Keputusan:** regex NIK tetap `(?<!\d)\d{16}(?!\d)`. NIK yang ditulis dengan spasi, strip, atau titik tidak dideteksi. Tes dengan pemisah memastikan **0 temuan**, supaya batasan terdokumentasi.
- **Alternatif:** mendukung pemisah seperti python-stdnum (membuang ` -.`) [69] dan tes Presidio [60].
- **Alasan:** menurut penyusun, NIK ditulis 16 digit tanpa pemisah. ⚠️ Belum dicek apakah PP 40/2019 [5] menyebut penulisannya. Mendukung pemisah juga menambah risiko temuan palsu (angka berderet seperti nomor telepon, ID, atau tanggal) yang belum diukur.
- **Batas:** NIK di berkas nyata yang diberi pemisah, atau yang terpotong menjadi 15 digit signifikan oleh spreadsheet (dugaan di format-pii-indonesia.md bagian 8, nomor 1 ⚠️), tidak terdeteksi. Seberapa sering terjadi tidak diukur.
- **Jurnal:** Keterbatasan, Saran (versi 2: ukur bentuk NIK di berkas nyata).


### K-33 Email dikeluarkan dari cakupan
- **Status:** **Diganti oleh K-34** pada hari yang sama (24 Nov 2026). Dicatat tetap supaya riwayat keputusan utuh. Penyusun berubah pikiran: email tetap dicakup, tetapi hanya email pribadi.
- **Keputusan:** PRISM tidak mendeteksi email. Jenis di laporan hanya `nik` dan `hp`. Mengubah K-03 (12 Nov 2026).
- **Alasan penyusun:** yang berbahaya bila bocor adalah password, bukan email. ⚠️ Pernyataan penyusun, tanpa sumber. Pendukung dari riset sebelumnya: UU PDP tidak menyebut email secara eksplisit [31], `info@company.com` bukan data pribadi menurut Komisi Eropa [36], dan alamat SSH serta contoh dokumentasi berpotensi menjadi temuan palsu (format-pii-indonesia.md bagian 7.4–7.5).
- **Konsekuensi untuk SRS (belum diubah):** hapus KF-09 dan KF-13, kata konteks email di KF-14, aturan mask email, dan bagian email di contoh keluaran, tes, serta jumlah kriteria MVP. Langkah 7 menjadi HP saja.
- **Keterbatasan yang harus ditulis:** email pribadi (nama.lengkap@) yang bocor tidak terdeteksi. **Password dan secret juga tidak terdeteksi** karena di luar cakupan (K-05). Bila kekhawatiran utama adalah password, itu ranah pemindai secret seperti Gitleaks, dan PRISM tidak menggantikannya.
- **Jurnal:** Batasan masalah, Keterbatasan, Saran.

### K-34 Email dideteksi hanya untuk penyedia email pribadi
- **Status:** Diputuskan, 24 Nov 2026, atas masukan penyusun. **Daftar domain pribadi disetujui penyusun pada hari yang sama.** Menggantikan K-33. ⚠️ Rencana yang disetujui dosen pada 18 Nov memuat email tanpa pembatasan domain, jadi perubahan ini perlu disampaikan.
- **Keputusan:** email dideteksi, tetapi dinilai menurut domain. Domain ada di daftar penyedia email pribadi (gmail, icloud, yahoo, dan sejenisnya) → `medium`. Domain lain → `low`: tidak dilaporkan pada ambang bawaan, tetapi terhitung di `suppressed_low`. Jenis laporan: `nik`, `hp`, `email`. Mengubah KF-13.
- **Alasan penyusun:** email pribadi lazimnya memakai penyedia umum, sedangkan alamat perusahaan berakhiran nama perusahaan dan tidak dipedulikan. ⚠️ Pendapat penyusun, tanpa sumber.
- **Efek samping yang menguntungkan:** alamat SSH (`git@github.com:user/repo.git`), domain contoh (`example.com`), dan alamat perusahaan jatuh ke `low` dengan sendirinya karena domainnya tak ada di daftar. Aturan RFC 2606 dan "nama peran" di KF-13 jadi tidak perlu sebagai aturan terpisah ⚠️ (sederhanakan KF-13 setelah disetujui).
- **Batas yang harus ditulis di jurnal:**
  - Email pribadi di domain sendiri atau domain kampus dan sekolah (`ac.id`, `sch.id`) tidak dilaporkan.
  - Email kantor berbentuk `nama.lengkap@perusahaan` tetap data pribadi menurut Komisi Eropa [36]. Keputusan ini sengaja mengabaikannya.
  - Daftar domain disusun sendiri, tidak bersumber ⚠️. Daftar awal yang ditetapkan, boleh ditambah bila waktu ada (tiap tambahan dicatat di sini): `gmail.com`, `googlemail.com`, `yahoo.com`, `yahoo.co.id`, `ymail.com`, `outlook.com`, `hotmail.com`, `live.com`, `msn.com`, `icloud.com`, `me.com`, `proton.me`, `protonmail.com`.
  - Kata konteks `email` tetap menaikkan `low` ke `medium` (KF-14), jadi `email: budi@pt-abc.co.id` akan dilaporkan. Bila tidak diinginkan, kecualikan konteks untuk domain di luar daftar. **Belum diputuskan.**
  - Password dan secret tetap tidak terdeteksi (K-05).
- **Pengujian:** tes unit per baris tabel, ditambah pindai repo publik (D4) untuk melihat berapa email di domain luar daftar yang sebenarnya pribadi.
- **Jurnal:** Metode, Keterbatasan.

---

## B. Metode deteksi

### K-08 Regex + validasi + tingkat bukti, tanpa ML atau NER
- **Status:** Diputuskan. Tanggal tidak tercatat.
- **Alternatif:** NER/spaCy, Presidio penuh.
- **Alasan:** PII Indonesia yang dicakup berpola tetap dan punya aturan validasi dari peraturan. Nama tanpa pola tidak bisa ditangani regex, dan itu sudah ditulis sebagai di luar cakupan ([implementasi.md](implementasi.md) bagian "Tanpa NER").
- **Batas:** ⚠️ klaim "hasilnya mirip Presidio" tidak boleh ditulis tanpa pengukuran. Alasan "F1 lebih baik" tidak boleh dipakai tanpa bukti ([cek-dan-belajar.md](cek-dan-belajar.md)).
- **Jurnal:** Metode, Pembahasan.

### K-09 Tingkat bukti (`high`/`medium`/`low`), bukan skor angka
- **Status:** Diputuskan. Tanggal tidak tercatat.
- **Alternatif:** skor 0–1 seperti Presidio ([implementasi.md](implementasi.md) memakai 0,35 dan 0,4 dari default Presidio).
- **Alasan:** skor angka butuh kalibrasi dari data berlabel yang belum ada. Tingkat hanya mengurutkan kekuatan bukti dan tidak mengklaim probabilitas.
- **Konsekuensi:** [implementasi.md](implementasi.md) belum disesuaikan (diakui di [mvp-t5.md](mvp-t5.md) bagian 4.4).
- **Jurnal:** Metode, Pembahasan (perbedaan dengan Presidio).

### K-10 Kriteria tingkat bukti NIK
- **Status:** Diputuskan, tercantum di KF-11 ([mvp-t5.md](mvp-t5.md)).
- **Keputusan:**
  - `high`: tanggal sah **dan** kode kecamatan (6 digit pertama) terdaftar.
  - `medium`: tanggal sah, provinsi terdaftar, kecamatan tidak ada.
  - `low`: selainnya, termasuk 16 digit acak.
- **Aturan dasar:** hari 01–31 atau 41–71 (perempuan +40), bulan 01–12, hari sesuai bulan, 29 Feb diterima. Provinsi dari 38 kode, kecamatan dari 7.285 kode.
- **Bukti:** struktur NIK dari PP 40/2019 [5]. Daftar wilayah dari Kepmendagri 2430 [1], disimpan di `data/reference/kode-wilayah/`.
- **Batas:** peluang lolos kebetulan ±0,053% (`high`) dan ±2,73% (`medium`) dihitung dengan **asumsi angka acak merata**, jadi hanya gambaran. Angka sebenarnya diukur di uji U5. Nomor urut (4 digit terakhir) tidak dicek karena tidak ada aturannya. Tidak ada checksum pada NIK. Daftar kecamatan baru diverifikasi sampai jumlah per provinsi, ⚠️ belum satu per satu.
- **Jurnal:** Metode, Hasil (U5).

### K-11 Pemeriksaan tanggal lahir tetap dipakai
- **Status:** Diputuskan, 12 Nov 2026.
- **Alasan:** tanggal lahir adalah data yang rawan, dan tanggal sah bersama kecamatan terdaftar menjadi syarat `high`.
- **Batas:** NIK asli dengan tanggal salah (mis. bulan 13) jatuh ke `low` dan hanya dilaporkan bila ada kata konteks di baris yang sama. Diterima untuk menekan temuan palsu. Seberapa sering terjadi diukur di langkah evaluasi ⚠️.
- **Jurnal:** Metode, Keterbatasan.

### K-12 NIK dengan kode wilayah lama diterima sebagai batasan
- **Status:** Diputuskan, 12 Nov 2026.
- **Keputusan:** NIK asli dengan kecamatan yang tidak ada di daftar 2025 (mis. karena pemekaran) jatuh ke `medium` bila provinsinya terdaftar dan formatnya sah. Daftar diperbarui bila ada keputusan baru.
- **Alasan:** yang dicari adalah apakah angka itu NIK yang bisa bocor, bukan asal wilayahnya.
- **Jurnal:** Keterbatasan.

### K-13 Kata konteks menaikkan satu tingkat
- **Status:** Diputuskan sebagai **hipotesis**. ⚠️ Belum punya dasar teori atau sumber.
- **Keputusan:** kata petunjuk (`nik`, `ktp`, dan sejenisnya) di baris yang sama (±40 karakter ⚠️) menaikkan tingkat satu langkah.
- **Perubahan 24 Nov 2026:** kata konteks email (`email`, `surel`, `mail`) sempat dicabut oleh K-33, lalu berlaku kembali lewat K-34.
- **Alasan:** ⚠️ dugaan: meniru pola konteks di Presidio (konteks menaikkan skor), belum diverifikasi. Besar kenaikan dan jarak di sini adalah pilihan sendiri.
- **Pengujian:** diuji di U5. Hasil kalibrasi harus dicatat sebagai keputusan baru. Bila hasil menunjukkan konteks tidak membantu, aturan diganti (status K-13 menjadi "Diganti").
- **Batas:** judul kolom CSV (`nik`) tidak terjangkau karena konteks hanya dicari di baris yang sama. Itu sebabnya `high` dan `medium` harus bisa dilaporkan tanpa konteks.
- **Jurnal:** Metode, Hasil (U5), Keterbatasan.

### K-14 Aturan HP: bentuk yang dikenali dan tingkat bukti
- **Status:** **Diputuskan sebagai hipotesis**, 24 Nov 2026. Penyusun menyetujui bentuk yang dikenali (enam bentuk di bawah) dan pilihan (a) untuk `81234567890` polos. Semua tingkat tetap ⚠️ hipotesis sampai diuji di U5. Aturan email ada di K-34.
- **Masukan penyusun, 24 Nov 2026:** nomor HP rawan dipakai untuk spam dan penipuan lewat SMS atau email, dan bentuk penulisannya berbeda di tiap database. ⚠️ Ini pengalaman penyusun, bukan sumber tertulis. Penyusun menyebut enam bentuk yang ditemui:

| Bentuk | Contoh | Regex di SRS (KF-08) | Usulan tingkat |
|---|---|---|---|
| Nasional polos | `081234567890` | Cocok | `medium` (KF-12) |
| Nasional berpemisah | `0812-3456-7890` | Cocok | `high` (KF-12) |
| Internasional `+` polos | `+6281234567890` | Cocok | `high` (KF-12) |
| Internasional `+` berpemisah | `+62 812-3456-7890` | Cocok bila pemisah setelah `+62` ditangani ⚠️ perlu dipastikan di regex | `high` (KF-12) |
| Tanpa nol, berpemisah | `812-3456-7890` | **Tidak cocok**. Dimasukkan atas permintaan penyusun | `medium` ⚠️ hipotesis: pola 3-4-4 berawalan `8x` jarang muncul kebetulan |
| Tanpa nol, polos | `81234567890` | **Tidak cocok** (format-pii-indonesia.md bagian 6.3: "terlalu ambigu"). Dimasukkan atas permintaan penyusun | `low`, naik ke `medium` hanya bila ada kata konteks (`hp`, `telp`, `wa`) ⚠️ lihat catatan di bawah |

- **Keputusan penyusun, 24 Nov 2026:** dua bentuk tanpa nol harus dikenali. Alasan: isian sering memuat pilihan `+62` di kolom terpisah, sehingga basis data menyimpan nomor tanpa `0` di depan, terutama pada aplikasi lintas negara. ⚠️ Ini asumsi penyusun, belum diverifikasi ke database atau aplikasi nyata.
- **Batas yang perlu disadari:** bila kode negara ada di kolom terpisah, nomornya biasanya juga berdiri sendiri di kolom sendiri (mis. CSV `62,81234567890`). Konteks hanya dicari di baris yang sama, jadi judul kolom `hp` tidak terjangkau (K-13). Akibatnya `81234567890` polos yang berstatus `low` **tidak dilaporkan pada ambang bawaan** kecuali ada kata konteks di barisnya. Pilihan: (a) tetap `low` dan tulis sebagai batasan; (b) naikkan ke `medium` dan terima temuan palsu dari angka 11 digit berawalan `8x` (ID, nominal) ⚠️ belum diukur; (c) baca judul kolom CSV (tahap 2). **Dipilih: (a)** (24 Nov 2026). Pilihan (b) dan (c) dipikirkan lagi bila waktu ada, setelah kalibrasi U5 dan pindai repo publik (D4).
- **Mengapa dua bentuk terakhir diusulkan masuk:** penyusun menemuinya di database. Memakai tingkat bukti dan konteks, bentuk yang ambigu tidak harus dibuang, cukup diberi tingkat rendah. Pertimbangan di format-pii-indonesia.md bagian 6.2: melewatkan nomor lebih buruk daripada satu temuan palsu.
- **Dampak:** perlu satu pola regex tambahan (tanpa awalan `0`, `62`, atau `+62`) dan perubahan KF-08, KF-12, dan tes. Ruang lingkup ±15–30 menit tambahan di langkah 5 dan 7 ⚠️ perkiraan.
- **Dasar:** NDC seluler `08XY` dari Permenkominfo 14/2018 [25]. Panjang 9–12 digit setelah awalan dari metadata libphonenumber [26], bukan sumber pemerintah.
- **Belum diketahui:** tabel alokasi NDC per operator dan perubahannya setelah 2018, panjang nomor pelanggan resmi, dan sebaran bentuk HP di database nyata. Semua tingkat di tabel adalah hipotesis yang diuji di U5.
- **Jurnal:** Metode. Tulis sebagai desain, bukan hasil terverifikasi, sampai disetujui.

### K-15 Ambang pelaporan bawaan `medium`
- **Status:** Diputuskan. Opsi `--min-level` (`low`/`medium`/`high`).
- **Alasan:** ⚠️ dugaan: `low` mencakup 16 digit acak sehingga banyak temuan palsu. Belum diukur. Temuan `low` tidak dicetak, hanya jumlahnya di ringkasan (`suppressed_low`).
- **Pengujian:** ambang dibandingkan di kalibrasi, lalu dibekukan (lihat K-26).
- **Jurnal:** Metode, Hasil.

### K-16 Prefilter baris dan dedup
- **Status:** Diputuskan.
- **Prefilter:** baris dilanjutkan bila jumlah digit ≥ 8 (walau dipisah spasi, titik, strip) atau ada `@`. Alasannya: HP seperti `0812-3456-7890` tidak punya 8 digit berurutan.
- **Dedup:** temuan beririsan dipilih menurut tingkat tertinggi, lalu terpanjang, lalu urutan rule (NIK lebih dulu).
- **Jurnal:** Metode.

### K-17 Berkas yang dilewati
- **Status:** Diputuskan.
- **Keputusan:** `.git`, berkas biner (ekstensi umum atau ada byte nol), berkas di atas 1 MB ⚠️, folder `--exclude`.
- **Batas:** batas 1 MB belum punya dasar. PII di berkas besar atau biner tidak terdeteksi.
- **Jurnal:** Keterbatasan.

### K-18 Hanya pustaka standar Python; Python 3.13 di lokal dan CI
- **Status:** Diputuskan.
- **Alasan:** ringan dipasang di runner dan hasil sama antara lokal dan CI. pytest dan Faker hanya saat pengembangan. Rincian: [library-bawaan-python.md](../research/library-bawaan-python.md).
- **Jurnal:** Implementasi.

---

## C. Laporan dan CI

### K-19 Nilai PII selalu di-mask, tanpa opsi menampilkan utuh
- **Status:** Diputuskan.
- **Keputusan:** NIK dan HP: 4 karakter terakhir, sisanya `*`. Email: bagian sebelum `@` jadi `*`, domain tetap (keputusan 16 Nov 2026, karena "4 karakter terakhir" pada email menghasilkan `.com`). Fungsi `mask()` dibuat sendiri.
- **Perubahan 24 Nov 2026:** aturan mask email sempat dicabut oleh K-33, lalu berlaku kembali lewat K-34.
- **Alternatif:** Presidio Anonymizer (tidak dipakai karena PRISM hanya melapor dan tidak mengubah sumber); hash.
- **Alasan:** laporan PRISM tidak boleh menjadi sumber kebocoran baru bila log atau artifact terunggah (NFR-04).
- **Batas:** 4 digit terakhir NIK adalah nomor urut, sedikit informasi tetap terbuka. Domain email pribadi tetap terbaca. Panjang local-part terlihat dari jumlah `*`. ⚠️ Metode ini belum punya rujukan di `referensi.md`.
- **Jurnal:** Metode, Keterbatasan.

### K-20 Fingerprint HMAC untuk mengenali temuan yang sama ditunda
- **Status:** Ditunda.
- **Alasan:** hash SHA-256 polos tidak aman karena ruang nilai NIK dan HP kecil sehingga bisa ditebak. Perlu HMAC berkunci. Di luar MVP.
- **Jurnal:** Saran.

### K-21 Exit code 0 bersih, 1 ada temuan, 2 gagal pindai
- **Status:** Diputuskan.
- **Alasan:** gagal pindai tidak boleh terlihat bersih. Bila ada error dan temuan, 2 didahulukan. Kedua kode bukan nol menggagalkan job.
- **Jurnal:** Metode, Implementasi.

### K-22 Aturan gagal: semua temuan di atas ambang menggagalkan job
- **Status:** Diputuskan, 2 Nov 2026 (tercatat di `rencana-harian-11-nov.md` dan [implementasi.md](implementasi.md)).
- **Alternatif:** peringatan saja tanpa menggagalkan. Tingkat keparahan dan pengecualian tidak dikerjakan di MVP.
- **Batas:** job merah tidak menolak push dan tidak menghapus data. PRISM hanya mendeteksi dan melapor.
- **Jurnal:** Metode, Pembahasan.

---

## D. Evaluasi

Seluruh bagian ini adalah **usulan** sampai penyusun mengonfirmasi. Rincian ada di [skema-evaluasi.md](skema-evaluasi.md). Sumber di [pengujian-tool-lain-dan-data-uji.md](../research/pengujian-tool-lain-dan-data-uji.md).

### K-23 Evaluasi dimulai dari satu bidang, diperluas bila hasil kurang
- **Status:** Diputuskan, 18 Nov 2026, atas saran dosen pembimbing. Menggantikan usulan sebelumnya "tidak memakai bidang tertentu".
- **Keputusan:** data uji tahap pertama dibuat dengan **satu bidang** sebagai tema (mis. kesehatan atau keuangan). Bila hasil dirasa kurang, tahap kedua memperluas ke beberapa bidang.
- **Alternatif:** langsung banyak bidang (usulan awal saya, karena satu NIK bisa muncul di bidang mana pun dan repo nyata sulit dilabeli).
- **Alasan:** saran dosen. Satu bidang lebih murah dibuat dan dijelaskan. ⚠️ Alasan dosen tidak dicatat rinci, tambahkan bila ada.
- **Catatan konsistensi:** "bidang" tetap **tema pembuat data**, bukan label PII (K-25). Bidang dicatat sebagai metadata set data (nama folder, README), bukan kolom `ground_truth.csv`. Bila tahap kedua dikerjakan dan hasil mau dipecah per bidang, kolom `bidang` baru ditambahkan saat itu.
- **Batas:** satu bidang membatasi generalisasi. Jurnal harus menulis bahwa hasil berlaku untuk bidang itu. ⚠️ Kata "dirasa kurang" belum didefinisikan (lihat bagian G, nomor 13). Bila kriteria baru ditulis **setelah** melihat hasil, pembaca bisa menilai perluasan itu sebagai pilihan yang menyesuaikan hasil.
- **Jurnal:** Metode (evaluasi), Keterbatasan, Saran.

### K-24 Empat sumber data
- **Status:** Usulan, 18 Nov 2026.
- **Keputusan:** D1 repo tiruan sintetis berlabel (wajib), D2 sekitar 30 kasus tulisan tangan (wajib), D3 pembanding independen python-stdnum [69] (wajib), D4 repo publik untuk precision (opsional).
- **Alasan:** repo tiruan memberi label pasti tetapi bisa terlalu bagus (sirkular). Kasus tulisan tangan dan python-stdnum mengimbangi. Repo publik tidak bisa menghitung recall.
- **Bukti hasil periksa:** ai4privacy [67], [68] tidak dipakai sebagai ground truth NIK. Dari sampel 30 baris Indonesia, IDCARDNUM berbentuk alfanumerik 10 karakter, dan 2 dari 6 TAXNUM yang dicek berkode provinsi tidak valid. Sampel kecil, jangan digeneralisasi.
- **Catatan:** D1 dan D2 mengikuti K-23 (satu bidang dulu). Bidang yang dipilih belum diputuskan (bagian G, nomor 14).
- **Jurnal:** Metode (data uji), Keterbatasan.

### K-25 Kolom ground truth tidak memuat "bidang"
- **Status:** Usulan, 18 Nov 2026.
- **Keputusan:** `berkas, baris, jenis, label, level_diharapkan, asal_sampel, kata_konteks, jenis_berkas, split`.
- **Alasan:** koreksi dari penyusun. Satu NIK bisa menjadi data pribadi orang, NPWP, atau BPJS, jadi "bidang" bukan label PII yang valid. Bidang hanya tema pembuat data.
- **Jurnal:** Metode (data uji).

### K-26 Pembagian per berkas, aturan beku, data uji dijalankan sekali
- **Status:** Usulan, 18 Nov 2026.
- **Keputusan:** data dibagi per berkas menjadi kalibrasi dan uji. Ambang dan aturan konteks ditetapkan dari kalibrasi, ditulis, dibekukan, lalu data uji dijalankan sekali. Bila hasil mengecewakan lalu aturan diperbaiki, laporan harus menyebut bahwa data uji sudah terlihat.
- **Alasan:** mencegah kebocoran antara data penyetel dan data uji (praktik serupa di presidio-research [59]).
- **Batas:** ⚠️ sumber untuk praktik pemisahan kalibrasi/uji secara umum belum dikutip.
- **Jurnal:** Metode (evaluasi).

### K-27 Metrik dan pembanding
- **Status:** Usulan, 18 Nov 2026.
- **Keputusan:** precision, recall, F1, FPR per ambang, precision per tingkat bukti, waktu pindai. Pembanding: baseline `\d{16}` polos dan python-stdnum. Presidio opsional (U1).
- **Batas:** ⚠️ definisi metrik belum bersumber (rencana: dokumentasi scikit-learn atau buku teks).
- **Jurnal:** Metode, Hasil.

### K-28 Tes otomatis bergaya Presidio (pytest)
- **Status:** Usulan, 18 Nov 2026.
- **Keputusan:** tabel `(teks, jumlah temuan, tingkat)` per rule, termasuk contoh yang tidak boleh terdeteksi. Contoh: `3171011503900001` → `high`, `3171991503900001` → `medium`, `4171011503900001` → `low`, `3171011513900001` → `low`.
- **Jurnal:** Implementasi (pengujian).

### K-29 Jadwal evaluasi 1 minggu
- **Status:** Usulan, 18 Nov 2026.
- **Keputusan:** H1–H7, dengan urutan pemotongan bila waktu kurang. Perkiraan minimum ±10,5–11 jam dan penuh ±13–14 jam. Semua perkiraan, bukan hasil pengukuran.
- **Jurnal:** tidak untuk jurnal. Hanya pegangan kerja.

### K-35 Tes ditulis bersamaan dengan tiap langkah, bukan di akhir
- **Status:** Usulan, 24 Nov 2026. ⚠️ Belum disetujui penyusun. Mengubah urutan di [mvp-t5.md](mvp-t5.md) Lampiran B (tes `pytest` baru dilengkapi di langkah 11).
- **Keputusan:** tiap langkah 3 sampai 9 selesai bila tes langkah itu hijau **dan** seluruh `pytest` lama tetap hijau. Langkah 11 menjadi pelengkap: matriks KF → tes, tes pengecoh, dan pemeriksaan di lingkungan bersih. Tes progres memakai contoh tulisan tangan di berkas tes, **bukan** `data/synthetic/` bagian `uji` (K-26). Rincian per langkah: [rencana-progres-implementasi.md](rencana-progres-implementasi.md).
- **Alternatif:** tes dikumpulkan di langkah 11 sesuai mvp-t5.
- **Alasan:** bug di rule NIK baru akan ketahuan setelah HP, laporan, dan CI dibangun di atasnya. Tes yang ditulis lebih awal juga memaksa spesifikasi jelas sebelum kode. ⚠️ Alasan penyusun, belum diuji.
- **Batas:** tes lulus hanya membuktikan kode sesuai harapan penyusun, bukan harapannya benar (itu urusan sumber resmi dan evaluasi). `pytest` bukan pustaka standar: boleh dipakai sebagai alat pengembangan lokal, tidak boleh di-`import` dari `src/` (K-18).
- **Jurnal:** Implementasi (pengujian).

---

## E. Proses penelitian

### K-30 Semua riset dicatat di `referensi.md`, format IEEE
- **Status:** Diputuskan (skill `riset-referensi`).
- **Aturan:** nomor berurutan, peta sumber, ⚠️ untuk sumber yang belum dibaca langsung, jangan menebak judul, penulis, atau tahun. Sumber yang dibaca lewat OCR atau agregator ditulis apa adanya.
- **Jurnal:** Daftar pustaka.

### K-31 Data uji sepenuhnya sintetis
- **Status:** Diputuskan ([sebelum-implementasi.md](sebelum-implementasi.md) bagian A, butir 8).
- **Alasan:** tidak memakai data asli orang. Generator NIK dibuat sendiri karena Faker tidak punya provider `ssn` untuk `id_ID` [70].
- **Jurnal:** Metode, Etika.

### K-32 Repo indonesian-id-card-identification tidak dipakai sebagai kode, data, atau pembanding
- **Status:** Diputuskan, 24 Nov 2026, setelah repo dicek atas saran penyusun.
- **Keputusan:** repo [75] hanya dipakai sebagai bahan banding desain dan catatan di tinjauan pustaka. Kode dan datanya tidak dipakai. Pembanding independen tetap python-stdnum [69] (K-24).
- **Alasan:** (1) bukan pemindai, melainkan API yang menerima NIK dari pemanggil; (2) tanpa lisensi, jadi kode dan CSV tidak boleh disalin; (3) dua cacat yang saya konfirmasi lewat tulis ulang logikanya: nol di depan tanggal hilang (`010190` terbaca 10-01-1990) dan pemeriksaan 4 digit terakhir selalu lolos; (4) data wilayah dari 2021 dengan 33 provinsi, berselisih dengan data PRISM.
- **Yang dipelajari:** struktur pemeriksaannya (panjang, wilayah, tanggal +40, gender, 4 digit terakhir) sama dengan penilaian NIK PRISM. Tetapi README tidak menyebut sumber aturan, jadi ini bukan bukti independen atas aturan. Repo mensyaratkan umur ≥ 17 tahun. PRISM sengaja tidak meniru karena NIK untuk anak tetap data pribadi (⚠️ belum bersumber).
- **Bukti:** [75], rincian di [pengujian-tool-lain-dan-data-uji.md](../research/pengujian-tool-lain-dan-data-uji.md) bagian 3.4. Selisih tabel wilayah menguatkan K-12.
- **Jurnal:** Tinjauan pustaka (karya serupa), Pembahasan.

---

## F. Koreksi dan temuan yang memengaruhi tulisan

Bagian ini mencatat klaim yang pernah salah atau terlalu kuat, agar tidak muncul di jurnal.

| Tanggal | Klaim awal | Koreksi | Sumber |
|---|---|---|---|
| 18 Nov 2026 | "NPWP 15 digit tidak berlaku sejak 1 Juli 2024" | Terlalu kuat. NPWP 15 digit masih diterbitkan dan dipakai berdampingan. Wajib pajak pihak lain menggunakan NPWP 16 digit paling lambat 31 Des 2024 | PENG-26/PJ.09/2024 [12], PER-6/PJ/2024 (hanya lewat [12], [16], [17]) |
| 18 Nov 2026 | NPWP badan baru "acak" | Tidak ada sumber resmi yang menyebut "acak" atau pola. Hanya "16 digit dibuat sistem" | [16]–[20] |
| 18 Nov 2026 | Hitungan jam evaluasi ±8 | Diperbaiki menjadi ±10,5–11 (minimum) dan ±13–14 (penuh) | [skema-evaluasi.md](skema-evaluasi.md) |
| 18 Nov 2026 | Kolom "bidang" di ground truth | Dihapus, bukan label PII yang valid (K-25) | umpan balik penyusun |
| 18 Nov 2026 | "Seluruhnya berakhiran 999x" (ai4privacy) | 6 dari 7 nilai dicek, nilai ketujuh tidak dicek | [pengujian-tool-lain-dan-data-uji.md](../research/pengujian-tool-lain-dan-data-uji.md) |

---

## G. Belum diputuskan atau belum diverifikasi

| No | Hal | Terkait |
|---|---|---|
| 1 | ~~Dukungan pemisah NIK~~ Selesai 24 Nov 2026 (K-07). Sisa: cek PP 40/2019 [5] apakah menyebut cara penulisan | K-07 |
| 2 | ~~Persetujuan KF-12 dan KF-13~~ Disetujui sebagai hipotesis 24 Nov 2026 (K-14 pilihan (a), K-34). Sisa: pilihan (b)/(c) bila waktu ada | K-14, K-34 |
| 3 | Isi `loc.dat` python-stdnum dibandingkan dengan Kepmendagri 2430/2025. Bila daftarnya lama, selisih hasil bisa berasal dari tahun daftar | K-24 |
| 4 | Teks resmi PER-6/PJ/2024 dibaca langsung (sekarang hanya lewat sumber lain) | K-03, koreksi NPWP |
| 5 | Definisi metrik (precision, recall, F1, FPR) dari sumber yang bisa dikutip | K-27 |
| 6 | Sumber untuk pemisahan kalibrasi dan uji | K-26 |
| 7 | Rujukan untuk masking parsial | K-19 |
| 8 | Dasar batas ±40 karakter dan 1 MB | K-13, K-17 |
| 9 | Sinkronisasi dokumen lama (`implementasi.md`, `riset-privacy-scanner-cicd.md`) dengan keputusan terbaru | K-09 |
| 10 | Metode penelitian (kandidat Design Science Research [Hevner 2004, Peffers 2007] ⚠️ belum diverifikasi) dan bagian jurnalnya | - |
| 11 | ~~Pembaruan `mvp-t5.md` langkah 10 dan KF-25~~ Selesai 24 Nov 2026 (kolom baru, D1–D4, `split`, K-23 sampai K-26). Sisa: pilih bidang tahap pertama (G-14) | K-25 |
| 12 | Catatan rinci persetujuan dosen: apa saja yang disetujui dan apakah ada syarat | Persetujuan |
| 13 | Kriteria "hasil kurang" yang memicu perluasan ke banyak bidang (mis. recall di bawah angka tertentu, atau selisih besar dengan python-stdnum). **Tulis sebelum menjalankan data uji** | K-23, K-26 |
| 14 | Bidang yang dipilih untuk tahap pertama dan alasannya | K-23 |
| 15 | SRS sudah diubah untuk K-07, K-14, K-34, dan (24 Nov 2026, sore) K-23 sampai K-27 serta K-35 (langkah 10, 11, 13, KF-25 sampai 27). **Belum:** beri tahu dosen tentang K-34 | K-34 |
| 17 | Sumber untuk daftar domain pribadi, dan apakah konteks `email` berlaku untuk domain di luar daftar (usulan: tidak berlaku). Putuskan di langkah 8 | K-34 |
| 18 | Cek asumsi "kode negara di kolom terpisah sehingga nomor tersimpan tanpa 0" ke contoh database atau aplikasi nyata | K-14 |
| 16 | Tabel NDC per operator di Permenkominfo 14/2018 [25] dibaca atau diputuskan memakai batas libphonenumber [26] sebagai hipotesis | K-14 |
