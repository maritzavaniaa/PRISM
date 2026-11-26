"""Tes langkah 10: pemeriksa data uji sintetis dan label (KF-25).

Memeriksa berkas data yang sudah ada di repo, bukan menjalankan PRISM pada data uji. Data `uji` hanya
dijalankan sekali di langkah 13 (aturan beku, skema-evaluasi.md bagian 3).
"""

import csv
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

import pytest

from prism.rules import assess_nik

ROOT = Path(__file__).resolve().parent.parent
LABEL = ROOT / "data" / "labels" / "ground_truth.csv"
RINGKASAN = ROOT / "data" / "labels" / "ringkasan.json"
KOLOM_SPEC = ["berkas", "baris", "jenis", "label", "level_diharapkan", "asal_sampel", "kata_konteks", "jenis_berkas", "split"]
POLA_NIK = re.compile(r"(?<!\d)\d{4}[ .-]?\d{4}[ .-]?\d{4}[ .-]?\d{4}(?!\d)")
POLA_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


@pytest.fixture(scope="module")
def label():
    with open(LABEL, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def baris_berkas(rel):
    return (ROOT / rel).read_text(encoding="utf-8").split("\n")


def kandidat_nik(baris):
    return [re.sub(r"[ .-]", "", m.group()) for m in POLA_NIK.finditer(baris)]


# --- kolom dan isi dasar ---


def test_kolom_sesuai_skema_evaluasi():
    with open(LABEL, encoding="utf-8", newline="") as f:
        assert next(csv.reader(f)) == KOLOM_SPEC


def test_nilai_kolom_kategori_valid(label):
    assert {b["jenis"] for b in label} <= {"nik", "hp", "email"}
    assert {b["label"] for b in label} <= {"positif", "negatif"}
    assert {b["split"] for b in label} <= {"kalibrasi", "uji"}
    assert {b["jenis_berkas"] for b in label} <= {"csv", "yaml", "md", "kode", "log"}
    assert {b["level_diharapkan"] for b in label} <= {"", "high", "medium", "low"}


def test_tiap_label_menunjuk_berkas_dan_baris_yang_ada(label):
    for b in label:
        baris = baris_berkas(b["berkas"])
        n = int(b["baris"])
        assert 1 <= n <= len(baris) - 1, b
        teks = baris[n - 1]
        # Tiap baris berlabel memuat sesuatu yang mirip data: minimal 8 digit atau '@'.
        assert "@" in teks or sum(c.isdigit() for c in teks) >= 8, (b["berkas"], n)


def test_kunci_berkas_baris_jenis_unik(label):
    kunci = Counter((b["berkas"], b["baris"], b["jenis"]) for b in label)
    assert [k for k, n in kunci.items() if n > 1] == []


def test_jenis_berkas_cocok_dengan_ekstensi(label):
    ekstensi = {"csv": {".csv"}, "yaml": {".yaml", ".yml"}, "md": {".md"}, "kode": {".py", ".js"}, "log": {".log"}}
    for b in label:
        assert Path(b["berkas"]).suffix in ekstensi[b["jenis_berkas"]], b


# --- pembagian split (per berkas) ---


def test_tidak_ada_berkas_di_dua_split(label):
    split = {}
    for b in label:
        split.setdefault(b["berkas"], set()).add(b["split"])
    assert [k for k, s in split.items() if len(s) > 1] == []


def test_pembagian_sekitar_sepertiga_d1_kalibrasi_dan_d2_seluruhnya_uji(label):
    d1 = {b["berkas"]: b["split"] for b in label if "layanan_publik" in b["berkas"]}
    d2 = {b["berkas"]: b["split"] for b in label if "tulis_tangan" in b["berkas"]}
    assert len(d1) == 36 and sum(1 for s in d1.values() if s == "kalibrasi") == 12
    assert set(d2.values()) == {"uji"} and len(d2) == 5


def test_semua_berkas_data_punya_label(label):
    ada = {str(p.relative_to(ROOT)) for p in (ROOT / "data" / "synthetic").rglob("*") if p.is_file() and p.suffix != ".gitkeep" and "labels_" not in p.name and p.name != ".gitkeep"}
    assert ada == {b["berkas"] for b in label}


# --- jumlah positif dan negatif tercatat ---


def test_ringkasan_json_cocok_dengan_label(label):
    ringkasan = json.loads(RINGKASAN.read_text(encoding="utf-8"))
    hitung = Counter(b["label"] for b in label)
    assert ringkasan["semua"] == {"total": len(label), "positif": hitung["positif"], "negatif": hitung["negatif"]}
    for jenis in ("nik", "hp", "email"):
        sub = [b for b in label if b["jenis"] == jenis]
        assert ringkasan["per_jenis"][jenis]["total"] == len(sub)
    assert hitung["positif"] > 0 and hitung["negatif"] > 0


def test_jumlah_kasus_tulisan_tangan_minimal_30(label):
    assert sum(1 for b in label if "tulis_tangan" in b["berkas"]) >= 30


def test_ada_semua_asal_sampel_yang_diwajibkan(label):
    asal = {b["asal_sampel"] for b in label}
    assert {"nik", "npwp_op", "kk", "hp", "email", "acak16", "rekening", "id_transaksi", "timestamp", "uuid"} <= asal


def test_nik_positif_ada_tiap_tingkat_dan_negatif_low_ada(label):
    positif = Counter(b["level_diharapkan"] for b in label if b["jenis"] == "nik" and b["label"] == "positif")
    assert positif["high"] > 0 and positif["medium"] > 0
    assert any(b["label"] == "negatif" and b["level_diharapkan"] == "low" for b in label)


# --- assess_nik sama dengan level_diharapkan ---


def test_assess_nik_sama_dengan_level_diharapkan_untuk_semua_nik_positif(label):
    salah = []
    diperiksa = 0
    for b in label:
        if b["jenis"] != "nik" or b["label"] != "positif":
            continue
        kandidat = kandidat_nik(baris_berkas(b["berkas"])[int(b["baris"]) - 1])
        assert kandidat, (b["berkas"], b["baris"])
        for nilai in kandidat:
            diperiksa += 1
            if assess_nik(nilai) != b["level_diharapkan"]:
                salah.append((b["berkas"], b["baris"], b["level_diharapkan"], assess_nik(nilai)))
    assert diperiksa >= 100
    assert salah == []


def test_nik_negatif_berlevel_juga_sesuai(label):
    salah = []
    for b in label:
        if b["jenis"] == "nik" and b["label"] == "negatif" and b["level_diharapkan"]:
            for nilai in kandidat_nik(baris_berkas(b["berkas"])[int(b["baris"]) - 1]):
                if assess_nik(nilai) != b["level_diharapkan"]:
                    salah.append((b["berkas"], b["baris"], b["level_diharapkan"], assess_nik(nilai)))
    assert salah == []


# --- tidak ada data asli ---


def semua_teks_data():
    for p in sorted((ROOT / "data" / "synthetic").rglob("*")):
        if p.is_file() and p.name != ".gitkeep" and "labels_" not in p.name:
            yield p, p.read_text(encoding="utf-8")


def test_nik_positif_selalu_bernomor_urut_0000(label):
    # Asumsi ⚠️ (belum diverifikasi): nomor urut asli mulai dari 0001, jadi NIK berakhiran 0000 bukan milik orang nyata.
    for b in label:
        if b["jenis"] == "nik" and b["label"] == "positif":
            for nilai in kandidat_nik(baris_berkas(b["berkas"])[int(b["baris"]) - 1]):
                assert nilai.endswith("0000"), (b["berkas"], b["baris"])


def test_email_selalu_memuat_penanda_uji():
    ditemukan = 0
    for p, teks in semua_teks_data():
        for m in POLA_EMAIL.finditer(teks):
            ditemukan += 1
            assert ".uji" in m.group().split("@")[0] or m.group().split("@")[0].endswith("uji") or ".uji." in m.group(), (p.name, m.group())
    assert ditemukan > 100


def test_hp_positif_berawalan_pelanggan_555(label):
    # Penanda sintetis: setelah kode operator, nomor pelanggan dimulai 555.
    for b in label:
        if b["jenis"] == "hp" and b["label"] == "positif":
            digit = re.sub(r"\D", "", baris_berkas(b["berkas"])[int(b["baris"]) - 1].replace("2026-11", ""))
            assert "555" in digit, (b["berkas"], b["baris"])


# --- generator bisa diulang ---


def muat_generator():
    spec = importlib.util.spec_from_file_location("make_dataset", ROOT / "evaluation" / "scripts" / "make_dataset.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def test_generator_menghasilkan_label_d1_yang_sama_dengan_yang_ada_di_repo(tmp_path, monkeypatch, label):
    m = muat_generator()
    monkeypatch.setattr(m, "AKAR", tmp_path)
    monkeypatch.setattr(m, "FOLDER_DATA", tmp_path / "data" / "synthetic" / "layanan_publik")
    monkeypatch.setattr(m, "LABEL", tmp_path / "ground_truth.csv")
    monkeypatch.setattr(m, "RINGKASAN", tmp_path / "ringkasan.json")
    (tmp_path / "data" / "labels").mkdir(parents=True)

    assert m.main() == 0

    with open(tmp_path / "ground_truth.csv", encoding="utf-8", newline="") as f:
        baru = list(csv.DictReader(f))
    assert baru == label
    for p in (tmp_path / "data" / "synthetic" / "layanan_publik").iterdir():
        asli = ROOT / "data" / "synthetic" / "layanan_publik" / p.name
        assert p.read_text(encoding="utf-8") == asli.read_text(encoding="utf-8"), p.name
