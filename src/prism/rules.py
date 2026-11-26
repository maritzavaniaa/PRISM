"""Isi rule PII (langkah 5 sampai 7: KF-07 sampai KF-09, KF-11 sampai KF-13).

Modul ini menyimpan DATA tiap rule: regex, fungsi penilaian, dan kata konteks.
Cara menjalankannya ada di engine.py. Menambah jenis PII baru cukup menambah
satu Rule di sini (KN-07).
"""

import re
from dataclasses import dataclass
from typing import Callable

from prism import domain_email, wilayah

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


# --- Nomor HP (langkah 7: KF-08, KF-12) ---

PEMISAH_HP = " .-"

# Awalan opsional (+62, 62, atau 0), lalu 8, digit 1-9, lalu 7-10 digit lagi: 9-12 digit
# dihitung dari angka 8. Pemisah (spasi, titik, strip) boleh ada di antara digit.
# Digit kedua 1-9 menurut Permenkominfo 14/2018. Panjang 9-12 digit dari metadata
# komunitas (libphonenumber) ⚠️ hipotesis. Batas bukan-digit di kiri dan kanan.
# Batas kanan hanya menolak digit yang LANGSUNG menempel: "0812-3456-7890-1234" tetap
# menghasilkan kandidat "0812-3456-7890" (batasan yang diterima).
POLA_HP = re.compile(
    r"(?<!\d)(?:(?:\+62|62|0)[ .-]?)?8[ .-]?[1-9](?:[ .-]?\d){7,10}(?!\d)",
    re.ASCII,
)

# Tanpa awalan, pola tampilan 3-4-4: 812-3456-7890.
POLA_HP_344 = re.compile(r"8\d\d[ .-]\d{4}[ .-]\d{4}", re.ASCII)


def assess_hp(nilai: str) -> str:
    """Tingkat bukti KF-12 (hipotesis, disetujui 24 Nov. 2026, diuji di langkah 13).

    high   : berawalan +62, atau berawalan 0 atau 62 dengan pemisah
    medium : berawalan 08 atau 62 berupa digit polos, atau tanpa awalan berpola 3-4-4
    low    : tanpa awalan selain itu (misalnya 81234567890 polos)

    62 berpemisah (62 812-3456-7890) tidak ada di tabel KF-12. Diperlakukan sama dengan
    0 berpemisah: alasannya sama (pemisah jarang muncul kebetulan) ⚠️ perluasan penyusun.
    """
    if nilai.startswith("+62"):
        return HIGH
    berpemisah = any(c in PEMISAH_HP for c in nilai)
    if nilai[0] in "06":  # awalan 0 atau 62
        return HIGH if berpemisah else MEDIUM
    return MEDIUM if POLA_HP_344.fullmatch(nilai) else LOW


HP = Rule(
    id="hp",
    regex=POLA_HP,
    assess=assess_hp,
    context=("hp", "telp", "telepon", "wa", "whatsapp", "kontak"),
)


# --- Email (langkah 7: KF-09, KF-13) ---

# Subset praktis RFC 5322 (format-pii-indonesia.md 7.3):
# - local-part: huruf, angka, dan _ % + -, dipisah titik tunggal (tidak di awal, akhir, atau berurutan), maks 64
# - domain: label huruf, angka, atau strip dipisah titik, minimal satu titik, TLD minimal 2 huruf, maks 255
# Lookbehind awal memastikan local-part diambil utuh. Local-part lebih dari 64 karakter
# tidak jadi kandidat, bukan dipotong. Tidak didukung: quoted-string, domain-literal,
# karakter ! # $ & ' * / = ? ^ ` { | } ~, dan domain internasional (IDN).
POLA_EMAIL = re.compile(
    r"(?<![A-Za-z0-9._%+-])"
    r"(?=[A-Za-z0-9._%+-]{1,64}@)"
    r"[A-Za-z0-9_%+-]+(?:\.[A-Za-z0-9_%+-]+)*"
    r"@"
    r"(?=[A-Za-z0-9.-]{1,255}(?![A-Za-z0-9.-]))"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,}"
    r"(?![A-Za-z0-9-])",
    re.ASCII,
)


def assess_email(nilai: str) -> str:
    """Tingkat bukti KF-13: medium bila domain ada di daftar penyedia email pribadi, selainnya low.

    Daftar dibaca dari berkas data (domain_email.py), bukan dari kode.
    """
    domain = nilai.rpartition("@")[2].lower()
    return MEDIUM if domain in domain_email.domain_pribadi() else LOW


EMAIL = Rule(id="email", regex=POLA_EMAIL, assess=assess_email, context=("email", "surel", "mail"))

# Urutan daftar ini juga dipakai dedup saat tingkat dan panjang sama (KF-16).
RULES = (NIK, HP, EMAIL)
