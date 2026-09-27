# ST06: RSI(2) mean reversion (Larry Connors style), long only

**Source:** flagged by Martin's earlier YouTube/web research (`project_trading_strategy_research_2026_09`): an independent 9,000-strategy test found mean reversion was the only family that stayed positive out-of-sample in stocks/ETFs (vs trend/breakout families, which mostly didn't). Testing it here on the same stock/ETF data as ST01-ST05, so it's judged by the same bar.
**Status:** rules frozen 2026-09-27, before any run.

## Frozen rules
- Daily bars. RSI(2) of the close (Wilder smoothing).
- **Trend filter (the standard version of this system):** only take the trade if the close is above its 200-day SMA (buy dips in an uptrend, not falling stocks).
- **Entry:** buy at the next day's open when RSI(2) closes below 10 (deeply oversold) and the 200-day filter holds.
- **Exit:** sell at the next day's open when RSI(2) closes above 70 (mean reverted). Hard time exit at 10 trading days if neither happens. No stop (short holding period, no leverage): pre-registered variant ST06-D adds a stop.
- Long only, one position per asset, no pyramiding.
- Costs: 0.05%/side, same universe (49 stocks + SPY/QQQ/IWM), same 70/30 split, same random-entry and buy-and-hold baselines as ST01.
- Pre-registered variants: ST06-B RSI(2)<5 entry / >75 exit (stricter); ST06-C no 200-day filter (buy any dip); ST06-D adds a 3%% hard stop.
- Pass bar: same as ST01 (OOS Calmar beats buy&hold, beats random entries at the 95th percentile, positive on >=60%% of assets, >=100 OOS trades).
