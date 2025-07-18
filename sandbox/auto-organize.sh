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
