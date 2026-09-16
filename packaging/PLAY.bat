@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================================
echo              CHECKOUT OF HELL - PORTABLE DEV BUILD
echo ============================================================
echo.

echo [1/2] Preparing legal runtime dependencies...
powershell -NoProfile -ExecutionPolicy Bypass -File "tools\bootstrap_runtime.ps1"
if errorlevel 1 goto :failed

set "PK3=%CD%\dist\checkout-of-hell-prototype.pk3"
if not exist "%CD%\external\gzdoom\gzdoom.exe" goto :failed
if not exist "%CD%\external\freedoom2.wad" goto :failed
if not exist "%PK3%" goto :missing_game

echo [2/2] Starting CHECKOUT OF HELL...
start "CHECKOUT OF HELL" "%CD%\external\gzdoom\gzdoom.exe" -iwad "%CD%\external\freedoom2.wad" -file "%PK3%" +map MAP01
exit /b 0

:missing_game
echo.
echo The prebuilt CHECKOUT OF HELL PK3 is missing from this package.
echo Re-download the official project artifact instead of searching for random game files.
echo.
pause
exit /b 1

:failed
echo.
echo CHECKOUT OF HELL could not start.
echo Required runtime files are downloaded only from the official pinned upstream releases.
echo Check your internet connection and the error above, then run PLAY.bat again.
echo.
pause
exit /b 1
