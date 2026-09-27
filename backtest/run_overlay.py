"""ST07 RSI(2) overlay on a permanent core holding. Rules: ../strategies/ST07_rsi2_overlay.md (frozen before running)."""
import glob, os, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
COST = 0.0005; CUT = 0.7

def load(f):
    d = pd.read_csv(f); d['dt'] = pd.to_datetime(d.dt).dt.tz_localize(None); return d.set_index('dt')[['o', 'h', 'l', 'c']]

def rsi2(c, n=2):
    d = c.diff(); up = d.clip(lower=0); dn = -d.clip(upper=0)
    ru = up.ewm(alpha=1 / n, adjust=False).mean(); rd = dn.ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + ru / rd.replace(0, np.nan))

def weight_series(d, boost):
    """Decide the weight to hold FOR tomorrow using only information known at today's close (index i). Returned series
    is already shifted: w[i] is the weight applied to day i's return, decided at day i-1's close. No look-ahead."""
    c = d.c; r = rsi2(c); ma = c.rolling(200).mean(); N = len(d)
    base = np.where(c.values > ma.values, 1.0, 0.5); base[np.isnan(ma.values)] = 1.0   # decided at close i, using data through i
    decided = base.copy(); overlay_on = False
    for i in range(205, N):
        if overlay_on:
            decided[i] = boost
            if r.iloc[i] > 70 or base[i] == 0.5: overlay_on = False
        elif r.iloc[i] < 10 and base[i] == 1.0:
            overlay_on = True; decided[i] = boost
    applied = np.empty(N); applied[0] = base[0]; applied[1:] = decided[:-1]   # shift: today's exposure = yesterday's decision
    return pd.Series(applied, index=d.index)

def port_return(d, w):
    ret = d.c.pct_change().fillna(0)
    turn = w.diff().abs().fillna(w.iloc[0])
    return ret * w - turn * COST

def stats(r):
    r = r.dropna()
    if len(r) < 60: return dict(ann=np.nan, dd=np.nan, sharpe=np.nan, calmar=np.nan)
    eq = (1 + r).cumprod(); dd = (eq / eq.cummax() - 1).min(); yrs = len(r) / 252
    ann = eq.iloc[-1] ** (1 / yrs) - 1
    return dict(ann=ann * 100, dd=dd * 100, sharpe=r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan, calmar=ann / abs(dd) if dd < 0 else np.nan)

def evaluate(name, D, boost, label):
    R = {}; BH = {}; pc = []; dd_imp = []
    for s, d in D.items():
        w = weight_series(d, boost); R[s] = port_return(d, w); BH[s] = d.c.pct_change().fillna(0)
        cut = d.index[int(CUT * len(d))]
        a = stats(R[s].loc[cut:]); b = stats(BH[s].loc[cut:])
        if not np.isnan(a['calmar']) and not np.isnan(b['calmar']): pc.append(a['calmar'] > b['calmar']); dd_imp.append(a['dd'] > b['dd'])
    R = pd.DataFrame(R); B = pd.DataFrame(BH)
    port = R.mean(axis=1).dropna(); bhp = B.mean(axis=1).dropna(); split = port.index[int(CUT * len(port))]
    a = stats(port.loc[split:]); b = stats(bhp.loc[split:]); ai = stats(port.loc[:split]); bi = stats(bhp.loc[:split])
    print(f'\n[{label}] {name}: split {split.date()}')
    print(f'  OOS overlay: ann {a["ann"]:5.1f}% DD {a["dd"]:6.1f}% Sharpe {a["sharpe"]:.2f} Calmar {a["calmar"]:.2f}  || buy&hold: ann {b["ann"]:5.1f}% DD {b["dd"]:6.1f}% Sharpe {b["sharpe"]:.2f} Calmar {b["calmar"]:.2f}   (gap {a["ann"]-b["ann"]:+.1f}pp)')
    print(f'  IS  overlay: ann {ai["ann"]:5.1f}% DD {ai["dd"]:6.1f}% Sharpe {ai["sharpe"]:.2f} Calmar {ai["calmar"]:.2f}  || buy&hold: ann {bi["ann"]:5.1f}% DD {bi["dd"]:6.1f}% Sharpe {bi["sharpe"]:.2f} Calmar {bi["calmar"]:.2f}')
    print(f'  assets with better Calmar: {np.mean(pc) * 100:.0f}% of {len(pc)}  |  assets with smaller drawdown: {np.mean(dd_imp) * 100:.0f}% of {len(dd_imp)}')
    return dict(name=name, label=label, ann=a['ann'], dd=a['dd'], calmar=a['calmar'], ann_b=b['ann'], dd_b=b['dd'], calmar_b=b['calmar'], gap=a['ann'] - b['ann'], pct_beat_calmar=np.mean(pc) * 100, pct_beat_dd=np.mean(dd_imp) * 100)

if __name__ == '__main__':
    stocks = {os.path.basename(f).split('_')[0]: load(f) for f in glob.glob('../data/*_1d.csv')}
    etfs = {k: stocks.pop(k) for k in ('SPY', 'QQQ', 'IWM') if k in stocks}
    for k in list(stocks):
        if len(stocks[k]) < 500: stocks.pop(k)
    print(f'{len(stocks)} stocks, {len(etfs)} ETFs')
    rows = []
    for name, boost in (('ST07-A overlay 1.5x', 1.5), ('ST07-B overlay 2.0x', 2.0)):
        rows.append(evaluate(name, stocks, boost, 'STOCKS'))
        rows.append(evaluate(name, etfs, boost, 'ETFs  '))
    pd.DataFrame(rows).to_csv('../results/overlay_summary.csv', index=False)
