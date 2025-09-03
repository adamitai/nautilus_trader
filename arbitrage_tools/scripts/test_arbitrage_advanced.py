#!/usr/bin/env python3
# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2025 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

import time
from decimal import Decimal

import pandas as pd

from nautilus_trader.adapters.binance import BINANCE_VENUE
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

# Import our custom arbitrage strategy
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strategies.arbitrage_strategy import ArbitrageStrategy


if __name__ == "__main__":
    print("🚀 Starting Advanced Arbitrage Strategy Test")
    print("=" * 60)
    
    # Configure backtest engine
    config = BacktestEngineConfig(
        trader_id=TraderId("ARBITRAGE-TESTER-001"),
        logging=LoggingConfig(
            log_level="INFO",
            log_colors=True,
            use_pyo3=False,
        ),
    )

    # Build the backtest engine
    engine = BacktestEngine(config=config)

    # Add a trading venue
    engine.add_venue(
        venue=BINANCE_VENUE,
        oms_type=OmsType.NETTING,
        book_type=BookType.L1_MBP,
        account_type=AccountType.CASH,
        base_currency=None,
        starting_balances=[Money(1_000_000.0, USDT), Money(10.0, ETH)],
        trade_execution=True,
    )

    # Add instruments
    ETHUSDT_BINANCE = TestInstrumentProvider.ethusdt_binance()
    engine.add_instrument(ETHUSDT_BINANCE)

    # Add data from test provider
    provider = TestDataProvider()
    
    # Create two different bar types for arbitrage testing
    # One using bid prices, one using ask prices
    bar_spec_bid = BarSpecification(1, BarAggregation.MINUTE, PriceType.BID)
    bar_spec_ask = BarSpecification(1, BarAggregation.MINUTE, PriceType.ASK)
    
    bar_type_bid = BarType(ETHUSDT_BINANCE.id, bar_spec_bid)
    bar_type_ask = BarType(ETHUSDT_BINANCE.id, bar_spec_ask)

    # Add trade tick data (this will be aggregated into bars)
    wrangler = TradeTickDataWrangler(instrument=ETHUSDT_BINANCE)
    ticks = wrangler.process(provider.read_csv_ticks("binance/ethusdt-trades.csv"))
    engine.add_data(ticks)

    # Create arbitrage strategy with a small threshold
    strategy = ArbitrageStrategy(
        bar_type_node1=bar_type_bid,
        bar_type_node2=bar_type_ask,
        threshold=0.50,  # $0.50 threshold for arbitrage detection
    )
    
    # Add strategy to engine
    engine.add_strategy(strategy=strategy)

    print("✅ Setup complete. Starting advanced arbitrage backtest...")
    print("📊 Strategy will monitor price differences between BID and ASK prices")
    print("💰 Arbitrage opportunities will be logged when difference > $0.50")
    print("-" * 60)

    # Run the engine
    engine.run()

    print("=" * 60)
    print("📈 Advanced Backtest Complete!")
    print("=" * 60)

    # View reports
    with pd.option_context(
        "display.max_rows",
        100,
        "display.max_columns",
        None,
        "display.width",
        300,
    ):
        print(engine.trader.generate_account_report(BINANCE_VENUE))
        print(engine.trader.generate_order_fills_report())
        print(engine.trader.generate_positions_report())

    # Reset and dispose
    engine.reset()
    engine.dispose() 