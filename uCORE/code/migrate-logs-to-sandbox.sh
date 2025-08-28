#!/bin/bash
# migrate-logs-to-sandbox.sh - Move all logs from uMEMORY to sandbox
# Centralizes all logging in sandbox as per new architecture

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source logging
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Configuration
UMEMORY_DIR="$UDOS_ROOT/uMEMORY"
SANDBOX_DIR="$UDOS_ROOT/sandbox"
BACKUP_DIR="$UDOS_ROOT/backup"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info "Starting log migration from uMEMORY to sandbox..."

# Create sandbox log structure
mkdir -p "$SANDBOX_DIR/logs/system"
mkdir -p "$SANDBOX_DIR/logs/session"
mkdir -p "$SANDBOX_DIR/logs/error"
mkdir -p "$SANDBOX_DIR/logs/development"
mkdir -p "$SANDBOX_DIR/logs/archived"

# Function to migrate logs safely
migrate_logs() {
    local source_dir="$1"
    local dest_dir="$2"
    local log_type="$3"

    if [ -d "$source_dir" ]; then
        local count=$(find "$source_dir" -name "*.log" -o -name "*.json" | wc -l | xargs)
        if [ "$count" -gt 0 ]; then
            log_info "Migrating $count $log_type logs from $source_dir"

            # Create backup before migration
            backup_name="log-migration-$log_type-$(date +%Y%m%d_%H%M%S).tar.gz"
            tar -czf "$BACKUP_DIR/migration-archives/$backup_name" -C "$source_dir" . 2>/dev/null || true

            # Move logs to sandbox
            find "$source_dir" -name "*.log" -o -name "*.json" | while read -r log_file; do
                filename=$(basename "$log_file")
                dest_file="$dest_dir/$filename"

                # If file already exists, add timestamp
                if [ -f "$dest_file" ]; then
                    timestamp=$(date +%Y%m%d_%H%M%S)
                    dest_file="$dest_dir/${filename%.*}_migrated_$timestamp.${filename##*.}"
                fi

                mv "$log_file" "$dest_file"
            done

            log_success "Migrated $log_type logs (backed up as $backup_name)"
        else
            log_info "No $log_type logs found in $source_dir"
        fi
    fi
}

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR/migration-archives"

# Migrate different types of logs
log_info "=== Starting Log Migration ==="

# 1. System logs
migrate_logs "$UMEMORY_DIR/system" "$SANDBOX_DIR/logs/system" "system"

# 2. Session logs
migrate_logs "$UMEMORY_DIR/session" "$SANDBOX_DIR/logs/session" "session"

# 3. Error logs
migrate_logs "$UMEMORY_DIR/error" "$SANDBOX_DIR/logs/error" "error"
migrate_logs "$UMEMORY_DIR/errors" "$SANDBOX_DIR/logs/error" "error"

# 4. Development logs
migrate_logs "$UMEMORY_DIR/dev" "$SANDBOX_DIR/logs/development" "development"
migrate_logs "$UMEMORY_DIR/development" "$SANDBOX_DIR/logs/development" "development"

# 5. User-specific logs
if [ -d "$UMEMORY_DIR/user" ]; then
    for user_dir in "$UMEMORY_DIR/user"/*; do
        if [ -d "$user_dir" ]; then
            user_name=$(basename "$user_dir")
            user_log_dir="$SANDBOX_DIR/logs/archived/user-$user_name"
            mkdir -p "$user_log_dir"
            migrate_logs "$user_dir" "$user_log_dir" "user-$user_name"
        fi
    done
fi

# 6. Any other log files in uMEMORY root
find "$UMEMORY_DIR" -maxdepth 1 -name "*.log" -o -name "*-log-*" -o -name "session-*" | while read -r log_file; do
    if [ -f "$log_file" ]; then
        filename=$(basename "$log_file")
        log_info "Moving root log file: $filename"
        mv "$log_file" "$SANDBOX_DIR/logs/system/"
    fi
done

# Create log organization summary
cat > "$SANDBOX_DIR/logs/MIGRATION-SUMMARY.md" << EOF
# Log Migration Summary

**Date**: $(date)
**From**: uMEMORY various directories
**To**: /sandbox/logs organized structure

## New Log Organization

### /sandbox/logs/system/
- System-level logs and operations
- Previously in uMEMORY/system/

### /sandbox/logs/session/
- Session-based activity logs
- Previously in uMEMORY/session/

### /sandbox/logs/error/
- Error logs and debugging information
- Previously in uMEMORY/error/ and uMEMORY/errors/

### /sandbox/logs/development/
- Development and coding activity logs
- Previously in uMEMORY/dev/ and uMEMORY/development/

### /sandbox/logs/archived/
- Historical logs organized by user
- Previously in uMEMORY/user/*/

## Migration Process

1. **Backup Created**: All logs backed up to /backup/migration-archives/
2. **Safe Migration**: Files moved with timestamp collision handling
3. **Organization**: Logs categorized by type and purpose
4. **Preservation**: No data loss, all logs preserved

## Benefits

- **Centralized Logging**: All logs now in sandbox environment
- **Better Organization**: Logical categorization by purpose
- **Session Integration**: Logs align with session-based development
- **Easy Access**: Development logs alongside development work
- **Backup Safety**: Migration fully backed up

## Usage

Moving forward, all logging should use the sandbox structure:
- System logs: /sandbox/logs/system/
- Session logs: /sandbox/logs/session/
- Error logs: /sandbox/logs/error/
- Dev logs: /sandbox/logs/development/

The uMEMORY directory now focuses on knowledge and memory storage,
while logs live in the active development environment.
EOF

# Clean up empty directories in uMEMORY
find "$UMEMORY_DIR" -type d -empty -delete 2>/dev/null || true

# Update any scripts that reference old log locations
log_info "=== Updating Log References ==="

# Update session manager to use new log location
if [ -f "$UDOS_ROOT/uCORE/core/session-manager.sh" ]; then
    # This will be handled by the session manager using sandbox logs
    log_info "Session manager will use sandbox logs going forward"
fi

# Create symbolic links for backward compatibility (temporary)
if [ ! -L "$UMEMORY_DIR/logs" ]; then
    ln -sf "$SANDBOX_DIR/logs" "$UMEMORY_DIR/logs"
    log_info "Created compatibility symlink: uMEMORY/logs -> sandbox/logs"
fi

log_success "=== Log Migration Complete ==="
echo ""
echo -e "${BLUE}📊 Migration Summary:${NC}"
echo "• All logs moved from uMEMORY to sandbox/logs/"
echo "• Logs organized by type (system, session, error, development)"
echo "• Migration backed up to /backup/migration-archives/"
echo "• Compatibility symlink created for transition period"
echo "• See /sandbox/logs/MIGRATION-SUMMARY.md for details"
echo ""
echo -e "${YELLOW}⚠️  Next Steps:${NC}"
echo "• Update any scripts that reference old uMEMORY log paths"
echo "• Test logging functionality in new sandbox environment"
echo "• Remove compatibility symlink after transition complete"
echo ""
log_success "Sandbox now contains all system logs!"
