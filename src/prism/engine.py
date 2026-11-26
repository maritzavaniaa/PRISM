"""Mesin rule (langkah 5 dan 8): menjalankan semua rule pada satu baris.

Mesin ini tidak tahu isi tiap rule. Urutan proses (KF-14 sampai KF-16):
  1. periksa_baris   : regex mencari kandidat, assess menilai bukti, konteks menaikkan satu tingkat
  2. terapkan_ambang : buang tingkat di bawah --min-level (kandidat low yang dibuang dihitung)
  3. hapus_duplikat  : bila dua temuan beririsan, tinggal satu
Urutan ini penting: ambang harus sesudah konteks, kalau tidak NIK `low` yang punya kata `nik`
akan terbuang sebelum sempat naik.
"""

import re
from dataclasses import dataclass, field

from prism.rules import HIGH, LOW, MEDIUM

URUTAN_TINGKAT = {LOW: 0, MEDIUM: 1, HIGH: 2}
JARAK_KONTEKS = 40  # karakter di kiri dan kanan kandidat (hipotesis, KF-14)

# "phoneNumber" dipecah jadi "phone Number". Kata diambil dari huruf a-z saja, jadi garis bawah,
# strip, titik, angka, dan tanda baca semuanya menjadi pemisah ("no_hp", "e-mail", "hp2").
_BATAS_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_KATA = re.compile(r"[a-z]+")


@dataclass(frozen=True)
class Temuan:
    berkas: str
    baris: int  # mulai 1
    kolom: int  # mulai 1 (seperti penomoran di editor)
    rule_id: str
    tingkat: str
    # repr=False: nilai utuh tidak ikut tercetak lewat repr, log, atau pesan tes gagal (KF-20).
    nilai: str = field(repr=False)


def kata_dalam(teks: str) -> set:
    """Himpunan kata huruf kecil dari teks. Tidak membedakan huruf besar kecil."""
    return set(_KATA.findall(_BATAS_CAMEL.sub(" ", teks).lower()))


def ada_konteks(teks: str, awal: int, akhir: int, kata_konteks, judul: str | None = None) -> bool:
    """Apakah ada kata konteks di sekitar kandidat teks[awal:akhir] (KF-14)?

    Jendela: JARAK_KONTEKS karakter tepat di kiri `awal` dan di kanan `akhir`, di baris yang sama.
    Sebuah kata hanya dihitung bila seluruhnya berada di dalam jendela. Isi kandidat sendiri
    tidak ikut dibaca. `judul` (judul kolom CSV) dibaca sebagai konteks tambahan.
    """
    if not kata_konteks:
        return False
    jendela = teks[max(0, awal - JARAK_KONTEKS) : awal] + " " + teks[akhir : akhir + JARAK_KONTEKS]
    kata = kata_dalam(jendela)
    if judul:
        kata |= kata_dalam(judul)
    return bool(kata & set(kata_konteks))


def naikkan(tingkat: str) -> str:
    """Naik satu tingkat: low -> medium -> high. high tetap."""
    return MEDIUM if tingkat == LOW else HIGH


def periksa_baris(berkas: str, nomor_baris: int, teks: str, rules, judul_kolom=None) -> list:
    """Kembalikan semua kandidat satu baris dengan tingkat akhir (bukti + konteks), terurut menurut kolom.

    judul_kolom(posisi) -> judul kolom CSV di posisi itu, atau None (opsional).
    Ambang dan dedup belum diterapkan di sini.
    """
    hasil = []
    for rule in rules:
        for m in rule.regex.finditer(teks):
            nilai = m.group()
            tingkat = rule.assess(nilai)
            boleh_naik = tingkat == MEDIUM or (tingkat == LOW and rule.konteks_menaikkan_low)
            if boleh_naik:
                judul = judul_kolom(m.start()) if judul_kolom is not None else None
                if ada_konteks(teks, m.start(), m.end(), rule.context, judul):
                    tingkat = naikkan(tingkat)
            hasil.append(
                Temuan(
                    berkas=berkas,
                    baris=nomor_baris,
                    kolom=m.start() + 1,
                    rule_id=rule.id,
                    tingkat=tingkat,
                    nilai=nilai,
                )
            )
    hasil.sort(key=lambda t: t.kolom)  # sort stabil: urutan rule dipertahankan bila kolom sama
    return hasil


def terapkan_ambang(temuan, min_level: str):
    """Buang temuan di bawah `min_level` (KF-15). Kembalikan (yang_dilaporkan, jumlah_low_dibuang).

    Hanya kandidat low yang dibuang yang dihitung. Ambang tidak mengubah tingkat.
    """
    batas = URUTAN_TINGKAT[min_level]
    dilaporkan = []
    low_dibuang = 0
    for t in temuan:
        if URUTAN_TINGKAT[t.tingkat] >= batas:
            dilaporkan.append(t)
        elif t.tingkat == LOW:
            low_dibuang += 1
    return dilaporkan, low_dibuang


def hapus_duplikat(temuan, rules) -> list:
    """Bila dua temuan di satu baris beririsan (berbagi paling sedikit satu karakter), pilih satu (KF-16).

    Pemenang berurutan: tingkat tertinggi, lalu nilai terpanjang, lalu urutan rule di `rules`.
    Temuan yang tidak beririsan dengan siapa pun dibiarkan. Hasil terurut menurut kolom.
    """
    urutan_rule = {rule.id: i for i, rule in enumerate(rules)}
    peringkat = sorted(
        temuan,
        key=lambda t: (-URUTAN_TINGKAT[t.tingkat], -len(t.nilai), urutan_rule[t.rule_id], t.kolom),
    )
    terpilih = []
    for t in peringkat:
        awal, akhir = t.kolom, t.kolom + len(t.nilai)
        if all(akhir <= x.kolom or awal >= x.kolom + len(x.nilai) for x in terpilih):
            terpilih.append(t)
    return sorted(terpilih, key=lambda t: t.kolom)
