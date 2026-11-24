"""Antarmuka baris perintah PRISM (langkah 3: kerangka).

Exit code (KF-21): 0 bersih, 1 ada temuan, 2 gagal pindai atau salah pemakaian.
Di langkah ini belum ada pencarian temuan, jadi hanya 0 dan 2 yang terpakai.
"""

import argparse
import os
import sys

EXIT_OK = 0
EXIT_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prism",
        description="PRISM: pemindai PII Indonesia di repositori.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="pindai satu berkas atau satu folder")
    scan.add_argument("path", help="berkas atau folder yang dipindai")
    return parser


def _scan(path: str) -> int:
    if not os.path.exists(path):
        print(f"Error: path tidak ditemukan: {path}", file=sys.stderr)
        return EXIT_ERROR

    # Sementara (langkah 3): hanya berkas. Penelusuran folder dikerjakan di langkah 4.
    if os.path.isdir(path):
        print(
            f"Error: folder belum didukung di langkah ini: {path}",
            file=sys.stderr,
        )
        return EXIT_ERROR

    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            jumlah_baris = sum(1 for _ in f)
    except OSError as e:
        print(f"Error: gagal membaca {path}: {e.strerror}", file=sys.stderr)
        return EXIT_ERROR

    print(f"{path}: {jumlah_baris} baris")
    return EXIT_OK


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "scan":
        return _scan(args.path)
    return EXIT_ERROR  # tidak tercapai: subperintah wajib
