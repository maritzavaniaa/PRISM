"""Tes langkah 5: rule NIK dengan regex (KF-07). Semua nilai sintetis."""

import pytest

from prism.rules import NIK, POLA_NIK, RULES

NIK_SINTETIS = "3171011503900001"


def kandidat(teks):
    return [m.group() for m in POLA_NIK.finditer(teks)]


def test_16_digit_satu_kandidat():
    assert kandidat(NIK_SINTETIS) == [NIK_SINTETIS]


def test_16_digit_di_tengah_kalimat():
    assert kandidat(f"nik: {NIK_SINTETIS}, terdaftar") == [NIK_SINTETIS]


def test_15_digit_tidak_terdeteksi():
    assert kandidat("317101150390000") == []


def test_17_digit_tidak_terdeteksi_karena_diapit_digit():
    assert kandidat("31710115039000012") == []
    assert kandidat("13171011503900001") == []


def test_dua_nik_di_satu_baris_terdeteksi_keduanya():
    assert kandidat(f"{NIK_SINTETIS} dan 3171015503900002") == [
        NIK_SINTETIS,
        "3171015503900002",
    ]


@pytest.mark.parametrize(
    "teks",
    [
        "3171 0115 0390 0001",
        "3171-0115-0390-0001",
        "3171.0115.0390.0001",
    ],
)
def test_nik_dengan_pemisah_tidak_terdeteksi(teks):
    # Batasan yang diterima (mvp-t5 5.2): NIK hanya dikenali tanpa pemisah.
    # Tes ini mendokumentasikan batasan itu. Ubah bila keputusan berubah.
    assert kandidat(teks) == []


@pytest.mark.parametrize(
    "teks",
    [
        f"abc{NIK_SINTETIS}",
        f"{NIK_SINTETIS}abc",
        f"id_{NIK_SINTETIS}.txt",
    ],
)
def test_huruf_di_sekitar_tidak_menghalangi(teks):
    # Keputusan langkah 5: batas hanya menolak DIGIT di sekitar, bukan huruf.
    assert kandidat(teks) == [NIK_SINTETIS]


def test_rule_nik_terdaftar_dan_punya_kata_konteks():
    assert RULES[0] is NIK
    assert NIK.id == "nik"
    assert "nik" in NIK.context and "ktp" in NIK.context


def test_pola_nik_hanya_digit_ascii():
    # Digit Arab-Indic (Unicode) bukan NIK. Tanpa re.ASCII, \d akan mencocokkannya.
    assert kandidat("\u0663\u0661\u0667\u0661\u0660\u0661\u0661\u0665\u0660\u0663\u0669\u0660\u0660\u0660\u0660\u0661") == []
