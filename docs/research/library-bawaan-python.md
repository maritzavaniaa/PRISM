# Library Bawaan Python untuk PRISM

> Dasar: dokumentasi resmi Python, dibaca pada 16 November 2026 (sumber [49]–[58] di [referensi.md](referensi.md)). Halaman dibaca lewat ringkasan alat fetch, bukan teks mentah, dan beberapa halaman hanya terbaca sebagian (lihat peta sumber).
> Tanda ⚠️ = belum terkonfirmasi atau belum diuji. Bagian berlabel **Relevansi PRISM** adalah analisis sendiri, bukan kutipan dokumentasi.
> Keputusan MVP yang dirujuk ada di [mvp-t5.md](../planning/mvp-t5.md) bagian 4: Python, hanya library standar (`argparse`, `re`, `os`, `json`, `dataclasses`).

## 1. Library bawaan itu apa

**Library** adalah kumpulan kode siap pakai yang tinggal dipanggil. **Library bawaan** (*standard library*) adalah library yang ikut terdistribusi bersama Python, sehingga tidak perlu `pip install`. Dokumentasi resmi menyebut manual ini "describes the standard library distributed with Python" [49].

| | Library bawaan | Library tambahan |
|---|---|---|
| Contoh | `re`, `os`, `json`, `sys`, `argparse`, `csv` | `numpy`, `pandas`, `google-re2` [47], `presidio-analyzer` |
| Perlu `pip install` | Tidak | Ya |
| Cara memakai | `import re` | `pip install ...`, lalu `import ...` |

**Dua catatan dari dokumentasi [49]:**
- Di Windows, installer Python "usually include the entire standard library". Di sistem mirip Unix, Python "is normally provided as a collection of packages, so it may be necessary to use the packaging tools provided with the operating system to obtain some or all of the optional components". Artinya "bawaan" belum tentu lengkap di semua distribusi Linux. ⚠️ Belum dicek untuk runner GitHub Actions dengan `actions/setup-python`.
- Kata *built-in* punya dua arti. Dalam dokumentasi, "built-in modules" berarti modul yang ditulis dengan C, sedangkan "built-in functions" (seperti `open()`, `print()`) punya halaman terpisah [49]. Dalam percakapan, "bawaan" di sini berarti seluruh library standar.

## 2. Ringkasan

| Library | Kegunaan | Dipakai PRISM untuk | Status di keputusan MVP |
|---|---|---|---|
| `re` | Mencocokkan pola teks (regex) | Mencari kandidat NIK, HP, email | Dipakai |
| `os` | Sistem file dan environment | Menelusuri folder, melewati `.git`, ukuran file | Dipakai |
| `json` | Membaca dan menulis JSON | Laporan `--json` | Dipakai |
| `argparse` | Antarmuka perintah (CLI) | `prism scan <folder> --json --exclude ...` | Dipakai |
| `dataclasses` | Kelas data ringkas | Struktur `Rule` dan temuan | Dipakai |
| `sys` | Interpreter yang sedang jalan | **Exit code** 0/1/2, stdin, stderr | Dipakai (untuk `sys.exit`) |
| `csv` | Membaca dan menulis CSV | Data uji, label, hasil evaluasi, tabel kode wilayah | Evaluasi dan data, bukan mesin pemindai |
| `tomllib` | Membaca TOML | Konfigurasi gaya Gitleaks | Tidak dipakai di MVP. Opsi nanti |

## 3. Per library

### 3.1 `re`: mencari pola

> "This module provides regular expression matching operations similar to those found in Perl." [50]

| Fungsi | Cara kerja | Output |
|---|---|---|
| `re.compile(pola)` | Mengubah pola menjadi objek regex. Pola yang baru dipakai di-cache [50] | Objek regex |
| `re.finditer(pola, teks)` | Memindai teks dari kiri ke kanan dan mengembalikan semua kecocokan yang tidak beririsan, urut sesuai temuan [50] | Iterator `Match` |
| `Match.start()`, `.end()`, `.span()` | Posisi awal dan akhir kecocokan. Argumen kelompok default 0, yaitu seluruh kecocokan [50] | Indeks karakter |

Flag yang relevan [50]:
- `re.ASCII`: membuat `\w`, `\W`, `\b`, `\B`, `\d`, `\D`, `\s`, `\S` hanya cocok dengan ASCII, bukan Unicode penuh.
- `re.IGNORECASE`: tidak membedakan huruf besar kecil (setara `(?i)`).
- `re.MULTILINE`: `^` dan `$` cocok di tiap baris.

**Relevansi PRISM:**
- **Posisi untuk laporan.** `m.start()` memberi kolom temuan (FR-04).
- **`\d` tanpa `re.ASCII` cocok dengan digit Unicode.** Dari definisi flag di [50], tanpa flag itu `\d` memakai pencocokan Unicode penuh. Untuk NIK sebaiknya `[0-9]` atau `re.ASCII`. Sebagai pembanding, `\d` di RE2 hanya ASCII (`[0-9]`) [48]. Perilakunya perlu diuji ⚠️.
- **Lookahead dan lookbehind didukung Python** [50], tetapi tidak didukung RE2 [48]. Itu sebabnya pola NIK sebaiknya tanpa lookaround agar bisa dipindah ke RE2.
- **Backtracking berlebihan.** Halaman [50] tidak membahas catastrophic backtracking maupun kompleksitas waktu. Peringatan "Python tidak menjamin waktu linear" di dokumen riset berasal dari pengetahuan umum dan perbandingan dengan RE2, bukan dari halaman ini ⚠️. Jaga pola tetap pendek dan terbatas (`[0-9]{16}`, bukan `.*`).

### 3.2 `os` dan `os.path`: menelusuri folder

> "This module provides a portable way of using operating system dependent functionality." [51]

| Fungsi | Cara kerja | Output |
|---|---|---|
| `os.walk(top, topdown=True, onerror=None, followlinks=False)` | Menelusuri pohon folder. Untuk tiap folder menghasilkan `(dirpath, dirnames, filenames)` [51] | Generator tiga-serangkai |
| `os.path.join(a, b, ...)` | Menyambung bagian path dengan pemisah yang benar [52] | String path |
| `os.path.getsize(path)` | Ukuran file dalam byte. Melempar `OSError` bila file tidak ada atau tidak bisa diakses [52] | Integer |
| `os.environ` | Pemetaan variabel lingkungan proses, misalnya `environ['HOME']` [51] | Dictionary-like |

Detail `os.walk` [51]:
- **Memangkas folder:** bila `topdown=True`, `dirnames` boleh diubah di tempat (`del` atau `remove`) dan `walk()` hanya masuk ke subfolder yang tersisa. Contoh resmi: `dirs.remove('__pycache__')`.
- **Symlink:** secara default `walk()` tidak masuk ke symlink yang mengarah ke folder. `followlinks=True` dapat menyebabkan rekursi tak berujung bila ada link ke folder induk.
- **Error:** "By default, errors from the `scandir()` call are ignored." Dengan `onerror` berupa fungsi, error dilaporkan lewat `OSError`.

**Relevansi PRISM:**
- **Melewati `.git`:** hapus `.git` dari `dirnames` agar tidak ditelusuri (sesuai keputusan "berkas dilewati" di MVP).
- **Folder `--exclude`:** cara yang sama.
- **Batas ukuran file:** `os.path.getsize` untuk file di atas 1 MB ⚠️ (angka batas masih tanda tanya di rencana).
- **Exit code 2.** Karena error `scandir()` **diabaikan secara default**, folder yang tidak bisa dibaca bisa terlihat seperti hasil bersih. Pakai `onerror` untuk mencatat error lalu keluar dengan kode 2 (NFR-07). Ini turunan dari dokumentasi [51], bukan kutipan.
- **Kunci HMAC:** `os.environ` untuk membaca kunci dari GitHub Secrets agar tidak tertulis di kode.

### 3.3 `json`: laporan

> "JSON ... is a lightweight data interchange format" [53]

| Fungsi | Cara kerja | Output |
|---|---|---|
| `json.dumps(obj)` | Mengubah objek Python menjadi string JSON [53] | `str` |
| `json.dump(obj, fp)` | Sama, tetapi menulis ke file. `fp` harus menerima `str` [53] | Berkas JSON |
| `json.loads(s)`, `json.load(fp)` | Kebalikannya. Melempar `JSONDecodeError` bila JSON tidak valid [53] | Objek Python |

Parameter yang relevan [53]:
- `indent`: bilangan bulat positif memberi indentasi. `None` (default) tanpa baris baru.
- `ensure_ascii`: default `True`, semua karakter non-ASCII di-escape (`ሴ`). `False` menulis apa adanya.

**Relevansi PRISM:** laporan `--json` (FR-05). Berkas hanya memuat lokasi dan nilai yang sudah di-mask, tidak pernah nilai PII utuh (NFR-04). `json.dump` ke berkas satu kali dalam satu laporan. Memanggil `dump` berulang pada berkas yang sama menghasilkan JSON tidak valid [53].

### 3.4 `sys`: exit code dan aliran data

| Fungsi | Cara kerja | Output |
|---|---|---|
| `sys.exit(arg)` | Melempar `SystemExit`. Integer = status keluar, 0 sukses, selain 0 "abnormal termination". Kebanyakan sistem hanya menerima 0–127 [54] | Kode keluar proses |
| `sys.stdin` | Aliran input standar [54] | Objek file teks |
| `sys.stdout` | Aliran untuk keluaran `print()` [54] | Objek file teks |
| `sys.stderr` | Aliran untuk pesan error interpreter [54] | Objek file teks |
| `sys.argv` | Daftar argumen baris perintah. `argv[0]` adalah nama skrip [54] | List string |

**Perangkap penting [54]:** bila `sys.exit()` diberi objek bukan integer (misalnya string), objek itu dicetak ke `stderr` dan kode keluarnya **1**, bukan 2. Untuk exit code 2 di PRISM, cetak pesan ke `sys.stderr` lalu panggil `sys.exit(2)` dengan integer.

**Relevansi PRISM:**
- **Gating CI (FR-06):** `sys.exit(0)` bersih, `sys.exit(1)` ada temuan, `sys.exit(2)` error pindai.
- **Mode stdin:** `prism scan -` membaca `sys.stdin` (mode `log` nanti).
- **Pesan error ke `sys.stderr`**, agar `stdout` hanya berisi laporan.

### 3.5 `argparse`: antarmuka perintah

> "The `argparse` module makes it easy to write user-friendly command-line interfaces." [55]

| Fungsi | Cara kerja | Output |
|---|---|---|
| `ArgumentParser(...)` | Wadah spesifikasi argumen [55] | Objek parser |
| `add_argument('path')` | Argumen posisi (wajib) [55] | - |
| `add_argument('--json', action='store_true')` | Opsi bernilai `True` bila diberikan, `False` bila tidak [55] | - |
| `add_argument('--min-level', choices=[...])` | Nilai dicek, error bila di luar pilihan [55] | - |
| `parse_args()` | Membaca `sys.argv`, mengembalikan namespace [55] | `Namespace` |

Perilaku lain [55]:
- Bantuan otomatis lewat `-h` atau `--help`.
- Argumen tidak valid menghasilkan pesan di `sys.stderr` dan kode keluar **2**.

**Relevansi PRISM:**
- Seluruh pintu masuk CLI: path, `--json`, `--output`, `--exclude` (boleh berulang), `--min-level`.
- **Bentrok makna kode 2.** Kesalahan penggunaan argumen sudah menghasilkan 2 dari `argparse` [55]. PRISM juga memakai 2 untuk error pindai. Keduanya tetap "bukan hasil bersih" dan sama-sama menggagalkan job, jadi tidak berbahaya, tetapi catat saat menulis dokumentasi pengguna.

### 3.6 `csv`: data uji dan evaluasi

> "The `csv` module implements classes to read and write tabular data in CSV format." [56]

| Fungsi | Cara kerja | Output |
|---|---|---|
| `csv.reader(f)` | Membaca baris, setiap baris berupa list string. Tidak ada konversi tipe otomatis [56] | Iterator list |
| `csv.DictReader(f)` | Memetakan baris ke dictionary. Bila `fieldnames` tidak diberikan, baris pertama jadi nama kolom [56] | Iterator dict |
| `csv.writer(f)` | Menulis baris. `None` ditulis sebagai string kosong, nilai lain di-`str()` [56] | Berkas CSV |
| `csv.DictWriter(f, fieldnames)` | `fieldnames` wajib. Kunci di luar `fieldnames` menimbulkan `ValueError` secara default [56] | Berkas CSV |

Saran resmi: buka berkas dengan `newline=''` [56].

**Relevansi PRISM:**
- Membaca label ground truth di `data/labels/` dan menulis hasil precision/recall di `evaluation/results/`.
- Membaca `provinsi.csv` dan `kecamatan.csv` (kode wilayah, lihat [mvp-t5.md](../planning/mvp-t5.md) bagian 4). Karena tidak ada konversi tipe, kode wilayah terbaca sebagai **string**, sehingga angka nol di depan (misalnya `11`, `1101`) tidak hilang.
- Bukan untuk mesin pemindai: scanner membaca berkas apa pun sebagai teks per baris.

### 3.7 `dataclasses`: struktur data

> "This module provides a decorator and functions for automatically adding generated special methods such as `__init__()` and `__repr__()` to user-defined classes." [58]

| Fitur | Cara kerja |
|---|---|
| `@dataclass` | Menghasilkan `__init__`, `__repr__`, dan `__eq__` dari variabel kelas yang diberi anotasi tipe [58] |
| `frozen=True` | Mengubah isi field menimbulkan `FrozenInstanceError`, sehingga objek bersifat read-only [58] |
| `field(default_factory=list)` | Nilai default berupa objek baru untuk tiap instance. Perlu untuk default yang bisa diubah, karena default `[]` ditolak [58] |

Sejak Python 3.13, `__eq__` membandingkan tiap field satu per satu [58].

**Relevansi PRISM:** `Rule(id, regex, context, validate)` dan `Finding(rule_id, file, line, column, value_masked, level)`. `frozen=True` cocok untuk temuan agar tidak berubah tidak sengaja.

### 3.8 `tomllib`: konfigurasi (opsi nanti)

- Menyediakan antarmuka untuk membaca TOML. **Tidak mendukung penulisan TOML.** Ditambahkan di Python 3.11 [57].
- **Relevansi PRISM:** bila rule dan allowlist dipindah ke berkas konfigurasi gaya Gitleaks, TOML cukup untuk membaca. Tidak ada di keputusan MVP, jadi hanya opsi.
- Python 3.13 (target MVP) sudah memilikinya. Interpreter default `python3` di mesin penulis saat riset ini adalah 3.10.14 dan **tidak punya** `tomllib` (diuji: `ModuleNotFoundError`). Lihat bagian 5.

## 4. Pertanyaan: apakah ada library di luar bawaan yang dipakai?

Untuk **scanner** yang berjalan di CI: **tidak**. Keputusan MVP menyebut Python dengan hanya library standar [mvp-t5.md bagian 4](../planning/mvp-t5.md). Tetapi di luar scanner ada beberapa yang bukan bawaan:

| Kategori | Item | Bawaan? | Sumber |
|---|---|---|---|
| **Scanner (dipasang di CI pengguna)** | `argparse`, `re`, `os`, `json`, `dataclasses`, `sys` | ✅ Semua bawaan | Keputusan MVP |
| **Pengembangan dan tes** | `pytest` | ❌ Perlu `pip install` | [mvp-t5.md](../planning/mvp-t5.md) langkah tes otomatis |
| **Pembuatan data uji** | `Faker` (`id_ID`) | ❌ Perlu `pip install` | [mvp-t5.md](../planning/mvp-t5.md) `make_dataset.py` |
| **Tes kompatibilitas RE2 (opsional)** | `google-re2` | ❌ Perlu `pip install` [47] | Rekomendasi sesi riset ini, bukan keputusan MVP |
| **Pembanding eksperimen** | Presidio, Betterleaks | ❌ Bukan dependensi | MVP: "keduanya hanya pembanding" |
| **Langkah workflow** | `actions/setup-python`, `actions/upload-artifact` | Bukan library Python, tetapi Action pihak ketiga | [mvp-t5.md](../planning/mvp-t5.md), tabel risiko |
| **Data referensi** | `provinsi.csv`, `kecamatan.csv` | Bukan library, hanya berkas data | [mvp-t5.md](../planning/mvp-t5.md) |

**Kesimpulan:** kode scanner-nya bisa bebas dari `pip install`. Tapi repo PRISM sebagai keseluruhan tetap memakai `pytest` dan `Faker` untuk pengembangan dan evaluasi. Pisahkan keduanya, misalnya dengan `requirements-dev.txt`, supaya pengguna scanner tidak ikut memasang alat uji.

## 5. Catatan versi Python

| Hal | Isi |
|---|---|
| Target MVP | Python 3.13, disamakan antara lokal dan CI ([mvp-t5.md](../planning/mvp-t5.md) bagian 4) |
| Interpreter default `python3` di mesin penulis | **3.10.14** (diuji 16 Nov. 2026) |
| Python 3.13 | Terpasang di `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13` (hasil `which`) |
| Python 3.12 | Terpasang di `/opt/homebrew/bin/python3.12` |
| Dampak | Menjalankan `python3 -m prism` di mesin ini bisa memakai 3.10, bukan 3.13. `tomllib` tidak tersedia di 3.10 [57]. Periksa `python3 --version` sebelum menjalankan tes |
| Versi dokumentasi | Ringkasan tidak menyebut versi halaman. Ada rujukan fitur 3.14 (`os.reload_environ`) di [51], jadi halaman bisa lebih baru dari 3.13. Cek catatan *Added in version* sebelum memakai fitur baru |

## 6. Library bawaan lain yang mungkin terpakai ⚠️

Belum dibaca di dokumentasi. Tulis hanya sebagai daftar kandidat sampai diverifikasi.

| Library | Kandidat untuk |
|---|---|
| `hmac`, `hashlib` | Fingerprint HMAC untuk allowlist atau baseline |
| `datetime` | Validasi tanggal lahir NIK |
| `fnmatch` | Pola path untuk allowlist |
| `pathlib` | Alternatif modern untuk `os.path` |
| `tempfile` | Berkas sementara di tes |
