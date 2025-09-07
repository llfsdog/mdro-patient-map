@echo off
chcp 65001 >nul
title MDRO患者分布地图启动器

echo ========================================
echo    MDRO患者分布地图启动器
echo ========================================
echo.
echo 正在检查Python环境...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未检测到Python环境
    echo.
    echo 请先安装Python：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装Python
    echo 3. 安装时勾选"Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo Python环境检测正常
echo.
echo 正在启动HTTP服务器...
echo 服务器地址：http://localhost:8000
echo.
echo 提示：服务器启动后，浏览器会自动打开地图页面
echo 如需停止服务器，请按 Ctrl+C
echo.

start "" "http://localhost:8000"
python -m http.server 8000

echo.
echo 服务器已停止
pause
