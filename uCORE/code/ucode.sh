#!/bin/bash
# uDOS v1.3 - Modular Core System
# Minimal core that delegates to uSCRIPT modules and uMEMORY templates

set -uo pipefail

# ═══════════════════════════════════════════════════════════════════════
# CORE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
UCORE="$UDOS_ROOT/uCORE"
UMEMORY="$UDOS_ROOT/uMEMORY"
USCRIPT="$UDOS_ROOT/uSCRIPT"
SANDBOX="$UDOS_ROOT/sandbox"
WIZARD="$UDOS_ROOT/wizard"

# Version
VERSION="v1.3"

# Mode tracking
CURRENT_MODE="COMMAND"
export UDOS_MODE="$CURRENT_MODE"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_header() { echo -e "${BLUE}🌀 $1${NC}"; }

# ═══════════════════════════════════════════════════════════════════════
# MODULE LOADING SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Load uSCRIPT module
load_uscript_module() {
    local module_name="$1"
    local module_path="$USCRIPT/library/ucode/${module_name}.sh"
    
    if [[ -f "$module_path" && -x "$module_path" ]]; then
        source "$module_path"
        return 0
    else
        log_error "Module not found: $module_name"
        return 1
    fi
}

# Execute uSCRIPT command
execute_uscript() {
    local script_name="$1"
    shift
    local args="$@"
    
    local script_path="$USCRIPT/library/ucode/${script_name}.sh"
    
    if [[ -f "$script_path" && -x "$script_path" ]]; then
        "$script_path" $args
    else
        log_error "uSCRIPT not found: $script_name"
        return 1
    fi
}

# Load template from uMEMORY
load_template() {
    local template_name="$1"
    local template_path="$UMEMORY/templates/${template_name}"
    
    if [[ -f "$template_path" ]]; then
        cat "$template_path"
    else
        log_error "Template not found: $template_name"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# CORE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════

# Initialize directories
init_directories() {
    local dirs=("$UMEMORY" "$USCRIPT" "$SANDBOX" "$WIZARD")
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            log_warning "Creating missing directory: $dir"
            mkdir -p "$dir"
        fi
    done
}

# Initialize core modules
init_core_modules() {
    # Load essential modules from uSCRIPT
    local core_modules=(
        "startup"
        "authentication" 
        "validation"
        "display"
        "input"
    )
    
    for module in "${core_modules[@]}"; do
        if ! load_uscript_module "$module"; then
            log_warning "Core module missing: $module - creating stub"
            create_module_stub "$module"
        fi
    done
}

# Create module stub if missing
create_module_stub() {
    local module_name="$1"
    local module_path="$USCRIPT/library/ucode/${module_name}.sh"
    
    mkdir -p "$(dirname "$module_path")"
    
    cat > "$module_path" << EOF
#!/bin/bash
# uDOS $module_name Module - Auto-generated stub
# Move functionality from monolithic ucode.sh here

# Module: $module_name
# Purpose: Modular ${module_name} functionality
# Status: STUB - needs implementation

${module_name}_main() {
    echo "⚡ $module_name module called with args: \$@"
    echo "🔧 This is a stub - functionality needs to be moved from ucode.sh"
}

# Export main function
if [[ "\${BASH_SOURCE[0]}" == "\${0}" ]]; then
    ${module_name}_main "\$@"
fi
EOF
    
    chmod +x "$module_path"
    log_info "Created module stub: $module_name"
}

# ═══════════════════════════════════════════════════════════════════════
# COMMAND ROUTING SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Route command to appropriate module/script
route_command() {
    local command="$1"
    shift
    local args="$@"
    
    case "$command" in
        # Core system commands
        HELP|help)
            execute_uscript "help" $args
            ;;
        STATUS|status)
            execute_uscript "status" $args
            ;;
        DASH|dash|DASHBOARD|dashboard)
            execute_uscript "dashboard" $args
            ;;
        DISPLAY|display)
            execute_uscript "display" $args
            ;;
        
        # User management
        USER|user)
            execute_uscript "user" $args
            ;;
        SESSION|session)
            execute_uscript "session" $args
            ;;
        
        # Memory and data
        MEMORY|MEM|memory|mem)
            execute_uscript "memory" $args
            ;;
        UMEMORY|umemory)
            execute_uscript "umemory" $args
            ;;
        
        # Mission and project management
        MISSION|mission)
            execute_uscript "mission" $args
            ;;
        PACKAGE|PACK|package|pack)
            execute_uscript "package" $args
            ;;
        
        # Development tools
        DEV|dev)
            execute_uscript "dev" $args
            ;;
        LOG|log)
            execute_uscript "logging" $args
            ;;
        
        # System operations
        DESTROY|destroy)
            execute_uscript "destroy" $args
            ;;
        SETUP|setup)
            execute_uscript "setup" $args
            ;;
        
        # Layout and display
        LAYOUT|layout)
            execute_uscript "layout" $args
            ;;
        PANEL|panel)
            execute_uscript "layout" "grid" $args
            ;;
        SIZE|size|RESIZE|resize)
            execute_uscript "display" "resize" $args
            ;;
        ASCII|ascii)
            execute_uscript "ascii" $args
            ;;
        
        # Input and system
        INPUT|input)
            execute_uscript "input" $args
            ;;
        VALIDATE|validate)
            execute_uscript "validation" $args
            ;;
        
        # Editor modes
        MODE|mode)
            execute_uscript "mode" $args
            ;;
        EDIT|edit)
            execute_uscript "editor" $args
            ;;
        NEW|new)
            execute_uscript "editor" "new" $args
            ;;
        
        # Input and shortcuts
        SHORTCUTS|shortcuts|GO|go)
            execute_uscript "shortcuts" $args
            ;;
        HISTORY|history)
            execute_uscript "history" $args
            ;;
        FAVORITES|favorites)
            execute_uscript "favorites" $args
            ;;
        
        # Character and input systems
        CHAR|char)
            execute_uscript "character" $args
            ;;
        INPUT|input)
            execute_uscript "input" $args
            ;;
        
        # Git and SSH operations
        GIT|git)
            execute_uscript "git" $args
            ;;
        REMOTE|remote)
            execute_uscript "git" "remote" $args
            ;;
        SSH-KEY|ssh-key|SSHKEY|sshkey)
            execute_uscript "ssh" $args
            ;;
        
        # System information
        TREE|tree)
            execute_uscript "tree" $args
            ;;
        
        # Backup system
        BACKUP|backup)
            handle_backup
            ;;
        
        # System control
        RESTART|restart|REBOOT|reboot|RELOAD|reload)
            handle_restart "$command"
            ;;
        RESET|reset|REFRESH|refresh)
            handle_reset
            ;;
        EXIT|exit|QUIT|quit|BYE|bye)
            handle_exit
            ;;
        
        # History recall
        !*)
            execute_uscript "history" "recall" "$command"
            ;;
        
        # Shortcode browser
        "[")
            execute_uscript "shortcuts" "browse"
            ;;
        
        # Shortcode execution
        "["*"]")
            execute_uscript "shortcuts" "execute" "$command"
            ;;
        
        *)
            log_error "Unknown command: $command"
            echo "Type 'HELP' for available commands or '[' for shortcode browser"
            return 1
            ;;
    esac
}

# ═══════════════════════════════════════════════════════════════════════
# SYSTEM CONTROL FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Handle restart with session logging
handle_restart() {
    local restart_type="$1"
    
    # Create session log
    local session_logger="$UCORE/code/session-logger.sh"
    if [[ -x "$session_logger" ]]; then
        case "$restart_type" in
            REBOOT|reboot)
                "$session_logger" reboot >/dev/null 2>&1
                ;;
            *)
                "$session_logger" restart >/dev/null 2>&1
                ;;
        esac
    fi
    
    log_info "Restarting uDOS session..."
    clear
    exec "$UCORE/code/startup.sh"
}

# Handle reset
handle_reset() {
    log_info "Refreshing uDOS interface..."
    clear
}

# Handle manual backup
handle_backup() {
    log_info "Running smart backup manually..."
    
    local smart_backup_script="$UCORE/code/smart-backup.sh"
    if [[ -x "$smart_backup_script" ]]; then
        "$smart_backup_script"
    else
        log_error "Smart backup script not found or not executable"
    fi
}

# Handle exit with backup and session logging
handle_exit() {
    log_info "Running smart backup before restart..."
    
    # Run smart backup if available
    local smart_backup_script="$UCORE/code/smart-backup.sh"
    if [[ -x "$smart_backup_script" ]]; then
        "$smart_backup_script" >/dev/null 2>&1 &
        sleep 1
        log_success "Smart backup initiated"
    fi
    
    # Create session log
    local session_logger="$UCORE/code/session-logger.sh"
    if [[ -x "$session_logger" ]]; then
        "$session_logger" restart >/dev/null 2>&1
    fi
    
    log_success "Restarting uDOS... 🚀"
    clear
    exec "$UCORE/code/startup.sh"
}

# ═══════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════

# Initialize system
init_system() {
    # Set development mode for better UX
    export UDOS_DEV_MODE=true
    
    # Initialize directories
    init_directories
    
    # Initialize core modules
    init_core_modules
    
    # Show startup banner
    execute_uscript "display" "banner"
    
    # Authenticate user
    local auth_script="$UCORE/code/user-auth.sh"
    if [[ -x "$auth_script" ]]; then
        if ! "$auth_script" auth; then
            log_error "Authentication failed"
            return 1
        fi
    fi
    
    # Validate system
    execute_uscript "validation" "system"
}

# Main interactive loop
main_loop() {
    log_header "System ready - Welcome to uDOS!"
    echo -e "${CYAN}💡 Smart Input Features:${NC}"
    echo -e "  • Type [ to browse shortcodes"
    echo -e "  • Use Tab for autocomplete"
    echo -e "  • Arrow keys to navigate suggestions"
    echo -e "  • Type GO for full reference"
    echo -e "  • Type EXIT to quit"
    echo ""
    
    while true; do
        # Show mode indicator
        echo -ne "${BLUE}🌀 ${NC}"
        
        # Read input
        read -r input || {
            echo ""
            log_info "Input interrupted"
            break
        }
        
        # Skip empty input
        [[ -z "$input" ]] && continue
        
        # Parse command and arguments
        local cmd=$(echo "$input" | awk '{print $1}')
        local args=""
        if [[ "$input" == *" "* ]]; then
            args=$(echo "$input" | cut -d' ' -f2-)
        fi
        
        # Route command
        route_command "$cmd" $args
    done
}

# Main function
main() {
    # Check for arguments
    if [[ $# -eq 0 ]]; then
        # Interactive mode
        if ! init_system; then
            log_error "System initialization failed"
            return 1
        fi
        
        main_loop
    else
        # Command line mode
        route_command "$@"
    fi
}

# Run main function
main "$@"
