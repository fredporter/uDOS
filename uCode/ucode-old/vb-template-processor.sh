#!/bin/bash
# vb-template-processor.sh - VB Command Template Processing System
# Generates VB commands from templates with full uDOS integration
# Version: 2.0.0

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
UMEM="${UHOME}/uMemory"
UTEMPLATE="${UHOME}/uTemplate"

# Template system integration
DISPLAY_VARS="${UMEM}/config/display-vars.sh"
VB_TEMPLATE_DIR="${UTEMPLATE}/vb-templates"
VB_GENERATED_DIR="${UMEM}/vb-generated"
VB_COMMANDS_CONFIG="${UTEMPLATE}/datasets/vb-commands.json"

# Load display configuration if available
[[ -f "$DISPLAY_VARS" ]] && source "$DISPLAY_VARS" 2>/dev/null || true

# Color helpers for visibility
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }
dim() { echo -e "\033[2m$1\033[0m"; }

# Template processing state
VB_TEMPLATE_VARIABLES=""
VB_CURRENT_CONTEXT=""
VB_PROCESSING_MODE="standard"

# Initialize VB template processor
init_vb_template_processor() {
    bold "🎨 VB Command Template Processor v2.0.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Create required directories
    mkdir -p "$VB_TEMPLATE_DIR" "$VB_GENERATED_DIR"
    mkdir -p "$VB_GENERATED_DIR/commands" "$VB_GENERATED_DIR/sets" "$VB_GENERATED_DIR/examples"
    
    # Load user context and system variables
    load_user_context
    load_system_variables
    load_grid_context
    
    green "✅ VB Template Processor initialized"
    show_template_status
}

# Load user context from identity
load_user_context() {
    cyan "👤 Loading user context..."
    
    local identity_file="${UMEM}/user/identity.md"
    local variables_file="${UMEM}/user/variables.json"
    
    # Default values
    local username="wizard"
    local location="Unknown"
    local timezone="UTC"
    local grid_position="A1"
    
    # Load from identity file if available
    if [[ -f "$identity_file" ]]; then
        username=$(grep -E "^Name:|^Username:" "$identity_file" | head -1 | cut -d':' -f2 | xargs || echo "wizard")
        location=$(grep "Location:" "$identity_file" | cut -d':' -f2 | xargs || echo "Unknown")
        timezone=$(grep "Timezone:" "$identity_file" | cut -d':' -f2 | xargs || echo "UTC")
    fi
    
    # Store in template variables
    vb_set_template_var "username" "$username"
    vb_set_template_var "location" "$location"
    vb_set_template_var "timezone" "$timezone"
    vb_set_template_var "grid_position" "$grid_position"
    
    echo "  👤 User: $username"
    echo "  📍 Location: $location"
    echo "  🕐 Timezone: $timezone"
    echo "  🎯 Grid: $grid_position"
}

# Load system variables
load_system_variables() {
    cyan "⚙️  Loading system variables..."
    
    local timestamp=$(date -Iseconds)
    local date_only=$(date '+%Y-%m-%d')
    local time_only=$(date '+%H:%M:%S')
    
    # System context
    vb_set_template_var "timestamp" "$timestamp"
    vb_set_template_var "date" "$date_only"
    vb_set_template_var "time" "$time_only"
    vb_set_template_var "uhome" "$UHOME"
    vb_set_template_var "umem" "$UMEM"
    vb_set_template_var "utemplate" "$UTEMPLATE"
    
    # VB system variables
    vb_set_template_var "vb_version" "2.0.0"
    vb_set_template_var "template_version" "2.0.0"
    vb_set_template_var "processor_version" "2.0.0"
    
    echo "  📅 Timestamp: $timestamp"
    echo "  🏠 uDOS Home: $UHOME"
    echo "  🧠 Memory: $UMEM"
}

# Load grid context
load_grid_context() {
    cyan "🗺️  Loading grid context..."
    
    # Use display configuration if available
    local grid_mode="${UDOS_GRID_MODE:-standard}"
    local grid_cols="${UDOS_GRID_COLS_MAX:-26}"
    local grid_rows="${UDOS_GRID_ROWS_MAX:-99}"
    local cell_width="${UDOS_GRID_CELL_WIDTH:-4}"
    local cell_height="${UDOS_GRID_CELL_HEIGHT:-2}"
    
    vb_set_template_var "grid_mode" "$grid_mode"
    vb_set_template_var "grid_cols_max" "$grid_cols"
    vb_set_template_var "grid_rows_max" "$grid_rows"
    vb_set_template_var "grid_cell_width" "$cell_width"
    vb_set_template_var "grid_cell_height" "$cell_height"
    
    echo "  🎲 Grid Mode: $grid_mode"
    echo "  📏 Grid Size: ${grid_cols}×${grid_rows}"
    echo "  🧱 Cell Size: ${cell_width}×${cell_height}"
}

# Set template variable
vb_set_template_var() {
    local var_name="$1"
    local var_value="$2"
    
    # Remove existing variable if it exists
    VB_TEMPLATE_VARIABLES=$(echo "$VB_TEMPLATE_VARIABLES" | grep -v "^${var_name}:" || true)
    
    # Add new variable
    if [[ -z "$VB_TEMPLATE_VARIABLES" ]]; then
        VB_TEMPLATE_VARIABLES="${var_name}:${var_value}"
    else
        VB_TEMPLATE_VARIABLES="${VB_TEMPLATE_VARIABLES}|${var_name}:${var_value}"
    fi
}

# Get template variable
vb_get_template_var() {
    local var_name="$1"
    local var_info=$(echo "$VB_TEMPLATE_VARIABLES" | tr '|' '\n' | grep "^${var_name}:" || echo "")
    if [[ -n "$var_info" ]]; then
        echo "$var_info" | cut -d':' -f2-
    fi
}

# Process template with variable substitution
process_template() {
    local template_file="$1"
    local output_file="$2"
    local context="${3:-standard}"
    
    cyan "🎨 Processing template: $(basename "$template_file")"
    
    if [[ ! -f "$template_file" ]]; then
        red "❌ Template file not found: $template_file"
        return 1
    fi
    
    # Read template content
    local template_content=$(cat "$template_file")
    
    # Process all template variables using bash substitution
    while IFS='|' read -ra VARS; do
        for var_pair in "${VARS[@]}"; do
            if [[ -n "$var_pair" && "$var_pair" == *":"* ]]; then
                local var_name=$(echo "$var_pair" | cut -d':' -f1)
                local var_value=$(echo "$var_pair" | cut -d':' -f2-)
                
                # Use bash parameter expansion for safe replacement
                template_content="${template_content//\{\{${var_name}\}\}/${var_value}}"
            fi
        done
    done <<< "$VB_TEMPLATE_VARIABLES"
    
    # Write processed template
    echo "$template_content" > "$output_file"
    
    echo "  📄 Generated: $(basename "$output_file")"
    echo "  📍 Path: $output_file"
    
    return 0
}

# Generate VB command from template
generate_vb_command() {
    local command_name="$1"
    local template_type="${2:-command}"
    local output_name="${3:-$command_name}"
    
    bold "🌀 Generating VB Command: $command_name"
    
    # Set command-specific variables
    vb_set_template_var "command_name" "$command_name"
    vb_set_template_var "command_type" "$template_type"
    vb_set_template_var "output_name" "$output_name"
    
    # Determine template file
    local template_file
    case "$template_type" in
        "command")
            template_file="${UTEMPLATE}/vb-command-template.md"
            ;;
        "set")
            template_file="${UTEMPLATE}/vb-command-set-template.md"
            ;;
        *)
            red "❌ Unknown template type: $template_type"
            return 1
            ;;
    esac
    
    # Generate output file path
    local output_dir="${VB_GENERATED_DIR}/${template_type}s"
    local output_file="${output_dir}/${output_name}.md"
    
    # Ensure output directory exists
    mkdir -p "$output_dir"
    
    # Process template
    process_template "$template_file" "$output_file" "$template_type"
    
    green "✅ VB command generated: $command_name"
    echo "   📄 File: $output_file"
}

# Generate VB command set
generate_vb_command_set() {
    local set_name="$1"
    local commands_list="$2"
    local set_type="${3:-standard}"
    
    bold "📦 Generating VB Command Set: $set_name"
    
    # Set command set variables
    vb_set_template_var "command_set_name" "$set_name"
    vb_set_template_var "command_set_type" "$set_type"
    vb_set_template_var "set_version" "1.0.0"
    
    # Count commands
    local command_count=$(echo "$commands_list" | tr ',' '\n' | wc -l | xargs)
    vb_set_template_var "command_count" "$command_count"
    
    # Generate individual commands
    local commands_generated=0
    while IFS=',' read -ra COMMANDS; do
        for command in "${COMMANDS[@]}"; do
            command=$(echo "$command" | xargs)  # Trim whitespace
            if [[ -n "$command" ]]; then
                generate_vb_command "$command" "command" "${set_name}-${command}"
                ((commands_generated++))
            fi
        done
    done <<< "$commands_list"
    
    # Generate command set template
    generate_vb_command "$set_name" "set" "$set_name"
    
    green "✅ VB command set generated: $set_name"
    echo "   📊 Commands: $commands_generated"
    echo "   📦 Set file: ${VB_GENERATED_DIR}/sets/${set_name}.md"
}

# Show template processor status
show_template_status() {
    echo
    bold "📊 VB Template Processor Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Count template variables
    local var_count=0
    if [[ -n "$VB_TEMPLATE_VARIABLES" ]]; then
        var_count=$(echo "$VB_TEMPLATE_VARIABLES" | tr '|' '\n' | wc -l | xargs)
    fi
    
    # Count generated files
    local command_count=0
    local set_count=0
    
    if [[ -d "${VB_GENERATED_DIR}/commands" ]]; then
        command_count=$(find "${VB_GENERATED_DIR}/commands" -name "*.md" 2>/dev/null | wc -l | xargs)
    fi
    
    if [[ -d "${VB_GENERATED_DIR}/sets" ]]; then
        set_count=$(find "${VB_GENERATED_DIR}/sets" -name "*.md" 2>/dev/null | wc -l | xargs)
    fi
    
    echo "📊 Template Variables: $var_count"
    echo "🌀 Generated Commands: $command_count"
    echo "📦 Generated Sets: $set_count"
    echo "📁 Output Directory: $VB_GENERATED_DIR"
    echo
}

# List available templates
list_templates() {
    bold "📋 Available VB Templates"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    echo "🎨 Core Templates:"
    if [[ -f "${UTEMPLATE}/vb-command-template.md" ]]; then
        echo "  ✅ vb-command-template.md - Individual command template"
    else
        echo "  ❌ vb-command-template.md - Missing"
    fi
    
    if [[ -f "${UTEMPLATE}/vb-command-set-template.md" ]]; then
        echo "  ✅ vb-command-set-template.md - Command set template"
    else
        echo "  ❌ vb-command-set-template.md - Missing"
    fi
    
    echo
    echo "📁 Custom Templates:"
    if [[ -d "$VB_TEMPLATE_DIR" ]]; then
        local custom_count=$(find "$VB_TEMPLATE_DIR" -name "*.md" 2>/dev/null | wc -l | xargs)
        if [[ "$custom_count" -gt 0 ]]; then
            find "$VB_TEMPLATE_DIR" -name "*.md" | while read -r template; do
                echo "  📄 $(basename "$template")"
            done
        else
            echo "  📁 No custom templates found"
        fi
    else
        echo "  📁 Custom template directory not created"
    fi
    echo
}

# Interactive VB command generator
interactive_generator() {
    bold "🎯 Interactive VB Command Generator"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Command name
    echo -n "📝 Command name: "
    read -r command_name
    
    if [[ -z "$command_name" ]]; then
        red "❌ Command name is required"
        return 1
    fi
    
    # Command type
    echo
    echo "🎯 Command type:"
    echo "  1) Individual command"
    echo "  2) Command set"
    echo -n "Select (1-2): "
    read -r type_choice
    
    case "$type_choice" in
        "1")
            generate_vb_command "$command_name" "command"
            ;;
        "2")
            echo -n "📦 Commands in set (comma-separated): "
            read -r commands_list
            generate_vb_command_set "$command_name" "$commands_list"
            ;;
        *)
            red "❌ Invalid selection"
            return 1
            ;;
    esac
    
    echo
    green "✅ Generation complete!"
    show_template_status
}

# Main execution
case "${1:-help}" in
    "init"|"setup")
        init_vb_template_processor
        ;;
    "generate"|"gen")
        if [[ $# -lt 2 ]]; then
            red "❌ Usage: $0 generate <command_name> [type] [output_name]"
            exit 1
        fi
        init_vb_template_processor >/dev/null
        generate_vb_command "$2" "${3:-command}" "${4:-$2}"
        ;;
    "set"|"command-set")
        if [[ $# -lt 3 ]]; then
            red "❌ Usage: $0 set <set_name> <commands_list>"
            exit 1
        fi
        init_vb_template_processor >/dev/null
        generate_vb_command_set "$2" "$3" "${4:-standard}"
        ;;
    "interactive"|"int")
        init_vb_template_processor
        interactive_generator
        ;;
    "status"|"show")
        init_vb_template_processor >/dev/null
        show_template_status
        ;;
    "list"|"templates")
        list_templates
        ;;
    "test")
        init_vb_template_processor
        echo
        bold "🧪 Testing VB Template Processing"
        echo
        
        # Test individual command
        generate_vb_command "TEST_CMD" "command" "test-command"
        
        # Test command set
        generate_vb_command_set "TEST_SET" "CMD1,CMD2,CMD3" "test"
        
        show_template_status
        ;;
    "help"|"-h"|"--help")
        bold "🎨 VB Template Processor v2.0.0"
        echo
        echo "Usage: $0 [command] [options]"
        echo
        echo "Commands:"
        echo "  init                     Initialize template processor"
        echo "  generate <name> [type]   Generate VB command from template"
        echo "  set <name> <commands>    Generate VB command set"
        echo "  interactive              Interactive command generator"
        echo "  status                   Show processor status"
        echo "  list                     List available templates"
        echo "  test                     Test template processing"
        echo "  help                     Show this help message"
        echo
        echo "Examples:"
        echo "  $0 generate USER_LOGIN command"
        echo "  $0 set BASIC_COMMANDS 'DIM,SET,IF,FOR'"
        echo "  $0 interactive"
        echo
        ;;
    *)
        red "❌ Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
