#!/bin/bash
# uDOS Universal Startup Script v1.4
# Beautiful startup sequence with integrated display mode options

set -euo pipefail

# Enhanced debugging integration
if [[ -f "$UDOS_ROOT/dev/scripts/enhanced-debug.sh" ]]; then
    source "$UDOS_ROOT/dev/scripts/enhanced-debug.sh"
fi


# Configuration
export UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)}"
export UDOS_VERSION="1.0.4.1"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

# Function to get current role level
get_current_role() {
    local role="ghost"  # Default minimum role
    
    # Check sandbox role config
    if [[ -f "$UDOS_ROOT/sandbox/current-role.conf" ]]; then
        role=$(cat "$UDOS_ROOT/sandbox/current-role.conf" 2>/dev/null || echo "ghost")
    fi
    
    echo "$role"
}

# Function to get role level number
get_role_level() {
    local role="$1"
    case "$role" in
        "ghost") echo "10" ;;
        "tomb") echo "20" ;;
        "crypt") echo "30" ;;
        "drone") echo "40" ;;
        "knight") echo "50" ;;
        "user") echo "60" ;;
        "imp") echo "70" ;;
        "dev") echo "80" ;;
        "sorcerer") echo "90" ;;
        "wizard") echo "100" ;;
        *) echo "10" ;;
    esac
}

# Function to check role permissions
check_role_permissions() {
    local current_role=$(get_current_role)
    local role_level=$(get_role_level "$current_role")
    
    echo -e "${CYAN}🎭 Current Role: ${WHITE}$current_role${NC} ${CYAN}(Level $role_level)${NC}"
}

# Function to show uDOS startup sequence
show_startup_sequence() {
    # Show rainbow ASCII banner
    "$UDOS_ROOT/uSCRIPT/library/ucode/ascii.sh" startup
    
    echo ""
    check_role_permissions
    echo ""
    
    # Brief pause for dramatic effect
    sleep 1
    
    # Show boot sequence
    "$UDOS_ROOT/uSCRIPT/library/ucode/ascii.sh" boot
    
    echo ""
    echo -e "${GREEN}✅ uDOS v$UDOS_VERSION startup complete${NC}"
    echo ""
}

# Function to show startup options
show_startup_options() {
    echo -e "${WHITE}🚀 uDOS Startup Options${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${CYAN}Choose your uDOS experience:${NC}"
    echo ""
    echo -e "  ${GREEN}[1]${NC} 🖥️  Interactive Dashboard - Full system control"
    echo -e "  ${GREEN}[2]${NC} 🌐 Web Export Mode - Launch web interface"
    echo -e "  ${GREEN}[3]${NC} 🖥️  Desktop App Mode - Native application"
    echo -e "  ${GREEN}[4]${NC} 🔧 Display Setup - Configure display system"
    echo -e "  ${GREEN}[5]${NC} 📋 Available Modes - Check what's ready"
    echo ""
    echo -e "  ${GREEN}[h]${NC} 📚 Help & Documentation"
    echo -e "  ${GREEN}[q]${NC} 🚪 Exit"
    echo ""
}

# Function to handle user choice
handle_startup_choice() {
    echo -e "${YELLOW}Select an option (1-5, h, q):${NC} "
    read -r choice
    
    case "$choice" in
        "1")
            echo ""
            echo -e "${CYAN}🖥️ Starting Interactive Dashboard...${NC}"
            sleep 1
            exec "$UDOS_ROOT/uCORE/core/commands/ucode.sh" dashboard
            ;;
        "2")
            echo ""
            echo -e "${CYAN}🌐 Launching Web Export Mode...${NC}"
            sleep 1
            cd "$UDOS_ROOT"
            exec ./uNETWORK/display/udos-display.sh export dashboard --open
            ;;
        "3")
            echo ""
            echo -e "${CYAN}🖥️ Launching Desktop App Mode...${NC}"
            sleep 1
            cd "$UDOS_ROOT"
            exec ./uNETWORK/display/udos-display.sh desktop
            ;;
        "4")
            echo ""
            echo -e "${CYAN}🔧 Display System Setup${NC}"
            cd "$UDOS_ROOT"
            ./uNETWORK/display/setup-display-system.sh
            echo ""
            show_startup_options
            handle_startup_choice
            ;;
        "5")
            echo ""
            echo -e "${CYAN}📋 Available Display Modes${NC}"
            cd "$UDOS_ROOT"
            ./uNETWORK/display/setup-display-system.sh quick
            echo ""
            echo -e "${CYAN}Press Enter to return to startup menu...${NC}"
            read -r
            show_startup_options
            handle_startup_choice
            ;;
        "h")
            echo ""
            echo -e "${CYAN}📚 uDOS Help & Documentation${NC}"
            echo ""
            echo -e "${WHITE}Available Documentation:${NC}"
            echo -e "  • ${CYAN}User Guide:${NC} $UDOS_ROOT/docs/USER-GUIDE.md"
            echo -e "  • ${CYAN}Architecture:${NC} $UDOS_ROOT/docs/ARCHITECTURE.md"
            echo -e "  • ${CYAN}Quick Start:${NC} $UDOS_ROOT/QUICKSTART.md"
            echo -e "  • ${CYAN}README:${NC} $UDOS_ROOT/README.md"
            echo ""
            echo -e "${WHITE}Online Resources:${NC}"
            echo -e "  • ${CYAN}Repository:${NC} https://github.com/fredporter/uDOS"
            echo ""
            echo -e "${CYAN}Press Enter to return to startup menu...${NC}"
            read -r
            show_startup_options
            handle_startup_choice
            ;;
        "q")
            echo ""
            echo -e "${GREEN}Thank you for using uDOS v$UDOS_VERSION${NC}"
            echo -e "${CYAN}Come back anytime! 👋${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo ""
            echo -e "${RED}Invalid option. Please try again.${NC}"
            sleep 1
            show_startup_options
            handle_startup_choice
            ;;
    esac
}

# Main function
main() {
    # Show the beautiful startup sequence
    show_startup_sequence
    
    # Show options menu
    show_startup_options
    
    # Handle user choice
    handle_startup_choice
}

# Execute main function
main "$@"
