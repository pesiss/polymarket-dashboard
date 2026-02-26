#!/bin/bash
# Automatic consolidation + GitHub push
# Runs hourly via cron

WORKSPACE="/home/pesiss/.openclaw/workspace"
LOG_FILE="$WORKSPACE/consolidation.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S UTC')

echo "[$TIMESTAMP] Starting consolidation..." >> $LOG_FILE

# Run consolidation
cd $WORKSPACE
python3 consolidate_trades.py >> $LOG_FILE 2>&1

# Get new P&L
PNL=$(python3 << 'EOF'
import json
try:
    with open("all_trades.json", 'r') as f:
        data = json.load(f)
    print(f"P&L: ${data.get('total_pnl', 0):.2f} | ROI: {data.get('total_roi', 0):.1f}% | Closed: {data.get('closed_positions', 0)}")
except:
    print("Error reading trades")
EOF
)

echo "Result: $PNL" >> $LOG_FILE

# Push to GitHub
git add all_trades.json >> $LOG_FILE 2>&1
git commit -m "Auto: Consolidate trades [$TIMESTAMP] - $PNL" >> $LOG_FILE 2>&1
git push origin main >> $LOG_FILE 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Consolidation + Push SUCCESS at $TIMESTAMP" >> $LOG_FILE
else
    echo "❌ Push failed at $TIMESTAMP" >> $LOG_FILE
fi

echo "" >> $LOG_FILE
