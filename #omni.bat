@echo off
REM ================================================
REM OmniParser V2 Quick Launcher
REM ================================================
REM This file starts with # to protect it from deletion
REM Quickly launches the OmniParser server
REM ================================================

title OmniParser V2 Server

echo ================================================
echo          OmniParser V2 Server Launcher
echo ================================================
echo.

REM Check if standalone_omniparser.py exists
if not exist "%~dp0#standalone_omniparser.py" (
    echo ERROR: #standalone_omniparser.py not found!
    echo Please ensure #standalone_omniparser.py is in the same directory
    pause
    exit /b 1
)

echo Starting OmniParser server...
echo Using OmniParser from: D:\omni\omni
echo.

REM Set PYTHONPATH to include the OmniParser directory
set PYTHONPATH=D:\omni\omni;%PYTHONPATH%

echo The server will show its output below:
echo ------------------------------------------------

REM Run OmniParser server with output visible
python -u "%~dp0#standalone_omniparser.py"

echo.
echo ------------------------------------------------
echo OmniParser server has stopped.
echo.
pause