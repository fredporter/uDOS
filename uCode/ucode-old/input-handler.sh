#!/bin/bash
# uDOS Input Handler v1.0.0
# Integrates predictive shortcode input system with main uCode shell
# Provides seamless [ trigger for shortcode selection and forms

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"

# Source input system
source "$SCRIPT_DIR/input-system.sh"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

# Input handling configuration
TRIGGER_CHAR="["
COMPLETION_TIMEOUT=3
MAX_SUGGESTIONS=8

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🎯 ENHANCED INPUT LOOP WITH PREDICTIVE FEATURES
# ═══════════════════════════════════════════════════════════════════════════════════════

# input prompt with shortcode detection
enhanced_input_prompt() {
    local prompt_text="${1:-🌀}"
    local current_input=""
    local suggestions=()
    local show_suggestions=false
    local selected_suggestion=0
    
    while true; do
        # Clear line and show prompt
        printf "\r\033[K"
        echo -ne "${CYAN}${prompt_text} ${NC}"
        
        # Show current input
        echo -n "$current_input"
        
        # Show suggestions if triggered
        if [[ "$show_suggestions" == true ]] && [[ ${#suggestions[@]} -gt 0 ]]; then
            echo
            show_inline_suggestions suggestions "$selected_suggestion"
            # Move cursor back up
            printf "\033[%dA" $((${#suggestions[@]} + 1))
            # Position cursor at end of input
            printf "\033[%dC" $((${#prompt_text} + ${#current_input} + 2))
        fi
        
        # Read single character
        read -rsn1 key
        
        case "$key" in
            $'\n'|$'\r')  # Enter - execute input
                if [[ "$show_suggestions" == true ]] && [[ ${#suggestions[@]} -gt 0 ]]; then
                    # Use selected suggestion
                    current_input="${suggestions[$selected_suggestion]}"
                    show_suggestions=false
                fi
                echo
                echo "$current_input"
                return 0
                ;;
            $'\t')  # Tab - show/cycle suggestions
                if [[ "$current_input" =~ ^\[ ]]; then
                    if [[ "$show_suggestions" == false ]]; then
                        update_suggestions current_input suggestions
                        show_suggestions=true
                        selected_suggestion=0
                    else
                        # Cycle through suggestions
                        ((selected_suggestion++))
                        [[ $selected_suggestion -ge ${#suggestions[@]} ]] && selected_suggestion=0
                    fi
                fi
                ;;
            $'\e')  # Escape sequence (arrow keys)
                read -rsn2 key
                case "$key" in
                    "[A")  # Up arrow
                        if [[ "$show_suggestions" == true ]] && [[ ${#suggestions[@]} -gt 0 ]]; then
                            ((selected_suggestion--))
                            [[ $selected_suggestion -lt 0 ]] && selected_suggestion=$((${#suggestions[@]} - 1))
                        fi
                        ;;
                    "[B")  # Down arrow
                        if [[ "$show_suggestions" == true ]] && [[ ${#suggestions[@]} -gt 0 ]]; then
                            ((selected_suggestion++))
                            [[ $selected_suggestion -ge ${#suggestions[@]} ]] && selected_suggestion=0
                        fi
                        ;;
                    "[C")  # Right arrow - accept suggestion
                        if [[ "$show_suggestions" == true ]] && [[ ${#suggestions[@]} -gt 0 ]]; then
                            current_input="${suggestions[$selected_suggestion]}"
                            show_suggestions=false
                        fi
                        ;;
                esac
                ;;
            $'\x7f'|$'\b')  # Backspace
                if [[ ${#current_input} -gt 0 ]]; then
                    current_input="${current_input%?}"
                    # Reset suggestions if we're no longer in shortcode
                    [[ ! "$current_input" =~ ^\[ ]] && show_suggestions=false
                fi
                ;;
            $'\x03')  # Ctrl+C
                echo
                return 1
                ;;
            *)  # Regular character
                current_input+="$key"
                
                # Trigger shortcode suggestions
                if [[ "$current_input" == "[" ]]; then
                    show_suggestions=true
                    update_suggestions current_input suggestions
                    selected_suggestion=0
                elif [[ "$current_input" =~ ^\[ ]]; then
                    update_suggestions current_input suggestions
                    [[ ${#suggestions[@]} -eq 0 ]] && show_suggestions=false
                else
                    show_suggestions=false
                fi
                ;;
        esac
    done
}

# Update suggestions based on current input
update_suggestions() {
    local current_input="$1"
    local -n suggestions_ref=$2
    
    suggestions_ref=()
    
    # Extract partial shortcode for matching
    local partial=""
    if [[ "$current_input" =~ ^\[([A-Za-z]*) ]]; then
        partial="${BASH_REMATCH[1]}"
    fi
    
    # Get suggestions from input system
    local suggestions_json
    suggestions_json=$(get_shortcode_suggestions "$partial" "$MAX_SUGGESTIONS")
    
    # Parse suggestions into array
    while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            local example=$(echo "$line" | jq -r '.examples' 2>/dev/null || echo "")
            [[ -n "$example" ]] && suggestions_ref+=("$example")
        fi
    done < <(echo "$suggestions_json" | jq -c '.[]' 2>/dev/null || echo "")
}

# Show inline suggestions
show_inline_suggestions() {
    local -n suggestions_ref=$1
    local selected="$2"
    
    echo -e "\n${DIM}Suggestions:${NC}"
    for i in "${!suggestions_ref[@]}"; do
        local prefix="  "
        local style=""
        
        if [[ $i -eq $selected ]]; then
            prefix="${GREEN}▶ "
            style="${BOLD}${GREEN}"
        fi
        
        echo -e "${prefix}${style}${suggestions_ref[$i]}${NC}"
    done
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🔧 FORM INTEGRATION WITH UCODE COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════════════

# command processing with datagets
process_command_with_forms() {
    local input="$1"
    
    # Check for DATAGET command
    if [[ "$input" =~ ^ucode\ DATAGET\ (.+)$ ]]; then
        local dataget_name="${BASH_REMATCH[1]}"
        local dataget_file="$UHOME/uTemplate/datagets/${dataget_name}.json"
        "MISSION")
            case "${args%% *}" in
                "CREATE"|"NEW")
                    echo -e "${CYAN}🎯 Creating new mission with form...${NC}"
                    interactive_form "$(cat "$UHOME/uTemplate/forms/mission-create.json")" "$UHOME/uMemory/forms/mission-$(date +%Y%m%d-%H%M%S).json"
                    ;;
                *)
                    return 2
                    ;;
            esac
            ;;
        "CONFIG"|"CONFIGURE")
            echo -e "${CYAN}⚙️ System configuration form...${NC}"
            interactive_form "$(cat "$UHOME/uTemplate/forms/system-config.json")" "$UHOME/uMemory/forms/system-config-$(date +%Y%m%d-%H%M%S).json"
            ;;
        "FORM")
            # Direct form processing
            local form_name="$args"
            local form_file="$UHOME/uTemplate/forms/${form_name}.json"
            
            if [[ -f "$form_file" ]]; then
                echo -e "${CYAN}📝 Processing form: $form_name${NC}"
                interactive_form "$(cat "$form_file")" "$UHOME/uMemory/forms/${form_name}-$(date +%Y%m%d-%H%M%S).json"
            else
                echo -e "${RED}❌ Form not found: $form_name${NC}"
                echo -e "${DIM}Available forms:${NC}"
                find "$UHOME/uTemplate/forms" -name "*.json" -exec basename {} .json \; 2>/dev/null || echo "None found"
            fi
            ;;
        "INPUT")
            # Launch input system selector
            case "$args" in
                "SHORTCODE"|"SC")
                    interactive_shortcode_selector ""
                    ;;
                "DEMO")
                    demo_input_system
                    ;;
                *)
                    echo -e "${CYAN}🎯 uDOS Input System${NC}"
                    echo
                    echo "Available commands:"
                    echo "  INPUT SHORTCODE - Launch shortcode selector"
                    echo "  INPUT DEMO      - Run input system demonstration"
                    echo "  [               - Trigger predictive shortcode input"
                    ;;
            esac
            ;;
        *)
            return 2  # Not handled by input system
            ;;
    esac
    
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🎯 SHORTCODE DETECTION AND PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════════════

# Detect if input should trigger shortcode selector
should_trigger_shortcode_selector() {
    local input="$1"
    
    # Trigger on single [ character
    [[ "$input" == "[" ]] && return 0
    
    # Trigger on incomplete shortcode patterns
    [[ "$input" =~ ^\[[A-Z]*$ ]] && return 0
    
    return 1
}

# Process shortcode input
process_shortcode_input() {
    local input="$1"
    
    # If it's just [, launch selector
    if [[ "$input" == "[" ]]; then
        echo -e "${CYAN}🔍 Launching shortcode selector...${NC}"
        local selected_shortcode
        selected_shortcode=$(interactive_shortcode_selector "")
        
        if [[ $? -eq 0 ]] && [[ -n "$selected_shortcode" ]]; then
            echo -e "${GREEN}✅ Selected: $selected_shortcode${NC}"
            # Process the selected shortcode
            if [[ -f "$SCRIPT_DIR/processor.sh" ]]; then
                bash "$SCRIPT_DIR/processor.sh" process "$selected_shortcode"
            fi
        fi
        return 0
    fi
    
    # If it's a complete shortcode, process normally
    if [[ "$input" =~ ^\[.*\]$ ]]; then
        if [[ -f "$SCRIPT_DIR/processor.sh" ]]; then
            bash "$SCRIPT_DIR/processor.sh" process "$input"
        fi
        return 0
    fi
    
    # If it's an incomplete shortcode, offer completion
    if [[ "$input" =~ ^\[ ]]; then
        echo -e "${YELLOW}🔍 Incomplete shortcode detected...${NC}"
        local partial="${input#[}"
        local selected_shortcode
        selected_shortcode=$(interactive_shortcode_selector "$partial")
        
        if [[ $? -eq 0 ]] && [[ -n "$selected_shortcode" ]]; then
            echo -e "${GREEN}✅ Completed: $selected_shortcode${NC}"
            # Process the completed shortcode
            if [[ -f "$SCRIPT_DIR/processor.sh" ]]; then
                bash "$SCRIPT_DIR/processor.sh" process "$selected_shortcode"
            fi
        fi
        return 0
    fi
    
    return 1
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🎯 MAIN INTEGRATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════════

# Initialize input system integration
init_input_integration() {
    log_input "Initializing input system integration..."
    
    # Initialize datasets
    init_shortcode_datasets
    
    # Check for required files
    local missing_files=()
    
    [[ ! -f "$SCRIPT_DIR/input-system.sh" ]] && missing_files+=("input-system.sh")
    [[ ! -d "$UHOME/uTemplate/forms" ]] && missing_files+=("forms directory")
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        echo -e "${YELLOW}⚠️ Missing input system components:${NC}"
        printf '   - %s\n' "${missing_files[@]}"
        return 1
    fi
    
    log_input "Input system integration ready"
    return 0
}

# Main input handler for uCode integration
handle_enhanced_input() {
    local input="$1"
    
    # Handle shortcode detection
    if should_trigger_shortcode_selector "$input" || [[ "$input" =~ ^\[.*$ ]]; then
        process_shortcode_input "$input"
        return 0
    fi
    
    # Handle form-commands
    if process_command_with_forms "$input"; then
        return 0
    fi
    
    # Not handled by input system
    return 2
}

# Export functions for uCode integration
export -f handle_enhanced_input
export -f enhanced_input_prompt
export -f init_input_integration

# Show status when sourced
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    echo -e "${GREEN}✅ input system loaded${NC}"
    init_input_integration
fi
