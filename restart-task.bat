@echo off
REM Quick restart for Antec Flux Pro Display task
REM Must be run as Administrator

echo Restarting Antec Flux Pro Display Monitor...
schtasks /end /tn "Antec Flux Pro Display Monitor" >nul 2>&1
timeout /t 2 /nobreak >nul
schtasks /run /tn "Antec Flux Pro Display Monitor"

if %errorlevel% equ 0 (
    echo ✅ Task restarted successfully!
) else (
    echo ❌ Failed to restart task
    echo Make sure to run as Administrator
)

pause