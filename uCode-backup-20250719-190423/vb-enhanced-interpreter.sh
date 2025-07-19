#!/bin/bash
# vb-enhanced-interpreter.sh - Enhanced VB interpreter with Shortcode and Variable integration
# Integrates with uDOS mapping system, timestamps, filenames, and templates
# Version: 2.1.0

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"

# Core integration files
LOCATION_MAP="$UHOME/uTemplate/datasets/locationMap.json"
TIMEZONE_MAP="$UHOME/uTemplate/datasets/timezoneMap.json"
SHORTCODES_CONFIG="$UHOME/uTemplate/system/shortcodes.json"
USER_VARIABLES="$UHOME/uMemory/user/variables.json"
USER_SHORTCODES="$UHOME/uMemory/user/shortcodes.json"

# Enhanced VB system variables
VB_ENHANCED_VARIABLES=""
VB_SHORTCODE_REGISTRY=""
VB_CURRENT_LOCATION=""
VB_CURRENT_TIMEZONE=""
VB_GRID_POSITION=""

# === CORE SYSTEM INTEGRATION ===

# Initialize enhanced VB system with mapping integration
vb_enhanced_init() {
    echo "🔷 Enhanced VB System v2.1.0 - Initializing..."
    
    # Load current user location and timezone
    vb_load_user_context
    
    # Initialize grid system
    vb_init_grid_system
    
    # Load shortcode registry
    vb_load_shortcode_registry
    
    # Set up default system variables
    vb_setup_system_variables
    
    echo "✅ Enhanced VB system ready with mapping and shortcode integration!"
}

# Load user context from identity
vb_load_user_context() {
    local identity_file="$UHOME/uMemory/user/identity.md"
    
    if [[ -f "$identity_file" ]]; then
        VB_CURRENT_LOCATION=$(grep "Location:" "$identity_file" | cut -d':' -f2 | xargs)
        VB_CURRENT_TIMEZONE=$(grep "Timezone:" "$identity_file" | cut -d':' -f2 | xargs)
        
        echo "📍 User context loaded: $VB_CURRENT_LOCATION ($VB_CURRENT_TIMEZONE)"
        
        # Resolve location to grid coordinates if available
        vb_resolve_location_to_grid "$VB_CURRENT_LOCATION"
    else
        echo "⚠️ User identity not found, using defaults"
        VB_CURRENT_LOCATION="unknown"
        VB_CURRENT_TIMEZONE="UTC"
        VB_GRID_POSITION="A1"
    fi
}

# Resolve location to grid coordinates using location dataset
vb_resolve_location_to_grid() {
    local location="$1"
    
    if [[ -f "$LOCATION_MAP" ]] && command -v jq >/dev/null 2>&1; then
        local grid_data=$(jq -r --arg loc "$location" '.data[] | select(.city | test($loc; "i")) | .tile' "$LOCATION_MAP" 2>/dev/null | head -1)
        
        if [[ -n "$grid_data" ]]; then
            VB_GRID_POSITION="$grid_data"
            echo "🗺️  Grid position resolved: $VB_GRID_POSITION"
        else
            VB_GRID_POSITION="UNKNOWN"
            echo "⚠️ Grid position not found for: $location"
        fi
    else
        VB_GRID_POSITION="OFFLINE"
        echo "⚠️ Location mapping unavailable"
    fi
}

# Initialize grid system for coordinate-based operations
vb_init_grid_system() {
    echo "🗺️  Initializing grid system..."
    
    # Grid system: A1-Z99 format
    # A-Z (columns), 1-99 (rows)
    # Each grid point can have associated data/scripts/templates
    
    mkdir -p "$UHOME/uMemory/grid"
    mkdir -p "$UHOME/uMemory/grid/scripts"
    mkdir -p "$UHOME/uMemory/grid/data"
    mkdir -p "$UHOME/uMemory/grid/templates"
    
    echo "✅ Grid system initialized"
}

# Load shortcode registry from system and user configurations
vb_load_shortcode_registry() {
    echo "📝 Loading shortcode registry..."
    
    VB_SHORTCODE_REGISTRY=""
    
    # Load system shortcodes
    if [[ -f "$SHORTCODES_CONFIG" ]] && command -v jq >/dev/null 2>&1; then
        local system_shortcodes=$(jq -r '.shortcodes[].name' "$SHORTCODES_CONFIG" 2>/dev/null | tr '\n' '|')
        VB_SHORTCODE_REGISTRY="$system_shortcodes"
        echo "📦 System shortcodes loaded: $(echo "$system_shortcodes" | tr '|' ' ')"
    fi
    
    # Load user shortcodes if available
    if [[ -f "$USER_SHORTCODES" ]] && command -v jq >/dev/null 2>&1; then
        local user_shortcodes=$(jq -r '.shortcodes[].name' "$USER_SHORTCODES" 2>/dev/null | tr '\n' '|')
        VB_SHORTCODE_REGISTRY="${VB_SHORTCODE_REGISTRY}${user_shortcodes}"
        echo "👤 User shortcodes loaded: $(echo "$user_shortcodes" | tr '|' ' ')"
    fi
    
    echo "✅ Shortcode registry ready"
}

# Set up system variables that integrate with uDOS ecosystem
vb_setup_system_variables() {
    echo "⚙️ Setting up system variables..."
    
    # Core system variables
    vb_set_enhanced_variable "UDOS_VERSION" "String" "1.0.0"
    vb_set_enhanced_variable "CURRENT_USER" "String" "$(whoami)"
    vb_set_enhanced_variable "UHOME" "String" "$UHOME"
    vb_set_enhanced_variable "CURRENT_LOCATION" "String" "$VB_CURRENT_LOCATION"
    vb_set_enhanced_variable "CURRENT_TIMEZONE" "String" "$VB_CURRENT_TIMEZONE"
    vb_set_enhanced_variable "GRID_POSITION" "String" "$VB_GRID_POSITION"
    vb_set_enhanced_variable "DATETIME" "String" "$(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    vb_set_enhanced_variable "TIMESTAMP" "String" "$(date +%Y%m%d-%H%M%S)"
    vb_set_enhanced_variable "DATE_TODAY" "String" "$(date +%Y-%m-%d)"
    
    # Mission context variables
    local current_mission=""
    if [[ -f "$UHOME/uMemory/state/current-mission.txt" ]]; then
        current_mission=$(cat "$UHOME/uMemory/state/current-mission.txt")
    fi
    vb_set_enhanced_variable "CURRENT_MISSION" "String" "${current_mission:-none}"
    
    echo "✅ System variables configured"
}

# === ENHANCED VARIABLE SYSTEM ===

# Enhanced variable storage with metadata
vb_set_enhanced_variable() {
    local var_name="$1"
    local var_type="$2"
    local var_value="$3"
    local var_metadata="${4:-system}"
    
    # Format: name:type:value:metadata:timestamp
    local timestamp=$(date +%s)
    local var_entry="${var_name}:${var_type}:${var_value}:${var_metadata}:${timestamp}"
    
    # Remove existing variable if it exists
    VB_ENHANCED_VARIABLES=$(echo "$VB_ENHANCED_VARIABLES" | tr '|' '\n' | grep -v "^${var_name}:" | tr '\n' '|')
    
    # Add new variable
    if [[ -z "$VB_ENHANCED_VARIABLES" ]]; then
        VB_ENHANCED_VARIABLES="$var_entry"
    else
        VB_ENHANCED_VARIABLES="${VB_ENHANCED_VARIABLES}${var_entry}|"
    fi
}

# Get enhanced variable with metadata
vb_get_enhanced_variable() {
    local var_name="$1"
    local var_info=$(echo "$VB_ENHANCED_VARIABLES" | tr '|' '\n' | grep "^${var_name}:")
    if [[ -n "$var_info" ]]; then
        echo "$var_info" | cut -d':' -f3
    fi
}

# === SHORTCODE PROCESSING ===

# Process shortcodes in VB expressions
vb_process_shortcodes() {
    local input="$1"
    local processed="$input"
    
    # Find all shortcodes: [SHORTCODE:params]
    while [[ "$processed" =~ \[([^:]+):([^\]]+)\] ]]; do
        local shortcode_name=$(echo "${BASH_REMATCH[1]}" | awk '{print toupper($0)}')
        local shortcode_params="${BASH_REMATCH[2]}"
        local shortcode_full="${BASH_REMATCH[0]}"
        
        echo "🔧 Processing shortcode: [$shortcode_name:$shortcode_params]"
        
        local result=$(vb_execute_shortcode "$shortcode_name" "$shortcode_params")
        processed="${processed/$shortcode_full/$result}"
    done
    
    echo "$processed"
}

# Execute a specific shortcode
vb_execute_shortcode() {
    local shortcode_name="$1"
    local params="$2"
    
    case "$shortcode_name" in
        "GRID")
            vb_shortcode_grid "$params"
            ;;
        "LOCATION")
            vb_shortcode_location "$params"
            ;;
        "TIME")
            vb_shortcode_time "$params"
            ;;
        "FILE")
            vb_shortcode_file "$params"
            ;;
        "TEMPLATE")
            vb_shortcode_template "$params"
            ;;
        "MISSION")
            vb_shortcode_mission "$params"
            ;;
        "SCRIPT")
            vb_shortcode_script "$params"
            ;;
        *)
            echo "SHORTCODE_ERROR:Unknown_$shortcode_name"
            ;;
    esac
}

# Grid-based shortcodes
vb_shortcode_grid() {
    local params="$1"
    
    case "$params" in
        "current")
            echo "$VB_GRID_POSITION"
            ;;
        "move:"*)
            local new_position="${params#move:}"
            vb_grid_move "$new_position"
            ;;
        "data:"*)
            local grid_pos="${params#data:}"
            vb_grid_get_data "$grid_pos"
            ;;
        *)
            echo "GRID_ERROR:Invalid_params"
            ;;
    esac
}

# Location-based shortcodes
vb_shortcode_location() {
    local params="$1"
    
    case "$params" in
        "current")
            echo "$VB_CURRENT_LOCATION"
            ;;
        "timezone")
            echo "$VB_CURRENT_TIMEZONE"
            ;;
        "coordinates")
            echo "$VB_GRID_POSITION"
            ;;
        "lookup:"*)
            local location="${params#lookup:}"
            vb_location_lookup "$location"
            ;;
        *)
            echo "LOCATION_ERROR:Invalid_params"
            ;;
    esac
}

# Time-based shortcodes
vb_shortcode_time() {
    local params="$1"
    
    case "$params" in
        "now")
            date +"%Y-%m-%d %H:%M:%S"
            ;;
        "timestamp")
            date +%Y%m%d-%H%M%S
            ;;
        "date")
            date +%Y-%m-%d
            ;;
        "filename")
            echo "$(date +%Y%m%d-%H%M%S)-${VB_GRID_POSITION}"
            ;;
        *)
            echo "TIME_ERROR:Invalid_params"
            ;;
    esac
}

# File-based shortcodes for dynamic filename generation
vb_shortcode_file() {
    local params="$1"
    
    case "$params" in
        "mission")
            local mission_name=$(vb_get_enhanced_variable "CURRENT_MISSION")
            echo "${mission_name:-unknown}-$(date +%Y%m%d)"
            ;;
        "log")
            echo "log-$(date +%Y%m%d-%H%M%S)-${VB_GRID_POSITION}"
            ;;
        "script")
            echo "script-$(date +%Y%m%d-%H%M%S)-${VB_GRID_POSITION}.vb"
            ;;
        "template:"*)
            local template_type="${params#template:}"
            echo "${template_type}-$(date +%Y%m%d)-${VB_GRID_POSITION}"
            ;;
        *)
            echo "FILE_ERROR:Invalid_params"
            ;;
    esac
}

# Template integration shortcodes
vb_shortcode_template() {
    local params="$1"
    
    case "$params" in
        "mission:"*)
            local mission_name="${params#mission:}"
            vb_generate_mission_template "$mission_name"
            ;;
        "milestone:"*)
            local milestone_name="${params#milestone:}"
            vb_generate_milestone_template "$milestone_name"
            ;;
        "list")
            ls "$UHOME/uTemplate/"*.md 2>/dev/null | xargs -n1 basename | sed 's/-template.md//' | tr '\n' ' '
            ;;
        *)
            echo "TEMPLATE_ERROR:Invalid_params"
            ;;
    esac
}

# === ENHANCED VB COMMANDS ===

# Enhanced PRINT command with shortcode and variable processing
vb_enhanced_print() {
    local args="$*"
    
    # Process shortcodes first
    local processed=$(vb_process_shortcodes "$args")
    
    # Then process variables
    local output=""
    local word
    for word in $processed; do
        if [[ "$word" =~ ^\$([a-zA-Z][a-zA-Z0-9_]*)$ ]]; then
            local var_name="${BASH_REMATCH[1]}"
            local var_value=$(vb_get_enhanced_variable "$var_name")
            if [[ -z "$var_value" ]]; then
                var_value="<undefined:$var_name>"
            fi
            output="$output$var_value"
        else
            output="$output$word"
        fi
    done
    
    echo "$output"
}

# Enhanced DIM command with system integration
vb_enhanced_dim() {
    local args="$*"
    
    # Parse enhanced DIM: DIM varname As type [= value] [GRID position] [PERSIST]
    if [[ "$args" =~ ^([a-zA-Z][a-zA-Z0-9_]*)[[:space:]]+As[[:space:]]+([a-zA-Z]+)([[:space:]]*=[[:space:]]*([^[:space:]]+))?([[:space:]]+GRID[[:space:]]+([A-Z][0-9]+))?([[:space:]]+PERSIST)?$ ]]; then
        local var_name="${BASH_REMATCH[1]}"
        local var_type="${BASH_REMATCH[2]}"
        local initial_value="${BASH_REMATCH[4]}"
        local grid_pos="${BASH_REMATCH[6]}"
        local persist="${BASH_REMATCH[7]}"
        
        # Process initial value for shortcodes
        if [[ -n "$initial_value" ]]; then
            initial_value=$(vb_process_shortcodes "$initial_value")
        fi
        
        local metadata="user"
        if [[ -n "$grid_pos" ]]; then
            metadata="grid:$grid_pos"
        fi
        if [[ -n "$persist" ]]; then
            metadata="$metadata:persist"
        fi
        
        vb_set_enhanced_variable "$var_name" "$var_type" "${initial_value:-}" "$metadata"
        
        echo "✅ Enhanced variable $var_name declared as $var_type"
        if [[ -n "$grid_pos" ]]; then
            echo "🗺️  Grid position: $grid_pos"
        fi
        if [[ -n "$persist" ]]; then
            echo "💾 Persistent storage enabled"
        fi
    else
        echo "❌ Invalid enhanced DIM syntax"
        echo "💡 Use: DIM varname As type [= value] [GRID position] [PERSIST]"
        return 1
    fi
}

# === UTILITY FUNCTIONS ===

# Grid movement and data functions
vb_grid_move() {
    local new_position="$1"
    
    if [[ "$new_position" =~ ^[A-Z][0-9]+$ ]]; then
        VB_GRID_POSITION="$new_position"
        vb_set_enhanced_variable "GRID_POSITION" "String" "$new_position"
        echo "🗺️  Moved to grid position: $new_position"
    else
        echo "❌ Invalid grid position format: $new_position"
        echo "💡 Use format: A1, B23, Z99, etc."
    fi
}

# Get data associated with grid position
vb_grid_get_data() {
    local grid_pos="$1"
    local data_file="$UHOME/uMemory/grid/data/${grid_pos}.json"
    
    if [[ -f "$data_file" ]]; then
        cat "$data_file"
    else
        echo "NO_DATA"
    fi
}

# Location lookup using dataset
vb_location_lookup() {
    local location="$1"
    
    if [[ -f "$LOCATION_MAP" ]] && command -v jq >/dev/null 2>&1; then
        jq -r --arg loc "$location" '.data[] | select(.city | test($loc; "i")) | "\(.city), \(.country) (\(.tile))"' "$LOCATION_MAP" 2>/dev/null | head -1
    else
        echo "LOOKUP_UNAVAILABLE"
    fi
}

# Generate mission template with current context
vb_generate_mission_template() {
    local mission_name="$1"
    local template_file="$UHOME/uTemplate/mission-template.md"
    local output_file="$UHOME/uMemory/missions/${mission_name}-$(date +%Y%m%d).md"
    
    if [[ -f "$template_file" ]]; then
        # Process template with current variables
        local processed_template=$(cat "$template_file")
        
        # Replace template variables with current values
        processed_template="${processed_template//\{\{mission_name\}\}/$mission_name}"
        processed_template="${processed_template//\{\{start_date\}\}/$(date +%Y-%m-%d)}"
        processed_template="${processed_template//\{\{location\}\}/$VB_CURRENT_LOCATION}"
        processed_template="${processed_template//\{\{timezone\}\}/$VB_CURRENT_TIMEZONE}"
        processed_template="${processed_template//\{\{generated_date\}\}/$(date -u +"%Y-%m-%dT%H:%M:%SZ")}"
        
        echo "$processed_template" > "$output_file"
        echo "✅ Mission template generated: $output_file"
    else
        echo "❌ Mission template not found: $template_file"
    fi
}

# Export enhanced functions
export -f vb_enhanced_init vb_enhanced_print vb_enhanced_dim vb_process_shortcodes vb_execute_shortcode

echo "🔷 Enhanced VB interpreter loaded with shortcode and mapping integration"
