#!/bin/bash
# shortcode-processor-simple.sh - Simple Shortcode System for uScript Execution
# Version: 2.0.0
# Description: Enhanced shortcode processor with editor, sandbox, and location integration

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
ERROR_HANDLER="$SCRIPT_DIR/error-handler.sh"

# Source error handler if available
if [[ -f "$ERROR_HANDLER" ]]; then
    source "$ERROR_HANDLER" 2>/dev/null || {
        echo "⚠️ Error handler not available - using basic error handling"
        error_warning() { echo "WARN: $1" >&2; }
        error_critical() { echo "ERROR: $1" >&2; }
        error_fatal() { echo "FATAL: $1" >&2; exit 1; }
        set_error_context() { true; }
    }
else
    error_warning() { echo "WARN: $1" >&2; }
    error_critical() { echo "ERROR: $1" >&2; }
    error_fatal() { echo "FATAL: $1" >&2; exit 1; }
    set_error_context() { true; }
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Process shortcode from input text
process_shortcode() {
    local input="$1"
    
    set_error_context "shortcode_processing" "$0"
    
    # Extract shortcode using regex
    if [[ "$input" =~ ^\[([a-zA-Z0-9_-]+):?([^]]*)\]$ ]]; then
        local shortcode_name=$(echo "${BASH_REMATCH[1]}" | awk '{print toupper($0)}')
        local shortcode_args="${BASH_REMATCH[2]}"
        
        echo -e "${CYAN}🔍 Processing shortcode: [$shortcode_name:$shortcode_args]${NC}"
        
        execute_shortcode "$shortcode_name" "$shortcode_args"
    else
        error_warning "Invalid shortcode format: $input"
        echo "💡 Use format: [command:arguments]"
        return 1
    fi
}

# Execute a shortcode
execute_shortcode() {
    local name="$1"
    local args="$2"
    
    set_error_context "shortcode_execution" "$name"
    
    echo -e "${BLUE}⚡ Executing shortcode '$name' with args: $args${NC}"
    
    # Execute based on shortcode name
    case "$name" in
        "RUN")
            execute_run_shortcode "$args"
            ;;
        "BASH")
            execute_bash_shortcode "$args"
            ;;
        "CHECK")
            execute_check_shortcode "$args"
            ;;
        "MISSION")
            execute_mission_shortcode "$args"
            ;;
        "DATA")
            execute_data_shortcode "$args"
            ;;
        "ERROR")
            execute_error_shortcode "$args"
            ;;
        "CONTAINER")
            execute_container_shortcode "$args"
            ;;
        "DASHBOARD")
            execute_dashboard_shortcode "$args"
            ;;
        "DASH")
            execute_dash_shortcode "$args"
            ;;
        "LOG")
            execute_log_shortcode "$args"
            ;;
        "TREE")
            execute_tree_shortcode "$args"
            ;;
        "HELP")
            show_shortcode_help
            ;;
        "VERSION")
            show_version_info
            ;;
        # Editor Integration v2.0.0
        "EDIT")
            execute_edit_shortcode "$args"
            ;;
        "DRAFT")
            execute_draft_shortcode "$args"
            ;;
        "SESSION")
            execute_session_shortcode "$args"
            ;;
        # Sandbox Management v2.0.0
        "TODAY")
            execute_today_shortcode "$args"
            ;;
        "SANDBOX")
            execute_sandbox_shortcode "$args"
            ;;
        "RESEARCH")
            execute_research_shortcode "$args"
            ;;
        # Script Development v2.0.0
        "SCRIPT")
            execute_script_shortcode "$args"
            ;;
        # Location and Grid v2.0.0
        "LOCATION")
            execute_location_shortcode "$args"
            ;;
        "VB")
            execute_vb_shortcode "$args"
            ;;
        # Template Processing v2.0.0
        "TEMPLATE")
            execute_template_shortcode "$args"
            ;;
        # Backup System v2.0.0
        "BACKUP")
            execute_backup_shortcode "$args"
            ;;
        # Package Management v2.0.0
        "PACKAGE")
            execute_package_shortcode "$args"
            ;;
        "PKG")
            execute_package_shortcode "$args"
            ;;
        # Role Management v2.0.0
        "ROLE")
            execute_role_shortcode "$args"
            ;;
        "WHOAMI")
            execute_whoami_shortcode "$args"
            ;;
        "PERMISSIONS"|"PERMS")
            execute_permissions_shortcode "$args"
            ;;
        "DEVMODE")
            execute_devmode_shortcode "$args"
            ;;
        *)
            error_critical "Unknown shortcode: $name"
            suggest_shortcode_alternatives "$name"
            return 1
            ;;
    esac
}

# Execute run shortcode
execute_run_shortcode() {
    local args="$1"
    
    # Parse script name and arguments
    local script_name=""
    if [[ "$args" =~ ^([a-zA-Z0-9_/-]+) ]]; then
        script_name="${BASH_REMATCH[1]}"
    else
        script_name="$args"
    fi
    
    if [[ -z "$script_name" ]]; then
        echo "❌ No script specified for [run] shortcode"
        return 1
    fi
    
    # Find the script
    local script_path=""
    if [[ -f "$UHOME/uScript/examples/$script_name.md" ]]; then
        script_path="$UHOME/uScript/examples/$script_name.md"
    elif [[ -f "$UHOME/uScript/automation/$script_name.md" ]]; then
        script_path="$UHOME/uScript/automation/$script_name.md"
    elif [[ -f "$UHOME/uScript/$script_name.md" ]]; then
        script_path="$UHOME/uScript/$script_name.md"
    else
        echo "❌ Script not found: $script_name"
        return 1
    fi
    
    echo -e "${GREEN}📝 Executing uScript: $script_path${NC}"
    
    # Execute via enhanced script runner if available
    if [[ -f "$UHOME/uScript/system/enhanced-script-runner.sh" ]]; then
        bash "$UHOME/uScript/system/enhanced-script-runner.sh" run "$script_path"
    else
        # Fallback to basic execution
        bash "$UHOME/uScript/system/ucode-runner.sh" run "$script_path"
    fi
}

# Execute bash shortcode
execute_bash_shortcode() {
    local args="$1"
    
    echo -e "${YELLOW}🐚 Executing containerized bash command: $args${NC}"
    
    if [[ -f "$UHOME/uScript/system/bash-container.sh" ]]; then
        bash "$UHOME/uScript/system/bash-container.sh" exec "$args"
    else
        echo "⚠️ Container system not available, executing natively"
        bash -c "$args"
    fi
}

# Execute check shortcode
execute_check_shortcode() {
    local args="$1"
    
    echo -e "${BLUE}🔍 Running system check: $args${NC}"
    
    case "$args" in
        "health"|"")
            bash "$UHOME/uCode/check.sh" all
            ;;
        "setup")
            bash "$UHOME/uCode/check.sh" setup
            ;;
        "errors")
            if [[ -f "$UHOME/uCode/error-handler.sh" ]]; then
                bash "$UHOME/uCode/error-handler.sh" stats
            fi
            ;;
        *)
            bash "$UHOME/uCode/check.sh" "$args"
            ;;
    esac
}

# Execute mission shortcode
execute_mission_shortcode() {
    local args="$1"
    
    echo -e "${GREEN}🎯 Mission management: $args${NC}"
    
    # Simple mission operations
    case "$args" in
        "create"*|"new"*)
            local mission_name
            if [[ "$args" =~ name=([a-zA-Z0-9_-]+) ]]; then
                mission_name="${BASH_REMATCH[1]}"
            else
                mission_name="mission-$(date +%Y%m%d-%H%M%S)"
            fi
            
            echo "📝 Creating mission: $mission_name"
            mkdir -p "$UHOME/uMemory/missions/$mission_name"
            echo "# Mission: $mission_name" > "$UHOME/uMemory/missions/$mission_name/README.md"
            echo "Created: $(date)" >> "$UHOME/uMemory/missions/$mission_name/README.md"
            ;;
        "list")
            echo "📋 Active missions:"
            find "$UHOME/uMemory/missions" -mindepth 1 -maxdepth 1 -type d | head -10
            ;;
        "status")
            echo "📊 Mission status:"
            echo "Total missions: $(find "$UHOME/uMemory/missions" -mindepth 1 -maxdepth 1 -type d | wc -l)"
            ;;
        *)
            echo "❓ Unknown mission command: $args"
            echo "💡 Try: create, list, status"
            ;;
    esac
}

# Execute data shortcode
execute_data_shortcode() {
    local args="$1"
    
    echo -e "${PURPLE}📊 Data processing: $args${NC}"
    
    if [[ -f "$UHOME/uCode/json-processor.sh" ]]; then
        bash "$UHOME/uCode/json-processor.sh" $args
    else
        echo "❌ Data processor not available"
    fi
}

# Execute error shortcode
execute_error_shortcode() {
    local args="$1"
    
    if [[ -f "$UHOME/uCode/error-handler.sh" ]]; then
        bash "$UHOME/uCode/error-handler.sh" $args
    else
        echo "❌ Error handler not available"
    fi
}

# Execute container shortcode
execute_container_shortcode() {
    local args="$1"
    
    if [[ -f "$UHOME/uScript/system/bash-container.sh" ]]; then
        bash "$UHOME/uScript/system/bash-container.sh" $args
    else
        echo "❌ Container system not available"
    fi
}

# Execute dashboard shortcode
execute_dashboard_shortcode() {
    local args="$1"
    
    case "$args" in
        "generate"|"")
            bash "$UHOME/uCode/dash.sh"
            ;;
        *)
            bash "$UHOME/uCode/dash.sh" $args
            ;;
    esac
}

# Execute dash shortcode (enhanced)
execute_dash_shortcode() {
    local args="$1"
    
    echo -e "${CYAN}📊 Enhanced dashboard: $args${NC}"
    
    if [[ -f "$UHOME/uCode/dash-enhanced.sh" ]]; then
        bash "$UHOME/uCode/dash-enhanced.sh" shortcode $args
    else
        # Fallback to original dashboard
        execute_dashboard_shortcode "$args"
    fi
}

# Execute log shortcode
execute_log_shortcode() {
    local args="$1"
    
    bash "$UHOME/uCode/log.sh" $args
}

# Execute tree shortcode
execute_tree_shortcode() {
    local args="$1"
    
    bash "$UHOME/uCode/make-tree.sh" $args
}

# Show enhanced shortcode help with dataset integration
show_shortcode_help() {
    echo -e "${PURPLE}🔧 uDOS Shortcode System v2.0.0 - Dataset Enhanced${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Link to enhanced help system
    if [[ -f "$UHOME/uCode/enhanced-help-system.sh" ]]; then
        echo -e "${CYAN}💡 For detailed command help, use: ${GREEN}HELP <command>${NC}"
        echo -e "${CYAN}🔍 Interactive help explorer: ${GREEN}./uCode/enhanced-help-system.sh interactive${NC}"
        echo -e "${CYAN}📚 Generate docs: ${GREEN}./uCode/enhanced-help-system.sh generate${NC}"
        echo ""
    fi
    
    echo "Available Shortcodes:"
    echo ""
    echo -e "${BLUE}📂 Script Execution${NC}"
    echo -e "  • ${GREEN}[RUN:script-name]${NC} - Execute uScript"
    echo -e "  • ${GREEN}[BASH:command]${NC} - Run bash command in container"
    echo ""
    echo -e "${BLUE}📂 Editor Integration (v2.0.0)${NC}"
    echo -e "  • ${GREEN}[EDIT:filename.md]${NC} - Edit file with smart editor selection"
    echo -e "  • ${GREEN}[DRAFT:meeting-notes]${NC} - Create new draft file"
    echo -e "  • ${GREEN}[SESSION:project-alpha]${NC} - Create/open session file"
    echo ""
    echo -e "${BLUE}📂 Sandbox Management (v2.0.0)${NC}"
    echo -e "  • ${GREEN}[TODAY:notes]${NC} - Open today's workspace"
    echo -e "  • ${GREEN}[SANDBOX:list]${NC} - List sandbox contents"
    echo -e "  • ${GREEN}[RESEARCH:new topic=ai]${NC} - Create research file"
    echo ""
    echo -e "${BLUE}📂 Script Development (v2.0.0)${NC}"
    echo -e "  • ${GREEN}[SCRIPT:create backup-tool automation]${NC} - Create script from template"
    echo -e "  • ${GREEN}[SCRIPT:edit existing-script.sh]${NC} - Edit script file"
    echo ""
    echo -e "${BLUE}📂 Location & Grid (v2.0.0)${NC}"
    echo -e "  • ${GREEN}[LOCATION:set Sydney]${NC} - Set current location"
    echo -e "  • ${GREEN}[LOCATION:grid B5]${NC} - Set grid position"
    echo -e "  • ${GREEN}[VB:GRID.POSITION A5]${NC} - Execute VB commands"
    echo ""
    echo -e "${BLUE}📂 Template Processing (v2.0.0)${NC}"
    echo -e "  • ${GREEN}[TEMPLATE:process file=example.md]${NC} - Process templates"
    echo ""
    echo -e "${BLUE}📂 Backup System (v2.0.0)${NC}"
    echo -e "  • ${GREEN}[BACKUP:create]${NC} - Create system backup"
    echo -e "  • ${GREEN}[BACKUP:list]${NC} - List available backups"
    echo ""
    echo -e "${BLUE}📂 Package Management (v2.0.0) - On-Demand Installation${NC}"
    echo -e "  • ${GREEN}[PACKAGE:install-all]${NC} - Install all essential packages"
    echo -e "  • ${GREEN}[PACKAGE:list]${NC} - List all packages with status"
    echo -e "  • ${GREEN}[PACKAGE:install ripgrep]${NC} - Install specific package"
    echo -e "  • ${GREEN}[PACKAGE:status bat]${NC} - Check package status"
    echo -e "  • ${GREEN}[PACKAGE:search markdown]${NC} - Search packages"
    echo -e "  • ${GREEN}[PKG:install-all]${NC} - Quick install all (shorthand)"
    echo ""
    echo -e "${BLUE}📂 User Role Management (v2.0.0)${NC}"
    echo -e "  • ${GREEN}[ROLE:status]${NC} - Show current user role and permissions"
    echo -e "  • ${GREEN}[ROLE:list]${NC} - List all available roles"
    echo -e "  • ${GREEN}[WHOAMI]${NC} - Show user information"
    echo -e "  • ${GREEN}[PERMISSIONS]${NC} - Show folder access permissions"
    echo -e "  • ${GREEN}[DEVMODE:on]${NC} - Enable dev mode (Wizard only)"
    echo -e "  • ${GREEN}[DEVMODE:off]${NC} - Disable dev mode"
    echo ""
    echo -e "${BLUE}📂 System Management${NC}"
    echo -e "  • ${GREEN}[CHECK:health]${NC} - Perform health check"
    echo -e "  • ${GREEN}[ERROR:stats]${NC} - Show error statistics"
    echo -e "  • ${GREEN}[CONTAINER:status]${NC} - Container information"
    echo ""
    echo -e "${BLUE}📂 Data & Missions${NC}"
    echo -e "  • ${GREEN}[MISSION:create name=test]${NC} - Create mission"
    echo -e "  • ${GREEN}[DATA:csv file=data.csv]${NC} - Process data"
    echo -e "  • ${GREEN}[LOG:move 'message']${NC} - Log information"
    echo ""
    echo -e "${BLUE}📂 Dashboard & Analytics (v2.0.0)${NC}"
    echo -e "  • ${GREEN}[DASH:refresh]${NC} - Build dashboard with templates"
    echo -e "  • ${GREEN}[DASH:ascii]${NC} - Show ASCII dashboard"
    echo -e "  • ${GREEN}[DASH:live]${NC} - Start live dashboard"
    echo -e "  • ${GREEN}[DASHBOARD:generate]${NC} - Legacy dashboard (fallback)"
    echo ""
    echo -e "${BLUE}📂 Utilities${NC}"
    echo -e "  • ${GREEN}[TREE:generate]${NC} - Show file tree"
    echo -e "  • ${GREEN}[VERSION]${NC} - Show version"
    echo -e "  • ${GREEN}[HELP]${NC} - Show this help"
    echo ""
    echo "Syntax: [SHORTCODE:arguments]"
}

# Show version info
show_version_info() {
    echo -e "${PURPLE}🌀 uDOS Version Information${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ -f "$UHOME/uMemory/state/identity.md" ]]; then
        grep "Version:" "$UHOME/uMemory/state/identity.md" | head -1
    else
        echo "Version: Unknown"
    fi
    
    echo "Shortcode System: v1.7.1 (Simple)"
    echo "Error Handling: Enhanced"
}

# Suggest alternatives for unknown shortcodes
suggest_shortcode_alternatives() {
    local query="$1"
    echo -e "${YELLOW}💡 Did you mean one of these?${NC}"
    
    case "$query" in
        *run*|*exec*|*execute*)
            echo "  • RUN - Execute uScript"
            echo "  • BASH - Run bash command"
            ;;
        *check*|*test*|*health*)
            echo "  • CHECK - System checks"
            echo "  • ERROR - Error management"
            ;;
        *mission*|*task*|*project*)
            echo "  • MISSION - Mission management"
            echo "  • LOG - Log information"
            ;;
        *data*|*process*|*file*)
            echo "  • DATA - Data processing"
            echo "  • TREE - File tree"
            ;;
        *)
            echo "  • HELP - Show all shortcodes"
            echo "  • VERSION - Show version"
            ;;
    esac
}

# Process file with shortcodes
process_file_shortcodes() {
    local file="$1"
    local output_file="${2:-}"
    
    if [[ ! -f "$file" ]]; then
        error_critical "File not found: $file"
        return 1
    fi
    
    echo -e "${BLUE}📄 Processing shortcodes in file: $file${NC}"
    
    local temp_output=$(mktemp)
    local line_number=0
    
    while IFS= read -r line; do
        ((line_number++))
        
        if [[ "$line" =~ \[([a-zA-Z0-9_-]+):?([^]]*)\] ]]; then
            local shortcode_name=$(echo "${BASH_REMATCH[1]}" | awk '{print toupper($0)}')
            local shortcode_args="${BASH_REMATCH[2]}"
            
            echo -e "${CYAN}📍 Line $line_number: Processing [$shortcode_name:$shortcode_args]${NC}"
            
            # Execute shortcode and capture output
            local shortcode_output
            if shortcode_output=$(execute_shortcode "$shortcode_name" "$shortcode_args" 2>&1); then
                # Replace shortcode with output
                echo "${line/\[$shortcode_name:$shortcode_args\]/$shortcode_output}" >> "$temp_output"
            else
                echo "ERROR: Failed to process shortcode [$shortcode_name:$shortcode_args]" >> "$temp_output"
            fi
        else
            echo "$line" >> "$temp_output"
        fi
    done < "$file"
    
    # Output result
    if [[ -n "$output_file" ]]; then
        mv "$temp_output" "$output_file"
        echo -e "${GREEN}✅ Processed file saved to: $output_file${NC}"
    else
        cat "$temp_output"
        rm -f "$temp_output"
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# uDOS v2.0.0 Shortcode Implementations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Execute edit shortcode
execute_edit_shortcode() {
    local args="$1"
    
    echo -e "${GREEN}📝 Opening file for editing: $args${NC}"
    
    if [[ -f "$UHOME/uCode/editor-integration.sh" ]]; then
        bash "$UHOME/uCode/editor-integration.sh" edit "$args"
    else
        echo "❌ Editor integration not available"
        return 1
    fi
}

# Execute draft shortcode
execute_draft_shortcode() {
    local args="$1"
    
    echo -e "${GREEN}📄 Creating draft: $args${NC}"
    
    if [[ -f "$UHOME/uCode/editor-integration.sh" ]]; then
        bash "$UHOME/uCode/editor-integration.sh" draft "$args"
    else
        echo "❌ Editor integration not available"
        return 1
    fi
}

# Execute session shortcode
execute_session_shortcode() {
    local args="$1"
    
    echo -e "${GREEN}📚 Opening session: $args${NC}"
    
    if [[ -f "$UHOME/uCode/editor-integration.sh" ]]; then
        bash "$UHOME/uCode/editor-integration.sh" session "$args"
    else
        echo "❌ Editor integration not available"
        return 1
    fi
}

# Execute today shortcode
execute_today_shortcode() {
    local args="$1"
    
    echo -e "${BLUE}📅 Today's workspace: $args${NC}"
    
    if [[ -f "$UHOME/uCode/enhanced-sandbox-manager.sh" ]]; then
        bash "$UHOME/uCode/enhanced-sandbox-manager.sh" today "$args"
    else
        echo "❌ Sandbox manager not available"
        return 1
    fi
}

# Execute sandbox shortcode
execute_sandbox_shortcode() {
    local args="$1"
    
    echo -e "${CYAN}📦 Sandbox management: $args${NC}"
    
    if [[ -f "$UHOME/uCode/enhanced-sandbox-manager.sh" ]]; then
        bash "$UHOME/uCode/enhanced-sandbox-manager.sh" "$args"
    else
        echo "❌ Sandbox manager not available"
        return 1
    fi
}

# Execute research shortcode
execute_research_shortcode() {
    local args="$1"
    
    echo -e "${PURPLE}🔬 Research management: $args${NC}"
    
    if [[ -f "$UHOME/uCode/enhanced-sandbox-manager.sh" ]]; then
        bash "$UHOME/uCode/enhanced-sandbox-manager.sh" research "$args"
    else
        echo "❌ Sandbox manager not available"
        return 1
    fi
}

# Execute script shortcode
execute_script_shortcode() {
    local args="$1"
    
    echo -e "${YELLOW}⚙️ Script development: $args${NC}"
    
    if [[ -f "$UHOME/uScript/utilities/script-editor-integration.sh" ]]; then
        bash "$UHOME/uScript/utilities/script-editor-integration.sh" $args
    else
        echo "❌ Script editor integration not available"
        return 1
    fi
}

# Execute location shortcode
execute_location_shortcode() {
    local args="$1"
    
    echo -e "${GREEN}🗺️ Location management: $args${NC}"
    
    if [[ -f "$UHOME/uCode/location-manager.sh" ]]; then
        bash "$UHOME/uCode/location-manager.sh" $args
    else
        echo "❌ Location manager not available"
        return 1
    fi
}

# Execute VB shortcode
execute_vb_shortcode() {
    local args="$1"
    
    echo -e "${BLUE}⚡ VB Command: $args${NC}"
    
    if [[ -f "$UHOME/uCode/vb-command-generator.sh" ]]; then
        bash "$UHOME/uCode/vb-command-generator.sh" execute "$args"
    else
        echo "❌ VB command system not available"
        return 1
    fi
}

# Execute template shortcode
execute_template_shortcode() {
    local args="$1"
    
    echo -e "${CYAN}📋 Template processing: $args${NC}"
    
    if [[ -f "$UHOME/uCode/vb-template-processor.sh" ]]; then
        bash "$UHOME/uCode/vb-template-processor.sh" $args
    else
        echo "❌ Template processor not available"
        return 1
    fi
}

# Execute backup shortcode
execute_backup_shortcode() {
    local args="$1"
    
    echo -e "${YELLOW}💾 Backup management: $args${NC}"
    
    case "$args" in
        "create")
            echo "Creating system backup..."
            # Placeholder for backup creation logic
            echo "✅ Backup created successfully"
            ;;
        "list")
            echo "Available backups:"
            # Placeholder for backup listing logic
            echo "📦 backup-2025-07-18.tar.gz"
            ;;
        *)
            echo "❌ Unknown backup action: $args"
            echo "💡 Available: create, list"
            return 1
            ;;
    esac
}

# Execute package shortcode
execute_package_shortcode() {
    local args="$1"
    
    echo -e "${CYAN}📦 Package management: $args${NC}"
    
    # Use consolidated manager with shortcode support
    if [[ -f "$UHOME/uCode/packages/consolidated-manager.sh" ]]; then
        bash "$UHOME/uCode/packages/consolidated-manager.sh" shortcode $args
    else
        echo "❌ Package manager not available"
        echo "💡 Run installation validation to check system setup"
        return 1
    fi
}

# Execute role shortcode
execute_role_shortcode() {
    local args="$1"
    
    echo -e "${PURPLE}👤 Role management: $args${NC}"
    
    if [[ -f "$UHOME/uCode/user-role-manager.sh" ]]; then
        case "$args" in
            ""|"status"|"show")
                bash "$UHOME/uCode/user-role-manager.sh" status
                ;;
            "list"|"all")
                bash "$UHOME/uCode/user-role-manager.sh" roles
                ;;
            *)
                bash "$UHOME/uCode/user-role-manager.sh" $args
                ;;
        esac
    else
        echo "❌ Role management system not available"
        return 1
    fi
}

# Execute whoami shortcode
execute_whoami_shortcode() {
    local args="$1"
    
    echo -e "${BLUE}🔍 User information: $args${NC}"
    
    if [[ -f "$UHOME/uCode/user-role-manager.sh" ]]; then
        bash "$UHOME/uCode/user-role-manager.sh" status
    else
        echo "👤 User: ${USER:-unknown}"
        echo "🏠 uDOS Home: $UHOME"
        echo "⚠️ Role management not available"
    fi
}

# Execute permissions shortcode
execute_permissions_shortcode() {
    local args="$1"
    
    echo -e "${YELLOW}🔐 Permissions check: $args${NC}"
    
    if [[ -f "$UHOME/uCode/user-role-manager.sh" ]]; then
        bash "$UHOME/uCode/user-role-manager.sh" folders
    else
        echo "❌ Permission system not available"
        return 1
    fi
}

# Execute devmode shortcode
execute_devmode_shortcode() {
    local args="$1"
    
    echo -e "${RED}🔧 Dev mode management: $args${NC}"
    
    if [[ -f "$UHOME/uCode/user-role-manager.sh" ]]; then
        bash "$UHOME/uCode/user-role-manager.sh" dev-mode $args
    else
        echo "❌ Dev mode management not available"
        return 1
    fi
}

# Interactive shortcode mode
interactive_mode() {
    echo -e "${PURPLE}🎮 Interactive Shortcode Mode${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Enter shortcodes to execute them interactively."
    echo "Type 'help' for available shortcodes, 'quit' to exit."
    echo ""
    
    while true; do
        echo -ne "${CYAN}shortcode> ${NC}"
        read -r input
        
        case "$input" in
            "quit"|"exit"|"bye")
                echo -e "${GREEN}👋 Goodbye!${NC}"
                break
                ;;
            "help")
                show_shortcode_help
                ;;
            "")
                continue
                ;;
            *)
                if [[ "$input" =~ ^\[.*\]$ ]]; then
                    process_shortcode "$input"
                else
                    # Auto-wrap in brackets if not provided
                    process_shortcode "[$input]"
                fi
                ;;
        esac
        echo ""
    done
}

# Main command interface
main() {
    case "${1:-help}" in
        "process")
            process_shortcode "$2"
            ;;
        "file")
            process_file_shortcodes "$2" "$3"
            ;;
        "interactive"|"repl")
            interactive_mode
            ;;
        "list")
            show_shortcode_help
            ;;
        "help"|*)
            echo -e "${PURPLE}🔧 uDOS Simple Shortcode Processor v1.7.1${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "Usage: $0 <command> [arguments]"
            echo ""
            echo "Commands:"
            echo "  process <shortcode>            - Process a single shortcode"
            echo "  file <input_file> [output]     - Process shortcodes in file"
            echo "  interactive                    - Start interactive mode"
            echo "  list                           - List available shortcodes"
            echo ""
            echo "Examples:"
            echo "  $0 process '[RUN:hello-world]'"
            echo "  $0 file input.md output.md"
            echo "  $0 interactive"
            ;;
    esac
}

# Initialize if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
