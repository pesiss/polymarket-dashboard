
import json
from datetime import datetime, timedelta

from collections import defaultdict

def generate_dashboard_data(trades_file_path: str, base_capital: float = 1000.0, compounding_cap_multiplier: float = 3.0):
    """
    Generates dashboard data including actual and simulated compounding P&L history.
    """
    with open(trades_file_path, 'r') as f:
        bot_data = json.load(f)

    all_trades = bot_data['trades']
    
    # Filter out Oracle Lag for "actual" P&L (since it's disabled)
    filtered_closed_trades = [t for t in all_trades if t['status'] == 'CLOSED' and t['strategy'] != 'Oracle Lag Exploit']
    
    # Sort trades by resolved_at for chronological processing
    filtered_closed_trades.sort(key=lambda x: datetime.fromisoformat(x['resolved_at'].replace('Z', '+00:00') if 'Z' in x['resolved_at'] else x['resolved_at']))

    # --- Actual P&L Calculation (Filtered, Non-Compounding) ---
    actual_pnl_history = []
    current_actual_pnl = 0.0
    for trade in filtered_closed_trades:
        current_actual_pnl += float(trade.get('pnl', 0))
        actual_pnl_history.append({
            'timestamp': trade['resolved_at'],
            'pnl': current_actual_pnl
        })
    
    # --- Simulated Compounding P&L Calculation ---
    compounding_pnl_history = []
    simulated_capital = base_capital
    
    # Strategy base position sizes (from paper_trading_engine.py)
    strategy_base_positions = {
        "Whale Copy-Trading": 15,
        "Whale Copy-Trading v2": 15,
        "Settlement Edge": 25,
        # Oracle Lag is disabled, so we don't simulate compounding for it
    }

    for trade in filtered_closed_trades:
        strategy = trade.get('strategy', 'Unknown')
        original_pnl = float(trade.get('pnl', 0))
        original_notional_value = float(trade.get('notional_value', 0))
        
        # Determine the base position size for this strategy
        base_pos_size_for_strategy = strategy_base_positions.get(strategy, 0)
        if base_pos_size_for_strategy == 0: # Should not happen for active strats
            continue

        # Calculate position multiplier for compounding
        position_multiplier = min(simulated_capital / base_capital, compounding_cap_multiplier)
        
        # Calculate simulated position size for this trade
        simulated_position_size = int(base_pos_size_for_strategy * position_multiplier)
        simulated_position_size = max(1, simulated_position_size) # Ensure at least 1 unit

        # Recalculate P&L based on simulated position size (proportional to original notional value / original position size)
        # Assuming P&L scales linearly with position size
        if original_notional_value > 0:
            simulated_pnl = (simulated_position_size / (original_notional_value / trade['entry_price'])) * original_pnl
        else:
            simulated_pnl = original_pnl # If notional_value was 0, P&L is also 0
        
        simulated_capital += simulated_pnl
        
        compounding_pnl_history.append({
            'timestamp': trade['resolved_at'],
            'pnl': simulated_capital - base_capital # Store cumulative profit, not total capital
        })

    # --- Final Metrics (Actual) ---
    actual_total_pnl = sum(float(t.get('pnl', 0)) for t in filtered_closed_trades)
    actual_total_roi = (actual_total_pnl / base_capital * 100) if base_capital > 0 else 0
    actual_closed_trades = len(filtered_closed_trades)
    actual_open_positions = len([t for t in all_trades if t['status'] == 'OPEN' and t['strategy'] != 'Oracle Lag Exploit'])
    
    # --- Final Metrics (Compounding) ---
    compounding_total_pnl = simulated_capital - base_capital
    compounding_total_roi = (compounding_total_pnl / base_capital * 100) if base_capital > 0 else 0
    compounding_closed_trades = len(filtered_closed_trades) # Same number of trades

    # --- Strategy Breakdown (Actual, Filtered) ---
    strategy_stats = defaultdict(lambda: {'name': '', 'trades': 0, 'wins': 0, 'losses': 0, 'total_pnl': 0, 'win_rate': 0.0})
    for trade in filtered_closed_trades:
        strat = trade.get('strategy', 'Unknown')
        strategy_stats[strat]['trades'] += 1
        strategy_stats[strat]['name'] = strat
        pnl = float(trade.get('pnl', 0))
        strategy_stats[strat]['total_pnl'] += pnl
        if pnl > 0:
            strategy_stats[strat]['wins'] += 1
        else:
            strategy_stats[strat]['losses'] += 1
    
    for strat in strategy_stats:
        stats = strategy_stats[strat]
        if stats['trades'] > 0:
            stats['win_rate'] = (stats['wins'] / stats['trades']) * 100

    # --- Prepare final dashboard data ---
    dashboard_data = {
        'timestamp': datetime.now().isoformat(),
        'base_capital': base_capital,
        'compounding_cap_multiplier': compounding_cap_multiplier,

        'actual': {
            'total_pnl': actual_total_pnl,
            'total_roi': actual_total_roi,
            'closed_trades': actual_closed_trades,
            'open_positions': actual_open_positions,
            'strategies': {k: v for k, v in strategy_stats.items() if k != 'Oracle Lag Exploit'},
            'pnl_history': actual_pnl_history
        },
        'compounding': {
            'total_pnl': compounding_total_pnl,
            'total_roi': compounding_total_roi,
            'closed_trades': compounding_closed_trades,
            'pnl_history': compounding_pnl_history
        }
    }
    return dashboard_data

if __name__ == '__main__':
    trades_path = '/home/pesiss/.openclaw/agents/polymarket/trades.json'
    output_path = '/home/pesiss/.openclaw/workspace/live_data.json'
    
    data = generate_dashboard_data(trades_path)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Dashboard data generated and saved to {output_path}")
    print(f"Actual P&L: ${data['actual']['total_pnl']:.2f}, ROI: {data['actual']['total_roi']:.2f}%")
    print(f"Compounding P&L: ${data['compounding']['total_pnl']:.2f}, ROI: {data['compounding']['total_roi']:.2f}%")
