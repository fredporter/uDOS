#!/bin/bash
# uDOS Template System - User Setup Processor v2.0
# Processes user setup template with shortcodes and variables

set -euo pipefail

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
SETUP_TEMPLATE="${UHOME}/uTemplate/user-setup-template.md"
TEMP_DIR="${UMEM}/temp/setup-$$"

# Color output helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }
dim() { echo -e "\033[2m$1\033[0m"; }

# Create temp directory
mkdir -p "$TEMP_DIR"

# Check bash version for associative array support
if [[ ${BASH_VERSION%%.*} -lt 4 ]]; then
    echo "❌ Template setup requires bash 4.0+ for associative arrays"
    echo "💡 Current bash version: $BASH_VERSION"
    echo "🔄 Falling back to legacy setup..."
    exit 1
fi

# Declare associative array for variables
declare -A SETUP_VARS

# Helper functions
show_intro() {
    local intro
    intro=$(sed -n '/\[SETUP_INTRO\]/,/\[\/SETUP_INTRO\]/p' "$SETUP_TEMPLATE" | sed '1d;$d')
    echo
    bold "$(echo "$intro" | head -n1)"
    echo "$(echo "$intro" | tail -n+2)"
    echo
}

# Parse input block and get user input
process_input_block() {
    local block_name="$1"
    local block_content
    local question variable validation default options help
    
    # Extract block content
    block_content=$(sed -n "/\[${block_name}\]/,/\[\\/${block_name}\]/p" "$SETUP_TEMPLATE" | sed '1d;$d')
    
    # Parse block properties
    question=$(echo "$block_content" | grep "^Question:" | cut -d' ' -f2-)
    variable=$(echo "$block_content" | grep "^Variable:" | cut -d' ' -f2 | tr -d '$')
    validation=$(echo "$block_content" | grep "^Validation:" | cut -d' ' -f2-)
    default=$(echo "$block_content" | grep "^Default:" | cut -d' ' -f2-)
    options=$(echo "$block_content" | grep "^Options:" | cut -d' ' -f2-)
    help=$(echo "$block_content" | grep "^Help:" | cut -d' ' -f2-)
    
    # Show help if available
    if [[ -n "$help" ]]; then
        dim "💡 $help"
    fi
    
    # Handle different input types
    if [[ "$validation" == *"boolean"* ]]; then
        process_boolean_input "$question" "$variable" "$default" "$options"
    elif [[ "$validation" == *"options"* ]]; then
        process_options_input "$question" "$variable" "$default" "$options"
    else
        process_text_input "$question" "$variable" "$default" "$validation"
    fi
    
    echo
}

# Process boolean input
process_boolean_input() {
    local question="$1" variable="$2" default="$3" options="$4"
    local prompt_suffix="(y/N)"
    local user_input
    
    if [[ "$default" == "true" ]]; then
        prompt_suffix="(Y/n)"
    fi
    
    while true; do
        read -p "❓ $question $prompt_suffix: " user_input
        
        case "${user_input,,}" in
            ""|"")
                SETUP_VARS["$variable"]="$default"
                break
                ;;
            y|yes|true)
                SETUP_VARS["$variable"]="true"
                break
                ;;
            n|no|false)
                SETUP_VARS["$variable"]="false"
                break
                ;;
            *)
                red "⚠️  Please enter y/yes/true or n/no/false"
                ;;
        esac
    done
    
    # Show confirmation
    local value="${SETUP_VARS[$variable]}"
    if [[ "$value" == "true" ]]; then
        green "✅ $variable: Enabled"
    else
        yellow "❌ $variable: Disabled"
    fi
}

# Process options input
process_options_input() {
    local question="$1" variable="$2" default="$3" options="$4"
    local user_input
    local options_array
    IFS=',' read -ra options_array <<< "$options"
    
    echo "📋 $question"
    for i in "${!options_array[@]}"; do
        local option="${options_array[$i]}"
        if [[ "$option" == "$default" ]]; then
            echo "   $((i+1)). $option (default)"
        else
            echo "   $((i+1)). $option"
        fi
    done
    
    while true; do
        read -p "Choose (1-${#options_array[@]}) or enter option name [default: $default]: " user_input
        
        if [[ -z "$user_input" ]]; then
            SETUP_VARS["$variable"]="$default"
            break
        elif [[ "$user_input" =~ ^[0-9]+$ ]] && (( user_input >= 1 && user_input <= ${#options_array[@]} )); then
            SETUP_VARS["$variable"]="${options_array[$((user_input-1))]}"
            break
        else
            # Check if input matches an option
            for option in "${options_array[@]}"; do
                if [[ "${user_input,,}" == "${option,,}" ]]; then
                    SETUP_VARS["$variable"]="$option"
                    break 2
                fi
            done
            red "⚠️  Invalid option. Please choose from: ${options}"
        fi
    done
    
    green "✅ $variable: ${SETUP_VARS[$variable]}"
}

# Process text input
process_text_input() {
    local question="$1" variable="$2" default="$3" validation="$4"
    local user_input
    local is_required=false
    
    if [[ "$validation" == *"required"* ]]; then
        is_required=true
    fi
    
    # Handle special defaults
    if [[ "$default" == '$USER' ]]; then
        default="$USER"
    elif [[ "$default" == '$SYSTEM_TIMEZONE' ]]; then
        default=$(timedatectl show --property=Timezone --value 2>/dev/null || date +%Z)
    fi
    
    while true; do
        if [[ -n "$default" ]]; then
            read -p "📝 $question [default: $default]: " user_input
            user_input="${user_input:-$default}"
        else
            read -p "📝 $question: " user_input
        fi
        
        # Validation
        if [[ "$is_required" == true ]] && [[ -z "$user_input" ]]; then
            red "⚠️  This field is required"
            continue
        fi
        
        if [[ "$validation" == *"email"* ]] && [[ -n "$user_input" ]]; then
            if ! [[ "$user_input" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
                red "⚠️  Please enter a valid email address"
                continue
            fi
        fi
        
        if [[ "$validation" == *"alphanumeric"* ]] && [[ -n "$user_input" ]]; then
            if ! [[ "$user_input" =~ ^[A-Za-z0-9]+$ ]]; then
                red "⚠️  Please use only letters and numbers"
                continue
            fi
        fi
        
        break
    done
    
    SETUP_VARS["$variable"]="$user_input"
    
    if [[ -n "$user_input" ]]; then
        green "✅ $variable: $user_input"
    else
        dim "⏭️  $variable: (not set)"
    fi
}

# Process variables block
process_variables() {
    echo
    bold "🔄 Processing system variables..."
    
    # Set basic system variables
    SETUP_VARS["SETUP_DATE"]=$(date '+%Y-%m-%d %H:%M:%S')
    SETUP_VARS["SETUP_TIMESTAMP"]=$(date '+%s')
    SETUP_VARS["UHOME_PATH"]="$UHOME"
    SETUP_VARS["UMEMORY_PATH"]="$UMEM"
    SETUP_VARS["SYSTEM_TIMEZONE"]=$(timedatectl show --property=Timezone --value 2>/dev/null || date +%Z)
    
    # Generate user ID
    local username="${SETUP_VARS[USERNAME]}"
    SETUP_VARS["USER_ID"]=$(echo "$username" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')
    
    # Process location data if location code provided
    local location_code="${SETUP_VARS[LOCATION_CODE]:-}"
    if [[ -n "$location_code" ]]; then
        local city_data_file="$UHOME/uTemplate/datasets/cityMap.json"
        if [[ -f "$city_data_file" ]]; then
            local location_data
            location_data=$(jq -r ".cities[] | select(.code==\"$location_code\")" "$city_data_file" 2>/dev/null || echo "{}")
            
            if [[ "$location_data" != "{}" ]]; then
                SETUP_VARS["CITY_NAME"]=$(echo "$location_data" | jq -r '.name // empty')
                SETUP_VARS["COUNTRY_CODE"]=$(echo "$location_data" | jq -r '.country // empty')
                SETUP_VARS["COORDINATES"]=$(echo "$location_data" | jq -r '.coordinates // empty')
                green "📍 Location data found: ${SETUP_VARS[CITY_NAME]}"
            else
                yellow "⚠️  Location code '$location_code' not found in database"
            fi
        fi
    fi
    
    # Handle timezone
    if [[ -z "${SETUP_VARS[TIMEZONE]:-}" ]]; then
        SETUP_VARS["TIMEZONE"]="${SETUP_VARS[SYSTEM_TIMEZONE]}"
    fi
    
    echo "✅ Variables processed successfully"
}

# Generate output from template
generate_output() {
    local output_name="$1"
    local output_file="$2"
    
    bold "📄 Generating $output_name..."
    
    # Extract output template
    local template_content
    template_content=$(sed -n "/\[OUTPUT_${output_name}\]/,/\[\/OUTPUT_${output_name}\]/p" "$SETUP_TEMPLATE" | sed '1d;$d')
    
    # Replace variables in template
    local processed_content="$template_content"
    for var in "${!SETUP_VARS[@]}"; do
        local value="${SETUP_VARS[$var]}"
        processed_content="${processed_content//\$$var/$value}"
    done
    
    # Process conditional blocks
    processed_content=$(echo "$processed_content" | while IFS= read -r line; do
        if [[ "$line" =~ ^\$\(\ \[\[.*\]\]\ \&\&\ echo\ \".*\"\ \)$ ]]; then
            # Extract condition and content
            local condition=$(echo "$line" | sed 's/^\$( \[\[ *//;s/ *\]\] && echo ".*" )$//')
            local content=$(echo "$line" | sed 's/^.*echo "\(.*\)" )$/\1/')
            
            # Evaluate condition (simple variable checks)
            if eval "[[ $condition ]]" 2>/dev/null; then
                echo "$content"
            fi
        else
            echo "$line"
        fi
    done)
    
    # Save to file
    echo "$processed_content" > "$output_file"
    green "✅ $output_name saved to: $output_file"
}

# Main setup process
main() {
    clear
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                     🎭 uDOS User Setup v2.0                  ║"
    echo "║              Template-Driven Configuration System             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    
    show_intro
    
    # Process all input blocks
    bold "📋 Collecting user information..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    process_input_block "INPUT_USERNAME"
    process_input_block "INPUT_FULLNAME"
    process_input_block "INPUT_EMAIL"
    
    echo
    bold "🌍 Location & Time Settings"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    process_input_block "INPUT_LOCATION"
    process_input_block "INPUT_TIMEZONE"
    
    echo
    bold "⚙️ System Preferences"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    process_input_block "INPUT_THEME"
    process_input_block "INPUT_DEBUG_MODE"
    process_input_block "INPUT_AUTO_BACKUP"
    process_input_block "INPUT_AI_COMPANION"
    
    echo
    bold "🎯 Development Preferences"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    process_input_block "INPUT_DEFAULT_ROLE"
    process_input_block "INPUT_AUTO_PACKAGES"
    process_input_block "INPUT_VSCODE_INTEGRATION"
    
    # Process variables
    process_variables
    
    echo
    bold "📄 Generating configuration files..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Create output files
    mkdir -p "${UMEM}/user" "${UMEM}/config" "${UMEM}/missions"
    
    generate_output "USER_IDENTITY" "${UMEM}/user/identity.md"
    generate_output "CONFIG_VARS" "${UMEM}/config/setup-vars.sh"
    generate_output "FIRST_MISSION" "${UMEM}/missions/001-welcome-mission.md"
    
    echo
    green "🎉 Setup completed successfully!"
    echo
    bold "Next steps:"
    echo "1. 🔍 Run: ucode CHECK all"
    echo "2. 📊 Try: ucode DASH live"
    echo "3. 📖 Read: docs/user-manual.md"
    echo
    
    # Cleanup
    rm -rf "$TEMP_DIR"
}

# Export variables for use in other scripts
export_setup_vars() {
    local config_file="${UMEM}/config/setup-vars.sh"
    if [[ -f "$config_file" ]]; then
        source "$config_file"
    fi
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
