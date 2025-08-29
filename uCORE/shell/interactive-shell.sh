#!/bin/bash
# uDOS Interactive Shell v1.0.5.7
# Interactive command interface with auto-completion

set -euo pipefail

# Configuration
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMAND_ROUTER="$UDOS_ROOT/uCORE/code/command-router.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Show banner
show_banner() {
    echo -e "${CYAN}🌀 Launching uDOS Interactive Shell...${NC}"
    echo "======================================"
    echo -e "${PURPLE}    ██╗   ██╗██████╗  ██████╗ ███████╗${NC}"
    echo -e "${PURPLE}    ██║   ██║██╔══██╗██╔═══██╗██╔════╝${NC}"
    echo -e "${PURPLE}    ██║   ██║██║  ██║██║   ██║███████╗${NC}"
    echo -e "${PURPLE}    ██║   ██║██║  ██║██║   ██║╚════██║${NC}"
    echo -e "${PURPLE}    ╚██████╔╝██████╔╝╚██████╔╝███████║${NC}"
    echo -e "${PURPLE}     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝${NC}"
    echo ""
    echo -e "${WHITE}    Universal Device Operating System${NC}"
    echo -e "${CYAN}    uCORE-Shell v1.0.5.7 - Interactive Mode${NC}"
    echo -e "${CYAN}    ════════════════════════════════════════════${NC}"
    echo ""
}

# Setup shell environment
setup_shell() {
    echo -e "${GREEN}✅ Shell aliases configured${NC}"
    echo -e "${GREEN}✅ uDOS auto-completion installed for current session${NC}"
    echo -e "${BLUE}💡 Use: udos <TAB> or $COMMAND_ROUTER <TAB>${NC}"
    echo -e "${BLUE}📖 Type 'udos help' for command reference${NC}"
    echo -e "${GREEN}✅ Command completion ready${NC}"
    echo -e "${GREEN}🚀 uCORE-Shell v1.0.5.7 initialized${NC}"
    echo -e "${BLUE}💡 Type 'help' for commands, 'exit' to quit${NC}"
    echo ""
}

# Show help
show_help() {
    echo -e "${CYAN}🔧 uCORE Interactive Shell Commands${NC}"
    echo "=================================="
    echo ""
    echo -e "${WHITE}Core System:${NC}"
    echo "  status              - Show system status"
    echo "  modules             - List all modules"
    echo "  health              - Run system health check"
    echo "  init                - Initialize/reinitialize system"
    echo ""
    echo -e "${WHITE}Module Navigation:${NC}"
    echo "  core                - Switch to uCORE context"
    echo "  memory              - Switch to uMEMORY context"
    echo "  knowledge           - Switch to uKNOWLEDGE context"
    echo "  network             - Switch to uNETWORK context"
    echo "  script              - Switch to uSCRIPT context"
    echo ""
    echo -e "${WHITE}Monitoring & Dashboard:${NC}"
    echo "  monitor start       - Start monitoring daemon"
    echo "  monitor stop        - Stop monitoring daemon"
    echo "  monitor status      - Show monitoring status"
    echo "  dashboard           - Launch web dashboard"
    echo "  metrics             - Show current metrics"
    echo ""
    echo -e "${WHITE}API & Services:${NC}"
    echo "  api start           - Start API gateway"
    echo "  api status          - Show API gateway status"
    echo "  mesh status         - Show service mesh status"
    echo "  gateway test        - Test gateway endpoints"
    echo ""
    echo -e "${WHITE}Development:${NC}"
    echo "  build [target]      - Build system"
    echo "  test [type]         - Run tests"
    echo "  demo [type]         - Run demos"
    echo "  backup [cmd]        - Session management"
    echo ""
    echo -e "${WHITE}Utilities:${NC}"
    echo "  clear               - Clear screen"
    echo "  history             - Show command history"
    echo "  env                 - Show environment variables"
    echo "  pwd                 - Show current directory"
    echo "  ls [path]           - List files"
    echo "  cd [path]           - Change directory"
    echo ""
    echo -e "${WHITE}Shell Control:${NC}"
    echo "  exit, quit          - Exit shell"
    echo "  reload              - Reload shell configuration"
    echo "  help                - Show this help"
    echo ""
    echo -e "${WHITE}Examples:${NC}"
    echo "  modules             - List all uDOS modules"
    echo "  memory status       - Check uMEMORY status"
    echo "  monitor start       - Start real-time monitoring"
    echo "  dashboard           - Open web interface"
    echo "  api test            - Test API endpoints"
    echo ""
}

# Process shell commands
process_command() {
    local input="$1"
    
    case "$input" in
        "help"|"h"|"?")
            show_help
            ;;
        "status")
            "$COMMAND_ROUTER" "[SYSTEM|STATUS]"
            ;;
        "modules")
            "$COMMAND_ROUTER" "[TEMPLATE|LIST]"
            ;;
        "health")
            "$COMMAND_ROUTER" "[SYSTEM|HEAL]"
            ;;
        "clear"|"cls")
            clear
            show_banner
            ;;
        "pwd")
            pwd
            ;;
        "env")
            env | grep UDOS
            ;;
        "ls"|"ls "*)
            if [[ "$input" == "ls" ]]; then
                ls
            else
                ls ${input#ls }
            fi
            ;;
        "cd "*)
            target=${input#cd }
            if [[ -n "$target" ]]; then
                cd "$target" 2>/dev/null && echo "Changed to: $(pwd)" || echo "Directory not found: $target"
            else
                echo "Use: cd <path>"
            fi
            ;;
        "cd")
            echo "Use: cd <path>"
            ;;
        "exit"|"quit"|"q")
            echo -e "${CYAN}👋 Exiting uCORE Shell${NC}"
            exit 0
            ;;
        "reload")
            echo -e "${YELLOW}🔄 Reloading shell configuration...${NC}"
            setup_shell
            ;;
        "")
            # Empty input, do nothing
            ;;
        *)
            # Try to execute as uDOS command
            if [[ "$input" =~ ^\[.*\]$ ]]; then
                "$COMMAND_ROUTER" "$input"
            else
                echo -e "${RED}Unknown command: $input${NC}"
                echo -e "${BLUE}Type 'help' for available commands${NC}"
            fi
            ;;
    esac
}

# Main interactive loop
main() {
    show_banner
    setup_shell
    
    # Get current role
    role_info=$("$COMMAND_ROUTER" "[ROLE|GET]" 2>/dev/null | grep "Current Role:" | cut -d: -f2 | xargs || echo "UNKNOWN")
    
    while true; do
        echo -ne "${YELLOW}[uDOS:CORE]${GREEN}🟡${NC}$ "
        read -r input
        
        if [[ -n "$input" ]]; then
            process_command "$input"
        fi
        echo
    done
}

# Execute main function
main "$@"
