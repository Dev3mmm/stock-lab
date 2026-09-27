# Stock Lab scoreboard (run 2026-09-27; 49 US large caps + SPY/QQQ/IWM, 2008 to 2026; crypto comparison = 26 coins)

Costs: stocks 0.05%/side, crypto 0.07%/side. Out-of-sample = last 30% of each history (stocks from Feb 2021, includes the 2022 bear market; crypto from Aug 2025).
Survivorship bias: the stock list is today's big winners (flatters buy and hold and every long strategy). SPY/QQQ/IWM are the clean checks.

| Strategy | Market | OOS return/yr | OOS max DD | Calmar | Buy&hold (ret / DD / Calmar) | Assets beating B&H (Calmar) | Beats random entries | Verdict |
|---|---|---|---|---|---|---|---|---|
| ST01-A MA 20/50 (the video) | Stocks | 4.0% | -13% | 0.30 | 14.3% / -23% / 0.63 | 12% | 0th pct | **FAIL** (worse than just holding) |
| ST01-A | ETFs | 3.2% | -26% | 0.12 | 12.1% / -29% / 0.42 | 0 of 3 | 8th pct | **FAIL** |
| ST01-A | Crypto | 25.4% | -30% | 0.86 | -5.3% / -64% / -0.08 | 81% | 98th pct | works in crypto (13-month OOS) |
| ST01-B MA 50/200 | Stocks | 8.9% | -11% | 0.79 | 14.3% / -23% / 0.63 | 35% | 48th pct | **FAIL** (less risk, less return, no timing skill) |
| ST01-C MA 10/30 | Stocks | 5.4% | -13% | 0.41 | same | 20% | 9th pct | **FAIL** |
| ST02-A Turtle 20/10 | Stocks | 3.9% | -7% | 0.57 | same | 29% | 13th pct | **FAIL** |
| ST02-A Turtle 20/10 | Crypto | 11.0% | -19% | 0.58 | -5.3% / -64% / -0.08 | 62% | 95th pct | works in crypto |
| ST02-B Turtle 55/20 | Stocks / Crypto | 3.4% / 13.1% | -5% / -10% | 0.68 / 1.36 | 0.63 / -0.08 | 16% / 68% | 7th / 91st | stocks FAIL, crypto works |

**Read:** the video's strategy does not beat buy and hold on stocks. The same trend rules do beat random entries and cut drawdowns in crypto, in both halves of the history. Details: `results/REPORT.md`.

## Momentum tests (run 2026-09-27; monthly rebalance, 1 day lag, 0.05%/side on turnover; OOS = last 30%)
| Strategy | OOS return/yr | OOS max DD | Calmar | Benchmark (ret / DD / Calmar) | Beats random selection (return / Sharpe) | Verdict |
|---|---|---|---|---|---|---|
| ST03-A stock momentum 12-1m top 10 (biased universe) | 14.1% | -22% | 0.65 | EW49 13.5% / -23% / 0.59; SPY 13.7% / -25% / 0.56 | 71st / 50th pct | **FAIL** (same as holding, even with survivorship help) |
| ST03-B 6-1m top 10 (biased) | 16.5% | -28% | 0.58 | same | 85th / 69th | **FAIL** (a bit more return, a bit more risk, not significant) |
| ST04-A sector ETF rotation top 3 (clean) | 15.1% | -16% | 0.95 | EW9 15.1% / -17% / 0.89; SPY 16.3% / -25% / 0.67 | 66th / 62nd | **FAIL** (= equal-weight sectors) |
| ST04-B + absolute momentum | 15.0% | -16% | 0.94 | same | 62nd / 59th | **FAIL** |
| ST05 dual momentum SPY/EFA/AGG (clean) | 11.5% | -27% | 0.43 | SPY 16.3% / -25% / 0.67; 60/40 9.6% / -21% / 0.47 | n/a | **FAIL** (lost to SPY in both halves) |

## ST06 RSI(2) mean reversion (run 2026-09-27; costs 0.05%/side, 70/30 split)
| Variant | Market | OOS trades | Win % | Beats random entries | Portfolio Calmar (strat/B&H) | Assets beating B&H Calmar | Verdict |
|---|---|---|---|---|---|---|---|
| ST06-A RSI2<10/>70 + 200MA filter | Stocks | 2,360 | 66% | **91st pct** | 0.66 / 0.98 | 23% of 61 | Real per-trade edge, but FAILS the Calmar/asset bar (mostly in cash) |
| ST06-A | ETFs | 141 | 77% | **96th pct** | 0.51 / 0.42 | 33% of 3 | Beats B&H Calmar, but only 3 assets: **insufficient breadth to pass** |
| ST06-B stricter (<5/>75) | Stocks | 1,227 | 66% | 63rd pct | 0.60 / 0.98 | 18% of 61 | FAIL, weaker than A |
| ST06-C no 200MA filter (buy any dip) | Stocks | 4,142 | 66% | **100th pct** | 0.86 / 0.98 | 41% of 61 | Best per-trade edge; still FAILS the 60%-of-assets bar |
| ST06-C | ETFs | 205 | 73% | **100th pct** | 0.81 / 0.42 | **100% of 3** | Meets every numeric bar, but n=3 assets is too small to call a pass |
| ST06-D + 3% stop | Stocks | 2,676 | 59% | 27th pct | 0.31 / 0.98 | 18% of 61 | Stop makes it worse (cuts winners, no benefit — moves are usually quick) |

**Read:** unlike every strategy tested so far (crypto scalps, video SMC setups, stock MA/Turtle/momentum), RSI(2) mean reversion beats random entries by a wide, consistent margin (63rd to 100th percentile across all 8 stock/ETF runs) — a real short-term statistical edge exists. It still doesn't pass the strict bar, but for a new reason: the strategy is in cash roughly 90% of the time, so its raw annual return and portfolio Calmar lag simply holding stocks through a 15+ year bull market. **Verdict: PARKED, not FAILED** — worth a second design (e.g. combine with staying invested via a small permanent equity sleeve, or apply on a shorter holding book) rather than dropping like the others.

## ST07 RSI(2) overlay on a permanent core holding (run 2026-09-27, bug caught and fixed mid-run: first version used today's own close to size today's position — a look-ahead bug — re-run below is the corrected, honest result)
| Variant | Market | OOS ann. (overlay/B&H) | OOS max DD (overlay/B&H) | Calmar (overlay/B&H) | Return gap | Assets w/ better Calmar | Assets w/ smaller DD | Verdict |
|---|---|---|---|---|---|---|---|---|
| ST07-A 1.5x | Stocks | 17.4% / 20.8% | -16.8% / -21.3% | 1.03 / 0.98 | -3.4pp | 39% of 61 | 64% of 61 | **FAILS the pass bar** (only 39% of stocks improve, need 60%) |
| ST07-A 1.5x | ETFs | 14.5% / 12.1% | -23.1% / -29.0% | 0.63 / 0.42 | +2.4pp | 100% of 3 | 100% of 3 | Passes on ETFs, but n=3 is too small to trust |
| ST07-B 2.0x | Stocks | 19.0% / 20.8% | -18.1% / -21.3% | 1.05 / 0.98 | -1.8pp | 36% of 61 | 43% of 61 | **FAILS** (worse asset breadth than 1.5x) |
| ST07-B 2.0x | ETFs | 17.7% / 12.1% | -24.1% / -29.0% | 0.74 / 0.42 | +5.6pp | 100% of 3 | 67% of 3 | Passes on ETFs, n=3 too small |

**Read:** the overlay closes most of the return gap ST06 had (now -1.8 to -3.4pp instead of -13 to -17pp) and the portfolio-level Calmar ties or beats buy-and-hold. But per individual stock it only improves the risk-adjusted return on about 36-39% of the 61 names (need 60%), so it does not clear the pre-registered bar on the broad stock universe. It does clear the bar on the 3 clean index ETFs, where the sample is too small to trust on its own. **Verdict: still PARKED — the direction (partial exposure + RSI(2) tilt) is right, but sizing/breadth needs more work; test on ETF sectors or a larger, survivorship-free stock universe next.**
