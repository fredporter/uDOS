#!/bin/bash
# uDOS v1.4 Display Mode Launcher
# Three distinct modes: CLI (always), Desktop App (Crypt and above), Web Export (sharing)

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DISPLAY_DIR="$UDOS_ROOT/uNETWORK/display"

# Load core systems
source "$UDOS_ROOT/uSCRIPT/library/shell/ensure-utf8.sh"
source "$UDOS_ROOT/uCORE/system/polaroid-colors.sh"

# Mode functions
launch_desktop_app() {
    polaroid_echo "cyan" "🖥️  Launching uDOS Desktop App..."

    cd "$DISPLAY_DIR"

    # Check if desktop app is built
    if [[ -f "src-tauri/target/release/udos-display" ]]; then
        ./src-tauri/target/release/udos-display
    elif [[ -f "src-tauri/target/debug/udos-display" ]]; then
        ./src-tauri/target/debug/udos-display
    else
        polaroid_echo "yellow" "🔨 Desktop app not built yet, building now..."
        if command -v npm >/dev/null 2>&1; then
            npm run tauri build || npm run tauri dev
        else
            polaroid_echo "orange" "❌ Desktop app requires Node.js and Tauri"
            polaroid_echo "cyan" "   Run: ./setup-display-system.sh setup"
            return 1
        fi
    fi
}

launch_web_export() {
    local export_type="${1:-dashboard}"

    polaroid_echo "cyan" "🌐 Generating web export ($export_type)..."

    # Start backend server for web export
    "$DISPLAY_DIR/launch-display-server.sh" start

    # Wait for server to start
    sleep 2

    case "$export_type" in
        "dashboard"|"status")
            polaroid_echo "lime" "✅ System dashboard available at: http://localhost:8080"
            ;;
        "terminal"|"session")
            polaroid_echo "lime" "✅ Terminal session available at: http://localhost:8080/terminal"
            ;;
        "memory"|"browse")
            polaroid_echo "lime" "✅ Memory browser available at: http://localhost:8080/memory"
            ;;
        *)
            polaroid_echo "lime" "✅ Web interface available at: http://localhost:8080"
            ;;
    esac

    # Optionally open browser for immediate viewing
    if [[ "${2:-}" == "--open" ]]; then
        if command -v open >/dev/null 2>&1; then
            open "http://localhost:8080"
        elif command -v xdg-open >/dev/null 2>&1; then
            xdg-open "http://localhost:8080"
        fi
    fi
}

show_cli_info() {
    polaroid_echo "cyan" "💻 CLI Mode Information"
    echo
    polaroid_echo "lime" "Terminal interface is always available:"
    polaroid_echo "cyan" "  udos                    # Main uDOS interface"
    polaroid_echo "cyan" "  udos terminal           # Force CLI mode"
    polaroid_echo "cyan" "  udos --help             # Show all commands"
    echo
    polaroid_echo "lime" "Best for:"
    polaroid_echo "cyan" "  • System administration"
    polaroid_echo "cyan" "  • Automation and scripting"
    polaroid_echo "cyan" "  • GHOST/TOMB role usage"
    polaroid_echo "cyan" "  • Headless server management"
}

check_role_permissions() {
    local mode="$1"
    local current_role="${UDOS_USER_ROLE:-user}"

    case "$mode" in
        "desktop"|"app")
            if [[ "$current_role" == "ghost" ]] || [[ "$current_role" == "tomb" ]]; then
                polaroid_echo "orange" "❌ Desktop app requires Crypt and above role permissions"
                polaroid_echo "cyan" "   Current role: $current_role"
                polaroid_echo "cyan" "   Available: CLI mode only"
                return 1
            fi
            ;;
        "export"|"web")
            # Web export available to all Crypt and above roles
            if [[ "$current_role" == "ghost" ]] || [[ "$current_role" == "tomb" ]]; then
                polaroid_echo "orange" "❌ Web export requires Crypt and above role permissions"
                polaroid_echo "cyan" "   Current role: $current_role"
                return 1
            fi
            ;;
    esac
    return 0
}

main() {
    local mode="${1:-help}"

    case "$mode" in
        "app"|"desktop"|"gui")
            if check_role_permissions "desktop"; then
                launch_desktop_app
            fi
            ;;
        "export"|"web"|"share")
            local export_type="${2:-dashboard}"
            local open_flag="${3:-}"
            if check_role_permissions "export"; then
                launch_web_export "$export_type" "$open_flag"
            fi
            ;;
        "cli"|"terminal"|"tty")
            show_cli_info
            ;;
        "status"|"info")
            polaroid_echo "cyan" "🎯 uDOS v1.4 Display Modes Status"
            echo

            # Check CLI availability
            polaroid_echo "lime" "✅ CLI Mode: Always available"

            # Check Desktop App
            if [[ -f "$DISPLAY_DIR/src-tauri/target/release/udos-display" ]] || \
               [[ -f "$DISPLAY_DIR/src-tauri/target/debug/udos-display" ]]; then
                polaroid_echo "lime" "✅ Desktop App: Built and ready"
            else
                polaroid_echo "yellow" "⏳ Desktop App: Needs building"
            fi

            # Check Web Export
            if [[ -f "$DISPLAY_DIR/server/display-server.py" ]]; then
                polaroid_echo "lime" "✅ Web Export: Available"
            else
                polaroid_echo "orange" "❌ Web Export: Not configured"
            fi

            echo
            polaroid_echo "cyan" "Current role: ${UDOS_USER_ROLE:-user}"
            ;;
        "build")
            polaroid_echo "cyan" "🔨 Building desktop app..."
            cd "$DISPLAY_DIR"
            if command -v npm >/dev/null 2>&1; then
                npm run tauri build
            else
                polaroid_echo "orange" "❌ Building requires Node.js and Tauri"
                polaroid_echo "cyan" "   Run: ./setup-display-system.sh setup"
            fi
            ;;
        "help"|"-h"|"--help")
            cat << EOF
🎯 uDOS v1.4 Display Mode Launcher

Three distinct display modes for different purposes:

MODES:
  cli         CLI terminal interface (always available)
  app         Desktop application (Crypt and above roles)
  export      Web export for sharing (Crypt and above roles)

USAGE:
  $0 cli                      # Show CLI information
  $0 app                      # Launch desktop application
  $0 export [type] [--open]   # Generate web export

  $0 status                   # Show mode availability
  $0 build                    # Build desktop application
  $0 help                     # Show this help

EXPORT TYPES:
  dashboard   System status and metrics (default)
  terminal    Interactive terminal session
  memory      uMEMORY browser interface

EXAMPLES:
  $0 app                      # Professional desktop interface
  $0 export dashboard --open  # Share system status via web
  $0 export terminal          # Provide web-based terminal access
  $0 cli                      # Show terminal commands

PURPOSE:
  • CLI: Direct system control and automation
  • Desktop App: Professional development interface
  • Web Export: Share uDOS state with others

No complexity, no fallbacks - just the right tool for the job.
EOF
            ;;
        *)
            polaroid_echo "orange" "❌ Unknown mode: $mode"
            polaroid_echo "cyan" "   Use: $0 help"
            exit 1
            ;;
    esac
}

main "$@"
