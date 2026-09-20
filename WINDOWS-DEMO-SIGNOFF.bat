@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title CHECKOUT OF HELL - Windows Demo Sign-off
echo ============================================================
echo       CHECKOUT OF HELL - TARGET WINDOWS SIGN-OFF
echo ============================================================
echo.
echo This developer tool builds and validates the exact non-public
echo release-candidate package, guides the required human checks,
echo records the explicit Closing Time polish review and verifies
echo the final evidence against the exact clean commit.
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
if not "%COH_EXIT%"=="0" goto :done

echo.
echo Base gameplay, controller and hardware sign-off passed.
echo Running the explicit Closing Time polish review...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\closing_time_polish_review.ps1" -EvidenceRoot "%~dp0dist\windows-demo-signoff"
set "COH_EXIT=%ERRORLEVEL%"
if not "%COH_EXIT%"=="0" goto :done

echo.
echo Explicit polish review passed. Independently verifying the newest evidence...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\verify_latest_windows_signoff.ps1" -EvidenceRoot "%~dp0dist\windows-demo-signoff"
set "COH_EXIT=%ERRORLEVEL%"

:done
echo.
if "%COH_EXIT%"=="0" (
    echo Complete target-Windows gameplay, polish and evidence chain: PASS.
    echo This still does NOT publish or authorize a public demo.
) else (
    echo Sign-off did not produce a fully verified PASS. Review the evidence and errors above.
    echo No release should be published from this result.
)
echo.
pause
exit /b %COH_EXIT%
