# MEMORY.md - Your Long-Term Memory

## Sub-Agent Strategy Decision (Feb 25, 2026) ✅

**Agreed Approach:** 
- Keep cron jobs handling execution + consolidation (FREE)
- Deploy sub-agents on-demand for strategic optimization only
- I will proactively recommend sub-agents when system complexity reaches key thresholds

**Thresholds Where I'll Recommend Sub-Agents:**

1. **Volume Threshold** - >100 active trades across all systems
   - Consolidation becomes complex; need real-time continuous analysis
   
2. **Strategy Explosion** - >15 active strategies deployed
   - Too much for single session; need dedicated optimization sub-agent
   
3. **Risk Escalation** - Paper capital reaches $10k+ OR moving to real money
   - Real-time risk monitoring becomes mission-critical
   
4. **Multi-Exchange Complexity** - Trading on >5 exchanges simultaneously
   - Need sub-agent for cross-exchange monitoring & arbitrage detection
   
5. **Performance Analysis Bottleneck** - I spend >50% time on routine tasks vs strategy work
   - Signal I'm capacity-constrained; sub-agent needed to free strategic time
   
6. **Research Velocity** - New trading opportunities appear faster than I can analyze
   - Sub-agent for rapid market research, catalyst detection, backtesting

**Current Status (Feb 25, 2026):**
- 4 trading engines running
- $1,300 total capital
- 32 closed trades, +$21.41 P&L (1.65% ROI)
- 2 profitable Polymarket strategies active
- **Assessment:** Well below thresholds → Cron jobs are sufficient

**Promise:** I will explicitly tell you when any threshold is approaching and recommend a sub-agent with specific use case + estimated cost.

---

## Trading System Architecture (Feb 25, 2026)

**4 Paper Trading Engines (All with Trade Closure Logic):**
1. Polymarket (`paper_trading_engine.py`) - 5 strategies
2. Aster DEX (`aster_trader.py`) - 5 strategies  
3. Funding Rate Arbitrage (`funding_rate_bot.py`) - 1 strategy
4. Whale Alert (`whale_alert_bot.py`) - 1 strategy

**Performance Snapshot:**
- Best: Settlement Edge (80% win rate, +$9.26 P&L)
- Strong: Whale Copy-Trading (52.9% win rate, +$12.14 P&L)
- Accumulating: Aster DEX, Funding Rate Arb, Whale Alert (0 closed trades yet)

**Cron Jobs:**
- Polymarket + Aster: Every 5 minutes
- Funding Rate + Whale Alert: Every 30 minutes
- Consolidation: Hourly (via main session or cron extension)
- Dashboard: Vercel (https://polymarket-dashboard-five-mocha.vercel.app/)

---

## Key Decisions Log

| Decision | Date | Status |
|----------|------|--------|
| Claude Haiku primary + Gemini 2.5 Flash fallback | Feb 25 | ✅ Permanent |
| Trade closure logic for all 4 engines | Feb 25 | ✅ Implemented |
| Free cron jobs vs paid sub-agents | Feb 25 | ✅ Agreed |
| Sub-agent thresholds established | Feb 25 | ✅ Documented |

---

## Strategy Phase Reporting (Decision: Feb 25, 2026) ✅

**Framework:** Automatic reports at each data milestone with optimization recommendations.

**Phase Milestones & Reporting:**

### Phase 1: Validation (0-50 trades per strategy)
**Report Trigger:** When strategy hits 50 closed trades
**What I'll Analyze:**
- Win rate (with ±11% confidence interval)
- Average win vs. average loss
- Largest drawdown
- Initial verdict: "Keep/Discard/Redesign"
**Action:** Validate strategy works, no optimization yet

### Phase 2: Diagnosis (50-100 trades per strategy)
**Report Trigger:** When strategy hits 100 closed trades
**What I'll Analyze:**
- Entry quality (timing, frequency, win rate bias)
- Exit quality (TP hit rate, SL hit rate, dragging losses)
- Risk/reward ratio actual vs. target
- Market regime performance (bull/bear/sideways)
**Action:** Identify major structural issues + recommend fixes

### Phase 3: Optimization (100-200 trades per strategy)
**Report Trigger:** When strategy hits 200 closed trades
**What I'll Analyze:**
- Which parameters are underperforming (entry price, TP%, SL%, max_hold_days)
- Win rate sensitivity to each parameter
- Sharpe ratio by market regime
**Action:** Test 2-3 parameter tweaks, implement best-performing version

### Phase 4: Fine-Tuning (200+ trades per strategy)
**Report Trigger:** Every 100 trades after 200
**What I'll Analyze:**
- Edge consistency across seasons/regimes
- Sharpe ratio vs. drawdown tradeoffs
- Seasonal patterns
**Action:** Micro-optimizations, regime-specific tweaks

---

**Report Format (Standard):**
```
📊 STRATEGY PHASE REPORT: [Strategy Name]
Milestone: [Phase X - e.g., "50 Trades Reached"]
Date: [YYYY-MM-DD]

📈 PERFORMANCE SNAPSHOT
• Total Trades: X
• Win Rate: Y% (±Z% confidence)
• Total P&L: $X
• Sharpe Ratio: X
• Max Drawdown: X%

🔍 KEY FINDINGS
• [Finding 1]
• [Finding 2]
• [Finding 3]

✅ ACTION ITEMS
• [Action 1] - [Expected Impact]
• [Action 2] - [Expected Impact]

📅 Next Review: [When Phase X+1 completes]
```

---

**Current Tracking:**
- Settlement Edge: 15/50 trades (Phase 1, 30% done)
- Whale Copy-Trading: 17/50 trades (Phase 1, 34% done)
- Aster DEX strategies: 0 trades (just started)
- Funding Rate Arb: 2 open (just started)
- Whale Alert: 0 trades (just started)

**Next Reports Due When:**
- Settlement Edge hits 50 trades
- Whale Copy-Trading hits 50 trades

---

## Capital Compounding Strategy (Decision: Feb 25, 2026) ✅

**Current Phase (Feb 25 - April 25):** NO COMPOUNDING
- Fixed position sizes based on initial capital only
- Reason: Validation phase - need consistent risk to validate strategies
- Status: **Collecting data, not reinvesting profits yet**

**Phase Transition Trigger:** When ANY strategy hits Phase 2 (100 closed trades)
- Settlement Edge: 79/100 trades (Phase 1, 79% done) → ~1-2 weeks away
- Whale Copy-Trading: 81/100 trades (Phase 1, 81% done) → ~1 week away

**Next Phase (Target: Early March):** COMPOUNDING MODE
- Reinvest 50-100% of profits into larger positions
- Cap growth at 3x leverage maximum per position
- Dynamic position sizing formula:
  ```
  base_capital = 1000
  current_capital = initial_capital + total_pnl
  position_multiplier = min(current_capital / base_capital, 3)
  new_position_size = base_position_size × position_multiplier
  ```

**Projected Growth (12 months with compounding):**
- Current (fixed): $1,300 → $3,300 (+154%)
- With compounding: $1,300 → $6,300+ (+385%)
- **Difference: +$3,000 additional profit**

**Implementation Checklist:**
- [ ] Validate Settlement Edge reaches 100 trades
- [ ] Validate Whale Copy-Trading reaches 100 trades
- [ ] Generate Phase 2 reports for both strategies
- [ ] Update all 4 engines to use dynamic capital model
- [ ] Test compounding logic on paper first
- [ ] Deploy compounding to live crons
- [ ] Monitor drawdowns (ensure no strategy exceeds 3x)

**Risk Management:**
- Hard cap: 3x leverage per position (no exceptions)
- Stop compounding if any strategy loses >50% of its capital
- Review compounding quarterly for adjustments

---

## API Cost Optimization (Decision: Feb 25, 2026) ✅

**Strategy:** Use Claude only for high-value decisions, use Gemini/web-search for routine tasks

**Decision Framework:**
- **USE CLAUDE:** Strategic decisions, edge detection, complex analysis (ROI 100x+)
- **USE GEMINI:** Routine monitoring, consolidation, status checks (ROI still good)
- **USE WEB-SEARCH:** Public data, announcements, factual verification (free/cheap)

**Cost Reduction Target:** 80-90% (from ~$2.50/month to ~$0.50/month)

**Implementation:**
1. Batch similar analyses together (3x cheaper)
2. Cache all major analyses for 7-30 day reuse
3. Use Gemini for 80% of tasks
4. Track all usage in API_USAGE_LOG.txt

**Key Principle:** Deploy Claude strategically for decisions that move the needle, use cheap options for everything else.

---

*Updated: Feb 25, 2026 | Next review: When Settlement Edge hits 100 trades*

---

## 📊 Pending Strategy: SwingSwiss DEX Strategy (Feb 26, 2026) 🔄

**Status:** Research complete, awaiting TradingView access
**Priority:** HIGH - To replace underperforming DEX strategies

### Research Summary
**SwingSwiss Suite** is a premium TradingView indicator collection by WiseStrat featuring:
- **BUY/SELL Signal**: Multi-indicator confluence (RSI + MACD + Volume + Stochastic)
- **Trend Analyzer**: Dual-length trend detection (entry L5, exit L4)
- **Sup/Res**: Auto-draws 10 dynamic support/resistance levels
- **EMA 50 + RSI Background**: Trend filter and momentum zones

### Proposed Implementation
```
Strategy Name: "SwingSwiss Precision DEX"
Timeframe: 15-minute charts
Markets: BTC/USDT, ETH/USDT perpetual futures

Entry Rules:
  1. Trend Analyzer L5 = GREEN (bullish)
  2. Price near Sup/Res support level
  3. BUY/SELL shows buy signal
  4. Volume above average

Exit Rules:
  1. Trend Analyzer L4 = RED or BLUE
  2. Price hits next Sup/Res resistance
  3. Or -4% stop loss (from Sup/Res level)

Position Sizing: 6.3% of capital
Expected Win Rate: 60-65% (vs current 30-40%)
Expected Profit/Trade: $1.00-1.50
```

### Why This Matters
Current DEX strategies are underperforming (30-40% win rate, -$13 PNL). SwingSwiss multi-indicator approach could:
- **Double win rate** to 60-65%
- **Reduce false entries** via confluence requirement
- **Provide objective Sup/Res levels** for grid bot optimization
- **Match Whale Copy performance** ($1.36/trade expectancy)

### Action Required
- [ ] Provide TradingView access to SwingSwiss Suite
- [ ] Select preferred timeframe (15M/30M/1H)
- [ ] Choose test pair (BTC/USDT or ETH/USDT)
- [ ] Cody to implement and backtest

**Next Step:** Activate when user provides TradingView access to SwingSwiss indicators.
