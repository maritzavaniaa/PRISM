"""Antarmuka baris perintah PRISM (langkah 9: keluaran teks, JSON, exit code).

Exit code (KF-21): 2 bila ada error pindai (didahulukan), jika tidak 1 bila ada
temuan yang dilaporkan, jika tidak 0.
"""

import argparse
import os
import sys
from dataclasses import replace

from prism import domain_email, wilayah
from prism.csv_judul import JudulCsv
from prism.engine import hapus_duplikat, periksa_baris, rentang_sensitif, terapkan_ambang
from prism.report import (
    baris_ringkasan,
    baris_temuan,
    buat_json,
    hitung_per_rule,
    samarkan_rentang,
    tulis_json,
    urutkan_temuan,
)
from prism.rules import HIGH, LOW, MEDIUM, RULES
from prism.scanner import ScanResult, scan

EXIT_OK = 0
EXIT_TEMUAN = 1
EXIT_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prism",
        description="PRISM: pemindai PII Indonesia di repositori.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pindai = sub.add_parser("scan", help="pindai satu berkas atau satu folder")
    pindai.add_argument("path", help="berkas atau folder yang dipindai")
    pindai.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="FOLDER",
        help="folder yang dilewati (boleh diulang)",
    )
    pindai.add_argument(
        "--min-level",
        choices=[LOW, MEDIUM, HIGH],
        default=MEDIUM,
        help="tingkat terendah yang dilaporkan (bawaan: medium)",
    )
    pindai.add_argument("--json", action="store_true", help="tulis laporan JSON (wajib bersama --output)")
    pindai.add_argument("--output", metavar="BERKAS", help="berkas tujuan laporan JSON (wajib bersama --json)")
    return parser


def _tulis_laporan_json(output, temuan, ringkasan) -> bool:
    """Tulis JSON bila diminta. Kembalikan False hanya bila penulisan gagal (sudah dilaporkan ke stderr)."""
    if output is None:
        return True
    try:
        tulis_json(output, buat_json(temuan, RULES, ringkasan))
    except OSError as e:
        print(f"Error: laporan JSON tidak bisa ditulis: {e.strerror}", file=sys.stderr)
        return False
    return True


def _ringkasan(hasil: ScanResult, low_dibuang: int, min_level: str) -> dict:
    return {
        "files": hasil.berkas_diperiksa,
        "skipped": hasil.berkas_dilewati,
        "lines": hasil.baris_dibaca,
        "lines_prefiltered": hasil.baris_lolos_prefilter,
        "suppressed_low": low_dibuang,
        "errors": hasil.berkas_error,
        "min_level": min_level,
    }


def _penyamar_path(min_level: str):
    """Fungsi yang menyamarkan PII di dalam path atau pesan sebelum dicetak (KF-20, perluasan 26 Nov. 2026).

    Apa pun yang bisa dilaporkan sebagai temuan tidak boleh tampil utuh di path. Batasnya: ambang
    pengguna, tetapi tidak pernah lebih tinggi dari medium (di ambang high, medium tetap disamarkan).
    Memanggil rule, jadi data referensi harus sudah termuat.
    """
    batas = LOW if min_level == LOW else MEDIUM
    cache = {}

    def samarkan(teks: str) -> str:
        if teks not in cache:
            cache[teks] = samarkan_rentang(teks, rentang_sensitif(teks, RULES, batas))
        return cache[teks]

    return samarkan


def _scan(path: str, exclude, min_level: str = MEDIUM, output: str | None = None) -> int:
    # Data referensi dimuat di awal, sebelum apa pun dicetak. Bila hilang atau rusak, keluar dengan 2:
    # crash Python berkode 1 akan terbaca sebagai "ada temuan". Path baru boleh dicetak sesudah
    # data termuat, karena penyamaran path memakai rule.
    galat = None
    for nama, muat in (
        ("kode wilayah", wilayah.pastikan_termuat),
        ("domain email pribadi", domain_email.pastikan_termuat),
    ):
        try:
            muat()
        except (OSError, ValueError) as e:
            galat = f"data {nama} tidak bisa dimuat: {e}"
            break
    if galat is None and not os.path.exists(path):
        galat = "path tidak ditemukan: " + _penyamar_path(min_level)(path)
    if galat is not None:
        print(f"Error: {galat}", file=sys.stderr)
        _tulis_laporan_json(output, [], _ringkasan(ScanResult(berkas_error=1), 0, min_level))
        return EXIT_ERROR

    samarkan = _penyamar_path(min_level)
    temuan = []
    low_dibuang = 0
    judul_csv = JudulCsv()

    def proses(berkas, nomor, teks, judul_kolom):
        # Urutan KF-14 sampai KF-16: bukti dan konteks, lalu ambang, lalu dedup.
        nonlocal low_dibuang
        kandidat = periksa_baris(berkas, nomor, teks, RULES, judul_kolom=judul_kolom)
        lolos, dibuang = terapkan_ambang(kandidat, min_level)
        low_dibuang += dibuang
        temuan.extend(hapus_duplikat(lolos, RULES))

    def proses_baris(berkas, nomor, teks):
        proses(berkas, nomor, teks, lambda posisi: judul_csv.judul_di(berkas, teks, posisi))

    def proses_nama(berkas, nama):
        # Nama berkas atau folder: baris 0, kolom dihitung di dalam nama. Tanpa judul kolom CSV.
        proses(berkas, 0, nama, None)

    hasil = scan(
        path,
        exclude=exclude,
        proses_baris=proses_baris,
        proses_header=judul_csv.catat_header,
        proses_nama=proses_nama,
    )
    temuan = urutkan_temuan(temuan)  # urut menurut path asli, baru disamarkan untuk tampilan
    tampil = [replace(t, berkas=samarkan(t.berkas)) for t in temuan]

    # Semua hasil dikumpulkan dulu, baru dicetak dan ditulis (3.2.2). Hanya nilai dan path ter-mask yang keluar (KF-20).
    json_ok = _tulis_laporan_json(output, tampil, _ringkasan(hasil, low_dibuang, min_level))

    print(f"Memindai: {samarkan(path)}")
    print(f"Berkas: {hasil.berkas_diperiksa} diperiksa, {hasil.berkas_dilewati} dilewati, {hasil.berkas_error} error")
    for pesan in hasil.pesan_error:
        print(f"ERROR {samarkan(pesan)}")
    if tampil:
        print()
        for t in tampil:
            print(baris_temuan(t))
        print()
    nama_json = samarkan(output) if (output is not None and json_ok) else None
    print(baris_ringkasan(hitung_per_rule(tampil, RULES), low_dibuang, bool(hasil.berkas_error), nama_json))

    if hasil.berkas_error or not json_ok:
        return EXIT_ERROR
    if temuan:
        return EXIT_TEMUAN
    return EXIT_OK


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        if args.json != (args.output is not None):
            parser.error("--json dan --output harus dipakai bersama")
        return _scan(args.path, args.exclude, args.min_level, args.output)
    return EXIT_ERROR  # tidak tercapai: subperintah wajib
