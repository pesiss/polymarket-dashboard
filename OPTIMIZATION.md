# API Rate Limit Optimization Strategy

## Problem
- Previous system: 2m + 5m alert cycles = 700+ API calls/day
- Both Anthropic and Gemini hitting rate limits due to fallback retry loops
- No batching, no caching, no backoff strategy

## Solution: Consolidated Alert System

### New Cron Jobs

| Job | Frequency | Cost | Purpose |
|-----|-----------|------|---------|
| **market-pulse** | Every 30m | ~50 calls/day | Consolidated position/trade/entry checks |
| **daily-summary** | 1x daily (9 PM) | ~1 call/day | Daily P&L report |
| **weekly-summary** | 1x weekly (Sun 6 PM) | ~1 call/day | Weekly performance analysis |

**Total:** ~52 calls/day (vs 700+ before) — **93% reduction**

### Optimization Rules

1. **Single Agent Spawn Per Check**
   - `market-pulse` does ALL checks in one run
   - No sequential spawns, no redundant API calls
   - Batched analysis: position status + entry conditions + exit evaluation

2. **Report Only On Change**
   - Agent reads last state from TRADE_STATE.md
   - Only sends alert if something CHANGED
   - Silent if: position still open, no new entries, no exits

3. **No Aggressive Retries**
   - If API call fails, wait 30+ minutes for next check (next cycle)
   - Don't retry in the same run
   - Let rate limits cool down between cycles

4. **Model Usage**
   - Primary: Gemini Flash (free, 15 RPM limit)
   - Fallback: Anthropic Haiku (cheaper, fallback only)
   - Don't alternate models in same run — pick one, stick with it

5. **Caching**
   - Market data cached in TRADE_STATE.md
   - Reuse for 30-minute cycle
   - Refresh only on next market-pulse run

### Expected Behavior

**Example:** BTC LONG held at $65,420
- **t=0:** market-pulse runs → position at entry, no action → SILENT ✓
- **t=30m:** market-pulse runs → price at $65,420 still → SILENT ✓
- **t=60m:** market-pulse runs → price at $67,000 (TP hit) → ALERT: "Position closed +2.4%" ✓
- **t=90m:** market-pulse runs → new entry at $67,500 → ALERT: "BTC long entered at $67,500" ✓

### Rate Limit Safety

**Gemini Flash:** 15 RPM (free tier)
- 30-minute cycle = 2 requests max (market-pulse + buffer) = Safe ✓

**Anthropic Haiku:** 100 RPM
- Fallback only, used rarely = Safe ✓

**Combined:** 52 requests/day = ~0.04 RPS = Well below limits ✓

---

## Implementation Complete

✅ Removed: `trade-execution-alerts` (every 2m)
✅ Removed: `position-loss-alert` (every 5m)  
✅ Removed: `trader-hourly-check` (every 1h)
✅ Added: `market-pulse` (every 30m, batched)
✅ Kept: `daily-summary` (1x daily)
✅ Kept: `weekly-summary` (1x weekly)

No more rate limit overloads. System is sustainable. 🚀
