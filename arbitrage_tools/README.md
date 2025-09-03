# Arbitrage Tools

A comprehensive suite of tools for detecting and analyzing arbitrage opportunities across cryptocurrency exchanges using NautilusTrader.

## 📁 Directory Structure

```
arbitrage_tools/
├── monitors/           # Signal monitoring applications
├── scripts/           # Utility and test scripts
├── examples/          # Example configurations and templates
├── docs/             # Documentation files
├── csv_output/       # Generated CSV data files
└── README.md         # This file
```

## 🚀 Quick Start

### 1. Demo Monitor (No API Keys Required)
```bash
cd arbitrage_tools/monitors
python demo_signal_monitor.py
```

### 2. Test CSV Output
```bash
cd arbitrage_tools/scripts
python test_csv_output.py
```

### 3. Analyze Results
```bash
cd arbitrage_tools/scripts
python analyze_csv_data.py
```

## 📊 Available Tools

### Monitors
- **`demo_signal_monitor.py`** - Simulated arbitrage detection (no API keys needed)
- **`signal_monitor.py`** - Live arbitrage detection with real exchange data
- **`working_signal_monitor.py`** - Alternative live monitor implementation
- **`simple_signal_monitor.py`** - Basic signal monitor for testing

### Scripts
- **`test_csv_output.py`** - Quick test of CSV output functionality
- **`analyze_csv_data.py`** - Analyze CSV data and generate insights
- **`test_env.py`** - Test environment variable loading
- **`test_arbitrage_*.py`** - Various arbitrage testing scripts

### Examples
- **`live_arbitrage_example.py`** - Complete live arbitrage example
- **`api_keys_example.txt`** - Template for API key configuration

### Documentation
- **`ARBITRAGE_SIGNAL_MONITOR_README.md`** - Complete guide to signal monitoring
- **`CSV_OUTPUT_README.md`** - CSV output feature documentation

## 🔧 Setup

### 1. Environment Variables
Create a `.env` file in the project root:
```bash
# Copy the example
cp arbitrage_tools/examples/api_keys_example.txt .env

# Edit with your actual API keys
nano .env
```

### 2. Install Dependencies
```bash
# Install python-dotenv for environment variables
pip install python-dotenv
```

### 3. Test Environment
```bash
cd arbitrage_tools/scripts
python test_env.py
```

## 📈 Usage Examples

### Demo Mode (Recommended for Testing)
```bash
cd arbitrage_tools/monitors
python demo_signal_monitor.py
```

### Live Mode (Requires API Keys)
```bash
cd arbitrage_tools/monitors
python signal_monitor.py
```

### Generate and Analyze Data
```bash
# Generate sample data
cd arbitrage_tools/scripts
python test_csv_output.py

# Analyze the results
python analyze_csv_data.py
```

## 🎯 Features

- **Real-time Monitoring** - Live price feeds from multiple exchanges
- **Arbitrage Detection** - Automatic detection of price differences
- **CSV Export** - Comprehensive data logging for analysis
- **Profit Calculation** - Simulated trade profit/loss analysis
- **Multi-Exchange Support** - Binance, Bybit, and OKX integration
- **Configurable Thresholds** - Adjustable minimum price differences

## 📊 Data Output

All monitors generate CSV files in the `csv_output/` directory:

- **Price Data** - Real-time price updates from all exchanges
- **Arbitrage Opportunities** - Detected opportunities with profit calculations
- **Analysis Reports** - Statistical summaries and recommendations

## 🔒 Security

- API keys are loaded from environment variables
- No hardcoded credentials in source code
- `.env` file is automatically gitignored
- Demo mode available for testing without API keys

## 📚 Documentation

- **Signal Monitoring Guide** - `docs/ARBITRAGE_SIGNAL_MONITOR_README.md`
- **CSV Output Guide** - `docs/CSV_OUTPUT_README.md`
- **API Configuration** - `examples/api_keys_example.txt`

## 🛠️ Development

### Adding New Exchanges
1. Add exchange configuration to monitors
2. Update CSV output headers
3. Test with demo data first

### Customizing Thresholds
```python
monitor = DemoSignalMonitor(
    symbol="ETHUSDT",
    threshold=0.50,  # Adjust minimum price difference
    csv_output=True
)
```

### Extending Analysis
Modify `scripts/analyze_csv_data.py` to add custom analysis features.

## 🐛 Troubleshooting

### Common Issues
1. **Import Errors** - Ensure you're in the correct directory
2. **API Key Errors** - Check `.env` file configuration
3. **CSV Permission Errors** - Ensure write permissions in `csv_output/`

### Getting Help
1. Check the documentation in `docs/`
2. Run test scripts to verify setup
3. Use demo mode for initial testing

## 📄 License

This project is part of the NautilusTrader ecosystem. See the main project LICENSE file for details. 