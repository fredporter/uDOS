#!/bin/bash
# uDOS Smart Input CLI Enhanced v2.1 - ASCII Color Block Interface
# Advanced CLI input with color blocks, button-style options, and predictive text

set -euo pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Enhanced Color Palette (Polaroid theme from uDOS)
readonly BLOCK_RED='\033[48;5;196m'      # Background red
readonly BLOCK_GREEN='\033[48;5;46m'     # Background green
readonly BLOCK_YELLOW='\033[48;5;226m'   # Background yellow
readonly BLOCK_BLUE='\033[48;5;21m'      # Background blue
readonly BLOCK_PURPLE='\033[48;5;201m'   # Background purple
readonly BLOCK_CYAN='\033[48;5;51m'      # Background cyan
readonly BLOCK_WHITE='\033[48;5;255m'    # Background white
readonly BLOCK_BLACK='\033[48;5;16m'     # Background black
readonly BLOCK_GRAY='\033[48;5;240m'     # Background gray

# Text colors
readonly TEXT_RED='\033[38;5;196m'
readonly TEXT_GREEN='\033[38;5;46m'
readonly TEXT_YELLOW='\033[38;5;226m'
readonly TEXT_BLUE='\033[38;5;21m'
readonly TEXT_PURPLE='\033[38;5;201m'
readonly TEXT_CYAN='\033[38;5;51m'
readonly TEXT_WHITE='\033[38;5;255m'
readonly TEXT_BLACK='\033[38;5;16m'
readonly TEXT_BOLD='\033[1m'
readonly TEXT_DIM='\033[2m'
readonly NC='\033[0m'

# Button styles
readonly BUTTON_PRIMARY="${BLOCK_BLUE}${TEXT_WHITE}${TEXT_BOLD}"
readonly BUTTON_SUCCESS="${BLOCK_GREEN}${TEXT_BLACK}${TEXT_BOLD}"
readonly BUTTON_WARNING="${BLOCK_YELLOW}${TEXT_BLACK}${TEXT_BOLD}"
readonly BUTTON_DANGER="${BLOCK_RED}${TEXT_WHITE}${TEXT_BOLD}"
readonly BUTTON_INFO="${BLOCK_CYAN}${TEXT_BLACK}${TEXT_BOLD}"
readonly BUTTON_SECONDARY="${BLOCK_GRAY}${TEXT_WHITE}"
readonly BUTTON_SELECTED="${BLOCK_PURPLE}${TEXT_WHITE}${TEXT_BOLD}"

# Unicode box drawing characters
readonly BOX_TOP_LEFT="┌"
readonly BOX_TOP_RIGHT="┐"
readonly BOX_BOTTOM_LEFT="└"
readonly BOX_BOTTOM_RIGHT="┘"
readonly BOX_HORIZONTAL="─"
readonly BOX_VERTICAL="│"
readonly BOX_TEE_DOWN="┬"
readonly BOX_TEE_UP="┴"
readonly BOX_TEE_RIGHT="├"
readonly BOX_TEE_LEFT="┤"
readonly BOX_CROSS="┼"

# Emojis for interface elements
readonly ICON_CURSOR="▶"
readonly ICON_SELECTED="●"
readonly ICON_UNSELECTED="○"
readonly ICON_ARROW_UP="↑"
readonly ICON_ARROW_DOWN="↓"
readonly ICON_ARROW_LEFT="←"
readonly ICON_ARROW_RIGHT="→"
readonly ICON_CHECK="✓"
readonly ICON_CROSS="✗"
readonly ICON_QUESTION="?"
readonly ICON_INFO="ℹ"
readonly ICON_WARNING="⚠"
readonly ICON_ERROR="✗"

# Initialize smart input system
init_cli_smart_input() {
    # Clear screen for clean interface
    clear

    # Create logs directory
    mkdir -p "$UDOS_ROOT/sandbox/logs/input"

    echo "🎨 CLI Smart Input System Initialized"
}

# Draw a box with title
draw_box() {
    local title="$1"
    local width="${2:-60}"
    local content="${3:-}"

    # Top border with title
    echo -ne "${TEXT_CYAN}${BOX_TOP_LEFT}"
    local title_length=${#title}
    local padding_each=$(( (width - title_length - 4) / 2 ))

    for ((i=1; i<=padding_each; i++)); do echo -ne "${BOX_HORIZONTAL}"; done
    echo -ne " ${TEXT_BOLD}${title}${NC}${TEXT_CYAN} "
    for ((i=1; i<=padding_each; i++)); do echo -ne "${BOX_HORIZONTAL}"; done
    echo -e "${BOX_TOP_RIGHT}${NC}"

    # Content lines
    if [[ -n "$content" ]]; then
        while IFS= read -r line; do
            echo -e "${TEXT_CYAN}${BOX_VERTICAL}${NC} ${line} ${TEXT_CYAN}${BOX_VERTICAL}${NC}"
        done <<< "$content"
    fi

    # Bottom border
    echo -ne "${TEXT_CYAN}${BOX_BOTTOM_LEFT}"
    for ((i=1; i<=width-2; i++)); do echo -ne "${BOX_HORIZONTAL}"; done
    echo -e "${BOX_BOTTOM_RIGHT}${NC}"
}

# Create a button with specified style
create_button() {
    local text="$1"
    local style="${2:-$BUTTON_SECONDARY}"
    local key="${3:-}"
    local width="${4:-20}"

    local text_length=${#text}
    local padding=$(( (width - text_length) / 2 ))

    if [[ -n "$key" ]]; then
        echo -ne "${style} [$key] "
    else
        echo -ne "${style} "
    fi

    for ((i=1; i<=padding; i++)); do echo -ne " "; done
    echo -ne "$text"
    for ((i=1; i<=padding; i++)); do echo -ne " "; done
    echo -ne " ${NC}"
}

# Display button menu
show_button_menu() {
    local title="$1"
    shift
    local options=("$@")

    echo ""
    echo -e "${TEXT_BOLD}${TEXT_CYAN}━━━ $title ━━━${NC}"
    echo ""

    local i=1
    for option in "${options[@]}"; do
        if [[ $i -lt 10 ]]; then
            create_button "$option" "$BUTTON_PRIMARY" "$i" 25
            echo ""
        else
            create_button "$option" "$BUTTON_SECONDARY" "${i}" 25
            echo ""
        fi
        ((i++))
    done
    echo ""
}

# Predictive text system
get_predictions() {
    local partial_input="$1"
    local context="${2:-general}"
    local max_suggestions="${3:-5}"

    # Common uDOS terms and commands
    local ucore_terms=("GHOST" "TOMB" "CRYPT" "DRONE" "KNIGHT" "IMP" "SORCERER" "WIZARD")
    local commands=("STATUS" "HELP" "GRID" "TEMPLATE" "ROLE" "BACKUP" "RESTORE")
    local modes=("CLI" "DESKTOP" "WEB" "AUTO")
    local types=("personal" "team" "enterprise" "development" "demo")

    local suggestions=()

    case "$context" in
        "role")
            for term in "${ucore_terms[@]}"; do
                if [[ "$term" == "$partial_input"* ]]; then
                    suggestions+=("$term")
                fi
            done
            ;;
        "command")
            for cmd in "${commands[@]}"; do
                if [[ "$cmd" == "$partial_input"* ]]; then
                    suggestions+=("$cmd")
                fi
            done
            ;;
        "mode")
            for mode in "${modes[@]}"; do
                if [[ "$mode" == "$partial_input"* ]]; then
                    suggestions+=("$mode")
                fi
            done
            ;;
        "type")
            for type in "${types[@]}"; do
                if [[ "$type" == "$partial_input"* ]]; then
                    suggestions+=("$type")
                fi
            done
            ;;
        *)
            # General predictions from all categories
            local all_terms=("${ucore_terms[@]}" "${commands[@]}" "${modes[@]}" "${types[@]}")
            for term in "${all_terms[@]}"; do
                if [[ "$term" == "$partial_input"* ]]; then
                    suggestions+=("$term")
                fi
            done
            ;;
    esac

    # Limit to max suggestions
    if [[ ${#suggestions[@]} -gt $max_suggestions ]]; then
        suggestions=("${suggestions[@]:0:$max_suggestions}")
    fi

    echo "${suggestions[@]}"
}

# Show predictive text suggestions
show_predictions() {
    local suggestions=("$@")

    if [[ ${#suggestions[@]} -gt 0 ]]; then
        echo -ne "${TEXT_DIM}${TEXT_YELLOW}"
        echo -n "💡 Suggestions: "
        for ((i=0; i<${#suggestions[@]}; i++)); do
            if [[ $i -eq 0 ]]; then
                echo -ne "${TEXT_BOLD}${suggestions[i]}${TEXT_DIM}"
            else
                echo -ne ", ${suggestions[i]}"
            fi
        done
        echo -e "${NC}"
    fi
}

# Enhanced input with predictive text and validation
smart_input_with_prediction() {
    local prompt="$1"
    local validation_type="${2:-text}"
    local suggestions_context="${3:-general}"
    local required="${4:-true}"
    local help_text="${5:-}"

    echo ""
    draw_box "$prompt" 70 "$help_text"
    echo ""

    local input=""
    local char=""
    local predictions=()

    # Show initial prompt
    echo -ne "${TEXT_CYAN}${ICON_CURSOR}${NC} ${TEXT_BOLD}Enter your choice:${NC} "

    # Read character by character for real-time predictions
    while true; do
        read -n1 -s char

        case "$char" in
            $'\n'|$'\r')
                # Enter pressed
                break
                ;;
            $'\b'|$'\177')
                # Backspace
                if [[ ${#input} -gt 0 ]]; then
                    input="${input%?}"
                    echo -ne "\b \b"

                    # Clear prediction line and redraw
                    echo -ne "\033[2K\033[1A\033[2K"
                    echo -ne "${TEXT_CYAN}${ICON_CURSOR}${NC} ${TEXT_BOLD}Enter your choice:${NC} $input"

                    # Update predictions
                    if [[ ${#input} -gt 0 ]]; then
                        maparray predictions <<< "$(get_predictions "$input" "$suggestions_context")"
                        echo ""
                        show_predictions "${predictions[@]}"
                        echo -ne "${TEXT_CYAN}${ICON_CURSOR}${NC} ${TEXT_BOLD}Enter your choice:${NC} $input"
                    fi
                fi
                ;;
            $'\t')
                # Tab - autocomplete with first suggestion
                if [[ ${#predictions[@]} -gt 0 ]]; then
                    local suggestion="${predictions[0]}"
                    local to_add="${suggestion:${#input}}"
                    input="$suggestion"
                    echo -ne "$to_add"
                fi
                ;;
            *)
                # Regular character
                if [[ -n "$char" ]]; then
                    input="$input$char"
                    echo -ne "$char"

                    # Get and show predictions
                    maparray predictions <<< "$(get_predictions "$input" "$suggestions_context")"
                    if [[ ${#predictions[@]} -gt 0 ]]; then
                        echo ""
                        show_predictions "${predictions[@]}"
                        echo -ne "${TEXT_CYAN}${ICON_CURSOR}${NC} ${TEXT_BOLD}Enter your choice:${NC} $input"
                    fi
                fi
                ;;
        esac
    done

    echo ""

    # Validate input
    if validate_cli_input "$input" "$validation_type" "$required"; then
        echo -e "${BUTTON_SUCCESS} ${ICON_CHECK} Valid input accepted ${NC}"
        echo "$input"
        return 0
    else
        echo -e "${BUTTON_DANGER} ${ICON_CROSS} Invalid input ${NC}"
        return 1
    fi
}

# Enhanced multiple choice with button-style options
smart_choice_buttons() {
    local prompt="$1"
    local help_text="$2"
    shift 2
    local options=("$@")

    draw_box "$prompt" 70 "$help_text"
    echo ""

    show_button_menu "Choose an option:" "${options[@]}"

    local choice=""
    while true; do
        echo -ne "${TEXT_CYAN}${ICON_CURSOR}${NC} ${TEXT_BOLD}Select option [1-${#options[@]}]:${NC} "
        read -r choice

        if [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -le "${#options[@]}" ]]; then
            local selected_index=$((choice - 1))
            local selected_option="${options[$selected_index]}"

            echo ""
            create_button "$selected_option" "$BUTTON_SELECTED" "✓" 30
            echo ""
            echo -e "${BUTTON_SUCCESS} ${ICON_CHECK} Selected: $selected_option ${NC}"

            echo "$selected_option"
            return 0
        else
            echo -e "${BUTTON_DANGER} ${ICON_CROSS} Invalid choice. Please select 1-${#options[@]} ${NC}"
        fi
    done
}

# Validation functions
validate_cli_input() {
    local input="$1"
    local type="$2"
    local required="$3"

    # Check if required and empty
    if [[ "$required" == "true" && -z "$input" ]]; then
        return 1
    fi

    case "$type" in
        "role")
            [[ "$input" =~ ^(GHOST|TOMB|CRYPT|DRONE|KNIGHT|IMP|SORCERER|WIZARD)$ ]]
            ;;
        "mode")
            [[ "$input" =~ ^(CLI|DESKTOP|WEB)$ ]]
            ;;
        "yes_no")
            [[ "$input" =~ ^(yes|no|y|n|true|false)$ ]]
            ;;
        "number")
            [[ "$input" =~ ^[0-9]+$ ]]
            ;;
        "email")
            [[ "$input" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]
            ;;
        *)
            # Default text validation - always true if not empty when required
            true
            ;;
    esac
}

# Array mapping function (for older bash compatibility)
maparray() {
    local -n arr_ref=$1
    local line
    arr_ref=()
    while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            arr_ref+=("$line")
        fi
    done
}

# Progress bar with color blocks
show_progress() {
    local current="$1"
    local total="$2"
    local width="${3:-50}"
    local title="${4:-Progress}"

    local percentage=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))

    echo ""
    echo -e "${TEXT_BOLD}$title: $percentage%${NC}"
    echo -ne "${TEXT_CYAN}["

    # Filled portion
    for ((i=0; i<filled; i++)); do
        echo -ne "${BLOCK_GREEN} ${NC}"
    done

    # Empty portion
    for ((i=0; i<empty; i++)); do
        echo -ne "${BLOCK_GRAY} ${NC}"
    done

    echo -e "${TEXT_CYAN}]${NC}"
    echo ""
}

# Animated typing effect
type_text() {
    local text="$1"
    local delay="${2:-0.03}"
    local color="${3:-$TEXT_WHITE}"

    echo -ne "$color"
    for ((i=0; i<${#text}; i++)); do
        echo -ne "${text:$i:1}"
        sleep "$delay"
    done
    echo -e "${NC}"
}

# Main interface for variable collection
cli_variable_interface() {
    local variable_name="$1"
    local variable_type="$2"
    local variable_prompt="$3"
    local variable_help="$4"
    local variable_values="$5"

    clear

    # Header
    echo -e "${TEXT_BOLD}${TEXT_CYAN}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                    🎨 uDOS Smart Input CLI                        ║"
    echo "║                     Variable Collection System                     ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    # Variable info
    echo -e "${TEXT_DIM}Variable: ${TEXT_BOLD}$variable_name${NC}${TEXT_DIM} (Type: $variable_type)${NC}"
    echo ""

    local result=""

    if [[ -n "$variable_values" ]]; then
        # Multiple choice with buttons
        IFS=',' read -ra values_array <<< "$variable_values"
        result=$(smart_choice_buttons "$variable_prompt" "$variable_help" "${values_array[@]}")
    else
        # Free text input with prediction
        local context=""
        case "$variable_type" in
            "role") context="role" ;;
            "mode") context="mode" ;;
            "string") context="general" ;;
            *) context="general" ;;
        esac

        result=$(smart_input_with_prediction "$variable_prompt" "$variable_type" "$context" true "$variable_help")
    fi

    echo "$result"
}

# Demo function
demo_cli_interface() {
    init_cli_smart_input

    echo "🎭 CLI Smart Input Demo"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Demo role selection
    cli_variable_interface "USER-ROLE" "role" "What is your role in uDOS?" "Choose your experience level and access capabilities" "GHOST,TOMB,CRYPT,DRONE,KNIGHT,IMP,SORCERER,WIZARD"

    echo ""
    echo "Demo complete! 🎉"
}

# Main function
main() {
    local command="${1:-demo}"

    case "$command" in
        "demo")
            demo_cli_interface
            ;;
        "collect")
            cli_variable_interface "$2" "$3" "$4" "$5" "$6"
            ;;
        "init")
            init_cli_smart_input
            ;;
        *)
            echo "Usage: $0 {demo|collect|init}"
            echo ""
            echo "Commands:"
            echo "  demo                                   - Run interactive demo"
            echo "  collect <name> <type> <prompt> <help> <values> - Collect single variable"
            echo "  init                                   - Initialize system"
            ;;
    esac
}

# Execute if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
