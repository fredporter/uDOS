#!/bin/bash
# ucode-editor-integration.sh - Integrated Text, Markdown, and Code Editors for uCode
# Provides nano, vim, micro, and VS Code integration for uDOS development
# Version: 2.0.0

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
UMEM="${UHOME}/uMemory"
SANDBOX="${UHOME}/sandbox"

# Editor configuration
EDITOR_CONFIG="${UMEM}/config/editor-config.json"
USER_EDITOR_PREFS="${SANDBOX}/user-data/editor-preferences.json"

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Initialize editor integration
init_editor_integration() {
    bold "📝 uCode Editor Integration v2.0.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Create required directories
    mkdir -p "${UMEM}/config" "${SANDBOX}/user-data" "${SANDBOX}/drafts" "${SANDBOX}/sessions"
    
    # Initialize editor configuration
    setup_editor_config
    
    # Detect available editors
    detect_available_editors
    
    # Setup user preferences
    setup_user_preferences
    
    green "✅ Editor integration initialized"
}

# Setup editor configuration
setup_editor_config() {
    cyan "⚙️ Setting up editor configuration..."
    
    cat > "$EDITOR_CONFIG" << 'EOF'
{
  "editor_integration": {
    "version": "2.0.0",
    "supported_editors": [
      {
        "name": "nano",
        "command": "nano",
        "type": "terminal",
        "file_types": ["txt", "md", "sh", "json", "yaml"],
        "features": ["basic_editing", "syntax_highlighting"],
        "description": "Simple terminal-based editor"
      },
      {
        "name": "vim", 
        "command": "vim",
        "type": "terminal",
        "file_types": ["txt", "md", "sh", "json", "yaml", "js", "ts", "py"],
        "features": ["advanced_editing", "syntax_highlighting", "plugins"],
        "description": "Advanced terminal editor"
      },
      {
        "name": "micro",
        "command": "micro",
        "type": "terminal", 
        "file_types": ["txt", "md", "sh", "json", "yaml", "js", "ts", "py"],
        "features": ["modern_interface", "syntax_highlighting", "mouse_support"],
        "description": "Modern terminal editor"
      },
      {
        "name": "code",
        "command": "code",
        "type": "gui",
        "file_types": ["*"],
        "features": ["full_ide", "extensions", "debugging", "git_integration"],
        "description": "Visual Studio Code"
      }
    ],
    "default_assignments": {
      "txt": "nano",
      "md": "micro",
      "sh": "vim", 
      "json": "code",
      "yaml": "code",
      "js": "code",
      "ts": "code",
      "py": "code"
    }
  }
}
EOF
    
    echo "  📄 Editor configuration created: $EDITOR_CONFIG"
}

# Detect available editors
detect_available_editors() {
    cyan "🔍 Detecting available editors..."
    
    local available_editors=()
    
    # Check for each editor
    if command -v nano >/dev/null 2>&1; then
        available_editors+=("nano")
        echo "  ✅ nano - Available"
    else
        echo "  ❌ nano - Not found"
    fi
    
    if command -v vim >/dev/null 2>&1; then
        available_editors+=("vim")
        echo "  ✅ vim - Available"
    else
        echo "  ❌ vim - Not found"
    fi
    
    if command -v micro >/dev/null 2>&1; then
        available_editors+=("micro")
        echo "  ✅ micro - Available"
    else
        echo "  ❌ micro - Not found (install with: brew install micro)"
    fi
    
    if command -v code >/dev/null 2>&1; then
        available_editors+=("code")
        echo "  ✅ VS Code - Available"
    else
        echo "  ❌ VS Code - Not found"
    fi
    
    # Store available editors
    local available_json=$(printf '%s\n' "${available_editors[@]}" | jq -R . | jq -s .)
    echo "{\"available_editors\": $available_json, \"detected_at\": \"$(date -Iseconds)\"}" > "${UMEM}/config/available-editors.json"
}

# Setup user preferences
setup_user_preferences() {
    cyan "👤 Setting up user editor preferences..."
    
    if [[ ! -f "$USER_EDITOR_PREFS" ]]; then
        cat > "$USER_EDITOR_PREFS" << 'EOF'
{
  "user_preferences": {
    "default_editor": "auto",
    "preferred_terminal_editor": "nano",
    "preferred_gui_editor": "code",
    "auto_save": true,
    "backup_files": true,
    "syntax_highlighting": true,
    "line_numbers": true,
    "file_type_preferences": {
      "markdown": "micro",
      "code": "code",
      "config": "nano",
      "logs": "nano"
    }
  },
  "session_settings": {
    "remember_last_files": true,
    "auto_restore_session": false,
    "max_recent_files": 10
  }
}
EOF
        echo "  📄 Created user preferences: $USER_EDITOR_PREFS"
    else
        echo "  📄 User preferences exist: $USER_EDITOR_PREFS"
    fi
}

# Smart editor selection
select_editor() {
    local file_path="$1"
    local force_editor="${2:-auto}"
    
    # Get file extension
    local ext="${file_path##*.}"
    
    # If force editor specified and available, use it
    if [[ "$force_editor" != "auto" ]] && command -v "$force_editor" >/dev/null 2>&1; then
        echo "$force_editor"
        return
    fi
    
    # Smart selection based on file type and availability
    case "$ext" in
        "md"|"markdown")
            if command -v micro >/dev/null 2>&1; then
                echo "micro"
            elif command -v vim >/dev/null 2>&1; then
                echo "vim"
            else
                echo "nano"
            fi
            ;;
        "sh"|"bash")
            if command -v vim >/dev/null 2>&1; then
                echo "vim"
            elif command -v micro >/dev/null 2>&1; then
                echo "micro"
            else
                echo "nano"
            fi
            ;;
        "json"|"yaml"|"js"|"ts"|"py")
            if command -v code >/dev/null 2>&1; then
                echo "code"
            elif command -v vim >/dev/null 2>&1; then
                echo "vim"
            else
                echo "nano"
            fi
            ;;
        *)
            # Default fallback
            if command -v nano >/dev/null 2>&1; then
                echo "nano"
            elif command -v vim >/dev/null 2>&1; then
                echo "vim"
            else
                echo "cat"  # View-only fallback
            fi
            ;;
    esac
}

# Edit file with smart editor selection
edit_file() {
    local file_path="$1"
    local editor="${2:-auto}"
    local create_dirs="${3:-true}"
    
    cyan "📝 Opening file: $(basename "$file_path")"
    
    # Create directory if needed
    if [[ "$create_dirs" == "true" ]]; then
        mkdir -p "$(dirname "$file_path")"
    fi
    
    # Select appropriate editor
    local selected_editor=$(select_editor "$file_path" "$editor")
    
    echo "  🔧 Using editor: $selected_editor"
    
    # Log the edit action to uMemory
    log_edit_action "$file_path" "$selected_editor"
    
    # Open file with selected editor
    case "$selected_editor" in
        "code")
            code "$file_path"
            ;;
        "nano"|"vim"|"micro")
            "$selected_editor" "$file_path"
            ;;
        "cat")
            yellow "⚠️ No suitable editor found, viewing file:"
            cat "$file_path"
            ;;
        *)
            red "❌ Unknown editor: $selected_editor"
            return 1
            ;;
    esac
}

# Log edit actions to uMemory
log_edit_action() {
    local file_path="$1"
    local editor="$2"
    local timestamp=$(date -Iseconds)
    
    local log_entry="{
        \"timestamp\": \"$timestamp\",
        \"action\": \"file_edit\",
        \"file\": \"$file_path\",
        \"editor\": \"$editor\",
        \"location\": \"$(pwd)\",
        \"user\": \"$(whoami)\"
    }"
    
    # Append to edit log
    local edit_log="${UMEM}/logs/edit-history.jsonl"
    mkdir -p "$(dirname "$edit_log")"
    echo "$log_entry" >> "$edit_log"
}

# Quick file creation functions
create_draft() {
    local draft_name="$1"
    local type="${2:-md}"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    
    local draft_file="${SANDBOX}/drafts/${timestamp}_${draft_name}.${type}"
    
    cyan "📝 Creating draft: $draft_name"
    
    # Create draft with template
    case "$type" in
        "md")
            cat > "$draft_file" << EOF
# $draft_name

**Created:** $(date -Iseconds)  
**Type:** Draft  
**Session:** $(date '+%Y-%m-%d')

---

## Notes



---

*Draft created by uDOS Editor Integration*
EOF
            ;;
        "txt")
            cat > "$draft_file" << EOF
$draft_name
Created: $(date -Iseconds)

EOF
            ;;
        *)
            touch "$draft_file"
            ;;
    esac
    
    edit_file "$draft_file"
    echo "  📄 Draft created: $draft_file"
}

# Session file management
create_session_file() {
    local session_name="${1:-$(date '+%Y%m%d')}"
    local session_file="${SANDBOX}/sessions/${session_name}_session.md"
    
    cyan "📅 Creating session file: $session_name"
    
    if [[ ! -f "$session_file" ]]; then
        cat > "$session_file" << EOF
# Session: $session_name

**Date:** $(date '+%Y-%m-%d')  
**Started:** $(date '+%H:%M:%S')  
**Location:** $(pwd)

---

## Today's Goals
- [ ] 

## Progress Notes



## Ideas & Insights



## Action Items
- [ ] 

---

## Session Log
- $(date '+%H:%M') - Session started

EOF
    fi
    
    edit_file "$session_file"
    echo "  📅 Session file: $session_file"
}

# List recent files
list_recent_files() {
    bold "📂 Recent Files"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ -f "${UMEM}/logs/edit-history.jsonl" ]]; then
        echo "Recent edits:"
        tail -10 "${UMEM}/logs/edit-history.jsonl" | while read -r line; do
            local file=$(echo "$line" | jq -r '.file')
            local editor=$(echo "$line" | jq -r '.editor') 
            local timestamp=$(echo "$line" | jq -r '.timestamp')
            printf "  📄 %-30s [%s] %s\n" "$(basename "$file")" "$editor" "$timestamp"
        done
    else
        echo "  📭 No recent edits found"
    fi
    
    echo
    echo "Drafts:"
    if [[ -d "${SANDBOX}/drafts" ]]; then
        find "${SANDBOX}/drafts" -name "*.md" -o -name "*.txt" | head -5 | while read -r file; do
            printf "  📝 %s\n" "$(basename "$file")"
        done
    fi
    
    echo
    echo "Session files:"
    if [[ -d "${SANDBOX}/sessions" ]]; then
        find "${SANDBOX}/sessions" -name "*_session.md" | head -5 | while read -r file; do
            printf "  📅 %s\n" "$(basename "$file")"
        done
    fi
}

# Main execution
case "${1:-help}" in
    "init"|"setup")
        init_editor_integration
        ;;
    "edit"|"e")
        if [[ $# -lt 2 ]]; then
            red "❌ Usage: $0 edit <file> [editor]"
            exit 1
        fi
        init_editor_integration >/dev/null 2>&1
        edit_file "$2" "${3:-auto}"
        ;;
    "draft"|"d")
        init_editor_integration >/dev/null 2>&1
        create_draft "${2:-untitled}" "${3:-md}"
        ;;
    "session"|"s")
        init_editor_integration >/dev/null 2>&1
        create_session_file "$2"
        ;;
    "list"|"recent"|"l")
        list_recent_files
        ;;
    "editors")
        detect_available_editors
        ;;
    "help"|"-h"|"--help")
        bold "📝 uCode Editor Integration v2.0.0"
        echo
        echo "Usage: $0 [command] [options]"
        echo
        echo "Commands:"
        echo "  init                    Initialize editor integration"
        echo "  edit <file> [editor]    Edit file with smart editor selection"
        echo "  draft <name> [type]     Create new draft file"
        echo "  session [name]          Create/open session file"
        echo "  list                    Show recent files"
        echo "  editors                 Show available editors"
        echo "  help                    Show this help"
        echo
        echo "Examples:"
        echo "  $0 edit notes.md"
        echo "  $0 draft meeting-notes"
        echo "  $0 session project-alpha"
        echo
        ;;
    *)
        red "❌ Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
