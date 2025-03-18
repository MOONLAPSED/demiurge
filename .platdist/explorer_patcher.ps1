# Script to install ExplorerPatcher
# Author: MOONLAPSED
# Last Updated: 2025-03-15

# Log start time and user with specific format
$currentUtcTime = [DateTime]::UtcNow.ToString("yyyy-MM-dd HH:mm:ss")
Write-Output "Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): $currentUtcTime"
Write-Output "Current User's Login: $env:USERNAME"

# Ensure we stop on any error
$ErrorActionPreference = 'Stop'

# Function to check if running as administrator
function Test-AdminPrivileges {
    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object System.Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to verify file hash (when available)
function Test-FileHash {
    param (
        [string]$FilePath,
        [string]$ExpectedHash  # Could be added in the future if EP provides consistent hashes
    )
    try {
        $hash = Get-FileHash -Path $FilePath -Algorithm SHA256
        Write-Output "File hash: $($hash.Hash)"
        return $true  # For now, just return true as we're only logging the hash
    } catch {
        Write-Warning "Could not verify file hash: $_"
        return $false
    }
}

# Function to check Windows version compatibility
function Test-WindowsCompatibility {
    $osInfo = Get-WmiObject -Class Win32_OperatingSystem
    $windowsVersion = [System.Version]($osInfo.Version)
    
    # Check if Windows 11 (Windows 10 build 22000 or higher)
    if ($windowsVersion.Build -ge 22000) {
        return $true
    } else {
        Write-Warning "ExplorerPatcher is designed for Windows 11 (build 22000+). Current build: $($windowsVersion.Build)"
        return $false
    }
}

try {
    # Check for admin privileges
    if (-not (Test-AdminPrivileges)) {
        throw "This script requires administrator privileges. Please run as administrator."
    }

    # Check Windows compatibility
    if (-not (Test-WindowsCompatibility)) {
        throw "Unsupported Windows version. ExplorerPatcher requires Windows 11."
    }

    # Define the URL for the latest release of ExplorerPatcher
    $url = "https://github.com/valinet/ExplorerPatcher/releases/latest/download/ep_setup.exe"
    
    # Define the path where the installer will be saved
    $output = Join-Path $env:TEMP "ep_setup.exe"

    # Ensure temp directory exists
    if (-not (Test-Path $env:TEMP)) {
        New-Item -ItemType Directory -Path $env:TEMP -Force | Out-Null
    }

    # Download the installer with progress bar
    Write-Output "Downloading ExplorerPatcher..."
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($url, $output)

    # Verify download
    if (Test-Path $output) {
        # Verify file hash (logging only for now)
        Test-FileHash -FilePath $output

        Write-Output "Download complete. Installing ExplorerPatcher..."

        # Run the installer with error handling
        $process = Start-Process -FilePath $output -ArgumentList "/silent" -NoNewWindow -Wait -PassThru

        # Check process exit code
        if ($process.ExitCode -eq 0) {
            Write-Output "ExplorerPatcher installation completed successfully."
            
            # Check if the main DLL exists (basic installation verification)
            $epDll = "$env:SystemRoot\dxgi.dll"
            if (Test-Path $epDll) {
                Write-Output "Installation verified: ExplorerPatcher files found."
            } else {
                Write-Warning "Installation might be incomplete: Could not find ExplorerPatcher files."
            }
        } else {
            throw "Installation failed with exit code: $($process.ExitCode)"
        }

        # Clean up
        if (Test-Path $output) {
            Write-Output "Cleaning up temporary files..."
            Remove-Item -Path $output -Force -ErrorAction SilentlyContinue
        }

        # Notify user about potential restart requirement
        Write-Output "`nNote: You may need to restart Explorer or your computer for changes to take effect."
        Write-Output "To restart Explorer: taskkill /f /im explorer.exe & start explorer.exe"
    } else {
        throw "Download failed: Installer file not found."
    }
} catch {
    Write-Error "An error occurred: $_"
    exit 1
} finally {
    # Ensure cleanup even if script fails
    if (Test-Path $output) {
        Remove-Item -Path $output -Force -ErrorAction SilentlyContinue
    }
}