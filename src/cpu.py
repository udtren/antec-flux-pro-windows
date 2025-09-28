"""
CPU temperature monitoring for Windows using multiple methods.
"""

import wmi
import psutil
from typing import Optional


class CPUMonitor:
    """Monitor CPU temperature on Windows systems."""

    def __init__(self, device: Optional[str] = None):
        self.device = device or "auto"
        self.wmi_connection = None
        self.methods_tried = []
        self._initialize()

    def _initialize(self):
        """Initialize available monitoring methods."""
        # Try WMI connection
        try:
            self.wmi_connection = wmi.WMI(namespace="root\\cimv2")
            self._test_wmi_access()
        except Exception as e:
            print(f"Warning: Failed to initialize WMI connection: {e}")
            self.wmi_connection = None

    def _test_wmi_access(self):
        """Test if WMI temperature access is available."""
        methods_available = []

        try:
            # Try to access thermal zone temperature
            thermal_zones = self.wmi_connection.query(
                "SELECT * FROM MSAcpi_ThermalZoneTemperature"
            )
            if thermal_zones:
                methods_available.append("MSAcpi_ThermalZoneTemperature")
        except Exception:
            pass

        try:
            # Try alternative WMI class
            temp_probes = self.wmi_connection.query(
                "SELECT * FROM Win32_TemperatureProbe"
            )
            if temp_probes:
                methods_available.append("Win32_TemperatureProbe")
        except Exception:
            pass

        try:
            # Try OpenHardwareMonitor WMI namespace (if installed)
            ohm_wmi = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            sensors = ohm_wmi.query(
                "SELECT * FROM Sensor WHERE SensorType='Temperature' AND Name LIKE '%CPU%'"
            )
            if sensors:
                methods_available.append("OpenHardwareMonitor")
                self.ohm_connection = ohm_wmi
        except Exception:
            self.ohm_connection = None

        try:
            # Try LibreHardwareMonitor WMI namespace (if installed)
            lhm_wmi = wmi.WMI(namespace="root\\LibreHardwareMonitor")
            sensors = lhm_wmi.query(
                "SELECT * FROM Sensor WHERE SensorType='Temperature' AND Name LIKE '%CPU%'"
            )
            if sensors:
                methods_available.append("LibreHardwareMonitor")
                self.lhm_connection = lhm_wmi
        except Exception:
            self.lhm_connection = None

        if not methods_available:
            print("Warning: No WMI temperature sources found")
            print(
                "CPU temperature may not be available without additional hardware monitoring software"
            )
        else:
            print(f"Available WMI methods: {', '.join(methods_available)}")

    def get_temperature(self) -> Optional[float]:
        """Get current CPU temperature in Celsius."""
        self.methods_tried = []

        # Try psutil first (if available)
        temp = self._get_psutil_temperature()
        if temp is not None:
            return temp

        if not self.wmi_connection:
            return None

        # Try OpenHardwareMonitor/LibreHardwareMonitor WMI
        temp = self._get_hardware_monitor_temperature()
        if temp is not None:
            return temp

        # Try MSAcpi_ThermalZoneTemperature
        temp = self._get_thermal_zone_temperature()
        if temp is not None:
            return temp

        # Try Win32_TemperatureProbe as fallback
        temp = self._get_temperature_probe()
        if temp is not None:
            return temp

        # Try performance counter as last resort
        temp = self._get_performance_counter_temperature()
        if temp is not None:
            return temp

        return None

    def _get_psutil_temperature(self) -> Optional[float]:
        """Try to get temperature using psutil."""
        try:
            temps = psutil.sensors_temperatures()
            self.methods_tried.append("psutil")

            # Look for CPU-related temperature sensors
            for name, entries in temps.items():
                if (
                    "cpu" in name.lower()
                    or "core" in name.lower()
                    or "package" in name.lower()
                ):
                    for entry in entries:
                        if entry.current and 0 < entry.current < 150:
                            return entry.current

        except Exception as e:
            pass

        return None

    def _get_hardware_monitor_temperature(self) -> Optional[float]:
        """Get temperature from OpenHardwareMonitor or LibreHardwareMonitor."""
        # Try OpenHardwareMonitor
        if hasattr(self, "ohm_connection") and self.ohm_connection:
            try:
                sensors = self.ohm_connection.query(
                    "SELECT * FROM Sensor WHERE SensorType='Temperature' AND (Name LIKE '%CPU%' OR Name LIKE '%Core%')"
                )
                self.methods_tried.append("OpenHardwareMonitor")

                for sensor in sensors:
                    if hasattr(sensor, "Value") and sensor.Value:
                        temp = float(sensor.Value)
                        if 0 < temp < 150:
                            return temp
            except Exception:
                pass

        # Try LibreHardwareMonitor
        if hasattr(self, "lhm_connection") and self.lhm_connection:
            try:
                sensors = self.lhm_connection.query(
                    "SELECT * FROM Sensor WHERE SensorType='Temperature' AND (Name LIKE '%CPU%' OR Name LIKE '%Core%')"
                )
                self.methods_tried.append("LibreHardwareMonitor")

                for sensor in sensors:
                    if hasattr(sensor, "Value") and sensor.Value:
                        temp = float(sensor.Value)
                        if 0 < temp < 150:
                            return temp
            except Exception:
                pass

        return None

    def _get_thermal_zone_temperature(self) -> Optional[float]:
        """Get temperature from MSAcpi_ThermalZoneTemperature."""
        try:
            thermal_zones = self.wmi_connection.query(
                "SELECT * FROM MSAcpi_ThermalZoneTemperature"
            )
            for zone in thermal_zones:
                if hasattr(zone, "CurrentTemperature") and zone.CurrentTemperature:
                    # Convert from tenths of Kelvin to Celsius
                    temp_celsius = (zone.CurrentTemperature / 10.0) - 273.15
                    if 0 < temp_celsius < 150:  # Sanity check
                        return temp_celsius
        except Exception as e:
            pass  # Silently fail and try next method

        return None

    def _get_temperature_probe(self) -> Optional[float]:
        """Get temperature from Win32_TemperatureProbe."""
        try:
            probes = self.wmi_connection.query("SELECT * FROM Win32_TemperatureProbe")
            for probe in probes:
                if hasattr(probe, "CurrentReading") and probe.CurrentReading:
                    # Convert from tenths of Kelvin to Celsius
                    temp_celsius = (probe.CurrentReading / 10.0) - 273.15
                    if 0 < temp_celsius < 150:  # Sanity check
                        return temp_celsius
        except Exception as e:
            pass  # Silently fail and try next method

        return None

    def _get_performance_counter_temperature(self) -> Optional[float]:
        """Get temperature from performance counters."""
        try:
            counters = self.wmi_connection.query(
                "SELECT * FROM Win32_PerfRawData_Counters_ThermalZoneInformation"
            )
            for counter in counters:
                if hasattr(counter, "Temperature") and counter.Temperature:
                    # Convert from Kelvin to Celsius
                    temp_celsius = (counter.Temperature / 10.0) - 273.15
                    if 0 < temp_celsius < 150:  # Sanity check
                        return temp_celsius
        except Exception as e:
            pass  # Silently fail

        return None

    def get_info(self) -> str:
        """Get information about the CPU monitoring method."""
        if not self.wmi_connection:
            return "CPU monitoring: WMI unavailable"

        info = "CPU monitoring: Multiple methods"
        if self.methods_tried:
            info += f" (tried: {', '.join(self.methods_tried)})"

        return info
