#!/bin/bash

# Live Market Monitor Runner
# This script runs the live market monitor with proper environment setup

echo "🚀 Starting Live Market Monitor"
echo "============================================================"

# Navigate to the arbitrage_tools directory
cd "$(dirname "$0")"

# Activate virtual environment
source ../.venv/bin/activate

# Check if API keys are available
if [ -z "$BINANCE_API_KEY" ] || [ -z "$BINANCE_API_SECRET" ] || [ -z "$BYBIT_API_KEY" ] || [ -z "$BYBIT_API_SECRET" ]; then
    echo "❌ Error: API keys not found in environment variables"
    echo "Please set the following environment variables:"
    echo "  - BINANCE_API_KEY"
    echo "  - BINANCE_API_SECRET"
    echo "  - BYBIT_API_KEY"
    echo "  - BYBIT_API_SECRET"
    exit 1
fi

echo "✅ API keys found - proceeding with live monitoring"
echo ""

# Run the live monitor
python scripts/run_live_monitor.py

echo ""
echo "✅ Live monitor completed"
echo "📁 Check the csv_output/ directory for generated JSON files" 