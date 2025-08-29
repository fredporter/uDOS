#!/bin/bash
# uDOS Enhanced CLI Interface
# Interactive command-line interface leveraging the integrated command router and variable system

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMAND_ROUTER="/home/wizard/uDOS/uCORE/code/command-router.sh"

# Source dependencies
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Color definitions for enhanced interface
declare -A COLORS
COLORS[reset]='\033[0m'
COLORS[bold]='\033[1m'
COLORS[red]='\033[0;31m'
COLORS[green]='\033[0;32m'
COLORS[yellow]='\033[0;33m'
COLORS[blue]='\033[0;34m'
COLORS[purple]='\033[0;35m'
COLORS[cyan]='\033[0;36m'
COLORS[white]='\033[0;37m'

# Get current user role and level for dynamic interface
get_user_role() {
    if [[ -f "$COMMAND_ROUTER" ]]; then
        local role_output
        role_output=$("$COMMAND_ROUTER" "[ROLE|GET]" 2>/dev/null | grep "Current role:" | cut -d':' -f2 | tr -d ' ')
        echo "${role_output:-GHOST}"
    else
        echo "GHOST"
    fi
}

get_role_level() {
    local role="$1"
    case "$role" in
        "GHOST") echo "10" ;;
        "TOMB") echo "20" ;;
        "CRYPT") echo "30" ;;
        "DRONE") echo "40" ;;
        "KNIGHT") echo "50" ;;
        "IMP") echo "60" ;;
        "SORCERER") echo "80" ;;
        "WIZARD") echo "100" ;;
        *) echo "0" ;;
    esac
}

# Get role-specific color scheme
get_role_color() {
    local role="$1"
    case "$role" in
        "GHOST") echo "${COLORS[white]}" ;;
        "TOMB") echo "${COLORS[yellow]}" ;;
        "CRYPT") echo "${COLORS[purple]}" ;;
        "DRONE") echo "${COLORS[blue]}" ;;
        "KNIGHT") echo "${COLORS[cyan]}" ;;
        "IMP") echo "${COLORS[red]}" ;;
        "SORCERER") echo "${COLORS[purple]}" ;;
        "WIZARD") echo "${COLORS[green]}" ;;
        *) echo "${COLORS[white]}" ;;
    esac
}

# Display enhanced banner with role information
show_banner() {
    local current_role=$(get_user_role)
    local role_level=$(get_role_level "$current_role")
    local role_color=$(get_role_color "$current_role")

    clear
    echo -e "${COLORS[bold]}${COLORS[cyan]}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    uDOS Enhanced CLI v1.0.4.1               ║"
    echo "║              Universal Device Operating System               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${COLORS[reset]}"
    echo ""
    echo -e "🌟 ${COLORS[bold]}Current Session${COLORS[reset]}"
    echo -e "   Role: ${role_color}${COLORS[bold]}$current_role${COLORS[reset]} (Level $role_level)"
    echo -e "   Date: $(date '+%d %B %Y')"
    echo -e "   Time: $(date '+%I:%M %p %Z')"
    echo ""

    # Show role-specific capabilities
    case "$current_role" in
        "GHOST")
            echo -e "👻 ${COLORS[white]}Demo Mode Active${COLORS[reset]} - Explore safely!"
            echo -e "   Available: Basic commands, Help system"
            ;;
        "TOMB"|"CRYPT")
            echo -e "🗃️ ${role_color}Archive Mode Active${COLORS[reset]} - Store and organize!"
            echo -e "   Available: Variables, Storage, Basic automation"
            ;;
        "DRONE")
            echo -e "🤖 ${role_color}Automation Mode Active${COLORS[reset]} - Systemize workflows!"
            echo -e "   Available: ASSIST basic, Variables, Automation"
            ;;
        "KNIGHT")
            echo -e "⚔️ ${role_color}Guardian Mode Active${COLORS[reset]} - Protect and serve!"
            echo -e "   Available: Role management, System protection"
            ;;
        "IMP")
            echo -e "😈 ${role_color}Creative Mode Active${COLORS[reset]} - Build and innovate!"
            echo -e "   Available: ASSIST advanced, Development tools"
            ;;
        "SORCERER")
            echo -e "🧙‍♂️ ${role_color}Magic Mode Active${COLORS[reset]} - Configure and enchant!"
            echo -e "   Available: System configuration, Advanced features"
            ;;
        "WIZARD")
            echo -e "✨ ${role_color}Master Mode Active${COLORS[reset]} - Full system control!"
            echo -e "   Available: All commands, Core system access"
            ;;
    esac
    echo ""
}

# Generate dynamic prompt based on role
generate_prompt() {
    local current_role=$(get_user_role)
    local role_color=$(get_role_color "$current_role")
    local prompt_symbol

    case "$current_role" in
        "GHOST") prompt_symbol="👻" ;;
        "TOMB") prompt_symbol="🗿" ;;
        "CRYPT") prompt_symbol="🔐" ;;
        "DRONE") prompt_symbol="🤖" ;;
        "KNIGHT") prompt_symbol="⚔️" ;;
        "IMP") prompt_symbol="😈" ;;
        "SORCERER") prompt_symbol="🧙‍♂️" ;;
        "WIZARD") prompt_symbol="✨" ;;
        *) prompt_symbol=">" ;;
    esac

    echo -e "${role_color}${prompt_symbol} uDOS${COLORS[reset]}"
}

# Process command with enhanced feedback
process_command() {
    local input="$1"

    # Skip empty input
    if [[ -z "$input" || "$input" =~ ^[[:space:]]*$ ]]; then
        return 0
    fi

    # Handle special CLI commands
    case "$input" in
        "help"|"HELP")
            "$COMMAND_ROUTER" "[HELP]"
            return 0
            ;;
        "exit"|"quit"|"EXIT"|"QUIT")
            echo -e "${COLORS[green]}Thank you for using uDOS! Goodbye! 👋${COLORS[reset]}"
            exit 0
            ;;
        "clear"|"CLEAR")
            show_banner
            return 0
            ;;
        "status"|"STATUS")
            "$COMMAND_ROUTER" "[SYSTEM|STATUS]"
            return 0
            ;;
        "vars"|"variables"|"VARS"|"VARIABLES")
            "$COMMAND_ROUTER" "[LIST]"
            return 0
            ;;
        "stories"|"STORIES")
            "$COMMAND_ROUTER" "[STORY|LIST]"
            return 0
            ;;
    esac

    # Check if input looks like uCODE format
    if [[ "$input" =~ ^\[.*\]$ ]]; then
        # Direct uCODE command
        echo -e "${COLORS[blue]}Processing uCODE: ${COLORS[cyan]}$input${COLORS[reset]}"
        echo ""
        "$COMMAND_ROUTER" "$input"
    else
        # Try to parse as natural language command
        local parsed_command=$(parse_natural_command "$input")
        if [[ -n "$parsed_command" ]]; then
            echo -e "${COLORS[blue]}Interpreted as: ${COLORS[cyan]}$parsed_command${COLORS[reset]}"
            echo ""
            "$COMMAND_ROUTER" "$parsed_command"
        else
            echo -e "${COLORS[yellow]}💡 Tip: Use uCODE format [COMMAND|ACTION] or try:${COLORS[reset]}"
            echo "  help - Show available commands"
            echo "  status - Show system status"
            echo "  vars - List variables"
            echo "  stories - List available stories"
            echo ""
            echo "  Example: [GET|USER-ROLE] or [HELP|VARIABLE]"
        fi
    fi
}

# Parse natural language to uCODE (basic implementation)
parse_natural_command() {
    local input="$1"
    input=$(echo "$input" | tr '[:upper:]' '[:lower:]')

    case "$input" in
        "get "*)
            local var_name=$(echo "$input" | sed 's/get //' | tr '[:lower:]' '[:upper:]' | sed 's/-/_/g')
            echo "[GET|$var_name]"
            ;;
        "set "*)
            local rest=$(echo "$input" | sed 's/set //')
            if [[ "$rest" =~ ^([^[:space:]]+)[[:space:]]+(.+)$ ]]; then
                local var_name="${BASH_REMATCH[1]}"
                local var_value="${BASH_REMATCH[2]}"
                var_name=$(echo "$var_name" | tr '[:lower:]' '[:upper:]' | sed 's/_/-/g')
                echo "[SET|$var_name*$var_value]"
            fi
            ;;
        "list variables"|"show variables")
            echo "[LIST]"
            ;;
        "show role"|"get role"|"what role")
            echo "[ROLE|GET]"
            ;;
        "change role "*|"set role "*)
            local role=$(echo "$input" | sed 's/.*role //' | tr '[:lower:]' '[:upper:]')
            echo "[ROLE|SET*$role]"
            ;;
        "run story "*|"execute story "*)
            local story=$(echo "$input" | sed 's/.*story //')
            echo "[STORY|RUN*$story]"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Show quick help overlay
show_quick_help() {
    echo -e "${COLORS[cyan]}Quick Help:${COLORS[reset]}"
    echo "  help        - Full command list"
    echo "  status      - System status"
    echo "  vars        - List variables"
    echo "  stories     - List stories"
    echo "  clear       - Clear screen"
    echo "  exit        - Exit uDOS"
    echo ""
    echo -e "${COLORS[cyan]}uCODE Examples:${COLORS[reset]}"
    echo "  [GET|USER-ROLE]              - Get current role"
    echo "  [SET|PROJECT-NAME*MyProject] - Set project name"
    echo "  [HELP|VARIABLE]              - Variable help"
    echo "  [STORY|RUN*wizard-startup]   - Run wizard setup"
    echo ""
}

# Main interactive loop
main() {
    # Check if command router is available
    if [[ ! -f "$COMMAND_ROUTER" ]]; then
        log_error "Command router not found: $COMMAND_ROUTER"
        echo "Please run the variable system optimizer first:"
        echo "./uCORE/code/variable-system-optimizer.sh"
        exit 1
    fi

    # Show banner
    show_banner

    # Show quick help on first run
    show_quick_help

    # Main loop
    while true; do
        echo ""
        echo -n "$(generate_prompt) "

        # Read user input
        read -r user_input

        # Process the command
        if ! process_command "$user_input"; then
            echo -e "${COLORS[red]}Command failed. Type 'help' for assistance.${COLORS[reset]}"
        fi
    done
}

# Run main function if script executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
