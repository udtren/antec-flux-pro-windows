# Antec Flux Pro Display - Windows Service (Python)

A Windows system service that monitors CPU and GPU temperatures and displays them on the Antec Flux Pro case's built-in display via USB.

## Features

- **CPU Temperature Monitoring**: Multiple methods including LibreHardwareMonitor DLL (direct access), Windows Management Instrumentation (WMI), and psutil
- **GPU Temperature Monitoring**: Supports NVIDIA GPUs through pynvml (Python NVML bindings)
- **USB Communication**: Communicates with the Antec Flux Pro display via USB using PyUSB
- **Windows Service**: Runs as a Windows system service for automatic startup
- **Configuration**: TOML-based configuration file

## Prerequisites

### Hardware
- Antec Flux Pro case with built-in display
- USB connection to the display unit

### Software
- Windows 11 (recommended) or Windows 10
- Python 3.8 or later
- NVIDIA GPU drivers (if using NVIDIA GPU)

## Installation

### 1. Install Python
Download and install Python 3.8+ from [python.org](https://python.org/)
Make sure to check "Add Python to PATH" during installation.

### 2. Download/Clone Project
Download or extract the project files to a directory (e.g., `C:\af-pro-display`)

### 3. USB Driver Setup
The Antec Flux Pro display requires a compatible USB driver:

1. Download [Zadig](https://zadig.akeo.ie/) USB driver tool
2. Connect your Antec Flux Pro case
3. In Zadig, look for the device with VID 2022, PID 0522
4. Install the WinUSB driver for this device

### 4. Install Dependencies
```powershell
# Navigate to the project directory
cd antec-flux-pro-windows

# Run the setup script (creates venv and installs dependencies)
.\scripts\build.ps1

# Download LibreHardwareMonitorLib.dll (recommended for accurate CPU temps)
python download_dll.py

# Set up LibreHardwareMonitor DLL support
python setup_libre_hardware_monitor.py
```

Or set up manually:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment  
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install LibreHardwareMonitor DLL support
pip install pythonnet==3.0.3

# Download DLL manually from:
# https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases/latest
# Extract LibreHardwareMonitorLib.dll to project root
```

## Usage

### Command Line Mode
```powershell
# Activate virtual environment first
.\activate.ps1

# Run directly (useful for testing)  
python main.py

# Specify custom config file
python main.py --config "C:\custom\path\config.toml"
```

### Windows Service Mode

#### Install the Service
```powershell
# Run as Administrator
.\scripts\install-service.ps1
```

Or manually:
```powershell
# Run as Administrator
python service.py install
```

#### Manage the Service
```powershell
# Start the service
python service.py start

# Stop the service  
python service.py stop

# Check service status
python service.py status

# Remove the service
python service.py remove
```

## Configuration

The application uses a TOML configuration file located at:
- Command line mode: `%APPDATA%\af-pro-display\config.toml`
- Service mode: `%PROGRAMDATA%\af-pro-display\config.toml`

### Default Configuration
```toml
# CPU device path (Windows uses WMI by default)
cpu_device = "WMI"

# GPU device (auto-detected for NVIDIA GPUs)
gpu_device = "auto"

# Polling interval in milliseconds
polling_interval = 1000
```

## Dependencies

The project requires these Python packages (installed automatically):

- **pyusb**: USB communication
- **pynvml**: NVIDIA GPU monitoring  
- **WMI**: Windows Management Instrumentation for CPU monitoring
- **toml**: Configuration file parsing
- **pywin32**: Windows service functionality
- **psutil**: System monitoring (fallback)

## Troubleshooting

### USB Device Not Found
1. Verify the Antec Flux Pro case is connected via USB
2. Check Windows Device Manager for the device (VID 2022, PID 0522)
3. Install WinUSB driver using Zadig tool
4. Try running as Administrator

### CPU Temperature Not Available
1. **LibreHardwareMonitor DLL (Recommended)**: The project includes LibreHardwareMonitorLib.dll for direct hardware access
   - Run: `python setup_libre_hardware_monitor.py`
   - Provides most accurate temperature readings
2. Run as Administrator (required for WMI temperature access)
3. Check if your motherboard supports WMI temperature reporting
4. Alternative: Install LibreHardwareMonitor application for WMI namespace support

### GPU Temperature Not Available
1. Ensure NVIDIA drivers are installed and up to date
2. Install pynvml: `pip install pynvml`
3. Verify GPU is supported by NVML

### Testing
```powershell
# Test the application
.\scripts\test.ps1

# Test LibreHardwareMonitor DLL integration
python test_libre_hardware_monitor.py

# Or run directly
python main.py
```

## CPU Temperature Monitoring Methods

The application uses multiple methods to obtain CPU temperature, in order of priority:

1. **LibreHardwareMonitor DLL**: Direct access via .NET interop (most accurate)
2. **psutil**: Cross-platform system monitoring
3. **WMI - OpenHardwareMonitor/LibreHardwareMonitor**: WMI namespace (requires app installed)
4. **WMI - MSAcpi_ThermalZoneTemperature**: Windows ACPI thermal zones
5. **WMI - Win32_TemperatureProbe**: Generic temperature probes
6. **WMI - Performance Counters**: Thermal zone performance data

The LibreHardwareMonitor DLL method provides the most reliable and accurate readings without requiring additional software installation.