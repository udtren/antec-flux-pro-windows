# Test script for Antec Flux Pro Display Windows (Python)

Write-Host "Testing Antec Flux Pro Display..." -ForegroundColor Green

# Get the current script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Error "Virtual environment not found. Please run .\scripts\build.ps1 first."
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if the main script exists
if (-not (Test-Path "main.py")) {
    Write-Error "main.py not found. Please ensure you're in the project directory."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host "Starting temperature monitor test..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the test" -ForegroundColor Cyan

# Run the application
try {
    python main.py --config "config.toml"
} catch {
    Write-Error "Failed to run the application: $_"
}

Read-Host "Press Enter to exit"