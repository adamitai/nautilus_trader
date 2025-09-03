#!/usr/bin/env python3
"""
Run Live Market Monitor
Connects to real exchanges for live market data but doesn't execute real trades.
"""

import asyncio
import sys
import os

# Add the monitors directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'monitors'))

from live_market_monitor import LiveMarketMonitor


async def run_live_monitor():
    """Run the live market monitor with real data."""
    print("🚀 Starting Live Market Monitor with Real Data")
    print("="*60)
    print("⚠️  IMPORTANT: This connects to real exchanges but does NOT execute real trades")
    print("📊 Only market data monitoring and signal detection")
    print("="*60)
    
    # Check if API keys are configured
    from dotenv import load_dotenv
    load_dotenv()
    
    binance_key = os.getenv('BINANCE_API_KEY')
    binance_secret = os.getenv('BINANCE_API_SECRET')
    bybit_key = os.getenv('BYBIT_API_KEY')
    bybit_secret = os.getenv('BYBIT_API_SECRET')
    
    if not all([binance_key, binance_secret, bybit_key, bybit_secret]):
        print("❌ API keys not configured!")
        print("Please set up your .env file with API keys:")
        print("  BINANCE_API_KEY=your_binance_key")
        print("  BINANCE_API_SECRET=your_binance_secret")
        print("  BYBIT_API_KEY=your_bybit_key")
        print("  BYBIT_API_SECRET=your_bybit_secret")
        print("\nYou can copy from: arbitrage_tools/examples/api_keys_example.txt")
        return
    
    print("✅ API keys found - proceeding with live monitoring")
    print()
    
    # Create monitor
    monitor = LiveMarketMonitor(
        symbol="ETHUSDT",
        threshold=0.50,  # $0.50 minimum price difference
        json_logging=True  # Enable JSON logging
    )
    
    try:
        # Run the live monitor for 60 seconds
        await monitor.start_monitoring(duration_seconds=60)
        
    except KeyboardInterrupt:
        print("\n🛑 Live monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error during live monitoring: {e}")
        print("This might be due to:")
        print("  - Network connectivity issues")
        print("  - Invalid API keys")
        print("  - Exchange API rate limits")
        print("  - Exchange maintenance")


if __name__ == "__main__":
    asyncio.run(run_live_monitor()) 