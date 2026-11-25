"""Pemuatan kode wilayah untuk penilaian NIK (langkah 6: KF-11).

Data: src/prism/data/kode-wilayah/{provinsi,kecamatan}.csv (kolom `kode`, `nama`).
Data ikut berada di dalam paket prism, jadi menyalin folder src/prism/ sudah membawa datanya.
Tiap berkas dimuat SEKALI per proses lalu disimpan (bukan per baris).

Risiko data hilang atau rusak di produksi: mvp-t5.md bagian 5.1.
"""

import csv
from functools import lru_cache
from pathlib import Path

# Data berada di sebelah kode: src/prism/data/kode-wilayah/ (satu folder dengan modul ini).
FOLDER_BAWAAN = Path(__file__).resolve().parent / "data" / "kode-wilayah"

PANJANG_PROVINSI = 2
PANJANG_KECAMATAN = 6


@lru_cache(maxsize=None)
def muat_kode(nama_berkas: str, folder: str, panjang: int | None = None) -> frozenset:
    """Baca kolom `kode` dari satu CSV menjadi himpunan.

    Melempar OSError bila berkas tidak ada, dan ValueError bila kolom `kode`
    tidak ada, datanya kosong, atau (bila `panjang` diberikan) ada kode yang bukan
    digit dengan panjang itu. Himpunan kosong dilarang: diam-diam akan membuat
    semua NIK turun tingkat tanpa ada yang tahu.
    """
    path = Path(folder) / nama_berkas
    with open(path, encoding="utf-8", newline="") as f:
        pembaca = csv.DictReader(f)
        if pembaca.fieldnames is None or "kode" not in pembaca.fieldnames:
            raise ValueError(f"kolom 'kode' tidak ada di {path}")
        kode = frozenset(baris["kode"].strip() for baris in pembaca if baris["kode"].strip())
    if not kode:
        raise ValueError(f"tidak ada kode di {path}")
    if panjang is not None:
        salah = sorted(k for k in kode if not (len(k) == panjang and k.isascii() and k.isdigit()))
        if salah:
            raise ValueError(
                f"{len(salah)} kode di {path} bukan {panjang} digit (contoh: {salah[0]!r})"
            )
    return kode


def provinsi() -> frozenset:
    return muat_kode("provinsi.csv", str(FOLDER_BAWAAN), PANJANG_PROVINSI)


def kecamatan() -> frozenset:
    return muat_kode("kecamatan.csv", str(FOLDER_BAWAAN), PANJANG_KECAMATAN)


def pastikan_termuat() -> None:
    """Muat semua data wilayah di awal pindai, supaya kegagalan muncul sebelum memindai."""
    provinsi()
    kecamatan()
