#!/bin/bash
# enhanced-sandbox-manager.sh - Advanced Sandbox Management for User Data
# Organizes drafts, sessions, research, and daily files while keeping uMemory separate
# Version: 2.0.0

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
UMEM="${UHOME}/uMemory"
SANDBOX="${UHOME}/sandbox"

# Sandbox structure
USER_DATA_DIR="${SANDBOX}/user-data"
DRAFTS_DIR="${SANDBOX}/drafts"
SESSIONS_DIR="${SANDBOX}/sessions"
TODAY_DIR="${SANDBOX}/today"
RESEARCH_DIR="${SANDBOX}/temp/research"
LISTS_DIR="${SANDBOX}/user-data/lists"

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Initialize sandbox
init_enhanced_sandbox() {
    bold "📁 Sandbox Manager v2.0.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Create sandbox directory structure
    create_sandbox_structure
    
    # Setup user data organization
    setup_user_data_organization
    
    # Initialize today's workspace
    init_todays_workspace
    
    # Setup automatic organization
    setup_auto_organization
    
    green "✅ sandbox initialized"
    show_sandbox_status
}

# Create sandbox directory structure
create_sandbox_structure() {
    cyan "📁 Creating sandbox directory structure..."
    
    # Core directories
    mkdir -p "$USER_DATA_DIR" "$DRAFTS_DIR" "$SESSIONS_DIR" "$TODAY_DIR" "$RESEARCH_DIR" "$LISTS_DIR"
    
    # Subdirectories for organization
    mkdir -p "${USER_DATA_DIR}/preferences" "${USER_DATA_DIR}/profiles" "${USER_DATA_DIR}/bookmarks"
    mkdir -p "${DRAFTS_DIR}/archive" "${DRAFTS_DIR}/templates"
    mkdir -p "${SESSIONS_DIR}/archive" "${SESSIONS_DIR}/projects"
    mkdir -p "${TODAY_DIR}/notes" "${TODAY_DIR}/tasks" "${TODAY_DIR}/ideas"
    mkdir -p "${RESEARCH_DIR}/topics" "${RESEARCH_DIR}/archive"
    mkdir -p "${LISTS_DIR}/todo" "${LISTS_DIR}/shopping" "${LISTS_DIR}/projects"
    
    # Create .gitkeep files to preserve structure
    find "$SANDBOX" -type d -exec touch {}/.gitkeep \;
    
    echo "  📁 Sandbox structure created"
    echo "     📂 User Data: $USER_DATA_DIR"
    echo "     📝 Drafts: $DRAFTS_DIR"
    echo "     📅 Sessions: $SESSIONS_DIR" 
    echo "     📋 Today: $TODAY_DIR"
    echo "     🔬 Research: $RESEARCH_DIR"
    echo "     📋 Lists: $LISTS_DIR"
}

# Setup user data organization
setup_user_data_organization() {
    cyan "👤 Setting up user data organization..."
    
    # Create user data configuration
    cat > "${USER_DATA_DIR}/organization-config.json" << 'EOF'
{
  "organization_settings": {
    "version": "2.0.0",
    "auto_organize": true,
    "archive_after_days": 30,
    "cleanup_empty_dirs": true,
    "backup_before_cleanup": true
  },
  "file_categories": {
    "drafts": {
      "extensions": [".md", ".txt", ".doc"],
      "max_age_days": 30,
      "auto_archive": true
    },
    "sessions": {
      "extensions": [".md", ".txt"],
      "max_age_days": 90,
      "auto_archive": true
    },
    "research": {
      "extensions": [".md", ".txt", ".pdf", ".url"],
      "max_age_days": 180,
      "auto_archive": false
    },
    "lists": {
      "extensions": [".md", ".txt", ".json"],
      "max_age_days": 60,
      "auto_archive": true
    }
  },
  "memory_separation": {
    "user_data_location": "sandbox/user-data",
    "system_data_location": "uMemory",
    "cross_reference": true,
    "sync_metadata": true
  }
}
EOF
    
    # Create user preferences template
    if [[ ! -f "${USER_DATA_DIR}/preferences/user-preferences.json" ]]; then
        cat > "${USER_DATA_DIR}/preferences/user-preferences.json" << 'EOF'
{
  "user_preferences": {
    "workspace": {
      "default_editor": "auto",
      "auto_save": true,
      "backup_frequency": "daily",
      "theme": "default"
    },
    "organization": {
      "file_naming": "timestamp_prefix",
      "auto_categorize": true,
      "daily_cleanup": true
    },
    "privacy": {
      "exclude_from_sync": ["passwords", "keys", "private"],
      "encrypt_sensitive": false,
      "backup_location": "local"
    }
  }
}
EOF
    fi
    
    echo "  👤 User data organization configured"
}

# Initialize today's workspace
init_todays_workspace() {
    cyan "📅 Initializing today's workspace..."
    
    local today=$(date '+%Y-%m-%d')
    local today_file="${TODAY_DIR}/notes/${today}_daily.md"
    local tasks_file="${TODAY_DIR}/tasks/${today}_tasks.md"
    local ideas_file="${TODAY_DIR}/ideas/${today}_ideas.md"
    
    # Create today's notes file if it doesn't exist
    if [[ ! -f "$today_file" ]]; then
        cat > "$today_file" << EOF
# Daily Notes - $today

**Date:** $(date '+%A, %B %d, %Y')  
**Started:** $(date '+%H:%M')  
**Location:** $(pwd)

---

## Today's Focus
- 

## Notes


## Meetings & Calls


## Random Thoughts


---

## End of Day Summary
- 

**Completed:** $(date '+%H:%M')
EOF
    fi
    
    # Create today's tasks file if it doesn't exist
    if [[ ! -f "$tasks_file" ]]; then
        cat > "$tasks_file" << EOF
# Daily Tasks - $today

**Date:** $(date '+%A, %B %d, %Y')

---

## Priority Tasks
- [ ] 

## Regular Tasks
- [ ] 

## Quick Tasks
- [ ] 

## Completed Tasks
- [x] 

---

## Notes
EOF
    fi
    
    # Create today's ideas file if it doesn't exist
    if [[ ! -f "$ideas_file" ]]; then
        cat > "$ideas_file" << EOF
# Daily Ideas - $today

**Date:** $(date '+%A, %B %d, %Y')

---

## New Ideas


## Project Ideas


## Improvements


## Random Thoughts


---

*Ideas captured on $today*
EOF
    fi
    
    echo "  📅 Today's workspace ready"
    echo "     📝 Notes: $today_file"
    echo "     ✅ Tasks: $tasks_file"
    echo "     💡 Ideas: $ideas_file"
}

# Setup automatic organization
setup_auto_organization() {
    cyan "🤖 Setting up automatic organization..."
    
    # Create organization script
    cat > "${SANDBOX}/auto-organize.sh" << 'EOF'
#!/bin/bash
# Auto-organization script for sandbox
# Runs automatically to organize files

SANDBOX="${HOME}/uDOS/sandbox"
UMEM="${HOME}/uDOS/uMemory"

# Log organization activity
log_activity() {
    local action="$1"
    local details="$2"
    local timestamp=$(date -Iseconds)
    
    local log_entry="{
        \"timestamp\": \"$timestamp\",
        \"action\": \"$action\",
        \"details\": \"$details\",
        \"location\": \"sandbox\"
    }"
    
    mkdir -p "${UMEM}/logs"
    echo "$log_entry" >> "${UMEM}/logs/sandbox-organization.jsonl"
}

# Archive old files
archive_old_files() {
    local days_old=30
    
    # Archive old drafts
    find "${SANDBOX}/drafts" -name "*.md" -o -name "*.txt" | while read -r file; do
        if [[ $(find "$file" -mtime +$days_old) ]]; then
            mkdir -p "${SANDBOX}/drafts/archive/$(date '+%Y/%m')"
            mv "$file" "${SANDBOX}/drafts/archive/$(date '+%Y/%m')/"
            log_activity "archive_draft" "$(basename "$file")"
        fi
    done
    
    # Archive old sessions (90 days)
    find "${SANDBOX}/sessions" -name "*_session.md" | while read -r file; do
        if [[ $(find "$file" -mtime +90) ]]; then
            mkdir -p "${SANDBOX}/sessions/archive/$(date '+%Y/%m')"
            mv "$file" "${SANDBOX}/sessions/archive/$(date '+%Y/%m')/"
            log_activity "archive_session" "$(basename "$file")"
        fi
    done
}

# Clean empty directories
clean_empty_dirs() {
    find "$SANDBOX" -type d -empty -not -path "*/.*" -delete 2>/dev/null || true
    log_activity "cleanup" "removed empty directories"
}

# Run organization
archive_old_files
clean_empty_dirs
log_activity "auto_organize" "completed automatic organization"
EOF
    
    chmod +x "${SANDBOX}/auto-organize.sh"
    
    echo "  🤖 Auto-organization configured"
}

# Log activity to uMemory (separate from user data)
log_to_memory() {
    local action="$1"
    local target="$2"
    local details="${3:-}"
    local timestamp=$(date -Iseconds)
    
    local log_entry="{
        \"timestamp\": \"$timestamp\",
        \"action\": \"$action\",
        \"target\": \"$target\",
        \"details\": \"$details\",
        \"user\": \"$(whoami)\",
        \"location\": \"$(pwd)\"
    }"
    
    local log_file="${UMEM}/logs/sandbox-activity.jsonl"
    mkdir -p "$(dirname "$log_file")"
    echo "$log_entry" >> "$log_file"
}

# Create new draft
create_draft() {
    local draft_name="$1"
    local type="${2:-md}"
    local category="${3:-general}"
    
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local draft_file="${DRAFTS_DIR}/${timestamp}_${draft_name}.${type}"
    
    cyan "📝 Creating draft: $draft_name"
    
    case "$type" in
        "md")
            cat > "$draft_file" << EOF
# $draft_name

**Created:** $(date -Iseconds)  
**Category:** $category  
**Type:** Draft

---

## Content



---

*Draft created by Sandbox Manager*
EOF
            ;;
        "txt")
            cat > "$draft_file" << EOF
$draft_name
Created: $(date -Iseconds)
Category: $category

EOF
            ;;
    esac
    
    log_to_memory "create_draft" "$draft_file" "category: $category"
    echo "  📝 Draft created: $draft_file"
    
    # Open in editor if available
    if command -v "${UHOME}/uCode/editor-integration.sh" >/dev/null 2>&1; then
        "${UHOME}/uCode/editor-integration.sh" edit "$draft_file"
    fi
}

# Create research file
create_research() {
    local topic="$1"
    local category="${2:-general}"
    
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local research_file="${RESEARCH_DIR}/topics/${timestamp}_${topic// /_}.md"
    
    cyan "🔬 Creating research file: $topic"
    
    cat > "$research_file" << EOF
# Research: $topic

**Topic:** $topic  
**Category:** $category  
**Started:** $(date -Iseconds)  
**Status:** In Progress

---

## Research Questions
- 

## Sources


## Key Findings


## Notes


## Next Steps
- [ ] 

---

## References


*Research file created on $(date '+%Y-%m-%d')*
EOF
    
    log_to_memory "create_research" "$research_file" "topic: $topic"
    echo "  🔬 Research file created: $research_file"
}

# Open today's files
open_today() {
    local today=$(date '+%Y-%m-%d')
    local file_type="${1:-notes}"
    
    case "$file_type" in
        "notes")
            local file="${TODAY_DIR}/notes/${today}_daily.md"
            ;;
        "tasks")
            local file="${TODAY_DIR}/tasks/${today}_tasks.md"
            ;;
        "ideas")
            local file="${TODAY_DIR}/ideas/${today}_ideas.md"
            ;;
        *)
            red "❌ Unknown file type: $file_type"
            return 1
            ;;
    esac
    
    if [[ -f "$file" ]]; then
        cyan "📅 Opening today's $file_type"
        log_to_memory "open_today" "$file" "type: $file_type"
        
        # Open in editor
        if command -v "${UHOME}/uCode/editor-integration.sh" >/dev/null 2>&1; then
            "${UHOME}/uCode/editor-integration.sh" edit "$file"
        else
            echo "  📄 File: $file"
        fi
    else
        yellow "⚠️ Today's $file_type file not found, initializing..."
        init_todays_workspace
        open_today "$file_type"
    fi
}

# List sandbox contents
list_sandbox() {
    bold "📁 Sandbox Contents"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo "📝 Recent Drafts:"
    if [[ -d "$DRAFTS_DIR" ]]; then
        find "$DRAFTS_DIR" -name "*.md" -o -name "*.txt" | head -5 | while read -r file; do
            local modified=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file" 2>/dev/null || date)
            printf "  📄 %-40s %s\n" "$(basename "$file")" "$modified"
        done
    fi
    
    echo
    echo "📅 Recent Sessions:"
    if [[ -d "$SESSIONS_DIR" ]]; then
        find "$SESSIONS_DIR" -name "*_session.md" | head -5 | while read -r file; do
            local modified=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file" 2>/dev/null || date)
            printf "  📅 %-40s %s\n" "$(basename "$file")" "$modified"
        done
    fi
    
    echo
    echo "📋 Today's Files:"
    local today=$(date '+%Y-%m-%d')
    for type in notes tasks ideas; do
        local file="${TODAY_DIR}/${type}/${today}_${type%s}.md"
        if [[ -f "$file" ]]; then
            printf "  📋 %-20s %s\n" "$type" "$(basename "$file")"
        fi
    done
    
    echo
    echo "🔬 Recent Research:"
    if [[ -d "$RESEARCH_DIR/topics" ]]; then
        find "$RESEARCH_DIR/topics" -name "*.md" | head -3 | while read -r file; do
            printf "  🔬 %s\n" "$(basename "$file")"
        done
    fi
}

# Show sandbox status
show_sandbox_status() {
    echo
    bold "📊 Sandbox Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Count files in each category
    local drafts_count=0
    local sessions_count=0
    local research_count=0
    local today_count=0
    
    if [[ -d "$DRAFTS_DIR" ]]; then
        drafts_count=$(find "$DRAFTS_DIR" -name "*.md" -o -name "*.txt" | wc -l | xargs)
    fi
    
    if [[ -d "$SESSIONS_DIR" ]]; then
        sessions_count=$(find "$SESSIONS_DIR" -name "*_session.md" | wc -l | xargs)
    fi
    
    if [[ -d "$RESEARCH_DIR" ]]; then
        research_count=$(find "$RESEARCH_DIR" -name "*.md" | wc -l | xargs)
    fi
    
    if [[ -d "$TODAY_DIR" ]]; then
        today_count=$(find "$TODAY_DIR" -name "*.md" | wc -l | xargs)
    fi
    
    echo "📝 Drafts: $drafts_count files"
    echo "📅 Sessions: $sessions_count files"
    echo "🔬 Research: $research_count files"
    echo "📋 Today: $today_count files"
    echo "📁 Location: $SANDBOX"
    echo "🧠 System Data: $UMEM (separate)"
}

# Organize sandbox
organize_sandbox() {
    cyan "🗂️ Organizing sandbox..."
    
    # Run auto-organization script
    if [[ -f "${SANDBOX}/auto-organize.sh" ]]; then
        "${SANDBOX}/auto-organize.sh"
    fi
    
    log_to_memory "organize_sandbox" "$SANDBOX" "manual organization"
    green "✅ Sandbox organized"
}

# Backup sandbox
backup_sandbox() {
    local backup_name="${1:-$(date '+%Y%m%d_%H%M%S')}"
    local backup_dir="${SANDBOX}/backups"
    
    cyan "💾 Creating sandbox backup: $backup_name"
    
    mkdir -p "$backup_dir"
    
    # Create backup archive
    tar -czf "${backup_dir}/sandbox_backup_${backup_name}.tar.gz" \
        -C "$SANDBOX" \
        --exclude="backups" \
        --exclude="*.tmp" \
        --exclude=".DS_Store" \
        .
    
    log_to_memory "backup_sandbox" "${backup_dir}/sandbox_backup_${backup_name}.tar.gz" "backup created"
    echo "  💾 Backup created: ${backup_dir}/sandbox_backup_${backup_name}.tar.gz"
    
    # Keep only last 5 backups
    find "$backup_dir" -name "sandbox_backup_*.tar.gz" | sort -r | tail -n +6 | xargs rm -f
}

# Main execution
case "${1:-help}" in
    "init"|"setup")
        init_enhanced_sandbox
        ;;
    "draft")
        if [[ $# -lt 2 ]]; then
            red "❌ Usage: $0 draft <name> [type] [category]"
            exit 1
        fi
        create_draft "$2" "${3:-md}" "${4:-general}"
        ;;
    "research")
        if [[ $# -lt 2 ]]; then
            red "❌ Usage: $0 research <topic> [category]"
            exit 1
        fi
        create_research "$2" "${3:-general}"
        ;;
    "today")
        open_today "${2:-notes}"
        ;;
    "list"|"ls")
        list_sandbox
        ;;
    "status")
        show_sandbox_status
        ;;
    "organize"|"clean")
        organize_sandbox
        ;;
    "backup")
        backup_sandbox "$2"
        ;;
    "help"|"-h"|"--help")
        bold "📁 Sandbox Manager v2.0.0"
        echo
        echo "Usage: $0 [command] [options]"
        echo
        echo "Commands:"
        echo "  init                       Initialize sandbox"
        echo "  draft <name> [type] [cat]  Create new draft file"
        echo "  research <topic> [cat]     Create research file"
        echo "  today [notes|tasks|ideas]  Open today's files"
        echo "  list                       List sandbox contents"
        echo "  status                     Show sandbox status"
        echo "  organize                   Organize and clean sandbox"
        echo "  backup [name]              Create sandbox backup"
        echo "  help                       Show this help"
        echo
        echo "Examples:"
        echo "  $0 draft meeting-notes md work"
        echo "  $0 research 'machine learning' ai"
        echo "  $0 today tasks"
        echo "  $0 backup weekly"
        echo
        ;;
    *)
        red "❌ Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
