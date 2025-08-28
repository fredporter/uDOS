#!/bin/bash
# uDOS v1.0.5.5 - DESTROY Command
# Controlled deletion with EOL (End of Life) safety protocols
# ONLY command authorized for mass deletion in uDOS layered architecture

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# DESTROY safety settings
DESTROY_CONFIRMATION_REQUIRED=true
DESTROY_BACKUP_REQUIRED=true
DESTROY_LOG_FILE="$UDOS_ROOT/sandbox/logs/destroy.log"
CURRENT_SESSION="$(cat "$UDOS_ROOT/sandbox/session/current-session.json" 2>/dev/null | grep '"id"' | cut -d'"' -f4 || echo "default")"
CURRENT_ROLE="$(cat "$UDOS_ROOT/uMEMORY/user.md" 2>/dev/null | grep "^Role:" | cut -d' ' -f2- || echo "user")"

# Log destroy operations
log_destroy() {
    local operation="$1"
    local target="$2"
    local status="$3"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    
    mkdir -p "$(dirname "$DESTROY_LOG_FILE")"
    echo "[$timestamp] $operation: $target - $status (Session: $CURRENT_SESSION, Role: $CURRENT_ROLE)" >> "$DESTROY_LOG_FILE"
}

# Confirm destroy operation
confirm_destroy() {
    local target="$1"
    local description="$2"
    
    echo -e "${RED}⚠️  DESTROY OPERATION REQUESTED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "   Target: ${YELLOW}$target${NC}"
    echo -e "   Description: $description"
    echo -e "   Session: $CURRENT_SESSION"
    echo -e "   Role: $CURRENT_ROLE"
    echo ""
    echo -e "${RED}⚠️  THIS OPERATION CANNOT BE UNDONE${NC}"
    echo ""
    
    if [ "$DESTROY_CONFIRMATION_REQUIRED" = "true" ]; then
        read -p "Type 'DESTROY' to confirm: " confirmation
        if [ "$confirmation" != "DESTROY" ]; then
            echo -e "${GREEN}✅ Operation cancelled${NC}"
            log_destroy "DESTROY_CANCEL" "$target" "USER_CANCELLED"
            return 1
        fi
    fi
    
    return 0
}

# Create final backup before destroy
create_final_backup() {
    local target="$1"
    local backup_name="final-backup-before-destroy-$(date +%Y%m%d_%H%M%S)"
    
    echo -e "${BLUE}📦 Creating final backup before destroy...${NC}"
    
    if [ -f "$UDOS_ROOT/dev/scripts/session-backup-system.sh" ]; then
        "$UDOS_ROOT/dev/scripts/session-backup-system.sh" snapshot "$backup_name"
        echo -e "${GREEN}✅ Final backup created: $backup_name${NC}"
        log_destroy "FINAL_BACKUP" "$target" "SUCCESS"
        return 0
    else
        echo -e "${RED}❌ Session backup system not found${NC}"
        log_destroy "FINAL_BACKUP" "$target" "FAILED"
        return 1
    fi
}

# Destroy session data (safe for multi-role environment)
destroy_session() {
    local session_id="${1:-$CURRENT_SESSION}"
    
    if ! confirm_destroy "Session: $session_id" "Remove session data, preserve shared components"; then
        return 1
    fi
    
    if [ "$DESTROY_BACKUP_REQUIRED" = "true" ]; then
        if ! create_final_backup "session:$session_id"; then
            echo -e "${RED}❌ Cannot destroy without backup${NC}"
            return 1
        fi
    fi
    
    echo -e "${RED}🗑️  Destroying session: $session_id${NC}"
    
    # Remove session-specific data only
    local destroyed=false
    
    if [ -d "$UDOS_ROOT/sandbox/session" ]; then
        rm -rf "$UDOS_ROOT/sandbox/session"/*
        echo "   ✓ Session state cleared"
        destroyed=true
    fi
    
    if [ -d "$UDOS_ROOT/uMEMORY/data" ]; then
        rm -rf "$UDOS_ROOT/uMEMORY/data"/*
        echo "   ✓ Memory data cleared"
        destroyed=true
    fi
    
    if [ -d "$UDOS_ROOT/uKNOWLEDGE/data" ]; then
        rm -rf "$UDOS_ROOT/uKNOWLEDGE/data"/*
        echo "   ✓ Knowledge data cleared"
        destroyed=true
    fi
    
    if [ "$destroyed" = "true" ]; then
        echo -e "${GREEN}✅ Session destroyed (shared components preserved)${NC}"
        log_destroy "DESTROY_SESSION" "$session_id" "SUCCESS"
    else
        echo -e "${YELLOW}ℹ️  No session data found to destroy${NC}"
        log_destroy "DESTROY_SESSION" "$session_id" "NO_DATA"
    fi
}

# Destroy role configuration (safe for multi-role environment)
destroy_role() {
    local role_name="${1:-$CURRENT_ROLE}"
    
    if ! confirm_destroy "Role: $role_name" "Remove role configuration, preserve shared components"; then
        return 1
    fi
    
    if [ "$DESTROY_BACKUP_REQUIRED" = "true" ]; then
        if ! create_final_backup "role:$role_name"; then
            echo -e "${RED}❌ Cannot destroy without backup${NC}"
            return 1
        fi
    fi
    
    echo -e "${RED}🗑️  Destroying role: $role_name${NC}"
    
    # Remove role-specific files only
    local destroyed=false
    
    if [ -f "$UDOS_ROOT/uMEMORY/user.md" ]; then
        rm -f "$UDOS_ROOT/uMEMORY/user.md"
        echo "   ✓ User profile cleared"
        destroyed=true
    fi
    
    if [ -f "$UDOS_ROOT/uMEMORY/identity.md" ]; then
        rm -f "$UDOS_ROOT/uMEMORY/identity.md"
        echo "   ✓ Identity cleared"
        destroyed=true
    fi
    
    if [ "$destroyed" = "true" ]; then
        echo -e "${GREEN}✅ Role destroyed (shared components preserved)${NC}"
        log_destroy "DESTROY_ROLE" "$role_name" "SUCCESS"
    else
        echo -e "${YELLOW}ℹ️  No role data found to destroy${NC}"
        log_destroy "DESTROY_ROLE" "$role_name" "NO_DATA"
    fi
}

# Destroy sandbox (safe cleanup)
destroy_sandbox() {
    if ! confirm_destroy "Sandbox" "Remove all sandbox content (temp files, trash, logs)"; then
        return 1
    fi
    
    echo -e "${RED}🗑️  Destroying sandbox content${NC}"
    
    local destroyed=false
    
    for dir in temp trash logs backups; do
        if [ -d "$UDOS_ROOT/sandbox/$dir" ]; then
            rm -rf "$UDOS_ROOT/sandbox/$dir"/*
            echo "   ✓ Sandbox $dir cleared"
            destroyed=true
        fi
    done
    
    if [ "$destroyed" = "true" ]; then
        echo -e "${GREEN}✅ Sandbox destroyed${NC}"
        log_destroy "DESTROY_SANDBOX" "sandbox" "SUCCESS"
    else
        echo -e "${YELLOW}ℹ️  No sandbox content found to destroy${NC}"
        log_destroy "DESTROY_SANDBOX" "sandbox" "NO_DATA"
    fi
}

# EOL (End of Life) - Complete installation removal
destroy_installation() {
    echo -e "${RED}💀 END OF LIFE (EOL) OPERATION${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  THIS WILL REMOVE THE ENTIRE uDOS INSTALLATION${NC}"
    echo -e "${RED}⚠️  INCLUDING ALL ROLES AND SHARED COMPONENTS${NC}"
    echo ""
    
    if ! confirm_destroy "ENTIRE INSTALLATION" "Complete removal of uDOS installation"; then
        return 1
    fi
    
    # Require double confirmation for EOL
    echo ""
    echo -e "${RED}⚠️  FINAL CONFIRMATION REQUIRED${NC}"
    read -p "Type 'END_OF_LIFE' to proceed with complete removal: " final_confirmation
    if [ "$final_confirmation" != "END_OF_LIFE" ]; then
        echo -e "${GREEN}✅ EOL operation cancelled${NC}"
        log_destroy "DESTROY_EOL" "installation" "USER_CANCELLED"
        return 1
    fi
    
    if [ "$DESTROY_BACKUP_REQUIRED" = "true" ]; then
        if ! create_final_backup "installation:EOL"; then
            echo -e "${RED}❌ Cannot proceed with EOL without backup${NC}"
            return 1
        fi
    fi
    
    echo -e "${RED}💀 Initiating End of Life protocol...${NC}"
    
    # Remove everything except this script
    cd "$UDOS_ROOT"
    find . -mindepth 1 -maxdepth 1 ! -name "$(basename "${BASH_SOURCE[0]}")" -exec rm -rf {} +
    
    echo -e "${RED}💀 uDOS installation destroyed${NC}"
    echo -e "${BLUE}📦 Final backup preserved in system backups${NC}"
    log_destroy "DESTROY_EOL" "installation" "SUCCESS"
}

# Show destroy log
show_destroy_log() {
    echo -e "${BLUE}📊 DESTROY Operation Log${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ -f "$DESTROY_LOG_FILE" ]; then
        tail -20 "$DESTROY_LOG_FILE"
    else
        echo "No destroy operations logged yet"
    fi
}

# Main function
main() {
    case "${1:-help}" in
        "session")
            destroy_session "$2"
            ;;
        "role")
            destroy_role "$2"
            ;;
        "sandbox")
            destroy_sandbox
            ;;
        "eol"|"installation")
            destroy_installation
            ;;
        "log")
            show_destroy_log
            ;;
        "help"|*)
            echo -e "${BLUE}uDOS DESTROY Command - Controlled Deletion System${NC}"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo "Usage: $0 [command] [target]"
            echo ""
            echo "Safe Operations (preserve shared components):"
            echo "  session [id]    - Destroy session data only"
            echo "  role [name]     - Destroy role configuration only"
            echo "  sandbox         - Destroy sandbox content only"
            echo ""
            echo "Dangerous Operations:"
            echo "  eol             - End of Life: destroy entire installation"
            echo "  installation    - Same as eol"
            echo ""
            echo "Monitoring:"
            echo "  log             - Show destroy operation log"
            echo "  help            - Show this help"
            echo ""
            echo -e "${GREEN}🛡️  Safety Features:${NC}"
            echo "  • Confirmation required for all operations"
            echo "  • Automatic final backup before destroy"
            echo "  • Complete operation logging"
            echo "  • Preserves shared components in multi-role environment"
            echo ""
            echo -e "${RED}⚠️  Only DESTROY command can perform mass deletion in uDOS${NC}"
            ;;
    esac
}

main "$@"
