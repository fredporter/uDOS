#!/bin/bash
# uDOS Input Module v1.3
# Advanced input processing, command history, and smart suggestions

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
UCORE="$UDOS_ROOT/uCORE"
UMEMORY="$UDOS_ROOT/uMEMORY"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# History file
HISTORY_FILE="$UMEMORY/user/command_history.log"

# Add command to history
add_to_history() {
    local command="$1"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    local session_id="${SESSION_ID:-$(date +%s)}"
    
    # Create history directory if needed
    mkdir -p "$(dirname "$HISTORY_FILE")"
    
    # Add to history with metadata
    echo "$timestamp|$session_id|$command" >> "$HISTORY_FILE"
    
    # Keep only last 1000 commands
    if [[ -f "$HISTORY_FILE" ]]; then
        tail -1000 "$HISTORY_FILE" > "$HISTORY_FILE.tmp" && mv "$HISTORY_FILE.tmp" "$HISTORY_FILE"
    fi
}

# Show command history
show_command_history() {
    local count="${1:-20}"
    
    echo -e "${BLUE}📚 Command History${NC}"
    echo ""
    
    if [[ -f "$HISTORY_FILE" ]]; then
        local i=1
        tail -"$count" "$HISTORY_FILE" | while IFS='|' read -r timestamp session_id command; do
            echo -e "${CYAN}[$i]${NC} ${YELLOW}$timestamp${NC} - $command"
            ((i++))
        done
    else
        echo "No command history found"
    fi
}

# Search command history
search_command_history() {
    local search_term="$1"
    
    if [[ -z "$search_term" ]]; then
        echo -e "${RED}Please provide a search term${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🔍 Searching history for: '$search_term'${NC}"
    echo ""
    
    if [[ -f "$HISTORY_FILE" ]]; then
        local results=$(grep -i "$search_term" "$HISTORY_FILE")
        
        if [[ -n "$results" ]]; then
            local i=1
            echo "$results" | while IFS='|' read -r timestamp session_id command; do
                echo -e "${CYAN}[$i]${NC} ${YELLOW}$timestamp${NC} - $command"
                ((i++))
            done
        else
            echo "No matching commands found"
        fi
    else
        echo "No command history available"
    fi
}

# Get smart suggestions based on context
get_smart_suggestions() {
    local input="$1"
    local context="${2:-general}"
    
    echo -e "${BLUE}💡 Smart Suggestions${NC}"
    echo ""
    
    # Suggest based on partial input
    case "$input" in
        "h"*|"help"*)
            echo "• help [topic] - Show help for specific topic"
            echo "• help areas - Show system areas"
            echo "• help development - Development guide"
            ;;
        "s"*|"status"*)
            echo "• status - Full system status"
            echo "• status health - Health check only"
            echo "• status modules - Module status"
            ;;
        "u"*|"user"*)
            echo "• user info - Show user information"
            echo "• user login - Authenticate user"
            echo "• user setup - Create user account"
            ;;
        "m"*|"memory"*)
            echo "• memory status - Memory system status"
            echo "• memory search <term> - Search memory"
            echo "• memory backup - Create backup"
            ;;
        "d"*|"display"*)
            echo "• display - Show main banner"
            echo "• display simple - Simple banner"
            echo "• display resize - Terminal size tips"
            ;;
        *)
            # Show most common commands
            echo "Common commands:"
            echo "• help - Show help system"
            echo "• status - System status"
            echo "• dashboard - Interactive dashboard"
            echo "• user info - User information"
            echo "• memory status - Memory system"
            ;;
    esac
    
    # Show recent commands if available
    if [[ -f "$HISTORY_FILE" ]]; then
        echo ""
        echo -e "${CYAN}Recent commands:${NC}"
        tail -5 "$HISTORY_FILE" | while IFS='|' read -r timestamp session_id command; do
            echo "• $command"
        done
    fi
}

# Enhanced prompt with context
show_enhanced_prompt() {
    local mode="${1:-normal}"
    local context="${2:-}"
    
    case "$mode" in
        "dev")
            echo -ne "${PURPLE}[DEV]${NC} ${CYAN}uDOS${NC} ❯ "
            ;;
        "admin")
            echo -ne "${RED}[ADMIN]${NC} ${CYAN}uDOS${NC} ❯ "
            ;;
        "session")
            echo -ne "${YELLOW}[SESSION]${NC} ${CYAN}uDOS${NC} ❯ "
            ;;
        *)
            echo -ne "${CYAN}uDOS${NC} ❯ "
            ;;
    esac
}

# Input validation
validate_input() {
    local input="$1"
    local type="${2:-command}"
    
    case "$type" in
        "command")
            # Check if command exists in modules
            local command_name=$(echo "$input" | awk '{print $1}')
            local module_file="$UDOS_ROOT/uSCRIPT/library/ucode/${command_name}.sh"
            
            if [[ -f "$module_file" ]]; then
                return 0
            else
                echo -e "${YELLOW}⚠️ Unknown command: $command_name${NC}"
                echo "Type 'help' for available commands"
                return 1
            fi
            ;;
        "path")
            if [[ -e "$input" ]]; then
                return 0
            else
                echo -e "${RED}❌ Path not found: $input${NC}"
                return 1
            fi
            ;;
        "number")
            if [[ "$input" =~ ^[0-9]+$ ]]; then
                return 0
            else
                echo -e "${RED}❌ Invalid number: $input${NC}"
                return 1
            fi
            ;;
    esac
}

# Auto-completion suggestions
show_completions() {
    local partial="$1"
    
    echo -e "${BLUE}📝 Completions for '$partial':${NC}"
    echo ""
    
    # Find matching modules
    local modules=$(find "$UDOS_ROOT/uSCRIPT/library/ucode" -name "${partial}*.sh" -exec basename {} .sh \;)
    
    if [[ -n "$modules" ]]; then
        echo "Modules:"
        echo "$modules" | while read -r module; do
            echo "• $module"
        done
    fi
    
    # Find matching commands from history
    if [[ -f "$HISTORY_FILE" ]]; then
        local history_matches=$(grep "^[^|]*|[^|]*|$partial" "$HISTORY_FILE" | cut -d'|' -f3 | sort -u | head -5)
        
        if [[ -n "$history_matches" ]]; then
            echo ""
            echo "From history:"
            echo "$history_matches" | while read -r cmd; do
                echo "• $cmd"
            done
        fi
    fi
}

# Interactive input with suggestions
interactive_input() {
    local prompt="${1:-uDOS ❯ }"
    local suggestions="${2:-true}"
    
    while true; do
        echo -ne "$prompt"
        read -r input
        
        # Add to history
        [[ -n "$input" ]] && add_to_history "$input"
        
        # Handle special commands
        case "$input" in
            "help"|"?")
                "$UDOS_ROOT/uSCRIPT/library/ucode/help.sh"
                ;;
            "history")
                show_command_history
                ;;
            "suggest"*)
                local term=$(echo "$input" | cut -d' ' -f2-)
                get_smart_suggestions "$term"
                ;;
            "exit"|"quit")
                break
                ;;
            "")
                # Empty input, just continue
                ;;
            *)
                # Validate and execute command
                if validate_input "$input"; then
                    # This would route to the main command processor
                    echo "Executing: $input"
                fi
                ;;
        esac
    done
}

# Format different types of text
format_command() { echo -e "${CYAN}$1${NC}"; }
format_shortcode() { echo -e "${YELLOW}[$1]${NC}"; }
format_variable() { echo -e "${GREEN}\$$1${NC}"; }
format_path() { echo -e "${BLUE}$1${NC}"; }
format_text() { echo -e "${NC}$1${NC}"; }

# Show input statistics
show_input_stats() {
    echo -e "${BLUE}📊 Input Statistics${NC}"
    echo ""
    
    if [[ -f "$HISTORY_FILE" ]]; then
        local total_commands=$(wc -l < "$HISTORY_FILE")
        local unique_commands=$(cut -d'|' -f3 "$HISTORY_FILE" | sort -u | wc -l)
        local today_commands=$(grep "$(date '+%Y-%m-%d')" "$HISTORY_FILE" | wc -l)
        
        echo "Total commands: $total_commands"
        echo "Unique commands: $unique_commands"
        echo "Today's commands: $today_commands"
        
        echo ""
        echo "Most used commands:"
        cut -d'|' -f3 "$HISTORY_FILE" | awk '{print $1}' | sort | uniq -c | sort -nr | head -5 | while read -r count cmd; do
            echo "  $cmd: $count times"
        done
    else
        echo "No command history available"
    fi
}

# Main input function
input_main() {
    local action="${1:-interactive}"
    local param="${2:-}"
    
    case "$action" in
        "interactive")
            interactive_input
            ;;
        "history")
            show_command_history "$param"
            ;;
        "search")
            search_command_history "$param"
            ;;
        "suggest")
            get_smart_suggestions "$param"
            ;;
        "validate")
            validate_input "$param" "${3:-command}"
            ;;
        "complete")
            show_completions "$param"
            ;;
        "stats")
            show_input_stats
            ;;
        "add")
            add_to_history "$param"
            echo -e "${GREEN}✅ Added to history${NC}"
            ;;
        *)
            echo "Input module - Available actions: interactive, history [count], search <term>, suggest [term], validate <input>, complete <partial>, stats, add <command>"
            ;;
    esac
}

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    input_main "$@"
fi
