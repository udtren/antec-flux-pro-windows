#!/usr/bin/env python3
"""
Download LibreHardwareMonitorLib.dll from official releases.
"""

import os
import sys
import urllib.request
import zipfile
import tempfile
import shutil


def download_libre_hardware_monitor_dll():
    """Download LibreHardwareMonitorLib.dll from GitHub releases."""

    # LibreHardwareMonitor GitHub releases URL
    # This is the official release URL - adjust version as needed
    release_url = "https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases/latest/download/LibreHardwareMonitor-net472.zip"

    project_root = os.path.dirname(os.path.abspath(__file__))
    dll_path = os.path.join(project_root, "LibreHardwareMonitorLib.dll")

    # Check if DLL already exists
    if os.path.exists(dll_path):
        print(f"✅ LibreHardwareMonitorLib.dll already exists at: {dll_path}")
        return True

    print("Downloading LibreHardwareMonitor from GitHub releases...")
    print(f"URL: {release_url}")

    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "LibreHardwareMonitor.zip")

            # Download the ZIP file
            print("📥 Downloading...")
            urllib.request.urlretrieve(release_url, zip_path)

            # Extract the ZIP file
            print("📦 Extracting...")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find the DLL file
            dll_found = False
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file == "LibreHardwareMonitorLib.dll":
                        source_dll = os.path.join(root, file)
                        shutil.copy2(source_dll, dll_path)
                        dll_found = True
                        break
                if dll_found:
                    break

            if dll_found:
                print(
                    f"✅ LibreHardwareMonitorLib.dll downloaded successfully to: {dll_path}"
                )
                return True
            else:
                print(
                    "❌ LibreHardwareMonitorLib.dll not found in the downloaded package"
                )
                return False

    except Exception as e:
        print(f"❌ Failed to download LibreHardwareMonitorLib.dll: {e}")
        print("\nManual download instructions:")
        print(
            "1. Go to: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases/latest"
        )
        print("2. Download LibreHardwareMonitor-net472.zip")
        print("3. Extract and copy LibreHardwareMonitorLib.dll to the project root")
        return False


def main():
    """Main function."""
    print("LibreHardwareMonitor DLL Downloader")
    print("=" * 40)

    success = download_libre_hardware_monitor_dll()

    if success:
        print("\n✅ Setup completed successfully!")
        print("Next steps:")
        print("1. Run: python setup_libre_hardware_monitor.py")
        print("2. Run: python test_libre_hardware_monitor.py")
    else:
        print("\n❌ Download failed. Please download manually.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
