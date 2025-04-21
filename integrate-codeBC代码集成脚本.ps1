# 泰迪杯项目BC代码集成脚本
# 功能：将BC成员开发的代码整合到Docker环境中
# 使用说明：1. BC成员将代码放入shared_code目录
#          2. A成员运行此脚本进行集成
# 更新日期：2025-03-20

# 设置控制台颜色
$ErrorActionPreference = "Stop"
$InformationPreference = "Continue"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# 显示欢迎信息
Write-ColorOutput Green "======================= 泰迪杯BC代码集成工具 ======================="
Write-ColorOutput Green "开始集成B和C成员代码..."

# 检查共享目录是否存在
if (-not (Test-Path "shared_code")) {
    Write-ColorOutput Red "错误: 未找到shared_code目录，请确保目录已创建!"
    exit 1
}

# 检查app目录是否存在
if (-not (Test-Path "app")) {
    Write-ColorOutput Yellow "警告: 未找到app目录，正在创建..."
    New-Item -Path "app" -ItemType Directory -Force | Out-Null
}

# 如果shared_code目录为空，提示并退出
if ((Get-ChildItem -Path "shared_code" -Recurse -File).Count -eq 0) {
    Write-ColorOutput Yellow "警告: shared_code目录为空，没有找到要集成的代码!"
    exit 0
}

# 复制B和C成员代码
Write-ColorOutput Cyan "正在复制shared_code中的文件到app目录..."

# 确保目标目录存在
if (Test-Path "shared_code\data_processing") {
    if (-not (Test-Path "app\data_processing")) {
        New-Item -Path "app\data_processing" -ItemType Directory -Force | Out-Null
    }
    Copy-Item -Path "shared_code\data_processing\*" -Destination "app\data_processing\" -Recurse -Force
    Write-ColorOutput Green "✓ 成功复制B成员的数据处理代码"
}

if (Test-Path "shared_code\models") {
    if (-not (Test-Path "app\models")) {
        New-Item -Path "app\models" -ItemType Directory -Force | Out-Null
    }
    Copy-Item -Path "shared_code\models\*" -Destination "app\models\" -Recurse -Force
    Write-ColorOutput Green "✓ 成功复制C成员的模型代码"
}

# 检查其他可能的代码目录
$otherDirs = Get-ChildItem -Path "shared_code" -Directory | Where-Object { $_.Name -ne "data_processing" -and $_.Name -ne "models" }
foreach ($dir in $otherDirs) {
    if (-not (Test-Path "app\$($dir.Name)")) {
        New-Item -Path "app\$($dir.Name)" -ItemType Directory -Force | Out-Null
    }
    Copy-Item -Path "shared_code\$($dir.Name)\*" -Destination "app\$($dir.Name)\" -Recurse -Force
    Write-ColorOutput Green "✓ 成功复制$($dir.Name)代码"
}

# 处理根目录下的文件
$rootFiles = Get-ChildItem -Path "shared_code" -File
foreach ($file in $rootFiles) {
    Copy-Item -Path $file.FullName -Destination "app\" -Force
    Write-ColorOutput Green "✓ 成功复制文件: $($file.Name)"
}

# 提示是否要启动Docker环境
$startDocker = Read-Host "是否要在Docker环境中部署集成后的代码? (Y/N)"
if ($startDocker -eq "Y" -or $startDocker -eq "y") {
    # 检查Docker是否已安装
    $dockerInstalled = $null
    try {
        $dockerInstalled = Get-Command "docker" -ErrorAction SilentlyContinue
    } catch {
        # 忽略错误
    }
    
    if ($dockerInstalled) {
        Write-ColorOutput Cyan "正在启动Docker环境..."
        try {
            if (Test-Path "docker\dev") {
                Set-Location "docker\dev"
                docker-compose up -d
                Set-Location "..\..\"
                Write-ColorOutput Green "✓ Docker环境已启动，服务运行中"
            } else {
                Write-ColorOutput Yellow "警告: 未找到docker\dev目录，无法启动Docker环境"
            }
        } catch {
            Write-ColorOutput Red "错误: 启动Docker环境失败: $_"
        }
    } else {
        Write-ColorOutput Yellow "警告: 未检测到Docker命令，请手动启动Docker环境"
    }
}

# 完成信息
Write-ColorOutput Green "======================= 代码集成完成! ======================="
Write-ColorOutput Green "应用目录app中现已包含最新的BC成员代码"
Write-ColorOutput Green "集成完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" 