@echo off
REM 表格提取演示启动脚本
REM 泰迪杯智能客服系统 - PDF表格提取演示程序

echo === 泰迪杯智能客服系统 - PDF表格提取演示 ===
echo 正在准备启动演示环境...

REM 设置Python环境
set PYTHONPATH=%~dp0..
set PYTHONIOENCODING=utf-8

REM 创建必要的目录
if not exist "temp" mkdir temp
if not exist "data\processed" mkdir data\processed

REM 清理Excel锁文件（如果有）
python -c "from app.data_processing.extract_tables import cleanup_excel_locks; cleanup_excel_locks('data/processed', auto_remove=True)" 2>nul

REM 启动演示服务器
echo 正在启动演示服务器，请等待...
echo 服务启动后，请访问 http://localhost:8000 查看演示
python demo/dashboard/table_demo.py

echo 演示服务已停止运行。
pause 