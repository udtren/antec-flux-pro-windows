# Create Windows startup shortcut for Antec Flux Pro Display

Write-Host "Creating Windows startup shortcut..." -ForegroundColor Green

# Get paths
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PythonScript = Join-Path $ProjectRoot "main.py"
$VenvPython = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$StartupFolder = [System.Environment]::GetFolderPath('Startup')

# Check if files exist
if (-not (Test-Path $PythonScript)) {
    Write-Error "main.py not found at: $PythonScript"
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment Python not found at: $VenvPython"
    Write-Host "Please run .\scripts\build.ps1 first to set up the virtual environment"
    Read-Host "Press Enter to exit"
    exit 1
}

# Create shortcut
Write-Host "Creating shortcut in startup folder..." -ForegroundColor Yellow
Write-Host "Startup folder: $StartupFolder"

$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("$StartupFolder\Antec Flux Pro Display.lnk")
$Shortcut.TargetPath = $VenvPython
$Shortcut.Arguments = "`"$PythonScript`""
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.Description = "Antec Flux Pro Display Temperature Monitor"
$Shortcut.WindowStyle = 7  # Minimized
$Shortcut.Save()

Write-Host "✅ Startup shortcut created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "The application will now start automatically when Windows boots." -ForegroundColor Cyan
Write-Host "It will run minimized in the background."
Write-Host ""
Write-Host "To remove auto-startup:" -ForegroundColor Yellow
Write-Host "Delete: $StartupFolder\Antec Flux Pro Display.lnk"

Read-Host "Press Enter to exit"