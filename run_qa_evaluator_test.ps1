# 运行qa_evaluator.py测试
# 用法: .\run_qa_evaluator_test.ps1

# 设置颜色输出
function Write-ColorOutput {
    param (
        [string]$message,
        [string]$color = "White"
    )
    Write-Host $message -ForegroundColor $color
}

# 显示标题
Write-ColorOutput "=====================================================" "Magenta"
Write-ColorOutput "      泰迪杯智能客服系统 - 答案评估系统测试脚本      " "Magenta"
Write-ColorOutput "=====================================================" "Magenta"
Write-ColorOutput ""

# 切换到项目根目录
$rootDir = Split-Path -Parent $PSScriptRoot
Set-Location $rootDir

# 确保结果目录存在
$resultsDir = "tests_real"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir -Force | Out-Null
    Write-ColorOutput "创建测试结果目录: $resultsDir" "Cyan"
}

# 运行测试
try {
    Write-ColorOutput "开始运行测试..." "Cyan"
    Write-ColorOutput "=====================================================" "Yellow"
    
    # 运行本地AnswerEvaluator测试
    Write-ColorOutput "运行本地评估器测试..." "Cyan"
    python -m tests_real.test_qa_evaluator_api
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 测试成功完成!" "Green"
    } else {
        Write-ColorOutput "❌ 测试失败，退出代码: $LASTEXITCODE" "Red"
    }
} catch {
    Write-ColorOutput "❌ 测试过程中发生错误: $_" "Red"
    exit 1
}

# 显示结果
Write-ColorOutput "=====================================================" "Magenta"
Write-ColorOutput "测试完成，结果保存在 $resultsDir 目录" "Green"
exit 0 