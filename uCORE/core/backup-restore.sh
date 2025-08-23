#!/bin/bash
# backup-restore.sh - Enhanced Backup/Restore System with Undo/Redo
# uDOS v1.3 - Advanced backup management with session-based undo/redo

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source common utilities from uCORE
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Configuration - using sandbox for session data
USER_MD_FILE="$UDOS_ROOT/sandbox/user.md"
UMEMORY_DIR="$UDOS_ROOT/uMEMORY"
SANDBOX_SESSION="$UDOS_ROOT/sandbox/session"
SESSION_MOVES_LOG="$SANDBOX_SESSION/moves/current-session.json"
DAILY_MOVES_LOG="$SANDBOX_SESSION/logs/daily-moves-$(date +%Y%m%d).json"
UNDO_STACK_FILE="$SANDBOX_SESSION/undo-stack/undo-stack.json"
BACKUP_METADATA="$UMEMORY_DIR/system/backup-metadata.json"

# Ensure system directories exist - using centralized backup structure and sandbox session
mkdir -p "$UMEMORY_DIR/system"
mkdir -p "$UDOS_ROOT/backup/session-backups"
mkdir -p "$UDOS_ROOT/backup/daily-backups"
mkdir -p "$UDOS_ROOT/backup/manual-backups"
mkdir -p "$UDOS_ROOT/backup/role-backups"
mkdir -p "$SANDBOX_SESSION/logs"
mkdir -p "$SANDBOX_SESSION/moves"
mkdir -p "$SANDBOX_SESSION/undo-stack"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# ═══════════════════════════════════════════════════════════════════════
# USER ROLE AND ENCRYPTION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Get user role from user.md
get_user_role() {
    if [ -f "$USER_MD_FILE" ]; then
        grep "^\*\*Role\*\*:" "$USER_MD_FILE" 2>/dev/null | sed 's/^\*\*Role\*\*: *//' | head -1
    else
        echo "ghost"
    fi
}

# Get backup directory based on role - using centralized /backup
get_backup_dir() {
    local role="${1:-$(get_user_role)}"
    local backup_root="$UDOS_ROOT/backup"
    case "$role" in
        tomb|sorcerer|wizard|imp|drone|ghost) echo "$backup_root/role-backups/$role" ;;
        *) echo "$backup_root/role-backups/ghost" ;;
    esac
}

# Check if encryption is available
has_encryption() {
    [ -f "$USER_MD_FILE" ] && grep -q "^\*\*Password\*\*: SET" "$USER_MD_FILE"
}

# Get encryption key from password hash
get_encryption_key() {
    if has_encryption; then
        grep "^\*\*Password Hash\*\*:" "$USER_MD_FILE" | sed 's/^\*\*Password Hash\*\*: *//' | cut -c1-32
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# SESSION MOVE LOGGING
# ═══════════════════════════════════════════════════════════════════════

# Initialize session moves log
init_session_log() {
    local session_id="$(date +%Y%m%d_%H%M%S)_$$"
    cat > "$SESSION_MOVES_LOG" << EOF
{
    "session_id": "$session_id",
    "started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "moves": [],
    "undo_stack": [],
    "redo_stack": [],
    "current_position": 0
}
EOF
    log_info "Session move logging initialized: $session_id"
}

# Log a move to session
log_move() {
    local move_type="$1"
    local description="$2"
    local data="${3:-{}}"

    # Ensure session log exists
    [ ! -f "$SESSION_MOVES_LOG" ] && init_session_log

    # Create move entry
    local timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    local move_id="$(date +%s%N | cut -c1-13)"

    # Create backup before the move for undo capability
    local backup_file="$UMEMORY_DIR/backups/session/move_${move_id}_pre.tar.gz"
    create_session_backup "$backup_file"

    # Update session log
    local temp_file=$(mktemp)
    jq --arg type "$move_type" \
       --arg desc "$description" \
       --arg ts "$timestamp" \
       --arg id "$move_id" \
       --arg backup "$backup_file" \
       --argjson data "$data" \
       '.moves += [{
           "id": $id,
           "type": $type,
           "description": $desc,
           "timestamp": $ts,
           "backup_file": $backup,
           "data": $data
       }] | .current_position = (.moves | length)' \
       "$SESSION_MOVES_LOG" > "$temp_file" && mv "$temp_file" "$SESSION_MOVES_LOG"

    # Also log to daily moves
    log_daily_move "$move_type" "$description" "$data"

    log_info "Move logged: $move_type - $description"
}

# Log to daily moves
log_daily_move() {
    local move_type="$1"
    local description="$2"
    local data="${3:-{}}"

    # Initialize daily log if needed
    if [ ! -f "$DAILY_MOVES_LOG" ]; then
        cat > "$DAILY_MOVES_LOG" << EOF
{
    "date": "$(date +%Y-%m-%d)",
    "moves": [],
    "milestones": [],
    "missions_completed": []
}
EOF
    fi

    # Add move to daily log
    local timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    local temp_file=$(mktemp)
    jq --arg type "$move_type" \
       --arg desc "$description" \
       --arg ts "$timestamp" \
       --argjson data "$data" \
       '.moves += [{
           "type": $type,
           "description": $desc,
           "timestamp": $ts,
           "data": $data
       }]' \
       "$DAILY_MOVES_LOG" > "$temp_file" && mv "$temp_file" "$DAILY_MOVES_LOG"
}

# ═══════════════════════════════════════════════════════════════════════
# UNDO/REDO SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Get available undo operations
get_undo_count() {
    if [ -f "$SESSION_MOVES_LOG" ]; then
        jq -r '.current_position // 0' "$SESSION_MOVES_LOG"
    else
        echo "0"
    fi
}

# Get available redo operations
get_redo_count() {
    if [ -f "$SESSION_MOVES_LOG" ]; then
        jq -r '(.moves | length) - (.current_position // 0)' "$SESSION_MOVES_LOG"
    else
        echo "0"
    fi
}

# Undo last move
undo_move() {
    local undo_count=$(get_undo_count)

    if [ "$undo_count" -eq 0 ]; then
        log_warning "No moves to undo in current session"
        return 1
    fi

    log_info "Undoing last move..."

    # Get the move to undo
    local move_info=$(jq -r --argjson pos "$((undo_count - 1))" '.moves[$pos]' "$SESSION_MOVES_LOG")
    local move_id=$(echo "$move_info" | jq -r '.id')
    local backup_file=$(echo "$move_info" | jq -r '.backup_file')
    local description=$(echo "$move_info" | jq -r '.description')

    # Create backup of current state for redo
    local redo_backup="$UMEMORY_DIR/backups/session/redo_${move_id}_post.tar.gz"
    create_session_backup "$redo_backup"

    # Restore from pre-move backup
    if restore_from_backup "$backup_file"; then
        # Update session log
        local temp_file=$(mktemp)
        jq --arg redo_backup "$redo_backup" \
           '.current_position -= 1 |
            .moves[.current_position].redo_backup = $redo_backup' \
           "$SESSION_MOVES_LOG" > "$temp_file" && mv "$temp_file" "$SESSION_MOVES_LOG"

        log_success "Successfully undone: $description"
        log_info "Undo count: $((undo_count - 1)), Redo count: $(($(get_redo_count) + 1))"
        return 0
    else
        log_error "Failed to undo move: $description"
        return 1
    fi
}

# Redo next move
redo_move() {
    local redo_count=$(get_redo_count)

    if [ "$redo_count" -eq 0 ]; then
        log_warning "No moves to redo in current session"
        return 1
    fi

    log_info "Redoing next move..."

    # Get the move to redo
    local current_pos=$(jq -r '.current_position // 0' "$SESSION_MOVES_LOG")
    local move_info=$(jq -r --argjson pos "$current_pos" '.moves[$pos]' "$SESSION_MOVES_LOG")
    local move_id=$(echo "$move_info" | jq -r '.id')
    local redo_backup=$(echo "$move_info" | jq -r '.redo_backup // empty')
    local description=$(echo "$move_info" | jq -r '.description')

    if [ -z "$redo_backup" ] || [ "$redo_backup" = "null" ]; then
        log_error "No redo backup available for this move"
        return 1
    fi

    # Restore from redo backup
    if restore_from_backup "$redo_backup"; then
        # Update session log
        local temp_file=$(mktemp)
        jq '.current_position += 1' "$SESSION_MOVES_LOG" > "$temp_file" && mv "$temp_file" "$SESSION_MOVES_LOG"

        log_success "Successfully redone: $description"
        log_info "Undo count: $(($(get_undo_count))), Redo count: $((redo_count - 1))"
        return 0
    else
        log_error "Failed to redo move: $description"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# BACKUP FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Create session backup (lightweight, no compression)
create_session_backup() {
    local backup_file="$1"
    local backup_dir=$(dirname "$backup_file")

    mkdir -p "$backup_dir"

    # Create lightweight backup for undo/redo
    tar -czf "$backup_file" \
        -C "$UDOS_ROOT" \
        --exclude="uMEMORY/backups" \
        --exclude="uMEMORY/system/session-moves.json" \
        --exclude="*.log" \
        --exclude=".DS_Store" \
        uMEMORY sandbox wizard 2>/dev/null || true
}

# Create full backup with metadata
create_backup() {
    local backup_type="${1:-manual}"  # manual, daily, session, startup, exit
    local description="${2:-Backup created via backup-restore system}"

    log_info "Creating $backup_type backup..."

    # Get user role and backup directory
    local role=$(get_user_role)
    local backup_dir=$(get_backup_dir "$role")
    mkdir -p "$backup_dir"

    # Generate backup filename with hex timestamp
    local timestamp=$(printf "%08X-%06X" $(date +%s) $$)
    local backup_file="$backup_dir/$timestamp-backup.tar.gz"

    # Create backup - only include existing directories
    local backup_size=0
    local backup_targets=""

    # Build list of existing backup targets
    for target in uMEMORY sandbox wizard uCORE dev; do
        if [ -d "$UDOS_ROOT/$target" ]; then
            backup_targets="$backup_targets $target"
        fi
    done

    if [ -z "$backup_targets" ]; then
        log_error "No backup targets found"
        return 1
    fi

    if tar -czf "$backup_file" \
        -C "$UDOS_ROOT" \
        --exclude="*.log" \
        --exclude=".DS_Store" \
        --exclude="uMEMORY/backups" \
        --exclude="backup/*" \
        --exclude="cache/*" \
        --exclude="trash/*" \
        $backup_targets 2>/dev/null; then

        backup_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null || echo "0")
    else
        log_error "Failed to create backup"
        return 1
    fi

    # Encrypt if password is set
    local final_file="$backup_file"
    if has_encryption; then
        local key=$(get_encryption_key)
        if [ -n "$key" ]; then
            openssl enc -aes-256-cbc -salt -pbkdf2 -iter 10000 -pass pass:"$key" \
                -in "$backup_file" -out "$backup_file.enc" && {
                rm "$backup_file"
                final_file="$backup_file.enc"
                log_info "Backup encrypted successfully"
            }
        fi
    fi

    # Update metadata
    update_backup_metadata "$final_file" "$backup_type" "$description" "$role" "$backup_size"

    # Cleanup old backups (keep 2 max: 1 most recent + 1 largest)
    cleanup_old_backups "$backup_dir"

    # Log the backup as a move - use basename to avoid path issues
    local backup_data=$(printf '{"type":"%s","file":"%s","size":%s}' "$backup_type" "$(basename "$final_file")" "$backup_size")
    log_move "backup" "$description" "$backup_data"

    # Display summary
    local display_size=$(numfmt --to=iec-i --suffix=B $backup_size 2>/dev/null || echo "${backup_size}B")
    local encrypted_status="NO"
    [[ "$final_file" == *.enc ]] && encrypted_status="YES"

    echo -e "${BOLD}${BLUE}📊 Backup Summary:${NC}"
    echo -e "  • File: $(basename "$final_file")"
    echo -e "  • Size: $display_size"
    echo -e "  • Location: $backup_dir"
    echo -e "  • Encrypted: $encrypted_status"
    echo -e "  • Type: $backup_type"

    log_success "Backup completed: $(basename "$final_file")"
    echo "$final_file"
}

# Update backup metadata
update_backup_metadata() {
    local backup_file="$1"
    local backup_type="$2"
    local description="$3"
    local role="$4"
    local size="$5"

    local metadata_entry=$(cat << EOF
{
    "file": "$backup_file",
    "type": "$backup_type",
    "description": "$description",
    "role": "$role",
    "size": $size,
    "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "encrypted": $(has_encryption && echo "true" || echo "false")
}
EOF
)

    # Initialize metadata file if needed
    [ ! -f "$BACKUP_METADATA" ] && echo '{"backups":[]}' > "$BACKUP_METADATA"

    # Add entry
    local temp_file=$(mktemp)
    jq --argjson entry "$metadata_entry" '.backups += [$entry]' "$BACKUP_METADATA" > "$temp_file" && \
        mv "$temp_file" "$BACKUP_METADATA"
}

# Cleanup old backups (keep 2: 1 most recent + 1 largest)
cleanup_old_backups() {
    local backup_dir="$1"

    # Count backups
    local backup_count=$(find "$backup_dir" -name "*-backup.tar.gz*" -type f | wc -l)

    if [ "$backup_count" -le 2 ]; then
        return 0
    fi

    log_info "Cleaning up old backups (keeping 1 most recent + 1 largest)..."

    # Get most recent backup
    local recent_backup=$(find "$backup_dir" -name "*-backup.tar.gz*" -type f -exec stat -f "%m %N" {} \; 2>/dev/null | \
        sort -nr | head -1 | cut -d' ' -f2-)

    # Get largest backup
    local largest_backup=$(find "$backup_dir" -name "*-backup.tar.gz*" -type f -exec stat -f "%z %N" {} \; 2>/dev/null | \
        sort -nr | head -1 | cut -d' ' -f2-)

    # If they're the same file, keep 2 most recent
    if [ "$recent_backup" = "$largest_backup" ]; then
        local files_to_keep=$(find "$backup_dir" -name "*-backup.tar.gz*" -type f -exec stat -f "%m %N" {} \; 2>/dev/null | \
            sort -nr | head -2 | cut -d' ' -f2-)
    else
        # Keep both recent and largest
        local files_to_keep=$(echo -e "$recent_backup\n$largest_backup" | sort -u)
    fi

    # Remove files not in keep list, move to archive
    find "$backup_dir" -name "*-backup.tar.gz*" -type f | while read -r file; do
        if ! echo "$files_to_keep" | grep -Fxq "$file"; then
            # Move to archive directory instead of deleting
            local archive_dir="$UDOS_ROOT/backup/archived-backups"
            mkdir -p "$archive_dir"
            local archived_name="$(date +%Y%m%d-%H%M%S)-$(basename "$file")"
            if mv "$file" "$archive_dir/$archived_name" 2>/dev/null; then
                log_info "Archived old backup: $(basename "$file")"
            else
                # Fallback to deletion if move fails
                rm -f "$file"
                log_info "Removed old backup: $(basename "$file")"
            fi
        fi
    done
}

# ═══════════════════════════════════════════════════════════════════════
# RESTORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# List available backups
list_backups() {
    local role=$(get_user_role)
    local backup_dir=$(get_backup_dir "$role")

    if [ ! -d "$backup_dir" ]; then
        log_warning "No backup directory found for role: $role"
        return 1
    fi

    echo -e "${BOLD}${CYAN}Available Backups for role '$role':${NC}"
    echo ""

    # List backups with details
    local count=1
    find "$backup_dir" -name "*-backup.tar.gz*" -type f | sort -r | while read -r backup_file; do
        local basename_file=$(basename "$backup_file")
        local size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null || echo "0")
        local display_size=$(numfmt --to=iec-i --suffix=B $size 2>/dev/null || echo "${size}B")
        local mod_time=$(stat -f%Sm -t"%Y-%m-%d %H:%M" "$backup_file" 2>/dev/null || \
                        stat -c%y "$backup_file" 2>/dev/null | cut -d. -f1)
        local encrypted="NO"
        [[ "$basename_file" == *.enc ]] && encrypted="YES"

        echo -e "  ${BOLD}[$count]${NC} $basename_file"
        echo -e "      Size: $display_size | Modified: $mod_time | Encrypted: $encrypted"
        echo ""
        count=$((count + 1))
    done

    echo -e "${YELLOW}Use 'RESTORE <number>' to restore a backup${NC}"
}

# Restore from backup
restore_from_backup() {
    local backup_file="$1"
    local extract_to="${2:-$UDOS_ROOT}"

    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi

    log_info "Restoring from backup: $(basename "$backup_file")"

    # Check if encrypted
    local temp_file="$backup_file"
    if [[ "$backup_file" == *.enc ]]; then
        if ! has_encryption; then
            log_error "Backup is encrypted but no password is set"
            return 1
        fi

        local key=$(get_encryption_key)
        temp_file=$(mktemp)

        if ! openssl enc -aes-256-cbc -d -salt -pbkdf2 -iter 10000 -pass pass:"$key" \
            -in "$backup_file" -out "$temp_file"; then
            log_error "Failed to decrypt backup (wrong password?)"
            rm -f "$temp_file"
            return 1
        fi

        log_info "Backup decrypted successfully"
    fi

    # Extract backup
    if tar -xzf "$temp_file" -C "$extract_to" 2>/dev/null; then
        # Cleanup temp file if it was created for decryption
        [ "$temp_file" != "$backup_file" ] && rm -f "$temp_file"

        log_success "Backup restored successfully"
        return 0
    else
        # Cleanup temp file if it was created for decryption
        [ "$temp_file" != "$backup_file" ] && rm -f "$temp_file"

        log_error "Failed to extract backup"
        return 1
    fi
}

# Interactive restore
interactive_restore() {
    local role=$(get_user_role)
    local backup_dir=$(get_backup_dir "$role")

    # List backups and get user choice
    list_backups

    echo ""
    read -p "Enter backup number to restore (or 'cancel'): " choice

    if [ "$choice" = "cancel" ]; then
        log_info "Restore cancelled"
        return 0
    fi

    # Validate choice is a number
    if ! [[ "$choice" =~ ^[0-9]+$ ]]; then
        log_error "Invalid choice: $choice"
        return 1
    fi

    # Get the backup file
    local backup_files=($(find "$backup_dir" -name "*-backup.tar.gz*" -type f | sort -r))
    local selected_index=$((choice - 1))

    if [ $selected_index -lt 0 ] || [ $selected_index -ge ${#backup_files[@]} ]; then
        log_error "Invalid backup number: $choice"
        return 1
    fi

    local selected_backup="${backup_files[$selected_index]}"

    # Confirm restore
    echo ""
    log_warning "This will restore your system to the state in backup: $(basename "$selected_backup")"
    read -p "Are you sure? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log_info "Restore cancelled"
        return 0
    fi

    # Create backup before restore for undo capability
    log_move "restore" "Restoring from backup: $(basename "$selected_backup")"

    # Perform restore
    if restore_from_backup "$selected_backup"; then
        log_success "System restored from backup: $(basename "$selected_backup")"
        return 0
    else
        log_error "Failed to restore from backup"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# MISSION AND MILESTONE TRACKING
# ═══════════════════════════════════════════════════════════════════════

# Add milestone
add_milestone() {
    local title="$1"
    local description="${2:-}"

    local timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    local milestone_id="$(date +%s%N | cut -c1-13)"

    # Add to daily log
    local temp_file=$(mktemp)
    jq --arg id "$milestone_id" \
       --arg title "$title" \
       --arg desc "$description" \
       --arg ts "$timestamp" \
       '.milestones += [{
           "id": $id,
           "title": $title,
           "description": $desc,
           "timestamp": $ts
       }]' \
       "$DAILY_MOVES_LOG" > "$temp_file" && mv "$temp_file" "$DAILY_MOVES_LOG"

    log_success "Milestone added: $title"
}

# Complete mission
complete_mission() {
    local mission_name="$1"
    local reward="${2:-}"

    local timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    local mission_id="$(date +%s%N | cut -c1-13)"

    # Add to daily log
    local temp_file=$(mktemp)
    jq --arg id "$mission_id" \
       --arg name "$mission_name" \
       --arg reward "$reward" \
       --arg ts "$timestamp" \
       '.missions_completed += [{
           "id": $id,
           "name": $name,
           "reward": $reward,
           "completed_at": $ts
       }]' \
       "$DAILY_MOVES_LOG" > "$temp_file" && mv "$temp_file" "$DAILY_MOVES_LOG"

    log_success "Mission completed: $mission_name"
}

# ═══════════════════════════════════════════════════════════════════════
# COMMAND INTERFACE
# ═══════════════════════════════════════════════════════════════════════

# Show help
show_help() {
    echo -e "${BOLD}${BLUE}uDOS Backup/Restore System v1.3${NC}"
    echo ""
    echo -e "${BOLD}BACKUP COMMANDS:${NC}"
    echo -e "  ${CYAN}backup${NC}                  Create manual backup"
    echo -e "  ${CYAN}backup daily${NC}            Create daily backup"
    echo -e "  ${CYAN}backup startup${NC}          Create startup backup"
    echo -e "  ${CYAN}backup exit${NC}             Create exit backup"
    echo ""
    echo -e "${BOLD}RESTORE COMMANDS:${NC}"
    echo -e "  ${CYAN}restore${NC}                 Interactive restore"
    echo -e "  ${CYAN}restore <file>${NC}          Restore specific backup file"
    echo -e "  ${CYAN}list${NC}                    List available backups"
    echo ""
    echo -e "${BOLD}UNDO/REDO COMMANDS:${NC}"
    echo -e "  ${CYAN}undo${NC}                    Undo last move in session"
    echo -e "  ${CYAN}redo${NC}                    Redo next move in session"
    echo -e "  ${CYAN}history${NC}                 Show session move history"
    echo ""
    echo -e "${BOLD}TRACKING COMMANDS:${NC}"
    echo -e "  ${CYAN}milestone <title>${NC}       Add milestone"
    echo -e "  ${CYAN}mission <name>${NC}          Complete mission"
    echo -e "  ${CYAN}log-move <type> <desc>${NC}  Log custom move"
    echo ""
    echo -e "${BOLD}INFO COMMANDS:${NC}"
    echo -e "  ${CYAN}status${NC}                  Show backup status"
    echo -e "  ${CYAN}help${NC}                    Show this help"
}

# Show status
show_status() {
    local role=$(get_user_role)
    local backup_dir=$(get_backup_dir "$role")
    local undo_count=$(get_undo_count)
    local redo_count=$(get_redo_count)

    echo -e "${BOLD}${BLUE}📊 Backup/Restore Status${NC}"
    echo ""
    echo -e "${BOLD}User Role:${NC} $role"
    echo -e "${BOLD}Backup Directory:${NC} $backup_dir"
    echo -e "${BOLD}Encryption:${NC} $(has_encryption && echo "Enabled" || echo "Disabled")"
    echo ""
    echo -e "${BOLD}Session Status:${NC}"
    echo -e "  • Undo available: $undo_count moves"
    echo -e "  • Redo available: $redo_count moves"
    echo ""

    if [ -d "$backup_dir" ]; then
        local backup_count=$(find "$backup_dir" -name "*-backup.tar.gz*" -type f | wc -l)
        echo -e "${BOLD}Available Backups:${NC} $backup_count"

        if [ $backup_count -gt 0 ]; then
            local latest_backup=$(find "$backup_dir" -name "*-backup.tar.gz*" -type f -exec stat -f "%m %N" {} \; 2>/dev/null | \
                sort -nr | head -1 | cut -d' ' -f2-)
            echo -e "${BOLD}Latest Backup:${NC} $(basename "$latest_backup")"
        fi
    else
        echo -e "${BOLD}Available Backups:${NC} 0"
    fi
}

# Show session history
show_history() {
    if [ ! -f "$SESSION_MOVES_LOG" ]; then
        log_warning "No session history available"
        return 1
    fi

    echo -e "${BOLD}${BLUE}📚 Session Move History${NC}"
    echo ""

    local session_id=$(jq -r '.session_id' "$SESSION_MOVES_LOG")
    local current_pos=$(jq -r '.current_position // 0' "$SESSION_MOVES_LOG")

    echo -e "${BOLD}Session ID:${NC} $session_id"
    echo -e "${BOLD}Current Position:${NC} $current_pos"
    echo ""

    # Show moves with current position indicator
    jq -r '.moves[] | "\(.timestamp) | \(.type) | \(.description)"' "$SESSION_MOVES_LOG" | \
    nl -v0 | while read -r line_num line_content; do
        if [ $line_num -lt $current_pos ]; then
            echo -e "  ${GREEN}✓${NC} [$line_num] $line_content"
        elif [ $line_num -eq $current_pos ]; then
            echo -e "  ${YELLOW}→${NC} [$line_num] $line_content ${BOLD}(current)${NC}"
        else
            echo -e "  ${RED}○${NC} [$line_num] $line_content"
        fi
    done
}

# Main command processor
main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        backup)
            local backup_type="${1:-manual}"
            local description="${2:-Manual backup via backup-restore system}"
            create_backup "$backup_type" "$description"
            ;;
        restore)
            if [ $# -eq 0 ]; then
                interactive_restore
            else
                local backup_file="$1"
                restore_from_backup "$backup_file"
            fi
            ;;
        list)
            list_backups
            ;;
        undo)
            undo_move
            ;;
        redo)
            redo_move
            ;;
        history)
            show_history
            ;;
        milestone)
            local title="$1"
            local description="${2:-}"
            if [ -z "$title" ]; then
                log_error "Milestone title required"
                exit 1
            fi
            add_milestone "$title" "$description"
            ;;
        mission)
            local mission_name="$1"
            local reward="${2:-}"
            if [ -z "$mission_name" ]; then
                log_error "Mission name required"
                exit 1
            fi
            complete_mission "$mission_name" "$reward"
            ;;
        log-move)
            local move_type="$1"
            local description="$2"
            local data="${3:-{}}"
            if [ -z "$move_type" ] || [ -z "$description" ]; then
                log_error "Move type and description required"
                exit 1
            fi
            log_move "$move_type" "$description" "$data"
            ;;
        status)
            show_status
            ;;
        init-session)
            init_session_log
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Initialize session on first run if needed
[ ! -f "$SESSION_MOVES_LOG" ] && init_session_log

# Run main function
main "$@"
