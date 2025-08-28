#!/bin/bash
# destroy.sh - Enhanced Destroy System with Smart Protection
# uDOS v1.3 - Role-based destruction with advanced backup options

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source backup-restore functions
if [ -f "$SCRIPT_DIR/backup-restore.sh" ]; then
    source "$SCRIPT_DIR/backup-restore.sh"
else
    # Define minimal logging functions if backup-restore not available
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
fi

# Configuration
USER_MD_FILE="$UDOS_ROOT/sandbox/user.md"
UMEMORY_DIR="$UDOS_ROOT/uMEMORY"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'
BOLD='\033[1m'

# ═══════════════════════════════════════════════════════════════════════
# PROTECTION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Check if user.md is protected from exposure
is_user_md_protected() {
    [ -f "$USER_MD_FILE" ] && grep -q "^\*\*Password\*\*: SET" "$USER_MD_FILE"
}

# Get user role safely
get_user_role_safe() {
    if [ -f "$USER_MD_FILE" ]; then
        grep "^\*\*Role\*\*:" "$USER_MD_FILE" 2>/dev/null | sed 's/^\*\*Role\*\*: *//' | head -1
    else
        echo "ghost"
    fi
}

# Create emergency backup before any destructive operation
create_emergency_backup() {
    local operation="$1"
    
    log_info "Creating emergency backup before $operation..."
    
    # Use the backup-restore system if available
    if command -v create_backup >/dev/null 2>&1; then
        local backup_file=$(create_backup "emergency" "Pre-$operation emergency backup")
        
        if [ -n "$backup_file" ] && [ -f "$backup_file" ]; then
            echo -e "${GREEN}✓${NC} Emergency backup created: $(basename "$backup_file")"
            echo "$backup_file"
            return 0
        fi
    fi
    
    # Fallback manual backup
    local timestamp=$(printf "%08X-%06X" $(date +%s) $$)
    local backup_dir="$UMEMORY_DIR/backups/emergency"
    mkdir -p "$backup_dir"
    local backup_file="$backup_dir/$timestamp-pre-$operation.tar.gz"
    
    if tar -czf "$backup_file" -C "$UDOS_ROOT" \
        --exclude="uMEMORY/backups" \
        --exclude="*.log" \
        --exclude=".DS_Store" \
        uMEMORY sandbox 2>/dev/null; then
        
        echo -e "${GREEN}✓${NC} Emergency backup created: $(basename "$backup_file")"
        echo "$backup_file"
        return 0
    else
        echo -e "${RED}✗${NC} Failed to create emergency backup!"
        return 1
    fi
}

# Protect sandbox/user.md from exposure
protect_user_md() {
    local temp_location="$UMEMORY_DIR/system/.user-protected.md"
    
    if [ -f "$USER_MD_FILE" ]; then
        mkdir -p "$(dirname "$temp_location")"
        # Move to protected location
        cp "$USER_MD_FILE" "$temp_location"
        chmod 600 "$temp_location"
        
        # Remove from sandbox temporarily
        rm -f "$USER_MD_FILE"
        
        log_info "User profile protected from exposure"
        return 0
    fi
    
    return 1
}

# Restore protected user.md
restore_user_md() {
    local temp_location="$UMEMORY_DIR/system/.user-protected.md"
    
    if [ -f "$temp_location" ]; then
        mkdir -p "$(dirname "$USER_MD_FILE")"
        cp "$temp_location" "$USER_MD_FILE"
        chmod 644 "$USER_MD_FILE"
        rm -f "$temp_location"
        
        log_info "User profile restored"
        return 0
    fi
    
    return 1
}

# ═══════════════════════════════════════════════════════════════════════
# BACKUP MANAGEMENT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Backup role folders before destruction
backup_role_folders() {
    local operation="$1"
    local role=$(get_user_role_safe)
    
    log_info "Backing up role folders before $operation..."
    
    # Create role-specific backup directory
    local role_backup_dir="$UMEMORY_DIR/backups/role-archives"
    mkdir -p "$role_backup_dir"
    
    local timestamp=$(printf "%08X-%06X" $(date +%s) $$)
    local archive_file="$role_backup_dir/$timestamp-pre-$operation-roles.tar.gz"
    
    # Backup all role folders
    local roles=("tomb" "sorcerer" "wizard" "imp" "drone" "ghost")
    local existing_roles=()
    
    for role_name in "${roles[@]}"; do
        if [ -d "$UDOS_ROOT/$role_name" ]; then
            existing_roles+=("$role_name")
        fi
    done
    
    if [ ${#existing_roles[@]} -gt 0 ]; then
        if tar -czf "$archive_file" -C "$UDOS_ROOT" "${existing_roles[@]}" 2>/dev/null; then
            log_success "Role folders archived: $(basename "$archive_file")"
            echo "$archive_file"
            return 0
        else
            log_error "Failed to archive role folders"
            return 1
        fi
    else
        log_warning "No role folders found to backup"
        return 1
    fi
}

# Show role folder status
show_role_status() {
    echo -e "${BOLD}${BLUE}📁 Role Folder Status:${NC}"
    echo ""
    
    local roles=("tomb" "sorcerer" "wizard" "imp" "drone" "ghost")
    for role in "${roles[@]}"; do
        if [ -d "$UDOS_ROOT/$role" ]; then
            local size=$(du -sh "$UDOS_ROOT/$role" 2>/dev/null | cut -f1)
            local file_count=$(find "$UDOS_ROOT/$role" -type f | wc -l)
            echo -e "  ${GREEN}✓${NC} $role - $size ($file_count files)"
        else
            echo -e "  ${RED}✗${NC} $role - Not found"
        fi
    done
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════
# DESTRUCTION OPTIONS
# ═══════════════════════════════════════════════════════════════════════

# Option 1: Reset Identity (Enhanced)
reset_identity() {
    echo -e "${BOLD}${YELLOW}⚠️  RESET IDENTITY${NC}"
    echo -e "This will reset your identity while preserving all data and role folders."
    echo -e "A backup will be created before proceeding."
    echo ""
    
    # Create emergency backup
    local backup_file
    if ! backup_file=$(create_emergency_backup "identity-reset"); then
        log_error "Cannot proceed without backup"
        return 1
    fi
    
    # Reset identity files
    log_info "Resetting identity..."
    
    # Clear identity but preserve setup
    if [ -f "$USER_MD_FILE" ]; then
        cat > "$USER_MD_FILE" << 'EOF'
# User Profile

**Status**: New User
**Role**: ghost
**Created**: [timestamp will be updated on next login]

Welcome to uDOS! Your previous session has been backed up.

## Quick Start
- Run the welcome mission to get started
- Your data and role folders have been preserved
- Use 'restore' command if you need to recover your previous identity

## Backup Information
Your previous identity and all data has been backed up automatically.
EOF
    fi
    
    # Clear session logs but preserve system
    rm -f "$UMEMORY_DIR/system/session-moves.json" 2>/dev/null || true
    rm -f "$UMEMORY_DIR/system/undo-stack.json" 2>/dev/null || true
    
    log_success "Identity reset completed. Previous state backed up to: $(basename "$backup_file")"
    echo -e "${GREEN}✓${NC} Your data and role folders remain intact"
    echo -e "${GREEN}✓${NC} Emergency backup available for recovery"
}

# Option 2: Fresh Start (Enhanced)
fresh_start() {
    echo -e "${BOLD}${YELLOW}⚠️  FRESH START${NC}"
    echo -e "This will clear uMEMORY and sandbox but preserve role folders."
    echo -e "A complete backup will be created before proceeding."
    echo ""
    
    read -p "Are you sure you want a fresh start? (type 'yes' to confirm): " confirm
    if [ "$confirm" != "yes" ]; then
        log_info "Fresh start cancelled"
        return 0
    fi
    
    # Create emergency backup
    local backup_file
    if ! backup_file=$(create_emergency_backup "fresh-start"); then
        log_error "Cannot proceed without backup"
        return 1
    fi
    
    # Backup role folders
    backup_role_folders "fresh-start"
    
    # Protect user.md
    protect_user_md
    
    # Clear memory and sandbox
    log_info "Clearing uMEMORY and sandbox..."
    
    # Clear uMEMORY but preserve system backups
    find "$UMEMORY_DIR" -mindepth 1 -not -path "*/backups/*" -not -path "*/system/.user-protected.md" -delete 2>/dev/null || true
    
    # Clear sandbox
    rm -rf "$UDOS_ROOT/sandbox"
    mkdir -p "$UDOS_ROOT/sandbox"
    
    # Restore user.md
    restore_user_md
    
    # Initialize fresh uMEMORY structure
    mkdir -p "$UMEMORY_DIR"/{core,system,templates,user}
    
    # Create fresh user.md if needed
    if [ ! -f "$USER_MD_FILE" ]; then
        cat > "$USER_MD_FILE" << 'EOF'
# User Profile

**Status**: Fresh Start
**Role**: ghost
**Created**: [timestamp will be updated on setup]

Welcome to your fresh uDOS environment!

## What Was Preserved
- All role folders and their contents
- System backups and archives
- Emergency backup of previous state

## What Was Cleared
- uMEMORY (except backups)
- Sandbox user data (except user.md)
- Session history

## Recovery
Your previous state is available in the emergency backup.
Use the backup-restore system to recover if needed.
EOF
    fi
    
    log_success "Fresh start completed. Previous state backed up to: $(basename "$backup_file")"
    echo -e "${GREEN}✓${NC} Role folders preserved"
    echo -e "${GREEN}✓${NC} Emergency backup available for recovery"
}

# Option 3: Archive & Reset (Enhanced)
archive_and_reset() {
    echo -e "${BOLD}${YELLOW}⚠️  ARCHIVE & RESET${NC}"
    echo -e "This will archive everything and start completely fresh."
    echo -e "All data will be preserved in archives but the system will be reset."
    echo ""
    
    read -p "Are you sure you want to archive and reset? (type 'ARCHIVE' to confirm): " confirm
    if [ "$confirm" != "ARCHIVE" ]; then
        log_info "Archive and reset cancelled"
        return 0
    fi
    
    # Create master archive
    local timestamp=$(printf "%08X-%06X" $(date +%s) $$)
    local archive_dir="$UMEMORY_DIR/backups/master-archives"
    mkdir -p "$archive_dir"
    local master_archive="$archive_dir/$timestamp-complete-system.tar.gz"
    
    log_info "Creating master archive of entire system..."
    
    # Protect user.md before archiving
    protect_user_md
    
    # Create complete system archive
    if tar -czf "$master_archive" \
        -C "$UDOS_ROOT" \
        --exclude="uMEMORY/backups/master-archives/$timestamp-complete-system.tar.gz" \
        --exclude="*.log" \
        --exclude=".DS_Store" \
        uMEMORY sandbox tomb sorcerer wizard imp drone ghost 2>/dev/null; then
        
        log_success "Master archive created: $(basename "$master_archive")"
    else
        log_error "Failed to create master archive"
        restore_user_md
        return 1
    fi
    
    # Clear everything except the archive
    log_info "Resetting system to factory state..."
    
    # Clear all role folders
    local roles=("tomb" "sorcerer" "wizard" "imp" "drone" "ghost")
    for role in "${roles[@]}"; do
        if [ -d "$UDOS_ROOT/$role" ]; then
            rm -rf "$UDOS_ROOT/$role"
            log_info "Cleared role folder: $role"
        fi
    done
    
    # Clear memory and sandbox
    find "$UMEMORY_DIR" -mindepth 1 -not -path "*/backups/*" -delete 2>/dev/null || true
    rm -rf "$UDOS_ROOT/sandbox"
    
    # Initialize factory fresh system
    mkdir -p "$UDOS_ROOT/sandbox"
    mkdir -p "$UMEMORY_DIR"/{core,system,templates,user}
    
    # Create minimal ghost role
    mkdir -p "$UDOS_ROOT/ghost"/{backup,public-docs,temp-sandbox,demo-interface}
    echo '{"role": "ghost", "permissions": ["read"], "restrictions": ["no_admin"]}' > "$UDOS_ROOT/ghost/permissions.json"
    
    # Create factory user.md
    cat > "$UDOS_ROOT/sandbox/user.md" << 'EOF'
# User Profile

**Status**: Factory Reset
**Role**: ghost
**Created**: [timestamp will be updated on setup]

Welcome to uDOS! Your system has been reset to factory state.

## Archive Information
Your complete previous system has been archived and is available for restoration.

## What's Available
- Fresh ghost role environment
- Clean sandbox
- All previous data preserved in master archive

## Recovery
Your complete previous system is archived and can be restored if needed.
Run the backup-restore system to access your archives.
EOF
    
    log_success "Archive and reset completed. Master archive: $(basename "$master_archive")"
    echo -e "${GREEN}✓${NC} Complete system archived"
    echo -e "${GREEN}✓${NC} Fresh environment initialized"
    echo -e "${GREEN}✓${NC} All data preserved in archive"
}

# Option 4: Reboot Only (Enhanced)
reboot_only() {
    echo -e "${BOLD}${BLUE}🔄 REBOOT ONLY${NC}"
    echo -e "This will restart the system without any data changes."
    echo -e "All data will be preserved exactly as-is."
    echo ""
    
    # Clear only temporary files
    log_info "Clearing temporary files..."
    
    # Clear session state but preserve history
    rm -f "$UMEMORY_DIR/system/session-moves.json" 2>/dev/null || true
    
    # Clear any temp files
    find "$UDOS_ROOT" -name "*.tmp" -delete 2>/dev/null || true
    find "$UDOS_ROOT" -name ".DS_Store" -delete 2>/dev/null || true
    
    # Auto-cleanup trash during reboot
    if [ -x "$UDOS_ROOT/uCORE/bin/trash" ]; then
        log_info "Running automatic trash cleanup..."
        "$UDOS_ROOT/uCORE/bin/trash" cleanup
        "$UDOS_ROOT/uCORE/bin/trash" optimize
    fi
    
    # Update user.md with reboot timestamp
    if [ -f "$USER_MD_FILE" ]; then
        if grep -q "**Last Reboot**:" "$USER_MD_FILE"; then
            sed -i '' "s/\*\*Last Reboot\*\*:.*/\*\*Last Reboot\*\*: $(date)/" "$USER_MD_FILE"
        else
            echo "**Last Reboot**: $(date)" >> "$USER_MD_FILE"
        fi
    fi
    
    log_success "System rebooted. All data preserved."
    echo -e "${GREEN}✓${NC} Temporary files cleared"
    echo -e "${GREEN}✓${NC} Session state reset"
    echo -e "${GREEN}✓${NC} Trash auto-cleanup completed"
    echo -e "${GREEN}✓${NC} All user data intact"
}

# Option 5: Exit Safely (Enhanced)
exit_safely() {
    echo -e "${BOLD}${GREEN}💾 EXIT SAFELY${NC}"
    echo -e "This will create an exit backup and shut down safely."
    echo -e "All data will be preserved with automatic backup."
    echo ""
    
    # Create exit backup
    local backup_file
    if command -v create_backup >/dev/null 2>&1; then
        backup_file=$(create_backup "exit" "Safe exit backup")
    else
        backup_file=$(create_emergency_backup "exit")
    fi
    
    # Show final status
    show_role_status
    
    log_success "Exit backup completed: $(basename "$backup_file")"
    echo -e "${GREEN}✓${NC} All data safely backed up"
    echo -e "${GREEN}✓${NC} System ready for shutdown"
    echo ""
    echo -e "${BOLD}${BLUE}Thank you for using uDOS!${NC}"
    
    exit 0
}

# ═══════════════════════════════════════════════════════════════════════
# INTERACTIVE MENU
# ═══════════════════════════════════════════════════════════════════════

show_destroy_menu() {
    local role=$(get_user_role_safe)
    local protected=$(is_user_md_protected && echo "Yes" || echo "No")
    
    echo -e "${BOLD}${RED}⚠️  uDOS DESTROY SYSTEM v1.3${NC}"
    echo -e "${BOLD}${RED}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "${BOLD}Current Status:${NC}"
    echo -e "  • Role: $role"
    echo -e "  • User Protection: $protected"
    echo -e "  • Emergency Backups: Enabled"
    echo ""
    show_role_status
    echo ""
    echo -e "${BOLD}${YELLOW}Destruction Options:${NC}"
    echo ""
    echo -e "  ${BOLD}[1]${NC} ${CYAN}Reset Identity${NC}"
    echo -e "      Reset user identity, preserve all data and role folders"
    echo -e "      ${GREEN}✓${NC} Creates emergency backup"
    echo -e "      ${GREEN}✓${NC} Preserves all role folders and data"
    echo ""
    echo -e "  ${BOLD}[2]${NC} ${CYAN}Fresh Start${NC}" 
    echo -e "      Clear uMEMORY and sandbox, preserve role folders"
    echo -e "      ${GREEN}✓${NC} Creates emergency backup"
    echo -e "      ${GREEN}✓${NC} Preserves role folders"
    echo -e "      ${YELLOW}⚠${NC}  Clears uMEMORY and sandbox"
    echo ""
    echo -e "  ${BOLD}[3]${NC} ${CYAN}Archive & Reset${NC}"
    echo -e "      Archive everything and start completely fresh"
    echo -e "      ${GREEN}✓${NC} Creates master archive of entire system"
    echo -e "      ${YELLOW}⚠${NC}  Resets everything to factory state"
    echo ""
    echo -e "  ${BOLD}[4]${NC} ${CYAN}Reboot Only${NC}"
    echo -e "      Restart system without any data changes"
    echo -e "      ${GREEN}✓${NC} Preserves all data exactly as-is"
    echo -e "      ${GREEN}✓${NC} Only clears temporary files"
    echo ""
    echo -e "  ${BOLD}[5]${NC} ${CYAN}Exit Safely${NC}"
    echo -e "      Create backup and shut down safely"
    echo -e "      ${GREEN}✓${NC} Creates exit backup"
    echo -e "      ${GREEN}✓${NC} Safe shutdown"
    echo ""
    echo -e "  ${BOLD}[T]${NC} ${PURPLE}Trash Management${NC}"
    echo -e "      Empty trash, optimize backups"
    echo ""
    echo -e "  ${BOLD}[B]${NC} ${PURPLE}Backup Management${NC}"
    echo -e "      Access backup/restore system"
    echo ""
    echo -e "  ${BOLD}[Q]${NC} ${WHITE}Quit${NC}"
    echo -e "      Exit without changes"
    echo ""
}

# Main interactive loop
interactive_destroy() {
    while true; do
        clear
        show_destroy_menu
        
        read -p "Choose an option [1-5, T, B, Q]: " choice
        
        case "$choice" in
            1)
                echo ""
                reset_identity
                read -p "Press Enter to continue..."
                ;;
            2)
                echo ""
                fresh_start
                read -p "Press Enter to continue..."
                ;;
            3)
                echo ""
                archive_and_reset
                read -p "Press Enter to continue..."
                ;;
            4)
                echo ""
                reboot_only
                read -p "Press Enter to continue..."
                ;;
            5)
                echo ""
                exit_safely
                ;;
            [Tt])
                echo ""
                echo -e "${BOLD}${PURPLE}🗑️ TRASH MANAGEMENT${NC}"
                echo ""
                echo "1. Empty all trash"
                echo "2. Empty deprecated files only"  
                echo "3. Empty old backups only"
                echo "4. Optimize backup retention"
                echo "5. Show trash status"
                echo "6. Return to destroy menu"
                echo ""
                read -p "Choose trash option [1-6]: " trash_choice
                
                case "$trash_choice" in
                    1)
                        if [ -x "$UDOS_ROOT/uCORE/bin/trash" ]; then
                            echo ""
                            echo "⚠️  This will permanently delete ALL trash contents"
                            read -p "Type 'EMPTY' to confirm: " confirm
                            if [ "$confirm" = "EMPTY" ]; then
                                "$UDOS_ROOT/uCORE/bin/trash" empty all
                                log_success "All trash emptied"
                            else
                                log_info "Trash empty cancelled"
                            fi
                        else
                            log_error "Trash system not available"
                        fi
                        ;;
                    2)
                        if [ -x "$UDOS_ROOT/uCORE/bin/trash" ]; then
                            "$UDOS_ROOT/uCORE/bin/trash" empty deprecated
                            log_success "Deprecated files emptied from trash"
                        else
                            log_error "Trash system not available"
                        fi
                        ;;
                    3)
                        if [ -x "$UDOS_ROOT/uCORE/bin/trash" ]; then
                            "$UDOS_ROOT/uCORE/bin/trash" empty backups
                            log_success "Old backups emptied from trash"
                        else
                            log_error "Trash system not available"
                        fi
                        ;;
                    4)
                        if [ -x "$UDOS_ROOT/uCORE/bin/trash" ]; then
                            "$UDOS_ROOT/uCORE/bin/trash" optimize
                            log_success "Backup retention optimized"
                        else
                            log_error "Trash system not available"
                        fi
                        ;;
                    5)
                        if [ -x "$UDOS_ROOT/uCORE/bin/trash" ]; then
                            "$UDOS_ROOT/uCORE/bin/trash" status
                        else
                            log_error "Trash system not available"
                        fi
                        ;;
                    6)
                        # Return to main menu
                        ;;
                    *)
                        log_error "Invalid trash option: $trash_choice"
                        ;;
                esac
                echo ""
                read -p "Press Enter to continue..."
                ;;
            [Bb])
                echo ""
                echo -e "${BOLD}${PURPLE}Launching Backup Management...${NC}"
                echo ""
                if [ -f "$SCRIPT_DIR/backup-restore.sh" ]; then
                    "$SCRIPT_DIR/backup-restore.sh" help
                else
                    echo "Backup system not available. Use manual backup commands."
                fi
                echo ""
                read -p "Press Enter to return to destroy menu..."
                ;;
            [Qq])
                echo ""
                log_info "Exiting without changes"
                exit 0
                ;;
            *)
                echo ""
                log_error "Invalid choice: $choice"
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# ═══════════════════════════════════════════════════════════════════════
# COMMAND LINE INTERFACE
# ═══════════════════════════════════════════════════════════════════════

# Show help
show_help() {
    echo -e "${BOLD}${RED}uDOS Destroy System v1.3${NC}"
    echo ""
    echo -e "${BOLD}USAGE:${NC}"
    echo -e "  destroy                     Interactive destroy menu"
    echo -e "  destroy reset-identity      Reset identity only"
    echo -e "  destroy fresh-start         Fresh start with role preservation"
    echo -e "  destroy archive-reset       Archive everything and reset"
    echo -e "  destroy reboot              Reboot without data changes"
    echo -e "  destroy exit                Exit safely with backup"
    echo ""
    echo -e "${BOLD}FEATURES:${NC}"
    echo -e "  • Emergency backups before destructive operations"
    echo -e "  • Role folder preservation options"
    echo -e "  • User profile protection from exposure"
    echo -e "  • Master archiving for complete preservation"
    echo -e "  • Integration with backup-restore system"
    echo ""
    echo -e "${BOLD}SAFETY:${NC}"
    echo -e "  • All destructive operations create backups first"
    echo -e "  • User credentials never exposed during operations"
    echo -e "  • Role-based data preservation"
    echo -e "  • Comprehensive logging of all operations"
}

# Main function
main() {
    local command="${1:-interactive}"
    
    case "$command" in
        interactive|"")
            interactive_destroy
            ;;
        reset-identity)
            reset_identity
            ;;
        fresh-start)
            fresh_start
            ;;
        archive-reset)
            archive_and_reset
            ;;
        reboot)
            reboot_only
            ;;
        exit)
            exit_safely
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

# Check for legacy compatibility
if [ "$#" -eq 0 ]; then
    # Check if this is being called in legacy mode (single letter choice)
    if [ -t 0 ] && [ -t 1 ]; then
        # Interactive terminal - use new interface
        main "interactive"
    else
        # Non-interactive or legacy - show help
        show_help
    fi
else
    # Run with provided arguments
    main "$@"
fi
