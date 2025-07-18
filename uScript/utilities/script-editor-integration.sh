#!/bin/bash
# uscript-editor-integration.sh - Advanced Script Editor Integration for uScript
# Specialized editors for script development with syntax highlighting and debugging
# Version: 2.0.0

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
UMEM="${UHOME}/uMemory"
SANDBOX="${UHOME}/sandbox"
USCRIPT="${UHOME}/uScript"

# Script editor configuration
SCRIPT_EDITOR_CONFIG="${UMEM}/config/script-editor-config.json"
SCRIPT_TEMPLATES_DIR="${USCRIPT}/templates"

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Initialize script editor integration
init_script_editor_integration() {
    bold "🔧 uScript Editor Integration v2.0.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Create required directories
    mkdir -p "${UMEM}/config" "${SANDBOX}/scripts" "${USCRIPT}/templates" "${USCRIPT}/utilities"
    
    # Initialize script editor configuration
    setup_script_editor_config
    
    # Setup script templates
    setup_script_templates
    
    # Setup development environment
    setup_dev_environment
    
    green "✅ Script editor integration initialized"
}

# Setup script editor configuration
setup_script_editor_config() {
    cyan "⚙️ Setting up script editor configuration..."
    
    cat > "$SCRIPT_EDITOR_CONFIG" << 'EOF'
{
  "script_editor_integration": {
    "version": "2.0.0",
    "script_types": [
      {
        "type": "bash",
        "extension": "sh",
        "template": "bash-script-template.sh",
        "editor_preference": "vim",
        "syntax_highlighting": true,
        "debugging": true,
        "features": ["shellcheck", "execution", "testing"]
      },
      {
        "type": "automation",
        "extension": "sh", 
        "template": "automation-script-template.sh",
        "editor_preference": "code",
        "syntax_highlighting": true,
        "debugging": true,
        "features": ["cron_integration", "logging", "error_handling"]
      },
      {
        "type": "utility",
        "extension": "sh",
        "template": "utility-script-template.sh", 
        "editor_preference": "micro",
        "syntax_highlighting": true,
        "debugging": false,
        "features": ["command_line_args", "help_text", "validation"]
      },
      {
        "type": "system",
        "extension": "sh",
        "template": "system-script-template.sh",
        "editor_preference": "vim",
        "syntax_highlighting": true,
        "debugging": true,
        "features": ["system_integration", "error_handling", "logging", "monitoring"]
      }
    ],
    "development_tools": {
      "syntax_checker": "shellcheck",
      "formatter": "shfmt",
      "debugger": "bash -x",
      "linter": "shellcheck",
      "test_runner": "bats"
    }
  }
}
EOF
    
    echo "  📄 Script editor configuration created: $SCRIPT_EDITOR_CONFIG"
}

# Setup script templates
setup_script_templates() {
    cyan "📋 Setting up script templates..."
    
    # Bash script template
    cat > "${SCRIPT_TEMPLATES_DIR}/bash-script-template.sh" << 'EOF'
#!/bin/bash
# {{SCRIPT_NAME}} - {{SCRIPT_DESCRIPTION}}
# Created: {{TIMESTAMP}}
# Author: {{USER}}
# Version: 1.0.0

set -euo pipefail

# Environment setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Main function
main() {
    bold "🚀 {{SCRIPT_NAME}} v1.0.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Your script logic here
    echo "Script is running..."
    
    green "✅ {{SCRIPT_NAME}} completed successfully"
}

# Execute main function
main "$@"
EOF
    
    # Automation script template
    cat > "${SCRIPT_TEMPLATES_DIR}/automation-script-template.sh" << 'EOF'
#!/bin/bash
# {{SCRIPT_NAME}} - {{SCRIPT_DESCRIPTION}}
# Automation script for uDOS system
# Created: {{TIMESTAMP}}
# Author: {{USER}}
# Version: 1.0.0

set -euo pipefail

# Environment setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
UMEM="${UHOME}/uMemory"
LOG_FILE="${UMEM}/logs/automation/{{SCRIPT_NAME}}.log"

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date -Iseconds)
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Error handling
error_handler() {
    local line_number="$1"
    log "ERROR" "Script failed at line $line_number"
    red "❌ Error on line $line_number"
    exit 1
}

trap 'error_handler $LINENO' ERR

# Main automation function
main() {
    log "INFO" "Starting {{SCRIPT_NAME}} automation"
    bold "🤖 {{SCRIPT_NAME}} Automation v1.0.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Your automation logic here
    cyan "🔄 Running automation tasks..."
    
    # Example automation tasks
    # check_system_status
    # process_data
    # generate_reports
    
    log "INFO" "{{SCRIPT_NAME}} automation completed successfully"
    green "✅ Automation completed"
}

# Execute main function
main "$@"
EOF
    
    # Utility script template
    cat > "${SCRIPT_TEMPLATES_DIR}/utility-script-template.sh" << 'EOF'
#!/bin/bash
# {{SCRIPT_NAME}} - {{SCRIPT_DESCRIPTION}}
# Utility script for uDOS system
# Created: {{TIMESTAMP}}
# Author: {{USER}}
# Version: 1.0.0

set -euo pipefail

# Script metadata
SCRIPT_NAME="{{SCRIPT_NAME}}"
SCRIPT_VERSION="1.0.0"
SCRIPT_DESCRIPTION="{{SCRIPT_DESCRIPTION}}"

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Show help
show_help() {
    bold "$SCRIPT_NAME v$SCRIPT_VERSION"
    echo
    echo "$SCRIPT_DESCRIPTION"
    echo
    echo "Usage: $0 [options] [arguments]"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --version  Show version information"
    echo "  -q, --quiet    Quiet mode"
    echo "  -d, --debug    Debug mode"
    echo
    echo "Examples:"
    echo "  $0 --help"
    echo "  $0 argument1 argument2"
    echo
}

# Main utility function
main() {
    local quiet=false
    local debug=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                echo "$SCRIPT_NAME v$SCRIPT_VERSION"
                exit 0
                ;;
            -q|--quiet)
                quiet=true
                shift
                ;;
            -d|--debug)
                debug=true
                set -x
                shift
                ;;
            -*)
                red "❌ Unknown option: $1"
                echo "Use '$0 --help' for usage information"
                exit 1
                ;;
            *)
                # Positional arguments
                break
                ;;
        esac
    done
    
    if [[ "$quiet" == "false" ]]; then
        bold "🔧 $SCRIPT_NAME v$SCRIPT_VERSION"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo
    fi
    
    # Your utility logic here
    cyan "🛠️ Running utility..."
    
    if [[ "$quiet" == "false" ]]; then
        green "✅ Utility completed"
    fi
}

# Execute main function
main "$@"
EOF
    
    echo "  📋 Script templates created in: $SCRIPT_TEMPLATES_DIR"
}

# Setup development environment
setup_dev_environment() {
    cyan "🛠️ Setting up development environment..."
    
    # Create development directories
    mkdir -p "${SANDBOX}/scripts/development" "${SANDBOX}/scripts/testing" "${SANDBOX}/scripts/utilities"
    
    # Create script development configuration
    cat > "${SANDBOX}/user-data/script-dev-config.json" << 'EOF'
{
  "development_preferences": {
    "auto_format": true,
    "syntax_check": true,
    "auto_backup": true,
    "test_on_save": false,
    "preferred_shell": "bash",
    "indentation": "2_spaces",
    "line_endings": "unix"
  },
  "project_structure": {
    "scripts_dir": "sandbox/scripts",
    "templates_dir": "uScript/templates", 
    "utilities_dir": "uScript/utilities",
    "tests_dir": "sandbox/scripts/testing"
  }
}
EOF
    
    echo "  🛠️ Development environment configured"
}

# Create new script from template
create_script() {
    local script_name="$1"
    local script_type="${2:-utility}"
    local description="${3:-uDOS script}"
    
    cyan "📝 Creating script: $script_name"
    
    # Determine output directory based on type
    local output_dir
    case "$script_type" in
        "automation")
            output_dir="${USCRIPT}/automation"
            ;;
        "utility")
            output_dir="${USCRIPT}/utilities"
            ;;
        "system")
            output_dir="${USCRIPT}/system"
            ;;
        "development")
            output_dir="${SANDBOX}/scripts/development"
            ;;
        *)
            output_dir="${SANDBOX}/scripts"
            ;;
    esac
    
    mkdir -p "$output_dir"
    
    local script_file="${output_dir}/${script_name}.sh"
    local template_file="${SCRIPT_TEMPLATES_DIR}/${script_type}-script-template.sh"
    
    # Check if template exists, fallback to utility template
    if [[ ! -f "$template_file" ]]; then
        template_file="${SCRIPT_TEMPLATES_DIR}/utility-script-template.sh"
    fi
    
    if [[ -f "$template_file" ]]; then
        # Process template variables
        local timestamp=$(date -Iseconds)
        local user=$(whoami)
        
        # Copy and process template
        sed -e "s/{{SCRIPT_NAME}}/$script_name/g" \
            -e "s/{{SCRIPT_DESCRIPTION}}/$description/g" \
            -e "s/{{TIMESTAMP}}/$timestamp/g" \
            -e "s/{{USER}}/$user/g" \
            "$template_file" > "$script_file"
        
        # Make script executable
        chmod +x "$script_file"
        
        # Log creation to uMemory
        log_script_creation "$script_file" "$script_type"
        
        echo "  📄 Script created: $script_file"
        echo "  🔧 Type: $script_type"
        echo "  📁 Location: $output_dir"
        
        # Open in editor
        edit_script "$script_file"
        
    else
        red "❌ Template not found: $template_file"
        return 1
    fi
}

# Edit script with appropriate editor
edit_script() {
    local script_file="$1"
    local editor="${2:-auto}"
    
    cyan "📝 Editing script: $(basename "$script_file")"
    
    # Select editor based on preferences
    if [[ "$editor" == "auto" ]]; then
        if command -v code >/dev/null 2>&1; then
            editor="code"
        elif command -v vim >/dev/null 2>&1; then
            editor="vim"
        elif command -v micro >/dev/null 2>&1; then
            editor="micro"
        else
            editor="nano"
        fi
    fi
    
    echo "  🔧 Using editor: $editor"
    
    # Log edit action
    log_script_edit "$script_file" "$editor"
    
    # Open in editor
    "$editor" "$script_file"
}

# Test script
test_script() {
    local script_file="$1"
    
    cyan "🧪 Testing script: $(basename "$script_file")"
    
    if [[ ! -f "$script_file" ]]; then
        red "❌ Script not found: $script_file"
        return 1
    fi
    
    # Syntax check with shellcheck if available
    if command -v shellcheck >/dev/null 2>&1; then
        echo "  🔍 Running shellcheck..."
        if shellcheck "$script_file"; then
            green "  ✅ Syntax check passed"
        else
            yellow "  ⚠️ Syntax check found issues"
        fi
    fi
    
    # Dry run check
    echo "  🏃 Running dry run..."
    if bash -n "$script_file"; then
        green "  ✅ Dry run passed"
    else
        red "  ❌ Dry run failed"
        return 1
    fi
    
    # Log test action
    log_script_test "$script_file"
    
    echo "  🧪 Script testing completed"
}

# Logging functions
log_script_creation() {
    local script_file="$1"
    local script_type="$2"
    local timestamp=$(date -Iseconds)
    
    local log_entry="{
        \"timestamp\": \"$timestamp\",
        \"action\": \"script_creation\",
        \"script\": \"$script_file\",
        \"type\": \"$script_type\",
        \"location\": \"$(pwd)\",
        \"user\": \"$(whoami)\"
    }"
    
    local log_file="${UMEM}/logs/script-development.jsonl"
    mkdir -p "$(dirname "$log_file")"
    echo "$log_entry" >> "$log_file"
}

log_script_edit() {
    local script_file="$1"
    local editor="$2"
    local timestamp=$(date -Iseconds)
    
    local log_entry="{
        \"timestamp\": \"$timestamp\",
        \"action\": \"script_edit\",
        \"script\": \"$script_file\",
        \"editor\": \"$editor\",
        \"location\": \"$(pwd)\",
        \"user\": \"$(whoami)\"
    }"
    
    local log_file="${UMEM}/logs/script-development.jsonl"
    mkdir -p "$(dirname "$log_file")"
    echo "$log_entry" >> "$log_file"
}

log_script_test() {
    local script_file="$1"
    local timestamp=$(date -Iseconds)
    
    local log_entry="{
        \"timestamp\": \"$timestamp\",
        \"action\": \"script_test\",
        \"script\": \"$script_file\",
        \"location\": \"$(pwd)\",
        \"user\": \"$(whoami)\"
    }"
    
    local log_file="${UMEM}/logs/script-development.jsonl"
    mkdir -p "$(dirname "$log_file")"
    echo "$log_entry" >> "$log_file"
}

# List recent scripts
list_recent_scripts() {
    bold "📂 Recent Script Development"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ -f "${UMEM}/logs/script-development.jsonl" ]]; then
        echo "Recent script activities:"
        tail -10 "${UMEM}/logs/script-development.jsonl" | while read -r line; do
            local action=$(echo "$line" | jq -r '.action')
            local script=$(echo "$line" | jq -r '.script')
            local timestamp=$(echo "$line" | jq -r '.timestamp')
            printf "  🔧 %-20s %-30s %s\n" "$action" "$(basename "$script")" "$timestamp"
        done
    else
        echo "  📭 No recent script activities found"
    fi
}

# Main execution
case "${1:-help}" in
    "init"|"setup")
        init_script_editor_integration
        ;;
    "create"|"new")
        if [[ $# -lt 2 ]]; then
            red "❌ Usage: $0 create <script_name> [type] [description]"
            exit 1
        fi
        init_script_editor_integration >/dev/null 2>&1
        create_script "$2" "${3:-utility}" "${4:-uDOS script}"
        ;;
    "edit"|"e")
        if [[ $# -lt 2 ]]; then
            red "❌ Usage: $0 edit <script_file> [editor]"
            exit 1
        fi
        edit_script "$2" "${3:-auto}"
        ;;
    "test"|"t")
        if [[ $# -lt 2 ]]; then
            red "❌ Usage: $0 test <script_file>"
            exit 1
        fi
        test_script "$2"
        ;;
    "list"|"recent"|"l")
        list_recent_scripts
        ;;
    "help"|"-h"|"--help")
        bold "🔧 uScript Editor Integration v2.0.0"
        echo
        echo "Usage: $0 [command] [options]"
        echo
        echo "Commands:"
        echo "  init                           Initialize script editor integration"
        echo "  create <name> [type] [desc]    Create new script from template"
        echo "  edit <script> [editor]         Edit script file"
        echo "  test <script>                  Test script syntax and dry run"
        echo "  list                           Show recent script activities"
        echo "  help                           Show this help"
        echo
        echo "Script Types:"
        echo "  utility      - General utility scripts (default)"
        echo "  automation   - Automation and scheduled scripts" 
        echo "  system       - System integration scripts"
        echo "  development  - Development and testing scripts"
        echo
        echo "Examples:"
        echo "  $0 create backup-tool automation 'Daily backup automation'"
        echo "  $0 edit backup-tool.sh vim"
        echo "  $0 test backup-tool.sh"
        echo
        ;;
    *)
        red "❌ Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
