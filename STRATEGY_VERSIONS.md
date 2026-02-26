# Strategy Versions Documentation

## Whale Copy-Trading A/B Test

**Start Date:** 2026-02-26  
**Expected Comparison Completion:** After 100 trades per version (~2-3 weeks)

---

## Overview

We are running a parallel A/B test between two versions of the Whale Copy-Trading strategy to determine if a tighter stop loss (6% vs 8%) improves overall performance.

---

## Version Details

### Whale Copy-Trading v1 (Baseline)
- **Strategy Key:** `whale_copy_trading`
- **Stop Loss (SL):** 8% (0.08)
- **Take Profit (TP):** 20% (0.20)
- **Win Rate:** 70% target
- **Avg Profit:** +15%
- **Avg Loss:** -8%
- **Max Hold:** 2 days
- **Capital Allocation:** 50% of Whale Copy budget ($75 of $150)

### Whale Copy-Trading v2 (Test)
- **Strategy Key:** `whale_copy_trading_v2`
- **Stop Loss (SL):** 6% (0.06) ← **Only difference**
- **Take Profit (TP):** 20% (0.20)
- **Win Rate:** 70% target
- **Avg Profit:** +15%
- **Avg Loss:** -6%
- **Max Hold:** 2 days
- **Capital Allocation:** 50% of Whale Copy budget ($75 of $150)

---

## What We're Testing

### Hypothesis
A tighter 6% stop loss will:
1. Reduce average loss per losing trade (-6% vs -8%)
2. Potentially increase win rate (earlier exits on reversals)
3. Maintain or improve risk-adjusted returns

### Trade-offs
| Factor | v1 (8% SL) | v2 (6% SL) | Impact |
|--------|-----------|-----------|--------|
| Max loss per trade | -8% | -6% | v2 loses 25% less on stops |
| Whipsaw risk | Lower | Higher | v2 may exit on noise |
| Win rate | Baseline | TBD | Expect v2 to be equal or higher |
| Expectancy | Baseline | TBD | Key metric for decision |

---

## Parallel Execution Logic

Both versions:
1. Receive **identical whale signals** at the **same time**
2. Enter at the **same entry price**
3. Use **same position sizing** (50/50 split)
4. Only differ in **exit behavior** when price moves against the position

### Example Scenario
```
Whale Signal: Theo4 buys YES on BTC $100k market @ 0.67

v1 Trade: Entry @ 0.67, SL @ 0.6164 (-8%), TP @ 0.804 (+20%)
v2 Trade: Entry @ 0.67, SL @ 0.6298 (-6%), TP @ 0.804 (+20%)

If price drops to 0.62:
- v1: Still holding (0.62 > 0.6164)
- v2: Stopped out @ 0.6298 (-6% loss)

If price recovers and hits 0.804:
- v1: TP hit (+20% profit)
- v2: Already stopped out (missed the win)
```

---

## Success Criteria

### v2 is BETTER if:
- [ ] Win rate improves by >5% vs v1
- [ ] Expectancy per trade is higher
- [ ] Max drawdown is lower
- [ ] Risk-adjusted return (PnL/volatility) is better

### v2 is WORSE if:
- [ ] Win rate drops by >5% vs v1
- [ ] Significant increase in whipsaw losses
- [ ] Lower total PnL despite smaller individual losses

### Keep v1 (Baseline) if:
- [ ] Results are within ±3% of each other (no significant difference)

---

## Tracking & Analysis

### Data Collection
Both versions log trades separately in `trades.json`:
- v1 tagged: `"strategy": "Whale Copy-Trading"`
- v2 tagged: `"strategy": "Whale Copy-Trading v2"`

### Comparison Metrics (after 100 trades each)
| Metric | v1 (8%) | v2 (6%) | Winner |
|--------|---------|---------|--------|
| Total Trades | | | |
| Win Rate | | | |
| Avg Winner | | | |
| Avg Loser | | | |
| Expectancy | | | |
| Max Drawdown | | | |
| Total PnL | | | |
| Sharpe Ratio | | | |

---

## Implementation Notes

### Code Changes
File: `/home/pesiss/.openclaw/agents/polymarket/paper_trading_engine.py`

1. Added `STRATEGY_PARAMS` entry for v2:
```python
"Whale Copy-Trading v2": {
    "win_rate": 0.70, 
    "avg_profit": 0.15, 
    "avg_loss": -0.06,  # Changed from -0.08
    "sl_pct": 0.06,     # Changed from 0.08
    "tp_pct": 0.20, 
    "max_hold_days": 2
}
```

2. Updated `run_scan_cycle()` to execute both versions on same signal
3. Split position sizing 50/50 between versions
4. Added v2 to performance tracking and daily reports

### Risk Management
- Combined Whale Copy allocation remains at $150 (or whatever the original total was)
- Each version gets 50% allocation to maintain same risk exposure
- Circuit breaker applies to combined Whale Copy PnL

---

## Timeline

| Date | Milestone |
|------|-----------|
| 2026-02-26 | A/B test initiated, v2 deployed |
| 2026-03-05 | 25 trades check - preliminary analysis |
| 2026-03-12 | 50 trades check - trend assessment |
| 2026-03-19 | 100 trades reached - final comparison |
| 2026-03-20 | Decision: Keep v1, switch to v2, or continue testing |

---

## Decision Framework

After 100 trades:

```
IF v2_win_rate >= v1_win_rate AND v2_expectancy > v1_expectancy:
    → Migrate to v2 (6% SL)
    → Archive v1
    
ELIF v2_win_rate < v1_win_rate - 5%:
    → Keep v1 (8% SL)
    → Archive v2
    
ELSE:
    → Results inconclusive
    → Continue test to 200 trades OR
    → Keep both running with 50/50 split
```

---

## Related Files

- **Engine:** `/home/pesiss/.openclaw/agents/polymarket/paper_trading_engine.py`
- **Trades:** `/home/pesiss/.openclaw/agents/polymarket/trades.json`
- **Analysis:** `/home/pesiss/.openclaw/workspace/analyze_phase3.py`
- **Consolidated:** `/home/pesiss/.openclaw/workspace/all_trades.json`

---

## Notes

- This is a controlled experiment with real market conditions
- Both versions receive identical signals to ensure fair comparison
- Document any observations about market behavior during the test period
- Note any unusual market conditions that might affect results

---

*Last Updated: 2026-02-26*  
*Next Review: When 100 trades reached or 2026-03-20 (whichever comes first)*
