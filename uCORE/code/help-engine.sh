#!/bin/bash
# uDOS Help Engine
# Unified command help system with uDATA format support

# Set script directory and load core functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SYSTEM_DIR="$UDOS_ROOT/uMEMORY/system"

# Load system configuration if available
source "$UDOS_ROOT/uCORE/core/core-functions.sh" 2>/dev/null || {
    # Fallback logging functions if core-functions not available
    log_info() { echo "[INFO] $*"; }
    log_error() { echo "[ERROR] $*" >&2; }
    log_success() { echo "[SUCCESS] $*"; }
    log_warn() { echo "[WARN] $*"; }
}

# Color definitions for enhanced output
HEADER="\033[1;36m"     # Cyan bold
COMMAND="\033[1;33m"    # Yellow bold
SYNTAX="\033[0;32m"     # Green
EXAMPLE="\033[0;35m"    # Magenta
ERROR="\033[1;31m"      # Red bold
SUCCESS="\033[1;32m"    # Green bold
INFO="\033[0;36m"       # Cyan
RESET="\033[0m"         # Reset

# Global variables
CURRENT_ROLE="${USER_ROLE:-DRONE}"
COMMAND_CACHE_FILE="$SYSTEM_DIR/temp/command-cache.json"
UDATA_COMMANDS_FILE="$UDOS_ROOT/uMEMORY/system/uDATA-commands.json"
HELP_SESSION_LOG="$SYSTEM_DIR/temp/help-session.log"

# Ensure temp directory exists
mkdir -p "$SYSTEM_DIR/temp"

# Initialize help engine
init_help_engine() {
    log_info "Initializing uDOS Help Engine with uDATA format support"

    # Check if uDATA command file exists
    if [[ ! -f "$UDATA_COMMANDS_FILE" ]]; then
        log_error "uDATA command system file not found: $UDATA_COMMANDS_FILE"
        return 1
    fi

    # Validate uDATA format
    if ! validate_udata_format; then
        log_error "Invalid uDATA format in commands file"
        return 1
    fi

    # Create command index cache
    if ! create_command_index; then
        log_warn "Failed to create command index cache"
    fi

    log_success "Help engine initialized successfully"
    return 0
}

# Validate uDATA format
validate_udata_format() {
    local line_count=$(wc -l < "$UDATA_COMMANDS_FILE")

    if [[ $line_count -lt 2 ]]; then
        log_error "uDATA file must have at least 2 lines (metadata + data)"
        return 1
    fi

    # Check metadata line
    if ! head -1 "$UDATA_COMMANDS_FILE" | jq -e '.metadata' >/dev/null 2>&1; then
        log_error "First line must contain valid metadata"
        return 1
    fi

    # Check data lines
    if ! tail -n +2 "$UDATA_COMMANDS_FILE" | jq -e '.command' >/dev/null 2>&1; then
        log_error "Data lines must contain valid command objects"
        return 1
    fi

    log_info "uDATA format validation passed ($line_count lines)"
    return 0
}

# Create searchable command index from uDATA format
create_command_index() {
    local cache_file="$COMMAND_CACHE_FILE"

    log_info "Creating command index cache from uDATA format..."

    # Get metadata
    local metadata=$(head -1 "$UDATA_COMMANDS_FILE")
    local command_count=$(echo "$metadata" | jq -r '.metadata.command_count // 0')

    # Create cache file header
    cat > "$cache_file" << EOF
{
    "last_updated": "$(date +"%Y-%m-%d %H:%M:%S")",
    "current_role": "$CURRENT_ROLE",
    "source_format": "uDATA-v1",
    "command_count": $command_count,
    "commands": [
EOF

    # Process uDATA commands (skip first metadata line)
    tail -n +2 "$UDATA_COMMANDS_FILE" | jq -c '{
        "command": .command,
        "category": .category,
        "description": .description,
        "syntax": .syntax,
        "args": .args,
        "examples": .examples
    }' | sed '$!s/$/,/' >> "$cache_file"

    # Close the JSON structure
    echo '    ]
}' >> "$cache_file"

    if [[ $? -eq 0 ]]; then
        log_success "Command index cache created: $cache_file"
        return 0
    else
        log_error "Failed to create command index cache"
        return 1
    fi
}

# Get all commands from uDATA format
get_all_commands() {
    tail -n +2 "$UDATA_COMMANDS_FILE" | jq -c '.'
}

# Filter commands by category
filter_by_category() {
    local category="$1"

    if [[ -z "$category" ]]; then
        log_error "Category parameter required"
        return 1
    fi

    tail -n +2 "$UDATA_COMMANDS_FILE" | jq --arg cat "$category" -c '
    select(.category == $cat)
    '
}

# Get command details by name
get_command_details() {
    local command="$1"

    if [[ -z "$command" ]]; then
        log_error "Command parameter required"
        return 1
    fi

    # Convert to uppercase for consistency
    command=$(echo "$command" | tr '[:lower:]' '[:upper:]')

    tail -n +2 "$UDATA_COMMANDS_FILE" | jq --arg cmd "$command" -c '
    select(.command == $cmd)
    '
}

# Get list of available categories
get_categories() {
    tail -n +2 "$UDATA_COMMANDS_FILE" | jq -r '.category' | sort | uniq
}

# Search commands by keyword
search_commands() {
    local keyword="$1"

    if [[ -z "$keyword" ]]; then
        log_error "Search keyword required"
        return 1
    fi

    tail -n +2 "$UDATA_COMMANDS_FILE" | jq --arg keyword "$keyword" -c '
    select(
        (.command | test($keyword; "i")) or
        (.description | test($keyword; "i")) or
        (.syntax | test($keyword; "i"))
    )
    '
}

# Display command help with formatting
display_command_help() {
    local command="$1"
    local details

    if [[ -z "$command" ]]; then
        log_error "Command name required"
        return 1
    fi

    details=$(get_command_details "$command")

    if [[ -z "$details" ]]; then
        echo -e "${ERROR}Command '$command' not found${RESET}"
        return 1
    fi

    # Extract details
    local cmd_name=$(echo "$details" | jq -r '.command')
    local cmd_syntax=$(echo "$details" | jq -r '.syntax')
    local cmd_desc=$(echo "$details" | jq -r '.description')
    local cmd_category=$(echo "$details" | jq -r '.category')
    local cmd_args=$(echo "$details" | jq -r '.args[]?' | tr '\n' ' ')
    local cmd_examples=$(echo "$details" | jq -r '.examples[]?')

    # Display formatted help
    echo
    echo -e "${HEADER}━━━ uDOS Command Help ━━━${RESET}"
    echo
    echo -e "${COMMAND}Command:${RESET}    $cmd_name"
    echo -e "${COMMAND}Category:${RESET}   $cmd_category"
    echo -e "${COMMAND}Description:${RESET} $cmd_desc"
    echo
    echo -e "${SYNTAX}Syntax:${RESET}     $cmd_syntax"

    if [[ -n "$cmd_args" ]]; then
        echo -e "${SYNTAX}Arguments:${RESET}  $cmd_args"
    fi

    if [[ -n "$cmd_examples" ]]; then
        echo
        echo -e "${EXAMPLE}Examples:${RESET}"
        while IFS= read -r example; do
            [[ -n "$example" ]] && echo -e "  ${EXAMPLE}$example${RESET}"
        done <<< "$cmd_examples"
    fi

    echo
}

# Display command list by category
display_category_help() {
    local category="$1"

    if [[ -z "$category" ]]; then
        echo -e "${ERROR}Category required${RESET}"
        return 1
    fi

    echo
    echo -e "${HEADER}━━━ Commands in Category: $category ━━━${RESET}"
    echo

    filter_by_category "$category" | while IFS= read -r cmd_data; do
        local cmd_name=$(echo "$cmd_data" | jq -r '.command')
        local cmd_desc=$(echo "$cmd_data" | jq -r '.description')
        local cmd_syntax=$(echo "$cmd_data" | jq -r '.syntax')

        echo -e "${COMMAND}$cmd_name${RESET} - $cmd_desc"
        echo -e "  ${SYNTAX}$cmd_syntax${RESET}"
        echo
    done
}

# Display all available commands
display_all_commands() {
    echo
    echo -e "${HEADER}━━━ All uDOS Commands ━━━${RESET}"
    echo

    # Group by category
    for category in $(get_categories); do
        echo -e "${INFO}▶ $category${RESET}"
        filter_by_category "$category" | while IFS= read -r cmd_data; do
            local cmd_name=$(echo "$cmd_data" | jq -r '.command')
            local cmd_desc=$(echo "$cmd_data" | jq -r '.description')
            echo -e "  ${COMMAND}$cmd_name${RESET} - $cmd_desc"
        done
        echo
    done
}

# Search and display results
display_search_results() {
    local keyword="$1"
    local results

    if [[ -z "$keyword" ]]; then
        log_error "Search keyword required"
        return 1
    fi

    results=$(search_commands "$keyword")

    if [[ -z "$results" ]]; then
        echo -e "${ERROR}No commands found matching: $keyword${RESET}"
        return 1
    fi

    echo
    echo -e "${HEADER}━━━ Search Results for: $keyword ━━━${RESET}"
    echo

    echo "$results" | while IFS= read -r cmd_data; do
        local cmd_name=$(echo "$cmd_data" | jq -r '.command')
        local cmd_desc=$(echo "$cmd_data" | jq -r '.description')
        local cmd_syntax=$(echo "$cmd_data" | jq -r '.syntax')

        echo -e "${COMMAND}$cmd_name${RESET} - $cmd_desc"
        echo -e "  ${SYNTAX}$cmd_syntax${RESET}"
        echo
    done
}

# Main help function
main_help() {
    local command="$1"
    local option="$2"

    case "$command" in
        "COMMANDS"|"LIST")
            display_all_commands
            ;;
        "SEARCH")
            if [[ -n "$option" ]]; then
                display_search_results "$option"
            else
                echo -e "${ERROR}Search keyword required: [HELP|SEARCH*keyword]${RESET}"
            fi
            ;;
        "CATEGORY")
            if [[ -n "$option" ]]; then
                display_category_help "$option"
            else
                echo -e "${INFO}Available categories:${RESET}"
                get_categories | while read -r cat; do
                    echo -e "  ${COMMAND}$cat${RESET}"
                done
            fi
            ;;
        *)
            if [[ -n "$command" ]]; then
                display_command_help "$command"
            else
                display_all_commands
            fi
            ;;
    esac
}

# CLI interface
main() {
    case "${1:-help}" in
        "init")
            init_help_engine
            ;;
        "command"|"cmd")
            display_command_help "$2"
            ;;
        "category"|"cat")
            display_category_help "$2"
            ;;
        "search")
            display_search_results "$2"
            ;;
        "list"|"all")
            display_all_commands
            ;;
        "validate")
            validate_udata_format
            ;;
        "cache")
            create_command_index
            ;;
        "help"|*)
            echo "uDOS Help Engine - uDATA Format Support"
            echo "Usage: $0 <command> [args]"
            echo ""
            echo "Commands:"
            echo "  init                    Initialize help engine"
            echo "  command <name>          Show help for specific command"
            echo "  category <name>         Show commands in category"
            echo "  search <keyword>        Search commands by keyword"
            echo "  list                    Show all commands"
            echo "  validate                Validate uDATA format"
            echo "  cache                   Rebuild command cache"
            echo ""
            echo "Examples:"
            echo "  $0 command CHECK"
            echo "  $0 category system"
            echo "  $0 search grid"
            ;;
    esac
}

# Export functions for use by other scripts
export -f get_command_details
export -f filter_by_category
export -f search_commands
export -f display_command_help

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
