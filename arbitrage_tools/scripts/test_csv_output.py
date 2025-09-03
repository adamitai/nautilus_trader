#!/usr/bin/env python3
"""
Test CSV Output Functionality
Quick test to demonstrate CSV file generation.
"""

import sys
import os

# Add the monitors directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'monitors'))

from demo_signal_monitor import DemoSignalMonitor


def test_csv_output():
    """Test the CSV output functionality."""
    print("🧪 Testing CSV Output Functionality")
    print("="*40)
    
    # Create monitor with CSV output enabled
    monitor = DemoSignalMonitor(
        symbol="ETHUSDT",
        threshold=0.30,  # Lower threshold for more opportunities
        csv_output=True
    )
    
    # Run for just 10 seconds to generate some data
    print("Running for 10 seconds to generate CSV data...")
    monitor.start_monitoring(duration_seconds=10)
    
    print("\n✅ CSV Output Test Complete!")
    print("Check the 'csv_output' directory for generated files.")


if __name__ == "__main__":
    test_csv_output() 