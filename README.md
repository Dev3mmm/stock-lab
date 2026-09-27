# Stock Lab

Sister folder to `..\strategy_lab\` (crypto). Same rules: every idea is written as frozen, testable rules BEFORE testing, then scored against buy and hold and random entries, then (if it survives) forward tested on paper.

```
stock_lab/
  strategies/    frozen rules, one file per strategy (ST01, ST02, ...)
  sources/       where each idea came from (v1 = Ray Fu "AI Trading Bot with Claude" video)
  data/          daily candles, 52 US stocks and ETFs, 2008 to 2026 (Yahoo Finance via yfinance, split/dividend adjusted)
  backtest/      fetch_stocks.py, lab.py (engine), run_stock.py
  results/       output tables and REPORT.md
  scoreboard.md  one row per strategy: verdict
```

**The question this lab answers (from Martin's friend):** "crypto is not an established market, so it is easier to trade than stocks." We test that directly: the same strategies, the same costs logic, stocks vs crypto, judged against buy and hold.

**Paper trading path:** Alpaca (free paper account, no real money) is what the source video uses. Nothing is connected yet; a strategy only gets a paper account after it passes the backtest.
