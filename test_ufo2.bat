@echo off
echo === UFO2 Integration Test ===
echo.

REM Set environment variables
set GEMINI_API_KEY=AIzaSyBC4m0pBy8t6D1Q0OAdzPGJ0m8ZAdXr7o0
set GOOGLE_API_KEY=AIzaSyBC4m0pBy8t6D1Q0OAdzPGJ0m8ZAdXr7o0
set PYTHONIOENCODING=utf-8

echo Step 1: Testing Python installation...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

echo.
echo Step 2: Testing Gemini API...
python test_gemini.py

echo.
echo Step 3: Testing UFO2 connection...
python test_ufo2_connection.py

echo.
echo === Test Complete ===
echo.
echo If all tests passed, UFO2 should work in TabletGPT.
echo If not, please run install_gemini.bat first.
pause