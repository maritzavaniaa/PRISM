"""Pembuat data uji sintetis D1 untuk evaluasi PRISM (langkah 10). Hanya pustaka standar.

Pakai (dari akar repo):
    python3 evaluation/scripts/make_dataset.py

Keluaran:
    data/synthetic/layanan_publik/   36 berkas (csv, yaml, md, kode, log), tema layanan publik
    data/labels/ground_truth.csv     label D1 digabung dengan label D2 (tulis_tangan/labels_tulis_tangan.csv)
    data/labels/ringkasan.json       jumlah positif dan negatif

Semua nilai REKAAN. Nomor urut NIK (4 digit terakhir) dibuat `0000` (asumsi ⚠️ belum diverifikasi:
nomor urut asli dimulai dari 0001). HP berbagi awalan pelanggan `555`, email memakai bagian `uji`.
Tidak ada nilai yang diambil dari sumber nyata, tetapi kecocokan kebetulan dengan nomor atau alamat
nyata tidak bisa dikecualikan sepenuhnya ⚠️.

Faker TIDAK dipakai (rencana awal: Faker id_ID untuk nama). Alasannya: Faker bukan pustaka standar,
tidak punya generator NIK Indonesia, dan nama cukup diambil dari daftar di bawah. Pembuat ini ditulis
terpisah dari kode PRISM (tidak mengimpor `prism`), tetapi aturan NIK-nya mengikuti KF-11, jadi data
D1 SIRKULAR: NIK `high` pasti dikenali PRISM. D1 untuk recall dan FPR pada pengecoh, bukan bukti
akurasi aturan. Bukti yang tidak sirkular: D2 (tulisan tangan) dan D3 (python-stdnum).

Pembagian `split` per BERKAS: setiap berkas ketiga menjadi `kalibrasi`, sisanya `uji`.
Data `uji` tidak boleh dipakai menyetel aturan (skema-evaluasi.md bagian 3, aturan beku).
"""

import csv
import json
import random
import re
import shutil
import sys
import uuid
from collections import Counter
from pathlib import Path

SEED = 20261126
AKAR = Path(__file__).resolve().parents[2]
FOLDER_DATA = AKAR / "data" / "synthetic" / "layanan_publik"
LABEL = AKAR / "data" / "labels" / "ground_truth.csv"
RINGKASAN = AKAR / "data" / "labels" / "ringkasan.json"
LABEL_TULIS_TANGAN = AKAR / "data" / "synthetic" / "tulis_tangan" / "labels_tulis_tangan.csv"
WILAYAH = AKAR / "src" / "prism" / "data" / "kode-wilayah"

KOLOM = ["berkas", "baris", "jenis", "label", "level_diharapkan", "asal_sampel", "kata_konteks", "jenis_berkas", "split"]

# Kata petunjuk per jenis (KF-14), ditulis ulang di sini karena pembuat data tidak mengimpor `prism`.
KATA_KONTEKS = {
    "nik": {"nik", "ktp"},
    "hp": {"hp", "telp", "telepon", "wa", "whatsapp", "kontak", "phone", "mobile", "tel", "msisdn"},
    "email": {"email", "surel", "mail"},
}
# Kata yang membedakan asal sampel tetapi bukan kata konteks PRISM. Dicatat apa adanya di kolom kata_konteks.
KATA_LAIN = {"npwp", "kk"}

NAMA_DEPAN = ["Budi", "Siti", "Agus", "Dewi", "Rudi", "Wati", "Eko", "Sri", "Andi", "Rina", "Joko", "Lestari", "Hadi", "Maya"]
NAMA_BELAKANG = ["Santoso", "Wijaya", "Hartono", "Putri", "Kusuma", "Pratama", "Rahayu", "Nugroho", "Saputra", "Lestari"]
EMAIL_LOKAL = ["budi", "siti", "agus", "dewi", "rudi", "wati", "eko", "sri", "andi", "rina"]
DOMAIN_PRIBADI = [
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.id", "ymail.com", "outlook.com", "hotmail.com",
    "live.com", "msn.com", "icloud.com", "me.com", "proton.me", "protonmail.com",
]  # fmt: skip
DOMAIN_PERUSAHAAN = ["pt-abc.co.id", "example.com", "perusahaan.id", "kampus.ac.id", "dinas.go.id", "toko-maju.com"]
BENTUK_HP = ["plus62", "plus62-344", "nol", "nol-pemisah", "62-polos", "62-pemisah", "344", "polos", "pemisah-lain"]
HP_TANPA_AWALAN = {"344", "polos", "pemisah-lain"}

_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_KATA = re.compile(r"[a-z]+")


def kata_dalam(teks: str) -> set:
    return set(_KATA.findall(_CAMEL.sub(" ", teks).lower()))


def kata_konteks(teks_tanpa_nilai: str, jenis: str) -> str:
    """Kata konteks (atau KK/NPWP) yang ada di baris, dipilih tetap urut abjad. Kosong bila tidak ada."""
    ditemukan = kata_dalam(teks_tanpa_nilai) & (KATA_KONTEKS[jenis] | KATA_LAIN)
    return ",".join(sorted(ditemukan))


class Berkas:
    def __init__(self, rel: str, jenis_berkas: str, split: str):
        self.rel, self.jenis_berkas, self.split = rel, jenis_berkas, split
        self.baris: list = []
        self.label: list = []

    def tulis(self, teks: str, *label) -> None:
        """Tambah satu baris. label: (jenis, label, level, asal, kata_konteks)."""
        self.baris.append(teks)
        for jenis, lab, level, asal, kata in label:
            self.label.append([self.rel, len(self.baris), jenis, lab, level, asal, kata, self.jenis_berkas, self.split])


class Pembuat:
    def __init__(self):
        self.r = random.Random(SEED)
        with open(WILAYAH / "provinsi.csv", encoding="utf-8", newline="") as f:
            self.provinsi = sorted(b["kode"].strip() for b in csv.DictReader(f))
        with open(WILAYAH / "kecamatan.csv", encoding="utf-8", newline="") as f:
            self.kecamatan = sorted(b["kode"].strip() for b in csv.DictReader(f))
        self.set_kecamatan = set(self.kecamatan)

    # --- nilai ---

    def angka(self, n: int) -> str:
        return "".join(self.r.choice("0123456789") for _ in range(n))

    def tanggal(self, perempuan: bool, bulan=None, hari=None) -> str:
        r = self.r
        h = hari if hari is not None else r.randint(1, 28) + (40 if perempuan else 0)
        b = bulan if bulan is not None else r.randint(1, 12)
        return f"{h:02d}{b:02d}{r.randint(0, 99):02d}"

    def nik(self, jenis: str) -> str:
        r = self.r
        perempuan = r.random() < 0.5
        if jenis == "high":
            return r.choice(self.kecamatan) + self.tanggal(perempuan) + "0000"
        if jenis == "medium":
            while True:
                kec = r.choice(self.provinsi) + f"{r.randint(0, 9999):04d}"
                if kec not in self.set_kecamatan:
                    return kec + self.tanggal(perempuan) + "0000"
        if jenis == "bulan_salah":
            return r.choice(self.kecamatan) + self.tanggal(perempuan, bulan=r.randint(13, 99)) + "0000"
        if jenis == "acak16":
            return self.angka(16)
        raise ValueError(jenis)

    def kk(self) -> str:
        return self.r.choice(self.kecamatan) + self.tanggal(False) + "0000"  # tanggal perekaman: tanpa +40

    def hp(self, bentuk: str) -> str:
        r = self.r
        n = 11 if bentuk in ("plus62-344", "nol-pemisah", "62-pemisah", "344", "pemisah-lain") else r.randint(9, 12)
        h = "8" + str(r.randint(1, 9)) + "555" + self.angka(n - 5)
        return {
            "plus62": "+62" + h,
            "plus62-344": f"+62 {h[:3]}-{h[3:7]}-{h[7:11]}",
            "nol": "0" + h,
            "nol-pemisah": f"0{h[:3]}-{h[3:7]}-{h[7:11]}",
            "62-polos": "62" + h,
            "62-pemisah": f"62 {h[:3]} {h[3:7]} {h[7:11]}",
            "344": f"{h[:3]}-{h[3:7]}-{h[7:11]}",
            "polos": h,
            "pemisah-lain": f"{h[:4]}-{h[4:8]}-{h[8:11]}",
        }[bentuk]

    def email(self, pribadi: bool) -> str:
        r = self.r
        domain = r.choice(DOMAIN_PRIBADI if pribadi else DOMAIN_PERUSAHAAN)
        return f"{r.choice(EMAIL_LOKAL)}.uji.{r.choice(EMAIL_LOKAL)}@{domain}"

    def nama(self) -> str:
        return f"{self.r.choice(NAMA_DEPAN)} {self.r.choice(NAMA_BELAKANG)}"

    def stempel(self) -> str:
        r = self.r
        return f"2026-11-{r.randint(1, 25):02d} {r.randint(0, 23):02d}:{r.randint(0, 59):02d}:{r.randint(0, 59):02d}"

    def pengecoh(self):
        """(nilai, jenis_yang_mirip, asal_sampel). Dibuat tanpa memeriksa apa yang dilakukan PRISM padanya."""
        r = self.r
        pilihan = r.choice(["acak16", "rekening", "id_transaksi", "timestamp", "uuid", "epoch"])
        if pilihan == "acak16":
            return self.nik("acak16"), "nik", "acak16"
        if pilihan == "rekening":
            n = r.choice([10, 11, 12, 13, 15, 16])
            return str(r.randint(1, 9)) + self.angka(n - 1), ("nik" if n == 16 else "hp"), "rekening"
        if pilihan == "id_transaksi":
            n = r.choice([14, 16])  # tanggal + urutan
            return "TRX" + f"202611{r.randint(1, 25):02d}" + self.angka(n - 8), ("nik" if n == 16 else "hp"), "id_transaksi"
        if pilihan == "timestamp":
            return f"202611{r.randint(1, 25):02d}{r.randint(0, 23):02d}{r.randint(0, 59):02d}{r.randint(0, 59):02d}", "hp", "timestamp"
        if pilihan == "epoch":
            return str(r.randint(1_700_000_000_000, 1_800_000_000_000)), "hp", "timestamp"
        return str(uuid.UUID(int=r.getrandbits(128), version=4)), "nik", "uuid"

    # --- kejadian: satu baris berisi satu PII atau pengecoh ---

    def kejadian(self):
        """Pilih satu kejadian: (jenis, label, level, asal, nilai)."""
        r = self.r
        x = r.random()
        if x < 0.26:
            t = "high" if r.random() < 0.7 else "medium"
            return "nik", "positif", t, "nik", self.nik(t)
        if x < 0.30:
            return "nik", "positif", "high", "npwp_op", self.nik("high")
        if x < 0.34:
            return "nik", "positif", "high", "kk", self.kk()
        if x < 0.38:
            return "nik", "negatif", "low", "bulan_salah", self.nik("bulan_salah")
        if x < 0.60:
            b = r.choice(BENTUK_HP)
            return "hp", "positif", "", ("hp_tanpa_awalan" if b in HP_TANPA_AWALAN else "hp"), self.hp(b)
        if x < 0.78:
            if r.random() < 0.7:
                return "email", "positif", "", "email", self.email(True)
            return "email", "negatif", "", "email_perusahaan", self.email(False)
        v, jenis, asal = self.pengecoh()
        return jenis, "negatif", "low" if jenis == "nik" and asal in ("acak16", "id_transaksi") else "", asal, v


# Templat per jenis berkas. Kunci: "nik", "npwp_op", "kk", "bulan_salah" (NIK-like), "hp", "email", "pengecoh".
# {v} nilai, {n} nama, {t} stempel waktu. Kata konteks dihitung otomatis dari templat (tanpa nilai).
TEMPLAT = {
    "md": {
        "nik": ["Pemohon {n} terdaftar dengan NIK {v}.", "KTP {v} milik {n} sudah dicetak.", "Berkas {n} ({v}) telah diperiksa petugas.", "Data {n}: {v}"],
        "npwp_op": ["NPWP pribadi {n}: {v}.", "Pajak {n} memakai nomor {v}."],
        "kk": ["Nomor KK keluarga {n}: {v}.", "Kartu keluarga {n} bernomor {v}."],
        "bulan_salah": ["Pemohon {n} terdaftar dengan NIK {v}.", "Berkas {n} ({v}) telah diperiksa petugas."],
        "hp": ["Hubungi {n} di {v} pada jam kerja.", "WhatsApp {n}: {v}", "Telepon kantor {n} {v}", "Nomor ponsel {n} adalah {v}."],
        "email": ["Surel {n}: {v}", "Kirim dokumen ke {v} segera.", "Email {n}: {v}", "Korespondensi lewat {v}."],
        "pengecoh": ["Nomor rekening tujuan {v}.", "ID transaksi {v} sudah lunas.", "Dibuat pada {v}.", "Sesi {v} berakhir.", "Kode tiket {v}."],
    },
    "kode": {
        "nik": ['    "nik": "{v}",', 'NIK_UJI = "{v}"', '    "no_identitas": "{v}",', '# contoh KTP: {v}'],
        "npwp_op": ['    "npwp": "{v}",'],
        "kk": ['    "kk": "{v}",'],
        "bulan_salah": ['    "nik": "{v}",', '    "no_identitas": "{v}",'],
        "hp": ['    "phone": "{v}",', 'HP_UJI = "{v}"', '    "nomor_ponsel": "{v}",', '    "contact": "{v}",'],
        "email": ['    "email": "{v}",', 'SUREL = "{v}"', '    "alamat_surat": "{v}",'],
        "pengecoh": ['ID_TRANSAKSI = "{v}"', '    "session": "{v}",', 'REKENING = "{v}"', '    "ts": "{v}",'],
    },
    "log": {
        "nik": ["{t} INFO  validasi nik={v} hasil=ok", "{t} INFO  pemohon {n} id={v}", "{t} INFO  ktp diterima {v}"],
        "npwp_op": ["{t} INFO  validasi npwp={v}"],
        "kk": ["{t} INFO  validasi kk={v}"],
        "bulan_salah": ["{t} WARN  validasi nik={v} gagal", "{t} WARN  pemohon {n} id={v}"],
        "hp": ["{t} INFO  kirim notifikasi wa ke {v} sukses", "{t} INFO  kontak pemohon {v}", "{t} INFO  penerima {v}", "{t} INFO  phone={v}"],
        "email": ["{t} INFO  kirim email ke {v}", "{t} INFO  penerima {v}", "{t} INFO  surel={v}"],
        "pengecoh": ["{t} INFO  trx={v} lunas", "{t} INFO  rekening tujuan {v}", "{t} DEBUG session={v}", "{t} DEBUG epoch_ms={v}"],
    },
    "yaml": {
        "nik": ['    nik: "{v}"', '    no_identitas: "{v}"', '    ktp: "{v}"'],
        "npwp_op": ['    npwp: "{v}"'],
        "kk": ['    kk: "{v}"'],
        "bulan_salah": ['    nik: "{v}"', '    no_identitas: "{v}"'],
        "hp": ['    hp: "{v}"', '    nomor_ponsel: "{v}"', "    whatsapp: {v}", "    kontak: {v}"],
        "email": ["    email: {v}", "    alamat_surat: {v}", "    surel: {v}"],
        "pengecoh": ['    rekening: "{v}"', "    ref_transaksi: {v}", "    sesi: {v}", '    waktu: "{v}"'],
    },
}
JENIS_NIK_LIKE = {"nik", "npwp_op", "kk", "bulan_salah"}


def kunci_templat(jenis, asal, label) -> str:
    if jenis == "nik" and asal in JENIS_NIK_LIKE:
        return asal if asal != "nik" else "nik"
    if jenis == "nik":
        return "pengecoh"
    return "pengecoh" if label == "negatif" and asal not in ("email_perusahaan",) and jenis != "email" else jenis


def isi_baris(p: Pembuat, berkas: Berkas, kej) -> None:
    jenis, label, level, asal, nilai = kej
    kunci = kunci_templat(jenis, asal, label)
    if asal == "email_perusahaan":
        kunci = "email"
    templat = p.r.choice(TEMPLAT[berkas.jenis_berkas][kunci])
    teks = templat.replace("{v}", nilai).replace("{n}", p.nama()).replace("{t}", p.stempel())
    kata = kata_konteks(templat.replace("{v}", " ").replace("{t}", " ").replace("{n}", " "), jenis)
    berkas.tulis(teks, (jenis, label, level, asal, kata))


def buat_csv(p: Pembuat, berkas: Berkas) -> None:
    r = p.r
    kol_nik = r.choice(["nik", "no_ktp", "no_identitas"])
    kol_hp = r.choice(["telepon", "hp", "no_wa", "nomor_kontak", "nomor_ponsel"])
    kol_email = r.choice(["email", "surel", "alamat_surat"])
    berkas.tulis(f"id,nama,{kol_nik},{kol_hp},{kol_email},ref")

    def header(kol, jenis):
        kata = kata_dalam(kol) & KATA_KONTEKS[jenis]
        return f"header:{sorted(kata)[0]}" if kata else ""

    for i in range(1, r.randint(9, 13)):
        if r.random() < 0.25:  # baris pengecoh: hanya kolom ref terisi
            v, jenis, asal = p.pengecoh()
            level = "low" if jenis == "nik" and asal in ("acak16", "id_transaksi") else ""
            berkas.tulis(f"{i},-,,,,{v}", (jenis, "negatif", level, asal, ""))
            continue
        t = "high" if r.random() < 0.7 else "medium"
        b = r.choice(BENTUK_HP)
        pribadi = r.random() < 0.75
        em = p.email(pribadi)
        berkas.tulis(
            f"{i},{p.nama()},{p.nik(t)},{p.hp(b)},{em}, ",
            ("nik", "positif", t, "nik", header(kol_nik, "nik")),
            ("hp", "positif", "", "hp_tanpa_awalan" if b in HP_TANPA_AWALAN else "hp", header(kol_hp, "hp")),
            ("email", "positif" if pribadi else "negatif", "", "email" if pribadi else "email_perusahaan", header(kol_email, "email")),
        )
    # baris ref kosong di akhir dibuang supaya tidak ada spasi sisa
    berkas.baris = [b[:-1] if b.endswith(", ") else b for b in berkas.baris]


def buat_berkas_templat(p: Pembuat, berkas: Berkas) -> None:
    r = p.r
    judul = {"md": "# Catatan layanan (data rekaan)", "kode": "# Modul contoh layanan publik (data rekaan)",
             "log": None, "yaml": "pemohon:"}[berkas.jenis_berkas]  # fmt: skip
    if judul:
        berkas.tulis(judul)
    for _ in range(r.randint(10, 15)):
        isi_baris(p, berkas, p.kejadian())


EKSTENSI = {"csv": ".csv", "yaml": ".yaml", "md": ".md", "kode": ".py", "log": ".log"}
JUMLAH_BERKAS = {"csv": 8, "yaml": 7, "md": 7, "kode": 7, "log": 7}


def main() -> int:
    p = Pembuat()
    if FOLDER_DATA.exists():
        shutil.rmtree(FOLDER_DATA)
    FOLDER_DATA.mkdir(parents=True)
    semua: list = []
    urutan = [(j, i) for j, n in JUMLAH_BERKAS.items() for i in range(1, n + 1)]
    p.r.shuffle(urutan)  # pembagian split tidak menumpuk pada satu jenis berkas
    for indeks, (jenis_berkas, nomor) in enumerate(urutan):
        split = "kalibrasi" if indeks % 3 == 0 else "uji"
        rel = f"data/synthetic/layanan_publik/{jenis_berkas}_{nomor:02d}{EKSTENSI[jenis_berkas]}"
        berkas = Berkas(rel, jenis_berkas, split)
        (buat_csv if jenis_berkas == "csv" else buat_berkas_templat)(p, berkas)
        (AKAR / rel).write_text("\n".join(berkas.baris) + "\n", encoding="utf-8")
        semua += berkas.label

    # D2: label tulisan tangan digabung apa adanya (split uji).
    with open(LABEL_TULIS_TANGAN, encoding="utf-8", newline="") as f:
        d2 = [[b[k] for k in KOLOM] for b in csv.DictReader(f)]
    semua += d2

    semua.sort(key=lambda b: (b[0], int(b[1]), b[2]))
    with open(LABEL, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(KOLOM)
        w.writerows(semua)

    def hitung(baris):
        return {
            "total": len(baris),
            "positif": sum(1 for b in baris if b[3] == "positif"),
            "negatif": sum(1 for b in baris if b[3] == "negatif"),
        }

    ringkasan = {
        "seed": SEED,
        "semua": hitung(semua),
        "per_split": {s: hitung([b for b in semua if b[8] == s]) for s in ("kalibrasi", "uji")},
        "per_jenis": {j: hitung([b for b in semua if b[2] == j]) for j in ("nik", "hp", "email")},
        "per_asal_sampel": dict(sorted(Counter(b[5] for b in semua).items())),
        "per_jenis_berkas": dict(sorted(Counter(b[7] for b in semua).items())),
        "berkas_per_split": {
            s: len({b[0] for b in semua if b[8] == s and "layanan_publik" in b[0]}) for s in ("kalibrasi", "uji")
        },
    }
    RINGKASAN.write_text(json.dumps(ringkasan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: ringkasan[k] for k in ("semua", "per_split", "per_jenis", "berkas_per_split")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
