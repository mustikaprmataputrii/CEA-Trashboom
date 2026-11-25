# -*- coding: utf-8 -*-
"""Uji sederhana. Jalankan:  python -m pytest -q   (atau:  python tests/test_model.py)"""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from model import default_data, params, draw_volumes, sim, summarize, icer_table, pooled


def _run(R=200, seed=2026, **kw):
    D = default_data()
    VN, U = draw_volumes(D, R, np.random.default_rng(seed))
    return D, VN, U, sim(D, params(**kw), VN, U)


def test_kategori_dan_kapasitas():
    D = default_data()
    assert list(D.cat) == ['Sedang', 'Sedang', 'Tinggi', 'Tinggi', 'Rendah', 'Tinggi', 'Rendah', 'Sedang', 'Sedang', 'Rendah']
    assert set(D.ctb) == {45.0, 150.0, 300.0}


def test_neraca_massa():
    D, VN, U, res = _run()
    assert (res['tons'] <= res['V'][:, :, None] + 1e-9).all()      # terangkat tidak melebihi volume
    assert (res['tons'] >= 0).all()


def test_volume_normal_sesuai_rentang():
    D, VN, U, _ = _run()
    assert (VN.min(axis=(0, 2)) >= D.minv).all() and (VN.max(axis=(0, 2)) <= D.maxv).all()
    assert ((U >= 50) & (U <= 80)).all()


def test_reproduksibel():
    a = _run(R=50)[3]['cost']; b = _run(R=50)[3]['cost']
    assert np.array_equal(a, b)


def test_manual_didominasi():
    D, VN, U, res = _run(R=300)
    s = summarize(D, res)
    for c in ('Rendah', 'Sedang', 'Tinggi', 'ALL'):
        assert s[c]['status']['B'].startswith('didominasi') and s[c]['status']['D'].startswith('didominasi')


def test_icer_logika():
    cm = np.array([100.0, 300.0, 80.0, 400.0]); tm = np.array([900.0, 500.0, 700.0, 600.0])
    status, ic, front = icer_table(cm, tm)
    assert front == ['C', 'A'] and abs(ic['A']['icer'] - 0.1) < 1e-9


def test_diskonto_menaikkan_biaya_modal():
    D, VN, U, r1 = _run(R=50, r=0.0)
    r2 = _run(R=50, r=0.10)[3]
    assert (r2['cost'][:, :, 0] > r1['cost'][:, :, 0]).all()


if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'):
            f(); print('OK', n)
