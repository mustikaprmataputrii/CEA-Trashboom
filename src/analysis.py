# -*- coding: utf-8 -*-
"""Analisis Monte Carlo, sensitivitas, PSA, dan optimasi alokasi anggaran (lihat subbab 2.4-2.6 naskah)."""
import numpy as np
from model import (SCN, CATS, LAMBDA_REF, params, draw_volumes, sim, pooled, group, icer_table, summarize)


def per_river(D, res, base_P):
    riv = {}
    rain = res['rain']
    for i in range(D.n):
        cm = res['cost'][:, i, :].mean(0); tm = res['tons'][:, i, :].mean(0); V = res['V'][:, i].mean()
        st, ic, fr = icer_table(cm, tm)
        nmb = LAMBDA_REF * res['tons'][:, i, :] - res['cost'][:, i, :]
        best = np.argmax(nmb, axis=1)
        share = {s: float((best == k).mean()) for k, s in enumerate(SCN)}
        opexA = res['opexA'][:, i].mean()
        ppeq = D.capex[i] / (cm[1] * (tm[0] / tm[1]) - opexA)       # persamaan 15 (tonase setara)
        ppraw = D.capex[i] / (cm[1] - opexA)                          # tanpa penyetaraan tonase
        gA = res['gA'][:, i, :]; gC = res['gC'][:, i, :]
        cer_rep = res['cost'][:, i, :] / res['tons'][:, i, :]
        riv[D.kode[i]] = dict(
            nama=D.nama[i], cat=str(D.cat[i]), akses=D.akses[i], V=float(V), cost=cm.tolist(), tons=tm.tolist(),
            cer=(cm / tm).tolist(), ef=(tm / V).tolist(), lol=(V - tm).tolist(), icer=ic, front=fr, status=st, share=share,
            ppeq=float(ppeq), ppraw=float(ppraw), eff_share=float((res['opA'][:, i, :] / res['Nact'][:, i, :]).mean()),
            fA_dry=float(np.ceil(gA[:, ~rain] / 5).mean()), fA_rain=float(np.ceil(gA[:, rain] / 5).mean()),
            fA_max=float(np.ceil(gA / 5).max(axis=1).mean()), fC_dry=float(np.ceil(gC[:, ~rain] / 5).mean()),
            fC_rain=float(np.ceil(gC[:, rain] / 5).mean()), fC_max=float(np.ceil(gC / 5).max(axis=1).mean()),
            gA_dry=float(gA[:, ~rain].mean()), gA_rain=float(gA[:, rain].mean()),
            gC_dry=float(gC[:, ~rain].mean()), gC_rain=float(gC[:, rain].mean()),
            cer_lo=np.percentile(cer_rep, 2.5, axis=0).tolist(), cer_hi=np.percentile(cer_rep, 97.5, axis=0).tolist())
    return riv


def category_extras(D, riv):
    out = {}
    for cat in CATS + ['ALL']:
        ix = group(D, cat)
        d = {k: float(np.mean([riv[D.kode[i]][k] for i in ix]))
             for k in ('fA_dry', 'fA_rain', 'fA_max', 'fC_dry', 'fC_rain', 'fC_max', 'eff_share', 'ppeq', 'ppraw')}
        d['c_rec_A'] = float(np.mean([max(riv[D.kode[i]]['gA_dry'] / 15, riv[D.kode[i]]['gA_rain'] / 30) for i in ix]))
        d['c_rec_C'] = float(np.mean([max(riv[D.kode[i]]['gC_dry'] / 15, riv[D.kode[i]]['gC_rain'] / 30) for i in ix]))
        out[cat] = d
    return out


def psa(D, n=2000, seed=7):
    rng = np.random.default_rng(seed)
    names = ['fb', 'fk', 'eta_m', 'leak', 'pR', 'wm', 'cm', 'r', 'eta_v', 'n_rain']
    lo = dict(fb=0.5, fk=0.3, eta_m=0.4, leak=0.05, pR=0.05, wm=0.8, cm=0.8, r=0.05, eta_v=0.6, n_rain=4)
    hi = dict(fb=1.0, fk=0.8, eta_m=0.8, leak=0.27, pR=0.30, wm=1.2, cm=1.2, r=0.10, eta_v=1.0, n_rain=8)
    X = np.zeros((n, len(names)))
    lam_grid = np.arange(0, 1_000_001, 20_000)
    keys = CATS + ['ALL']
    store = {c: dict(cost=np.zeros((n, 4)), tons=np.zeros((n, 4))) for c in keys}
    for k in range(n):
        P = params()
        for j, nme in enumerate(names):
            v = rng.uniform(lo[nme], hi[nme])
            if nme == 'n_rain':
                v = int(round(v))
            P[nme] = v; X[k, j] = v
        v1, u1 = draw_volumes(D, 1, rng)
        res = sim(D, P, v1, u1)
        for c in keys:
            cost, tons, _ = pooled(D, res, c)
            store[c]['cost'][k] = cost[0]; store[c]['tons'][k] = tons[0]
    rank = lambda a: np.argsort(np.argsort(a)).astype(float)
    out = {}
    for c in keys:
        cost, tons = store[c]['cost'], store[c]['tons']
        cer = cost / tons
        nmb = LAMBDA_REF * tons - cost
        pref = {s: float((np.argmax(nmb, 1) == j).mean()) for j, s in enumerate(SCN)}
        ceac = {s: [] for s in SCN}
        for lam in lam_grid:
            best = np.argmax(lam * tons - cost, 1)
            for j, s in enumerate(SCN):
                ceac[s].append(float((best == j).mean()))
        with np.errstate(divide='ignore', invalid='ignore'):
            icer_ac = (cost[:, 0] - cost[:, 2]) / (tons[:, 0] - tons[:, 2])
        icer_ac = np.where(np.isfinite(icer_ac), icer_ac, np.nan)
        ok = np.isfinite(icer_ac)
        diff = cer[:, 0] - cer[:, 2]
        sp = {nme: dict(diff=float(np.corrcoef(rank(X[:, j]), rank(diff))[0, 1]),
                        cerC=float(np.corrcoef(rank(X[:, j]), rank(cer[:, 2]))[0, 1]),
                        icer=float(np.corrcoef(rank(X[ok, j]), rank(icer_ac[ok]))[0, 1])) for j, nme in enumerate(names)}
        out[c] = dict(cer_p=[np.percentile(cer, q, axis=0).tolist() for q in (2.5, 50, 97.5)], pref=pref, ceac=ceac,
                      icer_ac_p=[float(np.nanpercentile(icer_ac, q)) for q in (2.5, 50, 97.5)], spearman=sp)
    return dict(n=n, lam_grid=lam_grid.tolist(), names=names, lo=lo, hi=hi, res=out)


def optimise(D, res):
    """Pencacahan penuh 4^10 kombinasi skenario per sungai -> batas efisien biaya-ton."""
    cm = np.array([res['cost'][:, i, :].mean(0) for i in range(D.n)])
    tm = np.array([res['tons'][:, i, :].mean(0) for i in range(D.n)])
    totc = np.zeros(1); tott = np.zeros(1)
    for i in range(D.n):
        totc = (totc[:, None] + cm[i][None, :]).ravel()
        tott = (tott[:, None] + tm[i][None, :]).ravel()
    order = np.argsort(totc)
    cs, ts = totc[order], tott[order]
    runmax = np.maximum.accumulate(ts)
    keep = np.concatenate([[True], runmax[1:] > runmax[:-1] + 1e-9])
    def decode(idx):
        digs = []
        for _ in range(D.n):
            digs.append(idx % 4); idx //= 4
        return digs[::-1]
    budgets = {}
    for B in (760e6, 800e6, 850e6, 900e6, 934e6):
        feas = np.where(totc <= B)[0]
        if feas.size:
            j = feas[np.argmax(tott[feas])]
            budgets[str(int(B / 1e6))] = dict(cost=float(totc[j] / 1e6), tons=float(tott[j]), alloc=[SCN[k] for k in decode(int(j))])
    ref = {f'all{s}': [float(cm[:, k].sum() / 1e6), float(tm[:, k].sum())] for k, s in enumerate(SCN)}
    return dict(n_combos=int(totc.size), front_cost=(cs[keep] / 1e6).tolist(), front_tons=ts[keep].tolist(),
                all_cost=(totc[::997] / 1e6).tolist(), all_tons=tott[::997].tolist(), budgets=budgets, ref=ref,
                nmb_alloc=[SCN[int(np.argmax(LAMBDA_REF * tm[i] - cm[i]))] for i in range(D.n)])


def run_all(D, R=1000, seed=2026, n_psa=2000, psa_seed=7):
    rng = np.random.default_rng(seed)
    VN, U = draw_volumes(D, R, rng)
    P0 = params()
    base = sim(D, P0, VN, U)
    out = {'meta': dict(R=R, seed=seed, lam=LAMBDA_REF, n_psa=n_psa, psa_seed=psa_seed)}
    out['verif'] = dict(volume_normal_rerata_vs_analitik=float(np.abs(VN.mean(axis=(0, 2)) / ((D.minv + D.maxv) / 2) - 1).max()),
                        tons_melebihi_volume=float((base['tons'] - base['V'][:, :, None]).max()),
                        tons_negatif=float(base['tons'].min()), n_pengamatan=int(R * D.n * 12))
    out['base'] = summarize(D, base)
    out['riv'] = per_river(D, base, P0)
    out['catx'] = category_extras(D, out['riv'])

    def variant(**kw):
        return summarize(D, sim(D, params(**kw), VN, U))
    acc = {'Mudah': 1.0, 'Sedang': 1.25, 'Sulit': 1.5}
    cases = {'Dasar': {}, 'Upah +20%': dict(wm=1.2), 'Material −20%': dict(cm=0.8), 'Diskonto 5%': dict(r=0.05),
             'Diskonto 10%': dict(r=0.10), 'Nilai sisa 20%': dict(S=0.2), 'Kebocoran 27%': dict(leak=0.269),
             'Efisiensi relawan 60%': dict(eta_v=0.6), 'Tanpa pembulatan': dict(rnd=False),
             'Akses berbobot': dict(g=np.array([acc[a] for a in D.akses])), 'Hujan 4 bulan': dict(n_rain=4), 'Hujan 8 bulan': dict(n_rain=8)}
    out['sens'] = {k: variant(**v) for k, v in cases.items()}
    out['tip_fb'] = {str(round(f, 2)): variant(fb=float(f)) for f in np.arange(0.5, 1.0001, 0.05)}
    out['tip_fk'] = {str(round(f, 2)): variant(fk=float(f)) for f in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)}
    out['tip_pr'] = {str(round(p, 2)): variant(pR=float(p)) for p in (0.0, 0.1, 0.2, 0.3, 0.4)}
    out['psa'] = psa(D, n_psa, psa_seed)
    out['opt'] = optimise(D, base)
    out['desc'] = dict(lebar=D.lebar.tolist(), capex=(D.capex / 1e6).tolist(), maint=(D.maint / 1e6).tolist(),
                       wage=(D.wage / 1e6).tolist(), trans=(D.trans / 1e6).tolist(), vol=((D.minv + D.maxv) / 2).tolist(),
                       minv=D.minv.tolist(), maxv=D.maxv.tolist(), ctb=D.ctb.tolist(),
                       r_lebar_capex=float(np.corrcoef(D.lebar, D.capex)[0, 1]))
    return out
