# ===== 泰迪杯智能客服系统简易启动脚本 (PowerShell版) =====
# 版本: 1.1.0
# 提供一键启动功能，包含智能性能优化

param (
    [switch]$Help,
    [int]$Port = 8000,
    [switch]$Open,
    [switch]$Performance
)

# 显示欢迎信息
function Show-Welcome {
    Write-Host "===== 泰迪杯智能客服系统简易启动脚本 =====" -ForegroundColor Cyan
    Write-Host "版本: 1.1.0" -ForegroundColor Cyan
    Write-Host "=======================================" -ForegroundColor Cyan
    Write-Host ""
}

# 显示帮助信息
function Show-Help {
    Write-Host "使用方法: .\run_easy.ps1 [-Help] [-Port <端口号>] [-Open] [-Performance]" -ForegroundColor Yellow
    Write-Host "参数:"
    Write-Host "  -Help          显示帮助信息"
    Write-Host "  -Port <值>     设置服务器端口 (默认: 8000)"
    Write-Host "  -Open          启动后自动打开浏览器"
    Write-Host "  -Performance   启用性能优化模式（自动调整资源配置）"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\run_easy.ps1              使用默认配置启动"
    Write-Host "  .\run_easy.ps1 -Port 8080   在端口8080上启动"
    Write-Host "  .\run_easy.ps1 -Open        启动并自动打开浏览器"
    Write-Host "  .\run_easy.ps1 -Performance 启用性能优化模式"
    Write-Host ""
    Exit 0
}

# 检查Python环境
function Test-PythonEnvironment {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ 已检测到Python: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "× 未检测到Python，请安装Python 3.9+" -ForegroundColor Red
        Write-Host "按任意键退出..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        Exit 1
    }
}

# 检查必要文件
function Test-RequiredFiles {
    if (-not (Test-Path -Path "app\main.py")) {
        Write-Host "× 未找到app\main.py文件，请确保您在正确的目录中运行此脚本" -ForegroundColor Red
        Write-Host "按任意键退出..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        Exit 1
    }
    Write-Host "✓ 已找到所需的应用文件" -ForegroundColor Green
}

# 创建必要的目录
function New-RequiredDirectories {
    if (-not (Test-Path -Path "logs")) {
        New-Item -Path "logs" -ItemType Directory | Out-Null
        Write-Host "✓ 已创建logs目录" -ForegroundColor Green
    }
    
    if (-not (Test-Path -Path "data\processed")) {
        New-Item -Path "data\processed" -ItemType Directory -Force | Out-Null
        Write-Host "✓ 已创建data\processed目录" -ForegroundColor Green
    }
}

# 智能性能配置（分析系统资源并设置最佳参数）
function Set-PerformanceOptimization {
    Write-Host ""
    Write-Host "进行性能优化配置..." -ForegroundColor Cyan
    
    # 获取系统信息
    $cpuCores = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
    $totalMemoryGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
    
    Write-Host "系统信息: $cpuCores 核心CPU, $totalMemoryGB GB内存" -ForegroundColor Green
    
    # 计算最佳参数
    $workerCount = [math]::Min($cpuCores, 4) # 最多使用4个工作进程
    
    # 设置优化环境变量
    $env:WORKER_COUNT = $workerCount
    $env:OPTIMIZE_MEMORY = "1"
    $env:PRELOAD_MODELS = "1"
    $env:LOAD_BALANCE = "auto"
    
    Write-Host "已配置最佳性能参数:" -ForegroundColor Green
    Write-Host "  - 工作进程: $workerCount"
    Write-Host "  - 内存优化: 已启用"
    Write-Host "  - 模型预加载: 已启用"
    Write-Host "  - 负载均衡: 自动"
    Write-Host ""
    
    # 运行预热脚本（如果存在）
    if (Test-Path -Path "scripts\preload.py") {
        Write-Host "运行系统预热脚本..." -ForegroundColor Yellow
        Start-Process -FilePath "python" -ArgumentList "scripts\preload.py" -NoNewWindow -Wait
    }
}

# 清理临时文件（提高性能）
function Remove-TempFiles {
    Write-Host "清理临时文件..." -ForegroundColor Yellow
    
    # 清理Excel锁定文件
    Get-ChildItem -Path "data\processed" -Filter "~$*" -Recurse | Remove-Item -Force
    
    # 清理缓存文件
    if (Test-Path -Path "app\__pycache__") {
        Remove-Item -Path "app\__pycache__\*.pyc" -Force -ErrorAction SilentlyContinue
    }
    
    # 清理旧日志（保留最近7天）
    $cutoffDate = (Get-Date).AddDays(-7)
    Get-ChildItem -Path "logs" -Filter "*.log" | Where-Object { $_.LastWriteTime -lt $cutoffDate } | Remove-Item -Force
    
    Write-Host "✓ 临时文件清理完成" -ForegroundColor Green
}

# 启动服务
function Start-Server {
    param (
        [int]$Port,
        [bool]$OpenBrowser,
        [bool]$PerformanceMode
    )
    
    # 设置环境变量
    $env:PYTHONPATH = (Get-Location).Path
    $env:FASTSTART = 1
    $env:UI_PRIORITY = 1
    $env:API_PORT = $Port
    
    # 性能模式配置
    if ($PerformanceMode) {
        Set-PerformanceOptimization
        Remove-TempFiles
        
        # 启用性能监控
        $env:ENABLE_MONITORING = 1
    }
    
    Write-Host ""
    Write-Host "启动服务器，配置如下:" -ForegroundColor Cyan
    Write-Host "- 端口: $Port" -ForegroundColor White
    Write-Host "- 快速启动模式: 已启用" -ForegroundColor White
    Write-Host "- UI优先模式: 已启用" -ForegroundColor White
    if ($PerformanceMode) {
        Write-Host "- 性能优化模式: 已启用" -ForegroundColor White
    }
    Write-Host ""
    
    Write-Host "服务器启动后，可通过以下地址访问:" -ForegroundColor Yellow
    Write-Host "- 演示界面: http://localhost:$Port/dashboard" -ForegroundColor White
    Write-Host "- API文档: http://localhost:$Port/docs" -ForegroundColor White
    Write-Host ""
    
    Write-Host "正在启动服务，请稍候..." -ForegroundColor Cyan
    Write-Host "请使用Ctrl+C停止服务" -ForegroundColor Yellow
    Write-Host ""
    
    # 准备启动命令
    $startCmd = "python -m app.main --port $Port --fast --ui-priority"
    if ($PerformanceMode) {
        $startCmd += " --optimize"
    }
    
    # 启动服务
    try {
        if ($OpenBrowser) {
            # 创建一个后台作业来启动浏览器
            Start-Job -ScriptBlock {
                param($Port)
                Start-Sleep -Seconds 3
                Start-Process "http://localhost:$Port/dashboard"
            } -ArgumentList $Port | Out-Null
        }
        
        # 显示启动时间
        $startTime = Get-Date
        Write-Host "开始启动时间: $startTime" -ForegroundColor Gray
        
        # 启动主服务
        Invoke-Expression $startCmd
    }
    catch {
        Write-Host "× 启动服务时出现错误: $_" -ForegroundColor Red
        Write-Host "按任意键退出..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        Exit 1
    }
}

# 主流程
Show-Welcome

if ($Help) {
    Show-Help
}

Test-PythonEnvironment
Test-RequiredFiles
New-RequiredDirectories
Start-Server -Port $Port -OpenBrowser $Open.IsPresent -PerformanceMode $Performance.IsPresent

# 脚本结束
Write-Host ""
Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")