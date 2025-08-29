#!/bin/bash
# 🌀 uDOS macOS Launcher v1.0.4.1
# Three-mode display launcher for macOS: CLI Terminal, Desktop App, Web Export

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export UDOS_ROOT="$SCRIPT_DIR"

# Load core color system if available
if [[ -f "$UDOS_ROOT/uCORE/system/polaroid-colors.sh" ]]; then
    source "$UDOS_ROOT/uCORE/system/polaroid-colors.sh"
    polaroid_echo "cyan" "🌀 uDOS v1.4 - macOS Launcher"
else
    echo -e "\033[0;36m🌀 uDOS v1.4 - macOS Launcher\033[0m"
fi

# Check if we're in the right place
if [[ ! -f "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" ]]; then
    if command -v polaroid_echo >/dev/null 2>&1; then
        polaroid_echo "orange" "❌ uDOS not found in current directory"
    else
        echo -e "\033[0;31m❌ uDOS not found in current directory\033[0m"
    fi
    echo "Please run this script from the uDOS root directory"
    exit 1
fi

# Show three-mode launch options
echo ""
echo -e "\033[0;36m🎯 uDOS v1.4 Display Modes:\033[0m"
echo -e "   \033[1;33m1)\033[0m 🖥️  CLI Terminal \033[0;35m(all roles - uCORE)\033[0m"
echo -e "   \033[1;33m2)\033[0m 🪟 Desktop Application \033[0;32m(Crypt and above: level 30+)\033[0m"
echo -e "   \033[1;33m3)\033[0m 🌐 Web Export \033[0;32m(Crypt and above: level 30+)\033[0m"
echo -e "   \033[1;33m4)\033[0m 🧙‍♂️ VS Code Development \033[0;95m(Wizard only: level 100)\033[0m"
echo ""
echo -e "\033[0;36m💡 Feature Access by Role Level:\033[0m"
echo -e "   \033[0;35mGhost/Tomb (10-20):\033[0m uCORE only"
echo -e "   \033[0;34mCrypt and above (30+):\033[0m uCORE + uNETWORK + uSCRIPT + Display Modes"
echo -e "   \033[1;33mSorcerer and above (80+):\033[0m + Gemini-CLI"
echo -e "   \033[0;95mWizard (100):\033[0m + VS Code Dev Mode"
echo ""

read -p "Select mode [1-4]: " mode_choice

case "$mode_choice" in
    1)
        # CLI Terminal mode
        if command -v polaroid_echo >/dev/null 2>&1; then
            polaroid_echo "lime" "✅ Starting CLI Terminal..."
        else
            echo -e "\033[0;32m✅ Starting CLI Terminal...\033[0m"
        fi
        chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
        exec "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
        ;;
    2)
        # Desktop Application mode
        if command -v polaroid_echo >/dev/null 2>&1; then
            polaroid_echo "cyan" "🪟 Launching Desktop Application..."
        else
            echo -e "\033[0;36m🪟 Launching Desktop Application...\033[0m"
        fi
        if [[ -f "$UDOS_ROOT/uNETWORK/display/udos-display.sh" ]]; then
            chmod +x "$UDOS_ROOT/uNETWORK/display/udos-display.sh"
            exec "$UDOS_ROOT/uNETWORK/display/udos-display.sh" app
        else
            if command -v polaroid_echo >/dev/null 2>&1; then
                polaroid_echo "orange" "❌ Desktop app not available - falling back to CLI"
            else
                echo -e "\033[1;33m❌ Desktop app not available - falling back to CLI\033[0m"
            fi
            chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
            exec "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
        fi
        ;;
    3)
        # Web Export mode
        if command -v polaroid_echo >/dev/null 2>&1; then
            polaroid_echo "cyan" "🌐 Starting Web Export..."
        else
            echo -e "\033[0;36m🌐 Starting Web Export...\033[0m"
        fi
        if [[ -f "$UDOS_ROOT/uNETWORK/display/udos-display.sh" ]]; then
            chmod +x "$UDOS_ROOT/uNETWORK/display/udos-display.sh"
            exec "$UDOS_ROOT/uNETWORK/display/udos-display.sh" export dashboard --open
        else
            if command -v polaroid_echo >/dev/null 2>&1; then
                polaroid_echo "orange" "❌ Web export not available - falling back to CLI"
            else
                echo -e "\033[1;33m❌ Web export not available - falling back to CLI\033[0m"
            fi
            chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
            exec "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" --ui-mode
        fi
        ;;
    4)
        # VS Code Development mode
        if command -v polaroid_echo >/dev/null 2>&1; then
            polaroid_echo "purple" "🧙‍♂️ Starting VS Code Development..."
        else
            echo -e "\033[0;35m🧙‍♂️ Starting VS Code Development...\033[0m"
        fi
        if [[ -f "$UDOS_ROOT/dev/vscode/start-vscode-dev.sh" ]]; then
            chmod +x "$UDOS_ROOT/dev/vscode/start-vscode-dev.sh"
            exec "$UDOS_ROOT/dev/vscode/start-vscode-dev.sh"
        else
            if command -v polaroid_echo >/dev/null 2>&1; then
                polaroid_echo "orange" "❌ VS Code dev mode not available - falling back to CLI"
            else
                echo -e "\033[1;33m❌ VS Code dev mode not available - falling back to CLI\033[0m"
            fi
            chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
            exec "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" --vscode-dev
        fi
        ;;
    *)
        if command -v polaroid_echo >/dev/null 2>&1; then
            polaroid_echo "orange" "❌ Invalid choice, starting CLI Terminal"
        else
            echo -e "\033[1;33m❌ Invalid choice, starting CLI Terminal\033[0m"
        fi
        chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
        exec "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
        ;;
esac
