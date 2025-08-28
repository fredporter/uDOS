#!/bin/bash
# uDOS Smart Input CLI Simple v2.1 - ASCII Button Interface
# Compatible CLI input with color blocks and button-style options

set -euo pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Enhanced Colors (compatible with most terminals)
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly GRAY='\033[0;90m'
readonly BOLD='\033[1m'
readonly DIM='\033[2m'
readonly NC='\033[0m'

# Background colors for buttons
readonly BG_RED='\033[41m'
readonly BG_GREEN='\033[42m'
readonly BG_YELLOW='\033[43m'
readonly BG_BLUE='\033[44m'
readonly BG_PURPLE='\033[45m'
readonly BG_CYAN='\033[46m'
readonly BG_WHITE='\033[47m'
readonly BG_GRAY='\033[100m'

# Button styles
readonly BTN_PRIMARY="${BG_BLUE}${WHITE}${BOLD}"
readonly BTN_SUCCESS="${BG_GREEN}${WHITE}${BOLD}"
readonly BTN_WARNING="${BG_YELLOW}${WHITE}${BOLD}"
readonly BTN_DANGER="${BG_RED}${WHITE}${BOLD}"
readonly BTN_INFO="${BG_CYAN}${WHITE}${BOLD}"
readonly BTN_SECONDARY="${BG_GRAY}${WHITE}"
readonly BTN_SELECTED="${BG_PURPLE}${WHITE}${BOLD}"

# ASCII Art Elements
draw_header() {
    local title="$1"

    echo -e "${CYAN}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    printf "║%*s║\n" 68 " "
    printf "║%*s%s%*s║\n" $(((68-${#title})/2)) " " "$title" $(((68-${#title})/2)) " "
    printf "║%*s║\n" 68 " "
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Create button with ASCII styling
create_button() {
    local text="$1"
    local style="${2:-$BTN_SECONDARY}"
    local key="${3:-}"
    local selected="${4:-false}"

    if [[ "$selected" == "true" ]]; then
        style="$BTN_SELECTED"
    fi

    echo -ne "${style}"
    if [[ -n "$key" ]]; then
        printf " [%s] %-20s " "$key" "$text"
    else
        printf " %-24s " "$text"
    fi
    echo -ne "${NC}"
}

# Show options as buttons with default highlighting
show_options_menu() {
    local title="$1"
    local default_option="${2:-1}"
    shift 2
    local options=("$@")

    echo ""
    echo -e "${BOLD}${CYAN}$title${NC}"
    echo -e "${CYAN}$(printf '━%.0s' {1..50})${NC}"
    echo ""

    local i=1
    for option in "${options[@]}"; do
        if [[ $i -eq $default_option ]]; then
            create_button "$option ⭐" "$BTN_INFO" "$i" "true"
            echo -e " ${DIM}(default)${NC}"
        else
            create_button "$option" "$BTN_PRIMARY" "$i"
            echo ""
        fi
        ((i++))
    done
    echo ""
    echo -e "${DIM}💡 Press Enter for default option ⭐ or type number [1-${#options[@]}]${NC}"
    echo ""
}# Get predictions for input
get_simple_predictions() {
    local input="$1"
    local context="${2:-general}"

    case "$context" in
        "role")
            echo "GHOST TOMB CRYPT DRONE KNIGHT IMP SORCERER WIZARD" | tr ' ' '\n' | grep "^${input}" | head -3
            ;;
        "mode")
            echo "CLI DESKTOP WEB" | tr ' ' '\n' | grep "^${input}" | head -3
            ;;
        "type")
            echo "personal team enterprise development demo" | tr ' ' '\n' | grep "^${input}" | head -3
            ;;
        *)
            echo "yes no true false enabled disabled" | tr ' ' '\n' | grep "^${input}" | head -3
            ;;
    esac
}

# Get smart default based on context and variable type
get_smart_default() {
    local var_name="$1"
    local var_type="$2"
    local context="$3"
    local current_role="$(cat "$UDOS_ROOT/sandbox/current-role.conf" 2>/dev/null | grep "^ROLE=" | cut -d'=' -f2 | tr -d '"' || echo "GHOST")"

    case "$var_name" in
        "USER-ROLE"|"ROLE")
            echo "$current_role"
            ;;
        "DISPLAY-MODE")
            echo "CLI"
            ;;
        "INSTALLATION-TYPE")
            echo "personal"
            ;;
        "SECURITY-LEVEL")
            case "$current_role" in
                "GHOST"|"TOMB") echo "basic" ;;
                "CRYPT"|"KNIGHT") echo "enhanced" ;;
                *) echo "standard" ;;
            esac
            ;;
        "DEVELOPER-NAME")
            echo "$(whoami)"
            ;;
        "PROJECT-TYPE")
            echo "learning"
            ;;
        "ADVENTURE-MODE")
            echo "enabled"
            ;;
        "DETAIL-LEVEL")
            case "$current_role" in
                "GHOST") echo "VERBOSE" ;;
                "WIZARD"|"SORCERER") echo "MINIMAL" ;;
                *) echo "STANDARD" ;;
            esac
            ;;
        *)
            # Context-based defaults
            case "$context" in
                "yes_no"|"boolean") echo "yes" ;;
                "mode") echo "CLI" ;;
                "type") echo "personal" ;;
                *) echo "" ;;
            esac
            ;;
    esac
}

# Get smart default option index for multiple choice
get_smart_default_index() {
    local var_name="$1"
    shift
    local options=("$@")
    local smart_default
    smart_default=$(get_smart_default "$var_name" "" "")

    if [[ -n "$smart_default" ]]; then
        for ((i=0; i<${#options[@]}; i++)); do
            if [[ "${options[$i]}" == "$smart_default" ]]; then
                echo $((i + 1))
                return
            fi
        done
    fi

    # Default to first option if no smart match
    echo "1"
}

# Show contextual help for input
show_input_help() {
    local var_type="$1"
    local context="$2"

    echo ""
    echo -e "${BTN_INFO} 📖 Input Help ${NC}"
    echo -e "${CYAN}─────────────────────────────────────────${NC}"

    case "$var_type" in
        "role")
            echo -e "${WHITE}Available roles:${NC}"
            echo -e "  👻 GHOST    - Demo access, learning mode"
            echo -e "  🗿 TOMB     - Basic storage and organization"
            echo -e "  🔐 CRYPT    - Security and protection features"
            echo -e "  🤖 DRONE    - Automation and efficiency"
            echo -e "  ⚔️  KNIGHT   - System protection and service"
            echo -e "  😈 IMP      - Creative development tools"
            echo -e "  🧙‍♂️ SORCERER - Advanced administration"
            echo -e "  🌟 WIZARD   - Complete system mastery"
            ;;
        "mode")
            echo -e "${WHITE}Display modes:${NC}"
            echo -e "  CLI     - Terminal command interface"
            echo -e "  DESKTOP - Native desktop application"
            echo -e "  WEB     - Browser-based interface"
            ;;
        *)
            echo -e "${WHITE}General help:${NC}"
            echo -e "  • Type '?' or 'help' for this help"
            echo -e "  • Type '!' for context suggestions"
            echo -e "  • Type 'prev' to use previous value"
            echo -e "  • Press Enter to use default (if available)"
            ;;
    esac

    echo -e "${CYAN}─────────────────────────────────────────${NC}"
    echo ""
}

# Show context-specific suggestions
show_context_suggestions() {
    local context="$1"
    local var_name="$2"

    echo ""
    echo -e "${BTN_INFO} 💡 Smart Suggestions ${NC}"
    echo -e "${CYAN}─────────────────────────────────────────${NC}"

    case "$context" in
        "role")
            local current_role="$(cat "$UDOS_ROOT/sandbox/current-role.conf" 2>/dev/null | grep "^ROLE=" | cut -d'=' -f2 | tr -d '"' || echo "GHOST")"
            echo -e "${YELLOW}💡 Current role: $current_role${NC}"
            echo -e "${WHITE}Suggested progression:${NC}"
            case "$current_role" in
                "GHOST") echo "  → Try TOMB for basic features" ;;
                "TOMB") echo "  → Try CRYPT for security or DRONE for automation" ;;
                "CRYPT"|"DRONE") echo "  → Try KNIGHT for protection or IMP for development" ;;
                "KNIGHT"|"IMP") echo "  → Try SORCERER for advanced features" ;;
                "SORCERER") echo "  → Try WIZARD for complete access" ;;
                "WIZARD") echo "  → You have maximum access!" ;;
            esac
            ;;
        "type")
            echo -e "${WHITE}Based on your role, consider:${NC}"
            echo -e "  • personal    - Individual use"
            echo -e "  • development - Building and testing"
            echo -e "  • team        - Collaborative work"
            echo -e "  • enterprise  - Large organization"
            ;;
        *)
            echo -e "${WHITE}Context-aware suggestions will appear here${NC}"
            ;;
    esac

    echo -e "${CYAN}─────────────────────────────────────────${NC}"
    echo ""
}

# Get previous value for a variable (from logs or history)
get_previous_value() {
    local var_name="$1"
    local log_file="$UDOS_ROOT/sandbox/logs/input/variable-history.log"

    if [[ -f "$log_file" ]]; then
        grep "^$var_name=" "$log_file" | tail -1 | cut -d'=' -f2- | tr -d '"'
    fi
}

# Save variable value to history
save_to_history() {
    local var_name="$1"
    local var_value="$2"
    local log_file="$UDOS_ROOT/sandbox/logs/input/variable-history.log"

# Enhanced validation with smart suggestions
validate_input() {
    local input="$1"
    local var_type="$2"
    local options_array=("${@:3}")

    # Empty input is handled by caller (default fallback)
    if [[ -z "$input" ]]; then
        return 0
    fi

    case "$var_type" in
        "role")
            # Accept role names (case insensitive)
            local upper_input="$(echo "$input" | tr '[:lower:]' '[:upper:]')"
            for role in "GHOST" "TOMB" "CRYPT" "DRONE" "KNIGHT" "IMP" "SORCERER" "WIZARD"; do
                if [[ "$upper_input" == "$role" ]]; then
                    echo "$role"
                    return 0
                fi
            done
            ;;
        "mode")
            # Accept mode names (case insensitive)
            local upper_input="$(echo "$input" | tr '[:lower:]' '[:upper:]')"
            for mode in "CLI" "DESKTOP" "WEB"; do
                if [[ "$upper_input" == "$mode" ]]; then
                    echo "$mode"
                    return 0
                fi
            done
            ;;
        "number")
            # Validate numeric input within range
            if [[ "$input" =~ ^[0-9]+$ ]] && [ "$input" -ge 1 ] && [ "$input" -le "${#options_array[@]}" ]; then
                echo "$input"
                return 0
            fi
            ;;
    esac

    # If validation fails, return empty
    return 1
}

# Smart tab completion simulation
get_completion_suggestions() {
    local partial="$1"
    local var_type="$2"

    case "$var_type" in
        "role")
            local roles=("GHOST" "TOMB" "CRYPT" "DRONE" "KNIGHT" "IMP" "SORCERER" "WIZARD")
            local matches=()
            local upper_partial="$(echo "$partial" | tr '[:lower:]' '[:upper:]')"

            for role in "${roles[@]}"; do
                if [[ "$role" == "$upper_partial"* ]]; then
                    matches+=("$role")
                fi
            done

            if [ ${#matches[@]} -eq 1 ]; then
                echo "${matches[0]}"
            elif [ ${#matches[@]} -gt 1 ]; then
                echo -e "\n${YELLOW}Matches: ${matches[*]}${NC}"
            fi
            ;;
    esac
}

# Progress indicator for longer operations
show_progress() {
    local step="$1"
    local total="$2"
    local description="$3"

    local progress=$((step * 100 / total))
    local filled=$((progress / 5))
    local empty=$((20 - filled))

    printf "\r${CYAN}["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] %d%% - %s${NC}" "$progress" "$description"

    if [ "$step" -eq "$total" ]; then
        echo ""
    fi
}

# Keyboard shortcut helper
# Smart context detection - automatically determine best input method
detect_optimal_input_method() {
    local var_name="$1"
    local var_type="$2"
    local context="$3"
    local options_count="${4:-0}"

    # If we have a small number of options, use buttons
    if [[ "$options_count" -gt 0 && "$options_count" -le 8 ]]; then
        echo "buttons"
        return 0
    fi

    # For role selection, always use buttons
    if [[ "$var_type" == "role" || "$var_name" =~ role ]]; then
        echo "buttons"
        return 0
    fi

    # For yes/no questions, use buttons
    if [[ "$var_type" == "boolean" || "$var_type" == "yesno" ]]; then
        echo "buttons"
        return 0
    fi

    # For long text, use enhanced input
    if [[ "$var_type" =~ text|description|comment ]]; then
        echo "enhanced"
        return 0
    fi

    # Default to enhanced input with smart features
    echo "enhanced"
}

# Auto-complete suggestions based on context
get_smart_suggestions() {
    local partial_input="$1"
    local context="$2"
    local var_type="$3"

    case "$context" in
        "installation")
            case "$partial_input" in
                "dev"*) echo "development" ;;
                "per"*) echo "personal" ;;
                "tea"*) echo "team" ;;
                "ent"*) echo "enterprise" ;;
            esac
            ;;
        "role")
            case "$(echo "$partial_input" | tr '[:lower:]' '[:upper:]')" in
                "G"*) echo "GHOST" ;;
                "T"*) echo "TOMB" ;;
                "C"*) echo "CRYPT" ;;
                "D"*) echo "DRONE" ;;
                "K"*) echo "KNIGHT" ;;
                "I"*) echo "IMP" ;;
                "S"*) echo "SORCERER" ;;
                "W"*) echo "WIZARD" ;;
            esac
            ;;
        "mode")
            case "$(echo "$partial_input" | tr '[:lower:]' '[:upper:]')" in
                "C"*) echo "CLI" ;;
                "D"*) echo "DESKTOP" ;;
                "W"*) echo "WEB" ;;
            esac
            ;;
    esac
}

# Smart formatting based on input type
format_display_value() {
    local value="$1"
    local var_type="$2"

    case "$var_type" in
        "role")
            case "$value" in
                "GHOST") echo "👻 $value" ;;
                "TOMB") echo "🗿 $value" ;;
                "CRYPT") echo "🔐 $value" ;;
                "DRONE") echo "🤖 $value" ;;
                "KNIGHT") echo "⚔️ $value" ;;
                "IMP") echo "😈 $value" ;;
                "SORCERER") echo "🧙‍♂️ $value" ;;
                "WIZARD") echo "🌟 $value" ;;
                *) echo "$value" ;;
            esac
            ;;
        "mode")
            case "$value" in
                "CLI") echo "💻 $value" ;;
                "DESKTOP") echo "🖥️ $value" ;;
                "WEB") echo "🌐 $value" ;;
                *) echo "$value" ;;
            esac
            ;;
        "boolean"|"yesno")
            case "$(echo "$value" | tr '[:lower:]' '[:upper:]')" in
                "TRUE"|"YES"|"Y"|"1") echo "✅ Yes" ;;
                "FALSE"|"NO"|"N"|"0") echo "❌ No" ;;
                *) echo "$value" ;;
            esac
            ;;
        *)
            echo "$value"
            ;;
    esac
}

# Context-aware help that adapts to current situation
show_adaptive_help() {
    local var_name="$1"
    local var_type="$2"
    local context="$3"
    local current_role="$(cat "$UDOS_ROOT/sandbox/current-role.conf" 2>/dev/null | grep "^ROLE=" | cut -d'=' -f2 | tr -d '"' || echo "GHOST")"

    echo ""
    echo -e "${BTN_INFO} 🎯 Smart Help - Context: $context ${NC}"
    echo -e "${CYAN}─────────────────────────────────────────${NC}"
    echo -e "${WHITE}Current role: $(format_display_value "$current_role" "role")${NC}"
    echo ""

    case "$context" in
        "startup")
            echo -e "${WHITE}Startup Configuration Help:${NC}"
            echo -e "  • This affects how uDOS starts and behaves"
            echo -e "  • Your current role ($current_role) determines available options"
            echo -e "  • Changes are saved for future sessions"
            ;;
        "installation")
            echo -e "${WHITE}Installation Type Help:${NC}"
            echo -e "  • personal    - Single user, local machine"
            echo -e "  • development - For coding and testing"
            echo -e "  • team        - Shared workspace setup"
            echo -e "  • enterprise  - Large organization deployment"
            ;;
        "adventure")
            echo -e "${WHITE}Adventure System Help:${NC}"
            echo -e "  • Stories adapt to your role and experience level"
            echo -e "  • Progress is saved across sessions"
            echo -e "  • Achievements unlock new features"
            ;;
        *)
            echo -e "${WHITE}General context: $context${NC}"
            ;;
    esac

    echo ""
# Universal smart input - automatically routes to best method
universal_smart_input() {
    local var_name="$1"
    local prompt_text="$2"
    local var_type="${3:-text}"
    local context="${4:-general}"
    local default_value="$5"
    shift 5
    local options=("$@")

    # Smart method detection
    local optimal_method
    optimal_method=$(detect_optimal_input_method "$var_name" "$var_type" "$context" "${#options[@]}")

    # Show context banner
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} ${BOLD}🎯 Smart Input System${NC} ${BLUE}║${NC}"
    echo -e "${BLUE}╠══════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║${NC} Variable: ${CYAN}$var_name${NC} | Type: ${YELLOW}$var_type${NC} | Context: ${GREEN}$context${NC} ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC} Method: ${MAGENTA}$optimal_method${NC} | Options: ${WHITE}${#options[@]}${NC} ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"

    # Route to appropriate method
    case "$optimal_method" in
        "buttons")
            if [[ ${#options[@]} -gt 0 ]]; then
                multiple_choice_buttons "$prompt_text" "Select from options below" "" "${options[@]}"
            else
                # Create options based on type
                case "$var_type" in
                    "role")
                        multiple_choice_buttons "$prompt_text" "Choose your role" "1" "👻 GHOST" "🗿 TOMB" "🔐 CRYPT" "🤖 DRONE" "⚔️ KNIGHT" "😈 IMP" "🧙‍♂️ SORCERER" "🌟 WIZARD"
                        ;;
                    "mode")
                        multiple_choice_buttons "$prompt_text" "Choose display mode" "1" "💻 CLI" "🖥️ DESKTOP" "🌐 WEB"
                        ;;
                    "boolean"|"yesno")
                        multiple_choice_buttons "$prompt_text" "Choose yes or no" "1" "✅ Yes" "❌ No"
                        ;;
                    *)
                        smart_input_with_defaults "$prompt_text" "$var_type" "$context" "Enhanced input with smart features" "$default_value"
                        ;;
                esac
            fi
            ;;
        "enhanced"|*)
            smart_input_with_defaults "$prompt_text" "$var_type" "$context" "Enhanced input with smart features" "$default_value"
            ;;
    esac
}

# Quick access functions for common patterns
quick_role_select() {
    local current_role="${1:-$(cat "$UDOS_ROOT/sandbox/current-role.conf" 2>/dev/null | grep "^ROLE=" | cut -d'=' -f2 | tr -d '"' || echo "GHOST")}"
    universal_smart_input "USER_ROLE" "Select your uDOS role" "role" "role_selection" "$current_role"
}

quick_mode_select() {
    local default_mode="${1:-CLI}"
    universal_smart_input "DISPLAY_MODE" "Choose your preferred interface" "mode" "interface" "$default_mode"
}

quick_yesno() {
    local question="$1"
    local default="${2:-Yes}"
    universal_smart_input "CONFIRMATION" "$question" "boolean" "confirmation" "$default"
}

# Smart input with memory - remembers and suggests based on history
smart_input_with_memory() {
    local var_name="$1"
    local prompt_text="$2"
    local var_type="${3:-text}"
    local context="${4:-general}"

    # Get smart default from history or context
    local smart_default
    smart_default=$(get_previous_value "$var_name")

    if [[ -z "$smart_default" ]]; then
        smart_default=$(get_smart_default "$var_name" "$var_type" "$context")
    fi

    # Use universal smart input with memory
    universal_smart_input "$var_name" "$prompt_text" "$var_type" "$context" "$smart_default"
}

# Enhanced input with smart defaults and predictions
smart_input_with_defaults() {
    local prompt="$1"
    local validation_type="${2:-text}"
    local context="${3:-general}"
    local help_text="${4:-}"
    local default_value="${5:-}"

    echo ""
    echo -e "${CYAN}┌─ ${BOLD}$prompt${NC}${CYAN} ─┐${NC}"
    if [[ -n "$help_text" ]]; then
        echo -e "${GRAY}│ 💡 $help_text${NC}"
    fi
    if [[ -n "$default_value" ]]; then
        echo -e "${GRAY}│ 🎯 Default: ${BOLD}$default_value${NC}${GRAY} (press Enter to use)${NC}"
    fi
    echo -e "${CYAN}└─────────────────────────────────────────────────────────────────┘${NC}"
    echo ""

    local input=""
    local attempt=1
    local max_attempts=3

    while [[ $attempt -le $max_attempts ]]; do
        if [[ -n "$default_value" ]]; then
            echo -ne "${CYAN}❯${NC} ${BOLD}Enter value${NC} ${DIM}[${default_value}]${NC}: "
        else
            echo -ne "${CYAN}❯${NC} ${BOLD}Enter value:${NC} "
        fi

        read -r input

        # Handle special commands and shortcuts
        if [[ "$input" == "?" || "$input" == "help" ]]; then
            show_input_help "$var_type" "$context"
            continue
        elif [[ "$input" == "!" ]]; then
            show_context_suggestions "$context" "$var_name"
            continue
        elif [[ "$input" == "prev" || "$input" == "last" ]]; then
            local prev_value
            prev_value=$(get_previous_value "$var_name")
            if [[ -n "$prev_value" ]]; then
                input="$prev_value"
                echo -e "${BTN_INFO} 📚 Using previous: $prev_value ${NC}"
            else
                echo -e "${YELLOW}⚠ No previous value found${NC}"
                continue
            fi
        fi
            if [[ -n "$default_value" ]]; then
                input="$default_value"
                echo -e "${BTN_INFO} ⭐ Using default: $default_value ${NC}"
            else
                echo -e "${YELLOW}⚠ Empty input detected${NC}"
                if [[ $attempt -lt $max_attempts ]]; then
                    echo -e "${YELLOW}Please enter a value (attempt $((attempt+1))/$max_attempts)${NC}"
                    ((attempt++))
                    continue
                else
                    echo -e "${BTN_DANGER} ✗ No input provided ${NC}"
                    return 1
                fi
            fi
        fi

        if [[ -n "$input" ]]; then
            # Show predictions if input is partial and not using default
            if [[ "$input" != "$default_value" ]]; then
                local predictions
                predictions=$(get_simple_predictions "$input" "$context")
                if [[ -n "$predictions" && ${#input} -lt 10 ]]; then
                    echo -e "${DIM}${YELLOW}💡 Suggestions: $(echo "$predictions" | tr '\n' ' ')${NC}"
                fi
            fi
        fi

        # Validate input
        if validate_input "$input" "$validation_type"; then
            echo -e "${BTN_SUCCESS} ✓ Valid input ${NC}"
            echo "$input"
            return 0
        else
            echo -e "${BTN_DANGER} ✗ Invalid input ${NC}"
            if [[ $attempt -lt $max_attempts ]]; then
                echo -e "${YELLOW}Please try again (attempt $((attempt+1))/$max_attempts)${NC}"
            fi
            ((attempt++))
        fi
    done

    echo -e "${BTN_DANGER} ✗ Maximum attempts reached ${NC}"
    return 1
}# Multiple choice with styled buttons and smart defaults
multiple_choice_buttons() {
    local prompt="$1"
    local help_text="$2"
    local default_index="${3:-1}"
    shift 3
    local options=("$@")

    echo ""
    draw_header "🎯 $prompt"

    if [[ -n "$help_text" ]]; then
        echo -e "${GRAY}💡 $help_text${NC}"
        echo ""
    fi

    show_options_menu "Choose an option:" "$default_index" "${options[@]}"

    local choice=""
    local attempts=0
    local max_attempts=3

    while [[ $attempts -lt $max_attempts ]]; do
        echo -ne "${CYAN}❯${NC} ${BOLD}Select [1-${#options[@]}] or Enter for default:${NC} "
        read -r choice

        # Handle empty input (use default)
        if [[ -z "$choice" ]]; then
            choice="$default_index"
            echo -e "${BTN_INFO} ⭐ Using default option ${NC}"
        fi

        if [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -le "${#options[@]}" ]]; then
            local selected_index=$((choice - 1))
            local selected_option="${options[$selected_index]}"

            echo ""
            if [[ "$choice" -eq "$default_index" ]]; then
                echo -e "Selected: ${BTN_SELECTED} $selected_option ⭐ ${NC} ${DIM}(default)${NC}"
            else
                echo -e "Selected: ${BTN_SELECTED} $selected_option ${NC}"
            fi
            echo ""

            echo "$selected_option"
            return 0
        else
            echo -e "${BTN_DANGER} ✗ Invalid choice. Select 1-${#options[@]} or press Enter for default ${NC}"
            ((attempts++))
        fi
    done

    # Fallback to default if max attempts reached
    if [[ "$default_index" -ge 1 ]] && [[ "$default_index" -le "${#options[@]}" ]]; then
        local fallback_index=$((default_index - 1))
        local fallback_option="${options[$fallback_index]}"
        echo -e "${BTN_WARNING} ⚠ Using fallback default: $fallback_option ${NC}"
        echo "$fallback_option"
        return 0
    fi

    return 1
}

# Input validation
validate_input() {
    local input="$1"
    local type="$2"

    [[ -n "$input" ]] || return 1

    case "$type" in
        "role")
            [[ "$input" =~ ^(GHOST|TOMB|CRYPT|DRONE|KNIGHT|IMP|SORCERER|WIZARD)$ ]]
            ;;
        "mode")
            [[ "$input" =~ ^(CLI|DESKTOP|WEB)$ ]]
            ;;
        "yes_no"|"boolean")
            [[ "$input" =~ ^(yes|no|y|n|true|false|enabled|disabled)$ ]]
            ;;
        "number")
            [[ "$input" =~ ^[0-9]+$ ]]
            ;;
        *)
            true
            ;;
    esac
}

# Main variable collection interface with smart defaults
collect_variable_enhanced() {
    local var_name="$1"
    local var_type="$2"
    local var_prompt="$3"
    local var_help="$4"
    local var_values="$5"

    # Clear screen for clean interface
    clear

    # Show header
    draw_header "🎨 uDOS Variable Collection"
    echo -e "${DIM}Variable: ${BOLD}$var_name${NC}${DIM} | Type: $var_type${NC}"
    echo ""

    local result=""

    if [[ -n "$var_values" ]]; then
        # Multiple choice with smart defaults
        IFS=',' read -ra values_array <<< "$var_values"
        local smart_default_idx
        smart_default_idx=$(get_smart_default_index "$var_name" "${values_array[@]}")
        result=$(multiple_choice_buttons "$var_prompt" "$var_help" "$smart_default_idx" "${values_array[@]}")
    else
        # Free text input with smart defaults
        local context=""
        case "$var_type" in
            *"role"*) context="role" ;;
            *"mode"*) context="mode" ;;
            *"type"*) context="type" ;;
            *"security"*) context="security" ;;
            *) context="general" ;;
        esac

        local smart_default
        smart_default=$(get_smart_default "$var_name" "$var_type" "$context")
        result=$(smart_input_with_defaults "$var_prompt" "$var_type" "$context" "$var_help" "$smart_default")
    fi

    if [[ $? -eq 0 ]]; then
        echo "$result"
        return 0
    else
        return 1
    fi
}# Progress indicator for stories
show_story_progress() {
    local current="$1"
    local total="$2"
    local title="${3:-Story Progress}"

    local percentage=$((current * 100 / total))
    local filled=$((current * 5 / total))

    echo ""
    echo -e "${BOLD}$title${NC}"
    echo -ne "${CYAN}["
    for ((i=0; i<filled; i++)); do
        echo -ne "${GREEN}█${NC}"
    done
    for ((i=filled; i<5; i++)); do
        echo -ne "${GRAY}░${NC}"
    done
    echo -e "${CYAN}] ${percentage}%${NC}"
    echo ""
}

# Demo function
demo_enhanced_cli() {
    clear
    draw_header "🎭 Enhanced CLI Smart Input Demo"

    echo -e "${YELLOW}This demo shows the enhanced CLI interface capabilities:${NC}"
    echo ""
    echo -e "• ${GREEN}Color-coded buttons and interfaces${NC}"
    echo -e "• ${BLUE}Predictive text suggestions${NC}"
    echo -e "• ${PURPLE}ASCII-styled boxes and menus${NC}"
    echo -e "• ${CYAN}Input validation and error handling${NC}"
    echo ""

    read -p "Press Enter to continue with demo..."

    # Demo variable collection
    echo ""
    echo -e "${BOLD}Demo 1: Role Selection${NC}"
    collect_variable_enhanced "USER-ROLE" "role" "Select your uDOS role" "Your role determines your capabilities and access level" "GHOST,TOMB,CRYPT,DRONE,KNIGHT,IMP,SORCERER,WIZARD"

    echo ""
    read -p "Press Enter for next demo..."

    echo ""
    echo -e "${BOLD}Demo 2: Free Text Input${NC}"
    collect_variable_enhanced "DEVELOPER-NAME" "string" "Enter your developer name" "This will be used for project attribution and logs" ""

    echo ""
    echo -e "${BTN_SUCCESS} 🎉 Demo Complete! ${NC}"
}

# Integration with variable manager
variable_manager_integration() {
    local var_name="$1"
    local var_type="$2"
    local var_prompt="$3"
    local var_help="$4"
    local var_values="$5"
    local session_id="${6:-current}"

    # Use enhanced CLI to collect the variable
    local result
    result=$(collect_variable_enhanced "$var_name" "$var_type" "$var_prompt" "$var_help" "$var_values")

    if [[ $? -eq 0 && -n "$result" ]]; then
        # Set the variable using the variable manager
        if [[ -x "$UDOS_ROOT/uCORE/code/variable-manager.sh" ]]; then
            "$UDOS_ROOT/uCORE/code/variable-manager.sh" SET "$var_name" "$result" "$session_id"
            echo -e "${BTN_SUCCESS} Variable $var_name set to: $result ${NC}"
        fi
        return 0
    else
        echo -e "${BTN_DANGER} Failed to collect variable $var_name ${NC}"
        return 1
    fi
}

# Main function
main() {
    local command="${1:-demo}"

    case "$command" in
        "demo")
            demo_enhanced_cli
            ;;
        "collect")
            collect_variable_enhanced "$2" "$3" "$4" "$5" "$6"
            ;;
        "integrate")
            variable_manager_integration "$2" "$3" "$4" "$5" "$6" "$7"
            ;;
        "test")
            # Quick test
            clear
            draw_header "🧪 Quick Test"
            multiple_choice_buttons "Choose a test option" "This is a test of the button system" "Option A" "Option B" "Option C"
            ;;
        *)
            echo "🎨 uDOS Enhanced CLI Smart Input System"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "Commands:"
            echo "  demo                                           - Run interactive demo"
            echo "  collect <name> <type> <prompt> <help> <values> - Collect variable"
            echo "  integrate <name> <type> <prompt> <help> <values> <session> - Collect and set variable"
            echo "  test                                           - Quick interface test"
            echo ""
            echo "Features:"
            echo "  • ASCII color block styling"
            echo "  • Button-style option selection"
            echo "  • Predictive text suggestions"
            echo "  • Input validation"
            echo "  • Progress indicators"
            echo "  • Variable manager integration"
            ;;
    esac
}

# Execute if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
