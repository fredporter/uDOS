#!/bin/bash
# uDOS Layout Module v1.3
# Advanced layout management, panels, and terminal optimization

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
UCORE="$UDOS_ROOT/uCORE"
UMEMORY="$UDOS_ROOT/uMEMORY"

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Layout presets
declare_layout_presets() {
    # Terminal size presets for different use cases
    LAYOUT_PRESETS=(
        "compact:80x24:Minimal efficiency mode"
        "standard:120x30:Balanced workspace"
        "wide:140x35:Spacious development"
        "tall:120x50:Code-focused layout"
        "dashboard:160x40:Data visualization"
        "ultra:200x50:Maximum real estate"
    )
}

# Panel drawing functions
draw_panel_border() {
    local width=$1
    local height=$2
    local style="${3:-single}"
    
    case "$style" in
        "double")
            local top_left="╔" top_right="╗" bottom_left="╚" bottom_right="╝"
            local horizontal="═" vertical="║"
            ;;
        "rounded")
            local top_left="╭" top_right="╮" bottom_left="╰" bottom_right="╯"
            local horizontal="─" vertical="│"
            ;;
        *)
            local top_left="┌" top_right="┐" bottom_left="└" bottom_right="┘"
            local horizontal="─" vertical="│"
            ;;
    esac
    
    # Top border
    echo -n "$top_left"
    for ((i=1; i<width-1; i++)); do echo -n "$horizontal"; done
    echo "$top_right"
    
    # Side borders
    for ((i=1; i<height-1; i++)); do
        echo -n "$vertical"
        for ((j=1; j<width-1; j++)); do echo -n " "; done
        echo "$vertical"
    done
    
    # Bottom border
    echo -n "$bottom_left"
    for ((i=1; i<width-1; i++)); do echo -n "$horizontal"; done
    echo "$bottom_right"
}

# Format content for panels
format_panel_content() {
    local content="$1"
    local width="$2"
    local padding="${3:-2}"
    
    local max_width=$((width - padding * 2))
    
    echo "$content" | fold -s -w "$max_width" | while read -r line; do
        local spaces=$((max_width - ${#line}))
        printf "%*s%s%*s\n" $padding "" "$line" $spaces ""
    done
}

# Panel positioning
position_panel() {
    local x=$1
    local y=$2
    local content="$3"
    
    printf "\033[%d;%dH%s" "$y" "$x" "$content"
}

# Layout configuration management
load_layout_config() {
    local config_file="$UCORE/config/layout.conf"
    [[ -f "$config_file" ]] && source "$config_file"
}

save_layout_config() {
    local config_file="$UCORE/config/layout.conf"
    mkdir -p "$(dirname "$config_file")"
    
    cat > "$config_file" << EOF
# uDOS Layout Configuration
TERMINAL_WIDTH=${TERMINAL_WIDTH:-120}
TERMINAL_HEIGHT=${TERMINAL_HEIGHT:-30}
PREFERRED_LAYOUT=${PREFERRED_LAYOUT:-standard}
PANEL_STYLE=${PANEL_STYLE:-single}
AUTO_OPTIMIZE=${AUTO_OPTIMIZE:-true}
EOF
}

# Detect optimal layout based on content
detect_optimal_layout() {
    local content_type="$1"
    local cols=$(tput cols 2>/dev/null || echo 80)
    local lines=$(tput lines 2>/dev/null || echo 24)
    
    case "$content_type" in
        "code"|"dev")
            if [[ $cols -ge 140 ]]; then
                echo "wide"
            elif [[ $lines -ge 40 ]]; then
                echo "tall"
            else
                echo "standard"
            fi
            ;;
        "data"|"dashboard")
            [[ $cols -ge 160 ]] && echo "dashboard" || echo "wide"
            ;;
        "minimal"|"focus")
            echo "compact"
            ;;
        *)
            echo "standard"
            ;;
    esac
}

# Apply layout settings
apply_layout() {
    local layout_name="$1"
    declare_layout_presets
    
    for preset in "${LAYOUT_PRESETS[@]}"; do
        IFS=':' read -r name size desc <<< "$preset"
        if [[ "$name" == "$layout_name" ]]; then
            IFS='x' read -r width height <<< "$size"
            echo -e "${BLUE}📐 Applying $name layout: ${size}${NC}"
            echo -e "   $desc"
            
            # Set terminal size if possible
            if command -v resize >/dev/null 2>&1; then
                resize -s "$height" "$width" 2>/dev/null
            fi
            
            # Save preference
            export TERMINAL_WIDTH="$width"
            export TERMINAL_HEIGHT="$height"
            export PREFERRED_LAYOUT="$layout_name"
            save_layout_config
            
            return 0
        fi
    done
    
    echo -e "${RED}❌ Unknown layout: $layout_name${NC}"
    return 1
}

# Show layout manager
show_layout_manager() {
    clear
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    LAYOUT MANAGER                    ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${BLUE}📐 Current Terminal: $(tput cols)x$(tput lines)${NC}"
    echo ""
    
    echo -e "${BLUE}Available Layouts:${NC}"
    declare_layout_presets
    
    local i=1
    for preset in "${LAYOUT_PRESETS[@]}"; do
        IFS=':' read -r name size desc <<< "$preset"
        echo -e "  [$i] ${YELLOW}$name${NC} ($size) - $desc"
        ((i++))
    done
    
    echo ""
    echo -e "${YELLOW}Enter layout number or name:${NC} "
    read -r choice
    
    if [[ "$choice" =~ ^[0-9]+$ ]]; then
        local preset_index=$((choice - 1))
        if [[ $preset_index -ge 0 && $preset_index -lt ${#LAYOUT_PRESETS[@]} ]]; then
            IFS=':' read -r name size desc <<< "${LAYOUT_PRESETS[$preset_index]}"
            apply_layout "$name"
        else
            echo -e "${RED}Invalid selection${NC}"
        fi
    else
        apply_layout "$choice"
    fi
}

# Panel generation functions
generate_memory_panel() {
    local width="${1:-60}"
    local height="${2:-15}"
    
    echo -e "${BLUE}╔══ MEMORY SYSTEM ══╗${NC}"
    
    # Memory usage
    local memory_usage=$(find "$UMEMORY" -type f | wc -l)
    local storage_size=$(du -sh "$UMEMORY" 2>/dev/null | cut -f1)
    
    echo "📊 Files: $memory_usage"
    echo "💾 Size: $storage_size"
    echo "📝 Sessions: $(find "$UMEMORY" -name "*Session.md" | wc -l)"
    echo "📋 Templates: $(find "$UMEMORY/templates" -name "*.md" 2>/dev/null | wc -l)"
}

generate_status_panel() {
    local width="${1:-60}"
    local height="${2:-10}"
    
    echo -e "${GREEN}╔══ SYSTEM STATUS ══╗${NC}"
    
    # System info
    echo "🕐 $(date '+%H:%M:%S')"
    echo "📊 Load: $(uptime | awk -F'load average:' '{print $2}' | xargs)"
    echo "💿 Disk: $(df "$UDOS_ROOT" | tail -1 | awk '{print $5}')"
    echo "🔧 Modules: $(find "$UDOS_ROOT/uSCRIPT/library/ucode" -name "*.sh" | wc -l)"
}

# Create panel grid system
create_panel_grid() {
    local cols="$1"
    local rows="$2"
    
    clear
    
    local term_width=$(tput cols)
    local term_height=$(tput lines)
    local panel_width=$((term_width / cols))
    local panel_height=$((term_height / rows))
    
    for ((row=0; row<rows; row++)); do
        for ((col=0; col<cols; col++)); do
            local x=$((col * panel_width + 1))
            local y=$((row * panel_height + 1))
            
            # Draw panel based on position
            case "$row-$col" in
                "0-0") generate_status_panel "$panel_width" "$panel_height" ;;
                "0-1") generate_memory_panel "$panel_width" "$panel_height" ;;
                *) echo "Panel $row-$col" ;;
            esac
        done
    done
}

# Main layout function
layout_main() {
    local action="${1:-manager}"
    local param="${2:-}"
    
    case "$action" in
        "manager"|"menu")
            show_layout_manager
            ;;
        "apply")
            apply_layout "$param"
            ;;
        "detect")
            local optimal=$(detect_optimal_layout "$param")
            echo "Optimal layout for '$param': $optimal"
            apply_layout "$optimal"
            ;;
        "grid")
            local cols="${param:-2}"
            local rows="${3:-2}"
            create_panel_grid "$cols" "$rows"
            ;;
        "save")
            save_layout_config
            echo -e "${GREEN}✅ Layout configuration saved${NC}"
            ;;
        "presets")
            declare_layout_presets
            echo -e "${BLUE}📐 Available Layout Presets:${NC}"
            for preset in "${LAYOUT_PRESETS[@]}"; do
                IFS=':' read -r name size desc <<< "$preset"
                echo -e "  • ${YELLOW}$name${NC} ($size) - $desc"
            done
            ;;
        *)
            echo "Layout module - Available actions: manager, apply <name>, detect <type>, grid [cols] [rows], save, presets"
            ;;
    esac
}

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    layout_main "$@"
fi
