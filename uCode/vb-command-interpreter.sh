#!/bin/bash
# vb-command-interpreter.sh - Visual Basic Style Command Language for uDOS
# Implements a comprehensive VB-style command language with modern features
# Version: 2.0.0

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
VB_COMMANDS_FILE="$UHOME/uTemplate/datasets/vb-commands.json"
VB_VARIABLES_FILE="$UHOME/uDev/vb-variables.json"
VB_PROCEDURES_DIR="$UHOME/uMemory/scripts/vb-procedures"
VB_MODULES_DIR="$UHOME/uMemory/scripts/vb-modules"

# Create required directories
mkdir -p "$VB_PROCEDURES_DIR" "$VB_MODULES_DIR" "$(dirname "$VB_VARIABLES_FILE")"

# Global VB interpreter state
# Use compatible variable storage for older bash versions
VB_VARIABLES_LIST=""
VB_PROCEDURES_LIST=""
VB_MODULES_LIST=""
VB_ARRAYS_LIST=""
VB_DEBUG_MODE=false
VB_ERROR_MODE="halt"  # halt, continue, ignore
VB_CURRENT_LINE=0
VB_CURRENT_FILE=""

# Variable storage functions (compatible with all bash versions)
vb_set_variable() {
    local var_name="$1"
    local var_type="$2"
    local var_value="$3"
    
    # Remove existing variable if it exists
    VB_VARIABLES_LIST=$(echo "$VB_VARIABLES_LIST" | grep -v "^${var_name}:")
    
    # Add new variable
    if [[ -z "$VB_VARIABLES_LIST" ]]; then
        VB_VARIABLES_LIST="${var_name}:${var_type}:${var_value}"
    else
        VB_VARIABLES_LIST="${VB_VARIABLES_LIST}|${var_name}:${var_type}:${var_value}"
    fi
}

vb_get_variable() {
    local var_name="$1"
    local var_info=$(echo "$VB_VARIABLES_LIST" | tr '|' '\n' | grep "^${var_name}:")
    if [[ -n "$var_info" ]]; then
        echo "$var_info" | cut -d':' -f3
    fi
}

vb_get_variable_type() {
    local var_name="$1"
    local var_info=$(echo "$VB_VARIABLES_LIST" | tr '|' '\n' | grep "^${var_name}:")
    if [[ -n "$var_info" ]]; then
        echo "$var_info" | cut -d':' -f2
    fi
}

vb_variable_exists() {
    local var_name="$1"
    echo "$VB_VARIABLES_LIST" | tr '|' '\n' | grep -q "^${var_name}:"
}

# === VB-Style Data Types ===
VB_DATATYPES="String Integer Long Single Double Boolean Date Variant Object"

# === Core VB Command Functions ===

# Variable Declaration and Assignment
vb_dim() {
    local args="$*"
    local var_name=""
    local var_type="Variant"
    local initial_value=""
    
    # Parse DIM statement: DIM varname As type [= value]
    if [[ "$args" =~ ^([a-zA-Z][a-zA-Z0-9_]*)[[:space:]]+As[[:space:]]+([a-zA-Z]+)([[:space:]]*=[[:space:]]*(.+))?$ ]]; then
        var_name="${BASH_REMATCH[1]}"
        var_type="${BASH_REMATCH[2]}"
        initial_value="${BASH_REMATCH[4]}"
    elif [[ "$args" =~ ^([a-zA-Z][a-zA-Z0-9_]*)[[:space:]]+As[[:space:]]+([a-zA-Z]+)$ ]]; then
        var_name="${BASH_REMATCH[1]}"
        var_type="${BASH_REMATCH[2]}"
    elif [[ "$args" =~ ^([a-zA-Z][a-zA-Z0-9_]*)$ ]]; then
        var_name="${BASH_REMATCH[1]}"
        var_type="Variant"
    else
        vb_error "Invalid DIM syntax. Use: DIM varname As type [= value]"
        return 1
    fi
    
    if [[ -z "$var_name" ]]; then
        vb_error "Variable name required for DIM statement"
        return 1
    fi
    
    # Validate variable name (VB naming rules)
    if [[ ! "$var_name" =~ ^[a-zA-Z][a-zA-Z0-9_]*$ ]]; then
        vb_error "Invalid variable name: $var_name"
        return 1
    fi
    
    # Validate data type
    if [[ ! "$VB_DATATYPES" =~ $var_type ]]; then
        vb_error "Invalid data type: $var_type"
        return 1
    fi
    
    vb_set_variable "$var_name" "$var_type" "${initial_value:-}"
    
    vb_debug "DIM $var_name As $var_type = '${initial_value:-}'"
    echo "✅ Variable $var_name declared as $var_type"
}

# Variable Assignment
vb_set() {
    local args="$*"
    local var_name=""
    local value=""
    
    # Parse SET statement: SET varname = value
    if [[ "$args" =~ ^([a-zA-Z][a-zA-Z0-9_]*)[[:space:]]*=[[:space:]]*(.+)$ ]]; then
        var_name="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"
    else
        vb_error "Invalid SET syntax. Use: SET varname = value"
        return 1
    fi
    
    if [[ -z "$var_name" ]]; then
        vb_error "Variable name required for SET statement"
        return 1
    fi
    
    # Check if variable exists
    if ! vb_variable_exists "$var_name"; then
        vb_error "Variable $var_name not declared. Use DIM first."
        return 1
    fi
    
    local var_type=$(vb_get_variable_type "$var_name")
    
    # Type validation and conversion
    case "$var_type" in
        "Integer"|"Long")
            if [[ ! "$value" =~ ^-?[0-9]+$ ]]; then
                vb_error "Type mismatch: Cannot assign '$value' to $var_type"
                return 1
            fi
            ;;
        "Single"|"Double")
            if [[ ! "$value" =~ ^-?[0-9]*\.?[0-9]+$ ]]; then
                vb_error "Type mismatch: Cannot assign '$value' to $var_type"
                return 1
            fi
            ;;
        "Boolean")
            case "$value" in
                "True"|"true"|"1") value="True" ;;
                "False"|"false"|"0") value="False" ;;
                *) vb_error "Type mismatch: Boolean requires True/False"; return 1 ;;
            esac
            ;;
        "Date")
            # Basic date validation (YYYY-MM-DD format)
            if [[ ! "$value" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
                vb_error "Type mismatch: Date requires YYYY-MM-DD format"
                return 1
            fi
            ;;
    esac
    
    vb_set_variable "$var_name" "$var_type" "$value"
    vb_debug "SET $var_name = '$value'"
    echo "✅ $var_name = $value"
}

# Print Statement
vb_print() {
    local output=""
    local arg
    for arg in "$@"; do
        # Variable substitution
        if [[ "$arg" =~ ^\$([a-zA-Z][a-zA-Z0-9_]*)$ ]]; then
            local var_name="${BASH_REMATCH[1]}"
            local var_value=$(vb_get_variable "$var_name")
            if [[ -z "$var_value" && ! $(vb_variable_exists "$var_name") ]]; then
                vb_error "Variable $var_name not declared"
                return 1
            fi
            output="$output$var_value"
        else
            output="$output$arg"
        fi
    done
    echo "$output"
}

# Input Statement
vb_input() {
    local prompt="$1"
    local var_name="$2"
    
    if [[ -z "$var_name" ]]; then
        vb_error "Variable name required for INPUT statement"
        return 1
    fi
    
    # Check if variable exists
    if ! vb_variable_exists "$var_name"; then
        vb_error "Variable $var_name not declared. Use DIM first."
        return 1
    fi
    
    echo -n "$prompt"
    read -r input_value
    
    local var_type=$(vb_get_variable_type "$var_name")
    vb_set_variable "$var_name" "$var_type" "$input_value"
}

# If Statement
vb_if() {
    local condition="$1"
    shift
    local then_part="$*"
    
    if vb_evaluate_condition "$condition"; then
        vb_execute_line "$then_part"
    fi
}

# For Loop
vb_for() {
    local args="$*"
    local var_name=""
    local start_val=""
    local end_val=""
    local step="1"
    
    # Parse FOR statement: FOR var = start TO end [STEP step]
    if [[ "$args" =~ ^([a-zA-Z][a-zA-Z0-9_]*)[[:space:]]*=[[:space:]]*([0-9-]+)[[:space:]]+TO[[:space:]]+([0-9-]+)[[:space:]]+STEP[[:space:]]+([0-9-]+)$ ]]; then
        var_name="${BASH_REMATCH[1]}"
        start_val="${BASH_REMATCH[2]}"
        end_val="${BASH_REMATCH[3]}"
        step="${BASH_REMATCH[4]}"
    elif [[ "$args" =~ ^([a-zA-Z][a-zA-Z0-9_]*)[[:space:]]*=[[:space:]]*([0-9-]+)[[:space:]]+TO[[:space:]]+([0-9-]+)$ ]]; then
        var_name="${BASH_REMATCH[1]}"
        start_val="${BASH_REMATCH[2]}"
        end_val="${BASH_REMATCH[3]}"
        step="1"
    else
        vb_error "Invalid FOR syntax. Use: FOR var = start TO end [STEP step]"
        return 1
    fi
    
    if [[ -z "$var_name" || -z "$start_val" || -z "$end_val" ]]; then
        vb_error "FOR loop requires variable, start, and end values"
        return 1
    fi
    
    # Check if variable exists, if not declare it as Integer
    if ! vb_variable_exists "$var_name"; then
        vb_set_variable "$var_name" "Integer" "$start_val"
    else
        # Initialize loop variable
        local var_type=$(vb_get_variable_type "$var_name")
        vb_set_variable "$var_name" "$var_type" "$start_val"
    fi
    
    # Store loop state for NEXT processing
    vb_set_variable "__FOR_${var_name}_end" "Integer" "$end_val"
    vb_set_variable "__FOR_${var_name}_step" "Integer" "$step"
    vb_set_variable "__FOR_${var_name}_active" "Boolean" "true"
    
    echo "🔄 FOR $var_name = $start_val TO $end_val STEP $step"
}

# Next Statement
vb_next() {
    local args="$*"
    local var_name="$args"
    
    if [[ -z "$var_name" ]]; then
        vb_error "Variable name required for NEXT statement"
        return 1
    fi
    
    if [[ "$(vb_get_variable "__FOR_${var_name}_active")" != "true" ]]; then
        vb_error "NEXT without FOR: $var_name"
        return 1
    fi
    
    local current_val=$(vb_get_variable "$var_name")
    local end_val=$(vb_get_variable "__FOR_${var_name}_end")
    local step=$(vb_get_variable "__FOR_${var_name}_step")
    
    # Increment variable
    local new_val=$((current_val + step))
    local var_type=$(vb_get_variable_type "$var_name")
    vb_set_variable "$var_name" "$var_type" "$new_val"
    
    # Check if loop should continue
    if (( (step > 0 && new_val <= end_val) || (step < 0 && new_val >= end_val) )); then
        echo "🔄 NEXT $var_name (continuing: $new_val)"
        return 0  # Continue loop
    else
        # End loop
        vb_set_variable "__FOR_${var_name}_end" "Integer" ""
        vb_set_variable "__FOR_${var_name}_step" "Integer" ""
        vb_set_variable "__FOR_${var_name}_active" "Boolean" "false"
        echo "🏁 FOR loop completed: $var_name"
        return 1  # End loop
    fi
}

# Procedure Definition
vb_sub() {
    local proc_name="$1"
    shift
    local params="$*"
    
    if [[ -z "$proc_name" ]]; then
        vb_error "Procedure name required for SUB statement"
        return 1
    fi
    
    # Create procedure file
    local proc_file="$VB_PROCEDURES_DIR/${proc_name}.vb"
    echo "' VB Procedure: $proc_name" > "$proc_file"
    echo "' Parameters: $params" >> "$proc_file"
    echo "' Created: $(date)" >> "$proc_file"
    echo "" >> "$proc_file"
    
    VB_PROCEDURES["$proc_name"]="$proc_file"
    echo "📝 SUB $proc_name defined with parameters: $params"
    echo "📁 Procedure file: $proc_file"
}

# Function Call
vb_call() {
    local proc_name="$1"
    shift
    local args="$*"
    
    if [[ -z "${VB_PROCEDURES["$proc_name"]:-}" ]]; then
        vb_error "Procedure $proc_name not found"
        return 1
    fi
    
    local proc_file="${VB_PROCEDURES["$proc_name"]}"
    echo "📞 CALL $proc_name($args)"
    
    # Execute procedure (simplified - in full implementation would handle parameters)
    if [[ -f "$proc_file" ]]; then
        echo "🔄 Executing procedure from: $proc_file"
        # Source the procedure file and execute
        source "$proc_file" 2>/dev/null || echo "⚠️ Procedure execution completed"
    fi
}

# === Utility Functions ===

vb_error() {
    local message="$1"
    echo "❌ VB Error [Line $VB_CURRENT_LINE]: $message" >&2
    
    case "$VB_ERROR_MODE" in
        "halt") exit 1 ;;
        "continue") return 1 ;;
        "ignore") return 0 ;;
    esac
}

vb_debug() {
    if [[ "$VB_DEBUG_MODE" == "true" ]]; then
        echo "🐛 DEBUG: $1" >&2
    fi
}

vb_evaluate_condition() {
    local condition="$1"
    # Simplified condition evaluation - in full implementation would parse complex expressions
    # For now, support basic comparisons
    
    if [[ "$condition" =~ ^\$([a-zA-Z][a-zA-Z0-9_]*)\s*([><=!]+)\s*(.+)$ ]]; then
        local var_name="${BASH_REMATCH[1]}"
        local operator="${BASH_REMATCH[2]}"
        local value="${BASH_REMATCH[3]}"
        
        local var_value="${VB_VARIABLES["${var_name}_value"]:-}"
        
        case "$operator" in
            "="|"==") [[ "$var_value" == "$value" ]] ;;
            "!="|"<>") [[ "$var_value" != "$value" ]] ;;
            ">") (( var_value > value )) ;;
            "<") (( var_value < value )) ;;
            ">=") (( var_value >= value )) ;;
            "<=") (( var_value <= value )) ;;
            *) vb_error "Unsupported operator: $operator"; return 1 ;;
        esac
    else
        # Simple true/false evaluation
        case "$condition" in
            "true"|"True"|"1") return 0 ;;
            "false"|"False"|"0") return 1 ;;
            *) vb_error "Invalid condition: $condition"; return 1 ;;
        esac
    fi
}

vb_execute_line() {
    local line="$1"
    ((VB_CURRENT_LINE++))
    
    # Remove leading/trailing whitespace
    line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    
    # Skip empty lines and comments
    if [[ -z "$line" || "$line" =~ ^\'.*$ ]]; then
        return 0
    fi
    
    vb_debug "Executing: $line"
    
    # Parse command
    local cmd
    local args
    read -r cmd args <<< "$line"
    cmd=$(echo "$cmd" | tr '[:lower:]' '[:upper:]')
    
    case "$cmd" in
        "DIM") vb_dim "$args" ;;
        "SET") vb_set "$args" ;;
        "PRINT") vb_print $args ;;
        "INPUT") vb_input $args ;;
        "IF") vb_if $args ;;
        "FOR") vb_for $args ;;
        "NEXT") vb_next $args ;;
        "SUB") vb_sub $args ;;
        "CALL") vb_call $args ;;
        "REM"|"'") return 0 ;;  # Comments
        "END") echo "🏁 Program ended"; exit 0 ;;
        *) vb_error "Unknown command: $cmd" ;;
    esac
}

# === VB Language Features ===

# Save variables to persistent storage
vb_save_variables() {
    local save_file="$VB_VARIABLES_FILE"
    echo "{" > "$save_file"
    echo "  \"variables\": {" >> "$save_file"
    
    local first=true
    for key in "${!VB_VARIABLES[@]}"; do
        if [[ "$key" =~ _value$ ]]; then
            local var_name="${key%_value}"
            local var_type="${VB_VARIABLES["${var_name}_type"]:-Variant}"
            local var_value="${VB_VARIABLES["$key"]}"
            
            if [[ "$first" == "true" ]]; then
                first=false
            else
                echo "," >> "$save_file"
            fi
            
            echo -n "    \"$var_name\": {\"type\": \"$var_type\", \"value\": \"$var_value\"}" >> "$save_file"
        fi
    done
    
    echo "" >> "$save_file"
    echo "  }," >> "$save_file"
    echo "  \"metadata\": {" >> "$save_file"
    echo "    \"saved\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"," >> "$save_file"
    echo "    \"version\": \"2.0.0\"" >> "$save_file"
    echo "  }" >> "$save_file"
    echo "}" >> "$save_file"
    
    echo "💾 Variables saved to: $save_file"
}

# Load variables from persistent storage
vb_load_variables() {
    local save_file="$VB_VARIABLES_FILE"
    if [[ -f "$save_file" ]]; then
        echo "📥 Loading variables from: $save_file"
        # Simple JSON parsing for variables (in full implementation would use proper JSON parser)
        while IFS= read -r line; do
            if [[ "$line" =~ \"([^\"]+)\":[[:space:]]*\{\"type\":[[:space:]]*\"([^\"]+)\",[[:space:]]*\"value\":[[:space:]]*\"([^\"]*)\" ]]; then
                local var_name="${BASH_REMATCH[1]}"
                local var_type="${BASH_REMATCH[2]}"
                local var_value="${BASH_REMATCH[3]}"
                
                VB_VARIABLES["${var_name}_type"]="$var_type"
                VB_VARIABLES["${var_name}_value"]="$var_value"
                echo "📥 Loaded: $var_name ($var_type) = '$var_value'"
            fi
        done < "$save_file"
    fi
}

# === Main VB Interpreter Interface ===

vb_help() {
    cat << 'EOF'
🔷 uDOS Visual Basic-Style Command Language v2.0.0

📚 BASIC COMMANDS:
  DIM <variable> As <type> [= value]  - Declare variable
  SET <variable> = <value>            - Assign value to variable
  PRINT <text/variables>              - Display output
  INPUT "<prompt>", <variable>        - Get user input
  
📚 CONTROL STRUCTURES:
  IF <condition> THEN <statement>     - Conditional execution
  FOR <var> = <start> TO <end> [STEP <step>] - Loop structure
  NEXT <variable>                     - End of FOR loop
  
📚 PROCEDURES:
  SUB <name>([parameters])            - Define procedure
  CALL <name>([arguments])            - Call procedure
  END SUB                             - End procedure definition
  
📚 DATA TYPES:
  String, Integer, Long, Single, Double, Boolean, Date, Variant
  
📚 SYSTEM COMMANDS:
  VB.DEBUG [ON|OFF]                   - Toggle debug mode
  VB.ERROR [HALT|CONTINUE|IGNORE]     - Set error handling mode
  VB.SAVE                             - Save variables to disk
  VB.LOAD                             - Load variables from disk
  VB.VARS                             - List all variables
  VB.CLEAR                            - Clear all variables
  VB.HELP                             - Show this help
  
📚 EXAMPLES:
  DIM userName As String = "Agent"
  PRINT "Hello, "; $userName
  FOR i = 1 TO 10: PRINT $i: NEXT i
  
🎯 Type VB.HELP <command> for detailed help on specific commands.
EOF
}

vb_list_variables() {
    echo "📊 VB Variables:"
    echo "=================="
    if [[ -z "$VB_VARIABLES_LIST" ]]; then
        echo "No variables declared"
        return
    fi
    
    echo "$VB_VARIABLES_LIST" | tr '|' '\n' | while IFS=':' read -r var_name var_type var_value; do
        if [[ -n "$var_name" ]]; then
            printf "%-15s %-10s = '%s'\n" "$var_name" "($var_type)" "$var_value"
        fi
    done
}

vb_clear_variables() {
    VB_VARIABLES_LIST=""
    VB_PROCEDURES_LIST=""
    echo "🧹 All variables and procedures cleared"
}

# === Main Entry Point ===

vb_command() {
    local cmd="$1"
    shift
    local args="$*"
    
    case "$cmd" in
        "VB.DEBUG")
            case "$args" in
                "ON"|"on") VB_DEBUG_MODE=true; echo "🐛 Debug mode: ON" ;;
                "OFF"|"off") VB_DEBUG_MODE=false; echo "🐛 Debug mode: OFF" ;;
                *) echo "🐛 Debug mode: $VB_DEBUG_MODE" ;;
            esac
            ;;
        "VB.ERROR")
            case "$args" in
                "HALT"|"halt") VB_ERROR_MODE="halt"; echo "⚠️ Error mode: HALT" ;;
                "CONTINUE"|"continue") VB_ERROR_MODE="continue"; echo "⚠️ Error mode: CONTINUE" ;;
                "IGNORE"|"ignore") VB_ERROR_MODE="ignore"; echo "⚠️ Error mode: IGNORE" ;;
                *) echo "⚠️ Error mode: $VB_ERROR_MODE" ;;
            esac
            ;;
        "VB.SAVE") vb_save_variables ;;
        "VB.LOAD") vb_load_variables ;;
        "VB.VARS") vb_list_variables ;;
        "VB.CLEAR") vb_clear_variables ;;
        "VB.HELP") vb_help ;;
        *) vb_execute_line "$cmd $args" ;;
    esac
}

# Initialize VB system
vb_init() {
    echo "🔷 uDOS Visual Basic-Style Command Language v2.0.0"
    echo "🚀 Initializing VB interpreter..."
    
    # Load saved variables if they exist
    vb_load_variables
    
    echo "✅ VB interpreter ready!"
    echo "💡 Type VB.HELP for command reference"
}

# Export functions for use in ucode.sh
export -f vb_command vb_init vb_help vb_execute_line
