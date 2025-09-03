# JSON Logging and Interface Data Guide

## 🎯 **Complete JSON Logging System**

The arbitrage tools now include comprehensive JSON logging that captures every aspect of the monitoring session for interface presentation and analysis.

## 📊 **JSON Log Structure**

### **Execution Log** (`execution_log_YYYYMMDD_HHMMSS.json`)

```json
{
  "session_info": {
    "symbol": "ETHUSDT",
    "threshold": 0.5,
    "start_time": "2025-06-22T22:27:43.595325",
    "end_time": "2025-06-22T22:30:22.996573",
    "duration_seconds": 159.4,
    "total_price_updates": 30,
    "total_opportunities": 30,
    "profitable_opportunities": 23,
    "total_simulated_profit": 181.26
  },
  "price_updates": [...],
  "opportunities": [...],
  "system_events": [...]
}
```

### **Interface Data** (`interface_data_YYYYMMDD_HHMMSS.json`)

```json
{
  "dashboard": {
    "symbol": "ETHUSDT",
    "threshold": 0.5,
    "duration_minutes": 2.66,
    "total_opportunities": 30,
    "profitable_opportunities": 23,
    "success_rate": 76.7,
    "total_profit": 181.26,
    "average_profit": 7.88
  },
  "recent_opportunities": [...],
  "price_history": [...],
  "performance_metrics": {...},
  "exchange_performance": {...}
}
```

## 🚀 **Usage**

### **1. Enable JSON Logging**

```python
from arbitrage_tools.monitors.demo_signal_monitor import DemoSignalMonitor

monitor = DemoSignalMonitor(
    symbol="ETHUSDT",
    threshold=0.50,
    csv_output=True,
    json_logging=True  # Enable JSON logging
)
```

### **2. Run Monitoring**

```bash
# Demo mode (simulated data)
cd arbitrage_tools/monitors
python demo_signal_monitor.py

# Live mode (real data, no real trades)
cd arbitrage_tools/scripts
python run_live_monitor.py
```

### **3. Analyze Results**

```bash
cd arbitrage_tools/scripts
python analyze_json_log.py
```

## 📈 **Data Captured**

### **Session Information**
- Symbol and threshold settings
- Start/end times and duration
- Total price updates and opportunities
- Profitability statistics

### **Price Updates**
- Real-time prices from all exchanges
- Price differences and percentages
- Exchange identifiers

### **Arbitrage Opportunities**
- Complete opportunity details
- Buy/sell exchange and prices
- Profit calculations with fees
- Timestamps and session duration

### **System Events**
- Session start/stop events
- Error conditions
- User interruptions

## 🖥️ **Interface Data Generation**

The system automatically generates interface-ready data including:

### **Dashboard Metrics**
- Real-time performance indicators
- Success rates and profitability
- Duration and opportunity counts

### **Performance Metrics**
- Hourly and daily profit projections
- Profit per opportunity ratios
- Scalability indicators

### **Exchange Performance**
- Opportunity distribution across exchanges
- Exchange-specific statistics
- Comparative analysis

### **Recent Data**
- Last 10 opportunities
- Last 20 price updates
- Real-time trend analysis

## 📊 **Example Analysis Output**

```
📄 JSON Log Analysis
==================================================
File: execution_log_20250622_222743.json

📊 SESSION INFORMATION
------------------------------
Symbol: ETHUSDT
Threshold: $0.5
Duration: 159.4 seconds
Total Opportunities: 30
Profitable Opportunities: 23
Success Rate: 76.7%
Total Profit: $181.26

🏆 TOP 5 PROFITABLE OPPORTUNITIES
----------------------------------------
1. OKX → BINANCE: $2969.91 → $3021.38 (Profit: $45.48)
2. BINANCE → BYBIT: $2990.48 → $3009.12 (Profit: $12.64)
3. BYBIT → OKX: $2992.15 → $3009.83 (Profit: $11.68)
```

## 🔧 **Integration with Interfaces**

### **Web Dashboard**
```javascript
// Load interface data
fetch('/api/interface-data')
  .then(response => response.json())
  .then(data => {
    // Update dashboard metrics
    updateDashboard(data.dashboard);
    
    // Display recent opportunities
    displayOpportunities(data.recent_opportunities);
    
    // Show performance charts
    updateCharts(data.performance_metrics);
  });
```

### **Real-time Updates**
```javascript
// WebSocket connection for real-time data
const ws = new WebSocket('ws://localhost:8080/arbitrage-feed');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateRealTimeMetrics(data);
};
```

### **Mobile App**
```python
# API endpoint for mobile apps
@app.route('/api/arbitrage-data')
def get_arbitrage_data():
    return jsonify(load_latest_interface_data())
```

## 📁 **File Organization**

```
arbitrage_tools/csv_output/
├── execution_log_20250622_222743.json      # Complete execution log
├── interface_data_20250622_223116.json     # Interface-ready data
├── price_data_20250622_222743.csv          # CSV price data
└── arbitrage_opportunities_20250622_222743.csv  # CSV opportunities
```

## 🎯 **Benefits**

### **Complete Audit Trail**
- Every event captured with timestamps
- Full session history preserved
- Debugging and analysis capabilities

### **Interface Ready**
- Pre-formatted data for dashboards
- Real-time metrics and statistics
- Performance indicators

### **Scalable Architecture**
- JSON format for easy parsing
- Structured data for APIs
- Compatible with any frontend

### **Analysis Capabilities**
- Historical trend analysis
- Performance optimization
- Strategy backtesting

## 🔒 **Security Considerations**

- No sensitive data in logs (API keys excluded)
- Timestamped files for audit trails
- Structured format for easy filtering
- Export capabilities for compliance

## 📈 **Performance Metrics**

The system calculates:
- **Success Rate**: Percentage of profitable opportunities
- **Hourly Profit**: Projected hourly earnings
- **Daily Profit**: Projected daily earnings
- **Average Profit**: Per-opportunity profitability
- **Exchange Performance**: Distribution across exchanges

## 🚀 **Next Steps**

1. **Run Demo**: Test with simulated data
2. **Configure API Keys**: Set up for live data
3. **Run Live Monitor**: Connect to real exchanges
4. **Analyze Results**: Generate interface data
5. **Integrate**: Use data in your interface

## 📞 **Support**

For questions or issues:
1. Check the main README in `arbitrage_tools/`
2. Review the CSV output guide
3. Test with demo mode first
4. Verify API key configuration

---

**Ready to start?** Run `python arbitrage_tools/monitors/demo_signal_monitor.py` to generate your first JSON logs! 