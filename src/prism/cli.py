"""Antarmuka baris perintah PRISM (langkah 9: keluaran teks, JSON, exit code).

Exit code (KF-21): 2 bila ada error pindai (didahulukan), jika tidak 1 bila ada
temuan yang dilaporkan, jika tidak 0.
"""

import argparse
import os
import sys

from prism import domain_email, wilayah
from prism.csv_judul import JudulCsv
from prism.engine import hapus_duplikat, periksa_baris, terapkan_ambang
from prism.report import (
    baris_ringkasan,
    baris_temuan,
    buat_json,
    hitung_per_rule,
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
        print(f"Error: laporan JSON tidak bisa ditulis ke {output}: {e.strerror}", file=sys.stderr)
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


def _gagal_sebelum_pindai(pesan: str, output, min_level: str) -> int:
    """Error sebelum pindai dimulai (path salah, data referensi rusak). JSON tetap ditulis bila diminta."""
    print(f"Error: {pesan}", file=sys.stderr)
    kosong = ScanResult(berkas_error=1)
    _tulis_laporan_json(output, [], _ringkasan(kosong, 0, min_level))
    return EXIT_ERROR


def _scan(path: str, exclude, min_level: str = MEDIUM, output: str | None = None) -> int:
    if not os.path.exists(path):
        return _gagal_sebelum_pindai(f"path tidak ditemukan: {path}", output, min_level)

    # Data referensi dimuat di awal. Bila hilang atau rusak, keluar dengan 2: crash Python
    # berkode 1 akan terbaca sebagai "ada temuan".
    for nama, muat in (
        ("kode wilayah", wilayah.pastikan_termuat),
        ("domain email pribadi", domain_email.pastikan_termuat),
    ):
        try:
            muat()
        except (OSError, ValueError) as e:
            return _gagal_sebelum_pindai(f"data {nama} tidak bisa dimuat: {e}", output, min_level)

    temuan = []
    low_dibuang = 0
    judul_csv = JudulCsv()

    def proses_baris(berkas, nomor, teks):
        # Urutan KF-14 sampai KF-16: bukti dan konteks, lalu ambang, lalu dedup.
        nonlocal low_dibuang
        kandidat = periksa_baris(
            berkas, nomor, teks, RULES, judul_kolom=lambda posisi: judul_csv.judul_di(berkas, teks, posisi)
        )
        lolos, dibuang = terapkan_ambang(kandidat, min_level)
        low_dibuang += dibuang
        temuan.extend(hapus_duplikat(lolos, RULES))

    hasil = scan(path, exclude=exclude, proses_baris=proses_baris, proses_header=judul_csv.catat_header)
    temuan = urutkan_temuan(temuan)

    # Semua hasil dikumpulkan dulu, baru dicetak dan ditulis (3.2.2). Hanya nilai ter-mask yang keluar (KF-20).
    json_ok = _tulis_laporan_json(output, temuan, _ringkasan(hasil, low_dibuang, min_level))

    print(f"Memindai: {path}")
    print(f"Berkas: {hasil.berkas_diperiksa} diperiksa, {hasil.berkas_dilewati} dilewati, {hasil.berkas_error} error")
    for pesan in hasil.pesan_error:
        print(f"ERROR {pesan}")
    if temuan:
        print()
        for t in temuan:
            print(baris_temuan(t))
        print()
    nama_json = output if (output is not None and json_ok) else None
    print(baris_ringkasan(hitung_per_rule(temuan, RULES), low_dibuang, bool(hasil.berkas_error), nama_json))

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
