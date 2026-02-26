#!/usr/bin/env python3
"""
Polymarket Paper Trading System
Automated mean-reversion strategy for crypto "Up/Down" prediction markets
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path

# Polymarket API endpoints
GAMMA_API = "https://gamma-api.polymarket.com"
MARKETS_ENDPOINT = f"{GAMMA_API}/markets"

# Config
DATA_DIR = Path("polymarket_data")
TRADES_FILE = DATA_DIR / "trades.json"
STATE_FILE = DATA_DIR / "state.json"
MAX_POSITION_SIZE = 10.0  # $10 max per trade
CIRCUIT_BREAKER_LOSSES = 3  # Stop after 3 consecutive losses

# Crypto "Up" markets to track
TARGET_MARKETS = ["Bitcoin", "Ethereum", "Solana"]
TARGET_KEYWORDS = ["Up", "higher", "increase"]


def init_data_dir():
    """Initialize data directory and files"""
    DATA_DIR.mkdir(exist_ok=True)
    
    if not TRADES_FILE.exists():
        with open(TRADES_FILE, 'w') as f:
            json.dump({"trades": [], "total_pnl": 0.0, "win_rate": 0.0}, f, indent=2)
    
    if not STATE_FILE.exists():
        with open(STATE_FILE, 'w') as f:
            json.dump({
                "consecutive_losses": 0,
                "last_updated": None,
                "active_positions": [],
                "circuit_breaker_triggered": False
            }, f, indent=2)


def fetch_markets(limit=100):
    """Fetch active markets from Polymarket API"""
    try:
        params = {"limit": limit, "active": True}
        response = requests.get(MARKETS_ENDPOINT, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        return []


def discover_crypto_markets():
    """Find Bitcoin, Ethereum, Solana "Up/Down" markets"""
    print("🔍 Discovering active crypto markets...")
    
    all_markets = fetch_markets()
    
    if not all_markets:
        print("❌ No markets found")
        return []
    
    crypto_markets = []
    
    for market in all_markets:
        question = market.get("question", "").lower()
        
        # Look for our target crypto markets with "Up" keywords
        if any(crypto.lower() in question for crypto in TARGET_MARKETS):
            if any(keyword.lower() in question for keyword in TARGET_KEYWORDS):
                crypto_markets.append({
                    "id": market.get("id"),
                    "question": market.get("question"),
                    "outcome_prices": market.get("outcomePrices", []),
                    "volume": market.get("volume24h", 0),
                    "liquidity": market.get("liquidity", 0),
                    "end_date": market.get("endDate"),
                })
    
    return crypto_markets


def display_markets(markets):
    """Display discovered markets in a readable format"""
    if not markets:
        print("❌ No crypto 'Up' markets found")
        return
    
    print(f"\n✅ Found {len(markets)} active crypto markets:\n")
    print("=" * 100)
    
    for i, market in enumerate(markets[:10], 1):  # Show top 10
        print(f"\n{i}. {market['question']}")
        print(f"   Market ID: {market['id']}")
        
        # Display outcome prices (YES and NO)
        prices = market['outcome_prices']
        if prices and len(prices) >= 2:
            print(f"   YES Price: ${prices[0]:.2f} | NO Price: ${prices[1]:.2f}")
        
        print(f"   24h Volume: ${market['volume']:,.0f}")
        print(f"   Liquidity: ${market['liquidity']:,.0f}")
        print(f"   Expires: {market['end_date']}")
    
    print("\n" + "=" * 100)


def check_strategy_signal(yes_price, market_question):
    """
    Check if strategy signal is triggered
    
    Buy: YES price < 0.40 on "Up" market (mean reversion)
    Sell: YES price > 0.60 on "Up" market (take profit)
    """
    signals = {"action": "HOLD", "reason": ""}
    
    if yes_price < 0.40:
        signals["action"] = "BUY"
        signals["reason"] = f"YES undervalued at ${yes_price:.2f} (< $0.40)"
    elif yes_price > 0.60:
        signals["action"] = "SELL"
        signals["reason"] = f"YES overbought at ${yes_price:.2f} (> $0.60)"
    
    return signals


def load_state():
    """Load trading state"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_state(state):
    """Save trading state"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def main():
    print("🚀 Polymarket Paper Trading System")
    print("=" * 100)
    
    # Initialize
    init_data_dir()
    
    # Discover markets
    markets = discover_crypto_markets()
    display_markets(markets)
    
    # Show strategy signals for each market
    if markets:
        print("\n📊 STRATEGY ANALYSIS:")
        print("=" * 100)
        
        for market in markets[:5]:  # Analyze top 5
            prices = market['outcome_prices']
            if prices and len(prices) >= 2:
                yes_price = prices[0]
                signal = check_strategy_signal(yes_price, market['question'])
                
                print(f"\n{market['question'][:60]}...")
                print(f"  Current YES Price: ${yes_price:.4f}")
                print(f"  Signal: {signal['action']} - {signal['reason']}")
    
    # Show state
    state = load_state()
    print(f"\n⚙️ TRADING STATE:")
    print(f"  Consecutive Losses: {state.get('consecutive_losses', 0)}")
    print(f"  Circuit Breaker: {'🛑 TRIGGERED' if state.get('circuit_breaker_triggered') else '✅ Active'}")
    print(f"  Last Updated: {state.get('last_updated', 'Never')}")


if __name__ == "__main__":
    main()
