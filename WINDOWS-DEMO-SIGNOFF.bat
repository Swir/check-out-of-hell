@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title CHECKOUT OF HELL - Windows Demo Sign-off
echo ============================================================
echo       CHECKOUT OF HELL - TARGET WINDOWS SIGN-OFF
echo ============================================================
echo.
echo This developer tool builds and validates the exact non-public
echo release-candidate package, then guides the remaining manual checks.
echo It does NOT publish a demo or mark a release ready by itself.
echo.

where powershell.exe >nul 2>&1
if errorlevel 1 (
    echo Windows PowerShell was not found. This sign-off tool requires a supported Windows installation.
    echo.
    pause
    exit /b 10
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\windows_demo_signoff.ps1"
set "COH_EXIT=%ERRORLEVEL%"

echo.
if "%COH_EXIT%"=="0" (
    echo Sign-off tool finished. Review the evidence path printed above.
) else (
    echo Sign-off tool did not produce a PASS result. Review the evidence and errors above.
)
echo.
pause
exit /b %COH_EXIT%
