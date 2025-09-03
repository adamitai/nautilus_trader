#!/usr/bin/env python3
"""
Live Arbitrage Strategy Example
This shows how to set up API keys securely for live trading.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from nautilus_trader.adapters.binance import BINANCE
from nautilus_trader.adapters.binance import BinanceAccountType
from nautilus_trader.adapters.binance import BinanceDataClientConfig
from nautilus_trader.adapters.binance import BinanceExecClientConfig
from nautilus_trader.adapters.bybit import BYBIT
from nautilus_trader.adapters.bybit import BybitDataClientConfig
from nautilus_trader.adapters.bybit import BybitExecClientConfig
from nautilus_trader.adapters.bybit import BybitProductType
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.trading.config import TradingNodeConfig
from nautilus_trader.trading.node import TradingNode

# Import our custom arbitrage strategy
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strategies.arbitrage_strategy import ArbitrageStrategy


def main():
    print("🚀 Setting up Live Arbitrage Strategy")
    print("=" * 50)
    
    # Method 1: Environment Variables (Recommended)
    # The adapters will automatically pick up these environment variables
    binance_api_key = os.getenv("BINANCE_API_KEY")
    binance_api_secret = os.getenv("BINANCE_API_SECRET")
    bybit_api_key = os.getenv("BYBIT_API_KEY")
    bybit_api_secret = os.getenv("BYBIT_API_SECRET")
    
    # Method 2: Direct Configuration (Alternative)
    # You can also pass keys directly to the config objects
    config = TradingNodeConfig(
        trader_id="LIVE-ARBITRAGE-001",
        log_level="INFO",
    )
    
    node = TradingNode(config=config)
    
    # Configure Binance
    node.add_data_client_config(
        BINANCE,
        BinanceDataClientConfig(
            api_key=binance_api_key,  # Will use env var if None
            api_secret=binance_api_secret,  # Will use env var if None
            account_type=BinanceAccountType.SPOT,  # or USDT_FUTURE
            us=False,  # Set to True for Binance US
        ),
    )
    
    node.add_exec_client_config(
        BINANCE,
        BinanceExecClientConfig(
            api_key=binance_api_key,  # Will use env var if None
            api_secret=binance_api_secret,  # Will use env var if None
            account_type=BinanceAccountType.SPOT,  # or USDT_FUTURE
            us=False,  # Set to True for Binance US
        ),
    )
    
    # Configure Bybit
    node.add_data_client_config(
        BYBIT,
        BybitDataClientConfig(
            api_key=bybit_api_key,  # Will use env var if None
            api_secret=bybit_api_secret,  # Will use env var if None
            product_type=BybitProductType.SPOT,  # or LINEAR, INVERSE
            testnet=False,  # Set to True for testnet
        ),
    )
    
    node.add_exec_client_config(
        BYBIT,
        BybitExecClientConfig(
            api_key=bybit_api_key,  # Will use env var if None
            api_secret=bybit_api_secret,  # Will use env var if None
            product_type=BybitProductType.SPOT,  # or LINEAR, INVERSE
            testnet=False,  # Set to True for testnet
        ),
    )
    
    print("✅ Configuration complete!")
    print("📊 API Keys loaded from environment variables")
    print("🔐 Keys are secure and not hardcoded in the script")
    
    # Add your arbitrage strategy here
    # strategy = ArbitrageStrategy(...)
    # node.add_strategy(strategy)
    
    print("=" * 50)
    print("🚀 Ready to start live trading!")
    print("=" * 50)


if __name__ == "__main__":
    main() 