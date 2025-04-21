@echo off
rem ===== 泰迪杯智能客服系统简易启动脚本 =====
rem 版本: 1.0.0
rem 提供最简单的一键启动方式

echo ===== 泰迪杯智能客服系统简易启动脚本 =====
echo 版本: 1.0.0
echo =======================================
echo.

rem 解析简单参数
set PORT=8000
set OPEN_BROWSER=0

if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="-p" set PORT=%2
if "%1"=="--port" set PORT=%2
if "%1"=="-o" set OPEN_BROWSER=1
if "%1"=="--open" set OPEN_BROWSER=1

rem 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请安装Python 3.9+
    pause
    exit /b 1
)

rem 检查必要文件
if not exist app\main.py (
    echo [错误] 未找到app\main.py文件，请确保您在正确的目录中运行此脚本
    pause
    exit /b 1
)

rem 创建必要的目录
if not exist logs mkdir logs
if not exist data\processed mkdir data\processed

rem 设置环境变量
set PYTHONPATH=%cd%
set FASTSTART=1
set UI_PRIORITY=1
set API_PORT=%PORT%

echo.
echo 启动服务器，配置如下:
echo - 端口: %PORT%
echo - 快速启动模式: 已启用
echo - UI优先模式: 已启用
echo.

echo 服务器启动后，可通过以下地址访问:
echo - 演示界面: http://localhost:%PORT%/dashboard
echo - API文档: http://localhost:%PORT%/docs
echo.

echo 正在启动服务，请稍候...
echo 请使用Ctrl+C停止服务
echo.

rem 启动服务
python -m app.main --port %PORT% --fast --ui-priority

rem 如果需要打开浏览器
if %OPEN_BROWSER%==1 (
    timeout /t 3 >nul
    start http://localhost:%PORT%/dashboard
)

goto :end

:show_help
echo 使用方法: run_easy.bat [选项]
echo 选项:
echo   -h, --help     显示帮助信息
echo   -p, --port N   设置服务器端口 (默认: 8000)
echo   -o, --open     启动后自动打开浏览器
echo.
echo 示例:
echo   run_easy.bat               使用默认配置启动
echo   run_easy.bat -p 8080       在端口8080上启动
echo   run_easy.bat -o            启动并自动打开浏览器
echo.

:end
pause 