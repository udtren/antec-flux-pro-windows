# Antec Flux Pro Display Windows Service
# PowerShell uninstallation script

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    Read-Host "Press Enter to exit"
    exit 1
}

$ServiceName = "AfProDisplay"

Write-Host "Uninstalling Antec Flux Pro Display Windows Service (Python)..." -ForegroundColor Red

# Get the current script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Cannot uninstall Python service."
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if service exists and remove it
Write-Host "Removing Python Windows service..." -ForegroundColor Yellow
Set-Location $ProjectRoot
try {
    python service.py remove
    Write-Host "Service removed successfully." -ForegroundColor Green
}
catch {
    Write-Warning "Failed to remove service or service was not installed."
}

# Ask if user wants to remove configuration
$RemoveConfig = Read-Host "Do you want to remove configuration files? (y/N)"
if ($RemoveConfig -match "^[Yy]") {
    $ConfigDir = "$env:PROGRAMDATA\af-pro-display"
    if (Test-Path $ConfigDir) {
        Write-Host "Removing configuration directory..." -ForegroundColor Yellow
        Remove-Item -Path $ConfigDir -Recurse -Force
        Write-Host "Configuration removed." -ForegroundColor Green
    }
    else {
        Write-Host "Configuration directory not found." -ForegroundColor Yellow
    }
}

Write-Host "`nUninstallation complete!" -ForegroundColor Green
Read-Host "Press Enter to exit"