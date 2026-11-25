"""Isi rule PII (langkah 5: KF-07).

Modul ini menyimpan DATA tiap rule: regex, fungsi penilaian, dan kata konteks.
Cara menjalankannya ada di engine.py. Menambah jenis PII baru cukup menambah
satu Rule di sini (KN-07).
"""

import re
from dataclasses import dataclass
from typing import Callable

from prism import wilayah

HIGH = "high"
MEDIUM = "medium"
LOW = "low"


@dataclass(frozen=True)
class Rule:
    id: str
    regex: re.Pattern
    assess: Callable[[str], str]  # nilai kandidat -> HIGH / MEDIUM / LOW
    context: tuple = ()  # kata konteks, dipakai mulai langkah 8


# NIK: tepat 16 digit berurutan yang tidak diapit digit lain (KF-07).
# (?<!\d) dan (?!\d) hanya melihat DIGIT. Huruf di depan atau di belakang tidak
# menghalangi: "abc3171011503900001" tetap kandidat. NIK yang ditulis dengan spasi
# atau strip tidak terdeteksi (batasan yang diterima, mvp-t5 5.2).
# re.ASCII: \d hanya 0-9. Tanpa itu \d juga cocok dengan digit Unicode (misalnya Arab-Indic).
POLA_NIK = re.compile(r"(?<!\d)\d{16}(?!\d)", re.ASCII)

# Jumlah hari maksimum per bulan. Februari 29 karena tahun lahir tidak dicek (KF-11).
HARI_MAKSIMUM = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
                 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def _enam_belas_digit_ascii(nilai: str) -> bool:
    return len(nilai) == 16 and nilai.isascii() and nilai.isdigit()


def tanggal_valid(nilai: str) -> bool:
    """Digit 7-8 hari (01-31 laki-laki, 41-71 perempuan), digit 9-10 bulan 01-12.

    Jumlah hari harus sesuai bulan. 29 Februari diterima. Tahun tidak dicek.
    """
    if not _enam_belas_digit_ascii(nilai):
        return False
    hari = int(nilai[6:8])
    bulan = int(nilai[8:10])
    if 41 <= hari <= 71:
        hari -= 40  # perempuan: hari + 40
    elif not 1 <= hari <= 31:
        return False
    return 1 <= bulan <= 12 and hari <= HARI_MAKSIMUM[bulan]


def provinsi_valid(nilai: str) -> bool:
    """2 digit pertama ada di provinsi.csv."""
    return nilai[:2] in wilayah.provinsi()


def kecamatan_valid(nilai: str) -> bool:
    """6 digit pertama ada di kecamatan.csv."""
    return nilai[:6] in wilayah.kecamatan()


def assess_nik(nilai: str) -> str:
    """Tingkat bukti KF-11.

    high   : tanggal sah dan kecamatan terdaftar
    medium : tanggal sah dan provinsi terdaftar, kecamatan tidak ditemukan
    low    : selainnya (termasuk 16 digit acak)
    Nomor urut (4 digit terakhir) tidak dicek: tidak ada aturannya. NIK berawalan 99
    (WNI di luar negeri) belum ditangani dan jatuh ke low karena 99 bukan provinsi.
    """
    if not tanggal_valid(nilai) or not provinsi_valid(nilai):
        return LOW
    return HIGH if kecamatan_valid(nilai) else MEDIUM


NIK = Rule(id="nik", regex=POLA_NIK, assess=assess_nik, context=("nik", "ktp"))

# Urutan daftar ini juga dipakai dedup saat tingkat dan panjang sama (KF-16).
RULES = (NIK,)
