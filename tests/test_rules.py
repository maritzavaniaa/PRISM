"""Tes langkah 5: rule NIK dengan regex (KF-07). Semua nilai sintetis."""

import pytest

from prism.rules import LOW, NIK, POLA_NIK, RULES, assess_nik

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


def test_assess_sementara_semua_low():
    # SEMENTARA (langkah 5). Tes ini diganti tes tabel KF-11 di langkah 6.
    assert assess_nik(NIK_SINTETIS) == LOW
    assert assess_nik("1234567890123456") == LOW
