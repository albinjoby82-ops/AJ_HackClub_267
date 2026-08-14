@echo off
REM ============================================================
REM  ARDUINO ARCADE - one-click setup for Windows
REM  Creates .venv, installs dependencies, checks the install.
REM ============================================================
setlocal
cd /d "%~dp0"

echo.
echo   ARDUINO ARCADE - SETUP
echo   ======================
echo.

REM --- 1. find Python -----------------------------------------
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
    where python >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo [ERROR] Python was not found on this PC.
    echo.
    echo   Install Python 3.11 or newer from https://www.python.org/downloads/
    echo   IMPORTANT: tick "Add python.exe to PATH" in the installer.
    echo   Then run setup.bat again.
    echo.
    pause
    exit /b 1
)

%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)"
if errorlevel 1 (
    echo [ERROR] Python 3.9 or newer is required.
    %PY% --version
    pause
    exit /b 1
)
echo   [1/3] Python found:
%PY% --version

REM --- 2. virtual environment ---------------------------------
if exist ".venv\Scripts\python.exe" (
    echo   [2/3] Using existing virtual environment .venv
) else (
    echo   [2/3] Creating virtual environment .venv ...
    %PY% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Could not create the virtual environment.
        echo         Try running this window as Administrator, or check disk space.
        pause
        exit /b 1
    )
)

REM --- 3. dependencies ----------------------------------------
echo   [3/3] Installing dependencies ^(pygame, pyserial, pytest^) ...
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Dependency installation failed.
    echo         Check your internet connection, then run setup.bat again.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -c "import pygame, serial; print('   verified pygame', pygame.version.ver, '/ pyserial', serial.__version__)"
if errorlevel 1 (
    echo [ERROR] Dependencies installed but could not be imported.
    pause
    exit /b 1
)

echo.
echo   SETUP COMPLETE.
echo.
echo   NEXT STEPS
echo     1. Upload arduino\arcade_controller\arcade_controller.ino to the Arduino.
echo     2. CLOSE the Arduino IDE Serial Monitor ^(it holds the COM port^).
echo     3. Double-click run_arcade.bat to play.
echo.
echo   No Arduino yet?  run_arcade.bat still works - choose PLAY WITHOUT ARDUINO,
echo   or run:  run_arcade.bat --keyboard
echo.
pause
