#!/bin/bash
# Development Mode Launcher for uDOS
# Specifically designed for development workflow with VS Code integration

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

# Development mode banner
show_dev_banner() {
    echo -e "${PURPLE}🧑‍💻 uDOS Development Mode${NC}"
    echo -e "${CYAN}=============================${NC}"
    echo -e "${BLUE}Platform: $PLATFORM_NAME${NC}"
    echo -e "${BLUE}Root: $UDOS_ROOT${NC}"
    echo -e "${BLUE}VS Code: $([ "$VSCODE_AVAILABLE" = true ] && echo -e "${GREEN}Available${NC}" || echo -e "${YELLOW}Not Available${NC}")${NC}"
    echo ""
}

# Setup development environment
setup_dev_environment() {
    echo -e "${YELLOW}🔧 Setting up development environment...${NC}"
    
    # Ensure VS Code workspace configuration exists
    if [ ! -d "$UDOS_ROOT/.vscode" ]; then
        echo -e "${BLUE}📁 Creating VS Code workspace configuration...${NC}"
        mkdir -p "$UDOS_ROOT/.vscode"
        
        # Copy VS Code configuration from launcher
        if [ -f "$UDOS_ROOT/uCORE/launcher/vscode/settings.json" ]; then
            cp "$UDOS_ROOT/uCORE/launcher/vscode/settings.json" "$UDOS_ROOT/.vscode/"
        fi
        
        if [ -f "$UDOS_ROOT/uCORE/launcher/vscode/tasks.json" ]; then
            cp "$UDOS_ROOT/uCORE/launcher/vscode/tasks.json" "$UDOS_ROOT/.vscode/"
        fi
        
        if [ -f "$UDOS_ROOT/uCORE/launcher/vscode/launch.json" ]; then
            cp "$UDOS_ROOT/uCORE/launcher/vscode/launch.json" "$UDOS_ROOT/.vscode/"
        fi
    fi
    
    # Install recommended extensions if setup script exists
    if [ -f "$UDOS_ROOT/uCORE/launcher/vscode/setup-vscode.sh" ]; then
        echo -e "${BLUE}🔌 Installing recommended VS Code extensions...${NC}"
        bash "$UDOS_ROOT/uCORE/launcher/vscode/setup-vscode.sh"
    fi
}

# Check development prerequisites
check_dev_prerequisites() {
    local missing_tools=()
    
    # Check for essential development tools
    if ! command -v git >/dev/null 2>&1; then
        missing_tools+=("git")
    fi
    
    if ! command -v node >/dev/null 2>&1 && [ -d "$UDOS_ROOT/uDOS-Extension" ]; then
        missing_tools+=("node.js (for extension development)")
    fi
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Missing development tools:${NC}"
        for tool in "${missing_tools[@]}"; do
            echo -e "  - ${RED}$tool${NC}"
        done
        echo ""
        echo -e "${BLUE}💡 These tools are recommended for full development experience${NC}"
        echo ""
    fi
}

# Launch development environment
launch_development() {
    if [ "$VSCODE_AVAILABLE" = true ]; then
        echo -e "${GREEN}🚀 Launching VS Code with uDOS project...${NC}"
        
        cd "$UDOS_ROOT"
        
        # Launch VS Code with specific files open
        if command -v code >/dev/null 2>&1; then
            # Open main files for development
            code . \
                --goto "README.md:1" \
                --goto "uCORE/code/ucode.sh:1" \
                --goto "uMEMORY/README.md:1"
        else
            # Platform-specific VS Code launching
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
                        echo -e "${RED}❌ VS Code not properly installed${NC}"
                        fallback_to_terminal
                    fi
                    ;;
            esac
        fi
        
        echo -e "${GREEN}✅ Development environment ready!${NC}"
        echo -e "${BLUE}💡 Use VS Code tasks (Ctrl+Shift+P) to run uDOS commands${NC}"
        
    else
        echo -e "${YELLOW}⚠️  VS Code not available, using enhanced terminal mode${NC}"
        fallback_to_terminal
    fi
}

# Fallback to enhanced terminal mode
fallback_to_terminal() {
    echo -e "${BLUE}🖥️  Starting uDOS in development terminal mode...${NC}"
    
    cd "$UDOS_ROOT"
    
    # Set development environment variables
    export UDOS_DEV_MODE=true
    export UDOS_DEBUG=true
    
    # Launch uDOS with development flags
    exec "$UDOS_ROOT/uCORE/code/ucode.sh" --dev
}

# Main execution
main() {
    show_dev_banner
    
    # Check if uDOS exists
    if [ ! -d "$UDOS_ROOT" ] || [ ! -f "$UDOS_ROOT/uCORE/code/ucode.sh" ]; then
        echo -e "${RED}❌ uDOS installation not found${NC}"
        echo -e "${YELLOW}💡 Expected location: $UDOS_ROOT${NC}"
        exit 1
    fi
    
    check_dev_prerequisites
    setup_dev_environment
    launch_development
}

# Handle command line arguments
case "$1" in
    --help|-h)
        echo -e "${CYAN}uDOS Development Mode Launcher${NC}"
        echo ""
        echo "This script sets up and launches uDOS in development mode with:"
        echo "  - VS Code integration (if available)"
        echo "  - Development environment setup"
        echo "  - Recommended extensions installation"
        echo "  - Debug mode enabled"
        echo ""
        echo "Usage: $0 [--help]"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
