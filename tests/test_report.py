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
