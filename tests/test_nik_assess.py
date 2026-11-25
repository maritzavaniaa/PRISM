"""Tes langkah 6: penilaian bukti NIK (KF-11, KF-10). Semua nilai sintetis.

Contoh nilai: docs/research/format-pii-indonesia.md bagian 2.4.
Tingkat dihitung tanpa kata konteks.
"""

import pytest

from prism import wilayah
from prism.engine import periksa_baris
from prism.rules import (
    HIGH,
    LOW,
    MEDIUM,
    RULES,
    assess_nik,
    kecamatan_valid,
    provinsi_valid,
    tanggal_valid,
)

# --- tabel tingkat: satu baris satu kasus ---


@pytest.mark.parametrize(
    "nik, tingkat, alasan",
    [
        ("3171011503900001", HIGH, "Jakarta Pusat, Gambir, laki-laki"),
        ("3171015503900002", HIGH, "perempuan (hari 55 = 15 + 40)"),
        ("3171991503900001", MEDIUM, "kecamatan 99 tidak ada"),
        ("4171011503900001", LOW, "provinsi 41 tidak ada"),
        ("3171011513900001", LOW, "bulan 13"),
        ("3171013203900001", LOW, "hari 32"),
        ("3171010003900001", LOW, "hari 00"),
        ("3171017203900001", LOW, "hari 72"),
        ("3171014003900001", LOW, "hari 40 (di antara dua rentang)"),
        ("3171010004900001", LOW, "hari 00 di bulan lain"),
        ("1234567890123456", LOW, "hanya 16 digit"),
        ("0000000000000000", LOW, "nol semua"),
    ],
)
def test_tabel_tingkat_kf11(nik, tingkat, alasan):
    assert assess_nik(nik) == tingkat, alasan


@pytest.mark.parametrize(
    "nik",
    [
        "3171013104900001",  # 31 April (April hanya 30 hari)
        "3171013002900001",  # 30 Februari
        "3171013102900001",  # 31 Februari
        "3171017104900001",  # perempuan 71 - 40 = 31 April
    ],
)
def test_hari_melebihi_jumlah_hari_bulan_itu_low(nik):
    # Kecamatan 317101 terdaftar, jadi yang menurunkan ke low hanya tanggalnya.
    assert kecamatan_valid(nik)
    assert assess_nik(nik) == LOW


def test_29_februari_tidak_ditolak_karena_tahun_tidak_dicek():
    assert assess_nik("3171012902900001") == HIGH  # 1990 bukan kabisat, tetap diterima
    assert assess_nik("3171016902900001") == HIGH  # perempuan 69 - 40 = 29


def test_batas_hari_laki_laki_dan_perempuan():
    assert assess_nik("3171010103900001") == HIGH  # 01
    assert assess_nik("3171013103900001") == HIGH  # 31 Maret
    assert assess_nik("3171014103900001") == HIGH  # 41 (perempuan, hari 1)
    assert assess_nik("3171017103900001") == HIGH  # 71 (perempuan, hari 31)


def test_bulan_batas_01_dan_12():
    assert assess_nik("3171011501900001") == HIGH
    assert assess_nik("3171011512900001") == HIGH
    assert assess_nik("3171011500900001") == LOW


def test_nik_berawalan_99_belum_ditangani_jatuh_ke_low():
    # WNI di luar negeri (PP 40/2019 Pasal 32). Didokumentasikan lewat tes ini.
    # 99 bukan provinsi, jadi bahkan dengan tanggal sah hasilnya low.
    assert assess_nik("9971011503900001") == LOW


def test_nomor_urut_tidak_dicek():
    assert assess_nik("3171011503900000") == HIGH
    assert assess_nik("3171011503909999") == HIGH


def test_tahun_lahir_tidak_dicek():
    assert assess_nik("3171011503000001") == HIGH
    assert assess_nik("3171011503990001") == HIGH


# --- pemeriksa satu per satu ---


def test_tanggal_valid_menolak_nilai_bukan_16_digit_ascii():
    assert tanggal_valid("3171011503900001") is True
    assert tanggal_valid("317101150390000") is False  # 15 digit
    assert tanggal_valid("31710115039000011") is False  # 17 digit
    assert tanggal_valid("31710115039000a1") is False  # ada huruf
    assert tanggal_valid("") is False


def test_provinsi_dan_kecamatan_valid():
    assert provinsi_valid("3171011503900001") is True
    assert provinsi_valid("4171011503900001") is False
    assert kecamatan_valid("3171011503900001") is True
    assert kecamatan_valid("3171991503900001") is False


# --- KF-10: NPWP orang pribadi (16 digit) dilaporkan sebagai nik ---


def test_npwp_pribadi_16_digit_dilaporkan_sebagai_nik():
    # NPWP orang pribadi = NIK (PMK 112/2022). Tidak ada rule NPWP terpisah.
    [t] = periksa_baris("a.txt", 1, "npwp: 3171011503900001", RULES)

    assert t.rule_id == "nik"
    assert t.tingkat == HIGH


# --- data wilayah ---


def test_jumlah_kode_wilayah_sesuai_dokumen():
    assert len(wilayah.provinsi()) == 38
    assert len(wilayah.kecamatan()) == 7285


def test_semua_kode_wilayah_berbentuk_digit_dengan_panjang_benar():
    assert all(len(k) == 2 and k.isdigit() for k in wilayah.provinsi())
    assert all(len(k) == 6 and k.isdigit() for k in wilayah.kecamatan())


def test_setiap_kecamatan_berada_di_provinsi_yang_terdaftar():
    assert all(k[:2] in wilayah.provinsi() for k in wilayah.kecamatan())


def test_data_dimuat_sekali_bukan_per_baris():
    wilayah.muat_kode.cache_clear()
    for _ in range(50):
        assess_nik("3171011503900001")
        assess_nik("3171991503900001")

    info = wilayah.muat_kode.cache_info()
    assert info.misses == 2  # provinsi.csv dan kecamatan.csv, masing-masing sekali
    assert info.hits >= 98


def test_muat_kode_menolak_csv_tanpa_kolom_kode(tmp_path):
    (tmp_path / "x.csv").write_text("id,nama\n11,Aceh\n", encoding="utf-8")

    with pytest.raises(ValueError, match="kode"):
        wilayah.muat_kode("x.csv", str(tmp_path))


def test_muat_kode_menolak_csv_kosong(tmp_path):
    (tmp_path / "x.csv").write_text("kode,nama\n", encoding="utf-8")

    with pytest.raises(ValueError):
        wilayah.muat_kode("x.csv", str(tmp_path))


def test_muat_kode_berkas_tidak_ada_melempar_oserror(tmp_path):
    with pytest.raises(OSError):
        wilayah.muat_kode("tidak-ada.csv", str(tmp_path))


def test_muat_kode_menolak_kode_bukan_digit_atau_panjang_salah(tmp_path):
    (tmp_path / "x.csv").write_text("kode,nama\n11,Aceh\n1A,Rusak\n123,Pendek\n", encoding="utf-8")

    with pytest.raises(ValueError, match="2 digit"):
        wilayah.muat_kode("x.csv", str(tmp_path), 2)


def test_data_bawaan_berada_di_dalam_paket_prism():
    # Menyalin folder src/prism/ saja sudah membawa datanya.
    from pathlib import Path

    import prism

    folder_paket = Path(prism.__file__).resolve().parent
    assert folder_paket in wilayah.FOLDER_BAWAAN.parents
    assert (wilayah.FOLDER_BAWAAN / "provinsi.csv").is_file()
    assert (wilayah.FOLDER_BAWAAN / "kecamatan.csv").is_file()
