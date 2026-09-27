# ST03 to ST05: Momentum strategies for stocks and ETFs

**Source:** the stock ideas listed at the end of `results/REPORT.md` (cross-sectional momentum, sector rotation, dual momentum). These are the best-documented equity factors in academic research (Jegadeesh-Titman 1993, Antonacci dual momentum), so they are the fair test of "is stock trading possible".
**Status:** rules frozen 2026-09-27, before any run.

## Frozen rules
All strategies rebalance monthly at the last trading day's close. Weights apply from the second trading day after the signal (one full day of lag, no look-ahead). Costs: 0.05% per side on traded weight. Data: Yahoo, adjusted for splits and dividends. Cash earns the SHY (1-3 year Treasury ETF) return.

- **ST03-A cross-sectional stock momentum:** rank the 49 large caps by total return over the past 252 trading days excluding the most recent 21 (12-1 month). Hold the top 10, equal weight. Benchmarks: equal-weight all 49 (monthly rebalanced), SPY. ST03-B: 126-day lookback (6-1 month). Survivorship warning: the 49 are today's large caps, which flatters momentum.
- **ST04-A sector ETF rotation (clean, no survivorship):** the 9 SPDR sector ETFs (XLK XLF XLE XLV XLY XLP XLI XLB XLU). Rank by 12-1 momentum, hold the top 3, equal weight. ST04-B: same, but a sector is only held if its own 12-1 return is above zero, otherwise that slot is cash (absolute momentum). Benchmarks: equal-weight 9 sectors, SPY.
- **ST05 dual momentum (clean):** each month compare SPY and EFA (developed international) on 12-month return. If the better one beat SHY over 12 months hold it, otherwise hold AGG (bonds). Benchmarks: SPY, 60/40 (60% SPY, 40% AGG monthly rebalanced).
- **Split:** first 70% of the common history in-sample, last 30% out-of-sample; verdict on out-of-sample.
- **Selection-skill test (ST03, ST04):** 1,000 random portfolios with the same number of holdings, picked at random each month from the same universe. The strategy's out-of-sample annual return and Sharpe must beat the 95th percentile of random selection.
- **Pass bar:** out-of-sample Calmar above the benchmark's AND beats random selection at the 95th percentile (return AND Sharpe) AND positive in both halves. For ST03 the survivorship bias is stated in the verdict.
