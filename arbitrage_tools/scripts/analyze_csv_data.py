#!/usr/bin/env python3
"""
CSV Data Analysis Script
Demonstrates how to analyze the CSV output from signal monitors.
"""

import pandas as pd
import os
from datetime import datetime


def analyze_csv_data():
    """Analyze CSV data from signal monitors."""
    print("📊 CSV Data Analysis")
    print("="*40)
    
    # Find the most recent CSV files
    csv_dir = os.path.join(os.path.dirname(__file__), '..', 'csv_output')
    if not os.path.exists(csv_dir):
        print("❌ No CSV output directory found. Run a signal monitor first.")
        return
    
    # Find CSV files
    price_files = [f for f in os.listdir(csv_dir) if f.startswith("price_data_")]
    opportunity_files = [f for f in os.listdir(csv_dir) if f.startswith("arbitrage_opportunities_")]
    
    if not price_files or not opportunity_files:
        print("❌ No CSV files found. Run a signal monitor first.")
        return
    
    # Use the most recent files
    latest_price_file = sorted(price_files)[-1]
    latest_opportunity_file = sorted(opportunity_files)[-1]
    
    price_path = os.path.join(csv_dir, latest_price_file)
    opportunity_path = os.path.join(csv_dir, latest_opportunity_file)
    
    print(f"📈 Analyzing price data: {latest_price_file}")
    print(f"🎯 Analyzing opportunities: {latest_opportunity_file}")
    print()
    
    # Load data
    try:
        price_df = pd.read_csv(price_path)
        opps_df = pd.read_csv(opportunity_path)
    except Exception as e:
        print(f"❌ Error loading CSV files: {e}")
        return
    
    # Basic statistics
    print("📊 BASIC STATISTICS")
    print("-" * 20)
    print(f"Total price updates: {len(price_df)}")
    print(f"Total opportunities: {len(opps_df)}")
    print(f"Profitable opportunities: {len(opps_df[opps_df['profitable'] == True])}")
    print(f"Unprofitable opportunities: {len(opps_df[opps_df['profitable'] == False])}")
    print()
    
    # Price analysis
    print("💰 PRICE ANALYSIS")
    print("-" * 20)
    avg_diff = price_df['price_diff'].mean()
    max_diff = price_df['price_diff'].max()
    min_diff = price_df['price_diff'].min()
    
    print(f"Average price difference: ${avg_diff:.2f}")
    print(f"Maximum price difference: ${max_diff:.2f}")
    print(f"Minimum price difference: ${min_diff:.2f}")
    print()
    
    # Exchange performance
    print("🏢 EXCHANGE PERFORMANCE")
    print("-" * 20)
    binance_avg = price_df['binance_price'].mean()
    bybit_avg = price_df['bybit_price'].mean()
    
    print(f"Binance average price: ${binance_avg:.2f}")
    print(f"Bybit average price: ${bybit_avg:.2f}")
    print(f"Price difference: ${abs(binance_avg - bybit_avg):.2f}")
    print()
    
    # Profitability analysis
    print("💵 PROFITABILITY ANALYSIS")
    print("-" * 20)
    if len(opps_df) > 0:
        profitable_opps = opps_df[opps_df['profitable'] == True]
        unprofitable_opps = opps_df[opps_df['profitable'] == False]
        
        total_profit = opps_df['net_profit'].sum()
        avg_profit = opps_df['net_profit'].mean()
        total_fees = opps_df['total_fees'].sum()
        
        print(f"Total potential profit: ${total_profit:.2f}")
        print(f"Average profit per trade: ${avg_profit:.2f}")
        print(f"Total fees paid: ${total_fees:.2f}")
        print(f"Profitability rate: {(len(profitable_opps) / len(opps_df) * 100):.1f}%")
        print()
        
        if len(profitable_opps) > 0:
            best_trade = profitable_opps.loc[profitable_opps['net_profit'].idxmax()]
            print(f"Best profitable trade:")
            print(f"  Buy: {best_trade['buy_exchange']} @ ${best_trade['buy_price']:.2f}")
            print(f"  Sell: {best_trade['sell_exchange']} @ ${best_trade['sell_price']:.2f}")
            print(f"  Profit: ${best_trade['net_profit']:.2f}")
            print()
    
    # Time analysis
    print("⏰ TIME ANALYSIS")
    print("-" * 20)
    if len(opps_df) > 0:
        opps_df['timestamp'] = pd.to_datetime(opps_df['timestamp'])
        opps_df['hour'] = opps_df['timestamp'].dt.hour
        opps_df['minute'] = opps_df['timestamp'].dt.minute
        
        # Find most active minute
        minute_counts = opps_df.groupby('minute').size()
        most_active_minute = minute_counts.idxmax()
        print(f"Most active minute: {most_active_minute}:XX")
        print(f"Opportunities in that minute: {minute_counts.max()}")
        print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS")
    print("-" * 20)
    if len(opps_df) > 0:
        profitable_rate = len(profitable_opps) / len(opps_df) * 100
        
        if profitable_rate > 70:
            print("✅ High profitability rate - consider lowering threshold")
        elif profitable_rate < 30:
            print("⚠️  Low profitability rate - consider raising threshold")
        else:
            print("🔄 Moderate profitability rate - current threshold seems appropriate")
        
        if avg_diff < 5:
            print("💡 Small price differences - consider monitoring more volatile pairs")
        elif avg_diff > 20:
            print("💡 Large price differences - consider more conservative thresholds")
        
        print(f"📈 Suggested threshold: ${max(0.5, avg_diff * 0.8):.2f}")
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    analyze_csv_data() 