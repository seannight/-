# 泰迪杯智能客服系统 - 问答质量评估系统测试脚本
# 适用于Windows系统，PowerShell执行

# 清屏
Clear-Host

Write-Host "泰迪杯智能客服系统 - 问答质量评估系统测试" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 设置环境变量
$Env:TEST_KNOWLEDGE_DIR = "tests_real/data/knowledge"
$Env:PYTHONPATH = "."

# 检查Python环境
$pythonVersion = python --version
Write-Host "Python版本: $pythonVersion" -ForegroundColor Green

# 检查必要模块
Write-Host "`n检查必要模块..." -ForegroundColor Yellow
$modules = @("jieba", "scikit-learn", "fastapi", "uvicorn")
foreach ($module in $modules) {
    $installed = python -c "import $module; print('$module 已安装')" 2>$null
    if ($installed) {
        Write-Host "✅ $installed" -ForegroundColor Green
    } else {
        Write-Host "❌ $module 未安装 - 正在安装..." -ForegroundColor Red
        pip install $module
    }
}

# 运行测试
Write-Host "`n[1/3] 运行集成测试..." -ForegroundColor Yellow
python -m tests_real.test_qa_integration

# 生成测试报告
Write-Host "`n[2/3] 查看测试报告..." -ForegroundColor Yellow
if (Test-Path "tests_real/C成员第四周任务测试报告.md") {
    Write-Host "测试报告已生成: tests_real/C成员第四周任务测试报告.md" -ForegroundColor Green
} else {
    Write-Host "测试报告不存在!" -ForegroundColor Red
}

# 启动演示服务器
Write-Host "`n[3/3] 启动演示API服务器..." -ForegroundColor Yellow
Write-Host "按Ctrl+C停止服务器`n" -ForegroundColor Yellow

# 检查是否要启动服务器
$startServer = Read-Host "是否启动API服务器查看评估功能? (y/n)"
if ($startServer -eq "y") {
    uvicorn app.main:app --reload --port 8000
} else {
    Write-Host "测试完成，未启动服务器。" -ForegroundColor Green
} 