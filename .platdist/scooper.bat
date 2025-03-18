@echo off
echo Running scooper.bat...

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    :: If running as administrator, restart without administrator privileges
    echo This script should not be run as administrator. Restarting without elevated privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -ArgumentList '%*' -NoNewWindow"
    exit /b
)

:: Add Scoop to PATH for this session
set "SCOOP=C:\Users\DEV\AppData\Local\Programs\Scoop\bin"
set PATH=%PATH%;%SCOOP%
echo PATH after adding Scoop: %PATH%

:: Check if Scoop is installed
where scoop > nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Scoop is already installed.
    echo Proceeding to invoke PowerShell script...
) ELSE (
    echo Scoop is not installed. Attempting to install Scoop...
    powershell -Command "Set-ExecutionPolicy RemoteSigned -scope CurrentUser -Force"
    powershell -Command "iwr -useb get.scoop.sh | iex"

    :: Check again if Scoop is installed after installation
    where scoop > nul 2>&1
    IF %ERRORLEVEL% EQU 0 (
        echo Scoop successfully installed and added to PATH.
        echo Proceeding to invoke PowerShell script...
    ) ELSE (
        echo Failed to install Scoop. Exiting script.
        exit /b 1
    )
)

:: Invoke the PowerShell script with specific arguments
echo.
echo Invoking scoop.ps1 script with execution policy bypass...
cd /d "%~dp0"
timeout /t 1 >nul
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "scoop.ps1"
set PS1_ERROR=%ERRORLEVEL%

IF %PS1_ERROR% NEQ 0 (
    echo PowerShell script execution failed with error code %PS1_ERROR%
    exit /b %PS1_ERROR%
)

echo.
echo Initialization completed successfully.
exit /b 0