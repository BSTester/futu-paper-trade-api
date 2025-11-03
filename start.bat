@echo off
chcp 65001 >nul
echo ========================================
echo Futu Paper Trade API Service
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Please install Python: https://www.python.org/
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found
    echo.
    echo Please follow these steps:
    echo 1. Copy .env.example to .env
    echo 2. Edit .env file and fill in your Cookie and Account IDs
    echo.
    echo How to get Cookie:
    echo 1. Visit https://www.futunn.com/paper-trade
    echo 2. Login to your Futu account
    echo 3. Press F12 to open Developer Tools
    echo 4. Find Cookie in Network tab request headers
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo [INFO] Checking dependencies...
pip show httpx >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo [OK] Environment check completed
echo.
echo [START] Starting API service...
echo.
echo Service URL: http://localhost:9000
echo API Docs: http://localhost:9000/docs
echo.
echo Press Ctrl+C to stop the service
echo ========================================
echo.

python main.py

pause
