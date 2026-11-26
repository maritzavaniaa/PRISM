"""Tes langkah 8: judul kolom CSV sebagai konteks. Semua nilai sintetis."""

from prism.csv_judul import JudulCsv
from prism.engine import periksa_baris
from prism.rules import LOW, MEDIUM, RULES

NIK_LOW = "1234567890123456"


def judul(header, baris, nilai):
    j = JudulCsv()
    j.catat_header("a.csv", header)
    return j.judul_di("a.csv", baris, baris.index(nilai))


def test_judul_kolom_koma():
    assert judul("id,nama,nik,kota", f"1,Budi,{NIK_LOW},Jakarta", NIK_LOW) == "nik"
    assert judul("id,nama,nik,kota", f"1,Budi,{NIK_LOW},Jakarta", "Jakarta") == "kota"
    assert judul("id,nama,nik,kota", f"1,Budi,{NIK_LOW},Jakarta", "1") == "id"


def test_pembatas_titik_koma_dan_tab_dikenali_otomatis():
    assert judul("id;nama;nik", f"1;Budi;{NIK_LOW}", NIK_LOW) == "nik"
    assert judul("id\tnama\tnik", f"1\tBudi\t{NIK_LOW}", NIK_LOW) == "nik"


def test_pembatas_di_dalam_kutip_tidak_menggeser_kolom():
    assert judul("id,nama,nik", f'1,"Budi, S.",{NIK_LOW}', NIK_LOW) == "nik"
    assert judul('id,"nama, lengkap",nik', f'1,Budi,{NIK_LOW}', NIK_LOW) == "nik"


def test_kolom_melebihi_jumlah_header_tidak_punya_judul():
    assert judul("id,nama", f"1,Budi,{NIK_LOW}", NIK_LOW) is None


def test_berkas_tanpa_header_tercatat_tidak_punya_judul():
    assert JudulCsv().judul_di("lain.csv", "1,2,3", 0) is None


def test_header_dengan_bom_tidak_merusak_judul_pertama():
    j = JudulCsv()
    j.catat_header("a.csv", "﻿nik,nama")
    assert j.judul_di("a.csv", f"{NIK_LOW},Budi", 0) == "﻿nik"


def test_judul_dipakai_engine_sebagai_konteks():
    j = JudulCsv()
    j.catat_header("a.csv", "id,nama,nik")
    teks = f"1,Budi,{NIK_LOW}"

    [dengan] = periksa_baris("a.csv", 2, teks, RULES, judul_kolom=lambda p: j.judul_di("a.csv", teks, p))
    [tanpa] = periksa_baris("a.csv", 2, teks, RULES)

    assert dengan.tingkat == MEDIUM
    assert tanpa.tingkat == LOW


def test_judul_dengan_bom_tetap_menaikkan():
    j = JudulCsv()
    j.catat_header("a.csv", "﻿nik,nama")
    teks = f"{NIK_LOW},Budi"
    [t] = periksa_baris("a.csv", 2, teks, RULES, judul_kolom=lambda p: j.judul_di("a.csv", teks, p))
    assert t.tingkat == MEDIUM
