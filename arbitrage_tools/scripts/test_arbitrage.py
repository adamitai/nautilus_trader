import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import BarAggregation
from nautilus_trader.model.enums import PriceType
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.trading.config import TradingNodeConfig
from nautilus_trader.trading.node import TradingNode
from strategies.arbitrage_strategy import ArbitrageStrategy


async def main():
    # Create two different bar types for the same symbol but different venues
    symbol = Symbol("BTCUSDT", Venue("BINANCE"))
    bar_type_node1 = BarType(symbol, BarAggregation.MINUTE, PriceType.BID)
    bar_type_node2 = BarType(symbol, BarAggregation.MINUTE, PriceType.ASK)
    
    # Create the arbitrage strategy
    strategy = ArbitrageStrategy(bar_type_node1, bar_type_node2, threshold=0.01)
    
    # Create trading node configuration
    config = TradingNodeConfig(
        trader_id="TRADER-001",
        log_level="INFO",
    )
    
    # Create and start the trading node
    node = TradingNode(config=config)
    
    # Add the strategy to the node
    node.add_strategy(strategy)
    
    # Start the node
    await node.start()
    
    # Keep the node running for a while to test
    await asyncio.sleep(60)  # Run for 60 seconds
    
    # Stop the node
    await node.stop()


if __name__ == "__main__":
    asyncio.run(main()) 