#!/bin/bash
# Quick Status Check for Paper Trading

echo "╔════════════════════════════════════════════════════════════╗"
echo "║      POLYMARKET PAPER TRADING - QUICK STATUS CHECK        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if paper trades file exists
if [ ! -f "/home/pesiss/.openclaw/agents/polymarket/paper_trades.json" ]; then
    echo "❌ Paper trading not initialized yet"
    exit 1
fi

# Extract key metrics from JSON
echo "📊 CURRENT PORTFOLIO:"
echo ""

python3 << 'EOF'
import json

with open("/home/pesiss/.openclaw/agents/polymarket/paper_trades.json", 'r') as f:
    data = json.load(f)

open_trades = [t for t in data['trades'] if t['status'] == 'OPEN']
closed_trades = [t for t in data['trades'] if t['status'] == 'CLOSED']

total_pnl = sum([t.get('pnl', 0) for t in closed_trades])
wins = len([t for t in closed_trades if t.get('outcome') == 'WIN'])
losses = len([t for t in closed_trades if t.get('outcome') == 'LOSS'])

print(f"Initial Capital:     $50.00")
print(f"Total Invested:      ${sum([t['position_size'] for t in open_trades]):.2f}")
print(f"Total P&L:          ${total_pnl:+.2f}")
print(f"ROI:                {(total_pnl / 50 * 100):+.1f}%")
print("")
print(f"Open Trades:        {len(open_trades)}")
print(f"Closed Trades:      {len(closed_trades)}")
print(f"Win Rate:           {(wins / len(closed_trades) * 100) if closed_trades else 0:.1f}% ({wins}W/{losses}L)")
print("")
print("📈 BY STRATEGY:")

# Group by strategy
strategies = {}
for trade in open_trades + closed_trades:
    strat = trade['market_name'].split('-')[0]
    if strat not in strategies:
        strategies[strat] = {'open': 0, 'closed': 0, 'pnl': 0, 'wins': 0}
    
    if trade['status'] == 'OPEN':
        strategies[strat]['open'] += 1
    else:
        strategies[strat]['closed'] += 1
        strategies[strat]['pnl'] += trade.get('pnl', 0)
        if trade.get('outcome') == 'WIN':
            strategies[strat]['wins'] += 1

for strat, metrics in sorted(strategies.items()):
    print(f"\n{strat}:")
    print(f"  Open: {metrics['open']}, Closed: {metrics['closed']}")
    if metrics['closed'] > 0:
        wr = metrics['wins'] / metrics['closed'] * 100
        print(f"  P&L: ${metrics['pnl']:+.2f} | Win Rate: {wr:.0f}%")

print("\n" + "="*60)
print(f"Last Updated: {data['last_updated']}")
print("="*60)

EOF

echo ""
echo "✅ Status check complete"
echo ""
echo "For detailed report, run:"
echo "  cat /home/pesiss/.openclaw/agents/polymarket/paper_trading_report.txt"
