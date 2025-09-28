"""
Windows Service implementation for Antec Flux Pro Display.
Uses pywin32 for Windows service functionality.
"""

import os
import sys
import time
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import Config
from src.cpu import CPUMonitor
from src.gpu import GPUMonitor
from src.usb import USBDevice


class AfProDisplayService(win32serviceutil.ServiceFramework):
    """Windows service for Antec Flux Pro Display temperature monitoring."""

    _svc_name_ = "AfProDisplay"
    _svc_display_name_ = "Antec Flux Pro Display Monitor"
    _svc_description_ = "Monitors CPU and GPU temperatures and displays them on Antec Flux Pro case display"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

        # Service configuration
        self.config_path = (
            Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData"))
            / "af-pro-display"
            / "config.toml"
        )

        # Initialize components
        self.config = None
        self.cpu_monitor = None
        self.gpu_monitor = None
        self.usb_device = None

    def SvcStop(self):
        """Handle service stop request."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False

    def SvcDoRun(self):
        """Main service loop."""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )

        try:
            self._initialize()
            self._main_loop()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {e}")
        finally:
            self._cleanup()

    def _initialize(self):
        """Initialize service components."""
        # Load configuration
        self._load_config()

        # Initialize monitors
        self.cpu_monitor = CPUMonitor(self.config.cpu_device)
        self.gpu_monitor = GPUMonitor(self.config.gpu_device)

        # Connect to USB device
        try:
            self.usb_device = USBDevice()
            servicemanager.LogInfoMsg("Connected to Antec Flux Pro display")
        except Exception as e:
            servicemanager.LogErrorMsg(f"Failed to connect to USB device: {e}")
            raise

    def _load_config(self):
        """Load service configuration."""
        # Create config directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create default config if it doesn't exist
        if not self.config_path.exists():
            default_config = Config()
            import toml

            with open(self.config_path, "w") as f:
                toml.dump(default_config.to_dict(), f)

        # Load config
        import toml

        with open(self.config_path, "r") as f:
            config_data = toml.load(f)

        self.config = Config.from_dict(config_data)

    def _main_loop(self):
        """Main service monitoring loop."""
        while self.running:
            # Check if we should stop
            if (
                win32event.WaitForSingleObject(self.hWaitStop, 0)
                == win32event.WAIT_OBJECT_0
            ):
                break

            try:
                # Get temperatures
                cpu_temp = self.cpu_monitor.get_temperature()
                gpu_temp = self.gpu_monitor.get_temperature()

                # Send to display
                if self.usb_device:
                    self.usb_device.send_temperatures(cpu_temp, gpu_temp)

                # Wait for next poll (check stop event during wait)
                if (
                    win32event.WaitForSingleObject(
                        self.hWaitStop, self.config.polling_interval
                    )
                    == win32event.WAIT_OBJECT_0
                ):
                    break

            except Exception as e:
                servicemanager.LogErrorMsg(f"Monitoring error: {e}")
                time.sleep(5)  # Wait before retrying

    def _cleanup(self):
        """Cleanup resources."""
        if self.usb_device:
            try:
                # Clear display
                self.usb_device.send_temperatures(0.0, 0.0)
                self.usb_device.close()
            except:
                pass

        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, ""),
        )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AfProDisplayService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AfProDisplayService)
