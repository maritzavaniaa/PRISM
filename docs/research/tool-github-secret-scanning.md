# Riset Tool: GitHub Secret Scanning

> Sumber utama: dokumentasi resmi docs.github.com dan changelog GitHub. Semua klaim di bawah dicek ulang ke halaman resmi pada 2 November 2026. Klaim yang tidak bisa dipastikan diberi tanda ⚠️.
> Bagian yang diberi label **Relevansi PRISM** adalah analisis sendiri, bukan kutipan dokumentasi.

## 1. Ringkasan

| Aspek | Isi |
|---|---|
| Jenis | Fitur bawaan platform GitHub, bukan CLI atau library |
| Berjalan di | Infrastruktur GitHub, bukan runner GitHub Actions |
| Yang dideteksi | Secret/kredensial (API key, token, password, private key). Tidak ada deteksi PII seperti NIK/NPWP |
| Keluaran | Alert di tab *Security and quality*. Tidak ada exit code |
| Cara memblokir | Push protection (menolak push) dan ruleset blokir merge PR |
| Ketersediaan | Gratis di repo publik. Repo privat butuh GitHub Secret Protection (berbayar) |

## 2. Yang dipindai

| Objek | Dipindai? |
|---|---|
| Seluruh riwayat Git, semua branch | ✅ |
| Deskripsi dan komentar issue (terbuka dan tertutup) | ✅ |
| Judul, deskripsi, komentar pull request | ✅ |
| GitHub Discussions, wiki, secret gist | ✅ |
| Log workflow, artifact, cache, image Docker | ⚠️ Tidak disebut di halaman resmi (detection scope). Artinya belum terbukti ada atau tidak ada, bukan terbukti tidak dipindai |

## 3. Cara deteksi

| Metode | Keterangan | Validity check |
|---|---|---|
| Provider (partner) patterns | Pola khusus per penyedia layanan, aktif secara default. Jumlah pastinya tidak disebut di halaman, tapi sekitar 500 pola ⚠️ | Hanya sebagian pola |
| Generic patterns | Private key, connection string, API key generik. Harus diaktifkan terpisah | Tidak didukung |
| AI-detected | Mendeteksi secret tak terstruktur seperti password | Tidak didukung |
| Custom patterns | Regex buatan sendiri | Tidak ada |

**Pola custom (paling relevan untuk PRISM):**
- Memakai library **Hyperscan**, yaitu subset sintaks PCRE. Modifier opsi Hyperscan tidak didukung.
- Tiga bidang: *Secret format*, *Before secret* (default `\A|[^0-9A-Za-z]`), dan *After secret* (default `\z|[^0-9A-Za-z]`).
- Batas: **500** pola per organisasi/enterprise, **100** per repositori.
- Konstruksi regex yang boleh dipakai tidak dirinci di halaman ini, melainkan merujuk ke dokumentasi Hyperscan. ⚠️ Cek apakah lookahead dan backreference didukung sebelum merancang pola NIK.

**Validity check:** memeriksa apakah secret masih aktif dengan menghubungi layanan penerbitnya. Ini bukan checksum matematis. Tersedia untuk sebagian pola provider saja.

## 4. Hasil deteksi

Tiga jenis alert (terkonfirmasi):

| Jenis | Muncul di mana |
|---|---|
| User alerts | Tab *Security and quality* repositori |
| Push protection alerts | Tab yang sama, saat kontributor melewati blokir push |
| Partner alerts | Dikirim langsung ke penyedia secret, tidak muncul di repositori |

**REST API** (terkonfirmasi di docs.github.com/en/rest/secret-scanning):
- `GET /orgs/{org}/secret-scanning/alerts`
- `GET /repos/{owner}/{repo}/secret-scanning/alerts`
- `GET`/`PATCH /repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}`
- `GET /repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}/locations`
- Token klasik butuh scope `repo` atau `security_events`, dan penggunanya harus admin repo/organisasi.
- `GITHUB_TOKEN` dengan izin `security-events` **tidak bisa** membaca alert secret scanning. Dokumentasi workflow syntax menyatakan perlu GitHub App atau personal access token.

## 5. Pencegahan

**Push protection:**
- Memblokir push yang berisi secret sebelum masuk repositori. Mencakup pola provider, generik, custom, dan AI (AI masih public preview).
- Siapa pun dengan akses tulis bisa melewati blokir dengan alasan: *It's used in tests*, *It's a false positive*, atau *I'll fix it later*. Dua alasan pertama membuat alert tertutup, yang ketiga membuat alert terbuka. Event masuk audit log dan email dikirim ke pemilik.
- Batas teknis (halaman detection scope): push besar bisa timeout dan tidak terblokir (tetap dipindai setelah push); hanya 5 secret ditampilkan per push; push dengan lebih dari 1.000 secret yang sudah ada tidak diblokir; di repo publik, push di atas 50 MB dilewati.
- Dua jenis: **repositori** (butuh Secret Protection, nonaktif secara default) dan **pengguna** (khusus github.com, aktif default, hanya untuk repo publik).

**Blokir merge PR** (changelog 9 September 2026, *public preview*):
- Aturan ruleset: "Require secret scanning alerts are resolved".
- Memeriksa bahwa pemindaian commit head sudah selesai dan tidak ada alert terbuka dari commit di PR itu.
- Default hanya pola provider. Bisa dikonfigurasi untuk pola custom atau generik.
- Butuh GitHub Secret Protection atau GitHub Advanced Security.

## 6. Ketersediaan dan biaya

| Jenis repositori | Ketersediaan |
|---|---|
| Publik | Otomatis dan gratis |
| Privat/internal milik organisasi | Butuh Secret Protection di GitHub Team atau Enterprise Cloud |
| Milik akun pengguna (personal) | Hanya di Enterprise Cloud dengan Enterprise Managed Users, atau Enterprise Server yang mengaktifkan Secret Protection |

- Penagihan per *active committer* (90 hari terakhir). Contoh di halaman resmi: **$19** per committer. Itu angka ilustrasi, jadi cek kalkulator terbaru sebelum dikutip.
- Sumber pihak ketiga menyebut angka lain ($30). Jangan dipakai.

## 7. Koreksi terhadap catatan awal

| Catatan awal | Hasil verifikasi |
|---|---|
| "521 pola" | Halaman resmi tidak menyebut total. Hanya "sekitar 500 pola provider + 10 generik + 1 AI (`password`)". Pakai "sekitar 500". |
| "Copilot secret scanning" untuk AI | Halaman resmi hanya menyebut "AI-detected secrets", tanpa nama Copilot. Pakai istilah resmi. |
| "Hanya 5 lokasi pertama untuk pola non-provider" | Tidak ditemukan di halaman resmi. Yang terkonfirmasi: 5 secret per push pada push protection. Hapus klaim awal. |
| Alert ketiga "belum terbaca" | Jenis ketiga adalah **push protection alerts**. |
| "Tidak ada CLI/Action resmi" | Konsisten dengan dokumentasi, tapi tetap berstatus *tidak ditemukan*, bukan *tidak ada*. Hasil pencarian hanya menemukan tool pihak ketiga (misalnya ggshield, Datadog). |
| "Tidak memindai artifact, Docker, log CI" | Hanya dari sumber pihak ketiga. Dokumen resmi diam soal ini. Tulis sebagai "tidak tercakup menurut dokumentasi", bukan sebagai fakta. |
| "Commit lama tidak dipindai retroaktif" | Salah. Dokumentasi resmi menyatakan seluruh riwayat Git di semua branch dipindai. |
| Blokir merge PR (9 Sept 2026) | Benar dan berstatus public preview. |
| Endpoint REST API | Benar. |
| `GITHUB_TOKEN` tidak bisa baca alert | Benar, dari dokumentasi workflow syntax. |

## 8. Kelebihan dan kekurangan untuk PRISM

> Bagian ini analisis sendiri berdasarkan fakta di atas.

### Kelebihan
| Poin | Penjelasan |
|---|---|
| Cakupan luas tanpa pengaturan | Riwayat Git, issue, PR, wiki, dan discussions otomatis dipindai. Scanner PRISM yang hanya memindai working tree tidak mencakup itu |
| Pola provider matang | Sekitar 500 pola dengan validity check. Tidak masuk akal ditandingi dengan scanner buatan sendiri untuk token pihak ketiga |
| Pencegahan sebelum masuk | Push protection menolak push, sementara PRISM baru bereaksi saat job CI berjalan |
| Tanpa instalasi | Cukup diaktifkan di pengaturan repositori |
| Gratis untuk repo publik | Bisa dijadikan pembanding pada repo uji publik tanpa biaya |

### Kekurangan
| Poin | Penjelasan |
|---|---|
| Tidak mendeteksi PII | Tidak ada pola NIK, NPWP, atau nomor HP Indonesia bawaan. Ini gap utama yang membenarkan PRISM |
| Pola custom hanya regex | Tidak ada checksum atau validasi tanggal lahir seperti rencana PRISM. Hanya bidang before/after sebagai konteks, jadi false positive pada angka 16 digit sulit ditekan |
| Tidak berjalan di runner | Tidak ada exit code atau step workflow, jadi pipeline tidak otomatis gagal. Mekanisme pengganti adalah blokir push dan blokir merge |
| Log keluaran tes tidak tercakup (S3) | Dokumentasi tidak menyebut pemindaian log pipeline. Ini celah untuk S3, tapi perlu diuji langsung sebelum diklaim |
| Alert sulit diambil dari workflow | `GITHUB_TOKEN` tidak cukup. Perlu PAT atau GitHub App |
| Biaya untuk repo privat | Repo privat organisasi butuh lisensi. Repo pribadi mahasiswa kemungkinan tidak memenuhi syarat |
| Push protection bisa dilewati | Cukup memberi alasan, dan alasan "It's used in tests" menghasilkan alert tertutup |
| Batas teknis | Timeout push besar dan push di atas 50 MB di repo publik tidak terblokir |
| Kendali penyimpanan | Alert disimpan di GitHub dan tidak bisa diatur pengguna |
| Terkunci ke GitHub | Tidak bisa dipakai di GitLab atau Bitbucket ⚠️ (dari sumber pihak ketiga, tapi konsisten dengan sifatnya sebagai fitur platform) |

## 9. Relevansi untuk skenario PRISM

| Skenario | Dukungan GitHub secret scanning | Catatan |
|---|---|---|
| S1: PII di berkas repositori | ❌ Tidak bawaan | Bisa dicoba pola custom, tapi tanpa validasi |
| S2: Token/kredensial di commit | ✅ Sangat baik | Ini keunggulan utama mereka |
| S3: PII di log keluaran tes | ⚠️ Tidak terdokumentasi | Uji langsung dengan repo uji |

**Implikasi untuk metodologi:**
1. Jadikan GitHub secret scanning sebagai **pembanding S2**, bukan pesaing untuk S1 dan S3. PRISM sebaiknya tidak mengklaim lebih baik untuk token pihak ketiga.
2. Argumen gap untuk Introduction: GitHub secret scanning berfokus pada kredensial, tidak mendeteksi PII berformat Indonesia, tidak memberi gating lewat exit code di runner, dan tidak terdokumentasi memindai log keluaran tes.
3. Ada dua hal yang bisa diuji langsung dan kemudian dilaporkan sebagai temuan: (a) apakah pola custom NIK di repo publik bisa dibuat dan seberapa banyak false positive-nya, dan (b) apakah secret yang tercetak ke log workflow menghasilkan alert.

## 10. Yang masih perlu dicek

- [ ] Apakah lookahead dan backreference didukung Hyperscan (halaman Hyperscan *Pattern support*).
- [ ] Apakah pola custom tersedia di repo publik tanpa Secret Protection.
- [ ] Apakah secret di log workflow atau artifact menghasilkan alert (uji langsung di repo uji).
- [ ] Apakah ada cara resmi menjalankan pemindaian dari workflow Actions.
- [ ] Harga terbaru di github.com/pricing sebelum dikutip.

## Sumber

**Resmi (sudah diverifikasi 2 Nov 2026):**
- [Secret scanning (konsep)](https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning)
- [Push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection)
- [Detection scope](https://docs.github.com/en/code-security/reference/secret-security/secret-scanning-detection-scope)
- [Supported secret scanning patterns](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns)
- [Custom patterns](https://docs.github.com/en/code-security/reference/secret-security/custom-patterns)
- [REST API secret scanning](https://docs.github.com/en/rest/secret-scanning/secret-scanning)
- [Workflow syntax, bagian permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Estimasi harga Secret Protection](https://docs.github.com/en/code-security/how-tos/secure-at-scale/configure-organization-security/configure-specific-tools/estimating-the-price-of-secret-protection)
- [Changelog: blokir merge PR dengan secret (9 Sept 2026)](https://github.blog/changelog/2026-09-09-block-pull-requests-with-exposed-secrets-from-merging)

**Tidak resmi (jangan dikutip sebagai fakta):** ringkasan awesome-copilot, answers.securityscientist.net, redresscompliance.com.
