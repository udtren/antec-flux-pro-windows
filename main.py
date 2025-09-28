"""
Antec Flux Pro Display - Windows Service
Python implementation for monitoring CPU and GPU temperatures
and displaying them on Antec Flux Pro case display via USB.
"""

import argparse
import json
import os
import signal
import sys
import time
import toml
from pathlib import Path
from typing import Optional

from src.config import Config
from src.cpu import CPUMonitor
from src.gpu import GPUMonitor
from src.usb import USBDevice


class TemperatureMonitor:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.running = True
        self.load_config()

        # Initialize hardware monitors
        self.cpu_monitor = CPUMonitor(self.config.cpu_device)
        self.gpu_monitor = GPUMonitor(self.config.gpu_device)
        self.usb_device = None

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def load_config(self):
        """Load configuration from TOML file, create default if not exists."""
        if not self.config_path.exists():
            print(f"Config file not found at: {self.config_path}")
            print("Creating default config file...")

            # Create directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write default config
            default_config = Config()
            with open(self.config_path, "w") as f:
                toml.dump(default_config.to_dict(), f)

        # Load config
        with open(self.config_path, "r") as f:
            config_data = toml.load(f)

        self.config = Config.from_dict(config_data)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nReceived signal {signum}, shutting down...")
        self.running = False

    def connect_usb(self) -> bool:
        """Connect to the USB device."""
        try:
            self.usb_device = USBDevice()
            print("Connected to Antec Flux Pro display")
            return True
        except Exception as e:
            print(f"Failed to connect to USB device: {e}")
            print("This is normal if:")
            print("1. The Antec Flux Pro case is not connected")
            print("2. WinUSB driver is not installed (use Zadig tool)")
            print("3. Running without Administrator privileges")
            print("")
            print("The application will continue in demo mode (no display output)")
            return False

    def run(self):
        """Main monitoring loop."""
        print("Starting Antec Flux Pro Display monitor...")

        # Connect to USB device
        usb_connected = self.connect_usb()

        print(f"CPU monitor: {self.cpu_monitor.get_info()}")
        print(f"GPU monitor: {self.gpu_monitor.get_info()}")
        print(f"Polling interval: {self.config.polling_interval}ms")
        if usb_connected:
            print("Press Ctrl+C to stop...")
        else:
            print("Running in demo mode - Press Ctrl+C to stop...")

        try:
            while self.running:
                # Get temperatures
                cpu_temp = self.cpu_monitor.get_temperature()
                gpu_temp = self.gpu_monitor.get_temperature()

                # Display temperatures
                if cpu_temp is not None:
                    print(f"CPU: {cpu_temp:.1f}°C", end="")
                else:
                    print("CPU: --°C", end="")

                if gpu_temp is not None:
                    print(f" | GPU: {gpu_temp:.1f}°C")
                else:
                    print(" | GPU: --°C")

                # Send to display
                if self.usb_device:
                    self.usb_device.send_temperatures(cpu_temp, gpu_temp)

                # Wait for next poll
                time.sleep(self.config.polling_interval / 1000.0)

        except KeyboardInterrupt:
            pass

        finally:
            # Send zero temperatures before exiting
            if self.usb_device:
                print("Clearing display...")
                self.usb_device.send_temperatures(0.0, 0.0)
                self.usb_device.close()

        print("Shutdown complete.")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Monitor CPU and GPU temperatures on Antec Flux Pro display"
    )
    parser.add_argument(
        "-c",
        "--config",
        default=os.path.expandvars(r"%APPDATA%\af-pro-display\config.toml"),
        help="Path to configuration file",
    )

    args = parser.parse_args()

    monitor = TemperatureMonitor(args.config)
    return monitor.run()


if __name__ == "__main__":
    sys.exit(main())
