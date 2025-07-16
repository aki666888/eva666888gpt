@echo off

echo ============================================
echo    TabletGPT - Pharmacy Automation System
echo ============================================
echo.

cd /d "%~dp0"

:: Kill any existing processes on port 5000
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :5000') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: Open browser after delay
start /b cmd /c "timeout /t 3 >nul && start http://127.0.0.1:5000"

:: Start the server
python main.py

pause