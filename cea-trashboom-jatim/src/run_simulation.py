# -*- coding: utf-8 -*-
"""Jalankan seluruh simulasi dan simpan ke results/results.json.
Contoh:  python src/run_simulation.py            (R = 1.000, PSA = 2.000, benih 2026)
         python src/run_simulation.py --R 200 --psa 300   (uji cepat)
"""
import argparse
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import default_data
from analysis import run_all


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--R', type=int, default=1000, help='jumlah replikasi Monte Carlo')
    ap.add_argument('--psa', type=int, default=2000, help='jumlah undian PSA')
    ap.add_argument('--seed', type=int, default=2026)
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results', 'results.json'))
    a = ap.parse_args()
    out = run_all(default_data(), R=a.R, seed=a.seed, n_psa=a.psa)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, 'w', encoding='utf8') as f:
        json.dump(out, f)
    for c in ('Rendah', 'Sedang', 'Tinggi', 'ALL'):
        b = out['base'][c]
        print(c, 'CER (Rp ribu/ton):', [round(x / 1000, 1) for x in b['cer']], '| pilihan NMB:', b['best'])
    print('Tersimpan:', os.path.abspath(a.out))


if __name__ == '__main__':
    main()
