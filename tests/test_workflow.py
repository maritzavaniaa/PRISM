"""Tes langkah 11: workflow CI (KF-22, KF-23, KF-24, KN-08).

Tes ini hanya memeriksa isi `privacy-scan.yml`. Hijau/merah di GitHub sungguhan dibuktikan manual
(lihat matriks-kf-tes.md), bukan oleh pytest.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "privacy-scan.yml"


def teks():
    return WORKFLOW.read_text(encoding="utf-8")


def test_workflow_dipicu_push_dan_pull_request():
    t = teks()
    assert "push" in t and "pull_request" in t


def test_workflow_memasang_python_versi_lokal():
    t = teks()
    assert "actions/setup-python" in t
    assert '"3.13"' in t or "'3.13'" in t or "3.13" in t  # KN-08: sama dengan lokal


def test_workflow_menjalankan_prism_scan():
    t = teks()
    assert "actions/checkout" in t
    assert "python -m prism scan" in t


def test_workflow_mengecualikan_folder_data_uji():
    t = teks()
    for folder in ("data/synthetic", "tests", "evaluation/results"):
        assert f"--exclude {folder}" in t


def test_workflow_tidak_menelan_exit_code():
    # Job merah bila exit code bukan 0 (KF-23): langkah pindai tidak boleh menelan kegagalannya.
    t = teks()
    assert "continue-on-error" not in t
    assert "|| true" not in t
