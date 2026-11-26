"""Tes langkah 5: mask (KF-20). Semua nilai sintetis."""

import pytest

from prism.report import mask


def test_mask_nik_empat_terakhir_terlihat():
    assert mask("3171011503900001") == "************0001"


def test_mask_hp():
    assert mask("081234567890") == "********7890"


def test_mask_mempertahankan_panjang():
    for nilai in ("3171011503900001", "081234567890", "12345"):
        assert len(mask(nilai)) == len(nilai)


@pytest.mark.parametrize("nilai", ["", "1", "1234"])
def test_nilai_empat_karakter_atau_kurang_disamarkan_seluruhnya(nilai):
    assert mask(nilai) == "*" * len(nilai)


def test_nilai_lima_karakter_menampilkan_empat_terakhir():
    assert mask("12345") == "*2345"


def test_mask_tidak_memuat_bagian_depan_nilai():
    assert "317101" not in mask("3171011503900001")


# --- langkah 9: baris teks, ringkasan, JSON (KF-17 sampai KF-19) ---

import re  # noqa: E402

from prism.engine import Temuan  # noqa: E402
from prism.report import (  # noqa: E402
    baris_ringkasan,
    baris_temuan,
    buat_json,
    hitung_per_rule,
    urutkan_temuan,
)
from prism.rules import RULES  # noqa: E402

POLA_BARIS = re.compile(r"^.+:\d+:\d+  (nik|hp|email)  (high|medium|low)  [*0-9A-Za-z@.\-]+$")


def temuan(berkas, baris, kolom, rule_id="nik", tingkat="high", nilai="3171011503900001"):
    return Temuan(berkas, baris, kolom, rule_id, tingkat, nilai)


def test_mask_email_tanpa_at_memakai_aturan_nik_hp():
    assert mask("budi@example.com") == "****@example.com"
    assert mask("tanpaat123456") == "*********3456"


def test_baris_temuan_cocok_pola_dan_nilai_di_mask():
    baris = baris_temuan(temuan("app/data.csv", 12, 34))
    assert baris == "app/data.csv:12:34  nik  high  ************0001"
    assert POLA_BARIS.match(baris)
    assert "3171011503900001" not in baris


def test_baris_temuan_email_dan_hp():
    assert baris_temuan(temuan("a.md", 5, 20, "hp", "medium", "081234567890")) == "a.md:5:20  hp  medium  ********7890"
    assert baris_temuan(temuan("c.yaml", 8, 14, "email", "medium", "budi@gmail.com")) == "c.yaml:8:14  email  medium  ****@gmail.com"


def test_urutan_temuan_berkas_baris_kolom():
    acak = [temuan("b.txt", 1, 1), temuan("a.txt", 2, 5), temuan("a.txt", 2, 1), temuan("a.txt", 1, 9)]
    hasil = [(t.berkas, t.baris, t.kolom) for t in urutkan_temuan(acak)]
    assert hasil == [("a.txt", 1, 9), ("a.txt", 2, 1), ("a.txt", 2, 5), ("b.txt", 1, 1)]


def test_hitung_per_rule_semua_jenis_tercatat():
    t = [temuan("a", 1, 1), temuan("a", 2, 1, "email", "medium", "x@gmail.com")]
    assert hitung_per_rule(t, RULES) == {"nik": 1, "hp": 0, "email": 1}


@pytest.mark.parametrize(
    "per_rule, low, lengkap, nama_json, diharapkan",
    [
        ({"nik": 1, "hp": 1, "email": 1}, 2, True, "prism-report.json",
         "3 temuan (nik 1, hp 1, email 1). Tidak dilaporkan: 2 kandidat low. Laporan JSON: prism-report.json"),
        ({"nik": 0, "hp": 0, "email": 0}, 0, True, None, "0 temuan. Tidak dilaporkan: 0 kandidat low."),
        ({"nik": 2, "hp": 0, "email": 0}, 1, True, None, "2 temuan (nik 2). Tidak dilaporkan: 1 kandidat low."),
        ({"nik": 0, "hp": 0, "email": 0}, 0, False, None, "0 temuan. Tidak dilaporkan: 0 kandidat low. Pindai tidak lengkap."),
    ],
)  # fmt: skip
def test_baris_ringkasan(per_rule, low, lengkap, nama_json, diharapkan):
    assert baris_ringkasan(per_rule, low, not lengkap, nama_json) == diharapkan


def ringkasan_contoh():
    return {"files": 41, "skipped": 7, "lines": 1284, "lines_prefiltered": 90, "suppressed_low": 2, "errors": 0, "min_level": "medium"}


def test_buat_json_struktur_dan_urutan_kunci():
    laporan = buat_json([temuan("app/seed.csv", 12, 34)], RULES, ringkasan_contoh())

    assert list(laporan) == ["schema_version", "findings", "scan"]
    assert laporan["schema_version"] == 1
    assert laporan["findings"] == [
        {
            "rule_id": "nik",
            "level": "high",
            "location": {"file": "app/seed.csv", "line": 12, "column": 34, "target": "content"},
            "match": {"value": "************0001"},
        }
    ]
    assert laporan["scan"] == {
        "mode": "repo", "files": 41, "skipped": 7, "lines": 1284, "lines_prefiltered": 90,
        "findings": 1, "findings_by_rule": {"nik": 1, "hp": 0, "email": 0},
        "suppressed_low": 2, "errors": 0, "min_level": "medium",
    }  # fmt: skip


def test_buat_json_memakai_level_bukan_score():
    laporan = buat_json([temuan("a", 1, 1)], RULES, ringkasan_contoh())
    assert "level" in laporan["findings"][0]
    assert "score" not in laporan["findings"][0]


def test_buat_json_nilai_utuh_tidak_ada():
    import json as _json

    t = [temuan("a", 1, 1), temuan("a", 2, 1, "email", "medium", "budi.santoso@gmail.com")]
    teks = _json.dumps(buat_json(t, RULES, ringkasan_contoh()))
    assert "3171011503900001" not in teks
    assert "budi.santoso" not in teks
    assert "************@gmail.com" in teks
