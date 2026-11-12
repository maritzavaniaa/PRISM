# Dasar Hukum Cakupan PII: UU PDP Pasal 4

> Keluaran riset nomor 4: apa yang dikatakan teks resmi UU PDP tentang jenis data pribadi, dan apa artinya bagi cakupan MVP PRISM.
> Sumber: UU Nomor 27 Tahun 2022 [31]. Semua kutipan dibaca dari PDF resmi BPK. Butir c sampai f ayat (3) dicek langsung pada gambar halaman.
> ⚠️ = interpretasi saya atau belum diverifikasi.

## 1. Teks yang dibaca

**Pasal 1 butir 1 [31]:** Data Pribadi adalah data tentang orang perseorangan yang teridentifikasi atau dapat diidentifikasi secara tersendiri atau dikombinasi dengan informasi lainnya baik secara langsung maupun tidak langsung melalui sistem elektronik atau nonelektronik.

**Pasal 4 ayat (1) [31]:** Data Pribadi terdiri atas (a) data pribadi yang bersifat spesifik dan (b) data pribadi yang bersifat umum.

**Pasal 4 ayat (2): spesifik [31]**

| Huruf | Isi |
|---|---|
| a | data dan informasi kesehatan |
| b | data biometrik |
| c | data genetika |
| d | catatan kejahatan |
| e | data anak |
| f | data keuangan pribadi |
| g | data lainnya sesuai dengan ketentuan peraturan perundang-undangan |

**Pasal 4 ayat (3): umum [31]**

| Huruf | Isi |
|---|---|
| a | nama lengkap |
| b | jenis kelamin |
| c | kewarganegaraan |
| d | agama |
| e | status perkawinan |
| f | Data Pribadi yang dikombinasikan untuk mengidentifikasi seseorang |

Daftar butir a sampai e sama dengan yang kamu tempel sebelumnya.

## 2. Penjelasan yang paling berpengaruh

| Bagian | Isi penjelasan [31] |
|---|---|
| Pasal 4 ayat (3) huruf f | "Yang dimaksud dengan 'Data Pribadi yang dikombinasikan untuk mengidentifikasi seseorang' antara lain **nomor telepon seluler dan IP Address**." |
| Pasal 4 ayat (2) huruf f | "Yang dimaksud dengan 'data keuangan pribadi' adalah termasuk namun tidak terbatas kepada data jumlah simpanan pada bank termasuk tabungan, deposito, dan **data kartu kredit**." |
| Pasal 4 ayat (2) huruf e (data anak) | Cukup jelas |

Dua frasa "antara lain" dan "termasuk namun tidak terbatas" berarti daftarnya **tidak tertutup**.

## 3. Artinya bagi MVP

| Jenis di MVP | Disebut dalam teks UU? | Dasar | Kekuatan |
|---|---|---|---|
| Nomor HP | **Ya**, eksplisit | Penjelasan Pasal 4 ayat (3) huruf f | Kuat |
| NIK | Tidak disebut | Pasal 1 butir 1 (dapat diidentifikasi, termasuk bila dikombinasi) dan huruf f ("antara lain") | Tafsiran ⚠️ |
| NPWP | Tidak disebut | Sama seperti NIK | Tafsiran ⚠️ |
| Email | Tidak disebut | Sama seperti NIK | Tafsiran ⚠️ |

- Kalimat di mvp-t5.md "Keempatnya termasuk data pribadi umum butir f" sudah tepat sebagai tafsiran, tetapi **hanya nomor HP** yang disebut teks. NIK, NPWP, dan email perlu ditulis sebagai tafsiran berdasarkan definisi di Pasal 1 butir 1.
- Argumen untuk tafsiran itu: NIK adalah nomor identitas tunggal untuk semua urusan pelayanan publik (PP 40/2019 Pasal 30 [5]), jadi ia pasti dapat mengidentifikasi seseorang. Untuk NPWP orang pribadi yang sama dengan NIK (lihat bagian 4 [format-pii-indonesia.md](format-pii-indonesia.md) dan P1.4 [format-pii-parkir.md](format-pii-parkir.md)) argumennya sama. Email bergantung pada isinya: alamat pribadi mengidentifikasi seseorang, alamat generik badan hukum belum tentu ⚠️.
- Jenis lain di kriteria "umum" (nama lengkap, jenis kelamin, kewarganegaraan, agama, status perkawinan) disebut eksplisit dan sudah dijadwalkan di tahap 2.

## 4. Dua jenis data yang eksplisit di teks UU tetapi belum ada di MVP awal

| Jenis | Disebut di | Keputusan (11 Nov. 2026) | Catatan |
|---|---|---|---|
| **IP Address** | Penjelasan Pasal 4 ayat (3) huruf f | **Tidak dikerjakan dulu** | Sangat sering ada di konfigurasi dan log. Risiko temuan palsu tinggi: alamat privat (`192.168.x.x`, `10.x.x.x`), `127.0.0.1`, nomor versi seperti `1.2.3.4` |
| **Kartu kredit** | Penjelasan Pasal 4 ayat (2) huruf f (data keuangan pribadi) | **Diparkir** (12 Nov. 2026) | Format sudah diriset di [format-pii-parkir.md](format-pii-parkir.md) bagian P2. Kategori **spesifik**, risiko lebih besar menurut Penjelasan ayat (1) huruf a |
| **Kartu debit** | Tidak disebut namanya. Penjelasan memakai "termasuk namun tidak terbatas" | Ikut kartu kredit, lewat tafsiran ⚠️ | Format sama (16 digit menurut Bank Indonesia) |

## 4a. Bukti pendukung dari luar UU PDP

Teks UU hanya menyebut nomor HP dan IP Address sebagai contoh butir f. Pembanding internasional berikut menunjukkan jenis-jenis lain diperlakukan sebagai PII di praktik umum. **Ini bukan hukum Indonesia**, hanya penguat untuk pembahasan.

| Jenis | NIST SP 800-122 [35] | European Commission [36] |
|---|---|---|
| Nomor HP | "Telephone numbers, including mobile, business, and personal numbers" (hlm. 14) | Tidak disebut |
| Email | "Address information, such as street address or email address" (hlm. 14) | Pribadi: `name.surname@company.com`. **Bukan** data pribadi: `info@company.com` |
| Nomor identitas | "taxpayer identification number" dan "financial account or credit card number" (hlm. 14) | "an identification card number". Bukan: "a company registration number" |
| IP Address | "Internet Protocol (IP) or Media Access Control (MAC) address" yang secara konsisten terkait satu orang atau kelompok kecil (hlm. 14) | "an Internet Protocol (IP) address" |

- Catatan penting dari [35] hlm. 17: PII yang memang boleh dipublikasikan (misalnya nomor telepon kantor di direktori pegawai) tidak perlu dilindungi kerahasiaannya. Dari [36]: alamat email generik milik badan bukan data pribadi. Dua poin ini mendukung bahwa kecocokan pola belum tentu kebocoran, dan konteks serta jenis alamat perlu dipertimbangkan.
- Beberapa tulisan sekunder menyebut UU PDP "secara tegas" memuat email. Teks resmi tidak menyebut email ⚠️. Jangan dikutip.

## 5. Hal lain yang relevan

- Pasal 2 ayat (2): UU tidak berlaku untuk pemrosesan data pribadi oleh orang perseorangan dalam kegiatan pribadi atau rumah tangga [31]. Pengguna PRISM adalah tim pengembang atau organisasi, jadi dianggap di luar pengecualian ⚠️ (interpretasi).
- Pasal 4 ayat (2) huruf g: data spesifik juga mencakup data lain menurut peraturan perundang-undangan. Peraturan pelaksana tidak dicari.
- Teks resmi hanya memberi daftar jenis, tidak memberi format. Format NIK, HP, dan sebagainya tetap dari sumber lain (bagian 2 sampai 7 format-pii-indonesia.md).

## 6. Belum diketahui

- Peraturan pelaksana UU PDP (misalnya Peraturan Pemerintah) yang bisa menambah atau merinci jenis data.
- Apakah ada putusan atau tafsiran resmi yang menyebut NIK, NPWP, atau email sebagai data pribadi umum.
- Putusan MK 151/PUU-XXII/2024 hanya menyangkut Pasal 53 ayat (1) huruf b menurut ringkasan pencarian. Tidak dibaca langsung.
