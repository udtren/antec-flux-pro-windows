#!/usr/bin/env python3
"""
Test script for LibreHardwareMonitor DLL integration.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cpu import CPUMonitor


def test_libre_hardware_monitor():
    """Test LibreHardwareMonitor DLL functionality."""
    print("Testing LibreHardwareMonitor DLL integration...")
    print("=" * 50)

    # Create CPU monitor instance
    monitor = CPUMonitor()

    # Print initialization info
    print(monitor.get_info())
    print()

    # Try to get temperature
    try:
        temp = monitor.get_temperature()
        if temp is not None:
            print(f"✅ CPU Temperature: {temp:.1f}°C")
            print(f"Methods tried: {', '.join(monitor.methods_tried)}")
        else:
            print("❌ Failed to get CPU temperature")
            print(f"Methods tried: {', '.join(monitor.methods_tried)}")
    except Exception as e:
        print(f"❌ Error getting temperature: {e}")

    # Test multiple readings
    print("\nTesting multiple readings:")
    for i in range(3):
        temp = monitor.get_temperature()
        if temp is not None:
            print(f"Reading {i+1}: {temp:.1f}°C")
        else:
            print(f"Reading {i+1}: Failed")

    # Clean up
    monitor.close()
    print("\n✅ Test completed")


if __name__ == "__main__":
    test_libre_hardware_monitor()
