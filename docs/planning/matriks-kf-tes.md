# Matriks KF → tes

> Dibuat 26 Nov. 2026 (langkah 11). Diperiksa otomatis oleh `tests/test_matriks_kf.py`: tiap KF punya paling sedikit satu tes, dan tiap tes yang disebut benar-benar ada.
> Format rujukan: `tests/<berkas>.py::<fungsi>` (tes berparameter dihitung satu fungsi).
> **Bukti manual** adalah hal yang tidak bisa dibuktikan oleh pytest (GitHub sungguhan). Hasilnya dicatat di mvp-t5.md.

| KF | Tes | Bukti manual / catatan |
|---|---|---|
| KF-01 | tests/test_cli.py::test_scan_berkas_ada_exit_0_dan_mencetak_jumlah_baris; tests/test_cli.py::test_scan_folder_mencetak_ringkasan_dan_exit_0 | |
| KF-02 | tests/test_cli.py::test_scan_path_tidak_ada_exit_2_pesan_di_stderr; tests/test_cli.py::test_tanpa_argumen_exit_2 | |
| KF-03 | tests/test_scanner.py::test_folder_bersarang_jumlah_berkas_sama_dengan_hitungan_manual; tests/test_scanner.py::test_penelusuran_terurut_abjad_dan_bisa_diulang | |
| KF-04 | tests/test_scanner.py::test_folder_git_dilewati_dan_terhitung; tests/test_scanner.py::test_exclude_diulang_dua_kali; tests/test_scanner.py::test_ekstensi_biner_dilewati; tests/test_scanner.py::test_berkas_dengan_byte_nol_dilewati; tests/test_scanner.py::test_berkas_lebih_dari_1_mb_dilewati; tests/test_scanner.py::test_berkas_tepat_1_mb_masih_dipindai | |
| KF-05 | tests/test_scanner.py::test_non_utf8_terbaca_tanpa_error; tests/test_scanner.py::test_berkas_tanpa_izin_baca_error_dan_pindai_lanjut | |
| KF-06 | tests/test_scanner.py::test_prefilter_lolos_bila_digit_minimal_8; tests/test_scanner.py::test_prefilter_tidak_lolos_bila_digit_kurang_dari_8; tests/test_scanner.py::test_prefilter_lolos_bila_ada_at; tests/test_scanner.py::test_prefilter_menghitung_digit_tersebar_di_baris | |
| KF-07 | tests/test_rules.py::test_16_digit_satu_kandidat; tests/test_rules.py::test_15_digit_tidak_terdeteksi; tests/test_rules.py::test_17_digit_tidak_terdeteksi_karena_diapit_digit | |
| KF-08 | tests/test_hp.py::test_enam_bentuk_terdeteksi_utuh; tests/test_hp.py::test_pengecoh_bukan_kandidat; tests/test_hp.py::test_batas_panjang_9_sampai_12_digit_dari_angka_8 | |
| KF-09 | tests/test_email.py::test_bentuk_sah_terdeteksi; tests/test_email.py::test_local_part_64_karakter_diterima_65_tidak; tests/test_email.py::test_tld_satu_huruf_tidak_terdeteksi | |
| KF-10 | tests/test_nik_assess.py::test_npwp_pribadi_16_digit_dilaporkan_sebagai_nik; tests/test_dataset.py::test_ada_semua_asal_sampel_yang_diwajibkan | KK: data uji `asal_sampel=kk` di D1 dan D2 |
| KF-11 | tests/test_nik_assess.py::test_tabel_tingkat_kf11; tests/test_nik_assess.py::test_hari_melebihi_jumlah_hari_bulan_itu_low; tests/test_nik_assess.py::test_nik_berawalan_99_belum_ditangani_jatuh_ke_low; tests/test_nik_assess.py::test_provinsi_dan_kecamatan_valid | |
| KF-12 | tests/test_hp.py::test_tingkat_tiap_bentuk; tests/test_hp.py::test_tingkat_bentuk_di_luar_tabel | |
| KF-13 | tests/test_email.py::test_tingkat_menurut_domain; tests/test_email.py::test_menambah_domain_di_berkas_mengubah_hasil_tanpa_mengubah_kode | |
| KF-14 | tests/test_engine.py::test_konteks_nik; tests/test_engine.py::test_batas_40_karakter_di_kiri_diuji_di_kedua_sisi; tests/test_engine.py::test_batas_40_karakter_di_kanan_diuji_di_kedua_sisi; tests/test_engine.py::test_konteks_hp; tests/test_engine.py::test_konteks_email | |
| KF-15 | tests/test_engine.py::test_ambang_medium_melaporkan_a_dan_b_dan_menghitung_c; tests/test_engine.py::test_ambang_low_melaporkan_semuanya; tests/test_engine.py::test_ambang_high_hanya_a_dan_hanya_low_yang_dihitung; tests/test_cli.py::test_hanya_low_pada_ambang_bawaan_exit_0 | |
| KF-16 | tests/test_engine.py::test_irisan_tingkat_sama_yang_terpanjang_menang; tests/test_engine.py::test_irisan_hp_high_menang_atas_email_walau_lebih_pendek; tests/test_engine.py::test_irisan_tingkat_dan_panjang_sama_urutan_rule_menentukan | |
| KF-17 | tests/test_laporan.py::test_tiap_baris_temuan_cocok_pola; tests/test_report.py::test_baris_temuan_cocok_pola_dan_nilai_di_mask | |
| KF-18 | tests/test_laporan.py::test_json_ditulis_dengan_struktur_lengkap; tests/test_report.py::test_buat_json_struktur_dan_urutan_kunci | |
| KF-19 | tests/test_laporan.py::test_ringkasan_json_pada_folder_uji; tests/test_report.py::test_baris_ringkasan | |
| KF-20 | tests/test_report.py::test_mask_nik_empat_terakhir_terlihat; tests/test_report.py::test_mask_hp; tests/test_email.py::test_mask_email_bagian_sebelum_at_jadi_bintang; tests/test_laporan.py::test_nilai_utuh_tidak_ada_di_stdout_stderr_dan_json; tests/test_laporan.py::test_nilai_utuh_tidak_ada_pada_error_baca_berkas | |
| KF-21 | tests/test_laporan.py::test_tiga_exit_code; tests/test_cli.py::test_error_baca_didahulukan_atas_temuan_exit_2 | |
| KF-22 | tests/test_workflow.py::test_workflow_dipicu_push_dan_pull_request; tests/test_workflow.py::test_workflow_memasang_python_versi_lokal; tests/test_workflow.py::test_workflow_menjalankan_prism_scan | Dua tes terakhir `xfail` sampai langkah 12. Integrasi nyata sudah dicoba di repo percobaan prism-test (checkout, setup-python, pindai) |
| KF-23 | tests/test_workflow.py::test_workflow_tidak_menelan_exit_code; tests/test_laporan.py::test_tiga_exit_code | **Manual (langkah 12):** push berkas bersih hijau, berkas berNIK merah, dihapus hijau. Sudah terbukti di prism-test (merah, hijau, hijau) |
| KF-24 | tests/test_cli.py::test_exclude_bisa_diulang_dan_dihitung_dilewati; tests/test_workflow.py::test_workflow_mengecualikan_folder_data_uji | Tes workflow `xfail` sampai langkah 12 |
| KF-25 | tests/test_dataset.py::test_assess_nik_sama_dengan_level_diharapkan_untuk_semua_nik_positif; tests/test_dataset.py::test_tidak_ada_berkas_di_dua_split; tests/test_dataset.py::test_ringkasan_json_cocok_dengan_label | |
| KF-26 | - | **Belum ada tes:** `evaluate.py` dibuat di langkah 13, tesnya menyusul di sana. Dikecualikan eksplisit di `test_matriks_kf.py` |
| KF-27 | tests/test_matriks_kf.py::test_semua_kf_punya_tes_yang_ada | Matriks ini sendiri |
| KF-28 | tests/test_path_pii.py::test_nama_berkas_biner_dengan_nik_dilaporkan_di_baris_0; tests/test_path_pii.py::test_nama_folder_dengan_nik_dilaporkan; tests/test_scanner.py::test_nama_berkas_dan_folder_dengan_digit_diteruskan | |
| KF-29 | tests/test_path_pii.py::test_path_dengan_nik_disamarkan_di_baris_temuan_isi; tests/test_path_pii.py::test_path_disamarkan_di_json_dan_ada_target; tests/test_path_pii.py::test_path_pada_pesan_error_disamarkan | |

## Tes di luar matriks KF

| Aspek | Tes |
|---|---|
| Pengecoh (UUID, timestamp, rekening, ID transaksi, angka biasa) | tests/test_pengecoh.py |
| Keterulangan (dua kali jalan identik) | tests/test_laporan.py::test_keterulangan_dua_kali_jalan_identik; tests/test_scanner.py::test_penelusuran_terurut_abjad_dan_bisa_diulang; tests/test_dataset.py::test_generator_menghasilkan_label_d1_yang_sama_dengan_yang_ada_di_repo |
| Tanpa jaringan (KN-04) | tests/test_laporan.py::test_kode_tidak_mengimpor_modul_jaringan |
| Versi Python sama dengan lokal (KN-08) | tests/test_cli.py::test_python_yang_dipakai_adalah_3_13 |
| Batasan yang didokumentasikan lewat tes | NIK berpemisah 0 temuan (test_rules.py), kandidat HP palsu dari NIK berpemisah (test_hp.py), email + ekstensi (test_path_pii.py), UTF-16 dilewati (prism-test) |
