"""Tes langkah 3: kerangka CLI (KF-01, KF-02, KN-08).

Menjalankan `python -m prism` sungguhan lewat subprocess, supaya exit code,
stdout, dan stderr diuji seperti yang dilihat CI.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_prism(*args):
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-m", "prism", *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=ROOT,
    )


def test_scan_berkas_ada_exit_0_dan_mencetak_jumlah_baris(tmp_path):
    berkas = tmp_path / "contoh.txt"
    berkas.write_text("satu\ndua\ntiga\n", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert hasil.returncode == 0
    assert "3 baris" in hasil.stdout
    assert hasil.stderr == ""


def test_scan_berkas_kosong_0_baris(tmp_path):
    berkas = tmp_path / "kosong.txt"
    berkas.write_text("", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert hasil.returncode == 0
    assert "0 baris" in hasil.stdout


def test_scan_baris_terakhir_tanpa_newline_tetap_terhitung(tmp_path):
    berkas = tmp_path / "tanpa_newline.txt"
    berkas.write_text("satu\ndua", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert "2 baris" in hasil.stdout


def test_scan_path_tidak_ada_exit_2_pesan_di_stderr(tmp_path):
    hasil = run_prism("scan", str(tmp_path / "tidak-ada.txt"))

    assert hasil.returncode == 2
    assert "tidak ditemukan" in hasil.stderr
    assert hasil.stdout == ""


def test_tanpa_argumen_exit_2():
    hasil = run_prism()

    assert hasil.returncode == 2
    assert hasil.stdout == ""


def test_scan_tanpa_path_exit_2():
    hasil = run_prism("scan")

    assert hasil.returncode == 2
    assert hasil.stdout == ""


def test_scan_folder_sementara_exit_2(tmp_path):
    # Perilaku sementara langkah 3. Diganti di langkah 4 (penelusuran folder).
    hasil = run_prism("scan", str(tmp_path))

    assert hasil.returncode == 2
    assert "folder belum didukung" in hasil.stderr


def test_berkas_non_utf8_tidak_membuat_crash(tmp_path):
    berkas = tmp_path / "biner.txt"
    berkas.write_bytes(b"halo\n\xff\xfe\nlagi\n")

    hasil = run_prism("scan", str(berkas))

    assert hasil.returncode == 0
    assert "3 baris" in hasil.stdout


def test_python_yang_dipakai_adalah_3_13():
    # KN-08: versi sama di lokal dan CI. Gagal bila tes dijalankan dengan Python lain.
    assert sys.version_info[:2] == (3, 13)
