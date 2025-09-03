#!/usr/bin/env python3
"""
Signal Monitor for Arbitrage Detection
Reads market data from multiple exchanges and simulates arbitrage opportunities
without placing actual trades.
"""

import asyncio
import os
import time
import csv
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from dotenv import load_dotenv

from nautilus_trader.adapters.binance import BINANCE
from nautilus_trader.adapters.binance import BinanceAccountType
from nautilus_trader.adapters.binance import BinanceDataClientConfig
from nautilus_trader.adapters.bybit import BYBIT
from nautilus_trader.adapters.bybit import BybitDataClientConfig
from nautilus_trader.adapters.bybit import BybitProductType
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.data import BarSpecification
from nautilus_trader.model.enums import BarAggregation
from nautilus_trader.model.enums import PriceType
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.trading.config import TradingNodeConfig
from nautilus_trader.trading.node import TradingNode


class ArbitrageSignalMonitor:
    """
    Monitors multiple exchanges for arbitrage opportunities
    and simulates trades without executing them.
    """
    
    def __init__(self, symbol: str = "ETHUSDT", threshold: float = 0.50, csv_output: bool = True):
        self.symbol = symbol
        self.threshold = threshold
        self.csv_output = csv_output
        self.prices: Dict[str, float] = {}
        self.opportunities: list = []
        self.start_time = None
        
        # Load environment variables
        load_dotenv()
        
        # Initialize trading node
        self.node = TradingNode(
            config=TradingNodeConfig(
                trader_id="SIGNAL-MONITOR-001",
                log_level="INFO",
            )
        )
        
        # Configure data clients for each exchange
        self._setup_data_clients()
        
        # CSV file setup
        if self.csv_output:
            self._setup_csv_files()
        
    def _setup_data_clients(self):
        """Setup data clients for all exchanges."""
        
        # Binance Data Client
        self.node.add_data_client_config(
            BINANCE,
            BinanceDataClientConfig(
                api_key=os.getenv("BINANCE_API_KEY"),
                api_secret=os.getenv("BINANCE_API_SECRET"),
                account_type=BinanceAccountType.SPOT,
                us=False,
            ),
        )
        
        # Bybit Data Client
        self.node.add_data_client_config(
            BYBIT,
            BybitDataClientConfig(
                api_key=os.getenv("BYBIT_API_KEY"),
                api_secret=os.getenv("BYBIT_API_SECRET"),
                product_type=BybitProductType.SPOT,
                testnet=False,
            ),
        )
        
        # Note: OKX adapter might not be fully ready yet
        # We'll monitor Binance and Bybit for now
        
    def _setup_csv_files(self):
        """Setup CSV files for data output."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory if it doesn't exist
        csv_dir = os.path.join(os.path.dirname(__file__), '..', 'csv_output')
        os.makedirs(csv_dir, exist_ok=True)
        
        # Price data CSV
        self.price_csv_file = os.path.join(csv_dir, f"live_price_data_{timestamp}.csv")
        self.price_csv_writer = None
        self.price_csv_file_handle = None
        
        # Arbitrage opportunities CSV
        self.opportunity_csv_file = os.path.join(csv_dir, f"live_arbitrage_opportunities_{timestamp}.csv")
        self.opportunity_csv_writer = None
        self.opportunity_csv_file_handle = None
        
        # Initialize CSV files
        self._init_price_csv()
        self._init_opportunity_csv()
        
    def _init_price_csv(self):
        """Initialize price data CSV file."""
        self.price_csv_file_handle = open(self.price_csv_file, 'w', newline='')
        self.price_csv_writer = csv.writer(self.price_csv_file_handle)
        
        # Write header
        header = ['timestamp', 'binance_price', 'bybit_price', 'min_price', 'max_price', 'price_diff', 'price_diff_percent']
        self.price_csv_writer.writerow(header)
        
    def _init_opportunity_csv(self):
        """Initialize arbitrage opportunities CSV file."""
        self.opportunity_csv_file_handle = open(self.opportunity_csv_file, 'w', newline='')
        self.opportunity_csv_writer = csv.writer(self.opportunity_csv_file_handle)
        
        # Write header
        header = [
            'timestamp', 'symbol', 'buy_exchange', 'buy_price', 'sell_exchange', 'sell_price',
            'price_diff', 'price_diff_percent', 'quantity', 'gross_profit', 'total_fees', 
            'net_profit', 'profitable'
        ]
        self.opportunity_csv_writer.writerow(header)
        
    def _write_price_to_csv(self, timestamp: str, prices: Dict[str, float]):
        """Write price data to CSV."""
        if not self.csv_output or not self.price_csv_writer:
            return
            
        # Calculate min/max for this update
        if len(prices) >= 2:
            min_price = min(prices.values())
            max_price = max(prices.values())
            price_diff = max_price - min_price
            price_diff_percent = (price_diff / min_price) * 100
        else:
            min_price = max_price = price_diff = price_diff_percent = 0
            
        # Write row
        row = [
            timestamp,
            prices.get('BINANCE', 0),
            prices.get('BYBIT', 0),
            min_price,
            max_price,
            price_diff,
            price_diff_percent
        ]
        self.price_csv_writer.writerow(row)
        self.price_csv_file_handle.flush()  # Ensure data is written immediately
        
    def _write_opportunity_to_csv(self, opportunity: Dict):
        """Write arbitrage opportunity to CSV."""
        if not self.csv_output or not self.opportunity_csv_writer:
            return
            
        profit_info = opportunity['estimated_profit']
        
        row = [
            opportunity['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
            opportunity['symbol'],
            opportunity['buy_exchange'],
            opportunity['buy_price'],
            opportunity['sell_exchange'],
            opportunity['sell_price'],
            opportunity['price_diff'],
            opportunity['price_diff_percent'],
            profit_info['quantity'],
            profit_info['gross_profit'],
            profit_info['total_fees'],
            profit_info['net_profit'],
            profit_info['profitable']
        ]
        self.opportunity_csv_writer.writerow(row)
        self.opportunity_csv_file_handle.flush()  # Ensure data is written immediately
        
    def _close_csv_files(self):
        """Close CSV file handles."""
        if self.price_csv_file_handle:
            self.price_csv_file_handle.close()
        if self.opportunity_csv_file_handle:
            self.opportunity_csv_file_handle.close()

    def on_bar(self, bar: Bar):
        """Handle incoming bar data from any exchange."""
        exchange = bar.bar_type.venue.value
        price = float(bar.close)
        
        # Store the latest price for this exchange
        self.prices[exchange] = price
        
        # Log the price update
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {exchange}: ${price:.4f}")
        
        # Check for arbitrage opportunities
        self._check_arbitrage_opportunities()
        
    def _check_arbitrage_opportunities(self):
        """Check for arbitrage opportunities across exchanges."""
        if len(self.prices) < 2:
            return  # Need at least 2 exchanges to compare
            
        exchanges = list(self.prices.keys())
        prices = list(self.prices.values())
        
        # Find min and max prices
        min_price = min(prices)
        max_price = max(prices)
        min_exchange = exchanges[prices.index(min_price)]
        max_exchange = exchanges[prices.index(max_price)]
        
        price_diff = max_price - min_price
        price_diff_percent = (price_diff / min_price) * 100
        
        if price_diff > self.threshold:
            # Simulate arbitrage opportunity
            opportunity = {
                'timestamp': datetime.now(),
                'symbol': self.symbol,
                'buy_exchange': min_exchange,
                'buy_price': min_price,
                'sell_exchange': max_exchange,
                'sell_price': max_price,
                'price_diff': price_diff,
                'price_diff_percent': price_diff_percent,
                'estimated_profit': self._simulate_trade_profit(min_price, max_price)
            }
            
            self.opportunities.append(opportunity)
            self._write_opportunity_to_csv(opportunity)
            self._log_opportunity(opportunity)
            
    def _simulate_trade_profit(self, buy_price: float, sell_price: float) -> Dict:
        """Simulate a trade and calculate potential profit."""
        # Simulate trading 1 ETH
        quantity = 1.0
        
        # Calculate gross profit
        gross_profit = (sell_price - buy_price) * quantity
        
        # Simulate fees (typical 0.1% per trade)
        buy_fee = buy_price * quantity * 0.001
        sell_fee = sell_price * quantity * 0.001
        total_fees = buy_fee + sell_fee
        
        # Net profit
        net_profit = gross_profit - total_fees
        
        return {
            'quantity': quantity,
            'gross_profit': gross_profit,
            'total_fees': total_fees,
            'net_profit': net_profit,
            'profitable': net_profit > 0
        }
        
    def _log_opportunity(self, opportunity: Dict):
        """Log arbitrage opportunity details."""
        timestamp = opportunity['timestamp'].strftime("%H:%M:%S")
        
        print("\n" + "="*60)
        print(f"🚨 ARBITRAGE OPPORTUNITY DETECTED! [{timestamp}]")
        print("="*60)
        print(f"Symbol: {opportunity['symbol']}")
        print(f"Buy:  {opportunity['buy_exchange']} @ ${opportunity['buy_price']:.4f}")
        print(f"Sell: {opportunity['sell_exchange']} @ ${opportunity['sell_price']:.4f}")
        print(f"Price Difference: ${opportunity['price_diff']:.4f} ({opportunity['price_diff_percent']:.2f}%)")
        
        profit_info = opportunity['estimated_profit']
        print(f"\n💰 SIMULATED TRADE (1 {opportunity['symbol']}):")
        print(f"   Gross Profit: ${profit_info['gross_profit']:.4f}")
        print(f"   Total Fees:   ${profit_info['total_fees']:.4f}")
        print(f"   Net Profit:   ${profit_info['net_profit']:.4f}")
        
        if profit_info['profitable']:
            print("   ✅ PROFITABLE OPPORTUNITY!")
        else:
            print("   ❌ Not profitable after fees")
            
        print("="*60 + "\n")
        
    async def start_monitoring(self):
        """Start monitoring market data from all exchanges."""
        print("🚀 Starting Arbitrage Signal Monitor")
        print("="*50)
        print(f"Symbol: {self.symbol}")
        print(f"Threshold: ${self.threshold}")
        print("Monitoring: Binance, Bybit")
        print("Mode: Signal Detection Only (No Trading)")
        if self.csv_output:
            print(f"CSV Output: ✅ Enabled")
            print(f"Price Data: {self.price_csv_file}")
            print(f"Opportunities: {self.opportunity_csv_file}")
        else:
            print("CSV Output: ❌ Disabled")
        print("="*50)
        
        self.start_time = datetime.now()
        
        # Subscribe to market data
        symbol_binance = Symbol(self.symbol, Venue("BINANCE"))
        symbol_bybit = Symbol(self.symbol, Venue("BYBIT"))
        
        # Create bar specifications
        bar_spec = BarSpecification(1, BarAggregation.MINUTE, PriceType.LAST)
        
        # Subscribe to data streams
        self.node.subscribe_bars(BarType(symbol_binance, bar_spec))
        self.node.subscribe_bars(BarType(symbol_bybit, bar_spec))
        
        # Start the node
        await self.node.start()
        
        print("✅ Monitoring started! Press Ctrl+C to stop.")
        print("-" * 50)
        
        try:
            # Keep running and monitor for opportunities
            while True:
                await asyncio.sleep(1)
                
                # Print summary every 30 seconds
                if len(self.opportunities) > 0 and len(self.opportunities) % 5 == 0:
                    self._print_summary()
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping signal monitor...")
            await self.node.stop()
            self._print_final_summary()
            self._close_csv_files()
            
    def _print_summary(self):
        """Print monitoring summary."""
        print(f"\n📊 SUMMARY: {len(self.opportunities)} opportunities detected")
        if self.opportunities:
            profitable_count = sum(1 for opp in self.opportunities 
                                 if opp['estimated_profit']['profitable'])
            print(f"   Profitable: {profitable_count}")
            print(f"   Not Profitable: {len(self.opportunities) - profitable_count}")
            
    def _print_final_summary(self):
        """Print final summary when stopping."""
        duration = datetime.now() - self.start_time
        print(f"\n📈 FINAL SUMMARY")
        print("="*30)
        print(f"Monitoring Duration: {duration}")
        print(f"Total Opportunities: {len(self.opportunities)}")
        
        if self.csv_output:
            print(f"CSV Files Created:")
            print(f"  📊 Price Data: {self.price_csv_file}")
            print(f"  🎯 Opportunities: {self.opportunity_csv_file}")
        
        if self.opportunities:
            profitable_opps = [opp for opp in self.opportunities 
                             if opp['estimated_profit']['profitable']]
            total_profit = sum(opp['estimated_profit']['net_profit'] 
                             for opp in profitable_opps)
            
            print(f"Profitable Opportunities: {len(profitable_opps)}")
            print(f"Total Simulated Profit: ${total_profit:.4f}")
            
            if profitable_opps:
                avg_profit = total_profit / len(profitable_opps)
                print(f"Average Profit per Trade: ${avg_profit:.4f}")


async def main():
    """Main function to run the signal monitor."""
    monitor = ArbitrageSignalMonitor(
        symbol="ETHUSDT",
        threshold=0.50  # $0.50 minimum price difference
    )
    
    await monitor.start_monitoring()


if __name__ == "__main__":
    asyncio.run(main()) 