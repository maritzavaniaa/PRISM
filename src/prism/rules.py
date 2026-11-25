"""Isi rule PII (langkah 5: KF-07).

Modul ini menyimpan DATA tiap rule: regex, fungsi penilaian, dan kata konteks.
Cara menjalankannya ada di engine.py. Menambah jenis PII baru cukup menambah
satu Rule di sini (KN-07).
"""

import re
from dataclasses import dataclass
from typing import Callable

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
POLA_NIK = re.compile(r"(?<!\d)\d{16}(?!\d)")


def assess_nik(nilai: str) -> str:
    """SEMENTARA (langkah 5): semua kandidat 16 digit bertingkat low.

    Langkah 6 menggantinya dengan penilaian KF-11 (tanggal, provinsi, kecamatan).
    """
    return LOW


NIK = Rule(id="nik", regex=POLA_NIK, assess=assess_nik, context=("nik", "ktp"))

# Urutan daftar ini juga dipakai dedup saat tingkat dan panjang sama (KF-16).
RULES = (NIK,)
