# ✅ AUTOMATIC CONSOLIDATION SETUP
## Hourly Trade Data Updates → Vercel Dashboard

**Date:** Feb 25, 2026
**Status:** ✅ ACTIVE
**Frequency:** Every hour at the top of the hour (00 minutes)

---

## 🎯 WHAT THIS DOES

Every hour, automatically:

1. **Consolidates trade data** from all 4 trading engines
   - Polymarket (`/trades.json`)
   - Aster DEX (`/aster_trades.json`)
   - Funding Rate (`/funding_trades.json`)
   - Whale Alert (`/whale_trades.json`)

2. **Generates updated `all_trades.json`** with:
   - Total P&L
   - Total ROI
   - Closed/Open positions
   - Per-strategy performance
   - Timestamp

3. **Pushes to GitHub** automatically
   - Git add, commit, push all in one script
   - Vercel auto-deploys on push
   - Dashboard updates 1-2 minutes later

4. **Logs all activity** for monitoring
   - Consolidation status
   - P&L snapshot
   - Push success/failure

---

## ⚙️ CRON JOB DETAILS

**Schedule:** `0 * * * * /home/pesiss/.openclaw/workspace/consolidate_and_push.sh`

**Translation:**
- `0` = At minute 0 (top of the hour)
- `*` = Every hour
- `*` = Every day of month
- `*` = Every month
- `*` = Every day of week

**Runs at:**
- 00:00 UTC
- 01:00 UTC
- 02:00 UTC
- ... (every hour)
- 23:00 UTC

---

## 📊 WHAT GETS LOGGED

Each run logs to: `/home/pesiss/.openclaw/workspace/consolidation.log`

**Example log entry:**
```
[2026-02-25 16:00:00 UTC] Starting consolidation...
Result: P&L: $194.03 | ROI: 14.93% | Closed: 219
✅ Consolidation + Push SUCCESS at 2026-02-25 16:00:00 UTC
```

---

## 📈 EFFECT ON YOUR DASHBOARD

### Before (Manual Consolidation)
- P&L updates only when you manually consolidate
- Can lag by 1-2 hours if you forget
- Vercel shows stale data

### After (Automatic Consolidation)
- P&L updates every hour automatically
- Max lag: ~1 hour (until next cron run)
- Vercel always shows fresh data within 1 hour

---

## 🔍 HOW TO MONITOR

### Check the consolidation log:
```bash
tail -20 /home/pesiss/.openclaw/workspace/consolidation.log
```

### See recent updates:
```bash
tail -50 /home/pesiss/.openclaw/workspace/consolidation.log | head -30
```

### Check cron job is active:
```bash
crontab -l | grep consolidate_and_push
```

---

## 🛠️ IF SOMETHING BREAKS

### Check if script runs manually:
```bash
bash /home/pesiss/.openclaw/workspace/consolidate_and_push.sh
```

### Check git is configured:
```bash
git config user.email
git config user.name
```

### Check cron logs (on some systems):
```bash
grep consolidate_and_push /var/log/syslog
# or
log show --predicate 'process == "cron"' | tail -20
```

### Manually run consolidation:
```bash
cd /home/pesiss/.openclaw/workspace && python3 consolidate_trades.py && git add all_trades.json && git commit -m "Manual consolidation" && git push origin main
```

---

## 📝 CONSOLE OUTPUT DURING RUNS

You won't see output in the terminal (cron runs silently), but:

✅ The script creates/updates `/consolidation.log`
✅ The script pushes to GitHub (you can see commits)
✅ Vercel deploys automatically (check https://vercel.com/dashboard)

---

## 🎯 DASHBOARD UPDATE TIMELINE

**Trades close** → `consolidation.log` captures update → GitHub push happens → Vercel updates → Your dashboard reflects new P&L

**Total time: 1-5 minutes after each trade closes (within hourly window)**

---

## ✨ KEY BENEFITS

✅ **No manual work** - Consolidation happens automatically
✅ **Always fresh** - Vercel updated every hour
✅ **Reliable** - Cron runs consistently
✅ **Auditable** - All runs logged with timestamps
✅ **Low overhead** - Runs for <30 seconds each hour

---

## 🚀 ACTIVATION

**Status:** ✅ **LIVE NOW**

Cron job added:
```
0 * * * * /home/pesiss/.openclaw/workspace/consolidate_and_push.sh
```

**Next run:** Top of next hour
**Log file:** `/home/pesiss/.openclaw/workspace/consolidation.log`

---

## 📊 EXAMPLE FLOW

```
14:00 UTC - Trading engines execute trades
            New trades close, P&L updates in trade files

15:00 UTC - CRON JOB TRIGGERS
            1. Consolidates all 4 engines' trades
            2. Generates all_trades.json
            3. Git push to GitHub
            4. Vercel auto-deploys
            5. Dashboard refreshes (1-2 min later)

15:02 UTC - Your dashboard shows updated P&L

16:00 UTC - Next cron job runs (repeat)
```

---

## 🎊 RESULT

**Your Vercel dashboard is now:**
- ✅ Always in sync with live trading data
- ✅ Updated automatically every hour
- ✅ No manual consolidation needed
- ✅ Ready to scale with more trading engines

---

*Automatic Consolidation Activated: Feb 25, 2026*
*Schedule: Hourly at top of hour*
*Next run: [Next :00 UTC]*
*Status: ✅ ACTIVE*
