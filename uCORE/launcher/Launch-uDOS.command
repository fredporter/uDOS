#!/bin/bash
# uDOS macOS Launcher v1.3.1
# Enhanced launcher with role selection and startup choices

set -euo pipefail

# Configuration
export UDOS_ROOT="${UDOS_ROOT:-$HOME/uDOS}"

# Color definitions
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

echo -e "${CYAN}🌀 uDOS macOS Launcher v1.3.1${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if uDOS directory exists
if [[ ! -d "$UDOS_ROOT" ]]; then
    echo -e "${RED}❌ uDOS not found at $UDOS_ROOT${NC}"
    echo ""
    echo -e "${BLUE}📦 Installation Required${NC}"
    echo "uDOS needs to be installed. You can:"
    echo ""
    echo -e "  ${GREEN}[1]${NC} 🚀 Run automatic installer"
    echo -e "  ${GREEN}[2]${NC} � Get manual installation instructions"
    echo -e "  ${GREEN}[3]${NC} ❌ Cancel"
    echo ""
    read -p "👉 Your choice (1-3): " install_choice
    
    case "$install_choice" in
        1)
            if [[ -f "$(dirname "$0")/platform/macos/install-udos.sh" ]]; then
                exec "$(dirname "$0")/platform/macos/install-udos.sh"
            else
                echo -e "${RED}❌ Installer not found${NC}"
                exit 1
            fi
            ;;
        2)
            echo ""
            echo -e "${BLUE}📋 Manual Installation${NC}"
            echo "1. Open Terminal"
            echo "2. Run: git clone https://github.com/fredporter/uDOS.git ~/uDOS"
            echo "3. Launch uDOS again"
            echo ""
            read -p "Press Enter to exit..."
            exit 0
            ;;
        3)
            echo -e "${YELLOW}Installation cancelled${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
fi

echo -e "${GREEN}✅ Found uDOS at: $UDOS_ROOT${NC}"
echo ""

# Check for VS Code
VSCODE_AVAILABLE=false
if command -v code >/dev/null 2>&1; then
    VSCODE_AVAILABLE=true
    echo -e "${GREEN}✅ VS Code detected${NC}"
else
    echo -e "${YELLOW}ℹ️  VS Code not detected${NC}"
fi

echo ""

# Use the app bundle launcher for enhanced startup menu
if [[ -f "$UDOS_ROOT/uDOS.app/Contents/MacOS/uDOS" ]]; then
    exec "$UDOS_ROOT/uDOS.app/Contents/MacOS/uDOS"
else
    # Fallback to universal launcher
    exec "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
fi
