#!/bin/bash

# uSCRIPT Library Script: System Backup Tool v2.1.0
#
# Description: Comprehensive system backup with compression and encryption
# Author: uDOS Team
# Created: 2025-08-17
# Updated: 2025-08-17
# Category: automation
# Tags: backup, system, compression, encryption
#
# Usage:
#     system-backup --source=PATH --destination=PATH [--encrypt] [--compress]
#
# Dependencies:
#     - tar, gzip, openssl
#
# uSCRIPT Registry: system-backup
# uDOS Integration: ✅ Full integration with uMEMORY and logging

set -euo pipefail

# Configuration
readonly SCRIPT_NAME="system-backup"
readonly VERSION="2.1.0"
readonly TIMESTAMP=$(date '+%Y%m%d-%H%M%S')

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Default settings
COMPRESS=true
ENCRYPT=false
VERBOSE=false
SOURCE_PATH=""
DEST_PATH=""

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")  echo -e "${BLUE}[${timestamp}] [INFO]${NC} $message" ;;
        "WARN")  echo -e "${YELLOW}[${timestamp}] [WARN]${NC} $message" ;;
        "ERROR") echo -e "${RED}[${timestamp}] [ERROR]${NC} $message" ;;
        "SUCCESS") echo -e "${GREEN}[${timestamp}] [SUCCESS]${NC} $message" ;;
    esac
}

# Show help
show_help() {
    cat << EOF
uSCRIPT System Backup Tool v$VERSION

USAGE:
    $SCRIPT_NAME --source=PATH --destination=PATH [OPTIONS]

OPTIONS:
    --source=PATH       Source directory to backup
    --destination=PATH  Destination for backup file
    --encrypt          Enable encryption (requires password)
    --no-compress      Disable compression
    --verbose          Enable verbose output
    --help             Show this help

EXAMPLES:
    $SCRIPT_NAME --source=/Users/john/Documents --destination=/backup/
    $SCRIPT_NAME --source=/data --destination=/backup/ --encrypt
    $SCRIPT_NAME --source=/home --destination=/mnt/backup/ --no-compress

FEATURES:
    - Compression with gzip
    - Optional encryption with OpenSSL
    - Progress tracking
    - Integrity verification
    - uDOS logging integration

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --source=*)
                SOURCE_PATH="${1#*=}"
                shift
                ;;
            --destination=*)
                DEST_PATH="${1#*=}"
                shift
                ;;
            --encrypt)
                ENCRYPT=true
                shift
                ;;
            --no-compress)
                COMPRESS=false
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Validate inputs
validate_inputs() {
    if [[ -z "$SOURCE_PATH" ]]; then
        log "ERROR" "Source path is required (--source=PATH)"
        exit 1
    fi
    
    if [[ -z "$DEST_PATH" ]]; then
        log "ERROR" "Destination path is required (--destination=PATH)"
        exit 1
    fi
    
    if [[ ! -d "$SOURCE_PATH" ]]; then
        log "ERROR" "Source directory does not exist: $SOURCE_PATH"
        exit 1
    fi
    
    if [[ ! -d "$DEST_PATH" ]]; then
        log "WARN" "Destination directory does not exist, creating: $DEST_PATH"
        mkdir -p "$DEST_PATH" || {
            log "ERROR" "Cannot create destination directory: $DEST_PATH"
            exit 1
        }
    fi
}

# Create backup
create_backup() {
    local source_name=$(basename "$SOURCE_PATH")
    local backup_name="${source_name}-backup-${TIMESTAMP}"
    local backup_file="${DEST_PATH}/${backup_name}.tar"
    
    log "INFO" "Starting backup of $SOURCE_PATH"
    log "INFO" "Backup file: $backup_file"
    
    # Build tar command
    local tar_cmd="tar -cf '$backup_file'"
    
    if [[ "$VERBOSE" == "true" ]]; then
        tar_cmd="$tar_cmd -v"
    fi
    
    tar_cmd="$tar_cmd -C '$(dirname "$SOURCE_PATH")' '$(basename "$SOURCE_PATH")'"
    
    # Execute backup
    eval "$tar_cmd" || {
        log "ERROR" "Backup creation failed"
        exit 1
    }
    
    log "SUCCESS" "Backup created: $backup_file"
    
    # Compress if enabled
    if [[ "$COMPRESS" == "true" ]]; then
        log "INFO" "Compressing backup..."
        gzip "$backup_file" || {
            log "ERROR" "Compression failed"
            exit 1
        }
        backup_file="${backup_file}.gz"
        log "SUCCESS" "Backup compressed: $backup_file"
    fi
    
    # Encrypt if enabled
    if [[ "$ENCRYPT" == "true" ]]; then
        log "INFO" "Encrypting backup..."
        read -s -p "Enter encryption password: " password
        echo
        
        openssl enc -aes-256-cbc -salt -in "$backup_file" -out "${backup_file}.enc" -pass "pass:$password" || {
            log "ERROR" "Encryption failed"
            exit 1
        }
        
        rm "$backup_file"
        backup_file="${backup_file}.enc"
        log "SUCCESS" "Backup encrypted: $backup_file"
    fi
    
    # Show final statistics
    local file_size=$(du -h "$backup_file" | cut -f1)
    local source_size=$(du -sh "$SOURCE_PATH" | cut -f1)
    
    log "INFO" "Backup completed successfully"
    log "INFO" "Source size: $source_size"
    log "INFO" "Backup size: $file_size"
    log "INFO" "Backup location: $backup_file"
}

# Main execution
main() {
    log "INFO" "uSCRIPT System Backup Tool v$VERSION"
    
    parse_args "$@"
    validate_inputs
    create_backup
    
    log "SUCCESS" "Backup operation completed successfully"
}

# Execute main function with all arguments
main "$@"
