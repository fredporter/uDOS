echo "User folder backed up to $BACKUP_DIR/user-backup-$STAMP.tar.gz"
#!/bin/bash
# uDOS User Folder Backup Script
# Supports: BACKUP, RESTORE, REDO, UNDO, SESSION, CLEANUP
# Only backs up user folder. In dev mode, also backs up core folders to wizard/backup.

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
USER_DIR="$UDOS_ROOT/sandbox/user"
BACKUP_DIR="$UDOS_ROOT/sandbox/backup"
WIZARD_BACKUP_DIR="$UDOS_ROOT/wizard/backup"
SESSION_ID="${UDOS_SESSION_ID:-default}"


automate_session_backup() {
    # Run session backup every 30 minutes (example)
    while true; do
        session_backup
        cleanup_backups
        sleep 1800
    done
}

repair_core_system() {
    if [[ "${UDOS_DEV_MODE:-false}" == "true" ]]; then
        echo "Checking for core/system file modifications via git..."
        cd "$UDOS_ROOT"
        local modified=$(git status --porcelain | grep -E "^( M|MM|AM|RM|A |R |D )" | grep -E "uCORE|uSERVER|uSCRIPT|uMEMORY|uKNOWLEDGE")
        if [[ -n "$modified" ]]; then
            echo "Modifications detected in core/system files:"
            echo "$modified"
            echo "Attempting git repair (checkout)..."
            echo "$modified" | awk '{print $2}' | xargs git checkout --
            echo "Repair complete."
        else
            echo "No core/system modifications detected."
        fi
    else
        echo "REPAIR only available in dev mode."
    fi
}

push_dev_mode() {
    if [[ "${UDOS_DEV_MODE:-false}" == "true" ]]; then
        cd "$UDOS_ROOT"
        git add -A
        git commit -m "Dev Mode PUSH: Automated commit $(date +%Y%m%d-%H%M%S)"
        git push
        echo "Dev Mode PUSH complete."
    else
        echo "Dev Mode PUSH only available in dev mode."
    fi
}
# uDOS Ethos: Clean, flat, minimal data. Respect host system. Backup and cleanup always.

STAMP=$(date +%Y%m%d-%H%M%S)

backup_user() {
    mkdir -p "$BACKUP_DIR"
    tar czf "$BACKUP_DIR/user-backup-$STAMP-$SESSION_ID.tar.gz" -C "$USER_DIR" .
    echo "User folder backed up to $BACKUP_DIR/user-backup-$STAMP-$SESSION_ID.tar.gz"
    if [[ "${UDOS_DEV_MODE:-false}" == "true" ]]; then
        mkdir -p "$WIZARD_BACKUP_DIR"
        for core in uCORE uSERVER uSCRIPT uMEMORY uKNOWLEDGE; do
            if [[ -d "$UDOS_ROOT/$core" ]]; then
                tar czf "$WIZARD_BACKUP_DIR/${core}-backup-$STAMP-$SESSION_ID.tar.gz" -C "$UDOS_ROOT/$core" .
                echo "$core backed up to $WIZARD_BACKUP_DIR/${core}-backup-$STAMP-$SESSION_ID.tar.gz"
            fi
        done
    fi
    AUTOBACKUP)
        automate_session_backup
        ;;
    REPAIR)
        repair_core_system
        ;;
    PUSH)
        push_dev_mode
        ;;
}

restore_user() {
    local file=$(ls -t "$BACKUP_DIR"/user-backup-*-$SESSION_ID.tar.gz 2>/dev/null | head -1)
    if [[ -f "$file" ]]; then
        tar xzf "$file" -C "$USER_DIR"
        echo "User folder restored from $file"
    else
        echo "No backup found for session $SESSION_ID"
    fi
}

redo_user() {
    backup_user
    echo "REDO: User folder backed up again."
}

undo_user() {
    restore_user
    echo "UNDO: User folder restored to last backup."
}

session_backup() {
    backup_user
    echo "Session backup complete."
}

cleanup_backups() {
    # Keep only last 5 backups per session
    find "$BACKUP_DIR" -name "user-backup-*-$SESSION_ID.tar.gz" | sort -r | tail -n +6 | xargs rm -f
    echo "Old backups cleaned for session $SESSION_ID."
}

case "${1:-BACKUP}" in
    BACKUP)
        backup_user
        ;;
    RESTORE)
        restore_user
        ;;
    REDO)
        redo_user
        ;;
    UNDO)
        undo_user
        ;;
    SESSION)
        session_backup
        ;;
    CLEANUP)
        cleanup_backups
        ;;
    *)
        echo "Usage: $0 [BACKUP|RESTORE|REDO|UNDO|SESSION|CLEANUP]"
        ;;
esac
