"""Tes langkah 4: penelusuran folder dan prefilter (KF-03 sampai KF-06, KN-06).

Memakai tmp_path pytest. Semua isi berkas sintetis.
"""

import os

import pytest

from prism.scanner import BATAS_UKURAN_BYTE, lolos_prefilter, scan


def tulis(path, isi="isi\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(isi, bytes):
        path.write_bytes(isi)
    else:
        path.write_text(isi, encoding="utf-8")
    return path


# --- KF-03: penelusuran folder ---


def test_folder_bersarang_jumlah_berkas_sama_dengan_hitungan_manual(tmp_path):
    tulis(tmp_path / "a.txt")
    tulis(tmp_path / "s1" / "b.txt")
    tulis(tmp_path / "s1" / "s2" / "c.txt")
    tulis(tmp_path / "s1" / "s2" / "s3" / "d.txt")
    tulis(tmp_path / "lain" / "e.txt")

    hasil = scan(str(tmp_path))

    assert hasil.berkas_diperiksa == 5
    assert hasil.berkas_dilewati == 0
    assert hasil.berkas_error == 0


def test_folder_kosong_tidak_ada_berkas(tmp_path):
    hasil = scan(str(tmp_path))

    assert hasil.berkas_diperiksa == 0


def test_penelusuran_terurut_abjad_dan_bisa_diulang(tmp_path):
    for nama in ("z.txt", "a.txt", "m/k.txt", "b/c.txt"):
        tulis(tmp_path / nama, "12345678\n")

    def urutan():
        dilihat = []
        scan(str(tmp_path), proses_baris=lambda p, n, t: dilihat.append(os.path.relpath(p, tmp_path)))
        return dilihat

    pertama = urutan()

    # os.walk top-down: berkas di folder itu dulu (abjad), lalu subfolder (abjad).
    assert pertama == ["a.txt", "z.txt", os.path.join("b", "c.txt"), os.path.join("m", "k.txt")]
    assert urutan() == pertama


# --- KF-04: yang dilewati ---


def test_folder_git_dilewati_dan_terhitung(tmp_path):
    tulis(tmp_path / "a.txt")
    tulis(tmp_path / ".git" / "config")
    tulis(tmp_path / ".git" / "objects" / "ab" / "cd")

    hasil = scan(str(tmp_path))

    assert hasil.berkas_diperiksa == 1
    assert hasil.berkas_dilewati == 2


def test_exclude_diulang_dua_kali(tmp_path):
    tulis(tmp_path / "a" / "x.txt")
    tulis(tmp_path / "b" / "y.txt")
    tulis(tmp_path / "b" / "dalam" / "z.txt")
    tulis(tmp_path / "c" / "w.txt")

    hasil = scan(str(tmp_path), exclude=[str(tmp_path / "a"), "b"])

    assert hasil.berkas_diperiksa == 1
    assert hasil.berkas_dilewati == 3  # a/x, b/y, b/dalam/z


def test_exclude_path_bersarang_relatif_ke_folder_yang_dipindai(tmp_path):
    tulis(tmp_path / "data" / "synthetic" / "x.txt")
    tulis(tmp_path / "data" / "lain.txt")

    hasil = scan(str(tmp_path), exclude=[os.path.join("data", "synthetic")])

    assert hasil.berkas_diperiksa == 1
    assert hasil.berkas_dilewati == 1


def test_exclude_tidak_cocok_dengan_nama_folder_di_tempat_lain(tmp_path):
    # "tests" hanya dikecualikan sebagai path, bukan sebagai nama di mana saja.
    tulis(tmp_path / "src" / "tests" / "x.txt")

    hasil = scan(str(tmp_path), exclude=["tests"])

    assert hasil.berkas_diperiksa == 1
    assert hasil.berkas_dilewati == 0


@pytest.mark.parametrize("nama", ["gambar.png", "arsip.ZIP", "dok.pdf", "lib.so"])
def test_ekstensi_biner_dilewati(tmp_path, nama):
    tulis(tmp_path / nama, "teks biasa\n")

    hasil = scan(str(tmp_path))

    assert hasil.berkas_diperiksa == 0
    assert hasil.berkas_dilewati == 1


def test_berkas_dengan_byte_nol_dilewati(tmp_path):
    tulis(tmp_path / "data.dat", b"abc\x00def\n")

    hasil = scan(str(tmp_path))

    assert hasil.berkas_diperiksa == 0
    assert hasil.berkas_dilewati == 1


def test_byte_nol_setelah_1_kb_pertama_tidak_dicek(tmp_path):
    # Batas pengecekan 1 KB (KF-04): nol di luar itu tidak membuat berkas dilewati.
    tulis(tmp_path / "data.dat", b"a" * 1024 + b"\x00\n")

    hasil = scan(str(tmp_path))

    assert hasil.berkas_diperiksa == 1


def test_berkas_lebih_dari_1_mb_dilewati(tmp_path):
    tulis(tmp_path / "besar.txt", b"a" * (BATAS_UKURAN_BYTE + 1))

    hasil = scan(str(tmp_path))

    assert hasil.berkas_diperiksa == 0
    assert hasil.berkas_dilewati == 1


def test_berkas_tepat_1_mb_masih_dipindai(tmp_path):
    # Keputusan langkah 4: batas inklusif. Tepat 1.000.000 byte dipindai.
    tulis(tmp_path / "pas.txt", b"a" * BATAS_UKURAN_BYTE)

    hasil = scan(str(tmp_path))

    assert hasil.berkas_diperiksa == 1
    assert hasil.berkas_dilewati == 0


def test_symlink_tidak_diikuti(tmp_path):
    asli = tulis(tmp_path / "asli" / "x.txt")
    (tmp_path / "tautan_berkas.txt").symlink_to(asli)
    (tmp_path / "tautan_folder").symlink_to(tmp_path / "asli", target_is_directory=True)

    hasil = scan(str(tmp_path))

    assert hasil.berkas_diperiksa == 1  # hanya asli/x.txt
    assert hasil.berkas_dilewati == 2


# --- KF-05: membaca teks ---


def test_non_utf8_terbaca_tanpa_error(tmp_path):
    tulis(tmp_path / "campur.txt", b"halo\n\xff\xfe\nlagi\n")

    hasil = scan(str(tmp_path))

    assert hasil.berkas_diperiksa == 1
    assert hasil.berkas_error == 0
    assert hasil.baris_dibaca == 3


@pytest.mark.skipif(os.name == "nt" or os.geteuid() == 0, reason="butuh pengguna biasa di POSIX")
def test_berkas_tanpa_izin_baca_error_dan_pindai_lanjut(tmp_path):
    terkunci = tulis(tmp_path / "a_terkunci.txt")
    tulis(tmp_path / "b_biasa.txt", "satu\ndua\n")
    terkunci.chmod(0o000)
    try:
        hasil = scan(str(tmp_path))
    finally:
        terkunci.chmod(0o644)

    assert hasil.berkas_error == 1
    assert hasil.berkas_diperiksa == 1  # b_biasa tetap diperiksa
    assert hasil.baris_dibaca == 2
    assert any("a_terkunci.txt" in pesan for pesan in hasil.pesan_error)


def test_hitung_baris_dan_baris_terakhir_tanpa_newline(tmp_path):
    tulis(tmp_path / "a.txt", "satu\ndua")

    hasil = scan(str(tmp_path))

    assert hasil.baris_dibaca == 2


def test_berkas_tunggal_dipindai_langsung(tmp_path):
    berkas = tulis(tmp_path / "a.txt", "satu\ndua\ntiga\n")

    hasil = scan(str(berkas))

    assert hasil.berkas_diperiksa == 1
    assert hasil.baris_dibaca == 3


# --- KF-06: prefilter ---


@pytest.mark.parametrize(
    "baris",
    [
        "0812-3456-7890",
        "+62 812 3456 7890",
        "01.234.567.8-901.000",
        "nik 3171011503900001 terdaftar",
        "12345678",
    ],
)
def test_prefilter_lolos_bila_digit_minimal_8(baris):
    assert lolos_prefilter(baris) is True


@pytest.mark.parametrize(
    "baris",
    [
        "",
        "tanpa angka sama sekali",
        "1234567",  # 7 digit
        "ada 1234 lalu 567",  # 7 digit tersebar
    ],
)
def test_prefilter_tidak_lolos_bila_digit_kurang_dari_8(baris):
    assert lolos_prefilter(baris) is False


def test_prefilter_menghitung_digit_tersebar_di_baris():
    # Sengaja longgar (KF-06): 8 digit tersebar tetap lolos. Rule yang menyaring lebih lanjut.
    assert lolos_prefilter("tahun 2026, bulan 11, tgl 25") is True


def test_prefilter_lolos_bila_ada_at():
    assert lolos_prefilter("kontak: budi@gmail.com") is True
    assert lolos_prefilter("@") is True


def test_prefilter_tidak_menghitung_digit_unicode():
    assert lolos_prefilter("²²²²²²²²²²") is False  # superscript bukan digit 0-9


def test_scan_meneruskan_hanya_baris_yang_lolos_prefilter(tmp_path):
    tulis(
        tmp_path / "a.txt",
        "tanpa angka\n0812-3456-7890\nbudi@gmail.com\n123\n",
    )
    diterima = []

    hasil = scan(str(tmp_path), proses_baris=lambda p, n, t: diterima.append((n, t)))

    assert diterima == [(2, "0812-3456-7890"), (3, "budi@gmail.com")]
    assert hasil.baris_dibaca == 4
    assert hasil.baris_lolos_prefilter == 2


# --- angka ringkasan vs hitungan manual ---


def test_ringkasan_sesuai_hitungan_manual_pada_folder_uji_kecil(tmp_path):
    tulis(tmp_path / "a.txt", "satu\n0812-3456-7890\n")  # diperiksa, 2 baris, 1 lolos
    tulis(tmp_path / "sub" / "b.py", "x@y.com\nz\nw\n")  # diperiksa, 3 baris, 1 lolos
    tulis(tmp_path / "gambar.png", "abc")  # dilewati (ekstensi)
    tulis(tmp_path / "bin.dat", b"\x00\x01")  # dilewati (byte nol)
    tulis(tmp_path / ".git" / "HEAD")  # dilewati (.git)
    tulis(tmp_path / "keluar" / "q.txt")  # dilewati (--exclude)

    hasil = scan(str(tmp_path), exclude=["keluar"])

    assert (
        hasil.berkas_diperiksa,
        hasil.berkas_dilewati,
        hasil.berkas_error,
        hasil.baris_dibaca,
        hasil.baris_lolos_prefilter,
    ) == (2, 4, 0, 5, 2)
