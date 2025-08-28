#!/bin/bash
# uDOS Help Module v1.3
# Comprehensive help system for uDOS commands and features

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)" pwd)"

show_main_help() {
    echo -e "${BLUE}📚 uDOS Help System v1.3${NC}"
    echo ""
    echo -e "${CYAN}Core Commands:${NC}"
    echo "  help [topic]         - Show this help or specific topic help"
    echo "  status [type]        - System status and health checks"
    echo "  dashboard           - Interactive system dashboard"
    echo "  user [action]       - User management and authentication"
    echo "  session [action]    - Session management and logging"
    echo "  memory [action]     - Memory system operations"
    echo "  display [type]      - Display banners and layouts"
    echo ""
    echo -e "${CYAN}System Areas:${NC}"
    echo "  🏠 sandbox          - User workspace and files"
    echo "  🧠 uMEMORY          - Knowledge and session storage"
    echo "  ⚙️  uCORE           - Core system functionality" 
    echo "  📜 uSCRIPT          - Script execution and automation"
    echo "  🔮 wizard           - Development and debugging tools"
    echo "  👻 ghost            - Public interface and demos"
    echo ""
    echo -e "${CYAN}Quick Actions:${NC}"
    echo "  restart             - Restart uDOS system"
    echo "  destroy             - Secure system shutdown"
    echo "  reboot              - System reboot (creates session log)"
    echo "  layout              - Adjust terminal layout"
    echo "  clear               - Clear screen and show banner"
    echo ""
    echo -e "${YELLOW}💡 Use 'help [command]' for detailed information${NC}"
    echo -e "${YELLOW}💡 Use 'status' to check system health${NC}"
}

show_status_help() {
    echo -e "${BLUE}📊 Status Command Help${NC}"
    echo ""
    echo "Usage: status [type]"
    echo ""
    echo "Types:"
    echo "  full     - Complete system status (default)"
    echo "  health   - System health and performance"
    echo "  modules  - Available uSCRIPT modules"
    echo "  quick    - Brief status overview"
    echo ""
    echo "Examples:"
    echo "  status           # Full system status"
    echo "  status health    # Health check only"
    echo "  status modules   # Module availability"
}

show_user_help() {
    echo -e "${BLUE}👤 User Command Help${NC}"
    echo ""
    echo "Usage: user [action]"
    echo ""
    echo "Actions:"
    echo "  login            - Authenticate user"
    echo "  info             - Show user information"
    echo "  change-password  - Change user password"
    echo "  setup            - Initial user setup"
    echo "  profile          - View user profile"
    echo ""
    echo "Security:"
    echo "  • Passwords are SHA-256 hashed"
    echo "  • User data stored in sandbox/user.md"
    echo "  • 1-16 character limit for passwords"
    echo "  • Automatic lockout after failed attempts"
}

show_session_help() {
    echo -e "${BLUE}📝 Session Command Help${NC}"
    echo ""
    echo "Usage: session [action]"
    echo ""
    echo "Actions:"
    echo "  new              - Create new session log"
    echo "  current          - Show current session info"
    echo "  list             - List recent sessions"
    echo "  view [id]        - View specific session"
    echo "  cleanup          - Clean old session logs"
    echo ""
    echo "Session Logs:"
    echo "  • Automatic creation on restart/reboot"
    echo "  • Format: uLOG-YYYYMMDD-HHMMSS-HEX-Session.md"
    echo "  • Stored in uMEMORY/"
    echo "  • Include system state and user activity"
}

show_memory_help() {
    echo -e "${BLUE}🧠 Memory Command Help${NC}"
    echo ""
    echo "Usage: memory [action]"
    echo ""
    echo "Actions:"
    echo "  status           - Memory system status"
    echo "  templates        - List available templates"
    echo "  search [term]    - Search memory content"
    echo "  backup           - Create memory backup"
    echo "  restore          - Restore from backup"
    echo ""
    echo "Memory Structure:"
    echo "  • uMEMORY/templates/ - System templates"
    echo "  • uMEMORY/user/      - User knowledge"
    echo "  • uMEMORY/system/    - System data"
    echo "  • Session logs and installation data"
}

show_display_help() {
    echo -e "${BLUE}🎨 Display Command Help${NC}"
    echo ""
    echo "Usage: display [type]"
    echo ""
    echo "Types:"
    echo "  banner           - Show full uDOS banner (default)"
    echo "  simple-banner    - Show simple ASCII banner"
    echo "  boot             - Show boot sequence"
    echo "  resize           - Terminal size recommendations"
    echo ""
    echo "Terminal Optimization:"
    echo "  • Recommended: 120x30 or larger"
    echo "  • Compact: 80x24 (minimal)"
    echo "  • Wide: 140x35 (spacious)"
    echo "  • Coding: 120x50 (tall)"
}

show_development_help() {
    echo -e "${BLUE}🔧 Development Help${NC}"
    echo ""
    echo "Module Development:"
    echo "  • Create modules in uSCRIPT/library/ucode/"
    echo "  • Use template structure from existing modules"
    echo "  • Export main function for command routing"
    echo "  • Make executable with chmod +x"
    echo ""
    echo "Template System:"
    echo "  • Templates in uMEMORY/templates/"
    echo "  • Use Markdown format"
    echo "  • Support for ASCII art and layouts"
    echo ""
    echo "Debugging:"
    echo "  • Check logs in uMEMORY/"
    echo "  • Use wizard/ for development tools"
    echo "  • Test modules directly"
}

show_areas_help() {
    echo -e "${BLUE}🏗️ System Areas Help${NC}"
    echo ""
    echo -e "${CYAN}sandbox/         ${NC}- User workspace"
    echo "  • user.md          - User credentials and data"
    echo "  • Personal files and projects"
    echo "  • Safe testing environment"
    echo ""
    echo -e "${CYAN}uMEMORY/         ${NC}- Knowledge storage"
    echo "  • Session logs and installation data"
    echo "  • Templates and system knowledge"
    echo "  • User memory and preferences"
    echo ""
    echo -e "${CYAN}uCORE/           ${NC}- Core functionality"
    echo "  • code/            - Core system modules"
    echo "  • config/          - System configuration"
    echo "  • launcher/        - System startup"
    echo ""
    echo -e "${CYAN}uSCRIPT/         ${NC}- Script execution"
    echo "  • library/         - Reusable modules"
    echo "  • active/          - Running scripts"
    echo "  • templates/       - Script templates"
}

# Main function
help_main() {
    local topic="${1:-main}"
    
    case "$topic" in
        "main"|"")
            show_main_help
            ;;
        "status")
            show_status_help
            ;;
        "user")
            show_user_help
            ;;
        "session")
            show_session_help
            ;;
        "memory")
            show_memory_help
            ;;
        "display")
            show_display_help
            ;;
        "development"|"dev")
            show_development_help
            ;;
        "areas"|"system")
            show_areas_help
            ;;
        *)
            echo -e "${YELLOW}Unknown help topic: $topic${NC}"
            echo ""
            show_main_help
            ;;
    esac
}

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    help_main "$@"
fi
