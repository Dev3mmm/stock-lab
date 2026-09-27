# ST07: RSI(2) overlay on a permanent core holding

**Source:** follow-up to ST06. ST06 showed a real per-trade edge (beats random entries 91st-100th percentile) but underperformed buy-and-hold because it sat in cash ~90% of the time. This design keeps a base equity holding at all times and only uses RSI(2) to size up or down, so the bull-market drift is captured either way.
**Status:** rules frozen 2026-09-27, before any run.

## Frozen rules
- Daily bars, same universe as ST06 (49 stocks + SPY/QQQ/IWM), same 70/30 split, same costs (0.05%/side on the traded portion only), same random and buy-and-hold baselines.
- **Per asset weight, evaluated at each day's close, applied from the next open:**
  - Base weight = 1.0 (100% invested) at all times, EXCEPT: base weight = 0.5 whenever price is below its 200-day SMA (the ST06 trend filter, softened from a full exit to a half-size defensive stance).
  - **Overlay:** while RSI(2) < 10 and price is above the 200-day SMA, weight = 1.5 (lever up 50% into the dip) until RSI(2) closes above 70, then weight reverts to base (1.0).
  - No overlay boost when price is below the 200-day SMA (do not lever into a downtrend dip).
- Portfolio: equal weight across the universe, each asset's own weight (0.5, 1.0 or 1.5) applied to its 1/N slot; the un-invested/under-invested remainder earns 0% (cash), leverage above 1.0 funded at 0% (i.e. a simplifying assumption disclosed in the verdict, since real margin has a cost).
- Pre-registered variant: ST07-B overlay weight 2.0 instead of 1.5 (double the position size on a dip) to see if a bigger tilt helps or just adds risk.
- Benchmarks: equal-weight buy and hold of the same universe (weight always 1.0), SPY.
- Pass bar: OOS Calmar beats buy-and-hold's AND OOS annualised return is within 2 percentage points of buy-and-hold's (i.e. it must no longer give up meaningful return to earn its risk reduction) AND positive on >=60% of assets by Calmar AND max drawdown improves on buy-and-hold's.
