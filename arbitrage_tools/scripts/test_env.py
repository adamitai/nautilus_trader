#!/usr/bin/env python3
"""
Test script to verify .env file is working correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_env_variables():
    print("🔐 Testing Environment Variables")
    print("=" * 40)
    
    # Test Binance keys
    binance_key = os.getenv("BINANCE_API_KEY")
    binance_secret = os.getenv("BINANCE_API_SECRET")
    
    print(f"Binance API Key: {'✅ Loaded' if binance_key else '❌ Not found'}")
    print(f"Binance API Secret: {'✅ Loaded' if binance_secret else '❌ Not found'}")
    
    # Test Bybit keys
    bybit_key = os.getenv("BYBIT_API_KEY")
    bybit_secret = os.getenv("BYBIT_API_SECRET")
    
    print(f"Bybit API Key: {'✅ Loaded' if bybit_key else '❌ Not found'}")
    print(f"Bybit API Secret: {'✅ Loaded' if bybit_secret else '❌ Not found'}")
    
    # Test OKX keys
    okx_key = os.getenv("OKX_API_KEY")
    okx_secret = os.getenv("OKX_API_SECRET")
    okx_passphrase = os.getenv("OKX_PASSPHRASE")
    
    print(f"OKX API Key: {'✅ Loaded' if okx_key else '❌ Not found'}")
    print(f"OKX API Secret: {'✅ Loaded' if okx_secret else '❌ Not found'}")
    print(f"OKX Passphrase: {'✅ Loaded' if okx_passphrase else '❌ Not found'}")
    
    print("=" * 40)
    
    if all([binance_key, binance_secret, bybit_key, bybit_secret]):
        print("🎉 All API keys loaded successfully!")
        print("🚀 You're ready to run live trading strategies!")
    else:
        print("⚠️  Some API keys are missing. Check your .env file.")
    
    # Show first few characters of keys (for verification)
    print("\n📋 Key Preview (first 10 chars):")
    print(f"Binance Key: {binance_key[:10]}..." if binance_key else "Not found")
    print(f"Bybit Key: {bybit_key[:10]}..." if bybit_key else "Not found")
    print(f"OKX Key: {okx_key[:10]}..." if okx_key else "Not found")

if __name__ == "__main__":
    test_env_variables() 