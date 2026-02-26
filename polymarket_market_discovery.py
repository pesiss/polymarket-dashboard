#!/usr/bin/env python3
"""
Polymarket Market Discovery Tool
Automated search for high-alpha asymmetric trades
Usage: python3 polymarket_market_discovery.py [category]
"""

import json
import urllib.request
import urllib.error
from datetime import datetime

# Configuration
GAMMA_API = "https://gamma-api.polymarket.com/markets"
CACHE_FILE = "polymarket_markets.json"

# High-alpha search criteria
CRITERIA = {
    "min_price": 0.00,      # Below $0.10 (ultra-low)
    "max_price": 0.10,
    "max_volume_24h": 10000, # Under $10k daily volume (illiquid = high alpha)
    "min_risk_reward": 50,   # At least 50:1 asymmetry
}

# Categories to search
SEARCH_CATEGORIES = [
    "weather",
    "temperature", 
    "climate",
    "AI",
    "tech",
    "space",
    "crypto",
    "Science",
]

def fetch_markets(limit=100, category=None):
    """Fetch markets from Polymarket API"""
    try:
        url = f"{GAMMA_API}?limit={limit}"
        if category:
            url += f"&category={category}"
        
        print(f"📡 Fetching from: {url}")
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            print(f"✅ Fetched {len(data) if isinstance(data, list) else 'unknown'} markets")
            return data if isinstance(data, list) else []
            
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"❌ Error fetching markets: {str(e)}")
        return []

def analyze_market(market):
    """Analyze single market for asymmetric opportunity"""
    try:
        # Extract data
        question = market.get("question", "Unknown")
        slug = market.get("slug", "")
        volume_24h = float(market.get("volume24hr", 0))
        outcome_prices = market.get("outcomePrices", "[]")
        
        # Parse prices safely
        try:
            prices = json.loads(outcome_prices.replace("'", '"'))
            prices = [float(p) if p else 0 for p in prices]
        except:
            prices = [0, 0]
        
        # Calculate asymmetry
        yes_price = prices[0] if len(prices) > 0 else 0
        no_price = prices[1] if len(prices) > 1 else 0
        
        # Find if prices are extreme (good asymmetry)
        has_asymmetry = (yes_price < 0.05 and no_price > 0.95) or \
                        (no_price < 0.05 and yes_price > 0.95)
        
        # Check if meets criteria
        meets_criteria = (
            has_asymmetry and
            volume_24h < CRITERIA["max_volume_24h"]
        )
        
        return {
            "question": question,
            "slug": slug,
            "url": f"https://polymarket.com/event/{slug}",
            "yes_price": yes_price,
            "no_price": no_price,
            "asymmetry_score": abs(yes_price - 0.5) + abs(no_price - 0.5),
            "volume_24h": volume_24h,
            "meets_criteria": meets_criteria,
        }
    except Exception as e:
        return None

def search_markets(category=None, min_asymmetry=0.8):
    """Search for high-alpha markets"""
    print(f"\n{'='*70}")
    print(f"🔍 POLYMARKET ASYMMETRIC MARKET FINDER")
    print(f"{'='*70}")
    print(f"Search Category: {category or 'All'}")
    print(f"Min Asymmetry Score: {min_asymmetry}")
    print(f"Max Volume 24h: ${CRITERIA['max_volume_24h']:,}")
    print(f"{'='*70}\n")
    
    # Fetch markets
    markets = fetch_markets(limit=100, category=category)
    
    if not markets:
        print("❌ No markets found")
        return []
    
    # Analyze each market
    results = []
    high_alpha_markets = []
    
    for market in markets:
        analysis = analyze_market(market)
        if analysis and analysis["meets_criteria"]:
            high_alpha_markets.append(analysis)
    
    # Sort by asymmetry score
    high_alpha_markets.sort(key=lambda x: x["asymmetry_score"], reverse=True)
    
    # Display top 10 results
    print(f"\n📊 TOP 10 ASYMMETRIC MARKETS (Min Asymmetry: {min_asymmetry}):\n")
    
    for i, market in enumerate(high_alpha_markets[:10], 1):
        print(f"{i}. {market['question'][:70]}")
        print(f"   URL: {market['url']}")
        print(f"   YES: {market['yes_price']:.2%} | NO: {market['no_price']:.2%}")
        print(f"   Asymmetry Score: {market['asymmetry_score']:.2f}")
        print(f"   24h Volume: ${market['volume_24h']:,.0f}")
        print(f"   ✅ RECOMMENDATION: {'BUY YES' if market['no_price'] < 0.05 else 'BUY NO'}\n")
    
    return high_alpha_markets

def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🚀 POLYMARKET AUTOMATED DISCOVERY")
    print("="*70)
    print("\nCost: FREE (using Polymarket GAMMA API)")
    print("Status: ✅ LIVE\n")
    
    # Search across multiple categories
    all_results = []
    for category in SEARCH_CATEGORIES:
        results = search_markets(category=category)
        all_results.extend(results)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📈 SUMMARY: Found {len(all_results)} high-alpha asymmetric markets")
    print(f"{'='*70}\n")
    
    # Save results
    with open("polymarket_discovery_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_markets_found": len(all_results),
            "markets": all_results[:50],  # Top 50
        }, f, indent=2)
    
    print(f"✅ Results saved to: polymarket_discovery_results.json\n")
    
    # Next steps
    print("NEXT STEPS:")
    print("1. Review polymarket_discovery_results.json")
    print("2. Pick top 5 markets with highest asymmetry")
    print("3. Share URLs with me for detailed analysis")
    print("4. I'll code Phase 1 trading strategy\n")

if __name__ == "__main__":
    main()
