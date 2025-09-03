#!/usr/bin/env python3
"""
Simple Live Market Monitor for Arbitrage Opportunities

This script connects to multiple exchanges (Binance and Bybit) and monitors
live market data for arbitrage opportunities. All data is logged to a single
consolidated JSON file for easy analysis.

Usage:
    python simple_live_monitor.py
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger

from nautilus_trader.config import TradingNodeConfig, LoggingConfig
from nautilus_trader.live.node import TradingNode
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig
from nautilus_trader.adapters.bybit.config import BybitDataClientConfig
from nautilus_trader.model.data import BarType, BarSpecification
from nautilus_trader.model.enums import BarAggregation, PriceType
from nautilus_trader.model.identifiers import Symbol, Venue
from nautilus_trader.model.instruments import Instrument


# Load environment variables
load_dotenv()

# Configuration
EXCHANGES = {
    'binance': {
        'api_key': os.getenv('BINANCE_API_KEY'),
        'api_secret': os.getenv('BINANCE_API_SECRET'),
        'venue': Venue('BINANCE'),
        'symbol': Symbol('ETHUSDT'),
    },
    'bybit': {
        'api_key': os.getenv('BYBIT_API_KEY'),
        'api_secret': os.getenv('BYBIT_API_SECRET'),
        'venue': Venue('BYBIT'),
        'symbol': Symbol('ETHUSDT'),
    }
}

# Arbitrage threshold (price difference percentage)
ARBITRAGE_THRESHOLD = 0.5  # 0.5%

# Create output directory
OUTPUT_DIR = Path(__file__).parent.parent / 'csv_output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Create timestamp for the log file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = f"consolidated_monitor_log_{timestamp}.json"
log_filepath = OUTPUT_DIR / log_filename


class ConsolidatedLogger:
    """Logger that writes all data to a single JSON file"""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.logger = logging.getLogger('consolidated_monitor')
        self.logger.setLevel(logging.INFO)
        
        # Create JSON formatter
        formatter = jsonlogger.JsonFormatter(
            fmt='%(timestamp)s %(level)s %(name)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create file handler
        file_handler = logging.FileHandler(filepath)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Create console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log_market_data(self, exchange: str, symbol: str, price: float, timestamp: datetime):
        """Log market data"""
        self.logger.info(
            "Market data received",
            extra={
                'event_type': 'market_data',
                'exchange': exchange,
                'symbol': symbol,
                'price': price,
                'timestamp': timestamp.isoformat(),
            }
        )
    
    def log_arbitrage_opportunity(self, exchange1: str, exchange2: str, 
                                price1: float, price2: float, 
                                difference: float, percentage: float):
        """Log arbitrage opportunity"""
        self.logger.info(
            "Arbitrage opportunity detected",
            extra={
                'event_type': 'arbitrage_opportunity',
                'exchange1': exchange1,
                'exchange2': exchange2,
                'price1': price1,
                'price2': price2,
                'difference': difference,
                'percentage': percentage,
                'timestamp': datetime.now().isoformat(),
            }
        )
    
    def log_connection_status(self, exchange: str, status: str, details: str = None):
        """Log connection status"""
        extra_data = {
            'event_type': 'connection_status',
            'exchange': exchange,
            'status': status,
            'timestamp': datetime.now().isoformat(),
        }
        if details:
            extra_data['details'] = details
        
        self.logger.info(f"Connection {status} for {exchange}", extra=extra_data)
    
    def log_error(self, exchange: str, error: str, details: str = None):
        """Log errors"""
        extra_data = {
            'event_type': 'error',
            'exchange': exchange,
            'error': error,
            'timestamp': datetime.now().isoformat(),
        }
        if details:
            extra_data['details'] = details
        
        self.logger.error(f"Error on {exchange}: {error}", extra=extra_data)


class ArbitrageMonitor:
    """Monitor for arbitrage opportunities across exchanges"""
    
    def __init__(self):
        self.logger = ConsolidatedLogger(log_filepath)
        self.prices = {}
        self.node = None
        
    async def start_monitoring(self):
        """Start the monitoring process"""
        self.logger.log_connection_status('system', 'starting', f"Log file: {log_filepath}")
        
        try:
            # Create trading node configuration
            log_config = LoggingConfig()
            config = TradingNodeConfig(
                logging=log_config,
                data_clients={
                    'binance': BinanceDataClientConfig(
                        api_key=EXCHANGES['binance']['api_key'],
                        api_secret=EXCHANGES['binance']['api_secret'],
                    ),
                    'bybit': BybitDataClientConfig(
                        api_key=EXCHANGES['bybit']['api_key'],
                        api_secret=EXCHANGES['bybit']['api_secret'],
                    ),
                },
            )
            
            # Create and start trading node
            self.node = TradingNode(config=config)
            
            # Subscribe to market data
            await self._subscribe_to_market_data()
            
            # Start monitoring
            await self._monitor_arbitrage_opportunities()
            
        except Exception as e:
            self.logger.log_error('system', str(e))
            raise
    
    async def _subscribe_to_market_data(self):
        """Subscribe to market data from all exchanges"""
        for exchange_name, exchange_config in EXCHANGES.items():
            try:
                venue = exchange_config['venue']
                symbol = exchange_config['symbol']
                
                # Subscribe to tick data
                await self.node.subscribe_ticker(
                    venue=venue,
                    symbol=symbol,
                    handler=self._handle_tick_data
                )
                
                self.logger.log_connection_status(
                    exchange_name, 
                    'connected', 
                    f"Subscribed to {symbol} on {venue}"
                )
                
            except Exception as e:
                self.logger.log_error(exchange_name, str(e))
    
    async def _handle_tick_data(self, tick):
        """Handle incoming tick data"""
        try:
            exchange = tick.venue.value
            symbol = tick.symbol.value
            price = float(tick.last_price)
            timestamp = tick.timestamp
            
            # Store the latest price
            self.prices[exchange] = {
                'price': price,
                'timestamp': timestamp,
                'symbol': symbol
            }
            
            # Log the market data
            self.logger.log_market_data(exchange, symbol, price, timestamp)
            
        except Exception as e:
            self.logger.log_error(exchange, f"Error handling tick data: {str(e)}")
    
    async def _monitor_arbitrage_opportunities(self):
        """Monitor for arbitrage opportunities"""
        self.logger.log_connection_status('system', 'monitoring', 'Starting arbitrage monitoring')
        
        while True:
            try:
                # Check if we have prices from both exchanges
                if len(self.prices) >= 2:
                    exchanges = list(self.prices.keys())
                    
                    # Calculate price differences
                    for i, exchange1 in enumerate(exchanges):
                        for exchange2 in exchanges[i+1:]:
                            price1 = self.prices[exchange1]['price']
                            price2 = self.prices[exchange2]['price']
                            
                            # Calculate difference and percentage
                            difference = abs(price1 - price2)
                            percentage = (difference / min(price1, price2)) * 100
                            
                            # Check if arbitrage opportunity exists
                            if percentage >= ARBITRAGE_THRESHOLD:
                                self.logger.log_arbitrage_opportunity(
                                    exchange1, exchange2,
                                    price1, price2,
                                    difference, percentage
                                )
                
                # Wait before next check
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.log_error('system', f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop the monitoring process"""
        if self.node:
            await self.node.stop()
        self.logger.log_connection_status('system', 'stopped')


async def main():
    """Main function"""
    monitor = ArbitrageMonitor()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        await monitor.stop()
    except Exception as e:
        print(f"Error: {e}")
        await monitor.stop()


if __name__ == "__main__":
    asyncio.run(main()) 