"""
Arbitrage Tools Package

A comprehensive suite of tools for detecting and analyzing arbitrage opportunities
across cryptocurrency exchanges using NautilusTrader.
"""

__version__ = "1.0.0"
__author__ = "NautilusTrader Community"
__description__ = "Arbitrage detection and analysis tools for cryptocurrency trading"

# Import main classes for easy access
try:
    from .monitors.demo_signal_monitor import DemoSignalMonitor
    from .monitors.signal_monitor import SignalMonitor
except ImportError:
    # Handle case where monitors aren't available
    pass

__all__ = [
    "DemoSignalMonitor",
    "SignalMonitor",
] 