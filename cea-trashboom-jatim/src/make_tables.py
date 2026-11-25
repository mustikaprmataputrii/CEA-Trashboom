# -*- coding: utf-8 -*-
"""Buat tabel-tabel naskah (CSV) dari results/results.json.
Tabel 4 memuat rata-rata ± simpangan baku 1.000 replikasi dengan dua angka desimal."""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results', 'results.json')
OUT = os.path.join(HERE, '..', 'results', 'tables')
CATS = ['Rendah', 'Sedang', 'Tinggi']
SCN = ['A', 'B', 'C', 'D']


def write(name, header, rows):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf8') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    o = json.load(open(RES, encoding='utf8'))
    # ---- Tabel 4: rata-rata ± simpangan baku (desimal)
    rows = []
    for c in CATS:
        b = o['base'][c]
        for k, s in enumerate(SCN):
            ic = b['icer'].get(s)
            status = ('tak didominasi' if b['status'][s] == 'tak-didominasi' else 'didominasi')
            rows.append([c, s, round(b['cost'][k] / 1e6, 2), round(b['cost_sd'][k] / 1e6, 2),
                         round(b['tons'][k], 2), round(b['tons_sd'][k], 2),
                         round(b['cer'][k] / 1000, 2), round(b['cer_sd'][k] / 1000, 2),
                         '' if s == 'B' else round(b['eb'][k] * 100, 2), '' if s == 'B' else round(b['eb_sd'][k] * 100, 2),
                         status, round(ic['icer'] / 1000, 2) if ic else ''])
    write('tabel04_perbandingan_biaya_efektivitas.csv',
          ['kategori', 'skenario', 'biaya_rp_juta_per_tahun_rerata', 'biaya_sd', 'terangkat_ton_per_tahun_rerata', 'terangkat_sd',
           'cer_rp_ribu_per_ton', 'cer_sd', 'e_biaya_persen', 'e_biaya_sd', 'dominansi', 'icer_vs_pembanding_rp_ribu_per_ton'], rows)
    # ---- Tabel 5: per sungai
    rows = []
    for k, r in o['riv'].items():
        ic = r['icer'].get('A')
        rows.append([k, r['nama'], r['cat'], r['akses'], round(r['share']['A'] * 100, 1), round(r['share']['C'] * 100, 1),
                     round(ic['icer'] / 1000, 2) if ic and ic['vs'] == 'C' else '', round(r['ppeq'], 2), round(r['ppraw'], 2),
                     round(r['eff_share'] * 100, 1)])
    write('tabel05_per_sungai.csv', ['kode', 'nama', 'kategori', 'akses', 'A_dipilih_persen', 'C_dipilih_persen',
                                     'icer_A_vs_C_rp_ribu_per_ton', 'pp_tonase_setara_tahun', 'pp_tanpa_penyetaraan_tahun', 'porsi_berbayar_efektif_persen'], rows)
    # ---- Tabel 6: frekuensi dan kapasitas angkat
    rows = [[c, round(d['fA_dry'], 2), round(d['fA_rain'], 2), round(d['fA_max'], 2), round(d['c_rec_A'], 2), round(d['eff_share'] * 100, 1)]
            for c, d in o['catx'].items()]
    write('tabel06_frekuensi_kapasitas.csv', ['kategori', 'frek_normal', 'frek_hujan', 'frek_puncak', 'kapasitas_angkat_anjuran_ton', 'porsi_berbayar_efektif_persen'], rows)
    # ---- Tabel 7: sensitivitas satu arah
    rows = []
    for k, v in o['sens'].items():
        a = v['ALL']; ic = a['icer'].get('A')
        rows.append([k, round(a['cer'][0] / 1000, 2), round(a['cer'][1] / 1000, 2), round(a['cer'][2] / 1000, 2),
                     round(ic['icer'] / 1000, 2) if ic and ic['vs'] == 'C' else '', '/'.join(v[c]['best'] for c in CATS)])
    write('tabel07_sensitivitas.csv', ['kasus', 'cer_A', 'cer_B', 'cer_C', 'icer_A_vs_C', 'pilihan_rendah_sedang_tinggi'], rows)
    # ---- Tabel 8: alokasi optimal
    rows = [[b, round(v['cost'], 2), round(v['tons'], 2), ' '.join(v['alloc'])] for b, v in o['opt']['budgets'].items()]
    write('tabel08_alokasi_anggaran.csv', ['pagu_rp_juta', 'biaya_rp_juta', 'ton_per_tahun', 'alokasi_S01_S10'], rows)
    print('Tabel tersimpan di', os.path.abspath(OUT))


if __name__ == '__main__':
    main()
