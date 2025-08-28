@echo off
REM 🌀 uDOS Windows Launcher v1.4.0
REM Three-mode display launcher for Windows: CLI Terminal, Desktop App, Web Export

echo 🌀 uDOS v1.4 - Windows Launcher

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

echo.
echo 🎯 uDOS v1.4 Display Modes:
echo   1^) 🖥️  CLI Terminal ^(all roles - uCORE^)
echo   2^) 🪟 Desktop Application ^(Crypt and above: level 30+^)
echo   3^) 🌐 Web Export ^(Crypt and above: level 30+^)
echo   4^) 🧙‍♂️ VS Code Development ^(Wizard only: level 100^)
echo.
echo 💡 Feature Access by Role Level:
echo    Ghost/Tomb ^(10-20^): uCORE only
echo    Crypt and above ^(30+^): uCORE + uNETWORK + uSCRIPT + Display Modes
echo    Sorcerer and above ^(80+^): + Gemini-CLI
echo    Wizard ^(100^): + VS Code Dev Mode
echo.

set /p mode_choice="Select mode [1-4]: "

if "%mode_choice%"=="1" goto cli_mode
if "%mode_choice%"=="2" goto desktop_mode
if "%mode_choice%"=="3" goto web_export_mode
if "%mode_choice%"=="4" goto vscode_mode
goto cli_mode

:cli_mode
echo ✅ Starting CLI Terminal...
goto launch_cli

:desktop_mode
echo 🪟 Launching Desktop Application...
if exist "%UDOS_ROOT%\uNETWORK\display\udos-display.sh" (
    goto launch_desktop
) else (
    echo ❌ Desktop app not available - falling back to CLI
    goto launch_cli
)

:web_export_mode
echo 🌐 Starting Web Export...
if exist "%UDOS_ROOT%\uNETWORK\display\udos-display.sh" (
    goto launch_web_export
) else (
    echo ❌ Web export not available - falling back to CLI with UI
    goto launch_cli_ui
)

:vscode_mode
echo 🧙‍♂️ Starting VS Code Development...
if exist "%UDOS_ROOT%\uCORE\launcher\vscode\start-vscode-dev.sh" (
    goto launch_vscode
) else (
    echo ❌ VS Code dev mode not available - falling back to CLI
    goto launch_cli
)

:launch_desktop
REM Check for Git Bash or WSL for desktop app
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%UDOS_ROOT%\uNETWORK\display\udos-display.sh" app
) else if exist "C:\Windows\System32\bash.exe" (
    bash.exe "%UDOS_ROOT%\uNETWORK\display\udos-display.sh" app
) else (
    echo ❌ Desktop app requires Git Bash or WSL - falling back to CLI
    goto launch_cli
)
goto end

:launch_web_export
REM Check for Git Bash or WSL for web export
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%UDOS_ROOT%\uNETWORK\display\udos-display.sh" export dashboard --open
) else if exist "C:\Windows\System32\bash.exe" (
    bash.exe "%UDOS_ROOT%\uNETWORK\display\udos-display.sh" export dashboard --open
) else (
    echo ❌ Web export requires Git Bash or WSL - falling back to CLI
    goto launch_cli
)
goto end

:launch_vscode
REM Check for Git Bash or WSL for VS Code dev
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%UDOS_ROOT%\uCORE\launcher\vscode\start-vscode-dev.sh"
) else if exist "C:\Windows\System32\bash.exe" (
    bash.exe "%UDOS_ROOT%\uCORE\launcher\vscode\start-vscode-dev.sh"
) else (
    echo ❌ VS Code dev requires Git Bash or WSL - falling back to CLI
    goto launch_cli
)
goto end

:launch_cli_ui
REM Launch CLI with UI mode
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%UDOS_ROOT%\uCORE\launcher\universal\start-udos.sh" --ui-mode
) else if exist "C:\Windows\System32\bash.exe" (
    bash.exe "%UDOS_ROOT%\uCORE\launcher\universal\start-udos.sh" --ui-mode
) else (
    echo ❌ Bash not found. Please install Git for Windows or WSL.
    echo Download Git for Windows: https://git-scm.com/download/win
    pause
    exit /b 1
)
goto end

:launch_cli
REM Launch standard CLI
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

:end
