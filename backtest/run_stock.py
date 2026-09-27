"""Stocks vs crypto: ST01 (MA crossover) and ST02 (Turtle) against buy and hold. Rules: ../strategies/*.md (frozen before running)."""
import glob, os, json, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
rng = np.random.default_rng(4)
CUT = 0.7

def load_stock(f):
    d = pd.read_csv(f); d['dt'] = pd.to_datetime(d.dt).dt.tz_localize(None); return d.set_index('dt')[['o', 'h', 'l', 'c']]
def load_crypto(f):
    d = pd.read_csv(f); d['dt'] = pd.to_datetime(d.t, unit='ms'); return d.set_index('dt')[['o', 'h', 'l', 'c']]

def sim_entries(d, entries, cost):
    """entries: list of (entry_idx, exit_idx) using open prices; returns daily return series and trade list."""
    o, c = d.o.values, d.c.values; N = len(d); ret = np.zeros(N); tr = []
    for ei, xi, xp in entries:
        prev = o[ei]
        for k in range(ei, xi + 1):
            px = xp if k == xi else c[k]
            ret[k] += px / prev - 1; prev = c[k]
        ret[ei] -= cost; ret[xi] -= cost
        tr.append(dict(entry=d.index[ei], exit=d.index[xi], pct=xp / o[ei] - 1 - 2 * cost, days=xi - ei + 1))
    return pd.Series(ret, index=d.index), tr

def ma_cross(d, fast, slow, cost):
    c, o = d.c.values, d.o.values; N = len(d)
    f = d.c.rolling(fast).mean().values; s = d.c.rolling(slow).mean().values
    up = (f > s) & (np.roll(f, 1) <= np.roll(s, 1)); dn = (f < s) & (np.roll(f, 1) >= np.roll(s, 1))
    ent = []; pos = False; ei = 0
    for i in range(slow + 1, N - 1):
        if not pos and up[i]: pos = True; ei = i + 1
        elif pos and dn[i]: ent.append((ei, i + 1, o[i + 1])); pos = False
    if pos: ent.append((ei, N - 1, c[N - 1]))
    return sim_entries(d, ent, cost)

def turtle(d, ent_n, ex_n, cost):
    hi = d.h.rolling(ent_n).max().shift(1).values; lo = d.l.rolling(ex_n).min().shift(1).values
    tr_ = np.maximum(d.h - d.l, np.maximum((d.h - d.c.shift()).abs(), (d.l - d.c.shift()).abs())); a = tr_.rolling(20).mean().values
    o, h, l, c = d.o.values, d.h.values, d.l.values, d.c.values; N = len(d); ent = []; i = ent_n + 1
    while i < N - 1:
        if c[i] > hi[i] and not np.isnan(a[i]):
            ei = i + 1; stop = o[ei] - 2 * a[i]; j = ei; xp = c[-1]; xi = N - 1
            while j < N:
                if l[j] <= stop: xp = min(stop, o[j]) if j > ei else stop; xi = j; break
                if j > ei and c[j - 1] < lo[j - 1]: xp = o[j]; xi = j; break
                if j == N - 1: xp = c[j]; xi = j; break
                j += 1
            ent.append((ei, xi, xp)); i = xi
        i += 1
    return sim_entries(d, ent, cost)

def stats(r):
    r = r.dropna()
    if len(r) < 60: return dict(ann=np.nan, dd=np.nan, sharpe=np.nan, calmar=np.nan)
    eq = (1 + r).cumprod(); dd = (eq / eq.cummax() - 1).min(); yrs = len(r) / 252
    ann = eq.iloc[-1] ** (1 / yrs) - 1
    return dict(ann=ann * 100, dd=dd * 100, sharpe=r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan, calmar=ann / abs(dd) if dd < 0 else np.nan)

def evaluate(name, D, fn, days_per_year, cost, label):
    R = {}; BH = {}; rows = []; percalmar = []
    for s, d in D.items():
        r, t = fn(d, cost); R[s] = r; BH[s] = d.c.pct_change().fillna(0)
        cut = d.index[int(CUT * len(d))]
        for x in t: rows.append(dict(sym=s, split='OOS' if x['entry'] >= cut else 'IS', **x))
        a = stats(r.loc[cut:]); b = stats(BH[s].loc[cut:])
        if not np.isnan(a['calmar']) and not np.isnan(b['calmar']): percalmar.append((s, a['calmar'], b['calmar'], a['ann'], b['ann'], a['dd'], b['dd']))
    R = pd.DataFrame(R); B = pd.DataFrame(BH)
    port = R.mean(axis=1).dropna(); bhp = B.mean(axis=1).dropna(); split = port.index[int(CUT * len(port))]
    T = pd.DataFrame(rows); oo = T[T.split == 'OOS']
    a = stats(port.loc[split:]); b = stats(bhp.loc[split:]); ai = stats(port.loc[:split]); bi = stats(bhp.loc[:split])
    # random baseline: same hold lengths, random OOS entries on the same asset
    sims = []
    for _ in range(300):
        tot = []
        for _, t in oo.iterrows():
            d = D[t.sym]; N = len(d); c0 = int(CUT * N); L = int(t.days)
            if N - c0 - L - 2 <= 0: continue
            i = rng.integers(c0, N - L - 1); tot.append(d.c.values[i + L] / d.o.values[i + 1] - 1 - 2 * cost)
        sims.append(np.mean(tot))
    sims = np.array(sims); m = oo.pct.mean() if len(oo) else np.nan
    pc = pd.DataFrame(percalmar, columns='sym cal_strat cal_bh ann_s ann_b dd_s dd_b'.split())
    beat = (pc.cal_strat > pc.cal_bh).mean() * 100 if len(pc) else np.nan
    print(f'\n[{label}] {name}: {len(D)} assets, portfolio split {split.date()}')
    print(f'  OUT-OF-SAMPLE  strategy: ann {a["ann"]:6.1f}%  maxDD {a["dd"]:6.1f}%  Sharpe {a["sharpe"]:.2f}  Calmar {a["calmar"]:.2f}   |  buy&hold EW: ann {b["ann"]:6.1f}%  maxDD {b["dd"]:6.1f}%  Sharpe {b["sharpe"]:.2f}  Calmar {b["calmar"]:.2f}')
    print(f'  IN-SAMPLE      strategy: ann {ai["ann"]:6.1f}%  maxDD {ai["dd"]:6.1f}%  Sharpe {ai["sharpe"]:.2f}  Calmar {ai["calmar"]:.2f}   |  buy&hold EW: ann {bi["ann"]:6.1f}%  maxDD {bi["dd"]:6.1f}%  Sharpe {bi["sharpe"]:.2f}  Calmar {bi["calmar"]:.2f}')
    print(f'  OOS trades {len(oo)}  win {(oo.pct > 0).mean() * 100:.0f}%  avg/trade {m * 100:+.2f}%  vs random same-length {np.nanmean(sims) * 100:+.2f}% (beats {np.mean(sims < m) * 100:.0f}% of draws)  | assets where strategy Calmar > buy&hold: {beat:.0f}% of {len(pc)}')
    return dict(label=label, name=name, ann_s=a['ann'], dd_s=a['dd'], cal_s=a['calmar'], ann_b=b['ann'], dd_b=b['dd'], cal_b=b['calmar'], trades=len(oo), avg=m * 100, rand=np.nanmean(sims) * 100, beats_rand=np.mean(sims < m) * 100, assets_beat=beat)

if __name__ == '__main__':
    stocks = {os.path.basename(f).split('_')[0]: load_stock(f) for f in glob.glob('../data/*_1d.csv')}
    etfs = {k: stocks.pop(k) for k in ('SPY', 'QQQ', 'IWM')}
    crypto = {}
    for f in glob.glob('../../strategy_lab/backtest/data/*_1d.csv'):
        s = os.path.basename(f).split('_')[0]
        if s != 'XAUUSDT': crypto[s] = load_crypto(f)
    print(f'{len(stocks)} stocks, {len(etfs)} ETFs, {len(crypto)} crypto coins')
    out = []
    strategies = [('ST01-A MA 20/50 (video)', lambda d, c: ma_cross(d, 20, 50, c)), ('ST01-B MA 50/200', lambda d, c: ma_cross(d, 50, 200, c)), ('ST01-C MA 10/30', lambda d, c: ma_cross(d, 10, 30, c)),
                  ('ST02-A Turtle 20/10', lambda d, c: turtle(d, 20, 10, c)), ('ST02-B Turtle 55/20', lambda d, c: turtle(d, 55, 20, c))]
    for name, fn in strategies:
        out.append(evaluate(name, stocks, fn, 252, 0.0005, 'STOCKS'))
        out.append(evaluate(name, etfs, fn, 252, 0.0005, 'ETFs  '))
        out.append(evaluate(name, crypto, fn, 365, 0.0007, 'CRYPTO'))
    pd.DataFrame(out).to_csv('../results/summary.csv', index=False)
