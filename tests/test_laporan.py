"""Tes langkah 9 end-to-end: JSON, nilai utuh tidak bocor, exit code, keterulangan, tanpa jaringan.

Semua nilai sintetis. Memakai subprocess supaya yang diuji persis yang dilihat CI.
"""

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
POLA_BARIS = re.compile(r"^.+:\d+:\d+  (nik|hp|email)  (high|medium|low)  [*0-9A-Za-z@.\-]+$")

NIK = "3171011503900001"
HP = "081234567890"
HP_PLUS = "+62 812-3456-7890"
EMAIL = "budi.santoso@gmail.com"
ISI_PII = f"nik: {NIK}\nhp: {HP}\nkontak {HP_PLUS}\nemail: {EMAIL}\n"


def run_prism(*args):
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-m", "prism", *args], capture_output=True, text=True, env=env, cwd=ROOT
    )


@pytest.fixture
def laporan_di(tmp_path_factory):
    return tmp_path_factory.mktemp("laporan") / "prism-report.json"


# --- JSON (KF-18, KF-19) ---


def test_json_ditulis_dengan_struktur_lengkap(tmp_path, laporan_di):
    (tmp_path / "data.txt").write_text(ISI_PII + "ref: 1234567890123456\n", encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path), "--json", "--output", str(laporan_di))
    laporan = json.loads(laporan_di.read_text(encoding="utf-8"))

    assert hasil.returncode == 1
    assert list(laporan) == ["schema_version", "findings", "scan"]
    assert laporan["schema_version"] == 1
    assert len(laporan["findings"]) == 4
    for f in laporan["findings"]:
        assert set(f) == {"rule_id", "level", "location", "match"}
        assert f["level"] in ("high", "medium", "low") and "score" not in f
        assert set(f["location"]) == {"file", "line", "column", "target"}
        assert set(f["match"]) == {"value"}
    assert laporan["scan"]["mode"] == "repo"
    assert laporan["scan"]["findings"] == 4
    assert laporan["scan"]["findings_by_rule"] == {"nik": 1, "hp": 2, "email": 1}
    assert laporan["scan"]["suppressed_low"] == 1  # `ref:` tanpa kata konteks
    assert laporan["scan"]["min_level"] == "medium"
    assert f"Laporan JSON: {laporan_di}" in hasil.stdout


def test_ringkasan_json_pada_folder_uji(tmp_path, laporan_di):
    (tmp_path / "a.txt").write_text(f"nik: {NIK}\nsatu\n", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("dua\ntiga\n", encoding="utf-8")
    (tmp_path / "foto.png").write_bytes(b"\x89PNG")

    run_prism("scan", str(tmp_path), "--json", "--output", str(laporan_di))
    ringkasan = json.loads(laporan_di.read_text(encoding="utf-8"))["scan"]

    assert (ringkasan["files"], ringkasan["skipped"], ringkasan["errors"]) == (2, 1, 0)
    assert ringkasan["lines"] == 4
    assert ringkasan["lines_prefiltered"] == 1


def test_min_level_tercatat_di_json(tmp_path, laporan_di):
    (tmp_path / "a.txt").write_text("ref: 1234567890123456\n", encoding="utf-8")

    run_prism("scan", str(tmp_path), "--min-level", "low", "--json", "--output", str(laporan_di))
    laporan = json.loads(laporan_di.read_text(encoding="utf-8"))

    assert laporan["scan"]["min_level"] == "low"
    assert [f["level"] for f in laporan["findings"]] == ["low"]
    assert laporan["scan"]["suppressed_low"] == 0


def test_json_ditulis_pada_exit_0_1_dan_2(tmp_path, tmp_path_factory):
    bersih = tmp_path / "bersih"
    bersih.mkdir()
    (bersih / "a.txt").write_text("halo\n", encoding="utf-8")
    ada = tmp_path / "ada"
    ada.mkdir()
    (ada / "a.txt").write_text(f"nik: {NIK}\n", encoding="utf-8")

    for path, kode in ((bersih, 0), (ada, 1), (tmp_path / "tidak-ada", 2)):
        keluaran = tmp_path_factory.mktemp("r") / "r.json"
        hasil = run_prism("scan", str(path), "--json", "--output", str(keluaran))
        assert hasil.returncode == kode
        assert json.loads(keluaran.read_text(encoding="utf-8"))["schema_version"] == 1

    # Error sebelum pindai tetap menghasilkan JSON dengan errors = 1.
    assert json.loads(keluaran.read_text(encoding="utf-8"))["scan"]["errors"] == 1


def test_json_tanpa_output_dan_output_tanpa_json_ditolak(tmp_path):
    (tmp_path / "a.txt").write_text("halo\n", encoding="utf-8")

    tanpa_output = run_prism("scan", str(tmp_path), "--json")
    tanpa_json = run_prism("scan", str(tmp_path), "--output", str(tmp_path / "x.json"))

    for hasil in (tanpa_output, tanpa_json):
        assert hasil.returncode == 2
        assert "--json dan --output harus dipakai bersama" in hasil.stderr
        assert hasil.stdout == ""
    assert not (tmp_path / "x.json").exists()


def test_json_gagal_ditulis_exit_2_dengan_pesan_jelas(tmp_path):
    (tmp_path / "a.txt").write_text("halo\n", encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path), "--json", "--output", str(tmp_path / "tidak-ada" / "r.json"))

    assert hasil.returncode == 2
    assert "laporan JSON tidak bisa ditulis" in hasil.stderr
    assert "Laporan JSON:" not in hasil.stdout
    assert "0 temuan." in hasil.stdout


# --- teks (KF-17) ---


def test_tiap_baris_temuan_cocok_pola(tmp_path):
    (tmp_path / "data.txt").write_text(ISI_PII, encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path))
    baris_temuan = [b for b in hasil.stdout.splitlines() if re.search(r":\d+:\d+  ", b)]

    assert len(baris_temuan) == 4
    for baris in baris_temuan:
        assert POLA_BARIS.match(baris), baris
    assert hasil.stdout.splitlines()[0] == f"Memindai: {tmp_path}"
    assert hasil.stdout.splitlines()[1] == "Berkas: 1 diperiksa, 0 dilewati, 0 error"
    assert hasil.stdout.splitlines()[-1].startswith("4 temuan (nik 1, hp 2, email 1). Tidak dilaporkan: 0 kandidat low.")


def test_urutan_temuan_berkas_baris_kolom(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "a.txt").write_text(f"x\nnik: {NIK}\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text(f"{NIK} dan {NIK}\n", encoding="utf-8")
    (tmp_path / "a.txt").write_text(f"nik: {NIK}\n", encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path))
    lokasi = [b.split("  ")[0].replace(str(tmp_path) + "/", "") for b in hasil.stdout.splitlines() if "  nik  " in b]

    assert lokasi == ["a.txt:1:6", "b.txt:1:1", "b.txt:1:22", "sub/a.txt:2:6"]


def test_keterulangan_dua_kali_jalan_identik(tmp_path, tmp_path_factory):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "a.txt").write_text(ISI_PII, encoding="utf-8")
    (tmp_path / "b.csv").write_text(f"id,nik\n1,{NIK}\n", encoding="utf-8")
    keluar = []
    for _ in range(2):
        r = tmp_path_factory.mktemp("ulang") / "r.json"
        hasil = run_prism("scan", str(tmp_path), "--json", "--output", str(r))
        keluar.append((hasil.stdout.replace(str(r), "<json>"), hasil.returncode, r.read_text(encoding="utf-8")))

    assert keluar[0] == keluar[1]


# --- nilai utuh tidak muncul (KF-20, KN-04) ---


UTUH = (NIK, HP, "812-3456-7890", EMAIL, "budi.santoso", "3456 7890")


def test_nilai_utuh_tidak_ada_di_stdout_stderr_dan_json(tmp_path, laporan_di):
    (tmp_path / "data.txt").write_text(ISI_PII, encoding="utf-8")

    hasil = run_prism("scan", str(tmp_path), "--min-level", "low", "--json", "--output", str(laporan_di))
    gabungan = hasil.stdout + hasil.stderr + laporan_di.read_text(encoding="utf-8")

    assert hasil.returncode == 1
    for utuh in UTUH:
        assert utuh not in gabungan
    assert "************0001" in gabungan and "************@gmail.com" in gabungan


@pytest.mark.skipif(os.name == "nt" or os.geteuid() == 0, reason="butuh pengguna biasa di POSIX")
def test_nilai_utuh_tidak_ada_pada_error_baca_berkas(tmp_path, laporan_di):
    (tmp_path / "a_data.txt").write_text(ISI_PII, encoding="utf-8")
    terkunci = tmp_path / "b_terkunci.txt"
    terkunci.write_text(ISI_PII, encoding="utf-8")
    terkunci.chmod(0o000)
    try:
        hasil = run_prism("scan", str(tmp_path), "--json", "--output", str(laporan_di))
    finally:
        terkunci.chmod(0o644)
    gabungan = hasil.stdout + hasil.stderr + laporan_di.read_text(encoding="utf-8")

    assert hasil.returncode == 2
    assert "ERROR" in hasil.stdout and "tidak bisa dibaca" in hasil.stdout
    for utuh in UTUH:
        assert utuh not in gabungan


def test_nilai_utuh_tidak_ada_di_repr_temuan():
    from prism.engine import Temuan

    assert NIK not in repr(Temuan("a", 1, 1, "nik", "high", NIK))


# --- exit code (KF-21) ---


def test_tiga_exit_code(tmp_path):
    bersih = tmp_path / "bersih.txt"
    bersih.write_text("halo\n", encoding="utf-8")
    ada = tmp_path / "ada.txt"
    ada.write_text(f"nik: {NIK}\n", encoding="utf-8")

    assert run_prism("scan", str(bersih)).returncode == 0
    assert run_prism("scan", str(ada)).returncode == 1
    assert run_prism("scan", str(tmp_path / "tidak-ada")).returncode == 2


def test_hanya_low_pada_ambang_bawaan_tidak_menggagalkan(tmp_path):
    (tmp_path / "a.txt").write_text("ref: 1234567890123456\n", encoding="utf-8")

    assert run_prism("scan", str(tmp_path)).returncode == 0
    assert run_prism("scan", str(tmp_path), "--min-level", "low").returncode == 1


# --- tanpa jaringan (KN-04) ---

MODUL_JARINGAN = {"socket", "urllib", "http", "requests", "ftplib", "smtplib", "ssl", "xmlrpc", "telnetlib", "poplib", "imaplib"}


def test_kode_tidak_mengimpor_modul_jaringan():
    ditemukan = []
    for berkas in (ROOT / "src").rglob("*.py"):
        for node in ast.walk(ast.parse(berkas.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                nama = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                nama = [node.module.split(".")[0]]
            else:
                continue
            ditemukan += [(berkas.name, n) for n in nama if n in MODUL_JARINGAN]

    assert ditemukan == []
