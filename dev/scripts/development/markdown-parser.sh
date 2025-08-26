#!/bin/bash
# uDOS Markdown Parser - Development Script
# Extracted from Markdown-Spec.md for future development

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Source logging functions
source "$UDOS_ROOT/uCORE/core/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Main parser function
parse_udos_markdown() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi

    local content=$(cat "$file")

    log_info "Processing markdown file: $file"

    # Extract front matter
    extract_front_matter "$content"

    # Process shortcodes
    process_shortcodes "$content"

    # Render ASCII art
    render_ascii_art "$content"

    # Apply colors
    apply_color_codes "$content"

    # Generate output
    generate_output "$content"
}

# Extract YAML front matter
extract_front_matter() {
    local content="$1"

    if [[ "$content" =~ ^---[[:space:]]*$ ]]; then
        log_info "Front matter detected"
        # Extract YAML between --- markers
        echo "$content" | sed -n '2,/^---$/p' | head -n -1
    fi
}

# Process uCODE shortcodes [COMMAND|ARGS]
process_shortcodes() {
    local content="$1"

    log_info "Processing shortcodes"

    # Match [COMMAND|ARGS] pattern
    echo "$content" | sed -E 's/\[([^|]+)\|([^]]+)\]/$(execute_shortcode "\1" "\2")/g'
}

# Execute individual shortcode
execute_shortcode() {
    local command="$1"
    local args="$2"

    log_info "Executing shortcode: [$command|$args]"

    case "$command" in
        "MEM")
            handle_memory_command "$args"
            ;;
        "MISSION")
            handle_mission_command "$args"
            ;;
        "GRID")
            handle_grid_command "$args"
            ;;
        "STATUS")
            handle_status_command "$args"
            ;;
        *)
            log_warning "Unknown command: $command"
            echo "[UNKNOWN: $command|$args]"
            ;;
    esac
}

# Handle memory commands
handle_memory_command() {
    local args="$1"

    case "$args" in
        "LIST")
            echo "Memory files: $(ls "$UDOS_ROOT/uMEMORY/user/" 2>/dev/null | wc -l)"
            ;;
        "VIEW|"*)
            local file="${args#VIEW|}"
            echo "Viewing: $file"
            ;;
        *)
            echo "Memory command: $args"
            ;;
    esac
}

# Handle mission commands
handle_mission_command() {
    local args="$1"
    echo "Mission command: $args"
}

# Handle grid commands
handle_grid_command() {
    local args="$1"
    echo "Grid command: $args"
}

# Handle status commands
handle_status_command() {
    local args="$1"
    echo "System status: Active"
}

# Render ASCII art blocks
render_ascii_art() {
    local content="$1"

    log_info "Rendering ASCII art"

    # Look for ```ascii blocks
    echo "$content" | sed -n '/```ascii/,/```/p'
}

# Apply color codes
apply_color_codes() {
    local content="$1"

    log_info "Applying color codes"

    # Replace {.color} tags with ANSI codes
    echo "$content" | \
        sed -E 's/\{\.red\}([^{]*)\{\/[^}]*\}/\x1b[31m\1\x1b[0m/g' | \
        sed -E 's/\{\.green\}([^{]*)\{\/[^}]*\}/\x1b[32m\1\x1b[0m/g' | \
        sed -E 's/\{\.yellow\}([^{]*)\{\/[^}]*\}/\x1b[33m\1\x1b[0m/g' | \
        sed -E 's/\{\.blue\}([^{]*)\{\/[^}]*\}/\x1b[34m\1\x1b[0m/g' | \
        sed -E 's/\{\.purple\}([^{]*)\{\/[^}]*\}/\x1b[35m\1\x1b[0m/g' | \
        sed -E 's/\{\.cyan\}([^{]*)\{\/[^}]*\}/\x1b[36m\1\x1b[0m/g'
}

# Generate final output
generate_output() {
    local content="$1"

    log_info "Generating output"
    echo "$content"
}

# Test function
test_parser() {
    local test_file="/tmp/test_markdown.md"

    cat > "$test_file" << 'EOF'
---
type: test
created: 2025-08-25
---

# Test Document

This is a test with [MEM|LIST] shortcode.

```ascii
┌─── TEST ───┐
│   ASCII    │
└────────────┘
```

{.green}Success message{/green}
EOF

    log_info "Testing parser with sample file"
    parse_udos_markdown "$test_file"

    rm -f "$test_file"
}

# Main execution
main() {
    case "${1:-}" in
        "test")
            test_parser
            ;;
        "parse")
            if [[ -z "${2:-}" ]]; then
                log_error "Usage: $0 parse <file.md>"
                exit 1
            fi
            parse_udos_markdown "$2"
            ;;
        *)
            log_info "uDOS Markdown Parser - Development Tool"
            log_info "Usage:"
            log_info "  $0 test              # Run test with sample file"
            log_info "  $0 parse <file.md>   # Parse specific file"
            ;;
    esac
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
