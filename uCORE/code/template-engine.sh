#!/bin/bash
# uDOS Template Engine v1.0.5
# Enhanced template processing with advanced variable resolution, caching, and performance optimization

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Core components
VARIABLE_MANAGER="$UDOS_ROOT/uCORE/code/variable-manager.sh"
ADVANCED_RESOLVER="$UDOS_ROOT/uCORE/code/advanced-variable-resolver.sh"
TEMPLATE_CONFIG="$UDOS_ROOT/uMEMORY/system/template-variable-integration.json"
TEMPLATE_CACHE_DIR="$UDOS_ROOT/sandbox/cache/templates"
SYSTEM_TEMPLATES_DIR="$UDOS_ROOT/uMEMORY/system/templates"

# Create required directories
mkdir -p "$TEMPLATE_CACHE_DIR" "$SYSTEM_TEMPLATES_DIR"

# Source logging functions
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Main template processing function
process_template() {
    local template_file="$1"
    local output_file="${2:-}"
    local context="${3:-default}"
    local session_id="${4:-$(date +%s)}"

    if [[ ! -f "$template_file" ]]; then
        log_error "Template file not found: $template_file"
        return 1
    fi

    log_info "Processing template: $(basename "$template_file") with context: $context"

    # Read template content
    local template_content
    template_content="$(cat "$template_file")"

    # Process variable substitutions
    local processed_content
    processed_content="$(process_variable_substitutions "$template_content" "$context" "$session_id")"

    # Process conditional blocks
    processed_content="$(process_conditional_blocks "$processed_content" "$session_id")"

    # Process template inheritance
    processed_content="$(process_template_inheritance "$processed_content")"

    # Output result
    if [[ -n "$output_file" ]]; then
        echo "$processed_content" > "$output_file"
        log_success "Template processed and saved to: $output_file"
    else
        echo "$processed_content"
    fi
}

# Process variable substitutions with multiple patterns
process_variable_substitutions() {
    local content="$1"
    local context="$2"
    local session_id="$3"

    # Process basic variables: {VARIABLE} and formatted: {VARIABLE:format}
    content="$(process_basic_variables "$content" "$session_id" "$context")"

    # Process variables with defaults: {VARIABLE|default}
    content="$(process_default_variables "$content" "$session_id" "$context")"

    # Process formatted variables: {VARIABLE:format} (additional pass for complex formatting)
    content="$(process_formatted_variables "$content" "$session_id" "$context")"

    echo "$content"
}

# Process basic variable substitution: {VARIABLE} using advanced resolver
process_basic_variables() {
    local content="$1"
    local session_id="$2"
    local context="${3:-default}"

    # Find all {VARIABLE} patterns including formatted ones
    local variables
    variables=$(echo "$content" | grep -oE '\{[A-Z][A-Z0-9_:-]*\}' | sed 's/[{}]//g' | sort -u)

    for var in $variables; do
        if [[ -n "$var" ]]; then
            local value=""
            
            # Try advanced resolver first
            if [[ -f "$ADVANCED_RESOLVER" ]] && value=$("$ADVANCED_RESOLVER" resolve "$var" "$context" "SESSION" 2>/dev/null); then
                content="${content//\{$var\}/$value}"
            else
                # Fallback to traditional variable manager
                value=$("$VARIABLE_MANAGER" GET "$var" "$session_id" 2>/dev/null || echo "")
                
                if [[ -n "$value" ]]; then
                    content="${content//\{$var\}/$value}"
                else
                log_warning "Variable not found: $var"
                content="${content//\{$var\}/[UNDEFINED:$var]}"
            fi
        fi
    done

    echo "$content"
}

# Process variables with defaults: {VARIABLE|default}
process_default_variables() {
    local content="$1"
    local session_id="$2"

    # Find all {VARIABLE|default} patterns
    while [[ "$content" =~ \{([A-Z][A-Z0-9_-]*)\|([^}]*)\} ]]; do
        local var="${BASH_REMATCH[1]}"
        local default="${BASH_REMATCH[2]}"
        local pattern="{$var|$default}"

        local value
        value=$("$VARIABLE_MANAGER" GET "$var" "$session_id" 2>/dev/null || echo "")

        if [[ -n "$value" ]]; then
            content="${content/$pattern/$value}"
        else
            content="${content/$pattern/$default}"
        fi
    done

    echo "$content"
}

# Process formatted variables: {VARIABLE:format}
process_formatted_variables() {
    local content="$1"
    local session_id="$2"

    # Find all {VARIABLE:format} patterns
    while [[ "$content" =~ \{([A-Z][A-Z0-9_-]*):([^}]*)\} ]]; do
        local var="${BASH_REMATCH[1]}"
        local format="${BASH_REMATCH[2]}"
        local pattern="{$var:$format}"

        local value
        value=$("$VARIABLE_MANAGER" GET "$var" "$session_id" 2>/dev/null || echo "")

        if [[ -n "$value" ]]; then
            local formatted_value
            formatted_value="$(format_variable_value "$value" "$format")"
            content="${content/$pattern/$formatted_value}"
        else
            content="${content/$pattern/[UNDEFINED:$var]}"
        fi
    done

    echo "$content"
}

# Format variable value according to format specification
format_variable_value() {
    local value="$1"
    local format="$2"

    case "$format" in
        "upper")
            echo "$value" | tr '[:lower:]' '[:upper:]'
            ;;
        "lower")
            echo "$value" | tr '[:upper:]' '[:lower:]'
            ;;
        "title")
            echo "$value" | sed 's/\b\(.\)/\u\1/g'
            ;;
        "number")
            # Extract numbers from value
            echo "$value" | grep -oE '[0-9]+' | head -1
            ;;
        "boolean")
            # Convert to true/false
            local lower_value
            lower_value=$(echo "$value" | tr '[:upper:]' '[:lower:]')
            case "$lower_value" in
                "true"|"yes"|"1"|"on"|"enabled") echo "true" ;;
                *) echo "false" ;;
            esac
            ;;
        "date")
            # Format as readable date if it's a timestamp
            if [[ "$value" =~ ^[0-9]+$ ]]; then
                date -r "$value" "+%d %B %Y" 2>/dev/null || echo "$value"
            else
                echo "$value"
            fi
            ;;
        *)
            echo "$value"
            ;;
    esac
}

# Process conditional blocks: {#if VARIABLE}content{/if}
process_conditional_blocks() {
    local content="$1"
    local session_id="$2"

    # Simple approach: check for conditional blocks using grep and sed
    local temp_file="/tmp/udos-conditional-$$.tmp"
    echo "$content" > "$temp_file"

    # Find all {#if VARIABLE} patterns
    local if_vars
    if_vars=$(grep -o "{#if [A-Z][A-Z0-9_-]*}" "$temp_file" | sed 's/{#if \([A-Z][A-Z0-9_-]*\)}/\1/' | sort -u)

    for var in $if_vars; do
        if [[ -n "$var" ]]; then
            local value
            value=$("$VARIABLE_MANAGER" GET "$var" "$session_id" 2>/dev/null || echo "")

            if [[ -n "$value" && "$value" != "false" && "$value" != "0" && "$value" != "no" ]]; then
                # Variable exists and is truthy - remove the conditional tags but keep content
                sed -i.bak -e "s/{#if $var}//g" -e "s/{\/if}//g" "$temp_file"
            else
                # Variable doesn't exist or is falsy - remove entire block
                # Use a more careful approach to remove from {#if VAR} to {/if}
                awk -v var="$var" '
                BEGIN { in_block = 0 }
                $0 ~ "{#if " var "}" { in_block = 1; next }
                $0 ~ "{/if}" && in_block { in_block = 0; next }
                !in_block { print }
                ' "$temp_file" > "$temp_file.new" && mv "$temp_file.new" "$temp_file"
            fi
        fi
    done

    content=$(cat "$temp_file")
    rm -f "$temp_file" "$temp_file.bak" "$temp_file.new" 2>/dev/null

    echo "$content"
}

# Process template inheritance: {#extend template}
process_template_inheritance() {
    local content="$1"

    # Check for extend directives using grep
    if echo "$content" | grep -q "{#extend "; then
        local parent_template
        parent_template=$(echo "$content" | grep -o "{#extend [^}]*}" | head -1 | sed 's/{#extend \(.*\)}/\1/')

        if [[ -n "$parent_template" ]]; then
            local parent_file="$SYSTEM_TEMPLATES_DIR/$parent_template"
            if [[ -f "$parent_file" ]]; then
                local parent_content
                parent_content="$(cat "$parent_file")"
                # Replace the extend directive with parent content
                content=$(echo "$content" | sed "s/{#extend [^}]*}/$parent_content/")
            else
                log_warning "Parent template not found: $parent_template"
                content=$(echo "$content" | sed "s/{#extend [^}]*}/[TEMPLATE_NOT_FOUND:$parent_template]/")
            fi
        fi
    fi

    echo "$content"
}

# Render template for CLI display
render_cli_template() {
    local template_file="$1"
    local context="${2:-cli}"
    local session_id="${3:-$(date +%s)}"

    log_info "Rendering CLI template: $(basename "$template_file")"

    # Process template and apply CLI-specific formatting
    local content
    content="$(process_template "$template_file" "" "$context" "$session_id")"

    # Apply CLI color codes and formatting
    content="$(apply_cli_formatting "$content")"

    echo "$content"
}

# Apply CLI-specific formatting
apply_cli_formatting() {
    local content="$1"

    # Apply color codes using sed
    content=$(echo "$content" | sed "s/\[INFO\]/$(tput setaf 6)[INFO]$(tput sgr0)/g")
    content=$(echo "$content" | sed "s/\[SUCCESS\]/$(tput setaf 2)[SUCCESS]$(tput sgr0)/g")
    content=$(echo "$content" | sed "s/\[WARNING\]/$(tput setaf 3)[WARNING]$(tput sgr0)/g")
    content=$(echo "$content" | sed "s/\[ERROR\]/$(tput setaf 1)[ERROR]$(tput sgr0)/g")

    # Apply text formatting using sed
    content=$(echo "$content" | sed "s/\*\*\([^*]*\)\*\*/$(tput bold)\1$(tput sgr0)/g")
    content=$(echo "$content" | sed "s/\*\([^*]*\)\*/$(tput smul)\1$(tput rmul)/g")

    echo "$content"
}

# Generate template from variable definitions
generate_template_from_variables() {
    local template_name="$1"
    local variables_list="$2"
    local context="${3:-default}"

    log_info "Generating template: $template_name"

    local template_file="$SYSTEM_TEMPLATES_DIR/generated/$template_name.md"
    mkdir -p "$(dirname "$template_file")"

    cat > "$template_file" << EOF
# Generated Template: $template_name
# Context: $context
# Generated: $(date)

EOF

    # Add variable sections
    IFS=',' read -ra VARS <<< "$variables_list"
    for var in "${VARS[@]}"; do
        var=$(echo "$var" | xargs) # trim whitespace
        echo "- **$var**: {$var|Not Set}" >> "$template_file"
    done

    log_success "Template generated: $template_file"
    echo "$template_file"
}

# Create role-specific template variant
create_role_template() {
    local base_template="$1"
    local role="$2"
    local session_id="${3:-$(date +%s)}"

    if [[ ! -f "$base_template" ]]; then
        log_error "Base template not found: $base_template"
        return 1
    fi

    local role_template="$SYSTEM_TEMPLATES_DIR/roles/$(basename "$base_template" .md)-$role.md"
    mkdir -p "$(dirname "$role_template")"

    # Process base template with role context
    local content
    content="$(process_template "$base_template" "" "role_$role" "$session_id")"

    # Add role-specific header
    cat > "$role_template" << EOF
{#extend base/role-header.md}

# Role-Specific Template for $role

$content
EOF

    log_success "Role template created: $role_template"
    echo "$role_template"
}

# Cache processed template
cache_template() {
    local template_file="$1"
    local processed_content="$2"
    local context="$3"

    local cache_file="$TEMPLATE_CACHE_DIR/$(basename "$template_file" .md)-$context-$(date +%s).cache"
    echo "$processed_content" > "$cache_file"

    log_info "Template cached: $cache_file"
}

# Main command dispatcher
main() {
    case "${1:-}" in
        "process")
            process_template "${2:-}" "${3:-}" "${4:-default}" "${5:-$(date +%s)}"
            ;;
        "render-cli")
            render_cli_template "${2:-}" "${3:-cli}" "${4:-$(date +%s)}"
            ;;
        "generate")
            generate_template_from_variables "${2:-}" "${3:-}" "${4:-default}"
            ;;
        "role-template")
            create_role_template "${2:-}" "${3:-}" "${4:-$(date +%s)}"
            ;;
        "test")
            test_template_engine
            ;;
        "help"|"")
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Test template engine functionality
test_template_engine() {
    log_info "Testing Template Engine functionality..."

    # Create test template
    local test_template="$TEMPLATE_CACHE_DIR/test-template.md"
    cat > "$test_template" << 'EOF'
# Test Template

## User Information
- **Role**: {USER-ROLE}
- **Level**: {USER-LEVEL:number}
- **Display**: {DISPLAY-MODE|CLI}

## Project Context
- **Name**: {PROJECT-NAME|No Project}

{#if DEV-MODE}
## Development Mode Active
- **Debug Level**: {DEBUG-LEVEL}
{/if}

## Status
This is a **test template** with *formatting*.
[INFO] Template processing successful!
EOF

    # Process test template
    log_info "Processing test template..."
    process_template "$test_template" "$TEMPLATE_CACHE_DIR/test-output.md" "test"

    # Display result
    log_success "Template processing test completed"
    cat "$TEMPLATE_CACHE_DIR/test-output.md"
}

# Show help information
show_help() {
    cat << 'EOF'
uDOS Template Engine v1.0.4.1

USAGE:
    template-engine.sh <command> [args...]

COMMANDS:
    process <template> [output] [context] [session]
        Process template with variable substitution

    render-cli <template> [context] [session]
        Render template for CLI display with formatting

    generate <name> <variables> [context]
        Generate template from variable list

    role-template <template> <role> [session]
        Create role-specific template variant

    test
        Run template engine functionality tests

    help
        Show this help information

VARIABLE PATTERNS:
    {VARIABLE}           - Basic substitution
    {VARIABLE|default}   - With default value
    {VARIABLE:format}    - With formatting (upper, lower, number, etc.)
    {#if VARIABLE}...{/if} - Conditional content
    {#extend template}   - Template inheritance

EXAMPLES:
    # Process command help template
    template-engine.sh process templates/help/command-help.md output.md cli

    # Generate template from variables
    template-engine.sh generate user-info "USER-ROLE,USER-LEVEL,PROJECT-NAME"

    # Create role-specific variant
    template-engine.sh role-template templates/dashboard.md WIZARD

EOF
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
