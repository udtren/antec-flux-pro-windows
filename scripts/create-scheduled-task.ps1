# Create Windows Task Scheduler entry for Antec Flux Pro Display
# This is more reliable than Python Windows Service

Write-Host "Creating Windows Task Scheduler entry..." -ForegroundColor Green

# Get paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$PythonScript = Join-Path $ProjectRoot "main.py"
$VenvPython = Join-Path $ProjectRoot "venv\Scripts\python.exe"

# Verify files exist
if (-not (Test-Path $PythonScript)) {
    Write-Error "main.py not found at: $PythonScript"
    exit 1
}

if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment Python not found at: $VenvPython"
    Write-Host "Run .\scripts\build.ps1 first to set up the virtual environment"
    exit 1
}

$TaskName = "Antec Flux Pro Display Monitor"
$Description = "Monitors CPU and GPU temperatures and displays them on Antec Flux Pro case display"

# Create the scheduled task action
$Action = New-ScheduledTaskAction -Execute $VenvPython -Argument "`"$PythonScript`"" -WorkingDirectory $ProjectRoot

# Create the trigger (at startup)
$Trigger = New-ScheduledTaskTrigger -AtStartup

# Create the principal (run as SYSTEM with highest privileges)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Create the settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

# Remove existing task if it exists
try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed existing task" -ForegroundColor Yellow
} catch {
    # Task didn't exist, continue
}

# Create the scheduled task
try {
    Register-ScheduledTask -TaskName $TaskName -Description $Description -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings
    Write-Host "✅ Task created successfully!" -ForegroundColor Green
    
    # Start the task immediately
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "✅ Task started!" -ForegroundColor Green
    
} catch {
    Write-Error "Failed to create scheduled task: $_"
    exit 1
}

Write-Host ""
Write-Host "✅ Antec Flux Pro Display Monitor is now configured to start automatically!" -ForegroundColor Green
Write-Host ""
Write-Host "Task Details:" -ForegroundColor Cyan
Write-Host "  Name: $TaskName"
Write-Host "  Runs as: SYSTEM (highest privileges)"
Write-Host "  Trigger: At Windows startup"
Write-Host "  Auto-restart: Yes (if crashes)"
Write-Host ""
Write-Host "Management commands:" -ForegroundColor Cyan
Write-Host "  Start:   Start-ScheduledTask '$TaskName'"
Write-Host "  Stop:    Stop-ScheduledTask '$TaskName'"
Write-Host "  Status:  Get-ScheduledTask '$TaskName' | Get-ScheduledTaskInfo"
Write-Host "  Remove:  Unregister-ScheduledTask '$TaskName'"
Write-Host ""
Write-Host "You can also manage it through Task Scheduler GUI (taskschd.msc)" -ForegroundColor Yellow

Read-Host "Press Enter to exit"