#!/bin/bash
# Browser-based editor command handler
# Usage: [EDIT|BROWSER]

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"

# Source logging functions
source "$UDOS_ROOT/uCORE/code/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Check if server is running
check_server() {
    if curl -s "http://localhost:8080/api/system/status" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Launch browser editor
launch_browser_editor() {
    log_info "Opening browser-based markdown editor..."

    # Check if server is running
    if ! check_server; then
        log_warning "uDOS server not running. Starting server..."
        # Try to start server in background
        if [[ -f "$UDOS_ROOT/uNETWORK/server/launch-with-venv.sh" ]]; then
            "$UDOS_ROOT/uNETWORK/server/launch-with-venv.sh" &
            sleep 3

            if ! check_server; then
                log_error "Failed to start uDOS server"
                exit 1
            fi
        else
            log_error "Server launch script not found"
            exit 1
        fi
    fi

    # Open browser to editor tab
    local editor_url="http://localhost:8080#editor"

    # Platform-specific browser opening
    case "$(uname -s)" in
        Darwin*)
            open "$editor_url"
            ;;
        Linux*)
            if command -v xdg-open >/dev/null 2>&1; then
                xdg-open "$editor_url"
            elif command -v firefox >/dev/null 2>&1; then
                firefox "$editor_url" &
            elif command -v chromium >/dev/null 2>&1; then
                chromium "$editor_url" &
            else
                log_warning "No suitable browser found. Please open: $editor_url"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            start "$editor_url"
            ;;
        *)
            log_warning "Unknown platform. Please open: $editor_url"
            ;;
    esac

    log_success "Browser editor opened at: $editor_url"
}

# ASCII block output for uCORE command mode
show_browser_status() {
    cat << 'EOF'
╔══════════════════════════════════════╗
║         🌐 BROWSER EDITOR            ║
║     Web-Based Markdown Editor        ║
╠══════════════════════════════════════╣
║ Features:                            ║
║ • Live markdown preview              ║
║ • Syntax highlighting               ║
║ • File browser integration          ║
║ • Auto-save to sandbox              ║
║ • uCODE syntax support              ║
╚══════════════════════════════════════╝
EOF
}

# Handle different argument patterns
case "${1:-launch}" in
    --status)
        show_browser_status
        ;;
    --help|help)
        show_browser_status
        echo
        echo "Usage: [EDIT|BROWSER]"
        echo "Opens the web-based markdown editor in your default browser"
        ;;
    launch|*)
        launch_browser_editor
        ;;
esac
