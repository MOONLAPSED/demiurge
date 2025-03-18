@echo off
echo Running Explorer Patcher installation script...

:: Get current UTC time in YYYY-MM-DD HH:MM:SS format
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set YYYY=%datetime:~0,4%
set MM=%datetime:~4,2%
set DD=%datetime:~6,2%
set HH=%datetime:~8,2%
set MIN=%datetime:~10,2%
set SS=%datetime:~12,2%

echo Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): %YYYY%-%MM%-%DD% %HH%:%MIN%:%SS%
echo Current User's Login: %USERNAME%

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    :: We are running as admin, which is what we want for EP
    echo Running with administrator privileges...
) else (
    :: If not running as administrator, restart with administrator privileges
    echo Requesting administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: Change to the script's directory
cd /d "%~dp0"

:: Invoke the PowerShell script with appropriate parameters
echo Invoking explorer_patcher.ps1 script...
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0explorer_patcher.ps1"

IF %ERRORLEVEL% NEQ 0 (
    echo There was an error executing the PowerShell script.
    echo Error code: %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo Installation process completed.
echo Note: You may need to restart Explorer or your computer for changes to take effect.
pause