# 泰迪杯智能客服系统 - PDF表格提取演示启动脚本 (PowerShell版)

param (
    [Parameter(HelpMessage = "是否自动打开浏览器")]
    [switch]$Open,
    
    [Parameter(HelpMessage = "指定端口号")]
    [int]$Port = 8000
)

# 显示欢迎信息
Write-Host "=== 泰迪杯智能客服系统 - PDF表格提取演示 ===" -ForegroundColor Cyan
Write-Host "正在准备启动演示环境..." -ForegroundColor Yellow

# 设置Python环境变量
$env:PYTHONPATH = Resolve-Path "$PSScriptRoot\.."
$env:PYTHONIOENCODING = "utf-8"

# 创建必要的目录
$tempDir = Join-Path $PSScriptRoot "temp"
$dataDir = Join-Path $PSScriptRoot "data\processed"

if (-not (Test-Path $tempDir)) {
    New-Item -Path $tempDir -ItemType Directory -Force | Out-Null
    Write-Host "创建临时目录: $tempDir" -ForegroundColor Green
}

if (-not (Test-Path $dataDir)) {
    New-Item -Path $dataDir -ItemType Directory -Force | Out-Null
    Write-Host "创建数据目录: $dataDir" -ForegroundColor Green
}

# 清理Excel锁文件（如果有）
try {
    Write-Host "正在清理Excel锁文件..." -ForegroundColor Yellow
    python -c "from app.data_processing.extract_tables import cleanup_excel_locks; cleanup_excel_locks('data/processed', auto_remove=True)"
    Write-Host "Excel锁文件清理完成" -ForegroundColor Green
} catch {
    Write-Host "清理Excel锁文件时发生错误: $_" -ForegroundColor Red
}

# 检查演示文件是否存在
$demoFile = Join-Path $env:PYTHONPATH "demo\dashboard\table_demo.py"
if (-not (Test-Path $demoFile)) {
    Write-Host "错误: 演示文件不存在: $demoFile" -ForegroundColor Red
    exit 1
}

# 启动演示服务器
Write-Host "正在启动演示服务器，请等待..." -ForegroundColor Yellow
Write-Host "服务启动后，请访问 http://localhost:$Port 查看演示" -ForegroundColor Green

# 如果指定了自动打开浏览器
if ($Open) {
    $demoUrl = "http://localhost:$Port"
    Write-Host "将在5秒后自动打开浏览器..." -ForegroundColor Cyan
    
    # 启动后台任务来打开浏览器
    Start-Job -ScriptBlock {
        param($url)
        Start-Sleep -Seconds 5
        Start-Process $url
    } -ArgumentList $demoUrl | Out-Null
}

# 使用指定端口启动服务器
try {
    & python -c "import sys; sys.path.insert(0, '$env:PYTHONPATH'); from demo.dashboard.table_demo import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=$Port)"
} catch {
    Write-Host "启动服务器时发生错误: $_" -ForegroundColor Red
    exit 1
}

Write-Host "演示服务已停止运行。" -ForegroundColor Yellow 