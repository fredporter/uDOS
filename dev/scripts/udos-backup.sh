#!/bin/bash

# uDOS Unified Backup Interface v1.4.0
# Central interface for all backup operations in uDOS
# Integrates with enhanced backup system and legacy compatibility

set -euo pipefail

readonly SCRIPT_NAME="udos-backup"
readonly VERSION="1.4.0"
readonly UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# Core backup system
readonly ENHANCED_BACKUP="$UDOS_ROOT/dev/scripts/enhanced-backup-system.sh"
readonly BACKUP_MIGRATION="$UDOS_ROOT/dev/scripts/migrate-backups.sh"
readonly BACKUP_CONFIG="$UDOS_ROOT/dev/scripts/backup-config.sh"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'
readonly BOLD='\033[1m'

# Source configuration if available
[[ -f "$BACKUP_CONFIG" ]] && source "$BACKUP_CONFIG"

log() {
    local level="$1"
    shift
    echo -e "${BOLD}[$(date +'%H:%M:%S')] ${level}:${NC} $*" >&2
}

log_info() { log "${BLUE}INFO${NC}" "$@"; }
log_warn() { log "${YELLOW}WARN${NC}" "$@"; }
log_error() { log "${RED}ERROR${NC}" "$@"; }
log_success() { log "${GREEN}SUCCESS${NC}" "$@"; }

# ═══════════════════════════════════════════════════════════════════════
# INITIALIZATION AND MIGRATION
# ═══════════════════════════════════════════════════════════════════════

# Initialize backup system
initialize_backup_system() {
    log_info "Initializing uDOS backup system..."

    # Ensure root backup directory exists
    mkdir -p "$UDOS_ROOT/backup"

    # Check if migration is needed
    if needs_migration; then
        log_info "Legacy backups detected - migration recommended"
        echo ""
        echo -e "${BOLD}${YELLOW}📦 Legacy Backup Migration${NC}"
        echo -e "${BOLD}═══════════════════════════════${NC}"
        echo "Legacy backup files were found in distributed locations."
        echo "These should be migrated to the new centralized backup system."
        echo ""
        read -p "Run migration now? (yes/no): " migrate_confirm

        if [[ "$migrate_confirm" == "yes" ]]; then
            if [[ -x "$BACKUP_MIGRATION" ]]; then
                "$BACKUP_MIGRATION" migrate
            else
                log_error "Migration script not found or not executable"
                return 1
            fi
        else
            log_warn "Migration skipped - you can run it later with: $BACKUP_MIGRATION migrate"
        fi
    fi

    log_success "Backup system initialized"
}

# Check if migration is needed
needs_migration() {
    local legacy_dirs=(
        "wizard/backup"
        "sorcerer/backup"
        "imp/backup"
        "ghost/backup"
        "drone/backup"
        "tomb/backup"
        "uMEMORY/backups"
    )

    for legacy_dir in "${legacy_dirs[@]}"; do
        local full_path="$UDOS_ROOT/$legacy_dir"
        if [[ -d "$full_path" ]] && [[ -n "$(find "$full_path" -name "*.tar.gz" -o -name "*.tar.gz.enc" 2>/dev/null | head -1)" ]]; then
            return 0  # Migration needed
        fi
    done

    return 1  # No migration needed
}

# ═══════════════════════════════════════════════════════════════════════
# BACKUP OPERATIONS
# ═══════════════════════════════════════════════════════════════════════

# Create backup with enhanced system
create_backup() {
    local backup_type="${1:-manual}"
    local description="${2:-}"
    local force_init="${3:-false}"

    # Initialize if needed
    if [[ "$force_init" == "true" ]] || [[ ! -d "$UDOS_ROOT/backup" ]]; then
        initialize_backup_system
    fi

    # Delegate to enhanced backup system
    if [[ -x "$ENHANCED_BACKUP" ]]; then
        "$ENHANCED_BACKUP" create "$backup_type" "$description"
    else
        log_error "Enhanced backup system not found"
        return 1
    fi
}

# List backups
list_backups() {
    local filter_type="${1:-}"
    local filter_role="${2:-}"

    if [[ -x "$ENHANCED_BACKUP" ]]; then
        "$ENHANCED_BACKUP" list "$filter_type" "$filter_role"
    else
        log_error "Enhanced backup system not found"
        return 1
    fi
}

# Restore from backup
restore_backup() {
    local backup_choice="${1:-}"

    if [[ -x "$ENHANCED_BACKUP" ]]; then
        "$ENHANCED_BACKUP" restore "$backup_choice"
    else
        log_error "Enhanced backup system not found"
        return 1
    fi
}

# Show backup statistics
show_stats() {
    if [[ -x "$ENHANCED_BACKUP" ]]; then
        "$ENHANCED_BACKUP" stats
    else
        log_error "Enhanced backup system not found"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# AUTOMATED BACKUP TRIGGERS
# ═══════════════════════════════════════════════════════════════════════

# Startup backup
backup_startup() {
    if [[ "${BACKUP_AUTO_ON_STARTUP:-true}" == "true" ]]; then
        log_info "Creating automatic startup backup..."
        create_backup "startup" "Automatic backup on system startup"
    fi
}

# Exit backup
backup_exit() {
    if [[ "${BACKUP_AUTO_ON_EXIT:-true}" == "true" ]]; then
        log_info "Creating automatic exit backup..."
        create_backup "exit" "Automatic backup on system exit"
    fi
}

# Session backup
backup_session() {
    if [[ "${BACKUP_AUTO_ON_SESSION_START:-true}" == "true" ]]; then
        log_info "Creating automatic session backup..."
        create_backup "session" "Automatic backup on session start"
    fi
}

# Emergency backup
backup_emergency() {
    local reason="${1:-System error detected}"
    log_warn "Creating emergency backup: $reason"
    create_backup "emergency" "Emergency backup: $reason"
}

# ═══════════════════════════════════════════════════════════════════════
# LEGACY COMPATIBILITY
# ═══════════════════════════════════════════════════════════════════════

# Legacy backup function for compatibility with existing scripts
legacy_backup() {
    local role="${1:-wizard}"
    local backup_type="${2:-manual}"
    local description="${3:-Legacy backup}"

    log_info "Legacy backup compatibility mode"
    create_backup "$backup_type" "$description ($role compatibility)"
}

# Legacy restore function
legacy_restore() {
    local role="${1:-wizard}"

    log_info "Legacy restore compatibility mode"
    echo -e "${YELLOW}Note: Using unified backup system${NC}"
    list_backups
    echo ""
    read -p "Enter backup number to restore: " choice
    restore_backup "$choice"
}

# ═══════════════════════════════════════════════════════════════════════
# MAINTENANCE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════

# Cleanup old backups
cleanup_backups() {
    if [[ -x "$ENHANCED_BACKUP" ]]; then
        "$ENHANCED_BACKUP" cleanup
    else
        log_error "Enhanced backup system not found"
        return 1
    fi
}

# Health check
health_check() {
    echo -e "${BOLD}${BLUE}🏥 Backup System Health Check${NC}"
    echo -e "${BOLD}═══════════════════════════════${NC}"
    echo ""

    local issues=0

    # Check backup directory
    if [[ -d "$UDOS_ROOT/backup" ]]; then
        echo -e "  ✅ Backup directory exists"
    else
        echo -e "  ❌ Backup directory missing"
        ((issues++))
    fi

    # Check enhanced backup system
    if [[ -x "$ENHANCED_BACKUP" ]]; then
        echo -e "  ✅ Enhanced backup system available"
    else
        echo -e "  ❌ Enhanced backup system not found"
        ((issues++))
    fi

    # Check configuration
    if [[ -f "$BACKUP_CONFIG" ]]; then
        echo -e "  ✅ Backup configuration available"
    else
        echo -e "  ⚠️  Backup configuration missing (using defaults)"
    fi

    # Check password setup
    if [[ -f "$UDOS_ROOT/sandbox/user.md" ]] && grep -q "Password: SET" "$UDOS_ROOT/sandbox/user.md"; then
        echo -e "  ✅ Password encryption available"
    else
        echo -e "  ⚠️  No password set (backups will be unencrypted)"
    fi

    # Check for legacy backups
    if needs_migration; then
        echo -e "  ⚠️  Legacy backups detected (migration recommended)"
    else
        echo -e "  ✅ No legacy backups found"
    fi

    echo ""
    if [[ $issues -eq 0 ]]; then
        echo -e "${GREEN}✅ Backup system is healthy${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Backup system has $issues issue(s)${NC}"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# MAIN INTERFACE
# ═══════════════════════════════════════════════════════════════════════

main() {
    local action="${1:-help}"

    case "$action" in
        # Core operations
        "create"|"backup")
            local type="${2:-manual}"
            local description="${3:-}"
            create_backup "$type" "$description" true
            ;;
        "list"|"ls"|"show")
            local filter_type="${2:-}"
            local filter_role="${3:-}"
            list_backups "$filter_type" "$filter_role"
            ;;
        "restore")
            local choice="${2:-}"
            restore_backup "$choice"
            ;;
        "stats"|"status"|"info")
            show_stats
            ;;

        # Automated triggers
        "startup")
            backup_startup
            ;;
        "exit")
            backup_exit
            ;;
        "session")
            backup_session
            ;;
        "emergency")
            local reason="${2:-System error}"
            backup_emergency "$reason"
            ;;

        # Legacy compatibility
        "legacy-backup")
            local role="${2:-wizard}"
            local type="${3:-manual}"
            local desc="${4:-Legacy backup}"
            legacy_backup "$role" "$type" "$desc"
            ;;
        "legacy-restore")
            local role="${2:-wizard}"
            legacy_restore "$role"
            ;;

        # Maintenance
        "cleanup")
            cleanup_backups
            ;;
        "migrate")
            if [[ -x "$BACKUP_MIGRATION" ]]; then
                "$BACKUP_MIGRATION" "${2:-migrate}"
            else
                log_error "Migration script not found"
                return 1
            fi
            ;;
        "init"|"initialize")
            initialize_backup_system
            ;;
        "health"|"check")
            health_check
            ;;

        # Help
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "Unknown action: $action"
            show_help
            return 1
            ;;
    esac
}

show_help() {
    cat << EOF
${BOLD}uDOS Unified Backup Interface v$VERSION${NC}

${BOLD}USAGE:${NC}
    $0 <action> [options]

${BOLD}CORE OPERATIONS:${NC}
    create [type] [description]  Create new backup
    list [type] [role]          List available backups
    restore [number]            Restore from backup
    stats                       Show backup statistics

${BOLD}AUTOMATED TRIGGERS:${NC}
    startup                     Create startup backup
    exit                        Create exit backup
    session                     Create session backup
    emergency [reason]          Create emergency backup

${BOLD}LEGACY COMPATIBILITY:${NC}
    legacy-backup [role] [type] Create backup (legacy mode)
    legacy-restore [role]       Restore backup (legacy mode)

${BOLD}MAINTENANCE:${NC}
    cleanup                     Clean up old backups
    migrate                     Migrate legacy backups
    init                        Initialize backup system
    health                      Run health check

${BOLD}BACKUP TYPES:${NC}
    manual, daily, session, startup, exit, emergency, pre-restore

${BOLD}EXAMPLES:${NC}
    $0 create manual "Before system update"
    $0 list manual
    $0 restore 1
    $0 migrate
    $0 health

${BOLD}FEATURES:${NC}
    ✅ Centralized backup storage in root backup folder
    ✅ Automatic password encryption when configured
    ✅ Legacy backup system compatibility
    ✅ Smart cleanup with retention policies
    ✅ Comprehensive metadata tracking
    ✅ Migration tools for existing backups

${BOLD}STORAGE:${NC}
    All backups stored in: ${PURPLE}$UDOS_ROOT/backup${NC}

EOF
}

# Install signal handlers for automatic backups
trap 'backup_exit' EXIT
trap 'backup_emergency "System interrupt"' INT
trap 'backup_emergency "System termination"' TERM

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
