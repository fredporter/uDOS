#!/bin/bash
# developer-mode.sh - uDOS v1.0 Developer Mode Management
# Single developer mode with limited backups and selective access control

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UMEM="${UDOS_ROOT}/uMemory"
DEV_STATE_FILE="${UMEM}/state/developer-mode.json"
BACKUP_DIR="${UMEM}/backups/developer"

# Ensure required directories exist
mkdir -p "$(dirname "$DEV_STATE_FILE")"
mkdir -p "$BACKUP_DIR"

# Get current developer mode status
get_developer_mode_status() {
    if [[ -f "$DEV_STATE_FILE" ]]; then
        jq -r '.enabled // false' "$DEV_STATE_FILE" 2>/dev/null || echo "false"
    else
        echo "false"
    fi
}

# Enable developer mode
enable_developer_mode() {
    local user_role
    user_role=$(get_user_role)
    
    if [[ "$user_role" != "wizard" && "$user_role" != "sorcerer" ]]; then
        echo "❌ Developer mode requires wizard or sorcerer role"
        echo "   Current role: $user_role"
        return 1
    fi
    
    echo "🔧 Enabling developer mode..."
    
    # Create backup of critical scripts
    backup_core_scripts
    
    # Set developer mode state
    cat > "$DEV_STATE_FILE" << EOF
{
  "enabled": true,
  "enabled_by": "$user_role",
  "enabled_at": "$(date -Iseconds)",
  "permissions": {
    "ucode_editing": true,
    "utemplate_editing": true,
    "uknowledge_editing": true,
    "script_backups": true
  }
}
EOF
    
    echo "✅ Developer mode enabled"
    echo "📋 Available capabilities:"
    echo "   - Edit uCode scripts (with backups)"
    echo "   - Modify uTemplate system"  
    echo "   - Full uKnowledge access"
    echo "   - Script backup management"
}

# Disable developer mode
disable_developer_mode() {
    echo "🔒 Disabling developer mode..."
    
    # Update state
    cat > "$DEV_STATE_FILE" << EOF
{
  "enabled": false,
  "disabled_at": "$(date -Iseconds)",
  "permissions": {
    "ucode_editing": false,
    "utemplate_editing": false,
    "uknowledge_editing": true,
    "script_backups": false
  }
}
EOF
    
    echo "✅ Developer mode disabled"
    echo "📋 Wizard mode still available:"
    echo "   - All wizard functions work"
    echo "   - uKnowledge read/write access"
    echo "   - Cannot edit uCode or uTemplate"
}

# Backup core scripts
backup_core_scripts() {
    echo "💾 Creating backups of core scripts..."
    
    local timestamp
    timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_session="${BACKUP_DIR}/${timestamp}"
    
    mkdir -p "$backup_session"
    
    # Backup critical uCode scripts
    if [[ -f "${UDOS_ROOT}/uCode/ucode.sh" ]]; then
        cp "${UDOS_ROOT}/uCode/ucode.sh" "${backup_session}/ucode.sh.backup"
        echo "✅ Backed up ucode.sh"
    fi
    
    # Backup other critical scripts
    for script in user-roles.sh companion-system.sh template-generator.sh; do
        if [[ -f "${UDOS_ROOT}/uCode/$script" ]]; then
            cp "${UDOS_ROOT}/uCode/$script" "${backup_session}/${script}.backup"
            echo "✅ Backed up $script"
        fi
    done
    
    # Create backup manifest
    cat > "${backup_session}/manifest.json" << EOF
{
  "created": "$(date -Iseconds)",
  "session": "$timestamp",
  "files": [
    "ucode.sh.backup",
    "user-roles.sh.backup", 
    "companion-system.sh.backup",
    "template-generator.sh.backup"
  ],
  "purpose": "Developer mode activation backup"
}
EOF
    
    echo "💾 Backup session created: $timestamp"
}

# List available backups
list_backups() {
    echo "💾 Available Script Backups:"
    echo "=========================="
    
    if [[ ! -d "$BACKUP_DIR" ]]; then
        echo "No backups found"
        return 0
    fi
    
    for backup_session in "$BACKUP_DIR"/*; do
        if [[ -d "$backup_session" && -f "$backup_session/manifest.json" ]]; then
            local session_name
            session_name=$(basename "$backup_session")
            local created
            created=$(jq -r '.created' "$backup_session/manifest.json" 2>/dev/null || echo "unknown")
            
            echo "📁 $session_name (created: $created)"
            
            # List files in backup
            if [[ -f "$backup_session/manifest.json" ]]; then
                jq -r '.files[]' "$backup_session/manifest.json" | sed 's/^/   ├── /'
            fi
        fi
    done
}

# Get user role (simplified version)
get_user_role() {
    if [[ -f "${UMEM}/user/identity.md" ]]; then
        grep "^Role:" "${UMEM}/user/identity.md" | cut -d: -f2 | tr -d ' ' || echo "ghost"
    else
        echo "ghost"
    fi
}

# Check if user can edit specific component
can_edit() {
    local component="$1"
    local dev_mode_enabled
    dev_mode_enabled=$(get_developer_mode_status)
    local user_role
    user_role=$(get_user_role)
    
    case "$component" in
        "ucode")
            [[ "$dev_mode_enabled" == "true" && ("$user_role" == "wizard" || "$user_role" == "sorcerer") ]]
            ;;
        "utemplate")
            [[ "$dev_mode_enabled" == "true" && ("$user_role" == "wizard" || "$user_role" == "sorcerer") ]]
            ;;
        "uknowledge")
            # Always available to wizard/sorcerer, even without developer mode
            [[ "$user_role" == "wizard" || "$user_role" == "sorcerer" ]]
            ;;
        *)
            return 1
            ;;
    esac
}

# Show developer mode status
show_status() {
    echo "🔧 Developer Mode Status:"
    echo "======================="
    
    local dev_enabled
    dev_enabled=$(get_developer_mode_status)
    local user_role
    user_role=$(get_user_role)
    
    echo "User Role: $user_role"
    echo "Developer Mode: $dev_enabled"
    echo ""
    
    echo "📋 Current Permissions:"
    if can_edit "ucode"; then
        echo "✅ uCode editing: enabled"
    else
        echo "❌ uCode editing: disabled"
    fi
    
    if can_edit "utemplate"; then
        echo "✅ uTemplate editing: enabled"
    else
        echo "❌ uTemplate editing: disabled"
    fi
    
    if can_edit "uknowledge"; then
        echo "✅ uKnowledge editing: enabled"
    else
        echo "❌ uKnowledge editing: disabled"
    fi
}

# Command interface
case "${1:-}" in
    "enable")
        enable_developer_mode
        ;;
    "disable")
        disable_developer_mode
        ;;
    "status")
        show_status
        ;;
    "backup")
        backup_core_scripts
        ;;
    "list-backups")
        list_backups
        ;;
    "can-edit")
        if [[ -n "${2:-}" ]]; then
            if can_edit "$2"; then
                echo "true"
            else
                echo "false"
            fi
        else
            echo "Usage: developer-mode.sh can-edit <component>"
            exit 1
        fi
        ;;
    *)
        echo "uDOS Developer Mode Manager v1.0"
        echo "==============================="
        echo "Commands:"
        echo "  enable       - Enable developer mode (wizard/sorcerer only)"
        echo "  disable      - Disable developer mode"
        echo "  status       - Show current developer mode status"
        echo "  backup       - Create backup of core scripts"
        echo "  list-backups - List available script backups"
        echo "  can-edit <component> - Check edit permissions"
        echo ""
        echo "Developer Mode Features:"
        echo "  ✅ Limited backups of modified core scripts (ucode.sh)"
        echo "  ✅ Ability to modify uKnowledge folder"
        echo "  ✅ Full access to uTemplates"
        echo "  ✅ uCode script editing capabilities"
        echo ""
        echo "Wizard Mode (developer off):"
        echo "  ✅ Can still run all wizard functions"
        echo "  ❌ Cannot edit uCode or uTemplate"
        echo "  ✅ Always maintains uKnowledge read/write access"
        ;;
esac
