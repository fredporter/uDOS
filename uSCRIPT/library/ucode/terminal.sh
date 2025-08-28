#!/bin/bash
# uDOS Terminal Management Module v1.3
# Advanced terminal size detection, optimization, and preset management

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Global terminal size variables
CURRENT_COLS=80
CURRENT_ROWS=24

# Terminal size presets
get_size_preset() {
    local preset="$1"
    case "$preset" in
        compact) echo "80x24" ;;
        standard) echo "120x30" ;;
        wide) echo "140x35" ;;
        ultra-wide) echo "160x40" ;;
        coding) echo "120x50" ;;
        dashboard) echo "140x45" ;;
        writing) echo "100x35" ;;
        *) echo "" ;;
    esac
}

# Preset descriptions
get_preset_description() {
    local preset="$1"
    case "$preset" in
        compact) echo "80x24 (minimal)" ;;
        standard) echo "120x30 (recommended)" ;;
        wide) echo "140x35 (comfortable)" ;;
        ultra-wide) echo "160x40 (spacious)" ;;
        coding) echo "120x50 (tall for code)" ;;
        dashboard) echo "140x45 (data viewing)" ;;
        writing) echo "100x35 (narrow for readability)" ;;
        *) echo "Unknown preset" ;;
    esac
}

# Log functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Detect current terminal dimensions
detect_terminal_size() {
    # Try tput first (most reliable)
    if command -v tput >/dev/null 2>&1; then
        CURRENT_COLS=$(tput cols 2>/dev/null || echo "80")
        CURRENT_ROWS=$(tput lines 2>/dev/null || echo "24")
    else
        # Fallback using stty
        local size_info=$(stty size 2>/dev/null || echo "24 80")
        CURRENT_ROWS=$(echo "$size_info" | cut -d' ' -f1 || echo "24")
        CURRENT_COLS=$(echo "$size_info" | cut -d' ' -f2 || echo "80")
    fi
    
    # Ensure we have valid numbers
    [[ "$CURRENT_COLS" =~ ^[0-9]+$ ]] || CURRENT_COLS=80
    [[ "$CURRENT_ROWS" =~ ^[0-9]+$ ]] || CURRENT_ROWS=24
}

# Set terminal window size using ANSI escape sequences
set_terminal_size() {
    local cols=${1:-120}
    local rows=${2:-30}
    
    log_info "Setting terminal size to ${cols}x${rows}..."
    
    # ANSI escape sequence to resize terminal (works on most terminals)
    printf '\e[8;%d;%dt' "$rows" "$cols"
    
    # Additional positioning (center on screen)
    printf '\e[3;100;100t'
    
    # For macOS Terminal.app specifically
    if [[ "$OSTYPE" == "darwin"* ]] && [[ "$TERM_PROGRAM" == "Apple_Terminal" ]]; then
        local width=$((cols * 8 + 50))
        local height=$((rows * 20 + 50))
        osascript -e "tell application \"Terminal\" to set bounds of front window to {100, 100, $width, $height}" 2>/dev/null || true
    fi
    
    # Update our tracking variables
    CURRENT_COLS=$cols
    CURRENT_ROWS=$rows
    
    # Brief pause to allow terminal to resize
    sleep 0.2
    
    # Verify the resize worked
    detect_terminal_size
    if [[ "$CURRENT_COLS" -eq "$cols" && "$CURRENT_ROWS" -eq "$rows" ]]; then
        log_success "Terminal resized successfully"
    else
        log_warning "Terminal resize may not have worked completely"
        log_info "Requested: ${cols}x${rows}, Actual: ${CURRENT_COLS}x${CURRENT_ROWS}"
    fi
}

# Apply a size preset
apply_size_preset() {
    local preset="$1"
    
    local size=$(get_size_preset "$preset")
    if [[ -z "$size" ]]; then
        log_error "Unknown preset: $preset"
        show_available_presets
        return 1
    fi
    
    local cols=$(echo "$size" | cut -d'x' -f1)
    local rows=$(echo "$size" | cut -d'x' -f2)
    local description=$(get_preset_description "$preset")
    
    log_info "Applying preset: $preset ($description)"
    set_terminal_size "$cols" "$rows"
}

# Show available presets
show_available_presets() {
    echo -e "\n${BOLD}🖥️  Available Terminal Presets:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local presets=("compact" "standard" "wide" "ultra-wide" "coding" "dashboard" "writing")
    for preset in "${presets[@]}"; do
        local description=$(get_preset_description "$preset")
        echo -e "  ${CYAN}$preset${NC} - $description"
    done
    echo ""
}

# Terminal size recommendation engine
recommend_terminal_size() {
    detect_terminal_size
    
    log_info "Current terminal: ${CURRENT_COLS}x${CURRENT_ROWS}"
    
    # Determine best recommendation based on current size
    local recommended="standard"
    local recommended_desc="120x30 (recommended)"
    
    if (( CURRENT_COLS >= 160 )); then
        recommended="ultra-wide"
        recommended_desc="160x40 (spacious)"
    elif (( CURRENT_COLS >= 140 )); then
        recommended="wide" 
        recommended_desc="140x35 (comfortable)"
    elif (( CURRENT_COLS >= 120 )); then
        recommended="standard"
        recommended_desc="120x30 (recommended)"
    else
        recommended="compact"
        recommended_desc="80x24 (minimal)"
    fi
    
    echo -e "\n${YELLOW}🖥️  Terminal Size Optimizer${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}Current size:${NC} ${CURRENT_COLS}x${CURRENT_ROWS}"
    echo -e "${GREEN}Recommended:${NC} $recommended_desc"
    echo ""
    show_available_presets
    echo -e "Options:"
    echo -e "  ${CYAN}c${NC} - Keep current size"
    echo -e "  ${CYAN}Enter${NC} - Use recommended ($recommended)"
    echo ""
    
    read -p "Select preset [preset name/c/Enter]: " choice
    
    case "$choice" in
        compact|standard|wide|ultra-wide|coding|dashboard|writing)
            apply_size_preset "$choice"
            ;;
        c|C) 
            log_info "Keeping current size: ${CURRENT_COLS}x${CURRENT_ROWS}" 
            ;;
        "") 
            apply_size_preset "$recommended" 
            ;;
        *) 
            if [[ -n "$choice" ]]; then
                log_warning "Unknown preset: $choice"
                show_available_presets
            else
                apply_size_preset "$recommended"
            fi
            ;;
    esac
}

# Auto-optimize terminal for content type
optimize_for_content() {
    local content_type="${1:-general}"
    
    case "$content_type" in
        code|coding|development)
            apply_size_preset "coding"
            log_info "Optimized for code editing (tall terminal)"
            ;;
        data|dashboard|analytics)
            apply_size_preset "dashboard"
            log_info "Optimized for data viewing (wide terminal)"
            ;;
        writing|markdown|docs)
            apply_size_preset "writing"
            log_info "Optimized for writing (narrow for readability)"
            ;;
        wide|presentation)
            apply_size_preset "ultra-wide"
            log_info "Optimized for presentations (maximum width)"
            ;;
        compact|minimal)
            apply_size_preset "compact"
            log_info "Optimized for minimal space usage"
            ;;
        *)
            apply_size_preset "standard"
            log_info "Using standard size for general use"
            ;;
    esac
}

# Show current terminal information
show_terminal_info() {
    detect_terminal_size
    
    echo -e "\n${YELLOW}🖥️  Terminal Information${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}Dimensions:${NC} ${CURRENT_COLS} columns × ${CURRENT_ROWS} rows"
    echo -e "${BLUE}Terminal:${NC} ${TERM_PROGRAM:-Unknown}"
    echo -e "${BLUE}Term Type:${NC} ${TERM:-Unknown}"
    echo -e "${BLUE}OS:${NC} ${OSTYPE:-Unknown}"
    
    # Determine category
    local category="Unknown"
    if (( CURRENT_COLS >= 160 )); then
        category="Ultra-wide"
    elif (( CURRENT_COLS >= 140 )); then
        category="Wide"
    elif (( CURRENT_COLS >= 120 )); then
        category="Standard"
    elif (( CURRENT_COLS >= 100 )); then
        category="Medium"
    else
        category="Compact"
    fi
    
    echo -e "${BLUE}Category:${NC} $category"
    
    # Show aspect ratio for tall vs wide
    local aspect_ratio=$(echo "scale=2; $CURRENT_COLS / $CURRENT_ROWS" | bc 2>/dev/null || echo "unknown")
    if [[ "$aspect_ratio" != "unknown" ]]; then
        echo -e "${BLUE}Aspect Ratio:${NC} $aspect_ratio"
        if (( $(echo "$aspect_ratio < 3" | bc 2>/dev/null || echo 0) )); then
            echo -e "${BLUE}Layout Style:${NC} Tall (good for code)"
        else
            echo -e "${BLUE}Layout Style:${NC} Wide (good for data)"
        fi
    fi
    
    echo ""
}

# Help function
show_terminal_help() {
    echo -e "\n${YELLOW}🖥️  Terminal Management Help${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BOLD}Usage:${NC}"
    echo "  terminal detect                 - Show current terminal size"
    echo "  terminal info                   - Show detailed terminal information"
    echo "  terminal recommend              - Get size recommendations"
    echo "  terminal set <cols> <rows>      - Set specific dimensions"
    echo "  terminal preset <name>          - Apply a preset size"
    echo "  terminal optimize <type>        - Auto-optimize for content type"
    echo "  terminal presets                - List available presets"
    echo ""
    echo -e "${BOLD}Presets:${NC}"
    show_available_presets
    echo -e "${BOLD}Content Types:${NC}"
    echo -e "  ${CYAN}code${NC} - Tall terminal for coding"
    echo -e "  ${CYAN}data${NC} - Wide terminal for data viewing"
    echo -e "  ${CYAN}writing${NC} - Narrow terminal for readability"
    echo -e "  ${CYAN}wide${NC} - Maximum width for presentations"
    echo -e "  ${CYAN}compact${NC} - Minimal space usage"
    echo ""
    echo -e "${BOLD}Examples:${NC}"
    echo "  terminal preset standard"
    echo "  terminal set 120 30"
    echo "  terminal optimize code"
    echo ""
}

# Main function dispatcher
main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        detect)
            detect_terminal_size
            echo "Terminal size: ${CURRENT_COLS}x${CURRENT_ROWS}"
            ;;
        info)
            show_terminal_info
            ;;
        recommend)
            recommend_terminal_size
            ;;
        set)
            local cols="$1"
            local rows="$2"
            if [[ -n "$cols" && -n "$rows" ]]; then
                set_terminal_size "$cols" "$rows"
            else
                log_error "Usage: terminal set <columns> <rows>"
                echo "Example: terminal set 120 30"
            fi
            ;;
        preset)
            local preset="$1"
            if [[ -n "$preset" ]]; then
                apply_size_preset "$preset"
            else
                log_error "Usage: terminal preset <preset_name>"
                show_available_presets
            fi
            ;;
        presets)
            show_available_presets
            ;;
        optimize)
            local content_type="$1"
            optimize_for_content "$content_type"
            ;;
        help|--help|-h)
            show_terminal_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_terminal_help
            ;;
    esac
}

# If script is executed directly, run main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
