# Service management script for Antec Flux Pro Display
# Must be run as Administrator

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "auto", "manual")]
    [string]$Action
)

$ServiceName = "AfProDisplay"

function Test-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

switch ($Action) {
    "start" {
        Write-Host "Starting $ServiceName..." -ForegroundColor Green
        sc.exe start $ServiceName
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Service started successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to start service" -ForegroundColor Red
        }
    }
    
    "stop" {
        Write-Host "Stopping $ServiceName..." -ForegroundColor Yellow
        sc.exe stop $ServiceName
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Service stopped successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to stop service" -ForegroundColor Red
        }
    }
    
    "restart" {
        Write-Host "Restarting $ServiceName..." -ForegroundColor Cyan
        sc.exe stop $ServiceName
        Start-Sleep -Seconds 2
        sc.exe start $ServiceName
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Service restarted successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to restart service" -ForegroundColor Red
        }
    }
    
    "status" {
        Write-Host "Service status:" -ForegroundColor Cyan
        sc.exe query $ServiceName
        Write-Host ""
        Get-Service -Name $ServiceName | Select-Object Name, Status, StartType, DisplayName
    }
    
    "auto" {
        Write-Host "Setting $ServiceName to start automatically..." -ForegroundColor Green
        sc.exe config $ServiceName start= auto
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Service set to automatic startup" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to configure service" -ForegroundColor Red
        }
    }
    
    "manual" {
        Write-Host "Setting $ServiceName to manual start..." -ForegroundColor Yellow
        sc.exe config $ServiceName start= demand
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Service set to manual startup" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to configure service" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "Usage examples (as Administrator):" -ForegroundColor Cyan
Write-Host "  .\manage-service.ps1 start     # Start the service"
Write-Host "  .\manage-service.ps1 stop      # Stop the service" 
Write-Host "  .\manage-service.ps1 restart   # Restart the service"
Write-Host "  .\manage-service.ps1 status    # Check service status"
Write-Host "  .\manage-service.ps1 auto      # Set to automatic startup"
Write-Host "  .\manage-service.ps1 manual    # Set to manual startup"