#!/usr/bin/env python3
"""
Simple Signal Monitor for Arbitrage Detection
Reads market data from multiple exchanges and simulates arbitrage opportunities.
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv

from nautilus_trader.adapters.binance import BINANCE
from nautilus_trader.adapters.binance import BinanceAccountType
from nautilus_trader.adapters.binance import BinanceDataClientConfig
from nautilus_trader.adapters.bybit import BYBIT
from nautilus_trader.adapters.bybit import BybitDataClientConfig
from nautilus_trader.adapters.bybit import BybitProductType
from nautilus_trader.model.data import BarType
from nautilus_trader.model.data import BarSpecification
from nautilus_trader.model.enums import BarAggregation
from nautilus_trader.model.enums import PriceType
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.trading.config import TradingNodeConfig
from nautilus_trader.trading.node import TradingNode


class SimpleSignalMonitor:
    def __init__(self, symbol="ETHUSDT", threshold=0.50):
        self.symbol = symbol
        self.threshold = threshold
        self.prices = {}
        self.opportunities = []
        
        # Load environment variables
        load_dotenv()
        
        # Setup trading node
        self.node = TradingNode(
            config=TradingNodeConfig(
                trader_id="SIGNAL-MONITOR-001",
                log_level="INFO",
            )
        )
        
        self._setup_data_clients()
        
    def _setup_data_clients(self):
        """Setup data clients for exchanges."""
        
        # Binance
        self.node.add_data_client_config(
            BINANCE,
            BinanceDataClientConfig(
                api_key=os.getenv("BINANCE_API_KEY"),
                api_secret=os.getenv("BINANCE_API_SECRET"),
                account_type=BinanceAccountType.SPOT,
                us=False,
            ),
        )
        
        # Bybit
        self.node.add_data_client_config(
            BYBIT,
            BybitDataClientConfig(
                api_key=os.getenv("BYBIT_API_KEY"),
                api_secret=os.getenv("BYBIT_API_SECRET"),
                product_type=BybitProductType.SPOT,
                testnet=False,
            ),
        )
        
    def on_bar(self, bar):
        """Handle incoming bar data."""
        exchange = bar.bar_type.venue.value
        price = float(bar.close)
        
        self.prices[exchange] = price
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {exchange}: ${price:.4f}")
        
        self._check_arbitrage()
        
    def _check_arbitrage(self):
        """Check for arbitrage opportunities."""
        if len(self.prices) < 2:
            return
            
        exchanges = list(self.prices.keys())
        prices = list(self.prices.values())
        
        min_price = min(prices)
        max_price = max(prices)
        min_exchange = exchanges[prices.index(min_price)]
        max_exchange = exchanges[prices.index(max_price)]
        
        price_diff = max_price - min_price
        
        if price_diff > self.threshold:
            self._log_opportunity(min_exchange, min_price, max_exchange, max_price, price_diff)
            
    def _log_opportunity(self, buy_exchange, buy_price, sell_exchange, sell_price, price_diff):
        """Log arbitrage opportunity."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print("\n" + "="*50)
        print(f"🚨 ARBITRAGE OPPORTUNITY! [{timestamp}]")
        print(f"Buy:  {buy_exchange} @ ${buy_price:.4f}")
        print(f"Sell: {sell_exchange} @ ${sell_price:.4f}")
        print(f"Diff: ${price_diff:.4f}")
        print("="*50 + "\n")
        
        self.opportunities.append({
            'timestamp': timestamp,
            'buy_exchange': buy_exchange,
            'buy_price': buy_price,
            'sell_exchange': sell_exchange,
            'sell_price': sell_price,
            'price_diff': price_diff
        })


def main():
    print("🚀 Starting Simple Signal Monitor")
    print("="*40)
    print("Monitoring: Binance, Bybit")
    print("Mode: Signal Detection Only")
    print("="*40)
    
    monitor = SimpleSignalMonitor("ETHUSDT", 0.50)
    
    try:
        # This would normally start the node and subscribe to data
        # For now, we'll simulate the monitoring
        print("✅ Monitor configured!")
        print("📊 Would start monitoring market data...")
        print("🛑 Press Ctrl+C to stop")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")


if __name__ == "__main__":
    main() 