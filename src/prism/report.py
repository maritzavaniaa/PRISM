"""Keluaran laporan (mask, KF-20).

Teks dan JSON menyusul di langkah 9 dan 10.
"""

JUMLAH_TERLIHAT = 4


def mask(nilai: str) -> str:
    """Samarkan nilai yang akan dilaporkan.

    Email (ada '@'): seluruh bagian sebelum '@' jadi '*', '@' dan domain tetap tampil.
    NIK dan HP (tanpa '@'): semua karakter jadi '*' kecuali 4 terakhir. Nilai berpanjang
    4 karakter atau kurang disamarkan seluruhnya. Panjang nilai selalu tetap.
    """
    if "@" in nilai:
        lokal, at, domain = nilai.rpartition("@")
        return "*" * len(lokal) + at + domain
    if len(nilai) <= JUMLAH_TERLIHAT:
        return "*" * len(nilai)
    return "*" * (len(nilai) - JUMLAH_TERLIHAT) + nilai[-JUMLAH_TERLIHAT:]
