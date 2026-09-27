# ST01: Moving average crossover 20/50 (the strategy in the video)

**Source:** Ray Fu, YouTube "Complete Guide to building an AI Trading Bot with Claude for Beginners" (128k views, 14 min). Transcript and comments in `sources/v1/`. He builds the bot with Claude Code + the Alpaca paper broker, on Apple, one share at a time, checking each weekday at 9:30 ET.
**Status:** rules frozen 2026-09-27, before any run.

## What the video teaches
Fast average (20-day) crossing above the slow average (50-day) = buy. Fast crossing below slow = sell (get out). "The simplest one that actually works." He admits it whipsaws in sideways markets and "no strategy wins every time". No backtest is shown at all.

## Gaps
No results, no comparison with just holding the stock, no costs, no stop, one stock only. Comments: a giveaway (like/subscribe/comment to win a Claude plan), one says "this is a scam", one notes the video shows how someone with no trading knowledge can sound knowledgeable.

## Frozen rules
- Daily bars, simple moving averages of the close. Signal is evaluated at the close.
- Entry: the day the 20-day SMA crosses above the 50-day (yesterday fast <= slow, today fast > slow). Buy at the next day's open.
- Exit: the day the 20-day crosses below the 50-day. Sell at the next day's open. Long only, no stop, no shorting (the video's "sell" means get out).
- Position: 100% of that asset's allocation while in the trade, cash otherwise.
- Costs: stocks 0.05% per side (spread + slippage; Alpaca charges no commission). Crypto comparison: 0.07% per side.
- Variants (pre-registered): ST01-B 50/200 (the "golden cross"), ST01-C 10/30.
- Universe: 49 US large-cap stocks + SPY, QQQ, IWM (Yahoo, adjusted for splits and dividends), 2008 to 2026. Comparison universe: the 27 crypto coins used in strategy_lab.
- Split: first 70% of each asset's history in-sample, last 30% out-of-sample (verdict on out-of-sample; for stocks OOS starts about May 2021 and includes the 2022 bear market).
- Baselines: buy and hold each asset; equal-weight buy and hold portfolio; random entries with the same hold length (1,000 draws).
- Pass bar: on the equal-weight portfolio, out-of-sample Calmar (return / max drawdown) higher than buy and hold AND the strategy beats buy and hold's Calmar on at least 60% of individual assets AND per-trade return beats random entries at the 95th percentile.
- Known biases stated up front: the stock list is today's large caps (survivorship, flatters buy and hold and every long strategy); SPY/QQQ/IWM are the clean, unbiased checks.
