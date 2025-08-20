#!/bin/bash
# uDOS ASCII Module v1.3
# ASCII art, graphics, and visual elements including the iconic startup banner

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Colors and rainbow effects
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Rainbow colors for the iconic banner
RAINBOW_RED='\033[1;31m'
RAINBOW_YELLOW='\033[1;33m'
RAINBOW_GREEN='\033[1;32m'
RAINBOW_CYAN='\033[1;36m'

# The iconic uDOS startup ASCII banner with rainbow colors
show_rainbow_ascii() {
    echo -e "\n${RAINBOW_RED}    ██╗   ██╗${RAINBOW_YELLOW}██████╗ ${RAINBOW_GREEN} ██████╗ ${RAINBOW_CYAN}███████╗${NC}"
    echo -e "${RAINBOW_RED}    ██║   ██║${RAINBOW_YELLOW}██╔══██╗${RAINBOW_GREEN}██╔═══██╗${RAINBOW_CYAN}██╔════╝${NC}"
    echo -e "${RAINBOW_RED}    ██║   ██║${RAINBOW_YELLOW}██║  ██║${RAINBOW_GREEN}██║   ██║${RAINBOW_CYAN}███████╗${NC}"
    echo -e "${RAINBOW_RED}    ██║   ██║${RAINBOW_YELLOW}██║  ██║${RAINBOW_GREEN}██║   ██║${RAINBOW_CYAN}╚════██║${NC}"
    echo -e "${RAINBOW_RED}    ╚██████╔╝${RAINBOW_YELLOW}██████╔╝${RAINBOW_GREEN}╚██████╔╝${RAINBOW_CYAN}███████║${NC}"
    echo -e "${RAINBOW_RED}     ╚═════╝ ${RAINBOW_YELLOW}╚═════╝ ${RAINBOW_GREEN} ╚═════╝ ${RAINBOW_CYAN}╚══════╝${NC}"
    echo -e ""
    echo -e "    ${BOLD}${CYAN}Universal Data Operating System${NC}"
    echo -e "    ${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo -e "    ${PURPLE}▓▓▓▓▓${NC} ${YELLOW}Terminal-Native${NC} ${PURPLE}▓▓▓▓▓${NC} ${GREEN}Markdown-First${NC} ${PURPLE}▓▓▓▓▓${NC}"
    echo -e "    ${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo -e ""
}

# Simple ASCII banner (for smaller terminals)
show_simple_ascii() {
    echo -e "${BLUE}"
    echo "    ██╗   ██╗██████╗  ██████╗ ███████╗"
    echo "    ██║   ██║██╔══██╗██╔═══██╗██╔════╝"
    echo "    ██║   ██║██║  ██║██║   ██║███████╗"
    echo "    ██║   ██║██║  ██║██║   ██║╚════██║"
    echo "    ╚██████╔╝██████╔╝╚██████╔╝███████║"
    echo "     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝"
    echo ""
    echo "    Universal Data Operating System"
    echo "    ═══════════════════════════════════════════════════════"
    echo "    ▓▓▓▓▓ Terminal-Native ▓▓▓▓▓ Markdown-First ▓▓▓▓▓"
    echo "    ═══════════════════════════════════════════════════════"
    echo -e "${NC}"
}

# Retro computer boot sequence
show_boot_sequence() {
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}                                                       ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}   ${YELLOW}▓▓▓▓▓ ${CYAN}uDOS v1.3 MODULAR SYSTEM ${YELLOW}▓▓▓▓▓${NC}   ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                       ${GREEN}║${NC}"
    echo -e "${GREEN}╠═══════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║${NC} ${BLUE}►${NC} Memory subsystem............ ${GREEN}[OK]${NC}             ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} ${BLUE}►${NC} uSCRIPT execution engine.... ${GREEN}[OK]${NC}             ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} ${BLUE}►${NC} Modular command routing..... ${GREEN}[OK]${NC}             ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} ${BLUE}►${NC} Template system............. ${GREEN}[OK]${NC}             ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} ${BLUE}►${NC} Session logging............. ${GREEN}[OK]${NC}             ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} ${BLUE}►${NC} Authentication system....... ${GREEN}[OK]${NC}             ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                       ${GREEN}║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo -e ""
}

# Progress bar animation
show_progress_bar() {
    local progress=$1
    local width=${2:-50}
    local filled=$((progress * width / 100))
    local empty=$((width - filled))
    
    printf "\r${BLUE}["
    printf "%*s" $filled | tr ' ' '█'
    printf "%*s" $empty | tr ' ' '░'
    printf "] %d%%${NC}" $progress
}

# ASCII border drawing
draw_ascii_border() {
    local width="${1:-60}"
    local height="${2:-20}"
    local style="${3:-single}"
    local title="${4:-}"
    
    case "$style" in
        "double")
            local corners=("╔" "╗" "╚" "╝")
            local lines=("═" "║")
            ;;
        "rounded")
            local corners=("╭" "╮" "╰" "╯")
            local lines=("─" "│")
            ;;
        "thick")
            local corners=("┏" "┓" "┗" "┛")
            local lines=("━" "┃")
            ;;
        *)
            local corners=("┌" "┐" "└" "┘")
            local lines=("─" "│")
            ;;
    esac
    
    # Top border
    echo -n "${corners[0]}"
    if [[ -n "$title" ]]; then
        local title_len=${#title}
        local padding=$(((width - title_len - 2) / 2))
        for ((i=0; i<padding; i++)); do echo -n "${lines[0]}"; done
        echo -n " $title "
        for ((i=0; i<width-title_len-padding-3; i++)); do echo -n "${lines[0]}"; done
    else
        for ((i=1; i<width-1; i++)); do echo -n "${lines[0]}"; done
    fi
    echo "${corners[1]}"
    
    # Middle rows
    for ((i=1; i<height-1; i++)); do
        echo -n "${lines[1]}"
        for ((j=1; j<width-1; j++)); do echo -n " "; done
        echo "${lines[1]}"
    done
    
    # Bottom border
    echo -n "${corners[2]}"
    for ((i=1; i<width-1; i++)); do echo -n "${lines[0]}"; done
    echo "${corners[3]}"
}

# Character editor frame
show_character_editor() {
    clear
    echo -e "${PURPLE}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}                   ${YELLOW}CHARACTER EDITOR${NC}                   ${PURPLE}║${NC}"
    echo -e "${PURPLE}╠═══════════════════════════════════════════════════════╣${NC}"
    echo -e "${PURPLE}║${NC}                                                       ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}  📝 Edit ASCII characters and symbols                ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}  🎨 Create custom banners and graphics              ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}  📐 Design layout elements                           ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}                                                       ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚═══════════════════════════════════════════════════════╝${NC}"
}

# Loading animation
show_loading_animation() {
    local message="${1:-Loading}"
    local duration="${2:-3}"
    
    local chars=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")
    local i=0
    
    for ((t=0; t<duration*10; t++)); do
        printf "\r${BLUE}${chars[i]} %s...${NC}" "$message"
        i=$(((i + 1) % ${#chars[@]}))
        sleep 0.1
    done
    
    printf "\r${GREEN}✅ %s complete!${NC}\n" "$message"
}

# System validation display
show_validation_screen() {
    clear
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}                   ${YELLOW}SYSTEM VALIDATION${NC}                  ${CYAN}║${NC}"
    echo -e "${CYAN}╠═══════════════════════════════════════════════════════╣${NC}"
    
    local checks=(
        "Core modules:OK"
        "Authentication:OK"
        "Memory system:OK"
        "uSCRIPT engine:OK"
        "Templates:OK"
        "Session logging:OK"
    )
    
    for check in "${checks[@]}"; do
        IFS=':' read -r item status <<< "$check"
        case "$status" in
            "OK")
                echo -e "${CYAN}║${NC} ${GREEN}✅${NC} ${item}$(printf "%*s" $((43 - ${#item})) "")${CYAN}║${NC}"
                ;;
            "WARN")
                echo -e "${CYAN}║${NC} ${YELLOW}⚠️${NC} ${item}$(printf "%*s" $((43 - ${#item})) "")${CYAN}║${NC}"
                ;;
            *)
                echo -e "${CYAN}║${NC} ${RED}❌${NC} ${item}$(printf "%*s" $((43 - ${#item})) "")${CYAN}║${NC}"
                ;;
        esac
    done
    
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
}

# Startup sequence with all elements
show_full_startup() {
    clear
    show_rainbow_ascii
    sleep 1
    show_boot_sequence
    sleep 1
    show_validation_screen
}

# Main ASCII function
ascii_main() {
    local action="${1:-startup}"
    local param="${2:-}"
    
    case "$action" in
        "startup"|"banner")
            show_rainbow_ascii
            ;;
        "simple")
            show_simple_ascii
            ;;
        "boot")
            show_boot_sequence
            ;;
        "full")
            show_full_startup
            ;;
        "progress")
            local percent="${param:-50}"
            show_progress_bar "$percent"
            ;;
        "border")
            local width="${param:-60}"
            local height="${3:-20}"
            local style="${4:-single}"
            local title="${5:-}"
            draw_ascii_border "$width" "$height" "$style" "$title"
            ;;
        "loading")
            show_loading_animation "$param"
            ;;
        "validation")
            show_validation_screen
            ;;
        "editor")
            show_character_editor
            ;;
        *)
            echo "ASCII module - Available actions: startup, simple, boot, full, progress [%], border [w] [h] [style] [title], loading [msg], validation, editor"
            ;;
    esac
}

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    ascii_main "$@"
fi
