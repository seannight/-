# 泰迪杯智能客服系统 - 全面自动化测试脚本
# 使用方法：./auto_test.ps1 [参数]
# 参数：
#   -TestPDF       : 测试PDF解析功能
#   -TestQA        : 测试问答系统功能
#   -TestAPI       : 测试API接口功能
#   -FullTest      : 执行所有测试
#   -GenerateReport: 生成HTML测试报告
#   -CleanTemp     : 清理临时文件

param (
    [switch]$TestPDF,
    [switch]$TestQA,
    [switch]$TestAPI,
    [switch]$FullTest,
    [switch]$GenerateReport,
    [switch]$CleanTemp
)

# 定义颜色
$colors = @{
    "success" = "Green"
    "warning" = "Yellow"
    "error" = "Red"
    "info" = "Cyan"
    "highlight" = "Magenta"
}

# 输出带颜色的消息
function Write-ColorOutput {
    param (
        [string]$message,
        [string]$color = "White"
    )
    Write-Host $message -ForegroundColor $color
}

# 创建输出目录
$outputDir = "tests_real/outputs"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-ColorOutput "创建输出目录: $outputDir" $colors.info
}

# 显示标题
Write-ColorOutput "====================================================" $colors.highlight
Write-ColorOutput "      泰迪杯智能客服系统 - 全面自动化测试脚本      " $colors.highlight
Write-ColorOutput "====================================================" $colors.highlight
Write-ColorOutput ""

# 设置测试参数
if ($FullTest) {
    $TestPDF = $true
    $TestQA = $true
    $TestAPI = $true
}

# 如果没有指定任何测试，默认执行所有测试
if (-not ($TestPDF -or $TestQA -or $TestAPI)) {
    $TestPDF = $true
    $TestQA = $true
    $TestAPI = $true
    Write-ColorOutput "未指定测试类型，默认执行所有测试" $colors.info
}

# 检查Python环境
Write-ColorOutput "检查Python环境..." $colors.info
try {
    $pythonVersion = python --version
    Write-ColorOutput "使用 $pythonVersion" $colors.success
}
catch {
    Write-ColorOutput "错误: 未找到Python。请确保Python已安装并添加到PATH中。" $colors.error
    exit 1
}

# 检查数据文件
$dataPath = "app/data/raw/附件1"
if (-not (Test-Path $dataPath)) {
    Write-ColorOutput "错误: 数据目录 $dataPath 不存在。" $colors.error
    exit 1
}
else {
    $pdfFiles = Get-ChildItem -Path $dataPath -Filter "*.pdf" | Measure-Object
    Write-ColorOutput "找到 $($pdfFiles.Count) 个PDF文件用于测试" $colors.success
}

# 记录开始时间
$startTime = Get-Date
$testResults = @()

# 测试PDF解析功能
if ($TestPDF) {
    Write-ColorOutput "`n===== 测试PDF表格提取功能 =====" $colors.highlight
    
    # 执行表格提取测试
    try {
        Write-ColorOutput "执行表格提取测试..." $colors.info
        $testOutputFile = "$outputDir/pdf_extraction_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
        $testOutput = & python -m tests_real.run_table_extraction_test 2>&1
        $testOutput | Out-File -FilePath $testOutputFile -Encoding utf8
        
        # 解析测试结果
        $success = $true
        $failedTests = @()
        
        foreach ($line in $testOutput) {
            if ($line -match "测试失败") {
                $success = $false
                $failedTests += $line
                Write-ColorOutput $line $colors.error
            }
            elseif ($line -match "警告") {
                Write-ColorOutput $line $colors.warning
            }
            elseif ($line -match "测试通过|成功") {
                Write-ColorOutput $line $colors.success
            }
            else {
                Write-Host $line
            }
        }
        
        if ($success) {
            Write-ColorOutput "PDF表格提取测试通过" $colors.success
            $testResults += @{
                "name" = "PDF表格提取"
                "status" = "通过"
                "log" = $testOutputFile
            }
        }
        else {
            Write-ColorOutput "PDF表格提取测试失败" $colors.error
            $testResults += @{
                "name" = "PDF表格提取"
                "status" = "失败"
                "failures" = $failedTests
                "log" = $testOutputFile
            }
        }
    }
    catch {
        Write-ColorOutput "执行PDF表格提取测试时出错: $_" $colors.error
        $testResults += @{
            "name" = "PDF表格提取"
            "status" = "错误"
            "error" = $_.ToString()
        }
    }
}

# 测试问答系统功能
if ($TestQA) {
    Write-ColorOutput "`n===== 测试问答系统功能 =====" $colors.highlight
    
    # 执行问答系统测试
    try {
        Write-ColorOutput "执行问答系统测试..." $colors.info
        $testOutputFile = "$outputDir/qa_system_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
        $testOutput = & python -m tests_real.test_qa_evaluator_api --skip-api-test 2>&1
        $testOutput | Out-File -FilePath $testOutputFile -Encoding utf8
        
        # 解析测试结果
        $success = $true
        $failedTests = @()
        
        foreach ($line in $testOutput) {
            if ($line -match "测试失败") {
                $success = $false
                $failedTests += $line
                Write-ColorOutput $line $colors.error
            }
            elseif ($line -match "警告") {
                Write-ColorOutput $line $colors.warning
            }
            elseif ($line -match "测试完成|所有测试已完成") {
                Write-ColorOutput $line $colors.success
            }
            else {
                Write-Host $line
            }
        }
        
        if ($success) {
            Write-ColorOutput "问答系统测试通过" $colors.success
            $testResults += @{
                "name" = "问答系统"
                "status" = "通过"
                "log" = $testOutputFile
            }
        }
        else {
            Write-ColorOutput "问答系统测试失败" $colors.error
            $testResults += @{
                "name" = "问答系统"
                "status" = "失败"
                "failures" = $failedTests
                "log" = $testOutputFile
            }
        }
    }
    catch {
        Write-ColorOutput "执行问答系统测试时出错: $_" $colors.error
        $testResults += @{
            "name" = "问答系统"
            "status" = "错误"
            "error" = $_.ToString()
        }
    }
}

# 测试API功能
if ($TestAPI) {
    Write-ColorOutput "`n===== 测试API接口功能 =====" $colors.highlight
    
    # 检查API服务是否运行
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "API服务正在运行" $colors.success
            $apiRunning = $true
        }
        else {
            Write-ColorOutput "警告: API服务返回状态码 $($response.StatusCode)" $colors.warning
            $apiRunning = $false
        }
    }
    catch {
        Write-ColorOutput "警告: API服务未运行或无法访问" $colors.warning
        Write-ColorOutput "尝试启动API服务..." $colors.info
        
        # 尝试启动API服务
        Start-Process -FilePath "python" -ArgumentList "-m app.main" -WindowStyle Hidden
        
        # 等待API服务启动
        Write-ColorOutput "等待API服务启动..." $colors.info
        $apiRunning = $false
        for ($i = 1; $i -le 10; $i++) {
            Start-Sleep -Seconds 2
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    Write-ColorOutput "API服务已启动" $colors.success
                    $apiRunning = $true
                    break
                }
            }
            catch {
                Write-ColorOutput "尝试 $i/10: API服务尚未就绪" $colors.warning
            }
        }
        
        if (-not $apiRunning) {
            Write-ColorOutput "无法启动API服务，跳过API测试" $colors.error
            $testResults += @{
                "name" = "API接口"
                "status" = "跳过"
                "reason" = "无法启动API服务"
            }
        }
    }
    
    # 如果API服务正在运行，执行API测试
    if ($apiRunning) {
        try {
            Write-ColorOutput "执行API测试..." $colors.info
            $testOutputFile = "$outputDir/api_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
            $testOutput = & python -m app.test_api 2>&1
            $testOutput | Out-File -FilePath $testOutputFile -Encoding utf8
            
            # 解析测试结果
            $success = $true
            $failedTests = @()
            
            foreach ($line in $testOutput) {
                if ($line -match "失败|错误") {
                    $success = $false
                    $failedTests += $line
                    Write-ColorOutput $line $colors.error
                }
                elseif ($line -match "警告") {
                    Write-ColorOutput $line $colors.warning
                }
                elseif ($line -match "通过|成功") {
                    Write-ColorOutput $line $colors.success
                }
                else {
                    Write-Host $line
                }
            }
            
            if ($success) {
                Write-ColorOutput "API测试通过" $colors.success
                $testResults += @{
                    "name" = "API接口"
                    "status" = "通过"
                    "log" = $testOutputFile
                }
            }
            else {
                Write-ColorOutput "API测试失败" $colors.error
                $testResults += @{
                    "name" = "API接口"
                    "status" = "失败"
                    "failures" = $failedTests
                    "log" = $testOutputFile
                }
            }
        }
        catch {
            Write-ColorOutput "执行API测试时出错: $_" $colors.error
            $testResults += @{
                "name" = "API接口"
                "status" = "错误"
                "error" = $_.ToString()
            }
        }
    }
}

# 计算测试时间
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

# 生成测试报告
if ($GenerateReport) {
    Write-ColorOutput "`n===== 生成测试报告 =====" $colors.highlight
    
    $reportFile = "tests_real/系统自动化测试报告.md"
    $reportContent = @"
# 泰迪杯智能客服系统 - 自动化测试报告

## 测试信息
- **测试时间**: $($startTime.ToString("yyyy-MM-dd HH:mm:ss"))
- **测试耗时**: $([math]::Round($duration, 2)) 秒
- **Python版本**: $pythonVersion
- **测试环境**: PowerShell

## 测试结果摘要
"@
    
    # 添加测试结果摘要
    $passedTests = $testResults | Where-Object { $_.status -eq "通过" } | Measure-Object
    $failedTests = $testResults | Where-Object { $_.status -eq "失败" } | Measure-Object
    $errorTests = $testResults | Where-Object { $_.status -eq "错误" } | Measure-Object
    $skippedTests = $testResults | Where-Object { $_.status -eq "跳过" } | Measure-Object
    
    $reportContent += @"

- **通过**: $($passedTests.Count)
- **失败**: $($failedTests.Count)
- **错误**: $($errorTests.Count)
- **跳过**: $($skippedTests.Count)
- **总计**: $($testResults.Count)

## 详细测试结果
"@
    
    # 添加详细测试结果
    foreach ($result in $testResults) {
        $reportContent += @"

### $($result.name)
- **状态**: $($result.status)
"@
        
        if ($result.status -eq "失败") {
            $reportContent += @"

- **失败项**:
"@
            foreach ($failure in $result.failures) {
                $reportContent += @"
  - $failure
"@
            }
        }
        
        if ($result.status -eq "错误") {
            $reportContent += @"

- **错误信息**: $($result.error)
"@
        }
        
        if ($result.status -eq "跳过") {
            $reportContent += @"

- **跳过原因**: $($result.reason)
"@
        }
        
        if ($result.log) {
            $reportContent += @"

- **日志文件**: $($result.log)
"@
        }
    }
    
    # 添加系统状态信息
    $reportContent += @"

## 系统状态
"@
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $healthData = $response.Content | ConvertFrom-Json
            $reportContent += @"

- **API状态**: 正常
- **启动时间**: $($healthData.startup_time)
- **运行时间**: $($healthData.uptime_seconds) 秒
- **API版本**: $($healthData.api_version)

### 组件状态
"@
            
            foreach ($component in $healthData.components.PSObject.Properties) {
                $reportContent += @"

- **$($component.Name)**: $($component.Value.status)
"@
            }
        }
        else {
            $reportContent += @"

- **API状态**: 异常 (状态码: $($response.StatusCode))
"@
        }
    }
    catch {
        $reportContent += @"

- **API状态**: 离线
"@
    }
    
    # 添加建议
    $reportContent += @"

## 测试结论与建议
"@
    
    if ($passedTests.Count -eq $testResults.Count) {
        $reportContent += @"

所有测试均已通过，系统功能运行正常。
"@
    }
    else {
        $reportContent += @"

测试中发现一些问题，建议采取以下措施：
"@
        
        if ($failedTests.Count -gt 0) {
            $reportContent += @"

1. 修复失败的测试项，特别是关注:
"@
            
            $failedItems = $testResults | Where-Object { $_.status -eq "失败" }
            foreach ($item in $failedItems) {
                $reportContent += @"
   - $($item.name)
"@
            }
        }
        
        if ($errorTests.Count -gt 0) {
            $reportContent += @"

2. 检查测试过程中出现错误的组件:
"@
            
            $errorItems = $testResults | Where-Object { $_.status -eq "错误" }
            foreach ($item in $errorItems) {
                $reportContent += @"
   - $($item.name): $($item.error)
"@
            }
        }
    }
    
    # 写入报告文件
    $reportContent | Out-File -FilePath $reportFile -Encoding utf8
    Write-ColorOutput "测试报告已生成: $reportFile" $colors.success
    
    # 生成HTML报告
    $htmlFile = $reportFile -replace "\.md$", ".html"
    $htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>泰迪杯智能客服系统 - 自动化测试报告</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; }
        h1 { color: #1a73e8; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        h2 { color: #1a73e8; margin-top: 30px; }
        h3 { color: #1a73e8; }
        pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .passed { color: green; }
        .failed { color: red; }
        .error { color: darkred; }
        .skipped { color: orange; }
        .summary { display: flex; justify-content: space-between; background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .summary div { text-align: center; }
    </style>
</head>
<body>
    <div id="content">
    $($reportContent -replace '^# ', '<h1>' -replace '^## ', '<h2>' -replace '^### ', '<h3>' -replace '^\*\*(.*?)\*\*', '<strong>$1</strong>' -replace '\*\*(.*?)\*\*', '<strong>$1</strong>' -replace '\n\n', '<br><br>' -replace '\n- ', '<br>• ' -replace '- \*\*状态\*\*: 通过', '- <span class="passed"><strong>状态</strong>: 通过</span>' -replace '- \*\*状态\*\*: 失败', '- <span class="failed"><strong>状态</strong>: 失败</span>' -replace '- \*\*状态\*\*: 错误', '- <span class="error"><strong>状态</strong>: 错误</span>' -replace '- \*\*状态\*\*: 跳过', '- <span class="skipped"><strong>状态</strong>: 跳过</span>')
    </div>
</body>
</html>
"@
    
    $htmlContent | Out-File -FilePath $htmlFile -Encoding utf8
    Write-ColorOutput "HTML测试报告已生成: $htmlFile" $colors.success
}

# 清理临时文件
if ($CleanTemp) {
    Write-ColorOutput "`n===== 清理临时文件 =====" $colors.highlight
    
    # 清理__pycache__目录
    $pycacheDirs = Get-ChildItem -Path "." -Filter "__pycache__" -Recurse -Directory
    foreach ($dir in $pycacheDirs) {
        Remove-Item -Path $dir.FullName -Recurse -Force
        Write-ColorOutput "已删除: $($dir.FullName)" $colors.info
    }
    
    # 清理临时文件
    $tempFiles = Get-ChildItem -Path "tests_real/outputs" -Filter "*.tmp" -File
    foreach ($file in $tempFiles) {
        Remove-Item -Path $file.FullName -Force
        Write-ColorOutput "已删除: $($file.FullName)" $colors.info
    }
    
    Write-ColorOutput "临时文件清理完成" $colors.success
}

# 显示总结
Write-ColorOutput "`n===== 测试总结 =====" $colors.highlight
Write-ColorOutput "测试耗时: $([math]::Round($duration, 2)) 秒" $colors.info

$passedCount = ($testResults | Where-Object { $_.status -eq "通过" }).Count
$failedCount = ($testResults | Where-Object { $_.status -eq "失败" }).Count
$errorCount = ($testResults | Where-Object { $_.status -eq "错误" }).Count
$skippedCount = ($testResults | Where-Object { $_.status -eq "跳过" }).Count
$totalCount = $testResults.Count

Write-ColorOutput "通过: $passedCount/$totalCount" $colors.success
if ($failedCount -gt 0) {
    Write-ColorOutput "失败: $failedCount/$totalCount" $colors.error
}
if ($errorCount -gt 0) {
    Write-ColorOutput "错误: $errorCount/$totalCount" $colors.error
}
if ($skippedCount -gt 0) {
    Write-ColorOutput "跳过: $skippedCount/$totalCount" $colors.warning
}

if ($passedCount -eq $totalCount) {
    Write-ColorOutput "测试结果: 所有测试通过" $colors.success
}
else {
    Write-ColorOutput "测试结果: 存在失败或错误" $colors.error
    Write-ColorOutput "请检查测试日志获取详细信息" $colors.info
    if ($GenerateReport) {
        Write-ColorOutput "详细报告: tests_real/系统自动化测试报告.md" $colors.info
    }
}

Write-ColorOutput "`n测试脚本执行完成。" $colors.highlight 