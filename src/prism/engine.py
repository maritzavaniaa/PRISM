"""Mesin rule (langkah 5): menjalankan semua rule pada satu baris.

Mesin ini tidak tahu isi tiap rule. Ia hanya mencari kandidat dengan regex lalu
memanggil assess milik rule. Konteks, ambang, dan dedup menyusul (langkah 8).
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Temuan:
    berkas: str
    baris: int  # mulai 1
    kolom: int  # mulai 1 (seperti penomoran di editor)
    rule_id: str
    tingkat: str
    # repr=False: nilai utuh tidak ikut tercetak lewat repr, log, atau pesan tes gagal (KF-20).
    nilai: str = field(repr=False)


def periksa_baris(berkas: str, nomor_baris: int, teks: str, rules) -> list:
    """Kembalikan semua kandidat di satu baris, terurut menurut kolom lalu urutan rule."""
    hasil = []
    for rule in rules:
        for m in rule.regex.finditer(teks):
            nilai = m.group()
            hasil.append(
                Temuan(
                    berkas=berkas,
                    baris=nomor_baris,
                    kolom=m.start() + 1,
                    rule_id=rule.id,
                    tingkat=rule.assess(nilai),
                    nilai=nilai,
                )
            )
    hasil.sort(key=lambda t: t.kolom)  # sort stabil: urutan rule dipertahankan bila kolom sama
    return hasil
