#!/usr/bin/env python3
"""
Polymarket Paper Trading System
Automated mean-reversion strategy for crypto "Up/Down" prediction markets

STRATEGY:
- Buy when YES price < 0.40 on "Up" markets (mean reversion)
- Sell when YES price > 0.60 (take profit)
- Max position: $10 per trade
- Max consecutive losses: 3 (circuit breaker)
- Run every 15 minutes via cron

FILE STRUCTURE:
- polymarket_data/
  - markets.json        (discovered markets cache)
  - trades.json         (all executed trades)
  - state.json          (current positions, consecutive losses)
  - dashboard.html      (performance visualization)
"""

import requests
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

GAMMA_API = "https://gamma-api.polymarket.com"
MARKETS_ENDPOINT = f"{GAMMA_API}/markets"
DATA_DIR = Path("polymarket_data")

# Trading parameters
MAX_POSITION_SIZE = 10.0         # $10 max per trade
BUY_THRESHOLD = 0.40             # Buy when YES < 0.40
SELL_THRESHOLD = 0.60            # Sell when YES > 0.60
CIRCUIT_BREAKER_LOSSES = 3       # Stop trading after 3 losses
MAX_HOLD_HOURS = 48              # Close position after 48h

# Target crypto markets
TARGET_MARKETS = ["Bitcoin", "Ethereum", "Solana"]
TARGET_KEYWORDS = ["Up", "higher", "increase"]

# API retry settings
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_data_dir():
    """Initialize data directory and required files"""
    DATA_DIR.mkdir(exist_ok=True)
    
    # Initialize trades.json if missing
    trades_file = DATA_DIR / "trades.json"
    if not trades_file.exists():
        with open(trades_file, 'w') as f:
            json.dump({
                "trades": [],
                "total_pnl": 0.0,
                "win_count": 0,
                "loss_count": 0,
                "win_rate": 0.0
            }, f, indent=2)
    
    # Initialize state.json if missing
    state_file = DATA_DIR / "state.json"
    if not state_file.exists():
        with open(state_file, 'w') as f:
            json.dump({
                "consecutive_losses": 0,
                "circuit_breaker_triggered": False,
                "open_positions": [],
                "last_updated": None,
                "markets_cache_updated": None
            }, f, indent=2)


# ============================================================================
# API CALLS
# ============================================================================

def fetch_markets(limit=100) -> List[Dict]:
    """
    Fetch active markets from Polymarket API
    
    Args:
        limit: Number of markets to fetch
    
    Returns:
        List of market dictionaries, or empty list on failure
    """
    for attempt in range(MAX_RETRIES):
        try:
            params = {"limit": limit, "active": True}
            response = requests.get(MARKETS_ENDPOINT, params=params, timeout=10)
            response.raise_for_status()
            
            print(f"✅ Fetched {len(response.json())} markets from API")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ API Error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            continue
    
    print("❌ Failed to fetch markets after retries")
    return []


def discover_crypto_markets() -> List[Dict]:
    """
    Find Bitcoin, Ethereum, Solana "Up/Down" markets
    
    Returns:
        List of crypto "Up" markets matching our criteria
    """
    print("\n🔍 Discovering crypto markets...")
    
    all_markets = fetch_markets()
    if not all_markets:
        return []
    
    crypto_markets = []
    
    for market in all_markets:
        question = market.get("question", "").lower()
        
        # Filter 1: Must contain target crypto
        if not any(crypto.lower() in question for crypto in TARGET_MARKETS):
            continue
        
        # Filter 2: Must contain "Up" keyword
        if not any(keyword.lower() in question for keyword in TARGET_KEYWORDS):
            continue
        
        # Filter 3: Must have outcome prices (YES/NO odds)
        prices_raw = market.get("outcomePrices", "")
        
        # Handle prices as JSON string: "[0.5, 0.5]"
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
            continue  # Skip malformed prices
        
        crypto_markets.append({
            "id": market.get("id"),
            "question": market.get("question"),
            "yes_price": yes_price,
            "no_price": no_price,
            "volume_24h": market.get("volume24h", 0),
            "liquidity": market.get("liquidity", 0),
            "end_date": market.get("endDate"),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    print(f"✅ Found {len(crypto_markets)} active crypto 'Up' markets")
    return crypto_markets


# ============================================================================
# STRATEGY: MEAN REVERSION
# ============================================================================

def check_buy_signal(yes_price: float) -> bool:
    """
    Check if we should BUY (mean reversion trigger)
    
    Buy when YES price drops below 0.40 on "Up" markets
    Logic: Low YES price = market thinks it won't go up = opportunity to buy
    """
    return yes_price < BUY_THRESHOLD


def check_sell_signal(yes_price: float) -> bool:
    """
    Check if we should SELL (take profit)
    
    Sell when YES price rises above 0.60
    Logic: High YES price = good profit target
    """
    return yes_price > SELL_THRESHOLD


def evaluate_market(market: Dict) -> Dict:
    """
    Evaluate a single market for trading opportunity
    
    Returns:
        {
            "market_id": str,
            "question": str,
            "signal": "BUY" | "SELL" | "HOLD",
            "yes_price": float,
            "reasoning": str
        }
    """
    yes_price = market["yes_price"]
    signal = "HOLD"
    reasoning = ""
    
    if check_buy_signal(yes_price):
        signal = "BUY"
        reasoning = f"YES undervalued at ${yes_price:.3f} (below $0.40 threshold)"
    
    elif check_sell_signal(yes_price):
        signal = "SELL"
        reasoning = f"YES overbought at ${yes_price:.3f} (above $0.60 threshold)"
    
    else:
        reasoning = f"No signal. YES at ${yes_price:.3f} (range $0.40-$0.60)"
    
    return {
        "market_id": market["id"],
        "question": market["question"][:80],  # Truncate for display
        "signal": signal,
        "yes_price": yes_price,
        "reasoning": reasoning
    }


# ============================================================================
# STATE & POSITION MANAGEMENT
# ============================================================================

def load_state() -> Dict:
    """Load current trading state (positions, consecutive losses)"""
    state_file = DATA_DIR / "state.json"
    if state_file.exists():
        with open(state_file, 'r') as f:
            return json.load(f)
    return {}


def save_state(state: Dict):
    """Save trading state"""
    state_file = DATA_DIR / "state.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)


def load_trades() -> Dict:
    """Load all trades from history"""
    trades_file = DATA_DIR / "trades.json"
    if trades_file.exists():
        with open(trades_file, 'r') as f:
            return json.load(f)
    return {"trades": [], "total_pnl": 0.0, "win_count": 0, "loss_count": 0}


def save_trade(entry_price: float, exit_price: Optional[float], market_id: str, market_question: str):
    """
    Log a completed trade to history
    
    Args:
        entry_price: Price we bought at (YES price)
        exit_price: Price we sold at (or None if still open)
        market_id: Polymarket market ID
        market_question: Human-readable market question
    """
    trades = load_trades()
    
    # Calculate P&L
    if exit_price:
        pnl = (exit_price - entry_price) * MAX_POSITION_SIZE
        is_win = pnl > 0
    else:
        pnl = 0.0
        is_win = None
    
    trade = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "market_id": market_id,
        "market_question": market_question,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "position_size": MAX_POSITION_SIZE,
        "pnl": pnl,
        "is_win": is_win
    }
    
    trades["trades"].append(trade)
    
    # Update stats if trade is closed
    if exit_price:
        trades["total_pnl"] += pnl
        if is_win:
            trades["win_count"] += 1
        else:
            trades["loss_count"] += 1
    
    # Calculate win rate
    total_closed = trades["win_count"] + trades["loss_count"]
    if total_closed > 0:
        trades["win_rate"] = (trades["win_count"] / total_closed) * 100
    
    with open(DATA_DIR / "trades.json", 'w') as f:
        json.dump(trades, f, indent=2)
    
    print(f"📝 Trade logged: {market_question[:50]}... | Entry: ${entry_price:.3f} | Exit: ${exit_price:.3f if exit_price else 'N/A'}")


# ============================================================================
# CIRCUIT BREAKER
# ============================================================================

def check_circuit_breaker() -> bool:
    """
    Check if we should stop trading due to consecutive losses
    
    Returns:
        True if circuit breaker is triggered (stop trading), False otherwise
    """
    state = load_state()
    consecutive_losses = state.get("consecutive_losses", 0)
    
    if consecutive_losses >= CIRCUIT_BREAKER_LOSSES:
        print(f"🛑 CIRCUIT BREAKER TRIGGERED: {consecutive_losses} consecutive losses")
        state["circuit_breaker_triggered"] = True
        save_state(state)
        return True
    
    return False


def update_consecutive_losses(is_win: bool):
    """
    Update consecutive loss counter
    
    Args:
        is_win: Whether the last trade was profitable
    """
    state = load_state()
    
    if is_win:
        state["consecutive_losses"] = 0  # Reset on win
        print("✅ Win! Consecutive losses reset to 0")
    else:
        state["consecutive_losses"] += 1
        print(f"❌ Loss. Consecutive losses: {state['consecutive_losses']}/{CIRCUIT_BREAKER_LOSSES}")
    
    save_state(state)


# ============================================================================
# DISPLAY
# ============================================================================

def print_market_analysis(markets: List[Dict]):
    """Display market analysis in a readable format"""
    if not markets:
        print("❌ No markets to analyze")
        return
    
    print(f"\n📊 MARKET ANALYSIS ({len(markets)} markets)")
    print("=" * 100)
    
    buy_signals = 0
    sell_signals = 0
    
    for market in markets[:10]:  # Show top 10
        analysis = evaluate_market(market)
        
        if analysis["signal"] == "BUY":
            buy_signals += 1
            print(f"🟢 BUY  | {analysis['question']}")
            print(f"        | YES: ${analysis['yes_price']:.4f} | {analysis['reasoning']}")
        
        elif analysis["signal"] == "SELL":
            sell_signals += 1
            print(f"🔴 SELL | {analysis['question']}")
            print(f"        | YES: ${analysis['yes_price']:.4f} | {analysis['reasoning']}")
        
        else:
            print(f"⚪ HOLD | {analysis['question']}")
            print(f"        | YES: ${analysis['yes_price']:.4f} | {analysis['reasoning']}")
    
    print("=" * 100)
    print(f"Summary: {buy_signals} BUY signals | {sell_signals} SELL signals")


def print_trading_stats():
    """Display current trading statistics"""
    trades = load_trades()
    state = load_state()
    
    print(f"\n📈 TRADING STATISTICS")
    print("=" * 50)
    print(f"Total P&L: ${trades['total_pnl']:+.2f}")
    print(f"Win Rate: {trades['win_rate']:.1f}% ({trades['win_count']} wins, {trades['loss_count']} losses)")
    print(f"Total Trades: {len(trades['trades'])}")
    print(f"Consecutive Losses: {state.get('consecutive_losses', 0)}/{CIRCUIT_BREAKER_LOSSES}")
    print(f"Circuit Breaker: {'🛑 TRIGGERED' if state.get('circuit_breaker_triggered') else '✅ Active'}")
    print("=" * 50)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point for the paper trading system"""
    print("\n🚀 Polymarket Paper Trading System")
    print("=" * 100)
    
    # Initialize
    init_data_dir()
    
    # Check circuit breaker
    if check_circuit_breaker():
        print("⛔ Trading halted due to circuit breaker. Reset state.json to resume.")
        return
    
    # Discover markets
    markets = discover_crypto_markets()
    
    if not markets:
        print("⚠️ No markets discovered. Retrying next cycle.")
        return
    
    # Analyze markets for signals
    print_market_analysis(markets)
    
    # Display current stats
    print_trading_stats()
    
    print("\n✅ Paper trading cycle complete")
    print("   Next run: In 15 minutes via cron job")


if __name__ == "__main__":
    main()
