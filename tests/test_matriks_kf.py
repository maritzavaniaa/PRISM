"""Tes langkah 11 (KF-27): matriks KF → tes tidak punya baris kosong, dan tiap tes yang disebut ada."""

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATRIKS = ROOT / "docs" / "planning" / "matriks-kf-tes.md"
MVP = ROOT / "docs" / "planning" / "mvp-t5.md"
POLA_BARIS = re.compile(r"^\| (KF-\d+) \|(.*)$", re.M)
POLA_RUJUKAN = re.compile(r"tests/([\w]+\.py)::(\w+)")
# KF yang sengaja belum punya tes, beserta alasannya. Setiap tambahan di sini harus punya alasan tertulis.
DIKECUALIKAN = {"KF-26": "evaluate.py dibuat di langkah 13"}


def baca_matriks():
    return {kf: isi for kf, isi in POLA_BARIS.findall(MATRIKS.read_text(encoding="utf-8"))}


def kf_di_spesifikasi():
    teks = MVP.read_text(encoding="utf-8")
    return set(re.findall(r"^\| (KF-\d+) \|", teks, re.M)) | set(re.findall(r"^\*\*(KF-\d+)\.", teks, re.M))


def test_semua_kf_di_spesifikasi_ada_di_matriks():
    assert kf_di_spesifikasi() - set(baca_matriks()) == set()
    assert len(kf_di_spesifikasi()) >= 29


def test_kf_01_sampai_24_masing_masing_punya_tes():
    matriks = baca_matriks()
    for n in range(1, 25):
        assert POLA_RUJUKAN.findall(matriks[f"KF-{n:02d}"]), f"KF-{n:02d} tidak punya tes"


def test_semua_kf_punya_tes_yang_ada():
    matriks = baca_matriks()
    kosong = [kf for kf, isi in matriks.items() if not POLA_RUJUKAN.findall(isi) and kf not in DIKECUALIKAN]
    assert kosong == []
    hilang = []
    for kf, isi in matriks.items():
        for berkas, fungsi in POLA_RUJUKAN.findall(isi):
            sumber = ROOT / "tests" / berkas
            if not sumber.exists():
                hilang.append((kf, berkas, "berkas"))
                continue
            nama = {n.name for n in ast.walk(ast.parse(sumber.read_text(encoding="utf-8"))) if isinstance(n, ast.FunctionDef)}
            if fungsi not in nama:
                hilang.append((kf, berkas, fungsi))
    assert hilang == []


def test_kf_yang_dikecualikan_punya_alasan_di_matriks():
    matriks = baca_matriks()
    for kf in DIKECUALIKAN:
        assert "Belum ada tes" in matriks[kf]
