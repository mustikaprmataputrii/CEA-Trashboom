# Kamus data: `parameter_sungai.csv`

| Kolom | Satuan | Keterangan |
|---|---|---|
| kode | – | S01 sampai S10 |
| nama | – | nama sungai |
| wilayah | – | kota atau kabupaten |
| akses | – | aksesibilitas lokasi: Mudah, Sedang, atau Sulit |
| lebar_m | m | lebar sungai |
| capex_rp | Rp | biaya pemasangan trashboom (estimasi) |
| perawatan_rp_per_bulan | Rp/bulan | biaya perawatan trashboom (estimasi) |
| umk_rp_per_bulan | Rp/bulan | upah minimum kabupaten/kota setempat; upah model = 19,06% dari nilai ini |
| transport_rp_per_hari | Rp/hari | biaya transportasi per hari angkut |
| vol_min_ton_bulan, vol_max_ton_bulan | ton/bulan | batas bawah dan atas volume bulanan kondisi normal |

## Catatan asal data
- CapEx pada delapan dari sepuluh sungai sama dengan Rp2.925.000 x lebar sungai (S02 dan S03 sedikit berbeda), dan perawatan sekitar 4,1% CapEx per bulan. Artinya nilai-nilai ini estimasi berbasis harga satuan, bukan realisasi biaya proyek.
- Dasar penetapan 19,06% UMK adalah asumsi penulis.
- Batas Min dan Maks volume dianggap mewakili kondisi normal (bukan hujan).
- Kategori beban (Rendah, Sedang, Tinggi) dan kelas kapasitas trashboom (45, 150, 300 ton/bulan) dihitung di `src/model.py`.
