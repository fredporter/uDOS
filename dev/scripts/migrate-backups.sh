#!/bin/bash

# uDOS Backup Migration Tool v1.4.0
# Migrate distributed backups to centralized root backup folder

set -euo pipefail

readonly SCRIPT_NAME="backup-migration"
readonly VERSION="1.4.0"
readonly UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# Source configuration
source "$(dirname "${BASH_SOURCE[0]}")/backup-config.sh" 2>/dev/null || {
    echo "Warning: Could not load backup configuration"
    BACKUP_ROOT_DIR="$UDOS_ROOT/backup"
}

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'
readonly BOLD='\033[1m'

# Ensure backup directory exists
mkdir -p "$BACKUP_ROOT_DIR"

log() {
    local level="$1"
    shift
    echo -e "${BOLD}[$(date +'%H:%M:%S')] ${level}:${NC} $*" >&2
}

log_info() { log "${BLUE}INFO${NC}" "$@"; }
log_warn() { log "${YELLOW}WARN${NC}" "$@"; }
log_error() { log "${RED}ERROR${NC}" "$@"; }
log_success() { log "${GREEN}SUCCESS${NC}" "$@"; }

# Find all existing backup files
find_legacy_backups() {
    local backup_files=()

    log_info "Scanning for legacy backup files..."

    # Define legacy backup locations
    local legacy_dirs=(
        "wizard/backup"
        "sorcerer/backup"
        "imp/backup"
        "ghost/backup"
        "drone/backup"
        "tomb/backup"
        "uMEMORY/backups"
    )

    # Scan each legacy directory
    for legacy_dir in "${legacy_dirs[@]}"; do
        local full_path="$UDOS_ROOT/$legacy_dir"
        if [[ -d "$full_path" ]]; then
            log_info "Scanning: $legacy_dir"

            # Find backup files (tar.gz, .enc files)
            while IFS= read -r -d '' backup_file; do
                if [[ -f "$backup_file" && "$backup_file" =~ \.(tar\.gz|tar\.gz\.enc)$ ]]; then
                    backup_files+=("$backup_file")
                    log_info "Found: $(basename "$backup_file")"
                fi
            done < <(find "$full_path" -type f \( -name "*.tar.gz" -o -name "*.tar.gz.enc" \) -print0 2>/dev/null || true)
        fi
    done

    # Also check for any other backup patterns in the root
    while IFS= read -r -d '' backup_file; do
        if [[ -f "$backup_file" && "$backup_file" =~ backup.*\.(tar\.gz|tar\.gz\.enc)$ ]]; then
            # Skip if already in backup directory
            if [[ "$backup_file" != "$BACKUP_ROOT_DIR"/* ]]; then
                backup_files+=("$backup_file")
                log_info "Found root backup: $(basename "$backup_file")"
            fi
        fi
    done < <(find "$UDOS_ROOT" -maxdepth 1 -type f \( -name "*backup*.tar.gz" -o -name "*backup*.tar.gz.enc" \) -print0 2>/dev/null || true)

    printf '%s\0' "${backup_files[@]}"
}

# Generate migration plan
generate_migration_plan() {
    local backup_files=()
    local total_size=0
    local migration_plan=()

    # Read backup files from stdin
    while IFS= read -r -d '' backup_file; do
        backup_files+=("$backup_file")
    done

    if [[ ${#backup_files[@]} -eq 0 ]]; then
        log_warn "No legacy backup files found to migrate"
        return 1
    fi

    log_info "Generating migration plan for ${#backup_files[@]} backup files..."

    # Analyze each backup file
    for backup_file in "${backup_files[@]}"; do
        local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null || echo "0")
        local filename=$(basename "$backup_file")
        local source_dir=$(dirname "$backup_file")
        local relative_source="${source_dir#$UDOS_ROOT/}"

        # Generate new standardized filename if needed
        local new_filename="$filename"
        if [[ ! "$filename" =~ ^[0-9]{8}-[0-9]{6}- ]]; then
            local timestamp=$(date +%Y%m%d-%H%M%S)
            local backup_id=$(printf "%08X" $RANDOM)
            new_filename="${timestamp}-migrated-${backup_id}-${filename}"
        fi

        migration_plan+=("$backup_file|$new_filename|$file_size|$relative_source")
        total_size=$((total_size + file_size))
    done

    # Display migration plan
    echo ""
    echo -e "${BOLD}${CYAN}📋 Migration Plan${NC}"
    echo -e "${BOLD}═══════════════════${NC}"
    echo ""
    echo -e "  📁 Files to migrate: ${YELLOW}${#backup_files[@]}${NC}"
    echo -e "  📏 Total size: ${PURPLE}$(numfmt --to=iec-i --suffix=B $total_size 2>/dev/null || echo "${total_size}B")${NC}"
    echo -e "  📂 Destination: ${CYAN}$BACKUP_ROOT_DIR${NC}"
    echo ""

    local count=1
    for plan_item in "${migration_plan[@]}"; do
        IFS='|' read -r source_file new_name file_size source_dir <<< "$plan_item"
        local display_size=$(numfmt --to=iec-i --suffix=B $file_size 2>/dev/null || echo "${file_size}B")

        echo -e "  ${BOLD}[$count]${NC} $(basename "$source_file")"
        echo -e "      📁 From: $source_dir"
        echo -e "      📏 Size: $display_size"
        if [[ "$(basename "$source_file")" != "$new_name" ]]; then
            echo -e "      🏷️  New name: $new_name"
        fi
        echo ""
        ((count++))
    done

    # Save migration plan
    printf '%s\n' "${migration_plan[@]}"
}

# Execute migration
execute_migration() {
    local migration_plan=()
    local migrated_count=0
    local total_migrated_size=0

    # Read migration plan from stdin
    while IFS= read -r plan_item; do
        migration_plan+=("$plan_item")
    done

    if [[ ${#migration_plan[@]} -eq 0 ]]; then
        log_warn "No migration plan provided"
        return 1
    fi

    log_info "Executing migration for ${#migration_plan[@]} files..."

    # Create migration metadata
    local migration_metadata="$BACKUP_ROOT_DIR/migration-$(date +%Y%m%d-%H%M%S).json"
    echo '{"migration_date":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","files":[]}' > "$migration_metadata"

    # Process each file
    for plan_item in "${migration_plan[@]}"; do
        IFS='|' read -r source_file new_name file_size source_dir <<< "$plan_item"

        local dest_file="$BACKUP_ROOT_DIR/$new_name"

        log_info "Migrating: $(basename "$source_file")"

        # Copy file to backup directory
        if cp "$source_file" "$dest_file"; then
            # Verify copy
            local dest_size=$(stat -f%z "$dest_file" 2>/dev/null || stat -c%s "$dest_file" 2>/dev/null || echo "0")

            if [[ "$dest_size" == "$file_size" ]]; then
                log_success "Migrated: $new_name"

                # Update metadata
                local metadata_entry=$(cat << EOF
{
    "original_file": "$source_file",
    "original_location": "$source_dir",
    "new_file": "$dest_file",
    "new_name": "$new_name",
    "size": $file_size,
    "migrated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
                )

                local temp_file=$(mktemp)
                jq --argjson entry "$metadata_entry" '.files += [$entry]' "$migration_metadata" > "$temp_file" && \
                    mv "$temp_file" "$migration_metadata"

                migrated_count=$((migrated_count + 1))
                total_migrated_size=$((total_migrated_size + file_size))

                # Move original to trash or delete
                if [[ -x "$UDOS_ROOT/uCORE/bin/trash" ]]; then
                    "$UDOS_ROOT/uCORE/bin/trash" file "$source_file" migration
                    log_info "Moved original to trash: $(basename "$source_file")"
                else
                    # Create backup of original before removing
                    local backup_original="${source_file}.migrated-$(date +%Y%m%d)"
                    mv "$source_file" "$backup_original"
                    log_info "Original backed up as: $(basename "$backup_original")"
                fi
            else
                log_error "Size mismatch after copy: $(basename "$source_file")"
                rm -f "$dest_file"
            fi
        else
            log_error "Failed to copy: $(basename "$source_file")"
        fi
    done

    # Display migration results
    echo ""
    echo -e "${BOLD}${GREEN}✅ Migration Summary${NC}"
    echo -e "${BOLD}════════════════════${NC}"
    echo -e "  📁 Files migrated: ${CYAN}$migrated_count${NC} / ${#migration_plan[@]}"
    echo -e "  📏 Total migrated: ${PURPLE}$(numfmt --to=iec-i --suffix=B $total_migrated_size 2>/dev/null || echo "${total_migrated_size}B")${NC}"
    echo -e "  📂 Destination: ${CYAN}$BACKUP_ROOT_DIR${NC}"
    echo -e "  📋 Metadata: ${YELLOW}$(basename "$migration_metadata")${NC}"
    echo ""

    if [[ $migrated_count -gt 0 ]]; then
        log_success "Migration completed successfully"
        return 0
    else
        log_error "Migration failed - no files were migrated"
        return 1
    fi
}

# Clean up empty legacy directories
cleanup_legacy_directories() {
    log_info "Cleaning up empty legacy backup directories..."

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
        if [[ -d "$full_path" ]]; then
            # Check if directory is empty (ignoring hidden files)
            if [[ -z "$(ls -A "$full_path" 2>/dev/null)" ]]; then
                log_info "Removing empty directory: $legacy_dir"
                rmdir "$full_path" 2>/dev/null || log_warn "Could not remove: $legacy_dir"
            else
                log_info "Directory not empty, preserving: $legacy_dir"
            fi
        fi
    done
}

# Main migration function
main() {
    local action="${1:-migrate}"

    case "$action" in
        "scan")
            echo -e "${BOLD}${BLUE}🔍 Scanning for Legacy Backups${NC}"
            echo -e "${BOLD}═══════════════════════════════${NC}"
            find_legacy_backups | while IFS= read -r -d '' backup_file; do
                local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null || echo "0")
                local display_size=$(numfmt --to=iec-i --suffix=B $file_size 2>/dev/null || echo "${file_size}B")
                echo -e "  📁 ${CYAN}$(basename "$backup_file")${NC} - $display_size"
                echo -e "      📍 ${PURPLE}${backup_file#$UDOS_ROOT/}${NC}"
            done
            ;;
        "plan")
            find_legacy_backups | generate_migration_plan
            ;;
        "migrate")
            echo -e "${BOLD}${GREEN}🚀 Starting Backup Migration${NC}"
            echo -e "${BOLD}═══════════════════════════════${NC}"

            # Generate and execute migration plan
            local migration_plan_output=$(find_legacy_backups | generate_migration_plan)

            if [[ -n "$migration_plan_output" ]]; then
                echo ""
                read -p "Proceed with migration? (yes/no): " confirm

                if [[ "$confirm" == "yes" ]]; then
                    echo "$migration_plan_output" | execute_migration
                    cleanup_legacy_directories
                else
                    log_info "Migration cancelled by user"
                fi
            fi
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
${BOLD}uDOS Backup Migration Tool v$VERSION${NC}

${BOLD}USAGE:${NC}
    $0 <action>

${BOLD}ACTIONS:${NC}
    scan     Scan for legacy backup files
    plan     Generate migration plan
    migrate  Execute full migration (default)
    help     Show this help

${BOLD}DESCRIPTION:${NC}
    Migrates distributed backup files from legacy locations to the
    centralized root backup folder for better compatibility and
    management.

${BOLD}LEGACY LOCATIONS:${NC}
    • wizard/backup
    • sorcerer/backup
    • imp/backup
    • ghost/backup
    • drone/backup
    • tomb/backup
    • uMEMORY/backups

${BOLD}FEATURES:${NC}
    ✅ Safe migration with verification
    ✅ Preserves original files until confirmed
    ✅ Standardized filename format
    ✅ Migration metadata tracking
    ✅ Empty directory cleanup

EOF
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
