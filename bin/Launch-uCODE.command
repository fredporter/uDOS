#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                   uCODE - Unified Terminal Launcher                       ║
# ║                  Launch any component from one entry point                ║
# ║                     macOS .command entry point                            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
#
# Usage:
#   - Open in Finder: Launch-uCODE.command
#   - CLI: ./Launch-uCODE.command [component] [role]
#   - CLI: ./Launch-uCODE.command core|wizard|goblin|app [dev|user]
#
# If no arguments, shows interactive menu based on available components
#
# Environment:
#   - User role: dev (all), user (limited to core TUI)
#   - Detects available: Core, Wizard Server, Goblin Dev, App Dev

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"

# Source unified launcher
source "$SCRIPT_DIR/udos-common.sh"

# ═══════════════════════════════════════════════════════════════════════════
# Component Detection
# ═══════════════════════════════════════════════════════════════════════════

_check_component() {
    local component="$1"
    case "$component" in
        core)
            [ -f "$UDOS_ROOT/uDOS.py" ] && [ -d "$UDOS_ROOT/core" ] && return 0
            ;;
        wizard)
            [ -d "$UDOS_ROOT/wizard" ] && [ -f "$UDOS_ROOT/wizard/server.py" ] && return 0
            ;;
        goblin)
            [ -d "$UDOS_ROOT/dev/goblin" ] && [ -f "$UDOS_ROOT/dev/goblin/dev_server.py" ] && return 0
            ;;
        app)
            [ -d "$UDOS_ROOT/app" ] && [ -f "$UDOS_ROOT/app/package.json" ] && return 0
            ;;
        *)
            return 1
            ;;
    esac
    return 1
}

_get_available_components() {
    local available=()
    _check_component "core" && available+=("core")
    _check_component "wizard" && available+=("wizard")
    _check_component "goblin" && available+=("goblin")
    _check_component "app" && available+=("app")
    echo "${available[@]}"
}

_get_user_role() {
    # Check for DEV_MODE environment variable or presence of dev/.git
    if [ -n "$DEV_MODE" ] || [ -d "$UDOS_ROOT/dev/.git" ]; then
        echo "dev"
    else
        echo "user"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# Interactive Menu (if no arguments)
# ═══════════════════════════════════════════════════════════════════════════

_show_menu() {
    local available=($(_get_available_components))
    local role=$(_get_user_role)

    printf "\n"
    printf "${BLUE}${TL}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${TR}${NC}\n"
    printf "${BLUE}${V_LINE}${NC}${WHITE}${BOLD}        uCODE - Unified Launcher${NC}${BLUE}${V_LINE}${NC}\n"
    printf "${BLUE}${V_LINE}${NC}      Role: ${CYAN}${role}${NC}${BLUE}${V_LINE}${NC}\n"
    printf "${BLUE}${BL}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${BR}${NC}\n\n"

    local idx=1
    for component in "${available[@]}"; do
        case "$component" in
            core) echo "  ${CYAN}${idx}${NC}) ${WHITE}Core TUI${NC} - Terminal interface (offline-first)" ;;
            wizard) echo "  ${CYAN}${idx}${NC}) ${WHITE}Wizard Server${NC} - Always-on services (port 8765)" ;;
            goblin) [ "$role" = "dev" ] && echo "  ${CYAN}${idx}${NC}) ${WHITE}Goblin Dev Server${NC} - Experimental features (port 8767)" ;;
            app) [ "$role" = "dev" ] && echo "  ${CYAN}${idx}${NC}) ${WHITE}App Dev${NC} - uMarkdown app development" ;;
        esac
        ((idx++))
    done

    echo ""
    printf "  ${YELLOW}q${NC}) Quit\n"
    printf "\n"

    read -p "Select component [1-$((${#available[@]}))]: " choice

    case "$choice" in
        q|Q) exit 0 ;;
        [0-9]*)
            if [ "$choice" -ge 1 ] && [ "$choice" -le "${#available[@]}" ]; then
                echo "${available[$((choice-1))]}"
            else
                echo "Invalid choice" >&2
                _show_menu
            fi
            ;;
        *)
            echo "Invalid choice" >&2
            _show_menu
            ;;
    esac
}

# ═══════════════════════════════════════════════════════════════════════════
# Main Launcher Logic
# ═══════════════════════════════════════════════════════════════════════════

main() {
    local component="${1:-}"
    local mode=""
    local extra_args=()
    
    # If no component specified, show menu
    if [ -z "$component" ]; then
        component=$(_show_menu)
    fi
    
    # Check if second arg is a mode or flag
    if [ -n "$2" ]; then
        case "$2" in
            tui|server|dev|user)
                mode="$2"
                shift 2
                extra_args=("$@")
                ;;
            *)
                shift 1
                extra_args=("$@")
                ;;
        esac
    else
        shift 1 2>/dev/null || true
        extra_args=("$@")
    fi
    
    # Validate component exists
    if ! _check_component "$component"; then
        printf "${RED}✗ Component '$component' not available${NC}\n" >&2
        exit 1
    fi
    
    # Determine default mode if not specified
    if [ -z "$mode" ]; then
        case "$component" in
            core) mode="tui" ;;
            wizard) mode="server" ;;
            goblin) mode="dev" ;;
            app) mode="dev" ;;
        esac
    fi
    
    # Dispatch to component launcher
    launch_component "$component" "$mode" "${extra_args[@]}"
main "$@"
