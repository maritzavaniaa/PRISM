"""Tes langkah 5: mesin rule (lokasi kandidat). Semua nilai sintetis."""

from prism.engine import Temuan, periksa_baris
from prism.rules import HIGH, RULES

NIK_SINTETIS = "3171011503900001"


def test_baris_tanpa_kandidat_mengembalikan_daftar_kosong():
    assert periksa_baris("a.txt", 1, "tidak ada angka panjang", RULES) == []


def test_lokasi_baris_dan_kolom_benar_dimulai_dari_1():
    # 9 karakter sebelum NIK, jadi NIK mulai di kolom 10.
    teks = "id nik = " + NIK_SINTETIS

    [t] = periksa_baris("a.txt", 3, teks, RULES)

    assert (t.berkas, t.baris, t.kolom) == ("a.txt", 3, 10)
    assert t.rule_id == "nik"
    assert t.tingkat == HIGH
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
    t = Temuan("a.txt", 1, 1, "nik", HIGH, NIK_SINTETIS)

    try:
        t.kolom = 2
    except AttributeError:
        return
    raise AssertionError("Temuan seharusnya frozen")


# --- langkah 8: konteks (KF-14), ambang (KF-15), dedup (KF-16) ---

import pytest  # noqa: E402

from prism.engine import ada_konteks, hapus_duplikat, kata_dalam, naikkan, terapkan_ambang  # noqa: E402
from prism.rules import EMAIL, HP, LOW, MEDIUM, NIK  # noqa: E402

NIK_LOW = "1234567890123456"  # tanggal tidak sah
NIK_MEDIUM = "3171991503900001"  # kecamatan 99 tidak terdaftar


def tingkat(teks, rules=RULES):
    return [(t.rule_id, t.tingkat) for t in periksa_baris("a.txt", 1, teks, rules)]


def test_naikkan_satu_tingkat_high_tetap():
    assert (naikkan(LOW), naikkan(MEDIUM), naikkan(HIGH)) == (MEDIUM, HIGH, HIGH)


@pytest.mark.parametrize(
    "teks, diharapkan",
    [
        (f"nik: {NIK_SINTETIS}", HIGH),  # sudah high, tetap
        (f"nik: {NIK_LOW}", MEDIUM),  # low naik satu
        (f"ref: {NIK_LOW}", LOW),  # tanpa kata petunjuk
        (f"NIK: {NIK_LOW}", MEDIUM),  # huruf besar tetap menaikkan
        (f"Nik: {NIK_LOW}", MEDIUM),
        (f"{NIK_LOW} (KTP)", MEDIUM),  # kata di kanan kandidat
        (f"nik: {NIK_MEDIUM}", HIGH),  # medium naik jadi high
    ],
)
def test_konteks_nik(teks, diharapkan):
    assert tingkat(teks) == [("nik", diharapkan)]


def test_batas_40_karakter_di_kiri_diuji_di_kedua_sisi():
    pas = "nik" + " " * 37  # kata persis memenuhi 40 karakter di kiri kandidat
    terlalu_jauh = "nik" + " " * 38  # kata terpotong: yang tersisa di jendela hanya "ik"
    assert tingkat(pas + NIK_LOW) == [("nik", MEDIUM)]
    assert tingkat(terlalu_jauh + NIK_LOW) == [("nik", LOW)]


def test_batas_40_karakter_di_kanan_diuji_di_kedua_sisi():
    pas = " " * 37 + "nik"
    terlalu_jauh = " " * 38 + "nik"
    assert tingkat(NIK_LOW + pas) == [("nik", MEDIUM)]
    assert tingkat(NIK_LOW + terlalu_jauh) == [("nik", LOW)]


def test_konteks_tidak_menjangkau_baris_lain():
    # periksa_baris hanya melihat satu baris: kata `nik` di baris lain tidak terbaca.
    assert tingkat(NIK_LOW) == [("nik", LOW)]


@pytest.mark.parametrize(
    "teks, ada",
    [
        ("no_hp: ", True),  # garis bawah memisahkan kata
        ("phone-number ", True),
        ("phoneNumber ", True),  # camelCase dipecah
        ("noHP ", True),  # camelCase: "no" + "HP"
        ("nohp ", False),  # tanpa pemisah sama sekali: bukan kata utuh (batasan)
        ("e-mail ", True),
        ("hp2 ", True),  # angka memisahkan kata
        ("water ", False),  # `wa` bukan kata utuh dalam "water"
        ("whatever ", False),
        ("telepon ", True),
        ("telephone ", False),
    ],
)
def test_pencocokan_konteks_per_kata_utuh(teks, ada):
    kata = ("hp", "wa", "telepon", "phone", "mail")
    assert ada_konteks(teks + "X", len(teks), len(teks) + 1, kata) is ada


def test_kata_dalam_tidak_membedakan_huruf_besar_kecil():
    assert kata_dalam("NIK Pemohon") == {"nik", "pemohon"}


def test_isi_kandidat_sendiri_tidak_dibaca_sebagai_konteks():
    # Local-part email `hp` bukan kata konteks bagi kandidat itu sendiri.
    teks = "hp@gmail.com"
    [t] = periksa_baris("a.txt", 1, teks, (EMAIL,))
    assert t.tingkat == MEDIUM  # tetap medium, tidak naik karena kata "hp" (bukan konteks email pula)


# --- konteks HP dan email ---


@pytest.mark.parametrize(
    "teks, diharapkan",
    [
        ("081234567890", MEDIUM),
        ("hp: 081234567890", HIGH),
        ("kontak: 081234567890", HIGH),
        ("81234567890", LOW),
        ("hp: 81234567890", MEDIUM),
        ("phone: 81234567890", MEDIUM),  # kata konteks berbahasa Inggris
        ("wa 81234567890", MEDIUM),
        ("water 81234567890", LOW),
    ],
)
def test_konteks_hp(teks, diharapkan):
    assert tingkat(teks, (HP,)) == [("hp", diharapkan)]


@pytest.mark.parametrize(
    "teks, diharapkan",
    [
        ("budi@gmail.com", MEDIUM),
        ("email: budi@gmail.com", HIGH),
        ("Email budi@gmail.com", HIGH),
        # Domain di luar daftar tetap low walau ada kata konteks (keputusan langkah 8).
        ("info@pt-abc.co.id", LOW),
        ("email: info@pt-abc.co.id", LOW),
        ("git@github.com:user/repo.git", LOW),
    ],
)
def test_konteks_email(teks, diharapkan):
    assert tingkat(teks, (EMAIL,)) == [("email", diharapkan)]


# --- ambang (KF-15) ---


def kandidat_abc():
    teks = f"{NIK_SINTETIS} {NIK_MEDIUM} {NIK_LOW}"
    return periksa_baris("a.txt", 1, teks, RULES)  # A high, B medium, C low


def test_ambang_medium_melaporkan_a_dan_b_dan_menghitung_c():
    dilaporkan, low_dibuang = terapkan_ambang(kandidat_abc(), MEDIUM)
    assert [t.tingkat for t in dilaporkan] == [HIGH, MEDIUM]
    assert low_dibuang == 1


def test_ambang_low_melaporkan_semuanya():
    dilaporkan, low_dibuang = terapkan_ambang(kandidat_abc(), LOW)
    assert [t.tingkat for t in dilaporkan] == [HIGH, MEDIUM, LOW]
    assert low_dibuang == 0


def test_ambang_high_hanya_a_dan_hanya_low_yang_dihitung():
    dilaporkan, low_dibuang = terapkan_ambang(kandidat_abc(), HIGH)
    assert [t.tingkat for t in dilaporkan] == [HIGH]
    assert low_dibuang == 1  # medium yang dibuang tidak dihitung


def test_ambang_tidak_mengubah_tingkat():
    semua = kandidat_abc()
    dilaporkan, _ = terapkan_ambang(semua, MEDIUM)
    assert dilaporkan == semua[:2]


# --- dedup (KF-16) ---


def dedup(teks):
    hasil = periksa_baris("a.txt", 1, teks, RULES)
    return [(t.rule_id, t.tingkat, t.nilai) for t in hapus_duplikat(hasil, RULES)]


def test_dua_temuan_tidak_beririsan_tetap_dua():
    hasil = dedup("hp: 08123456789, email: budi@gmail.com")
    assert [(r, n) for r, _, n in hasil] == [("hp", "08123456789"), ("email", "budi@gmail.com")]


def test_irisan_tingkat_sama_yang_terpanjang_menang():
    # HP medium (11 karakter) dan email medium (21 karakter) beririsan: email menang.
    hasil = dedup("08123456789@gmail.com")
    assert hasil == [("email", MEDIUM, "08123456789@gmail.com")]


def test_irisan_dengan_kata_kontak_hp_naik_ke_high_dan_menang():
    # Contoh di mvp-t5 mengira HP `medium`, padahal `kontak` adalah kata konteks HP: HP jadi high.
    hasil = dedup("kontak: 08123456789@gmail.com")
    assert hasil == [("hp", HIGH, "08123456789")]


def test_irisan_hp_high_menang_atas_email_walau_lebih_pendek():
    # ⚠️ Tingkat didahulukan daripada panjang. Apakah ini wajar dinilai di langkah 13.
    hasil = dedup("kontak: +6281234567890@gmail.com")
    assert hasil == [("hp", HIGH, "+6281234567890")]


def test_irisan_tingkat_dan_panjang_sama_urutan_rule_menentukan():
    a = Temuan("a.txt", 1, 1, "email", MEDIUM, "x" * 5)
    b = Temuan("a.txt", 1, 1, "nik", MEDIUM, "y" * 5)
    assert [t.rule_id for t in hapus_duplikat([a, b], RULES)] == ["nik"]
    assert [t.rule_id for t in hapus_duplikat([b, a], RULES)] == ["nik"]


def test_irisan_satu_karakter_sudah_dihitung_beririsan():
    a = Temuan("a.txt", 1, 1, "nik", HIGH, "a" * 5)  # kolom 1-5
    b = Temuan("a.txt", 1, 5, "hp", HIGH, "b" * 3)  # kolom 5-7: berbagi kolom 5
    c = Temuan("a.txt", 1, 6, "hp", HIGH, "c" * 3)  # kolom 6-8: tidak beririsan dengan a
    assert [t.nilai[0] for t in hapus_duplikat([a, b, c], RULES)] == ["a", "c"]


def test_dedup_hanya_memproses_yang_lolos_ambang():
    # NIK low dibuang oleh ambang, jadi tidak bisa "menang" lalu menghapus HP yang lolos.
    teks = "08123456789"
    kandidat = periksa_baris("a.txt", 1, teks, RULES)
    lolos, _ = terapkan_ambang(kandidat, MEDIUM)
    assert [t.rule_id for t in hapus_duplikat(lolos, RULES)] == ["hp"]
