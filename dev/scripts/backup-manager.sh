#!/bin/bash
# uDOS Backup Management System
# Universal Device Operating System
# Version: 1.0.5.3

# Centralized backup management for uDOS
# All backups are stored in dev/backups/ with proper organization

# Set up environment
UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
BACKUP_ROOT="${UDOS_ROOT}/dev/backups"
BACKUP_CONFIG="${BACKUP_ROOT}/backup-config.json"

# Backup directories
DAILY_BACKUPS="${BACKUP_ROOT}/daily"
MANUAL_BACKUPS="${BACKUP_ROOT}/manual"
SESSION_BACKUPS="${BACKUP_ROOT}/sessions"
CONFIG_BACKUPS="${BACKUP_ROOT}/config"

# Export environment
export UDOS_ROOT BACKUP_ROOT

# Initialize backup system
init_backup_system() {
    echo "💾 Initializing uDOS Backup Management System"
    echo "============================================="
    
    # Create backup directories
    mkdir -p "$DAILY_BACKUPS" "$MANUAL_BACKUPS" "$SESSION_BACKUPS" "$CONFIG_BACKUPS"
    
    # Create backup configuration
    if [[ ! -f "$BACKUP_CONFIG" ]]; then
        cat > "$BACKUP_CONFIG" << 'EOF'
{
    "backup_settings": {
        "max_daily_backups": 7,
        "max_manual_backups": 20,
        "max_session_backups": 10,
        "max_config_backups": 5,
        "compression": true,
        "cleanup_enabled": true
    },
    "backup_paths": [
        "uCORE/code/registry.json",
        "uCORE/config",
        "uMEMORY/data",
        "uKNOWLEDGE/data",
        "VERSION",
        "sandbox/session"
    ],
    "exclude_patterns": [
        "*.log",
        "cache/*",
        "tmp/*",
        ".git/*"
    ]
}
EOF
    fi
    
    echo "✅ Backup system initialized"
    echo "📁 Backup root: $BACKUP_ROOT"
}

# Create backup
create_backup() {
    local backup_type="$1"  # daily, manual, session, config
    local backup_name="${2:-$(date +%Y%m%d_%H%M%S)}"
    local description="${3:-Auto backup}"
    
    case "$backup_type" in
        "daily"|"manual"|"session"|"config")
            local backup_dir="${BACKUP_ROOT}/${backup_type}s/${backup_name}"
            ;;
        *)
            echo "ERROR: Invalid backup type. Use: daily, manual, session, config"
            return 1
            ;;
    esac
    
    echo "📦 Creating $backup_type backup: $backup_name"
    mkdir -p "$backup_dir"
    
    # Create backup manifest
    cat > "${backup_dir}/manifest.json" << EOF
{
    "backup_type": "$backup_type",
    "backup_name": "$backup_name",
    "description": "$description",
    "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "udos_version": "$(grep VERSION "$UDOS_ROOT/VERSION" | cut -d'=' -f2 | tr -d '"')"
}
EOF
    
    # Read backup paths from config
    local backup_paths
    if command -v python >/dev/null 2>&1 && [[ -f "$BACKUP_CONFIG" ]]; then
        backup_paths="$(python -c "
import json
with open('$BACKUP_CONFIG', 'r') as f: 
    config = json.load(f)
for path in config['backup_paths']:
    print(path)
")"
    else
        # Fallback backup paths
        backup_paths="uCORE/code/registry.json
uCORE/config
VERSION
sandbox/session"
    fi
    
    # Create backups
    echo "$backup_paths" | while read -r path; do
        if [[ -n "$path" && -e "${UDOS_ROOT}/${path}" ]]; then
            local dest_path="${backup_dir}/${path}"
            mkdir -p "$(dirname "$dest_path")"
            cp -r "${UDOS_ROOT}/${path}" "$dest_path" 2>/dev/null || echo "Warning: Could not backup $path"
        fi
    done
    
    # Compress if enabled
    if command -v tar >/dev/null 2>&1; then
        cd "$BACKUP_ROOT/${backup_type}s"
        tar -czf "${backup_name}.tar.gz" "$backup_name"
        rm -rf "$backup_name"
        echo "✅ Backup compressed: ${backup_name}.tar.gz"
    fi
    
    # Cleanup old backups
    cleanup_old_backups "$backup_type"
    
    echo "✅ Backup created successfully"
}

# List backups
list_backups() {
    local backup_type="${1:-all}"
    
    echo "📋 uDOS Backup Inventory"
    echo "======================="
    
    case "$backup_type" in
        "all")
            for type in daily manual session config; do
                list_backup_type "$type"
            done
            ;;
        "daily"|"manual"|"session"|"config")
            list_backup_type "$backup_type"
            ;;
        *)
            echo "ERROR: Invalid backup type. Use: all, daily, manual, session, config"
            return 1
            ;;
    esac
}

# List backups by type
list_backup_type() {
    local backup_type="$1"
    local backup_dir="${BACKUP_ROOT}/${backup_type}s"
    
    echo ""
    echo "📁 $(echo "$backup_type" | sed 's/./\U&/') backups:"
    if [[ -d "$backup_dir" ]]; then
        find "$backup_dir" -name "*.tar.gz" -o -type d -mindepth 1 -maxdepth 1 | sort | while read -r backup; do
            local backup_name="$(basename "$backup" .tar.gz)"
            echo "  - $backup_name"
        done
    else
        echo "  No $backup_type backups found"
    fi
}

# Restore backup
restore_backup() {
    local backup_type="$1"
    local backup_name="$2"
    local target_path="${3:-$UDOS_ROOT}"
    
    if [[ -z "$backup_type" || -z "$backup_name" ]]; then
        echo "ERROR: Backup type and name required"
        return 1
    fi
    
    local backup_file="${BACKUP_ROOT}/${backup_type}s/${backup_name}.tar.gz"
    local backup_dir="${BACKUP_ROOT}/${backup_type}s/${backup_name}"
    
    echo "🔄 Restoring backup: $backup_name"
    
    # Extract if compressed
    if [[ -f "$backup_file" ]]; then
        cd "${BACKUP_ROOT}/${backup_type}s"
        tar -xzf "${backup_name}.tar.gz"
    fi
    
    if [[ ! -d "$backup_dir" ]]; then
        echo "ERROR: Backup $backup_name not found"
        return 1
    fi
    
    # Restore files
    echo "Restoring to: $target_path"
    cp -r "${backup_dir}"/* "$target_path/"
    
    echo "✅ Backup restored successfully"
}

# Cleanup old backups
cleanup_old_backups() {
    local backup_type="$1"
    local max_backups
    
    # Get max backups from config
    if command -v python >/dev/null 2>&1 && [[ -f "$BACKUP_CONFIG" ]]; then
        max_backups="$(python -c "
import json
with open('$BACKUP_CONFIG', 'r') as f: 
    config = json.load(f)
print(config['backup_settings']['max_${backup_type}_backups'])
" 2>/dev/null || echo "5")"
    else
        max_backups=5
    fi
    
    local backup_dir="${BACKUP_ROOT}/${backup_type}s"
    
    if [[ -d "$backup_dir" ]]; then
        # Count existing backups
        local backup_count
        backup_count="$(find "$backup_dir" -name "*.tar.gz" | wc -l | tr -d ' ')"
        
        if [[ $backup_count -gt $max_backups ]]; then
            local excess=$((backup_count - max_backups))
            echo "🧹 Cleaning up $excess old $backup_type backups..."
            
            # Remove oldest backups
            find "$backup_dir" -name "*.tar.gz" | sort | head -n "$excess" | while read -r old_backup; do
                rm -f "$old_backup"
                echo "  Removed: $(basename "$old_backup")"
            done
        fi
    fi
}

# Backup statistics
backup_stats() {
    echo "📊 Backup Statistics"
    echo "==================="
    
    local total_size=0
    
    for type in daily manual session config; do
        local backup_dir="${BACKUP_ROOT}/${type}s"
        local count=0
        local size=0
        local type_name
        
        # Bash 3.x compatible capitalization
        case "$type" in
            "daily") type_name="Daily" ;;
            "manual") type_name="Manual" ;;
            "session") type_name="Session" ;;
            "config") type_name="Config" ;;
        esac
        
        if [[ -d "$backup_dir" ]]; then
            count="$(find "$backup_dir" -name "*.tar.gz" | wc -l | tr -d ' ')"
            if command -v du >/dev/null 2>&1; then
                size="$(du -sh "$backup_dir" 2>/dev/null | cut -f1 || echo "0")"
            fi
        fi
        
        echo "$type_name: $count backups ($size)"
    done
    
    if command -v du >/dev/null 2>&1; then
        local total_size_human
        total_size_human="$(du -sh "$BACKUP_ROOT" 2>/dev/null | cut -f1 || echo "0")"
        echo "Total: $total_size_human"
    fi
}

# Main command handler
main() {
    local command="${1:-help}"
    
    case "$command" in
        "init")
            init_backup_system
            ;;
        "create")
            local backup_type="$2"
            local backup_name="$3"
            local description="$4"
            create_backup "$backup_type" "$backup_name" "$description"
            ;;
        "list")
            local backup_type="$2"
            list_backups "$backup_type"
            ;;
        "restore")
            local backup_type="$2"
            local backup_name="$3"
            local target_path="$4"
            restore_backup "$backup_type" "$backup_name" "$target_path"
            ;;
        "cleanup")
            echo "🧹 Cleaning up old backups..."
            for type in daily manual session config; do
                cleanup_old_backups "$type"
            done
            echo "✅ Cleanup complete"
            ;;
        "stats")
            backup_stats
            ;;
        "help")
            echo "uDOS Backup Management System v1.0.5.3"
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Commands:"
            echo "  init                                - Initialize backup system"
            echo "  create <type> [name] [description] - Create backup (type: daily|manual|session|config)"
            echo "  list [type]                         - List backups (type: all|daily|manual|session|config)"
            echo "  restore <type> <name> [target]     - Restore backup"
            echo "  cleanup                             - Clean up old backups"
            echo "  stats                               - Show backup statistics"
            echo "  help                                - Show this help"
            ;;
        *)
            echo "Unknown command: $command"
            echo "Use '$0 help' for usage information"
            return 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
