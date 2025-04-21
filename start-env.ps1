param (
    [string]$Environment = "dev",
    [string]$Action = "up"
)

# 防火墙规则检查与创建
function Test-FirewallRule {
    param (
        [string]$DisplayName,
        [int]$Port
    )
    
    $rule = Get-NetFirewallRule -DisplayName $DisplayName -ErrorAction SilentlyContinue
    
    if ($null -eq $rule) {
        Write-Host "防火墙规则 '$DisplayName' 不存在，正在创建..."
        try {
            New-NetFirewallRule -DisplayName $DisplayName -Direction Inbound -Action Allow -Protocol TCP -LocalPort $Port | Out-Null
            Write-Host "✅ 防火墙规则已创建"
        } catch {
            Write-Host "⚠️ 无法创建防火墙规则，可能需要管理员权限: $_"
            Write-Host "请手动执行: New-NetFirewallRule -DisplayName `"$DisplayName`" -Direction Inbound -Action Allow -Protocol TCP -LocalPort $Port"
        }
    } else {
        Write-Host "✅ 防火墙规则 '$DisplayName' 已存在"
    }
}

# 环境变量文件检查
$envFile = "docker\.env"
$envFileContent = Get-Content $envFile -Raw -ErrorAction SilentlyContinue
if (-not (Test-Path $envFile)) {
    Write-Host "环境变量文件不存在，从模板创建..."
    Copy-Item "docker/.env.example" $envFile
    Write-Host "已创建环境变量文件: $envFile"
}

# 环境目录检查
$envDir = "docker/$Environment"
if (-not (Test-Path $envDir)) {
    Write-Host "错误: 环境目录 '$envDir' 不存在!"
    exit 1
}

# 检查docker-compose.yml文件
$composeFile = "$envDir/docker-compose.yml"
if (-not (Test-Path $composeFile)) {
    Write-Host "错误: docker-compose.yml文件不存在于 '$composeFile'!"
    exit 1
}

# 进入环境目录
Set-Location $envDir

# 根据Action参数执行相应操作
if ($Action -eq "down") {
    # 停止环境
    Write-Host "===== 停止 $Environment 环境 ====="
    Write-Host "停止并移除容器..."
    docker-compose down
    Write-Host "✅ 环境已停止"
} else {
    # 检查并创建防火墙规则
    Test-FirewallRule -DisplayName "TeddyCup-API" -Port 8000
    Test-FirewallRule -DisplayName "TeddyCup-DB" -Port 5432

    # 启动环境
    Write-Host "===== 启动 $Environment 环境 ====="

    # 停止并移除旧容器
    Write-Host "停止并移除旧容器..."
    docker-compose down

    # 构建并启动新容器
    Write-Host "构建并启动新容器..."
    docker-compose up -d --build

    # 检查容器状态
    Write-Host "容器状态:"
    docker-compose ps

    # 输出访问信息
    $envFileContent = Get-Content $envFile -Raw
    $apiPort = if ($envFileContent -match "API_PORT=(\d+)") { $matches[1] } else { "8000" }

    Write-Host "===== 环境已启动 ====="
    Write-Host "API地址: http://localhost:$apiPort"
    Write-Host "健康检查: http://localhost:$apiPort/health"
    Write-Host "API文档: http://localhost:$apiPort/docs"

    # 测试API连接
    Write-Host "正在测试API连接..."
    Start-Sleep -Seconds 10  # 增加等待时间

    # 简化测试方式
    Write-Host "API可能还在启动中，请手动访问: http://localhost:$apiPort/health 来验证"
}

# 返回项目根目录
Set-Location "../../" 
