# 环境检查脚本
Write-Host "检查Python环境..." -ForegroundColor Cyan
python --version

Write-Host "检查必要依赖..." -ForegroundColor Cyan
pip list | findstr "pdfplumber PyPDF2 jieba fastapi pandas"

Write-Host "检查目录结构..." -ForegroundColor Cyan
if (!(Test-Path "data/raw")) { New-Item -Path "data/raw" -ItemType Directory -Force }
if (!(Test-Path "data/processed")) { New-Item -Path "data/processed" -ItemType Directory -Force }
if (!(Test-Path "shared_code")) { New-Item -Path "shared_code" -ItemType Directory -Force }