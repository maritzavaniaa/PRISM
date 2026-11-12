# Format PII Indonesia: Diparkir

> **Bukan fokus MVP.** Dokumen ini menampung riset yang sudah dikerjakan tetapi tidak dipakai sekarang (keputusan 12 Nov. 2026). Fokus MVP ada di [format-pii-indonesia.md](format-pii-indonesia.md): NIK (+NPWP orang pribadi, +KK), nomor HP, dan email.
> Semua sumber: [referensi.md](referensi.md). ⚠️ = belum diverifikasi atau belum diuji.

## Daftar isi

| Bagian | Isi | Status |
|---|---|---|
| P1 | NPWP: format lama 15 digit, NPWP badan, kasus kebocoran | Sebagian |
| P2 | Kartu kredit dan debit | Format ada, tingkat bukti belum diputuskan |
| P3 | Identifier perorangan lain (kandidat) | Belum diriset |
| P4 | Tabel parkir (NIK `99`, WNA, NOP, akta, IP Address, dan lain-lain) | - |

## P1. NPWP

> NPWP **orang pribadi penduduk** adalah NIK dan sudah tercakup di dokumen fokus. Bagian ini hanya untuk format lama dan hal di luar fokus.

### P1.1 Format NPWP lama 15 digit milik orang pribadi

- **Penduduk:** NPWP-nya adalah **NIK**. Jadi dideteksi oleh rule NIK dan tidak bisa dibedakan dari NIK.
- **NPWP 15 digit lama** milik orang pribadi akan terus muncul di berkas lama (faktur, bukti potong, kontrak) karena dokumen lama tetap sah [7] Pasal 13.
- Status 15 digit setelah 2024 masih tidak pasti. Pengumuman DJP PENG-26/PJ.09/2024 [12] menyebut DJP masih menerbitkan 15 digit di samping 16 digit dan pihak lain boleh memakai 15 digit sampai 31 Des. 2024. Status per Nov. 2026 belum diketahui ⚠️.
- Format tulis 15 digit memakai titik dan tanda hubung. Contoh dari [13]: `00.000.000.0-000.000` (placeholder). Format 16 digit ditulis tanpa titik dan tanda hubung [13].

### P1.2 Struktur 15 digit

Dari ringkasan hasil pencarian (**tidak resmi** ⚠️, tidak ditemukan di dokumen DJP yang dibaca):

| Posisi | Isi |
|---|---|
| 2 digit | Jenis wajib pajak |
| 6 digit | Nomor urut |
| 1 digit | Digit pemeriksa (algoritma belum terverifikasi, **tidak dipakai**) |
| 3 digit | Kode KPP |
| 3 digit | Status pusat atau cabang (`000` = pusat) |

### P1.3 Usulan tingkat bukti NPWP 15 digit (belum disetujui ⚠️)

| Tingkat | Syarat |
|---|---|
| `medium` | Berbentuk `XX.XXX.XXX.X-XXX.XXX` (titik dan tanda hubung pada posisi tersebut) |
| `medium` | 15 digit polos **dan** ada kata konteks `npwp` di baris yang sama |
| `low` | 15 digit polos tanpa konteks. Tidak dilaporkan |

Bentuk bertitik jarang muncul kebetulan, dan kata konteks mengganti struktur internal yang belum bersumber.

### P1.4 NPWP badan: di luar cakupan

- UU PDP mendefinisikan data pribadi sebagai data tentang **orang perseorangan** (Pasal 1 butir 1 dan 6 [31]). Badan usaha bukan orang perseorangan.
- European Commission [36] menyebut "a company registration number" bukan data pribadi.
- Jadi NPWP badan dan NITKU (NPWP pusat 16 digit + 6 digit urut, untuk cabang) tidak dideteksi. Usaha perseorangan memakai NPWP pemiliknya, yang sudah tercakup.
- Catatan riset awal: tidak ada sumber resmi tentang pola nomor 16 digit untuk badan baru. Badan lama memakai `0` + 15 digit lama [6] Pasal 7.

### P1.5 Kasus kebocoran NPWP yang pernah diberitakan (dicari 12 Nov. 2026)

| Kasus | Yang dilaporkan | Status |
|---|---|---|
| **Sept. 2024** | Akun "Bjorka" dilaporkan menjual sekitar 6,6 juta data di Breach Forums, ±US$10.000, 10.000 baris sampel (nama, NIK, NPWP, alamat, email, HP, tanggal lahir). Disebut mencakup NPWP Presiden dan sejumlah menteri [37] | **Klaim, belum terbukti.** DJP membantah: log akses 6 tahun tidak menunjukkan kebocoran langsung dari sistemnya [38]. Hasil forensik resmi tidak saya temukan ⚠️ |
| **Sept. 2026** | Pelaku tak bernama mengklaim data DJP (NPWP, nama, alamat, HP, kata sandi, token) [39] | **Klaim, belum dikonfirmasi.** DJP: belum dapat dipastikan berasal dari sistem DJP. Satu sumber media ⚠️ |

- Penyalahgunaan NPWP bocor terhadap orang tertentu tidak saya temukan kasus terbuktinya. Yang ada hanya risiko yang disebut media (pinjaman online atas nama korban, tagihan pajak palsu).
- Sejak NPWP orang pribadi sama dengan NIK, kebocoran NPWP orang pribadi sama dengan kebocoran NIK.
- Semua kasus adalah kebocoran basis data dari sistem, **bukan** NPWP di berkas repositori.

### P1.6 Belum diketahui (⚠️)

- Struktur segmen 15 digit dari sumber resmi. PDF DJP [12] belum terbaca penuh karena teksnya terkompresi.
- Ada tidaknya digit pemeriksa.
- Status NPWP 15 digit pada 2026.

## P2. Kartu kredit dan debit

### P2.1 Dasar sebagai data pribadi

- Kartu **kredit**: disebut eksplisit di Penjelasan Pasal 4 ayat (2) huruf f UU PDP (data keuangan pribadi) [31]. Kategori **spesifik**.
- Kartu **debit**: tidak disebut namanya. Masuk lewat tafsiran "termasuk namun tidak terbatas" ⚠️.
- NIST [35] hlm. 14 mencantumkan "financial account or credit card number".

### P2.2 Format

- **Bank Indonesia [32]:** kartu kredit dan kartu ATM/debet sama-sama "Nomor kartu yang terdiri atas 16 digit". Satu-satunya sumber resmi Indonesia yang ditemukan. "Nomor verifikasi" 3 digit di belakang **bukan** nomor kartu.
- **Standar internasional** (lewat ringkasan [33], standar ISO tidak dibaca): PAN maksimum 19 digit, awalnya IIN (6 atau 8 digit) dengan digit pertama MII (3 perjalanan dan hiburan, 4 dan 5 perbankan, 6 perdagangan dan perbankan), digit terakhir hasil algoritma Luhn.
- **Luhn [34]:** dari digit paling kanan lipat-gandakan setiap digit kedua (kurangi 9 bila lebih dari 9), jumlahkan, sah bila habis dibagi 10. Contoh: `17893729974` sah. Luhn mendeteksi salah ketik, bukan alat keamanan.

### P2.3 Peluang lolos kebetulan (simulasi 200.000 angka acak 16 digit)

| Syarat | Lolos |
|---|---|
| Lolos Luhn | ±10,1% |
| Lolos Luhn dan digit pertama 3–6 | ±4,0% |

Jauh lebih besar daripada NIK `high` (±0,05%), jadi kartu tanpa bukti tambahan lebih rentan menghasilkan temuan palsu.

### P2.4 Apakah kartu Indonesia berpola sama? (dicari 12 Nov. 2026)

| Jenis kartu | Temuan | Kepastian |
|---|---|---|
| Kredit dan debit, jaringan internasional (Visa, Mastercard) | Rentang kartu bank Indonesia di data komunitas [40] berawalan `4` (Visa, 16 rentang) dan `5` (Mastercard, 11 rentang), 6 digit, sesuai pola MII internasional | Sedang. Hanya 27 rentang dari 12 bank, data tidak lengkap ⚠️ |
| Kartu berlogo GPN (debit nasional) | **Tidak ditemukan sumber** yang menyebut awalan atau pola nomornya. Penjelasan PBI 19/8/2017 [41] tidak memuat aturan nomor kartu. Bank Indonesia hanya menyebut 16 digit [32]. Wikipedia GPN tidak memuat BIN | Tidak diketahui |
| Lolos Luhn | Standar ISO mensyaratkannya untuk PAN [33][34]. Untuk kartu GPN **tidak terverifikasi** ⚠️ | Tidak diketahui untuk GPN |

- Kesimpulan: kartu kredit dan debit yang diterbitkan di Indonesia dengan logo jaringan internasional **tampak berpola sama** dengan pola internasional. Untuk kartu debit GPN murni, **tidak bisa dipastikan**.
- Digit pertama 9 adalah MII untuk badan standar nasional [33]. Kartu skema nasional mungkin memakainya ⚠️ (dugaan saya, tidak bersumber), sehingga batasan "digit pertama 3–6" berisiko melewatkan kartu GPN.
- **Penanganan bila nanti dikerjakan, tanpa menunggu riset itu:** kartu dengan digit pertama di luar 3–6 tetap `low`, tetapi aturan konteks menaikkannya ke `medium` bila ada kata `kartu`, `debit`, `kredit`, atau `atm` di baris yang sama. Jadi kartu GPN tetap tertangkap bila konteksnya jelas, dan kartu tanpa konteks tidak membanjiri laporan.
- Rentang BIN GPN mungkin dipegang lembaga standar (ASPI menurut hasil pencarian, belum diverifikasi ⚠️). Dokumennya tidak ditemukan.

### P2.5 Usulan tingkat bukti (belum disetujui ⚠️)

| Tingkat | Syarat |
|---|---|
| `high` | 16 digit, lolos Luhn, digit pertama 3–6, **dan** ada kata konteks (`kartu`, `card`, `cc`, `visa`, `mastercard`, `kredit`, `debit`, `pan`) |
| `medium` | Sama, tanpa konteks (±4%) |
| `low` | Gagal Luhn atau digit pertama lain. Tidak dilaporkan |

- Pemisah spasi atau strip tiap 4 digit adalah dugaan umum, tidak ada di [32] ⚠️. Daftar kata konteks disusun sendiri.
- Bertabrakan dengan NIK: dedup memilih tingkat tertinggi, lalu yang terpanjang, lalu urutan rule. NIK `high` mengalahkan kartu `medium`.
- `medium` melaporkan ±4% angka 16 digit acak, jadi repo yang banyak berisi ID 16 digit akan menghasilkan banyak temuan. Perlu diukur.
- Contoh sintetis (buatan generator, bukan kartu asli ⚠️): `4000526018159083` (`medium`), `4000526018159084` (`low`, gagal Luhn), `5100301661318600` (`medium`), `9100301661318601` (`low`, digit pertama 9).

### P2.6 Belum diketahui (⚠️)

- Rentang BIN resmi kartu GPN. Teks PBI 19/8/PBI/2017 sendiri tidak dibaca (hanya penjelasannya [41]), dan standar ISO/IEC 7812 serta daftar IIN per jaringan juga tidak.
- Kartu 15 digit (misalnya American Express) atau 13–19 digit. MVP mengikuti 16 digit dari [32].
- Apakah nomor rekening 10–16 digit sering lolos Luhn secara kebetulan.

### P2.7 Cara menghitung peluang kebetulan kartu

| Pemeriksaan | Perhitungan | Hasil |
|---|---|---|
| Lolos Luhn | Untuk 15 digit pertama mana pun, tepat **satu** dari 10 kemungkinan digit terakhir membuat jumlah habis dibagi 10 [34]. Jadi 1/10 | **10%** |
| Digit pertama 3–6 | 4 dari 10 digit | 40% |
| Keduanya | 10% × 40% (bebas: digit pertama tidak memengaruhi digit terakhir yang menentukan Luhn) | **4%** |

Simulasi 200.000 angka acak 16 digit memberi 10,1% dan 4,0%. Cocok dengan rumus.

## P3. Identifier perorangan lain (kandidat)

Daftar ini **belum diriset**. Panjang dan struktur berasal dari pengetahuan umum dan perlu diverifikasi sebelum dipakai ⚠️.

### P3.1 Bernomor dengan struktur (bisa dideteksi dengan pola dan pemeriksaan)

| Identifier | Perkiraan bentuk ⚠️ | Catatan |
|---|---|---|
| NIP PNS | 18 digit, memuat tanggal lahir, bulan dan tahun pengangkatan, jenis kelamin, nomor urut | Strukturnya paling kaya dan paling mirip NIK. Kandidat pertama |
| Nomor BPJS Kesehatan | Nomor kartu 13 digit masih ada, tetapi **NIK sudah menjadi nomor identitas peserta sejak 26 Jan. 2022** menurut ringkasan hasil pencarian (berita, belum dibaca, peraturan turunannya tidak ditemukan ⚠️) | Prioritas rendah: identitas utamanya sudah NIK, yang tercakup rule NIK |
| Nomor BPJS Ketenagakerjaan | 11 digit | Sumber yang dicari: BPJS |
| NISN, NUPTK | 10 digit dan 16 digit | NUPTK berbentuk 16 digit, bisa tertukar dengan NIK |
| Nomor SIM | 12 digit | Sumber yang dicari: Korlantas |
| Nomor paspor | Huruf diikuti angka | Sumber yang dicari: Ditjen Imigrasi |
| Nomor rekening bank | 10–16 digit, tanpa standar checksum | Panjang berbeda tiap bank |
| Nomor kendaraan, STNK, BPKB | Huruf dan angka | - |
| Nomor rekam medis | Bervariasi per fasilitas | Kategori kesehatan (spesifik) |

### P3.2 Tanpa nomor (perlu kunci, kamus, atau NER)

| Data | Sumber di UU PDP [31] |
|---|---|
| Nama lengkap, jenis kelamin, kewarganegaraan, agama, status perkawinan | Pasal 4 ayat (3) huruf a–e |
| Tanggal lahir, tempat lahir, alamat, pekerjaan, nama ibu kandung | Tidak disebut. Termasuk tafsiran "dikombinasikan untuk mengidentifikasi" huruf f ⚠️ |
| Data kesehatan, biometrik, genetika, catatan kejahatan, data anak | Pasal 4 ayat (2), data **spesifik** |
| IP Address, koordinat lokasi, ID perangkat | IP Address disebut eksplisit di Penjelasan. IP **tidak dikerjakan dulu** |

Sebagian besar hanya bisa dideteksi lewat nama kolom, nilai tertutup (misalnya agama), atau NER. Itu pekerjaan tahap 2.

### P3.3 Prioritas menurut risiko penipuan keuangan (usulan, 12 Nov. 2026)

Dipilih dari sudut: data apa yang paling sering dipakai untuk penipuan, pembukaan rekening, atau pinjaman atas nama orang lain. Daftar ini penilaian saya, bukan hasil riset ⚠️.

| Prioritas | Data | Alasan | Status |
|---|---|---|---|
| Sudah masuk | NIK (+ KK, NPWP orang pribadi), nomor HP, email | Bahan utama verifikasi identitas dan penerimaan OTP | Bagian 2–7 |
| Diparkir | Kartu kredit dan debit | Langsung finansial | Bagian 8 |
| **Berikutnya** | **Nomor rekening bank dan virtual account** | Langsung finansial. Panjang berbeda tiap bank dan tanpa checksum standar, jadi deteksi bergantung pada kata konteks (`rekening`, `no rek`, `VA`) | Belum diriset |
| **Berikutnya** | Nomor paspor | Dokumen identitas yang dipakai verifikasi | Belum diriset |
| Lebih rendah | NIP PNS, BPJS, NISN, NUPTK, SIM | Kurang berkaitan dengan penipuan keuangan, atau identitas utamanya sudah NIK | Belum diriset |
| Di luar kemampuan teks | Foto KTP, KK, paspor, dan swafoto | Berupa gambar, sedangkan PRISM hanya memindai teks. Gagasan murah untuk tahap 2: temuan tingkat berkas berdasarkan nama dan ekstensi (misalnya `ktp.jpg`, `kk.pdf`), tanpa membaca isi gambar ⚠️ | Gagasan |
| Di luar cakupan | Kode OTP, PIN, CVV, kata sandi | Kredensial, bukan data pribadi menurut keputusan cakupan | - |

## P4. Tabel parkir

Dibuka lagi bila hasil uji menunjukkan perlu.

| Hal | Yang diketahui | Yang belum | Dampak bila diabaikan |
|---|---|---|---|
| NIK WNI di luar negeri (awalan `99`) | PP 40/2019 Pasal 32 [5]: 6 digit pertama = `99` + 3 digit kode negara + 1 digit kode Perwakilan RI | Daftar kode negara dan kode Perwakilan RI | NIK berawalan `99` jatuh ke `low` (tidak terdeteksi). Jumlah diperkirakan kecil ⚠️ |
| NIK orang asing (WNA) | - | Ada tidaknya dan bentuknya | Tidak terdeteksi bila bentuknya berbeda |
| Peraturan Menteri tata cara penerbitan NIK | Disebut di Pasal 31 ayat 7 [5] | Judul dan isi | Tidak ada, struktur cukup dari [5] |
| Kode kabupaten/kota/kecamatan satu per satu | Jumlah per provinsi cocok dengan [1] | Lampiran B dan C Kepmendagri 2138/2025 tidak diperoleh | Kode keliru bisa lolos atau tertolak |
| Keputusan menteri lebih baru dari 2025 | - | Belum dicari | Daftar wilayah ketinggalan |
| NOP PBB | 18 digit dengan kode provinsi dan kabupaten/kota di depan; kecamatan 3 digit [15] | [15] sudah tidak berlaku. Aturan penggantinya tidak ditemukan | Tidak terdeteksi. Kaitan dengan UU PDP belum dikaji |
| Nomor akta kelahiran | Contoh beredar `3578-LU-28112012-0018` (dugaan, dari media yang tidak terbaca) | Format resmi dan arti `LU`, `LT` | Tidak terdeteksi |
| IP Address | Disebut eksplisit di Penjelasan Pasal 4 ayat (3) huruf f [31] | Keputusan cakupan | Tidak terdeteksi. Risiko temuan palsu tinggi bila dimasukkan |
| NPWP 15 digit (format lama) | Dokumen lama tetap sah [7]. Bentuk bertitik `XX.XXX.XXX.X-XXX.XXX` dari contoh [13] | Struktur segmen dari sumber resmi | NPWP perorangan format lama di berkas lama tidak terdeteksi. Bagian P1.2, P1.3 |
| Kartu kredit dan debit | 16 digit [32], Luhn, polanya mirip pola internasional untuk Visa dan Mastercard [40] | Pola kartu debit GPN, dan keputusan tingkat `medium` | Nomor kartu tidak terdeteksi. Bagian P2 |
| Identifier lain (rekening bank, virtual account, paspor, NIP, BPJS, SIM) | Daftar kandidat di bagian P3 | Format dan sumber resmi | Tidak terdeteksi. Bagian P3 |

## Sumber

Semua sumber ada di [referensi.md](referensi.md).

| Kelompok | Nomor |
|---|---|
| Dibaca langsung (dokumen resmi) | [5], [6], [7], [8], [31], [35] |
| Resmi, dibaca lewat ringkasan alat fetch | [9], [10], [18], [19], [32], [36] |
| Resmi, dibaca setelah diekstrak, tidak memuat aturan nomor kartu | [41] |
| Resmi, dibaca lewat OCR otomatis (PDF gambar) | [12], [13], [20] |
| Resmi tetapi sudah tidak berlaku menurut DDTC | [15] |
| Data komunitas | [40] |
| Tidak resmi (media, Wikipedia, opini) | [11], [16], [17], [33], [34], [37], [38], [39] |
