# Riset Tool: Betterleaks

> Sumber utama: repositori resmi github.com/betterleaks/betterleaks (README, `docs/scanning.md`, `docs/config.md`, `docs/v2_migration.md`, halaman Releases). Dicek ulang ke halaman tersebut pada 10 November 2026. Berita dan blog diberi tanda sebagai sumber non-resmi.
> Klaim yang tidak bisa dipastikan diberi tanda ⚠️. Bagian berlabel **Relevansi PRISM** adalah analisis sendiri, bukan kutipan dokumentasi.
> Dokumen ini mengikuti dokumentasi **v2** (branch `main`). Perbedaan dengan v1 dicatat di bagian 7.

## 1. Ringkasan

| Aspek | Isi |
|---|---|
| Jenis | CLI dan library Go, lisensi MIT. Binary mandiri, bukan fitur platform |
| Pembuat | README: "maintained by the folks who made Gitleaks, including the original author". Didukung Aikido Security |
| Yang dideteksi | Secret/kredensial. README dan halaman yang dibaca tidak menyebut PII |
| Cara deteksi | Regex (RE2), prefilter keyword Aho-Corasick, lalu filter Expr (entropi, BPE/token efficiency, konteks git) |
| Keluaran | Teks di terminal, JSON, atau JSONL (v2). Exit code `1` bila ada temuan (default) |
| Cara memblokir | Exit code membuat step CI gagal. Tidak ada fitur blokir bawaan platform |
| Validasi ke penyedia | Opsional (`-v`/`--validate`), mati secara default |
| Status rilis | v2 masih kandidat rilis (lihat bagian 2) |

## 2. Hubungan dengan Gitleaks dan status versi

| Hal | Hasil verifikasi |
|---|---|
| Dibuat oleh tim Gitleaks | ✅ README, termasuk penulis aslinya |
| "Successor" Gitleaks | ✅ BleepingComputer, 15 Maret 2026 (non-resmi), mengutip Zach Rice: "Betterleaks is the successor to Gitleaks". README sendiri tidak memakai kata itu |
| Pembuat saat ini | BleepingComputer: Zach Rice, Head of Secrets Scanning di Aikido Security, dibantu tiga maintainer lain |
| Proyek terpisah | ✅ Repositori dan nama baru, bukan versi Gitleaks yang dinaikkan |
| "Drop-in replacement" | ⚠️ Tidak ada di artikel BleepingComputer. Muncul di sumber lain (vpncentral, mengutip pengumuman Aikido). Berlaku untuk v1. v2 memutus kompatibilitas (bagian 7) |
| Branch | `main` = pengembangan v2. Pemeliharaan v1 di branch `v1.x` |

**Rilis (halaman Releases, dibaca 10 Nov 2026; halaman tidak menulis tahun):**

| Tag | Tanggal | Status |
|---|---|---|
| v2.0.0-rc.7 | 4 Nov | Pre-release |
| v1.10.0 | 4 Nov | Latest (stabil) |
| v2.0.0-rc.1 sampai rc.6 | 30 Sep sampai 30 Okt | Pre-release |
| v1.9.0 | 29 Sep | Rilis |
| v1.8.1 | 18 Agu | Rilis |

- Belum ada v2 stabil. Tujuh kandidat rilis dalam sekitar lima minggu menunjukkan v2 masih bergerak cepat.
- README: sampai v2 stabil, package manager dan tag Docker `latest` mungkin masih menyajikan v1.

## 3. Alur deteksi (urutan tahap)

| No | Tahap | Teknologi | Keterangan |
|---|---|---|---|
| 1 | Source | Pembaca per sumber | Data dipecah menjadi fragment (misalnya satu patch commit) |
| 2 | Prefilter | Expr | Membuang seluruh file, commit, atau fragment sebelum regex. Hanya melihat `attributes` (path, penulis git, dll.). Fungsi konten dan tokenizer ditolak saat kompilasi |
| 3 | Keyword | Aho-Corasick | Fragment hanya diuji regex bila memuat keyword rule. Sangat disarankan |
| 4 | Regex | RE2 | README menyebut `re2`. ⚠️ Default CLI tidak dinyatakan eksplisit di halaman yang dibaca. `v2_migration.md` menyatakan **SDK** default ke regex standar Go, RE2 harus diaktifkan |
| 5 | Filter | Expr | Membuang kandidat palsu. Melihat `attributes` dan `finding` (secret, match, line). Nilai `true` berarti dibuang |
| 6 | Confidence | `setConfidence` | low, medium, high |
| 7 | Validasi (opsional) | Ekspresi `validate`, `http.get`/`http.post` | Status: valid, needs_validation, invalid, revoked, unknown, error |
| 8 | Analisis (opsional) | Ekspresi `analyze` | Identitas, kemampuan, tingkat keparahan. Implies validasi |
| 9 | Revoke | `betterleaks revoke --rule <id>` | "Scans never run revocation" |

**Fungsi filter (config.md):** `matchesAny`, `findMatch`, `containsAny` (Aho-Corasick), `startsWithAny`, `intersects`, `entropy` (Shannon), `tokenRatio` (panjang byte per jumlah token), `failsTokenEfficiency` (rasio token + wordlist + panjang), `setConfidence`, `crypto.sha256`.

**BPE / token efficiency:** README: tokenisasi BPE dipakai untuk menyaring false positive berupa bahasa alami dengan mengukur seberapa "langka" sebuah string. Klaim recall 98,6% dibanding 70,4% untuk entropi pada dataset CredData berasal dari BleepingComputer (non-resmi) dan **dibandingkan dengan entropi, bukan dengan Gitleaks**. Belum diuji sendiri.

**Rule multipart:** `components` mendeklarasikan rule pendamping yang harus muncul berdekatan (misalnya ID akun + secret). Temuan yang ter-encode (base64, persen) ikut didekode dan memuat `encodings` serta `decode_depth`.

## 4. Yang dipindai

| Sumber | Perintah | Keterangan (dari scanning.md) |
|---|---|---|
| File/folder | `betterleaks fs <path>` | "Files are not skipped by MIME type". Prefilter bawaan tetap melewati ekstensi gambar dan font |
| Riwayat git | `betterleaks git <path-atau-url>` | Dibaca in-process (tidak memanggil `git`). Default: HEAD dan semua ref non-notes. Merge commit tidak di-diff secara default. Tipe sumber: history, merges, commit-messages, notes, tag-messages, reflogs, objects, unreachable-objects |
| Perubahan staged/unstaged | `git diff --cached \| betterleaks stdin --git-diff` | **Flag `--staged`, `--unstaged`, `--pre-receive` dihapus di v2.** Gunakan `set -o pipefail` agar kegagalan `git` tidak terlihat seperti scan bersih |
| GitHub | `betterleaks github <url>` | repos, forks, prs, pr-comments, issues, issue-comments, **actions**, **action-artifacts**, discussions, releases, release-assets, gists. Memakai `GITHUB_TOKEN` |
| GitLab | `betterleaks gitlab <url>` | Mirip, plus mrs, snippets, **ci-jobs**, **ci-artifacts** |
| Hugging Face | `betterleaks hf <url>` | repos, discussions, prs, buckets |
| S3 | `betterleaks s3 <url>` | AWS, R2, MinIO, dan endpoint kompatibel |
| Container | `betterleaks container` (alias `docker`) | Image registry, daemon docker/podman, arsip, OCI layout. *Tidak ada di catatan awal* |
| URL | `betterleaks url <url>` | Satu respons HTTP(S), tanpa crawling |
| Stdin | `<perintah> \| betterleaks stdin` | Konten dialirkan. `--git-diff` untuk keluaran patch git |

- Arsip dan decoding dibatasi `--max-archive-depth` (default 8 untuk git dan container).
- Remote clone v2 hanya mengambil branch, tag, dan notes, bukan ref pull request.
- Dukungan GitHub Actions: scanning.md menyarankan `fetch-depth: 0` untuk atribusi riwayat yang akurat.

## 5. Hasil, laporan, dan penyimpanan

| Aspek | Isi |
|---|---|
| Default | Teks di terminal |
| `--jsonl` | Satu amplop per temuan, lalu satu record metadata `scan` |
| `-o/--output <path>` | Laporan di-stream. Format dari ekstensi (`.json`/`.jsonl`). `-` menulis ke stdout |
| Skema JSON v2 | Objek `{schema_version, findings, scan}`. Field berpindah: `rule_id`, `match.value`, `location.*`, `analysis.status` |
| `--redact` | Menyamarkan nilai secret di laporan |
| `--silent` / `--no-banner` | Menekan keluaran terminal / hanya banner |
| Penyimpanan | Betterleaks tidak menyimpan apa pun sendiri. Di CI, file laporan harus diunggah sebagai artifact atau dibaca step berikutnya (analisis sendiri) |
| Exit code | `1` bila ada temuan, default (v2_migration.md). ⚠️ Flag `--exit-code` dari catatan awal tidak muncul di halaman yang dibaca |

**Mengabaikan temuan:**
- Komentar `betterleaks:allow` atau `gitleaks:allow` (bisa diganti `--allow-signature`, dimatikan `--no-allow-signatures`).
- `.betterleaksignore`: berisi SHA-256 (atau HMAC) dari **nilai secret**, bukan lokasi. Entri dibuat dengan `betterleaks fingerprint`.

**Fingerprint:** SHA-256 dari byte secret, atau HMAC bila kunci diberikan (catatan awal: `--hmac-key` / `BETTERLEAKS_FINGERPRINT_HMAC_KEY`, ⚠️ nama flag belum dicek ulang). Ini penting untuk PRISM (bagian 9).

## 6. Penggunaan di CI/CD

- **Instalasi:** Homebrew, `dnf` (Fedora), image Docker `ghcr.io/betterleaks/betterleaks:v2`, `go install`, atau build dari sumber.
- **GitHub Action resmi:** ⚠️ **Tidak ditemukan.** README tidak menyebutnya. Pencarian web tidak menemukan repositori `betterleaks-action`. `AikidoSec/github-actions-workflow` adalah Action Aikido untuk dependensi dan SAST, bukan Betterleaks. Satu blog Jepang (serverworks) mencantumkan dukungan GitHub Actions di tabel, tetapi itu satu-satunya sumber.
- **Pola paling sederhana (analisis sendiri, belum diuji):** pasang binary, jalankan `betterleaks fs .` atau `betterleaks git .` di sebuah step. Exit code `1` menggagalkan step otomatis.
- **Hook pre-commit:** repo memuat `.pre-commit-hooks.yaml`, tetapi README tidak menjelaskan isinya. ⚠️ Karena `--staged` dihapus di v2, isi hook perlu dibaca langsung sebelum dikutip.
- **Hook pre-receive:** ada contoh di scanning.md (lewat `stdin`).
- **Pihak lain:** README menyebut MegaLinter (agregator linter untuk CI) membawa Betterleaks bawaan.
- **Library Go:** `scan.New(cfg)`, lalu `ScanString`/`Scan`.

## 7. Perubahan v1 ke v2 yang perlu diwaspadai

Semua dari `docs/v2_migration.md`, kecuali ditandai.

| Area | Perubahan |
|---|---|
| Jaringan | Scan tidak menghubungi penyedia secara default. Validasi butuh `-v`, analisis butuh `-a` |
| Reporter | CSV, JUnit, **SARIF**, dan template dihapus. `--baseline-path` dihapus, tanpa konversi otomatis |
| Subcommand | `dir`/`directory`/`file` menjadi `fs`. `detect` dan `protect` diganti `git`, `fs`, `stdin` |
| Git | Dibaca in-process. `--log-opts`, `--staged`, `--unstaged`, `--pre-receive` dihapus. Merge commit tidak di-diff. Remote clone hanya branch/tag/notes |
| Konfigurasi | Field tidak dikenal menggagalkan loading (termasuk di config turunan). `allowlist`, `entropy`, `tokenEfficiency`, `secretGroup`, `withinLines` dihapus; ganti `filter`, `valueGroup`, `components`. `.betterleaks.toml` tidak dimuat otomatis |
| Env var | `GITLEAKS_CONFIG` menjadi `BETTERLEAKS_CONFIG` (dan `_TOML`) |
| Flag | `--validation*` menjadi `--validate`/`--provider-*`. `--report-path` menjadi `--output`. `--enable-rule` menjadi `--isolate-rule` |
| File | Tidak lagi dilewati berdasarkan MIME type, sehingga temuan bisa lebih banyak dari v1 |
| JSON | Bare array menjadi objek `{schema_version, findings, scan}` |
| Go SDK | Modul `github.com/betterleaks/betterleaks/v2`, **Go 1.26.0 atau lebih baru**. `scan.Scanner` menggantikan `detect.Detector` |
| Ignore | Entri `.betterleaksignore` berupa digest SHA-256 polos. `.gitleaksignore` tidak ditemukan otomatis |

## 8. Konfigurasi (betterleaks.toml)

- **Bidang tingkat atas:** `title`, `description`, `provider`, `prefilter`, `filter`, `minVersion`, `[extend]`, `[[rules]]`.
- **Bidang rule:** `id`, `description`, `keywords`, `regex`, `path`, `valueGroup`, `specificity`, `tags`, `skipReport`, `filter`, `confidence`, `validate`, `analyze`, `revoke`, `components`, `[[rules.tests]]`.
- **Urutan pemilihan:** `--config`, lalu `BETTERLEAKS_CONFIG`, lalu `BETTERLEAKS_CONFIG_TOML`, lalu bawaan.
- **Extend:** `path` atau `useDefault` (tidak boleh bersamaan), `disabledRules`. `extend.url` ditolak. Maksimal dua tingkat pewarisan. Rule dengan ID sama di config turunan **mengganti seluruh rule**, tidak digabung.
- **`betterleaks config check`:** mengompilasi regex dan ekspresi, **menjalankan fixture `[[rules.tests]]` lewat scanner**, tanpa permintaan jaringan, dan keluar nonzero bila gagal.
- **Lookahead/backreference:** halaman config.md tidak menyatakan fitur regex yang didukung. Bila engine-nya RE2, keduanya tidak tersedia.
- README menyarankan untuk produksi mengelola konfigurasi sendiri, bukan memperluas konfigurasi bawaan langsung.

## 9. Koreksi terhadap catatan awal

| Catatan awal | Hasil verifikasi |
|---|---|
| `betterleaks git --staged`, `--unstaged`, `--pre-receive` | **Salah untuk v2.** Ketiganya dihapus. Pakai `git diff --cached \| betterleaks stdin --git-diff`. Berlaku untuk v1 saja |
| Go 1.25 ke atas | **Go 1.26.0 atau lebih baru** |
| Kandidat rilis v2.0.0-rc.1 | Usang. Per 10 Nov sudah **rc.7**, dan stabil terbaru adalah **v1.10.0** |
| "CLI memakai RE2 secara default" | ⚠️ Tidak terkonfirmasi. README menyebut `re2`, tetapi yang tertulis eksplisit hanya SDK default ke regex standar Go dan RE2 harus diaktifkan. Cek `betterleaks --help` |
| "Berita menyebut drop-in replacement" | Bukan dari BleepingComputer. Atribusi ke vpncentral (mengutip pengumuman Aikido), dan itu berlaku untuk v1 |
| "Kecepatan 4 sampai 5 kali Gitleaks" | ⚠️ **Tidak ada angka** di artikel BleepingComputer. Hanya gambar perbandingan tanpa angka dan fitur "parallelized git scanning". Jangan dikutip tanpa sumber lain |
| Recall 98,6% vs 70,4% | Ada di BleepingComputer, tetapi pembandingnya **entropi**, bukan Gitleaks |
| Konfigurasi `config.md` tampak salinan lama (`--validation`, `filter.*`) | ⚠️ Tidak bisa direproduksi. Versi yang dibaca memakai sintaks v2 (helper tingkat atas, `valueGroup`, `revoke`). Anggap tidak ada inkonsistensi sampai dilihat langsung |
| Daftar sumber scan | Kurang `container`/`docker`. Detail GitHub dan GitLab bertambah (ci-jobs, ci-artifacts, action-artifacts) |
| Daftar fungsi filter | Kurang `startsWithAny`, `intersects`, `crypto.sha256` |
| `.pre-commit-hooks.yaml` memindai staged dengan `--redact` dan tanpa jaringan | ⚠️ File ada, isinya tidak dijelaskan README. Belum diverifikasi |
| GitHub Action `AikidoSec/betterleaks-action` | Tetap **tidak ditemukan** |
| `--exit-code` mengubah exit code | ⚠️ Tidak terlihat di halaman yang dibaca. Yang terkonfirmasi hanya default `1` |
| Exit code 1 untuk temuan | ✅ Terkonfirmasi |
| Reporter SARIF/CSV/JUnit dihapus, skema JSON baru, env var, MIME, config tidak dimuat otomatis, urutan config, rule diganti total | ✅ Terkonfirmasi |
| Lisensi MIT, MegaLinter, `fetch-depth: 0` | ✅ Terkonfirmasi |

**Belum dicek ulang** (tidak terbaca pada pengambilan ini; bagian akhir scanning.md sekitar 5,7 ribu karakter terpotong): daftar provider revoke, fungsi bawaan AWS/GCP/Azure, contoh validasi dengan LLM, contoh prefilter bawaan README, seri blog pembuat, dan daftar rule bawaan.

## 10. Kelebihan, kekurangan, dan celah untuk PRISM

> Bagian ini analisis sendiri berdasarkan fakta di atas.

### Yang relevan (kelebihan Betterleaks, jangan diklaim dikalahkan)

| Poin | Penjelasan |
|---|---|
| Rule provider matang untuk token | Tepat untuk S2. PRISM sebaiknya memakai Betterleaks sebagai **pembanding S2**, sama seperti GitHub secret scanning |
| Rule TOML bisa dibuat sendiri | Betterleaks **bisa** mendeteksi PII lewat rule custom (regex + keywords + filter). Gap PRISM bukan "tidak bisa", melainkan "tidak ada bawaan dan tanpa validasi semantik" |
| Bisa memindai keluaran program | `stdin`, `fs` pada file log, dan sumber `github` dengan `actions`/`action-artifacts` secara mekanis mencakup S3. Ini lebih baik daripada GitHub secret scanning, yang tidak mendokumentasikan hal itu |
| Fixture `[[rules.tests]]` | Rule bisa diuji dengan `config check`. Pola yang layak ditiru untuk evaluasi PRISM |
| Pipeline filter bertahap | Prefilter, keyword, regex, filter menjadi referensi desain untuk menekan false positive |
| Exit code 1 default | Sama dengan target FR-06 |

### Celah yang bisa menonjolkan PRISM

| No | Celah | Dasar | Kekuatan argumen | Catatan |
|---|---|---|---|---|
| G1 | Tidak ada aturan PII Indonesia bawaan (NIK, NPWP, HP +62) | README tidak menyebut PII. ⚠️ Daftar rule bawaan belum dibaca | Sedang. Hanya bertahan jika rule bawaan memang dicek dan kosong | Harus dilaporkan sebagai "tidak ditemukan", bukan "tidak ada" |
| G2 | Tidak ada validasi semantik PII | Fungsi filter hanya regex, entropi, token ratio, dan pencocokan string. NIK butuh cek tanggal lahir (tanggal + 40 untuk perempuan) dan kode wilayah | Tinggi, **tapi belum diuji**. ⚠️ Ekspresi Expr mungkin cukup untuk aritmetika tanggal sederhana. Uji dulu sebelum mengklaim | Inilah pembeda utama terhadap angka 16 digit acak |
| G3 | Fingerprint dan laporan dirancang untuk secret, bukan PII | Fingerprint = SHA-256 byte secret (HMAC opsional). NIK dan HP punya ruang nilai kecil sehingga SHA-256 tanpa kunci bisa ditebak dengan brute force | Sedang sampai tinggi. Cocok dengan pertanyaan terbuka hash vs masking (riset utama bagian 12.2), NFR-04, dan T9. Opsi HMAC milik Betterleaks sekaligus **mendukung** keputusan memakai HMAC atau masking di PRISM | Perlu dicek apa yang ditulis laporan tanpa `--redact` dan apakah `match.value` ikut tercetak |
| G4 | Validasi mengirim data keluar | Validasi mati default, tetapi contoh LLM (⚠️ belum dicek ulang) mengirim konteks ke API pihak ketiga | Rendah sampai sedang. Relevan hanya sebagai kontras terhadap NFR-04 ("tidak dikirim ke layanan eksternal"), bukan celah nyata karena fitur ini opsional | Jangan dibesar-besarkan |
| G5 | Tanpa SARIF di v2 | Reporter SARIF dihapus di v2 | Rendah. Tidak relevan dengan inti PRISM, hanya batasan integrasi ke tab code scanning GitHub | Jangan dijadikan argumen utama |
| G6 | Kebijakan gagal per kategori | Betterleaks gagal pada temuan apa pun, dapat disaring `--confidence`. Tidak ada konsep kategori PII vs kredensial | Rendah. PRISM juga menetapkan gagal pada satu temuan apa pun | Hanya jadi argumen jika kebijakan per kategori dibuat (severity masuk "jangan dikerjakan dulu") |
| G7 | Stabilitas | v2 masih rc.7, skema JSON dan flag berubah dari v1 | Sedang untuk pembahasan risiko, bukan untuk menonjolkan PRISM | Pin versi pada eksperimen pembanding |

**Yang sebaiknya tidak diklaim PRISM:**
- Lebih baik dalam deteksi token pihak ketiga (Betterleaks punya rule provider jauh lebih banyak).
- Satu-satunya yang bisa memindai log (Betterleaks bisa lewat `stdin` dan `fs`).
- Betterleaks "tidak bisa mendeteksi PII". Yang benar: tidak ada rule bawaan, dan rule custom tidak punya validasi semantik bawaan.

**Pertanyaan yang pasti muncul dari penguji:** "Kenapa tidak menulis rule custom di Betterleaks saja?" Jawabannya harus berupa data. Lihat eksperimen di bagian 12.

## 11. Relevansi untuk skenario PRISM

| Skenario | Dukungan Betterleaks | Catatan |
|---|---|---|
| S1: PII di berkas repositori | ⚠️ Hanya dengan rule custom | Tanpa rule bawaan dan tanpa validasi tanggal/wilayah (belum diuji) |
| S2: Token di berkas/commit | ✅ Sangat baik | Pembanding S2. PRISM tidak perlu mengungguli |
| S3: PII di log keluaran | ⚠️ Mekanisme ada (`stdin`, `fs`, `github --include actions`), rule PII tidak | Pemindaian log run lewat API GitHub bersifat sesudah kejadian dan butuh token. Apakah log run yang sedang berjalan bisa dipindai dari job yang sama belum diuji |

**Selaras dengan keputusan scope:** PRISM memindai berkas di folder repo (bukan riwayat git) dan berkas log lewat argumen. Pada cakupan itu, `betterleaks fs <folder>` adalah padanan langsung, sehingga perbandingan bisa adil.

**Posisi di tabel perbandingan tool (bagian 9.1 riset utama):**

| Tool | Jenis | Berjalan di runner | PII Indonesia | Gating exit code |
|---|---|---|---|---|
| Betterleaks | CLI scanner secret, rule custom | Ya | Tidak ada bawaan ⚠️ | Ya (1) |
| GitHub secret scanning | Fitur platform | Tidak | Tidak | Tidak (push protection) |
| Presidio | Framework PII (teks) | Ya (library) | Perlu recognizer custom | Tidak bawaan |

## 12. Yang masih perlu dicek

- [ ] Eksperimen pembanding (padanan Bagian C di `sebelum-implementasi.md`): berkas berisi 1 NIK sintetis, 1 HP sintetis, 1 token `ghp_` palsu. Jalankan `betterleaks fs <folder>` dengan konfigurasi bawaan. Dugaan: token terdeteksi, NIK dan HP tidak. Catat versi yang dipakai (disarankan pin, mis. v1.10.0 stabil atau v2.0.0-rc.7).
- [ ] Eksperimen kunci: tulis rule TOML NIK (regex 16 digit + keywords + filter), lalu ukur false positive pada angka 16 digit acak (nomor rekening, ID transaksi) dibanding PRISM pada dataset berlabel yang sama. **Ini menentukan apakah G2 benar.**
- [ ] Apakah Expr mampu menghitung tanggal lahir NIK dan mencocokkan kode wilayah (`in` pada daftar).
- [ ] Engine regex default CLI (`betterleaks --help`, `--regex-engine`).
- [ ] Apa yang tertulis di laporan tanpa `--redact` (`match.value`, fingerprint).
- [ ] Isi `.pre-commit-hooks.yaml` dan daftar rule bawaan (`config/betterleaks.toml`, ada rule PII atau tidak).
- [ ] Flag `--exit-code` dan `--hmac-key` (nama dan perilaku).
- [ ] Bagian akhir scanning.md yang terpotong, seri blog pembuat, dan keberadaan Action resmi.

## Sumber

**Resmi (dicek 10 Nov 2026):**
- [Repositori dan README](https://github.com/betterleaks/betterleaks)
- [Panduan scanning](https://github.com/betterleaks/betterleaks/blob/main/docs/scanning.md)
- [Referensi konfigurasi](https://github.com/betterleaks/betterleaks/blob/main/docs/config.md)
- [Migrasi v1 ke v2](https://github.com/betterleaks/betterleaks/blob/main/docs/v2_migration.md)
- [Releases](https://github.com/betterleaks/betterleaks/releases)

**Non-resmi (jangan dikutip sebagai fakta tanpa cek ulang):**
- [BleepingComputer, 15 Maret 2026](https://www.bleepingcomputer.com/news/security/betterleaks-a-new-open-source-secrets-scanner-to-replace-gitleaks/) (dibaca langsung; sumber klaim "successor" dan recall 98,6%)
- [Help Net Security, 19 Maret 2026](https://www.helpnetsecurity.com/2026/03/19/betterleaks-open-source-secrets-scanner/) (⚠️ tidak dibaca ulang)
- [vpncentral](https://vpncentral.com/?p=246720) (sumber "drop-in replacement")
- [Blog perbandingan serverworks](https://blog.serverworks.co.jp/git-secret-detection-tools-comparison-2026) (satu-satunya yang menyebut dukungan GitHub Actions)
- [Canadian Web Hosting](https://blog.canadianwebhosting.com/betterleaks-gitleaks-secret-scanner-bpe/) dan [aicoolies](https://aicoolies.com/reviews/gitleaks-review) (⚠️ tidak dibaca ulang)
