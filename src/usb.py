"""
USB communication with Antec Flux Pro display.
Uses pyusb for cross-platform USB communication.
"""

import usb.core
import usb.util
import usb.backend.libusb1
from typing import Optional


class USBDevice:
    """USB communication with Antec Flux Pro display."""

    VENDOR_ID = 0x2022
    PRODUCT_ID = 0x0522

    def __init__(self):
        self.device = None
        self.endpoint = None
        self._connect()

    def _connect(self):
        """Connect to the USB device."""
        try:
            # Try multiple backends for Windows compatibility
            backend = None

            # First try libusb-package (includes Windows binaries)
            try:
                import libusb_package
                import usb.backend.libusb1

                backend = usb.backend.libusb1.get_backend(
                    find_library=libusb_package.find_library
                )
                print("Using libusb-package backend")
            except Exception as e:
                print(f"libusb-package backend failed: {e}")

            # Fallback to other backends
            if backend is None:
                try:
                    backend = usb.backend.libusb1.get_backend()
                    print("Using system libusb1 backend")
                except Exception:
                    print("No libusb1 backend available, using default")

            # Find the device
            self.device = usb.core.find(
                idVendor=self.VENDOR_ID, idProduct=self.PRODUCT_ID, backend=backend
            )

        except Exception as e:
            if "No backend available" in str(e):
                raise RuntimeError(
                    "USB backend not available. This usually means:\n"
                    "1. WinUSB driver is not installed for the Antec Flux Pro device\n"
                    "2. Device is using a different driver (like HID)\n\n"
                    "Solution: Use Zadig tool to install WinUSB driver:\n"
                    "1. Download Zadig from https://zadig.akeo.ie/\n"
                    "2. Run as Administrator\n"
                    "3. Options → List All Devices\n"
                    "4. Find device with VID 2022, PID 0522\n"
                    "5. Select WinUSB driver and install"
                )
            else:
                raise RuntimeError(f"USB error: {e}")

        if self.device is None:
            raise RuntimeError(
                f"USB device not found (VID:{self.VENDOR_ID:04x}, PID:{self.PRODUCT_ID:04x}).\n"
                "Make sure:\n"
                "1. Antec Flux Pro case is connected via USB\n"
                "2. Device appears in Windows Device Manager\n"
                "3. WinUSB driver is installed (use Zadig tool)"
            )

        # On Windows, we don't need to detach kernel drivers
        # Set the active configuration
        try:
            self.device.set_configuration()
        except usb.core.USBError as e:
            print(f"Warning: Could not set USB configuration: {e}")

        # Find the interrupt OUT endpoint
        cfg = self.device.get_active_configuration()
        intf = cfg[(0, 0)]

        self.endpoint = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress)
            == usb.util.ENDPOINT_OUT
            and usb.util.endpoint_type(e.bmAttributes) == usb.util.ENDPOINT_TYPE_INTR,
        )

        if self.endpoint is None:
            # Fallback to default endpoint
            self.endpoint = 0x03
        else:
            self.endpoint = self.endpoint.bEndpointAddress

    def send_temperatures(self, cpu_temp: Optional[float], gpu_temp: Optional[float]):
        """Send temperature data to the display."""
        if not self.device:
            return

        payload = self._generate_payload(cpu_temp, gpu_temp)

        try:
            # Use interrupt transfer for better compatibility
            bytes_written = self.device.write(
                self.endpoint, payload, 1000
            )  # 1 second timeout

            if bytes_written != len(payload):
                print(f"Warning: Only wrote {bytes_written} of {len(payload)} bytes")

        except usb.core.USBError as e:
            print(f"USB communication error: {e}")
            # Don't raise exception to keep the program running

    def _generate_payload(
        self, cpu_temp: Optional[float], gpu_temp: Optional[float]
    ) -> bytes:
        """Generate the USB payload for temperature data."""
        payload = bytearray([85, 170, 1, 1, 6])  # Header

        # Encode CPU temperature
        cpu_encoded = self._encode_temperature(cpu_temp)
        payload.extend(cpu_encoded)

        # Encode GPU temperature
        gpu_encoded = self._encode_temperature(gpu_temp)
        payload.extend(gpu_encoded)

        # Calculate checksum
        checksum = sum(payload) & 0xFF
        payload.append(checksum)

        return bytes(payload)

    def _encode_temperature(self, temp: Optional[float]) -> bytes:
        """Encode temperature value for the display protocol."""
        if temp is None:
            return bytes([238, 238, 238])  # No data marker

        ones = int(temp / 10.0)
        tens = int(temp % 10.0)
        tenths = int((temp * 10.0) % 10.0)

        return bytes([ones, tens, tenths])

    def close(self):
        """Close the USB connection."""
        if self.device:
            try:
                usb.util.dispose_resources(self.device)
            except:
                pass
            self.device = None
