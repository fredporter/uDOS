#!/bin/bash
# uDOS Viewport Manager CLI
# Command-line interface for managing Chromium viewports

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VIEWPORT_MANAGER="$UDOS_ROOT/extensions/viewport/viewport_manager.py"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m' 
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to display usage
show_usage() {
    echo -e "${WHITE}uDOS Viewport Manager - Single Window Edition${NC}"
    echo -e "${CYAN}Command-controlled minimal viewport (ONE WINDOW MODE)${NC}"
    echo ""
    echo -e "${YELLOW}ℹ️  Single Window Mode: Only one viewport active at a time${NC}"
    echo -e "${YELLOW}   Opening a new viewport automatically closes existing ones${NC}"
    echo ""
    echo -e "${WHITE}Usage:${NC}"
    echo "  $0 <action> [options]"
    echo ""
    echo -e "${WHITE}Actions:${NC}"
    echo -e "  ${GREEN}create${NC}     Create a new minimal viewport (closes existing)"
    echo -e "  ${GREEN}close${NC}      Close the active viewport"
    echo -e "  ${GREEN}list${NC}       Show active viewport"
    echo -e "  ${GREEN}cleanup${NC}    Clean up dead viewports"
    echo -e "  ${GREEN}close-mode${NC} Close all viewports for a mode"
    echo -e "  ${GREEN}launch${NC}     Quick launch preset configurations"
    echo -e "  ${GREEN}install${NC}    Install recommended minimal browsers"
    echo ""
    echo -e "${WHITE}Minimal Browser Priorities:${NC}"
    echo -e "  ${PURPLE}1. surf${NC}        Ultra-minimal suckless browser (WebKit)"
    echo -e "  ${PURPLE}2. qutebrowser${NC} Vim-like keyboard-driven browser"
    echo -e "  ${PURPLE}3. luakit${NC}      Lightweight WebKit browser"
    echo -e "  ${PURPLE}4. lynx${NC}        Terminal-based text browser"
    echo -e "  ${PURPLE}5. Safari${NC}      macOS native (minimal UI mode)"
    echo ""
    echo -e "${WHITE}Options:${NC}"
    echo -e "  ${YELLOW}--mode${NC}     User mode (wizard, dev, tomb, imp, sorcerer, drone, ghost, admin)"
    echo -e "  ${YELLOW}--type${NC}     Viewport type (development, monitoring, terminal, documentation, logs, dashboard, debug, administration)"
    echo -e "  ${YELLOW}--url${NC}      URL to open"
    echo -e "  ${YELLOW}--width${NC}    Window width (default: 1024)"
    echo -e "  ${YELLOW}--height${NC}   Window height (default: 768)"
    echo -e "  ${YELLOW}--id${NC}       Viewport ID (for close action)"
    echo ""
    echo -e "${WHITE}Quick Launch Presets (Minimal UI):${NC}"
    echo -e "  ${PURPLE}wizard${NC}     Wizard + DEV mode (command-controlled development)"
    echo -e "  ${PURPLE}sorcerer${NC}   Sorcerer mode (minimal administration interface)"
    echo -e "  ${PURPLE}imp${NC}        Imp mode (minimal terminal + debug)"
    echo -e "  ${PURPLE}tomb${NC}       Tomb mode (secure minimal monitoring)"
    echo -e "  ${PURPLE}drone${NC}      Drone mode (headless/minimal monitoring)"
    echo -e "  ${PURPLE}ghost${NC}      Ghost mode (private minimal monitoring)"
    echo -e "  ${PURPLE}dev-suite${NC}  Minimal development suite (keyboard-driven)"
    echo ""
    echo -e "${WHITE}Examples:${NC}"
    echo "  $0 install surf                    # Install minimal browser"
    echo "  $0 create --mode wizard --type development"
    echo "  $0 launch wizard                   # Command-controlled wizard mode"
    echo "  $0 list --mode dev"
    echo "  $0 close --id wizard_development_1234567890"
    echo "  $0 close-mode tomb"
    echo "  $0 cleanup"
}

# Function to check if Python script exists
check_dependencies() {
    if [[ ! -f "$VIEWPORT_MANAGER" ]]; then
        echo -e "${RED}❌ Viewport manager not found: $VIEWPORT_MANAGER${NC}"
        exit 1
    fi
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required but not installed${NC}"
        exit 1
    fi
    
    # Check if required Python packages are available
    python3 -c "import psutil" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Installing required Python package: psutil${NC}"
        pip3 install psutil
    }
}

# Function to install minimal browsers
install_minimal_browser() {
    local browser="$1"
    
    echo -e "${BLUE}📦 Installing minimal browser: ${browser}${NC}"
    
    case "$browser" in
        "surf")
            if command -v brew &> /dev/null; then
                echo -e "${YELLOW}Installing surf via Homebrew...${NC}"
                brew install surf
            elif command -v apt-get &> /dev/null; then
                echo -e "${YELLOW}Installing surf via apt...${NC}"
                sudo apt-get update && sudo apt-get install surf
            else
                echo -e "${RED}❌ Package manager not found. Install manually from: https://surf.suckless.org${NC}"
            fi
            ;;
        "qutebrowser")
            if command -v brew &> /dev/null; then
                echo -e "${YELLOW}Installing qutebrowser via Homebrew...${NC}"
                brew install qutebrowser
            elif command -v apt-get &> /dev/null; then
                echo -e "${YELLOW}Installing qutebrowser via apt...${NC}"
                sudo apt-get update && sudo apt-get install qutebrowser
            else
                echo -e "${RED}❌ Package manager not found. Install manually from: https://qutebrowser.org${NC}"
            fi
            ;;
        "luakit")
            if command -v brew &> /dev/null; then
                echo -e "${YELLOW}Installing luakit via Homebrew...${NC}"
                brew install luakit
            elif command -v apt-get &> /dev/null; then
                echo -e "${YELLOW}Installing luakit via apt...${NC}"
                sudo apt-get update && sudo apt-get install luakit
            else
                echo -e "${RED}❌ Package manager not found. Install manually from: https://luakit.github.io${NC}"
            fi
            ;;
        "lynx")
            if command -v brew &> /dev/null; then
                echo -e "${YELLOW}Installing lynx via Homebrew...${NC}"
                brew install lynx
            elif command -v apt-get &> /dev/null; then
                echo -e "${YELLOW}Installing lynx via apt...${NC}"
                sudo apt-get update && sudo apt-get install lynx
            else
                echo -e "${RED}❌ Package manager not found. Install manually.${NC}"
            fi
            ;;
        "all")
            echo -e "${BLUE}📦 Installing all recommended minimal browsers...${NC}"
            install_minimal_browser "surf"
            install_minimal_browser "qutebrowser" 
            install_minimal_browser "luakit"
            install_minimal_browser "lynx"
            ;;
        *)
            echo -e "${RED}❌ Unknown browser: $browser${NC}"
            echo -e "${WHITE}Available browsers: surf, qutebrowser, luakit, lynx, all${NC}"
            exit 1
            ;;
    esac
}
launch_preset() {
    local preset="$1"
    
    case "$preset" in
        "wizard")
            echo -e "${BLUE}🧙‍♂️ Launching Wizard + DEV mode (minimal UI)...${NC}"
            python3 "$VIEWPORT_MANAGER" create --mode wizard --type development --width 1200 --height 800
            ;;
        "sorcerer")
            echo -e "${PURPLE}🔮 Launching Sorcerer mode (command-controlled admin)...${NC}"
            python3 "$VIEWPORT_MANAGER" create --mode sorcerer --type administration --width 1400 --height 900
            ;;
        "imp")
            echo -e "${RED}😈 Launching Imp mode (minimal terminal)...${NC}"
            python3 "$VIEWPORT_MANAGER" create --mode imp --type terminal --width 1024 --height 600
            ;;
        "tomb") 
            echo -e "${YELLOW}⚰️ Launching Tomb mode (secure minimal monitoring)...${NC}"
            python3 "$VIEWPORT_MANAGER" create --mode tomb --type monitoring --width 1200 --height 700
            ;;
        "drone")
            echo -e "${CYAN}🚁 Launching Drone mode (headless minimal)...${NC}"
            python3 "$VIEWPORT_MANAGER" create --mode drone --type monitoring --width 800 --height 600
            ;;
        "ghost")
            echo -e "${WHITE}👻 Launching Ghost mode (private minimal)...${NC}"
            python3 "$VIEWPORT_MANAGER" create --mode ghost --type monitoring --width 1000 --height 650
            ;;
        "dev-suite")
            echo -e "${GREEN}💻 Launching Minimal Development Suite...${NC}"
            echo -e "${BLUE}  Creating command-controlled development viewport...${NC}"
            python3 "$VIEWPORT_MANAGER" create --mode dev --type development --width 1400 --height 900
            sleep 2
            echo -e "${BLUE}  Creating minimal terminal viewport...${NC}" 
            python3 "$VIEWPORT_MANAGER" create --mode dev --type terminal --width 1200 --height 600
            sleep 2
            echo -e "${BLUE}  Creating minimal debug viewport...${NC}"
            python3 "$VIEWPORT_MANAGER" create --mode dev --type debug --width 1000 --height 700
            echo -e "${GREEN}✅ Minimal dev suite launched! Use keyboard shortcuts for navigation.${NC}"
            ;;
        *)
            echo -e "${RED}❌ Unknown preset: $preset${NC}"
            echo -e "${WHITE}Available presets: wizard, sorcerer, imp, tomb, drone, ghost, dev-suite${NC}"
            exit 1
            ;;
    esac
}

# Main script logic
main() {
    # Check dependencies first
    check_dependencies
    
    # Handle no arguments
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 0
    fi
    
    local action="$1"
    shift
    
    case "$action" in
        "create"|"close"|"list"|"cleanup"|"close-mode")
            # Pass all arguments to Python script
            python3 "$VIEWPORT_MANAGER" "$action" "$@"
            ;;
        "launch")
            if [[ $# -eq 0 ]]; then
                echo -e "${RED}❌ Preset name required for launch action${NC}"
                show_usage
                exit 1
            fi
            launch_preset "$1"
            ;;
        "install")
            if [[ $# -eq 0 ]]; then
                echo -e "${RED}❌ Browser name required for install action${NC}"
                echo -e "${WHITE}Available browsers: surf, qutebrowser, luakit, lynx, all${NC}"
                exit 1
            fi
            install_minimal_browser "$1"
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        *)
            echo -e "${RED}❌ Unknown action: $action${NC}"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
