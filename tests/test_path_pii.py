"""Tes perluasan T5 (26 Nov. 2026): PII di nama berkas dan folder dipindai, dan path disamarkan di semua keluaran."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from prism.engine import rentang_sensitif
from prism.report import samarkan_rentang
from prism.rules import RULES

ROOT = Path(__file__).resolve().parent.parent
NIK = "3171011503900001"
NIK_LOW = "1234567890123456"
MASK = "************0001"


def run_prism(*args):
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-m", "prism", *args], capture_output=True, text=True, env=env, cwd=ROOT
    )


@pytest.fixture
def laporan_di(tmp_path_factory):
    return tmp_path_factory.mktemp("laporan") / "prism-report.json"


def lokasi(hasil, tmp_path):
    """Baris temuan tanpa awalan folder uji, supaya mudah dibandingkan."""
    return [b.replace(str(tmp_path) + "/", "") for b in hasil.stdout.splitlines() if "  nik  " in b or "  hp  " in b or "  email  " in b]


# --- unit: rentang dan penyamaran ---


def test_rentang_sensitif_dan_samarkan_rentang():
    teks = f"data/KTP_{NIK}.jpg"

    hasil = samarkan_rentang(teks, rentang_sensitif(teks, RULES, "medium"))

    assert hasil == f"data/KTP_{MASK}.jpg"
    assert len(hasil) == len(teks)


def test_rentang_di_bawah_ambang_tidak_disamarkan():
    teks = f"backup_{NIK_LOW}.sql"  # low: tanggal tidak sah, tanpa kata konteks

    assert rentang_sensitif(teks, RULES, "medium") == []
    assert rentang_sensitif(teks, RULES, "low") == [(7, 23)]


def test_kata_konteks_di_path_menaikkan_tingkat_rentang():
    assert rentang_sensitif(f"ktp_{NIK_LOW}.jpg", RULES, "medium") == [(4, 20)]


def test_rentang_beririsan_digabung():
    teks = "kontak/08123456789@gmail.com"  # HP dan email beririsan

    [(awal, akhir)] = rentang_sensitif(teks, RULES, "medium")

    assert teks[awal:akhir] == "08123456789@gmail.com"


def test_samarkan_tanpa_rentang_tidak_mengubah_teks():
    assert samarkan_rentang("a/b/c.txt", []) == "a/b/c.txt"


# --- poin 1: nama berkas dan folder dipindai ---


def test_nama_berkas_biner_dengan_nik_dilaporkan_di_baris_0(tmp_path):
    (tmp_path / f"KTP_{NIK}.jpg").write_bytes(b"\x89PNG\x00")

    hasil = run_prism("scan", str(tmp_path))

    assert hasil.returncode == 1
    assert lokasi(hasil, tmp_path) == [f"KTP_{MASK}.jpg:0:5  nik  high  {MASK}"]
    assert "Berkas: 0 diperiksa, 1 dilewati, 0 error" in hasil.stdout  # isinya tetap dilewati


def test_nama_folder_dengan_nik_dilaporkan(tmp_path):
    (tmp_path / NIK).mkdir()
    (tmp_path / NIK / "isi.txt").write_text("halo\n", encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path))

    assert hasil.returncode == 1
    assert lokasi(hasil, tmp_path) == [f"{MASK}:0:1  nik  high  {MASK}"]


def test_nama_dengan_email_dan_hp_dilaporkan(tmp_path):
    (tmp_path / "budi.santoso@gmail.com_ekspor.txt").write_text("x\n", encoding="utf-8")
    (tmp_path / "hp_+6281234567890.log").write_text("x\n", encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path))

    rules = sorted(b.split("  ")[1] for b in lokasi(hasil, tmp_path))
    assert rules == ["email", "hp"]
    assert "budi.santoso" not in hasil.stdout and "6281234567890" not in hasil.stdout


def test_email_di_nama_yang_diikuti_ekstensi_domainnya_menelan_ekstensi(tmp_path):
    # Batasan yang diterima: "budi@gmail.com.txt" dibaca sebagai domain `gmail.com.txt`, bukan
    # `gmail.com`, sehingga `low` dan tidak dilaporkan pada ambang bawaan. Perbaikan yang
    # dipertimbangkan: cocokkan awalan domain (gmail.com + ".txt"). Ditunda, mengubah KF-13.
    (tmp_path / "budi@gmail.com.txt").write_text("x\n", encoding="utf-8")

    bawaan = run_prism("scan", str(tmp_path))
    rendah = run_prism("scan", str(tmp_path), "--min-level", "low")

    assert bawaan.returncode == 0
    assert rendah.returncode == 1


def test_nama_low_tidak_dilaporkan_pada_ambang_bawaan_dan_dihitung(tmp_path):
    (tmp_path / f"backup_{NIK_LOW}.sql").write_text("x\n", encoding="utf-8")

    bawaan = run_prism("scan", str(tmp_path))
    rendah = run_prism("scan", str(tmp_path), "--min-level", "low")

    assert bawaan.returncode == 0
    assert "Tidak dilaporkan: 1 kandidat low." in bawaan.stdout
    assert rendah.returncode == 1
    assert lokasi(rendah, tmp_path) == [f"backup_************3456.sql:0:8  nik  low  ************3456"]


def test_kata_konteks_di_nama_menaikkan_tingkat(tmp_path):
    (tmp_path / f"ktp_{NIK_LOW}.jpg").write_bytes(b"\x00")

    hasil = run_prism("scan", str(tmp_path))

    assert hasil.returncode == 1
    assert lokasi(hasil, tmp_path) == [f"ktp_************3456.jpg:0:5  nik  medium  ************3456"]


def test_nama_berkas_csv_tidak_memakai_judul_kolom(tmp_path):
    # Nama berkas bukan baris CSV: judul kolom `nik` di berkas itu tidak boleh menaikkannya.
    (tmp_path / f"data_{NIK_LOW}.csv").write_text("nik,nama\n", encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path))

    assert hasil.returncode == 0


def test_nama_folder_akar_tidak_dipindai(tmp_path):
    akar = tmp_path / NIK
    akar.mkdir()
    (akar / "a.txt").write_text("halo\n", encoding="utf-8")

    hasil = run_prism("scan", str(akar))

    assert hasil.returncode == 0
    assert "0 temuan." in hasil.stdout


def test_berkas_tunggal_nama_dipindai(tmp_path):
    berkas = tmp_path / f"{NIK}.txt"
    berkas.write_text("halo\n", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert hasil.returncode == 1
    assert f"{MASK}.txt:0:1  nik  high  {MASK}" in hasil.stdout


# --- poin 2: path disamarkan di semua keluaran ---


def test_path_dengan_nik_disamarkan_di_baris_temuan_isi(tmp_path):
    (tmp_path / f"{NIK}.txt").write_text(f"nik: {NIK}\n", encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path))

    assert f"{MASK}.txt:1:6  nik  high  {MASK}" in hasil.stdout
    assert f"{MASK}.txt:0:1  nik  high  {MASK}" in hasil.stdout
    assert NIK not in hasil.stdout + hasil.stderr


def test_path_disamarkan_di_json_dan_ada_target(tmp_path, laporan_di):
    (tmp_path / f"{NIK}.txt").write_text(f"nik: {NIK}\n", encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path), "--json", "--output", str(laporan_di))
    teks = laporan_di.read_text(encoding="utf-8")
    temuan = json.loads(teks)["findings"]

    assert NIK not in teks and NIK not in hasil.stdout
    assert sorted((f["location"]["line"], f["location"]["target"]) for f in temuan) == [(0, "name"), (1, "content")]
    assert all(f["location"]["file"].endswith(f"{MASK}.txt") for f in temuan)


def test_urutan_temuan_mengikuti_path_asli_bukan_path_tersamar(tmp_path):
    # Urutan memakai path asli supaya stabil. Dua kali jalan harus identik.
    (tmp_path / f"b_{NIK}.txt").write_text(f"{NIK}\n", encoding="utf-8")
    (tmp_path / f"a_{NIK}.txt").write_text(f"{NIK}\n", encoding="utf-8")

    pertama = run_prism("scan", str(tmp_path)).stdout
    kedua = run_prism("scan", str(tmp_path)).stdout

    assert pertama == kedua
    baris = [b for b in pertama.splitlines() if "  nik  " in b]
    assert [b.split("/")[-1][:2] for b in baris] == ["a_", "a_", "b_", "b_"]


@pytest.mark.skipif(os.name == "nt" or os.geteuid() == 0, reason="butuh pengguna biasa di POSIX")
def test_path_pada_pesan_error_disamarkan(tmp_path):
    terkunci = tmp_path / f"{NIK}.txt"
    terkunci.write_text("isi\n", encoding="utf-8")
    terkunci.chmod(0o000)
    try:
        hasil = run_prism("scan", str(tmp_path))
    finally:
        terkunci.chmod(0o644)

    assert hasil.returncode == 2
    assert f"ERROR {tmp_path}/{MASK}.txt: tidak bisa dibaca" in hasil.stdout
    assert NIK not in hasil.stdout + hasil.stderr


def test_path_akar_dan_output_disamarkan(tmp_path):
    akar = tmp_path / f"proyek_{NIK}"
    akar.mkdir()
    (akar / "a.txt").write_text("halo\n", encoding="utf-8")
    keluaran = tmp_path / f"laporan_{NIK}.json"

    hasil = run_prism("scan", str(akar), "--json", "--output", str(keluaran))

    assert hasil.returncode == 0
    assert f"Memindai: {tmp_path}/proyek_{MASK}" in hasil.stdout
    assert f"Laporan JSON: {tmp_path}/laporan_{MASK}.json" in hasil.stdout
    assert NIK not in hasil.stdout + hasil.stderr
    assert keluaran.exists()  # berkas ditulis di path asli, hanya tampilannya yang disamarkan


def test_path_tidak_ditemukan_pada_stderr_disamarkan(tmp_path):
    hasil = run_prism("scan", str(tmp_path / f"{NIK}.txt"))

    assert hasil.returncode == 2
    assert "tidak ditemukan" in hasil.stderr
    assert NIK not in hasil.stderr and MASK in hasil.stderr


def test_path_bersih_tidak_berubah(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "data_2026-11-25.txt").write_text(f"nik: {NIK}\n", encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path))

    assert f"{tmp_path}/sub/data_2026-11-25.txt:1:6  nik  high  {MASK}" in hasil.stdout
