"""Antarmuka baris perintah PRISM (langkah 4: penelusuran folder dan ringkasan).

Exit code (KF-21): 0 bersih, 1 ada temuan, 2 gagal pindai atau salah pemakaian.
Di langkah ini belum ada pencarian temuan, jadi hanya 0 dan 2 yang terpakai.
"""

import argparse
import os
import sys

from prism.scanner import scan

EXIT_OK = 0
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

    hasil = scan(path, exclude=exclude)

    for pesan in hasil.pesan_error:
        print(f"Error: {pesan}", file=sys.stderr)

    print(f"Berkas diperiksa: {hasil.berkas_diperiksa}")
    print(f"Berkas dilewati: {hasil.berkas_dilewati}")
    print(f"Berkas error: {hasil.berkas_error}")
    print(f"Baris dibaca: {hasil.baris_dibaca}")
    print(f"Baris lolos prefilter: {hasil.baris_lolos_prefilter}")

    return EXIT_ERROR if hasil.berkas_error else EXIT_OK


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "scan":
        return _scan(args.path, args.exclude)
    return EXIT_ERROR  # tidak tercapai: subperintah wajib
