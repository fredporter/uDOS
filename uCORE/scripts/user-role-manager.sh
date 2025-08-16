#!/usr/bin/env bash
# [20-80-02] uDOS User Role Manager
# Location: uCORE/scripts/user-role-manager.sh
# Purpose: Manage user roles and data sovereignty for uMEMORY

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PRIVATE_MEMORY="$HOME/.uDOS/uMEMORY"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_help() {
    echo -e "${BLUE}uDOS User Role Manager${NC}"
    echo "====================="
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  init                    Initialize user role system"
    echo "  set-role <role>         Set current user role"
    echo "  get-role                Show current user role"
    echo "  validate <path>         Validate access to path"
    echo "  share <file> [public]   Share file (move to public)"
    echo "  unshare <file>          Unshare file (move to explicit)"
    echo "  list-shared             List publicly shared files"
    echo "  permissions             Show current permissions"
    echo ""
    echo "Roles:"
    echo "  wizard     Full access to all uMEMORY areas"
    echo "  sorcerer   Development access (sandbox, scripts, templates)"
    echo "  ghost      Read-only access to public content only"
    echo "  imp        Guided access through interfaces only"
    echo ""
    echo "Data Sovereignty:"
    echo "  explicit   Private data (default)"
    echo "  public     Shared data (opt-in)"
}

get_current_role() {
    if [[ -f "$PRIVATE_MEMORY/user/explicit/identity.md" ]]; then
        grep -o 'role.*' "$PRIVATE_MEMORY/user/explicit/identity.md" | cut -d: -f2 | xargs 2>/dev/null || echo "imp"
    else
        echo "imp"
    fi
}

validate_role() {
    local role="$1"
    case "$role" in
        wizard|sorcerer|ghost|imp) return 0 ;;
        *) return 1 ;;
    esac
}

validate_access() {
    local operation="$1"
    local path="$2"
    local role="$(get_current_role)"
    
    case "$operation" in
        "read")
            case "$role" in
                "wizard"|"sorcerer") return 0 ;;
                "ghost") [[ "$path" == *"/public/"* ]] && return 0 || return 1 ;;
                "imp") [[ "$path" == *"/guided/"* ]] && return 0 || return 1 ;;
            esac
            ;;
        "write")
            case "$role" in
                "wizard") return 0 ;;
                "sorcerer") 
                    [[ "$path" == *"/sandbox/"* || "$path" == *"/scripts/"* || "$path" == *"/templates/"* ]] && return 0 || return 1
                    ;;
                *) return 1 ;;
            esac
            ;;
    esac
    return 1
}

set_role() {
    local new_role="$1"
    
    if ! validate_role "$new_role"; then
        echo -e "${RED}❌ Invalid role: $new_role${NC}"
        echo "Valid roles: wizard, sorcerer, ghost, imp"
        return 1
    fi
    
    # Create identity file if it doesn't exist
    mkdir -p "$PRIVATE_MEMORY/user/explicit"
    
    # Update or create identity file
    local identity_file="$PRIVATE_MEMORY/user/explicit/identity.md"
    if [[ -f "$identity_file" ]]; then
        # Update existing role
        sed -i.bak "s/role:.*/role: $new_role/" "$identity_file"
    else
        # Create new identity file
        cat > "$identity_file" << EOF
# uDOS User Identity
[20-80-02] identity.md

## User Configuration
role: $new_role
created: $(date +"%Y-%m-%d %H:%M")
location: $(./uMEMORY/scripts/detect-location.sh 2>/dev/null | tail -1 || echo "UTC001")

## Data Sovereignty
default_sharing: explicit
allow_public_sharing: true

## Access Permissions
Based on role: $new_role
EOF
    fi
    
    # Set appropriate permissions
    apply_role_permissions "$new_role"
    
    echo -e "${GREEN}✅ Role set to: $new_role${NC}"
}

apply_role_permissions() {
    local role="$1"
    
    # Ensure private memory exists
    mkdir -p "$PRIVATE_MEMORY"/{user,sandbox,state,logs,missions,moves,milestones,scripts,templates,generated}/{explicit,public}
    
    case "$role" in
        "wizard")
            chmod -R 700 "$PRIVATE_MEMORY"
            echo -e "${GREEN}✅ Wizard permissions applied (full access)${NC}"
            ;;
        "sorcerer")
            chmod -R 700 "$PRIVATE_MEMORY"/{sandbox,scripts,templates}
            chmod -R 500 "$PRIVATE_MEMORY"/{user,state,logs,missions,moves,milestones,generated}
            echo -e "${GREEN}✅ Sorcerer permissions applied (development access)${NC}"
            ;;
        "ghost")
            chmod -R 500 "$PRIVATE_MEMORY"/*/public
            chmod -R 000 "$PRIVATE_MEMORY"/*/explicit
            chmod 700 "$PRIVATE_MEMORY" # Allow directory access
            echo -e "${GREEN}✅ Ghost permissions applied (read-only public)${NC}"
            ;;
        "imp")
            chmod -R 600 "$PRIVATE_MEMORY/user/explicit"  # Allow guided access
            chmod -R 400 "$PRIVATE_MEMORY"/*/public       # Read public content
            chmod -R 000 "$PRIVATE_MEMORY"/{sandbox,scripts,templates,state,logs,missions,moves,milestones,generated}/explicit
            echo -e "${GREEN}✅ Imp permissions applied (guided access only)${NC}"
            ;;
    esac
}

share_file() {
    local file_path="$1"
    local make_public="${2:-public}"
    local role="$(get_current_role)"
    
    if [[ ! -f "$file_path" ]]; then
        echo -e "${RED}❌ File not found: $file_path${NC}"
        return 1
    fi
    
    # Check if user can share files
    if [[ "$role" == "ghost" ]]; then
        echo -e "${RED}❌ Ghost users cannot share files${NC}"
        return 1
    fi
    
    # Convert explicit path to public path
    local public_path="${file_path/\/explicit\//\/public\/}"
    
    if [[ "$make_public" == "public" ]]; then
        # Move to public
        mkdir -p "$(dirname "$public_path")"
        mv "$file_path" "$public_path"
        echo -e "${GREEN}✅ File shared publicly: $(basename "$public_path")${NC}"
    else
        echo -e "${YELLOW}ℹ️  File remains private${NC}"
    fi
}

unshare_file() {
    local file_path="$1"
    local role="$(get_current_role)"
    
    if [[ ! -f "$file_path" ]]; then
        echo -e "${RED}❌ File not found: $file_path${NC}"
        return 1
    fi
    
    # Check if user can modify files
    if ! validate_access "write" "$file_path"; then
        echo -e "${RED}❌ Permission denied for: $file_path${NC}"
        return 1
    fi
    
    # Convert public path to explicit path
    local explicit_path="${file_path/\/public\//\/explicit\/}"
    
    mkdir -p "$(dirname "$explicit_path")"
    mv "$file_path" "$explicit_path"
    echo -e "${GREEN}✅ File made private: $(basename "$explicit_path")${NC}"
}

list_shared_files() {
    echo -e "${BLUE}📋 Publicly Shared Files${NC}"
    echo "========================"
    
    if [[ -d "$PRIVATE_MEMORY" ]]; then
        find "$PRIVATE_MEMORY" -path "*/public/*" -type f -name "*.md" | while read -r file; do
            local rel_path="${file#$PRIVATE_MEMORY/}"
            echo "  📄 $rel_path"
        done
    else
        echo -e "${YELLOW}No shared files found${NC}"
    fi
}

show_permissions() {
    local role="$(get_current_role)"
    echo -e "${BLUE}👤 Current User Role: $role${NC}"
    echo "=========================="
    
    case "$role" in
        "wizard")
            echo -e "${GREEN}✅ Full access to all uMEMORY areas${NC}"
            echo -e "${GREEN}✅ Can create and share any content${NC}"
            echo -e "${GREEN}✅ System administration access${NC}"
            ;;
        "sorcerer")
            echo -e "${GREEN}✅ Development access (sandbox, scripts, templates)${NC}"
            echo -e "${GREEN}✅ Can create explicit and public content in allowed areas${NC}"
            echo -e "${YELLOW}⚠️  Limited to development directories${NC}"
            ;;
        "ghost")
            echo -e "${YELLOW}⚠️  Read-only access to public content only${NC}"
            echo -e "${RED}❌ Cannot create or modify content${NC}"
            echo -e "${RED}❌ No access to private data${NC}"
            ;;
        "imp")
            echo -e "${YELLOW}⚠️  Guided access through interfaces only${NC}"
            echo -e "${YELLOW}⚠️  All content private by default${NC}"
            echo -e "${RED}❌ No direct file system access${NC}"
            ;;
    esac
    
    echo ""
    echo -e "${BLUE}🔒 Data Sovereignty:${NC}"
    echo "  explicit (private) - Default for all content"
    echo "  public (shared)    - Opt-in sharing"
}

# Main command handling
case "${1:-help}" in
    "init")
        echo -e "${BLUE}🔧 Initializing User Role System...${NC}"
        mkdir -p "$PRIVATE_MEMORY"/{user,sandbox,state,logs,missions,moves,milestones,scripts,templates,generated}/{explicit,public}
        set_role "wizard"  # Default to wizard for initialization
        echo -e "${GREEN}✅ User role system initialized${NC}"
        ;;
    "set-role")
        if [[ -z "${2:-}" ]]; then
            echo -e "${RED}❌ Role required${NC}"
            show_help
            exit 1
        fi
        set_role "$2"
        ;;
    "get-role")
        role="$(get_current_role)"
        echo -e "${BLUE}Current role: $role${NC}"
        ;;
    "validate")
        if [[ -z "${2:-}" ]]; then
            echo -e "${RED}❌ Path required${NC}"
            exit 1
        fi
        if validate_access "read" "$2"; then
            echo -e "${GREEN}✅ Read access granted${NC}"
        else
            echo -e "${RED}❌ Read access denied${NC}"
        fi
        if validate_access "write" "$2"; then
            echo -e "${GREEN}✅ Write access granted${NC}"
        else
            echo -e "${RED}❌ Write access denied${NC}"
        fi
        ;;
    "share")
        if [[ -z "${2:-}" ]]; then
            echo -e "${RED}❌ File path required${NC}"
            exit 1
        fi
        share_file "$2" "${3:-public}"
        ;;
    "unshare")
        if [[ -z "${2:-}" ]]; then
            echo -e "${RED}❌ File path required${NC}"
            exit 1
        fi
        unshare_file "$2"
        ;;
    "list-shared")
        list_shared_files
        ;;
    "permissions")
        show_permissions
        ;;
    "help"|*)
        show_help
        ;;
esac
