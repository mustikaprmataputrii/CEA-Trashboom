# Simulasi Analisis Efektivitas Biaya Trashboom dan Relawan di Sungai Jawa Timur

Kode dan data pendukung naskah **"Analisis Efektivitas Biaya Kombinasi Trashboom dan Partisipasi Masyarakat dalam Pembersihan Sampah Sungai"** (Jurnal Pustaka Data).
Seluruh angka pada bagian Metode serta Hasil dan Pembahasan naskah dapat dihasilkan ulang dari repositori ini.

> **Catatan penting tentang data.** Data biaya (CapEx, perawatan, upah, transportasi) dan batas volume bulanan pada `data/parameter_sungai.csv`
> adalah **estimasi**, bukan realisasi biaya proyek. CapEx mengikuti harga satuan sekitar Rp2,925 juta per meter lebar sungai,
> perawatan sekitar 4,1% CapEx per bulan, dan upah 19,06% dari UMK setempat. Hasil CER karenanya adalah perkiraan.

## Isi repositori

```
data/parameter_sungai.csv   parameter sepuluh sungai (S01-S10)
data/README_DATA.md         kamus data dan catatan asal data
src/model.py                model simulasi (skenario A, B, C, D) dan fungsi ICER/dominansi
src/analysis.py             replikasi Monte Carlo, sensitivitas, PSA, dan optimasi alokasi anggaran
src/run_simulation.py       menjalankan semuanya -> results/results.json
src/make_tables.py          membuat tabel naskah (CSV) -> results/tables/
src/make_figures.py         membuat gambar naskah (PNG) -> results/figures/
tests/test_model.py         uji sederhana (neraca massa, reproduksibilitas, dominansi, ICER)
results/                    hasil yang sudah dihasilkan (benih acak 2026)
```

## Cara menjalankan

Perlu Python 3.10 atau lebih baru.

```bash
git clone https://github.com/USERNAME/NAMA-REPOSITORI.git
cd NAMA-REPOSITORI
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python src/run_simulation.py       # 1.000 replikasi + 2.000 undian PSA (sekitar 1-2 menit)
python src/make_tables.py          # tabel CSV
python src/make_figures.py         # gambar PNG
python -m pytest -q                # uji
```

Uji cepat: `python src/run_simulation.py --R 200 --psa 300`.

## Hubungan dengan naskah

| Keluaran | Isi |
|---|---|
| `results/tables/tabel04_perbandingan_biaya_efektivitas.csv` | Tabel 4: rata-rata ± simpangan baku 1.000 replikasi (dua desimal), dominansi, dan ICER |
| `results/tables/tabel05_per_sungai.csv` | Tabel 5: pilihan skenario, ICER, dan periode balik modal per sungai |
| `results/tables/tabel06_frekuensi_kapasitas.csv` | Tabel 6: frekuensi pengangkatan dan kapasitas angkat anjuran |
| `results/tables/tabel07_sensitivitas.csv` | Tabel 7: sensitivitas satu arah |
| `results/tables/tabel08_alokasi_anggaran.csv` | Tabel 8: alokasi optimal pada beberapa pagu anggaran |
| `results/figures/gambar01...gambar07*.png` | Gambar 1 sampai Gambar 7 |
| `results/results.json` | seluruh hasil numerik (termasuk CEAC, korelasi peringkat, batas efisien) |

## Ringkasan model

- Volume normal bulanan diundi seragam di antara batas Min dan Maks tiap sungai (padanan `=RANDBETWEEN(Min; Maks)`), lalu lonjakan musim hujan 50–80% berlaku pada semua skenario di enam bulan hujan.
- Skenario A: trashboom stasioner. B: manual dengan tenaga tetap. C: trashboom ringan dan relawan. D: manual intensif.
- Biaya modal memakai faktor pemulihan modal (diskonto 8%, umur 5 tahun).
- Keputusan memakai dominansi, ICER, manfaat moneter bersih pada kesediaan membayar Rp500.000 per ton, dan kurva penerimaan biaya-efektivitas (CEAC).
- Parameter yang belum bersumber lapangan (efisiensi manual 60%, faktor biaya dan kapasitas trashboom ringan) diuji lewat sensitivitas probabilistik.
- Benih acak: 2026 (simulasi utama) dan 7 (PSA), sehingga hasil identik pada setiap eksekusi.

## Lisensi dan sitasi

Kode: lisensi MIT (`LICENSE`). Data pada `data/`: CC BY 4.0. Sitasi: lihat `CITATION.cff`.
