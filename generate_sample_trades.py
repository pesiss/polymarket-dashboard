#!/usr/bin/env python3
"""
Generate 10 sample trades following Late Entry strategy
For dashboard demo and Vercel deployment
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path("polymarket_data")
DATA_DIR.mkdir(exist_ok=True)

# Generate 10 realistic trades with Late Entry strategy characteristics
trades_data = {
    "strategy": "Late Entry (81% Win Rate)",
    "total_capital": 1000.0,
    "current_capital": 1000.0,
    "trades": [],
    "win_count": 0,
    "loss_count": 0,
    "consecutive_losses": 0,
    "circuit_breaker_triggered": False
}

# Sample trades with realistic Late Entry behavior
sample_trades = [
    {"market": "Bitcoin Up by 10% (24h)", "entry": 0.32, "exit": 0.68, "position": 20},
    {"market": "Ethereum Up by 5% (12h)", "entry": 0.38, "exit": 0.65, "position": 20},
    {"market": "Solana Up by 3% (6h)", "entry": 0.35, "exit": 0.62, "position": 20},
    {"market": "Bitcoin Up by 15% (48h)", "entry": 0.30, "exit": 0.70, "position": 20},
    {"market": "Ethereum Up by 8% (24h)", "entry": 0.42, "exit": 0.48, "position": 20},
    {"market": "Solana Up by 5% (12h)", "entry": 0.34, "exit": 0.69, "position": 20},
    {"market": "Bitcoin Up by 7% (6h)", "entry": 0.36, "exit": 0.55, "position": 20},
    {"market": "Ethereum Up by 10% (24h)", "entry": 0.33, "exit": 0.71, "position": 20},
    {"market": "Solana Up by 4% (12h)", "entry": 0.39, "exit": 0.50, "position": 20},
    {"market": "Bitcoin Up by 12% (48h)", "entry": 0.31, "exit": 0.72, "position": 20},
]

base_time = datetime.now(timezone.utc) - timedelta(hours=50)

for i, trade_data in enumerate(sample_trades):
    entry_time = base_time + timedelta(hours=i*5)
    exit_time = entry_time + timedelta(hours=4)
    
    entry_price = trade_data["entry"]
    exit_price = trade_data["exit"]
    position_size = trade_data["position"]
    
    # Calculate P&L
    pnl = (exit_price - entry_price) * position_size / entry_price
    is_win = pnl > 0
    
    trade = {
        "id": i + 1,
        "market": trade_data["market"],
        "entry_price": entry_price,
        "exit_price": exit_price,
        "entry_time": entry_time.isoformat(),
        "exit_time": exit_time.isoformat(),
        "position_size": position_size,
        "pnl": round(pnl, 2),
        "pnl_percent": round((pnl / position_size) * 100, 2),
        "status": "CLOSED",
        "is_win": is_win
    }
    
    trades_data["trades"].append(trade)
    
    if is_win:
        trades_data["win_count"] += 1
        trades_data["consecutive_losses"] = 0
    else:
        trades_data["loss_count"] += 1
        trades_data["consecutive_losses"] += 1
    
    trades_data["current_capital"] += pnl

# Calculate final stats
trades_data["total_pnl"] = trades_data["current_capital"] - trades_data["total_capital"]
trades_data["total_pnl_percent"] = (trades_data["total_pnl"] / trades_data["total_capital"]) * 100
total_trades = trades_data["win_count"] + trades_data["loss_count"]
trades_data["win_rate"] = (trades_data["win_count"] / total_trades * 100) if total_trades > 0 else 0

# Save to file
with open(DATA_DIR / "trades.json", 'w') as f:
    json.dump(trades_data, f, indent=2)

print("✅ Generated 10 sample trades")
print(f"   Win Rate: {trades_data['win_rate']:.1f}%")
print(f"   Total P&L: ${trades_data['total_pnl']:+.2f} ({trades_data['total_pnl_percent']:+.1f}%)")
print(f"   Final Capital: ${trades_data['current_capital']:.2f}")
