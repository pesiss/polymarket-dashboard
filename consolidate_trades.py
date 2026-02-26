import json
import os
import shutil
import time
import logging
from datetime import datetime, UTC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
MIN_EXPECTED_TRADES = {
    "polymarket": 400,  # Polymarket should have 400+ trades
    "aster": 50,
    "funding": 5,
    "whale": 5
}
TOTAL_MIN_TRADES = 100  # If consolidated result has fewer than this, it's likely corrupted
BACKUP_SUFFIX = ".backup"

# File paths
OUTPUT_FILE = "/home/pesiss/.openclaw/workspace/all_trades.json"
SOURCE_FILES = {
    "polymarket": "/home/pesiss/.openclaw/agents/polymarket/trades.json",
    "aster": "/home/pesiss/.openclaw/agents/aster-dex/aster_trades.json",
    "funding": "/home/pesiss/.openclaw/agents/arbitrage/funding_trades.json",
    "whale": "/home/pesiss/.openclaw/agents/whale-alert/whale_trades.json"
}


def load_json_with_retry(filepath, max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    """
    Load JSON file with retry logic and exponential backoff.
    Copies file to temp location before reading to avoid race conditions.
    """
    temp_path = filepath + ".tmp"
    
    for attempt in range(max_retries):
        try:
            # Copy to temp location first (atomic-ish read)
            if os.path.exists(filepath):
                shutil.copy2(filepath, temp_path)
                read_path = temp_path
            else:
                read_path = filepath
            
            # Read from temp copy
            with open(read_path, 'r') as f:
                data = json.load(f)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return data
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error on {filepath} (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
            else:
                logger.error(f"Failed to decode {filepath} after {max_retries} attempts")
                raise
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            raise
        finally:
            # Ensure temp file is cleaned up
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    return None


def validate_source_data(source_name, data):
    """
    Validate that loaded data is reasonable.
    Returns (is_valid, warning_message)
    """
    if data is None:
        return False, f"{source_name}: No data loaded"
    
    trades = data.get("trades", [])
    trade_count = len(trades)
    
    min_expected = MIN_EXPECTED_TRADES.get(source_name, 0)
    
    if trade_count == 0 and min_expected > 0:
        return False, f"{source_name}: ZERO trades detected (expected {min_expected}+)"
    
    if trade_count < min_expected * 0.5:  # Less than 50% of expected
        logger.warning(f"{source_name}: Suspiciously low trade count ({trade_count}, expected ~{min_expected})")
        return True, f"{source_name}: Low trade count warning"
    
    return True, None


def create_backup(filepath):
    """Create a backup of the file before overwriting."""
    backup_path = filepath + BACKUP_SUFFIX
    if os.path.exists(filepath):
        shutil.copy2(filepath, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return True
    return False


def restore_from_backup(filepath):
    """Restore file from backup if it exists."""
    backup_path = filepath + BACKUP_SUFFIX
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, filepath)
        logger.info(f"Restored {filepath} from backup")
        return True
    return False


def save_json(filepath, data):
    """Save JSON with backup creation first."""
    # Create backup of existing file
    create_backup(filepath)
    
    # Write to temp file first, then rename for atomicity
    temp_path = filepath + ".new"
    with open(temp_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Atomic rename
    os.replace(temp_path, filepath)
    logger.info(f"Saved {filepath}")


def load_source_data(source_name, filepath):
    """Load and validate source data with retry logic."""
    try:
        data = load_json_with_retry(filepath)
        is_valid, warning = validate_source_data(source_name, data)
        
        if warning:
            logger.warning(warning)
        
        if not is_valid:
            logger.error(f"Validation failed for {source_name}")
            return None
        
        return data
    except Exception as e:
        logger.error(f"Failed to load {source_name} from {filepath}: {e}")
        return None


def consolidate_trades():
    """Main consolidation function with validation and error handling."""
    
    all_trades_data = {
        "paper_capital": 0,
        "total_pnl": 0,
        "total_roi": 0,
        "open_positions": 0,
        "closed_positions": 0,
        "last_updated": "",
        "strategies": {},
        "trades": []
    }
    
    # Track which sources loaded successfully
    loaded_sources = {}
    failed_sources = []
    
    # --- Load Polymarket trades ---
    logger.info("Loading Polymarket trades...")
    polymarket_data = load_source_data("polymarket", SOURCE_FILES["polymarket"])
    if polymarket_data:
        loaded_sources["polymarket"] = polymarket_data
        all_trades_data["paper_capital"] += polymarket_data.get("paper_capital", 0)
        polymarket_portfolio = polymarket_data.get("portfolio", {})
        all_trades_data["total_pnl"] += polymarket_portfolio.get("total_pnl", 0)
        all_trades_data["open_positions"] += polymarket_portfolio.get("open_positions", 0)
        all_trades_data["closed_positions"] += polymarket_portfolio.get("closed_positions", 0)
        
        for trade in polymarket_data.get("trades", []):
            normalized_trade = {
                "trade_id": trade.get("trade_id"),
                "timestamp": trade.get("timestamp"),
                "strategy": trade.get("strategy"),
                "market_name": trade.get("market_name"), 
                "side": trade.get("side"),
                "entry_price": trade.get("entry_price"),
                "position_size": trade.get("position_size"),
                "notional_value": trade.get("notional_value"),
                "status": trade.get("status"),
                "exit_price": trade.get("exit_price"),
                "pnl": trade.get("actual_profit"), 
                "pnl_percent": None, 
                "closed_at": trade.get("resolved_at"), 
                "source_exchange": "Polymarket"
            }
            all_trades_data["trades"].append(normalized_trade)
        
        for strat_key, perf in polymarket_data.get("performance", {}).items():
            all_trades_data["strategies"][strat_key] = {
                "name": strat_key.replace("_", " ").title(),
                "trades": perf.get("trades", 0),
                "wins": perf.get("wins", 0),
                "losses": perf.get("losses", 0),
                "win_rate": perf.get("win_rate", 0),
                "total_pnl": perf.get("total_pnl", 0)
            }
    else:
        failed_sources.append("polymarket")
    
    # --- Load Aster DEX trades ---
    logger.info("Loading Aster DEX trades...")
    aster_data = load_source_data("aster", SOURCE_FILES["aster"])
    if aster_data:
        loaded_sources["aster"] = aster_data
        all_trades_data["paper_capital"] += aster_data.get("paper_capital", 0)
        aster_portfolio = aster_data.get("portfolio", {})
        all_trades_data["total_pnl"] += aster_portfolio.get("total_pnl", 0)
        all_trades_data["open_positions"] += aster_portfolio.get("open_positions", 0)
        all_trades_data["closed_positions"] += aster_portfolio.get("closed_positions", 0)
        
        for trade in aster_data.get("trades", []):
            normalized_trade = {
                "trade_id": trade.get("trade_id"),
                "timestamp": trade.get("timestamp"),
                "strategy": trade.get("strategy"),
                "market_name": trade.get("pair"), 
                "side": trade.get("side"),
                "entry_price": trade.get("entry_price"),
                "position_size": trade.get("position_size"),
                "notional_value": trade.get("notional_value"),
                "status": trade.get("status"),
                "exit_price": trade.get("exit_price"),
                "pnl": trade.get("pnl"), 
                "pnl_percent": trade.get("pnl_percent"),
                "closed_at": trade.get("closed_at"),
                "source_exchange": "Aster DEX"
            }
            all_trades_data["trades"].append(normalized_trade)
    
        for strat_key, perf in aster_data.get("performance", {}).items():
            formatted_key = strat_key.replace(" ", "_").lower()
            all_trades_data["strategies"][formatted_key] = {
                "name": strat_key,
                "trades": perf.get("trades", 0),
                "wins": perf.get("wins", 0),
                "losses": perf.get("losses", 0),
                "win_rate": perf.get("win_rate", 0),
                "total_pnl": perf.get("total_pnl", 0)
            }
    else:
        failed_sources.append("aster")
    
    # --- Load Funding Rate Arbitrage trades ---
    logger.info("Loading Funding Rate Arbitrage trades...")
    funding_data = load_source_data("funding", SOURCE_FILES["funding"])
    if funding_data:
        loaded_sources["funding"] = funding_data
        all_trades_data["paper_capital"] += funding_data.get("paper_capital", 0)
        funding_portfolio = funding_data.get("portfolio", {})
        all_trades_data["total_pnl"] += funding_portfolio.get("total_pnl", 0)
        all_trades_data["open_positions"] += funding_portfolio.get("open_positions", 0)
        all_trades_data["closed_positions"] += funding_portfolio.get("closed_positions", 0)
        
        for trade in funding_data.get("trades", []):
            normalized_trade = {
                "trade_id": trade.get("trade_id"),
                "timestamp": trade.get("timestamp"),
                "strategy": trade.get("strategy"),
                "market_name": f"{trade.get('asset')} Funding Arb", 
                "side": f"{trade.get('buy_exchange')} LONG / {trade.get('sell_exchange')} SHORT", 
                "entry_price": trade.get("spread_percent"), 
                "position_size": trade.get("position_value"),
                "notional_value": trade.get("position_value"), 
                "status": trade.get("status"),
                "exit_price": None,
                "pnl": trade.get("simulated_pnl"), 
                "pnl_percent": (trade.get("simulated_pnl",0) / trade.get("position_value",1) * 100) if trade.get("position_value") else 0,
                "closed_at": None,
                "source_exchange": "Funding Rate Arb"
            }
            all_trades_data["trades"].append(normalized_trade)
    
        all_trades_data["strategies"]["funding_rate_arb"] = {
            "name": "Funding Rate Arbitrage",
            "trades": funding_data.get("performance", {}).get("funding_rate_arb", {}).get("trades", 0),
            "wins": funding_data.get("performance", {}).get("funding_rate_arb", {}).get("wins", 0),
            "losses": funding_data.get("performance", {}).get("funding_rate_arb", {}).get("losses", 0),
            "win_rate": funding_data.get("performance", {}).get("funding_rate_arb", {}).get("win_rate", 0),
            "total_pnl": funding_data.get("performance", {}).get("funding_rate_arb", {}).get("total_pnl", 0)
        }
    else:
        failed_sources.append("funding")
    
    # --- Load Whale Alert trades ---
    logger.info("Loading Whale Alert trades...")
    whale_data = load_source_data("whale", SOURCE_FILES["whale"])
    if whale_data:
        loaded_sources["whale"] = whale_data
        all_trades_data["paper_capital"] += whale_data.get("paper_capital", 0)
        whale_portfolio = whale_data.get("portfolio", {})
        all_trades_data["total_pnl"] += whale_portfolio.get("total_pnl", 0)
        all_trades_data["open_positions"] += whale_portfolio.get("open_positions", 0)
        all_trades_data["closed_positions"] += whale_portfolio.get("closed_positions", 0)
        
        for trade in whale_data.get("trades", []):
            normalized_trade = {
                "trade_id": trade.get("trade_id"),
                "timestamp": trade.get("timestamp"),
                "strategy": trade.get("strategy"),
                "market_name": f"{trade.get('asset')} Whale Signal", 
                "side": trade.get("side"),
                "entry_price": None, 
                "position_size": trade.get("position_size"),
                "notional_value": trade.get("notional_value"),
                "status": trade.get("status"),
                "exit_price": None,
                "pnl": trade.get("simulated_pnl"), 
                "pnl_percent": trade.get("simulated_pnl_pct"),
                "closed_at": None,
                "source_exchange": "Whale Alert"
            }
            all_trades_data["trades"].append(normalized_trade)
    
        all_trades_data["strategies"]["whale_alert"] = {
            "name": "Whale Alert",
            "trades": whale_data.get("performance", {}).get("whale_alert", {}).get("trades", 0),
            "wins": whale_data.get("performance", {}).get("whale_alert", {}).get("wins", 0),
            "losses": whale_data.get("performance", {}).get("whale_alert", {}).get("losses", 0),
            "win_rate": whale_data.get("performance", {}).get("whale_alert", {}).get("win_rate", 0),
            "total_pnl": whale_data.get("performance", {}).get("whale_alert", {}).get("total_pnl", 0)
        }
    else:
        failed_sources.append("whale")
    
    # Calculate total ROI
    if all_trades_data["paper_capital"] > 0:
        all_trades_data["total_roi"] = (all_trades_data["total_pnl"] / all_trades_data["paper_capital"]) * 100
    
    # Sort trades by timestamp descending
    all_trades_data["trades"].sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    all_trades_data["last_updated"] = datetime.now(UTC).isoformat()
    
    # --- VALIDATION: Check if result is reasonable ---
    total_trades = len(all_trades_data["trades"])
    logger.info(f"Consolidated {total_trades} trades from {len(loaded_sources)} sources")
    
    if total_trades < TOTAL_MIN_TRADES:
        logger.error(f"CRITICAL: Consolidated trade count ({total_trades}) is below minimum threshold ({TOTAL_MIN_TRADES})")
        logger.error(f"Failed sources: {failed_sources}")
        logger.error("Data appears corrupted - restoring from backup instead")
        
        if restore_from_backup(OUTPUT_FILE):
            logger.info("Restored from backup successfully")
            return False
        else:
            logger.error("No backup available to restore from!")
            # Still save the data but with a warning
    
    # Save the consolidated data
    try:
        save_json(OUTPUT_FILE, all_trades_data)
        logger.info(f"Consolidation complete: PNL=${all_trades_data['total_pnl']:.2f}, ROI={all_trades_data['total_roi']:.1f}%, Trades={total_trades}")
        return True
    except Exception as e:
        logger.error(f"Failed to save consolidated data: {e}")
        return False


if __name__ == "__main__":
    success = consolidate_trades()
    exit(0 if success else 1)
