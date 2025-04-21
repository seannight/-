param(
    [string]$mode = "update"  # update, test, demo
)

if ($mode -eq "update") {
    # 从BC成员获取代码更新
    Write-Host "从shared_code同步代码..." -ForegroundColor Green
    if (Test-Path "shared_code/data_processing") {
        Copy-Item -Path "shared_code/data_processing/*" -Destination "app/data_processing/" -Recurse -Force
        Write-Host "已更新B成员代码" -ForegroundColor Green
    }
    if (Test-Path "shared_code/models") {
        Copy-Item -Path "shared_code/models/*" -Destination "app/models/" -Recurse -Force
        Write-Host "已更新C成员代码" -ForegroundColor Green
    }
}
elseif ($mode -eq "test") {
    # 运行测试
    Write-Host "测试核心功能..." -ForegroundColor Yellow
    python -m app.data_processing.pdf_parser
    python -m app.models.qa_engine
    Write-Host "测试完成" -ForegroundColor Green
}
elseif ($mode -eq "demo") {
    # 启动演示
    Write-Host "启动演示..." -ForegroundColor Cyan
    python -m demo.run_demo
}