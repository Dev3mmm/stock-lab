# Stock lab report (2026-09-27)

**Source video:** Ray Fu, "Complete Guide to building an AI Trading Bot with Claude for Beginners". It teaches the tools (Claude Code, Alpaca paper broker, yfinance) and one strategy, the 20/50-day moving average crossover on Apple. It shows no backtest.

**Friend's claim tested:** "crypto isn't an established market, so it's easier than stocks."

## Results
- **The video's strategy (20/50 crossover) on stocks:** out-of-sample +4.0% a year with -13% max drawdown, versus +14.3% and -23% for simply holding an equal-weight basket. It beat holding on only 12% of stocks, and its trades did worse than random entries of the same length. It lost the 2008-2026 return race to buy and hold on almost every stock. It does cut drawdowns, but it gives up much more return than it saves.
- **Golden cross 50/200 and Turtle breakouts on stocks:** lower drawdowns (-5% to -11%) but lower returns, and no better than random entries on a per-trade basis. On the clean ETFs (SPY, QQQ, IWM) the 20/50 lost to holding on all three.
- **The same rules on crypto (26 coins):** +11% to +25% a year out-of-sample with -10% to -30% drawdowns, versus -5% and -64% for holding. Per-trade returns beat random entries at the 91st to 98th percentile, and 54% to 81% of coins beat buy and hold on risk-adjusted terms. In the in-sample half, holding crypto returned more (35% a year) but with -62% drawdowns; the trend rules had much better Calmar (0.6 to 0.9 vs 0.56).

## What this says about the friend's claim
Partly true, and not in the way he means. Crypto shows something stocks do not: daily trend-following adds value there (it beats random entries and holds up in both halves of the history), while in large-cap stocks it does not. That is consistent with crypto being a less efficient, more trend-driven market. But it is not "easy":
- the crypto edge is slow trend following, about 25% to 30% winning trades, with drawdowns of 10% to 30%;
- the crypto out-of-sample window is only 13 months, mostly a falling market where any de-risking looks good;
- the coin list is today's top coins (survivorship bias) and covers only about 4 years of data;
- everything fast (scalps, ICT/SMC patterns, Asian range, Fibonacci) failed in crypto in the strategy lab.

## Is stock trading "possible"?
For large US stocks, the honest answer from this test is: buying and holding beat every timing strategy here, and the video's bot would have underperformed simply owning the stocks. The bot infrastructure (Alpaca paper account, daily check) is fine and could run any strategy, but the strategy in the video has no edge. Ideas worth testing next in stocks: cross-sectional momentum (needs survivorship-free data), a 200-day trend filter as risk control, and earnings-related drift.

## Update: momentum tests (ST03 to ST05, 2026-09-27)
Cross-sectional stock momentum, sector ETF rotation and dual momentum were tested with the same protocol. None passed. Stock momentum (top 10 of 49) returned 14.1% a year out-of-sample vs 13.5% for holding all 49 and 13.7% for SPY, no better than random stock selection at the 95th percentile, even though the universe is survivorship-flattered. Sector rotation matched an equal-weight sector basket. Dual momentum lost to SPY in both halves of the history. Conclusion: in US large-cap stocks/ETFs, holding the index beat every timing or selection rule tested here (MA crossover, Turtle, momentum). The one exploitable thing found so far anywhere in these labs is daily trend following in crypto.
