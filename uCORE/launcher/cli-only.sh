#!/usr/bin/env bash
# uDOS CLI-Only Launcher for GHOST and TOMB roles
# Provides terminal-only interface with proper role restrictions

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CLI_SERVER="$UDOS_ROOT/uCORE/server/cli_server.py"

# Colors for CLI output (if terminal supports it)
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
    RED=$(tput setaf 1)
    GREEN=$(tput setaf 2)
    YELLOW=$(tput setaf 3)
    BLUE=$(tput setaf 4)
    BOLD=$(tput bold)
    RESET=$(tput sgr0)
else
    RED="" GREEN="" YELLOW="" BLUE="" BOLD="" RESET=""
fi

# Detect role
detect_role() {
    local install_file="$UDOS_ROOT/uMEMORY/user/installation.md"
    if [[ -f "$install_file" ]]; then
        grep -i "^role:" "$install_file" | cut -d: -f2 | tr -d ' ' | tr '[:upper:]' '[:lower:]'
    else
        echo "ghost"  # Default to most restrictive
    fi
}

# Show CLI banner
show_banner() {
    local role="$1"
    echo "${BLUE}${BOLD}"
    echo "┌─────────────────────────────────────────────┐"
    echo "│              uDOS CLI Server                │"
    echo "│          Text-Only Interface               │"
    echo "├─────────────────────────────────────────────┤"
    printf "│ Role: %-34s │\n" "${role^^}"
    echo "├─────────────────────────────────────────────┤"
    echo "│ Commands: help, status, commands            │"
    echo "│ Type 'exit' to quit                        │"
    echo "└─────────────────────────────────────────────┘"
    echo "${RESET}"
}

# Show role-specific information
show_role_info() {
    local role="$1"

    case "$role" in
        "ghost")
            echo "${YELLOW}GHOST Role (Level 10):${RESET}"
            echo "• Minimal read-only access"
            echo "• Demo scripts only"
            echo "• Limited to 40x16 display"
            echo "• Suitable for demonstrations"
            ;;
        "tomb")
            echo "${GREEN}TOMB Role (Level 20):${RESET}"
            echo "• Basic storage manager"
            echo "• Archive script access"
            echo "• Limited to 40x16 display"
            echo "• File archival operations"
            ;;
        *)
            echo "${RED}Warning: Unexpected role '$role'${RESET}"
            echo "This launcher is designed for GHOST and TOMB roles only."
            ;;
    esac
    echo
}

# Main execution
main() {
    local role
    role=$(detect_role)

    # Validate role
    if [[ "$role" != "ghost" && "$role" != "tomb" ]]; then
        echo "${RED}${BOLD}ERROR:${RESET} This CLI launcher is for GHOST and TOMB roles only."
        echo "Detected role: $role"
        echo "Use the appropriate launcher for your role."
        exit 1
    fi

    # Check if CLI server exists
    if [[ ! -f "$CLI_SERVER" ]]; then
        echo "${RED}${BOLD}ERROR:${RESET} CLI server not found: $CLI_SERVER"
        exit 1
    fi

    # Show banner and role info
    clear 2>/dev/null || true
    show_banner "$role"
    show_role_info "$role"

    # Handle command line arguments
    if [[ $# -gt 0 ]]; then
        # Direct command execution
        echo "${BLUE}Executing:${RESET} $*"
        echo "─────────────────────────────────"
        python3 "$CLI_SERVER" "$@"
    else
        # Interactive mode
        echo "${GREEN}Starting interactive CLI mode...${RESET}"
        echo "Type 'help' for available commands."
        echo
        python3 "$CLI_SERVER"
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
