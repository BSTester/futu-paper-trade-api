@echo off
chcp 65001 >nul
echo ========================================
echo Futu Paper Trade API - Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Please install Python: https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python installed
python --version
echo.

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [OK] Dependencies installed
echo.

REM Create .env file
if not exist .env (
    echo [INFO] Creating .env file...
    copy .env.example .env >nul
    echo [OK] .env file created
    echo.
    echo [IMPORTANT] Please edit .env file and fill in:
    echo    1. FUTU_COOKIE - Your Futu Cookie
    echo    2. ACCOUNT_ID_US/HK/CN - Your account IDs
    echo.
    echo How to get Cookie:
    echo    1. Visit https://www.futunn.com/paper-trade
    echo    2. Login to your Futu account
    echo    3. Press F12 to open Developer Tools
    echo    4. Go to Network tab
    echo    5. Refresh page and find any request
    echo    6. Copy Cookie value from request headers
    echo.
    echo How to get Account IDs:
    echo    1. Configure Cookie in .env first
    echo    2. Run: python -c "from futu_client import FutuClient; import asyncio; asyncio.run(FutuClient().get_account_list())"
    echo.
) else (
    echo [INFO] .env file already exists, skipping
)

echo ========================================
echo [OK] Setup completed!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Run start.bat to start the service
echo 3. Visit http://localhost:8000/docs for API documentation
echo.
pause
