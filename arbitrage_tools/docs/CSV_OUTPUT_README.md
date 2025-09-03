# CSV Output Feature

The signal monitors now include comprehensive CSV output functionality to save all market data and arbitrage opportunities for analysis.

## Features

### 📊 Price Data CSV
- **File**: `csv_output/price_data_YYYYMMDD_HHMMSS.csv`
- **Content**: Real-time price updates from all monitored exchanges
- **Columns**:
  - `timestamp`: Time of the price update
  - `binance_price`: Price from Binance
  - `bybit_price`: Price from Bybit
  - `okx_price`: Price from OKX (demo only)
  - `min_price`: Lowest price across exchanges
  - `max_price`: Highest price across exchanges
  - `price_diff`: Absolute price difference
  - `price_diff_percent`: Percentage price difference

### 🎯 Arbitrage Opportunities CSV
- **File**: `csv_output/arbitrage_opportunities_YYYYMMDD_HHMMSS.csv`
- **Content**: All detected arbitrage opportunities with profit calculations
- **Columns**:
  - `timestamp`: Time opportunity was detected
  - `symbol`: Trading symbol (e.g., ETHUSDT)
  - `buy_exchange`: Exchange to buy from
  - `buy_price`: Buy price
  - `sell_exchange`: Exchange to sell on
  - `sell_price`: Sell price
  - `price_diff`: Absolute price difference
  - `price_diff_percent`: Percentage price difference
  - `quantity`: Simulated trade quantity
  - `gross_profit`: Profit before fees
  - `total_fees`: Estimated trading fees
  - `net_profit`: Profit after fees
  - `profitable`: Whether the trade is profitable

## Usage

### Demo Monitor (Simulated Data)
```python
from demo_signal_monitor import DemoSignalMonitor

# Enable CSV output
monitor = DemoSignalMonitor(
    symbol="ETHUSDT",
    threshold=0.50,
    csv_output=True  # Enable CSV output
)

# Run monitoring
monitor.start_monitoring(duration_seconds=60)
```

### Live Monitor (Real Data)
```python
from signal_monitor import SignalMonitor

# Enable CSV output
monitor = SignalMonitor(
    symbol="ETHUSDT",
    threshold=0.50,
    csv_output=True  # Enable CSV output
)

# Run monitoring (requires API keys)
await monitor.start_monitoring(duration_seconds=60)
```

### Disable CSV Output
```python
# Set csv_output=False to disable
monitor = DemoSignalMonitor(
    symbol="ETHUSDT",
    threshold=0.50,
    csv_output=False  # Disable CSV output
)
```

## File Structure

```
csv_output/
├── price_data_20241201_143022.csv          # Demo price data
├── arbitrage_opportunities_20241201_143022.csv  # Demo opportunities
├── live_price_data_20241201_143022.csv     # Live price data
└── live_arbitrage_opportunities_20241201_143022.csv  # Live opportunities
```

## Data Analysis

The CSV files can be used for:

1. **Historical Analysis**: Track price movements over time
2. **Arbitrage Statistics**: Analyze opportunity frequency and profitability
3. **Exchange Performance**: Compare price accuracy across exchanges
4. **Backtesting**: Use historical data to test trading strategies
5. **Reporting**: Generate reports for stakeholders

## Example Analysis Script

```python
import pandas as pd

# Load price data
price_df = pd.read_csv('csv_output/price_data_20241201_143022.csv')

# Load opportunities
opps_df = pd.read_csv('csv_output/arbitrage_opportunities_20241201_143022.csv')

# Basic statistics
print(f"Total price updates: {len(price_df)}")
print(f"Total opportunities: {len(opps_df)}")
print(f"Profitable opportunities: {len(opps_df[opps_df['profitable'] == True])}")

# Average price difference
avg_diff = price_df['price_diff'].mean()
print(f"Average price difference: ${avg_diff:.2f}")

# Total potential profit
total_profit = opps_df['net_profit'].sum()
print(f"Total potential profit: ${total_profit:.2f}")
```

## Quick Test

Run the test script to quickly generate sample CSV files:

```bash
python test_csv_output.py
```

This will run the demo monitor for 10 seconds and create sample CSV files in the `csv_output` directory.

## Notes

- Files are automatically created with timestamps to avoid overwrites
- Data is flushed immediately to prevent data loss
- Files are created in a `csv_output` directory for organization
- Both demo and live monitors support CSV output
- CSV output can be enabled/disabled independently of monitoring 