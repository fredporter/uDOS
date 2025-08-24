#!/bin/bash
# 🌀 uDOS macOS Launcher v1.4.0
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
    # Fallback colors
    readonly CYAN='\033[0;36m'
    readonly GREEN='\033[0;32m'
    readonly YELLOW='\033[1;33m'
    readonly RED='\033[0;31m'
    readonly NC='\033[0m'
    echo -e "${CYAN}🌀 uDOS v1.4 - macOS Launcher${NC}"
fi

# Check if we're in the right place
if [[ ! -f "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" ]]; then
    if command -v polaroid_echo >/dev/null 2>&1; then
        polaroid_echo "orange" "❌ uDOS not found in current directory"
    else
        echo -e "${RED}❌ uDOS not found in current directory${NC}"
    fi
    echo "Please run this script from the uDOS root directory"
    exit 1
fi

# Show three-mode launch options
echo ""
echo "🎯 uDOS v1.4 Display Modes:"
echo "  1) 🖥️  CLI Terminal (all roles - uCORE)"
echo "  2) 🪟 Desktop Application (DRONE+ roles: level 40+)"
echo "  3) 🌐 Web Export (DRONE+ roles: level 40+)"
echo "  4) 🧙‍♂️ VS Code Development (Wizard only: level 100)"
echo ""
echo "💡 Feature Access by Role Level:"
echo "   Ghost/Tomb (10-20): uCORE only"
echo "   Crypt+ (30+): uCORE + uNETWORK + uSCRIPT"
echo "   DRONE+ (40+): + Desktop App + Web Export"
echo "   Sorcerer+ (80+): + Gemini-CLI"
echo "   Wizard (100): + VS Code Dev Mode"
echo ""

read -p "Select mode [1-4]: " mode_choice

case "$mode_choice" in
    1)
        # CLI Terminal mode
        if command -v polaroid_echo >/dev/null 2>&1; then
            polaroid_echo "lime" "✅ Starting CLI Terminal..."
        else
            echo -e "${GREEN}✅ Starting CLI Terminal...${NC}"
        fi
        chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
        exec "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
        ;;
    2)
        # Desktop Application mode
        if command -v polaroid_echo >/dev/null 2>&1; then
            polaroid_echo "cyan" "🪟 Launching Desktop Application..."
        else
            echo -e "${CYAN}🪟 Launching Desktop Application...${NC}"
        fi
        if [[ -f "$UDOS_ROOT/uNETWORK/display/udos-display.sh" ]]; then
            chmod +x "$UDOS_ROOT/uNETWORK/display/udos-display.sh"
            exec "$UDOS_ROOT/uNETWORK/display/udos-display.sh" app
        else
            if command -v polaroid_echo >/dev/null 2>&1; then
                polaroid_echo "orange" "❌ Desktop app not available - falling back to CLI"
            else
                echo -e "${YELLOW}❌ Desktop app not available - falling back to CLI${NC}"
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
            echo -e "${CYAN}🌐 Starting Web Export...${NC}"
        fi
        if [[ -f "$UDOS_ROOT/uNETWORK/display/udos-display.sh" ]]; then
            chmod +x "$UDOS_ROOT/uNETWORK/display/udos-display.sh"
            exec "$UDOS_ROOT/uNETWORK/display/udos-display.sh" export dashboard --open
        else
            if command -v polaroid_echo >/dev/null 2>&1; then
                polaroid_echo "orange" "❌ Web export not available - falling back to CLI"
            else
                echo -e "${YELLOW}❌ Web export not available - falling back to CLI${NC}"
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
            echo -e "${PURPLE}🧙‍♂️ Starting VS Code Development...${NC}"
        fi
        if [[ -f "$UDOS_ROOT/uCORE/launcher/vscode/start-vscode-dev.sh" ]]; then
            chmod +x "$UDOS_ROOT/uCORE/launcher/vscode/start-vscode-dev.sh"
            exec "$UDOS_ROOT/uCORE/launcher/vscode/start-vscode-dev.sh"
        else
            if command -v polaroid_echo >/dev/null 2>&1; then
                polaroid_echo "orange" "❌ VS Code dev mode not available - falling back to CLI"
            else
                echo -e "${YELLOW}❌ VS Code dev mode not available - falling back to CLI${NC}"
            fi
            chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
            exec "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" --vscode-dev
        fi
        ;;
    *)
        if command -v polaroid_echo >/dev/null 2>&1; then
            polaroid_echo "orange" "❌ Invalid choice, starting CLI Terminal"
        else
            echo -e "${YELLOW}❌ Invalid choice, starting CLI Terminal${NC}"
        fi
        chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
        exec "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
        ;;
esac
