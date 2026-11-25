"""Keluaran laporan (langkah 5: mask, KF-20).

Teks dan JSON menyusul di langkah 9 dan 10.
"""

JUMLAH_TERLIHAT = 4


def mask(nilai: str) -> str:
    """Samarkan nilai NIK atau HP: semua karakter jadi '*' kecuali 4 terakhir.

    Nilai berpanjang 4 karakter atau kurang disamarkan seluruhnya. Panjang tetap.
    Aturan email (bagian sebelum '@') menyusul di langkah 9.
    """
    if len(nilai) <= JUMLAH_TERLIHAT:
        return "*" * len(nilai)
    return "*" * (len(nilai) - JUMLAH_TERLIHAT) + nilai[-JUMLAH_TERLIHAT:]
