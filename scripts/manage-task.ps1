# Task Scheduler management script for Antec Flux Pro Display
# Must be run as Administrator

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "remove")]
    [string]$Action
)

$TaskName = "Antec Flux Pro Display Monitor"

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
        Write-Host "Starting task '$TaskName'..." -ForegroundColor Green
        try {
            Start-ScheduledTask -TaskName $TaskName
            Write-Host "✅ Task started successfully" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Failed to start task: $_" -ForegroundColor Red
        }
    }
    
    "stop" {
        Write-Host "Stopping task '$TaskName'..." -ForegroundColor Yellow
        try {
            Stop-ScheduledTask -TaskName $TaskName
            Write-Host "✅ Task stopped successfully" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Failed to stop task: $_" -ForegroundColor Red
        }
    }
    
    "restart" {
        Write-Host "Restarting task '$TaskName'..." -ForegroundColor Cyan
        try {
            # Stop the task
            Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            Write-Host "⏸️ Task stopped" -ForegroundColor Yellow
            
            # Wait a moment
            Start-Sleep -Seconds 2
            
            # Start the task
            Start-ScheduledTask -TaskName $TaskName
            Write-Host "✅ Task restarted successfully" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Failed to restart task: $_" -ForegroundColor Red
        }
    }
    
    "status" {
        Write-Host "Task Status for '$TaskName':" -ForegroundColor Cyan
        Write-Host "=" * 50
        
        try {
            $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
            $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
            
            Write-Host "Task Name: $($task.TaskName)" -ForegroundColor White
            Write-Host "State: $($task.State)" -ForegroundColor $(if ($task.State -eq "Running") { "Green" } elseif ($task.State -eq "Ready") { "Yellow" } else { "Red" })
            Write-Host "Last Run Time: $($taskInfo.LastRunTime)" -ForegroundColor White
            Write-Host "Last Result: $($taskInfo.LastTaskResult) $(if($taskInfo.LastTaskResult -eq 0) {'(Success)'} else {'(Error)'})" -ForegroundColor $(if ($taskInfo.LastTaskResult -eq 0) { "Green" } else { "Red" })
            Write-Host "Next Run Time: $($taskInfo.NextRunTime)" -ForegroundColor White
            Write-Host "Number of Missed Runs: $($taskInfo.NumberOfMissedRuns)" -ForegroundColor White
            
            if ($task.State -eq "Running") {
                Write-Host ""
                Write-Host "🟢 The task is currently RUNNING" -ForegroundColor Green
            }
            elseif ($task.State -eq "Ready") {
                Write-Host ""
                Write-Host "🟡 The task is READY but not running" -ForegroundColor Yellow
            }
            else {
                Write-Host ""
                Write-Host "🔴 The task is in state: $($task.State)" -ForegroundColor Red
            }
            
        }
        catch {
            Write-Host "❌ Task not found or error: $_" -ForegroundColor Red
        }
    }
    
    "logs" {
        Write-Host "Recent Task Scheduler logs for '$TaskName':" -ForegroundColor Cyan
        Write-Host "=" * 50
        
        try {
            # Get recent Task Scheduler events
            $events = Get-WinEvent -FilterHashtable @{LogName = "Microsoft-Windows-TaskScheduler/Operational"; StartTime = (Get-Date).AddDays(-1) } -MaxEvents 20 -ErrorAction SilentlyContinue | 
            Where-Object { $_.Message -like "*$TaskName*" } |
            Sort-Object TimeCreated -Descending
            
            if ($events) {
                foreach ($event in $events) {
                    $color = switch ($event.LevelDisplayName) {
                        "Error" { "Red" }
                        "Warning" { "Yellow" }
                        "Information" { "Green" }
                        default { "White" }
                    }
                    Write-Host "[$($event.TimeCreated)] $($event.LevelDisplayName): $($event.Message)" -ForegroundColor $color
                }
            }
            else {
                Write-Host "No recent events found for this task" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "❌ Failed to retrieve logs: $_" -ForegroundColor Red
            Write-Host "Try checking Event Viewer manually (eventvwr.msc)" -ForegroundColor Yellow
        }
    }
    
    "remove" {
        Write-Host "Removing task '$TaskName'..." -ForegroundColor Red
        $confirm = Read-Host "Are you sure? (y/N)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            try {
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
                Write-Host "✅ Task removed successfully" -ForegroundColor Green
            }
            catch {
                Write-Host "❌ Failed to remove task: $_" -ForegroundColor Red
            }
        }
        else {
            Write-Host "Operation cancelled" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "Usage examples (as Administrator):" -ForegroundColor Cyan
Write-Host "  .\manage-task.ps1 start     # Start the scheduled task"
Write-Host "  .\manage-task.ps1 stop      # Stop the scheduled task" 
Write-Host "  .\manage-task.ps1 restart   # Restart the scheduled task"
Write-Host "  .\manage-task.ps1 status    # Check task status and info"
Write-Host "  .\manage-task.ps1 logs      # Show recent task logs"
Write-Host "  .\manage-task.ps1 remove    # Remove the scheduled task"