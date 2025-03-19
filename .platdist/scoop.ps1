Write-Host "Starting scoop.ps1 script..."

# Function to safely add a bucket
function Add-ScoopBucket {
    param([string]$bucketName, [string]$repoUrl = "")
    
    Write-Host "Checking bucket: $bucketName"
    $buckets = scoop bucket list
    if ($buckets -match $bucketName) {
        Write-Host "Bucket '$bucketName' is already added."
    } else {
        Write-Host "Adding bucket: $bucketName"
        if ($repoUrl) {
            scoop bucket add $bucketName $repoUrl
        } else {
            scoop bucket add $bucketName
        }
    }
}

# Function to safely install a package
function Install-ScoopPackage {
    param([string]$packageName, [string]$bucket = "")
    
    $fullPackageName = if ($bucket) { "$bucket/$packageName" } else { $packageName }
    Write-Host "Checking package: $fullPackageName"
    
    $installed = scoop list | Where-Object { $_.Name -eq $packageName }
    if ($installed) {
        Write-Host "Package '$fullPackageName' is already installed."
        return $true
    } else {
        Write-Host "Installing package: $fullPackageName"
        scoop install $fullPackageName
        return $?  # Return success status of installation
    }
}

# Function to set Windows Terminal Preview as default
function Set-WindowsTerminalPreviewAsDefault {
    try {
        # Get the Windows Terminal Preview package path
        $wtPreviewPath = Join-Path $env:USERPROFILE "AppData\Local\Programs\Scoop\bin\apps\windows-terminal-preview\current"
        if (Test-Path $wtPreviewPath) {
            # Import the context menu registry entries
            $regFile = Join-Path $wtPreviewPath "install-context.reg"
            if (Test-Path $regFile) {
                Write-Host "Setting up Windows Terminal Preview context menu..."
                reg import $regFile
            }

            # Set as default terminal (Windows 11 22H2 or later)
            if (Get-Command "windows-terminal-preview" -ErrorAction SilentlyContinue) {
                Write-Host "Attempting to set Windows Terminal Preview as default..."
                Start-Process "windows-terminal-preview" -ArgumentList "--default-terminal" -Wait
            }
        }
    } catch {
        Write-Host ("Error setting Windows Terminal Preview as default: {0}" -f $_.Exception.Message)
    }
}

# First, ensure git is installed (required for adding buckets)
Install-ScoopPackage "git"

# Add required buckets
Add-ScoopBucket "versions"
Add-ScoopBucket "extras"
Add-ScoopBucket "nerd-fonts"

Write-Host "Installing essential packages..."
# Install packages with error handling
$packages = @(
    @{name="gh"; bucket="main"},
    @{name="vscode-insiders"; bucket="versions"},
    @{name="windows-terminal-preview"; bucket="versions"},
    @{name="eza"; bucket="main"},
    @{name="hwmonitor"; bucket="extras"},
    @{name="dbeaver"; bucket="extras"},
    @{name="fzf"; bucket="main"},
    @{name="yazi"; bucket="main"},
    @{name="uv"; bucket="main"}
)

foreach ($package in $packages) {
    Install-ScoopPackage -packageName $package.name -bucket $package.bucket
}

# Set desktop target and PATH additions (using Environment Variables)
Write-Host "Setting environment variables..."
$desktop = "C:\Users\DEV\Desktop"
$desktopPath = "$desktop\uv;$desktop\Scoop\bin"
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")

# Only add to PATH if not already present
if ($currentPath -notlike "*$desktopPath*") {
    $env:PATH = $currentPath + ";$desktopPath"
    [Environment]::SetEnvironmentVariable("PATH", $env:PATH, "User")
    Write-Host "Updated PATH environment variable."
} else {
    Write-Host "PATH already contains required entries."
}

# Update all installed applications
Write-Host "Updating all installed applications..."
scoop update *

# Attempt to set Windows Terminal Preview as default
Set-WindowsTerminalPreviewAsDefault

# Launch common applications
Write-Host "Launching common applications..."
$apps = @(
    # @{path="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"; required=$false},
    @{path="C:\Windows\System32\notepad.exe"; required=$false},
    @{path="C:\Windows\explorer.exe"; required=$true}
)

foreach ($app in $apps) {
    try {
        if (Test-Path $app.path) {
            Start-Process $app.path -ErrorAction SilentlyContinue
            Write-Host "Started $($app.path)"
        } else {
            $message = if ($app.required) {
                "Error: Required application not found: $($app.path)"
            } else {
                "Warning: Could not find $($app.path)"
            }
            Write-Host $message
        }
    } catch {
        Write-Host ("Error starting {0}: {1}" -f $app.path, $_.Exception.Message)
    }
}

# Try to start Windows Terminal Preview, fallback to PowerShell if not available
try {
    $wtPath = Get-Command "wtp.exe" -ErrorAction SilentlyContinue
    if ($wtPath) {
        Write-Host "Starting Windows Terminal Preview..."
        Start-Process "wtp.exe" -Wait
    } else {
        Write-Host "Windows Terminal Preview not found in PATH, checking Scoop installation..."
        $wtpScoop = Join-Path $env:USERPROFILE "AppData\Local\Programs\Scoop\bin\apps\windows-terminal-preview\current\WindowsTerminalPreview.exe"
        if (Test-Path $wtpScoop) {
            Write-Host "Starting Windows Terminal Preview from Scoop installation..."
            Start-Process $wtpScoop -Wait
        } else {
            Write-Host "Windows Terminal Preview not found, starting PowerShell instead..."
            Start-Process "powershell.exe"
        }
    }
} catch {
    Write-Host ("Error launching terminal: {0}" -f $_.Exception.Message)
    Write-Host "Falling back to PowerShell..."
    Start-Process "powershell.exe"
}

Write-Host "scoop.ps1 script completed successfully."