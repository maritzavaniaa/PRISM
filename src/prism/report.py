"""Keluaran laporan (langkah 9: KF-17 sampai KF-20).

Semua yang sampai ke teks atau JSON melewati mask() lebih dulu. Nilai utuh tidak pernah ditulis.
"""

import json

SCHEMA_VERSION = 1
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


def samarkan_rentang(teks: str, rentang) -> str:
    """Ganti tiap rentang (awal, akhir) di `teks` dengan hasil mask() atasnya. Panjang teks tetap."""
    hasil = []
    sebelumnya = 0
    for awal, akhir in rentang:
        hasil.append(teks[sebelumnya:awal])
        hasil.append(mask(teks[awal:akhir]))
        sebelumnya = akhir
    hasil.append(teks[sebelumnya:])
    return "".join(hasil)


def urutkan_temuan(temuan) -> list:
    """Urutan tetap supaya dua kali jalan memberi keluaran sama: berkas, baris, lalu kolom (KN-06)."""
    return sorted(temuan, key=lambda t: (t.berkas, t.baris, t.kolom))


def baris_temuan(t) -> str:
    """Satu baris log: berkas:baris:kolom  rule  tingkat  nilai-mask (KF-17)."""
    return f"{t.berkas}:{t.baris}:{t.kolom}  {t.rule_id}  {t.tingkat}  {mask(t.nilai)}"


def hitung_per_rule(temuan, rules) -> dict:
    """Jumlah temuan per jenis, urut menurut daftar rule. Jenis tanpa temuan tetap tercatat 0."""
    hitung = {rule.id: 0 for rule in rules}
    for t in temuan:
        hitung[t.rule_id] += 1
    return hitung


def baris_ringkasan(per_rule: dict, low_dibuang: int, tidak_lengkap: bool, nama_json: str | None) -> str:
    """Satu baris ringkasan, contoh: `3 temuan (nik 1, hp 1, email 1). Tidak dilaporkan: 2 kandidat low.`"""
    total = sum(per_rule.values())
    if total:
        rincian = ", ".join(f"{nama} {n}" for nama, n in per_rule.items() if n)
        teks = f"{total} temuan ({rincian}). "
    else:
        teks = "0 temuan. "
    teks += f"Tidak dilaporkan: {low_dibuang} kandidat low."
    if tidak_lengkap:
        teks += " Pindai tidak lengkap."
    if nama_json:
        teks += f" Laporan JSON: {nama_json}"
    return teks


def buat_json(temuan, rules, ringkasan: dict) -> dict:
    """Susun laporan JSON (KF-18, KF-19). `ringkasan` berisi angka hasil pindai dan min_level.

    Urutan kunci: schema_version, findings, scan. Hanya nilai ter-mask yang masuk.
    """
    per_rule = hitung_per_rule(temuan, rules)
    return {
        "schema_version": SCHEMA_VERSION,
        "findings": [
            {
                "rule_id": t.rule_id,
                "level": t.tingkat,
                "location": {
                    "file": t.berkas,
                    "line": t.baris,
                    "column": t.kolom,
                    "target": "name" if t.baris == 0 else "content",
                },
                "match": {"value": mask(t.nilai)},
            }
            for t in temuan
        ],
        "scan": {
            "mode": "repo",
            "files": ringkasan["files"],
            "skipped": ringkasan["skipped"],
            "lines": ringkasan["lines"],
            "lines_prefiltered": ringkasan["lines_prefiltered"],
            "findings": len(temuan),
            "findings_by_rule": per_rule,
            "suppressed_low": ringkasan["suppressed_low"],
            "errors": ringkasan["errors"],
            "min_level": ringkasan["min_level"],
        },
    }


def tulis_json(path: str, laporan: dict) -> None:
    """Tulis laporan ke berkas UTF-8. Melempar OSError bila gagal."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(laporan, f, indent=2, ensure_ascii=True)
        f.write("\n")
