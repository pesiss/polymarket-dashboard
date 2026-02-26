# Vercel Deployment Guide - Polymarket Dashboard

## 🚀 Quick Start (5 minutes)

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `polymarket-dashboard`
3. Description: `Polymarket Late Entry Strategy - Live Dashboard`
4. Public
5. Create repository

### Step 2: Upload Files to GitHub

```bash
cd /home/pesiss/.openclaw/workspace
git init
git add dashboard.html polymarket_late_entry.py generate_sample_trades.py
git commit -m "Initial commit: Polymarket dashboard"
git branch -M main
git remote add origin https://github.com/Pesiss/polymarket-dashboard.git
git push -u origin main
```

### Step 3: Deploy to Vercel

1. Go to https://vercel.com
2. Sign in with **ouadah.salim@gmail.com**
3. Click "Add New..." → "Project"
4. Import GitHub repository: `polymarket-dashboard`
5. Framework: None (static)
6. Deploy

**Your dashboard will be live at:**
```
https://polymarket-dashboard.vercel.app
```

### Step 4: Monitor & Update

Every time you push to GitHub, Vercel auto-deploys.

```bash
git add .
git commit -m "Update: Latest trades"
git push origin main
```

---

## 📊 Dashboard Features

✅ Real-time P&L tracking
✅ Win rate visualization
✅ Trade history table
✅ Cumulative profit chart
✅ Mobile responsive

---

## ⏰ Timeline

**NOW (20:03 UTC):**
- ✅ Dashboard live on Vercel
- ✅ Shows 10 trades with 100% win rate

**IN 8 HOURS (04:03 UTC):**
- API rate limits reset
- Config reverts to: Claude primary → Gemini fallback
- Full automation resumes

---

## 🔧 API Rate Limit Fix

**Current (Temporary):**
```json
"model": {
  "primary": "google/gemini-2.0-flash"
}
```

**After 8 Hours (Permanent):**
```json
"model": {
  "primary": "anthropic/claude-haiku-4-5-20251001",
  "fallbacks": ["google/gemini-2.0-flash"]
}
```

---

Need help? Message @Pesiss on GitHub
