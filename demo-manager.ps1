# TeddyCup Demo Manager
# Script to manage multiple demo environments

function Show-Menu {
    Clear-Host
    Write-Host "====== TeddyCup Demo Manager ======" -ForegroundColor Cyan
    Write-Host "1: Start Local Demo (port 8000)"
    Write-Host "2: Start Docker Demo (port 8080)"
    Write-Host "3: Start Both Demos"
    Write-Host "4: Stop All Demos"
    Write-Host "5: Show Demo Status"
    Write-Host "Q: Exit"
    Write-Host "===================================="
}

function Start-LocalDemo {
    Write-Host "Starting local demo..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit -File $PSScriptRoot\run-local.ps1"
    Write-Host "Local demo started!" -ForegroundColor Green
}

function Start-DockerDemo {
    Write-Host "Starting Docker demo..." -ForegroundColor Yellow
    & $PSScriptRoot\start-demo.ps1
    Write-Host "Docker demo started!" -ForegroundColor Green
}

function Stop-AllDemos {
    Write-Host "Stopping all demos..." -ForegroundColor Yellow
    
    # Stop Docker demo
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    $rootPath = Split-Path -Parent $scriptPath
    Set-Location "$rootPath\docker\demo"
    docker-compose down
    Set-Location $rootPath
    
    # Find and stop local Python processes
    $processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*app.main*" }
    if ($processes) {
        $processes | ForEach-Object { Stop-Process -Id $_.Id -Force }
        Write-Host "Local demo processes stopped" -ForegroundColor Green
    } else {
        Write-Host "No local demo processes found" -ForegroundColor Yellow
    }
    
    Write-Host "All demos stopped!" -ForegroundColor Green
}

function Show-DemoStatus {
    Write-Host "Checking demo status..." -ForegroundColor Yellow
    
    # Check local demo
    $localRunning = $false
    $processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*app.main*" }
    if ($processes) {
        $localRunning = $true
    }
    
    # Check Docker demo
    $dockerRunning = $false
    $container = docker ps | Select-String "demo-api"
    if ($container) {
        $dockerRunning = $true
    }
    
    # Display status
    Write-Host "===== Demo Status =====" -ForegroundColor Cyan
    if ($localRunning) {
        Write-Host "Local Demo: " -NoNewline
        Write-Host "RUNNING" -ForegroundColor Green
        Write-Host "  URL: http://localhost:8000"
    } else {
        Write-Host "Local Demo: " -NoNewline
        Write-Host "STOPPED" -ForegroundColor Red
    }
    
    if ($dockerRunning) {
        Write-Host "Docker Demo: " -NoNewline
        Write-Host "RUNNING" -ForegroundColor Green
        Write-Host "  URL: http://localhost:8080"
    } else {
        Write-Host "Docker Demo: " -NoNewline
        Write-Host "STOPPED" -ForegroundColor Red
    }
    Write-Host "======================="
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice"
    
    switch ($choice) {
        '1' {
            Start-LocalDemo
            pause
        }
        '2' {
            Start-DockerDemo
            pause
        }
        '3' {
            Start-LocalDemo
            Start-DockerDemo
            pause
        }
        '4' {
            Stop-AllDemos
            pause
        }
        '5' {
            Show-DemoStatus
            pause
        }
        'q' {
            return
        }
    }
} until ($choice -eq 'q') 