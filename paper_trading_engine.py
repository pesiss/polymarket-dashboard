#!/usr/bin/env python3
"""
Polymarket Paper Trading Engine
Executes 3 complementary strategies in paper trading mode
"""

import json
import os
import time
from datetime import datetime, timedelta, UTC # Import UTC
from typing import Dict, List
import hashlib
import uuid
import random

# Configuration
POLYMARKET_API = "https://clob.polymarket.com"
TELEGRAM_CHAT_ID = "5118179564"
TELEGRAM_API_URL = "https://api.telegram.org"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Paper trading state
TRADES_FILE = "/home/pesiss/.openclaw/agents/polymarket/trades.json"

class PolymarketPaperTrader:
    def __init__(self):
        self.capital = 1000
        self.trades = []
        self.load_state()
        
    def load_state(self):
        """Load previous trading state from file"""
        if os.path.exists(TRADES_FILE):
            with open(TRADES_FILE, 'r') as f:
                state = json.load(f)
                self.capital = state.get('paper_capital', 1000)
                self.trades = state.get('trades', [])
        
    def save_state(self):
        """Save trading state to file"""
        state = {
            "paper_capital": self.capital,
            "reserved_capital": self.RESERVED_CAPITAL,
            "reserved_capital_note": self.RESERVED_CAPITAL_NOTE,
            "allocated": {
                "whale_copy_trading": 75,
                "whale_copy_trading_v2": 75,
                "settlement_edge": 150,
                "oracle_lag_exploit": 100
            },
            "portfolio": {
                "total_value": self.capital,
                "cash_available": self.capital,
                "open_positions": len([t for t in self.trades if t["status"] == "OPEN"]),
                "closed_positions": len([t for t in self.trades if t["status"] == "CLOSED"]),
                "total_pnl": sum([t.get("actual_profit", 0) for t in self.trades if t["status"] == "CLOSED"]),
                "total_roi": (sum([t.get("actual_profit", 0) for t in self.trades if t["status"] == "CLOSED"]) / self.capital * 100) if self.capital > 0 else 0
            },
            "trades": self.trades,
            "performance": self.calculate_performance(),
            "last_updated": datetime.now(UTC).isoformat(), # Updated to datetime.now(UTC)
            "status": "LIVE",
            "active_strategies": 4,
            "removed_strategies": ["binary_complement_arb", "catalyst_momentum", "favorite_compounder"]
        }
        
        with open(TRADES_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    
    def calculate_performance(self) -> Dict:
        """Calculate performance metrics per strategy (4 active strategies)"""
        performance = {
            "whale_copy_trading": {"trades": 0, "wins": 0, "losses": 0, "win_rate": 0, "total_pnl": 0, "max_drawdown": 0},
            "whale_copy_trading_v2": {"trades": 0, "wins": 0, "losses": 0, "win_rate": 0, "total_pnl": 0, "max_drawdown": 0},
            "settlement_edge": {"trades": 0, "wins": 0, "losses": 0, "win_rate": 0, "total_pnl": 0, "max_drawdown": 0},
            "oracle_lag_exploit": {"trades": 0, "wins": 0, "losses": 0, "win_rate": 0, "total_pnl": 0, "max_drawdown": 0}
        }
        
        for strategy_key in performance.keys():
            # Map strategy names to keys
            strategy_name_map = {
                "whale_copy_trading": "Whale Copy-Trading",
                "whale_copy_trading_v2": "Whale Copy-Trading v2",
                "settlement_edge": "Settlement Edge",
                "oracle_lag_exploit": "Oracle Lag Exploit"
            }
            
            target_strategy = strategy_name_map.get(strategy_key, strategy_key)
            strategy_trades = [t for t in self.trades if t["strategy"] == target_strategy]
            closed_trades = [t for t in strategy_trades if t["status"] == "CLOSED"]
            
            if strategy_trades:
                performance[strategy_key]["trades"] = len(closed_trades)
                performance[strategy_key]["wins"] = len([t for t in closed_trades if t.get("actual_profit", 0) > 0])
                performance[strategy_key]["losses"] = len([t for t in closed_trades if t.get("actual_profit", 0) < 0])
                
                if closed_trades:
                    performance[strategy_key]["win_rate"] = (performance[strategy_key]["wins"] / len(closed_trades) * 100) if closed_trades else 0
                    performance[strategy_key]["total_pnl"] = sum([t.get("actual_profit", 0) for t in closed_trades])
        
        return performance
    
    # Reserved capital from removed strategies (preserved for future deployment)
    RESERVED_CAPITAL = 1000  # $1,000 from binary_complement_arb ($300) + catalyst_momentum ($400) + favorite_compounder ($300)
    RESERVED_CAPITAL_NOTE = "Reserved for future strategy deployment"

    # NEW: Strategy parameters for trade resolution (4 active strategies)
    STRATEGY_PARAMS = {
        "Whale Copy-Trading": {"win_rate": 0.70, "avg_profit": 0.15, "avg_loss": -0.08, "sl_pct": 0.08, "tp_pct": 0.20, "max_hold_days": 2},
        "Whale Copy-Trading v2": {"win_rate": 0.70, "avg_profit": 0.15, "avg_loss": -0.06, "sl_pct": 0.06, "tp_pct": 0.20, "max_hold_days": 2},
        "Settlement Edge": {"win_rate": 0.75, "avg_profit": 0.10, "avg_loss": -0.05, "sl_pct": 0.035, "tp_pct": 0.15, "max_hold_days": 15},  # Musk optimized: 3.5% SL
        "Oracle Lag Exploit": {"win_rate": 0.72, "avg_profit": 0.25, "avg_loss": -0.08, "sl_pct": 0.08, "tp_pct": 0.30, "max_hold_days": 0.1}  # ~2.4 hours max hold
    }

    def get_strategy_params(self, strategy_name: str) -> Dict:
        return self.STRATEGY_PARAMS.get(strategy_name, {})

    def fetch_polymarket_data(self) -> List[Dict]:
        """Generate simulated market data for paper trading"""
        # In production, this would fetch from Polymarket API
        # For paper trading, we generate realistic-looking data
        
        markets = [
            {
                "id": "market_1",
                "type": "binary",
                "question": "Will Bitcoin exceed $100,000 by end of 2026?",
                "yes_price": 0.67,
                "no_price": 0.33,
                "days_to_expiry": 340
            },
            {
                "id": "market_2",
                "type": "binary",
                "question": "Will the Fed cut rates in Q1 2026?",
                "yes_price": 0.42,
                "no_price": 0.58,
                "days_to_expiry": 30
            },
            {
                "id": "market_3",
                "type": "binary",
                "question": "Will Ethereum ETF be approved by June 2026?",
                "yes_price": 0.78,
                "no_price": 0.22,
                "days_to_expiry": 120
            },
            {
                "id": "market_4",
                "type": "binary",
                "question": "Will Solana exceed $500 by end of 2026?",
                "yes_price": 0.45,
                "no_price": 0.55,
                "days_to_expiry": 310
            },
            {
                "id": "market_5",
                "type": "binary",
                "question": "Will there be a crypto market crash >30% in 2026?",
                "yes_price": 0.38,
                "no_price": 0.62,
                "days_to_expiry": 310
            }
        ]
        
        return markets
    
    def scan_whale_copy_trading(self) -> List[Dict]:
        """Scan for catalyst momentum opportunities (news-driven repricing)"""
        # In real implementation, would connect to news feeds (Twitter, Reddit, etc.)
        # For paper trading, we'll simulate based on recent market movements
        opportunities = []
        
        # Placeholder: In production, integrate with:
        # - Twitter API for crypto news
        # - Reddit API for sentiment
        # - CoinGecko/CoinMarketCap for major events
        
        return opportunities
    
    def scan_whale_copy_trading(self) -> List[Dict]:
        """Scan for whale trading signals"""
        # In production, would monitor Polymarket leaderboard + blockchain
        # Track top wallets (>$100k PnL, >60% win rate)
        # For paper trading, simulate whale positions
        opportunities = []
        
        # Simulated whale trades
        whale_signals = [
            {
                "whale": "Theo4",
                "market_id": "market_1",
                "market_name": "Will Bitcoin exceed $100,000 by end of 2026?",
                "side": "YES",
                "amount": 50000,
                "entry_price": 0.67,
                "lifetime_pnl": 22000000,
                "win_rate": 72
            }
        ]
        
        return whale_signals
    
    def scan_settlement_edge_trading(self) -> List[Dict]:
        """Scan for settlement rule mismatches vs market price"""
        # In production, deeply analyze resolution criteria vs market price
        # For paper trading, identify markets with rule ambiguities
        opportunities = []
        
        # Simulated rule-based opportunities
        rule_opportunities = [
            {
                "market_id": "market_5",
                "market_name": "Will there be a crypto market crash >30% in 2026?",
                "market_price": 0.38,
                "rules_based_price": 0.35,
                "edge": 0.03,
                "confidence": 0.75,
                "rule_notes": "30% crash = from current baseline, not from peak"
            }
        ]
        
        return rule_opportunities
    
    def scan_oracle_lag_exploit(self) -> List[Dict]:
        """Scan for information asymmetry between external outcome confirmation and oracle finalization"""
        # In production, would connect to:
        # - Sports APIs (ESPN, Sportradar) for live scores/results
        # - Politics APIs (AP News, Decision Desk) for election calls
        # - Macro APIs (Bloomberg, economic calendar) for data releases
        # - Crypto APIs for ETF/approval events
        opportunities = []
        
        # Simulated lag exploit opportunities (confirmed outcome but market hasn't priced in)
        lag_opportunities = [
            {
                "market_id": "market_1",
                "market_name": "Will Bitcoin exceed $100,000 by end of 2026?",
                "event_type": "crypto",
                "external_confirmation": "SEC ETF approval announced",
                "market_price_yes": 0.72,  # Market hasn't caught up yet (< 80%)
                "expected_price": 0.85,     # Should be higher given news
                "side": "YES",
                "edge": 0.13,
                "time_window_minutes": 45,
                "data_source": "crypto_api_placeholder"
            }
        ]
        
        return lag_opportunities
    
    def scan_liquidity_king(self, markets: List[Dict]) -> List[Dict]:
        """Market making strategy - provides liquidity on both sides of the order book"""
        # In production, would:
        # - Monitor order book depth
        # - Place maker orders 1-2% below/above mid price
        # - Capture bid-ask spread + liquidity rewards
        # - Dynamically manage inventory
        opportunities = []
        
        for market in markets:
            if market.get("type") != "binary":
                continue
            
            # Check market liquidity requirement ($10,000+)
            market_size = market.get("liquidity", 15000)  # Simulated liquidity
            if market_size < 10000:
                continue
            
            yes_price = float(market.get("yes_price", 0.5))
            no_price = float(market.get("no_price", 0.5))
            
            # Calculate mid price and spread
            mid_price = (yes_price + (1 - no_price)) / 2
            current_spread = abs(yes_price - (1 - no_price))
            
            # Only trade if spread is <= 2%
            if current_spread <= 0.02:
                # Calculate maker bid/ask (1-2% from mid)
                bid_price = max(0.01, mid_price * 0.985)  # 1.5% below mid
                ask_price = min(0.99, mid_price * 1.015)  # 1.5% above mid
                spread_capture = ask_price - bid_price
                
                opportunities.append({
                    "market_id": market.get("id"),
                    "market_name": market.get("question"),
                    "mid_price": mid_price,
                    "bid_price": bid_price,
                    "ask_price": ask_price,
                    "spread_capture": spread_capture,
                    "market_size": market_size,
                    "expected_round_trip_profit": spread_capture * 0.85  # After fees
                })
        
        return opportunities
    
    def execute_trade(self, strategy: str, market_id: str, market_name: str, side: str, 
                      entry_price: float, position_size: int) -> str:
        """Execute a paper trade"""
        trade_id = f"{strategy.split()[0][:3].upper()}_{uuid.uuid4().hex[:8].upper()}"
        
        params = self.get_strategy_params(strategy)

        trade = {
            "trade_id": trade_id,
            "timestamp": datetime.now(UTC).isoformat(), # Updated to datetime.now(UTC)
            "strategy": strategy,
            "market_id": market_id,
            "market_name": market_name,
            "side": side,
            "entry_price": entry_price,
            "position_size": position_size,
            "notional_value": entry_price * position_size,
            "expected_profit": None, 
            "status": "OPEN",
            "exit_price": None,
            "actual_profit": None,
            "resolved_at": None,
            "sl_pct": params.get("sl_pct", 0.0), # Ensure float
            "tp_pct": params.get("tp_pct", 0.0), # Ensure float
            "max_hold_days": params.get("max_hold_days", 0.0) # Ensure float
        }
        
        self.trades.append(trade)
        self.save_state()
        
        return trade_id
    
    def resolve_trades(self):
        """Simulate trade resolution (TP/SL/Time-based) for Polymarket strategies"""
        now = datetime.now(UTC)
        trades_to_process = [t for t in self.trades if t["status"] == "OPEN"]
        
        for trade in trades_to_process:
            entry_time_str = trade["timestamp"]
            # Handle cases where timestamp might not have timezone or is not isoformat initially
            try:
                entry_time = datetime.fromisoformat(entry_time_str)
            except ValueError:
                entry_time = datetime.strptime(entry_time_str, "%Y-%m-%dT%H:%M:%S.%f") # Fallback for no timezone
            
            max_hold_end = entry_time + timedelta(days=trade["max_hold_days"])
            
            # Apply slippage/spread simulation (0.5% assumed cost per trade for Polymarket)
            cost_factor = 0.005 

            # Simulate resolution based on win rate, TP/SL, and time
            params = self.get_strategy_params(trade["strategy"])
            
            # If max hold time passed, force close
            if now > max_hold_end and trade["max_hold_days"] > 0:
                # Simulate a small loss for time-based closures to reflect opportunity cost or slight adverse movement
                trade["actual_profit"] = trade["notional_value"] * params["avg_loss"] * 0.5 # Half average loss
                trade["status"] = "CLOSED"
                trade["resolved_at"] = now.isoformat()
                trade["exit_price"] = trade["entry_price"] * (1 + (params["avg_loss"] * 0.5))
                continue

            # Simulate a random check for TP/SL hit or win/loss based on strategy win rate
            # This simulates that not all trades resolve in a single cycle
            if random.random() < 0.2: # 20% chance to resolve per cycle to simulate progression
                is_win = random.random() < params["win_rate"]

                actual_pnl_pct = 0.0
                if is_win:
                    actual_pnl_pct = params["avg_profit"]
                else:
                    actual_pnl_pct = params["avg_loss"]
                
                # Adjust for simulated costs
                if actual_pnl_pct > 0: 
                    actual_pnl_pct -= cost_factor
                else: 
                    actual_pnl_pct -= cost_factor

                trade["actual_profit"] = trade["notional_value"] * actual_pnl_pct
                trade["resolved_at"] = now.isoformat()
                trade["status"] = "CLOSED"
                trade["exit_price"] = trade["entry_price"] * (1 + actual_pnl_pct) # Simulate exit price

        self.save_state()

    def run_scan_cycle(self):
        """Run one complete scan cycle for all active strategies (4 strategies)"""
        print(f"[{datetime.now(UTC).isoformat()}] Starting scan cycle (4 active strategies)...") # Updated to datetime.now(UTC)
        print(f"  Reserved capital: ${self.RESERVED_CAPITAL} - {self.RESERVED_CAPITAL_NOTE}")
        
        # Resolve open trades first
        self.resolve_trades()

        # Fetch latest market data
        markets = self.fetch_polymarket_data()
        
        if not markets:
            print("No market data available. Retrying in 5 minutes...")
            return
        
        # Strategy 1: Whale Copy-Trading (v1 - 8% SL)
        whale_opps = self.scan_whale_copy_trading()
        if whale_opps:
            print(f"Found {len(whale_opps)} whale trading signal(s)")
            for opp in whale_opps[:2]:
                # v1: 8% SL - 50% allocation ($75 if total $150)
                position_size_v1 = min(15, int(self.capital * 0.015 / opp["entry_price"]))
                trade_id_v1 = self.execute_trade(
                    strategy="Whale Copy-Trading",
                    market_id=opp["market_id"],
                    market_name=f"{opp['whale']} → {opp['market_name']}",
                    side=opp["side"],
                    entry_price=opp["entry_price"],
                    position_size=position_size_v1
                )
                print(f"  → Executed trade {trade_id_v1}: Following {opp['whale']} (v1 - 8% SL)")
                
                # v2: 6% SL - 50% allocation ($75 if total $150)
                position_size_v2 = min(15, int(self.capital * 0.015 / opp["entry_price"]))
                trade_id_v2 = self.execute_trade(
                    strategy="Whale Copy-Trading v2",
                    market_id=opp["market_id"],
                    market_name=f"{opp['whale']} → {opp['market_name']}",
                    side=opp["side"],
                    entry_price=opp["entry_price"],
                    position_size=position_size_v2
                )
                print(f"  → Executed trade {trade_id_v2}: Following {opp['whale']} (v2 - 6% SL)")
        
        # Strategy 2: Settlement Edge Trading
        settlement_opps = self.scan_settlement_edge_trading()
        if settlement_opps:
            print(f"Found {len(settlement_opps)} settlement edge opportunity/opportunities")
            for opp in settlement_opps[:2]:
                if opp["edge"] > 0.02:  # Only if >2% edge
                    position_size = min(25, int(self.capital * 0.015 / opp["market_price"]))
                    trade_id = self.execute_trade(
                        strategy="Settlement Edge",
                        market_id=opp["market_id"],
                        market_name=opp["market_name"],
                        side="YES" if opp["rules_based_price"] > opp["market_price"] else "NO",
                        entry_price=opp["market_price"],
                        position_size=position_size
                    )
                    print(f"  → Executed settlement edge trade {trade_id}: {opp['edge']*100:.1f}% edge")
        
        # Strategy 3: Oracle Lag Exploit
        lag_opps = self.scan_oracle_lag_exploit()
        if lag_opps:
            print(f"Found {len(lag_opps)} oracle lag exploit opportunity/opportunities")
            for opp in lag_opps[:2]:
                # Entry: When external data confirms outcome but market price < 80% (for YES) or > 20% (for NO)
                if opp["side"] == "YES" and opp["market_price_yes"] < 0.80:
                    position_size = min(63, int(self.capital * 0.063 / opp["market_price_yes"]))  # 6.3% of capital
                    trade_id = self.execute_trade(
                        strategy="Oracle Lag Exploit",
                        market_id=opp["market_id"],
                        market_name=f"[LAG] {opp['market_name']}",
                        side="YES",
                        entry_price=opp["market_price_yes"],
                        position_size=position_size
                    )
                    print(f"  → Executed oracle lag trade {trade_id}: {opp['edge']*100:.1f}% edge on {opp['event_type']}")
                elif opp["side"] == "NO" and opp["market_price_yes"] > 0.20:
                    no_price = 1 - opp["market_price_yes"]
                    position_size = min(63, int(self.capital * 0.063 / no_price))
                    trade_id = self.execute_trade(
                        strategy="Oracle Lag Exploit",
                        market_id=opp["market_id"],
                        market_name=f"[LAG] {opp['market_name']}",
                        side="NO",
                        entry_price=no_price,
                        position_size=position_size
                    )
                    print(f"  → Executed oracle lag trade {trade_id}: {opp['edge']*100:.1f}% edge on {opp['event_type']}")
        
        self.save_state()
        print(f"Scan cycle complete. Total trades: {len(self.trades)}")
    
    def generate_daily_report(self) -> str:
        """Generate daily performance report"""
        perf = self.calculate_performance()
        
        total_trades = sum([p["trades"] for p in perf.values()])
        total_wins = sum([p["wins"] for p in perf.values()])
        total_losses = sum([p["losses"] for p in perf.values()])
        total_pnl = sum([t.get("actual_profit", 0) for t in self.trades if t["status"] == "CLOSED"])
        
        overall_win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        roi = (total_pnl / self.capital * 100) if self.capital > 0 else 0
        
        report = f"""
📊 **Polymarket Paper Trading Daily Report**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Portfolio Summary**
• Capital: ${self.capital:.2f}
• Reserved Capital: ${self.RESERVED_CAPITAL:.2f} - {self.RESERVED_CAPITAL_NOTE}
• Total P&L: ${total_pnl:.2f}
• ROI: {roi:.2f}%
• Win Rate: {overall_win_rate:.1f}%
• Active Strategies: 4

**Strategy Breakdown**
1️⃣ **Whale Copy-Trading (v1 - 8% SL)**
   • Trades: {perf['whale_copy_trading']['trades']}
   • Win Rate: {perf['whale_copy_trading']['win_rate']:.1f}%
   • P&L: ${perf['whale_copy_trading']['total_pnl']:.2f}

2️⃣ **Whale Copy-Trading v2 (6% SL)**
   • Trades: {perf['whale_copy_trading_v2']['trades']}
   • Win Rate: {perf['whale_copy_trading_v2']['win_rate']:.1f}%
   • P&L: ${perf['whale_copy_trading_v2']['total_pnl']:.2f}

3️⃣ **Settlement Edge Trading**
   • Trades: {perf['settlement_edge']['trades']}
   • Win Rate: {perf['settlement_edge']['win_rate']:.1f}%
   • P&L: ${perf['settlement_edge']['total_pnl']:.2f}

4️⃣ **Oracle Lag Exploit**
   • Trades: {perf['oracle_lag_exploit']['trades']}
   • Win Rate: {perf['oracle_lag_exploit']['win_rate']:.1f}%
   • P&L: ${perf['oracle_lag_exploit']['total_pnl']:.2f}

**Status:** ✅ Paper trading LIVE
**Next Report:** Next 24 hours
"""
        return report

if __name__ == "__main__":
    trader = PolymarketPaperTrader()
    
    print("🚀 Polymarket Paper Trading Engine Started")
    print(f"Capital: ${trader.capital}")
    print(f"Reserved Capital: ${trader.RESERVED_CAPITAL} - {trader.RESERVED_CAPITAL_NOTE}")
    print(f"Scan Frequency: Every 5 minutes")
    print(f"Strategies Active: 4 (Whale Copy v1, Whale Copy v2, Settlement Edge, Oracle Lag)")
    print(f"Strategies Removed: 3 (Binary Complement Arb, Catalyst Momentum, Favorite Compounder)")
    print(f"A/B Testing: Whale Copy v1 (8% SL) vs v2 (6% SL) - Parallel execution")
    
    # Run initial scan
    trader.run_scan_cycle()
    
    # Generate initial report
    report = trader.generate_daily_report()
    print(report)
