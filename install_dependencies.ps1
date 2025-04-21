# 泰迪杯依赖项安装脚本 (PowerShell 版本)
# 版本: 1.0
# 日期: 2023-11-12
# 描述: 此脚本用于安装泰迪杯项目所需的所有Python依赖项

# 定义参数
param (
    [switch]$Help,          # 显示帮助信息
    [switch]$Mirror,        # 使用镜像源安装
    [switch]$Virtual,       # 使用虚拟环境
    [switch]$Force,         # 强制重新安装所有依赖
    [switch]$Minimal        # 仅安装最小依赖集
)

# 显示帮助信息
function Show-Help {
    Write-Host "泰迪杯依赖项安装脚本"
    Write-Host "用法: .\install_dependencies.ps1 [-Help] [-Mirror] [-Virtual] [-Force] [-Minimal]"
    Write-Host ""
    Write-Host "选项:"
    Write-Host "  -Help    : 显示此帮助信息"
    Write-Host "  -Mirror  : 使用清华镜像源安装依赖项"
    Write-Host "  -Virtual : 使用虚拟环境安装依赖项"
    Write-Host "  -Force   : 强制重新安装所有依赖项"
    Write-Host "  -Minimal : 只安装核心依赖项"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\install_dependencies.ps1 -Mirror -Virtual"
    Write-Host "  .\install_dependencies.ps1 -Minimal -Force"
    exit 0
}

# 如果指定了帮助选项则显示帮助信息
if ($Help) {
    Show-Help
}

# 欢迎信息
Write-Host "===================================================="
Write-Host "    泰迪杯依赖项安装脚本"
Write-Host "===================================================="
Write-Host ""

# 检查Python环境
Write-Host "正在检查Python环境..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未找到Python。请确保Python已安装并添加到PATH中。" -ForegroundColor Red
    exit 1
}

Write-Host "已找到: $pythonVersion" -ForegroundColor Green
Write-Host ""

# 定义镜像源
$mirrorSource = ""
if ($Mirror) {
    $mirrorSource = "-i https://pypi.tuna.tsinghua.edu.cn/simple"
    Write-Host "将使用清华镜像源安装依赖项" -ForegroundColor Yellow
    Write-Host ""
}

# 虚拟环境处理
if ($Virtual) {
    Write-Host "检查虚拟环境..." -ForegroundColor Cyan
    
    if (-not (Test-Path ".venv")) {
        Write-Host "创建新的虚拟环境..." -ForegroundColor Yellow
        python -m venv .venv
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "错误: 无法创建虚拟环境。请确保已安装venv模块。" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "已找到现有虚拟环境" -ForegroundColor Green
    }
    
    # 激活虚拟环境
    Write-Host "激活虚拟环境..." -ForegroundColor Yellow
    
    # 在Windows上激活虚拟环境
    if ($env:OS -match "Windows") {
        & ".\.venv\Scripts\Activate.ps1"
    } else {
        & "./.venv/bin/Activate.ps1"
    }
    
    Write-Host "虚拟环境已激活" -ForegroundColor Green
    Write-Host ""
}

# 升级pip
Write-Host "升级pip..." -ForegroundColor Cyan
$pipCommand = "python -m pip install --upgrade pip $mirrorSource"
Invoke-Expression $pipCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: 无法升级pip，但将继续安装依赖项" -ForegroundColor Yellow
} else {
    Write-Host "pip已成功升级" -ForegroundColor Green
}
Write-Host ""

# 安装wheel(避免编译问题)
Write-Host "安装wheel..." -ForegroundColor Cyan
$wheelCommand = "python -m pip install wheel $mirrorSource"
Invoke-Expression $wheelCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: 无法安装wheel，这可能会导致后续依赖项安装出现问题" -ForegroundColor Yellow
} else {
    Write-Host "wheel已成功安装" -ForegroundColor Green
}
Write-Host ""

# 定义依赖项安装函数
function Install-Dependency {
    param (
        [string]$Package,
        [string]$Description = ""
    )
    
    if ($Description -ne "") {
        Write-Host "安装$Description... ($Package)" -ForegroundColor Cyan
    } else {
        Write-Host "安装 $Package..." -ForegroundColor Cyan
    }
    
    $forceFlag = ""
    if ($Force) {
        $forceFlag = "--force-reinstall"
    }
    
    $installCommand = "python -m pip install $Package $mirrorSource $forceFlag"
    Invoke-Expression $installCommand
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "警告: 安装 $Package 时出现问题" -ForegroundColor Yellow
        return $false
    } else {
        Write-Host "$Package 已成功安装" -ForegroundColor Green
        return $true
    }
}

# 从requirements.txt安装依赖
function Install-RequirementsFile {
    param (
        [string]$RequirementsFile,
        [string]$Description = "依赖项"
    )
    
    if (-not (Test-Path $RequirementsFile)) {
        Write-Host "错误: 找不到依赖项文件 $RequirementsFile" -ForegroundColor Red
        return $false
    }
    
    Write-Host "正在从 $RequirementsFile 安装$Description..." -ForegroundColor Cyan
    
    $forceFlag = ""
    if ($Force) {
        $forceFlag = "--force-reinstall"
    }
    
    $installCommand = "python -m pip install -r $RequirementsFile $mirrorSource $forceFlag"
    Invoke-Expression $installCommand
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "警告: 从 $RequirementsFile 安装依赖项时出现问题" -ForegroundColor Yellow
        return $false
    } else {
        Write-Host "已成功安装 $RequirementsFile 中的依赖项" -ForegroundColor Green
        return $true
    }
}

# 安装核心依赖
$coreSuccess = $true

if ($Minimal) {
    # 安装最小依赖集
    Write-Host "=== 安装核心依赖项 ===" -ForegroundColor Magenta
    $coreSuccess = $coreSuccess -and (Install-Dependency "fastapi" "FastAPI框架")
    $coreSuccess = $coreSuccess -and (Install-Dependency "uvicorn" "ASGI服务器")
    $coreSuccess = $coreSuccess -and (Install-Dependency "pydantic" "数据验证库")
    $coreSuccess = $coreSuccess -and (Install-Dependency "jinja2" "模板引擎")
    $coreSuccess = $coreSuccess -and (Install-Dependency "PyPDF2" "PDF处理库")
    $coreSuccess = $coreSuccess -and (Install-Dependency "python-multipart" "文件上传支持")
    $coreSuccess = $coreSuccess -and (Install-Dependency "pandas" "数据处理库")
    $coreSuccess = $coreSuccess -and (Install-Dependency "openpyxl" "Excel支持")
    Write-Host ""
} else {
    # 从requirements.txt安装
    if (Test-Path "requirements.txt") {
        $coreSuccess = (Install-RequirementsFile "requirements.txt" "所有依赖项")
    } else {
        Write-Host "错误: 找不到requirements.txt文件" -ForegroundColor Red
        Write-Host "尝试使用 -Minimal 安装最小依赖集" -ForegroundColor Yellow
        exit 1
    }
}

# 单独安装psutil (避免可能的安装问题)
Write-Host "=== 安装系统监控依赖 ===" -ForegroundColor Magenta
$psutilSuccess = Install-Dependency "psutil" "系统监控库"
Write-Host ""

# 结果摘要
Write-Host "===================================================="
Write-Host "    安装结果摘要"
Write-Host "===================================================="

if ($coreSuccess) {
    Write-Host "核心依赖项: 已成功安装" -ForegroundColor Green
} else {
    Write-Host "核心依赖项: 部分安装失败" -ForegroundColor Yellow
}

if ($psutilSuccess) {
    Write-Host "系统监控依赖项(psutil): 已成功安装" -ForegroundColor Green
} else {
    Write-Host "系统监控依赖项(psutil): 安装失败" -ForegroundColor Yellow
    Write-Host "如需手动安装psutil，请尝试运行: python -m pip install psutil" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "安装过程完成。如有依赖项安装失败，请查看上方日志获取详细信息。" -ForegroundColor Cyan
Write-Host "可以使用 -Force 参数强制重新安装依赖项" -ForegroundColor Cyan
Write-Host "可以使用 -Mirror 参数使用镜像源加速安装" -ForegroundColor Cyan
Write-Host "" 