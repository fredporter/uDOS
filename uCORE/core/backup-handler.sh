#!/bin/bash
# backup-handler.sh - Central backup command handler for uDATA BACKUP commands
# Integrates with enhanced backup-restore.sh system

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/backup-restore.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ═══════════════════════════════════════════════════════════════════════
# BACKUP COMMAND HANDLER
# ═══════════════════════════════════════════════════════════════════════

# Main backup command handler - matches uDATA-commands.json format
handle_backup_command() {
    local action="${1:-}"
    shift || true

    case "$action" in
        CREATE)
            handle_backup_create "$@"
            ;;
        LIST)
            handle_backup_list "$@"
            ;;
        RESTORE)
            handle_backup_restore "$@"
            ;;
        STATUS)
            handle_backup_status "$@"
            ;;
        HISTORY)
            handle_backup_history "$@"
            ;;
        CLEANUP)
            handle_backup_cleanup "$@"
            ;;
        *)
            show_backup_help
            ;;
    esac
}

# Handle BACKUP CREATE command
handle_backup_create() {
    local backup_type="${1:-manual}"
    local description="${2:-Manual backup via uDATA command}"

    if [ -f "$BACKUP_SCRIPT" ]; then
        echo -e "${BLUE}📦 Creating $backup_type backup...${NC}"
        "$BACKUP_SCRIPT" backup "$backup_type" "$description"
    else
        echo -e "${YELLOW}⚠️  Enhanced backup system not found, using simple backup${NC}"
        "$UDOS_ROOT/uCORE/core/utilities/backup.sh" "$backup_type"
    fi
}

# Handle BACKUP LIST command
handle_backup_list() {
    if [ -f "$BACKUP_SCRIPT" ]; then
        echo -e "${BLUE}📋 Listing available backups...${NC}"
        "$BACKUP_SCRIPT" list
    else
        echo -e "${BLUE}📋 Available backups in /backup:${NC}"
        find "$UDOS_ROOT/backup" -name "*.tar.gz*" -type f -exec basename {} \; 2>/dev/null | sort -r | head -20
    fi
}

# Handle BACKUP RESTORE command
handle_backup_restore() {
    local backup_file="${1:-}"

    if [ -f "$BACKUP_SCRIPT" ]; then
        if [ -n "$backup_file" ]; then
            echo -e "${BLUE}🔄 Restoring from backup: $backup_file${NC}"
            "$BACKUP_SCRIPT" restore "$backup_file"
        else
            echo -e "${BLUE}🔄 Interactive restore mode...${NC}"
            "$BACKUP_SCRIPT" restore
        fi
    else
        echo -e "${RED}❌ Enhanced backup system required for restore${NC}"
        exit 1
    fi
}

# Handle BACKUP STATUS command
handle_backup_status() {
    if [ -f "$BACKUP_SCRIPT" ]; then
        echo -e "${BLUE}📊 Backup system status...${NC}"
        "$BACKUP_SCRIPT" status
    else
        echo -e "${BLUE}📊 Basic backup status:${NC}"
        local backup_count=$(find "$UDOS_ROOT/backup" -name "*.tar.gz*" -type f | wc -l | xargs)
        echo "Total backups: $backup_count"
        echo "Backup directory: $UDOS_ROOT/backup"
        echo "Latest backup: $(find "$UDOS_ROOT/backup" -name "*.tar.gz*" -type f -exec stat -f "%m %N" {} \; 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2- | xargs basename 2>/dev/null || echo "None")"
    fi
}

# Handle BACKUP HISTORY command
handle_backup_history() {
    if [ -f "$BACKUP_SCRIPT" ]; then
        echo -e "${BLUE}📜 Backup history...${NC}"
        "$BACKUP_SCRIPT" history
    else
        echo -e "${BLUE}📜 Recent backups:${NC}"
        find "$UDOS_ROOT/backup" -name "*.tar.gz*" -type f -exec stat -f "%m %N" {} \; 2>/dev/null | \
        sort -nr | head -10 | while read timestamp file; do
            date -r "$timestamp" "+%Y-%m-%d %H:%M:%S" 2>/dev/null && echo " - $(basename "$file")"
        done
    fi
}

# Handle BACKUP CLEANUP command
handle_backup_cleanup() {
    echo -e "${BLUE}🧹 Cleaning up old backups...${NC}"
    if [ -f "$BACKUP_SCRIPT" ]; then
        # Enhanced system handles its own cleanup during backup creation
        echo "Enhanced backup system maintains automatic cleanup"
    else
        # Simple cleanup for basic backups
        local backup_dir="$UDOS_ROOT/backup"
        local backup_count=$(find "$backup_dir" -name "*.tar.gz*" -type f | wc -l | xargs)

        if [ "$backup_count" -gt 5 ]; then
            echo "Found $backup_count backups, keeping 5 most recent..."
            find "$backup_dir" -name "*.tar.gz*" -type f -exec stat -f "%m %N" {} \; 2>/dev/null | \
            sort -nr | tail -n +6 | cut -d' ' -f2- | while read file; do
                echo "Removing old backup: $(basename "$file")"
                rm -f "$file"
            done
        else
            echo "Only $backup_count backups found, no cleanup needed"
        fi
    fi
}

# Show backup help
show_backup_help() {
    echo -e "${BLUE}📦 uDOS BACKUP Command Help${NC}"
    echo ""
    echo "Usage: BACKUP <action> [options]"
    echo ""
    echo "Actions:"
    echo "  CREATE [type] [description]  - Create new backup (manual/auto/session)"
    echo "  LIST                         - List available backups"
    echo "  RESTORE [file]              - Restore from backup (interactive if no file)"
    echo "  STATUS                      - Show backup system status"
    echo "  HISTORY                     - Show backup history"
    echo "  CLEANUP                     - Clean up old backups"
    echo ""
    echo "Examples:"
    echo "  BACKUP CREATE              - Create manual backup"
    echo "  BACKUP CREATE session      - Create session backup"
    echo "  BACKUP LIST                - Show available backups"
    echo "  BACKUP RESTORE             - Interactive restore"
    echo "  BACKUP RESTORE backup.tar.gz - Restore specific backup"
    echo ""
    echo "Features:"
    echo "  • Role-based access control"
    echo "  • AES-256-CBC encryption (if password set)"
    echo "  • Automatic cleanup and retention"
    echo "  • Session-based undo/redo support"
    echo "  • Centralized storage in /backup"
}

# ═══════════════════════════════════════════════════════════════════════
# SESSION COMMANDS (UNDO/REDO/HISTORY)
# ═══════════════════════════════════════════════════════════════════════

# Handle SESSION command for undo/redo operations
handle_session_command() {
    local action="${1:-}"
    shift || true

    if [ ! -f "$BACKUP_SCRIPT" ]; then
        echo -e "${RED}❌ Enhanced backup system required for session commands${NC}"
        exit 1
    fi

    case "$action" in
        SAVE)
            echo -e "${BLUE}💾 Creating session save point...${NC}"
            "$BACKUP_SCRIPT" backup session "Session save point"
            ;;
        UNDO)
            echo -e "${BLUE}↶ Undoing last operation...${NC}"
            "$BACKUP_SCRIPT" undo
            ;;
        REDO)
            echo -e "${BLUE}↷ Redoing operation...${NC}"
            "$BACKUP_SCRIPT" redo
            ;;
        HISTORY)
            echo -e "${BLUE}📜 Session history...${NC}"
            "$BACKUP_SCRIPT" history
            ;;
        CLEAR)
            echo -e "${BLUE}🧹 Clearing session history...${NC}"
            "$BACKUP_SCRIPT" init-session
            ;;
        STATUS)
            echo -e "${BLUE}📊 Session status...${NC}"
            "$BACKUP_SCRIPT" status
            ;;
        *)
            show_session_help
            ;;
    esac
}

# Show session help
show_session_help() {
    echo -e "${BLUE}🎯 uDOS SESSION Command Help${NC}"
    echo ""
    echo "Usage: SESSION <action>"
    echo ""
    echo "Actions:"
    echo "  SAVE                        - Create session save point"
    echo "  UNDO                        - Undo last operation"
    echo "  REDO                        - Redo undone operation"
    echo "  HISTORY                     - Show session history"
    echo "  CLEAR                       - Clear session history"
    echo "  STATUS                      - Show session status"
    echo ""
    echo "Examples:"
    echo "  SESSION SAVE               - Save current state"
    echo "  SESSION UNDO               - Undo last change"
    echo "  SESSION REDO               - Redo last undo"
    echo "  SESSION HISTORY            - View session timeline"
}

# ═══════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════

# Main execution based on first argument
main() {
    local command="${1:-}"
    shift || true

    case "$command" in
        BACKUP)
            handle_backup_command "$@"
            ;;
        SESSION)
            handle_session_command "$@"
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $command${NC}"
            echo "Supported commands: BACKUP, SESSION"
            exit 1
            ;;
    esac
}

# Run main function if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
