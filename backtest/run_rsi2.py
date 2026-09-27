"""ST06 RSI(2) mean reversion. Rules: ../strategies/ST06_rsi2_mean_reversion.md (frozen before running)."""
import glob, os, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
rng = np.random.default_rng(21); COST = 0.0005; CUT = 0.7

def load(f):
    d = pd.read_csv(f)
    if 'dt' in d.columns:
        d['dt'] = pd.to_datetime(d.dt).dt.tz_localize(None); return d.set_index('dt')[['o', 'h', 'l', 'c']]
    d['dt'] = pd.to_datetime(d.t, unit='ms'); return d.set_index('dt')[['o', 'h', 'l', 'c']]

def rsi2(c, n=2):
    d = c.diff(); up = d.clip(lower=0); dn = -d.clip(upper=0)
    ru = up.ewm(alpha=1 / n, adjust=False).mean(); rd = dn.ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + ru / rd.replace(0, np.nan))

def trades_for(d, entry_th, exit_th, use_ma, hold, stop_pct):
    c, o, h, l = d.c, d.o, d.h, d.l; r = rsi2(c); ma = c.rolling(200).mean()
    N = len(d); ent = []; i = 205
    while i < N - 1:
        ok = (r.iloc[i] < entry_th) and (not use_ma or c.iloc[i] > ma.iloc[i])
        if ok:
            ei = i + 1; entry = o.iloc[ei]; stop = entry * (1 - stop_pct) if stop_pct else -1
            xp = c.iloc[-1]; xi = N - 1
            for j in range(ei, min(ei + hold, N - 1) + 1):
                if stop_pct and l.iloc[j] <= stop: xp = min(stop, o.iloc[j]) if j > ei else stop; xi = j; break
                if j > ei and r.iloc[j - 1] > exit_th: xp = o.iloc[j]; xi = j; break
                if j == min(ei + hold, N - 1): xp = o.iloc[min(j + 1, N - 1)] if j + 1 < N else c.iloc[j]; xi = min(j + 1, N - 1); break
            ent.append((ei, xi, xp)); i = xi
        i += 1
    ret = np.zeros(N); tr = []
    for ei, xi, xp in ent:
        prev = o.iloc[ei]
        for k in range(ei, xi + 1):
            px = xp if k == xi else c.iloc[k]; ret[k] += px / prev - 1; prev = c.iloc[k]
        ret[ei] -= COST; ret[xi] -= COST
        tr.append(dict(entry=d.index[ei], exit=d.index[xi], pct=xp / o.iloc[ei] - 1 - 2 * COST, days=xi - ei + 1))
    return pd.Series(ret, index=d.index), tr

def stats(r):
    r = r.dropna()
    if len(r) < 60: return dict(ann=np.nan, dd=np.nan, sharpe=np.nan, calmar=np.nan)
    eq = (1 + r).cumprod(); dd = (eq / eq.cummax() - 1).min(); yrs = len(r) / 252
    ann = eq.iloc[-1] ** (1 / yrs) - 1
    return dict(ann=ann * 100, dd=dd * 100, sharpe=r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan, calmar=ann / abs(dd) if dd < 0 else np.nan)

def evaluate(name, D, entry_th, exit_th, use_ma, hold, stop_pct, label):
    R = {}; BH = {}; rows = []; pc = []
    for s, d in D.items():
        r, t = trades_for(d, entry_th, exit_th, use_ma, hold, stop_pct); R[s] = r; BH[s] = d.c.pct_change().fillna(0)
        cut = d.index[int(CUT * len(d))]
        for x in t: rows.append(dict(sym=s, split='OOS' if x['entry'] >= cut else 'IS', **x))
        a = stats(r.loc[cut:]); b = stats(BH[s].loc[cut:])
        if not np.isnan(a['calmar']) and not np.isnan(b['calmar']): pc.append((a['calmar'] > b['calmar']))
    R = pd.DataFrame(R); B = pd.DataFrame(BH)
    port = R.mean(axis=1).dropna(); bhp = B.mean(axis=1).dropna(); split = port.index[int(CUT * len(port))]
    T = pd.DataFrame(rows); oo = T[T.split == 'OOS'] if len(T) else T
    a = stats(port.loc[split:]); b = stats(bhp.loc[split:]); ai = stats(port.loc[:split]); bi = stats(bhp.loc[:split])
    sims = []
    for _ in range(300):
        tot = []
        for _, t in oo.iterrows():
            d = D[t.sym]; N = len(d); c0 = int(CUT * N); L = int(t.days)
            if N - c0 - L - 2 <= 0: continue
            i = rng.integers(c0, N - L - 1); tot.append(d.c.values[i + L] / d.o.values[i + 1] - 1 - 2 * COST)
        sims.append(np.mean(tot) if tot else np.nan)
    sims = np.array(sims); m = oo.pct.mean() if len(oo) else np.nan
    print(f'\n[{label}] {name}: split {split.date()}')
    print(f'  OOS strategy: ann {a["ann"]:5.1f}% DD {a["dd"]:6.1f}% Sharpe {a["sharpe"]:.2f} Calmar {a["calmar"]:.2f}  || buy&hold: ann {b["ann"]:5.1f}% DD {b["dd"]:6.1f}% Sharpe {b["sharpe"]:.2f} Calmar {b["calmar"]:.2f}')
    print(f'  IS  strategy: ann {ai["ann"]:5.1f}% DD {ai["dd"]:6.1f}% Sharpe {ai["sharpe"]:.2f} Calmar {ai["calmar"]:.2f}  || buy&hold: ann {bi["ann"]:5.1f}% DD {bi["dd"]:6.1f}% Sharpe {bi["sharpe"]:.2f} Calmar {bi["calmar"]:.2f}')
    print(f'  OOS trades {len(oo)} win {(oo.pct > 0).mean() * 100:.0f}% avg/trade {m * 100:+.2f}% vs random {np.nanmean(sims) * 100:+.2f}% (beats {np.mean(sims < m) * 100:.0f}% of draws) | assets beating B&H Calmar: {np.mean(pc) * 100:.0f}% of {len(pc)}')

if __name__ == '__main__':
    stocks = {os.path.basename(f).split('_')[0]: load(f) for f in glob.glob('../data/*_1d.csv')}
    etfs = {k: stocks.pop(k) for k in ('SPY', 'QQQ', 'IWM') if k in stocks}
    for k in list(stocks):
        if len(stocks[k]) < 500: stocks.pop(k)
    print(f'{len(stocks)} stocks, {len(etfs)} ETFs')
    for name, entry, exit_, ma, hold, stop in [
        ('ST06-A RSI2<10/>70, 200MA filter', 10, 70, True, 10, 0),
        ('ST06-B RSI2<5/>75, 200MA filter', 5, 75, True, 10, 0),
        ('ST06-C RSI2<10/>70, no 200MA filter', 10, 70, False, 10, 0),
        ('ST06-D RSI2<10/>70, 200MA, 3% stop', 10, 70, True, 10, 0.03),
    ]:
        evaluate(name, stocks, entry, exit_, ma, hold, stop, 'STOCKS')
        evaluate(name, etfs, entry, exit_, ma, hold, stop, 'ETFs  ')
