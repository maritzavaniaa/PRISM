"""Antarmuka baris perintah PRISM (temuan NIK, HP, email dan exit code).

Exit code (KF-21): 2 bila ada error pindai (didahulukan), jika tidak 1 bila ada
temuan, jika tidak 0.
"""

import argparse
import os
import sys

from prism import domain_email, wilayah
from prism.engine import periksa_baris
from prism.report import mask
from prism.rules import RULES
from prism.scanner import scan

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
    return parser


def _scan(path: str, exclude) -> int:
    if not os.path.exists(path):
        print(f"Error: path tidak ditemukan: {path}", file=sys.stderr)
        return EXIT_ERROR

    # Data referensi dimuat di awal. Bila hilang atau rusak, keluar dengan 2: crash Python
    # berkode 1 akan terbaca sebagai "ada temuan".
    for nama, muat in (
        ("kode wilayah", wilayah.pastikan_termuat),
        ("domain email pribadi", domain_email.pastikan_termuat),
    ):
        try:
            muat()
        except (OSError, ValueError) as e:
            print(f"Error: data {nama} tidak bisa dimuat: {e}", file=sys.stderr)
            return EXIT_ERROR

    temuan = []

    def proses_baris(berkas, nomor, teks):
        temuan.extend(periksa_baris(berkas, nomor, teks, RULES))

    hasil = scan(path, exclude=exclude, proses_baris=proses_baris)

    for pesan in hasil.pesan_error:
        print(f"Error: {pesan}", file=sys.stderr)

    # Hanya nilai yang sudah di-mask yang boleh sampai ke keluaran (KF-20).
    for t in temuan:
        print(f"{t.berkas}:{t.baris}:{t.kolom}  {t.rule_id}  {t.tingkat}  {mask(t.nilai)}")

    print(f"Berkas diperiksa: {hasil.berkas_diperiksa}")
    print(f"Berkas dilewati: {hasil.berkas_dilewati}")
    print(f"Berkas error: {hasil.berkas_error}")
    print(f"Baris dibaca: {hasil.baris_dibaca}")
    print(f"Baris lolos prefilter: {hasil.baris_lolos_prefilter}")
    print(f"Temuan: {len(temuan)}")

    if hasil.berkas_error:
        return EXIT_ERROR
    if temuan:
        return EXIT_TEMUAN
    return EXIT_OK


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "scan":
        return _scan(args.path, args.exclude)
    return EXIT_ERROR  # tidak tercapai: subperintah wajib
