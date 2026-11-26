"""Judul kolom CSV sebagai konteks (langkah 8, perluasan KF-14).

Konteks biasa hanya membaca baris yang sama, jadi header `id,nama,nik` di baris 1 tidak terbaca
untuk baris 2 dan seterusnya. Modul ini mengingat header tiap berkas CSV, lalu menjawab:
"kandidat di posisi ini berada di kolom bernama apa?". Judul itu dipakai sebagai kata konteks.

Batasan yang diterima: dibaca baris per baris, jadi sel bertanda kutip yang berisi baris baru
tidak didukung. Hanya baris pertama yang dianggap header.
"""

import csv

PEMBATAS_KANDIDAT = ",;\t"  # koma, titik koma (Excel berlokal Indonesia), tab


class JudulCsv:
    def __init__(self) -> None:
        self._header = {}  # berkas -> (pembatas, [judul kolom])

    def catat_header(self, berkas: str, teks: str) -> None:
        """Catat baris pertama berkas CSV. Pembatas dipilih dari yang paling sering muncul (seri: koma)."""
        pembatas = max(PEMBATAS_KANDIDAT, key=teks.count)
        try:
            judul = next(csv.reader([teks], delimiter=pembatas), [])
        except csv.Error:
            judul = []
        self._header[berkas] = (pembatas, judul)

    def judul_di(self, berkas: str, teks: str, posisi: int) -> str | None:
        """Judul kolom tempat `teks[posisi]` berada, atau None (bukan CSV, tanpa header, atau di luar kolom)."""
        if berkas not in self._header:
            return None
        pembatas, judul = self._header[berkas]
        kolom = 0
        dalam_kutip = False
        for ch in teks[:posisi]:
            if ch == '"':
                dalam_kutip = not dalam_kutip
            elif ch == pembatas and not dalam_kutip:
                kolom += 1
        return judul[kolom] if kolom < len(judul) else None
