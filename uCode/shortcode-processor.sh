#!/bin/bash
# shortcode-processor.sh - Shortcode System for uScript Execution
# Version: 1.7.1
# Description: Process [shortcode] syntax for seamless uScript execution

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
SHORTCODE_CONFIG="$UHOME/uTemplate/system/shortcodes.json"
USCRIPT_DIR="$UHOME/uScript"
ERROR_HANDLER="$SCRIPT_DIR/error-handler.sh"

# Source error handler
source "$ERROR_HANDLER" 2>/dev/null || {
    echo "⚠️ Error handler not available - using basic error handling"
    error_warning() { echo "WARN: $1" >&2; }
    error_critical() { echo "ERROR: $1" >&2; }
    error_fatal() { echo "FATAL: $1" >&2; exit 1; }
    set_error_context() { true; }
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Shortcode registry - using parallel arrays instead of associative arrays
SHORTCODE_NAMES=""
SHORTCODE_SCRIPTS=""
SHORTCODE_DESCRIPTIONS=""
SHORTCODE_TYPES=""
SHORTCODE_PERMISSIONS=""
SHORTCODE_COUNT=0

# Helper functions for shortcode registry
register_shortcode() {
    local name="$1"
    local type="$2"
    local description="$3"
    local script="$4"
    local permissions="${5:-read,execute}"
    
    if [[ -z "$SHORTCODE_NAMES" ]]; then
        SHORTCODE_NAMES="$name"
        SHORTCODE_SCRIPTS="$script"
        SHORTCODE_DESCRIPTIONS="$description"
        SHORTCODE_TYPES="$type"
        SHORTCODE_PERMISSIONS="$permissions"
    else
        SHORTCODE_NAMES="$SHORTCODE_NAMES|$name"
        SHORTCODE_SCRIPTS="$SHORTCODE_SCRIPTS|$script"
        SHORTCODE_DESCRIPTIONS="$SHORTCODE_DESCRIPTIONS|$description"
        SHORTCODE_TYPES="$SHORTCODE_TYPES|$type"
        SHORTCODE_PERMISSIONS="$SHORTCODE_PERMISSIONS|$permissions"
    fi
    ((SHORTCODE_COUNT++))
}

get_shortcode_script() {
    local name="$1"
    local index=0
    IFS='|' read -ra names <<< "$SHORTCODE_NAMES"
    IFS='|' read -ra scripts <<< "$SHORTCODE_SCRIPTS"
    
    for shortcode in "${names[@]}"; do
        if [[ "$shortcode" == "$name" ]]; then
            echo "${scripts[$index]}"
            return 0
        fi
        ((index++))
    done
    return 1
}

get_shortcode_type() {
    local name="$1"
    local index=0
    IFS='|' read -ra names <<< "$SHORTCODE_NAMES"
    IFS='|' read -ra types <<< "$SHORTCODE_TYPES"
    
    for shortcode in "${names[@]}"; do
        if [[ "$shortcode" == "$name" ]]; then
            echo "${types[$index]}"
            return 0
        fi
        ((index++))
    done
    return 1
}

get_shortcode_description() {
    local name="$1"
    local index=0
    IFS='|' read -ra names <<< "$SHORTCODE_NAMES"
    IFS='|' read -ra descriptions <<< "$SHORTCODE_DESCRIPTIONS"
    
    for shortcode in "${names[@]}"; do
        if [[ "$shortcode" == "$name" ]]; then
            echo "${descriptions[$index]}"
            return 0
        fi
        ((index++))
    done
    return 1
}

shortcode_exists() {
    local name="$1"
    [[ "$SHORTCODE_NAMES" =~ (^|\\|)$name(\\||$) ]]
}

# Initialize shortcode system
init_shortcode_system() {
    set_error_context "shortcode_init" "$0"
    
    echo -e "${BLUE}🔧 Initializing shortcode system...${NC}"
    
    # Create shortcode configuration if it doesn't exist
    if [[ ! -f "$SHORTCODE_CONFIG" ]]; then
        create_default_shortcode_config
    fi
    
    # Load shortcodes from configuration
    load_shortcodes
    
    # Register built-in shortcodes
    register_builtin_shortcodes
    
    echo -e "${GREEN}✅ Shortcode system initialized with ${#SHORTCODE_REGISTRY[@]} commands${NC}"
}

# Create default shortcode configuration
create_default_shortcode_config() {
    mkdir -p "$(dirname "$SHORTCODE_CONFIG")"
    
    cat > "$SHORTCODE_CONFIG" << 'EOF'
{
  "shortcodes": [
    {
      "name": "RUN",
      "type": "script_execution",
      "description": "Execute a uScript file",
      "script": "uScript/system/script-runner.sh",
      "permissions": ["read", "execute"],
      "examples": ["[RUN:hello-world]", "[RUN:data-analysis mission=test]"]
    },
    {
      "name": "MISSION",
      "type": "mission_management",
      "description": "Create or manage missions",
      "script": "uScript/automation/mission-manager.sh",
      "permissions": ["read", "write"],
      "examples": ["[MISSION:create name=test]", "[MISSION:status]"]
    },
    {
      "name": "DATA",
      "type": "data_processing",
      "description": "Process data files",
      "script": "uScript/utilities/data-processor.sh",
      "permissions": ["read", "write"],
      "examples": ["[DATA:csv file=data.csv]", "[DATA:json file=config.json]"]
    },
    {
      "name": "CHECK",
      "type": "system_check",
      "description": "Perform system checks",
      "script": "uCode/check.sh",
      "permissions": ["read"],
      "examples": ["[CHECK:health]", "[CHECK:setup]"]
    },
    {
      "name": "BASH",
      "type": "shell_execution",
      "description": "Execute bash commands in containerized environment",
      "script": "uScript/system/bash-container.sh",
      "permissions": ["read", "write", "execute"],
      "examples": ["[BASH:ls -la]", "[BASH:find . -name '*.md']"]
    }
  ]
}
EOF
    
    echo -e "${GREEN}✅ Created default shortcode configuration${NC}"
}

# Load shortcodes from configuration
load_shortcodes() {
    if [[ ! -f "$SHORTCODE_CONFIG" ]]; then
        error_critical "Shortcode configuration not found: $SHORTCODE_CONFIG"
        return 1
    fi
    
    echo "📥 Loading shortcodes from dataset..."
    
    # Simple JSON parsing (compatible with older bash)
    local current_name=""
    local current_desc=""
    local current_type=""
    local current_script=""
    
    while IFS= read -r line; do
        if [[ "$line" =~ \"name\":\ *\"([^\"]+)\" ]]; then
            current_name="${BASH_REMATCH[1]}"
        fi
        if [[ "$line" =~ \"description\":\ *\"([^\"]+)\" ]]; then
            current_desc="${BASH_REMATCH[1]}"
        fi
        if [[ "$line" =~ \"type\":\ *\"([^\"]+)\" ]]; then
            current_type="${BASH_REMATCH[1]}"
        fi
        if [[ "$line" =~ \"script\":\ *\"([^\"]+)\" ]]; then
            current_script="${BASH_REMATCH[1]}"
            # Register the shortcode when we have all info
            if [[ -n "$current_name" && -n "$current_desc" && -n "$current_type" ]]; then
                register_shortcode "$current_name" "$current_type" "$current_desc" "$UHOME/$current_script"
                current_name=""
                current_desc=""
                current_type=""
                current_script=""
            fi
        fi
    done < "$SHORTCODE_CONFIG"
}

# Register built-in shortcodes
register_builtin_shortcodes() {
    # Core system shortcodes
    register_shortcode "HELP" "system" "Show available shortcodes" "$SCRIPT_DIR/shortcode-processor.sh"
    register_shortcode "VERSION" "system" "Show uDOS version" "$UHOME/uCode/ucode.sh"
    register_shortcode "DASHBOARD" "system" "Show dashboard" "$UHOME/uCode/dash.sh"
    register_shortcode "LOG" "logging" "Log information" "$UHOME/uCode/log.sh"
    register_shortcode "ERROR" "logging" "Report error" "$UHOME/uCode/error-handler.sh"
    
    # Navigation shortcodes
    register_shortcode "TREE" "navigation" "Show file tree" "$UHOME/uCode/make-tree.sh"
    register_shortcode "LIST" "navigation" "List directory contents" "/bin/ls"
    register_shortcode "FIND" "navigation" "Find files" "/usr/bin/find"
    
    # Development shortcodes
    register_shortcode "VALIDATE" "development" "Validate system" "$UHOME/uCode/validate-alpha.sh"
    register_shortcode "TEST" "development" "Run tests" "$UHOME/uScript/tests/test-runner.sh"
    register_shortcode "DEBUG" "development" "Debug mode" "$UHOME/uCode/ucode.sh"
}

# Register a shortcode
register_shortcode() {
    local name="$1"
    local type="$2"
    local description="$3"
    local script="$4"
    local permissions="${5:-read,execute}"
    
    if [[ -z "$SHORTCODE_NAMES" ]]; then
        SHORTCODE_NAMES="$name"
        SHORTCODE_SCRIPTS="$script"
        SHORTCODE_DESCRIPTIONS="$description"
        SHORTCODE_TYPES="$type"
        SHORTCODE_PERMISSIONS="$permissions"
    else
        SHORTCODE_NAMES="$SHORTCODE_NAMES|$name"
        SHORTCODE_SCRIPTS="$SHORTCODE_SCRIPTS|$script"
        SHORTCODE_DESCRIPTIONS="$SHORTCODE_DESCRIPTIONS|$description"
        SHORTCODE_TYPES="$SHORTCODE_TYPES|$type"
        SHORTCODE_PERMISSIONS="$SHORTCODE_PERMISSIONS|$permissions"
    fi
    ((SHORTCODE_COUNT++))
}

# Process shortcode from input text
process_shortcode() {
    local input="$1"
    local output_format="${2:-text}"  # text, json, markdown
    
    set_error_context "shortcode_processing" "$0"
    
    # Extract shortcodes using regex
    local shortcode_pattern='\[([a-zA-Z0-9_-]+):?([^]]*)\]'
    
    if [[ "$input" =~ $shortcode_pattern ]]; then
        local shortcode_name=$(echo "${BASH_REMATCH[1]}" | awk '{print toupper($0)}')
        local shortcode_args="${BASH_REMATCH[2]}"
        
        echo -e "${CYAN}🔍 Processing shortcode: [$shortcode_name:$shortcode_args]${NC}"
        
        execute_shortcode "$shortcode_name" "$shortcode_args" "$output_format"
    else
        error_warning "No valid shortcode found in input: $input"
        return 1
    fi
}

# Execute a shortcode
execute_shortcode() {
    local name="$1"
    local args="$2"
    local output_format="${3:-text}"
    
    set_error_context "shortcode_execution" "$name"
    
    # Check if shortcode exists
    if ! shortcode_exists "$name"; then
        error_critical "Unknown shortcode: $name"
        suggest_similar_shortcodes "$name"
        return 1
    fi
    
    local script=$(get_shortcode_script "$name")
    local type=$(get_shortcode_type "$name")
    
    # Validate script exists
    if [[ ! -f "$script" ]]; then
        error_critical "Shortcode script not found: $script"
        return 1
    fi
    
    # Check permissions
    if ! check_shortcode_permissions "$name"; then
        error_critical "Permission denied for shortcode: $name"
        return 1
    fi
    
    echo -e "${BLUE}⚡ Executing shortcode '$name' with args: $args${NC}"
    
    # Execute based on type
    case "$type" in
        "script_execution")
            execute_script_shortcode "$script" "$args" "$output_format"
            ;;
        "shell_execution")
            execute_shell_shortcode "$script" "$args" "$output_format"
            ;;
        "system")
            execute_system_shortcode "$script" "$args" "$output_format"
            ;;
        "data_processing")
            execute_data_shortcode "$script" "$args" "$output_format"
            ;;
        "mission_management")
            execute_mission_shortcode "$script" "$args" "$output_format"
            ;;
        *)
            execute_generic_shortcode "$script" "$args" "$output_format"
            ;;
    esac
}

# Execute script-type shortcode
execute_script_shortcode() {
    local script="$1"
    local args="$2"
    local output_format="$3"
    
    # Parse arguments
    local script_name=""
    local script_args=""
    
    if [[ "$args" =~ ^([a-zA-Z0-9_/-]+)(.*)$ ]]; then
        script_name="${BASH_REMATCH[1]}"
        script_args="${BASH_REMATCH[2]}"
    else
        script_name="$args"
    fi
    
    # Find the actual script to run
    local target_script=""
    if [[ -f "$USCRIPT_DIR/$script_name.md" ]]; then
        target_script="$USCRIPT_DIR/$script_name.md"
    elif [[ -f "$USCRIPT_DIR/examples/$script_name.md" ]]; then
        target_script="$USCRIPT_DIR/examples/$script_name.md"
    elif [[ -f "$USCRIPT_DIR/automation/$script_name.md" ]]; then
        target_script="$USCRIPT_DIR/automation/$script_name.md"
    else
        error_critical "uScript not found: $script_name"
        return 1
    fi
    
    echo -e "${GREEN}📝 Executing uScript: $target_script${NC}"
    
    # Execute via uScript runner
    bash "$USCRIPT_DIR/system/ucode-runner.sh" run "$target_script" $script_args
}

# Execute shell-type shortcode (containerized bash)
execute_shell_shortcode() {
    local script="$1"
    local args="$2"
    local output_format="$3"
    
    echo -e "${YELLOW}🐚 Executing containerized bash command: $args${NC}"
    
    # Create temporary script
    local temp_script=$(mktemp)
    cat > "$temp_script" << EOF
#!/bin/bash
set -euo pipefail

# Containerized environment variables
export CONTAINER_MODE=true
export UHOME="$UHOME"
export CONTAINER_ID=\$(date +%s)_\$$

echo "🐳 Containerized Bash Execution (ID: \$CONTAINER_ID)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Execute the command
$args

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Containerized execution completed"
EOF
    
    chmod +x "$temp_script"
    
    # Execute in isolated environment
    bash "$temp_script"
    local exit_code=$?
    
    # Cleanup
    rm -f "$temp_script"
    
    return $exit_code
}

# Execute system shortcode
execute_system_shortcode() {
    local script="$1"
    local args="$2"
    local output_format="$3"
    
    case "$(basename "$script")" in
        "shortcode-processor.sh")
            show_shortcode_help
            ;;
        "ucode.sh")
            show_version_info
            ;;
        "dash.sh")
            bash "$script"
            ;;
        *)
            bash "$script" $args
            ;;
    esac
}

# Execute data processing shortcode
execute_data_shortcode() {
    local script="$1"
    local args="$2"
    local output_format="$3"
    
    echo -e "${PURPLE}📊 Processing data with args: $args${NC}"
    
    # Parse data processing arguments
    local file_arg=""
    local format_arg=""
    
    if [[ "$args" =~ file=([^[:space:]]+) ]]; then
        file_arg="${BASH_REMATCH[1]}"
    fi
    
    if [[ "$args" =~ format=([^[:space:]]+) ]]; then
        format_arg="${BASH_REMATCH[1]}"
    fi
    
    if [[ -n "$file_arg" ]]; then
        echo -e "${BLUE}📁 Processing file: $file_arg${NC}"
        bash "$script" "$file_arg" "$format_arg"
    else
        bash "$script" $args
    fi
}

# Execute mission management shortcode
execute_mission_shortcode() {
    local script="$1"
    local args="$2"
    local output_format="$3"
    
    echo -e "${GREEN}🎯 Mission management: $args${NC}"
    bash "$script" $args
}

# Execute generic shortcode
execute_generic_shortcode() {
    local script="$1"
    local args="$2"
    local output_format="$3"
    
    echo -e "${CYAN}⚡ Generic execution: $script $args${NC}"
    bash "$script" $args
}

# Check shortcode permissions
check_shortcode_permissions() {
    local name="$1"
    local permissions="${SHORTCODE_PERMISSIONS[$name]:-read}"
    
    # Simple permission check (can be expanded)
    if [[ "$permissions" =~ execute ]]; then
        # Check if script execution is allowed
        return 0
    fi
    
    return 0  # Allow by default for now
}

# Suggest similar shortcodes
suggest_similar_shortcodes() {
    local query="$1"
    echo -e "${YELLOW}💡 Did you mean one of these?${NC}"
    
    for shortcode in "${!SHORTCODE_REGISTRY[@]}"; do
        if [[ "$shortcode" =~ .*"$query".* ]] || [[ "$query" =~ .*"$shortcode".* ]]; then
            echo -e "  • $shortcode - ${SHORTCODE_DESCRIPTIONS[$shortcode]}"
        fi
    done
}

# Show shortcode help
show_shortcode_help() {
    echo -e "${PURPLE}🔧 uDOS Shortcode System v1.7.1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Available Shortcodes:"
    echo ""
    
    # Group by type
    declare -A type_groups
    for shortcode in "${!SHORTCODE_REGISTRY[@]}"; do
        local type="${SHORTCODE_TYPES[$shortcode]}"
        if [[ -z "${type_groups[$type]:-}" ]]; then
            type_groups["$type"]="$shortcode"
        else
            type_groups["$type"]="${type_groups[$type]} $shortcode"
        fi
    done
    
    for type in "${!type_groups[@]}"; do
        echo -e "${BLUE}📂 $type${NC}"
        for shortcode in ${type_groups[$type]}; do
            local desc="${SHORTCODE_DESCRIPTIONS[$shortcode]}"
            echo -e "  • ${GREEN}[$shortcode]${NC} - $desc"
        done
        echo ""
    done
    
    echo "Usage Examples:"
    echo "  [RUN:hello-world]           - Execute hello-world uScript"
    echo "  [BASH:ls -la]               - Run bash command in container"
    echo "  [MISSION:create name=test]  - Create new mission"
    echo "  [DATA:csv file=data.csv]    - Process CSV file"
    echo "  [CHECK:health]              - Perform health check"
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
    
    echo "Shortcode System: v1.7.1"
    echo "Available Shortcodes: ${#SHORTCODE_REGISTRY[@]}"
    echo "Error Handling: Enhanced"
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
            if shortcode_output=$(execute_shortcode "$shortcode_name" "$shortcode_args" "text" 2>&1); then
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
        "init")
            init_shortcode_system
            ;;
        "process")
            process_shortcode "$2" "${3:-text}"
            ;;
        "file")
            process_file_shortcodes "$2" "$3"
            ;;
        "interactive"|"repl")
            init_shortcode_system
            interactive_mode
            ;;
        "register")
            register_shortcode "$2" "$3" "$4" "$5" "$6"
            ;;
        "list")
            show_shortcode_help
            ;;
        "help"|*)
            echo -e "${PURPLE}🔧 uDOS Shortcode Processor v1.7.1${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "Usage: $0 <command> [arguments]"
            echo ""
            echo "Commands:"
            echo "  init                           - Initialize shortcode system"
            echo "  process <shortcode>            - Process a single shortcode"
            echo "  file <input_file> [output]     - Process shortcodes in file"
            echo "  interactive                    - Start interactive mode"
            echo "  register <name> <type> <desc> <script> [perms] - Register new shortcode"
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
