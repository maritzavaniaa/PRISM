"""Tes langkah 7: rule HP (KF-08, KF-12). Semua nilai sintetis."""

import pytest

from prism.rules import HIGH, HP, LOW, MEDIUM, POLA_HP, RULES, assess_hp

ENAM_BENTUK = [
    "081234567890",
    "81234567890",
    "0812-3456-7890",
    "812-3456-7890",
    "+6281234567890",
    "+62 812-3456-7890",
]


def kandidat(teks):
    return [m.group() for m in POLA_HP.finditer(teks)]


# --- KF-08: enam bentuk terdeteksi utuh ---


@pytest.mark.parametrize("nilai", ENAM_BENTUK)
def test_enam_bentuk_terdeteksi_utuh(nilai):
    assert kandidat(nilai) == [nilai]
    assert kandidat(f"hp: {nilai}, terima kasih") == [nilai]


@pytest.mark.parametrize(
    "nilai",
    ["62 812 3456 7890", "62-812-3456-7890", "0812.3456.7890", "+62-812-3456-7890", "0 812 3456 7890"],
)
def test_pemisah_spasi_titik_strip_diterima(nilai):
    assert kandidat(nilai) == [nilai]


def test_dua_hp_di_satu_baris():
    assert kandidat("0812-3456-7890 atau +6281234567891") == ["0812-3456-7890", "+6281234567891"]


# --- KF-12: tingkat bukti ---


@pytest.mark.parametrize(
    "nilai, tingkat",
    [
        ("+6281234567890", HIGH),
        ("+62 812-3456-7890", HIGH),
        ("0812-3456-7890", HIGH),
        ("081234567890", MEDIUM),
        ("6281234567890", MEDIUM),
        ("812-3456-7890", MEDIUM),
        ("81234567890", LOW),
    ],
)
def test_tingkat_tiap_bentuk(nilai, tingkat):
    assert assess_hp(nilai) == tingkat


@pytest.mark.parametrize(
    "nilai, tingkat",
    [
        ("62 812 3456 7890", HIGH),  # perluasan: 62 berpemisah disamakan dengan 0 berpemisah
        ("0812 3456 7890", HIGH),
        ("0812.3456.7890", HIGH),
        ("812.3456.7890", MEDIUM),
        ("812 3456 7890", MEDIUM),
        ("81-2345-6789", LOW),  # tanpa awalan, berpemisah, bukan pola 3-4-4
        ("8123-4567-890", LOW),
    ],
)
def test_tingkat_bentuk_di_luar_tabel(nilai, tingkat):
    assert kandidat(nilai) == [nilai]
    assert assess_hp(nilai) == tingkat


# --- pengecoh: bukan kandidat ---


@pytest.mark.parametrize(
    "teks",
    [
        "8123456",  # 7 digit
        "08123456789012",  # 14 digit berawalan 0: kelebihan digit
        "081234567890123",  # 15 digit
        "080123456789",  # digit kedua 0
        "+62 80123456789",
        "1081234567890",  # diapit digit di kiri
        "0812345678901234",  # diapit digit di kanan
        "12345678901234",  # 14 digit acak
    ],
)
def test_pengecoh_bukan_kandidat(teks):
    assert kandidat(teks) == []


def test_batas_panjang_9_sampai_12_digit_dari_angka_8():
    assert kandidat("81234567") == []  # 8 digit
    assert kandidat("812345678") == ["812345678"]  # 9 digit
    assert kandidat("812345678901") == ["812345678901"]  # 12 digit
    assert kandidat("8123456789012") == []  # 13 digit
    assert kandidat("62812345678901") == ["62812345678901"]  # 62 + 12 digit: panjang terbesar


def test_nik_16_digit_tidak_jadi_kandidat_hp():
    assert kandidat("3171011503900001") == []
    assert kandidat("0812345678901234") == []


def test_pola_hp_hanya_digit_ascii():
    arab = "".join(chr(0x0660 + int(d)) for d in "081234567890")
    assert kandidat(arab) == []


def test_batas_kanan_hanya_menolak_digit_yang_menempel():
    # Diterima sebagai batasan: kelompok digit berikutnya yang dipisah strip tidak menghalangi.
    assert kandidat("0812-3456-7890-1234") == ["0812-3456-7890"]


def test_rule_hp_terdaftar_dan_punya_kata_konteks():
    assert HP in RULES and HP.id == "hp"
    assert set(HP.context) == {"hp", "telp", "telepon", "wa", "whatsapp", "kontak"}


def test_nik_berpemisah_bisa_menghasilkan_kandidat_hp_palsu():
    # Batasan yang diterima: NIK berpemisah tidak terdeteksi sebagai NIK (mvp-t5 5.2), tetapi
    # kelompok di dalamnya yang berawalan 08 bisa cocok dengan pola HP berpemisah.
    assert kandidat("3171-0815-0390-0001") == ["0815-0390-0001"]
    assert kandidat("3171-0115-0390-0001") == []
