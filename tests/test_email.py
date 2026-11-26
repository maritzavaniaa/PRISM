"""Tes langkah 7: rule email (KF-09, KF-13) dan daftar domain. Semua nilai sintetis."""

import pytest

from prism import cli, domain_email
from prism.engine import periksa_baris
from prism.report import mask
from prism.rules import EMAIL, HIGH, LOW, MEDIUM, POLA_EMAIL, RULES, assess_email

DOMAIN_AWAL = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.id", "ymail.com",
    "outlook.com", "hotmail.com", "live.com", "msn.com", "icloud.com",
    "me.com", "proton.me", "protonmail.com",
}  # fmt: skip


def kandidat(teks):
    return [m.group() for m in POLA_EMAIL.finditer(teks)]


# --- KF-09: bentuk email ---


@pytest.mark.parametrize(
    "nilai",
    [
        "budi@gmail.com",
        "budi.santoso@gmail.com",
        "budi_s+tag@yahoo.co.id",
        "b-udi%x@mail.pt-abc.co.id",
        "BUDI@GMAIL.COM",
        "a@b.id",
    ],
)
def test_bentuk_sah_terdeteksi(nilai):
    assert kandidat(nilai) == [nilai]
    assert kandidat(f"email: {nilai}, terima kasih.") == [nilai]
    assert kandidat(f"<{nilai}>") == [nilai]


def test_local_part_64_karakter_diterima_65_tidak():
    assert kandidat("a" * 64 + "@gmail.com") == ["a" * 64 + "@gmail.com"]
    assert kandidat("a" * 65 + "@gmail.com") == []  # tidak dipotong menjadi 64 terakhir


def test_tld_satu_huruf_tidak_terdeteksi():
    assert kandidat("budi@gmail.c") == []
    assert kandidat("budi@gmail") == []  # tanpa titik


@pytest.mark.parametrize(
    "teks",
    [
        ".budi@gmail.com",
        "budi.@gmail.com",
        "bu..di@gmail.com",
        "budi@.gmail.com",
        "budi@gmail..com",
        "budi@-gmail.com",
        "budi@gmail.c0m",
        "@gmail.com",
        "budi @gmail.com",
    ],
)
def test_bentuk_tidak_sah_tidak_terdeteksi(teks):
    assert kandidat(teks) == []


def test_domain_lebih_dari_255_karakter_tidak_terdeteksi():
    label = "a" * 60
    panjang = ".".join([label] * 5) + ".com"  # 5 label x 61 + 4 = > 255
    assert len(panjang) > 255
    assert kandidat(f"budi@{panjang}") == []
    pendek = ".".join([label] * 4) + ".com"  # 4 x 61 + 4 = 248
    assert len(pendek) <= 255
    assert kandidat(f"budi@{pendek}") == [f"budi@{pendek}"]


def test_titik_di_akhir_kalimat_tidak_ikut():
    assert kandidat("hubungi budi@gmail.com.") == ["budi@gmail.com"]


def test_dua_email_di_satu_baris():
    assert kandidat("a@gmail.com; b@yahoo.com") == ["a@gmail.com", "b@yahoo.com"]


def test_email_pada_tautan_mailto():
    assert kandidat("[tulis](mailto:budi@gmail.com)") == ["budi@gmail.com"]


def test_karakter_non_ascii_di_local_part_tidak_didukung():
    # Batasan yang diterima (IDN dan local-part Unicode tidak didukung): bagian ASCII di
    # sebelah kanan karakter itu tetap dilaporkan sebagai kandidat, tidak diabaikan.
    assert kandidat("b٣di@gmail.com") == ["di@gmail.com"]
    assert kandidat("budi@gémail.com") == []  # domain Unicode tidak terdeteksi


# --- KF-13: tingkat menurut domain ---


@pytest.mark.parametrize(
    "nilai, tingkat",
    [
        ("budi@gmail.com", MEDIUM),
        ("budi@yahoo.co.id", MEDIUM),
        ("budi@proton.me", MEDIUM),
        ("Budi@GMAIL.com", MEDIUM),  # huruf besar tidak membedakan
        ("budi@example.com", LOW),
        ("git@github.com", LOW),  # dari alamat SSH git@github.com:user/repo.git
        ("info@pt-abc.co.id", LOW),
        ("budi@mail.gmail.com", LOW),  # subdomain tidak sama dengan domain induk
        ("budi@gmail.com.id", LOW),
    ],
)
def test_tingkat_menurut_domain(nilai, tingkat):
    assert assess_email(nilai) == tingkat


def test_alamat_ssh_git_jadi_low():
    [t] = periksa_baris("a.txt", 1, "git clone git@github.com:user/repo.git", (EMAIL,))
    assert (t.rule_id, t.tingkat) == ("email", LOW)
    assert t.nilai == "git@github.com"


def test_email_tidak_pernah_high_tanpa_konteks():
    # high hanya bisa dicapai lewat kata konteks (langkah 8), bukan dari penilaian domain.
    for nilai in ("budi@gmail.com", "budi@example.com"):
        assert assess_email(nilai) != HIGH


def test_rule_email_terdaftar_dan_punya_kata_konteks():
    assert EMAIL in RULES and EMAIL.id == "email"
    assert set(EMAIL.context) == {"email", "surel", "mail"}


# --- daftar domain dibaca dari berkas data ---


def test_daftar_domain_awal_13_domain_di_dalam_paket():
    assert domain_email.domain_pribadi() == DOMAIN_AWAL
    assert domain_email.FILE_BAWAAN.is_file()
    assert domain_email.FILE_BAWAAN.parent.parent.name == "prism"  # src/prism/data/


def test_menambah_domain_di_berkas_mengubah_hasil_tanpa_mengubah_kode(tmp_path, monkeypatch):
    berkas = tmp_path / "domain.txt"
    berkas.write_text("# contoh\n\nGmail.com\n", encoding="utf-8")
    monkeypatch.setattr(domain_email, "FILE_BAWAAN", berkas)
    assert assess_email("budi@pt-abc.co.id") == LOW

    berkas2 = tmp_path / "domain2.txt"
    berkas2.write_text("gmail.com\npt-abc.co.id\n", encoding="utf-8")
    monkeypatch.setattr(domain_email, "FILE_BAWAAN", berkas2)
    assert assess_email("budi@pt-abc.co.id") == MEDIUM


def test_loader_mengabaikan_komentar_dan_baris_kosong(tmp_path):
    berkas = tmp_path / "d.txt"
    berkas.write_text("# komentar\n\n  Gmail.com  \nyahoo.com\n", encoding="utf-8")
    assert domain_email.muat_domain(str(berkas)) == {"gmail.com", "yahoo.com"}


def test_loader_menolak_berkas_hilang(tmp_path):
    with pytest.raises(OSError):
        domain_email.muat_domain(str(tmp_path / "tidak-ada.txt"))


@pytest.mark.parametrize("isi", ["", "# hanya komentar\n\n", "gmail\n", "bukan domain\n", "a@gmail.com\n"])
def test_loader_menolak_daftar_kosong_atau_rusak(tmp_path, isi):
    berkas = tmp_path / "d.txt"
    berkas.write_text(isi, encoding="utf-8")
    with pytest.raises(ValueError):
        domain_email.muat_domain(str(berkas))


def test_daftar_domain_hilang_exit_2_bukan_1(tmp_path, monkeypatch, capsys):
    berkas = tmp_path / "data.txt"
    berkas.write_text("budi@gmail.com\n", encoding="utf-8")
    monkeypatch.setattr(domain_email, "FILE_BAWAAN", tmp_path / "tidak-ada.txt")

    kode = cli.main(["scan", str(berkas)])

    keluar = capsys.readouterr()
    assert kode == 2
    assert "domain email pribadi" in keluar.err
    assert keluar.out == ""


def test_daftar_domain_kosong_exit_2(tmp_path, monkeypatch, capsys):
    berkas = tmp_path / "data.txt"
    berkas.write_text("budi@gmail.com\n", encoding="utf-8")
    kosong = tmp_path / "kosong.txt"
    kosong.write_text("# kosong\n", encoding="utf-8")
    monkeypatch.setattr(domain_email, "FILE_BAWAAN", kosong)

    assert cli.main(["scan", str(berkas)]) == 2
    assert "domain email pribadi" in capsys.readouterr().err


# --- mask email ---


def test_mask_email_bagian_sebelum_at_jadi_bintang():
    assert mask("budi@example.com") == "****@example.com"
    assert mask("budi@gmail.com") == "****@gmail.com"


def test_mask_email_mempertahankan_panjang_dan_tidak_membocorkan_local_part():
    nilai = "budi.santoso@gmail.com"
    hasil = mask(nilai)
    assert len(hasil) == len(nilai)
    assert "budi" not in hasil and "santoso" not in hasil
    assert hasil.endswith("@gmail.com")
