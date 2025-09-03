#!/usr/bin/env python3
"""
Simple arbitrage strategy test using existing test data.
This example demonstrates how to test arbitrage between different price types
using the built-in test data provider.
"""

import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.engine import BacktestEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.model.currencies import ETH
from nautilus_trader.model.currencies import USDT
from nautilus_trader.model.data import BarType
from nautilus_trader.model.data import BarSpecification
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import BarAggregation
from nautilus_trader.model.enums import BookType
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.enums import PriceType
from nautilus_trader.model.identifiers import TraderId
from nautilus_trader.model.objects import Money
from nautilus_trader.persistence.wranglers import TradeTickDataWrangler
from nautilus_trader.test_kit.providers import TestDataProvider
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from strategies.arbitrage_strategy import ArbitrageStrategy


def main():
    print("🚀 Starting Arbitrage Strategy Test")
    print("=" * 50)
    
    # Configure backtest engine
    config = BacktestEngineConfig(
        trader_id=TraderId("ARBITRAGE-SIMPLE-001"),
        logging=LoggingConfig(
            log_level="INFO",
            log_colors=True,
            use_pyo3=False,
        ),
    )

    # Build the backtest engine
    engine = BacktestEngine(config=config)

    # Add Binance venue
    from nautilus_trader.adapters.binance import BINANCE_VENUE
    engine.add_venue(
        venue=BINANCE_VENUE,
        oms_type=OmsType.NETTING,
        book_type=BookType.L1_MBP,
        account_type=AccountType.CASH,
        base_currency=None,
        starting_balances=[Money(1_000_000.0, USDT), Money(10.0, ETH)],
        trade_execution=True,
    )

    # Add ETHUSDT instrument
    ETHUSDT_BINANCE = TestInstrumentProvider.ethusdt_binance()
    engine.add_instrument(ETHUSDT_BINANCE)

    # Create two different bar types for arbitrage testing
    # Using different price types to simulate different data sources
    bar_spec_last = BarSpecification(1, BarAggregation.MINUTE, PriceType.LAST)
    bar_spec_mid = BarSpecification(1, BarAggregation.MINUTE, PriceType.MID)
    
    bar_type_last = BarType(ETHUSDT_BINANCE.id, bar_spec_last)
    bar_type_mid = BarType(ETHUSDT_BINANCE.id, bar_spec_mid)

    # Add test data (using the same data for both, but different bar types)
    provider = TestDataProvider()
    wrangler = TradeTickDataWrangler(instrument=ETHUSDT_BINANCE)
    ticks = wrangler.process(provider.read_csv_ticks("binance/ethusdt-trades.csv"))
    engine.add_data(ticks)

    # Create arbitrage strategy
    strategy = ArbitrageStrategy(
        bar_type_node1=bar_type_last,
        bar_type_node2=bar_type_mid,
        threshold=1.0,  # $1.00 threshold for arbitrage detection
    )
    
    # Add strategy to engine
    engine.add_strategy(strategy=strategy)

    print("✅ Setup complete. Starting backtest...")
    print("📊 Strategy will monitor price differences between LAST and MID prices")
    print("💰 Arbitrage opportunities will be logged when difference > $1.00")
    print("-" * 50)

    # Run the engine
    engine.run()

    print("=" * 50)
    print("📈 Backtest Complete!")
    print("=" * 50)

    # Clean up
    engine.reset()
    engine.dispose()


if __name__ == "__main__":
    main() 