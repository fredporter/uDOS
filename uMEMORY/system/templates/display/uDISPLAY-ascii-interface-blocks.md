````markdown
# uDOS ASCII Interface Blocks Template

**Template**: uDISPLAY-ascii-interface-blocks.md
**Version**: v1.0.4.1
**Purpose**: Block-oriented ASCII interface components for responsive display
**Integration**: uGRID, uCELL, display system, three-mode architecture

---

## 🎨 Template System Variables

### Display Configuration Integration
```bash
# Auto-detected display configuration (from display-config.sh)
UDOS_TERMINAL_COLS="${UDOS_TERMINAL_COLS:-80}"
UDOS_TERMINAL_ROWS="${UDOS_TERMINAL_ROWS:-24}"
UDOS_DISPLAY_MODE="${UDOS_DISPLAY_MODE:-compact}"
UDOS_VIEWPORT_COLS="${UDOS_VIEWPORT_COLS:-60}"
UDOS_VIEWPORT_ROWS="${UDOS_VIEWPORT_ROWS:-20}"
UDOS_DASH_COLS="${UDOS_DASH_COLS:-20}"
UDOS_DASH_ROWS="${UDOS_DASH_ROWS:-20}"
UDOS_DASH_POSITION="${UDOS_DASH_POSITION:-bottom}"
UDOS_GRID_MODE="${UDOS_GRID_MODE:-standard}"
UDOS_BLOCK_WIDTH="${UDOS_BLOCK_WIDTH:-40}"
UDOS_BLOCK_HEIGHT="${UDOS_BLOCK_HEIGHT:-8}"
UDOS_BORDER_STYLE="${UDOS_BORDER_STYLE:-single}"
```

### Border Character Sets
```bash
# Single-line borders
UDOS_BORDER_TL="┌"      # Top-left
UDOS_BORDER_TR="┐"      # Top-right
UDOS_BORDER_BL="└"      # Bottom-left
UDOS_BORDER_BR="┘"      # Bottom-right
UDOS_BORDER_H="─"       # Horizontal
UDOS_BORDER_V="│"       # Vertical
UDOS_BORDER_L="├"       # Left junction
UDOS_BORDER_R="┤"       # Right junction

# Double-line borders
UDOS_BORDER_DOUBLE_TL="╔"
UDOS_BORDER_DOUBLE_TR="╗"
UDOS_BORDER_DOUBLE_BL="╚"
UDOS_BORDER_DOUBLE_BR="╝"
UDOS_BORDER_DOUBLE_H="═"
UDOS_BORDER_DOUBLE_V="║"

# Block characters
UDOS_BLOCK_FULL="█"
UDOS_BLOCK_LIGHT="░"
UDOS_BLOCK_MEDIUM="▒"
UDOS_BLOCK_DARK="▓"
```

---

## 🧱 Core Block Components

### Header Block Template
```bash
# Usage: render_header_block "Title Text"
render_header_block() {
    local title="$1"
    local width="${UDOS_BLOCK_WIDTH:-60}"
    local padding=$(( (width - ${#title} - 4) / 2 ))

    echo "${UDOS_BORDER_DOUBLE_TL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_DOUBLE_H}")${UDOS_BORDER_DOUBLE_TR}"
    echo "${UDOS_BORDER_DOUBLE_V}$(printf "%*s" $padding "")${title}$(printf "%*s" $((width-${#title}-padding-2)) "")${UDOS_BORDER_DOUBLE_V}"
    echo "${UDOS_BORDER_DOUBLE_BL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_DOUBLE_H}")${UDOS_BORDER_DOUBLE_BR}"
}
```

### Status Block Template
```bash
# Usage: render_status_block "Label" "Value" "Progress%"
render_status_block() {
    local label="$1"
    local value="$2"
    local progress="${3:-0}"
    local width="${UDOS_BLOCK_WIDTH:-40}"
    local progress_width=$(( width - 20 ))
    local filled=$(( progress * progress_width / 100 ))
    local empty=$(( progress_width - filled ))

    echo "${UDOS_BORDER_TL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_H}")${UDOS_BORDER_TR}"
    echo "${UDOS_BORDER_V} 🟢 ${label}: ${value}$(printf "%*s" $((width-${#label}-${#value}-8)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V} 📊 Progress: [$(printf "%*s" $filled "" | tr ' ' "${UDOS_BLOCK_FULL}")$(printf "%*s" $empty "" | tr ' ' "${UDOS_BLOCK_LIGHT}")] ${progress}%$(printf "%*s" $((width-progress_width-18)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_BL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_H}")${UDOS_BORDER_BR}"
}
```

### Input Form Block Template
```bash
# Usage: render_input_form "Title" "Label1" "Value1" "Label2" "Value2" "Button1" "Button2"
render_input_form() {
    local form_title="$1"
    local label1="$2"
    local value1="$3"
    local label2="$4"
    local value2="$5"
    local button1="$6"
    local button2="$7"
    local width="${UDOS_BLOCK_WIDTH:-50}"
    local input_width="${UDOS_INPUT_WIDTH:-20}"
    local button_width="${UDOS_BUTTON_WIDTH:-10}"

    echo "${UDOS_BORDER_DOUBLE_TL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_DOUBLE_H}")${UDOS_BORDER_DOUBLE_TR}"
    echo "${UDOS_BORDER_DOUBLE_V} ${form_title}$(printf "%*s" $((width-${#form_title}-3)) "")${UDOS_BORDER_DOUBLE_V}"
    echo "${UDOS_BORDER_L}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_H}")${UDOS_BORDER_R}"
    echo "${UDOS_BORDER_V}$(printf "%*s" $((width-2)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V} ${label1}: [${value1}$(printf "%*s" $((input_width-${#value1})) "")]$(printf "%*s" $((width-input_width-${#label1}-7)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V} ${label2}: [${value2}$(printf "%*s" $((input_width-${#value2})) "")]$(printf "%*s" $((width-input_width-${#label2}-7)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V}$(printf "%*s" $((width-2)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V}   [${button1}$(printf "%*s" $((button_width-${#button1}-2)) "")]  [${button2}$(printf "%*s" $((button_width-${#button2}-2)) "")]$(printf "%*s" $((width-button_width*2-8)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V}$(printf "%*s" $((width-2)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_DOUBLE_BL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_DOUBLE_H}")${UDOS_BORDER_DOUBLE_BR}"
}
```

### Grid Map Block Template
```bash
# Usage: render_grid_map "Position" "Row1" "Row2" "Row3"
render_grid_map() {
    local position="$1"
    local row1="$2"
    local row2="$3"
    local row3="$4"
    local width="${UDOS_BLOCK_WIDTH:-40}"

    echo "${UDOS_BORDER_TL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_H}")${UDOS_BORDER_TR}"
    echo "${UDOS_BORDER_V} 🗺️  Grid Position: ${position}$(printf "%*s" $((width-${#position}-20)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_L}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_H}")${UDOS_BORDER_R}"
    echo "${UDOS_BORDER_V}$(printf "%*s" $((width-2)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V}   ${row1}$(printf "%*s" $((width-${#row1}-5)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V}   ${row2}$(printf "%*s" $((width-${#row2}-5)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V}   ${row3}$(printf "%*s" $((width-${#row3}-5)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V}$(printf "%*s" $((width-2)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_BL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_H}")${UDOS_BORDER_BR}"
}
```

### Progress Meter Block Template
```bash
# Usage: render_progress_meter "Label" "Percentage"
render_progress_meter() {
    local label="$1"
    local percentage="$2"
    local width="${UDOS_BLOCK_WIDTH:-40}"
    local progress_width="${UDOS_PROGRESS_WIDTH:-20}"
    local filled=$(( percentage * progress_width / 100 ))
    local empty=$(( progress_width - filled ))

    echo "${UDOS_BORDER_TL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_H}")${UDOS_BORDER_TR}"
    echo "${UDOS_BORDER_V} 📈 ${label}$(printf "%*s" $((width-${#label}-6)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V}$(printf "%*s" $((width-2)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V} [$(printf "%*s" $filled "" | tr ' ' "${UDOS_BLOCK_FULL}")$(printf "%*s" $empty "" | tr ' ' "${UDOS_BLOCK_LIGHT}")] ${percentage}%$(printf "%*s" $((width-progress_width-8)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V}$(printf "%*s" $((width-2)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_BL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_H}")${UDOS_BORDER_BR}"
}
```

### Menu Selection Block Template
```bash
# Usage: render_menu "Title" "Item1" "Selected1" "Item2" "Selected2" "Item3" "Selected3"
render_menu() {
    local menu_title="$1"
    local item1="$2"
    local selected1="$3"
    local item2="$4"
    local selected2="$5"
    local item3="$6"
    local selected3="$7"
    local width="${UDOS_BLOCK_WIDTH:-40}"

    local sel1="$([[ "$selected1" == "true" ]] && echo "●" || echo "○")"
    local sel2="$([[ "$selected2" == "true" ]] && echo "●" || echo "○")"
    local sel3="$([[ "$selected3" == "true" ]] && echo "●" || echo "○")"

    echo "${UDOS_BORDER_DOUBLE_TL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_DOUBLE_H}")${UDOS_BORDER_DOUBLE_TR}"
    echo "${UDOS_BORDER_DOUBLE_V} 🎯 ${menu_title}$(printf "%*s" $((width-${#menu_title}-6)) "")${UDOS_BORDER_DOUBLE_V}"
    echo "${UDOS_BORDER_L}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_DOUBLE_H}")${UDOS_BORDER_R}"
    echo "${UDOS_BORDER_V}$(printf "%*s" $((width-2)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V} ${sel1} ${item1}$(printf "%*s" $((width-${#item1}-6)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V} ${sel2} ${item2}$(printf "%*s" $((width-${#item2}-6)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V} ${sel3} ${item3}$(printf "%*s" $((width-${#item3}-6)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V}$(printf "%*s" $((width-2)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_DOUBLE_BL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_DOUBLE_H}")${UDOS_BORDER_DOUBLE_BR}"
}
```

### Dashboard Summary Block Template
```bash
# Usage: render_dashboard "Username" "Position" "Mission" "Moves" "Health%"
render_dashboard() {
    local username="$1"
    local position="$2"
    local mission="$3"
    local moves="$4"
    local health="$5"
    local width="${UDOS_BLOCK_WIDTH:-50}"
    local health_width=15
    local health_filled=$(( health * health_width / 100 ))
    local health_empty=$(( health_width - health_filled ))

    echo "${UDOS_BORDER_DOUBLE_TL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_DOUBLE_H}")${UDOS_BORDER_DOUBLE_TR}"
    echo "${UDOS_BORDER_DOUBLE_V} 🌀 uDOS Dashboard$(printf "%*s" $((width-18)) "")${UDOS_BORDER_DOUBLE_V}"
    echo "${UDOS_BORDER_L}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_DOUBLE_H}")${UDOS_BORDER_R}"
    echo "${UDOS_BORDER_V} 👤 User: ${username}$(printf "%*s" $((width-${#username}-10)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V} 📍 Position: ${position}$(printf "%*s" $((width-${#position}-15)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V} 🎯 Mission: ${mission}$(printf "%*s" $((width-${#mission}-13)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V} 🧭 Moves: ${moves}$(printf "%*s" $((width-${#moves}-12)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_V} 💚 Health: [$(printf "%*s" $health_filled "" | tr ' ' "${UDOS_BLOCK_FULL}")$(printf "%*s" $health_empty "" | tr ' ' "${UDOS_BLOCK_LIGHT}")] ${health}%$(printf "%*s" $((width-health_width-15)) "")${UDOS_BORDER_V}"
    echo "${UDOS_BORDER_DOUBLE_BL}$(printf "%*s" $((width-2)) "" | tr ' ' "${UDOS_BORDER_DOUBLE_H}")${UDOS_BORDER_DOUBLE_BR}"
}
```

---

## 📐 Layout Templates

### Full Screen Layout (Dashboard Bottom)
```bash
# Usage: render_full_screen_bottom "viewport_content" "dashboard_content"
render_full_screen_bottom() {
    local viewport_content="$1"
    local dashboard_content="$2"

    # Render viewport area
    echo "$viewport_content"
    echo

    # Render separator
    printf "%*s\n" "$UDOS_DASH_COLS" "" | tr ' ' "─"

    # Render dashboard area
    echo "$dashboard_content"
}
```

### Split Screen Layout (Dashboard Right)
```bash
# Usage: render_split_screen_right "viewport_lines" "dashboard_lines"
render_split_screen_right() {
    local IFS=$'\n'
    local viewport_lines=($1)
    local dashboard_lines=($2)
    local max_lines=${#viewport_lines[@]}

    for ((i=0; i<max_lines; i++)); do
        local viewport_line="${viewport_lines[i]}"
        local dashboard_line="${dashboard_lines[i]}"
        printf "%-*s %s %s\n" "$UDOS_VIEWPORT_COLS" "$viewport_line" "$UDOS_BORDER_V" "$dashboard_line"
    done
}
```

### Compact Layout (Minimal Dashboard)
```bash
# Usage: render_compact "header" "content" "status"
render_compact() {
    local header="$1"
    local content="$2"
    local status="$3"

    echo "$header"
    echo
    echo "$content"
    echo
    echo "$status"
}
```

---

## 🎨 Color and Style Integration

### Polaroid Color Scheme
```bash
# ANSI Color Codes (from uCORE/system/polaroid-colors.sh)
HEADER_COLOR="\033[1;36m"     # Bright Cyan
STATUS_COLOR="\033[1;32m"     # Bright Green
WARNING_COLOR="\033[1;33m"    # Bright Yellow
ERROR_COLOR="\033[1;31m"      # Bright Red
INFO_COLOR="\033[1;34m"       # Bright Blue
RESET_COLOR="\033[0m"         # Reset
BOLD="\033[1m"               # Bold
DIM="\033[2m"                # Dim
```

### Role-Based Color Coding
```bash
get_role_color() {
    local role="$1"
    case "$role" in
        "GHOST") echo "\033[2;37m" ;;    # Dim White
        "TOMB") echo "\033[0;37m" ;;     # White
        "CRYPT") echo "\033[1;37m" ;;    # Bright White
        "DRONE") echo "\033[1;34m" ;;    # Bright Blue
        "KNIGHT") echo "\033[1;32m" ;;   # Bright Green
        "IMP") echo "\033[1;33m" ;;      # Bright Yellow
        "SORCERER") echo "\033[1;35m" ;; # Bright Magenta
        "WIZARD") echo "\033[1;31m" ;;   # Bright Red
        *) echo "\033[0m" ;;             # Reset
    esac
}
```

### Responsive Block Sizing
```bash
set_responsive_blocks() {
    case "$UDOS_DISPLAY_MODE" in
        "ultra"|"mega")
            UDOS_BLOCK_WIDTH=80
            UDOS_BLOCK_HEIGHT=12
            ;;
        "full"|"wide")
            UDOS_BLOCK_WIDTH=60
            UDOS_BLOCK_HEIGHT=10
            ;;
        "compact"|*)
            UDOS_BLOCK_WIDTH=40
            UDOS_BLOCK_HEIGHT=8
            ;;
    esac
}
```

---

## 🚀 Usage Examples

### Simple Status Display
```bash
# Initialize display configuration
source "$UMEMORY/config/display-vars.sh"

# Render status block
render_status_block "System" "Online" "85"
```

### Interactive Menu
```bash
# Render menu with selections
render_menu "Main Menu" "Option 1" "true" "Option 2" "false" "Option 3" "false"
```

### System Dashboard
```bash
# Get system information
username="$(whoami)"
position="A1-B2"
mission="Development Phase"
moves="127"
health="92"

# Render dashboard
render_dashboard "$username" "$position" "$mission" "$moves" "$health"
```

### Progress Tracking
```bash
# Show progress meter
render_progress_meter "Mission Progress" "67"
```

---

## 🔧 Integration Points

### uCode Command Integration
```bash
# Commands that use this template system:
# ucode DASHBOARD    → Uses render_dashboard
# ucode SETUP        → Uses render_input_form
# ucode MAP          → Uses render_grid_map
# ucode STATUS       → Uses render_status_block
# ucode MENU         → Uses render_menu
```

### Display System Integration
```bash
# Three-mode display support:
# CLI Terminal      → ASCII blocks only
# Desktop App       → Enhanced ASCII with fonts
# Web Export        → HTML conversion with CSS
```

### VS Code Task Integration
```bash
# VS Code tasks automatically:
# - Detect terminal size changes
# - Refresh display configuration
# - Re-render ASCII blocks with new dimensions
# - Maintain consistent visual appearance
```

---

## 📱 Template Processing

### Variable Substitution
```bash
# Process template with variables
process_template() {
    local template="$1"
    local output_file="$2"

    # Source display configuration
    source "$UMEMORY/config/display-vars.sh"

    # Set responsive sizing
    set_responsive_blocks

    # Process template
    envsubst < "$template" > "$output_file"
}
```

### Dynamic Content Generation
```bash
# Generate content based on context
generate_dynamic_content() {
    local context="$1"

    case "$context" in
        "dashboard")
            render_dashboard "$(get_username)" "$(get_position)" "$(get_mission)" "$(get_moves)" "$(get_health)"
            ;;
        "status")
            render_status_block "$(get_status_label)" "$(get_status_value)" "$(get_progress)"
            ;;
        "menu")
            render_menu "$(get_menu_title)" "$(get_menu_items)"
            ;;
    esac
}
```

---

*uDOS v1.0.4.1 Display Template - ASCII Interface Blocks*
*Responsive block-oriented components for three-mode display architecture*

````
