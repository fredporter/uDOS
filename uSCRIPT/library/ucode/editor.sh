#!/bin/bash
# uDOS Editor Integration Module v1.3
# Multi-mode editor integration with external editor support

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
UMEMORY="$UDOS_ROOT/uMEMORY"
SANDBOX="$UDOS_ROOT/sandbox"
USCRIPT="$UDOS_ROOT/uSCRIPT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

# Editor modes
EDITOR_MODES=("MARKDOWN" "USCRIPT" "COMMAND" "CONFIG" "JSON")

# Default editors by type
DEFAULT_EDITORS=()
DEFAULT_EDITORS["markdown"]="nano"
DEFAULT_EDITORS["uscript"]="nano"
DEFAULT_EDITORS["config"]="nano"
DEFAULT_EDITORS["json"]="nano"

# Editor preferences file
EDITOR_PREFS="$SANDBOX/.editor_preferences"

# Log functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Load editor preferences
load_editor_preferences() {
    if [[ -f "$EDITOR_PREFS" ]]; then
        source "$EDITOR_PREFS"
    else
        # Create default preferences
        create_default_preferences
    fi
}

# Create default editor preferences
create_default_preferences() {
    cat > "$EDITOR_PREFS" << 'EOF'
# uDOS Editor Preferences
# Edit this file to customize your editor settings

# Default editor for each file type
MARKDOWN_EDITOR="nano"
USCRIPT_EDITOR="nano"
CONFIG_EDITOR="nano"
JSON_EDITOR="nano"
TEXT_EDITOR="nano"

# Enable syntax highlighting if available
SYNTAX_HIGHLIGHTING=true

# Auto-save settings
AUTO_SAVE=true
AUTO_SAVE_INTERVAL=30

# Editor behavior
SHOW_LINE_NUMBERS=true
WORD_WRAP=true
TAB_SIZE=4

# Web editor settings
WEB_EDITOR_PORT=8080
WEB_EDITOR_HOST="localhost"

# External editor integration
EXTERNAL_EDITOR=""  # Set to "code", "vim", "emacs", etc.
EOF
    log_info "Created default editor preferences: $EDITOR_PREFS"
}

# Detect available editors
detect_editors() {
    local available_editors=()
    
    # Check for common editors
    local editors=("nano" "vim" "emacs" "code" "subl" "atom" "micro")
    
    for editor in "${editors[@]}"; do
        if command -v "$editor" >/dev/null 2>&1; then
            available_editors+=("$editor")
        fi
    done
    
    echo "${available_editors[@]}"
}

# Get editor for file type
get_editor_for_type() {
    local file_type="$1"
    local editor
    
    case "$file_type" in
        markdown|md)
            editor="${MARKDOWN_EDITOR:-nano}"
            ;;
        uscript|us)
            editor="${USCRIPT_EDITOR:-nano}"
            ;;
        config|conf|cfg)
            editor="${CONFIG_EDITOR:-nano}"
            ;;
        json)
            editor="${JSON_EDITOR:-nano}"
            ;;
        *)
            editor="${TEXT_EDITOR:-nano}"
            ;;
    esac
    
    # Use external editor if set
    if [[ -n "$EXTERNAL_EDITOR" ]] && command -v "$EXTERNAL_EDITOR" >/dev/null 2>&1; then
        editor="$EXTERNAL_EDITOR"
    fi
    
    echo "$editor"
}

# Open file in appropriate editor
open_file() {
    local filepath="$1"
    local file_type="$2"
    
    if [[ ! -f "$filepath" ]]; then
        log_error "File not found: $filepath"
        return 1
    fi
    
    load_editor_preferences
    
    local editor=$(get_editor_for_type "$file_type")
    
    log_info "Opening $(basename "$filepath") with $editor"
    
    # Special handling for different editors
    case "$editor" in
        code)
            "$editor" "$filepath" >/dev/null 2>&1 &
            ;;
        subl|atom)
            "$editor" "$filepath" >/dev/null 2>&1 &
            ;;
        nano|vim|emacs|micro)
            "$editor" "$filepath"
            ;;
        *)
            if command -v "$editor" >/dev/null 2>&1; then
                "$editor" "$filepath"
            else
                log_warning "Editor not found: $editor, falling back to nano"
                nano "$filepath"
            fi
            ;;
    esac
    
    log_success "File editing session completed"
}

# Create new file with template
create_new_file() {
    local file_type="$1"
    local filename="$2"
    local target_dir="$3"
    
    # Determine target directory
    case "$target_dir" in
        memory|umemory)
            target_dir="$UMEMORY"
            ;;
        sandbox)
            target_dir="$SANDBOX"
            ;;
        uscript)
            target_dir="$USCRIPT/active"
            ;;
        *)
            target_dir="$SANDBOX"
            ;;
    esac
    
    # Generate filename if not provided
    if [[ -z "$filename" ]]; then
        local timestamp=$(date +%Y%m%d-%H%M%S)
        case "$file_type" in
            markdown)
                filename="FILE-${timestamp}-new-001.md"
                ;;
            uscript)
                filename="script-${timestamp}.us"
                ;;
            config)
                filename="config-${timestamp}.conf"
                ;;
            json)
                filename="data-${timestamp}.json"
                ;;
            *)
                filename="file-${timestamp}.txt"
                ;;
        esac
    fi
    
    local filepath="$target_dir/$filename"
    
    # Create file with appropriate template
    case "$file_type" in
        markdown)
            create_markdown_template "$filepath"
            ;;
        uscript)
            create_uscript_template "$filepath"
            ;;
        config)
            create_config_template "$filepath"
            ;;
        json)
            create_json_template "$filepath"
            ;;
        *)
            touch "$filepath"
            ;;
    esac
    
    log_success "Created new file: $filename"
    
    # Open the new file for editing
    open_file "$filepath" "$file_type"
}

# Create markdown template
create_markdown_template() {
    local filepath="$1"
    
    cat > "$filepath" << EOF
# Document Title

**Created**: $(date "+%Y-%m-%d %H:%M:%S")  
**Type**: Documentation  
**Status**: Draft

## Overview

Brief description of the document content.

## Content

### Section 1

Content goes here.

### Section 2

More content here.

## Notes

- Note 1
- Note 2

## References

- [Link 1](https://example.com)
- [Link 2](https://example.com)

---

*Created with uDOS Editor v1.3*
EOF
}

# Create uScript template
create_uscript_template() {
    local filepath="$1"
    
    cat > "$filepath" << 'EOF'
#!/bin/bash
# uSCRIPT Template
#
# Description: Brief description of the script
# Author: User
# Created: $(date "+%Y-%m-%d")
# Version: 1.0
#
# Usage: ./script.us [arguments]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Main function
main() {
    log_info "Starting script execution..."
    
    # Your code here
    echo "Hello from uSCRIPT!"
    
    log_success "Script completed successfully!"
}

# Show help
show_help() {
    echo "uSCRIPT Template"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
    shift
done

# Execute main function
main "$@"
EOF
    
    chmod +x "$filepath"
}

# Create config template
create_config_template() {
    local filepath="$1"
    
    cat > "$filepath" << EOF
# uDOS Configuration File
# Created: $(date "+%Y-%m-%d %H:%M:%S")

# System Settings
SYSTEM_NAME="uDOS"
VERSION="1.3"
DEBUG_MODE=false

# User Settings
DEFAULT_EDITOR="nano"
AUTO_SAVE=true
SYNTAX_HIGHLIGHTING=true

# Network Settings
HOST="localhost"
PORT=8080

# File Paths
MEMORY_PATH="uMEMORY"
SANDBOX_PATH="sandbox"
USCRIPT_PATH="uSCRIPT"

# Feature Flags
EXPERIMENTAL_FEATURES=false
ADVANCED_MODE=false
EOF
}

# Create JSON template
create_json_template() {
    local filepath="$1"
    
    cat > "$filepath" << EOF
{
  "name": "uDOS Data",
  "version": "1.3",
  "created": "$(date -Iseconds)",
  "type": "configuration",
  "data": {
    "settings": {
      "enabled": true,
      "debug": false
    },
    "metadata": {
      "author": "$(whoami)",
      "description": "JSON data file"
    }
  }
}
EOF
}

# Start markdown editor mode
start_markdown_mode() {
    local file="$1"
    
    echo -e "\n${GREEN}📝 Markdown Editor Mode${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ -n "$file" ]]; then
        if [[ -f "$file" ]]; then
            open_file "$file" "markdown"
        else
            log_warning "File not found: $file"
            read -p "Create new file? (y/N): " create
            if [[ "$create" =~ ^[Yy] ]]; then
                create_new_file "markdown" "$(basename "$file")" "$(dirname "$file")"
            fi
        fi
    else
        # Interactive file selection
        echo "Recent markdown files:"
        find "$UMEMORY" "$SANDBOX" -name "*.md" -type f -mtime -7 | head -10 | nl
        echo ""
        read -p "Select file number or 'n' for new: " choice
        
        if [[ "$choice" == "n" ]]; then
            read -p "Enter filename: " filename
            create_new_file "markdown" "$filename" "memory"
        elif [[ "$choice" =~ ^[0-9]+$ ]]; then
            local file=$(find "$UMEMORY" "$SANDBOX" -name "*.md" -type f -mtime -7 | head -10 | sed -n "${choice}p")
            if [[ -n "$file" ]]; then
                open_file "$file" "markdown"
            else
                log_error "Invalid selection"
            fi
        fi
    fi
}

# Start uScript editor mode
start_uscript_mode() {
    local file="$1"
    
    echo -e "\n${BLUE}⚡ uSCRIPT Editor Mode${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ -n "$file" ]]; then
        if [[ -f "$file" ]]; then
            open_file "$file" "uscript"
        else
            log_warning "File not found: $file"
            read -p "Create new script? (y/N): " create
            if [[ "$create" =~ ^[Yy] ]]; then
                create_new_file "uscript" "$(basename "$file")" "uscript"
            fi
        fi
    else
        # Interactive script selection
        echo "Recent uSCRIPT files:"
        find "$USCRIPT" -name "*.us" -type f | head -10 | nl
        echo ""
        read -p "Select script number or 'n' for new: " choice
        
        if [[ "$choice" == "n" ]]; then
            read -p "Enter script name: " scriptname
            create_new_file "uscript" "$scriptname" "uscript"
        elif [[ "$choice" =~ ^[0-9]+$ ]]; then
            local file=$(find "$USCRIPT" -name "*.us" -type f | head -10 | sed -n "${choice}p")
            if [[ -n "$file" ]]; then
                open_file "$file" "uscript"
            else
                log_error "Invalid selection"
            fi
        fi
    fi
}

# Configure editor preferences
configure_editors() {
    echo -e "\n${YELLOW}⚙️  Editor Configuration${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo "Available editors:"
    local available=($(detect_editors))
    for i in "${!available[@]}"; do
        echo "  $((i+1)). ${available[i]}"
    done
    echo ""
    
    load_editor_preferences
    
    echo "Current settings:"
    echo "  Markdown: $MARKDOWN_EDITOR"
    echo "  uSCRIPT: $USCRIPT_EDITOR"
    echo "  Config: $CONFIG_EDITOR"
    echo "  JSON: $JSON_EDITOR"
    echo ""
    
    read -p "Update settings? (y/N): " update
    if [[ "$update" =~ ^[Yy] ]]; then
        echo "Select editor for each file type (or press Enter to keep current):"
        
        read -p "Markdown editor [$MARKDOWN_EDITOR]: " new_md
        read -p "uSCRIPT editor [$USCRIPT_EDITOR]: " new_us
        read -p "Config editor [$CONFIG_EDITOR]: " new_conf
        read -p "JSON editor [$JSON_EDITOR]: " new_json
        
        # Update preferences file
        if [[ -n "$new_md" ]]; then sed -i '' "s/MARKDOWN_EDITOR=.*/MARKDOWN_EDITOR=\"$new_md\"/" "$EDITOR_PREFS"; fi
        if [[ -n "$new_us" ]]; then sed -i '' "s/USCRIPT_EDITOR=.*/USCRIPT_EDITOR=\"$new_us\"/" "$EDITOR_PREFS"; fi
        if [[ -n "$new_conf" ]]; then sed -i '' "s/CONFIG_EDITOR=.*/CONFIG_EDITOR=\"$new_conf\"/" "$EDITOR_PREFS"; fi
        if [[ -n "$new_json" ]]; then sed -i '' "s/JSON_EDITOR=.*/JSON_EDITOR=\"$new_json\"/" "$EDITOR_PREFS"; fi
        
        log_success "Editor preferences updated"
    fi
}

# Show editor help
show_editor_help() {
    echo -e "\n${YELLOW}📝 Editor Integration Help${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BOLD}Usage:${NC}"
    echo "  editor open <file> [type]       - Open file in appropriate editor"
    echo "  editor new <type> [name] [dir]  - Create new file with template"
    echo "  editor markdown [file]          - Start markdown editor mode"
    echo "  editor uscript [file]           - Start uSCRIPT editor mode"
    echo "  editor config                   - Configure editor preferences"
    echo "  editor help                     - Show this help"
    echo ""
    echo -e "${BOLD}File Types:${NC}"
    echo "  markdown, uscript, config, json, text"
    echo ""
    echo -e "${BOLD}Examples:${NC}"
    echo "  editor open document.md"
    echo "  editor new markdown 'My Notes' memory"
    echo "  editor uscript"
    echo "  editor config"
    echo ""
}

# Main function dispatcher
main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        open)
            local file="$1"
            local type="${2:-auto}"
            if [[ -n "$file" ]]; then
                # Auto-detect type from extension if not specified
                if [[ "$type" == "auto" ]]; then
                    case "${file##*.}" in
                        md) type="markdown" ;;
                        us) type="uscript" ;;
                        conf|cfg) type="config" ;;
                        json) type="json" ;;
                        *) type="text" ;;
                    esac
                fi
                open_file "$file" "$type"
            else
                log_error "File path required"
            fi
            ;;
        new)
            local type="$1"
            local name="$2"
            local dir="$3"
            if [[ -n "$type" ]]; then
                create_new_file "$type" "$name" "$dir"
            else
                log_error "File type required (markdown, uscript, config, json)"
            fi
            ;;
        markdown)
            start_markdown_mode "$1"
            ;;
        uscript)
            start_uscript_mode "$1"
            ;;
        config)
            configure_editors
            ;;
        help|--help|-h)
            show_editor_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_editor_help
            ;;
    esac
}

# If script is executed directly, run main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
