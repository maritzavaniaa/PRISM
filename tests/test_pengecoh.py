"""Tes langkah 11: pengecoh (`fps`, gaya Gitleaks dan TruffleHog). UUID, timestamp, nomor rekening, dan
ID transaksi tidak boleh dilaporkan pada ambang bawaan. Semua nilai sintetis, ditulis tangan.

Pada ambang `low`, sebagian pengecoh memang muncul sebagai kandidat `low`. Itu perilaku yang dirancang
(tingkat `low` = bukti lemah) dan didokumentasikan di sini, bukan dianggap lolos.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from prism.engine import hapus_duplikat, periksa_baris, terapkan_ambang
from prism.rules import RULES

ROOT = Path(__file__).resolve().parent.parent

# (nilai, jenis kandidat `low` yang muncul pada ambang low, atau None bila tidak ada kandidat sama sekali)
PENGECOH = [
    # UUID
    ("550e8400-e29b-41d4-a716-446655440000", None),
    ("123e4567-e89b-12d3-a456-426614174000", None),
    ("f47ac10b-58cc-4372-a567-0e02b2c3d479", None),
    ("3b241101-e2bb-4255-8caf-4136c566a962", None),
    ("8d3f2a1c-81b2-4c9d-9e8f-123456789012", None),
    # timestamp
    ("20261125103045", None),
    ("1764058800000", None),
    ("1764058800", None),
    ("2026-11-25T10:30:45.123Z", None),
    ("20261125103045123", None),
    ("1764058800123456", "nik"),  # 16 digit: bentuk NIK, hari 88 tidak sah
    # nomor rekening
    ("1234567890", None),
    ("0123456789012", None),
    ("8201234567", "hp"),  # 10 digit berawalan 82: bentuk HP tanpa awalan
    ("123456789012345", None),
    ("4111111111111111", "nik"),  # 16 digit: provinsi 41 tidak ada
    # ID transaksi
    ("TRX-20261125-000123", None),
    ("INV/2026/11/0042", None),
    ("ORD20261125103045", None),
    ("TRX2026112510304500", "nik"),  # huruf tidak menghalangi, 16 digit di belakangnya
    # angka biasa
    ("v2.4.1", None),
    ("192.168.100.200", None),
    ("978-3-16-148410-0", None),
    ("Total Rp 1.250.000.000", None),
    ("Total Rp 8.123.456.789", "hp"),  # nominal berawalan 8 dengan pemisah titik
    ("sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", None),
]
IDS = [n[:28] for n, _ in PENGECOH]


def kandidat(nilai):
    return hapus_duplikat(periksa_baris("a.txt", 1, f"nilai {nilai} selesai", RULES), RULES)


@pytest.mark.parametrize("nilai, _", PENGECOH, ids=IDS)
def test_pengecoh_tidak_dilaporkan_pada_ambang_bawaan(nilai, _):
    lolos, _dibuang = terapkan_ambang(kandidat(nilai), "medium")
    assert lolos == []


@pytest.mark.parametrize("nilai, jenis_low", PENGECOH, ids=IDS)
def test_pengecoh_pada_ambang_low_didokumentasikan(nilai, jenis_low):
    # Perilaku saat ini. Bila berubah, perbarui daftar ini dan catat alasannya.
    hasil = [(t.rule_id, t.tingkat) for t in kandidat(nilai)]
    assert hasil == ([] if jenis_low is None else [(jenis_low, "low")])


def test_pengecoh_semuanya_dalam_satu_berkas_exit_0_pada_ambang_bawaan(tmp_path):
    (tmp_path / "pengecoh.txt").write_text("\n".join(f"nilai {n} selesai" for n, _ in PENGECOH) + "\n", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}

    bawaan = subprocess.run([sys.executable, "-m", "prism", "scan", str(tmp_path)], capture_output=True, text=True, env=env, cwd=ROOT)
    rendah = subprocess.run([sys.executable, "-m", "prism", "scan", str(tmp_path), "--min-level", "low"], capture_output=True, text=True, env=env, cwd=ROOT)

    jumlah_low = sum(1 for _, j in PENGECOH if j)
    assert bawaan.returncode == 0
    assert f"Tidak dilaporkan: {jumlah_low} kandidat low." in bawaan.stdout
    assert rendah.returncode == 1
    assert f"{jumlah_low} temuan" in rendah.stdout
