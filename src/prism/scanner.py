"""Penelusuran folder dan prefilter baris (langkah 4: KF-03 sampai KF-06).

Tugas modul ini: menemukan berkas yang layak dibaca, membaca barisnya, dan
meneruskan hanya baris yang lolos prefilter ke penerima (rule dipasang di
langkah 5). Modul ini tidak tahu apa itu NIK, HP, atau email.
"""

import os
from dataclasses import dataclass, field

BATAS_UKURAN_BYTE = 1_000_000  # berkas > batas ini dilewati; tepat 1.000.000 byte masih dipindai
UKURAN_CEK_BYTE_NOL = 1024
MIN_DIGIT_PREFILTER = 8
FOLDER_SELALU_DILEWATI = ".git"
EKSTENSI_BERJUDUL = frozenset({".csv", ".tsv"})  # baris pertama diteruskan sebagai header (langkah 8)

# Ekstensi biner umum (KF-04). Daftar ini penilaian penulis, bukan standar.
EKSTENSI_BINER = frozenset(
    {
        # gambar
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".tif", ".tiff",
        # arsip dan kemasan
        ".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar", ".whl", ".jar",
        # dokumen biner
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        # media
        ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv",
        # font
        ".ttf", ".otf", ".woff", ".woff2",
        # program dan objek
        ".exe", ".dll", ".so", ".dylib", ".class", ".pyc", ".o", ".bin",
    }
)

_DIGIT = "0123456789"  # bukan str.isdigit(): itu juga menerima digit Unicode seperti "²"


@dataclass
class ScanResult:
    berkas_diperiksa: int = 0
    berkas_dilewati: int = 0
    berkas_error: int = 0
    baris_dibaca: int = 0
    baris_lolos_prefilter: int = 0
    pesan_error: list = field(default_factory=list)


def lolos_prefilter(baris: str) -> bool:
    """KF-06: ≥ 8 karakter digit (walau terpisah spasi, titik, atau strip) atau ada '@'."""
    if "@" in baris:
        return True
    jumlah = 0
    for ch in baris:
        if ch in _DIGIT:
            jumlah += 1
            if jumlah >= MIN_DIGIT_PREFILTER:
                return True
    return False


def _hitung_berkas(folder: str) -> int:
    """Jumlah semua berkas di bawah folder (untuk folder yang dilewati)."""
    return sum(len(files) for _, _, files in os.walk(folder))


def _alasan_dilewati(path: str) -> str | None:
    """Kembalikan alasan berkas dilewati, atau None bila layak dibaca. Bisa melempar OSError."""
    if os.path.islink(path):
        return "symlink"
    if os.path.splitext(path)[1].lower() in EKSTENSI_BINER:
        return "biner (ekstensi)"
    if os.path.getsize(path) > BATAS_UKURAN_BYTE:
        return "lebih dari 1 MB"
    with open(path, "rb") as f:
        if b"\x00" in f.read(UKURAN_CEK_BYTE_NOL):
            return "biner (byte nol)"
    return None


def _periksa_berkas(path: str, hasil: ScanResult, proses_baris, proses_header=None) -> None:
    try:
        if _alasan_dilewati(path) is not None:
            hasil.berkas_dilewati += 1
            return
        dibaca = 0
        lolos = 0
        berjudul = proses_header is not None and os.path.splitext(path)[1].lower() in EKSTENSI_BERJUDUL
        with open(path, encoding="utf-8", errors="replace") as f:
            for nomor, teks in enumerate(f, start=1):
                dibaca += 1
                teks = teks.rstrip("\r\n")
                if berjudul and nomor == 1:
                    proses_header(path, teks)  # header tidak melewati prefilter: biasanya tanpa digit
                if lolos_prefilter(teks):
                    lolos += 1
                    if proses_baris is not None:
                        proses_baris(path, nomor, teks)
    except OSError as e:
        hasil.berkas_error += 1
        hasil.pesan_error.append(f"{path}: tidak bisa dibaca ({e.strerror})")
        return
    hasil.berkas_diperiksa += 1
    hasil.baris_dibaca += dibaca
    hasil.baris_lolos_prefilter += lolos


def _folder_dikecualikan(root: str, exclude) -> set:
    """Path absolut folder yang dikecualikan. Tiap --exclude dicoba relatif ke cwd dan ke folder yang dipindai."""
    hasil = set()
    for e in exclude:
        hasil.add(os.path.abspath(e))
        hasil.add(os.path.abspath(os.path.join(root, e)))
    return hasil


def scan(path: str, exclude=(), proses_baris=None, proses_header=None) -> ScanResult:
    """Pindai satu berkas atau satu folder.

    proses_baris(path, nomor_baris, teks) dipanggil untuk tiap baris yang lolos
    prefilter. proses_header(path, teks) dipanggil untuk baris pertama berkas .csv dan .tsv,
    tanpa prefilter. Urutan penelusuran diurutkan abjad supaya hasil bisa diulang (KN-06).
    """
    hasil = ScanResult()

    if not os.path.isdir(path):
        _periksa_berkas(path, hasil, proses_baris, proses_header)
        return hasil

    dikecualikan = _folder_dikecualikan(path, exclude)

    def saat_error(e: OSError) -> None:
        hasil.berkas_error += 1
        hasil.pesan_error.append(f"{e.filename}: folder tidak bisa dibuka ({e.strerror})")

    for dirpath, dirnames, filenames in os.walk(path, onerror=saat_error):
        dirnames.sort()
        filenames.sort()

        tersisa = []
        for nama in dirnames:
            sub = os.path.join(dirpath, nama)
            if os.path.islink(sub):
                hasil.berkas_dilewati += 1  # symlink folder tidak diikuti
            elif nama == FOLDER_SELALU_DILEWATI or os.path.abspath(sub) in dikecualikan:
                hasil.berkas_dilewati += _hitung_berkas(sub)
            else:
                tersisa.append(nama)
        dirnames[:] = tersisa  # os.walk tidak masuk ke folder yang dibuang dari daftar

        for nama in filenames:
            _periksa_berkas(os.path.join(dirpath, nama), hasil, proses_baris, proses_header)

    return hasil
