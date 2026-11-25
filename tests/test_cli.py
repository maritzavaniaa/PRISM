"""Tes CLI (langkah 3: KF-01, KF-02, KN-08; langkah 4: ringkasan dan --exclude).

Menjalankan `python -m prism` sungguhan lewat subprocess, supaya exit code,
stdout, dan stderr diuji seperti yang dilihat CI.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

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
    assert "Baris dibaca: 3" in hasil.stdout
    assert "Berkas diperiksa: 1" in hasil.stdout
    assert hasil.stderr == ""


def test_scan_berkas_kosong_0_baris(tmp_path):
    berkas = tmp_path / "kosong.txt"
    berkas.write_text("", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert hasil.returncode == 0
    assert "Baris dibaca: 0" in hasil.stdout


def test_scan_baris_terakhir_tanpa_newline_tetap_terhitung(tmp_path):
    berkas = tmp_path / "tanpa_newline.txt"
    berkas.write_text("satu\ndua", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert "Baris dibaca: 2" in hasil.stdout


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


def test_scan_folder_mencetak_ringkasan_dan_exit_0(tmp_path):
    (tmp_path / "a.txt").write_text("satu\ndua\n", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("tiga\n", encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path))

    assert hasil.returncode == 0
    assert "Berkas diperiksa: 2" in hasil.stdout
    assert "Berkas dilewati: 0" in hasil.stdout
    assert "Berkas error: 0" in hasil.stdout
    assert "Baris dibaca: 3" in hasil.stdout


def test_exclude_bisa_diulang_dan_dihitung_dilewati(tmp_path):
    for nama in ("a", "b", "c"):
        (tmp_path / nama).mkdir()
        (tmp_path / nama / "x.txt").write_text("isi\n", encoding="utf-8")

    hasil = run_prism(
        "scan", str(tmp_path), "--exclude", str(tmp_path / "a"), "--exclude", "b"
    )

    assert hasil.returncode == 0
    assert "Berkas diperiksa: 1" in hasil.stdout
    assert "Berkas dilewati: 2" in hasil.stdout


def test_berkas_non_utf8_tidak_membuat_crash(tmp_path):
    berkas = tmp_path / "biner.txt"
    berkas.write_bytes(b"halo\n\xff\xfe\nlagi\n")

    hasil = run_prism("scan", str(berkas))

    assert hasil.returncode == 0
    assert "Baris dibaca: 3" in hasil.stdout


def test_python_yang_dipakai_adalah_3_13():
    # KN-08: versi sama di lokal dan CI. Gagal bila tes dijalankan dengan Python lain.
    assert sys.version_info[:2] == (3, 13)


# --- langkah 5: temuan NIK, mask, dan exit code (KF-20, KF-21) ---

NIK_SINTETIS = "3171011503900001"


def test_berkas_dengan_nik_exit_1_dan_nilai_utuh_tidak_tercetak(tmp_path):
    berkas = tmp_path / "data.txt"
    berkas.write_text(f"nik: {NIK_SINTETIS}\n", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert hasil.returncode == 1
    assert NIK_SINTETIS not in hasil.stdout
    assert NIK_SINTETIS not in hasil.stderr
    assert "************0001" in hasil.stdout
    assert "Temuan: 1" in hasil.stdout


def test_lokasi_temuan_berkas_baris_kolom(tmp_path):
    berkas = tmp_path / "data.txt"
    berkas.write_text(f"satu\ndua\nid nik = {NIK_SINTETIS}\n", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert f"{berkas}:3:10  nik  low  ************0001" in hasil.stdout


def test_berkas_bersih_exit_0(tmp_path):
    berkas = tmp_path / "bersih.txt"
    berkas.write_text("tidak ada data pribadi di sini\n317101150390000\n", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert hasil.returncode == 0
    assert "Temuan: 0" in hasil.stdout


def test_folder_dengan_nik_di_subfolder_exit_1(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "x.txt").write_text(NIK_SINTETIS + "\n", encoding="utf-8")
    (tmp_path / "bersih.txt").write_text("halo\n", encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path))

    assert hasil.returncode == 1
    assert NIK_SINTETIS not in hasil.stdout


def test_error_baca_didahulukan_atas_temuan_exit_2(tmp_path):
    if os.name == "nt" or os.geteuid() == 0:
        pytest.skip("butuh pengguna biasa di POSIX")
    (tmp_path / "a_ada_nik.txt").write_text(NIK_SINTETIS + "\n", encoding="utf-8")
    terkunci = tmp_path / "b_terkunci.txt"
    terkunci.write_text("isi\n", encoding="utf-8")
    terkunci.chmod(0o000)
    try:
        hasil = run_prism("scan", str(tmp_path))
    finally:
        terkunci.chmod(0o644)

    assert hasil.returncode == 2
    assert "Temuan: 1" in hasil.stdout  # temuan tetap dilaporkan
    assert NIK_SINTETIS not in hasil.stdout
