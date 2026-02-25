#!/usr/bin/env python3
"""
Polymarket Paper Trading - Late Entry Strategy
Based on "The Better Traders" research (81% win rate)

Strategy: Wait for confirmation. Then strike.
- Only trade when market conditions are CLEAR
- Market regime filter: Skip choppy markets
- Circuit breaker: Stop after 3 consecutive losses
- Position cap: $20 max per trade
- API resilience: Timeouts + exponential backoff
"""

import requests
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
import time
import statistics

# ============================================================================
# CONFIGURATION
# ============================================================================

GAMMA_API = "https://gamma-api.polymarket.com"
MARKETS_ENDPOINT = f"{GAMMA_API}/markets"
DATA_DIR = Path("polymarket_data")

# Late Entry Strategy Parameters
POSITION_CAP = 20.0                    # $20 max per trade
CIRCUIT_BREAKER_LOSSES = 3             # Stop after 3 losses
STARTING_CAPITAL = 1000.0              # $1000 starting capital

# Confirmation Thresholds
CONFIRMATION_WINDOW = 4                # Last 4 hours must be green
MIN_VOLUME_MULTIPLIER = 1.2            # Volume > 20% above average

# Market Regime Filter
TREND_THRESHOLD = 25                   # ADX > 25 = trending
BB_THRESHOLD = 0.7                     # Bollinger Band width threshold

# Target Markets
TARGET_MARKETS = ["Bitcoin", "Ethereum", "Solana"]
TARGET_KEYWORDS = ["Up", "higher", "increase"]

# API Settings
MAX_RETRIES = 3
RETRY_DELAY = 1
API_TIMEOUT = 10


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_data_dir():
    """Initialize data directory"""
    DATA_DIR.mkdir(exist_ok=True)
    
    # Initialize trades log
    trades_file = DATA_DIR / "trades.json"
    if not trades_file.exists():
        with open(trades_file, 'w') as f:
            json.dump({
                "trades": [],
                "total_pnl": 0.0,
                "total_capital": STARTING_CAPITAL,
                "current_capital": STARTING_CAPITAL,
                "win_count": 0,
                "loss_count": 0,
                "win_rate": 0.0,
                "consecutive_losses": 0,
                "circuit_breaker_triggered": False,
                "strategy": "Late Entry (Wait for Confirmation)"
            }, f, indent=2)


# ============================================================================
# API CALLS WITH RESILIENCE
# ============================================================================

def fetch_markets_with_retry(limit=100) -> Optional[List[Dict]]:
    """Fetch markets with exponential backoff retry logic"""
    backoff = 1
    
    for attempt in range(MAX_RETRIES):
        try:
            params = {"limit": limit, "active": True}
            response = requests.get(
                MARKETS_ENDPOINT, 
                params=params, 
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            print(f"✅ Fetched {len(response.json())} markets")
            return response.json()
            
        except requests.exceptions.Timeout:
            print(f"⏱️ API timeout (attempt {attempt + 1}/{MAX_RETRIES})")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ API Error: {e} (attempt {attempt + 1}/{MAX_RETRIES})")
        
        if attempt < MAX_RETRIES - 1:
            print(f"   Waiting {backoff}s before retry...")
            time.sleep(backoff)
            backoff *= 2  # Exponential backoff
    
    return None


# ============================================================================
# MARKET DISCOVERY & FILTERING
# ============================================================================

def discover_crypto_markets() -> List[Dict]:
    """Find crypto markets matching our criteria"""
    all_markets = fetch_markets_with_retry()
    if not all_markets:
        print("❌ Failed to fetch markets")
        return []
    
    crypto_markets = []
    
    for market in all_markets:
        question = market.get("question", "").lower()
        
        # Filter: Contains target crypto + "Up" keyword
        if not any(crypto.lower() in question for crypto in TARGET_MARKETS):
            continue
        if not any(keyword.lower() in question for keyword in TARGET_KEYWORDS):
            continue
        
        # Parse prices
        prices_raw = market.get("outcomePrices", "")
        try:
            if isinstance(prices_raw, str):
                prices = json.loads(prices_raw)
            else:
                prices = prices_raw
            
            if not prices or len(prices) < 2:
                continue
            
            yes_price = float(prices[0]) if prices[0] else 0.0
            no_price = float(prices[1]) if prices[1] else 0.0
            
        except (json.JSONDecodeError, ValueError, TypeError):
            continue
        
        crypto_markets.append({
            "id": market.get("id"),
            "question": market.get("question"),
            "yes_price": yes_price,
            "no_price": no_price,
            "volume_24h": float(market.get("volume24h", 0)),
            "liquidity": float(market.get("liquidity", 0)),
            "end_date": market.get("endDate"),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    print(f"✅ Found {len(crypto_markets)} crypto markets")
    return crypto_markets


# ============================================================================
# LATE ENTRY STRATEGY
# ============================================================================

def assess_market_regime(yes_prices: List[float]) -> Dict[str, bool]:
    """
    Assess if market conditions are favorable for trading
    
    Returns:
        {
            "is_trending": bool,
            "volatility_healthy": bool,
            "ready_to_trade": bool
        }
    """
    if len(yes_prices) < 4:
        return {
            "is_trending": False,
            "volatility_healthy": False,
            "ready_to_trade": False
        }
    
    # Check if last 4 are green (uptrend)
    last_4 = yes_prices[-4:]
    is_green = all(last_4[i] <= last_4[i+1] for i in range(len(last_4)-1))
    
    # Check volatility (Bollinger Band proxy)
    price_stdev = statistics.stdev(yes_prices)
    avg_price = statistics.mean(yes_prices)
    bb_width = (price_stdev / avg_price) if avg_price > 0 else 0
    
    volatility_healthy = 0.01 < bb_width < 0.5  # Not too calm, not too chaotic
    
    return {
        "is_trending": is_green,
        "volatility_healthy": volatility_healthy,
        "ready_to_trade": is_green and volatility_healthy
    }


def check_late_entry_signal(market: Dict, regime: Dict) -> Dict:
    """
    Late Entry Logic:
    1. Market must be in favorable regime (trending + healthy vol)
    2. Price must be below entry threshold for LONG (mean reversion)
    3. High confidence signal required
    """
    yes_price = market["yes_price"]
    signal = {
        "action": "HOLD",
        "reasoning": "",
        "confidence": 0.0
    }
    
    if not regime["ready_to_trade"]:
        signal["reasoning"] = "Market regime not favorable (choppy or stalled)"
        return signal
    
    # Late Entry: Buy on pullback during uptrend
    # Entry: YES price < 0.35 (more selective than 0.40)
    if yes_price < 0.35 and regime["is_trending"]:
        signal["action"] = "BUY"
        signal["reasoning"] = f"Late entry: Pullback to ${yes_price:.3f} during uptrend"
        signal["confidence"] = 0.85  # High confidence on confirmed pullback
    
    # Exit: Sell at target price
    elif yes_price > 0.60:
        signal["action"] = "SELL"
        signal["reasoning"] = f"Target hit: YES at ${yes_price:.3f}"
        signal["confidence"] = 1.0
    
    return signal


# ============================================================================
# TRADE EXECUTION & TRACKING
# ============================================================================

def load_trades() -> Dict:
    """Load trade history"""
    trades_file = DATA_DIR / "trades.json"
    if trades_file.exists():
        with open(trades_file, 'r') as f:
            return json.load(f)
    return {}


def save_trade(entry_price: float, market_id: str, market_question: str):
    """Log a new trade (entry only, exit logged separately)"""
    trades = load_trades()
    
    trade = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "market_id": market_id,
        "market_question": market_question[:60],
        "entry_price": entry_price,
        "exit_price": None,
        "pnl": None,
        "status": "OPEN"
    }
    
    trades["trades"].append(trade)
    
    with open(DATA_DIR / "trades.json", 'w') as f:
        json.dump(trades, f, indent=2)
    
    print(f"📝 Trade entered: {market_question[:50]}... @ ${entry_price:.3f}")


def close_trade(trade_index: int, exit_price: float):
    """Close a trade and record P&L"""
    trades = load_trades()
    trade = trades["trades"][trade_index]
    
    entry_price = trade["entry_price"]
    pnl = (exit_price - entry_price) * POSITION_CAP / entry_price
    is_win = pnl > 0
    
    trade["exit_price"] = exit_price
    trade["pnl"] = pnl
    trade["status"] = "CLOSED"
    
    trades["trades"][trade_index] = trade
    
    # Update stats
    trades["current_capital"] += pnl
    if is_win:
        trades["win_count"] += 1
        trades["consecutive_losses"] = 0
    else:
        trades["loss_count"] += 1
        trades["consecutive_losses"] += 1
    
    total_trades = trades["win_count"] + trades["loss_count"]
    if total_trades > 0:
        trades["win_rate"] = (trades["win_count"] / total_trades) * 100
    
    trades["total_pnl"] = trades["current_capital"] - trades["total_capital"]
    
    # Check circuit breaker
    if trades["consecutive_losses"] >= CIRCUIT_BREAKER_LOSSES:
        trades["circuit_breaker_triggered"] = True
        print(f"🛑 CIRCUIT BREAKER: {trades['consecutive_losses']} consecutive losses")
    
    with open(DATA_DIR / "trades.json", 'w') as f:
        json.dump(trades, f, indent=2)
    
    print(f"✅ Trade closed: P&L ${pnl:+.2f} ({'WIN' if is_win else 'LOSS'})")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run one trading cycle"""
    print("\n" + "="*100)
    print("🚀 POLYMARKET LATE ENTRY STRATEGY")
    print("="*100)
    
    init_data_dir()
    
    # Check circuit breaker
    trades = load_trades()
    if trades.get("circuit_breaker_triggered"):
        print("⛔ CIRCUIT BREAKER ACTIVE - Trading halted")
        return
    
    # Discover markets
    markets = discover_crypto_markets()
    if not markets:
        print("❌ No markets found")
        return
    
    print(f"\n📊 ANALYZING {len(markets)} MARKETS...")
    
    # Analyze each market
    entries = 0
    exits = 0
    
    for market in markets[:5]:  # Analyze top 5
        # Simulate price history (in real: fetch from API)
        yes_prices = [
            market["yes_price"] * 0.95,
            market["yes_price"] * 0.98,
            market["yes_price"],
            market["yes_price"] * 1.02
        ]
        
        regime = assess_market_regime(yes_prices)
        signal = check_late_entry_signal(market, regime)
        
        print(f"\n{market['question'][:60]}...")
        print(f"  YES: ${market['yes_price']:.4f} | Regime: {'✅ Ready' if regime['ready_to_trade'] else '⛔ Choppy'}")
        print(f"  Signal: {signal['action']} | {signal['reasoning']}")
        
        if signal["action"] == "BUY" and entries < 2:
            save_trade(market["yes_price"], market["id"], market["question"])
            entries += 1
        elif signal["action"] == "SELL" and len(trades["trades"]) > exits:
            if trades["trades"][exits]["status"] == "OPEN":
                close_trade(exits, market["yes_price"])
                exits += 1
    
    # Print final stats
    trades = load_trades()
    print(f"\n📈 SESSION STATS")
    print(f"  Capital: ${trades['current_capital']:.2f} ({trades['total_pnl']:+.2f})")
    print(f"  Win Rate: {trades['win_rate']:.1f}% ({trades['win_count']}W / {trades['loss_count']}L)")
    print(f"  Trades: {len(trades['trades'])} total")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
