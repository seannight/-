@echo off
:: 安装psutil的批处理文件
:: 用于解决可能存在的编码和空字符问题

echo ===================================
echo  泰迪杯 - 修复版psutil安装工具
echo ===================================
echo.

:: 设置编码为UTF-8
chcp 65001 >nul

echo 正在检查Python环境...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 找不到Python，请确保已安装Python并添加到PATH中
    goto :end
)

echo.
echo 正在尝试安装psutil...
python -m pip install psutil

if %ERRORLEVEL% equ 0 (
    echo.
    echo 安装成功完成!
) else (
    echo.
    echo 安装失败，尝试使用镜像源...
    python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple psutil
    
    if %ERRORLEVEL% equ 0 (
        echo.
        echo 使用镜像源安装成功!
    ) else (
        echo.
        echo 安装仍然失败，建议手动安装或检查网络连接
    )
)

:end
echo.
echo 按任意键退出...
pause >nul 