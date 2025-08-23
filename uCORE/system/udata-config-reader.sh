#!/bin/bash
# uDATA Configuration Reader
# Simple shell-based reader for uDATA format files
# Replaces the Python config_loader.py

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
UMEMORY_SYSTEM="$UDOS_ROOT/uMEMORY/system"

# uDATA file paths - Updated for clean filenames (no date stamps)
UDATA_SYSTEM_CONFIG="$UMEMORY_SYSTEM/uDATA-system-config.json"  # If exists
UDATA_CONFIG="$UMEMORY_SYSTEM/uDATA-config.json"  # If exists
UDATA_COLOURS="$UMEMORY_SYSTEM/uDATA-colours.json"
UDATA_COMMANDS="$UMEMORY_SYSTEM/uDATA-commands.json"
UDATA_USER_ROLES="$UMEMORY_SYSTEM/uDATA-user-roles.json"
UDATA_SHORTCODES="$UMEMORY_SYSTEM/uDATA-shortcodes.json"
UDATA_VARIABLES="$UMEMORY_SYSTEM/uDATA-variable-system.json"

# Function to read uDATA value by name (handles both formats)
get_udata_value() {
    local file="$1"
    local name="$2"

    if [[ ! -f "$file" ]]; then
        echo "ERROR: uDATA file not found: $file" >&2
        return 1
    fi

    # Try JSON object format first (new format)
    local value=$(jq -r --arg name "$name" '
        if .config_variables then
            .config_variables[] | select(.name == $name) | .value
        elif .system_config then
            .system_config[] | select(.name == $name) | .value
        else
            # Handle direct array format
            .[] | select(.name == $name) | .value
        end
    ' "$file" 2>/dev/null | head -1)

    # If that fails, try line-by-line format (old format)
    if [[ -z "$value" || "$value" == "null" ]]; then
        value=$(tail -n +2 "$file" | jq -r --arg name "$name" 'select(.name == $name) | .value' 2>/dev/null | head -1)
    fi

    echo "$value"
}# Function to get system configuration value
get_system_config() {
    local name="$1"
    get_udata_value "$UDATA_SYSTEM_CONFIG" "$name"
}

# Function to get general configuration value
get_config() {
    local name="$1"
    get_udata_value "$UDATA_CONFIG" "$name"
}

# Function to get color palette
get_palette_colors() {
    local palette_name="$1"

    if [[ ! -f "$UDATA_COLOURS" ]]; then
        echo "ERROR: Color data file not found" >&2
        return 1
    fi

    # Get the palette entry and extract colors
    tail -n +2 "$UDATA_COLOURS" | jq -r --arg palette "$palette_name" 'select(.name == $palette) | .colors | to_entries[] | "\(.key)=\(.value)"' 2>/dev/null
}

# Function to get default values for display
get_display_defaults() {
    echo "DISPLAY_MODE=$(get_system_config 'DEFAULT_DISPLAY_MODE')"
    echo "INTERFACE_MODE=$(get_system_config 'DEFAULT_INTERFACE_MODE')"
    echo "FONT=$(get_system_config 'DEFAULT_FONT')"
    echo "FONT_SIZE=$(get_system_config 'DEFAULT_FONT_SIZE')"
    echo "GRID_COLUMNS=$(get_system_config 'DEFAULT_GRID_COLUMNS')"
    echo "GRID_ROWS=$(get_system_config 'DEFAULT_GRID_ROWS')"
    echo "VIEWPORT_WIDTH=$(get_system_config 'DEFAULT_VIEWPORT_WIDTH')"
    echo "VIEWPORT_HEIGHT=$(get_system_config 'DEFAULT_VIEWPORT_HEIGHT')"
}

# Function to check if features are enabled
get_feature_flags() {
    echo "SMART_TERMINAL=$(get_system_config 'ENABLE_SMART_TERMINAL')"
    echo "COMMAND_HISTORY=$(get_system_config 'ENABLE_COMMAND_HISTORY')"
    echo "AUTO_COMPLETE=$(get_system_config 'ENABLE_AUTO_COMPLETE')"
    echo "FONT_SCALING=$(get_system_config 'ENABLE_FONT_SCALING')"
    echo "DEBUG_MODE=$(get_system_config 'DEBUG_MODE')"
}

# Function to get performance settings
get_performance_settings() {
    echo "CACHE_LIMIT_MB=$(get_system_config 'CACHE_LIMIT_MB')"
    echo "TERMINAL_HISTORY_LIMIT=$(get_system_config 'TERMINAL_HISTORY_LIMIT')"
}

# Function to validate uDATA files exist
validate_udata_files() {
    local errors=0

    echo "Validating uDATA configuration files..."

    for file in "$UDATA_SYSTEM_CONFIG" "$UDATA_CONFIG" "$UDATA_COLOURS" "$UDATA_COMMANDS" "$UDATA_USER_ROLES"; do
        if [[ -f "$file" ]]; then
            # Check if file has metadata line and content
            local line_count=$(wc -l < "$file")
            if [[ $line_count -gt 1 ]]; then
                echo "✓ $(basename "$file") ($line_count lines)"
            else
                echo "✗ $(basename "$file") - insufficient content"
                errors=$((errors + 1))
            fi
        else
            echo "✗ $(basename "$file") - missing"
            errors=$((errors + 1))
        fi
    done

    return $errors
}

# Function to list available commands
list_commands() {
    if [[ ! -f "$UDATA_COMMANDS" ]]; then
        echo "ERROR: Commands file not found" >&2
        return 1
    fi

    echo "Available uDOS Commands:"
    tail -n +2 "$UDATA_COMMANDS" | jq -r '.name + " - " + .description' 2>/dev/null
}

# Function to get command syntax
get_command_syntax() {
    local command_name="$1"

    if [[ ! -f "$UDATA_COMMANDS" ]]; then
        echo "ERROR: Commands file not found" >&2
        return 1
    fi

    tail -n +2 "$UDATA_COMMANDS" | jq -r --arg cmd "$command_name" 'select(.name == $cmd) | .syntax' 2>/dev/null | head -1
}

# Function to generate CSS variables from color palette
generate_css_variables() {
    local palette_name="${1:-$(get_config 'DEFAULT_PALETTE')}"

    echo "/* CSS Variables for $palette_name palette */"
    echo ":root {"

    get_palette_colors "$palette_name" | while IFS= read -r color_line; do
        if [[ -n "$color_line" ]]; then
            echo "    --${color_line};"
        fi
    done

    echo "}"
}

# Main CLI interface
main() {
    case "${1:-help}" in
        "get-system-config")
            get_system_config "$2"
            ;;
        "get-config")
            get_config "$2"
            ;;
        "get-display-defaults")
            get_display_defaults
            ;;
        "get-feature-flags")
            get_feature_flags
            ;;
        "get-performance")
            get_performance_settings
            ;;
        "validate")
            validate_udata_files
            ;;
        "list-commands")
            list_commands
            ;;
        "get-command-syntax")
            get_command_syntax "$2"
            ;;
        "generate-css")
            generate_css_variables "$2"
            ;;
        "get-palette-colors")
            get_palette_colors "$2"
            ;;
        "help"|*)
            echo "uDATA Configuration Reader"
            echo "Usage: $0 <command> [args]"
            echo ""
            echo "Commands:"
            echo "  get-system-config <name>    Get system configuration value"
            echo "  get-config <name>           Get general configuration value"
            echo "  get-display-defaults        Get all display default values"
            echo "  get-feature-flags           Get all feature flag values"
            echo "  get-performance             Get performance settings"
            echo "  validate                    Validate all uDATA files"
            echo "  list-commands               List available commands"
            echo "  get-command-syntax <cmd>    Get syntax for specific command"
            echo "  generate-css [palette]      Generate CSS variables for palette"
            echo "  get-palette-colors <name>   Get colors for specific palette"
            echo ""
            echo "Examples:"
            echo "  $0 get-system-config DEFAULT_FONT"
            echo "  $0 get-display-defaults"
            echo "  $0 generate-css polaroid_colors"
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
