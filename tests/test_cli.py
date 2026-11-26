"""Tes CLI (langkah 3: KF-01, KF-02, KN-08; langkah 4: ringkasan dan --exclude).

Menjalankan `python -m prism` sungguhan lewat subprocess, supaya exit code,
stdout, dan stderr diuji seperti yang dilihat CI.
"""

import json
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


@pytest.fixture
def jalankan_json(tmp_path_factory):
    """Jalankan PRISM dengan --json --output ke folder lain (bukan folder yang dipindai). Kembalikan (proses, laporan)."""

    def _jalankan(*args):
        keluaran = tmp_path_factory.mktemp("laporan") / "r.json"
        hasil = run_prism(*args, "--json", "--output", str(keluaran))
        laporan = json.loads(keluaran.read_text(encoding="utf-8")) if keluaran.exists() else None
        return hasil, laporan

    return _jalankan


def test_scan_berkas_ada_exit_0_dan_mencetak_jumlah_baris(tmp_path, jalankan_json):
    berkas = tmp_path / "contoh.txt"
    berkas.write_text("satu\ndua\ntiga\n", encoding="utf-8")

    hasil, laporan = jalankan_json("scan", str(berkas))

    assert hasil.returncode == 0
    assert laporan["scan"]["lines"] == 3
    assert laporan["scan"]["files"] == 1
    assert "Berkas: 1 diperiksa, 0 dilewati, 0 error" in hasil.stdout
    assert hasil.stderr == ""


def test_scan_berkas_kosong_0_baris(tmp_path, jalankan_json):
    berkas = tmp_path / "kosong.txt"
    berkas.write_text("", encoding="utf-8")

    hasil, laporan = jalankan_json("scan", str(berkas))

    assert hasil.returncode == 0
    assert laporan["scan"]["lines"] == 0


def test_scan_baris_terakhir_tanpa_newline_tetap_terhitung(tmp_path, jalankan_json):
    berkas = tmp_path / "tanpa_newline.txt"
    berkas.write_text("satu\ndua", encoding="utf-8")

    _, laporan = jalankan_json("scan", str(berkas))

    assert laporan["scan"]["lines"] == 2


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


def test_scan_folder_mencetak_ringkasan_dan_exit_0(tmp_path, jalankan_json):
    (tmp_path / "a.txt").write_text("satu\ndua\n", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("tiga\n", encoding="utf-8")

    hasil, laporan = jalankan_json("scan", str(tmp_path))

    assert hasil.returncode == 0
    assert "Berkas: 2 diperiksa, 0 dilewati, 0 error" in hasil.stdout
    assert laporan["scan"]["files"] == 2
    assert laporan["scan"]["skipped"] == 0
    assert laporan["scan"]["errors"] == 0
    assert laporan["scan"]["lines"] == 3


def test_exclude_bisa_diulang_dan_dihitung_dilewati(tmp_path, jalankan_json):
    for nama in ("a", "b", "c"):
        (tmp_path / nama).mkdir()
        (tmp_path / nama / "x.txt").write_text("isi\n", encoding="utf-8")

    hasil, laporan = jalankan_json(
        "scan", str(tmp_path), "--exclude", str(tmp_path / "a"), "--exclude", "b"
    )

    assert hasil.returncode == 0
    assert "Berkas: 1 diperiksa, 2 dilewati, 0 error" in hasil.stdout
    assert (laporan["scan"]["files"], laporan["scan"]["skipped"]) == (1, 2)


def test_berkas_non_utf8_tidak_membuat_crash(tmp_path, jalankan_json):
    berkas = tmp_path / "biner.txt"
    berkas.write_bytes(b"halo\n\xff\xfe\nlagi\n")

    hasil, laporan = jalankan_json("scan", str(berkas))

    assert hasil.returncode == 0
    assert laporan["scan"]["lines"] == 3


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
    assert "1 temuan (nik 1)." in hasil.stdout


def test_lokasi_temuan_berkas_baris_kolom(tmp_path):
    berkas = tmp_path / "data.txt"
    berkas.write_text(f"satu\ndua\nid nik = {NIK_SINTETIS}\n", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert f"{berkas}:3:10  nik  high  ************0001" in hasil.stdout


def test_berkas_bersih_exit_0(tmp_path):
    berkas = tmp_path / "bersih.txt"
    berkas.write_text("tidak ada data pribadi di sini\n317101150390000\n", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert hasil.returncode == 0
    assert "0 temuan." in hasil.stdout


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
    assert "1 temuan (nik 1)." in hasil.stdout  # temuan tetap dilaporkan
    assert "Pindai tidak lengkap." in hasil.stdout
    assert f"ERROR {terkunci}: tidak bisa dibaca" in hasil.stdout
    assert NIK_SINTETIS not in hasil.stdout


# --- langkah 6: tingkat bukti end-to-end dan data wilayah (Gerbang 1) ---


def test_tingkat_nik_di_keluaran_high_medium_low(tmp_path):
    berkas = tmp_path / "data.txt"
    berkas.write_text(
        "3171011503900001\n3171991503900001\n1234567890123456\n", encoding="utf-8"
    )

    hasil = run_prism("scan", str(berkas), "--min-level", "low")

    assert hasil.returncode == 1
    assert f"{berkas}:1:1  nik  high  ************0001" in hasil.stdout
    assert f"{berkas}:2:1  nik  medium  ************0001" in hasil.stdout
    assert f"{berkas}:3:1  nik  low  ************3456" in hasil.stdout
    for utuh in ("3171011503900001", "3171991503900001", "1234567890123456"):
        assert utuh not in hasil.stdout
        assert utuh not in hasil.stderr


def test_data_wilayah_hilang_exit_2_bukan_1(tmp_path, monkeypatch, capsys):
    # Crash Python berkode 1 akan terbaca sebagai "ada temuan". Harus 2 dengan pesan jelas.
    from prism import cli, wilayah

    berkas = tmp_path / "data.txt"
    berkas.write_text("3171011503900001\n", encoding="utf-8")
    monkeypatch.setattr(wilayah, "FOLDER_BAWAAN", tmp_path / "tidak-ada")

    kode = cli.main(["scan", str(berkas)])

    keluar = capsys.readouterr()
    assert kode == 2
    assert "data kode wilayah" in keluar.err
    assert keluar.out == ""


# --- langkah 7: HP dan email end-to-end ---


def test_satu_berkas_berisi_nik_hp_dan_email_tingkat_dasar(tmp_path):
    # Tanpa kata konteks, jadi yang terlihat adalah tingkat bukti murni. --min-level low agar low ikut tampil.
    berkas = tmp_path / "campuran.txt"
    berkas.write_text(
        "3171011503900001\n"
        "+62 812-3456-7890\n"
        "081234567890\n"
        "81234567890\n"
        "budi@gmail.com\n"
        "git@github.com:user/repo.git\n",
        encoding="utf-8",
    )

    hasil = run_prism("scan", str(berkas), "--min-level", "low")

    assert hasil.returncode == 1
    assert f"{berkas}:1:1  nik  high  ************0001" in hasil.stdout
    assert f"{berkas}:2:1  hp  high  *************7890" in hasil.stdout
    assert f"{berkas}:3:1  hp  medium  ********7890" in hasil.stdout
    assert f"{berkas}:4:1  hp  low  *******7890" in hasil.stdout
    assert f"{berkas}:5:1  email  medium  ****@gmail.com" in hasil.stdout
    assert f"{berkas}:6:1  email  low  ***@github.com" in hasil.stdout
    assert "6 temuan (nik 1, hp 3, email 2)." in hasil.stdout
    for utuh in ("3171011503900001", "081234567890", "budi@", "812-3456-7890"):
        assert utuh not in hasil.stdout
        assert utuh not in hasil.stderr


# --- langkah 8: konteks, ambang, dedup, judul CSV ---


def test_ambang_bawaan_medium_membuang_low_dan_menghitungnya(tmp_path):
    berkas = tmp_path / "a.txt"
    berkas.write_text(
        "3171011503900001\n3171991503900001\n1234567890123456\n", encoding="utf-8"
    )

    hasil = run_prism("scan", str(berkas))

    assert hasil.returncode == 1
    assert "nik  high" in hasil.stdout and "nik  medium" in hasil.stdout
    assert "nik  low" not in hasil.stdout
    assert "2 temuan (nik 2)." in hasil.stdout
    assert "Tidak dilaporkan: 1 kandidat low." in hasil.stdout


def test_hanya_low_pada_ambang_bawaan_exit_0(tmp_path):
    # Hanya kandidat yang DILAPORKAN yang membuat exit 1.
    berkas = tmp_path / "a.txt"
    berkas.write_text("ref: 1234567890123456\n", encoding="utf-8")

    bawaan = run_prism("scan", str(berkas))
    rendah = run_prism("scan", str(berkas), "--min-level", "low")

    assert bawaan.returncode == 0
    assert "0 temuan. Tidak dilaporkan: 1 kandidat low." in bawaan.stdout
    assert rendah.returncode == 1
    assert "Tidak dilaporkan: 0 kandidat low." in rendah.stdout


def test_min_level_high_hanya_melaporkan_high(tmp_path):
    berkas = tmp_path / "a.txt"
    berkas.write_text("3171011503900001\n3171991503900001\n1234567890123456\n", encoding="utf-8")

    hasil = run_prism("scan", str(berkas), "--min-level", "high")

    assert "1 temuan (" in hasil.stdout
    assert "nik  high" in hasil.stdout
    # Hanya low yang dihitung. medium yang dibuang pada ambang high tidak terhitung (keputusan langkah 8).
    assert "Tidak dilaporkan: 1 kandidat low." in hasil.stdout


def test_min_level_tidak_valid_ditolak():
    hasil = run_prism("scan", ".", "--min-level", "sedang")

    assert hasil.returncode == 2
    assert "invalid choice" in hasil.stderr


def test_konteks_menaikkan_nik_low_sebelum_ambang(tmp_path):
    # Urutan: konteks SEBELUM ambang. Bila ambang lebih dulu, baris pertama ikut terbuang.
    berkas = tmp_path / "a.txt"
    berkas.write_text("nik: 1234567890123456\nref: 1234567890123456\n", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert f"{berkas}:1:6  nik  medium  ************3456" in hasil.stdout
    assert f"{berkas}:2:" not in hasil.stdout
    assert "Tidak dilaporkan: 1 kandidat low." in hasil.stdout


def test_judul_kolom_csv_menjadi_konteks(tmp_path):
    berkas = tmp_path / "data.csv"
    berkas.write_text(
        "id,nama,nik,kota\n1,Budi,1234567890123456,Jakarta\n2,Ani,1234567890123456 ,Bandung\n"
        "3,Cici,Jakarta,1234567890123456\n",
        encoding="utf-8",
    )

    hasil = run_prism("scan", str(berkas))

    assert f"{berkas}:2:8  nik  medium  ************3456" in hasil.stdout
    assert f"{berkas}:3:7  nik  medium  ************3456" in hasil.stdout
    assert f"{berkas}:4:" not in hasil.stdout  # kolom `kota`, bukan `nik`
    assert "Tidak dilaporkan: 1 kandidat low." in hasil.stdout


def test_judul_kolom_csv_hp_tanpa_nol_dan_titik_koma(tmp_path):
    # Excel berlokal Indonesia memakai titik koma. HP tanpa nol di depan hanya terlaporkan lewat judul kolom.
    berkas = tmp_path / "pemohon.csv"
    berkas.write_text(
        "id;nama;Phone Number;catatan\n1;Budi;81234567890;ok\n2;Ani;ok;81234567890\n",
        encoding="utf-8",
    )

    hasil = run_prism("scan", str(berkas))

    assert f"{berkas}:2:8  hp  medium  *******7890" in hasil.stdout
    assert f"{berkas}:3:" not in hasil.stdout
    assert "1 temuan (" in hasil.stdout


def test_judul_bukan_csv_tidak_dibaca(tmp_path):
    # Baris pertama berkas .txt bukan header, walau berisi kata nik.
    berkas = tmp_path / "a.txt"
    berkas.write_text("id,nama,nik,kota\n1,Budi,1234567890123456,Jakarta\n", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert hasil.returncode == 0
    assert "Tidak dilaporkan: 1 kandidat low." in hasil.stdout


def test_header_csv_tanpa_digit_tetap_dibaca(tmp_path, jalankan_json):
    # Header biasanya tidak lolos prefilter (tanpa digit), tetapi tetap harus dicatat.
    berkas = tmp_path / "a.csv"
    berkas.write_text("nik\n1234567890123456\n", encoding="utf-8")

    hasil, laporan = jalankan_json("scan", str(berkas))

    assert f"{berkas}:2:1  nik  medium" in hasil.stdout
    assert laporan["scan"]["lines_prefiltered"] == 1


def test_dedup_di_keluaran_email_dengan_digit_hp(tmp_path):
    berkas = tmp_path / "a.txt"
    berkas.write_text("08123456789@gmail.com\n", encoding="utf-8")

    hasil = run_prism("scan", str(berkas))

    assert "1 temuan (" in hasil.stdout
    assert "email  medium  ***********@gmail.com" in hasil.stdout
