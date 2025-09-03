#!/usr/bin/env python3
"""
Demo Signal Monitor for Arbitrage Detection
Simulates market data to demonstrate arbitrage opportunities.
"""

import time
import random
import csv
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List


class DemoArbitrageMonitor:
    """Demo arbitrage signal monitor with simulated data."""
    
    def __init__(self, symbols: List[str] = None, threshold: float = 0.5, 
                 volume_usd: float = 1000.0, json_logging: bool = True, 
                 csv_logging: bool = True, trade_fee_percent: float = 0.1,
                 slippage_percent: float = 0.05, min_volume_usd: float = 100.0,
                 max_volume_usd: float = 10000.0, confidence_threshold: float = 1.0):
        """
        Initialize the demo arbitrage monitor.
        
        Args:
            symbols: List of trading symbols to monitor
            threshold: Minimum profit percentage to trigger signal
            volume_usd: Trading volume in USD
            json_logging: Enable JSON logging
            csv_logging: Enable CSV logging
            trade_fee_percent: Trading fee percentage
            slippage_percent: Slippage percentage
            min_volume_usd: Minimum volume for trades
            max_volume_usd: Maximum volume for trades
            confidence_threshold: Minimum confidence level
        """
        self.symbols = symbols or ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"]
        self.threshold = threshold
        self.volume_usd = volume_usd
        self.json_logging = json_logging
        self.csv_logging = csv_logging
        self.trade_fee_percent = trade_fee_percent
        self.slippage_percent = slippage_percent
        self.min_volume_usd = min_volume_usd
        self.max_volume_usd = max_volume_usd
        self.confidence_threshold = confidence_threshold
        
        # Strategy parameters
        self.strategy_params = {
            "symbols": self.symbols,
            "threshold": self.threshold,
            "volume_usd": self.volume_usd,
            "trade_fee_percent": self.trade_fee_percent,
            "slippage_percent": self.slippage_percent,
            "min_volume_usd": self.min_volume_usd,
            "max_volume_usd": self.max_volume_usd,
            "confidence_threshold": self.confidence_threshold,
            "strategy_type": "cross_exchange_arbitrage",
            "risk_level": "medium",
            "execution_mode": "simulation",
            "data_frequency": "1_second",
            "max_positions": 5,
            "stop_loss_percent": 2.0,
            "take_profit_percent": 5.0
        }
        
        self.start_time = None
        self.running = False
        self.opportunities = []
        
        # Price storage for each symbol
        self.prices = {symbol: {} for symbol in self.symbols}
        
        # CSV output setup
        if self.csv_logging:
            self.csv_file = None
            self.csv_writer = None
            self._setup_csv_output()
        
        # Execution log for JSON output
        self.execution_log = {
            "session_info": {
                "symbols": self.symbols,
                "strategy_params": self.strategy_params,
                "threshold": threshold,
                "start_time": None,
                "end_time": None,
                "duration_seconds": 0,
                "total_price_updates": 0,
                "total_opportunities": 0,
                "profitable_opportunities": 0,
                "total_simulated_profit": 0.0,
                "data_source": "simulated",  # Indicate data source
                "data_quality": "demo",      # Data quality indicator
                "exchanges": ["BINANCE", "BYBIT", "OKX"]  # Simulated exchanges
            },
            "price_updates": [],
            "opportunities": [],
            "system_events": []
        }
        
        # CSV file setup
        if self.csv_logging:
            self._setup_csv_files()
            
        # JSON file setup
        if self.json_logging:
            self._setup_json_logging()
        
    def _setup_json_logging(self):
        """Setup JSON logging file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory if it doesn't exist
        csv_dir = os.path.join(os.path.dirname(__file__), '..', 'csv_output')
        os.makedirs(csv_dir, exist_ok=True)
        
        # JSON log file
        self.json_log_file = os.path.join(csv_dir, f"execution_log_{timestamp}.json")
        
    def _log_system_event(self, event_type: str, message: str, data: Dict = None):
        """Log a system event to JSON."""
        if not self.json_logging:
            return
            
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "data": data or {}
        }
        
        self.execution_log["system_events"].append(event)
        
    def _log_price_update(self, timestamp: str, prices: Dict[str, float], symbol: str):
        """Log price update to JSON."""
        if not self.json_logging:
            return
            
        # Calculate min/max for this update
        if len(prices) >= 2:
            min_price = min(prices.values())
            max_price = max(prices.values())
            price_diff = max_price - min_price
            price_diff_percent = (price_diff / min_price) * 100
        else:
            min_price = max_price = price_diff = price_diff_percent = 0
            
        price_update = {
            "timestamp": timestamp,
            "prices": prices,
            "min_price": min_price,
            "max_price": max_price,
            "price_diff": price_diff,
            "price_diff_percent": price_diff_percent,
            "exchanges": list(prices.keys()),
            "data_source": "simulated",  # Indicate this is simulated data
            "data_quality": "demo",       # Data quality indicator
            "symbol": symbol
        }
        
        self.execution_log["price_updates"].append(price_update)
        self.execution_log["session_info"]["total_price_updates"] += 1
        
    def _log_opportunity(self, opportunity: Dict):
        """Log arbitrage opportunity to JSON."""
        if not self.json_logging:
            return
            
        # Update session statistics
        self.execution_log["session_info"]["total_opportunities"] += 1
        if opportunity['estimated_profit']['profitable']:
            self.execution_log["session_info"]["profitable_opportunities"] += 1
            self.execution_log["session_info"]["total_simulated_profit"] += opportunity['estimated_profit']['net_profit']
        
        # Create opportunity log entry
        opportunity_log = {
            "timestamp": opportunity['timestamp'].isoformat(),
            "symbol": opportunity['symbol'],
            "buy_exchange": opportunity['buy_exchange'],
            "sell_exchange": opportunity['sell_exchange'],
            "buy_price": opportunity['buy_price'],
            "sell_price": opportunity['sell_price'],
            "price_difference": opportunity['price_diff'],
            "profit_percent": opportunity['price_diff_percent'],
            "estimated_profit_usd": opportunity['estimated_profit'],
            "volume_usd": opportunity['volume_usd'],
            "strategy_params": opportunity['strategy_params'],
            "data_source": "simulated",  # Indicate this is simulated data
            "data_quality": "demo",      # Data quality indicator
            "confidence": "high" if opportunity['price_diff_percent'] > 2.0 else "medium" if opportunity['price_diff_percent'] > 1.0 else "low"
        }
        
        self.execution_log["opportunities"].append(opportunity_log)
        
    def _save_json_log(self):
        """Save the complete execution log to JSON file."""
        if not self.json_logging:
            return
            
        # Update session info
        end_time = datetime.now()
        self.execution_log["session_info"]["end_time"] = end_time.isoformat()
        self.execution_log["session_info"]["duration_seconds"] = (end_time - self.start_time).total_seconds()
        
        # Save to file
        with open(self.json_log_file, 'w') as f:
            json.dump(self.execution_log, f, indent=2, default=str)
            
        print(f"📄 JSON Log: {self.json_log_file}")
        
    def _setup_csv_files(self):
        """Setup CSV files for data output."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory if it doesn't exist
        csv_dir = os.path.join(os.path.dirname(__file__), '..', 'csv_output')
        os.makedirs(csv_dir, exist_ok=True)
        
        # Price data CSV
        self.price_csv_file_path = f"csv_output/price_data_{timestamp}.csv"
        self.price_csv_file = None
        self.price_csv_writer = None
        if self.csv_logging:
            self.price_csv_file = open(self.price_csv_file_path, 'w', newline='')
            self.price_csv_writer = csv.writer(self.price_csv_file)
            header = ['timestamp', 'symbol', 'binance_price', 'bybit_price', 'okx_price', 'min_price', 'max_price', 'price_diff', 'price_diff_percent']
            self.price_csv_writer.writerow(header)
        
        # Opportunity CSV
        self.opportunity_csv_file_path = f"csv_output/arbitrage_opportunities_{timestamp}.csv"
        self.opportunity_csv_file = None
        self.opportunity_csv_writer = None
        if self.csv_logging:
            self.opportunity_csv_file = open(self.opportunity_csv_file_path, 'w', newline='')
            self.opportunity_csv_writer = csv.writer(self.opportunity_csv_file)
            header = ['timestamp', 'symbol', 'buy_exchange', 'buy_price', 'sell_exchange', 'sell_price', 'price_diff', 'price_diff_percent', 'estimated_profit', 'volume_usd', 'profitable']
            self.opportunity_csv_writer.writerow(header)
    
    def _write_price_to_csv(self, timestamp: str, prices: Dict[str, float], symbol: str):
        """Write price data to CSV."""
        if not self.csv_logging or not self.price_csv_writer:
            return
            
        binance_price = prices.get('BINANCE', 0)
        bybit_price = prices.get('BYBIT', 0)
        okx_price = prices.get('OKX', 0)
        
        min_price = min(prices.values()) if prices else 0
        max_price = max(prices.values()) if prices else 0
        price_diff = max_price - min_price
        price_diff_percent = (price_diff / min_price * 100) if min_price > 0 else 0
        
        row = [
            timestamp, symbol, binance_price, bybit_price, okx_price,
            min_price, max_price, price_diff, price_diff_percent
        ]
        self.price_csv_writer.writerow(row)
        self.price_csv_file.flush()
    
    def _write_opportunity_to_csv(self, opportunity: Dict):
        """Write arbitrage opportunity to CSV."""
        if not self.csv_logging or not self.opportunity_csv_writer:
            return
            
        row = [
            opportunity['timestamp'],
            opportunity['symbol'],
            opportunity['buy_exchange'],
            opportunity['buy_price'],
            opportunity['sell_exchange'],
            opportunity['sell_price'],
            opportunity['price_diff'],
            opportunity['price_diff_percent'],
            opportunity['estimated_profit']['net_profit'],
            opportunity['volume_usd'],
            opportunity['estimated_profit']['profitable']
        ]
        self.opportunity_csv_writer.writerow(row)
        self.opportunity_csv_file.flush()
        
    def simulate_market_data(self):
        """Simulate market data from different exchanges."""
        # Simulate realistic ETH prices around $3000
        base_price = 3000.0
        
        # Add some random variation to simulate real market conditions
        binance_price = base_price + random.uniform(-10, 10)
        bybit_price = base_price + random.uniform(-10, 10)
        okx_price = base_price + random.uniform(-10, 10)
        
        # Occasionally create larger price differences to trigger arbitrage
        if random.random() < 0.1:  # 10% chance of larger difference
            binance_price += random.uniform(-50, 50)
            bybit_price += random.uniform(-50, 50)
            okx_price += random.uniform(-50, 50)
        
        self.prices = {
            "BINANCE": round(binance_price, 2),
            "BYBIT": round(bybit_price, 2),
            "OKX": round(okx_price, 2)
        }
        
        return self.prices
        
    def check_arbitrage_opportunities(self):
        """Check for arbitrage opportunities across exchanges."""
        if len(self.prices) < 2:
            return
            
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
                'symbol': self.symbols[0],
                'buy_exchange': min_exchange,
                'buy_price': min_price,
                'sell_exchange': max_exchange,
                'sell_price': max_price,
                'price_diff': price_diff,
                'price_diff_percent': price_diff_percent,
                'estimated_profit': self.simulate_trade_profit(min_price, max_price)
            }
            
            self.opportunities.append(opportunity)
            self._write_opportunity_to_csv(opportunity)
            self._log_opportunity(opportunity)
            self.log_opportunity(opportunity)
            
    def simulate_trade_profit(self, buy_price: float, sell_price: float) -> dict:
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
        
    def log_opportunity(self, opportunity: dict):
        """Log arbitrage opportunity details."""
        timestamp = opportunity['timestamp'].strftime("%H:%M:%S")
        
        print("\n" + "="*60)
        print(f"🚨 ARBITRAGE OPPORTUNITY DETECTED! [{timestamp}]")
        print("="*60)
        print(f"Symbol: {opportunity['symbol']}")
        print(f"Buy:  {opportunity['buy_exchange']} @ ${opportunity['buy_price']:.2f}")
        print(f"Sell: {opportunity['sell_exchange']} @ ${opportunity['sell_price']:.2f}")
        print(f"Price Difference: ${opportunity['price_diff']:.2f} ({opportunity['price_diff_percent']:.2f}%)")
        
        profit_info = opportunity['estimated_profit']
        print(f"\n💰 SIMULATED TRADE (1 {opportunity['symbol']}):")
        print(f"   Gross Profit: ${profit_info['gross_profit']:.2f}")
        print(f"   Total Fees:   ${profit_info['total_fees']:.2f}")
        print(f"   Net Profit:   ${profit_info['net_profit']:.2f}")
        
        if profit_info['profitable']:
            print("   ✅ PROFITABLE OPPORTUNITY!")
        else:
            print("   ❌ Not profitable after fees")
            
        print("="*60 + "\n")
        
    def start(self, duration_seconds: int = 60):
        """Start the demo signal monitor."""
        print("🚀 Starting Demo Signal Monitor")
        print("="*50)
        print(f"Symbols: {', '.join(self.symbols)}")
        print(f"Threshold: {self.threshold}%")
        print("Monitoring: Binance, Bybit, OKX (Simulated)")
        print("Mode: Signal Detection Only")
        print(f"Duration: {duration_seconds} seconds")
        if self.csv_logging:
            print(f"CSV Output: ✅ Enabled")
            print(f"Price Data: {self.price_csv_file_path}")
            print(f"Opportunities: {self.opportunity_csv_file_path}")
        if self.json_logging:
            print(f"JSON Logging: ✅ Enabled")
        print()
        
        self.start_time = datetime.now()
        self.running = True
        
        # Log session start
        self._log_system_event("session_start", "Demo signal monitor started", {
            "symbols": self.symbols,
            "threshold": self.threshold,
            "duration_seconds": duration_seconds
        })
        
        end_time = self.start_time + timedelta(seconds=duration_seconds)
        
        try:
            while datetime.now() < end_time and self.running:
                # Generate simulated prices for each symbol
                for symbol in self.symbols:
                    self._generate_simulated_prices(symbol)
                
                time.sleep(1)  # Update every second
                
        except KeyboardInterrupt:
            print("\n⏹️  Stopping monitor...")
        finally:
            self.running = False
            self._finish_session()
    
    def _generate_simulated_prices(self, symbol: str):
        """Generate simulated prices for a specific symbol."""
        # Base prices for different symbols
        base_prices = {
            "BTCUSDT": 45000,
            "ETHUSDT": 2800,
            "ADAUSDT": 0.45,
            "DOTUSDT": 7.2,
            "LINKUSDT": 15.8
        }
        
        base_price = base_prices.get(symbol, 100)
        
        # Generate slightly different prices for each exchange
        prices = {}
        for exchange in ["BINANCE", "BYBIT", "OKX"]:
            # Add some random variation (±2%)
            variation = random.uniform(-0.02, 0.02)
            price = base_price * (1 + variation)
            prices[exchange] = round(price, 4)
        
        # Store prices
        self.prices[symbol] = prices
        
        # Log price update
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log_price_update(timestamp, prices, symbol)
        self._write_price_to_csv(timestamp, prices, symbol)
        
        # Check for arbitrage opportunities
        self._check_arbitrage_opportunity(prices, symbol)
    
    def _check_arbitrage_opportunity(self, prices: Dict[str, float], symbol: str):
        """Check for arbitrage opportunities in the given prices."""
        if len(prices) < 2:
            return
        
        # Find min and max prices
        min_price = min(prices.values())
        max_price = max(prices.values())
        min_exchange = min(prices, key=prices.get)
        max_exchange = max(prices, key=prices.get)
        
        price_difference = max_price - min_price
        price_diff_percent = (price_difference / min_price) * 100
        
        # Check if difference exceeds threshold
        if price_diff_percent >= self.threshold:
            # Calculate estimated profit
            estimated_profit = self.simulate_trade_profit(min_price, max_price)
            
            # Create opportunity record
            opportunity = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'buy_exchange': min_exchange,
                'buy_price': min_price,
                'sell_exchange': max_exchange,
                'sell_price': max_price,
                'price_diff': price_difference,
                'price_diff_percent': price_diff_percent,
                'estimated_profit': estimated_profit,
                'volume_usd': self.volume_usd,
                'strategy_params': self.strategy_params
            }
            
            self.opportunities.append(opportunity)
            
            # Log to CSV
            self._write_opportunity_to_csv(opportunity)
            
            # Log to JSON
            self._log_opportunity(opportunity)
            
            # Print to console
            print(f"🎯 ARBITRAGE OPPORTUNITY ({symbol}):")
            print(f"   Buy: {min_exchange} @ ${min_price:.4f}")
            print(f"   Sell: {max_exchange} @ ${max_price:.4f}")
            print(f"   Difference: ${price_difference:.4f} ({price_diff_percent:.2f}%)")
            print(f"   Estimated Profit: ${estimated_profit['net_profit']:.2f}")
            print()
        
    def _finish_session(self):
        """Finish the session and log end."""
        # Log session end
        self._log_system_event("session_end", "Demo signal monitor completed")
        
        self.print_final_summary()
        self._close_csv_files()
        self._save_json_log()
            
    def _close_csv_files(self):
        """Close CSV file handles."""
        if self.price_csv_file:
            self.price_csv_file.close()
        if self.opportunity_csv_file:
            self.opportunity_csv_file.close()
            
    def print_final_summary(self):
        """Print final summary when stopping."""
        duration = datetime.now() - self.start_time
        print(f"\n📈 FINAL SUMMARY")
        print("="*30)
        print(f"Monitoring Duration: {duration}")
        print(f"Total Opportunities: {len(self.opportunities)}")
        
        if self.csv_logging:
            print(f"CSV Files Created:")
            print(f"  📊 Price Data: {self.price_csv_file_path}")
            print(f"  🎯 Opportunities: {self.opportunity_csv_file_path}")
            
        if self.json_logging:
            print(f"JSON Log Created:")
            print(f"  📄 Execution Log: {self.json_log_file}")
        
        if self.opportunities:
            profitable_opps = [opp for opp in self.opportunities 
                             if opp['estimated_profit']['profitable']]
            total_profit = sum(opp['estimated_profit']['net_profit'] 
                             for opp in profitable_opps)
            
            print(f"Profitable Opportunities: {len(profitable_opps)}")
            print(f"Total Simulated Profit: ${total_profit:.2f}")
            
            if profitable_opps:
                avg_profit = total_profit / len(profitable_opps)
                print(f"Average Profit per Trade: ${avg_profit:.2f}")


def main():
    """Main function to run the demo signal monitor."""
    monitor = DemoArbitrageMonitor(
        symbols=["ETHUSDT"],
        threshold=0.50,  # $0.50 minimum price difference
        volume_usd=1000.0,
        json_logging=True,  # Enable JSON logging
        csv_logging=True,   # Enable CSV logging
        trade_fee_percent=0.1,
        slippage_percent=0.05,
        min_volume_usd=100.0,
        max_volume_usd=10000.0,
        confidence_threshold=1.0
    )
    
    # Run for 30 seconds
    monitor.start(duration_seconds=30)


if __name__ == "__main__":
    main() 