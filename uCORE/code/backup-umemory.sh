#!/bin/bash

# uMEMORY Backup System v1.3
# Backs up uMEMORY to visible backup folders in user-mode root directories and sandbox

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get the uDOS root directory
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UMEMORY_DIR="$UDOS_ROOT/uMEMORY"

# Generate hex timestamp for backup files
generate_hex_timestamp() {
    local current_date=$(date '+%Y%m%d')
    local current_time=$(date '+%H%M')
    local date_hex=$(printf "%08X" "$current_date")
    local time_hex=$(printf "%04X" "$current_time")
    echo "${date_hex:0:8}-${time_hex}"
}

# Log functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }

# Create backup archive
create_backup_archive() {
    local backup_dir="$1"
    local backup_name="$2"
    local hex_timestamp=$(generate_hex_timestamp)
    
    # Special naming for sandbox - just "sandbox-backup" not "sandbox-umemory-backup"
    if [[ "$backup_name" == "sandbox" ]]; then
        local backup_file="${backup_dir}/${hex_timestamp}-sandbox-backup.tar.gz"
    else
        local backup_file="${backup_dir}/${hex_timestamp}-${backup_name}-umemory-backup.tar.gz"
    fi
    
    # Create backup with compression
    cd "$UDOS_ROOT"
    tar -czf "$backup_file" --exclude='.DS_Store' uMEMORY/ 2>/dev/null
    
    local file_size=$(du -h "$backup_file" | cut -f1)
    log_success "Backup created: $(basename "$backup_file") (${file_size})"
    echo "$backup_file"
}

# Main backup function
backup_umemory() {
    echo "🗄️  uMEMORY Backup System v1.3"
    echo "==============================="
    
    if [[ ! -d "$UMEMORY_DIR" ]]; then
        echo "❌ uMEMORY directory not found: $UMEMORY_DIR"
        exit 1
    fi
    
    log_info "Backing up uMEMORY to all role directories and sandbox..."
    
    # Backup to all role directories
    local roles=("ghost" "drone" "imp" "sorcerer" "tomb" "wizard")
    for role in "${roles[@]}"; do
        local role_backup_dir="$UDOS_ROOT/$role/backup"
        if [[ -d "$role_backup_dir" ]]; then
            create_backup_archive "$role_backup_dir" "$role" >/dev/null
        fi
    done
    
    # Backup to sandbox
    local sandbox_backup_dir="$UDOS_ROOT/sandbox/backup"
    if [[ -d "$sandbox_backup_dir" ]]; then
        create_backup_archive "$sandbox_backup_dir" "sandbox" >/dev/null
    fi
    
    log_success "uMEMORY backup completed to all locations!"
}

# Handle command line arguments
case "${1:-}" in
    "help"|"--help"|"-h")
        echo "uMEMORY Backup System v1.3"
        echo ""
        echo "Usage: $0"
        echo ""
        echo "Backup locations:"
        echo "  • ghost/backup/     - Ghost role backup"
        echo "  • drone/backup/     - Drone role backup"  
        echo "  • imp/backup/       - Imp role backup"
        echo "  • sorcerer/backup/  - Sorcerer role backup"
        echo "  • tomb/backup/      - Tomb role backup"
        echo "  • wizard/backup/    - Wizard role backup"
        echo "  • sandbox/backup/   - Sandbox backup (named sandbox-backup.tar.gz)"
        ;;
    *)
        backup_umemory
        ;;
esac
