#!/usr/bin/env python3
"""
Demo Arbitrage Monitor Runner

This script runs the demo signal monitor with JSON logging enabled.
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitors.demo_signal_monitor import DemoArbitrageMonitor


def main():
    """Run the demo arbitrage monitor."""
    print("🚀 Starting Demo Arbitrage Monitor with JSON Logging")
    print("=" * 60)
    
    # Configuration with multiple symbols
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"]
    threshold = 0.5  # 0.5% minimum profit threshold
    duration_seconds = 300  # Run for 5 minutes
    json_logging = True  # Enable JSON logging
    
    # Strategy parameters
    strategy_params = {
        "volume_usd": 1000.0,
        "trade_fee_percent": 0.1,
        "slippage_percent": 0.05,
        "min_volume_usd": 100.0,
        "max_volume_usd": 10000.0,
        "confidence_threshold": 1.0
    }
    
    print(f"📊 Configuration:")
    print(f"   Symbols: {', '.join(symbols)}")
    print(f"   Threshold: {threshold}%")
    print(f"   Duration: {duration_seconds} seconds ({duration_seconds/60:.1f} minutes)")
    print(f"   Volume: ${strategy_params['volume_usd']}")
    print(f"   Trade Fee: {strategy_params['trade_fee_percent']}%")
    print(f"   Slippage: {strategy_params['slippage_percent']}%")
    print(f"   JSON Logging: {'Enabled' if json_logging else 'Disabled'}")
    print()
    
    # Create and run monitor
    monitor = DemoArbitrageMonitor(
        symbols=symbols,
        threshold=threshold,
        volume_usd=strategy_params['volume_usd'],
        json_logging=json_logging,
        csv_logging=True,
        trade_fee_percent=strategy_params['trade_fee_percent'],
        slippage_percent=strategy_params['slippage_percent'],
        min_volume_usd=strategy_params['min_volume_usd'],
        max_volume_usd=strategy_params['max_volume_usd'],
        confidence_threshold=strategy_params['confidence_threshold']
    )
    
    try:
        monitor.start(duration_seconds=duration_seconds)
        print("\n✅ Demo monitor completed successfully!")
        
        # Show the generated files
        if json_logging:
            print("\n📁 Generated Files:")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_file = f"csv_output/arbitrage_log_{timestamp}.json"
            if os.path.exists(json_file):
                print(f"   JSON Log: {json_file}")
            
            # Analyze the JSON log
            if os.path.exists(json_file):
                print(f"\n📊 Analyzing JSON Log...")
                from scripts.analyze_json_log import analyze_json_log
                analyze_json_log(json_file)
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo monitor stopped by user")
    except Exception as e:
        print(f"\n❌ Error running demo monitor: {e}")


if __name__ == "__main__":
    main() 