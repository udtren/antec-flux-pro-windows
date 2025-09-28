# Activate the Python virtual environment for Antec Flux Pro Display

Write-Host "Activating Python virtual environment..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Error "Virtual environment not found. Please run .\scripts\build.ps1 first to set up the project."
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate the virtual environment
& ".\venv\Scripts\Activate.ps1"

Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host "You can now run:" -ForegroundColor Cyan
Write-Host "  python main.py              # Test the application"
Write-Host "  python service.py install   # Install Windows service"
Write-Host "  python service.py start     # Start the service"
Write-Host "  python service.py stop      # Stop the service"
Write-Host "  deactivate                  # Exit virtual environment"