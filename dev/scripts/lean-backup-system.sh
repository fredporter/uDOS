#!/bin/bash
# uDOS v1.0.5.5 - Lean Backup System
# Intelligent backup with automatic expunging and size limits

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Backup configuration
BACKUP_ROOT="$UDOS_ROOT/dev/backups"
MAX_BACKUPS_SAFETY=3        # Keep only 3 safety backups
MAX_BACKUPS_SESSION=5       # Keep only 5 session backups  
MAX_BACKUPS_CONFIG=2        # Keep only 2 config backups
MAX_BACKUP_SIZE_MB=100      # Alert if backup exceeds 100MB
EXCLUDE_PATTERNS=(
    ".git"
    "node_modules"
    "*.log"
    "*.pid"
    "*.lock"
    "dev/backups"              # Never backup the backup directory!
    "sandbox/temp"
    "sandbox/trash" 
    "sandbox/logs"
    "uSCRIPT/venv"
    "uSCRIPT/legacy-python"
    "*/.cache"
    "*/cache"
    "*/__pycache__"
    "*.pyc"
    "build"
    "dist"
    ".DS_Store"
)

# Core directories to backup (essential only)
CORE_DIRS=(
    "uCORE/code"
    "uCORE/config"
    "uMEMORY/schemas"
    "uKNOWLEDGE/schemas"
    "uNETWORK/config"
    "uSCRIPT/config"
    "dev/scripts"
)

# Create lean backup
create_lean_backup() {
    local backup_type="$1"
    local backup_name="$2"
    local timestamp="$(date +%Y%m%d_%H%M%S)"
    local backup_dir="$BACKUP_ROOT/$backup_type"
    local backup_file="$backup_dir/${backup_name}_${timestamp}.tar.gz"
    
    echo "🗜️  Creating lean backup: $backup_type/$backup_name"
    
    # Create backup directory
    mkdir -p "$backup_dir"
    
    # Build exclude arguments
    local exclude_args=""
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        exclude_args="$exclude_args --exclude=$pattern"
    done
    
    # Create backup of core directories only
    if [ "$backup_type" = "safety" ]; then
        # Safety backup: core code only
        tar -czf "$backup_file" $exclude_args \
            -C "$UDOS_ROOT" \
            "${CORE_DIRS[@]}" 2>/dev/null || true
    elif [ "$backup_type" = "session" ]; then
        # Session backup: include user data
        tar -czf "$backup_file" $exclude_args \
            -C "$UDOS_ROOT" \
            "${CORE_DIRS[@]}" \
            uMEMORY/user \
            sandbox/session 2>/dev/null || true
    else
        # Full backup (but still exclude large/temp files)
        tar -czf "$backup_file" $exclude_args \
            -C "$UDOS_ROOT" \
            uCORE uMEMORY uKNOWLEDGE uNETWORK uSCRIPT 2>/dev/null || true
    fi
    
    # Check backup size
    if [ -f "$backup_file" ]; then
        local size_kb=$(du -k "$backup_file" | cut -f1)
        local size_mb=$((size_kb / 1024))
        
        if [ $size_mb -gt $MAX_BACKUP_SIZE_MB ]; then
            echo "⚠️  Warning: Backup size ${size_mb}MB exceeds limit (${MAX_BACKUP_SIZE_MB}MB)"
        else
            echo "✅ Backup created: ${size_mb}MB"
        fi
    else
        echo "❌ Backup failed"
        return 1
    fi
}

# Expunge old backups
expunge_old_backups() {
    local backup_type="$1"
    local max_backups="$2"
    local backup_dir="$BACKUP_ROOT/$backup_type"
    
    if [ ! -d "$backup_dir" ]; then
        return 0
    fi
    
    cd "$backup_dir"
    local backup_count=$(ls -1 *.tar.gz 2>/dev/null | wc -l)
    
    if [ $backup_count -gt $max_backups ]; then
        local to_remove=$((backup_count - max_backups))
        echo "🗑️  Expunging $to_remove old $backup_type backups"
        ls -t *.tar.gz 2>/dev/null | tail -n +$((max_backups + 1)) | xargs rm -f
    fi
}

# Show backup status
show_backup_status() {
    echo "📊 Lean Backup System Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local total_size=0
    for backup_type in safety session config; do
        local backup_dir="$BACKUP_ROOT/$backup_type"
        if [ -d "$backup_dir" ]; then
            local count=$(ls -1 "$backup_dir"/*.tar.gz 2>/dev/null | wc -l)
            local size_kb=$(du -sk "$backup_dir" 2>/dev/null | cut -f1)
            local size_mb=$((size_kb / 1024))
            total_size=$((total_size + size_mb))
            
            echo "  $backup_type: $count backups, ${size_mb}MB"
        else
            echo "  $backup_type: 0 backups, 0MB"
        fi
    done
    
    echo "  Total: ${total_size}MB"
    echo ""
}

# Clean all backups
clean_all_backups() {
    echo "🧹 Cleaning all backups..."
    rm -rf "$BACKUP_ROOT"/*
    echo "✅ All backups removed"
}

# Main function
main() {
    case "${1:-status}" in
        "safety")
            create_lean_backup "safety" "core"
            expunge_old_backups "safety" $MAX_BACKUPS_SAFETY
            ;;
        "session")
            create_lean_backup "session" "user"
            expunge_old_backups "session" $MAX_BACKUPS_SESSION
            ;;
        "config")
            create_lean_backup "config" "settings"
            expunge_old_backups "config" $MAX_BACKUPS_CONFIG
            ;;
        "clean")
            clean_all_backups
            ;;
        "status")
            show_backup_status
            ;;
        *)
            echo "Usage: $0 [safety|session|config|clean|status]"
            echo ""
            echo "Lean Backup System - Only essential files, auto-expunging"
            echo "  safety  - Backup core code only (${MAX_BACKUPS_SAFETY} kept)"
            echo "  session - Backup code + user data (${MAX_BACKUPS_SESSION} kept)"
            echo "  config  - Backup configuration (${MAX_BACKUPS_CONFIG} kept)"
            echo "  clean   - Remove all backups"
            echo "  status  - Show backup status"
            ;;
    esac
}

main "$@"
