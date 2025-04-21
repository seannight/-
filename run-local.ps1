# Teddy Cup Local Startup Script
# No Docker required

Write-Host "============================================================"
Write-Host "       Teddy Cup AI Demo - Local Version"
Write-Host "============================================================"

# Get project root directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootPath = Split-Path -Parent $scriptPath
Write-Host "Project root: $rootPath" -ForegroundColor Green

# Change to project root
Set-Location $rootPath

# Check Python
try {
    python --version
    Write-Host "Python detected" -ForegroundColor Green
}
catch {
    Write-Host "Error: Python not found. Please install Python first" -ForegroundColor Red
    exit 1
}

# Create necessary directories
if (!(Test-Path "data\raw")) {
    New-Item -Path "data\raw" -ItemType Directory -Force | Out-Null
    Write-Host "Created data\raw directory" -ForegroundColor Green
}
if (!(Test-Path "data\processed")) {
    New-Item -Path "data\processed" -ItemType Directory -Force | Out-Null
    Write-Host "Created data\processed directory" -ForegroundColor Green
}
if (!(Test-Path "data\temp")) {
    New-Item -Path "data\temp" -ItemType Directory -Force | Out-Null
    Write-Host "Created data\temp directory" -ForegroundColor Green
}

# Check sample files
if (Test-Path "demo\samples") {
    $sampleFiles = Get-ChildItem -Path "demo\samples" -Filter "*.pdf" | Measure-Object
    if ($sampleFiles.Count -eq 0) {
        Write-Host "Warning: No PDF files in demo\samples directory" -ForegroundColor Yellow
    } else {
        Write-Host "Found $($sampleFiles.Count) sample PDF files" -ForegroundColor Green
    }
} else {
    New-Item -Path "demo\samples" -ItemType Directory -Force | Out-Null
    Write-Host "Created demo\samples directory" -ForegroundColor Yellow
}

# Install required packages
Write-Host "Installing required Python packages..." -ForegroundColor Yellow
pip install fastapi uvicorn python-multipart pdfplumber pandas jieba -q

# Set environment variables
$env:SERVE_STATIC = "True"
$env:PYTHONPATH = $rootPath

# Copy sample files if they exist
if (Test-Path "demo\samples\*.pdf") {
    if (!(Test-Path "data\raw")) {
        New-Item -Path "data\raw" -ItemType Directory -Force | Out-Null
    }
    Copy-Item -Path "demo\samples\*.pdf" -Destination "data\raw\" -Force
    Write-Host "Copied sample PDF files to data\raw directory" -ForegroundColor Green
}

# Start local server
Write-Host "============================================================"
Write-Host "Starting demo environment..." -ForegroundColor Yellow
Write-Host "Demo will be available at http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "============================================================"

# Start server
python -m app.main 