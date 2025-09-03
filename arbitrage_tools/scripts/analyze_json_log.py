#!/usr/bin/env python3
"""
JSON Log Analyzer
Analyzes JSON execution logs and demonstrates interface presentation data.
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List


def find_latest_json_log():
    """Find the most recent JSON execution log."""
    csv_dir = os.path.join(os.path.dirname(__file__), '..', 'csv_output')
    if not os.path.exists(csv_dir):
        return None
    
    # Find all JSON log files
    json_files = glob.glob(os.path.join(csv_dir, "execution_log_*.json"))
    if not json_files:
        return None
    
    # Return the most recent file
    return max(json_files, key=os.path.getctime)


def analyze_json_log(json_file_path: str):
    """Analyze JSON log file and print summary."""
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        session_info = data.get('session_info', {})
        
        print(f"\n{'='*60}")
        print(f"ARBITRAGE MONITOR ANALYSIS")
        print(f"{'='*60}")
        
        # Data source information
        data_source = session_info.get('data_source', 'unknown')
        data_quality = session_info.get('data_quality', 'unknown')
        exchanges = session_info.get('exchanges', [])
        
        print(f"\n📊 DATA SOURCE ANALYSIS:")
        print(f"   Source: {data_source.upper()}")
        print(f"   Quality: {data_quality.upper()}")
        print(f"   Exchanges: {', '.join(exchanges)}")
        
        # Strategy parameters
        strategy_params = session_info.get('strategy_params', {})
        symbols = session_info.get('symbols', [])
        
        print(f"\n⚙️  STRATEGY PARAMETERS:")
        print(f"   Symbols: {', '.join(symbols)}")
        print(f"   Strategy Type: {strategy_params.get('strategy_type', 'unknown')}")
        print(f"   Risk Level: {strategy_params.get('risk_level', 'unknown')}")
        print(f"   Execution Mode: {strategy_params.get('execution_mode', 'unknown')}")
        print(f"   Volume USD: ${strategy_params.get('volume_usd', 0):,.2f}")
        print(f"   Trade Fee: {strategy_params.get('trade_fee_percent', 0)}%")
        print(f"   Slippage: {strategy_params.get('slippage_percent', 0)}%")
        print(f"   Min Volume: ${strategy_params.get('min_volume_usd', 0):,.2f}")
        print(f"   Max Volume: ${strategy_params.get('max_volume_usd', 0):,.2f}")
        print(f"   Confidence Threshold: {strategy_params.get('confidence_threshold', 0)}")
        print(f"   Stop Loss: {strategy_params.get('stop_loss_percent', 0)}%")
        print(f"   Take Profit: {strategy_params.get('take_profit_percent', 0)}%")
        print(f"   Max Positions: {strategy_params.get('max_positions', 0)}")
        
        # Session information
        threshold = session_info.get('threshold', 0)
        start_time = session_info.get('start_time')
        end_time = session_info.get('end_time')
        duration = session_info.get('duration_seconds', 0)
        
        print(f"\n📈 SESSION SUMMARY:")
        print(f"   Threshold: {threshold}%")
        print(f"   Start Time: {start_time}")
        print(f"   End Time: {end_time}")
        print(f"   Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        
        # Statistics
        total_updates = session_info.get('total_price_updates', 0)
        total_opportunities = session_info.get('total_opportunities', 0)
        profitable_opportunities = session_info.get('profitable_opportunities', 0)
        total_profit = session_info.get('total_simulated_profit', 0.0)
        
        print(f"\n📊 STATISTICS:")
        print(f"   Total Price Updates: {total_updates}")
        print(f"   Total Opportunities: {total_opportunities}")
        print(f"   Profitable Opportunities: {profitable_opportunities}")
        print(f"   Success Rate: {(profitable_opportunities/total_opportunities*100):.1f}%" if total_opportunities > 0 else "   Success Rate: 0%")
        print(f"   Total Simulated Profit: ${total_profit:.2f}")
        
        # Recent opportunities with symbol breakdown
        opportunities = data.get('opportunities', [])
        if opportunities:
            print(f"\n🎯 RECENT OPPORTUNITIES:")
            for i, opp in enumerate(opportunities[-5:], 1):  # Show last 5
                timestamp = opp.get('timestamp', 'Unknown')
                symbol = opp.get('symbol', 'Unknown')
                buy_ex = opp.get('buy_exchange', 'Unknown')
                sell_ex = opp.get('sell_exchange', 'Unknown')
                profit_pct = opp.get('profit_percent', 0)
                profit_usd = opp.get('estimated_profit_usd', {}).get('net_profit', 0)
                confidence = opp.get('confidence', 'unknown')
                
                print(f"   {i}. [{symbol}] {timestamp} | {buy_ex} → {sell_ex} | {profit_pct:.2f}% | ${profit_usd:.2f} | {confidence}")
            
            # Symbol breakdown
            symbol_stats = {}
            for opp in opportunities:
                symbol = opp.get('symbol', 'Unknown')
                if symbol not in symbol_stats:
                    symbol_stats[symbol] = {'count': 0, 'profit': 0}
                symbol_stats[symbol]['count'] += 1
                symbol_stats[symbol]['profit'] += opp.get('estimated_profit_usd', {}).get('net_profit', 0)
            
            if len(symbol_stats) > 1:
                print(f"\n📊 OPPORTUNITIES BY SYMBOL:")
                for symbol, stats in symbol_stats.items():
                    print(f"   {symbol}: {stats['count']} opportunities, ${stats['profit']:.2f} profit")
        
        # Data quality insights
        print(f"\n🔍 DATA QUALITY INSIGHTS:")
        if data_source == 'simulated':
            print(f"   ⚠️  This is DEMO data for testing purposes")
            print(f"   📝 Use for interface development and testing")
        elif data_source == 'live_market':
            print(f"   ✅ This is REAL market data from live exchanges")
            print(f"   🚨 Use for actual trading analysis")
        else:
            print(f"   ❓ Unknown data source")
        
        print(f"\n{'='*60}")
        
    except FileNotFoundError:
        print(f"❌ Error: JSON file not found: {json_file_path}")
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format: {e}")
    except Exception as e:
        print(f"❌ Error analyzing JSON log: {e}")


def generate_interface_data(data: Dict) -> Dict:
    """Generate data formatted for interface presentation."""
    session_info = data['session_info']
    opportunities = data['opportunities']
    price_updates = data['price_updates']
    
    # Calculate real-time metrics
    profitable_opps = [opp for opp in opportunities if opp['profitable']]
    total_profit = sum(opp['estimated_profit']['net_profit'] for opp in profitable_opps)
    
    # Generate interface-ready data
    interface_data = {
        "dashboard": {
            "symbol": session_info['symbol'],
            "threshold": session_info['threshold'],
            "duration_minutes": session_info['duration_seconds'] / 60,
            "total_opportunities": session_info['total_opportunities'],
            "profitable_opportunities": session_info['profitable_opportunities'],
            "success_rate": (session_info['profitable_opportunities'] / session_info['total_opportunities'] * 100) if session_info['total_opportunities'] > 0 else 0,
            "total_profit": total_profit,
            "average_profit": total_profit / len(profitable_opps) if profitable_opps else 0
        },
        "recent_opportunities": opportunities[-10:],  # Last 10 opportunities
        "price_history": price_updates[-20:],  # Last 20 price updates
        "performance_metrics": {
            "hourly_profit": total_profit * (3600 / session_info['duration_seconds']),
            "daily_profit": total_profit * (86400 / session_info['duration_seconds']),
            "profit_per_opportunity": total_profit / session_info['total_opportunities'] if session_info['total_opportunities'] > 0 else 0
        },
        "exchange_performance": {
            "binance_opportunities": len([opp for opp in opportunities if 'BINANCE' in [opp['buy_exchange'], opp['sell_exchange']]]),
            "bybit_opportunities": len([opp for opp in opportunities if 'BYBIT' in [opp['buy_exchange'], opp['sell_exchange']]]),
            "okx_opportunities": len([opp for opp in opportunities if 'OKX' in [opp['buy_exchange'], opp['sell_exchange']]])
        }
    }
    
    return interface_data


def save_interface_data(interface_data: Dict, output_file: str = None):
    """Save interface data to a file."""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_dir = os.path.join(os.path.dirname(__file__), '..', 'csv_output')
        output_file = os.path.join(csv_dir, f"interface_data_{timestamp}.json")
    
    with open(output_file, 'w') as f:
        json.dump(interface_data, f, indent=2, default=str)
    
    print(f"💾 Interface data saved to: {output_file}")
    return output_file


def main():
    """Main function to analyze JSON logs."""
    # Find the latest JSON log
    json_file = find_latest_json_log()
    
    if not json_file:
        print("❌ No JSON execution logs found!")
        print("Run a monitor first to generate JSON logs:")
        print("  cd arbitrage_tools/monitors")
        print("  python demo_signal_monitor.py")
        return
    
    # Analyze the log
    analyze_json_log(json_file)
    
    # Generate interface data
    print("🖥️  GENERATING INTERFACE DATA")
    print("="*50)
    interface_data = generate_interface_data(data)
    
    # Save interface data
    interface_file = save_interface_data(interface_data)
    
    # Show sample interface data
    print("\n📋 SAMPLE INTERFACE DATA STRUCTURE")
    print("-" * 40)
    print("Dashboard Metrics:")
    dashboard = interface_data['dashboard']
    print(f"  Symbol: {dashboard['symbol']}")
    print(f"  Success Rate: {dashboard['success_rate']:.1f}%")
    print(f"  Total Profit: ${dashboard['total_profit']:.2f}")
    print(f"  Average Profit: ${dashboard['average_profit']:.2f}")
    
    print("\nPerformance Metrics:")
    perf = interface_data['performance_metrics']
    print(f"  Hourly Profit: ${perf['hourly_profit']:.2f}")
    print(f"  Daily Profit: ${perf['daily_profit']:.2f}")
    
    print("\nExchange Performance:")
    exchanges = interface_data['exchange_performance']
    for exchange, count in exchanges.items():
        print(f"  {exchange}: {count} opportunities")
    
    print(f"\n✅ Analysis complete! Interface data ready for presentation.")


if __name__ == "__main__":
    main() 