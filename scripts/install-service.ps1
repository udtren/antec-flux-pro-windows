# Antec Flux Pro Display Windows Service
# PowerShell installation script

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    Read-Host "Press Enter to exit"
    exit 1
}

$ServiceName = "AfProDisplay"
$ServiceDisplayName = "Antec Flux Pro Display Monitor"
$ServiceDescription = "Monitors CPU and GPU temperatures and displays them on Antec Flux Pro case display"

Write-Host "Installing Antec Flux Pro Display Windows Service (Python)..." -ForegroundColor Green

# Get the current script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$ServiceScript = Join-Path $ProjectRoot "service.py"

Set-Location $ProjectRoot

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Error "Virtual environment not found. Please run .\scripts\build.ps1 first."
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if service script exists
if (-not (Test-Path $ServiceScript)) {
    Write-Error "Service script not found at: $ServiceScript"
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Stop service if it's running
$ExistingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($ExistingService) {
    Write-Host "Stopping existing service..." -ForegroundColor Yellow
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    
    Write-Host "Removing existing service..." -ForegroundColor Yellow
    sc.exe delete $ServiceName
    Start-Sleep -Seconds 2
}

# Install the Python service
Write-Host "Installing Python Windows service..." -ForegroundColor Green
$InstallResult = python service.py install
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install service"
    Read-Host "Press Enter to exit"
    exit 1
}

# Set service description
sc.exe description $ServiceName $ServiceDescription

# Create config directory and default config
$ConfigDir = "$env:PROGRAMDATA\af-pro-display"
if (-not (Test-Path $ConfigDir)) {
    Write-Host "Creating configuration directory..." -ForegroundColor Green
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
}

$ConfigFile = Join-Path $ConfigDir "config.toml"
if (-not (Test-Path $ConfigFile)) {
    Write-Host "Creating default configuration file..." -ForegroundColor Green
    $DefaultConfig = @"
# CPU device path (Windows uses WMI by default)
cpu_device = "WMI"

# GPU device (auto-detected) 
gpu_device = "auto"

# Polling interval in milliseconds
polling_interval = 1000
"@
    $DefaultConfig | Out-File -FilePath $ConfigFile -Encoding UTF8
}

# Start the service
Write-Host "Starting service..." -ForegroundColor Green
$StartResult = python service.py start
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Service installed but failed to start. This might be normal if USB device is not connected."
    Write-Host "You can start it later with: python service.py start"
}
else {
    Write-Host "Service started successfully!" -ForegroundColor Green
}

# Display service status
Write-Host "`nService Information:" -ForegroundColor Cyan
Write-Host "Name: $ServiceName"
Write-Host "Display Name: $ServiceDisplayName"
Write-Host "Script: $ServiceScript"
Write-Host "Config File: $ConfigFile"

Write-Host "`nService Management Commands:" -ForegroundColor Cyan
Write-Host "Start:   python service.py start"
Write-Host "Stop:    python service.py stop"
Write-Host "Status:  python service.py status"
Write-Host "Remove:  python service.py remove"

Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "Check Windows Event Viewer (Windows Logs > Application) for service logs." -ForegroundColor Yellow

Read-Host "Press Enter to exit"