@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================================
echo      CHECKOUT OF HELL - WINDOWS DEMO SIGN-OFF ASSISTANT
echo ============================================================
echo.
echo This helper prepares the pinned legal runtime, launches MAP01 with

echo an isolated config, then records a manual evidence report.
echo It does NOT publish a release or auto-approve the demo.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "tools\windows_playtest_assistant.ps1"
if errorlevel 1 goto :failed
exit /b 0

:failed
echo.
echo The playtest assistant could not complete.
echo Read the error above, fix the reported prerequisite, and run this file again.
echo.
pause
exit /b 1
