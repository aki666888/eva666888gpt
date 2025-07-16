@echo off
echo === Installing Google Generative AI Package for UFO2 ===
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Installing google-generativeai package...
python -m pip install google-generativeai

echo.
echo === Installation Complete ===
echo.
echo Please restart TabletGPT for changes to take effect.
pause