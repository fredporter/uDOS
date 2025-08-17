#!/bin/bash
# uDOS v1.2 - Unified Command System
# Minimal, efficient, flat-structure design

# More forgiving error handling for interactive mode
set -uo pipefail
# Only exit on errors in non-interactive functions

# Core configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UMEMORY="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/uMEMORY"
UTEMPLATE="${UHOME}/uTemplate"
UDEV="${UHOME}/wizard"

# Version
VERSION="v1.2"

# Editor mode system
CURRENT_MODE="COMMAND"  # COMMAND, MARKDOWN, USCRIPT, SHORTCODE
CURRENT_FILE=""
EDIT_BUFFER=""

# Advanced input intelligence system
COMMAND_HISTORY_FILE="$HOME/.udos_history"
FAVORITES_FILE="$HOME/.udos_favorites"
HISTORY_COUNT=0
MAX_HISTORY=100

# Responsive layout system
CURRENT_LAYOUT="auto"  # auto, compact, standard, wide, coding, writing, dashboard
LAYOUT_CONFIG_FILE="$HOME/.udos_layout"
AUTO_LAYOUT=true

# Layout definitions
declare_layout_presets() {
    # Compact layout (80x24)
    COMPACT_COLS=80
    COMPACT_ROWS=24
    
    # Standard layout (120x30)
    STANDARD_COLS=120
    STANDARD_ROWS=30
    
    # Wide layout (140x35)
    WIDE_COLS=140
    WIDE_ROWS=35
    
    # Coding layout (120x50) - tall for code
    CODING_COLS=120
    CODING_ROWS=50
    
    # Writing layout (100x35) - narrower for readability
    WRITING_COLS=100
    WRITING_ROWS=35
    
    # Dashboard layout (160x40) - wide for data
    DASHBOARD_COLS=160
    DASHBOARD_ROWS=40
}

# Panel Display System - ASCII Dashboard Framework
PANEL_WIDTH=60
PANEL_HEIGHT=20
PANEL_BORDER_STYLE="double"
PANEL_PADDING=1

# Panel grid system
GRID_COLS=3
GRID_ROWS=2
GRID_GAP=2

# Data constraints for minimal library
MAX_STRING_LENGTH=40
MAX_DISPLAY_LINES=15
MAX_PANEL_ITEMS=8

# Font and character system (Acorn-inspired, markdown-compatible)
FONT_STYLE="mono"
CHAR_SET="extended"

# Initialize shortcode templates
init_shortcode_templates() {
    # Create templates file if it doesn't exist
    mkdir -p "$(dirname "$COMMAND_HISTORY_FILE")"
    touch "$COMMAND_HISTORY_FILE"
    touch "$FAVORITES_FILE"
    
    # Load existing history count
    if [[ -f "$COMMAND_HISTORY_FILE" ]]; then
        HISTORY_COUNT=$(wc -l < "$COMMAND_HISTORY_FILE" 2>/dev/null || echo "0")
    fi
    
    # Initialize layout presets
    declare_layout_presets
    
    # Load saved layout preferences
    load_layout_config
}

# ASCII Panel Drawing Functions
draw_panel_border() {
    local width="$1"
    local height="$2"
    local style="${3:-single}"
    local title="$4"
    
    local top_left top_right bottom_left bottom_right horizontal vertical
    
    case "$style" in
        double)
            top_left="╔" top_right="╗" bottom_left="╚" bottom_right="╝"
            horizontal="═" vertical="║"
            ;;
        thick)
            top_left="┏" top_right="┓" bottom_left="┗" bottom_right="┛"
            horizontal="━" vertical="┃"
            ;;
        minimal)
            top_left="┌" top_right="┐" bottom_left="└" bottom_right="┘"
            horizontal="─" vertical="│"
            ;;
        *)  # single
            top_left="┌" top_right="┐" bottom_left="└" bottom_right="┘"
            horizontal="─" vertical="│"
            ;;
    esac
    
    # Top border with title
    local top_line="$top_left"
    if [[ -n "$title" ]]; then
        local title_len=${#title}
        local title_padding=$(( (width - title_len - 4) / 2 ))
        local remaining_padding=$(( width - title_len - title_padding - 4 ))
        
        top_line+="$(printf "%*s" $title_padding "" | tr ' ' "$horizontal")"
        top_line+="[ $title ]"
        top_line+="$(printf "%*s" $remaining_padding "" | tr ' ' "$horizontal")"
    else
        top_line+="$(printf "%*s" $((width - 2)) "" | tr ' ' "$horizontal")"
    fi
    top_line+="$top_right"
    
    echo "$top_line"
    
    # Side borders
    for ((i=1; i<height-1; i++)); do
        echo "$vertical$(printf "%*s" $((width - 2)) "")$vertical"
    done
    
    # Bottom border
    echo "$bottom_left$(printf "%*s" $((width - 2)) "" | tr ' ' "$horizontal")$bottom_right"
}

# Create data-constrained content
format_panel_content() {
    local content="$1"
    local max_width="$2"
    local max_lines="$3"
    
    # Truncate long strings
    content=$(echo "$content" | cut -c1-$MAX_STRING_LENGTH)
    
    # Word wrap for panel width
    local formatted=""
    while IFS= read -r line; do
        if [[ ${#line} -gt $max_width ]]; then
            # Split long lines
            local remaining="$line"
            while [[ ${#remaining} -gt $max_width ]]; do
                formatted+="$(echo "$remaining" | cut -c1-$max_width)\n"
                remaining="$(echo "$remaining" | cut -c$((max_width + 1))-)"
            done
            if [[ -n "$remaining" ]]; then
                formatted+="$remaining\n"
            fi
        else
            formatted+="$line\n"
        fi
    done <<< "$content"
    
    # Limit to max lines
    echo -e "$formatted" | head -n "$max_lines"
}

# Panel positioning system
position_panel() {
    local x="$1"
    local y="$2"
    local content="$3"
    
    # Move cursor to position and draw content
    local line_num=0
    while IFS= read -r line; do
        printf '\033[%d;%dH%s' $((y + line_num)) "$x" "$line"
        ((line_num++))
    done <<< "$content"
}

# Layout Management Functions
load_layout_config() {
    if [[ -f "$LAYOUT_CONFIG_FILE" ]]; then
        source "$LAYOUT_CONFIG_FILE" 2>/dev/null || true
    fi
}

save_layout_config() {
    cat > "$LAYOUT_CONFIG_FILE" << EOF
# uDOS Layout Configuration
CURRENT_LAYOUT="$CURRENT_LAYOUT"
AUTO_LAYOUT=$AUTO_LAYOUT
PREFERRED_CODING_LAYOUT="$CURRENT_LAYOUT"
PREFERRED_WRITING_LAYOUT="$CURRENT_LAYOUT"
PREFERRED_DASHBOARD_LAYOUT="$CURRENT_LAYOUT"
EOF
}

# Detect optimal layout based on content and screen size
detect_optimal_layout() {
    local mode="$1"
    local content_type="$2"
    
    detect_terminal_size
    
    # If auto layout is disabled, keep current
    if [[ "$AUTO_LAYOUT" != true ]]; then
        return
    fi
    
    local suggested_layout=""
    
    # Content-based suggestions
    case "$mode" in
        MARKDOWN)
            case "$content_type" in
                *mission*|*project*) suggested_layout="writing" ;;
                *log*|*report*) suggested_layout="standard" ;;
                *) suggested_layout="writing" ;;
            esac
            ;;
        USCRIPT)
            suggested_layout="coding"
            ;;
        SHORTCODE)
            suggested_layout="standard"
            ;;
        COMMAND)
            # Check what command is being used
            case "$content_type" in
                dashboard|dash) suggested_layout="dashboard" ;;
                *) suggested_layout="standard" ;;
            esac
            ;;
    esac
    
    # Screen size constraints
    if (( CURRENT_COLS < 100 )); then
        suggested_layout="compact"
    elif (( CURRENT_COLS >= 160 )); then
        if [[ "$suggested_layout" == "standard" ]]; then
            suggested_layout="wide"
        elif [[ "$suggested_layout" == "writing" ]]; then
            suggested_layout="writing"  # Keep writing narrow even on wide screens
        fi
    fi
    
    # Apply suggestion if different from current
    if [[ "$suggested_layout" != "$CURRENT_LAYOUT" && -n "$suggested_layout" ]]; then
        apply_layout "$suggested_layout" "auto-detected for $mode mode"
    fi
}

# Apply a specific layout
apply_layout() {
    local layout="$1"
    local reason="${2:-manual selection}"
    
    local cols rows
    
    case "$layout" in
        compact)
            cols=$COMPACT_COLS
            rows=$COMPACT_ROWS
            ;;
        standard)
            cols=$STANDARD_COLS
            rows=$STANDARD_ROWS
            ;;
        wide)
            cols=$WIDE_COLS
            rows=$WIDE_ROWS
            ;;
        coding)
            cols=$CODING_COLS
            rows=$CODING_ROWS
            ;;
        writing)
            cols=$WRITING_COLS
            rows=$WRITING_ROWS
            ;;
        dashboard)
            cols=$DASHBOARD_COLS
            rows=$DASHBOARD_ROWS
            ;;
        auto)
            # Auto-detect based on current mode
            detect_optimal_layout "$CURRENT_MODE" ""
            return
            ;;
        *)
            log_error "Unknown layout: $layout"
            return 1
            ;;
    esac
    
    # Apply the layout
    CURRENT_LAYOUT="$layout"
    set_terminal_size "$cols" "$rows"
    
    log_info "Layout changed to '$layout' ($reason)"
    save_layout_config
}

# Show layout information and options
show_layout_manager() {
    echo -e "\n${CYAN}📐 Responsive Layout Manager${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    detect_terminal_size
    
    echo -e "${BOLD}Current status:${NC}"
    echo -e "${CYAN}Screen size:${NC} ${CURRENT_COLS}x${CURRENT_ROWS}"
    echo -e "${CYAN}Active layout:${NC} $CURRENT_LAYOUT"
    echo -e "${CYAN}Auto layout:${NC} $(if [[ "$AUTO_LAYOUT" == true ]]; then echo "✅ Enabled"; else echo "❌ Disabled"; fi)"
    echo -e "${CYAN}Current mode:${NC} $CURRENT_MODE"
    
    echo ""
    echo -e "${BOLD}📱 Available layouts:${NC}"
    echo -e "  ${YELLOW}1.${NC} ${BLUE}compact${NC}     - 80x24   (minimal, mobile-friendly)"
    echo -e "  ${YELLOW}2.${NC} ${BLUE}standard${NC}    - 120x30  (balanced, recommended)"
    echo -e "  ${YELLOW}3.${NC} ${BLUE}wide${NC}        - 140x35  (spacious, comfortable)"
    echo -e "  ${YELLOW}4.${NC} ${BLUE}coding${NC}      - 120x50  (tall, perfect for scripts)"
    echo -e "  ${YELLOW}5.${NC} ${BLUE}writing${NC}     - 100x35  (narrow, focused reading)"
    echo -e "  ${YELLOW}6.${NC} ${BLUE}dashboard${NC}   - 160x40  (wide, data visualization)"
    echo -e "  ${YELLOW}7.${NC} ${BLUE}auto${NC}        - Auto-detect based on content"
    
    echo ""
    echo -e "${BOLD}🎯 Smart layout features:${NC}"
    echo -e "  • ${GREEN}Context-aware switching${NC} - Layouts adapt to your work"
    echo -e "  • ${GREEN}Content optimization${NC} - Different layouts for different tasks"
    echo -e "  • ${GREEN}Screen size detection${NC} - Automatic mobile/desktop adjustment"
    echo -e "  • ${GREEN}Workflow preservation${NC} - Remembers your preferences"
    
    echo ""
    echo -e "${CYAN}💡 Commands:${NC}"
    echo -e "  • ${BOLD}layout <name>${NC} - Switch to specific layout"
    echo -e "  • ${BOLD}layout auto on/off${NC} - Enable/disable auto-detection"
    echo -e "  • ${BOLD}layout info${NC} - Show current layout information"
    echo -e "  • ${BOLD}layout reset${NC} - Reset to optimal layout for current mode"
    echo ""
}

# Enhanced mode switching with layout awareness
set_mode_with_layout() {
    local new_mode="$1"
    local file="$2"
    local content_hint="$3"
    
    # Set the mode first
    CURRENT_MODE="$new_mode"
    CURRENT_FILE="$file"
    
    # Auto-detect optimal layout for this mode
    detect_optimal_layout "$new_mode" "$content_hint"
    
    log_info "Switched to $new_mode mode"
    if [[ -n "$file" ]]; then
        log_info "Editing: $(basename "$file")"
    fi
}

# Layout-aware terminal optimization
optimize_for_content() {
    local content_type="$1"
    
    case "$content_type" in
        *mission*|*project*)
            if [[ "$AUTO_LAYOUT" == true ]]; then
                apply_layout "writing" "optimized for project content"
            fi
            ;;
        *script*|*code*)
            if [[ "$AUTO_LAYOUT" == true ]]; then
                apply_layout "coding" "optimized for script editing"
            fi
            ;;
        *dashboard*|*stats*|*report*)
            if [[ "$AUTO_LAYOUT" == true ]]; then
                apply_layout "dashboard" "optimized for data viewing"
            fi
            ;;
    esac
}

# Multi-pane layout helpers
create_split_view() {
    local left_content="$1"
    local right_content="$2"
    local split_ratio="${3:-50}"  # Percentage for left pane
    
    detect_terminal_size
    local left_width=$(( CURRENT_COLS * split_ratio / 100 ))
    local right_width=$(( CURRENT_COLS - left_width - 1 ))
    
    echo -e "\n${CYAN}📊 Split view layout${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Create side-by-side display
    echo -e "${BOLD}Left Panel (${left_width} cols):${NC} $left_content"
    echo -e "${BOLD}Right Panel (${right_width} cols):${NC} $right_content"
    
    # This is a simplified version - full implementation would use terminal positioning
}

# Context-aware layout suggestions
suggest_layout_improvements() {
    local current_task="$1"
    
    detect_terminal_size
    
    echo -e "\n${YELLOW}💡 Layout Suggestions${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    case "$current_task" in
        *editing*|*markdown*)
            if [[ "$CURRENT_LAYOUT" != "writing" && $CURRENT_COLS -gt 110 ]]; then
                echo -e "${CYAN}📝 Writing Mode${NC} - Consider switching to 'writing' layout for better text readability"
            fi
            ;;
        *script*|*code*)
            if [[ "$CURRENT_LAYOUT" != "coding" && $CURRENT_ROWS -lt 45 ]]; then
                echo -e "${PURPLE}⚡ Coding Mode${NC} - Switch to 'coding' layout for more vertical space"
            fi
            ;;
        *dashboard*|*monitoring*)
            if [[ "$CURRENT_LAYOUT" != "dashboard" && $CURRENT_COLS -lt 150 ]]; then
                echo -e "${BLUE}📊 Dashboard Mode${NC} - Use 'dashboard' layout for better data visualization"
            fi
            ;;
    esac
    
    # Screen size suggestions
    if (( CURRENT_COLS < 100 )); then
        echo -e "${YELLOW}📱 Small Screen${NC} - Consider using 'compact' layout for mobile-friendly interface"
    elif (( CURRENT_COLS > 160 )); then
        echo -e "${GREEN}🖥️  Large Screen${NC} - You can use 'wide' or 'dashboard' layouts for more space"
    fi
    
    echo ""
}

# Panel Generator Functions
generate_memory_panel() {
    local width="$1"
    local height="$2"
    local content_width=$((width - 4))
    local content_height=$((height - 2))
    
    local panel_output=""
    panel_output+="$(draw_panel_border "$width" "$height" "double" "🧠 MEMORY")\n"
    
    # Memory statistics
    local memory_files=$(find "$UMEMORY" -type f 2>/dev/null | wc -l)
    local memory_size=$(du -sh "$UMEMORY" 2>/dev/null | cut -f1 || echo "0K")
    local recent_file=$(ls -t "$UMEMORY" 2>/dev/null | head -1 || echo "none")
    
    local content="Files: $memory_files\nSize: $memory_size\nRecent: $(echo "$recent_file" | cut -c1-20)...\n"
    content+="Status: ✅ Active\nType: Flat Structure"
    
    # Add formatted content with positioning
    local formatted_content=$(format_panel_content "$content" "$content_width" "$content_height")
    local line_num=1
    while IFS= read -r line; do
        panel_output+="$(printf "║ %-*s ║\n" $((content_width)) "$line")"
        ((line_num++))
    done <<< "$formatted_content"
    
    # Fill remaining space
    while ((line_num < content_height + 1)); do
        panel_output+="$(printf "║ %-*s ║\n" $((content_width)) "")"
        ((line_num++))
    done
    
    echo -e "$panel_output"
}

generate_mission_panel() {
    local width="$1"
    local height="$2"
    local content_width=$((width - 4))
    local content_height=$((height - 2))
    
    local panel_output=""
    panel_output+="$(draw_panel_border "$width" "$height" "double" "🎯 MISSIONS")\n"
    
    # Mission statistics
    local total_missions=$(find "$UMEMORY" -name "*-mission.md" 2>/dev/null | wc -l)
    local active_missions=$(grep -l "Status.*Active" "$UMEMORY"/*-mission.md 2>/dev/null | wc -l)
    local completed_missions=$((total_missions - active_missions))
    
    local content="Total: $total_missions\nActive: $active_missions\nCompleted: $completed_missions\n"
    
    # List recent missions (limited)
    content+="Recent:\n"
    find "$UMEMORY" -name "*-mission.md" 2>/dev/null | head -3 | while read mission; do
        local mission_name=$(basename "$mission" .md | sed 's/^[0-9]*-//' | sed 's/-mission$//' | cut -c1-15)
        content+="• $mission_name\n"
    done
    
    local formatted_content=$(format_panel_content "$content" "$content_width" "$content_height")
    local line_num=1
    while IFS= read -r line; do
        panel_output+="$(printf "║ %-*s ║\n" $((content_width)) "$line")"
        ((line_num++))
    done <<< "$formatted_content"
    
    # Fill remaining space
    while ((line_num < content_height + 1)); do
        panel_output+="$(printf "║ %-*s ║\n" $((content_width)) "")"
        ((line_num++))
    done
    
    echo -e "$panel_output"
}

generate_status_panel() {
    local width="$1"
    local height="$2"
    local content_width=$((width - 4))
    local content_height=$((height - 2))
    
    local panel_output=""
    panel_output+="$(draw_panel_border "$width" "$height" "double" "⚙️ STATUS")\n"
    
    # System status
    local uptime_info="$(uptime | cut -d',' -f1 | cut -c1-20)"
    local disk_usage=$(df "$UHOME" 2>/dev/null | tail -1 | awk '{print $5}' || echo "N/A")
    
    local content="System: ✅ Online\nMode: $CURRENT_MODE\nLayout: $CURRENT_LAYOUT\n"
    content+="Disk: $disk_usage\nUptime: $uptime_info"
    
    local formatted_content=$(format_panel_content "$content" "$content_width" "$content_height")
    local line_num=1
    while IFS= read -r line; do
        panel_output+="$(printf "║ %-*s ║\n" $((content_width)) "$line")"
        ((line_num++))
    done <<< "$formatted_content"
    
    # Fill remaining space
    while ((line_num < content_height + 1)); do
        panel_output+="$(printf "║ %-*s ║\n" $((content_width)) "")"
        ((line_num++))
    done
    
    echo -e "$panel_output"
}

generate_data_panel() {
    local width="$1"
    local height="$2"
    local content_width=$((width - 4))
    local content_height=$((height - 2))
    
    local panel_output=""
    panel_output+="$(draw_panel_border "$width" "$height" "double" "📊 DATA")\n"
    
    # Numerical data display
    local files_count=$(find "$UMEMORY" -type f 2>/dev/null | wc -l)
    local commands_run=${HISTORY_COUNT:-0}
    local avg_file_size=$(find "$UMEMORY" -type f -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
    
    local content=""
    content+="┌─ METRICS ────┐\n"
    content+="│ Files:   $(printf "%3d" "$files_count") │\n"
    content+="│ Commands:$(printf "%3d" "$commands_run") │\n"
    content+="│ Avg Size:$(printf "%3d" "$avg_file_size") │\n"
    content+="└──────────────┘\n"
    content+="Status: ACTIVE"
    
    local formatted_content=$(format_panel_content "$content" "$content_width" "$content_height")
    local line_num=1
    while IFS= read -r line; do
        panel_output+="$(printf "║ %-*s ║\n" $((content_width)) "$line")"
        ((line_num++))
    done <<< "$formatted_content"
    
    # Fill remaining space
    while ((line_num < content_height + 1)); do
        panel_output+="$(printf "║ %-*s ║\n" $((content_width)) "")"
        ((line_num++))
    done
    
    echo -e "$panel_output"
}

generate_input_panel() {
    local width="$1"
    local height="$2"
    local content_width=$((width - 4))
    local content_height=$((height - 2))
    
    local panel_output=""
    panel_output+="$(draw_panel_border "$width" "$height" "single" "🔧 INPUT")\n"
    
    local content="[SHORTCODE BUILDER]\n\n"
    content+="COMMANDS:\n"
    content+="┌─────────────────┐\n"
    content+="│ MEMORY|LIST     │\n"
    content+="│ MISSION|CREATE  │\n"
    content+="│ PACKAGE|INSTALL │\n"
    content+="└─────────────────┘\n"
    content+="TYPE: [CMD|ARGS]"
    
    local formatted_content=$(format_panel_content "$content" "$content_width" "$content_height")
    local line_num=1
    while IFS= read -r line; do
        panel_output+="$(printf "│ %-*s │\n" $((content_width)) "$line")"
        ((line_num++))
    done <<< "$formatted_content"
    
    # Fill remaining space
    while ((line_num < content_height + 1)); do
        panel_output+="$(printf "│ %-*s │\n" $((content_width)) "")"
        ((line_num++))
    done
    
    echo -e "$panel_output"
}

# Core panel rendering function
render_panel() {
    local panel_type="$1"
    local x="$2"
    local y="$3"
    local width="${4:-$PANEL_WIDTH}"
    local height="${5:-$PANEL_HEIGHT}"
    local title="$6"
    
    local panel_content=""
    
    case "$panel_type" in
        memory)
            panel_content=$(generate_memory_panel "$width" "$height")
            ;;
        mission)
            panel_content=$(generate_mission_panel "$width" "$height")
            ;;
        status)
            panel_content=$(generate_status_panel "$width" "$height")
            ;;
        data)
            panel_content=$(generate_data_panel "$width" "$height")
            ;;
        input)
            panel_content=$(generate_input_panel "$width" "$height")
            ;;
        *)
            panel_content=$(draw_panel_border "$width" "$height" "single" "$panel_type")
            ;;
    esac
    
    # Position and render the complete panel
    position_panel "$x" "$y" "$panel_content"
}

# Grid layout system
create_panel_grid() {
    local cols="${1:-$GRID_COLS}"
    local rows="${2:-$GRID_ROWS}"
    
    detect_terminal_size
    
    local panel_width=$(( (CURRENT_COLS - (cols + 1) * GRID_GAP) / cols ))
    local panel_height=$(( (CURRENT_ROWS - (rows + 1) * GRID_GAP - 5) / rows ))  # -5 for header/footer
    
    clear
    
    echo -e "${RAINBOW_CYAN}uDOS Panel Dashboard${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Grid positions
    local panel_types=("memory" "mission" "status" "data" "input" "log")
    local panel_index=0
    
    for ((row=0; row<rows; row++)); do
        for ((col=0; col<cols; col++)); do
            if [[ $panel_index -lt ${#panel_types[@]} ]]; then
                local x=$((col * (panel_width + GRID_GAP) + GRID_GAP))
                local y=$((row * (panel_height + GRID_GAP) + GRID_GAP + 4))  # +4 for header
                
                render_panel "${panel_types[$panel_index]}" "$x" "$y" "$panel_width" "$panel_height"
                ((panel_index++))
            fi
        done
    done
    
    # Footer
    printf '\033[%d;1H' $((CURRENT_ROWS - 2))
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}Press 'q' to exit panel view | Arrow keys to navigate${NC}"
}

# Panel dashboard command
show_panel_dashboard() {
    local style="${1:-standard}"
    
    case "$style" in
        compact)
            GRID_COLS=2
            GRID_ROWS=2
            PANEL_WIDTH=35
            PANEL_HEIGHT=12
            ;;
        wide)
            GRID_COLS=4
            GRID_ROWS=2
            PANEL_WIDTH=35
            PANEL_HEIGHT=15
            ;;
        tall)
            GRID_COLS=2
            GRID_ROWS=3
            PANEL_WIDTH=50
            PANEL_HEIGHT=18
            ;;
        *)  # standard
            GRID_COLS=3
            GRID_ROWS=2
            PANEL_WIDTH=40
            PANEL_HEIGHT=15
            ;;
    esac
    
    create_panel_grid
    
    # Interactive panel navigation
    while true; do
        read -rsn1 key
        case "$key" in
            q|Q) break ;;
            r|R) create_panel_grid ;;  # Refresh
            $'\033')  # Arrow keys
                read -rsn2 -t 0.1 arrow
                case "$arrow" in
                    "[A"|"[B"|"[C"|"[D") 
                        # Arrow key navigation (placeholder for panel selection)
                        echo -e "\n${CYAN}Panel navigation active${NC}"
                        ;;
                esac
                ;;
        esac
    done
    
    clear
    log_success "Exited panel dashboard"
}

# Acorn-inspired character editor
show_character_editor() {
    echo -e "\n${CYAN}🔤 uDOS Character Editor${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${YELLOW}📝 Font styles:${NC}"
    echo "  1. Mono     - Fixed-width ASCII (default)"
    echo "  2. Condensed - Compact display"
    echo "  3. Expanded - Wide character spacing"
    echo ""
    echo -e "${YELLOW}🎨 Character sets:${NC}"
    echo "  • Basic    - ASCII 32-126"
    echo "  • Extended - ASCII + Box Drawing"
    echo "  • Unicode  - Full Unicode subset"
    echo ""
    echo -e "${YELLOW}📏 Display constraints:${NC}"
    echo "  • String Length: ≤ $MAX_STRING_LENGTH chars"
    echo "  • Panel Lines:   ≤ $MAX_DISPLAY_LINES lines" 
    echo "  • Panel Items:   ≤ $MAX_PANEL_ITEMS items"
    echo ""
    echo -e "${BLUE}🧮 Markdown compatibility:${NC}"
    echo "  • Human-readable plain text"
    echo "  • Machine-parseable structure"
    echo "  • Minimal memory footprint"
    echo "  • Acorn BBC Micro inspired"
    echo ""
}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Rainbow colors for ASCII art
RAINBOW_RED='\033[91m'
RAINBOW_YELLOW='\033[93m'
RAINBOW_GREEN='\033[92m'
RAINBOW_CYAN='\033[96m'
RAINBOW_BLUE='\033[94m'
RAINBOW_PURPLE='\033[95m'

# Semantic colors for uDOS elements
COMMAND_COLOR="$YELLOW"
SHORTCODE_COLOR="$CYAN"
VARIABLE_COLOR="$GREEN"
PATH_COLOR="$BLUE"
ACCENT_COLOR="$PURPLE"

# uDOS text formatting functions
format_command() {
    echo -e "${COMMAND_COLOR}$1${NC}"
}

format_shortcode() {
    echo -e "${SHORTCODE_COLOR}[$1]${NC}"
}

format_variable() {
    echo -e "${VARIABLE_COLOR}\$$1${NC}"
}

format_path() {
    echo -e "${PATH_COLOR}$1${NC}"
}

# Enhanced text processing for mixed content
format_text() {
    local text="$1"
    # Replace COMMANDS with colored versions
    text=$(echo "$text" | sed -E "s/\b([A-Z]{2,})\b/${COMMAND_COLOR}\1${NC}/g")
    # Replace [SHORTCODE|ARGS] with colored versions
    text=$(echo "$text" | sed -E "s/\[([^]]+)\]/${SHORTCODE_COLOR}[\1]${NC}/g")
    # Replace $VARIABLES with colored versions
    text=$(echo "$text" | sed -E "s/\\\$([A-Z_][A-Z0-9_]*)\b/${VARIABLE_COLOR}\$\1${NC}/g")
    echo -e "$text"
}

# Logging
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_header() { echo -e "\n${BOLD}${CYAN}🌀 $1${NC}\n"; }

# Mode Management Functions
show_mode_indicator() {
    local mode_color=""
    local mode_icon=""
    
    case "$CURRENT_MODE" in
        COMMAND)
            mode_color="${RAINBOW_CYAN}"
            mode_icon="🌀"
            ;;
        MARKDOWN)
            mode_color="${RAINBOW_GREEN}"
            mode_icon="📝"
            ;;
        USCRIPT)
            mode_color="${RAINBOW_PURPLE}"
            mode_icon="⚡"
            ;;
        SHORTCODE)
            mode_color="${RAINBOW_YELLOW}"
            mode_icon="🔧"
            ;;
    esac
    
    # Just show the icon if not in COMMAND mode
    if [[ "$CURRENT_MODE" != "COMMAND" ]]; then
        echo -e "${mode_color}${mode_icon}${NC}"
        
        # Show current file if in editor mode
        if [[ -n "$CURRENT_FILE" ]]; then
            echo -e "${CYAN}📁 $(basename "$CURRENT_FILE")${NC}"
        fi
    fi
}

# Command History Management
add_to_history() {
    local command="$1"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    # Skip empty commands and certain meta commands
    [[ -z "$command" ]] && return
    [[ "$command" =~ ^(history|exit|quit)$ ]] && return
    
    # Add to history file with timestamp
    echo "$timestamp:$command" >> "$COMMAND_HISTORY_FILE"
    ((HISTORY_COUNT++))
    
    # Maintain history limit
    if [[ $HISTORY_COUNT -gt $MAX_HISTORY ]]; then
        # Keep only the last MAX_HISTORY lines
        tail -n "$MAX_HISTORY" "$COMMAND_HISTORY_FILE" > "${COMMAND_HISTORY_FILE}.tmp"
        mv "${COMMAND_HISTORY_FILE}.tmp" "$COMMAND_HISTORY_FILE"
        HISTORY_COUNT=$MAX_HISTORY
    fi
}

show_command_history() {
    echo -e "\n${CYAN}📚 Command History${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ ! -f "$COMMAND_HISTORY_FILE" ]] || [[ ! -s "$COMMAND_HISTORY_FILE" ]]; then
        echo -e "${YELLOW}No commands in history yet${NC}"
        return
    fi
    
    # Show last 10 commands
    local count=1
    tail -n 10 "$COMMAND_HISTORY_FILE" | while IFS=':' read -r timestamp command; do
        local display_time=$(echo "$timestamp" | cut -c 10-13 | sed 's/../&:/')
        echo -e "${BLUE}$count.${NC} ${YELLOW}$display_time${NC} $command"
        ((count++))
    done
    
    echo ""
    echo -e "${CYAN}💡 Use 'history search <term>' to find specific commands${NC}"
    echo -e "${CYAN}💡 Use '!<number>' to repeat a command from history${NC}"
}

search_command_history() {
    local search_term="$1"
    echo -e "\n${CYAN}🔍 Searching History for: '$search_term'${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ ! -f "$COMMAND_HISTORY_FILE" ]]; then
        echo -e "${YELLOW}No command history found${NC}"
        return
    fi
    
    local found=false
    local count=1
    grep -i "$search_term" "$COMMAND_HISTORY_FILE" | tail -n 10 | while IFS=':' read -r timestamp command; do
        local display_time=$(echo "$timestamp" | cut -c 10-13 | sed 's/../&:/')
        echo -e "${BLUE}$count.${NC} ${YELLOW}$display_time${NC} $command"
        found=true
        ((count++))
    done
    
    if ! grep -qi "$search_term" "$COMMAND_HISTORY_FILE" 2>/dev/null; then
        echo -e "${YELLOW}No commands found matching '$search_term'${NC}"
    fi
    echo ""
}

# Smart context-aware suggestions
get_smart_suggestions() {
    local input="$1"
    local suggestions=()
    
    # File completion for memory files
    if [[ "$input" == *"view "* || "$input" == *"edit "* || "$input" == *"view:"* || "$input" == *"edit:"* ]]; then
        if [[ -d "$UMEMORY" ]]; then
            while IFS= read -r file; do
                if [[ "$file" == *"${input##* }"* ]]; then
                    suggestions+=("${input% *} $file")
                fi
            done < <(ls "$UMEMORY" 2>/dev/null)
        fi
    fi
    
    # Mission name completion
    if [[ "$input" == *"complete "* || "$input" == *"complete:"* ]]; then
        if [[ -d "$UMEMORY" ]]; then
            while IFS= read -r mission; do
                local mission_name=$(basename "$mission" .md | sed 's/^[0-9]*-//' | sed 's/-mission$//')
                if [[ "$mission_name" == *"${input##* }"* ]]; then
                    suggestions+=("${input% *} $mission_name")
                fi
            done < <(find "$UMEMORY" -name "*-mission.md" 2>/dev/null)
        fi
    fi
    
    # Package completion
    if [[ "$input" == *"install "* || "$input" == *"install:"* ]]; then
        local packages=("ripgrep" "fd" "bat" "glow" "micro" "jq" "fzf" "tree" "htop")
        for pkg in "${packages[@]}"; do
            if [[ "$pkg" == *"${input##* }"* ]]; then
                suggestions+=("${input% *} $pkg")
            fi
        done
    fi
    
    # History-based suggestions
    if [[ -f "$COMMAND_HISTORY_FILE" ]]; then
        tail -n 20 "$COMMAND_HISTORY_FILE" | while IFS=':' read -r timestamp command; do
            if [[ "$command" == "$input"* && "$command" != "$input" ]]; then
                echo "$command"
            fi
        done | sort -u
    fi
}

set_mode() {
    local new_mode="$1"
    local file="$2"
    
    CURRENT_MODE="$new_mode"
    CURRENT_FILE="$file"
    
    log_info "Switched to $new_mode mode"
    if [[ -n "$file" ]]; then
        log_info "Editing: $(basename "$file")"
    fi
}

# Enhanced prompt with mode indicator
show_enhanced_prompt() {
    # Simple prompt with block cursor that blinks once
    # Use a static block cursor that's more reliable across terminals
    echo -ne "🌀 "
}

# Initialize directories
init_directories() {
    local dirs=(
        "$UHOME"
        "$UMEMORY" 
        "$UTEMPLATE"
        "$UDEV"
        "$UHOME/uScript"
        "$UHOME/uKnowledge"
        "$UHOME/package"
        "$UHOME/sandbox"
        "$UHOME/docs"
        "$UHOME/extension"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
    done
}

# Terminal size detection and management
detect_terminal_size() {
    # Get current terminal dimensions
    if command -v tput >/dev/null 2>&1; then
        CURRENT_COLS=$(tput cols 2>/dev/null || echo "80")
        CURRENT_ROWS=$(tput lines 2>/dev/null || echo "24")
    else
        # Fallback using stty
        CURRENT_COLS=$(stty size 2>/dev/null | cut -d' ' -f2 || echo "80")
        CURRENT_ROWS=$(stty size 2>/dev/null | cut -d' ' -f1 || echo "24")
    fi
    
    # Ensure we have valid numbers
    [[ "$CURRENT_COLS" =~ ^[0-9]+$ ]] || CURRENT_COLS=80
    [[ "$CURRENT_ROWS" =~ ^[0-9]+$ ]] || CURRENT_ROWS=24
}

# Set terminal window size using ANSI escape sequences
set_terminal_size() {
    local cols=${1:-120}
    local rows=${2:-30}
    
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
}

# Terminal size recommendation engine
recommend_terminal_size() {
    detect_terminal_size
    
    log_info "Current terminal: ${CURRENT_COLS}x${CURRENT_ROWS}"
    
    # Determine best recommendation based on current size
    local recommended="standard"
    local recommended_size="120x30"
    
    if (( CURRENT_COLS >= 160 )); then
        recommended="ultra-wide"
        recommended_size="160x40"
    elif (( CURRENT_COLS >= 140 )); then
        recommended="wide" 
        recommended_size="140x35"
    elif (( CURRENT_COLS >= 120 )); then
        recommended="standard"
        recommended_size="120x30"
    else
        recommended="compact"
        recommended_size="80x24"
    fi
    
    echo -e "\n${YELLOW}🖥️  Terminal Size Optimizer${NC}"
    echo -e "${BLUE}Current size:${NC} ${CURRENT_COLS}x${CURRENT_ROWS}"
    echo -e "${GREEN}Recommended:${NC} ${recommended_size} (${recommended})"
    echo -e ""
    echo -e "${BOLD}Available presets:${NC}"
    echo -e "  ${CYAN}1.${NC} Compact     - 80x24 (minimal)"
    echo -e "  ${CYAN}2.${NC} Standard    - 120x30 (recommended)"
    echo -e "  ${CYAN}3.${NC} Wide        - 140x35 (comfortable)"
    echo -e "  ${CYAN}4.${NC} Ultra-wide  - 160x40 (spacious)"
    echo -e "  ${CYAN}5.${NC} Coding      - 120x50 (tall for code)"
    echo -e "  ${CYAN}6.${NC} Dashboard   - 140x45 (data viewing)"
    echo -e "  ${CYAN}c.${NC} Keep current size"
    echo -e "  ${CYAN}Enter${NC} Use recommended (${recommended})"
    echo -e ""
    
    read -p "Select size [1-6/c/Enter]: " choice
    
    case "$choice" in
        1) apply_size_preset "compact" ;;
        2) apply_size_preset "standard" ;;
        3) apply_size_preset "wide" ;;
        4) apply_size_preset "ultra-wide" ;;
        5) apply_size_preset "coding" ;;
        6) apply_size_preset "dashboard" ;;
        c|C) log_info "Keeping current size: ${CURRENT_COLS}x${CURRENT_ROWS}" ;;
        "") apply_size_preset "$recommended" ;;
        *) log_warning "Invalid choice, keeping current size" ;;
    esac
}

# Apply size preset
apply_size_preset() {
    local preset=$1
    local size cols rows
    
    case "$preset" in
        "compact") size="80x24" ;;
        "standard") size="120x30" ;;
        "wide") size="140x35" ;;
        "ultra-wide") size="160x40" ;;
        "coding") size="120x50" ;;
        "dashboard") size="140x45" ;;
        *) size="120x30" ;; # fallback
    esac
    
    cols="${size%x*}"
    rows="${size#*x}"
    
    log_info "Applying $preset preset: ${cols}x${rows}"
    set_terminal_size "$cols" "$rows"
    
    # Brief pause to let terminal adjust
    sleep 0.5
}

# Enhanced Rainbow ASCII Art with retro styling
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

# Retro computer boot sequence
show_boot_sequence() {
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}                                                       ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}   ${YELLOW}▓▓▓▓▓ ${CYAN}uDOS v1.2 SYSTEM INITIALIZATION ${YELLOW}▓▓▓▓▓${NC}   ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                       ${GREEN}║${NC}"
    echo -e "${GREEN}╠═══════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║${NC} ${CYAN}►${NC} Memory subsystem............ ${GREEN}[${BOLD}OK${NC}${GREEN}]${NC}             ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} ${CYAN}►${NC} Shortcode processor......... ${GREEN}[${BOLD}OK${NC}${GREEN}]${NC}             ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} ${CYAN}►${NC} ASCII graphics engine....... ${GREEN}[${BOLD}OK${NC}${GREEN}]${NC}             ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} ${CYAN}►${NC} Adventure tutorial system... ${GREEN}[${BOLD}OK${NC}${GREEN}]${NC}             ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} ${CYAN}►${NC} Color display manager....... ${GREEN}[${BOLD}OK${NC}${GREEN}]${NC}             ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC} ${CYAN}►${NC} Interactive dashboard....... ${GREEN}[${BOLD}OK${NC}${GREEN}]${NC}             ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                       ${GREEN}║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# ASCII border generator
draw_ascii_border() {
    local width="${1:-55}"
    local title="$2"
    local style="${3:-double}"
    
    local top_left top_right bottom_left bottom_right horizontal vertical
    
    case "$style" in
        "single")
            top_left="┌" top_right="┐" bottom_left="└" bottom_right="┘"
            horizontal="─" vertical="│"
            ;;
        "double")
            top_left="╔" top_right="╗" bottom_left="╚" bottom_right="╝"
            horizontal="═" vertical="║"
            ;;
        "rounded")
            top_left="╭" top_right="╮" bottom_left="╰" bottom_right="╯"
            horizontal="─" vertical="│"
            ;;
        *)
            top_left="┌" top_right="┐" bottom_left="└" bottom_right="┘"
            horizontal="─" vertical="│"
            ;;
    esac
    
    # Top border with optional title
    if [[ -n "$title" ]]; then
        local title_len=${#title}
        local padding=$(( (width - title_len - 2) / 2 ))
        local remaining=$((width - title_len - 2 - padding))
        
        echo -n "$top_left"
        printf "%*s" $padding "" | tr ' ' "$horizontal"
        echo -n " $title "
        printf "%*s" $remaining "" | tr ' ' "$horizontal"
        echo "$top_right"
    else
        echo -n "$top_left"
        printf "%*s" $((width - 2)) "" | tr ' ' "$horizontal"
        echo "$top_right"
    fi
}

# ASCII progress bar
show_progress_bar() {
    local percentage="$1"
    local width="${2:-40}"
    local filled_width=$((percentage * width / 100))
    local empty_width=$((width - filled_width))
    
    echo -n "["
    printf "%*s" $filled_width "" | tr ' ' '█'
    printf "%*s" $empty_width "" | tr ' ' '░'
    echo -n "] ${percentage}%"
}

# System validation
validate_system() {
    local validation_failed=false
    
    log_info "Validating system integrity..."
    
    # Check critical directories
    local critical_dirs=("$UHOME" "$UMEMORY" "$UTEMPLATE")
    for dir in "${critical_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            log_error "Critical directory missing: $dir"
            validation_failed=true
        fi
    done
    
    # Check critical files
    local critical_files=("$UMEMORY/identity.md")
    for file in "${critical_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_warning "Critical file missing: $file"
            validation_failed=true
        fi
    done
    
    # Check for DESTROY scenario
    if [[ ! -f "$UMEMORY/identity.md" ]] || [[ ! -d "$UHOME" ]]; then
        log_warning "DESTROY scenario detected - full setup required"
        validation_failed=true
    fi
    
    if [[ "$validation_failed" == true ]]; then
        log_warning "System validation failed - initiating recovery"
        return 1
    fi
    
    log_success "System validation passed"
    return 0
}

# Password authentication
authenticate_user() {
    # Skip authentication in development mode or if --no-auth flag is passed
    if [[ "${UDOS_DEV_MODE:-false}" == "true" ]] || [[ "${1:-}" == "--no-auth" ]]; then
        log_info "Skipping authentication (development mode)"
        return 0
    fi
    
    # Check if password is set
    local password_file="$UMEMORY/.auth"
    
    if [[ -f "$password_file" ]]; then
        local stored_hash=$(cat "$password_file")
        
        # Skip if blank password is set
        if [[ "$stored_hash" == "BLANK" ]]; then
            return 0
        fi
        
        echo -ne "${CYAN}🔐 Enter password: ${NC}"
        read -s password
        echo ""
        
        # Simple hash check (for demo - use proper hashing in production)
        local input_hash=$(echo -n "$password" | sha256sum | cut -d' ' -f1 2>/dev/null || echo -n "$password" | shasum -a 256 | cut -d' ' -f1)
        
        if [[ "$input_hash" != "$stored_hash" ]]; then
            log_error "Authentication failed"
            exit 1
        fi
        
        log_success "Authentication successful"
    else
        # First time - set password
        echo -ne "${CYAN}🔐 Set password (or press Enter for none): ${NC}"
        read -s password
        echo ""
        
        if [[ -z "$password" ]]; then
            echo "BLANK" > "$password_file"
            log_info "Password disabled"
        else
            local password_hash=$(echo -n "$password" | sha256sum | cut -d' ' -f1 2>/dev/null || echo -n "$password" | shasum -a 256 | cut -d' ' -f1)
            echo "$password_hash" > "$password_file"
            log_success "Password set"
        fi
    fi
}

# Check if first-time setup needed
check_setup() {
    # Always prompt setup if critical files missing or DESTROY scenario
    if [[ ! -f "$UMEMORY/identity.md" ]] || [[ ! -d "$UHOME" ]] || [[ ! -d "$UMEMORY" ]]; then
        log_warning "Critical system files missing - setup required"
        setup_user
        return 0
    fi
    return 1
}

# User setup
setup_user() {
    log_header "🌀 uDOS v1.2 Setup Wizard"
    echo -e "${CYAN}Welcome to the Universal Data Operating System!${NC}"
    echo -e "You stand at the entrance to a vast digital realm...\n"
    
    # Phase 1: Character Creation
    echo -e "${BOLD}⚔️  Phase 1: Character creation${NC}"
    echo -e "${YELLOW}The Guardian of the Data Realm appears before you:${NC}"
    echo -e "\"Greetings, traveler! Before you can enter the realm of uDOS,\""
    echo -e "\"you must choose your identity. What name shall the realm know you by?\""
    echo ""
    read -p "👤 Enter your adventurer name: " USERNAME
    
    echo -e "\n${YELLOW}\"Excellent, $USERNAME! Now, what is your calling in this realm?\"${NC}"
    echo ""
    echo "  1. 🧙 **Wizard** - Master of ancient command-line magics"
    echo "  2. 🪄 **Sorcerer** - Wielder of advanced data manipulation spells"  
    echo "  3. 👻 **Ghost** - Silent wanderer who prefers minimal interfaces"
    echo "  4. 😈 **Trickster** - Mischievous experimenter of new features"
    echo "  5. 📚 **Scholar** - Keeper of documentation and methodical knowledge"
    echo ""
    read -p "🎯 Choose your class [1-5]: " role_choice
    
    case "$role_choice" in
        1) ROLE="wizard"; CLASS_DESC="Master of shortcuts and command mastery" ;;
        2) ROLE="sorcerer"; CLASS_DESC="Expert in data transformation and analysis" ;;
        3) ROLE="ghost"; CLASS_DESC="Minimalist who values clean, efficient interfaces" ;;
        4) ROLE="trickster"; CLASS_DESC="Bold experimenter always trying new features" ;;
        5) ROLE="scholar"; CLASS_DESC="Methodical learner who reads all documentation" ;;
        *) ROLE="wizard"; CLASS_DESC="Master of shortcuts and command mastery" ;;
    esac
    
    echo -e "\n${GREEN}\"Ah, a $ROLE! ${CLASS_DESC}.\"${NC}"
    
    # Phase 2: Equipment Selection (Terminal Setup)
    echo -e "\n${BOLD}�️  Phase 2: Equipment selection${NC}"
    echo -e "${YELLOW}\"Now you must choose your equipment. What type of viewing crystal do you possess?\"${NC}"
    echo ""
    echo "  1. 💻 **Portable Crystal** - Compact display, efficient magic"
    echo "  2. 🖥️  **Standard Orb** - Balanced viewing, comfortable scrying"
    echo "  3. 📺 **Great Seeing Stone** - Wide visions, maximum information"
    echo "  4. 📱 **Pocket Mirror** - Minimal display, touch-responsive"
    echo "  5. 🤖 **Adaptive Lens** - Automatically adjusts to your needs"
    echo ""
    read -p "🔮 Select your viewing equipment [1-5]: " screen_choice
    
    case "$screen_choice" in
        1) SCREEN_PREF="laptop"; EQUIP_DESC="Portable Crystal (efficient layouts)" ;;
        2) SCREEN_PREF="desktop"; EQUIP_DESC="Standard Orb (balanced viewing)" ;;
        3) SCREEN_PREF="large-screen"; EQUIP_DESC="Great Seeing Stone (wide layouts)" ;;
        4) SCREEN_PREF="mobile"; EQUIP_DESC="Pocket Mirror (minimal layouts)" ;;
        5) SCREEN_PREF="auto"; EQUIP_DESC="Adaptive Lens (auto-adjusting)" ;;
        *) SCREEN_PREF="auto"; EQUIP_DESC="Adaptive Lens (auto-adjusting)" ;;
    esac
    
    echo -e "\n${GREEN}\"The ${EQUIP_DESC} is an excellent choice!\"${NC}"
    
    # Phase 3: Adventure style
    echo -e "\n${BOLD}⚡ Phase 3: Adventure style${NC}"
    echo -e "${YELLOW}\"Finally, how do you wish to explore this realm?\"${NC}"
    echo ""
    echo "  1. 🚀 **Speed Runner** - Quick actions, minimal explanations"
    echo "  2. 🎯 **Guided Explorer** - Helpful hints and suggestions"
    echo "  3. 📖 **Thorough Investigator** - Full explanations and lore"
    echo "  4. 🔧 **Independent Adventurer** - Configure everything myself"
    echo ""
    read -p "⚔️ Choose your adventure style [1-4]: " workflow_choice
    
    case "$workflow_choice" in
        1) WORKFLOW="speed"; STYLE_DESC="Speed Runner (quick and efficient)" ;;
        2) WORKFLOW="guided"; STYLE_DESC="Guided Explorer (helpful hints)" ;;
        3) WORKFLOW="detailed"; STYLE_DESC="Thorough Investigator (full documentation)" ;;
        4) WORKFLOW="custom"; STYLE_DESC="Independent Adventurer (self-configured)" ;;
        *) WORKFLOW="guided"; STYLE_DESC="Guided Explorer (helpful hints)" ;;
    esac
    
    echo -e "\n${GREEN}\"The path of the ${STYLE_DESC} suits you well!\"${NC}"
    
    # Phase 4: Realm Registration
    echo -e "\n${BOLD}� Phase 4: Realm registration${NC}"
    echo -e "${YELLOW}\"Your character sheet is being inscribed in the Great Codex...\"${NC}"
    
    log_info "Creating your adventurer profile in the uDOS realm..."
    
    cat > "$UMEMORY/identity.md" << EOF
# ⚔️ Adventurer Profile

**Name**: $USERNAME  
**Class**: $ROLE  
**Joined Realm**: $(date +%Y-%m-%d)  
**System**: uDOS $VERSION

## Character Sheet

- **Equipment**: $EQUIP_DESC
- **Adventure Style**: $STYLE_DESC  
- **Memory Type**: Infinite Scroll Architecture
- **Spellbook**: uCode Visual Basic Dialect v1.2
- **Registration Date**: $(date +%Y-%m-%d)

## Current Stats
- **Level**: Apprentice
- **Experience**: 0 XP  
- **Realm Mastery**: Beginner
- **Favorite Spells**: To be discovered...

---

*Character profile for the uDOS realm*
EOF

    cat > "$UMEMORY/setup-vars.sh" << EOF
#!/bin/bash
# uDOS realm configuration

export UDOS_USER="$USERNAME"
export UDOS_ROLE="$ROLE"
export UDOS_SCREEN_PREF="$SCREEN_PREF"
export UDOS_WORKFLOW="$WORKFLOW"
export UDOS_VERSION="$VERSION"
export UDOS_SETUP_DATE="$(date +%Y-%m-%d)"
export UDOS_MEMORY_TYPE="flat"
EOF

    cat > "$UMEMORY/001-welcome-mission.md" << EOF
# 🎯 Mission: Welcome to uDOS v1.2

**Created**: $(date +%Y-%m-%d)  
**Status**: Active  
**Type**: Introduction

## Welcome, $USERNAME!

You've successfully set up uDOS v1.2 with the following features:

### 🧠 Flat memory structure
- All files in \`uMemory/\` directory
- Clear naming conventions
- Direct access to all data

### 🔄 Unified commands
- Shortcode syntax: \`[COMMAND|ARGS]\`
- Direct commands: \`COMMAND ARGS\`
- Template processing integrated

### 🎯 Your role: $ROLE
- Full system access based on your role
- Workflow optimized for $WORKFLOW style
- Screen layout preference: $SCREEN_PREF

### 🚀 Quick start
Try these commands to get started:
- \`STATUS\` - See system overview
- \`GO\` - Browse all shortcuts  
- \`[MEM|LIST]\` - List memory files
- \`DASH\` - View live dashboard

### 🎓 Next steps
1. Explore the shortcode system with \`GO\`
2. Try the dashboard with \`DASH\`
3. Create your first mission with \`MISSION CREATE my-first-task\`

---

**Mission Status**: Active 🎯
EOF

    # Phase 5: Setup Complete & Tutorial Offer
    echo -e "\n${BOLD}✅ Character creation complete!${NC}"
    echo -e "${GREEN}\"Welcome to the realm, $USERNAME the $ROLE!\"${NC}"
    echo -e "${YELLOW}\"Your adventure begins now...\"${NC}\n"
    
    # Offer tutorial adventure
    echo -e "${BOLD}🗡️ Begin your first quest?${NC}"
    echo "The Guardian holds up an ancient scroll..."
    echo -e "\"Would you like to embark on the ${CYAN}Trial of First Commands${NC}?\""
    echo "This interactive adventure will teach you the ways of uCode magic!"
    echo ""
    read -p "🎮 Start the tutorial adventure? [Y/n]: " start_tutorial
    
    if [[ "${start_tutorial,,}" != "n" ]]; then
        log_success "Your character sheet has been saved to the Great Codex!"
        start_adventure_tutorial
    else
        log_success "Your character sheet has been saved! Type HELP when ready to explore."
    fi
    
    echo -e "\n${CYAN}🎓 Would you like a quick tutorial?${NC}"
    echo "  1. 🚀 yes - Show me the basics (5 minutes)"
    echo "  2. 📚 guided - I'll explore with hints"
    echo "  3. 🏃 skip - I'll figure it out myself"
    read -p "Select option [1-3]: " tutorial_choice
    
    case "$tutorial_choice" in
        1) 
            log_info "Starting uDOS tutorial..."
            start_tutorial
            ;;
        2)
            log_info "Guided mode enabled - you'll see helpful tips!"
            echo "GUIDED_MODE=true" >> "$UMEMORY/setup-vars.sh"
            ;;
        3)
            log_info "Tutorial skipped - type GO anytime for help!"
            ;;
    esac
    
    log_success "Setup complete! Welcome to uDOS v1.2, $USERNAME!"
    echo -e "\n${CYAN}Type STATUS to see your system overview${NC}"
}

# Tutorial System for New Users
start_tutorial() {
    # Call the new adventure tutorial instead
    start_adventure_tutorial
}

# Adventure Tutorial - NetHack-inspired uCode learning
start_adventure_tutorial() {
    clear
    log_header "🗡️ The Trial of First Commands"
    echo -e "${CYAN}You find yourself in a mysterious digital dungeon...${NC}\n"
    
    # Chapter 1: The Entrance Hall
    adventure_chapter_1
    
    # Chapter 2: The Memory Chambers  
    adventure_chapter_2
    
    # Chapter 3: The Shortcode Sanctum
    adventure_chapter_3
    
    # Chapter 4: The Final Challenge
    adventure_chapter_4
    
    # Bonus: uCode Magic Demo
    adventure_bonus_ucode
    
    # Victory!
    adventure_complete
}

# Chapter 1: Basic Commands
adventure_chapter_1() {
    echo -e "${BOLD}� Chapter 1: The Entrance Hall${NC}"
    echo -e "You stand in a dimly lit stone chamber. Ancient runes glow on the walls."
    echo -e "To your ${YELLOW}north${NC}, you see a pedestal with a glowing crystal."
    echo -e "To your ${YELLOW}east${NC}, a heavy wooden door blocks your path."
    echo -e "A wise voice echoes: \"Speak the word of ${CYAN}STATUS${NC} to reveal the chamber's secrets.\""
    echo ""
    
    while true; do
        read -p "🧙 What do you do? (STATUS/quit): " action
        case "$(echo "$action" | tr '[:lower:]' '[:upper:]')" in
            "STATUS")
                echo -e "\n${GREEN}✨ The crystal blazes with light!${NC}"
                echo -e "The chamber's secrets are revealed:"
                show_status
                echo -e "\n${YELLOW}The eastern door creaks open with a satisfied rumble.${NC}"
                echo -e "You have learned the ${CYAN}STATUS${NC} spell! (+10 XP)"
                break
                ;;
            "QUIT")
                echo -e "\n${RED}You flee the dungeon. Perhaps another time...${NC}"
                return 1
                ;;
            *)
                echo -e "\n${RED}The chamber does not respond to '$action'. Try 'STATUS'.${NC}"
                ;;
        esac
    done
    
    echo ""
    read -p "Press Enter to continue east..."
    clear
}

# Chapter 2: Memory System  
adventure_chapter_2() {
    echo -e "${BOLD}📜 Chapter 2: The Memory Chambers${NC}"
    echo -e "You enter a vast library filled with floating scrolls and glowing tablets."
    echo -e "A robed figure approaches: \"Welcome to the ${CYAN}Memory Vaults${NC}, adventurer!\""
    echo -e "\"Here, all knowledge is stored in sacred ${YELLOW}.md scrolls${NC}.\""
    echo -e "\"To see what wisdom exists, cast the ${CYAN}MEM LIST${NC} spell.\""
    echo ""
    
    while true; do
        read -p "🧙 Cast your spell (MEM LIST/help/quit): " action
        case "$(echo "$action" | tr '[:lower:]' '[:upper:]')" in
            "MEM LIST")
                echo -e "\n${GREEN}✨ The scrolls organize themselves before you!${NC}"
                handle_memory "LIST"
                echo -e "\n${YELLOW}\"Excellent! You can now navigate the Memory Vaults!\"${NC}"
                echo -e "You have learned ${CYAN}Memory Navigation${NC}! (+15 XP)"
                break
                ;;
            "HELP")
                echo -e "\n${BLUE}The robed figure whispers:${NC}"
                echo -e "\"MEM LIST reveals all scrolls in the vault.\""
                echo -e "\"Each scroll name tells its creation date and purpose.\""
                ;;
            "QUIT")
                echo -e "\n${RED}You back away from the mystical library...${NC}"
                return 1
                ;;
            *)
                echo -e "\n${RED}\"That incantation has no power here. Try 'MEM LIST'.\"${NC}"
                ;;
        esac
    done
    
    echo ""
    read -p "Press Enter to venture deeper..."
    clear
}

# Chapter 3: Shortcode Magic
adventure_chapter_3() {
    echo -e "${BOLD}� Chapter 3: The Shortcode Sanctum${NC}"
    echo -e "You discover a circular chamber with glowing brackets carved into the floor."
    echo -e "An ancient wizard materializes: \"Ah! You seek the ${CYAN}Shortcode Arts${NC}!\""
    echo -e "\"These powerful spells use the sacred brackets: ${YELLOW}[SPELL|POWER]${NC}\""
    echo -e "\"Try the ${CYAN}[PACK|LIST]${NC} incantation to summon the Package Spirits!\""
    echo ""
    
    while true; do
        read -p "🧙 Cast shortcode magic ([PACK|LIST]/help/quit): " action
        case "$(echo "$action" | tr '[:lower:]' '[:upper:]')" in
            "[PACK|LIST]")
                echo -e "\n${GREEN}✨ Mystical energies swirl around you!${NC}"
                handle_package "LIST"
                echo -e "\n${YELLOW}\"Magnificent! You've mastered basic shortcode magic!\"${NC}"
                echo -e "\"Remember: ${CYAN}[COMMAND|ARGUMENT]${NC} is the sacred form.\""
                echo -e "You have learned ${CYAN}Shortcode Mastery${NC}! (+20 XP)"
                break
                ;;
            "HELP")
                echo -e "\n${BLUE}The wizard explains:${NC}"
                echo -e "\"Shortcodes are spells in bracket form: [COMMAND|ARGS]\""
                echo -e "\"[PACK|LIST] reveals available magical packages.\""
                echo -e "\"[MEM|LIST] shows memory scrolls. [DASH|LIVE] summons live visions!\""
                ;;
            "QUIT")
                echo -e "\n${RED}The magical energies dissipate as you retreat...${NC}"
                return 1
                ;;
            *)
                echo -e "\n${RED}\"Your magic fizzles. Use the exact form: [PACK|LIST]\"${NC}"
                ;;
        esac
    done
    
    echo ""
    read -p "Press Enter for the final challenge..."
    clear
}

# Bonus Chapter: uCode Magic Demonstration
adventure_bonus_ucode() {
    echo -e "${BOLD}📜 Bonus: The Hall of Living Code${NC}"
    echo -e "You discover a shimmering chamber with floating code fragments."
    echo -e "A master programmer appears: \"Behold! The power of ${CYAN}uCode${NC}!\""
    echo -e "\"Watch as I demonstrate Visual Basic-style magic in the terminal!\""
    echo ""
    
    echo -e "${YELLOW}The wizard begins chanting...${NC}"
    echo ""
    
    # Simple uCode demonstration
    echo -e "${CYAN}--- uCode Magic Example ---${NC}"
    echo -e "${BOLD}IF${NC} status = \"learning\" ${BOLD}THEN${NC}"
    echo -e "    ${GREEN}PRINT${NC} \"Welcome, \$username!\""
    echo -e "    ${GREEN}SET${NC} experience = experience + 10"
    echo -e "${BOLD}ELSE${NC}"
    echo -e "    ${GREEN}PRINT${NC} \"Ready for more adventures?\""
    echo -e "${BOLD}END IF${NC}"
    echo ""
    
    echo -e "${YELLOW}\"See how uCode flows like natural language?\"${NC}"
    echo -e "\"${CYAN}IF/THEN/ELSE${NC} logic, ${CYAN}PRINT${NC} statements, ${CYAN}SET${NC} variables!\""
    echo -e "\"Just like Visual Basic, but designed for data wizards!\""
    echo ""
    
    echo -e "${BOLD}Simple uCode spells you'll learn:${NC}"
    echo -e "  • ${YELLOW}PRINT \"Hello World\"${NC} - Display messages"
    echo -e "  • ${YELLOW}SET name = \"Wizard\"${NC} - Create variables"
    echo -e "  • ${YELLOW}IF answer = \"yes\" THEN...${NC} - Make decisions"
    echo -e "  • ${YELLOW}FOR each file IN memory...${NC} - Loop through data"
    echo -e "  • ${YELLOW}CALL memory_backup()${NC} - Run functions"
    
    echo ""
    read -p "🎭 Press Enter to witness the magic in action..."
    
    # Live demonstration
    echo -e "\n${GREEN}✨ Casting a real uCode spell...${NC}"
    echo ""
    echo -e "${CYAN}PRINT \"Greetings, brave adventurer!\"${NC}"
    echo -e "Greetings, brave adventurer!"
    echo -e "${CYAN}SET current_level = \"Novice\"${NC}"
    echo -e "${CYAN}PRINT \"Your current level is: \" + current_level${NC}"
    echo -e "Your current level is: Novice"
    echo -e "${CYAN}IF tutorial_complete = true THEN${NC}"
    echo -e "${CYAN}    PRINT \"🏆 Achievement Unlocked!\"${NC}"
    echo -e "🏆 Achievement Unlocked!"
    echo -e "${CYAN}END IF${NC}"
    
    echo ""
    echo -e "${YELLOW}\"Amazing! You've seen uCode in action!\"${NC}"
    echo -e "\"When you're ready to learn more, explore the uScript chambers!\""
    
    echo ""
    read -p "Press Enter to claim your final reward..."
    clear
}

# Chapter 4: The Choice Challenge
adventure_chapter_4() {
    echo -e "${BOLD}📜 Chapter 4: The Chamber of Choices${NC}"
    echo -e "You face a massive door with two keyholes: ${YELLOW}YES${NC} and ${YELLOW}NO${NC}."
    echo -e "A booming voice echoes: \"MORTAL! Answer wisely and gain passage!\""
    echo ""
    echo -e "🗣️ ${BOLD}\"Do you wish to learn the advanced arts of uCode scripting?\"${NC}"
    echo -e "   (uCode is like Visual Basic but for the command line!)"
    echo ""
    
    while true; do
        read -p "🗝️ Your answer (YES/NO): " choice
        case "$(echo "$choice" | tr '[:lower:]' '[:upper:]')" in
            "YES")
                echo -e "\n${GREEN}✨ The YES keyhole blazes with golden light!${NC}"
                echo -e "\"EXCELLENT! You hunger for knowledge!\""
                echo -e "\"uCode scripting allows you to:\""
                echo -e "  • Write simple IF/THEN logic"
                echo -e "  • Create loops and variables"  
                echo -e "  • Build custom commands"
                echo -e "  • Automate repetitive tasks\""
                echo -e "\n${YELLOW}\"You shall become a powerful script-mage!\"${NC}"
                echo -e "You have chosen the ${CYAN}Path of the Programmer${NC}! (+25 XP)"
                break
                ;;
            "NO")
                echo -e "\n${BLUE}✨ The NO keyhole glows with silver light!${NC}"
                echo -e "\"WISE! You prefer to master the basics first!\""
                echo -e "\"Focus on commands, shortcuts, and data mastery.\""
                echo -e "\"The scripting arts will await when you're ready.\""
                echo -e "\n${YELLOW}\"You have chosen the steady path!\"${NC}"
                echo -e "You have chosen the ${CYAN}Path of the Data Master${NC}! (+25 XP)"
                break
                ;;
            *)
                echo -e "\n${RED}\"SPEAK CLEARLY! YES or NO only!\"${NC}"
                ;;
        esac
    done
    
    echo ""
    read -p "Press Enter for your reward..."
    clear
}

# Adventure Complete
adventure_complete() {
    echo -e "${BOLD}� Adventure Complete!${NC}"
    echo -e "${GREEN}Congratulations! You have completed the Trial of First Commands!${NC}\n"
    
    echo -e "${YELLOW}🎖️ You have earned:${NC}"
    echo -e "  • ${CYAN}STATUS Mastery${NC} - View system information"
    echo -e "  • ${CYAN}Memory Navigation${NC} - Access your data vault"
    echo -e "  • ${CYAN}Shortcode Magic${NC} - Cast powerful [COMMAND|ARGS] spells"
    echo -e "  • ${CYAN}Choice Wisdom${NC} - Understanding of your learning path"
    echo -e "  • ${CYAN}uCode Enlightenment${NC} - Witnessed Visual Basic-style magic"
    echo -e "  • ${BOLD}Total: 85 XP${NC} - You are now an ${GREEN}Accomplished Adventurer${NC}!"
    
    echo -e "\n${CYAN}Your spellbook now contains:${NC}"
    echo -e "  • ${YELLOW}STATUS${NC} - Show realm overview"
    echo -e "  • ${YELLOW}GO${NC} - Browse all available shortcuts"
    echo -e "  • ${YELLOW}HELP${NC} - Summon the wisdom scrolls"
    echo -e "  • ${YELLOW}MEM LIST${NC} - View your memory vault"
    echo -e "  • ${YELLOW}[PACK|LIST]${NC} - List magical packages"
    echo -e "  • ${YELLOW}TUTORIAL${NC} - Replay this epic adventure"
    echo -e "  • ${YELLOW}[DASH|LIVE]${NC} - Summon the living dashboard"
    
    echo -e "\n${BOLD}🌟 Ready for your next adventure?${NC}"
    echo -e "Type ${CYAN}GO${NC} anytime to see all available commands!"
    echo -e "Type ${CYAN}HELP${NC} for detailed documentation!"
    echo -e "Type ${CYAN}DASH${NC} for a live view of your realm!"
    
    echo ""
    read -p "Press Enter to begin your journey in the uDOS realm..."
    clear
}

# Show dashboard
show_dashboard() {
    log_header "uDOS v1.2 Live Dashboard"
    
    # System Status
    echo -e "${BOLD}📊 System Overview${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Memory stats
    local memory_files=$(find "$UMEMORY" -type f | wc -l)
    local memory_size=$(du -sh "$UMEMORY" 2>/dev/null | cut -f1)
    echo -e "${CYAN}🧠 Memory:${NC}        $memory_files files ($memory_size)"
    
    # Mission stats
    local missions=$(find "$UMEMORY" -name "*-mission.md" | wc -l)
    local active_missions=$(grep -l "Status.*Active" "$UMEMORY"/*-mission.md 2>/dev/null | wc -l)
    echo -e "${PURPLE}🎯 Missions:${NC}       $missions total ($active_missions active)"
    
    # Log stats
    local logs=$(find "$UMEMORY" -name "*-log-*.md" | wc -l)
    echo -e "${YELLOW}📝 Logs:${NC}          $logs entries"
    
    # Template stats
    local templates=$(find "$UTEMPLATE" -name "*.md" | wc -l)
    echo -e "${GREEN}📋 Templates:${NC}     $templates available"
    
    # System health
    echo ""
    echo -e "${BOLD}🔍 System Health${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check critical commands
    local health_status="✅"
    for cmd in jq grep find; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            health_status="⚠️"
            break
        fi
    done
    echo -e "${GREEN}System Tools:${NC}     $health_status All essential tools available"
    
    # Storage check
    local disk_usage=$(df "$UHOME" | tail -1 | awk '{print $5}')
    if [[ ${disk_usage%\%} -gt 90 ]]; then
        echo -e "${RED}Storage:${NC}          ⚠️  Disk usage: $disk_usage"
    else
        echo -e "${GREEN}Storage:${NC}          ✅ Disk usage: $disk_usage"
    fi
    
    # Recent activity
    echo ""
    echo -e "${BOLD}📈 Recent Activity${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Show last 5 modified files
    find "$UMEMORY" -type f -exec ls -lt {} + | head -5 | while read line; do
        local file=$(echo "$line" | awk '{print $NF}')
        local date=$(echo "$line" | awk '{print $6, $7, $8}')
        local filename=$(basename "$file")
        echo -e "${BLUE}•${NC} $filename ${CYAN}($date)${NC}"
    done
    
    echo ""
    echo -e "${BOLD}🎯 Quick Actions${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}•${NC} Type ${BOLD}MISSION create <name>${NC} to start a new mission"
    echo -e "${GREEN}•${NC} Type ${BOLD}MEMORY list${NC} to see all your files"
    echo -e "${GREEN}•${NC} Type ${BOLD}LOG report${NC} to generate activity report"
    echo ""
}

# Variable and dataget detection system
detect_variables() {
    local variables=()
    
    # Scan memory files for $variables
    if [[ -d "$UMEMORY" ]]; then
        while IFS= read -r var; do
            variables+=("$var")
        done < <(grep -ho '\$[A-Za-z_][A-Za-z0-9_]*' "$UMEMORY"/*.md 2>/dev/null | sort -u | head -20)
    fi
    
    # Scan template files for $variables
    if [[ -d "$UTEMPLATE" ]]; then
        while IFS= read -r var; do
            variables+=("$var")
        done < <(grep -ho '\$[A-Za-z_][A-Za-z0-9_]*' "$UTEMPLATE"/*.md 2>/dev/null | sort -u | head -20)
    fi
    
    # Return unique variables
    printf '%s\n' "${variables[@]}" | sort -u
}

# Enhanced dataget processing with variable prediction
process_dataget() {
    local input="$1"
    local variables=()
    
    # Detect available variables
    mapfile -t variables < <(detect_variables)
    
    # If input contains partial variable, suggest completions
    if [[ "$input" == *'$'* ]]; then
        local partial_var=$(echo "$input" | grep -o '\$[A-Za-z_]*$' | tail -1)
        if [[ -n "$partial_var" ]]; then
            echo -e "\n${CYAN}💡 Available Variables:${NC}"
            for var in "${variables[@]}"; do
                if [[ "$var" == "$partial_var"* ]]; then
                    echo -e "  ${YELLOW}$var${NC}"
                fi
            done
            echo ""
        fi
    fi
    
    # Process the input normally
    echo "$input"
}

# Intelligent input system with autocomplete and prediction
intelligent_input() {
    local prompt="${1:-${RAINBOW_CYAN}WHIRL${NC}> }"
    local input=""
    local suggestions=()
    local suggestion_index=0
    local cursor_pos=0
    
    # Build command database
    local commands=("HELP" "STATUS" "DASH" "RESIZE" "DESTROY" "SETUP" "EXIT" 
                   "MEMORY list" "MEMORY view" "MEMORY search"
                   "MISSION list" "MISSION create" "MISSION complete"
                   "LOG report" "LOG stats" "LOG move"
                   "PACKAGE list" "PACKAGE install" "PACKAGE info"
                   "DEV status" "DEV report")
    
    # Build shortcode database
    local shortcodes=("[MEM|LIST]" "[MEM|VIEW]" "[MEM|SEARCH]"
                     "[MISSION|LIST]" "[MISSION|CREATE]" "[MISSION|COMPLETE]"
                     "[LOG|REPORT]" "[LOG|STATS]" "[LOG|MOVE]"
                     "[PACK|LIST]" "[PACK|INSTALL]" "[PACK|INFO]"
                     "[DASH|LIVE]" "[DEV|STATUS]" "[DEV|REPORT]")
    
    # Get existing data for predictions
    local existing_missions=()
    local existing_files=()
    local existing_packages=("ripgrep" "fd" "bat" "glow" "micro" "jq")
    local existing_variables=()
    
    if [[ -d "$UMEMORY" ]]; then
        mapfile -t existing_missions < <(find "$UMEMORY" -name "*-mission.md" -exec basename {} .md \; | sed 's/^[0-9]*-//' | sed 's/-mission$//')
        mapfile -t existing_files < <(ls "$UMEMORY" 2>/dev/null | head -10)
    fi
    
    # Get available variables
    mapfile -t existing_variables < <(detect_variables)
    
    # Smart prediction based on input
    predict_input() {
        local current_input="$1"
        suggestions=()
        
        # If input starts with [, show shortcode options
        if [[ "$current_input" == "["* ]]; then
            for shortcode in "${shortcodes[@]}"; do
                if [[ "$shortcode" == "$current_input"* ]]; then
                    suggestions+=("$shortcode")
                fi
            done
        # Command prediction
        elif [[ -n "$current_input" ]]; then
            # Match commands
            for cmd in "${commands[@]}"; do
                if [[ "$cmd" == "$current_input"* ]] || [[ "${cmd,,}" == "${current_input,,}"* ]]; then
                    suggestions+=("$cmd")
                fi
            done
            
            # Context-aware suggestions
            case "$current_input" in
                *"view "*|*"view:")
                    for file in "${existing_files[@]}"; do
                        suggestions+=("${current_input%view*}view $file")
                    done
                    ;;
                *"complete "*|*"complete:")
                    for mission in "${existing_missions[@]}"; do
                        suggestions+=("${current_input%complete*}complete $mission")
                    done
                    ;;
                *"install "*|*"install:")
                    for pkg in "${existing_packages[@]}"; do
                        suggestions+=("${current_input%install*}install $pkg")
                    done
                    ;;
                *'$'*)
                    # Variable suggestions
                    local partial_var=$(echo "$current_input" | grep -o '\$[A-Za-z_]*$')
                    for var in "${existing_variables[@]}"; do
                        if [[ "$var" == "$partial_var"* ]]; then
                            suggestions+=("${current_input%\$*}$var")
                        fi
                    done
                    ;;
            esac
        else
            # Default suggestions when no input
            suggestions=("HELP" "STATUS" "DASH" "MEM LIST" "MISSION LIST" "[MEM|LIST]")
        fi
        
        # Limit suggestions
        if [[ ${#suggestions[@]} -gt 8 ]]; then
            suggestions=("${suggestions[@]:0:8}")
        fi
    }
    
    # Display suggestions
    show_suggestions() {
        if [[ ${#suggestions[@]} -gt 0 ]]; then
            echo -e "\n${CYAN}💡 Suggestions:${NC}"
            for i in "${!suggestions[@]}"; do
                if [[ $i -eq $suggestion_index ]]; then
                    echo -e "  ${YELLOW}▶ ${suggestions[$i]}${NC}"
                else
                    echo -e "  ${BLUE}  ${suggestions[$i]}${NC}"
                fi
            done
            echo ""
        fi
    }
    
    # Clear suggestions display
    clear_suggestions() {
        if [[ ${#suggestions[@]} -gt 0 ]]; then
            local lines_to_clear=$((${#suggestions[@]} + 2))
            for ((i=0; i<lines_to_clear; i++)); do
                echo -e "\033[A\033[K"
            done
        fi
    }
    
    echo -ne "$prompt"
    
    while true; do
        # Get current input and update predictions
        predict_input "$input"
        
        # Show suggestions if we have any
        if [[ ${#suggestions[@]} -gt 0 ]]; then
            show_suggestions
            echo -ne "$prompt$input"
        fi
        
        # Read single character
        read -rsn1 char
        
        case "$char" in
            # Enter key
            "")
                clear_suggestions
                if [[ ${#suggestions[@]} -gt 0 && -n "${suggestions[$suggestion_index]}" ]]; then
                    # Use selected suggestion
                    input="${suggestions[$suggestion_index]}"
                fi
                echo ""
                echo "$input"
                return 0
                ;;
            # Tab key - autocomplete with first suggestion
            $'\t')
                if [[ ${#suggestions[@]} -gt 0 ]]; then
                    clear_suggestions
                    input="${suggestions[0]}"
                    echo -ne "\r$prompt$input"
                fi
                ;;
            # Up arrow - previous suggestion
            $'\033')
                read -rsn2 -t 0.1 arrow_key
                case "$arrow_key" in
                    "[A") # Up arrow
                        if [[ ${#suggestions[@]} -gt 0 ]]; then
                            ((suggestion_index--))
                            if [[ $suggestion_index -lt 0 ]]; then
                                suggestion_index=$((${#suggestions[@]} - 1))
                            fi
                            clear_suggestions
                            echo -ne "\r$prompt$input"
                        fi
                        ;;
                    "[B") # Down arrow
                        if [[ ${#suggestions[@]} -gt 0 ]]; then
                            ((suggestion_index++))
                            if [[ $suggestion_index -ge ${#suggestions[@]} ]]; then
                                suggestion_index=0
                            fi
                            clear_suggestions
                            echo -ne "\r$prompt$input"
                        fi
                        ;;
                    "[C") # Right arrow - accept suggestion
                        if [[ ${#suggestions[@]} -gt 0 ]]; then
                            clear_suggestions
                            input="${suggestions[$suggestion_index]}"
                            echo -ne "\r$prompt$input"
                        fi
                        ;;
                esac
                ;;
            # Backspace
            $'\177'|$'\b')
                if [[ ${#input} -gt 0 ]]; then
                    clear_suggestions
                    input="${input%?}"
                    suggestion_index=0
                    echo -ne "\r$prompt$input\033[K"
                fi
                ;;
            # Ctrl+C
            $'\003')
                clear_suggestions
                echo ""
                return 130
                ;;
            # Regular character
            *)
                clear_suggestions
                input+="$char"
                suggestion_index=0
                echo -ne "\r$prompt$input"
                ;;
        esac
    done
}

# Enhanced shortcode browser
browse_shortcodes() {
    local category="${1:-all}"
    
    echo -e "\n${YELLOW}🔧 Shortcode Browser${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    case "$category" in
        memory|MEMORY)
            echo -e "${CYAN}🧠 MEMORY SHORTCUTS:${NC}"
            echo "  [MEM|LIST] - LIST ALL MEMORY FILES"
            echo "  [MEM|VIEW|FILE-YYYYMMDD-LOCATION-HHMMSS.md] - VIEW SPECIFIC FILE"
            echo "  [MEM|SEARCH|TERM] - SEARCH MEMORY"
            echo "  [MEM|EDIT|FILE-YYYYMMDD-LOCATION-HHMMSS.md] - EDIT MEMORY FILE"
            ;;
        mission|MISSION)
            echo -e "${PURPLE}🎯 MISSION SHORTCUTS:${NC}"
            echo "  [MISSION|LIST] - LIST ALL MISSIONS"
            echo "  [MISSION|CREATE|NAME] - CREATE NEW MISSION"
            echo "  [MISSION|COMPLETE|NAME] - COMPLETE MISSION"
            echo "  [MISSION|EDIT|NAME] - EDIT EXISTING MISSION"
            ;;
        package|PACKAGE)
            echo -e "${GREEN}📦 PACKAGE SHORTCUTS:${NC}"
            echo "  [PACK|LIST] - SHOW AVAILABLE PACKAGES"
            echo "  [PACK|INSTALL|NAME] - INSTALL PACKAGE"
            echo "  [PACK|INFO|NAME] - PACKAGE INFORMATION"
            ;;
        log|LOG)
            echo -e "${YELLOW}📝 LOGGING SHORTCUTS:${NC}"
            echo "  [LOG|REPORT] - GENERATE DAILY REPORT"
            echo "  [LOG|STATS] - SHOW STATISTICS"
            echo "  [LOG|MOVE|COMMAND] - LOG A COMMAND"
            ;;
        dash|DASH)
            echo -e "${BLUE}📊 DASHBOARD SHORTCUTS:${NC}"
            echo "  [DASH|LIVE] - LIVE DASHBOARD MODE"
            ;;
        editor|EDITOR)
            echo -e "${RAINBOW_GREEN}📝 MICRO EDITOR INTEGRATION:${NC}"
            echo "  [EDIT|MARKDOWN|FILE-YYYYMMDD-LOCATION-HHMMSS.md] - OPEN MARKDOWN IN MICRO"
            echo "  [EDIT|USCRIPT|FILE-YYYYMMDD-LOCATION-HHMMSS.us] - OPEN USCRIPT IN MICRO"
            echo "  [EDIT|CONFIG] - EDIT MICRO CONFIGURATION"
            echo "  [NEW|MARKDOWN] - CREATE NEW MARKDOWN FILE"
            echo "  [NEW|USCRIPT] - CREATE NEW USCRIPT FILE"
            echo ""
            echo -e "${RAINBOW_GREEN}🌐 TYPO WEB EDITOR:${NC}"
            echo "  [TYPO|EDIT|file.md] - EDIT MARKDOWN IN WEB BROWSER"
            echo "  [TYPO|SERVER] - START TYPO DEVELOPMENT SERVER"
            echo "  [TYPO|NEW|filename] - CREATE NEW FILE IN TYPO"
            echo ""
            echo -e "${RAINBOW_GREEN}� ASCII ART GENERATION:${NC}"
            echo "  [ASCII|TEXT|Hello World] - GENERATE ASCII TEXT"
            echo "  [ASCII|LOGO|uDOS] - GENERATE SYSTEM LOGO"
            echo "  [ASCII|BANNER|Title|Subtitle] - GENERATE BANNER"
            echo "  [ASCII|IMAGE|path/to/image.jpg] - CONVERT IMAGE TO ASCII"
            echo ""
            echo -e "${RAINBOW_GREEN}�🎛️ MODE SWITCHING:${NC}"
            echo "  MODE MARKDOWN - SWITCH TO MARKDOWN MODE (micro integration)"
            echo "  MODE USCRIPT - SWITCH TO USCRIPT MODE (micro integration)"
            echo "  MODE COMMAND - RETURN TO NATIVE uCODE MODE"
            ;;
        games|GAMES)
            echo -e "${RAINBOW_PURPLE}🎮 CLASSIC GAMES:${NC}"
            echo "  [NETHACK|PLAY] - START NETHACK ADVENTURE"
            echo "  [NETHACK|CONTINUE] - RESUME SAVED GAME"
            echo "  [NETHACK|SCORES] - VIEW HIGH SCORES"
            echo "  [NETHACK|HELP] - GAME TUTORIAL AND CONTROLS"
            ;;
        all|*)
            echo -e "${BOLD}📋 All Available Shortcodes:${NC}"
            echo ""
            browse_shortcodes "memory"
            echo ""
            browse_shortcodes "mission"
            echo ""
            browse_shortcodes "package"
            echo ""
            browse_shortcodes "log"
            echo ""
            browse_shortcodes "dash"
            echo ""
            browse_shortcodes "editor"
            echo ""
            browse_shortcodes "games"
            ;;
    esac
    
    echo ""
    echo -e "${CYAN}💡 Tips:${NC}"
    echo "  • Type [ to see shortcode suggestions"
    echo "  • Use Tab to autocomplete"
    echo "  • Use arrow keys to navigate suggestions"
    echo "  • Type GO editor to see editor commands"
    echo "  • Type MODE TYPE to switch editing modes"
    echo ""
}

# Editor Integration Functions
start_markdown_editor() {
    local filename="${1:-new-document.md}"
    local filepath="$UMEMORY/$filename"
    
    set_mode_with_layout "MARKDOWN" "$filepath" "$(basename "$filename")"
    
    echo -e "\n${RAINBOW_GREEN}📝 Micro Editor - Markdown Mode${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}File:${NC} $filename"
    echo -e "${CYAN}Path:${NC} $filepath"
    echo -e "${CYAN}Mode:${NC} Markdown with syntax highlighting"
    echo ""
    
    if [[ ! -f "$filepath" ]]; then
        echo -e "${BLUE}� Creating new markdown file...${NC}"
        mkdir -p "$(dirname "$filepath")"
        cat > "$filepath" << 'EOF'
# New Document

**Created**: {{DATE}}  
**Author**: {{USER_NAME}}  
**Mission**: {{MISSION_NAME}}

---

## Content

Write your markdown content here...

### Features Available
- Full markdown syntax support
- uDOS shortcode integration: [COMMAND|ARGS]
- Smart input templates: {{VARIABLE}}
- ASCII art components from gallery

---

*Document created with uDOS Micro Editor*
EOF
    fi
    
    echo -e "${CYAN}� Launching micro editor...${NC}"
    echo -e "${YELLOW}�💡 Micro Editor Tips:${NC}"
    echo "  • Ctrl+S to save"
    echo "  • Ctrl+Q to quit"
    echo "  • Ctrl+G for help"
    echo "  • Syntax highlighting enabled for Markdown"
    echo ""
    echo -e "${GREEN}Press any key to open $filename in micro...${NC}"
    read -n 1
    
    # Launch micro with markdown syntax highlighting
    micro "$filepath"
    
    # Return to uDOS with status
    echo -e "\n${GREEN}✅ Returned from micro editor${NC}"
    echo -e "${CYAN}File saved:${NC} $filepath"
}

start_uscript_editor() {
    local filename="${1:-new-script.us}"
    local filepath="$UHOME/uScript/$filename"
    
    set_mode_with_layout "USCRIPT" "$filepath" "script"
    
    echo -e "\n${RAINBOW_PURPLE}⚡ Micro Editor - uScript Mode${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}File:${NC} $filename"
    echo -e "${CYAN}Path:${NC} $filepath"
    echo -e "${CYAN}Mode:${NC} uScript with bash syntax highlighting"
    echo ""
    
    # Ensure uScript directory exists
    mkdir -p "$UHOME/uScript"
    
    if [[ ! -f "$filepath" ]]; then
        echo -e "${BLUE}⚡ Creating new uScript file...${NC}"
        cat > "$filepath" << 'EOF'
#!/bin/bash
# uScript - Native uDOS Script Language
# Created: {{DATE}}
# Author: {{USER_NAME}}
# Mission: {{MISSION_NAME}}

# ═══════════════════════════════════════════════════════════════
# uScript integrates seamlessly with uCODE command language
# ═══════════════════════════════════════════════════════════════

# Initialize uDOS environment
source "$UHOME/uCode/ucode.sh"

# uCODE Commands (native uDOS language)
echo "🌀 uScript execution started..."

# Memory operations (uCODE style)
# [MEM|LIST] - equivalent to: handle_memory "list"
# [MISSION|CREATE|"Script Task"] - equivalent to: handle_mission "create Script Task"

# Native bash with uDOS functions
log_info "uScript running in native uCODE environment"

# Your script logic here
echo "Hello from uScript - the native uDOS scripting language!"

# Smart input integration
# {{INPUT:task_name|text|Enter task name|Default Task|required}}

# Template processing
# TEMPLATE PROCESS status-report.md output.md

# Dashboard integration
# [DASH|LIVE]

echo "✅ uScript execution completed"
EOF
        chmod +x "$filepath"
    fi
    
    echo -e "${CYAN}� Launching micro editor...${NC}"
    echo -e "${YELLOW}💡 Micro Editor Tips:${NC}"
    echo "  • Ctrl+S to save"
    echo "  • Ctrl+Q to quit"
    echo "  • Ctrl+G for help"
    echo "  • Ctrl+T to run script from editor"
    echo "  • Syntax highlighting enabled for bash/uScript"
    echo ""
    echo -e "${GREEN}Press any key to open $filename in micro...${NC}"
    read -n 1
    
    # Launch micro with shell syntax highlighting
    micro "$filepath"
    
    # Return to uDOS with status
    echo -e "\n${GREEN}✅ Returned from micro editor${NC}"
    echo -e "${CYAN}File saved:${NC} $filepath"
    
    # Offer to run the script
    echo ""
    echo -e "${YELLOW}Would you like to run this uScript? [y/N]:${NC}"
    read -n 1 run_choice
    echo ""
    if [[ "$run_choice" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🚀 Executing uScript...${NC}"
        bash "$filepath"
    fi
}

start_shortcode_builder() {
    set_mode "SHORTCODE" ""
    
    echo -e "\n${RAINBOW_YELLOW}🔧 Interactive Shortcode Builder${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${CYAN}🎯 Choose Construction Method:${NC}"
    echo "  ${YELLOW}1.${NC} Quick Templates - Use pre-built shortcodes"
    echo "  ${YELLOW}2.${NC} Step-by-Step Builder - Construct custom shortcodes"
    echo "  ${YELLOW}3.${NC} Browse Categories - Explore by function"
    echo "  ${YELLOW}4.${NC} Recent History - Reuse recent commands"
    echo ""
    echo -e "${CYAN}💡 Shortcode Builder Commands:${NC}"
    echo "  • Choose method by number (1-4)"
    echo "  • ':preview [shortcode]' to test shortcode"
    echo "  • ':save [shortcode]' to add to favorites"
    echo "  • ':exit' to return to command mode"
    echo ""
}

# Visual shortcode construction wizard
start_visual_builder() {
    echo -e "\n${RAINBOW_YELLOW}🛠️  Visual Shortcode Constructor${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${CYAN}Step 1: Select Command Category${NC}"
    echo "  ${YELLOW}1.${NC} 🧠 MEMORY - File operations (list, view, edit, search)"
    echo "  ${YELLOW}2.${NC} 🎯 MISSION - Project management (create, list, complete)"
    echo "  ${YELLOW}3.${NC} 📦 PACKAGE - Software management (install, list, info)"
    echo "  ${YELLOW}4.${NC} 📝 LOG - Logging operations (report, stats, move)"
    echo "  ${YELLOW}5.${NC} 📊 DASH - Dashboard (live view)"
    echo "  ${YELLOW}6.${NC} 📝 EDIT - Editor operations (markdown, uscript)"
    echo ""
    echo -ne "${CYAN}Choose category [1-6]: ${NC}"
}

build_shortcode_step_by_step() {
    local category="$1"
    local subcategory=""
    local parameters=""
    local built_shortcode=""
    
    case "$category" in
        1|memory|MEMORY)
            echo -e "\n${CYAN}🧠 MEMORY Operations${NC}"
            echo "  ${YELLOW}1.${NC} list - Show all memory files"
            echo "  ${YELLOW}2.${NC} view - Display specific file contents"
            echo "  ${YELLOW}3.${NC} edit - Open file for editing"
            echo "  ${YELLOW}4.${NC} search - Find text in memory files"
            echo -ne "${CYAN}Choose operation [1-4]: ${NC}"
            read -r subchoice
            
            case "$subchoice" in
                1|list) built_shortcode="[MEM|LIST]" ;;
                2|view) 
                    echo -ne "${CYAN}Enter filename: ${NC}"
                    read -r filename
                    built_shortcode="[MEM|VIEW|$filename]"
                    ;;
                3|edit)
                    echo -ne "${CYAN}Enter filename: ${NC}"
                    read -r filename
                    built_shortcode="[MEM|EDIT|$filename]"
                    ;;
                4|search)
                    echo -ne "${CYAN}Enter search term: ${NC}"
                    read -r term
                    built_shortcode="[MEM|SEARCH|$term]"
                    ;;
            esac
            ;;
        2|mission|MISSION)
            echo -e "\n${CYAN}🎯 MISSION Operations${NC}"
            echo "  ${YELLOW}1.${NC} list - Show all missions"
            echo "  ${YELLOW}2.${NC} create - Start new mission"
            echo "  ${YELLOW}3.${NC} complete - Finish existing mission"
            echo -ne "${CYAN}Choose operation [1-3]: ${NC}"
            read -r subchoice
            
            case "$subchoice" in
                1|list) built_shortcode="[MISSION|LIST]" ;;
                2|create)
                    echo -ne "${CYAN}Enter mission name: ${NC}"
                    read -r name
                    built_shortcode="[MISSION|CREATE|$name]"
                    ;;
                3|complete)
                    echo -ne "${CYAN}Enter mission name: ${NC}"
                    read -r name
                    built_shortcode="[MISSION|COMPLETE|$name]"
                    ;;
            esac
            ;;
        3|package|PACKAGE)
            echo -e "\n${CYAN}📦 PACKAGE Operations${NC}"
            echo "  ${YELLOW}1.${NC} list - Show available packages"
            echo "  ${YELLOW}2.${NC} install - Install a package"
            echo "  ${YELLOW}3.${NC} info - Get package information"
            echo -ne "${CYAN}Choose operation [1-3]: ${NC}"
            read -r subchoice
            
            case "$subchoice" in
                1|list) built_shortcode="[PACKAGE:list]" ;;
                2|install)
                    echo -e "\n${CYAN}Popular packages:${NC} ripgrep, fd, bat, glow, micro, jq"
                    echo -ne "${CYAN}Enter package name: ${NC}"
                    read -r pkg
                    built_shortcode="[PACKAGE:install:$pkg]"
                    ;;
                3|info)
                    echo -ne "${CYAN}Enter package name: ${NC}"
                    read -r pkg
                    built_shortcode="[PACKAGE:info:$pkg]"
                    ;;
            esac
            ;;
        6|edit|EDIT)
            echo -e "\n${CYAN}📝 EDITOR Operations${NC}"
            echo "  ${YELLOW}1.${NC} markdown - Open markdown editor"
            echo "  ${YELLOW}2.${NC} uscript - Open uScript editor"
            echo "  ${YELLOW}3.${NC} shortcode - Open shortcode builder"
            echo -ne "${CYAN}Choose editor [1-3]: ${NC}"
            read -r subchoice
            
            case "$subchoice" in
                1|markdown)
                    echo -ne "${CYAN}Enter filename (optional): ${NC}"
                    read -r filename
                    if [[ -n "$filename" ]]; then
                        built_shortcode="[EDIT|MARKDOWN|$filename]"
                    else
                        built_shortcode="[EDIT|MARKDOWN|new-document.md]"
                    fi
                    ;;
                2|uscript)
                    echo -ne "${CYAN}Enter filename (optional): ${NC}"
                    read -r filename
                    if [[ -n "$filename" ]]; then
                        built_shortcode="[EDIT|USCRIPT|$filename]"
                    else
                        built_shortcode="[EDIT|USCRIPT|new-script.us]"
                    fi
                    ;;
                3|shortcode)
                    built_shortcode="[EDIT|SHORTCODE]"
                    ;;
            esac
            ;;
    esac
    
    if [[ -n "$built_shortcode" ]]; then
        echo ""
        echo -e "${GREEN}✅ Shortcode Built:${NC} ${BOLD}$built_shortcode${NC}"
        echo ""
        echo -e "${CYAN}Options:${NC}"
        echo "  ${YELLOW}1.${NC} Execute now"
        echo "  ${YELLOW}2.${NC} Preview (test without execution)"
        echo "  ${YELLOW}3.${NC} Save to favorites"
        echo "  ${YELLOW}4.${NC} Copy to clipboard"
        echo "  ${YELLOW}5.${NC} Build another"
        echo -ne "${CYAN}Choose action [1-5]: ${NC}"
        read -r action
        
        case "$action" in
            1) 
                echo -e "\n${YELLOW}🚀 Executing Shortcode...${NC}"
                process_shortcode "$built_shortcode"
                ;;
            2)
                echo -e "\n${YELLOW}🔍 Preview Mode:${NC}"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo "Shortcode: $built_shortcode"
                echo "This would execute: $(describe_shortcode "$built_shortcode")"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                ;;
            3)
                add_to_favorites "$built_shortcode"
                log_success "Added to favorites: $built_shortcode"
                ;;
            4)
                echo "$built_shortcode" | pbcopy 2>/dev/null || echo "$built_shortcode"
                log_success "Copied to clipboard: $built_shortcode"
                ;;
            5)
                start_visual_builder
                ;;
        esac
    fi
}

# Quick template selector
show_quick_templates() {
    echo -e "\n${CYAN}⚡ Quick Templates${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${YELLOW}FREQUENTLY USED:${NC}"
    echo "  ${BLUE}1.${NC} [MEMORY|LIST] - SHOW ALL FILES"
    echo "  ${BLUE}2.${NC} [MISSION|LIST] - SHOW ALL MISSIONS"
    echo "  ${BLUE}3.${NC} [DASH|LIVE] - LIVE DASHBOARD"
    echo "  ${BLUE}4.${NC} [PACKAGE|LIST] - SHOW PACKAGES"
    echo ""
    echo -e "${YELLOW}FILE OPERATIONS:${NC}"
    echo "  ${BLUE}5.${NC} [MEMORY|VIEW|FILENAME] - VIEW FILE TEMPLATE"
    echo "  ${BLUE}6.${NC} [MEMORY|EDIT|FILENAME] - EDIT FILE TEMPLATE"
    echo "  ${BLUE}7.${NC} [EDIT|MARKDOWN|FILENAME] - NEW MARKDOWN"
    echo ""
    echo -e "${YELLOW}PROJECT MANAGEMENT:${NC}"
    echo "  ${BLUE}8.${NC} [MISSION|CREATE|NAME] - NEW MISSION TEMPLATE"
    echo "  ${BLUE}9.${NC} [MISSION|COMPLETE|NAME] - COMPLETE MISSION TEMPLATE"
    echo ""
    echo -ne "${CYAN}Select template [1-9] or 'custom' for builder: ${NC}"
}

# Describe what a shortcode does
describe_shortcode() {
    local shortcode="$1"
    
    case "$shortcode" in
        "[MEM|LIST]") echo "LIST ALL FILES IN MEMORY" ;;
        "[MEM|VIEW|"*) echo "DISPLAY CONTENTS OF FILE: ${shortcode#*|*|}" ;;
        "[MEM|EDIT|"*) echo "OPEN FILE FOR EDITING: ${shortcode#*|*|}" ;;
        "[MISSION|LIST]") echo "SHOW ALL MISSIONS" ;;
        "[MISSION|CREATE|"*) echo "CREATE NEW MISSION: ${shortcode#*|*|}" ;;
        "[DASH|LIVE]") echo "START LIVE DASHBOARD" ;;
        "[PACK|LIST]") echo "SHOW AVAILABLE PACKAGES" ;;
        *) echo "Execute shortcode: $shortcode" ;;
    esac
}

# Favorites management
add_to_favorites() {
    local shortcode="$1"
    echo "$shortcode" >> "$FAVORITES_FILE"
}

show_favorites() {
    echo -e "\n${CYAN}⭐ Favorite Commands${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ -f "$FAVORITES_FILE" && -s "$FAVORITES_FILE" ]]; then
        local count=1
        while IFS= read -r fav; do
            echo -e "${BLUE}$count.${NC} $fav"
            ((count++))
        done < "$FAVORITES_FILE"
    else
        echo -e "${YELLOW}No favorite commands yet${NC}"
        echo -e "${CYAN}💡 Use ':save [shortcode]' to add favorites${NC}"
    fi
    echo ""
}

# Process editor-specific input
process_editor_input() {
    local input="$1"
    
    case "$CURRENT_MODE" in
        MARKDOWN)
            process_markdown_input "$input"
            ;;
        USCRIPT)
            process_uscript_input "$input"
            ;;
        SHORTCODE)
            process_shortcode_input "$input"
            ;;
        *)
            return 1
            ;;
    esac
}

process_markdown_input() {
    local input="$1"
    
    case "$input" in
        ":save")
            if [[ -n "$CURRENT_FILE" ]]; then
                log_success "Saved: $(basename "$CURRENT_FILE")"
            else
                log_error "No file to save"
            fi
            ;;
        ":preview")
            if [[ -n "$CURRENT_FILE" && -f "$CURRENT_FILE" ]]; then
                echo -e "\n${YELLOW}📖 Markdown Preview:${NC}"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                # Simple markdown preview (could be enhanced with a proper renderer)
                cat "$CURRENT_FILE"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            fi
            ;;
        ":exit")
            set_mode "COMMAND" ""
            log_info "Returned to command mode"
            ;;
        ":uscript")
            start_uscript_editor
            ;;
        *)
            # Regular content input - would append to file in full implementation
            echo -e "${GREEN}📝${NC} $input"
            if [[ -n "$CURRENT_FILE" ]]; then
                echo "$input" >> "$CURRENT_FILE"
            fi
            ;;
    esac
}

process_uscript_input() {
    local input="$1"
    
    case "$input" in
        ":save")
            if [[ -n "$CURRENT_FILE" ]]; then
                chmod +x "$CURRENT_FILE"
                log_success "Saved and made executable: $(basename "$CURRENT_FILE")"
            else
                log_error "No script to save"
            fi
            ;;
        ":run")
            if [[ -n "$CURRENT_FILE" && -f "$CURRENT_FILE" ]]; then
                echo -e "\n${YELLOW}⚡ Running Script:${NC}"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                bash "$CURRENT_FILE"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            fi
            ;;
        ":exit")
            set_mode "COMMAND" ""
            log_info "Returned to command mode"
            ;;
        ":markdown")
            start_markdown_editor
            ;;
        *)
            # Regular script input - would append to file in full implementation
            echo -e "${PURPLE}⚡${NC} $input"
            if [[ -n "$CURRENT_FILE" ]]; then
                echo "$input" >> "$CURRENT_FILE"
            fi
            ;;
    esac
}

process_shortcode_input() {
    local input="$1"
    
    case "$input" in
        ":exit")
            set_mode "COMMAND" ""
            log_info "Returned to command mode"
            ;;
        ":preview"*)
            local shortcode=$(echo "$input" | cut -d' ' -f2-)
            if [[ -n "$shortcode" ]]; then
                echo -e "\n${YELLOW}🔍 Shortcode Preview:${NC}"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo "Description: $(describe_shortcode "$shortcode")"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            fi
            ;;
        ":save"*)
            local shortcode=$(echo "$input" | cut -d' ' -f2-)
            if [[ -n "$shortcode" ]]; then
                add_to_favorites "$shortcode"
                log_success "Saved to favorites: $shortcode"
            fi
            ;;
        ":favorites"|":fav")
            show_favorites
            ;;
        1)
            show_quick_templates
            ;;
        2)
            start_visual_builder
            ;;
        3)
            browse_shortcodes
            ;;
        4)
            show_command_history
            ;;
        [1-9])
            # Handle quick template selection
            case "$input" in
                1) process_shortcode "[MEM|LIST]" ;;
                2) process_shortcode "[MISSION|LIST]" ;;
                3) process_shortcode "[DASH|LIVE]" ;;
                4) process_shortcode "[PACK|LIST]" ;;
                5) 
                    echo -ne "${CYAN}Enter filename: ${NC}"
                    read -r filename
                    process_shortcode "[MEM|VIEW|$filename]"
                    ;;
                6)
                    echo -ne "${CYAN}Enter filename: ${NC}"
                    read -r filename
                    process_shortcode "[MEM|EDIT|$filename]"
                    ;;
                7)
                    echo -ne "${CYAN}Enter filename: ${NC}"
                    read -r filename
                    process_shortcode "[EDIT|MARKDOWN|$filename]"
                    ;;
                8)
                    echo -ne "${CYAN}Enter mission name: ${NC}"
                    read -r name
                    process_shortcode "[MISSION|CREATE|$name]"
                    ;;
                9)
                    echo -ne "${CYAN}Enter mission name: ${NC}"
                    read -r name
                    process_shortcode "[MISSION|COMPLETE|$name]"
                    ;;
            esac
            ;;
        "custom")
            start_visual_builder
            ;;
        "builder")
            build_shortcode_step_by_step
            ;;
        *)
            # Check if input is a category for visual builder
            if [[ "$input" =~ ^[1-6]$ ]]; then
                build_shortcode_step_by_step "$input"
            else
                log_info "Building shortcode... (choose 1-4 or type command)"
                echo -e "${CYAN}💡 Try: 1 (templates), 2 (builder), 3 (browse), 4 (history)${NC}"
            fi
            ;;
    esac
}

# WHIRL prompt with intelligent input
show_whirl_prompt() {
    intelligent_input "${RAINBOW_CYAN}WHIRL${NC}> "
}
# Show status
show_status() {
    log_header "uDOS v1.2 System Status"
    
    echo "📍 Location: $UHOME"
    echo "🧠 Memory: Flat structure ($(find "$UMEMORY" -type f | wc -l) files)"
    echo "📋 Missions: $(find "$UMEMORY" -name "*-mission.md" | wc -l)"
    echo "📊 Logs: $(find "$UMEMORY" -name "*-log-*.md" | wc -l)"
    echo "🎯 Version: $VERSION"
    
    if [[ -f "$UMEMORY/identity.md" ]]; then
        local user=$(grep -E '\*\*Name\*\*:|\*\*Name:\*\*|Name:' "$UMEMORY/identity.md" | cut -d':' -f2 | xargs)
        local role=$(grep -E '\*\*Role\*\*:|\*\*Role:\*\*|Role:' "$UMEMORY/identity.md" | cut -d':' -f2 | xargs)
        echo "👤 User: $user ($role)"
    fi
    
    echo ""
}

# Show help
show_help() {
    log_header "uDOS v1.2 command reference"
    
    echo "## CORE COMMANDS"
    format_text "- HELP - Show this help"
    format_text "- STATUS - System status and stats"  
    format_text "- DASH - Live dashboard with real-time stats"
    format_text "- SIZE - Terminal size optimizer with intelligent recommendations"
    format_text "- GO - Browse available shortcodes and smart input features"
    format_text "- DESTROY - Reset system requires confirmation"
    format_text "- SETUP - Run first-time setup"
    format_text "- RESTART - Restart uDOS session (aliases: REBOOT, RELOAD)"
    format_text "- RESET - Refresh interface (aliases: REFRESH)"
    format_text "- EXIT - Exit uDOS (aliases: QUIT, BYE)"
    echo ""
    
    echo "## Advanced input intelligence"
    format_text "- HISTORY - Show command history"
    format_text "- HISTORY SEARCH TERM - Search command history"
    format_text "- HISTORY CLEAR - Clear command history"
    format_text "- !NUMBER - Execute command from history by number"
    format_text "- FAVORITES - Show favorite commands"
    echo ""
    
    echo "## Editor integration commands"
    format_text "- MODE TYPE - Switch editing mode command|markdown|uscript|shortcode"
    format_text "- EDIT MARKDOWN FILE-YYYYMMDD-LOCATION-HHMMSS.md - Open markdown editor"
    format_text "- EDIT USCRIPT FILE-YYYYMMDD-LOCATION-HHMMSS.us - Open uScript editor"
    format_text "- EDIT SHORTCODE - Open interactive shortcode builder"
    echo ""
    
    echo "## Memory commands (alias MEM)"
    format_text "- MEM LIST - Show all memory files"
    format_text "- MEM VIEW FILE-YYYYMMDD-LOCATION-HHMMSS.md - View memory file"
    format_text "- MEM EDIT FILE-YYYYMMDD-LOCATION-HHMMSS.md - Edit memory file"
    format_text "- MEM SEARCH TERM - Search memory"
    echo ""
    
    echo "## Mission commands"
    format_text "- MISSION LIST - Show missions"
    format_text "- MISSION CREATE NAME - Create new mission"
    format_text "- MISSION COMPLETE NAME - Complete mission"
    echo ""
    
    echo "## Logging commands"
    format_text "- LOG REPORT - Generate daily report"
    format_text "- LOG STATS - Show statistics"
    format_text "- LOG MOVE COMMAND - Log a command"
    echo ""
    
    echo "## Package commands (alias PACK)"
    format_text "- PACK LIST - Show available packages"
    format_text "- PACK INSTALL NAME - Install package"
    format_text "- PACK INFO NAME - Package information"
    echo ""
    
    echo "## Development commands"
    format_text "- DEV - Development tools and testing"
    format_text "- VALIDATE - Validate system integrity"
    format_text "- DEBUG - Debug mode toggle"
    echo ""
    
    echo "## Responsive layout commands"
    format_text "- LAYOUT - Show layout manager and current status"
    format_text "- LAYOUT PRESET - Switch to layout preset (options: COMPACT|STANDARD|WIDE|CODING|WRITING|DASHBOARD|AUTO)"
    format_text "- LAYOUT INFO - Show current layout information"
    format_text "- LAYOUT AUTO ON/OFF - Enable/disable auto-detection"
    format_text "- LAYOUT RESET - Reset to optimal layout for current mode"
    format_text "- LAYOUT SUGGEST - Get layout suggestions for current task"
    format_text "- LAYOUT PRESETS - List all available layout presets"
    echo ""
    
    echo "## Panel display system"
    format_text "- PANEL - Show ASCII panel dashboard with real-time data"
    format_text "- PANEL DASH STYLE - Dashboard styles (options: COMPACT|STANDARD|WIDE|TALL)"
    format_text "- PANEL GRID - Custom grid layout system"
    format_text "- PANEL MEMORY - Memory statistics panel"
    format_text "- PANEL MISSION - Mission tracking panel"
    format_text "- PANEL DATA - Numerical data display with metrics"
    format_text "- PANEL STATUS - System status panel"
    format_text "- PANEL CHAR - Acorn-inspired character font editor"
    echo ""
    
    echo "## Character font system"
    format_text "- CHAR - Acorn BBC Micro inspired character editor"
    format_text "- Font styles: MONO|CONDENSED|EXPANDED"
    format_text "- Character sets: BASIC|EXTENDED|UNICODE"
    format_text "- Data constraints: strings ≤40 chars, panels ≤15 lines"
    echo ""
    
    echo "## Shortcode format"
    format_text "- [COMMAND|ARGS] - Process shortcode"
    format_text "- [MEM|EDIT|FILE-YYYYMMDD-LOCATION-HHMMSS.md] - Edit memory file"
    format_text "- [EDIT|MARKDOWN|FILE-YYYYMMDD-LOCATION-HHMMSS.md] - Open markdown editor"
    format_text "- [EDIT|USCRIPT|FILE-YYYYMMDD-LOCATION-HHMMSS.us] - Open uScript editor"
    format_text "- [EDIT|SHORTCODE] - Interactive shortcode builder"
    format_text "- [MISSION|CREATE|NAME] - Create mission"
    format_text "- [PACK|INSTALL|NAME] - Install package"
    format_text "- [DASH|LIVE] - Live dashboard mode"
    echo ""
    
    echo "## Editor mode commands when in editor mode"
    format_text "- \\SAVE - Save current file"
    format_text "- \\EXIT - Return to command mode"
    format_text "- \\VIEW - View render content"
    format_text "- \\RUN - Execute script uScript mode"
    echo ""
}

# DESTROY command - complete system reset
handle_destroy() {
    log_header "🧹 DESTROY - Complete System Reset"
    log_warning "This will PERMANENTLY DELETE all uDOS data!"
    echo ""
    echo -e "${RED}This action will remove:${NC}"
    echo -e "${RED}• All memory files${NC}"
    echo -e "${RED}• All missions and logs${NC}"
    echo -e "${RED}• User identity and settings${NC}"
    echo -e "${RED}• All personal data${NC}"
    echo ""
    echo -ne "${BOLD}${RED}Type 'CONFIRM DESTROY' to proceed: ${NC}"
    read -r confirmation
    
    if [[ "$confirmation" == "CONFIRM DESTROY" ]]; then
        log_info "Initiating system destruction..."
        
        # Remove user data
        rm -rf "$UMEMORY"
        rm -rf "$UDEV"
        
        # Clear any cached data
        rm -rf "$UHOME/.cache" 2>/dev/null
        
        log_success "System destroyed successfully"
        log_info "Restarting fresh setup..."
        
        # Force fresh setup
        init_directories
        setup_user
    else
        log_info "Destruction cancelled"
    fi
}

# Process shortcode
process_shortcode() {
    local shortcode="$1"
    
    # Extract command and args from [COMMAND|ARGS] format
    local cmd=$(echo "$shortcode" | sed -E 's/^\[([^|]+)\|.*\]$/\1/')
    local args=$(echo "$shortcode" | sed -E 's/^\[[^|]+\|(.*)\]$/\1/')
    
    # Handle single command format [COMMAND]
    if [[ "$shortcode" =~ ^\[[^|]+\]$ ]]; then
        cmd=$(echo "$shortcode" | sed -E 's/^\[([^]]+)\]$/\1/')
        args=""
    fi
    
    case "$cmd" in
        MEMORY|MEM)
            handle_memory "$args"
            ;;
        MISSION)
            handle_mission "$args"
            ;;
        PACKAGE|PACK)
            handle_package "$args"
            ;;
        LOG)
            handle_log "$args"
            ;;
        DASH)
            handle_dash "$args"
            ;;
        DEV)
            handle_dev "$args"
            ;;
        EDIT)
            handle_edit "$args"
            ;;
        PANEL)
            handle_panel_command "$args"
            ;;
        LAYOUT)
            handle_layout_command "$args"
            ;;
        *)
            log_error "Unknown shortcode command: $cmd"
            ;;
    esac
}

# Handle edit commands
handle_edit() {
    local subcmd="$1"
    local editor_type=$(echo "$subcmd" | cut -d':' -f1)
    local filename=$(echo "$subcmd" | cut -d':' -f2)
    
    case "$editor_type" in
        markdown)
            start_markdown_editor "$filename"
            ;;
        uscript)
            start_uscript_editor "$filename"
            ;;
        shortcode)
            start_shortcode_builder
            ;;
        *)
            log_error "Unknown editor type: $editor_type"
            ;;
    esac
}

# Handle dash commands
handle_dash() {
    local subcmd="$1"
    
    case "$subcmd" in
        LIVE)
            log_info "Starting live dashboard..."
            while true; do
                clear
                show_dashboard
                echo ""
                echo -e "${CYAN}Press Ctrl+C to exit live mode${NC}"
                sleep 5
            done
            ;;
        *)
            show_dashboard
            ;;
    esac
}

# Handle memory commands
        handle_memory() {
    local subcmd="$1"
    
    case "$subcmd" in
        LIST)
            log_info "Memory files:"
            ls -la "$UMEMORY" | grep -v "^total"
            ;;
        VIEW|*)
            local file=$(echo "$subcmd" | cut -d'|' -f2)
            if [[ -f "$UMEMORY/$file" ]]; then
                cat "$UMEMORY/$file"
            else
                log_error "File not found: $file"
            fi
            ;;
        EDIT|*)
            local file=$(echo "$subcmd" | cut -d'|' -f2)
            if [[ "$file" == *.md ]]; then
                start_markdown_editor "$file"
            else
                log_warning "File type not supported for editing: $file"
            fi
            ;;
        SEARCH|*)
            local term=$(echo "$subcmd" | cut -d'|' -f2)
            log_info "Searching for: $term"
            grep -r "$term" "$UMEMORY" || log_warning "No matches found"
            ;;
        *)
            log_error "Unknown memory command: $subcmd"
            ;;
    esac
}

# Handle uMEMORY commands
handle_umemory() {
    local subcmd="${1:-setup}"
    
    case "$subcmd" in
        SETUP|setup|INIT|init)
            log_info "Initializing uMEMORY system..."
            if [[ -x "$UMEMORY/setup.sh" ]]; then
                "$UMEMORY/setup.sh"
            else
                log_error "uMEMORY setup script not found"
            fi
            ;;
        BACKUP|backup)
            log_info "Creating uMEMORY backup..."
            if [[ -x "$UMEMORY/.backup/backup.sh" ]]; then
                "$UMEMORY/.backup/backup.sh"
            else
                log_warning "Backup script not found, running setup first..."
                "$UMEMORY/setup.sh" backup
            fi
            ;;
        IDENTITY|identity)
            if [[ -f "$UMEMORY/configs/identity.md" ]]; then
                log_info "Current user identity:"
                cat "$UMEMORY/configs/identity.md"
            else
                log_warning "No identity found, creating one..."
                "$UMEMORY/setup.sh" identity
            fi
            ;;
        STATUS|status)
            log_info "uMEMORY Status:"
            echo "📁 Location: $UMEMORY"
            echo "📊 Size: $(du -sh "$UMEMORY" 2>/dev/null | cut -f1 || echo "Unknown")"
            echo "📄 Files: $(find "$UMEMORY" -type f | wc -l || echo "Unknown")"
            echo "📂 Projects: $(find "$UMEMORY/projects" -name "*.md" 2>/dev/null | wc -l || echo "0")"
            echo "📝 Templates: $(find "$UMEMORY/templates" -type f 2>/dev/null | wc -l || echo "0")"
            echo "🔧 Scripts: $(find "$UMEMORY/scripts" -type f 2>/dev/null | wc -l || echo "0")"
            ;;
        RESET|reset)
            log_warning "This will reset your uMEMORY system!"
            read -p "Are you sure? [y/N]: " confirm
            if [[ "$confirm" == "y" ]]; then
                "$UMEMORY/setup.sh" reset
            else
                log_info "Reset cancelled"
            fi
            ;;
        HELP|help|*)
            log_info "uMEMORY Commands:"
            echo "  UMEMORY SETUP   - Initialize uMEMORY system"
            echo "  UMEMORY BACKUP  - Create backup"
            echo "  UMEMORY IDENTITY - Show/create user identity"
            echo "  UMEMORY STATUS  - Show system status"
            echo "  UMEMORY RESET   - Reset system (careful!)"
            echo "  UMEMORY HELP    - Show this help"
            ;;
    esac
}

# Handle mission commands
handle_mission() {
    local subcmd="$1"
    
    case "$subcmd" in
        LIST)
            log_info "Missions:"
            find "$UMEMORY" -name "*-mission.md" -exec basename {} \; | sort
            ;;
        CREATE|*)
            local name=$(echo "$subcmd" | cut -d'|' -f2)
            local mission_file="$UMEMORY/$(printf "%03d" $(($(find "$UMEMORY" -name "*-mission.md" | wc -l) + 1)))-${name}-mission.md"
            
            cat > "$mission_file" << EOF
# 🎯 Mission: $name

**Created**: $(date +%Y-%m-%d)  
**Status**: Active  
**Type**: User Created

## Objective

[Describe mission objective here]

## Tasks

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Progress

*Mission started*

---

**Status**: Active 🎯
EOF
            log_success "Mission created: $(basename "$mission_file")"
            ;;
        COMPLETE|*)
            local name=$(echo "$subcmd" | cut -d'|' -f2)
            local mission_file=$(find "$UMEMORY" -name "*${name}*mission.md" | head -1)
            
            if [[ -f "$mission_file" ]]; then
                # Create legacy file
                local legacy_file="$UMEMORY/legacy-${name}-$(date +%Y%m%d-%H%M%S)-E001-UTC.md"
                
                cat > "$legacy_file" << EOF
# 💎 Device Legacy: $name

**Preserved**: $(date +%Y-%m-%d %H:%M:%S)
**Original Mission**: $name
**Status**: Completed

## Legacy Value

This completed mission has been preserved as device legacy.

## Mission Archive

$(cat "$mission_file")

---

## ✅ Mission Completed

**Completion Date**: $(date +%Y-%m-%d)
**Summary**: Mission successfully completed and archived.
EOF
                
                rm "$mission_file"
                log_success "Mission completed and archived: $(basename "$legacy_file")"
            else
                log_error "Mission not found: $name"
            fi
            ;;
        *)
            log_error "Unknown mission command: $subcmd"
            ;;
    esac
}

# Handle package commands  
handle_package() {
    local subcmd="$1"
    
    case "$subcmd" in
        LIST)
            log_info "Available packages:"
            echo "- ripgrep (fast text search)"
            echo "- fd (fast file finder)"
            echo "- bat (syntax-highlighted viewer)"
            echo "- glow (markdown renderer)"
            echo "- micro (terminal editor)"
            echo "- jq (JSON processor)"
            ;;
        INSTALL|*)
            local pkg=$(echo "$subcmd" | cut -d'|' -f2)
            log_info "Installing package: $pkg"
            
            if command -v brew >/dev/null 2>&1; then
                brew install "$pkg" 2>/dev/null || log_warning "Package $pkg may already be installed"
                echo "$(date): Installed $pkg" >> "$UMEMORY/package-install.log"
                log_success "Package installed: $pkg"
            else
                log_error "Package manager not available"
            fi
            ;;
        INFO|*)
            local pkg=$(echo "$subcmd" | cut -d'|' -f2)
            case "$pkg" in
                ripgrep) echo "ripgrep: Ultra-fast text search tool" ;;
                fd) echo "fd: Fast file finder, modern replacement for find" ;;
                bat) echo "bat: Syntax-highlighted file viewer with Git integration" ;;
                *) log_error "No info available for: $pkg" ;;
            esac
            ;;
        *)
            log_error "Unknown package command: $subcmd"
            ;;
    esac
}

# Handle log commands
handle_log() {
    local subcmd="$1"
    
    case "$subcmd" in
        REPORT)
            if [[ -f "$SCRIPT_DIR/log.sh" ]]; then
                bash "$SCRIPT_DIR/log.sh" report
            else
                log_error "Logging system not available"
            fi
            ;;
        STATS)
            if [[ -f "$SCRIPT_DIR/log.sh" ]]; then
                bash "$SCRIPT_DIR/log.sh" stats
            else
                log_error "Logging system not available"
            fi
            ;;
        MOVE|*)
            local command=$(echo "$subcmd" | cut -d'|' -f2)
            if [[ -f "$SCRIPT_DIR/log.sh" ]]; then
                bash "$SCRIPT_DIR/log.sh" move "$command"
            fi
            ;;
        *)
            log_error "Unknown log command: $subcmd"
            ;;
    esac
}

# Handle LAYOUT command
handle_layout_command() {
    local args="$1"
    
    if [[ -z "$args" ]]; then
        show_layout_manager
        return
    fi
    
    local action=$(echo "$args" | cut -d' ' -f1)
    local value=$(echo "$args" | cut -d' ' -f2-)
    
    case "$action" in
        compact|standard|wide|coding|writing|dashboard|auto)
            apply_layout "$action" "user selection"
            ;;
        info|status)
            detect_terminal_size
            echo -e "\n${CYAN}📐 Current Layout Status${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo -e "${CYAN}Layout:${NC} $CURRENT_LAYOUT"
            echo -e "${CYAN}Screen:${NC} ${CURRENT_COLS}x${CURRENT_ROWS}"
            echo -e "${CYAN}Auto Layout:${NC} $(if [[ "$AUTO_LAYOUT" == true ]]; then echo "✅ Enabled"; else echo "❌ Disabled"; fi)"
            echo -e "${CYAN}Mode:${NC} $CURRENT_MODE"
            ;;
        auto)
            case "$value" in
                on|enable|true)
                    AUTO_LAYOUT=true
                    save_layout_config
                    log_success "Auto layout enabled"
                    detect_optimal_layout "$CURRENT_MODE" ""
                    ;;
                off|disable|false)
                    AUTO_LAYOUT=false
                    save_layout_config
                    log_success "Auto layout disabled"
                    ;;
                *)
                    echo -e "${CYAN}Auto Layout Status:${NC} $(if [[ "$AUTO_LAYOUT" == true ]]; then echo "✅ Enabled"; else echo "❌ Disabled"; fi)"
                    echo -e "${YELLOW}💡 Usage:${NC} layout auto on/off"
                    ;;
            esac
            ;;
        reset)
            apply_layout "auto" "reset to optimal"
            ;;
        suggest)
            suggest_layout_improvements "$CURRENT_MODE mode with $(basename "${CURRENT_FILE:-unknown}")"
            ;;
        presets|list)
            echo -e "\n${CYAN}📱 Available Layout Presets${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo -e "  ${BLUE}compact${NC}     - ${COMPACT_COLS}x${COMPACT_ROWS}   (minimal, mobile-friendly)"
            echo -e "  ${BLUE}standard${NC}    - ${STANDARD_COLS}x${STANDARD_ROWS}  (balanced, recommended)"
            echo -e "  ${BLUE}wide${NC}        - ${WIDE_COLS}x${WIDE_ROWS}  (spacious, comfortable)"
            echo -e "  ${BLUE}coding${NC}      - ${CODING_COLS}x${CODING_ROWS}  (tall, perfect for scripts)"
            echo -e "  ${BLUE}writing${NC}     - ${WRITING_COLS}x${WRITING_ROWS}  (narrow, focused reading)"
            echo -e "  ${BLUE}dashboard${NC}   - ${DASHBOARD_COLS}x${DASHBOARD_ROWS}  (wide, data visualization)"
            echo -e "  ${BLUE}auto${NC}        - Auto-detect based on content"
            ;;
        help|?)
            echo -e "\n${CYAN}📐 Layout Command Help${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo -e "${BOLD}Usage:${NC} layout [command] [options]"
            echo ""
            echo -e "${BOLD}Commands:${NC}"
            echo -e "  ${YELLOW}layout${NC}                    - Show layout manager"
            echo -e "  ${YELLOW}layout <preset>${NC}          - Switch to layout preset"
            echo -e "  ${YELLOW}layout info${NC}              - Show current layout status"
            echo -e "  ${YELLOW}layout auto on/off${NC}       - Enable/disable auto-detection"
            echo -e "  ${YELLOW}layout reset${NC}             - Reset to optimal layout"
            echo -e "  ${YELLOW}layout suggest${NC}           - Get layout suggestions"
            echo -e "  ${YELLOW}layout presets${NC}           - List available presets"
            echo ""
            echo -e "${BOLD}Presets:${NC} compact, standard, wide, coding, writing, dashboard, auto"
            ;;
        *)
            log_error "Unknown layout command: $action"
            echo -e "${YELLOW}💡 Tip:${NC} Use 'layout help' for available commands"
            ;;
    esac
}

# Handle PANEL command
handle_panel_command() {
    local args="$1"
    
    if [[ -z "$args" ]]; then
        show_panel_dashboard "standard"
        return
    fi
    
    local action=$(echo "$args" | cut -d' ' -f1)
    local value=$(echo "$args" | cut -d' ' -f2-)
    
    case "$action" in
        dashboard|dash)
            local style="${value:-standard}"
            show_panel_dashboard "$style"
            ;;
        grid)
            create_panel_grid "$value"
            ;;
        memory)
            clear
            echo -e "\n${CYAN}📊 Memory Panel${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            generate_memory_panel 60 20
            echo ""
            echo -e "${CYAN}Press any key to return...${NC}"
            read -rsn1
            ;;
        mission)
            clear
            echo -e "\n${CYAN}📊 Mission Panel${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            generate_mission_panel 60 20
            echo ""
            echo -e "${CYAN}Press any key to return...${NC}"
            read -rsn1
            ;;
        data)
            clear
            echo -e "\n${CYAN}📊 Data Panel${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            generate_data_panel 60 20
            echo ""
            echo -e "${CYAN}Press any key to return...${NC}"
            read -rsn1
            ;;
        status)
            clear
            echo -e "\n${CYAN}📊 Status Panel${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            generate_status_panel 60 20
            echo ""
            echo -e "${CYAN}Press any key to return...${NC}"
            read -rsn1
            ;;
        char|font)
            show_character_editor
            ;;
        help|?)
            echo -e "\n${CYAN}📊 Panel System Help${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo -e "${BOLD}Usage:${NC} panel [command] [options]"
            echo ""
            echo -e "${BOLD}Commands:${NC}"
            echo -e "  ${YELLOW}panel${NC}                    - Show standard dashboard"
            echo -e "  ${YELLOW}panel dashboard <style>${NC}  - Show dashboard (compact/standard/wide/tall)"
            echo -e "  ${YELLOW}panel grid${NC}              - Create custom grid layout"
            echo -e "  ${YELLOW}panel memory${NC}            - Show memory panel"
            echo -e "  ${YELLOW}panel mission${NC}           - Show mission panel"
            echo -e "  ${YELLOW}panel data${NC}              - Show data panel"
            echo -e "  ${YELLOW}panel status${NC}            - Show status panel"
            echo -e "  ${YELLOW}panel char${NC}              - Character/font editor"
            echo ""
            echo -e "${BOLD}Styles:${NC} compact, standard, wide, tall"
            echo -e "${BOLD}Features:${NC} ASCII borders, numerical displays, shortcode integration"
            ;;
        *)
            log_error "Unknown panel command: $action"
            echo -e "${YELLOW}💡 Tip:${NC} Use 'panel help' for available commands"
            ;;
    esac
}

# Handle dev commands
handle_dev() {
    local subcmd="$1"
    
    case "$subcmd" in
        status)
            log_info "Development System Status:"
            echo "📁 Reports: $(find "$UDEV/reports" -name "*.md" | wc -l)"
            echo "🔄 Migrations: $(find "$UDEV/migrations" -name "*.md" | wc -l)"
            echo "🔍 Analysis: $(find "$UDEV/analysis" -name "*.md" | wc -l)"
            ;;
        report:*)
            local type=$(echo "$subcmd" | cut -d':' -f2)
            local timestamp=$(date +%Y%m%d_%H%M%S)
            local report_file="$UDEV/reports/${type^^}_REPORT_${timestamp}.md"
            
            cat > "$report_file" << EOF
# 📊 ${type^^} Report

**Generated**: $(date +%Y-%m-%d)  
**Type**: Development Report  
**Status**: Draft

## Summary

[Report summary here]

## Details

[Detailed information]

## Action Items

- [ ] Item 1
- [ ] Item 2

---

*Generated by uDOS v1.2 Development System*
EOF
            log_success "Report created: $(basename "$report_file")"
            ;;
        *)
            log_error "Unknown dev command: $subcmd"
            ;;
    esac
}

# Main command processing
main() {
    # Set development mode for better UX during development
    export UDOS_DEV_MODE=true
    
    # Initialize advanced input intelligence systems
    init_shortcode_templates
    
    # Initialize system with error handling
    if ! init_directories; then
        log_error "Failed to initialize directories"
        return 1
    fi
    
    # Show enhanced startup sequence
    show_rainbow_ascii
    show_boot_sequence
    
    # Terminal size optimization (on first run or if requested)
    if [[ "${1:-}" == "--resize" ]] || [[ ! -f "$UMEMORY/terminal_size.conf" ]]; then
        recommend_terminal_size || true  # Don't fail if terminal size optimization fails
        # Save preference for next time
        mkdir -p "$UMEMORY"
        detect_terminal_size
        echo "${CURRENT_COLS}x${CURRENT_ROWS}" > "$UMEMORY/terminal_size.conf" 2>/dev/null || true
    fi
    
    # Authenticate user (skip in dev mode)
    if ! authenticate_user --no-auth; then
        log_warning "Authentication skipped (development mode)"
    fi
    
    # Validate system integrity
    if ! validate_system; then
        log_warning "System validation failed - initiating setup"
        setup_user || log_warning "Setup failed, continuing anyway"
    fi
    
    # Check for arguments
    if [[ $# -eq 0 ]]; then
        # Interactive mode
        log_header "System ready - Welcome to uDOS!"
        echo -e "${CYAN}💡 Smart Input Features:${NC}"
        echo -e "  • Type [ to browse shortcodes"
        echo -e "  • Use Tab for autocomplete"
        echo -e "  • Arrow keys to navigate suggestions"
        echo -e "  • Type GO for full reference"
        echo -e "  • Type EXIT to quit"
        echo ""
        
        # Check setup (hardened - always setup if files missing)
        check_setup || true  # Don't fail if setup check fails
        
        # Main interactive loop with error recovery
        while true; do
            # Show mode indicator
            show_mode_indicator
            
            # Use enhanced prompt based on current mode
            show_enhanced_prompt
            read -r input || {
                echo ""
                log_info "Input interrupted"
                break
            }
            
            # Skip empty input
            [[ -z "$input" ]] && continue
            
            # Handle exit and restart commands
            if [[ "$input" =~ ^(exit|quit|bye)$ ]]; then
                log_success "Goodbye from uDOS v1.2! 👋"
                break
            elif [[ "$input" =~ ^(restart|reboot|reload)$ ]]; then
                log_info "Restarting uDOS session..."
                clear
                exec "$0" "$@"  # Restart the script with same arguments
            elif [[ "$input" =~ ^(reset|refresh)$ ]]; then
                log_info "Refreshing uDOS interface..."
                clear
                continue  # Restart the loop but keep session
            fi
            
            # Process input with error handling
            if [[ "$CURRENT_MODE" != "COMMAND" ]]; then
                # In editor mode, use editor-specific processing
                if ! process_editor_input "$input"; then
                    log_warning "Editor command failed: $input"
                fi
            else
                # In command mode, use standard processing
                if ! process_input "$input"; then
                    log_warning "Command failed: $input"
                    echo "Type 'HELP' for available commands"
                fi
            fi
        done
    else
        # Command mode
        process_input "$*" || log_error "Command failed: $*"
    fi
}

# Process user input
process_input() {
    local input="$1"
    
    # Special case: just '[' shows shortcode browser
    if [[ "$input" == "[" ]]; then
        browse_shortcodes
        return
    fi
    
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
        TUTORIAL|tutorial)
            start_adventure_tutorial
            ;;
        STATUS|status)
            show_status
            ;;
        DASH|dash)
            show_dashboard
            ;;
        RESIZE|resize|SIZE|size)
            recommend_terminal_size
            ;;
        SHORTCUTS|shortcuts|GO|go)
            browse_shortcodes
            ;;
        DESTROY|destroy)
            handle_destroy
            ;;
        SETUP|setup)
            setup_user
            ;;
        RESTART|restart|REBOOT|reboot|RELOAD|reload)
            log_info "Restarting uDOS session..."
            clear
            exec "$0" "$@"
            ;;
        RESET|reset|REFRESH|refresh)
            log_info "Refreshing uDOS interface..."
            clear
            ;;
        MEMORY|MEM)
            handle_memory "$args"
            ;;
        UMEMORY|umemory)
            handle_umemory "$args"
            ;;
        MISSION)
            handle_mission "$args"
            ;;
        PACKAGE|PACK)
            handle_package "$args"
            ;;
        LOG)
            handle_log "$args"
            ;;
        DEV)
            handle_dev "$args"
            ;;
        MODE)
            handle_mode_switch "$args"
            ;;
        EDIT)
            handle_edit_command "$args"
            ;;
        NEW)
            handle_new_command "$args"
            ;;
        HISTORY|history)
            handle_history_command "$args"
            ;;
        FAVORITES|favorites)
            show_favorites
            ;;
        LAYOUT|layout)
            handle_layout_command "$args"
            ;;
        PANEL|panel)
            handle_panel_command "$args"
            ;;
        CHAR|char)
            show_character_editor
            ;;
        INPUT|input)
            handle_input_command "$args"
            ;;
        ASCII|ascii)
            handle_ascii_command "$args"
            ;;
        TYPO|typo)
            handle_typo_command "$args"
            ;;
        NETHACK|nethack|GAME|game)
            handle_nethack_command "$args"
            ;;
        TEMPLATE|template|TPL|tpl)
            handle_template_command "$args"
            ;;
        GIT|git)
            handle_git_command "$args"
            ;;
        PUSH|push)
            handle_git_push "$args"
            ;;
        PULL|pull)
            handle_git_pull "$args"
            ;;
        COMMIT|commit)
            handle_git_commit "$args"
            ;;
        CLONE|clone)
            handle_git_clone "$args"
            ;;
        BRANCH|branch)
            handle_git_branch "$args"
            ;;
        MERGE|merge)
            handle_git_merge "$args"
            ;;
        REBASE|rebase)
            handle_git_rebase "$args"
            ;;
        STASH|stash)
            handle_git_stash "$args"
            ;;
        REMOTE|remote)
            handle_git_remote "$args"
            ;;
        SSH-KEY|ssh-key|SSHKEY|sshkey)
            handle_ssh_key "$args"
            ;;
        *)
            # Check for history recall (!number)
            if [[ "$cmd" =~ ^!([0-9]+)$ ]]; then
                local hist_num="${BASH_REMATCH[1]}"
                if [[ -f "$COMMAND_HISTORY_FILE" ]]; then
                    local historical_command=$(sed -n "${hist_num}p" "$COMMAND_HISTORY_FILE" | cut -d':' -f2-)
                    if [[ -n "$historical_command" ]]; then
                        log_info "Executing from history: $historical_command"
                        process_input "$historical_command"
                        return
                    else
                        log_error "No command #$hist_num in history"
                    fi
                else
                    log_error "No command history found"
                fi
            else
                log_error "Unknown command: $cmd"
                echo "Type 'HELP' for available commands or '[' for shortcode browser"
            fi
            ;;
    esac
    
    # Add successful commands to history
    add_to_history "$input"
}

# Handle history commands
handle_history_command() {
    local subcmd="$1"
    
    case "$subcmd" in
        ""|list)
            show_command_history
            ;;
        search*)
            local term=$(echo "$subcmd" | cut -d' ' -f2-)
            if [[ -n "$term" ]]; then
                search_command_history "$term"
            else
                log_error "Usage: history search <term>"
            fi
            ;;
        clear)
            > "$COMMAND_HISTORY_FILE"  # Clear the file
            HISTORY_COUNT=0
            log_success "Command history cleared"
            ;;
        *)
            log_error "Unknown history command: $subcmd"
            echo "Available: history [list], history search <term>, history clear"
            ;;
    esac
}

# Handle mode switching
handle_mode_switch() {
    local mode=$(echo "$1" | tr '[:lower:]' '[:upper:]')
    
    case "$mode" in
        COMMAND)
            set_mode "COMMAND" ""
            ;;
        MARKDOWN)
            start_markdown_editor
            ;;
        USCRIPT)
            start_uscript_editor
            ;;
        SHORTCODE)
            start_shortcode_builder
            ;;
        *)
            log_error "Unknown mode: $mode"
            echo "Available modes: COMMAND, MARKDOWN, USCRIPT, SHORTCODE"
            ;;
    esac
}

# Handle direct edit commands
handle_edit_command() {
    local args="$1"
    local editor_type=$(echo "$args" | awk '{print $1}')
    local filename=$(echo "$args" | awk '{print $2}')
    
    case "$editor_type" in
        markdown|md)
            start_markdown_editor "$filename"
            ;;
        uscript|us)
            start_uscript_editor "$filename"
            ;;
        config|cfg)
            edit_micro_config
            ;;
        shortcode|sc)
            start_shortcode_builder
            ;;
        *)
            log_error "Unknown editor type: $editor_type"
            echo "Available editors: markdown, uscript, config, shortcode"
            ;;
    esac
}

# Setup micro editor integration
setup_micro_integration() {
    local micro_config_dir="$HOME/.config/micro"
    local syntax_dir="$micro_config_dir/syntax"
    
    echo -e "\n${YELLOW}🔧 Setting up micro editor integration...${NC}"
    
    # Create directories
    mkdir -p "$syntax_dir"
    
    # Copy syntax files
    if [[ -f "$SCRIPT_DIR/micro-syntax/uscript.yaml" ]]; then
        cp "$SCRIPT_DIR/micro-syntax/uscript.yaml" "$syntax_dir/"
        echo -e "${GREEN}✅ Installed uScript syntax highlighting${NC}"
    fi
    
    if [[ -f "$SCRIPT_DIR/micro-syntax/udos-markdown.yaml" ]]; then
        cp "$SCRIPT_DIR/micro-syntax/udos-markdown.yaml" "$syntax_dir/"
        echo -e "${GREEN}✅ Installed uDOS Markdown syntax highlighting${NC}"
    fi
    
    # Create basic micro configuration if it doesn't exist
    edit_micro_config > /dev/null 2>&1
    
    echo -e "${CYAN}🚀 Micro editor integration complete!${NC}"
    echo -e "${YELLOW}Features enabled:${NC}"
    echo "  • uScript syntax highlighting (.us files)"
    echo "  • uDOS Markdown with shortcode highlighting"
    echo "  • Template variable recognition"
    echo "  • Enhanced editing experience"
    echo ""
}

# Edit micro configuration
edit_micro_config() {
    local config_dir="$HOME/.config/micro"
    local config_file="$config_dir/settings.json"
    
    echo -e "\n${YELLOW}🔧 Micro Editor Configuration${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Create config directory if it doesn't exist
    mkdir -p "$config_dir"
    
    # Create default config if it doesn't exist
    if [[ ! -f "$config_file" ]]; then
        echo -e "${BLUE}📝 Creating default micro configuration...${NC}"
        cat > "$config_file" << 'EOF'
{
    "autoclose": true,
    "autoindent": true,
    "autosave": false,
    "colorscheme": "monokai",
    "cursorline": true,
    "diffgutter": true,
    "ignorecase": false,
    "indentchar": " ",
    "infobar": true,
    "keepautoindent": false,
    "keymenu": false,
    "mouse": true,
    "pluginchannels": [
        "https://raw.githubusercontent.com/micro-editor/plugin-channel/master/channel.json"
    ],
    "pluginrepos": [],
    "rmtrailingws": false,
    "ruler": true,
    "savecursor": false,
    "savehistory": true,
    "saveundo": false,
    "scrollbar": false,
    "scrollmargin": 3,
    "scrollspeed": 2,
    "smartpaste": true,
    "softwrap": false,
    "splitbottom": true,
    "splitright": true,
    "statusline": true,
    "sucmd": "sudo",
    "syntax": true,
    "tabmovement": false,
    "tabsize": 4,
    "tabstospaces": false,
    "termtitle": false,
    "useprimary": true
}
EOF
    fi
    
    echo -e "${CYAN}Current config path:${NC} $config_file"
    echo -e "${GREEN}Press any key to edit micro configuration...${NC}"
    read -n 1
    
    # Edit config with micro itself
    micro "$config_file"
    
    echo -e "\n${GREEN}✅ Micro configuration updated${NC}"
}

# Handle NEW command for creating files
handle_new_command() {
    local file_type="$1"
    local name="$2"
    
    case "$file_type" in
        markdown|md)
            if [[ -n "$name" ]]; then
                start_markdown_editor "$name"
            else
                # Generate filename with timestamp
                local timestamp=$(date +%Y%m%d-%H%M%S)
                local filename="document-$timestamp.md"
                start_markdown_editor "$filename"
            fi
            ;;
        uscript|us)
            if [[ -n "$name" ]]; then
                start_uscript_editor "$name"
            else
                # Generate filename with timestamp
                local timestamp=$(date +%Y%m%d-%H%M%S)
                local filename="script-$timestamp.us"
                start_uscript_editor "$filename"
            fi
            ;;
        *)
            log_error "Unknown file type: $file_type"
            echo "Available types: markdown, uscript"
            echo "Usage: NEW <type> [filename]"
            ;;
    esac
}

# Handle smart input commands
handle_input_command() {
    local subcmd="$1"
    shift
    local args="$@"
    
    case "$subcmd" in
        ""|help)
            echo "🎯 Smart Input Commands:"
            echo "  input demo              - Run interactive demo"
            echo "  input field <spec>      - Collect single field"
            echo "  input mission          - Create new mission with smart input"
            echo "  input template <name>   - Process template with smart input"
            echo ""
            echo "Field Specification Format:"
            echo "  name|type|prompt|default|validation"
            echo ""
            echo "Field Types:"
            echo "  text, select, boolean, date, number"
            ;;
        demo)
            "$SCRIPT_DIR/smart-input.sh" demo
            ;;
        field)
            if [[ -n "$args" ]]; then
                "$SCRIPT_DIR/smart-input.sh" field $args
            else
                log_error "Usage: input field <name> <type> [prompt] [default] [validation]"
            fi
            ;;
        mission)
            handle_smart_mission_creation
            ;;
        template)
            if [[ -n "$args" ]]; then
                handle_smart_template_processing "$args"
            else
                log_error "Usage: input template <template_name>"
            fi
            ;;
        init)
            "$SCRIPT_DIR/smart-input.sh" init
            ;;
        *)
            log_error "Unknown input command: $subcmd"
            echo "Type 'input help' for available commands"
            ;;
    esac
}

# Handle ASCII art generation commands
handle_ascii_command() {
    local subcmd="$1"
    shift
    local args="$@"
    
    # Check if ASCII generator is installed
    if ! command -v ascii-gen &> /dev/null && ! [[ -f "$HOME/uDOS/uCode/packages/ascii-generator/ascii_generator.py" ]]; then
        echo -e "${YELLOW}⚠️ ASCII Generator not installed${NC}"
        echo ""
        echo -e "${CYAN}Would you like to install it now? [Y/n]:${NC}"
        read -n 1 install_choice
        echo ""
        if [[ "$install_choice" =~ ^[Yy]$ ]] || [[ -z "$install_choice" ]]; then
            echo -e "${BLUE}📦 Installing ASCII Generator...${NC}"
            bash "$SCRIPT_DIR/packages/install-ascii-generator.sh"
            return
        else
            echo -e "${YELLOW}ASCII Generator installation skipped${NC}"
            return
        fi
    fi
    
    case "$subcmd" in
        ""|help)
            echo -e "\n${RAINBOW_YELLOW}🎨 ASCII Art Generator${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo -e "${CYAN}📝 TEXT COMMANDS:${NC}"
            echo "  ASCII TEXT 'Hello World'           - Generate ASCII text"
            echo "  ASCII LOGO 'uDOS'                  - Generate system logo"
            echo "  ASCII BANNER 'Title' 'Subtitle'    - Generate banner"
            echo ""
            echo -e "${CYAN}🖼️ IMAGE COMMANDS:${NC}"
            echo "  ASCII IMAGE path/to/image.jpg       - Convert image to ASCII"
            echo ""
            echo -e "${CYAN}⚙️ OPTIONS:${NC}"
            echo "  --font NAME      - Text font (small, big, block, shadow)"
            echo "  --width N        - Output width (default: 80)"
            echo "  --save FILE      - Save to file"
            echo ""
            echo -e "${CYAN}💾 INTEGRATION:${NC}"
            echo "  Output is automatically copied to clipboard"
            echo "  Generated art can be pasted into markdown files"
            echo "  Saved files go to ASCII Art Gallery"
            echo ""
            ;;
        text|TEXT)
            generate_ascii_text "$args"
            ;;
        logo|LOGO)
            generate_ascii_logo "$args"
            ;;
        banner|BANNER)
            generate_ascii_banner "$args"
            ;;
        image|IMAGE)
            generate_ascii_image "$args"
            ;;
        install)
            bash "$SCRIPT_DIR/packages/install-ascii-generator.sh"
            ;;
        *)
            log_error "Unknown ASCII command: $subcmd"
            echo "Type 'ASCII help' for available commands"
            ;;
    esac
}

# ASCII generation functions
generate_ascii_text() {
    local text="$1"
    local font="${2:-big}"
    
    if [[ -z "$text" ]]; then
        echo -e "${YELLOW}Enter text to convert to ASCII:${NC}"
        read -r text
    fi
    
    echo -e "\n${RAINBOW_YELLOW}🎨 Generating ASCII text...${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Use ASCII generator
    if command -v ascii-gen &> /dev/null; then
        ascii-gen text "$text" --font "$font"
    else
        cd "$HOME/uDOS/uCode/packages/ascii-generator"
        python3 ascii_generator.py --text "$text" --font "$font"
    fi
    
    echo ""
    echo -e "${GREEN}✅ ASCII text generated!${NC}"
    echo -e "${CYAN}💡 Tip: Copy and paste into your markdown files${NC}"
}

generate_ascii_logo() {
    local text="${1:-uDOS}"
    local font="${2:-big}"
    
    echo -e "\n${RAINBOW_YELLOW}🏷️ Generating ASCII logo...${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if command -v ascii-gen &> /dev/null; then
        ascii-gen text "$text" --font "$font" --width 60
    else
        cd "$HOME/uDOS/uCode/packages/ascii-generator"
        python3 ascii_generator.py --text "$text" --font "$font" --width 60
    fi
    
    echo ""
    echo -e "${GREEN}✅ Logo generated!${NC}"
    echo -e "${CYAN}💡 Add to your documentation headers${NC}"
}

generate_ascii_banner() {
    local title="$1"
    local subtitle="$2"
    
    if [[ -z "$title" ]]; then
        echo -e "${YELLOW}Enter banner title:${NC}"
        read -r title
    fi
    
    echo -e "\n${RAINBOW_YELLOW}🏮 Generating ASCII banner...${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Generate title
    if command -v ascii-gen &> /dev/null; then
        ascii-gen text "$title" --font big --width 80
        if [[ -n "$subtitle" ]]; then
            echo ""
            ascii-gen text "$subtitle" --font small --width 80
        fi
    else
        cd "$HOME/uDOS/uCode/packages/ascii-generator"
        python3 ascii_generator.py --text "$title" --font big --width 80
        if [[ -n "$subtitle" ]]; then
            echo ""
            python3 ascii_generator.py --text "$subtitle" --font small --width 80
        fi
    fi
    
    echo ""
    echo -e "${GREEN}✅ Banner generated!${NC}"
    echo -e "${CYAN}💡 Perfect for document headers${NC}"
}

generate_ascii_image() {
    local image_path="$1"
    
    if [[ -z "$image_path" ]]; then
        echo -e "${YELLOW}Enter path to image file:${NC}"
        read -r image_path
    fi
    
    if [[ ! -f "$image_path" ]]; then
        log_error "Image file not found: $image_path"
        return 1
    fi
    
    echo -e "\n${RAINBOW_YELLOW}🖼️ Converting image to ASCII...${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if command -v ascii-gen &> /dev/null; then
        ascii-gen image "$image_path" --width 80
    else
        cd "$HOME/uDOS/uCode/packages/ascii-generator"
        python3 ascii_generator.py --image "$image_path" --width 80
    fi
    
    echo ""
    echo -e "${GREEN}✅ Image converted to ASCII!${NC}"
    echo -e "${CYAN}💡 Great for adding visual elements to documentation${NC}"
}

# Handle Typo web editor commands
handle_typo_command() {
    local subcmd="$1"
    shift
    local args="$@"
    
    # Check if Typo is installed
    if ! [[ -f "$HOME/uDOS/uCode/packages/typo/package.json" ]]; then
        echo -e "${YELLOW}⚠️ Typo Markdown Editor not installed${NC}"
        echo ""
        echo -e "${CYAN}Would you like to install it now? [Y/n]:${NC}"
        read -n 1 install_choice
        echo ""
        if [[ "$install_choice" =~ ^[Yy]$ ]] || [[ -z "$install_choice" ]]; then
            echo -e "${BLUE}📦 Installing Typo...${NC}"
            bash "$SCRIPT_DIR/packages/install-typo.sh"
            return
        else
            echo -e "${YELLOW}Typo installation skipped${NC}"
            return
        fi
    fi
    
    case "$subcmd" in
        ""|help)
            echo -e "\n${RAINBOW_BLUE}🌐 Typo Web Markdown Editor${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo -e "${CYAN}📝 EDITING COMMANDS:${NC}"
            echo "  TYPO EDIT file.md              - Edit file in web browser"
            echo "  TYPO NEW filename.md           - Create and edit new file"
            echo "  TYPO SERVER                    - Start development server"
            echo ""
            echo -e "${CYAN}🌐 WEB INTERFACE:${NC}"
            echo "  • Modern browser-based editor"
            echo "  • Live markdown preview"
            echo "  • Real-time file watching"
            echo "  • Export capabilities"
            echo "  • Responsive design"
            echo ""
            echo -e "${CYAN}🔗 ACCESS:${NC}"
            echo "  Development: http://localhost:5173"
            echo "  Production:  http://localhost:4173"
            echo ""
            echo -e "${CYAN}💡 INTEGRATION:${NC}"
            echo "  • Works with all uDOS markdown files"
            echo "  • Supports uDOS shortcodes and templates"
            echo "  • Auto-saves changes"
            echo "  • Perfect for documentation editing"
            echo ""
            ;;
        edit|EDIT)
            handle_typo_edit "$args"
            ;;
        new|NEW)
            handle_typo_new "$args"
            ;;
        server|SERVER)
            handle_typo_server
            ;;
        install)
            bash "$SCRIPT_DIR/packages/install-typo.sh"
            ;;
        *)
            log_error "Unknown Typo command: $subcmd"
            echo "Type 'TYPO help' for available commands"
            ;;
    esac
}

# Typo editing functions
handle_typo_edit() {
    local file_path="$1"
    
    if [[ -z "$file_path" ]]; then
        echo -e "${YELLOW}Enter markdown file to edit:${NC}"
        read -r file_path
    fi
    
    # Convert to absolute path if relative
    if [[ ! "$file_path" = /* ]]; then
        file_path="$UMEMORY/$file_path"
    fi
    
    echo -e "\n${RAINBOW_BLUE}🌐 Opening Typo Web Editor${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}File:${NC} $file_path"
    echo ""
    
    # Ensure file exists
    if [[ ! -f "$file_path" ]]; then
        echo -e "${BLUE}📝 Creating new file...${NC}"
        mkdir -p "$(dirname "$file_path")"
        cat > "$file_path" << EOF
# New Document

**Created**: $(date)  
**Editor**: Typo Web Editor  
**uDOS Integration**: Active

---

## Content

Write your markdown content here...

### uDOS Features Available
- Shortcode support: [COMMAND|ARGS]
- Template variables: {{VARIABLE}}
- ASCII art integration
- Live preview in browser

---

*Document created with uDOS + Typo*
EOF
    fi
    
    echo -e "${GREEN}✅ File ready for editing${NC}"
    echo ""
    echo -e "${YELLOW}🚀 Starting Typo development server...${NC}"
    echo -e "${CYAN}Instructions:${NC}"
    echo "  1. Wait for server to start"
    echo "  2. Open http://localhost:5173 in your browser"
    echo "  3. Click 'Open File' and select: $file_path"
    echo "  4. Start editing with live preview!"
    echo ""
    echo -e "${GREEN}Press any key to start server... (Ctrl+C to stop)${NC}"
    read -n 1
    
    # Start Typo server
    cd "$HOME/uDOS/uCode/packages/typo"
    echo ""
    echo -e "${BLUE}🌐 Server starting at http://localhost:5173${NC}"
    npm run dev
}

handle_typo_new() {
    local filename="$1"
    
    if [[ -z "$filename" ]]; then
        echo -e "${YELLOW}Enter filename for new document:${NC}"
        read -r filename
    fi
    
    # Add .md extension if not present
    if [[ "$filename" != *.md ]]; then
        filename="$filename.md"
    fi
    
    # Create file in uMemory
    local filepath="$UMEMORY/$filename"
    
    echo -e "\n${RAINBOW_BLUE}📝 Creating New Document${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}File:${NC} $filepath"
    echo ""
    
    # Now edit the file with Typo
    handle_typo_edit "$filepath"
}

handle_typo_server() {
    echo -e "\n${RAINBOW_BLUE}🌐 Starting Typo Development Server${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${CYAN}Server will be available at:${NC} http://localhost:5173"
    echo -e "${YELLOW}Features:${NC}"
    echo "  • Live markdown preview"
    echo "  • File browser interface"
    echo "  • Real-time editing"
    echo "  • Export capabilities"
    echo ""
    echo -e "${GREEN}Press Ctrl+C to stop server${NC}"
    echo ""
    
    cd "$HOME/uDOS/uCode/packages/typo"
    npm run dev
}

# Handle NetHack game commands
handle_nethack_command() {
    local subcmd="$1"
    shift
    local args="$@"
    
    # Check if NetHack is installed
    if ! command -v nethack &> /dev/null && ! [[ -f "$HOME/uDOS/uCode/packages/nethack/udos-nethack-integration.sh" ]]; then
        echo -e "${YELLOW}⚠️ NetHack not installed${NC}"
        echo ""
        echo -e "${CYAN}Would you like to install it now? [Y/n]:${NC}"
        read -n 1 install_choice
        echo ""
        if [[ "$install_choice" =~ ^[Yy]$ ]] || [[ -z "$install_choice" ]]; then
            echo -e "${BLUE}📦 Installing NetHack...${NC}"
            bash "$SCRIPT_DIR/packages/install-nethack.sh"
            return
        else
            echo -e "${YELLOW}NetHack installation skipped${NC}"
            return
        fi
    fi
    
    case "$subcmd" in
        ""|help)
            echo -e "\n${RAINBOW_PURPLE}🎮 NetHack - The Classic Roguelike${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo -e "${CYAN}🗡️ ADVENTURE COMMANDS:${NC}"
            echo "  NETHACK PLAY                    - Start new adventure"
            echo "  NETHACK CONTINUE                - Resume saved game"
            echo "  NETHACK SCORES                  - View high scores"
            echo "  NETHACK HELP                    - Tutorial and controls"
            echo ""
            echo -e "${CYAN}⚔️ GAME FEATURES:${NC}"
            echo "  • Classic ASCII dungeon crawler"
            echo "  • Rich fantasy adventure with deep gameplay"
            echo "  • Procedurally generated dungeons"
            echo "  • Multiple character classes and races"
            echo "  • Complex inventory and magic system"
            echo "  • Decades of refined gameplay"
            echo ""
            echo -e "${CYAN}🎯 uDOS INTEGRATION:${NC}"
            echo "  • Save games stored in uMemory/games/"
            echo "  • Progress logged to uDOS activity"
            echo "  • Terminal-optimized experience"
            echo "  • Seamless integration with uCODE"
            echo ""
            echo -e "${CYAN}🏆 OBJECTIVE:${NC}"
            echo "  Descend into the Dungeons of Doom and retrieve"
            echo "  the legendary Amulet of Yendor from the depths!"
            echo ""
            ;;
        play|start|PLAY|START)
            handle_nethack_play
            ;;
        continue|resume|CONTINUE|RESUME)
            handle_nethack_continue
            ;;
        scores|highscores|SCORES)
            handle_nethack_scores
            ;;
        tutorial|controls|HELP)
            handle_nethack_tutorial
            ;;
        install)
            bash "$SCRIPT_DIR/packages/install-nethack.sh"
            ;;
        *)
            log_error "Unknown NetHack command: $subcmd"
            echo "Type 'NETHACK help' for available commands"
            ;;
    esac
}

# NetHack game functions
handle_nethack_play() {
    # Ensure game directory exists
    local nethack_dir="$UMEMORY/games/nethack"
    mkdir -p "$nethack_dir"
    
    echo -e "\n${RAINBOW_PURPLE}🎮 Starting NetHack Adventure!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # ASCII art welcome
    cat << 'EOF'
    ███╗   ██╗███████╗████████╗██╗  ██╗ █████╗  ██████╗██╗  ██╗
    ████╗  ██║██╔════╝╚══██╔══╝██║  ██║██╔══██╗██╔════╝██║ ██╔╝
    ██╔██╗ ██║█████╗     ██║   ███████║███████║██║     █████╔╝ 
    ██║╚██╗██║██╔══╝     ██║   ██╔══██║██╔══██║██║     ██╔═██╗ 
    ██║ ╚████║███████╗   ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗
    ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝

                    Welcome to the Dungeons of Doom!
    ══════════════════════════════════════════════════════════════
EOF
    
    echo ""
    echo -e "${YELLOW}🗡️ Your Quest:${NC} Retrieve the Amulet of Yendor from the depths!"
    echo ""
    echo -e "${CYAN}💡 Quick Tips for New Adventurers:${NC}"
    echo "   • Use arrow keys or hjkl to move"
    echo "   • Press '?' for complete help in-game"
    echo "   • Press 'Q' to quit and save progress"
    echo "   • Be careful - death is permanent!"
    echo ""
    echo -e "${GREEN}🎯 Choose your destiny...${NC}"
    echo ""
    echo "Press any key to enter the dungeon..."
    read -n 1
    
    # Log activity
    log_info "Started NetHack adventure"
    
    # Change to save directory and launch
    cd "$nethack_dir"
    clear
    
    if command -v nethack &> /dev/null; then
        nethack
    else
        bash "$HOME/uDOS/uCode/packages/nethack/udos-nethack-integration.sh" play
    fi
    
    # Return message
    echo ""
    echo -e "${GREEN}🏰 Welcome back to uDOS!${NC}"
    echo -e "${CYAN}Your NetHack progress has been saved.${NC}"
}

handle_nethack_continue() {
    local nethack_dir="$UMEMORY/games/nethack"
    
    echo -e "\n${RAINBOW_PURPLE}🔄 Continuing Your NetHack Adventure${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${YELLOW}⚔️ Returning to your quest...${NC}"
    echo ""
    
    cd "$nethack_dir"
    
    if command -v nethack &> /dev/null; then
        nethack
    else
        bash "$HOME/uDOS/uCode/packages/nethack/udos-nethack-integration.sh" continue
    fi
    
    echo ""
    echo -e "${GREEN}🏰 Welcome back to uDOS!${NC}"
}

handle_nethack_scores() {
    echo -e "\n${RAINBOW_PURPLE}🏆 NetHack Hall of Fame${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    local nethack_dir="$UMEMORY/games/nethack"
    cd "$nethack_dir" 2>/dev/null || cd /tmp
    
    if command -v nethack &> /dev/null; then
        nethack -s 2>/dev/null || echo "No scores recorded yet - start your adventure to set records!"
    else
        echo "🎮 No scores recorded yet"
        echo "   Start playing to establish your legend!"
    fi
    
    echo ""
    echo -e "${CYAN}💡 Tip: The greatest adventurers are remembered forever${NC}"
}

handle_nethack_tutorial() {
    echo -e "\n${RAINBOW_PURPLE}📚 NetHack Master's Guide${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    echo -e "${CYAN}🎮 MOVEMENT & BASIC CONTROLS:${NC}"
    echo "   Movement: Arrow keys or hjkl (vi-style)"
    echo "   Diagonal: yubn (number pad style)"
    echo "   Wait/Rest: . (period)"
    echo "   Search: s (find hidden doors/traps)"
    echo "   Go up stairs: <"
    echo "   Go down stairs: >"
    echo ""
    
    echo -e "${CYAN}⚔️ COMBAT & INTERACTION:${NC}"
    echo "   Attack: Move into enemy"
    echo "   Pickup item: , (comma)"
    echo "   Drop item: d"
    echo "   Inventory: i"
    echo "   Wear armor: W"
    echo "   Wield weapon: w"
    echo "   Remove item: R"
    echo ""
    
    echo -e "${CYAN}🔮 MAGIC & ITEMS:${NC}"
    echo "   Cast spell: Z"
    echo "   Read scroll/book: r"
    echo "   Quaff potion: q"
    echo "   Apply tool: a"
    echo "   Zap wand: z"
    echo "   Eat food: e"
    echo ""
    
    echo -e "${CYAN}🚪 DUNGEON NAVIGATION:${NC}"
    echo "   Open door: o"
    echo "   Close door: c"
    echo "   Kick: ^D (Ctrl+D)"
    echo "   Look at item: :"
    echo "   Name item: #name"
    echo ""
    
    echo -e "${CYAN}💾 GAME MANAGEMENT:${NC}"
    echo "   Save & Quit: S then y"
    echo "   Quit without saving: Q"
    echo "   Help: ?"
    echo "   Options menu: O"
    echo "   View discoveries: \\"
    echo ""
    
    echo -e "${CYAN}🎯 SURVIVAL TIPS:${NC}"
    echo "   • Always carry food - starvation kills!"
    echo "   • Test unknown potions/scrolls on monsters first"
    echo "   • Keep escape items (scrolls of teleportation)"
    echo "   • Learn to identify items (very important!)"
    echo "   • Save before trying anything dangerous"
    echo ""
    
    echo -e "${CYAN}🌐 RESOURCES:${NC}"
    echo "   • Official guide: https://nethack.org"
    echo "   • Wiki: https://nethackwiki.com"
    echo "   • Spoilers available online (use sparingly!)"
    echo ""
    
    echo -e "${GREEN}May your quest be successful, brave adventurer!${NC}"
}

# Handle template commands
handle_template_command() {
    local subcmd="$1"
    shift
    local args="$@"
    
    case "$subcmd" in
        ""|help)
            echo "📋 Template Commands:"
            echo "  template list           - List available templates"
            echo "  template create <name>  - Create new template"
            echo "  template process <name> - Process template with smart input"
            echo "  template edit <name>    - Edit existing template"
            echo "  template library        - Show template library"
            ;;
        list)
            list_templates
            ;;
        create)
            if [[ -n "$args" ]]; then
                create_template "$args"
            else
                log_error "Usage: template create <template_name>"
            fi
            ;;
        process)
            if [[ -n "$args" ]]; then
                handle_smart_template_processing "$args"
            else
                log_error "Usage: template process <template_name>"
            fi
            ;;
        edit)
            if [[ -n "$args" ]]; then
                edit_template "$args"
            else
                log_error "Usage: template edit <template_name>"
            fi
            ;;
        library)
            show_template_library
            ;;
        *)
            log_error "Unknown template command: $subcmd"
            echo "Type 'template help' for available commands"
            ;;
    esac
}

# Smart mission creation with input system
handle_smart_mission_creation() {
    echo ""
    echo "🚀 Creating New Mission with Smart Input"
    echo "════════════════════════════════════════"
    echo ""
    
    # Initialize input system
    "$SCRIPT_DIR/smart-input.sh" init
    
    # Collect mission details using smart input
    echo "Collecting mission details..."
    mission_name=$("$SCRIPT_DIR/smart-input.sh" field "mission_name" "text" "Mission name" "" "required,min:3,max:100" | tail -1 | sed 's/RESULT: //')
    priority=$("$SCRIPT_DIR/smart-input.sh" field "priority" "select" "Priority level" "Medium" "Low,Medium,High,Critical" | tail -1 | sed 's/RESULT: //')
    due_date=$("$SCRIPT_DIR/smart-input.sh" field "due_date" "date" "Due date" "today+7" "future" | tail -1 | sed 's/RESULT: //')
    description=$("$SCRIPT_DIR/smart-input.sh" field "description" "text" "Mission description" "" "max:500" | tail -1 | sed 's/RESULT: //')
    
    # Create mission file
    local mission_file="$MEMORY_DIR/missions/$(echo "$mission_name" | sed 's/[^a-zA-Z0-9]/-/g' | tr '[:upper:]' '[:lower:]').md"
    mkdir -p "$(dirname "$mission_file")"
    
    cat > "$mission_file" << EOF
# Mission: $mission_name

**Created**: $(date '+%Y-%m-%d %H:%M:%S')  
**Priority**: $priority  
**Due Date**: $due_date  
**Status**: Active

## Objective

$description

## Progress

- [ ] Mission planning
- [ ] Requirements analysis  
- [ ] Implementation
- [ ] Testing
- [ ] Documentation
- [ ] Review and completion

## Notes

*Mission created using uDOS Smart Input System*

---

*Last updated: $(date '+%Y-%m-%d %H:%M:%S')*
EOF
    
    log_success "Mission '$mission_name' created successfully!"
    echo "📄 File: $mission_file"
    echo ""
    echo "🎯 Mission Summary:"
    echo "   Name: $mission_name"
    echo "   Priority: $priority"
    echo "   Due: $due_date"
    echo ""
}

# Smart template processing
handle_smart_template_processing() {
    local template_name="$1"
    local template_file="$TEMPLATE_DIR/$template_name"
    
    if [[ ! -f "$template_file" ]]; then
        # Try with .md extension
        template_file="$TEMPLATE_DIR/$template_name.md"
        if [[ ! -f "$template_file" ]]; then
            log_error "Template not found: $template_name"
            return 1
        fi
    fi
    
    echo ""
    echo "📋 Processing Template: $template_name"
    echo "════════════════════════════════════════"
    echo ""
    
    # TODO: Implement template variable extraction and smart input collection
    # For now, just display the template
    echo "📄 Template content:"
    echo "─────────────────────"
    cat "$template_file"
    echo ""
    echo "🚧 Smart template processing will be implemented in next update"
    echo "   This will automatically detect INPUT fields and collect values"
    echo ""
}

# List available templates
list_templates() {
    echo ""
    echo "📋 Available Templates"
    echo "═════════════════════"
    echo ""
    
    if [[ -d "$TEMPLATE_DIR" ]]; then
        local count=0
        for template in "$TEMPLATE_DIR"/*.md; do
            if [[ -f "$template" ]]; then
                local name=$(basename "$template" .md)
                local size=$(wc -l < "$template")
                echo "  📄 $name ($size lines)"
                ((count++))
            fi
        done
        
        if [[ $count -eq 0 ]]; then
            echo "  No templates found in $TEMPLATE_DIR"
        else
            echo ""
            echo "Total: $count templates"
        fi
    else
        echo "  Template directory not found: $TEMPLATE_DIR"
    fi
    echo ""
}

# Show template library
show_template_library() {
    echo ""
    echo "📚 uDOS Template Library"
    echo "═══════════════════════"
    echo ""
    echo "📖 Documentation Templates:"
    echo "   • user-manual.md      - User guide template"
    echo "   • technical-spec.md   - Technical specification"
    echo "   • api-reference.md    - API documentation"
    echo "   • quick-start.md      - Quick start guide"
    echo ""
    echo "🏗️ System Templates:"
    echo "   • status-report.md    - System status template"
    echo "   • mission-brief.md    - Mission documentation"
    echo "   • error-log.md        - Error reporting template"
    echo "   • dashboard.md        - Dashboard layout"
    echo ""
    echo "🎨 ASCII Art Library:"
    echo "   • logos/              - System logos and branding"
    echo "   • borders/            - Border and frame styles"
    echo "   • icons/              - Small ASCII icons"
    echo "   • diagrams/           - Technical diagrams"
    echo ""
    echo "Use 'template create <name>' to create new templates"
    echo "Use 'template process <name>' for smart input processing"
    echo ""
}

# ============================================================================
# GIT COMMANDS WITH SSH KEY SUPPORT - DEV MODE ONLY
# ============================================================================

# SSH key management for sandbox/user/.ssh
get_ssh_dir() {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/sandbox/user/.ssh"
}

# Check if we're in Dev Mode (wizard folder exists)
check_dev_mode() {
    if [[ ! -d "$UDEV" ]]; then
        log_error "Dev Mode not available - wizard folder not found"
        return 1
    fi
    return 0
}

# Setup SSH agent with keys from sandbox
setup_ssh_agent() {
    local ssh_dir=$(get_ssh_dir)
    
    if [[ ! -d "$ssh_dir" ]]; then
        log_error "SSH directory not found: $ssh_dir"
        return 1
    fi
    
    # Start ssh-agent if not running
    if [[ -z "$SSH_AUTH_SOCK" ]]; then
        eval "$(ssh-agent -s)" > /dev/null
    fi
    
    # Add all private keys found in sandbox ssh directory
    local keys_added=0
    for key in "$ssh_dir"/id_*; do
        if [[ -f "$key" && ! "$key" == *.pub ]]; then
            if ssh-add "$key" 2>/dev/null; then
                ((keys_added++))
                log_info "Added SSH key: $(basename "$key")"
            fi
        fi
    done
    
    if [[ $keys_added -eq 0 ]]; then
        log_warning "No SSH keys found or added from $ssh_dir"
        return 1
    fi
    
    return 0
}

# Main Git command handler
handle_git_command() {
    local args="$1"
    
    if ! check_dev_mode; then
        return 1
    fi
    
    if [[ -z "$args" ]]; then
        log_error "Git operation required. Usage: GIT <operation> [options]"
        echo "Available operations: STATUS, PUSH, PULL, COMMIT, CLONE, BRANCH, MERGE, REBASE, STASH, REMOTE"
        return 1
    fi
    
    local operation=$(echo "$args" | awk '{print $1}' | tr '[:lower:]' '[:upper:]')
    local rest_args=""
    if [[ "$args" == *" "* ]]; then
        rest_args=$(echo "$args" | cut -d' ' -f2-)
    fi
    
    case "$operation" in
        STATUS)
            git status
            ;;
        ADD)
            git add $rest_args
            ;;
        DIFF)
            git diff $rest_args
            ;;
        LOG)
            git log --oneline -10 $rest_args
            ;;
        *)
            log_error "Unknown git operation: $operation"
            echo "Use specific commands: PUSH, PULL, COMMIT, CLONE, BRANCH, MERGE, REBASE, STASH, REMOTE"
            ;;
    esac
}

# Git push with SSH key support
handle_git_push() {
    local args="$1"
    
    if ! check_dev_mode; then
        return 1
    fi
    
    log_info "Setting up SSH keys for git push..."
    if ! setup_ssh_agent; then
        log_error "Failed to setup SSH keys"
        return 1
    fi
    
    echo -e "${BLUE}🚀 Pushing to remote repository...${NC}"
    if [[ -n "$args" ]]; then
        git push $args
    else
        git push
    fi
    
    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        log_info "✅ Push completed successfully"
    else
        log_error "❌ Push failed with exit code $exit_code"
    fi
    
    return $exit_code
}

# Git pull with SSH key support
handle_git_pull() {
    local args="$1"
    
    if ! check_dev_mode; then
        return 1
    fi
    
    log_info "Setting up SSH keys for git pull..."
    if ! setup_ssh_agent; then
        log_error "Failed to setup SSH keys"
        return 1
    fi
    
    echo -e "${BLUE}⬇️  Pulling from remote repository...${NC}"
    if [[ -n "$args" ]]; then
        git pull $args
    else
        git pull
    fi
    
    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        log_info "✅ Pull completed successfully"
    else
        log_error "❌ Pull failed with exit code $exit_code"
    fi
    
    return $exit_code
}

# Git commit
handle_git_commit() {
    local args="$1"
    
    if ! check_dev_mode; then
        return 1
    fi
    
    if [[ -z "$args" ]]; then
        log_error "Commit message required. Usage: COMMIT \"message\" [options]"
        return 1
    fi
    
    echo -e "${BLUE}📝 Creating commit...${NC}"
    git commit -m "$args"
    
    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        log_info "✅ Commit created successfully"
    else
        log_error "❌ Commit failed with exit code $exit_code"
    fi
    
    return $exit_code
}

# Git clone with SSH key support
handle_git_clone() {
    local args="$1"
    
    if ! check_dev_mode; then
        return 1
    fi
    
    if [[ -z "$args" ]]; then
        log_error "Repository URL required. Usage: CLONE <repository_url> [directory]"
        return 1
    fi
    
    log_info "Setting up SSH keys for git clone..."
    if ! setup_ssh_agent; then
        log_error "Failed to setup SSH keys"
        return 1
    fi
    
    echo -e "${BLUE}📥 Cloning repository...${NC}"
    git clone $args
    
    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        log_info "✅ Clone completed successfully"
    else
        log_error "❌ Clone failed with exit code $exit_code"
    fi
    
    return $exit_code
}

# Git branch operations
handle_git_branch() {
    local args="$1"
    
    if ! check_dev_mode; then
        return 1
    fi
    
    if [[ -z "$args" ]]; then
        git branch
        return
    fi
    
    local operation=$(echo "$args" | awk '{print $1}' | tr '[:lower:]' '[:upper:]')
    local branch_name=""
    if [[ "$args" == *" "* ]]; then
        branch_name=$(echo "$args" | cut -d' ' -f2-)
    fi
    
    case "$operation" in
        LIST)
            git branch -a
            ;;
        CREATE)
            if [[ -n "$branch_name" ]]; then
                git checkout -b "$branch_name"
            else
                log_error "Branch name required for CREATE operation"
            fi
            ;;
        SWITCH|CHECKOUT)
            if [[ -n "$branch_name" ]]; then
                git checkout "$branch_name"
            else
                log_error "Branch name required for SWITCH operation"
            fi
            ;;
        DELETE)
            if [[ -n "$branch_name" ]]; then
                git branch -d "$branch_name"
            else
                log_error "Branch name required for DELETE operation"
            fi
            ;;
        *)
            git branch $args
            ;;
    esac
}

# Git merge
handle_git_merge() {
    local args="$1"
    
    if ! check_dev_mode; then
        return 1
    fi
    
    if [[ -z "$args" ]]; then
        log_error "Branch name required. Usage: MERGE <branch> [options]"
        return 1
    fi
    
    echo -e "${BLUE}🔄 Merging branch...${NC}"
    git merge $args
    
    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        log_info "✅ Merge completed successfully"
    else
        log_error "❌ Merge failed with exit code $exit_code"
    fi
    
    return $exit_code
}

# Git rebase
handle_git_rebase() {
    local args="$1"
    
    if ! check_dev_mode; then
        return 1
    fi
    
    if [[ -z "$args" ]]; then
        log_error "Branch name required. Usage: REBASE <branch> [options]"
        return 1
    fi
    
    echo -e "${BLUE}🔄 Rebasing onto branch...${NC}"
    git rebase $args
    
    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        log_info "✅ Rebase completed successfully"
    else
        log_error "❌ Rebase failed with exit code $exit_code"
    fi
    
    return $exit_code
}

# Git stash operations
handle_git_stash() {
    local args="$1"
    
    if ! check_dev_mode; then
        return 1
    fi
    
    if [[ -z "$args" ]]; then
        git stash
        return
    fi
    
    local operation=$(echo "$args" | awk '{print $1}' | tr '[:lower:]' '[:upper:]')
    local rest_args=""
    if [[ "$args" == *" "* ]]; then
        rest_args=$(echo "$args" | cut -d' ' -f2-)
    fi
    
    case "$operation" in
        SAVE)
            git stash save "$rest_args"
            ;;
        POP)
            git stash pop
            ;;
        LIST)
            git stash list
            ;;
        DROP)
            git stash drop $rest_args
            ;;
        CLEAR)
            git stash clear
            ;;
        SHOW)
            git stash show $rest_args
            ;;
        *)
            git stash $args
            ;;
    esac
}

# Git remote operations
handle_git_remote() {
    local args="$1"
    
    if ! check_dev_mode; then
        return 1
    fi
    
    if [[ -z "$args" ]]; then
        git remote -v
        return
    fi
    
    local operation=$(echo "$args" | awk '{print $1}' | tr '[:lower:]' '[:upper:]')
    local remote_name=""
    local remote_url=""
    
    if [[ "$args" == *" "* ]]; then
        remote_name=$(echo "$args" | awk '{print $2}')
        if [[ "$args" =~ [[:space:]][^[:space:]]+[[:space:]] ]]; then
            remote_url=$(echo "$args" | awk '{print $3}')
        fi
    fi
    
    case "$operation" in
        ADD)
            if [[ -n "$remote_name" && -n "$remote_url" ]]; then
                git remote add "$remote_name" "$remote_url"
            else
                log_error "Remote name and URL required. Usage: REMOTE ADD <name> <url>"
            fi
            ;;
        REMOVE|RM)
            if [[ -n "$remote_name" ]]; then
                git remote remove "$remote_name"
            else
                log_error "Remote name required. Usage: REMOTE REMOVE <name>"
            fi
            ;;
        SET-URL)
            if [[ -n "$remote_name" && -n "$remote_url" ]]; then
                git remote set-url "$remote_name" "$remote_url"
            else
                log_error "Remote name and URL required. Usage: REMOTE SET-URL <name> <url>"
            fi
            ;;
        *)
            git remote $args
            ;;
    esac
}

# SSH key management
handle_ssh_key() {
    local args="$1"
    
    if ! check_dev_mode; then
        return 1
    fi
    
    local ssh_dir=$(get_ssh_dir)
    
    if [[ -z "$args" ]]; then
        log_error "SSH key operation required. Usage: SSH-KEY <operation> [options]"
        echo "Available operations: GENERATE, LIST, ADD, TEST, REMOVE"
        return 1
    fi
    
    local operation=$(echo "$args" | awk '{print $1}' | tr '[:lower:]' '[:upper:]')
    local key_name=""
    if [[ "$args" == *" "* ]]; then
        key_name=$(echo "$args" | cut -d' ' -f2-)
    fi
    
    case "$operation" in
        GENERATE|GEN)
            if [[ -z "$key_name" ]]; then
                key_name="id_rsa"
            fi
            
            local key_path="$ssh_dir/$key_name"
            if [[ -f "$key_path" ]]; then
                log_warning "SSH key already exists: $key_path"
                read -p "Overwrite? (y/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    log_info "SSH key generation cancelled"
                    return 0
                fi
            fi
            
            mkdir -p "$ssh_dir"
            echo -e "${BLUE}🔑 Generating SSH key: $key_name${NC}"
            ssh-keygen -t rsa -b 4096 -f "$key_path" -N ""
            
            if [[ -f "$key_path" ]]; then
                chmod 600 "$key_path"
                chmod 644 "$key_path.pub"
                log_info "✅ SSH key generated: $key_path"
                echo "Public key:"
                cat "$key_path.pub"
            else
                log_error "❌ Failed to generate SSH key"
            fi
            ;;
        LIST)
            echo -e "${BLUE}🔑 SSH Keys in $ssh_dir:${NC}"
            if [[ -d "$ssh_dir" ]]; then
                local count=0
                for key in "$ssh_dir"/id_*; do
                    if [[ -f "$key" && ! "$key" == *.pub ]]; then
                        local pub_key="${key}.pub"
                        echo "  🔐 $(basename "$key")"
                        if [[ -f "$pub_key" ]]; then
                            echo "  🔓 $(basename "$pub_key")"
                        fi
                        ((count++))
                    fi
                done
                if [[ $count -eq 0 ]]; then
                    echo "  No SSH keys found"
                fi
            else
                echo "  SSH directory not found: $ssh_dir"
            fi
            ;;
        ADD)
            if [[ -z "$key_name" ]]; then
                key_name="id_rsa"
            fi
            
            local key_path="$ssh_dir/$key_name"
            if [[ -f "$key_path" ]]; then
                ssh-add "$key_path"
                log_info "✅ SSH key added to agent: $key_name"
            else
                log_error "SSH key not found: $key_path"
            fi
            ;;
        TEST)
            if [[ -z "$key_name" ]]; then
                key_name="git@github.com"
            fi
            
            echo -e "${BLUE}🧪 Testing SSH connection to $key_name...${NC}"
            setup_ssh_agent
            ssh -T "$key_name"
            ;;
        REMOVE|RM)
            if [[ -z "$key_name" ]]; then
                log_error "Key name required. Usage: SSH-KEY REMOVE <key_name>"
                return 1
            fi
            
            local key_path="$ssh_dir/$key_name"
            if [[ -f "$key_path" ]]; then
                read -p "Remove SSH key $key_name? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    rm -f "$key_path" "$key_path.pub"
                    log_info "✅ SSH key removed: $key_name"
                else
                    log_info "SSH key removal cancelled"
                fi
            else
                log_error "SSH key not found: $key_path"
            fi
            ;;
        *)
            log_error "Unknown SSH key operation: $operation"
            echo "Available operations: GENERATE, LIST, ADD, TEST, REMOVE"
            ;;
    esac
}

# Run main function
main "$@"
