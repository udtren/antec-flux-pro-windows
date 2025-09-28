#!/usr/bin/env python3
"""
Test script to check USB device accessibility after driver installation.
"""

import usb.core
import usb.util

VENDOR_ID = 0x2022
PRODUCT_ID = 0x0522

try:
    # Try to find the device
    device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

    if device is None:
        print("❌ Device not found")
        print("Make sure:")
        print("1. Antec Flux Pro case is connected")
        print("2. WinUSB driver is installed via Zadig")
    else:
        print("✅ Device found!")
        print(f"Device: VID:{device.idVendor:04x}, PID:{device.idProduct:04x}")

        # Try to access device
        try:
            device.set_configuration()
            print("✅ Device configuration successful")
            print("🎉 USB communication should work now!")
        except Exception as e:
            print(f"⚠️  Configuration issue: {e}")
            print("Try running as Administrator")

except Exception as e:
    print(f"❌ Error: {e}")
    if "No backend available" in str(e):
        print("Install WinUSB driver using Zadig tool")
    else:
        print("Check USB connection and driver installation")
