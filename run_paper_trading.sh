#!/bin/bash
# Daily Paper Trading Runner
# Simulates Polymarket strategy execution

WORKSPACE="/home/pesiss/.openclaw/workspace"
POLYMARKET_DIR="/home/pesiss/.openclaw/agents/polymarket"
LOG_FILE="$WORKSPACE/paper_trading.log"

# Run paper trader
echo "[$(date '+%Y-%m-%d %H:%M:%S UTC')] Running paper trading simulation..." >> $LOG_FILE

cd $POLYMARKET_DIR && python3 polymarket_paper_trader.py >> $LOG_FILE 2>&1

# Append report to master log
echo "" >> $LOG_FILE
echo "========================================" >> $LOG_FILE
cat "$POLYMARKET_DIR/paper_trading_report.txt" >> $LOG_FILE
echo "========================================" >> $LOG_FILE
echo "" >> $LOG_FILE

echo "✅ Paper trading run completed at $(date)"
