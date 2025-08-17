#!/bin/bash
# uDOS v1.3 - Modular Command System
# Core shell and system commands only
# Complex functionality moved to uSCRIPT/library/ucode/

# Core configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UMEMORY="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/uMEMORY"
USCRIPT_PATH="${UHOME}/../uSCRIPT"
DATASETS_PATH="${UHOME}/datasets"

# Version
VERSION="v1.3"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_header() { echo -e "\n${BOLD}${CYAN}🌀 $1${NC}\n"; }

# uCode Script Executor
execute_ucode_script() {
    local script_name="$1"
    local args="$2"
    local script_path="$USCRIPT_PATH/library/ucode/${script_name}.ucode"
    
    if [[ -f "$script_path" ]]; then
        log_info "Executing uCode script: $script_name"
        # For now, simulate execution - actual uCode interpreter would go here
        echo "🔧 uCode Script: $script_name"
        echo "📄 Path: $script_path"
        echo "📝 Args: $args"
        echo "⚠️  uCode interpreter not yet implemented - this is a simulation"
        return 0
    else
        log_error "uCode script not found: $script_path"
        return 1
    fi
}

# Shortcode processor using dataset
process_shortcode() {
    local shortcode="$1"
    local clean_code="${shortcode//[\[\]]/}"  # Remove brackets
    
    # Parse shortcode components
    IFS='|' read -ra PARTS <<< "$clean_code"
    local command="${PARTS[0]}"
    local action="${PARTS[1]:-}"
    local argument="${PARTS[2]:-}"
    
    log_info "Processing shortcode: $command|$action|$argument"
    
    # Route to appropriate uCode script based on command
    case "$command" in
        DASH|dash)
            execute_ucode_script "DASH" "$action $argument"
            ;;
        PANEL|panel)
            execute_ucode_script "PANEL" "$action $argument"
            ;;
        TREE|tree)
            execute_ucode_script "TREE" "$action $argument"
            ;;
        MEM|MEMORY|mem|memory)
            execute_ucode_script "MEMORY" "$action $argument"
            ;;
        MISSION|mission)
            execute_ucode_script "MISSION" "$action $argument"
            ;;
        PACK|PACKAGE|pack|package)
            execute_ucode_script "PACKAGE" "$action $argument"
            ;;
        LOG|log)
            execute_ucode_script "LOG" "$action $argument"
            ;;
        DEV|dev)
            execute_ucode_script "DEV" "$action $argument"
            ;;
        RENDER|render)
            execute_ucode_script "RENDER" "$action $argument"
            ;;
        *)
            log_error "Unknown shortcode command: $command"
            echo "Available commands: DASH, PANEL, TREE, MEM, MISSION, PACK, LOG, DEV, RENDER"
            return 1
            ;;
    esac
}

# Core system commands only
show_status() {
    log_header "uDOS $VERSION System Status"
    
    echo -e "${BOLD}📊 Core System${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}Version:${NC}          $VERSION"
    echo -e "${CYAN}Architecture:${NC}     Multi-Installation (6 roles)"
    echo -e "${CYAN}Core Path:${NC}        $UHOME"
    echo -e "${CYAN}Memory Path:${NC}      $UMEMORY"
    echo -e "${CYAN}uScript Path:${NC}     $USCRIPT_PATH"
    
    # Check critical directories
    echo ""
    echo -e "${BOLD}📁 Directory Status${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    for dir in "$UHOME" "$UMEMORY" "$USCRIPT_PATH" "$DATASETS_PATH"; do
        if [[ -d "$dir" ]]; then
            echo -e "${GREEN}✅${NC} $(basename "$dir")"
        else
            echo -e "${RED}❌${NC} $(basename "$dir") (missing)"
        fi
    done
    
    # Check uCode scripts
    echo ""
    echo -e "${BOLD}🔧 uCode Scripts${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    local ucode_dir="$USCRIPT_PATH/library/ucode"
    if [[ -d "$ucode_dir" ]]; then
        local script_count=$(find "$ucode_dir" -name "*.ucode" | wc -l | tr -d ' ')
        echo -e "${GREEN}✅${NC} $script_count uCode scripts available"
        find "$ucode_dir" -name "*.ucode" | while read script; do
            echo -e "   • $(basename "$script" .ucode)"
        done
    else
        echo -e "${RED}❌${NC} uCode library not found"
    fi
    
    echo ""
}

show_help() {
    log_header "uDOS $VERSION Core Commands"
    
    echo -e "${BOLD}🌀 System Commands${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "  ${YELLOW}STATUS${NC}     - Show system status and health"
    echo -e "  ${YELLOW}HELP${NC}       - Show this help"
    echo -e "  ${YELLOW}EXIT${NC}       - Exit uDOS (aliases: QUIT, BYE)"
    echo -e "  ${YELLOW}RESTART${NC}    - Restart uDOS session"
    echo -e "  ${YELLOW}RESIZE${NC}     - Terminal size optimizer"
    echo ""
    
    echo -e "${BOLD}🔧 Shortcode Commands (Processed by uCode scripts)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "  ${CYAN}[DASH|LIVE]${NC}         - Live dashboard"
    echo -e "  ${CYAN}[PANEL|DASH]${NC}        - Panel dashboard"
    echo -e "  ${CYAN}[TREE|GENERATE]${NC}     - Generate repository structure"
    echo -e "  ${CYAN}[MEM|LIST]${NC}          - List memory files"
    echo -e "  ${CYAN}[MISSION|CREATE]${NC}    - Create new mission"
    echo -e "  ${CYAN}[PACK|LIST]${NC}         - List packages"
    echo -e "  ${CYAN}[LOG|REPORT]${NC}        - Generate log report"
    echo -e "  ${CYAN}[DEV|TEST]${NC}          - Development tools (wizard only)"
    echo -e "  ${CYAN}[RENDER|ART]${NC}        - Visual rendering and ASCII art"
    echo ""
    
    echo -e "${BOLD}💡 Architecture${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "  • ${GREEN}Core Shell${NC}        - Essential system commands (this file)"
    echo -e "  • ${GREEN}uCode Scripts${NC}     - Complex functionality in Visual Basic style"
    echo -e "  • ${GREEN}JSON Datasets${NC}     - Configuration data and shortcode definitions"
    echo -e "  • ${GREEN}Modular Design${NC}    - Clean separation of concerns"
    echo ""
}

# Terminal size management
detect_terminal_size() {
    if command -v tput >/dev/null 2>&1; then
        CURRENT_COLS=$(tput cols 2>/dev/null || echo "80")
        CURRENT_ROWS=$(tput lines 2>/dev/null || echo "24")
    else
        CURRENT_COLS=$(stty size 2>/dev/null | cut -d' ' -f2 || echo "80")
        CURRENT_ROWS=$(stty size 2>/dev/null | cut -d' ' -f1 || echo "24")
    fi
    
    [[ "$CURRENT_COLS" =~ ^[0-9]+$ ]] || CURRENT_COLS=80
    [[ "$CURRENT_ROWS" =~ ^[0-9]+$ ]] || CURRENT_ROWS=24
}

recommend_terminal_size() {
    detect_terminal_size
    
    log_info "Current terminal: ${CURRENT_COLS}x${CURRENT_ROWS}"
    
    echo -e "\n${YELLOW}🖥️  Terminal Size Optimizer${NC}"
    echo -e "${BLUE}Current size:${NC} ${CURRENT_COLS}x${CURRENT_ROWS}"
    echo -e "${GREEN}Recommended:${NC} 120x30 (standard)"
    echo -e ""
    echo -e "${BOLD}Available presets:${NC}"
    echo -e "  ${CYAN}1.${NC} Compact     - 80x24"
    echo -e "  ${CYAN}2.${NC} Standard    - 120x30 (recommended)"
    echo -e "  ${CYAN}3.${NC} Wide        - 140x35"
    echo -e "  ${CYAN}4.${NC} Coding      - 120x50 (tall for code)"
    echo -e "  ${CYAN}c.${NC} Keep current size"
    echo -e ""
}

# Simple startup sequence
show_startup() {
    echo -e "${CYAN}🌀 uDOS $VERSION - Modular Architecture${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  ${GREEN}✅ Core shell loaded${NC}"
    echo -e "  ${GREEN}✅ uCode integration ready${NC}"
    echo -e "  ${GREEN}✅ Modular architecture active${NC}"
    echo ""
}

# Initialize directories
init_directories() {
    local dirs=(
        "$UHOME"
        "$UMEMORY" 
        "$USCRIPT_PATH"
        "$DATASETS_PATH"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir" 2>/dev/null || true
    done
}

# Process user input
process_input() {
    local input="$1"
    
    # Handle shortcode format [COMMAND:args]
    if [[ "$input" =~ ^\[.*\]$ ]]; then
        process_shortcode "$input"
        return
    fi
    
    # Parse command and arguments
    local cmd=$(echo "$input" | awk '{print $1}')
    local args=""
    if [[ "$input" == *" "* ]]; then
        args=$(echo "$input" | cut -d' ' -f2-)
    fi
    
    case "$cmd" in
        HELP|help)
            show_help
            ;;
        STATUS|status)
            show_status
            ;;
        RESIZE|resize|SIZE|size)
            recommend_terminal_size
            ;;
        RESTART|restart|REBOOT|reboot|RELOAD|reload)
            log_info "Restarting uDOS session..."
            clear
            exec "$0" "$@"
            ;;
        RESET|reset|REFRESH|refresh)
            log_info "Refreshing uDOS interface..."
            clear
            show_startup
            ;;
        EXIT|exit|QUIT|quit|BYE|bye)
            log_success "Goodbye!"
            exit 0
            ;;
        # Route complex commands to uCode scripts
        DASH|dash)
            execute_ucode_script "DASH" "$args"
            ;;
        PANEL|panel)
            execute_ucode_script "PANEL" "$args"
            ;;
        TREE|tree)
            execute_ucode_script "TREE" "$args"
            ;;
        MEMORY|MEM|memory|mem)
            execute_ucode_script "MEMORY" "$args"
            ;;
        MISSION|mission)
            execute_ucode_script "MISSION" "$args"
            ;;
        PACKAGE|PACK|package|pack)
            execute_ucode_script "PACKAGE" "$args"
            ;;
        LOG|log)
            execute_ucode_script "LOG" "$args"
            ;;
        DEV|dev)
            execute_ucode_script "DEV" "$args"
            ;;
        RENDER|render)
            execute_ucode_script "RENDER" "$args"
            ;;
        *)
            log_error "Unknown command: $cmd"
            echo "Type 'HELP' for available commands"
            echo "Use [COMMAND|ACTION] for shortcode format"
            ;;
    esac
}

# Main function
main() {
    # Check if arguments provided (non-interactive mode)
    if [[ $# -gt 0 ]]; then
        init_directories
        process_input "$*"
        return
    fi
    
    # Interactive mode setup
    init_directories
    
    # Show startup
    show_startup
    
    # Interactive loop with better input handling
    while true; do
        echo -ne "${CYAN}🌀${NC} "
        
        # Check if we have a proper terminal
        if [[ ! -t 0 ]]; then
            echo -e "\n⚠️  No interactive terminal detected"
            echo "💡 Use: bash $0 [COMMAND] for non-interactive mode"
            break
        fi
        
        # Read input with timeout
        if ! read -r -t 30 input 2>/dev/null; then
            echo -e "\n⚠️  Input timeout"
            break
        fi
        
        [[ -z "$input" ]] && continue
        
        # Handle exit commands
        case "$input" in
            quit|exit|q)
                echo "✅ Goodbye!"
                break
                ;;
            *)
                process_input "$input"
                echo ""
                ;;
        esac
    done
}

# Execute main if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
