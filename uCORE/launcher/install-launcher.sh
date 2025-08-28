#!/bin/bash
# Universal uDOS Launcher Installation Script
# Detects platform and installs appropriate launchers

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Banner
echo -e "${PURPLE}🚀 uDOS Universal Launcher Installer${NC}"
echo -e "${CYAN}====================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source platform detection
source "$SCRIPT_DIR/universal/detect-platform.sh"
run_detection --verbose

# Make all scripts executable
echo -e "${YELLOW}🔧 Making scripts executable...${NC}"
find "$SCRIPT_DIR" -name "*.sh" -exec chmod +x {} \;
find "$SCRIPT_DIR" -name "*.command" -exec chmod +x {} \;
echo -e "${GREEN}✅ Scripts made executable${NC}"
echo ""

# Platform-specific installation
case "$PLATFORM" in
    macos)
        echo -e "${BLUE}🍎 Installing macOS launchers...${NC}"
        bash "$SCRIPT_DIR/platform/macos/install.sh"
        ;;
    windows)
        echo -e "${BLUE}🪟 Installing Windows launchers...${NC}"
        if command -v powershell >/dev/null 2>&1; then
            powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/platform/windows/install.ps1"
        else
            echo -e "${YELLOW}⚠️  PowerShell not found, manual installation required${NC}"
            echo -e "${BLUE}💡 Please run: $SCRIPT_DIR/platform/windows/install.ps1${NC}"
        fi
        ;;
    linux)
        echo -e "${BLUE}🐧 Installing Linux launchers...${NC}"
        bash "$SCRIPT_DIR/platform/linux/install.sh"
        ;;
    *)
        echo -e "${RED}❌ Unsupported platform: $PLATFORM_NAME${NC}"
        echo -e "${YELLOW}💡 Please install manually for your platform${NC}"
        exit 1
        ;;
esac

echo ""

# VS Code setup (optional)
if [ "$VSCODE_AVAILABLE" = true ]; then
    read -p "🔌 Setup VS Code integration? (Y/n): " setup_vscode
    if [[ "$setup_vscode" != "n" && "$setup_vscode" != "N" ]]; then
        echo ""
        bash "$SCRIPT_DIR/vscode/setup-vscode.sh"
    fi
else
    echo -e "${YELLOW}⚠️  VS Code not found, skipping VS Code integration${NC}"
    echo -e "${BLUE}💡 Install VS Code and re-run this script for development features${NC}"
fi

echo ""
echo -e "${GREEN}🎉 uDOS Launcher installation complete!${NC}"
echo ""
echo -e "${CYAN}🚀 Quick Start:${NC}"

case "$PLATFORM" in
    macos)
        echo -e "  • ${GREEN}Finder${NC}: Double-click ${YELLOW}uDOS.command${NC}"
        echo -e "  • ${GREEN}Terminal${NC}: ${YELLOW}$SCRIPT_DIR/universal/start-udos.sh${NC}"
        ;;
    windows)
        echo -e "  • ${GREEN}Explorer${NC}: Double-click ${YELLOW}uDOS.bat${NC}"
        echo -e "  • ${GREEN}PowerShell${NC}: ${YELLOW}$SCRIPT_DIR/platform/windows/uDOS.ps1${NC}"
        ;;
    linux)
        echo -e "  • ${GREEN}GUI${NC}: Applications menu → ${YELLOW}uDOS${NC}"
        echo -e "  • ${GREEN}Terminal${NC}: ${YELLOW}udos${NC} (if alias installed)"
        ;;
esac

echo -e "  • ${GREEN}Development${NC}: ${YELLOW}$SCRIPT_DIR/universal/start-dev.sh${NC}"

if [ "$VSCODE_AVAILABLE" = true ]; then
    echo -e "  • ${GREEN}VS Code${NC}: Open ${YELLOW}$UDOS_ROOT/uDOS.code-workspace${NC}"
fi

echo ""
echo -e "${BLUE}📚 Documentation: $UDOS_ROOT/uCORE/docs/User-Manual.md${NC}"
echo -e "${BLUE}🆘 Support: $UDOS_ROOT/README.md${NC}"
