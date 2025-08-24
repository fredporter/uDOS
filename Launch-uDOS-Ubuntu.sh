#!/bin/bash
# 🌀 uDOS Ubuntu 22 Launcher v1.4.0
# Three-mode display launcher for Ubuntu: CLI Terminal, Desktop App, Web Export

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export UDOS_ROOT="$SCRIPT_DIR"

# Load core color system if available
if [[ -f "$UDOS_ROOT/uCORE/system/polaroid-colors.sh" ]]; then
    source "$UDOS_ROOT/uCORE/system/polaroid-colors.sh"
    polaroid_echo "cyan" "🌀 uDOS v1.4 - Ubuntu Launcher"
else
    # Fallback colors
    readonly CYAN='\033[0;36m'
    readonly GREEN='\033[0;32m'
    readonly RED='\033[0;31m'
    readonly YELLOW='\033[1;33m'
    readonly PURPLE='\033[0;35m'
    readonly NC='\033[0m'
    echo -e "${CYAN}🌀 uDOS v1.4 - Ubuntu Launcher${NC}"
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

# Check for required dependencies
if command -v polaroid_echo >/dev/null 2>&1; then
    polaroid_echo "yellow" "🔍 Checking dependencies..."
else
    echo -e "${YELLOW}🔍 Checking dependencies...${NC}"
fi

# Check for bash
if ! command -v bash >/dev/null 2>&1; then
    if command -v polaroid_echo >/dev/null 2>&1; then
        polaroid_echo "orange" "❌ Bash not found"
    else
        echo -e "${RED}❌ Bash not found${NC}"
    fi
    echo "Please install bash: sudo apt update && sudo apt install bash"
    exit 1
fi

# Check for python3
if ! command -v python3 >/dev/null 2>&1; then
    if command -v polaroid_echo >/dev/null 2>&1; then
        polaroid_echo "yellow" "⚠️  Python3 not found, installing..."
    else
        echo -e "${YELLOW}⚠️  Python3 not found, installing...${NC}"
    fi
    sudo apt update && sudo apt install python3 python3-pip -y
fi

# Check for git
if ! command -v git >/dev/null 2>&1; then
    if command -v polaroid_echo >/dev/null 2>&1; then
        polaroid_echo "yellow" "⚠️  Git not found, installing..."
    else
        echo -e "${YELLOW}⚠️  Git not found, installing...${NC}"
    fi
    sudo apt update && sudo apt install git -y
fi

# Additional v1.4 dependencies check
if ! command -v node >/dev/null 2>&1; then
    if command -v polaroid_echo >/dev/null 2>&1; then
        polaroid_echo "yellow" "💡 Node.js not found (needed for Desktop App)"
    else
        echo -e "${YELLOW}💡 Node.js not found (needed for Desktop App)${NC}"
    fi
    echo "   Install Node.js for desktop application support"
fi

if ! command -v cargo >/dev/null 2>&1; then
    if command -v polaroid_echo >/dev/null 2>&1; then
        polaroid_echo "yellow" "💡 Rust not found (needed for Desktop App)"
    else
        echo -e "${YELLOW}💡 Rust not found (needed for Desktop App)${NC}"
    fi
    echo "   Install Rust for desktop application support"
fi

# Show three-mode launch options
echo ""
echo "🎯 uDOS v1.4 Display Modes:"
echo "  1) 🖥️  CLI Terminal (all roles)"
echo "  2) 🪟 Desktop Application (DRONE+ roles: level 40+)"
echo "  3) 🌐 Web Export (DRONE+ roles: level 40+)"
echo "  4) 🧙‍♂️ VS Code Development"
echo ""
echo "💡 DRONE+ roles (40+): Drone, Knight, User, Imp, Dev, Sorcerer, Wizard"
echo "   Higher roles inherit all capabilities of lower roles"
echo "   Complete hierarchy: Ghost(10) → Tomb(20) → Crypt(30) → DRONE+(40+)"
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
