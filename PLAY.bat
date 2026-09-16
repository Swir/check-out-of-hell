@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================================
echo              CHECKOUT OF HELL - ONE CLICK PLAY
echo ============================================================
echo.

echo [1/4] Preparing legal runtime dependencies...
powershell -NoProfile -ExecutionPolicy Bypass -File "tools\bootstrap_runtime.ps1"
if errorlevel 1 goto :failed

set "PK3=%CD%\dist\checkout-of-hell-prototype.pk3"
set "PYTHON_EXE="

if not exist "%PK3%" (
    echo [2/4] Game package is not built yet. Preparing build runtime...
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON_EXE=python"

    if not defined PYTHON_EXE (
        powershell -NoProfile -ExecutionPolicy Bypass -File "tools\bootstrap_python.ps1"
        if errorlevel 1 goto :failed
        set "PYTHON_EXE=%CD%\tools\runtime\python\python.exe"
    )

    echo [3/4] Building game package...
    "%PYTHON_EXE%" tools\build.py
    if errorlevel 1 goto :failed

    "%PYTHON_EXE%" tools\smoke_test.py
    if errorlevel 1 goto :failed
) else (
    echo [2/4] Prebuilt game package found.
    echo [3/4] Build step not required.
)

if not exist "%CD%\external\gzdoom\gzdoom.exe" goto :failed
if not exist "%CD%\external\freedoom2.wad" goto :failed
if not exist "%PK3%" goto :failed

echo [4/4] Starting CHECKOUT OF HELL...
start "CHECKOUT OF HELL" "%CD%\external\gzdoom\gzdoom.exe" -iwad "%CD%\external\freedoom2.wad" -file "%PK3%" +map MAP01
exit /b 0

:failed
echo.
echo CHECKOUT OF HELL could not start.
echo The setup only uses official upstream sources. Check your internet connection
echo and the error above, then run PLAY.bat again.
echo.
pause
exit /b 1
