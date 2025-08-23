@echo off
REM 🌀 uDOS Windows Launcher v1.3.3
REM Simple one-click launcher for Windows

echo 🌀 Launching uDOS...

REM Get the directory where this script is located
set "UDOS_ROOT=%~dp0"
set "UDOS_ROOT=%UDOS_ROOT:~0,-1%"

REM Check if we're in the right place
if not exist "%UDOS_ROOT%\uCORE\launcher\universal\start-udos.sh" (
    echo ❌ uDOS not found in current directory
    echo Please run this script from the uDOS root directory
    pause
    exit /b 1
)

echo ✅ Starting uDOS...

REM Check for Git Bash or WSL
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%UDOS_ROOT%\uCORE\launcher\universal\start-udos.sh"
) else if exist "C:\Windows\System32\bash.exe" (
    bash.exe "%UDOS_ROOT%\uCORE\launcher\universal\start-udos.sh"
) else (
    echo ❌ Bash not found. Please install Git for Windows or WSL.
    echo Download Git for Windows: https://git-scm.com/download/win
    pause
    exit /b 1
)
