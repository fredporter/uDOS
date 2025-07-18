#!/bin/bash
# sandbox-manager.sh - uDOS v1.0 Sandbox Session Management  
# Daily working space for organized user data and session management

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SANDBOX_DIR="${UDOS_ROOT}/sandbox"
UMEM="${UDOS_ROOT}/uMemory"
TODAY_DIR="${SANDBOX_DIR}/today"
SESSIONS_DIR="${SANDBOX_DIR}/sessions"
TEMP_DIR="${SANDBOX_DIR}/temp"
DRAFTS_DIR="${SANDBOX_DIR}/drafts"
FINALIZED_DIR="${SANDBOX_DIR}/finalized"

# Ensure sandbox structure exists
init_sandbox_structure() {
    mkdir -p "$TODAY_DIR"
    mkdir -p "$SESSIONS_DIR"
    mkdir -p "$TEMP_DIR"
    mkdir -p "$DRAFTS_DIR"
    mkdir -p "$FINALIZED_DIR"
}

# Start new daily session
start_session() {
    local date_str
    date_str=$(date +"%Y-%m-%d")
    local session_dir="${SESSIONS_DIR}/${date_str}"
    
    echo "🏖️ Starting daily session: $date_str"
    
    # Archive previous today if it exists and has content
    if [[ -d "$TODAY_DIR" ]] && [[ -n "$(ls -A "$TODAY_DIR" 2>/dev/null)" ]]; then
        echo "📦 Archiving previous session..."
        local prev_session="${SESSIONS_DIR}/$(date -d yesterday +"%Y-%m-%d" 2>/dev/null || date -v-1d +"%Y-%m-%d" 2>/dev/null || date +"%Y-%m-%d")"
        mkdir -p "$prev_session"
        mv "$TODAY_DIR"/* "$prev_session/" 2>/dev/null || true
    fi
    
    # Clean and prepare today directory
    rm -rf "$TODAY_DIR"
    mkdir -p "$TODAY_DIR"
    
    # Create session welcome file
    cat > "${TODAY_DIR}/session-info.md" << EOF
# 🏖️ Daily Session: $date_str

**Started:** $(date)
**Session Directory:** \`sandbox/today/\`

## 📋 Session Goals
- [ ] Goal 1
- [ ] Goal 2  
- [ ] Goal 3

## 📝 Session Notes
Write your daily working notes here...

## 🎯 Next Steps
- [ ] Next action 1
- [ ] Next action 2

---
*This session follows uDOS filename conventions - no folder structures needed*
EOF
    
    echo "✅ Daily session started in: sandbox/today/"
    echo "📝 Edit session-info.md to set your goals"
}

# Finalize current session
finalize_session() {
    local date_str
    date_str=$(date +"%Y-%m-%d")
    
    echo "🎯 Finalizing session: $date_str"
    
    if [[ ! -d "$TODAY_DIR" ]] || [[ -z "$(ls -A "$TODAY_DIR" 2>/dev/null)" ]]; then
        echo "⚠️ No active session to finalize"
        return 1
    fi
    
    # Create finalized session directory
    local finalized_session="${FINALIZED_DIR}/${date_str}"
    mkdir -p "$finalized_session"
    
    # Move important files to finalized
    echo "📦 Moving files to finalized storage..."
    for file in "$TODAY_DIR"/*; do
        if [[ -f "$file" ]]; then
            local filename
            filename=$(basename "$file")
            
            # Skip temporary files
            if [[ "$filename" =~ \.(tmp|temp|bak)$ ]]; then
                echo "🗑️ Skipping temporary file: $filename"
                continue
            fi
            
            # Copy to finalized
            cp "$file" "$finalized_session/"
            echo "✅ Finalized: $filename"
        fi
    done
    
    # Archive session
    local session_archive="${SESSIONS_DIR}/${date_str}"
    mkdir -p "$session_archive"
    mv "$TODAY_DIR"/* "$session_archive/" 2>/dev/null || true
    
    # Store important files in uMemory if they exist
    if [[ -d "$finalized_session" ]] && [[ -n "$(ls -A "$finalized_session" 2>/dev/null)" ]]; then
        local umem_archive="${UMEM}/archive/${date_str}"
        mkdir -p "$umem_archive"
        cp -r "$finalized_session"/* "$umem_archive/"
        echo "💾 Stored in uMemory: $umem_archive"
    fi
    
    echo "✅ Session finalized and archived"
}

# Clean temporary files
clean_temp() {
    echo "🧹 Cleaning temporary files..."
    
    # Clean temp directory
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "${TEMP_DIR:?}"/*
        echo "✅ Cleaned sandbox/temp/"
    fi
    
    # Clean old temporary files from other directories
    find "$SANDBOX_DIR" -name "*.tmp" -mtime +1 -delete 2>/dev/null || true
    find "$SANDBOX_DIR" -name "*.temp" -mtime +1 -delete 2>/dev/null || true
    find "$SANDBOX_DIR" -name "*.bak" -mtime +7 -delete 2>/dev/null || true
    
    echo "✅ Cleaned old temporary files"
}

# Archive old sessions
archive_old_sessions() {
    local days_to_keep="${1:-30}"
    echo "📦 Archiving sessions older than $days_to_keep days..."
    
    # Archive old sessions to compressed format
    find "$SESSIONS_DIR" -maxdepth 1 -type d -mtime +$days_to_keep | while read -r old_session; do
        if [[ "$old_session" != "$SESSIONS_DIR" ]]; then
            local session_name
            session_name=$(basename "$old_session")
            local archive_file="${UMEM}/archive/${session_name}.tar.gz"
            
            mkdir -p "$(dirname "$archive_file")"
            tar -czf "$archive_file" -C "$SESSIONS_DIR" "$session_name"
            rm -rf "$old_session"
            
            echo "📦 Archived: $session_name"
        fi
    done
}

# List sandbox contents
list_contents() {
    echo "🏖️ Sandbox Contents:"
    echo "==================="
    
    echo ""
    echo "📁 Today's Session:"
    if [[ -d "$TODAY_DIR" ]] && [[ -n "$(ls -A "$TODAY_DIR" 2>/dev/null)" ]]; then
        ls -la "$TODAY_DIR" | grep -v "^total" | tail -n +2
    else
        echo "   (empty)"
    fi
    
    echo ""
    echo "📁 Drafts:"
    if [[ -d "$DRAFTS_DIR" ]] && [[ -n "$(ls -A "$DRAFTS_DIR" 2>/dev/null)" ]]; then
        ls -la "$DRAFTS_DIR" | grep -v "^total" | tail -n +2 | head -5
        local count
        count=$(ls -1 "$DRAFTS_DIR" | wc -l)
        if [[ $count -gt 5 ]]; then
            echo "   ... and $((count - 5)) more files"
        fi
    else
        echo "   (empty)"
    fi
    
    echo ""
    echo "📁 Finalized:"
    if [[ -d "$FINALIZED_DIR" ]] && [[ -n "$(ls -A "$FINALIZED_DIR" 2>/dev/null)" ]]; then
        ls -la "$FINALIZED_DIR" | grep -v "^total" | tail -n +2 | head -3
        local count
        count=$(ls -1 "$FINALIZED_DIR" | wc -l)
        if [[ $count -gt 3 ]]; then
            echo "   ... and $((count - 3)) more directories"
        fi
    else
        echo "   (empty)"
    fi
}

# Show session status
show_status() {
    local date_str
    date_str=$(date +"%Y-%m-%d")
    
    echo "🏖️ Sandbox Status:"
    echo "=================="
    echo "Date: $date_str"
    echo "Active Session: sandbox/today/"
    
    if [[ -d "$TODAY_DIR" ]] && [[ -n "$(ls -A "$TODAY_DIR" 2>/dev/null)" ]]; then
        local file_count
        file_count=$(ls -1 "$TODAY_DIR" | wc -l)
        echo "Files in session: $file_count"
        
        if [[ -f "${TODAY_DIR}/session-info.md" ]]; then
            echo ""
            echo "📋 Session Goals:"
            grep "^- \[ \]" "${TODAY_DIR}/session-info.md" | head -3 || echo "   No goals set"
        fi
    else
        echo "Status: No active session"
        echo "💡 Run 'SANDBOX START' to begin"
    fi
}

# Initialize sandbox structure
init_sandbox_structure

# Command interface
case "${1:-}" in
    "start")
        start_session
        ;;
    "finalize")
        finalize_session
        ;;
    "clean")
        clean_temp
        ;;
    "archive")
        archive_old_sessions "${2:-30}"
        ;;
    "list")
        list_contents
        ;;
    "status")
        show_status
        ;;
    *)
        echo "🏖️ uDOS Sandbox Manager v1.0"
        echo "============================"
        echo "Commands:"
        echo "  start       - Start new daily session"
        echo "  finalize    - Finalize current session"
        echo "  clean       - Clean temporary files"
        echo "  archive [days] - Archive old sessions (default: 30 days)"
        echo "  list        - List sandbox contents"
        echo "  status      - Show current session status"
        echo ""
        echo "Daily Workflow:"
        echo "  1. SANDBOX START    - Begin daily session"
        echo "  2. Work in sandbox/today/"
        echo "  3. SANDBOX FINALIZE - Archive and store in uMemory"
        echo ""
        echo "File Organization:"
        echo "  sandbox/today/     - Current session workspace"
        echo "  sandbox/drafts/    - Work in progress"
        echo "  sandbox/finalized/ - Ready for uMemory storage"
        echo "  sandbox/temp/      - Temporary files (auto-cleanup)"
        ;;
esac
