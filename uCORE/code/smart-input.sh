#!/bin/bash

# uDOS Smart Input Engine
# Intelligent data collection with context awareness and validation
# Part of the Universal Data Operating System

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_CACHE_DIR="$SCRIPT_DIR/../uMemory/input-cache"
SUGGESTIONS_DB="$INPUT_CACHE_DIR/suggestions.json"
USER_HISTORY="$INPUT_CACHE_DIR/user-history.json"

# Initialize input system
init_input_system() {
    mkdir -p "$INPUT_CACHE_DIR"
    
    # Create suggestions database if it doesn't exist
    if [[ ! -f "$SUGGESTIONS_DB" ]]; then
        cat > "$SUGGESTIONS_DB" << 'EOF'
{
  "suggestions": {
    "mission": [
      "Documentation Update",
      "System Integration",
      "Feature Development",
      "Bug Investigation",
      "Performance Optimization",
      "Security Review",
      "User Training",
      "Database Migration",
      "API Development",
      "Testing Framework"
    ],
    "client": [
      "Internal Project",
      "Client Alpha",
      "Client Beta",
      "Research Division",
      "Development Team",
      "Quality Assurance",
      "Marketing Team",
      "Support Department"
    ],
    "tags": [
      "urgent",
      "documentation",
      "development",
      "testing",
      "deployment",
      "maintenance",
      "research",
      "planning",
      "review",
      "training"
    ],
    "priority": ["Low", "Medium", "High", "Critical"],
    "status": ["Draft", "In Progress", "Review", "Complete", "Archived"],
    "category": ["User", "Technical", "Reference", "Tutorial", "API"]
  }
}
EOF
    fi
    
    # Create user history if it doesn't exist
    if [[ ! -f "$USER_HISTORY" ]]; then
        cat > "$USER_HISTORY" << 'EOF'
{
  "history": {
    "recent_inputs": {},
    "frequent_values": {},
    "last_used": {},
    "preferences": {
      "default_priority": "Medium",
      "default_author": "",
      "preferred_tags": []
    }
  }
}
EOF
    fi
}

# Display ASCII art header
show_input_header() {
    echo ""
    echo "    ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗    ██╗███╗   ██╗██████╗ ██╗   ██╗████████╗"
    echo "    ██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝    ██║████╗  ██║██╔══██╗██║   ██║╚══██╔══╝"
    echo "    ███████╗██╔████╔██║███████║██████╔╝   ██║       ██║██╔██╗ ██║██████╔╝██║   ██║   ██║   "
    echo "    ╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║       ██║██║╚██╗██║██╔═══╝ ██║   ██║   ██║   "
    echo "    ███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║       ██║██║ ╚████║██║     ╚██████╔╝   ██║   "
    echo "    ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝    ╚═╝   "
    echo ""
    echo "    Universal Data Operating System - Smart Input Engine v$VERSION"
    echo "    ══════════════════════════════════════════════════════════════════════════════════════"
    echo ""
}

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Enhanced prompt function with color and styling
colored_prompt() {
    local prompt="$1"
    local default="$2"
    
    echo ""
    echo -e "${CYAN}┌────────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC} ${BOLD}$prompt${NC}"
    if [[ -n "$default" ]]; then
        echo -e "${CYAN}│${NC} ${YELLOW}Default: $default${NC}"
    fi
    echo -e "${CYAN}└────────────────────────────────────────────────────────────────────┘${NC}"
    echo -n -e "${GREEN}➤ ${NC}"
}

# Get suggestions for a field
get_suggestions() {
    local field_type="$1"
    local context="$2"
    
    if command -v jq >/dev/null 2>&1 && [[ -f "$SUGGESTIONS_DB" ]]; then
        jq -r ".suggestions.$field_type[]?" "$SUGGESTIONS_DB" 2>/dev/null | head -5
    fi
}

# Show suggestions
show_suggestions() {
    local suggestions="$1"
    
    if [[ -n "$suggestions" ]]; then
        echo ""
        echo -e "${BLUE}💡 Suggestions:${NC}"
        local i=1
        while IFS= read -r suggestion; do
            echo -e "  ${YELLOW}$i)${NC} $suggestion"
            ((i++))
        done <<< "$suggestions"
        echo ""
    fi
}

# Validate input based on rules
validate_input() {
    local value="$1"
    local validation_rules="$2"
    local errors=()
    
    if [[ -z "$validation_rules" ]]; then
        return 0
    fi
    
    IFS=',' read -ra rules <<< "$validation_rules"
    
    for rule in "${rules[@]}"; do
        rule=$(echo "$rule" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        case "$rule" in
            "required")
                if [[ -z "$value" ]]; then
                    errors+=("Field is required")
                fi
                ;;
            "min:"*)
                min_length="${rule#min:}"
                if [[ ${#value} -lt $min_length ]]; then
                    errors+=("Minimum length is $min_length characters")
                fi
                ;;
            "max:"*)
                max_length="${rule#max:}"
                if [[ ${#value} -gt $max_length ]]; then
                    errors+=("Maximum length is $max_length characters")
                fi
                ;;
            "email")
                if [[ ! "$value" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
                    errors+=("Invalid email format")
                fi
                ;;
            "alphanumeric")
                if [[ ! "$value" =~ ^[A-Za-z0-9]+$ ]]; then
                    errors+=("Only letters and numbers allowed")
                fi
                ;;
            "positive")
                if [[ ! "$value" =~ ^[0-9]+$ ]] || [[ "$value" -le 0 ]]; then
                    errors+=("Must be a positive number")
                fi
                ;;
        esac
    done
    
    if [[ ${#errors[@]} -gt 0 ]]; then
        echo ""
        echo -e "${RED}❌ Validation errors:${NC}"
        for error in "${errors[@]}"; do
            echo -e "   ${RED}•${NC} $error"
        done
        echo ""
        return 1
    fi
    
    return 0
}

# Collect text input
collect_text_input() {
    local field_name="$1"
    local prompt="$2"
    local default="$3"
    local validation="$4"
    local suggestions=""
    
    # Get context-aware suggestions
    if [[ "$field_name" =~ (mission|title|name) ]]; then
        suggestions=$(get_suggestions "mission" "$field_name")
    elif [[ "$field_name" =~ (client|author) ]]; then
        suggestions=$(get_suggestions "client" "$field_name")
    elif [[ "$field_name" =~ (tag) ]]; then
        suggestions=$(get_suggestions "tags" "$field_name")
    fi
    
    while true; do
        colored_prompt "$prompt" "$default"
        show_suggestions "$suggestions"
        
        read -r user_input
        
        # Use default if no input provided
        if [[ -z "$user_input" && -n "$default" ]]; then
            user_input="$default"
        fi
        
        # Validate input
        if validate_input "$user_input" "$validation"; then
            echo -e "${GREEN}✓ Valid input accepted${NC}"
            echo "$user_input"
            return 0
        fi
        
        echo -e "${YELLOW}Please try again...${NC}"
    done
}

# Collect selection input
collect_selection_input() {
    local field_name="$1"
    local prompt="$2"
    local default="$3"
    local options="$4"
    
    IFS=',' read -ra option_array <<< "$options"
    local selected_index=0
    
    # Find default index
    for i in "${!option_array[@]}"; do
        if [[ "${option_array[$i]}" == "$default" ]]; then
            selected_index=$i
            break
        fi
    done
    
    while true; do
        clear
        show_input_header
        
        echo -e "${CYAN}┌────────────────────────────────────────────────────────────────────┐${NC}"
        echo -e "${CYAN}│${NC} ${BOLD}$prompt${NC}"
        echo -e "${CYAN}└────────────────────────────────────────────────────────────────────┘${NC}"
        echo ""
        
        for i in "${!option_array[@]}"; do
            local option="${option_array[$i]}"
            if [[ $i -eq $selected_index ]]; then
                echo -e "   ${GREEN}●${NC} ${BOLD}$option${NC}"
            else
                echo -e "   ${BLUE}○${NC} $option"
            fi
        done
        
        echo ""
        echo -e "${YELLOW}Use ↑↓ to navigate, ENTER to confirm, ESC to cancel${NC}"
        
        # Read key input
        read -rsn1 key
        case "$key" in
            $'\x1b')  # ESC sequence
                read -rsn2 key
                case "$key" in
                    '[A')  # Up arrow
                        ((selected_index--))
                        if [[ $selected_index -lt 0 ]]; then
                            selected_index=$((${#option_array[@]} - 1))
                        fi
                        ;;
                    '[B')  # Down arrow
                        ((selected_index++))
                        if [[ $selected_index -ge ${#option_array[@]} ]]; then
                            selected_index=0
                        fi
                        ;;
                esac
                ;;
            '')  # Enter
                echo -e "${GREEN}✓ Selected: ${option_array[$selected_index]}${NC}"
                echo "${option_array[$selected_index]}"
                return 0
                ;;
        esac
    done
}

# Collect boolean input
collect_boolean_input() {
    local field_name="$1"
    local prompt="$2"
    local default="$3"
    
    colored_prompt "$prompt (y/n)" "$default"
    
    read -r user_input
    
    # Use default if no input
    if [[ -z "$user_input" ]]; then
        user_input="$default"
    fi
    
    case "${user_input,,}" in
        "y"|"yes"|"true"|"1")
            echo -e "${GREEN}✓ Yes${NC}"
            echo "true"
            ;;
        "n"|"no"|"false"|"0")
            echo -e "${GREEN}✓ No${NC}"
            echo "false"
            ;;
        *)
            echo -e "${RED}❌ Invalid input. Please enter y/n${NC}"
            collect_boolean_input "$field_name" "$prompt" "$default"
            ;;
    esac
}

# Collect date input
collect_date_input() {
    local field_name="$1"
    local prompt="$2"
    local default="$3"
    local validation="$4"
    
    # Process default date expressions
    case "$default" in
        "today")
            default=$(date +%Y-%m-%d)
            ;;
        "today+"*)
            days="${default#today+}"
            default=$(date -d "+$days days" +%Y-%m-%d)
            ;;
        "tomorrow")
            default=$(date -d "+1 day" +%Y-%m-%d)
            ;;
    esac
    
    while true; do
        colored_prompt "$prompt (YYYY-MM-DD)" "$default"
        
        read -r user_input
        
        if [[ -z "$user_input" && -n "$default" ]]; then
            user_input="$default"
        fi
        
        # Validate date format
        if [[ "$user_input" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] && date -d "$user_input" >/dev/null 2>&1; then
            # Additional validation for future dates if required
            if [[ "$validation" == *"future"* ]]; then
                if [[ $(date -d "$user_input" +%s) -le $(date +%s) ]]; then
                    echo -e "${RED}❌ Date must be in the future${NC}"
                    continue
                fi
            fi
            
            echo -e "${GREEN}✓ Valid date: $user_input${NC}"
            echo "$user_input"
            return 0
        else
            echo -e "${RED}❌ Invalid date format. Please use YYYY-MM-DD${NC}"
        fi
    done
}

# Process input field
process_input_field() {
    local field_definition="$1"
    
    # Parse field definition: field_name|type|prompt|default|validation
    IFS='|' read -ra field_parts <<< "$field_definition"
    
    local field_name="${field_parts[0]}"
    local field_type="${field_parts[1]:-text}"
    local prompt="${field_parts[2]:-Enter value for $field_name}"
    local default="${field_parts[3]:-}"
    local validation="${field_parts[4]:-}"
    
    case "$field_type" in
        "text")
            collect_text_input "$field_name" "$prompt" "$default" "$validation"
            ;;
        "select")
            collect_selection_input "$field_name" "$prompt" "$default" "$validation"
            ;;
        "boolean")
            collect_boolean_input "$field_name" "$prompt" "$default"
            ;;
        "date")
            collect_date_input "$field_name" "$prompt" "$default" "$validation"
            ;;
        "number")
            # For now, treat as text with numeric validation
            validation="positive,$validation"
            collect_text_input "$field_name" "$prompt" "$default" "$validation"
            ;;
        *)
            echo -e "${RED}❌ Unknown field type: $field_type${NC}"
            echo ""
            ;;
    esac
}

# Main input processing function
main() {
    local command="$1"
    shift
    
    case "$command" in
        "field"|"FIELD")
            if [[ $# -lt 2 ]]; then
                echo "Usage: smart-input.sh field <field_name> <field_type> [prompt] [default] [validation]"
                exit 1
            fi
            
            local field_name="$1"
            local field_type="$2"
            local prompt="${3:-Enter value for $field_name}"
            local default="${4:-}"
            local validation="${5:-}"
            
            init_input_system
            show_input_header
            
            field_definition="$field_name|$field_type|$prompt|$default|$validation"
            result=$(process_input_field "$field_definition")
            echo "RESULT: $result"
            ;;
            
        "demo"|"DEMO")
            init_input_system
            show_input_header
            
            echo -e "${BOLD}Smart Input System Demo${NC}"
            echo "Let's create a new mission with smart input collection:"
            echo ""
            
            # Demo mission creation
            mission_name=$(process_input_field "mission_name|text|Mission name||smart_suggest:mission")
            priority=$(process_input_field "priority|select|Priority level|Medium|Low,Medium,High,Critical")
            due_date=$(process_input_field "due_date|date|Due date|today+7|future")
            auto_save=$(process_input_field "auto_save|boolean|Enable auto-save?|true|")
            
            echo ""
            echo -e "${GREEN}✅ Mission Created Successfully!${NC}"
            echo ""
            echo -e "${BOLD}Mission Details:${NC}"
            echo -e "  Name: $mission_name"
            echo -e "  Priority: $priority"
            echo -e "  Due Date: $due_date"
            echo -e "  Auto-save: $auto_save"
            echo ""
            ;;
            
        "init"|"INIT")
            init_input_system
            echo -e "${GREEN}✅ Smart Input System initialized${NC}"
            ;;
            
        *)
            echo "uDOS Smart Input Engine v$VERSION"
            echo ""
            echo "Usage:"
            echo "  smart-input.sh field <name> <type> [prompt] [default] [validation]"
            echo "  smart-input.sh demo     - Run interactive demo"
            echo "  smart-input.sh init     - Initialize input system"
            echo ""
            echo "Field Types:"
            echo "  text      - Text input with validation"
            echo "  select    - Single selection from options"
            echo "  boolean   - Yes/no input"
            echo "  date      - Date input with smart defaults"
            echo "  number    - Numeric input with validation"
            echo ""
            ;;
    esac
}

# Run main function with all arguments
main "$@"
