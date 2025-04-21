# 泰迪杯智能客服系统 - 简单测试脚本

# 创建输出目录
$outputDir = "tests_real/outputs"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "创建输出目录: $outputDir" -ForegroundColor Cyan
}

# 显示标题
Write-Host "====================================================" -ForegroundColor Magenta
Write-Host "      泰迪杯智能客服系统 - 简单测试脚本      " -ForegroundColor Magenta
Write-Host "====================================================" -ForegroundColor Magenta
Write-Host ""

# 记录开始时间
$startTime = Get-Date

# 检查Python环境
Write-Host "检查Python环境..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version
    Write-Host "使用 $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "错误: 未找到Python。请确保Python已安装并添加到PATH中。" -ForegroundColor Red
    exit 1
}

# 执行问答系统测试
Write-Host "`n===== 测试问答系统功能 =====" -ForegroundColor Magenta
try {
    Write-Host "执行问答系统测试..." -ForegroundColor Cyan
    $testOutputFile = "$outputDir/qa_system_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    $testOutput = & python -m tests_real.test_qa_evaluator_api --skip-api-test 2>&1
    $testOutput | Out-File -FilePath $testOutputFile -Encoding utf8
    
    foreach ($line in $testOutput) {
        if ($line -match "测试失败") {
            Write-Host $line -ForegroundColor Red
        }
        elseif ($line -match "警告") {
            Write-Host $line -ForegroundColor Yellow
        }
        elseif ($line -match "测试完成|所有测试已完成") {
            Write-Host $line -ForegroundColor Green
        }
        else {
            Write-Host $line
        }
    }
    
    Write-Host "测试日志已保存到: $testOutputFile" -ForegroundColor Cyan
}
catch {
    Write-Host "执行问答系统测试时出错: $_" -ForegroundColor Red
}

# 计算运行时间
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

# 显示总结
Write-Host "`n===== 测试总结 =====" -ForegroundColor Magenta
Write-Host "测试耗时: $([math]::Round($duration, 2)) 秒" -ForegroundColor Cyan
Write-Host "测试脚本执行完成。" -ForegroundColor Magenta 