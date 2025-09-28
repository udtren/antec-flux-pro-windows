#!/usr/bin/env python3
"""
CPU Temperature Diagnostic Script for Windows
Tests various methods to read CPU temperature.
"""

import sys

print("=== CPU Temperature Diagnostic ===\n")

# Test 1: psutil
print("1. Testing psutil sensors...")
try:
    import psutil

    temps = psutil.sensors_temperatures()
    if temps:
        print("✅ psutil sensors found:")
        for name, entries in temps.items():
            print(f"  {name}:")
            for entry in entries:
                print(f"    {entry.label}: {entry.current}°C")
    else:
        print("❌ No psutil temperature sensors found")
except ImportError:
    print("❌ psutil not available")
except Exception as e:
    print(f"❌ psutil error: {e}")

print()

# Test 2: WMI Standard
print("2. Testing WMI standard methods...")
try:
    import wmi

    c = wmi.WMI(namespace="root\\cimv2")

    # Test MSAcpi_ThermalZoneTemperature
    print("   Testing MSAcpi_ThermalZoneTemperature...")
    try:
        zones = c.query("SELECT * FROM MSAcpi_ThermalZoneTemperature")
        if zones:
            print("   ✅ Thermal zones found:")
            for zone in zones:
                if hasattr(zone, "CurrentTemperature") and zone.CurrentTemperature:
                    temp_c = (zone.CurrentTemperature / 10.0) - 273.15
                    print(f"     Zone: {temp_c:.1f}°C")
        else:
            print("   ❌ No thermal zones found")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test Win32_TemperatureProbe
    print("   Testing Win32_TemperatureProbe...")
    try:
        probes = c.query("SELECT * FROM Win32_TemperatureProbe")
        if probes:
            print("   ✅ Temperature probes found:")
            for probe in probes:
                if hasattr(probe, "CurrentReading") and probe.CurrentReading:
                    temp_c = (probe.CurrentReading / 10.0) - 273.15
                    print(f"     Probe: {temp_c:.1f}°C")
        else:
            print("   ❌ No temperature probes found")
    except Exception as e:
        print(f"   ❌ Error: {e}")

except ImportError:
    print("❌ WMI not available")
except Exception as e:
    print(f"❌ WMI error: {e}")

print()

# Test 3: OpenHardwareMonitor WMI
print("3. Testing OpenHardwareMonitor WMI...")
try:
    import wmi

    ohm = wmi.WMI(namespace="root\\OpenHardwareMonitor")
    sensors = ohm.query("SELECT * FROM Sensor WHERE SensorType='Temperature'")
    if sensors:
        print("✅ OpenHardwareMonitor sensors found:")
        for sensor in sensors:
            if "CPU" in sensor.Name or "Core" in sensor.Name:
                print(f"   {sensor.Name}: {sensor.Value}°C")
    else:
        print("❌ OpenHardwareMonitor not running or no sensors")
except Exception as e:
    print(f"❌ OpenHardwareMonitor error: {e}")

print()

# Test 4: LibreHardwareMonitor WMI
print("4. Testing LibreHardwareMonitor WMI...")
try:
    import wmi

    lhm = wmi.WMI(namespace="root\\LibreHardwareMonitor")
    sensors = lhm.query("SELECT * FROM Sensor WHERE SensorType='Temperature'")
    if sensors:
        print("✅ LibreHardwareMonitor sensors found:")
        for sensor in sensors:
            if "CPU" in sensor.Name or "Core" in sensor.Name:
                print(f"   {sensor.Name}: {sensor.Value}°C")
    else:
        print("❌ LibreHardwareMonitor not running or no sensors")
except Exception as e:
    print(f"❌ LibreHardwareMonitor error: {e}")

print("\n=== Recommendations ===")
print("If no methods worked:")
print(
    "1. Install LibreHardwareMonitor (https://github.com/LibreHardwareMonitor/LibreHardwareMonitor)"
)
print("2. Run LibreHardwareMonitor as Administrator")
print("3. In newer versions, WMI is enabled by default - no extra setup needed")
print("4. Alternative: Use OpenHardwareMonitor (older but has explicit WMI option)")
print("5. Some motherboards don't expose temperature sensors via Windows APIs")
print("\nAlternative solution: Use a hardware monitoring library directly")
