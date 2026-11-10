# PRISM

Tool *automated privacy check* di pipeline CI/CD (GitHub Actions) untuk deteksi dini kebocoran data pribadi (PII) Indonesia dan kredensial pada repositori dan log. Pipeline gagal otomatis saat ada temuan.

Proyek skripsi. Dosen pembimbing: Warsun Najib, Dr., S.T., M.Sc.

## Struktur

| Folder | Isi |
|---|---|
| `docs/planning/` | Rencana harian, keputusan cakupan, catatan bimbingan |
| `docs/research/` | Ringkasan riset, perbandingan tool, format PII Indonesia, UU PDP, related work |
| `docs/analysis/` | DFD, analisis LINDDUN, requirements (PR/FR/NFR) |
| `docs/report/` | Draf laporan/artikel per bab (IMRaD) |
| `docs/guidance/` | Arahan dan catatan dari dosen |
| `src/prism/` | Kode scanner (CLI) |
| `tests/` | Unit test scanner |
| `sample-app/` | Aplikasi contoh yang menghasilkan log berisi PII sintetis (skenario S3) |
| `data/synthetic/` | Data uji sintetis (tanpa PII asli) |
| `data/labels/` | Ground truth untuk evaluasi |
| `evaluation/scripts/` | Skrip hitung precision, recall, FPR, dan waktu |
| `evaluation/results/` | Hasil evaluasi |
| `.github/workflows/` | Workflow CI/CD yang menjalankan scanner |

## Status

Lihat [docs/research/riset-privacy-scanner-cicd.md](docs/research/riset-privacy-scanner-cicd.md) bagian 2 dan [docs/planning/rencana-harian-11-nov.md](docs/planning/rencana-harian-11-nov.md).
