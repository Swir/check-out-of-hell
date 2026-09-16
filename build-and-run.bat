@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found in PATH.
    pause
    exit /b 1
)

python tools\build.py
if errorlevel 1 (
    pause
    exit /b 1
)

python tools\smoke_test.py
if errorlevel 1 (
    pause
    exit /b 1
)

if not exist "external\gzdoom.exe" (
    echo.
    echo Missing external\gzdoom.exe
    echo Put GZDoom in the external folder.
    pause
    exit /b 1
)

if not exist "external\freedoom2.wad" (
    echo.
    echo Missing external\freedoom2.wad
    echo Put Freedoom Phase 2 WAD in the external folder.
    pause
    exit /b 1
)

start "" "external\gzdoom.exe" -iwad "external\freedoom2.wad" -file "dist\checkout-of-hell-prototype.pk3" +map MAP01
