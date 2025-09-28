#!/usr/bin/env python3
"""
Setup script to install LibreHardwareMonitor DLL dependencies.
"""

import subprocess
import sys
import os


def install_pythonnet():
    """Install pythonnet package for .NET interop."""
    print("Installing pythonnet for LibreHardwareMonitor DLL support...")

    try:
        # Install pythonnet
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pythonnet==3.0.3"]
        )
        print("✅ pythonnet installed successfully")

        # Test if it works
        try:
            import clr

            print("✅ .NET interop is working")
            return True
        except ImportError as e:
            print(f"❌ .NET interop test failed: {e}")
            print("You may need to install .NET Runtime")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install pythonnet: {e}")
        return False


def check_dll():
    """Check if LibreHardwareMonitorLib.dll exists."""
    dll_path = os.path.join(os.path.dirname(__file__), "LibreHardwareMonitorLib.dll")
    if os.path.exists(dll_path):
        print(f"✅ LibreHardwareMonitorLib.dll found at: {dll_path}")
        return True
    else:
        print(f"❌ LibreHardwareMonitorLib.dll not found at: {dll_path}")
        print("Attempting to download automatically...")
        
        # Try to download using the download script
        try:
            import download_dll
            if download_dll.download_libre_hardware_monitor_dll():
                print("✅ DLL downloaded successfully")
                return True
        except Exception as e:
            print(f"Auto-download failed: {e}")
        
        print("Manual download required:")
        print("1. Run: python download_dll.py")
        print("2. Or download from: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases/latest")
        print("3. Extract LibreHardwareMonitorLib.dll to project root directory")
        return False


def main():
    """Main setup function."""
    print("LibreHardwareMonitor DLL Setup")
    print("=" * 40)

    # Check if DLL exists
    dll_ok = check_dll()

    # Install pythonnet
    pythonnet_ok = install_pythonnet()

    if dll_ok and pythonnet_ok:
        print("\n✅ Setup completed successfully!")
        print(
            "You can now use LibreHardwareMonitor DLL for CPU temperature monitoring."
        )
    else:
        print("\n❌ Setup incomplete. Please resolve the issues above.")

    print("\nNext steps:")
    print("1. Run: python test_libre_hardware_monitor.py")
    print("2. If successful, the main application will use DLL-based monitoring")


if __name__ == "__main__":
    main()
