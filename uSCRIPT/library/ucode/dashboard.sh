#!/bin/bash
# uDOS Dashboard Module v1.3
# Interactive system dashboard and menu interface

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)" pwd)"
UMEMORY="$UDOS_ROOT/uMEMORY"
SANDBOX="$UDOS_ROOT/sandbox"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

show_dashboard() {
    clear
    
    # Show banner
    "$UDOS_ROOT/uSCRIPT/library/ucode/display.sh" simple-banner
    
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    SYSTEM DASHBOARD                  ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # System status overview
    show_status_overview
    echo ""
    
    # Quick actions menu
    show_quick_menu
    echo ""
    
    # Recent activity
    show_recent_activity
}

show_status_overview() {
    echo -e "${BLUE}📊 System Overview${NC}"
    echo ""
    
    # User status
    if [[ -f "$SANDBOX/user.md" ]]; then
        local username=$(grep "^Username:" "$SANDBOX/user.md" 2>/dev/null | cut -d' ' -f2-)
        echo -e "  👤 User: ${GREEN}${username:-'Not set'}${NC}"
    else
        echo -e "  👤 User: ${RED}Not authenticated${NC}"
    fi
    
    # Session info
    local session_count=$(find "$UMEMORY" -name "*Session.md" 2>/dev/null | wc -l)
    echo -e "  📝 Sessions: ${session_count}"
    
    # Module count
    local module_count=$(find "$UDOS_ROOT/uSCRIPT/library/ucode" -name "*.sh" 2>/dev/null | wc -l)
    echo -e "  📦 Modules: ${module_count}"
    
    # System time
    echo -e "  🕐 Time: $(date '+%H:%M:%S')"
    
    # Disk usage
    local disk_usage=$(df "$UDOS_ROOT" | tail -1 | awk '{print $5}')
    echo -e "  💾 Disk: ${disk_usage} used"
}

show_quick_menu() {
    echo -e "${BLUE}⚡ Quick Actions${NC}"
    echo ""
    echo "  [1] User Management      [2] Session Logs"
    echo "  [3] System Status        [4] Memory Browser"
    echo "  [5] Help System          [6] Terminal Layout"
    echo "  [7] Development Tools    [8] System Settings"
    echo ""
    echo "  [r] Restart uDOS         [d] Destroy Session"
    echo "  [c] Clear Screen         [q] Quit Dashboard"
}

show_recent_activity() {
    echo -e "${BLUE}📈 Recent Activity${NC}"
    echo ""
    
    # Latest session log
    local latest_session=$(find "$UMEMORY" -name "*Session.md" -exec stat -f "%m %N" {} \; 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
    if [[ -n "$latest_session" ]]; then
        local session_name=$(basename "$latest_session" | sed 's/uLOG-//' | sed 's/-Session.md//')
        echo -e "  📝 Last session: ${session_name}"
        
        # Show session timestamp
        local session_date=$(echo "$session_name" | cut -d'-' -f1-3)
        echo -e "  📅 Date: ${session_date}"
    else
        echo -e "  📝 No recent sessions"
    fi
    
    # Check for user authentication
    if [[ -f "$SANDBOX/user.md" ]]; then
        local last_login=$(grep "Last Login:" "$SANDBOX/user.md" 2>/dev/null | cut -d' ' -f3-)
        [[ -n "$last_login" ]] && echo -e "  👤 Last login: ${last_login}"
    fi
}

handle_dashboard_input() {
    echo ""
    echo -e "${YELLOW}Select an option (1-8, r, d, c, q):${NC} "
    read -r choice
    
    case "$choice" in
        "1")
            echo ""
            "$UDOS_ROOT/uSCRIPT/library/ucode/user.sh" info
            read -p "Press Enter to continue..." -r
            show_dashboard
            ;;
        "2")
            echo ""
            "$UDOS_ROOT/uSCRIPT/library/ucode/session.sh" list
            read -p "Press Enter to continue..." -r
            show_dashboard
            ;;
        "3")
            echo ""
            "$UDOS_ROOT/uSCRIPT/library/ucode/status.sh" full
            read -p "Press Enter to continue..." -r
            show_dashboard
            ;;
        "4")
            echo ""
            "$UDOS_ROOT/uSCRIPT/library/ucode/memory.sh" status
            read -p "Press Enter to continue..." -r
            show_dashboard
            ;;
        "5")
            echo ""
            "$UDOS_ROOT/uSCRIPT/library/ucode/help.sh"
            read -p "Press Enter to continue..." -r
            show_dashboard
            ;;
        "6")
            echo ""
            "$UDOS_ROOT/uSCRIPT/library/ucode/display.sh" resize
            read -p "Press Enter to continue..." -r
            show_dashboard
            ;;
        "7")
            echo ""
            echo -e "${BLUE}🔧 Development Tools${NC}"
            echo "Available in wizard/ directory"
            echo "Use 'ls wizard/' to explore development utilities"
            read -p "Press Enter to continue..." -r
            show_dashboard
            ;;
        "8")
            echo ""
            echo -e "${BLUE}⚙️ System Settings${NC}"
            echo "Configuration files located in uCORE/config/"
            echo "Templates available in uMEMORY/templates/"
            read -p "Press Enter to continue..." -r
            show_dashboard
            ;;
        "r")
            echo ""
            echo -e "${YELLOW}Restarting uDOS...${NC}"
            # This would trigger the main ucode restart
            exit 0
            ;;
        "d")
            echo ""
            echo -e "${RED}Destroying session...${NC}"
            # This would trigger the destroy function
            exit 1
            ;;
        "c")
            show_dashboard
            ;;
        "q")
            echo ""
            echo -e "${GREEN}Exiting dashboard...${NC}"
            return 0
            ;;
        *)
            echo ""
            echo -e "${RED}Invalid option. Please try again.${NC}"
            sleep 1
            show_dashboard
            ;;
    esac
}

show_interactive_dashboard() {
    show_dashboard
    handle_dashboard_input
}

# Main function
dashboard_main() {
    local action="${1:-interactive}"
    
    case "$action" in
        "interactive"|"")
            show_interactive_dashboard
            ;;
        "status")
            show_status_overview
            ;;
        "menu")
            show_quick_menu
            ;;
        "activity")
            show_recent_activity
            ;;
        "static")
            show_dashboard
            ;;
        *)
            echo "Dashboard module - Available actions: interactive, status, menu, activity, static"
            ;;
    esac
}

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    dashboard_main "$@"
fi
