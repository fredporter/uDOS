# PowerShell Installation Script for uDOS Windows Launcher

Write-Host "🪟 Installing uDOS Windows Launcher..." -ForegroundColor Magenta

# Get script directory and uDOS root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$UdosRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..\..")

Write-Host "📂 uDOS Root: $UdosRoot" -ForegroundColor Blue

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

$Prerequisites = @()
if (-not (Get-Command bash -ErrorAction SilentlyContinue)) {
    if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
        $Prerequisites += "Git Bash or WSL (for shell script compatibility)"
    }
}

if ($Prerequisites.Count -gt 0) {
    Write-Host "⚠️  Missing prerequisites:" -ForegroundColor Yellow
    foreach ($Prereq in $Prerequisites) {
        Write-Host "  - $Prereq" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "💡 Recommendations:" -ForegroundColor Blue
    Write-Host "  - Install Git for Windows (includes Git Bash)" -ForegroundColor Cyan
    Write-Host "  - Enable WSL (Windows Subsystem for Linux)" -ForegroundColor Cyan
    Write-Host ""
}

# Create desktop shortcut
$CreateDesktop = Read-Host "📍 Create shortcut on Desktop? (Y/n)"
if ($CreateDesktop -ne "n" -and $CreateDesktop -ne "N") {
    $DesktopPath = [Environment]::GetFolderPath("Desktop")
    $ShortcutPath = Join-Path $DesktopPath "Launch uDOS.lnk"
    $BatPath = Join-Path $ScriptDir "uDOS.bat"
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $BatPath
    $Shortcut.WorkingDirectory = $UdosRoot
    $Shortcut.Description = "Launch uDOS Universal Data Operating System"
    $Shortcut.Save()
    
    Write-Host "✅ Desktop shortcut created" -ForegroundColor Green
}

# Create Start Menu shortcut
$CreateStartMenu = Read-Host "📱 Create shortcut in Start Menu? (Y/n)"
if ($CreateStartMenu -ne "n" -and $CreateStartMenu -ne "N") {
    $StartMenuPath = Join-Path ([Environment]::GetFolderPath("Programs")) "uDOS"
    if (-not (Test-Path $StartMenuPath)) {
        New-Item -ItemType Directory -Path $StartMenuPath -Force | Out-Null
    }
    
    $ShortcutPath = Join-Path $StartMenuPath "Launch uDOS.lnk"
    $BatPath = Join-Path $ScriptDir "uDOS.bat"
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $BatPath
    $Shortcut.WorkingDirectory = $UdosRoot
    $Shortcut.Description = "Launch uDOS Universal Data Operating System"
    $Shortcut.Save()
    
    Write-Host "✅ Start Menu shortcut created" -ForegroundColor Green
}

# Set execution policy for PowerShell scripts (if needed)
$CurrentPolicy = Get-ExecutionPolicy -Scope CurrentUser
if ($CurrentPolicy -eq "Restricted") {
    Write-Host "🔒 PowerShell execution policy is restricted" -ForegroundColor Yellow
    $SetPolicy = Read-Host "Allow PowerShell scripts for current user? (Y/n)"
    if ($SetPolicy -ne "n" -and $SetPolicy -ne "N") {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "✅ PowerShell execution policy updated" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🎉 Windows launcher installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  • Double-click: $($ScriptDir)\uDOS.bat" -ForegroundColor White
if ($CreateDesktop -ne "n" -and $CreateDesktop -ne "N") {
    Write-Host "  • Desktop: Launch uDOS.lnk" -ForegroundColor White
}
if ($CreateStartMenu -ne "n" -and $CreateStartMenu -ne "N") {
    Write-Host "  • Start Menu: uDOS > Launch uDOS" -ForegroundColor White
}
Write-Host ""
Write-Host "💡 For best compatibility, ensure Git Bash or WSL is installed" -ForegroundColor Blue
