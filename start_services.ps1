# 泰迪杯智能客服系统 - 服务启动和监控脚本
# 提供更可靠的服务启动机制和健康监控

# 设置颜色函数
function Write-ColorOutput($Message, $Color = "White") {
    $prevColor = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $Color
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $prevColor
}

# 显示欢迎信息
function Show-Banner {
    Write-ColorOutput "===================================================" "Cyan"
    Write-ColorOutput "  泰迪杯智能客服系统 - 服务启动与监控" "Cyan"
    Write-ColorOutput "  版本: 2.0.0 (带自动重启和健康检查)" "Cyan"
    Write-ColorOutput "===================================================" "Cyan"
    Write-Output ""
}

# 定义参数
param (
    [int]$Port = 8080,
    [switch]$Monitor,
    [switch]$Background,
    [switch]$Help
)

# 显示帮助信息
if ($Help) {
    Show-Banner
    Write-ColorOutput "用法: .\start_services.ps1 [-Port <端口>] [-Monitor] [-Background] [-Help]" "Yellow"
    Write-Output ""
    Write-Output "选项:"
    Write-Output "  -Port <端口>  : 设置服务器端口 (默认: 8080)"
    Write-Output "  -Monitor      : 启用服务监控 (每30秒检查一次)"
    Write-Output "  -Background   : 在后台运行服务"
    Write-Output "  -Help         : 显示帮助信息"
    Write-Output ""
    Write-Output "示例:"
    Write-Output "  .\start_services.ps1                  : 在默认端口启动服务"
    Write-Output "  .\start_services.ps1 -Port 3000       : 在端口3000启动服务"
    Write-Output "  .\start_services.ps1 -Monitor         : 启动服务并持续监控状态"
    Write-Output "  .\start_services.ps1 -Background      : 在后台启动服务"
    exit
}

Show-Banner

# 检查Python环境
try {
    $pythonVersion = python --version 2>&1
    Write-ColorOutput "✓ 检测到Python: $pythonVersion" "Green"
}
catch {
    Write-ColorOutput "✗ 未找到Python。请安装Python 3.7+后再试。" "Red"
    exit 1
}

# 检查必要文件
if (-not (Test-Path "app\main.py")) {
    Write-ColorOutput "✗ 未找到'app\main.py'。请确保您在正确的目录中。" "Red"
    exit 1
}

# 创建必要目录
$directories = @("logs", "data", "data\processed", "data\raw")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-ColorOutput "✓ 创建目录: $dir" "Green"
    }
}

# 检查端口是否被占用
function Test-PortInUse {
    param ([int]$Port)
    
    try {
        $conn = New-Object System.Net.Sockets.TcpClient
        $conn.Connect("127.0.0.1", $Port)
        $conn.Close()
        return $true
    }
    catch {
        return $false
    }
}

if (Test-PortInUse -Port $Port) {
    Write-ColorOutput "警告: 端口 $Port 已被占用" "Yellow"
    Write-Output "正在检查是否是我们的服务..."
    
    # 检查是否是我们的服务
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$Port/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response -and $response.status) {
            Write-ColorOutput "✓ 在端口 $Port 上找到现有的健康服务! 状态: $($response.status)" "Green"
            Write-Output "服务运行时间: $($response.uptime) 秒"
            Write-Output "服务已在运行，无需重启"
            
            if ($Monitor) {
                Write-ColorOutput "进入监控模式..." "Cyan"
                Start-ServiceMonitoring -Port $Port
            }
            
            exit 0
        }
    }
    catch {
        Write-ColorOutput "✗ 端口被其他服务占用，尝试使用另一个端口" "Red"
        for ($testPort = 8000; $testPort -lt 9000; $testPort++) {
            if (-not (Test-PortInUse -Port $testPort)) {
                $Port = $testPort
                Write-ColorOutput "找到可用端口: $Port" "Green"
                break
            }
        }
    }
}

# 启动服务函数
function Start-ApiService {
    param (
        [int]$Port,
        [switch]$Background
    )
    
    # 设置环境变量
    $env:API_PORT = $Port
    $env:FASTSTART = "1"
    $env:PYTHONPATH = Get-Location
    
    Write-ColorOutput "正在启动服务，端口: $Port" "Cyan"
    
    # 构建启动命令
    $startCmd = "python -m app.main --port $Port --emergency"
    
    # 执行启动命令
    if ($Background) {
        Write-Output "以后台模式启动服务..."
        Start-Process -FilePath "python" -ArgumentList "-m app.main --port $Port --emergency" -WindowStyle Hidden
    }
    else {
        Write-Output "命令: $startCmd"
        Write-Output "服务即将启动，按 Ctrl+C 可终止..."
        Invoke-Expression $startCmd
    }
}

# 服务监控函数
function Start-ServiceMonitoring {
    param ([int]$Port)
    
    Write-ColorOutput "启动服务监控，端口: $Port" "Cyan"
    Write-Output "每30秒检查一次服务健康状态..."
    
    while ($true) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Output "[$timestamp] 检查服务状态..."
        
        $isRunning = $false
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:$Port/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response -and $response.status) {
                Write-ColorOutput "[$timestamp] ✓ 服务运行正常: $($response.status)" "Green"
                $isRunning = $true
            }
        }
        catch {
            Write-ColorOutput "[$timestamp] ✗ 服务不可达或出错" "Red"
        }
        
        if (-not $isRunning) {
            Write-ColorOutput "[$timestamp] ! 检测到服务中断，正在尝试重启..." "Yellow"
            Start-ApiService -Port $Port -Background
            Write-Output "等待服务启动..."
            Start-Sleep -Seconds 10
        }
        
        Start-Sleep -Seconds 30
    }
}

# 主执行逻辑 - 启动服务
if ($Background) {
    Start-ApiService -Port $Port -Background
    Write-ColorOutput "服务已在后台启动，端口: $Port" "Green"
    Write-Output "访问地址: http://localhost:$Port/"
    Write-Output "健康检查: http://localhost:$Port/health"
    Write-Output "API文档: http://localhost:$Port/docs"
}
else {
    if ($Monitor) {
        # 在后台启动服务，然后进入监控模式
        Start-ApiService -Port $Port -Background
        Write-ColorOutput "等待服务启动..." "Yellow"
        Start-Sleep -Seconds 5
        Start-ServiceMonitoring -Port $Port
    }
    else {
        # 直接启动服务
        Start-ApiService -Port $Port
    }
} 