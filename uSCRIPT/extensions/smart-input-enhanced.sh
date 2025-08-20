#!/bin/bash

# uDOS Smart Input Enhanced v2.0 - Extension
# Advanced input collection, validation, and form generation system
# Enhanced from core smart-input.sh with form builders and AI-powered suggestions

set -euo pipefail

# Extension metadata
readonly EXTENSION_ID="smart-input-enhanced"
readonly EXTENSION_VERSION="2.0.0"
readonly EXTENSION_NAME="Smart Input Enhanced"

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly UCORE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
readonly PROJECT_ROOT="$(dirname "$UCORE_DIR")"
readonly FORMS_DIR="$PROJECT_ROOT/uMEMORY/forms"
readonly TEMPLATES_DIR="$SCRIPT_DIR/templates/forms"

# Colors for enhanced UI
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly MAGENTA='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly BOLD='\033[1m'
readonly DIM='\033[2m'
readonly ITALIC='\033[3m'
readonly UNDERLINE='\033[4m'
readonly BLINK='\033[5m'
readonly NC='\033[0m'

# Enhanced prompt styles
readonly PROMPT_SUCCESS="✅"
readonly PROMPT_ERROR="❌"
readonly PROMPT_WARNING="⚠️"
readonly PROMPT_INFO="ℹ️"
readonly PROMPT_QUESTION="❓"
readonly PROMPT_INPUT="📝"
readonly PROMPT_SELECT="🔽"
readonly PROMPT_MULTI="☑️"
readonly PROMPT_WIZARD="🧙‍♂️"

# Logging function
log_input_action() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] SMART-INPUT: $message" >> "$PROJECT_ROOT/uMEMORY/logs/input.log"
}

# Initialize enhanced input system
init_smart_input_system() {
    mkdir -p "$FORMS_DIR"/{active,completed,templates,drafts}
    mkdir -p "$TEMPLATES_DIR"/{basic,advanced,wizard,validation}
    mkdir -p "$PROJECT_ROOT/uMEMORY/logs"
    
    touch "$PROJECT_ROOT/uMEMORY/logs/input.log"
    log_input_action "Smart Input Enhanced system initialized"
}

# Enhanced prompt with validation and suggestions
smart_prompt() {
    local prompt_text="$1"
    local validation_type="${2:-text}"
    local suggestions="${3:-}"
    local required="${4:-true}"
    local help_text="${5:-}"
    
    local input=""
    local attempts=0
    local max_attempts=3
    
    while [[ $attempts -lt $max_attempts ]]; do
        # Display prompt with style
        echo -ne "${CYAN}${PROMPT_INPUT} ${prompt_text}${NC}"
        
        # Show suggestions if provided
        if [[ -n "$suggestions" ]]; then
            echo -ne "${DIM} (Suggestions: $suggestions)${NC}"
        fi
        
        # Show help if provided
        if [[ -n "$help_text" ]]; then
            echo -ne "${DIM} 💡 $help_text${NC}"
        fi
        
        echo -ne "${WHITE}\n❯ ${NC}"
        read -r input
        
        # Validation
        if validate_input "$input" "$validation_type" "$required"; then
            echo -e "${GREEN}${PROMPT_SUCCESS} Valid input accepted${NC}"
            echo "$input"
            log_input_action "Valid input collected: $validation_type"
            return 0
        else
            echo -e "${RED}${PROMPT_ERROR} Invalid input. Please try again.${NC}"
            ((attempts++))
            
            if [[ $attempts -lt $max_attempts ]]; then
                show_validation_help "$validation_type"
            fi
        fi
    done
    
    echo -e "${RED}${PROMPT_ERROR} Maximum attempts reached. Using default or empty value.${NC}"
    log_input_action "Input validation failed after $max_attempts attempts"
    echo ""
    return 1
}

# Advanced input validation
validate_input() {
    local input="$1"
    local type="$2"
    local required="$3"
    
    # Check if required and empty
    if [[ "$required" == "true" && -z "$input" ]]; then
        return 1
    fi
    
    case "$type" in
        "email")
            [[ "$input" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]
            ;;
        "url")
            [[ "$input" =~ ^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$ ]]
            ;;
        "number")
            [[ "$input" =~ ^[0-9]+$ ]]
            ;;
        "float")
            [[ "$input" =~ ^[0-9]+\.?[0-9]*$ ]]
            ;;
        "date")
            [[ "$input" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]
            ;;
        "time")
            [[ "$input" =~ ^[0-9]{2}:[0-9]{2}(:[0-9]{2})?$ ]]
            ;;
        "phone")
            [[ "$input" =~ ^[+]?[0-9\-\(\)\ ]{10,}$ ]]
            ;;
        "alphanum")
            [[ "$input" =~ ^[a-zA-Z0-9]+$ ]]
            ;;
        "filename")
            [[ "$input" =~ ^[a-zA-Z0-9._-]+$ ]]
            ;;
        "path")
            [[ "$input" =~ ^[a-zA-Z0-9._/-]+$ ]]
            ;;
        "json")
            echo "$input" | jq . >/dev/null 2>&1
            ;;
        "text"|*)
            true  # Always valid for basic text
            ;;
    esac
}

# Show validation help
show_validation_help() {
    local type="$1"
    
    echo -e "${YELLOW}${PROMPT_INFO} Validation Help:${NC}"
    case "$type" in
        "email") echo -e "  Format: user@domain.com" ;;
        "url") echo -e "  Format: https://example.com" ;;
        "number") echo -e "  Numbers only: 123" ;;
        "float") echo -e "  Decimal numbers: 123.45" ;;
        "date") echo -e "  Format: YYYY-MM-DD (2024-01-15)" ;;
        "time") echo -e "  Format: HH:MM or HH:MM:SS (14:30:00)" ;;
        "phone") echo -e "  Phone number with optional +, -, (, ), spaces" ;;
        "alphanum") echo -e "  Letters and numbers only" ;;
        "filename") echo -e "  Valid filename characters only" ;;
        "path") echo -e "  Valid file path format" ;;
        "json") echo -e "  Valid JSON format" ;;
    esac
    echo ""
}

# Multi-choice selection with enhanced UI
smart_select() {
    local prompt="$1"
    local options_string="$2"
    local allow_multiple="${3:-false}"
    local required="${4:-true}"
    
    # Convert options string to array
    IFS='|' read -ra options <<< "$options_string"
    
    echo -e "${CYAN}${PROMPT_SELECT} $prompt${NC}"
    echo ""
    
    # Display options
    for i in "${!options[@]}"; do
        local option_num=$((i + 1))
        echo -e "  ${WHITE}$option_num)${NC} ${options[i]}"
    done
    
    echo ""
    
    if [[ "$allow_multiple" == "true" ]]; then
        echo -e "${DIM}Enter multiple numbers separated by commas (e.g., 1,3,5)${NC}"
    else
        echo -e "${DIM}Enter the number of your choice${NC}"
    fi
    
    local selection=""
    echo -ne "${WHITE}❯ ${NC}"
    read -r selection
    
    if [[ "$allow_multiple" == "true" ]]; then
        # Handle multiple selections
        IFS=',' read -ra selected_nums <<< "$selection"
        local results=()
        
        for num in "${selected_nums[@]}"; do
            num=$(echo "$num" | tr -d ' ')  # Remove spaces
            if [[ "$num" =~ ^[0-9]+$ ]] && [[ $num -ge 1 ]] && [[ $num -le ${#options[@]} ]]; then
                results+=("${options[$((num-1))]}")
            fi
        done
        
        if [[ ${#results[@]} -gt 0 ]]; then
            printf '%s\n' "${results[@]}"
            log_input_action "Multi-select completed: ${#results[@]} items"
            return 0
        fi
    else
        # Handle single selection
        if [[ "$selection" =~ ^[0-9]+$ ]] && [[ $selection -ge 1 ]] && [[ $selection -le ${#options[@]} ]]; then
            echo "${options[$((selection-1))]}"
            log_input_action "Selection completed: ${options[$((selection-1))]}"
            return 0
        fi
    fi
    
    echo -e "${RED}${PROMPT_ERROR} Invalid selection${NC}"
    log_input_action "Invalid selection attempted"
    return 1
}

# Form builder system
create_form() {
    local form_name="$1"
    local form_type="${2:-basic}"
    
    echo -e "${MAGENTA}${PROMPT_WIZARD} Form Builder - Creating '$form_name'${NC}"
    echo ""
    
    local form_file="$FORMS_DIR/drafts/${form_name}-$(date +%s).json"
    
    # Initialize form structure
    cat > "$form_file" << EOF
{
  "form_id": "$form_name",
  "created_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "type": "$form_type",
  "title": "",
  "description": "",
  "fields": [],
  "validation": {},
  "actions": {}
}
EOF
    
    # Interactive form building
    local title
    title=$(smart_prompt "Form Title" "text" "" "true" "Brief descriptive title for the form")
    
    local description
    description=$(smart_prompt "Form Description" "text" "" "false" "Optional detailed description")
    
    # Update form metadata
    local updated_form
    updated_form=$(jq --arg title "$title" --arg desc "$description" \
        '.title = $title | .description = $desc' "$form_file")
    echo "$updated_form" > "$form_file"
    
    # Build fields interactively
    build_form_fields "$form_file"
    
    echo -e "${GREEN}${PROMPT_SUCCESS} Form '$form_name' created successfully!${NC}"
    echo -e "Location: $form_file"
    
    log_input_action "Form created: $form_name"
}

# Interactive field builder
build_form_fields() {
    local form_file="$1"
    
    echo -e "${CYAN}Building form fields...${NC}"
    echo ""
    
    while true; do
        echo -e "${WHITE}Add a field to the form:${NC}"
        
        local field_name
        field_name=$(smart_prompt "Field Name" "alphanum" "name,email,message,phone" "true" "Internal field identifier")
        
        local field_label
        field_label=$(smart_prompt "Field Label" "text" "" "true" "User-visible label")
        
        local field_type
        field_type=$(smart_select "Field Type" "text|email|number|date|select|multiselect|textarea|checkbox" "false" "true")
        
        local required
        required=$(smart_select "Required Field?" "yes|no" "false" "true")
        
        local validation=""
        if [[ "$field_type" == "email" ]]; then
            validation="email"
        elif [[ "$field_type" == "number" ]]; then
            validation="number"
        elif [[ "$field_type" == "date" ]]; then
            validation="date"
        fi
        
        # Add field to form
        local field_json
        field_json=$(jq -n \
            --arg name "$field_name" \
            --arg label "$field_label" \
            --arg type "$field_type" \
            --arg req "$required" \
            --arg val "$validation" \
            '{
                name: $name,
                label: $label,
                type: $type,
                required: ($req == "yes"),
                validation: $val,
                options: []
            }')
        
        # Update form file
        local updated_form
        updated_form=$(jq --argjson field "$field_json" '.fields += [$field]' "$form_file")
        echo "$updated_form" > "$form_file"
        
        echo -e "${GREEN}${PROMPT_SUCCESS} Field '$field_name' added${NC}"
        echo ""
        
        local continue_adding
        continue_adding=$(smart_select "Add another field?" "yes|no" "false" "true")
        
        if [[ "$continue_adding" == "no" ]]; then
            break
        fi
    done
}

# Form execution engine
execute_form() {
    local form_file="$1"
    local output_file="${2:-$FORMS_DIR/completed/form-response-$(date +%s).json}"
    
    if [[ ! -f "$form_file" ]]; then
        echo -e "${RED}${PROMPT_ERROR} Form file not found: $form_file${NC}"
        return 1
    fi
    
    local form_title
    form_title=$(jq -r '.title' "$form_file")
    
    local form_description
    form_description=$(jq -r '.description' "$form_file")
    
    # Display form header
    echo ""
    echo -e "${BOLD}${UNDERLINE}$form_title${NC}"
    if [[ "$form_description" != "null" && -n "$form_description" ]]; then
        echo -e "${DIM}$form_description${NC}"
    fi
    echo ""
    
    # Initialize response object
    local response_json='{}'
    response_json=$(jq --arg form_id "$(jq -r '.form_id' "$form_file")" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '. + {form_id: $form_id, submitted_at: $timestamp, responses: {}}' <<< "$response_json")
    
    # Process each field
    local field_count
    field_count=$(jq '.fields | length' "$form_file")
    
    for ((i=0; i<field_count; i++)); do
        local field
        field=$(jq ".fields[$i]" "$form_file")
        
        local field_name
        field_name=$(jq -r '.name' <<< "$field")
        
        local field_label
        field_label=$(jq -r '.label' <<< "$field")
        
        local field_type
        field_type=$(jq -r '.type' <<< "$field")
        
        local field_required
        field_required=$(jq -r '.required' <<< "$field")
        
        local field_validation
        field_validation=$(jq -r '.validation' <<< "$field")
        
        local response=""
        
        case "$field_type" in
            "select"|"multiselect")
                local options
                options=$(jq -r '.options | join("|")' <<< "$field")
                local allow_multi="false"
                [[ "$field_type" == "multiselect" ]] && allow_multi="true"
                
                response=$(smart_select "$field_label" "$options" "$allow_multi" "$field_required")
                ;;
            "checkbox")
                response=$(smart_select "$field_label" "yes|no" "false" "$field_required")
                ;;
            *)
                local validation_type="text"
                [[ "$field_validation" != "null" && -n "$field_validation" ]] && validation_type="$field_validation"
                
                response=$(smart_prompt "$field_label" "$validation_type" "" "$field_required")
                ;;
        esac
        
        # Add response to JSON
        response_json=$(jq --arg key "$field_name" --arg val "$response" \
            '.responses[$key] = $val' <<< "$response_json")
        
        echo ""
    done
    
    # Save response
    echo "$response_json" > "$output_file"
    
    echo -e "${GREEN}${PROMPT_SUCCESS} Form completed successfully!${NC}"
    echo -e "Response saved to: $output_file"
    
    log_input_action "Form executed: $form_title -> $output_file"
    echo "$output_file"
}

# Wizard system for complex workflows
start_wizard() {
    local wizard_name="$1"
    local wizard_config="${2:-}"
    
    echo -e "${MAGENTA}${PROMPT_WIZARD} Starting Wizard: $wizard_name${NC}"
    echo ""
    
    case "$wizard_name" in
        "mission-creation")
            mission_creation_wizard
            ;;
        "project-setup")
            project_setup_wizard
            ;;
        "template-builder")
            template_builder_wizard
            ;;
        "system-config")
            system_config_wizard
            ;;
        *)
            echo -e "${YELLOW}${PROMPT_WARNING} Unknown wizard: $wizard_name${NC}"
            echo -e "Available wizards: mission-creation, project-setup, template-builder, system-config"
            return 1
            ;;
    esac
}

# Generate uHEX code for file naming
generate_uhex() {
    openssl rand -hex 4 | tr '[:lower:]' '[:upper:]' 2>/dev/null || printf "%08X" $((RANDOM * RANDOM))
}

# Mission creation wizard
mission_creation_wizard() {
    echo -e "${CYAN}Mission Creation Wizard${NC}"
    echo -e "${DIM}Let's create a new mission step by step${NC}"
    echo ""
    
    local mission_title
    mission_title=$(smart_prompt "Mission Title" "text" "Learn,Build,Explore,Research" "true" "What do you want to accomplish?")
    
    local mission_type
    mission_type=$(smart_select "Mission Type" "learning|project|research|maintenance|exploration" "false" "true")
    
    local priority
    priority=$(smart_select "Priority Level" "low|medium|high|urgent" "false" "true")
    
    local estimated_duration
    estimated_duration=$(smart_prompt "Estimated Duration" "text" "1 hour,1 day,1 week,1 month" "false" "How long do you think this will take?")
    
    local mission_description
    mission_description=$(smart_prompt "Mission Description" "text" "" "false" "Detailed description of what needs to be done")
    
    # Create mission file with uHEX naming convention
    local uhex_code=$(generate_uhex)
    local clean_title="${mission_title//[^a-zA-Z0-9]/-}"
    local mission_file="$PROJECT_ROOT/uMEMORY/user/missions/uTASK-${uhex_code}-${clean_title}.md"
    
    # Ensure directory exists
    mkdir -p "$PROJECT_ROOT/uMEMORY/user/missions"
    
    cat > "$mission_file" << EOF
---
mission_id: "uTASK-${uhex_code}"
title: "$mission_title"
type: "$mission_type"
priority: "$priority"
status: "active"
created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
estimated_duration: "$estimated_duration"
progress: 0
---

# Mission: $mission_title

## Description
$mission_description

## Type
$mission_type

## Priority
$priority

## Estimated Duration
$estimated_duration

## Progress
- [ ] Initial planning
- [ ] Implementation
- [ ] Testing/Validation
- [ ] Completion

## Tasks
*Add specific tasks here as you break down the mission*

## Resources
*Add links, files, or references needed for this mission*

## Notes
*Add progress notes, obstacles, insights as you work*

---
*Created: $(date)*  
*Mission ID: uTASK-${uhex_code}*
EOF
    
    echo -e "${GREEN}${PROMPT_SUCCESS} Mission created: $mission_file${NC}"
    log_input_action "Mission created via wizard: $mission_title"
}

# List available forms and wizards
list_smart_features() {
    echo -e "${BOLD}🧠 Smart Input Enhanced Features${NC}"
    echo ""
    
    echo -e "${CYAN}📋 FORMS${NC}"
    echo -e "  • create_form <name> [type] - Build interactive forms"
    echo -e "  • execute_form <form_file> [output] - Run form and collect responses"
    echo -e "  • validate_input <input> <type> - Advanced input validation"
    echo ""
    
    echo -e "${CYAN}🧙‍♂️ WIZARDS${NC}"
    echo -e "  • mission-creation - Create new missions step-by-step"
    echo -e "  • project-setup - Initialize new projects"
    echo -e "  • template-builder - Build custom templates"
    echo -e "  • system-config - Configure system settings"
    echo ""
    
    echo -e "${CYAN}📝 INPUT TYPES${NC}"
    echo -e "  • text, email, url, number, float, date, time"
    echo -e "  • phone, alphanum, filename, path, json"
    echo -e "  • select, multiselect, checkbox, textarea"
    echo ""
    
    echo -e "${CYAN}💡 FEATURES${NC}"
    echo -e "  • Smart validation with helpful error messages"
    echo -e "  • Context-aware suggestions"
    echo -e "  • Multi-step wizards for complex workflows"
    echo -e "  • Form builder with JSON export"
    echo -e "  • Enhanced UI with colors and symbols"
    echo ""
    
    # Show existing forms
    if [[ -d "$FORMS_DIR" ]]; then
        local form_count
        form_count=$(find "$FORMS_DIR" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
        if [[ $form_count -gt 0 ]]; then
            echo -e "${CYAN}📁 EXISTING FORMS${NC}"
            find "$FORMS_DIR" -name "*.json" 2>/dev/null | while read -r form; do
                local form_title
                form_title=$(jq -r '.title // "Untitled"' "$form" 2>/dev/null || echo "Untitled")
                echo -e "  • $(basename "$form"): $form_title"
            done
            echo ""
        fi
    fi
}

# Main command dispatcher
main() {
    init_smart_input_system
    
    case "${1:-LIST}" in
        "PROMPT")
            [[ $# -lt 2 ]] && { echo "Usage: smart-input-enhanced.sh PROMPT <text> [type] [suggestions] [required] [help]" >&2; exit 1; }
            smart_prompt "$2" "${3:-text}" "${4:-}" "${5:-true}" "${6:-}"
            ;;
        "SELECT")
            [[ $# -lt 3 ]] && { echo "Usage: smart-input-enhanced.sh SELECT <prompt> <options> [multi] [required]" >&2; exit 1; }
            smart_select "$2" "$3" "${4:-false}" "${5:-true}"
            ;;
        "FORM")
            case "${2:-}" in
                "CREATE")
                    [[ $# -lt 3 ]] && { echo "Usage: smart-input-enhanced.sh FORM CREATE <name> [type]" >&2; exit 1; }
                    create_form "$3" "${4:-basic}"
                    ;;
                "EXECUTE")
                    [[ $# -lt 3 ]] && { echo "Usage: smart-input-enhanced.sh FORM EXECUTE <form_file> [output]" >&2; exit 1; }
                    execute_form "$3" "${4:-}"
                    ;;
                *)
                    echo "Form subcommands: CREATE, EXECUTE"
                    ;;
            esac
            ;;
        "WIZARD")
            [[ $# -lt 2 ]] && { echo "Usage: smart-input-enhanced.sh WIZARD <name> [config]" >&2; exit 1; }
            start_wizard "$2" "${3:-}"
            ;;
        "VALIDATE")
            [[ $# -lt 3 ]] && { echo "Usage: smart-input-enhanced.sh VALIDATE <input> <type> [required]" >&2; exit 1; }
            validate_input "$2" "$3" "${4:-true}"
            ;;
        "LIST"|*)
            list_smart_features
            ;;
    esac
}

# Execute main with all arguments
main "$@"
