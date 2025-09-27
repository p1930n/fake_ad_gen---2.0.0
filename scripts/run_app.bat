@echo off
echo ====================================================
echo           启动批量文件处理系统
echo ====================================================
echo.

:: 检查虚拟环境
if exist "fake_ad_env" (
    echo [激活] 激活虚拟环境...
    call fake_ad_env\Scripts\activate.bat
    echo.
    echo [启动] 运行主程序...
    python main_menu.py
) else (
    echo [错误] 虚拟环境不存在！
    echo [提示] 请先运行 setup_env.bat 创建环境
    echo.
    pause
) 