#!/bin/bash
# Configuration command handler for micro editor
# Usage: [EDIT|CONFIG]

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
EXTENSION_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_DIR="$EXTENSION_DIR/config"
MICRO_BIN="$EXTENSION_DIR/bin/micro"

# Source logging functions
source "$UDOS_ROOT/uCORE/code/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Show configuration menu
show_config_menu() {
    cat << 'EOF'
╔══════════════════════════════════════╗
║          ⚙️ MICRO EDITOR CONFIG       ║
║       Configuration Management       ║
╠══════════════════════════════════════╣
║ Options:                             ║
║ 1. Edit settings file                ║
║ 2. Reset to defaults                 ║
║ 3. Show current settings             ║
║ 4. Install/update micro              ║
║ 5. Test installation                 ║
║ q. Quit                              ║
╚══════════════════════════════════════╝
EOF
}

# Edit settings file
edit_settings() {
    local settings_file="$CONFIG_DIR/micro-settings.json"

    if [[ ! -f "$settings_file" ]]; then
        log_warning "Settings file not found. Creating default configuration..."
        "$EXTENSION_DIR/install-micro.sh" --config-only 2>/dev/null || {
            mkdir -p "$CONFIG_DIR"
            echo '{"tabsize": 4, "syntax": true, "autoindent": true}' > "$settings_file"
        }
    fi

    log_info "Opening micro settings: $settings_file"

    if [[ -x "$MICRO_BIN" ]]; then
        export MICRO_CONFIG_HOME="$CONFIG_DIR"
        "$MICRO_BIN" "$settings_file"
    else
        log_warning "Micro not installed. Opening with system editor..."
        "${EDITOR:-nano}" "$settings_file"
    fi
}

# Reset to defaults
reset_defaults() {
    log_info "Resetting micro configuration to defaults..."

    if [[ -d "$CONFIG_DIR" ]]; then
        mv "$CONFIG_DIR" "$CONFIG_DIR.backup.$(date +%s)"
        log_info "Existing config backed up"
    fi

    "$EXTENSION_DIR/install-micro.sh" --config-only 2>/dev/null || {
        mkdir -p "$CONFIG_DIR"
        cat > "$CONFIG_DIR/micro-settings.json" << 'EOF'
{
    "autoindent": true,
    "autosave": 2,
    "colorscheme": "default",
    "cursorline": true,
    "ignorecase": false,
    "mouse": true,
    "ruler": true,
    "statusline": true,
    "syntax": true,
    "tabsize": 4,
    "tabstospaces": false
}
EOF
    }

    log_success "Configuration reset to defaults"
}

# Show current settings
show_settings() {
    local settings_file="$CONFIG_DIR/micro-settings.json"

    echo "╔══════════════════════════════════════╗"
    echo "║         CURRENT MICRO SETTINGS      ║"
    echo "╚══════════════════════════════════════╝"
    echo

    if [[ -f "$settings_file" ]]; then
        if command -v jq >/dev/null 2>&1; then
            jq '.' "$settings_file"
        else
            cat "$settings_file"
        fi
    else
        echo "No configuration file found at: $settings_file"
        echo "Run option 2 to create default configuration."
    fi

    echo
    echo "Configuration directory: $CONFIG_DIR"
}

# Install or update micro
install_update_micro() {
    log_info "Installing/updating micro editor..."
    "$EXTENSION_DIR/install-micro.sh" --force
}

# Test installation
test_installation() {
    echo "╔══════════════════════════════════════╗"
    echo "║         MICRO INSTALLATION TEST     ║"
    echo "╚══════════════════════════════════════╝"
    echo

    if [[ -x "$MICRO_BIN" ]]; then
        local version
        version=$("$MICRO_BIN" --version 2>&1 | head -1)
        echo "✅ Micro editor found: $version"
        echo "📍 Location: $MICRO_BIN"

        if [[ -f "$CONFIG_DIR/micro-settings.json" ]]; then
            echo "✅ Configuration file exists"
        else
            echo "❌ Configuration file missing"
        fi

        echo "✅ Installation test passed"
    else
        echo "❌ Micro editor not found at: $MICRO_BIN"
        echo "💡 Run option 4 to install micro editor"
    fi
}

# Interactive configuration menu
interactive_config() {
    while true; do
        echo
        show_config_menu
        echo
        read -p "Select option [1-5, q]: " choice

        case "$choice" in
            1)
                edit_settings
                ;;
            2)
                reset_defaults
                ;;
            3)
                show_settings
                read -p "Press Enter to continue..."
                ;;
            4)
                install_update_micro
                ;;
            5)
                test_installation
                read -p "Press Enter to continue..."
                ;;
            q|Q)
                log_info "Configuration menu closed"
                break
                ;;
            *)
                log_warning "Invalid option. Please select 1-5 or q."
                ;;
        esac
    done
}

# Handle different argument patterns
case "${1:-interactive}" in
    --status)
        show_config_menu
        ;;
    --help|help)
        show_config_menu
        echo
        echo "Usage: [EDIT|CONFIG]"
        echo "Opens the micro editor configuration menu"
        ;;
    interactive|*)
        interactive_config
        ;;
esac
