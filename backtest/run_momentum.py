"""Momentum tests ST03-ST05. Rules: ../strategies/ST03_ST05_momentum.md (frozen before running)."""
import glob, os, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
rng = np.random.default_rng(12)
COST = 0.0005; CUT = 0.7

def panel(names):
    C = {};
    for s in names:
        d = pd.read_csv(f'../data/{s}_1d.csv'); d['dt'] = pd.to_datetime(d.dt).dt.tz_localize(None); C[s] = d.set_index('dt').c
    return pd.DataFrame(C).dropna(how='all')

def month_ends(idx):
    s = pd.Series(idx, index=idx); return set(s.groupby([idx.year, idx.month]).last().values)

def run_weights(P, wfun, cash='SHY', lag=1):
    """wfun(i, P) -> dict symbol->weight at close index i. Portfolio return series with a lag (weights from signal at i earn from i+1+lag)."""
    R = P.pct_change().fillna(0); idx = P.index; me = month_ends(idx); N = len(idx)
    w = pd.DataFrame(0.0, index=idx, columns=P.columns); cur = pd.Series(0.0, index=P.columns); pend = []
    turn = pd.Series(0.0, index=idx)
    for i in range(N):
        if i - lag - 0 >= 0 and pend and pend[0][0] <= i:
            _, tgt = pend.pop(0); turn.iloc[i] = (tgt - cur).abs().sum(); cur = tgt
        w.iloc[i] = cur.values
        if idx[i] in me:
            tgt = pd.Series(0.0, index=P.columns)
            for k, v in wfun(i, P).items(): tgt[k] += v
            pend.append((i + 1 + lag - 1 + 0, tgt))   # applied from day i+lag+? (weights in force from the day after next)
    # weights in force on day t earn R[t]; shift by 1 so weights decided at t-1 earn R[t]
    port = (w.shift(1) * R).sum(axis=1) - turn * COST
    return port

def mom(P, i, look, skip):
    if i < look + skip + 1: return None
    return P.iloc[i - skip] / P.iloc[i - look - skip] - 1

def stats(r):
    r = r.dropna()
    if len(r) < 60: return dict(ann=np.nan, dd=np.nan, sharpe=np.nan, calmar=np.nan)
    eq = (1 + r).cumprod(); dd = (eq / eq.cummax() - 1).min(); yrs = len(r) / 252
    ann = eq.iloc[-1] ** (1 / yrs) - 1
    return dict(ann=ann * 100, dd=dd * 100, sharpe=r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan, calmar=ann / abs(dd) if dd < 0 else np.nan)

def show(label, port, bench, split):
    for lab, sl in (('OUT-OF-SAMPLE', slice(split, None)), ('IN-SAMPLE', slice(None, split))):
        a = stats(port.loc[sl]); parts = f'  {lab:14s} {label}: ann {a["ann"]:5.1f}% DD {a["dd"]:6.1f}% Sharpe {a["sharpe"]:.2f} Calmar {a["calmar"]:.2f}'
        for bn, br in bench.items():
            b = stats(br.loc[sl]); parts += f'  || {bn}: ann {b["ann"]:5.1f}% DD {b["dd"]:6.1f}% Sharpe {b["sharpe"]:.2f} Calmar {b["calmar"]:.2f}'
        print(parts)

def random_test(P, syms, k, look, skip, real_port, split, n=300):
    idx = P.index; me = month_ends(idx); Rn = P[syms].pct_change().fillna(0).values; N, S = Rn.shape
    rebal = [i for i in range(N) if idx[i] in me and i > look + skip]; out = []
    for _ in range(n):
        w = np.zeros((N, S)); cur = np.zeros(S); turn = np.zeros(N)
        for j, i in enumerate(rebal):
            tgt = np.zeros(S); tgt[rng.choice(S, k, replace=False)] = 1.0 / k
            st = i + 1; en = rebal[j + 1] + 1 if j + 1 < len(rebal) else N
            if st >= N: break
            turn[st] = np.abs(tgt - cur).sum(); cur = tgt; w[st:en] = tgt
        pr = np.zeros(N); pr[1:] = (w[:-1] * Rn[1:]).sum(axis=1); pr -= turn * COST
        s_ = stats(pd.Series(pr, index=idx).loc[split:]); out.append((s_['ann'], s_['sharpe']))
    o = np.array(out); s0 = stats(real_port.loc[split:])
    return (o[:, 0] < s0['ann']).mean() * 100, (o[:, 1] < s0['sharpe']).mean() * 100, o[:, 0].mean(), o[:, 1].mean()

if __name__ == '__main__':
    stocks = [os.path.basename(f).split('_')[0] for f in glob.glob('../data/*_1d.csv')]
    etfs_bench = ['SPY', 'QQQ', 'IWM']; sect = 'XLK XLF XLE XLV XLY XLP XLI XLB XLU'.split(); other = ['EFA', 'AGG', 'SHY']
    big = [s for s in stocks if s not in etfs_bench + sect + other]
    PS = panel(big + ['SPY', 'SHY']); PS = PS[PS.index >= '2009-01-01']
    # ---------- ST03 cross-sectional momentum on 49 stocks (survivorship-biased)
    for name, look in (('ST03-A 12-1m top10', 252), ('ST03-B 6-1m top10', 126)):
        def wf(i, P, look=look):
            m = mom(P[big], i, look, 21)
            if m is None: return {}
            m = m.dropna().sort_values(ascending=False); top = list(m.index[:10]); return {s: 0.1 for s in top}
        port = run_weights(PS, wf); ew = run_weights(PS, lambda i, P: {s: 1 / len(big) for s in big}); spy = PS.SPY.pct_change().fillna(0)
        split = port.index[int(CUT * len(port))]
        print(f'\n=== {name} ({len(big)} stocks, {port.index[0].date()} to {port.index[-1].date()}, split {split.date()}; SURVIVORSHIP-BIASED universe)')
        show('momentum', port, {'EW all 49': ew, 'SPY': spy}, split)
        pr, ps_, rm, rs = random_test(PS[big], big, 10, look, 21, port, split)
        print(f'  random 10-stock picks (300 draws, OOS): mean ann {rm:.1f}%, mean Sharpe {rs:.2f} | momentum beats {pr:.0f}% of random by return, {ps_:.0f}% by Sharpe')
    # ---------- ST04 sector rotation (clean)
    PE = panel(sect + ['SPY', 'SHY', 'EFA', 'AGG']); PE = PE[PE.index >= '2007-01-01']
    for name, absf in (('ST04-A sector rotation top3', False), ('ST04-B sector rotation + absolute momentum', True)):
        def wf(i, P, absf=absf):
            m = mom(P[sect], i, 252, 21)
            if m is None: return {}
            m = m.dropna().sort_values(ascending=False); w = {}
            for s in list(m.index[:3]):
                if absf and m[s] <= 0: w['SHY'] = w.get('SHY', 0) + 1 / 3
                else: w[s] = w.get(s, 0) + 1 / 3
            return w
        port = run_weights(PE, wf); ew = run_weights(PE, lambda i, P: {s: 1 / len(sect) for s in sect}); spy = PE.SPY.pct_change().fillna(0)
        split = port.index[int(CUT * len(port))]
        print(f'\n=== {name} ({port.index[0].date()} to {port.index[-1].date()}, split {split.date()}; clean ETF universe)')
        show('momentum', port, {'EW 9 sectors': ew, 'SPY': spy}, split)
        pr, ps_, rm, rs = random_test(PE[sect], sect, 3, 252, 21, port, split)
        print(f'  random 3-sector picks (300 draws, OOS): mean ann {rm:.1f}%, mean Sharpe {rs:.2f} | momentum beats {pr:.0f}% of random by return, {ps_:.0f}% by Sharpe')
    # ---------- ST05 dual momentum (clean)
    def wf5(i, P):
        if i < 253: return {}
        r = lambda s: P[s].iloc[i] / P[s].iloc[i - 252] - 1
        best = 'SPY' if r('SPY') >= r('EFA') else 'EFA'
        return {best: 1.0} if r(best) > r('SHY') else {'AGG': 1.0}
    port = run_weights(PE, wf5); spy = PE.SPY.pct_change().fillna(0)
    sixty = run_weights(PE, lambda i, P: {'SPY': 0.6, 'AGG': 0.4}); split = port.index[int(CUT * len(port))]
    print(f'\n=== ST05 dual momentum SPY/EFA/AGG ({port.index[0].date()} to {port.index[-1].date()}, split {split.date()}; clean)')
    show('dual mom', port, {'SPY': spy, '60/40': sixty}, split)
