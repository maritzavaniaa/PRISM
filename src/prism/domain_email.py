"""Pemuatan daftar domain email pribadi untuk penilaian email (langkah 7: KF-13).

Data: src/prism/data/domain-email-pribadi.txt (satu domain per baris). Daftar ada di berkas
data, bukan di dalam kode, jadi mengubahnya tidak perlu mengubah kode.
Dimuat SEKALI per proses lalu disimpan (bukan per baris), dan dicek di awal pindai
seperti data wilayah: bila hilang atau rusak, PRISM keluar dengan kode 2.
"""

import re
from functools import lru_cache
from pathlib import Path

FILE_BAWAAN = Path(__file__).resolve().parent / "data" / "domain-email-pribadi.txt"

# Bentuk domain yang diterima di berkas: label huruf, angka, atau strip, dipisah titik, minimal satu titik.
POLA_DOMAIN = re.compile(r"[a-z0-9-]+(?:\.[a-z0-9-]+)+", re.ASCII)


@lru_cache(maxsize=None)
def muat_domain(path: str) -> frozenset:
    """Baca satu berkas daftar domain menjadi himpunan huruf kecil.

    Melempar OSError bila berkas tidak ada, dan ValueError bila daftarnya kosong atau
    ada baris yang bukan domain. Daftar kosong dilarang: diam-diam akan menurunkan semua
    email pribadi menjadi `low`.
    """
    with open(path, encoding="utf-8") as f:
        baris = [b.strip().lower() for b in f]
    domain = frozenset(b for b in baris if b and not b.startswith("#"))
    if not domain:
        raise ValueError(f"tidak ada domain di {path}")
    salah = sorted(d for d in domain if not POLA_DOMAIN.fullmatch(d))
    if salah:
        raise ValueError(f"{len(salah)} baris di {path} bukan domain (contoh: {salah[0]!r})")
    return domain


def domain_pribadi() -> frozenset:
    return muat_domain(str(FILE_BAWAAN))


def pastikan_termuat() -> None:
    """Muat daftar di awal pindai, supaya kegagalan muncul sebelum memindai."""
    domain_pribadi()
