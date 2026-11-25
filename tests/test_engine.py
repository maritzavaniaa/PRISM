"""Tes langkah 5: mesin rule (lokasi kandidat). Semua nilai sintetis."""

from prism.engine import Temuan, periksa_baris
from prism.rules import LOW, RULES

NIK_SINTETIS = "3171011503900001"


def test_baris_tanpa_kandidat_mengembalikan_daftar_kosong():
    assert periksa_baris("a.txt", 1, "tidak ada angka panjang", RULES) == []


def test_lokasi_baris_dan_kolom_benar_dimulai_dari_1():
    # 9 karakter sebelum NIK, jadi NIK mulai di kolom 10.
    teks = "id nik = " + NIK_SINTETIS

    [t] = periksa_baris("a.txt", 3, teks, RULES)

    assert (t.berkas, t.baris, t.kolom) == ("a.txt", 3, 10)
    assert t.rule_id == "nik"
    assert t.tingkat == LOW
    assert t.nilai == NIK_SINTETIS


def test_kandidat_di_awal_baris_kolom_1():
    [t] = periksa_baris("a.txt", 1, NIK_SINTETIS, RULES)

    assert t.kolom == 1


def test_dua_kandidat_terurut_menurut_kolom():
    teks = f"{NIK_SINTETIS} lalu 3171015503900002"

    hasil = periksa_baris("a.txt", 1, teks, RULES)

    # 16 digit + " lalu " (6 karakter) = 22 karakter sebelum NIK kedua, jadi kolom 23.
    assert [t.kolom for t in hasil] == [1, 23]


def test_repr_temuan_tidak_memuat_nilai_utuh():
    [t] = periksa_baris("a.txt", 1, NIK_SINTETIS, RULES)

    assert NIK_SINTETIS not in repr(t)


def test_temuan_tidak_bisa_diubah():
    t = Temuan("a.txt", 1, 1, "nik", LOW, NIK_SINTETIS)

    try:
        t.kolom = 2
    except AttributeError:
        return
    raise AssertionError("Temuan seharusnya frozen")
