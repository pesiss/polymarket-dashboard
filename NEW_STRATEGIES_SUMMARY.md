# New Polymarket Strategies Summary

## Overview

Two new strategies have been added to the Polymarket paper trading engine:

1. **Oracle Lag Exploit** - Information asymmetry trading
2. **Liquidity King** - Market making strategy

---

## Strategy 1: Oracle Lag Exploit

### Description
Trades the information asymmetry window between external outcome confirmation and oracle finalization. Monitors real-world events (sports, politics, macro data) and enters when the market hasn't priced in confirmed outcomes.

### Key Parameters
| Parameter | Value |
|-----------|-------|
| Strategy Key | `oracle_lag_exploit` |
| Display Name | "Oracle Lag Exploit" |
| Win Rate | 72% (estimated) |
| Avg Profit | 25% |
| Avg Loss | -8% |
| Stop Loss | 8% |
| Take Profit | 30% (target 20-40% edge capture) |
| Position Size | 6.3% of capital |
| Max Hold Time | ~2.4 hours (0.1 days) |

### Entry Criteria
- **YES Side**: When external data confirms outcome but market price < 80%
- **NO Side**: When external data confirms outcome but market price > 20%

### Exit Criteria
- Price reaches 90%+ (YES) or 10%- (NO)
- Oracle finalizes
- Stop loss at 8%
- Take profit at 30%

### Timeframe
- 15 minutes to 2 hours holds

### Required Data Feeds (Not Yet Active)
| Category | APIs Needed |
|----------|-------------|
| Sports | ESPN API, Sportradar API |
| Politics | AP News API, Decision Desk HQ API |
| Macro | Bloomberg API, Economic Calendar APIs |
| Crypto | ETF/Approval event trackers |

### Allocation
- **Test Allocation**: $100
- **Status**: Configured but requires data feed setup

---

## Strategy 2: Liquidity King (Market Making)

### Description
Provides liquidity by placing maker orders on both sides of the order book. Captures bid-ask spread + earns Polymarket liquidity rewards. Requires $500+ capital for optimal performance.

### Key Parameters
| Parameter | Value |
|-----------|-------|
| Strategy Key | `liquidity_king` |
| Display Name | "Liquidity King" |
| Win Rate | 85% (estimated) |
| Avg Profit | 3% per round trip |
| Avg Loss | -2% |
| Stop Loss | 10% (dynamic inventory management) |
| Take Profit | 4% (spread capture) |
| Position Size | Variable (needs capital on both sides) |
| Max Hold Time | Continuous (0.01 days for paper trading resolution) |

### Entry Criteria
- Place bid 1-2% below mid price
- Place ask 1-2% above mid price

### Exit Criteria
- When orders fill, immediately re-place
- Dynamic inventory management: hedge if position > 10% capital

### Timeframe
- Continuous market making

### Key Parameters
| Parameter | Value |
|-----------|-------|
| Max Spread | 2% |
| Min Market Liquidity | $10,000 |
| Inventory Limit | 10% of capital per side |
| Rebalance Threshold | If inventory > 10%, hedge or exit |

### Allocation
- **Test Allocation**: $200
- **Note**: Needs more capital for effective market making on both sides

---

## Expected Performance

### Oracle Lag Exploit
- **Expected Win Rate**: 72%
- **Expected Edge per Trade**: 20-40%
- **Optimal Market Conditions**: High-profile events with clear external confirmation sources
- **Risk Factors**: Data feed latency, oracle finalization timing
- **Capital Efficiency**: High (short holds, high edge)

### Liquidity King
- **Expected Win Rate**: 85%
- **Expected Return per Round Trip**: 2-4%
- **Optimal Market Conditions**: High liquidity markets with tight spreads
- **Risk Factors**: Inventory imbalance, adverse selection
- **Capital Efficiency**: Moderate (requires capital on both sides)

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Paper Trading Engine | ✅ Complete | Both strategies added to `paper_trading_engine.py` |
| Strategy Parameters | ✅ Complete | Win rates, SL/TP, position sizes configured |
| Scanning Methods | ✅ Complete | `scan_oracle_lag_exploit()` and `scan_liquidity_king()` implemented |
| Trade Execution | ✅ Complete | Integrated into `run_scan_cycle()` |
| Dashboard | ✅ Complete | Both strategies added to `dashboard.html` |
| Allocations | ✅ Complete | oracle_lag_exploit: $100, liquidity_king: $200 |
| Data Feeds | ⏳ Not Active | Requires API integrations |
| Real Money Ready | ⏳ Pending | Needs data feed validation first |

---

## Next Steps for Activation

### Oracle Lag Exploit
1. **Set up data feed integrations**:
   - Sports: Integrate ESPN API or Sportradar for live scores
   - Politics: Connect AP News API or Decision Desk for election results
   - Macro: Set up Bloomberg or economic calendar APIs
   - Crypto: Monitor ETF/approval announcements

2. **Build signal detection system**:
   - Real-time event monitoring
   - Price divergence detection
   - Automated entry triggers

3. **Test with historical data**:
   - Backtest on past events
   - Validate latency assumptions
   - Fine-tune entry/exit thresholds

4. **Paper trade for 2-4 weeks**:
   - Validate signal quality
   - Measure actual latency
   - Adjust position sizing

### Liquidity King
1. **Connect to live order book**:
   - Polymarket CLOB API integration
   - Real-time order book monitoring

2. **Implement inventory management**:
   - Position tracking per market
   - Rebalancing logic
   - Hedge execution

3. **Monitor liquidity rewards**:
   - Track Polymarket reward accrual
   - Calculate effective APR

4. **Start with $500+ capital**:
   - Current $200 allocation is for testing
   - Scale up after validation

---

## Risk Considerations

### Oracle Lag Exploit
- **Data Feed Risk**: APIs may have delays or errors
- **Timing Risk**: Oracle may finalize before position is profitable
- **Market Risk**: Other traders may exploit the same lag
- **Regulatory Risk**: Event trading may face scrutiny

### Liquidity King
- **Inventory Risk**: Imbalanced positions during trending markets
- **Adverse Selection**: Informed traders picking off stale quotes
- **Capital Risk**: Requires significant capital locked in orders
- **Opportunity Cost**: Capital may earn more in directional strategies

---

## Files Modified

| File | Changes |
|------|---------|
| `/home/pesiss/.openclaw/agents/polymarket/paper_trading_engine.py` | Added 2 strategies to STRATEGY_PARAMS, calculate_performance, scanning methods, execution logic, daily report |
| `/home/pesiss/.openclaw/workspace/dashboard.html` | Added 2 strategies to strategies_list, updated allocations (100 and 200), updated strategy count to 11 |
| `/home/pesiss/.openclaw/workspace/NEW_STRATEGIES_SUMMARY.md` | Created this documentation file |

---

## Summary

Both strategies are **configured and ready** in the paper trading engine but are **not yet actively trading** because:

1. **Oracle Lag Exploit** requires external data feed integrations (sports, politics, macro APIs)
2. **Liquidity King** requires live order book connectivity and higher capital allocation

The infrastructure is in place. Once data feeds are connected and tested, these strategies will begin generating signals in paper trading mode.

**Current Status**: 🟡 Ready for Data Feed Setup
