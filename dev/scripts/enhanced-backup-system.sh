#!/bin/bash

# uDOS Enhanced Root Backup System v1.4.0
# Stores all backups in root backup folder with password encoding
# Better compatibility and clean file location management

set -euo pipefail

# Configuration
readonly SCRIPT_NAME="enhanced-backup-system"
readonly VERSION="1.4.0"
readonly UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
readonly ROOT_BACKUP_DIR="$UDOS_ROOT/backup"
readonly USER_MD_FILE="$UDOS_ROOT/sandbox/user.md"
readonly BACKUP_METADATA="$ROOT_BACKUP_DIR/backup-metadata.json"
readonly BACKUP_INDEX="$ROOT_BACKUP_DIR/backup-index.json"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'
readonly BOLD='\033[1m'

# Ensure backup directory exists
mkdir -p "$ROOT_BACKUP_DIR"

# ═══════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

log() {
    local level="$1"
    shift
    echo -e "${BOLD}[$(date +'%H:%M:%S')] ${level}:${NC} $*" >&2
}

log_info() { log "${BLUE}INFO${NC}" "$@"; }
log_warn() { log "${YELLOW}WARN${NC}" "$@"; }
log_error() { log "${RED}ERROR${NC}" "$@"; }
log_success() { log "${GREEN}SUCCESS${NC}" "$@"; }

# Get user role safely
get_user_role() {
    local role="wizard"  # default
    if [[ -f "$USER_MD_FILE" ]]; then
        local file_role=$(grep "^\\\$ROLE=" "$USER_MD_FILE" 2>/dev/null | cut -d'=' -f2 || echo "")
        [[ -n "$file_role" ]] && role="$file_role"
    fi
    echo "$role"
}

# Get user password status
has_password() {
    [[ -f "$USER_MD_FILE" ]] && grep -q "^\*\*Password\*\*: SET" "$USER_MD_FILE"
}

# Get encryption key from password hash
get_encryption_key() {
    if has_password; then
        grep "^\*\*Password Hash\*\*:" "$USER_MD_FILE" 2>/dev/null | \
            sed 's/^\*\*Password Hash\*\*: *//' | cut -c1-32
    fi
}

# Generate unique backup ID
generate_backup_id() {
    printf "%08X-%06X" $(date +%s) $$
}

# ═══════════════════════════════════════════════════════════════════════
# BACKUP CREATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Create backup with optional encryption
create_backup() {
    local backup_type="${1:-manual}"
    local description="${2:-System backup created}"
    local include_paths="${3:-uMEMORY sandbox}"

    log_info "Creating $backup_type backup..."

    # Generate backup filename
    local backup_id=$(generate_backup_id)
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local role=$(get_user_role)
    local backup_name="${timestamp}-${role}-${backup_type}-${backup_id}"
    local backup_file="$ROOT_BACKUP_DIR/${backup_name}.tar.gz"

    # Create backup archive
    local backup_size=0
    log_info "Creating archive: $(basename "$backup_file")"

    if tar -czf "$backup_file" \
        -C "$UDOS_ROOT" \
        --exclude="backup/*" \
        --exclude="*.log" \
        --exclude=".DS_Store" \
        --exclude="cache/*" \
        --exclude="tmp/*" \
        --exclude="uMEMORY/backups" \
        --exclude="uMEMORY/viewports" \
        --exclude=".git" \
        $include_paths 2>/dev/null; then

        backup_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null || echo "0")
        log_success "Archive created: $(numfmt --to=iec-i --suffix=B $backup_size 2>/dev/null || echo "${backup_size}B")"
    else
        log_error "Failed to create backup archive"
        return 1
    fi

    # Encrypt if password is set
    local final_file="$backup_file"
    if has_password; then
        local encryption_key=$(get_encryption_key)
        if [[ -n "$encryption_key" ]]; then
            log_info "Encrypting backup with user password..."
            local encrypted_file="${backup_file}.enc"

            if openssl enc -aes-256-cbc -salt -pbkdf2 -iter 100000 \
                -pass pass:"$encryption_key" \
                -in "$backup_file" -out "$encrypted_file"; then

                rm "$backup_file"
                final_file="$encrypted_file"
                log_success "Backup encrypted successfully"
            else
                log_warn "Encryption failed, keeping unencrypted backup"
            fi
        fi
    else
        log_info "No password set - backup stored unencrypted"
    fi

    # Update metadata
    update_backup_metadata "$final_file" "$backup_type" "$description" "$role" "$backup_size" "$backup_id"

    # Cleanup old backups
    cleanup_old_backups

    # Display summary
    display_backup_summary "$final_file" "$backup_type" "$backup_size"

    echo "$final_file"
}

# Update backup metadata
update_backup_metadata() {
    local backup_file="$1"
    local backup_type="$2"
    local description="$3"
    local role="$4"
    local size="$5"
    local backup_id="$6"

    # Initialize metadata if needed
    if [[ ! -f "$BACKUP_METADATA" ]]; then
        echo '{"backups":[]}' > "$BACKUP_METADATA"
    fi

    # Create metadata entry
    local metadata_entry=$(cat << EOF
{
    "id": "$backup_id",
    "file": "$(basename "$backup_file")",
    "full_path": "$backup_file",
    "type": "$backup_type",
    "description": "$description",
    "role": "$role",
    "size": $size,
    "encrypted": $(has_password && echo "true" || echo "false"),
    "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "created_local": "$(date +'%Y-%m-%d %H:%M:%S')",
    "hostname": "$(hostname)",
    "uDOS_version": "1.3.3"
}
EOF
)

    # Add entry to metadata
    local temp_file=$(mktemp)
    if jq --argjson entry "$metadata_entry" '.backups += [$entry]' "$BACKUP_METADATA" > "$temp_file"; then
        mv "$temp_file" "$BACKUP_METADATA"

        # Also update index file for quick access
        update_backup_index "$backup_id" "$backup_file" "$backup_type" "$role"
    else
        log_warn "Failed to update backup metadata"
        rm -f "$temp_file"
    fi
}

# Update backup index for quick access
update_backup_index() {
    local backup_id="$1"
    local backup_file="$2"
    local backup_type="$3"
    local role="$4"

    # Initialize index if needed
    if [[ ! -f "$BACKUP_INDEX" ]]; then
        echo '{"latest":{},"by_type":{},"by_role":{}}' > "$BACKUP_INDEX"
    fi

    local temp_file=$(mktemp)
    jq --arg id "$backup_id" \
       --arg file "$(basename "$backup_file")" \
       --arg type "$backup_type" \
       --arg role "$role" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.latest = {id: $id, file: $file, timestamp: $timestamp} |
        .by_type[$type] = {id: $id, file: $file, timestamp: $timestamp} |
        .by_role[$role] = {id: $id, file: $file, timestamp: $timestamp}' \
       "$BACKUP_INDEX" > "$temp_file" && mv "$temp_file" "$BACKUP_INDEX"
}

# Display backup summary
display_backup_summary() {
    local backup_file="$1"
    local backup_type="$2"
    local backup_size="$3"

    local display_size=$(numfmt --to=iec-i --suffix=B $backup_size 2>/dev/null || echo "${backup_size}B")
    local encrypted_status=$(has_password && echo "YES" || echo "NO")
    local filename=$(basename "$backup_file")

    echo ""
    echo -e "${BOLD}${BLUE}📊 Backup Summary${NC}"
    echo -e "${BOLD}══════════════════${NC}"
    echo -e "  📁 File: ${CYAN}$filename${NC}"
    echo -e "  📏 Size: ${YELLOW}$display_size${NC}"
    echo -e "  📂 Location: ${PURPLE}$ROOT_BACKUP_DIR${NC}"
    echo -e "  🔐 Encrypted: ${encrypted_status}"
    echo -e "  🏷️  Type: ${backup_type}"
    echo -e "  👤 Role: $(get_user_role)"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════
# BACKUP MANAGEMENT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# List all backups
list_backups() {
    local filter_type="${1:-}"
    local filter_role="${2:-}"

    if [[ ! -f "$BACKUP_METADATA" ]]; then
        log_warn "No backup metadata found"
        return 1
    fi

    echo -e "${BOLD}${CYAN}📋 Available Backups${NC}"
    echo -e "${BOLD}════════════════════${NC}"
    echo ""

    local count=1
    local jq_filter='.backups'

    # Apply filters
    if [[ -n "$filter_type" ]]; then
        jq_filter="$jq_filter | map(select(.type == \"$filter_type\"))"
    fi
    if [[ -n "$filter_role" ]]; then
        jq_filter="$jq_filter | map(select(.role == \"$filter_role\"))"
    fi

    # Sort by creation date (newest first)
    jq_filter="$jq_filter | sort_by(.created) | reverse"

    jq -r "$jq_filter | .[] | \"\\(.id)|\\(.file)|\\(.size)|\\(.type)|\\(.role)|\\(.created_local)|\\(.encrypted)\"" "$BACKUP_METADATA" | \
    while IFS='|' read -r id file size type role created encrypted; do
        local display_size=$(numfmt --to=iec-i --suffix=B $size 2>/dev/null || echo "${size}B")
        local encrypted_icon=$([[ "$encrypted" == "true" ]] && echo "🔐" || echo "📁")

        echo -e "  ${BOLD}[$count]${NC} $encrypted_icon ${CYAN}$file${NC}"
        echo -e "      📏 Size: $display_size | 🏷️  Type: $type | 👤 Role: $role"
        echo -e "      🕒 Created: $created"
        echo ""
        ((count++))
    done

    if [[ $count -eq 1 ]]; then
        echo -e "${YELLOW}No backups found matching criteria${NC}"
        return 1
    fi
}

# Cleanup old backups (enhanced retention policy)
cleanup_old_backups() {
    log_info "Cleaning up old backups..."

    # Keep retention policy:
    # - 3 most recent manual backups
    # - 2 most recent daily backups
    # - 1 most recent of each type (session, startup, exit)
    # - 1 largest backup overall

    for backup_type in manual daily session startup exit; do
        local keep_count=3
        [[ "$backup_type" == "daily" ]] && keep_count=2
        [[ "$backup_type" =~ ^(session|startup|exit)$ ]] && keep_count=1

        cleanup_backup_type "$backup_type" "$keep_count"
    done

    # Keep one largest backup overall
    keep_largest_backup
}

# Cleanup specific backup type
cleanup_backup_type() {
    local backup_type="$1"
    local keep_count="$2"

    if [[ ! -f "$BACKUP_METADATA" ]]; then
        return 0
    fi

    # Get backups of this type, sorted by date (newest first)
    local backups_to_remove=$(jq -r ".backups | map(select(.type == \"$backup_type\")) | sort_by(.created) | reverse | .[${keep_count}:] | .[] | .full_path" "$BACKUP_METADATA" 2>/dev/null || echo "")

    if [[ -n "$backups_to_remove" ]]; then
        echo "$backups_to_remove" | while read -r backup_file; do
            if [[ -f "$backup_file" ]]; then
                # Move to trash instead of deleting
                if [[ -x "$UDOS_ROOT/uCORE/bin/trash" ]]; then
                    "$UDOS_ROOT/uCORE/bin/trash" file "$backup_file" backups
                    log_info "Moved old $backup_type backup to trash: $(basename "$backup_file")"
                else
                    rm -f "$backup_file"
                    log_info "Removed old $backup_type backup: $(basename "$backup_file")"
                fi

                # Remove from metadata
                remove_from_metadata "$backup_file"
            fi
        done
    fi
}

# Keep largest backup overall
keep_largest_backup() {
    if [[ ! -f "$BACKUP_METADATA" ]]; then
        return 0
    fi

    # Get largest backup
    local largest_backup=$(jq -r '.backups | sort_by(.size) | reverse | .[0] | .full_path' "$BACKUP_METADATA" 2>/dev/null)

    if [[ -n "$largest_backup" && "$largest_backup" != "null" ]]; then
        log_info "Preserving largest backup: $(basename "$largest_backup")"
    fi
}

# Remove backup from metadata
remove_from_metadata() {
    local backup_file="$1"

    if [[ -f "$BACKUP_METADATA" ]]; then
        local temp_file=$(mktemp)
        jq --arg file "$backup_file" '.backups |= map(select(.full_path != $file))' "$BACKUP_METADATA" > "$temp_file" && \
            mv "$temp_file" "$BACKUP_METADATA"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# RESTORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Restore from backup
restore_backup() {
    local backup_choice="${1:-}"

    if [[ -z "$backup_choice" ]]; then
        list_backups
        echo ""
        read -p "Enter backup number to restore (or 'cancel'): " backup_choice
    fi

    if [[ "$backup_choice" == "cancel" ]]; then
        log_info "Restore cancelled"
        return 0
    fi

    # Validate choice
    if ! [[ "$backup_choice" =~ ^[0-9]+$ ]]; then
        log_error "Invalid choice: $backup_choice"
        return 1
    fi

    # Get backup file
    local backup_files=($(jq -r '.backups | sort_by(.created) | reverse | .[] | .full_path' "$BACKUP_METADATA" 2>/dev/null))
    local selected_index=$((backup_choice - 1))

    if [[ $selected_index -lt 0 || $selected_index -ge ${#backup_files[@]} ]]; then
        log_error "Invalid backup number: $backup_choice"
        return 1
    fi

    local selected_backup="${backup_files[$selected_index]}"

    # Confirm restore
    echo ""
    echo -e "${BOLD}${YELLOW}⚠️  Restore Confirmation${NC}"
    echo -e "This will restore from: ${CYAN}$(basename "$selected_backup")${NC}"
    echo -e "Current data will be backed up before restore."
    echo ""
    read -p "Proceed with restore? (yes/no): " confirm

    if [[ "$confirm" != "yes" ]]; then
        log_info "Restore cancelled"
        return 0
    fi

    # Create pre-restore backup
    log_info "Creating pre-restore backup..."
    create_backup "pre-restore" "Backup before restore operation"

    # Perform restore
    perform_restore "$selected_backup"
}

# Perform the actual restore
perform_restore() {
    local backup_file="$1"

    log_info "Restoring from: $(basename "$backup_file")"

    # Check if encrypted
    local restore_file="$backup_file"
    if [[ "$backup_file" == *.enc ]]; then
        if has_password; then
            local encryption_key=$(get_encryption_key)
            local temp_file=$(mktemp)

            log_info "Decrypting backup..."
            if openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 \
                -pass pass:"$encryption_key" \
                -in "$backup_file" -out "$temp_file"; then
                restore_file="$temp_file"
                log_success "Backup decrypted successfully"
            else
                log_error "Failed to decrypt backup"
                rm -f "$temp_file"
                return 1
            fi
        else
            log_error "Backup is encrypted but no password is set"
            return 1
        fi
    fi

    # Extract backup
    log_info "Extracting backup..."
    if tar -xzf "$restore_file" -C "$UDOS_ROOT"; then
        log_success "Backup restored successfully"
    else
        log_error "Failed to extract backup"
        [[ "$restore_file" != "$backup_file" ]] && rm -f "$restore_file"
        return 1
    fi

    # Cleanup temp file if created
    [[ "$restore_file" != "$backup_file" ]] && rm -f "$restore_file"

    echo -e "${BOLD}${GREEN}✅ Restore completed successfully${NC}"
}

# ═══════════════════════════════════════════════════════════════════════
# QUICK ACCESS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Get backup statistics
show_stats() {
    if [[ ! -f "$BACKUP_METADATA" ]]; then
        echo -e "${YELLOW}No backup metadata found${NC}"
        return 1
    fi

    echo -e "${BOLD}${BLUE}📊 Backup Statistics${NC}"
    echo -e "${BOLD}═══════════════════${NC}"
    echo ""

    local total_backups=$(jq '.backups | length' "$BACKUP_METADATA")
    local total_size=$(jq '.backups | map(.size) | add // 0' "$BACKUP_METADATA")
    local encrypted_count=$(jq '.backups | map(select(.encrypted == true)) | length' "$BACKUP_METADATA")
    local display_size=$(numfmt --to=iec-i --suffix=B $total_size 2>/dev/null || echo "${total_size}B")

    echo -e "  📁 Total Backups: ${CYAN}$total_backups${NC}"
    echo -e "  📏 Total Size: ${YELLOW}$display_size${NC}"
    echo -e "  🔐 Encrypted: ${GREEN}$encrypted_count${NC}"
    echo -e "  📂 Location: ${PURPLE}$ROOT_BACKUP_DIR${NC}"
    echo ""

    # Show by type
    echo -e "${BOLD}By Type:${NC}"
    jq -r '.backups | group_by(.type) | .[] | "\(.[0].type): \(length)"' "$BACKUP_METADATA" | \
    while read -r type_info; do
        echo -e "  🏷️  $type_info"
    done
    echo ""

    # Show latest
    local latest_backup=$(jq -r '.backups | sort_by(.created) | reverse | .[0] | .file' "$BACKUP_METADATA" 2>/dev/null)
    if [[ "$latest_backup" != "null" ]]; then
        echo -e "  🕒 Latest: ${CYAN}$latest_backup${NC}"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# MAIN INTERFACE
# ═══════════════════════════════════════════════════════════════════════

main() {
    local action="${1:-help}"

    case "$action" in
        "create"|"backup")
            local type="${2:-manual}"
            local description="${3:-System backup created}"
            create_backup "$type" "$description"
            ;;
        "list"|"ls")
            local filter_type="${2:-}"
            local filter_role="${3:-}"
            list_backups "$filter_type" "$filter_role"
            ;;
        "restore")
            local choice="${2:-}"
            restore_backup "$choice"
            ;;
        "stats"|"status")
            show_stats
            ;;
        "cleanup")
            cleanup_old_backups
            ;;
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
${BOLD}uDOS Enhanced Root Backup System v$VERSION${NC}

${BOLD}USAGE:${NC}
    $0 <action> [options]

${BOLD}ACTIONS:${NC}
    create [type] [description]  Create a new backup
    list [type] [role]          List available backups
    restore [number]            Restore from backup
    stats                       Show backup statistics
    cleanup                     Clean up old backups
    help                        Show this help

${BOLD}BACKUP TYPES:${NC}
    manual, daily, session, startup, exit, pre-restore

${BOLD}EXAMPLES:${NC}
    $0 create manual "Before system update"
    $0 list manual
    $0 restore 1
    $0 stats

${BOLD}FEATURES:${NC}
    ✅ Centralized storage in root backup folder
    ✅ Automatic encryption when password is set
    ✅ Smart cleanup with retention policies
    ✅ Comprehensive metadata tracking
    ✅ Compatible with existing uDOS workflows

${BOLD}STORAGE LOCATION:${NC}
    All backups are stored in: ${PURPLE}$ROOT_BACKUP_DIR${NC}

EOF
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
