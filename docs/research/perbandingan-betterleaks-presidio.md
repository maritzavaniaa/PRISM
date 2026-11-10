# Perbandingan Betterleaks dan Presidio: Langkah, Metode, Research Gap, dan Relevansi untuk PRISM

> Dasar: [tool-betterleaks.md](tool-betterleaks.md) dan [tool-presidio.md](tool-presidio.md) (dicek ke dokumentasi resmi pada 10 November 2026). File ini hanya merangkum dan menganalisis. Tidak ada fakta baru dari luar kedua dokumen itu.
> Tanda ⚠️ = belum terkonfirmasi atau belum diuji. Bagian berlabel **Analisis sendiri** adalah kesimpulan penulis, bukan kutipan dokumentasi.
> Kebutuhan utama PRISM: **T3** (PII tercetak di log keluaran tes, skenario S3) dan **T5** (PII atau token ter-push ke repositori, skenario S1 dan S2). Lihat bagian 7.5 dan 10.1 di [riset-privacy-scanner-cicd.md](riset-privacy-scanner-cicd.md).

---

## 1. Gambaran satu tabel

| Aspek | Betterleaks | Presidio |
|---|---|---|
| Yang dicari | **Secret**: token API, password, kunci | **PII**: nama, email, telepon, kartu kredit, ID nasional |
| Bentuk | Program CLI dan library Go (MIT) | Library Python (MIT), opsi REST API lewat Docker |
| Yang dipindai | File, riwayat git, GitHub, S3, container, stdin | Teks (string) yang diberikan pemanggil |
| Cara menemukan | Regex, keyword, filter statistik | Regex, model NER, checksum, kata konteks |
| Hasil | Teks, JSON, atau JSONL, plus exit code | Objek di memori (`RecognizerResult`) |
| Menggagalkan CI sendiri | Ya, exit code `1` | Tidak, perlu pembungkus |
| Status | v2 masih rc.7, stabil v1.10.0 | Proyek komunitas, tanpa SLA |

Analogi: Betterleaks seperti **satpam yang memeriksa seluruh gedung** lalu membuat laporan. Presidio seperti **ahli yang menilai satu dokumen** yang diserahkan, dan pencatatan hasilnya dilakukan pemanggil.

---

## 2. Langkah Betterleaks: dari pemindaian sampai laporan

Alurnya berupa saringan bertingkat. Tahap awal murah dan cepat, tahap akhir lebih teliti.

| No | Tahap | Cara kerja singkat | Output |
|---|---|---|---|
| 1 | Source | Membaca data dari sumbernya (`fs`, `git`, `github`, `s3`, `container`, `stdin`) lalu memecahnya menjadi fragment, misalnya satu patch commit | Kumpulan fragment |
| 2 | Prefilter | Aturan Expr yang membuang seluruh file atau commit sebelum isinya dibaca. Hanya melihat path dan penulis | Fragment yang lolos |
| 3 | Keyword | Fragment hanya diteruskan bila memuat kata kunci rule (Aho-Corasick) | Fragment berpotensi relevan |
| 4 | Regex | Mencocokkan pola, misalnya `ghp_` diikuti 36 karakter. README menyebut RE2 ⚠️ | Daftar kandidat secret |
| 5 | Filter | Membuang kandidat palsu dengan entropi, BPE/token efficiency, dan konteks | Kandidat lebih bersih |
| 6 | Confidence | Memberi label low, medium, atau high | Label keyakinan |
| 7 | Validasi (opsional, `-v`) | Mencoba secret ke server penyedianya lewat HTTP | valid, invalid, revoked, dst. |
| 8 | Analisis (opsional, `-a`) | Mencari identitas dan hak akses pemilik secret | Identitas dan tingkat keparahan |
| 9 | Revoke (perintah terpisah) | `betterleaks revoke` mencabut secret. Pemindaian tidak pernah mencabut | Secret dicabut |

**Pelaporan:**
- Default berupa teks di terminal. `--jsonl` atau `-o file.json` untuk berkas.
- `--redact` menyamarkan nilai secret.
- Exit code `1` bila ada temuan.
- Betterleaks tidak menyimpan hasil sendiri. Di CI, berkas laporan harus diunggah sebagai artifact.
- Pengecualian lewat komentar `betterleaks:allow` atau `.betterleaksignore` (berisi SHA-256 dari nilai secret).

## 3. Langkah Presidio: dari analisis sampai laporan

Presidio **bukan lima tahap berurutan**. Beberapa detektor (*recognizer*) berjalan sendiri-sendiri, lalu hasilnya digabung dan dinilai. Urutan nyata dari kode `analyze()`:

| No | Tahap | Cara kerja singkat | Output |
|---|---|---|---|
| 1 | NLP engine | Teks dipecah menjadi token, lemma, dan entitas (spaCy secara default) | `NlpArtifacts` |
| 2 | Recognizer | Semua detektor berjalan: regex, NER, validasi checksum, logika custom | Kandidat dengan skor awal |
| 3 | Context enhancement | Skor naik bila ada kata petunjuk di sekitar kandidat | Skor yang disesuaikan |
| 4 | Filter skor | Kandidat di bawah `score_threshold` dibuang | Kandidat cukup yakin |
| 5 | Deduplikasi | Hasil yang tumpang tindih dirapikan | Daftar bersih |
| 6 | Allow list (opsional) | Nilai yang diizinkan tidak dilaporkan | Daftar akhir |
| 7 | Anonymizer (modul terpisah, opsional) | Menyamarkan PII yang sudah ditemukan: replace, redact, mask, hash, encrypt | Teks baru (`EngineResult`) |

**Pelaporan:**
- Output utama adalah daftar `RecognizerResult` berisi `entity_type`, `start`, `end`, `score`. **Tanpa nilai PII-nya.**
- Hasil hanya ada di memori. Tidak ada file, nomor baris, atau exit code.
- Log alasan keputusan (`log_decision_process=True`) mati secara default dan tercetak ke stdout. ⚠️ Kemungkinan memuat token teks asli, belum diuji.

---

## 4. Perbandingan sejajar per fungsi

| Fungsi | Betterleaks | Presidio |
|---|---|---|
| Menentukan yang dibaca | Prefilter (path, penulis) | Pemanggil memilih teks dan entity |
| Penyaringan cepat | Keyword Aho-Corasick | Tidak ada. Semua recognizer terpilih berjalan |
| Pencocokan pola | Regex per rule | Regex per `PatternRecognizer` |
| Pengenalan tanpa pola tetap | Tidak ada | NER (nama, lokasi) |
| Kurangi false positive | Entropi dan BPE (apakah string tampak acak) | Checksum dan `validate_result` (apakah nilai valid), kata konteks |
| Pemeriksaan keaslian | Opsional, lewat panggilan ke penyedia | Tidak ada. Hanya cek format |
| Penilaian | Confidence low, medium, high | Skor numerik, lalu `score_threshold` |
| Pengecualian | `betterleaks:allow`, `.betterleaksignore` (hash nilai) | `allow_list` (`allow_list_match` default `exact`) |
| Lokasi temuan | Path file dan baris | Offset karakter dalam teks |
| Bentuk laporan | Teks, JSON, JSONL | Objek Python |
| Keputusan lulus atau gagal | Exit code `1` bawaan | Tidak ada |
| Penyamaran nilai | `--redact`, fingerprint SHA-256 atau HMAC | Operator Anonymizer (`mask`, `hash` dengan salt acak, `encrypt`) |
| Penyimpanan hasil | Tidak ada. Pengguna mengunggah artifact | Tidak ada. Pengguna menyimpan |

---

## 5. Metode teknis: cara kerja dan output

| Metode | Dipakai oleh | Cara kerja (bahasa mudah) | Output |
|---|---|---|---|
| **Regex (RE2)** | Betterleaks | Mencocokkan pola teks. RE2 menjamin waktu proses linear, tanpa lookahead dan backreference | Potongan teks yang cocok, sebagai kandidat |
| **Keyword Aho-Corasick** | Betterleaks | Mencari banyak kata kunci sekaligus dalam satu kali baca. Regex mahal hanya dijalankan bila kata kuncinya muncul | Keputusan: fragment diteruskan atau dilewati |
| **Prefilter dan Filter Expr** | Betterleaks | Bahasa ekspresi kecil untuk membuang file atau kandidat. Prefilter melihat path dan penulis. Filter melihat nilai temuan | `true` = dibuang, `false` = dipertahankan |
| **Entropi Shannon** | Betterleaks | Mengukur keacakan string. `x9Kf3qLm2` memiliki entropi tinggi dan kemungkinan secret. `passwordpassword` rendah | Angka keacakan, dibandingkan dengan ambang |
| **BPE / token efficiency** | Betterleaks | Memecah string menjadi token seperti model bahasa. Bahasa alami terpecah efisien (rasio rendah), string acak tidak. Menyaring false positive berupa kalimat | Rasio token, dibandingkan dengan ambang |
| **Validasi HTTP** | Betterleaks | Mengirim secret ke API penyedia untuk melihat apakah masih aktif. Mati secara default | Status valid, invalid, revoked, unknown, error |
| **Fingerprint** | Betterleaks | Hash SHA-256 (atau HMAC) dari nilai secret sebagai identitas temuan | String hash, dipakai di `.betterleaksignore` |
| **PatternRecognizer (regex + deny list)** | Presidio | Regex dengan skor awal sesuai kekuatan pola. Kode pos 5 digit hanya 0,01 | Kandidat dengan skor |
| **Validasi / checksum** (`validate_result`) | Presidio | Kode Python memeriksa nilai, misalnya checksum kartu kredit. `True` = skor maksimum, `False` = dibuang, `None` = skor tetap | Skor dinaikkan atau kandidat dibuang |
| **invalidate_result** | Presidio | Pemeriksaan kedua. `True` memaksa dibuang walaupun lolos validasi | Kandidat dibuang |
| **NER (spaCy, Stanza, Transformers)** | Presidio | Model AI mengenali nama orang, lokasi, dan NRP dari konteks kalimat | Entitas PERSON, LOCATION, NRP dengan skor |
| **Context enhancer** | Presidio | Membandingkan lemma kata di sekitar kandidat dengan kata petunjuk (`phone`, `telepon`). Cocok = skor naik (default faktor 0,35, minimum 0,4) | Skor yang lebih tinggi |
| **Score threshold** | Presidio | Membuang semua kandidat di bawah ambang | Daftar kandidat yang bertahan |
| **Allow list** | Presidio | Nilai yang diizinkan (default cocok `exact`) dikeluarkan dari hasil | Daftar akhir tanpa nilai yang diizinkan |
| **Anonymizer** | Presidio | Mengganti PII dengan operator. `hash` memakai salt acak sehingga hasilnya berbeda tiap panggilan | Teks baru yang disamarkan |
| **Decision process log** | Presidio | Mencatat alasan skor: skor awal, tambahan konteks, hasil validasi | Trace di stdout (opsional) |

---

## 6. Research gap per tool

> **Analisis sendiri.** Kekuatan argumen dan tingkat bukti mengikuti bagian 10 dan 12 pada dokumen tool masing-masing.

### 6.1 Betterleaks

| No | Gap | Bukti | Kekuatan | Status |
|---|---|---|---|---|
| G1 | Tidak ada aturan PII Indonesia (NIK, NPWP, HP +62) bawaan | README tidak menyebut PII | Sedang | ⚠️ Daftar rule bawaan belum dibaca. Tulis "tidak ditemukan", bukan "tidak ada" |
| G2 | Tidak ada validasi semantik PII (tanggal lahir NIK, kode wilayah) | Fungsi filter hanya regex, entropi, token ratio, dan pencocokan string | Tinggi bila terbukti | ⚠️ Expr mungkin cukup untuk aritmetika tanggal sederhana. Harus diuji |
| G3 | Fingerprint dan laporan dirancang untuk secret, bukan PII. SHA-256 tanpa kunci pada NIK atau HP bisa ditebak lewat brute force | Fingerprint = SHA-256 byte secret, HMAC opsional | Sedang sampai tinggi | ⚠️ Belum dicek apa yang tertulis di laporan tanpa `--redact` |
| G4 | Pemindaian log tersedia secara mekanis (`stdin`, `fs`), tetapi tidak ada rule PII dan tidak ada panduan untuk log CI yang sedang berjalan | `scanning.md` | Sedang | ⚠️ Log job yang sedang berjalan belum diuji |
| G5 | v2 belum stabil (rc.7), skema JSON dan flag berubah dari v1, SARIF dihapus | `v2_migration.md`, Releases | Rendah (risiko, bukan keunggulan PRISM) | Pin versi saat eksperimen |
| G6 | Tidak ada GitHub Action resmi yang ditemukan | Pencarian web | Rendah | ⚠️ Perlu dicek ulang. Pola `run` dengan binary tetap bisa dipakai |

### 6.2 Presidio

| No | Gap | Bukti | Kekuatan | Status |
|---|---|---|---|---|
| P1 | Tidak ada recognizer PII Indonesia (NIK, NPWP) | Tabel Supported Entities | **Tinggi, terverifikasi** | Argumen paling aman |
| P2 | Bukan alat CI/CD: tidak ada CLI, penelusuran berkas, nomor baris, laporan, atau exit code | Presidio menganalisis string dan mengembalikan objek | **Tinggi** | Klaimnya integrasi, bukan algoritma deteksi |
| P3 | Nomor +62 tidak terdeteksi secara default | `DEFAULT_SUPPORTED_REGIONS` tidak memuat ID (branch `main`) | Sedang | ⚠️ Uji `supported_regions=("ID",)` agar adil |
| P4 | Dependensi berat: NLP engine dan model spaCy (`en_core_web_lg` default) | Halaman Installation | Sedang | ⚠️ Ukuran dan waktu instal di runner harus diukur |
| P5 | Konfigurasi bawaan hanya Inggris. Kata konteks Indonesia (`nik`, `ktp`, `telepon`) harus dibuat sendiri | Halaman Languages | Sedang | ⚠️ Model spaCy/Stanza Bahasa Indonesia belum dicek |
| P6 | Tidak mendeteksi token atau kredensial | Entity bawaan tidak memuat pola API key | Sedang | Skenario S2 tidak tercakup |
| P7 | Hash bawaan memakai salt acak, sehingga hasil tidak stabil antar-run | Dokumentasi Anonymizer | Rendah sampai sedang | Tidak cocok dengan NFR-07 tanpa salt tetap |
| P8 | Trace decision process mungkin mencetak teks asli ke stdout | Deskripsi field trace | Rendah | ⚠️ Inferensi, belum diuji |

### 6.3 Gap bersama (inti research gap PRISM)

| Gap | Betterleaks | Presidio |
|---|---|---|
| Aturan PII Indonesia siap pakai | Tidak ditemukan ⚠️ | Tidak ada |
| Validasi semantik NIK | Terbatas ke Expr (belum diuji) | Bisa lewat `validate_result`, tetapi harus ditulis sendiri |
| Gating CI + laporan dengan nilai disamarkan, dalam satu paket | Gating ada, laporan bukan untuk PII | Tidak ada keduanya |
| Ringan dan mudah dipasang di runner | Ya (binary tunggal) | Berat (model NLP) ⚠️ belum diukur |

---

## 7. Relevansi untuk T3 dan T5

> **Analisis sendiri.** Skenario mengikuti bagian 10.1 riset utama: S1 = PII di berkas repo (T5), S2 = token di commit (T5), S3 = PII di log keluaran tes (T3). Cakupan prototipe: berkas di folder repo dan berkas log lewat argumen, bukan riwayat git.

### 7.1 Dukungan per skenario

| Skenario | Threat | Betterleaks | Presidio |
|---|---|---|---|
| **S1**: PII di berkas repo | T5 | ⚠️ Mekanisme `fs` ada, tetapi PII hanya lewat rule custom tanpa validasi bawaan | ⚠️ Mesin deteksi cocok (recognizer + validasi), tetapi butuh pembungkus penelusur berkas dan recognizer Indonesia |
| **S2**: token di commit | T5 | ✅ **Sangat baik.** Rule provider matang | ❌ Tidak dirancang untuk itu |
| **S3**: PII di log keluaran tes | T3 | ⚠️ Mekanisme ada (`fs` pada berkas log, `stdin`), rule PII tidak ada | ✅ Cocok secara mekanis (log adalah teks biasa), butuh pembungkus |

### 7.2 Dukungan terhadap requirement

| Requirement | Betterleaks | Presidio |
|---|---|---|
| FR-01: periksa berkas (T5) | ✅ Bawaan | ❌ Perlu pembungkus |
| FR-02: periksa keluaran pipeline (T3) | ⚠️ Lewat `fs` atau `stdin` | ⚠️ Perlu pembungkus, teks log mudah dianalisis |
| FR-03: jenis temuan per kategori | ✅ `rule_id` | ✅ `entity_type` |
| FR-04: lokasi temuan | ✅ Path dan baris | ⚠️ Offset karakter, perlu dikonversi ke baris |
| FR-05: ringkasan hasil | ⚠️ Metadata `scan` di JSONL | ❌ Buat sendiri |
| FR-06: status untuk pipeline | ✅ Exit code `1` | ❌ Buat sendiri |
| NFR-01: integrasi mudah | ✅ Binary tunggal | ⚠️ Python + model NLP |
| NFR-03: efektivitas deteksi PII | ⚠️ Tergantung rule custom | ⚠️ Tergantung recognizer custom |
| NFR-04: laporan tidak menampilkan PII utuh | ⚠️ `--redact`, perlu dicek isi laporan | ✅ Hasil hanya offset dan skor |
| NFR-07: hasil konsisten | ✅ Deterministik | ⚠️ Deterministik, tetapi `hash` bawaan memakai salt acak |

### 7.3 Kesimpulan relevansi

| Kebutuhan | Yang paling relevan | Alasan |
|---|---|---|
| **T5 / S2** (token) | **Betterleaks** | Rule provider matang. Pakai sebagai **pembanding S2**. PRISM tidak perlu mengungguli |
| **T5 / S1** (PII di berkas) | **Presidio sebagai rujukan desain**, dilengkapi pembungkus CLI gaya Betterleaks | Arsitektur skor + validasi + konteks + allow list sama dengan rancangan PRISM, dan `validate_result` memungkinkan cek tanggal lahir dan wilayah NIK |
| **T3 / S3** (PII di log) | **Presidio sebagai rujukan desain**, dengan penelusuran berkas log lewat argumen | Log adalah teks biasa, cocok dengan model "analisis string". Betterleaks sama-sama bisa memindai log, tetapi tidak punya konsep PII |

**Pembagian peran yang disarankan:**

| Peran | Tool |
|---|---|
| Rujukan desain mesin deteksi PII (skor, validasi, konteks, allow list) | Presidio |
| Rujukan desain kemasan CLI (subcommand `fs`/`stdin`, exit code, `--redact`, pipeline saringan bertingkat, fixture uji rule) | Betterleaks |
| Pembanding eksperimen S2 | Betterleaks |
| Pembanding eksperimen S1 dan S3 | Betterleaks (rule NIK custom) dan Presidio (`PatternRecognizer` NIK custom), pada dataset berlabel yang sama |

**Inti:** tidak ada satu tool pun yang menyelesaikan T3 dan T5 sekaligus untuk PII Indonesia. Betterleaks unggul di **kemasan CI** tetapi lemah di **semantik PII**. Presidio unggul di **semantik PII** tetapi tidak punya **kemasan CI**. Posisi PRISM adalah menggabungkan keduanya: aturan PII Indonesia + validasi, dalam CLI ringan dengan exit code dan laporan yang menyamarkan nilai.

### 7.4 Yang sebaiknya tidak diklaim

- PRISM lebih baik dalam mendeteksi token pihak ketiga. Betterleaks punya rule provider jauh lebih banyak.
- Mesin deteksi PRISM lebih canggih dari Presidio. Konsepnya sama, dan Presidio lebih matang.
- Betterleaks "tidak bisa" mendeteksi PII. Yang benar: tidak ada rule bawaan, dan rule custom belum terbukti punya validasi semantik.
- Presidio "tidak bisa" memvalidasi NIK. Bisa, lewat `validate_result`.
- Presidio tidak bisa mendeteksi PII Indonesia sama sekali. Yang benar: tidak ada bawaan, tetapi bisa ditambah lewat recognizer custom.
- Angka "recall 98,6%" dan "4 sampai 5 kali lebih cepat" untuk Betterleaks. Angka pertama berasal dari BleepingComputer dan pembandingnya entropi, bukan Gitleaks. Angka kedua tidak ada di sumber.

---

## 8. Eksperimen yang menentukan apakah gap benar

Tanpa eksperimen ini, pertanyaan penguji "kenapa tidak pakai rule custom di Betterleaks atau recognizer NIK di Presidio?" belum bisa dijawab dengan data.

| No | Eksperimen | Menentukan |
|---|---|---|
| E1 | `betterleaks fs <folder>` dengan konfigurasi bawaan pada berkas berisi 1 NIK sintetis, 1 HP sintetis, dan 1 token `ghp_` palsu. Catat versi yang dipakai | G1: apakah PII memang tidak terdeteksi bawaan |
| E2 | Tulis rule NIK custom di Betterleaks (regex 16 digit + keywords + filter). Ukur false positive pada angka 16 digit acak (rekening, ID transaksi) | G2: apakah validasi semantik cukup di Expr |
| E3 | Tulis `PatternRecognizer` NIK + `validate_result` di Presidio. Ukur precision, recall, dan FPR pada dataset berlabel yang sama dengan E2 | Apakah PRISM berbeda di deteksi atau hanya di kemasan |
| E4 | Ukur waktu `pip install` + unduh model + analisis di runner GitHub Actions. Coba `en_core_web_sm` dan analisis tanpa NER | P4: bobot dependensi (NFR-01, NFR-02) |
| E5 | `PhoneRecognizer` dengan `supported_regions=("ID",)` pada nomor `08...` dan `+62...` | P3 |
| E6 | Periksa isi laporan Betterleaks tanpa `--redact` dan trace Presidio `log_decision_process=True` | G3, P8: apakah nilai PII ikut tercetak |
| E7 | Pindai berkas log yang dihasilkan aplikasi contoh dengan kedua tool | S3 dan T3 |

**Catatan:** rencana harian 3 Nov menyebut baseline Gitleaks. Betterleaks dibuat oleh tim Gitleaks dan disebut penerusnya oleh sumber non-resmi, tetapi v2 memutus kompatibilitas konfigurasi. Putuskan salah satu sebagai baseline agar tidak membandingkan tiga tool sekaligus.
