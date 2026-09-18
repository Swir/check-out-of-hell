@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title CHECKOUT OF HELL
echo ============================================================
echo        CHECKOUT OF HELL - WINDOWS PORTABLE CANDIDATE
echo ============================================================
echo.
echo This CI package is a release candidate, not a public demo.
echo.

where powershell.exe >nul 2>&1
if errorlevel 1 goto :missing_powershell

echo [1/3] Verifying packaged game files and bundled Freedoom content...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "tools\verify_player_package.ps1"
if errorlevel 1 goto :integrity_failed

echo.
echo [2/3] Preparing pinned GZDoom runtime...
echo Verified Freedoom base content is bundled; GZDoom comes only from its official upstream release.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "tools\bootstrap_runtime.ps1"
if errorlevel 1 goto :runtime_failed

set "GAME=%CD%\game\CHECKOUT-OF-HELL.pk3"
set "GZDOOM=%CD%\external\gzdoom\gzdoom.exe"
set "FREEDOOM=%CD%\external\freedoom2.wad"

if not exist "%GAME%" goto :integrity_failed
if not exist "%GZDOOM%" goto :runtime_failed
if not exist "%FREEDOOM%" goto :integrity_failed

echo.
echo [3/3] Clocking in...
start "CHECKOUT OF HELL" "%GZDOOM%" -iwad "%FREEDOOM%" -file "%GAME%" +map MAP01
if errorlevel 1 goto :launch_failed
exit /b 0

:missing_powershell
echo.
echo Windows PowerShell is required for the verified one-click setup but was not found.
echo Use a supported Windows installation with Windows PowerShell available.
echo Do not download random replacement launchers or runtime files.
echo.
pause
exit /b 10

:integrity_failed
echo.
echo Package integrity verification failed.
echo Re-extract the ZIP first. If it still fails, re-download the official project artifact.
echo Do not replace missing files from unofficial mirrors.
echo.
pause
exit /b 20

:runtime_failed
echo.
echo The pinned GZDoom engine could not be prepared.
echo CHECKOUT OF HELL resolves GZDoom only from its official upstream release.
echo The bundled Freedoom content is verified before bootstrap and does not need a separate download.
echo Check your internet connection on first launch and the error above, then run PLAY.bat again.
echo Existing verified GZDoom files are reused on later launches.
echo.
pause
exit /b 30

:launch_failed
echo.
echo GZDoom was prepared but the game process could not be started.
echo Re-run PLAY.bat and review any Windows security or filesystem error shown above.
echo.
pause
exit /b 40
