# Teddy Cup Demo Environment Starter
# Simple script to start the demo environment

# Display welcome message
Write-Host "====================================================="
Write-Host "       Teddy Cup AI Demo - Simple Version"
Write-Host "====================================================="

# Get project root directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootPath = Split-Path -Parent $scriptPath
Write-Host "Project root: $rootPath" -ForegroundColor Green

# Change to project root
Set-Location $rootPath

# Check Docker
try {
    docker --version
    Write-Host "Docker detected" -ForegroundColor Green
}
catch {
    Write-Host "Error: Docker not found. Please install Docker first" -ForegroundColor Red
    exit 1
}

# Enter docker-compose.yml directory
Set-Location "$rootPath\docker\demo"
Write-Host "Entered docker config directory: $(Get-Location)" -ForegroundColor Green

# Build and start docker containers
Write-Host "Building docker image..." -ForegroundColor Yellow
docker-compose build

Write-Host "Starting docker containers..." -ForegroundColor Yellow
docker-compose up -d

# Check status
if ($LASTEXITCODE -eq 0) {
    Write-Host "Demo environment started successfully!" -ForegroundColor Green
    Write-Host "Web demo: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "Alternative URL: http://localhost:81" -ForegroundColor Cyan
    Write-Host "Use 'docker-compose down' to stop services" -ForegroundColor Yellow
} 
else {
    Write-Host "Startup failed. Trying alternative..." -ForegroundColor Yellow
    docker-compose up -d api
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "API service started" -ForegroundColor Green
        Write-Host "API URL: http://localhost:8080" -ForegroundColor Cyan
    } 
    else {
        Write-Host "All services failed to start. Check Docker configuration" -ForegroundColor Red
    }
}

# Return to original directory
Set-Location $rootPath 