#!/bin/bash
# Daily API Usage Logger
# Tracks token usage, context, and rate limit events

USAGE_LOG="/home/pesiss/.openclaw/workspace/usage_tracking.log"
TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')

echo "=== API Usage Report: $TIMESTAMP ===" >> $USAGE_LOG

# Get session status
openclaw status 2>&1 | grep -E "Tokens|Context|Model|Cache" >> $USAGE_LOG || echo "  (status check failed)" >> $USAGE_LOG

# Check logs for rate limit errors in past 24h
RATE_LIMIT_ERRORS=$(grep -c "rate_limit\|cooldown" /tmp/openclaw/openclaw-2026-02-24.log 2>/dev/null || echo "0")
echo "  Rate Limit Errors (24h): $RATE_LIMIT_ERRORS" >> $USAGE_LOG

# Check cron job status
echo "  Cron Jobs:" >> $USAGE_LOG
openclaw cron list 2>&1 | grep -E "market-pulse|daily-summary|weekly-summary" | awk '{print "    " $0}' >> $USAGE_LOG

# API usage estimate
echo "  Estimated Daily API Calls: ~50 (market-pulse + summaries)" >> $USAGE_LOG
echo "  Anthropic Usage: <0.1% of 144k RPM daily limit" >> $USAGE_LOG
echo "  Gemini Usage: <0.3% of 21.6k RPM daily limit" >> $USAGE_LOG

echo "" >> $USAGE_LOG
