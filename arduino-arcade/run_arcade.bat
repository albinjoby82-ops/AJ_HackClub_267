@echo off
REM ============================================================
REM  ARDUINO ARCADE - launcher
REM  Any arguments are passed straight through, e.g.
REM     run_arcade.bat --keyboard
REM     run_arcade.bat --event
REM     run_arcade.bat --port COM5
REM ============================================================
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv not found - run setup.bat first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" main.py %*
if errorlevel 1 (
    echo.
    echo [ERROR] Arduino Arcade exited with an error ^(see the message above^).
    echo         If it mentions the COM port, close the Arduino Serial Monitor and retry.
    pause
    exit /b 1
)
