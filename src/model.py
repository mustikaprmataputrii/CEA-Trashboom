# -*- coding: utf-8 -*-
"""Model simulasi analisis efektivitas biaya (CEA) trashboom dan relawan di sungai Jawa Timur.

Skenario:  A = trashboom stasioner;  B = manual (tenaga tetap sesuai volume normal);
           C = trashboom ringan + relawan;  D = manual intensif (tenaga mengikuti volume aktual).
Lonjakan musim hujan berlaku untuk SEMUA skenario. Biaya modal memakai faktor pemulihan modal (diskonto).
Bentuk array simulasi: (replikasi, sungai, bulan).
"""
import csv
import os
import numpy as np

SCN = ['A', 'B', 'C', 'D']
CATS = ['Rendah', 'Sedang', 'Tinggi']
CAPCLASS = {'Rendah': 45.0, 'Sedang': 150.0, 'Tinggi': 300.0}     # kelas kapasitas trashboom (ton/bulan)
WAGE_FRACTION = 0.1906                                            # upah = 19,06% dari UMK (asumsi penulis)
RAIN_ORDER = [0, 1, 11, 2, 10, 3, 9, 4]                           # prioritas bulan hujan: Jan, Feb, Des, Mar, Nov, Apr, Okt, Mei
LAMBDA_REF = 500_000.0                                            # kesediaan membayar acuan (Rp/ton)

BASE = dict(r=0.08, L=5, S=0.0, eta_m=0.60, leak=0.10, fk=0.50, fb=0.70, pA=0.10, pC=0.10, pR=0.20,
            prod=7.5, d=4.0, eta_v=1.0, wm=1.0, cm=1.0, rnd=True, n_rain=6, g=None)


class Data:
    """Parameter sepuluh sungai, dibaca dari data/parameter_sungai.csv."""

    def __init__(self, path):
        with open(path, encoding='utf8') as f:
            rows = list(csv.DictReader(f))
        self.kode = [r['kode'] for r in rows]
        self.nama = [r['nama'] for r in rows]
        self.wilayah = [r['wilayah'] for r in rows]
        self.akses = [r['akses'] for r in rows]
        self.lebar = np.array([float(r['lebar_m']) for r in rows])
        self.capex = np.array([float(r['capex_rp']) for r in rows])
        self.maint = np.array([float(r['perawatan_rp_per_bulan']) for r in rows])
        self.umk = np.array([float(r['umk_rp_per_bulan']) for r in rows])
        self.wage = self.umk * WAGE_FRACTION
        self.trans = np.array([float(r['transport_rp_per_hari']) for r in rows])
        self.minv = np.array([int(r['vol_min_ton_bulan']) for r in rows])
        self.maxv = np.array([int(r['vol_max_ton_bulan']) for r in rows])
        mid = (self.minv + self.maxv) / 2 / 30
        self.cat = np.array(['Rendah' if x < 1 else ('Sedang' if x <= 5 else 'Tinggi') for x in mid])
        self.ctb = np.array([CAPCLASS[c] for c in self.cat])
        self.n = len(self.kode)


def default_data():
    here = os.path.dirname(os.path.abspath(__file__))
    return Data(os.path.join(here, '..', 'data', 'parameter_sungai.csv'))


def params(**kw):
    P = dict(BASE)
    P.update(kw)
    return P


def rainmask(n):
    m = np.zeros(12, bool)
    m[RAIN_ORDER[:n]] = True
    return m


def draw_volumes(D, R, rng):
    """Volume normal acak seragam (padanan =RANDBETWEEN) dan lonjakan hujan u acak 50-80."""
    VN = rng.integers(D.minv[None, :, None], D.maxv[None, :, None] + 1, size=(R, D.n, 12)).astype(float)
    U = rng.integers(50, 81, size=(R, D.n, 12)).astype(float)
    return VN, U


def sim(D, P, VN, U):
    """Biaya tahunan dan ton terangkat bersih untuk skenario A-D (persamaan 1-11 pada naskah)."""
    g = np.ones(D.n) if P['g'] is None else P['g']
    rain = rainmask(P['n_rain'])[None, None, :]
    V = VN * (1 + U / 100.0 * rain)                                   # persamaan 2
    prod, leak = P['prod'], P['leak']
    ceil = np.ceil if P['rnd'] else (lambda x: x)
    K = (D.capex * P['cm'])[None, :, None]
    crf = P['r'] / (1 - (1 + P['r']) ** (-P['L'])) if P['r'] > 0 else 1.0 / P['L']
    Keq = (K - P['S'] * K / (1 + P['r']) ** P['L']) * crf             # persamaan 7
    capm = Keq / 12.0
    m = D.maint[None, :, None]
    w = (D.wage * P['wm'])[None, :, None]
    c = (D.trans * g)[None, :, None]
    d = P['d']
    Ctb = D.ctb[None, :, None]
    Nplan = ceil(VN / prod)
    Nact = ceil(V / prod)                                              # persamaan 3
    tB = P['eta_m'] * np.minimum(V, Nplan * prod); cB = Nplan * w + c * d                 # persamaan 6 dan 8
    tD = P['eta_m'] * np.minimum(V, Nact * prod); cD = Nact * w + c * d
    gA = np.minimum(V, Ctb); lolA = (V - gA) + leak * gA; tA = V - lolA                   # persamaan 4
    opA = ceil(P['pA'] * Nact)
    opexA = m + opA * w + P['pA'] * c * d; cA = capm + opexA                              # persamaan 9
    vb = np.minimum(V, P['fk'] * Ctb)                                                     # persamaan 5
    Rr = ceil(P['pR'] * Nact)
    vv = np.minimum(V - vb, Rr * prod)
    tC = (1 - leak) * vb + P['eta_v'] * vv
    opC = ceil(P['pC'] * Nact)
    cC = P['fb'] * (capm + m) + opC * w + P['pC'] * c * d                                 # persamaan 10
    cost = np.stack([cA, cB, cC, cD], -1).sum(2)
    tons = np.stack([tA, tB, tC, tD], -1).sum(2)
    return dict(cost=cost, tons=tons, V=V.sum(2), opexA=opexA.sum(2), gA=gA, gC=vb, V12=V, opA=opA, Nact=Nact,
                rain=rain[0, 0])


def group(D, cat):
    return [i for i in range(D.n) if cat == 'ALL' or D.cat[i] == cat]


def pooled(D, res, cat):
    """Agregat sekelompok sungai: biaya (R,4), ton (R,4), volume (R,)."""
    ix = group(D, cat)
    return res['cost'][:, ix, :].sum(1), res['tons'][:, ix, :].sum(1), res['V'][:, ix].sum(1)


def icer_table(cm, tm):
    """Dominansi, dominansi diperluas, dan ICER dari rerata biaya (cm) dan ton (tm) tiap skenario."""
    order = np.argsort(cm)
    status, keep = {}, []
    for j in order:
        dom = any(cm[k] <= cm[j] and tm[k] >= tm[j] and (cm[k] < cm[j] or tm[k] > tm[j]) for k in range(4) if k != j)
        status[SCN[j]] = 'didominasi' if dom else 'tak-didominasi'
        if not dom:
            keep.append(j)
    changed = True
    while changed and len(keep) > 2:
        changed = False
        ic = [(cm[keep[i + 1]] - cm[keep[i]]) / (tm[keep[i + 1]] - tm[keep[i]]) for i in range(len(keep) - 1)]
        for i in range(len(ic) - 1):
            if ic[i] > ic[i + 1]:
                status[SCN[keep[i + 1]]] = 'didominasi-diperluas'
                keep.pop(i + 1)
                changed = True
                break
    out = {}
    for i in range(1, len(keep)):
        j0, j1 = keep[i - 1], keep[i]
        out[SCN[j1]] = dict(vs=SCN[j0], dC=float(cm[j1] - cm[j0]), dT=float(tm[j1] - tm[j0]),
                            icer=float((cm[j1] - cm[j0]) / (tm[j1] - tm[j0])))
    return status, out, [SCN[k] for k in keep]


def summarize(D, res, lam=LAMBDA_REF):
    """Ringkasan agregat per kategori: rerata, simpangan baku antarreplikasi, CER, ICER, dominansi, pilihan NMB."""
    out = {}
    for cat in CATS + ['ALL']:
        cost, tons, V = pooled(D, res, cat)
        cm, tm = cost.mean(0), tons.mean(0)
        status, ic, front = icer_table(cm, tm)
        cer_rep = cost / tons
        eb_rep = (cost[:, 1:2] - cost) / cost[:, 1:2]
        nmb = lam * tm - cm
        out[cat] = dict(cost=cm.tolist(), tons=tm.tolist(), V=float(V.mean()), cer=(cm / tm).tolist(),
                        ef=(tm / V.mean()).tolist(), lol=(V.mean() - tm).tolist(), status=status, icer=ic, front=front,
                        best=SCN[int(np.argmax(nmb))], eb=((cm[1] - cm) / cm[1]).tolist(),
                        cost_sd=cost.std(0).tolist(), tons_sd=tons.std(0).tolist(),
                        cer_sd=cer_rep.std(0).tolist(), eb_sd=eb_rep.std(0).tolist())
    return out
