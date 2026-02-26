#!/bin/bash
# Analyze API usage trends from usage_tracking.log

USAGE_LOG="/home/pesiss/.openclaw/workspace/usage_tracking.log"

if [ ! -f "$USAGE_LOG" ]; then
    echo "No usage log found. Run log_usage.sh first."
    exit 1
fi

echo "📊 API Usage Analysis"
echo "===================="
echo ""

# Count log entries
ENTRIES=$(grep -c "=== API Usage Report" "$USAGE_LOG")
echo "📋 Days Tracked: $ENTRIES"
echo ""

# Extract rate limit errors
echo "⚠️ Rate Limit Events:"
grep "Rate Limit Errors" "$USAGE_LOG" | tail -5
echo ""

# Show latest entry
echo "📈 Latest Report:"
tail -10 "$USAGE_LOG"
echo ""

echo "✅ Usage Tracking Active"
echo "   Daily log: $USAGE_LOG"
echo "   Cron job: daily-usage-log @ 10 PM UTC"
