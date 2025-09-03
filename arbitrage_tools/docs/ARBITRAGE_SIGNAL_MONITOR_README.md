# Arbitrage Signal Monitor

A comprehensive arbitrage detection system for NautilusTrader that monitors multiple exchanges and identifies profitable trading opportunities.

## 🚀 Features

### ✅ **Currently Supported Exchanges**
- **Binance** - Full support (Spot trading)
- **Bybit** - Full support (Spot trading)
- **OKX** - Demo simulation only (adapter not yet ready for live trading)

### 📊 **Key Capabilities**
- **Real-time Price Monitoring** - Live market data from multiple exchanges
- **Arbitrage Detection** - Identifies price differences above configurable thresholds
- **Profit/Loss Analysis** - Calculates potential profits including trading fees
- **Signal Simulation** - Simulates trades without executing them
- **Detailed Reporting** - Comprehensive logs and summary statistics

## 📁 Files Overview

### **Core Files**
- `working_signal_monitor.py` - Live trading signal monitor (requires API keys)
- `demo_signal_monitor.py` - Demo version with simulated data (no API keys needed)
- `strategies/arbitrage_strategy.py` - NautilusTrader strategy implementation
- `test_arbitrage_simple.py` - Simple backtest example
- `test_arbitrage_advanced.py` - Advanced backtest example

### **Configuration**
- `.env` - Environment variables for API keys (create from api_keys_example.txt)
- `api_keys_example.txt` - Template for API key configuration

## 🛠️ Setup Instructions

### **1. Environment Setup**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (already done)
uv sync --all-extras
```

### **2. API Key Configuration**
```bash
# Copy the example file
cp api_keys_example.txt .env

# Edit .env with your actual API keys
nano .env
```

**Required API Keys:**
```env
# Binance
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here

# Bybit
BYBIT_API_KEY=your_bybit_api_key_here
BYBIT_API_SECRET=your_bybit_api_secret_here

# OKX (for future use)
OKX_API_KEY=your_okx_api_key_here
OKX_API_SECRET=your_okx_api_secret_here
OKX_PASSPHRASE=your_okx_passphrase_here
```

## 🎯 Usage Examples

### **Demo Mode (No API Keys Required)**
```bash
python demo_signal_monitor.py
```

**Output:**
```
🚀 Starting Demo Signal Monitor
==================================================
Symbol: ETHUSDT
Threshold: $0.5
Monitoring: Binance, Bybit, OKX (Simulated)
Mode: Signal Detection Only
Duration: 30 seconds
==================================================
[22:11:18] BINANCE: $2999.57 | BYBIT: $3008.46 | OKX: $2997.57

============================================================
🚨 ARBITRAGE OPPORTUNITY DETECTED! [22:11:18]
============================================================
Symbol: ETHUSDT
Buy:  OKX @ $2997.57
Sell: BYBIT @ $3008.46
Price Difference: $10.89 (0.36%)

💰 SIMULATED TRADE (1 ETHUSDT):
   Gross Profit: $10.89
   Total Fees:   $6.01
   Net Profit:   $4.88
   ✅ PROFITABLE OPPORTUNITY!
============================================================
```

### **Live Mode (Requires API Keys)**
```bash
python working_signal_monitor.py
```

## ⚙️ Configuration Options

### **Symbol and Threshold**
```python
monitor = WorkingSignalMonitor(
    symbol="ETHUSDT",      # Trading pair to monitor
    threshold=0.50         # Minimum price difference in USD
)
```

### **Supported Symbols**
- `ETHUSDT` - Ethereum/USDT
- `BTCUSDT` - Bitcoin/USDT
- `ADAUSDT` - Cardano/USDT
- Any other trading pair available on the exchanges

### **Threshold Settings**
- **$0.50** - Conservative (fewer signals, higher quality)
- **$0.25** - Moderate (balanced signals)
- **$0.10** - Aggressive (more signals, may include noise)

## 📈 Understanding the Output

### **Price Updates**
```
[22:11:18] BINANCE: $2999.57 | BYBIT: $3008.46 | OKX: $2997.57
```
- Real-time prices from each exchange
- Updates every second

### **Arbitrage Alerts**
```
🚨 ARBITRAGE OPPORTUNITY DETECTED!
Buy:  OKX @ $2997.57
Sell: BYBIT @ $3008.46
Price Difference: $10.89 (0.36%)
```
- Shows the buy and sell exchanges
- Displays price difference in USD and percentage

### **Profit Analysis**
```
💰 SIMULATED TRADE (1 ETHUSDT):
   Gross Profit: $10.89
   Total Fees:   $6.01
   Net Profit:   $4.88
   ✅ PROFITABLE OPPORTUNITY!
```
- **Gross Profit**: Price difference × quantity
- **Total Fees**: Trading fees (0.1% per trade)
- **Net Profit**: Gross profit minus fees
- **Status**: Profitable or not profitable

## 🔧 Customization

### **Adding New Exchanges**
When OKX adapter is ready, add to `working_signal_monitor.py`:
```python
from nautilus_trader.adapters.okx.common.constants import OKX
from nautilus_trader.adapters.okx.config import OKXDataClientConfig
from nautilus_trader.adapters.okx.factories import OKXLiveDataClientFactory

# Add to data_clients config
OKX: OKXDataClientConfig(
    api_key=os.getenv("OKX_API_KEY"),
    api_secret=os.getenv("OKX_API_SECRET"),
    passphrase=os.getenv("OKX_PASSPHRASE"),
    instrument_types=(OKXInstrumentType.SPOT,),
    contract_types=(OKXContractType.NONE,),
    is_demo=False,
    instrument_provider=InstrumentProviderConfig(load_all=True),
),

# Add factory
self.node.add_data_client_factory(OKX, OKXLiveDataClientFactory)
```

### **Modifying Fee Structure**
```python
def _simulate_trade_profit(self, buy_price: float, sell_price: float) -> dict:
    # Change fee rate (currently 0.1%)
    fee_rate = 0.001  # 0.1%
    
    buy_fee = buy_price * quantity * fee_rate
    sell_fee = sell_price * quantity * fee_rate
```

### **Adding Risk Management**
```python
def _check_arbitrage_opportunities(self):
    # Add minimum profit threshold
    min_profit_threshold = 5.0  # $5 minimum profit
    
    if price_diff > self.threshold and net_profit > min_profit_threshold:
        # Only log if profitable enough
```

## 🚨 Important Notes

### **Security**
- Never commit API keys to version control
- Use `.env` file for sensitive data
- `.env` is already added to `.gitignore`

### **Risk Disclaimer**
- This is for educational and research purposes
- Always test thoroughly before live trading
- Past performance doesn't guarantee future results
- Trading involves risk of loss

### **OKX Status**
- OKX adapter exists but has import issues
- Demo version includes OKX simulation
- Will be added to live version when resolved

## 📊 Performance Metrics

### **Demo Results (30 seconds)**
- **Total Opportunities**: 30
- **Profitable Opportunities**: 26 (86.7%)
- **Total Simulated Profit**: $243.87
- **Average Profit per Trade**: $9.38

### **Real-World Considerations**
- Market conditions vary significantly
- Slippage and execution delays affect profitability
- Network latency impacts arbitrage success
- Exchange downtime can cause missed opportunities

## 🔮 Future Enhancements

### **Planned Features**
1. **OKX Integration** - When adapter is ready
2. **Execution Engine** - Convert signals to actual trades
3. **Risk Management** - Position sizing and stop-losses
4. **Database Storage** - Persist opportunities and results
5. **Web Dashboard** - Real-time monitoring interface
6. **Alert System** - Email/SMS notifications
7. **Backtesting** - Historical performance analysis

### **Advanced Strategies**
1. **Multi-leg Arbitrage** - Three or more exchanges
2. **Statistical Arbitrage** - Mean reversion strategies
3. **Cross-asset Arbitrage** - Different trading pairs
4. **Futures Arbitrage** - Spot vs futures opportunities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions:
1. Check the NautilusTrader documentation
2. Review the example files
3. Test with the demo version first
4. Ensure API keys are properly configured

---

**Happy Trading! 🚀** 