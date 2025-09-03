#!/usr/bin/env python3
"""
Working Signal Monitor for Arbitrage Detection
Connects to real exchanges and monitors live market data.
"""

import asyncio
import os
import time
from datetime import datetime
from dotenv import load_dotenv

from nautilus_trader.adapters.binance import BINANCE
from nautilus_trader.adapters.binance import BinanceAccountType
from nautilus_trader.adapters.binance import BinanceDataClientConfig
from nautilus_trader.adapters.binance import BinanceLiveDataClientFactory
from nautilus_trader.adapters.bybit import BYBIT
from nautilus_trader.adapters.bybit import BybitDataClientConfig
from nautilus_trader.adapters.bybit import BybitProductType
from nautilus_trader.adapters.bybit import BybitLiveDataClientFactory
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.data import BarSpecification
from nautilus_trader.model.enums import BarAggregation
from nautilus_trader.model.enums import PriceType
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.identifiers import TraderId
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.config import InstrumentProviderConfig
from nautilus_trader.live.node import TradingNode


class WorkingSignalMonitor:
    def __init__(self, symbol="ETHUSDT", threshold=0.50):
        self.symbol = symbol
        self.threshold = threshold
        self.prices = {}
        self.opportunities = []
        self.start_time = None
        
        # Load environment variables
        load_dotenv()
        
        # Setup trading node
        self.node = TradingNode(
            config=TradingNodeConfig(
                trader_id=TraderId("SIGNAL-MONITOR-001"),
                logging=LoggingConfig(log_level="INFO"),
                data_clients={
                    BINANCE: BinanceDataClientConfig(
                        api_key=os.getenv("BINANCE_API_KEY"),
                        api_secret=os.getenv("BINANCE_API_SECRET"),
                        account_type=BinanceAccountType.SPOT,
                        us=False,
                        testnet=False,
                        instrument_provider=InstrumentProviderConfig(load_all=True),
                    ),
                    BYBIT: BybitDataClientConfig(
                        api_key=os.getenv("BYBIT_API_KEY"),
                        api_secret=os.getenv("BYBIT_API_SECRET"),
                        product_types=[BybitProductType.SPOT],
                        testnet=False,
                        instrument_provider=InstrumentProviderConfig(load_all=True),
                    ),
                    # Note: OKX adapter is not yet fully ready for use
                    # Will be added when the adapter issues are resolved
                },
                timeout_connection=30.0,
                timeout_reconciliation=10.0,
                timeout_portfolio=10.0,
                timeout_disconnection=10.0,
                timeout_post_stop=5.0,
            )
        )
        
        # Add client factories
        self.node.add_data_client_factory(BINANCE, BinanceLiveDataClientFactory)
        self.node.add_data_client_factory(BYBIT, BybitLiveDataClientFactory)
        
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
            self._log_opportunity(opportunity)
            
    def _simulate_trade_profit(self, buy_price: float, sell_price: float) -> dict:
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
        
    def _log_opportunity(self, opportunity: dict):
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
        print("🚀 Starting Working Signal Monitor")
        print("="*50)
        print(f"Symbol: {self.symbol}")
        print(f"Threshold: ${self.threshold}")
        print("Monitoring: Binance, Bybit")
        print("Note: OKX support will be added when adapter is ready")
        print("Mode: Signal Detection Only (No Trading)")
        print("="*50)
        
        self.start_time = datetime.now()
        
        # Build and start the node
        self.node.build()
        
        print("✅ Node built! Press Ctrl+C to stop.")
        print("-" * 50)
        
        try:
            # Start the node
            self.node.run()
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping signal monitor...")
            self.node.dispose()
            self._print_final_summary()
            
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
    monitor = WorkingSignalMonitor(
        symbol="ETHUSDT",
        threshold=0.50  # $0.50 minimum price difference
    )
    
    await monitor.start_monitoring()


if __name__ == "__main__":
    asyncio.run(main()) 