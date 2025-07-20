#!/bin/bash
# uDOS Advanced Input System v1.0.0
# Predictive shortcode selection and enhanced data collection with ASCII blocks
# Integrated with uDOS template system and command datasets

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"

# Source display configuration for ASCII blocks
[[ -f "${UHOME}/uMemory/config/display-vars.sh" ]] && source "${UHOME}/uMemory/config/display-vars.sh"

# Colors and visual elements
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

# ASCII box drawing characters
readonly BOX_TL="┌"
readonly BOX_TR="┐"
readonly BOX_BL="└"
readonly BOX_BR="┘"
readonly BOX_H="─"
readonly BOX_V="│"
readonly BOX_VL="├"
readonly BOX_VR="┤"
readonly BOX_HT="┬"
readonly BOX_HB="┴"
readonly BOX_CROSS="┼"

# Enhanced box characters for headers
readonly BOX_DOUBLE_TL="╔"
readonly BOX_DOUBLE_TR="╗"
readonly BOX_DOUBLE_BL="╚"
readonly BOX_DOUBLE_BR="╝"
readonly BOX_DOUBLE_H="═"
readonly BOX_DOUBLE_V="║"

# Navigation symbols
readonly ARROW_UP="↑"
readonly ARROW_DOWN="↓"
readonly ARROW_LEFT="←"
readonly ARROW_RIGHT="→"
readonly SELECTED="●"
readonly UNSELECTED="○"
readonly HIGHLIGHT="▶"

# Input system configuration
INPUT_WIDTH=${UDOS_INPUT_WIDTH:-60}
BLOCK_WIDTH=${UDOS_BLOCK_WIDTH:-70}
BLOCK_HEIGHT=${UDOS_BLOCK_HEIGHT:-10}

# Dataset locations
SHORTCODE_DATASET="$UHOME/uTemplate/datasets/shortcodes.json"
COMMAND_DATASET="$UHOME/uKnowledge/datasets/commands.json"
TEMPLATE_VARS="$UHOME/uTemplate/variables/user-vars.json"

# Logging
log_input() {
    echo -e "${CYAN}[$(date '+%H:%M:%S')] [INPUT-SYSTEM]${NC} $1" >&2
}

error_input() {
    echo -e "${RED}[$(date '+%H:%M:%S')] [INPUT-ERROR]${NC} $1" >&2
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🎯 PREDICTIVE SHORTCODE INPUT SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════════════

# Initialize shortcode datasets
init_shortcode_datasets() {
    log_input "Initializing shortcode datasets..."
    
    # Create shortcode dataset if it doesn't exist
    if [[ ! -f "$SHORTCODE_DATASET" ]]; then
        mkdir -p "$(dirname "$SHORTCODE_DATASET")"
        create_default_shortcode_dataset
    fi
    
    # Verify command dataset exists
    if [[ ! -f "$COMMAND_DATASET" ]]; then
        mkdir -p "$(dirname "$COMMAND_DATASET")"
        create_default_command_dataset
    fi
}

# Create default shortcode dataset
create_default_shortcode_dataset() {
    cat > "$SHORTCODE_DATASET" << 'EOF'
{
    "metadata": {
        "version": "1.0.0",
        "description": "uDOS Shortcode Command Dataset",
        "last_updated": "2025-07-20",
        "total_shortcodes": 25
    },
    "categories": [
        "system", "dashboard", "mission", "data", "template", "package", "error", "utility"
    ],
    "shortcodes": [
        {
            "command": "DASH",
            "category": "dashboard",
            "description": "Dashboard operations",
            "args": ["live", "build", "stats", "export"],
            "examples": ["[DASH:live]", "[DASH:build]", "[DASH:stats]"],
            "help": "Generate and manage uDOS dashboard displays"
        },
        {
            "command": "CHECK",
            "category": "system", 
            "description": "System validation and checks",
            "args": ["health", "all", "setup", "time", "location", "user"],
            "examples": ["[CHECK:health]", "[CHECK:all]", "[CHECK:setup]"],
            "help": "Perform comprehensive system validation checks"
        },
        {
            "command": "MISSION",
            "category": "mission",
            "description": "Mission management operations",
            "args": ["create", "list", "show", "complete", "archive"],
            "examples": ["[MISSION:create]", "[MISSION:list]", "[MISSION:show]"],
            "help": "Create and manage uDOS missions and objectives"
        },
        {
            "command": "PACKAGE",
            "category": "package",
            "description": "Package management system",
            "args": ["install", "list", "update", "remove", "search"],
            "examples": ["[PACKAGE:install-all]", "[PACKAGE:list]", "[PACKAGE:search:ripgrep]"],
            "help": "Install and manage uDOS system packages"
        },
        {
            "command": "PKG",
            "category": "package",
            "description": "Package management (short form)",
            "args": ["install", "list", "update", "remove", "search"],
            "examples": ["[PKG:install-all]", "[PKG:list]", "[PKG:update]"],
            "help": "Short form package management commands"
        },
        {
            "command": "DATA",
            "category": "data",
            "description": "Data processing and manipulation",
            "args": ["query", "export", "import", "validate", "transform"],
            "examples": ["[DATA:query:users]", "[DATA:export:csv]", "[DATA:validate]"],
            "help": "Process and manipulate data files and datasets"
        },
        {
            "command": "TEMPLATE",
            "category": "template",
            "description": "Template system operations",
            "args": ["generate", "list", "validate", "process", "create"],
            "examples": ["[TEMPLATE:generate:user-setup]", "[TEMPLATE:list]", "[TEMPLATE:validate]"],
            "help": "Generate and manage uDOS templates"
        },
        {
            "command": "LOG",
            "category": "utility",
            "description": "Logging system operations",
            "args": ["create", "view", "export", "clean", "search"],
            "examples": ["[LOG:create:mission]", "[LOG:view:recent]", "[LOG:export]"],
            "help": "Create and manage system logs"
        },
        {
            "command": "ERROR",
            "category": "error",
            "description": "Error handling and diagnostics",
            "args": ["stats", "list", "clear", "export", "analyze"],
            "examples": ["[ERROR:stats]", "[ERROR:list]", "[ERROR:analyze]"],
            "help": "Handle and analyze system errors"
        },
        {
            "command": "BASH",
            "category": "utility",
            "description": "Execute bash commands",
            "args": ["*"],
            "examples": ["[BASH:ls -la]", "[BASH:pwd]", "[BASH:grep -r 'pattern' .]"],
            "help": "Execute bash commands with enhanced error handling"
        },
        {
            "command": "SCRIPT",
            "category": "utility",
            "description": "Execute uDOS scripts",
            "args": ["*"],
            "examples": ["[SCRIPT:backup-system]", "[SCRIPT:update-all]"],
            "help": "Execute custom uDOS scripts"
        },
        {
            "command": "JSON",
            "category": "data",
            "description": "JSON processing operations",
            "args": ["query", "validate", "format", "merge", "extract"],
            "examples": ["[JSON:query:user.name]", "[JSON:validate:config.json]"],
            "help": "Process and manipulate JSON files"
        },
        {
            "command": "SEARCH",
            "category": "utility",
            "description": "Search system content",
            "args": ["files", "content", "commands", "logs", "datasets"],
            "examples": ["[SEARCH:files:*.md]", "[SEARCH:content:uDOS]"],
            "help": "Search across uDOS system files and content"
        }
    ]
}
EOF
    log_input "Created default shortcode dataset with $(jq '.shortcodes | length' "$SHORTCODE_DATASET") entries"
}

# Create default command dataset
create_default_command_dataset() {
    cat > "$COMMAND_DATASET" << 'EOF'
{
    "metadata": {
        "version": "1.0.0",
        "description": "uDOS Command Reference Dataset",
        "last_updated": "2025-07-20"
    },
    "commands": [
        {"command": "CHECK", "args": ["TIME", "LOCATION", "USER", "SETUP", "HEALTH", "ALL"]},
        {"command": "DISPLAY", "args": ["INIT", "MODE", "TEST", "SUMMARY", "HELP"]},
        {"command": "MAP", "args": ["GENERATE", "REGION", "CITY", "SHOW", "INFO"]},
        {"command": "DASH", "args": ["BUILD", "LIVE", "EXPORT", "STATS"]},
        {"command": "SETUP", "args": ["USER", "SYSTEM", "PACKAGES", "TEMPLATES"]},
        {"command": "LIST", "args": ["COMMANDS", "FILES", "TEMPLATES", "MISSIONS"]},
        {"command": "RUN", "args": ["SCRIPT", "TEST", "VALIDATION", "BACKUP"]},
        {"command": "HELP", "args": ["COMMANDS", "TEMPLATES", "SHORTCODES", "SYSTEM"]}
    ]
}
EOF
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🎨 ASCII INTERFACE RENDERING
# ═══════════════════════════════════════════════════════════════════════════════════════

# Draw ASCII box with content
draw_box() {
    local title="$1"
    local content="$2"
    local width="${3:-$BLOCK_WIDTH}"
    local style="${4:-single}"
    
    local tl tr bl br h v
    
    case "$style" in
        "double")
            tl="$BOX_DOUBLE_TL" tr="$BOX_DOUBLE_TR" bl="$BOX_DOUBLE_BL" br="$BOX_DOUBLE_BR"
            h="$BOX_DOUBLE_H" v="$BOX_DOUBLE_V"
            ;;
        *)
            tl="$BOX_TL" tr="$BOX_TR" bl="$BOX_BL" br="$BOX_BR"
            h="$BOX_H" v="$BOX_V"
            ;;
    esac
    
    # Top border with title
    echo -ne "${CYAN}$tl"
    printf "%*s" $((width-2)) "" | tr ' ' "$h"
    echo -e "$tr${NC}"
    
    if [[ -n "$title" ]]; then
        local title_len=${#title}
        local padding=$(((width - title_len - 4) / 2))
        echo -ne "${CYAN}$v ${BOLD}${title}${NC}"
        printf "%*s" $((width - title_len - 3)) ""
        echo -e "${CYAN}$v${NC}"
        
        # Separator line
        echo -ne "${CYAN}├"
        printf "%*s" $((width-2)) "" | tr ' ' "$h"
        echo -e "┤${NC}"
    fi
    
    # Content lines
    while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            local line_len=${#line}
            echo -ne "${CYAN}$v${NC} $line"
            printf "%*s" $((width - line_len - 3)) ""
            echo -e "${CYAN}$v${NC}"
        else
            echo -ne "${CYAN}$v${NC}"
            printf "%*s" $((width-2)) ""
            echo -e "${CYAN}$v${NC}"
        fi
    done <<< "$content"
    
    # Bottom border
    echo -ne "${CYAN}$bl"
    printf "%*s" $((width-2)) "" | tr ' ' "$h"
    echo -e "$br${NC}"
}

# Draw selection menu with arrow navigation
draw_selection_menu() {
    local title="$1"
    local -n options_ref=$2
    local selected="$3"
    local width="${4:-$BLOCK_WIDTH}"
    
    local content=""
    
    for i in "${!options_ref[@]}"; do
        local prefix="  "
        local style=""
        
        if [[ $i -eq $selected ]]; then
            prefix="${GREEN}${HIGHLIGHT} "
            style="${BOLD}${GREEN}"
        fi
        
        content+="${prefix}${style}${options_ref[$i]}${NC}\n"
    done
    
    # Add navigation help
    content+="\n${DIM}${ARROW_UP}${ARROW_DOWN} Navigate | Enter: Select | Esc: Cancel${NC}"
    
    draw_box "$title" "$content" "$width"
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🔍 PREDICTIVE SHORTCODE SELECTOR
# ═══════════════════════════════════════════════════════════════════════════════════════

# Get shortcode suggestions based on partial input
get_shortcode_suggestions() {
    local partial="$1"
    local max_results="${2:-10}"
    
    if [[ ! -f "$SHORTCODE_DATASET" ]]; then
        echo "[]"
        return
    fi
    
    # Query shortcodes matching the partial input
    jq -r --arg partial "$partial" --argjson max "$max_results" '
        .shortcodes[] | 
        select(.command | startswith($partial | ascii_upcase)) |
        {
            command: .command,
            description: .description,
            category: .category,
            args: .args,
            examples: .examples[0]
        }
    ' "$SHORTCODE_DATASET" | jq -s ".[:$max_results]"
}

# Interactive shortcode selector
interactive_shortcode_selector() {
    local partial="${1:-}"
    local suggestions
    local selected=0
    local key
    
    # Initialize datasets
    init_shortcode_datasets
    
    while true; do
        clear
        
        # Get current suggestions
        suggestions=$(get_shortcode_suggestions "$partial")
        
        if [[ "$suggestions" == "[]" ]] || [[ -z "$suggestions" ]]; then
            draw_box "🔍 Shortcode Selector" "No matching shortcodes found for: $partial\n\nType to search or press Esc to cancel"
        else
            # Parse suggestions into arrays
            local commands=()
            local descriptions=()
            local examples=()
            
            while IFS= read -r line; do
                if [[ -n "$line" ]]; then
                    local cmd=$(echo "$line" | jq -r '.command')
                    local desc=$(echo "$line" | jq -r '.description')
                    local example=$(echo "$line" | jq -r '.examples')
                    
                    commands+=("$cmd")
                    descriptions+=("$desc")
                    examples+=("$example")
                fi
            done < <(echo "$suggestions" | jq -c '.[]')
            
            # Build display options
            local display_options=()
            for i in "${!commands[@]}"; do
                display_options+=("${commands[$i]} - ${descriptions[$i]}")
            done
            
            if [[ ${#display_options[@]} -gt 0 ]]; then
                # Ensure selected is within bounds
                [[ $selected -ge ${#display_options[@]} ]] && selected=$((${#display_options[@]} - 1))
                [[ $selected -lt 0 ]] && selected=0
                
                draw_selection_menu "🔍 Shortcode Selector - Type: [$partial" display_options "$selected"
                
                # Show example for selected item
                if [[ $selected -lt ${#examples[@]} ]]; then
                    echo
                    draw_box "💡 Example Usage" "${examples[$selected]}" 50
                fi
            fi
        fi
        
        echo
        echo -e "${DIM}Current input: ${WHITE}[$partial${DIM}${NC}"
        echo -e "${DIM}Press ${WHITE}Tab${DIM} to complete, ${WHITE}Enter${DIM} to select, ${WHITE}Backspace${DIM} to delete, ${WHITE}Esc${DIM} to cancel${NC}"
        
        # Read single character
        read -rsn1 key
        
        case "$key" in
            $'\e')  # Escape
                echo
                return 1
                ;;
            $'\t')  # Tab - autocomplete
                if [[ ${#commands[@]} -gt 0 ]] && [[ $selected -lt ${#commands[@]} ]]; then
                    partial="${commands[$selected]}"
                fi
                ;;
            $'\n'|$'\r')  # Enter - select
                if [[ ${#commands[@]} -gt 0 ]] && [[ $selected -lt ${#commands[@]} ]]; then
                    echo "${examples[$selected]}"
                    return 0
                fi
                ;;
            $'\x7f'|$'\b')  # Backspace
                if [[ ${#partial} -gt 0 ]]; then
                    partial="${partial%?}"
                    selected=0
                fi
                ;;
            $'\e[A')  # Up arrow
                [[ $selected -gt 0 ]] && ((selected--))
                ;;
            $'\e[B')  # Down arrow
                [[ $selected -lt $((${#display_options[@]} - 1)) ]] && ((selected++))
                ;;
            *)  # Regular character
                if [[ "$key" =~ [A-Za-z0-9] ]]; then
                    partial+="$key"
                    selected=0
                fi
                ;;
        esac
    done
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 📝 ENHANCED DATA COLLECTION FORMS
# ═══════════════════════════════════════════════════════════════════════════════════════

# Render form field with validation
render_form_field() {
    local field_data="$1"
    local current_value="$2"
    local width="${3:-$INPUT_WIDTH}"
    
    local label=$(echo "$field_data" | jq -r '.label // "Field"')
    local field_type=$(echo "$field_data" | jq -r '.type // "text"')
    local required=$(echo "$field_data" | jq -r '.required // false')
    local help_text=$(echo "$field_data" | jq -r '.help // ""')
    local options=$(echo "$field_data" | jq -r '.options[]? // empty')
    
    local req_marker=""
    [[ "$required" == "true" ]] && req_marker="${RED}*${NC}"
    
    echo -e "${BOLD}${label}${req_marker}${NC}"
    
    case "$field_type" in
        "choice"|"select")
            echo -e "${DIM}Options:${NC}"
            local opt_array=()
            while IFS= read -r opt; do
                [[ -n "$opt" ]] && opt_array+=("$opt")
            done < <(echo "$field_data" | jq -r '.options[]?')
            
            for i in "${!opt_array[@]}"; do
                local marker="$UNSELECTED"
                [[ "${opt_array[$i]}" == "$current_value" ]] && marker="$SELECTED"
                echo -e "  ${marker} ${opt_array[$i]}"
            done
            ;;
        "boolean")
            local yes_marker="$UNSELECTED"
            local no_marker="$UNSELECTED"
            case "$current_value" in
                "true"|"yes"|"y"|"1") yes_marker="$SELECTED" ;;
                "false"|"no"|"n"|"0") no_marker="$SELECTED" ;;
            esac
            echo -e "  ${yes_marker} Yes    ${no_marker} No"
            ;;
        "password")
            echo -ne "["
            printf "%*s" $((width-2)) "" | tr ' ' '*'
            echo "]"
            ;;
        *)  # text, number, email, etc.
            local display_value="$current_value"
            [[ -z "$current_value" ]] && display_value="${DIM}(empty)${NC}"
            
            echo -ne "["
            printf "%-*s" $((width-2)) "$display_value"
            echo "]"
            ;;
    esac
    
    [[ -n "$help_text" ]] && echo -e "${DIM}💡 $help_text${NC}"
}

# Interactive form field editor
edit_form_field() {
    local field_data="$1"
    local current_value="$2"
    
    local label=$(echo "$field_data" | jq -r '.label // "Field"')
    local field_type=$(echo "$field_data" | jq -r '.type // "text"')
    local validation=$(echo "$field_data" | jq -r '.validation // ""')
    local required=$(echo "$field_data" | jq -r '.required // false')
    
    case "$field_type" in
        "choice"|"select")
            # Show choice selector
            local options_array=()
            while IFS= read -r opt; do
                [[ -n "$opt" ]] && options_array+=("$opt")
            done < <(echo "$field_data" | jq -r '.options[]?')
            
            local selected=0
            # Find current selection
            for i in "${!options_array[@]}"; do
                [[ "${options_array[$i]}" == "$current_value" ]] && selected=$i && break
            done
            
            while true; do
                clear
                draw_selection_menu "Select $label" options_array "$selected"
                
                read -rsn1 key
                case "$key" in
                    $'\e[A') [[ $selected -gt 0 ]] && ((selected--)) ;;
                    $'\e[B') [[ $selected -lt $((${#options_array[@]} - 1)) ]] && ((selected++)) ;;
                    $'\n'|$'\r') echo "${options_array[$selected]}"; return 0 ;;
                    $'\e') echo "$current_value"; return 1 ;;
                esac
            done
            ;;
        "boolean")
            echo -e "${BOLD}$label${NC} (y/n):"
            read -p "> " response
            case "$response" in
                [yY]|[yY][eE][sS]|[tT][rR][uU][eE]|1) echo "true" ;;
                [nN]|[nN][oO]|[fF][aA][lL][sS][eE]|0) echo "false" ;;
                *) echo "$current_value" ;;
            esac
            ;;
        "password")
            echo -e "${BOLD}$label${NC}:"
            read -rsp "> " value
            echo
            echo "$value"
            ;;
        *)
            echo -e "${BOLD}$label${NC}:"
            [[ -n "$current_value" ]] && echo -e "${DIM}Current: $current_value${NC}"
            read -p "> " -e -i "$current_value" value
            
            # Validation
            if [[ -n "$validation" ]] && [[ -n "$value" ]]; then
                if ! [[ "$value" =~ $validation ]]; then
                    echo -e "${RED}❌ Invalid format. Please try again.${NC}"
                    read -p "Press Enter to continue..."
                    return 1
                fi
            fi
            
            # Required field check
            if [[ "$required" == "true" ]] && [[ -z "$value" ]]; then
                echo -e "${RED}❌ This field is required.${NC}"
                read -p "Press Enter to continue..."
                return 1
            fi
            
            echo "$value"
            ;;
    esac
}

# Render complete form
render_form() {
    local form_config="$1"
    local -n form_data_ref=$2
    local current_field="${3:-0}"
    
    clear
    
    local form_title=$(echo "$form_config" | jq -r '.title // "uDOS Form"')
    local form_description=$(echo "$form_config" | jq -r '.description // ""')
    
    # Form header
    draw_box "📝 $form_title" "$form_description" "$BLOCK_WIDTH" "double"
    echo
    
    # Get fields array
    local fields_json=$(echo "$form_config" | jq -c '.fields[]')
    local field_index=0
    
    while IFS= read -r field; do
        local field_name=$(echo "$field" | jq -r '.name')
        local current_value="${form_data_ref[$field_name]:-}"
        
        # Highlight current field
        if [[ $field_index -eq $current_field ]]; then
            echo -e "${YELLOW}${HIGHLIGHT} Field $((field_index + 1)):${NC}"
        else
            echo -e "${DIM}  Field $((field_index + 1)):${NC}"
        fi
        
        render_form_field "$field" "$current_value"
        echo
        
        ((field_index++))
    done <<< "$fields_json"
    
    # Form navigation
    echo -e "${DIM}${ARROW_UP}${ARROW_DOWN} Navigate | Enter: Edit | Tab: Next | Shift+Tab: Previous | Ctrl+S: Save | Esc: Cancel${NC}"
}

# Interactive dataget processor
interactive_form() {
    local dataget_config="$1"
    local output_file="$2"
    
    # Parse dataget configuration
    local fields_json=$(echo "$dataget_config" | jq -c '.fields[]')
    local field_names=()
    local field_configs=()
    
    # Build field arrays
    while IFS= read -r field; do
        local name=$(echo "$field" | jq -r '.name')
        field_names+=("$name")
        field_configs+=("$field")
    done <<< "$fields_json"
    
    # Initialize dataget data
    declare -A dataget_data
    for name in "${field_names[@]}"; do
        dataget_data["$name"]=""
    done
    
    local current_field=0
    local total_fields=${#field_names[@]}
    
    while true; do
        render_form "$form_config" form_data "$current_field"
        
        read -rsn1 key
        case "$key" in
            $'\e[A')  # Up arrow
                [[ $current_field -gt 0 ]] && ((current_field--))
                ;;
            $'\e[B')  # Down arrow  
                [[ $current_field -lt $((total_fields - 1)) ]] && ((current_field++))
                ;;
            $'\t')  # Tab - next field
                [[ $current_field -lt $((total_fields - 1)) ]] && ((current_field++))
                ;;
            $'\n'|$'\r')  # Enter - edit current field
                local field_name="${field_names[$current_field]}"
                local field_config="${field_configs[$current_field]}"
                local current_value="${form_data[$field_name]}"
                
                local new_value
                new_value=$(edit_form_field "$field_config" "$current_value")
                
                if [[ $? -eq 0 ]]; then
                    form_data["$field_name"]="$new_value"
                fi
                ;;
            $'\x13')  # Ctrl+S - save
                save_form_data form_data "$output_file"
                echo -e "\n${GREEN}✅ Form saved successfully!${NC}"
                read -p "Press Enter to continue..."
                return 0
                ;;
            $'\e')  # Escape - cancel
                echo -e "\n${YELLOW}Form cancelled.${NC}"
                return 1
                ;;
        esac
    done
}

# Save form data to file
save_form_data() {
    local -n data_ref=$1
    local output_file="$2"
    
    mkdir -p "$(dirname "$output_file")"
    
    # Create JSON output
    local json_output="{"
    local first=true
    
    for key in "${!data_ref[@]}"; do
        [[ "$first" == "false" ]] && json_output+=","
        json_output+="\"$key\":\"${data_ref[$key]}\""
        first=false
    done
    json_output+="}"
    
    echo "$json_output" | jq '.' > "$output_file"
    log_input "Form data saved to: $output_file"
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🎯 MAIN INPUT SYSTEM COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════════════

# Main command dispatcher
main() {
    local command="${1:-help}"
    local args="${2:-}"
    
    case "$command" in
        "shortcode"|"sc")
            interactive_shortcode_selector "$args"
            ;;
        "form"|"f")
            if [[ -f "$args" ]]; then
                local output_file="$UHOME/uMemory/forms/form-$(date +%Y%m%d-%H%M%S).json"
                interactive_form "$(cat "$args")" "$output_file"
            else
                error_input "Form configuration file not found: $args"
                return 1
            fi
            ;;
        "demo")
            demo_input_system
            ;;
        "init")
            init_shortcode_datasets
            echo -e "${GREEN}✅ Input system initialized${NC}"
            ;;
        "help")
            show_help
            ;;
        *)
            error_input "Unknown command: $command"
            show_help
            return 1
            ;;
    esac
}

# Demo system
demo_input_system() {
    echo -e "${CYAN}🎯 uDOS Advanced Input System Demo${NC}"
    echo
    
    while true; do
        echo -e "${BOLD}Choose demo:${NC}"
        echo "1. Predictive Shortcode Selector"
        echo "2. Enhanced Data Collection Form"
        echo "3. Exit Demo"
        echo
        
        read -p "Select option (1-3): " choice
        
        case "$choice" in
            1)
                echo -e "\n${YELLOW}Starting shortcode selector demo...${NC}"
                interactive_shortcode_selector ""
                ;;
            2)
                echo -e "\n${YELLOW}Creating demo form...${NC}"
                create_demo_form
                interactive_form "$(cat /tmp/demo-form.json)" "$UHOME/uMemory/forms/demo-form-$(date +%Y%m%d-%H%M%S).json"
                ;;
            3)
                echo -e "${GREEN}Demo completed!${NC}"
                return 0
                ;;
            *)
                echo -e "${RED}Invalid choice. Please select 1-3.${NC}"
                ;;
        esac
        echo
    done
}

# Create demo form configuration
create_demo_form() {
    cat > /tmp/demo-form.json << 'EOF'
{
    "title": "uDOS User Configuration",
    "description": "Configure your uDOS environment with enhanced input controls",
    "fields": [
        {
            "name": "username",
            "label": "Username",
            "type": "text",
            "required": true,
            "validation": "^[a-zA-Z][a-zA-Z0-9_]{2,19}$",
            "help": "Enter a username (3-20 characters, alphanumeric and underscore only)"
        },
        {
            "name": "role",
            "label": "Default Role",
            "type": "choice",
            "options": ["developer", "analyst", "admin", "user"],
            "required": true,
            "help": "Select your primary role in uDOS"
        },
        {
            "name": "theme",
            "label": "Interface Theme",
            "type": "choice",
            "options": ["dark", "light", "matrix", "cyberpunk"],
            "help": "Choose your preferred visual theme"
        },
        {
            "name": "auto_backup",
            "label": "Enable Auto Backup",
            "type": "boolean",
            "help": "Automatically backup your work and configurations"
        },
        {
            "name": "email",
            "label": "Email Address",
            "type": "text",
            "validation": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
            "help": "Optional: Enter your email for notifications"
        }
    ]
}
EOF
}

# Show help
show_help() {
    cat << 'EOF'
🎯 uDOS Advanced Input System v1.0.0

USAGE:
    ./input-system.sh [COMMAND] [ARGS]

COMMANDS:
    shortcode [PARTIAL]     Interactive shortcode selector with predictive search
    form CONFIG_FILE        Interactive form processor with validation
    demo                    Run demonstration of input system features
    init                    Initialize shortcode and command datasets
    help                    Show this help message

FEATURES:
    🔍 Predictive Shortcode Selection
    • Type-ahead search through command datasets
    • Arrow key navigation with visual feedback
    • Integrated help and example display
    • Auto-completion and smart suggestions

    📝 Enhanced Data Collection Forms
    • Multiple input types (text, choice, boolean, password)
    • Real-time validation and error handling
    • Keyboard navigation (arrows, tab, enter)
    • ASCII block-style visual interface
    • JSON output format

    🎨 ASCII Visual Interface
    • Responsive block-oriented design
    • Consistent with uDOS visual style
    • Terminal size adaptation
    • Enhanced typography and symbols

INTEGRATION:
    • Works with existing uDOS shortcode system
    • Uses uTemplate datasets for suggestions
    • Integrates with display configuration system
    • Saves form data to uMemory directory structure

EXAMPLES:
    # Launch shortcode selector
    ./input-system.sh shortcode

    # Process a configuration form
    ./input-system.sh form config/user-setup.json

    # Run demonstration
    ./input-system.sh demo

EOF
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
