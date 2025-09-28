# Setup script for Antec Flux Pro Display Windows (Python version)

Write-Host "Setting up Antec Flux Pro Display for Windows (Python)..." -ForegroundColor Green

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Please install Python 3.8+ from https://python.org/"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python version
$PythonVersion = python --version 2>&1
Write-Host "Found: $PythonVersion" -ForegroundColor Green

# Navigate to project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSetup completed successfully!" -ForegroundColor Green
    Write-Host "Virtual environment created and dependencies installed." -ForegroundColor Cyan
    Write-Host "`nTo use the application:" -ForegroundColor Cyan
    Write-Host "1. Activate virtual environment: .\venv\Scripts\Activate.ps1"
    Write-Host "2. Run: python main.py (command line version)"
    Write-Host "3. Or install service: .\scripts\install-service.ps1"
    
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Install USB driver using Zadig tool (WinUSB driver for device 2022:0522)"
    Write-Host "2. Ensure Antec Flux Pro case is connected via USB"
    Write-Host "3. Run as Administrator for full functionality"
} else {
    Write-Error "Dependency installation failed. Check error messages above."
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "- Network connectivity problems"
    Write-Host "- Python version compatibility (need 3.8+)"
    Write-Host "- Missing Visual Studio Build Tools for native extensions"
    Write-Host "- Administrator privileges may be required for some packages"
}

Read-Host "Press Enter to exit"