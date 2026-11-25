# -*- coding: utf-8 -*-
"""Buat gambar-gambar naskah (PNG) dari results/results.json -> results/figures/."""
import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results', 'results.json')
OUT = os.path.join(HERE, '..', 'results', 'figures')
os.makedirs(OUT, exist_ok=True)
fams = {f.name for f in font_manager.fontManager.ttflist}
fam = next((f for f in ('Liberation Serif', 'Times New Roman', 'DejaVu Serif') if f in fams), 'serif')
plt.rcParams.update({'font.family': fam, 'font.size': 7.5, 'axes.linewidth': 0.6, 'axes.titlesize': 8, 'axes.labelsize': 7.5,
                     'legend.fontsize': 7, 'xtick.labelsize': 7, 'ytick.labelsize': 7})
COL = {'A': '#1f3864', 'B': '#8c8c8c', 'C': '#2e8b57', 'D': '#c9a227'}
HAT = {'A': '', 'B': '///', 'C': '\\\\\\', 'D': 'xxx'}
MK = {'A': 'o', 'B': 's', 'C': '^', 'D': 'D'}
SC = ['A', 'B', 'C', 'D']
CATS = ['Rendah', 'Sedang', 'Tinggi']
o = json.load(open(RES, encoding='utf8'))
rv = o['riv']


def flow():
    fig, ax = plt.subplots(figsize=(6.3, 2.55)); ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.axis('off')
    boxes = [("1. Pengumpulan data", "10 lokasi sungai Ecoton:\nlebar, aksesibilitas, biaya,\nbatas volume Min–Maks"),
             ("2. Preprocessing & eksplorasi", "statistik deskriptif, pencilan,\nkategori beban dan\nkelas kapasitas trashboom"),
             ("3. Analisis biaya-efektivitas", "biaya tahunan ekuivalen\n(diskonto), ton terangkat,\nCER, ICER, dominansi"),
             ("4. Analisis skenario", "Skenario A–D, 12 bulan\ndengan musim hujan,\n1.000 replikasi Monte Carlo"),
             ("5. Analisis sensitivitas", "satu arah, uji ambang,\nPSA dan korelasi peringkat,\noptimasi alokasi anggaran"),
             ("6. Rekomendasi", "skenario terpilih menurut\nkondisi sungai dan\nkesediaan membayar")]
    W, H = 29, 15; xs = [2, 35.5, 69]; ys = [22, 2]
    pos = [(xs[0], ys[0]), (xs[1], ys[0]), (xs[2], ys[0]), (xs[0], ys[1]), (xs[1], ys[1]), (xs[2], ys[1])]
    for (x, y), (t, d) in zip(pos, boxes):
        ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle='round,pad=0.4,rounding_size=1.5', fc='#eaf0fb', ec='#1f3864', lw=1.1))
        ax.text(x + W / 2, y + H - 3.2, t, ha='center', va='center', fontsize=8, fontweight='bold', color='#1f3864')
        ax.text(x + W / 2, y + H / 2 - 2.4, d, ha='center', va='center', fontsize=7.3)
    arr = lambda a, b: ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=9, lw=1.1, color='#1f3864'))
    arr((xs[0] + W + 0.6, ys[0] + H / 2), (xs[1] - 0.6, ys[0] + H / 2)); arr((xs[1] + W + 0.6, ys[0] + H / 2), (xs[2] - 0.6, ys[0] + H / 2))
    arr((xs[0] + W + 0.6, ys[1] + H / 2), (xs[1] - 0.6, ys[1] + H / 2)); arr((xs[1] + W + 0.6, ys[1] + H / 2), (xs[2] - 0.6, ys[1] + H / 2))
    ax.plot([xs[2] + W / 2] * 2, [ys[0] - 0.5, 19.5], color='#1f3864', lw=1.1); ax.plot([xs[2] + W / 2, xs[0] + W / 2], [19.5, 19.5], color='#1f3864', lw=1.1)
    arr((xs[0] + W / 2, 19.5), (xs[0] + W / 2, ys[1] + H + 0.6))
    fig.savefig(os.path.join(OUT, 'gambar01_alur_metodologi.png'), dpi=300, bbox_inches='tight', pad_inches=0.05); plt.close(fig)


def costvol():
    V = np.array([rv[k]['V'] for k in rv])
    fig, ax = plt.subplots(figsize=(3.3, 2.8)); xs_ = np.linspace(0, 4200, 50)
    for j, s in enumerate(SC):
        y = np.array([rv[k]['cost'][j] for k in rv]) / 1e6
        ax.scatter(V, y, s=12, marker=MK[s], color=COL[s], label=f'Skenario {s}', zorder=3)
        b, a = np.polyfit(V, y, 1)
        ax.plot(xs_, a + b * xs_, color=COL[s], lw=0.8, alpha=0.8, ls=':' if s == 'D' else '-')
    ax.set_xlabel('Volume sampah tahunan (ton)'); ax.set_ylabel('Biaya total tahunan (Rp juta)'); ax.set_xlim(0, 4200); ax.set_ylim(0, 720)
    ax.spines[['top', 'right']].set_visible(False); ax.legend(frameon=False, loc='upper left', fontsize=6.8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'gambar02_biaya_vs_volume.png'), dpi=300); plt.close(fig)


def cer():
    fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.7), gridspec_kw={'width_ratios': [2.6, 1.1]})
    x = np.arange(10); w = 0.2; ax = axs[0]
    for j, s in enumerate(SC):
        m = np.array([rv[k]['cer'][j] for k in rv]) / 1000
        lo = np.array([rv[k]['cer_lo'][j] for k in rv]) / 1000; hi = np.array([rv[k]['cer_hi'][j] for k in rv]) / 1000
        ax.bar(x + (j - 1.5) * w, m, w, yerr=[m - lo, hi - m], color=COL[s], hatch=HAT[s], edgecolor='white', linewidth=0.3,
               error_kw=dict(lw=0.5, capsize=1), label='Skenario ' + s)
    ax.axhline(500, color='black', lw=0.6, ls='--'); ax.text(-0.45, 515, 'Rp500 rb/ton', fontsize=6.5)
    ax.set_xticks(x); ax.set_xticklabels([f"{k}\n{rv[k]['cat'][:3]}." for k in rv]); ax.set_ylabel('CER (Rp ribu per ton)'); ax.set_ylim(0, 760)
    ax.set_title('(a) Per sungai (95% variasi volume)', loc='left'); ax.spines[['top', 'right']].set_visible(False)
    ax.legend(ncol=4, frameon=False, loc='upper left', fontsize=6.5)
    ax = axs[1]; xc = np.arange(3)
    for j, s in enumerate(SC):
        p = [o['psa']['res'][c]['cer_p'] for c in CATS]
        med = np.array([q[1][j] for q in p]) / 1000; lo = np.array([q[0][j] for q in p]) / 1000; hi = np.array([q[2][j] for q in p]) / 1000
        ax.bar(xc + (j - 1.5) * w, med, w, yerr=[med - lo, hi - med], color=COL[s], hatch=HAT[s], edgecolor='white', linewidth=0.3,
               error_kw=dict(lw=0.5, capsize=1))
    ax.axhline(500, color='black', lw=0.6, ls='--'); ax.set_xticks(xc); ax.set_xticklabels(CATS); ax.set_ylim(0, 900)
    ax.set_title('(b) Agregat (PSA, 95%)', loc='left'); ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'gambar03_cer.png'), dpi=300); plt.close(fig)


def ef():
    fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.7)); xc = np.arange(3); w = 0.2
    for j, s in enumerate(SC):
        axs[0].bar(xc + (j - 1.5) * w, [o['base'][c]['ef'][j] * 100 for c in CATS], w, color=COL[s], hatch=HAT[s], edgecolor='white', linewidth=0.3, label='Skenario ' + s)
        axs[1].bar(xc + (j - 1.5) * w, [o['base'][c]['lol'][j] for c in CATS], w, color=COL[s], hatch=HAT[s], edgecolor='white', linewidth=0.3)
    axs[0].axhline(75, color='black', lw=0.6, ls='--'); axs[0].set_ylim(0, 105); axs[0].set_ylabel('E$_{fisik}$ agregat (%)'); axs[0].set_title('(a) Efektivitas fisik', loc='left')
    axs[1].set_yscale('log'); axs[1].set_ylabel('Sampah lolos (ton per tahun, skala log)'); axs[1].set_title('(b) Sampah lolos ke hilir (agregat kategori)', loc='left')
    for a in axs:
        a.set_xticks(xc); a.set_xticklabels(CATS); a.set_xlabel('Kategori beban sampah'); a.spines[['top', 'right']].set_visible(False)
    h, l = axs[0].get_legend_handles_labels(); fig.legend(h, l, ncol=4, frameon=False, loc='upper center', bbox_to_anchor=(0.5, 1.0), fontsize=7)
    fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig(os.path.join(OUT, 'gambar05_efektivitas_lolos.png'), dpi=300); plt.close(fig)


def ceac():
    fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.4), sharey=True); lam = np.array(o['psa']['lam_grid']) / 1000
    for ax, c in zip(axs, CATS):
        for s in SC:
            ax.plot(lam, o['psa']['res'][c]['ceac'][s], color=COL[s], lw=1.3 if s in 'AC' else 0.8, ls='-' if s in 'AC' else ':', label='Skenario ' + s)
        ax.axvline(500, color='black', lw=0.6, ls='--'); ax.set_title(c, loc='left'); ax.set_xlabel('Kesediaan membayar (Rp ribu/ton)')
        ax.spines[['top', 'right']].set_visible(False); ax.set_ylim(0, 1.02)
    axs[0].set_ylabel('Peluang efektif biaya'); h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=4, frameon=False, loc='upper center', bbox_to_anchor=(0.5, 1.0), fontsize=7)
    fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(os.path.join(OUT, 'gambar04_ceac.png'), dpi=300); plt.close(fig)


def sens():
    fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.5), gridspec_kw={'width_ratios': [1.25, 1, 1]})
    lab = {'fb': '$f_b$', 'fk': '$f_k$', 'eta_m': '$\\eta_m$', 'leak': 'bocor', 'pR': 'relawan', 'wm': 'upah', 'cm': 'material',
           'r': 'diskonto', 'eta_v': '$\\eta_v$', 'n_rain': 'bln hujan'}
    sp = o['psa']['res']['ALL']['spearman']; names = sorted(sp, key=lambda k: abs(sp[k]['diff']))
    axs[0].barh([lab[n] for n in names], [sp[n]['diff'] for n in names], color=['#2e8b57' if sp[n]['diff'] < 0 else '#1f3864' for n in names], height=0.65)
    axs[0].axvline(0, color='black', lw=0.6); axs[0].set_xlabel('Korelasi peringkat dengan CER A − CER C'); axs[0].set_title('(a) Sensitivitas global', loc='left')
    axs[0].spines[['top', 'right']].set_visible(False)

    def series(key, xs):
        ser = {}
        for c in CATS:
            y = []
            for x_ in xs:
                e = o[key][str(x_)][c]['icer'].get('A')
                y.append(e['icer'] / 1000 if e and e['vs'] == 'C' else np.nan)
            ser[c] = y
        return ser
    prs = [0.0, 0.1, 0.2, 0.3, 0.4]; fks = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    for ax, key, xs_, xl, tt in ((axs[1], 'tip_pr', prs, 'Porsi jam kerja relawan C', '(b) Relawan'),
                                 (axs[2], 'tip_fk', fks, 'Faktor kapasitas boom ringan $f_k$', '(c) Kapasitas boom ringan')):
        ser = series(key, xs_)
        for c, mk, cl in zip(CATS, ['o', 's', '^'], ['#c9a227', '#1f3864', '#2e8b57']):
            ax.plot(xs_, ser[c], marker=mk, ms=3, lw=1, color=cl, label=c)
        ax.axhline(500, color='black', lw=0.6, ls='--'); ax.set_yscale('log'); ax.set_ylim(10, 6000); ax.set_xlabel(xl)
        ax.set_title(tt, loc='left'); ax.spines[['top', 'right']].set_visible(False)
    axs[1].set_ylabel('ICER A vs C (Rp ribu/ton)'); axs[1].legend(frameon=False, fontsize=6.5, loc='upper right')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'gambar06_sensitivitas.png'), dpi=300); plt.close(fig)


def front():
    fig, ax = plt.subplots(figsize=(3.3, 2.7))
    ax.scatter(o['opt']['all_cost'], o['opt']['all_tons'], s=1.5, color='#cfcfcf', label='Seluruh kombinasi', rasterized=True)
    ax.plot(o['opt']['front_cost'], o['opt']['front_tons'], color='#1f3864', lw=1.2, label='Batas efisien')
    ref = o['opt']['ref']
    for s in SC:
        ax.scatter(ref['all' + s][0], ref['all' + s][1], s=22, marker=MK[s], color=COL[s], zorder=4, label=f'Semua sungai {s}')
    ax.set_xlabel('Biaya total tahunan (Rp juta)'); ax.set_ylabel('Sampah terangkat (ton/tahun)'); ax.set_xlim(600, 2900); ax.set_ylim(6000, 14200)
    ax.spines[['top', 'right']].set_visible(False); ax.legend(frameon=False, fontsize=6.3, loc='center right')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'gambar07_batas_efisien.png'), dpi=300); plt.close(fig)


if __name__ == '__main__':
    for f in (flow, costvol, cer, ceac, ef, sens, front):
        f()
    print('Gambar tersimpan di', os.path.abspath(OUT))
