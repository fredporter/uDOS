@echo off
REM Windows Batch Launcher for uDOS
REM Double-click launcher for Windows Explorer integration

echo Starting uDOS for Windows...

REM Get script directory and navigate to uDOS root
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"
cd ..\..\..\..

REM Set uDOS root
set "UDOS_ROOT=%cd%"

echo uDOS Root: %UDOS_ROOT%

REM Check if Git Bash is available (preferred)
where bash >nul 2>&1
if %errorlevel% == 0 (
    echo Using Git Bash for better compatibility...
    bash "%UDOS_ROOT%\uCORE\launcher\universal\start-udos.sh"
    goto :end
)

REM Check if WSL is available
where wsl >nul 2>&1
if %errorlevel% == 0 (
    echo Using WSL for Linux compatibility...
    wsl bash "%UDOS_ROOT%\uCORE\launcher\universal\start-udos.sh"
    goto :end
)

REM Fallback to PowerShell
echo Using PowerShell fallback...
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%\uDOS.ps1"

:end
popd
pause
