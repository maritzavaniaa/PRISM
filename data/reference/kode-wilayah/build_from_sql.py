"""Membuat provinsi.csv, kabkota.csv, dan kecamatan.csv dari wilayah.sql.

Pemakaian (dari folder mana pun):
    python3 -I build_from_sql.py <wilayah.sql> <folder-keluaran>

Hanya library standar. File masukan diperlakukan sebagai data, tidak dijalankan.
Kode dibuat tanpa titik, sesuai bentuk di NIK: provinsi 2 digit, kab/kota 4 digit,
kecamatan 6 digit. Desa dan kelurahan tidak diambil.
"""
import csv
import re
import sys
from pathlib import Path

PATTERN = re.compile(r"\('([0-9.]+)','((?:[^'\\]|''|\\.)*)'\)")


def main(src, outdir):
    text = Path(src).read_text(encoding="utf-8")
    rows = [(k, n.replace("''", "'").replace("\\'", "'").strip()) for k, n in PATTERN.findall(text)]
    levels = {1: [], 2: [], 3: []}
    for kode, nama in rows:
        lvl = kode.count(".") + 1
        if lvl in levels:
            levels[lvl].append((kode.replace(".", ""), nama))
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    for name, lvl in (("provinsi.csv", 1), ("kabkota.csv", 2), ("kecamatan.csv", 3)):
        with open(out / name, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["kode", "nama"])
            w.writerows(levels[lvl])
    print({"provinsi": len(levels[1]), "kabkota": len(levels[2]), "kecamatan": len(levels[3])})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
