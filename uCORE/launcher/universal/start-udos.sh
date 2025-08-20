#!/bin/bash
# Universal uDOS Startup Script
# Provides cross-platform launching with intelligent mode detection

# Source platform detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/detect-platform.sh"

# Run platform detection
run_detection

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Help function
show_help() {
    echo -e "${CYAN}uDOS Universal Launcher${NC}"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --dev, --development    Force development mode (VS Code)"
    echo "  --prod, --production    Force production mode (Terminal)"
    echo "  --terminal              Same as --production"
    echo "  --vscode                Force VS Code mode"
    echo "  --help, -h              Show this help message"
    echo ""
    echo "Default behavior:"
    echo "  - Auto-detect best launch method"
    echo "  - Prefer VS Code if available and in development context"
    echo "  - Fall back to terminal mode"
}

# Default mode
LAUNCH_MODE="auto"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev|--development)
            LAUNCH_MODE="development"
            shift
            ;;
        --prod|--production|--terminal)
            LAUNCH_MODE="production"
            shift
            ;;
        --vscode)
            LAUNCH_MODE="vscode"
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Check if uDOS is properly installed
check_udos_installation() {
    if [ ! -d "$UDOS_ROOT" ]; then
        echo -e "${RED}❌ uDOS not found at: $UDOS_ROOT${NC}"
        echo -e "${YELLOW}💡 Please check your uDOS installation${NC}"
        exit 1
    fi
    
    if [ ! -f "$UDOS_ROOT/uCORE/code/ucode.sh" ]; then
        echo -e "${RED}❌ uDOS core script not found${NC}"
        echo -e "${YELLOW}💡 Expected: $UDOS_ROOT/uCORE/code/ucode.sh${NC}"
        exit 1
    fi
}

# Determine launch mode
determine_launch_mode() {
    case "$LAUNCH_MODE" in
        development|vscode)
            if [ "$VSCODE_AVAILABLE" = true ]; then
                FINAL_MODE="vscode"
            else
                echo -e "${YELLOW}⚠️  VS Code not available, falling back to terminal${NC}"
                FINAL_MODE="terminal"
            fi
            ;;
        production|terminal)
            FINAL_MODE="terminal"
            ;;
        auto)
            # Auto-detection logic
            if [ "$VSCODE_AVAILABLE" = true ]; then
                # Check if we're in a development context
                if [ -f "$UDOS_ROOT/.vscode/settings.json" ] || [ -d "$UDOS_ROOT/uDOS-Extension" ]; then
                    FINAL_MODE="vscode"
                else
                    # Ask user preference
                    ask_launch_preference
                fi
            else
                FINAL_MODE="terminal"
            fi
            ;;
    esac
}

# Ask user for launch preference
ask_launch_preference() {
    echo -e "${BLUE}🚀 Choose launch mode:${NC}"
    echo -e "  ${GREEN}1${NC}) VS Code (Development Mode)"
    echo -e "  ${GREEN}2${NC}) Terminal (Production Mode)"
    echo ""
    echo -n "Selection (1-2, default: 1): "
    
    read -r choice
    case "$choice" in
        2)
            FINAL_MODE="terminal"
            ;;
        1|"")
            FINAL_MODE="vscode"
            ;;
        *)
            echo -e "${YELLOW}Invalid choice, using VS Code${NC}"
            FINAL_MODE="vscode"
            ;;
    esac
}

# Launch uDOS in VS Code
launch_vscode() {
    echo -e "${GREEN}🎯 Launching uDOS in VS Code...${NC}"
    echo -e "${BLUE}📂 Project: $UDOS_ROOT${NC}"
    
    cd "$UDOS_ROOT"
    
    # Check if code command is available
    if command -v code >/dev/null 2>&1; then
        code . --goto uCORE/code/ucode.sh
    else
        case "$PLATFORM" in
            macos)
                open -a "Visual Studio Code" .
                ;;
            windows)
                start code .
                ;;
            linux)
                if command -v code-insiders >/dev/null 2>&1; then
                    code-insiders .
                else
                    echo -e "${RED}❌ VS Code command not found${NC}"
                    echo -e "${YELLOW}💡 Please install VS Code or add it to PATH${NC}"
                    exit 1
                fi
                ;;
        esac
    fi
}

# Launch uDOS in terminal
launch_terminal() {
    echo -e "${GREEN}🖥️  Launching uDOS in Terminal...${NC}"
    echo -e "${BLUE}📂 Location: $UDOS_ROOT${NC}"
    echo ""
    
    cd "$UDOS_ROOT"
    
    # Make sure scripts are executable
    chmod +x "$UDOS_ROOT/uCORE/code/ucode.sh"
    chmod +x "$UDOS_ROOT/uCORE/code/startup.sh"
    
    # Launch uDOS via startup script (includes auto-backup)
    exec "$UDOS_ROOT/uCORE/code/startup.sh"
}

# Main execution
main() {
    echo -e "${PURPLE}🌟 uDOS Universal Launcher${NC}"
    echo -e "${CYAN}Platform: $PLATFORM_NAME${NC}"
    echo ""
    
    check_udos_installation
    determine_launch_mode
    
    case "$FINAL_MODE" in
        vscode)
            launch_vscode
            ;;
        terminal)
            launch_terminal
            ;;
        *)
            echo -e "${RED}❌ Unknown launch mode: $FINAL_MODE${NC}"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
