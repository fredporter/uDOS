#!/usr/bin/env bash
# uDOS Extension Manager
# Cross-platform extension management system

set -euo pipefail

# Set UDOS_ROOT if not already set
UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
EXTENSIONS_ROOT="$UDOS_ROOT/extensions"
UCORE_CODE_DIR="$UDOS_ROOT/uCORE/code"
USER_EXTENSIONS_DIR="$EXTENSIONS_ROOT/user"
PLATFORM_EXTENSIONS_DIR="$EXTENSIONS_ROOT/platform"

# Source uDOS core functions
source "${UDOS_ROOT}/uCORE/core/logging.sh" 2>/dev/null || true

log_info() {
    echo "[EXT] $1" >&2
}

log_error() {
    echo "[EXT ERROR] $1" >&2
}

# Load extension registry
load_registry() {
    local registry_file="$1"

    if [[ -f "$registry_file" ]]; then
        cat "$registry_file"
    else
        log_error "Registry not found: $registry_file"
        return 1
    fi
}

# List available extensions
list_extensions() {
    local type="${1:-all}"

    case "$type" in
        "core"|"ucore")
            log_info "uCORE Components:"
            if [[ -f "$UCORE_CODE_DIR/registry.json" ]]; then
                grep -v "metadata" "$UCORE_CODE_DIR/registry.json" | \
                jq -r '.name + " v" + .version + " (" + .status + ")"' 2>/dev/null || \
                grep '"name"' "$UCORE_CODE_DIR/registry.json" | cut -d'"' -f4
            fi
            ;;
        "user")
            log_info "User Extensions:"
            if [[ -f "$EXTENSIONS_ROOT/user/registry.json" ]]; then
                grep -v "metadata" "$EXTENSIONS_ROOT/user/registry.json" | \
                jq -r '.name + " v" + .version + " (" + .status + ")"' 2>/dev/null || \
                grep '"name"' "$EXTENSIONS_ROOT/user/registry.json" | cut -d'"' -f4
            fi
            ;;
        "all"|*)
            list_extensions "core"
            echo
            list_extensions "user"
            ;;
    esac
}

# Load extension commands into help system
load_extension_commands() {
    local extension_path="$1"
    local commands_file="$extension_path/commands/uDATA-commands.json"

    if [[ -f "$commands_file" ]]; then
        log_info "Loading commands from: $(basename "$extension_path")"
        cat "$commands_file"
    fi
}

# Install user extension
install_extension() {
    local extension_name="$1"
    local source_path="$2"

    local target_dir="$USER_EXTENSIONS_DIR/$extension_name"

    if [[ -d "$target_dir" ]]; then
        log_error "Extension already exists: $extension_name"
        return 1
    fi

    log_info "Installing extension: $extension_name"

    # Create target directory
    mkdir -p "$target_dir"

    # Copy extension files
    if [[ -d "$source_path" ]]; then
        cp -r "$source_path"/* "$target_dir/"
    else
        log_error "Source path not found: $source_path"
        return 1
    fi

    # Validate extension
    if validate_extension "$target_dir"; then
        log_info "Extension installed successfully: $extension_name"
        update_user_registry "$extension_name" "installed"
    else
        log_error "Extension validation failed: $extension_name"
        rm -rf "$target_dir"
        return 1
    fi
}

# Validate extension structure
validate_extension() {
    local extension_path="$1"

    # Check for required manifest
    if [[ ! -f "$extension_path/manifest.json" ]]; then
        log_error "Missing manifest.json in extension"
        return 1
    fi

    # Validate manifest JSON
    if ! jq . "$extension_path/manifest.json" >/dev/null 2>&1; then
        log_error "Invalid JSON in manifest.json"
        return 1
    fi

    log_info "Extension validation passed"
    return 0
}

# Update user registry
update_user_registry() {
    local extension_name="$1"
    local status="$2"

    local registry_file="$USER_EXTENSIONS_DIR/registry.json"

    # Create registry if it doesn't exist
    if [[ ! -f "$registry_file" ]]; then
        cat > "$registry_file" << EOF
{
  "metadata": {"version": "1.0.0", "total_extensions": 0, "last_updated": "$(date -u +%Y-%m-%d)"}
}
EOF
    fi

    # Add entry (simplified - in production would use proper JSON manipulation)
    local entry="{\"name\": \"$extension_name\", \"status\": \"$status\", \"installed\": \"$(date -u +%Y-%m-%d)\"}"
    echo "$entry" >> "$registry_file"

    log_info "Updated registry for: $extension_name"
}

# Get extension info
extension_info() {
    local extension_name="$1"

    # Search in uCORE code components
    local ucore_path="$UCORE_CODE_DIR/$extension_name"
    if [[ -d "$ucore_path" ]]; then
        log_info "uCORE Component: $extension_name"
        cat "$ucore_path/manifest.json" 2>/dev/null || echo "No manifest found"
        return 0
    fi

    # Search in user extensions
    find "$USER_EXTENSIONS_DIR" -name "$extension_name" -type d | while read -r user_path; do
        log_info "User Extension: $extension_name"
        cat "$user_path/manifest.json" 2>/dev/null || echo "No manifest found"
        return 0
    done

    log_error "Extension not found: $extension_name"
    return 1
}

# Main command interface
main() {
    local command="${1:-help}"

    case "$command" in
        "list")
            list_extensions "${2:-all}"
            ;;
        "install")
            if [[ $# -lt 3 ]]; then
                log_error "Usage: extension-manager install <name> <source_path>"
                return 1
            fi
            install_extension "$2" "$3"
            ;;
        "info")
            if [[ $# -lt 2 ]]; then
                log_error "Usage: extension-manager info <name>"
                return 1
            fi
            extension_info "$2"
            ;;
        "validate")
            if [[ $# -lt 2 ]]; then
                log_error "Usage: extension-manager validate <path>"
                return 1
            fi
            validate_extension "$2"
            ;;
        "load-commands")
            # Load all extension commands for help system integration
            find "$UCORE_CODE_DIR" -name "uDATA-commands.json" -exec cat {} \;
            find "$USER_EXTENSIONS_DIR" -name "uDATA-commands.json" -exec cat {} \;
            ;;
        "help"|*)
            cat << EOF
uDOS Extension Manager

Commands:
  list [type]              List extensions (core|user|all)
  install <name> <path>    Install user extension
  info <name>              Show extension information
  validate <path>          Validate extension structure
  load-commands            Load all extension commands
  help                     Show this help

Extension Structure:
  extensions/
  ├── core/essential/      Core system extensions (ships with uDOS)
  ├── user/               User-installed extensions
  ├── platform/           Platform-specific extensions
  └── registry.json       Master extension registry

Examples:
  extension-manager list
  extension-manager install my-tools /path/to/extension
  extension-manager info deployment-manager
EOF
            ;;
    esac
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
