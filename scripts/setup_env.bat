@echo off
echo ====================================================
echo           Python虚拟环境设置脚本
echo ====================================================
echo.

:: 检查虚拟环境是否存在
if exist "fake_ad_env" (
    echo [信息] 虚拟环境已存在
) else (
    echo [创建] 正在创建虚拟环境...
    python -m venv fake_ad_env
    echo [完成] 虚拟环境创建成功
)

echo.
echo [激活] 激活虚拟环境...
call fake_ad_env\Scripts\activate.bat

echo.
echo [安装] 安装项目依赖...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ====================================================
echo           环境设置完成！
echo ====================================================
echo.
echo 虚拟环境已激活，现在您可以：
echo   1. 运行主程序: python main_menu.py
echo   2. 退出环境: deactivate
echo   3. 重新激活: fake_ad_env\Scripts\activate.bat
echo.
echo 当前Python路径: 
where python
echo.
echo 已安装的包:
pip list
echo.
pause 