# PowerShell uDOS Launcher for Windows
# Provides native Windows launching capabilities

Write-Host "🪟 uDOS Windows PowerShell Launcher" -ForegroundColor Magenta
Write-Host "===================================" -ForegroundColor Cyan

# Get script directory and uDOS root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$UdosRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..\..")

Write-Host "📂 uDOS Root: $UdosRoot" -ForegroundColor Blue
Write-Host ""

# Platform detection
$Platform = "windows"
$PlatformName = "Windows"

# VS Code detection
$VsCodeAvailable = $false
if (Get-Command code -ErrorAction SilentlyContinue) {
    $VsCodeAvailable = $true
    Write-Host "✅ VS Code detected" -ForegroundColor Green
} else {
    Write-Host "⚠️  VS Code not found in PATH" -ForegroundColor Yellow
}

# Check uDOS installation
$UcodeScript = Join-Path $UdosRoot "uCORE\code\ucode.sh"
if (-not (Test-Path $UcodeScript)) {
    Write-Host "❌ uDOS core script not found" -ForegroundColor Red
    Write-Host "💡 Expected: $UcodeScript" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Launch mode selection
Write-Host "🚀 Choose launch mode:" -ForegroundColor Blue
Write-Host "  1) VS Code (Development Mode)" -ForegroundColor Green
Write-Host "  2) Terminal (Production Mode)" -ForegroundColor Green
Write-Host ""

$Choice = Read-Host "Selection (1-2, default: 1)"

switch ($Choice) {
    "2" {
        Write-Host "🖥️  Launching uDOS in Terminal..." -ForegroundColor Green
        
        # Try different shells in order of preference
        if (Get-Command bash -ErrorAction SilentlyContinue) {
            Write-Host "Using Bash..." -ForegroundColor Blue
            Set-Location $UdosRoot
            & bash $UcodeScript
        } elseif (Get-Command wsl -ErrorAction SilentlyContinue) {
            Write-Host "Using WSL..." -ForegroundColor Blue
            & wsl bash $UcodeScript
        } else {
            Write-Host "❌ No compatible shell found" -ForegroundColor Red
            Write-Host "💡 Please install Git Bash or WSL for best compatibility" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
    default {
        if ($VsCodeAvailable) {
            Write-Host "🎯 Launching uDOS in VS Code..." -ForegroundColor Green
            Write-Host "📂 Project: $UdosRoot" -ForegroundColor Blue
            
            Set-Location $UdosRoot
            & code . --goto "uCORE\code\ucode.sh"
            
            Write-Host "✅ VS Code launched with uDOS project" -ForegroundColor Green
        } else {
            Write-Host "⚠️  VS Code not available, falling back to terminal" -ForegroundColor Yellow
            
            # Same terminal fallback as option 2
            if (Get-Command bash -ErrorAction SilentlyContinue) {
                Set-Location $UdosRoot
                & bash $UcodeScript
            } elseif (Get-Command wsl -ErrorAction SilentlyContinue) {
                & wsl bash $UcodeScript
            } else {
                Write-Host "❌ No compatible shell found" -ForegroundColor Red
                Write-Host "💡 Please install Git Bash or WSL" -ForegroundColor Yellow
                Read-Host "Press Enter to exit"
                exit 1
            }
        }
    }
}

Write-Host ""
Write-Host "🎉 uDOS launch complete!" -ForegroundColor Green
