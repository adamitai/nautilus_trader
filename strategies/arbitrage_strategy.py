import datetime as dt

from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.trading.strategy import Strategy


class ArbitrageStrategy(Strategy):
    """
    A simple arbitrage strategy that subscribes to market data from two different nodes
    and logs arbitrage opportunities when the price difference exceeds a threshold.
    """

    def __init__(self, bar_type_node1: BarType, bar_type_node2: BarType, threshold: float):
        super().__init__()
        self.bar_type_node1 = bar_type_node1
        self.bar_type_node2 = bar_type_node2
        self.threshold = threshold
        self.price_node1 = None
        self.price_node2 = None
        self.start_time = None
        self.end_time = None

    def on_start(self):
        self.start_time = dt.datetime.now()
        self.log.info(f"Arbitrage strategy started at: {self.start_time}")
        self.subscribe_bars(self.bar_type_node1)
        self.subscribe_bars(self.bar_type_node2)
        self.log.info(f"Subscribed to {self.bar_type_node1} and {self.bar_type_node2}")

    def on_bar(self, bar: Bar):
        if bar.bar_type == self.bar_type_node1:
            self.price_node1 = bar.close
        elif bar.bar_type == self.bar_type_node2:
            self.price_node2 = bar.close

        if self.price_node1 is not None and self.price_node2 is not None:
            price_diff = abs(self.price_node1 - self.price_node2)
            if price_diff > self.threshold:
                self.log.info(f"Arbitrage opportunity detected! Price difference: {price_diff}")

    def on_stop(self):
        self.end_time = dt.datetime.now()
        self.log.info(f"Arbitrage strategy finished at: {self.end_time} | Duration: {(self.end_time - self.start_time).total_seconds():.2f} seconds.") 