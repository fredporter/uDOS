#!/bin/bash
# uDOS v1.0 - Display Configuration System
# 🖥️ display-config.sh — Terminal sizing, ASCII layout, and grid management
# v2.0 - Template System Integration with Block-Oriented Interface

set -euo pipefail

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
DISPLAY_CONFIG="${UMEM}/config/display.conf"
DISPLAY_VARS="${UMEM}/config/display-vars.sh"

# Color helpers for enhanced visibility
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }
dim() { echo -e "\033[2m$1\033[0m"; }

# Block characters for enhanced ASCII interface
BLOCK_FULL="█"
BLOCK_LIGHT="░"
BLOCK_MEDIUM="▒"
BLOCK_DARK="▓"
BLOCK_TOP="▀"
BLOCK_BOTTOM="▄"
BLOCK_LEFT="▌"
BLOCK_RIGHT="▐"

# Border characters for clean interfaces
BORDER_H="─"
BORDER_V="│"
BORDER_TL="┌"
BORDER_TR="┐"
BORDER_BL="└"
BORDER_BR="┘"
BORDER_CROSS="┼"
BORDER_T="┬"
BORDER_B="┴"
BORDER_L="├"
BORDER_R="┤"

# Enhanced border characters for headers
BORDER_DOUBLE_H="═"
BORDER_DOUBLE_V="║"
BORDER_DOUBLE_TL="╔"
BORDER_DOUBLE_TR="╗"
BORDER_DOUBLE_BL="╚"
BORDER_DOUBLE_BR="╝"

# Initialize display configuration
init_display_config() {
    bold "🖥️  Initializing uDOS Display Configuration System v2.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Create config directory if needed
    mkdir -p "${UMEM}/config"
    
    # Detect current terminal size
    detect_terminal_size
    
    # Determine optimal display mode
    determine_display_mode
    
    # Configure grid system
    configure_grid_system
    
    # Set up ASCII interface parameters
    configure_ascii_interface
    
    # Generate display variables
    generate_display_variables
    
    green "✅ Display configuration initialized"
    show_display_summary
}

# Detect terminal size using multiple methods
detect_terminal_size() {
    cyan "🔍 Detecting terminal size..."
    
    local cols rows
    
    # Method 1: tput (most reliable)
    if command -v tput >/dev/null 2>&1; then
        cols=$(tput cols 2>/dev/null || echo "")
        rows=$(tput lines 2>/dev/null || echo "")
    fi
    
    # Method 2: stty size (fallback)
    if [[ -z "$cols" ]] || [[ -z "$rows" ]]; then
        if command -v stty >/dev/null 2>&1; then
            local size_info
            size_info=$(stty size 2>/dev/null || echo "")
            if [[ -n "$size_info" ]]; then
                rows=$(echo "$size_info" | cut -d' ' -f1)
                cols=$(echo "$size_info" | cut -d' ' -f2)
            fi
        fi
    fi
    
    # Method 3: Environment variables (second fallback)
    if [[ -z "$cols" ]] || [[ -z "$rows" ]]; then
        cols="${COLUMNS:-80}"
        rows="${LINES:-24}"
    fi
    
    # Method 4: Default minimums (final fallback)
    cols="${cols:-80}"
    rows="${rows:-24}"
    
    # Validate and constrain values
    if [[ "$cols" -lt 40 ]]; then
        yellow "⚠️  Terminal width too small ($cols), setting minimum: 40"
        cols=40
    fi
    
    if [[ "$rows" -lt 20 ]]; then
        yellow "⚠️  Terminal height too small ($rows), setting minimum: 20"
        rows=20
    fi
    
    # Store detected values
    export UDOS_TERMINAL_COLS="$cols"
    export UDOS_TERMINAL_ROWS="$rows"
    
    echo "  📐 Detected: ${cols} × ${rows} characters"
}

# Determine optimal display mode based on terminal size
determine_display_mode() {
    cyan "📊 Determining optimal display mode..."
    
    local cols="$UDOS_TERMINAL_COLS"
    local rows="$UDOS_TERMINAL_ROWS"
    local mode viewport_cols viewport_rows dash_cols dash_rows dash_position
    
    # Match against predefined display modes (from 004-uDOS-interface.md)
    if [[ "$cols" -ge 640 ]] && [[ "$rows" -ge 480 ]]; then
        mode="ultra"
        viewport_cols=640
        viewport_rows=420
        dash_cols=640
        dash_rows=60
        dash_position="bottom"
    elif [[ "$cols" -ge 640 ]] && [[ "$rows" -ge 360 ]]; then
        mode="mega"
        viewport_cols=560
        viewport_rows=360
        dash_cols=80
        dash_rows=360
        dash_position="right"
    elif [[ "$cols" -ge 320 ]] && [[ "$rows" -ge 240 ]]; then
        mode="full"
        viewport_cols=320
        viewport_rows=180
        dash_cols=320
        dash_rows=60
        dash_position="bottom"
    elif [[ "$cols" -ge 320 ]] && [[ "$rows" -ge 180 ]]; then
        mode="wide"
        viewport_cols=240
        viewport_rows=180
        dash_cols=80
        dash_rows=180
        dash_position="right"
    elif [[ "$cols" -ge 160 ]] && [[ "$rows" -ge 120 ]]; then
        mode="console"
        viewport_cols=160
        viewport_rows=90
        dash_cols=160
        dash_rows=30
        dash_position="bottom"
    elif [[ "$cols" -ge 160 ]] && [[ "$rows" -ge 90 ]]; then
        mode="compact"
        viewport_cols=120
        viewport_rows=90
        dash_cols=40
        dash_rows=90
        dash_position="right"
    elif [[ "$cols" -ge 80 ]] && [[ "$rows" -ge 60 ]]; then
        mode="mini"
        viewport_cols=80
        viewport_rows=45
        dash_cols=80
        dash_rows=15
        dash_position="bottom"
    else
        mode="micro"
        viewport_cols=80
        viewport_rows=30
        dash_cols=80
        dash_rows=15
        dash_position="bottom"
    fi
    
    # Store display mode configuration
    export UDOS_DISPLAY_MODE="$mode"
    export UDOS_VIEWPORT_COLS="$viewport_cols"
    export UDOS_VIEWPORT_ROWS="$viewport_rows"
    export UDOS_DASH_COLS="$dash_cols"
    export UDOS_DASH_ROWS="$dash_rows"
    export UDOS_DASH_POSITION="$dash_position"
    
    echo "  🎯 Selected mode: $mode (${viewport_cols}×${viewport_rows} viewport + ${dash_cols}×${dash_rows} dashboard $dash_position)"
}

# Configure grid system for coordinate mapping
configure_grid_system() {
    cyan "🗺️  Configuring grid coordinate system..."
    
    # Grid system uses A-Z columns (26) and 1-99 rows (99) = 2,574 total positions
    # Enhanced for larger displays: AA-ZZ columns (676) and 01-99 rows (99) = 66,924 positions
    local grid_mode
    
    if [[ "$UDOS_VIEWPORT_COLS" -ge 320 ]]; then
        grid_mode="extended"  # AA-ZZ, 01-99 (676×99)
        export UDOS_GRID_COLS_MAX=676
        export UDOS_GRID_ROWS_MAX=99
        export UDOS_GRID_FORMAT="extended"  # AA14, BX99, etc.
    else
        grid_mode="standard"  # A-Z, 1-99 (26×99)
        export UDOS_GRID_COLS_MAX=26
        export UDOS_GRID_ROWS_MAX=99
        export UDOS_GRID_FORMAT="standard"  # A14, B99, etc.
    fi
    
    # Calculate grid cell size in characters
    local cell_width=$((UDOS_VIEWPORT_COLS / 20))  # Divide viewport into ~20 columns
    local cell_height=$((UDOS_VIEWPORT_ROWS / 15))  # Divide viewport into ~15 rows
    
    export UDOS_GRID_CELL_WIDTH="$cell_width"
    export UDOS_GRID_CELL_HEIGHT="$cell_height"
    export UDOS_GRID_MODE="$grid_mode"
    
    echo "  🎲 Grid: $grid_mode mode (${UDOS_GRID_COLS_MAX}×${UDOS_GRID_ROWS_MAX} positions)"
    echo "  📏 Cell size: ${cell_width}×${cell_height} characters"
}

# Configure ASCII interface parameters
configure_ascii_interface() {
    cyan "🎨 Configuring ASCII interface parameters..."
    
    # Block sizing based on display mode
    local block_width block_height border_style
    
    case "$UDOS_DISPLAY_MODE" in
        "ultra"|"mega"|"full"|"wide")
            block_width=60
            block_height=8
            border_style="double"
            ;;
        "console"|"compact")
            block_width=40
            block_height=6
            border_style="single"
            ;;
        "mini"|"micro")
            block_width=30
            block_height=4
            border_style="minimal"
            ;;
        *)
            block_width=40
            block_height=6
            border_style="single"
            ;;
    esac
    
    # Input field dimensions
    local input_width=$((block_width - 4))  # Account for borders
    local button_width=12
    local label_width=20
    
    # Progress bar configuration
    local progress_width=$((block_width - 8))
    local progress_chars="▓▒░"
    
    # Store ASCII interface configuration
    export UDOS_BLOCK_WIDTH="$block_width"
    export UDOS_BLOCK_HEIGHT="$block_height"
    export UDOS_BORDER_STYLE="$border_style"
    export UDOS_INPUT_WIDTH="$input_width"
    export UDOS_BUTTON_WIDTH="$button_width"
    export UDOS_LABEL_WIDTH="$label_width"
    export UDOS_PROGRESS_WIDTH="$progress_width"
    export UDOS_PROGRESS_CHARS="$progress_chars"
    
    echo "  🧱 Block size: ${block_width}×${block_height} ($border_style borders)"
    echo "  📝 Input width: $input_width characters"
    echo "  🔘 Button width: $button_width characters"
}

# Generate display variables file
generate_display_variables() {
    cyan "📝 Generating display configuration variables..."
    
    cat > "$DISPLAY_VARS" << 'VARS_EOF'
#!/bin/bash
# uDOS Display Configuration Variables
# Generated automatically by display-config.sh
# DO NOT EDIT MANUALLY

# Terminal Detection
export UDOS_TERMINAL_COLS="$UDOS_TERMINAL_COLS"
export UDOS_TERMINAL_ROWS="$UDOS_TERMINAL_ROWS"

# Display Mode Configuration
export UDOS_DISPLAY_MODE="$UDOS_DISPLAY_MODE"
export UDOS_VIEWPORT_COLS="$UDOS_VIEWPORT_COLS"
export UDOS_VIEWPORT_ROWS="$UDOS_VIEWPORT_ROWS"
export UDOS_DASH_COLS="$UDOS_DASH_COLS"
export UDOS_DASH_ROWS="$UDOS_DASH_ROWS"
export UDOS_DASH_POSITION="$UDOS_DASH_POSITION"

# Grid System Configuration
export UDOS_GRID_COLS_MAX="$UDOS_GRID_COLS_MAX"
export UDOS_GRID_ROWS_MAX="$UDOS_GRID_ROWS_MAX"
export UDOS_GRID_FORMAT="$UDOS_GRID_FORMAT"
export UDOS_GRID_CELL_WIDTH="$UDOS_GRID_CELL_WIDTH"
export UDOS_GRID_CELL_HEIGHT="$UDOS_GRID_CELL_HEIGHT"
export UDOS_GRID_MODE="$UDOS_GRID_MODE"

# ASCII Interface Configuration
export UDOS_BLOCK_WIDTH="$UDOS_BLOCK_WIDTH"
export UDOS_BLOCK_HEIGHT="$UDOS_BLOCK_HEIGHT"
export UDOS_BORDER_STYLE="$UDOS_BORDER_STYLE"
export UDOS_INPUT_WIDTH="$UDOS_INPUT_WIDTH"
export UDOS_BUTTON_WIDTH="$UDOS_BUTTON_WIDTH"
export UDOS_LABEL_WIDTH="$UDOS_LABEL_WIDTH"
export UDOS_PROGRESS_WIDTH="$UDOS_PROGRESS_WIDTH"
export UDOS_PROGRESS_CHARS="$UDOS_PROGRESS_CHARS"

# Block Characters
export UDOS_BLOCK_FULL="█"
export UDOS_BLOCK_LIGHT="░"
export UDOS_BLOCK_MEDIUM="▒"
export UDOS_BLOCK_DARK="▓"
export UDOS_BLOCK_TOP="▀"
export UDOS_BLOCK_BOTTOM="▄"
export UDOS_BLOCK_LEFT="▌"
export UDOS_BLOCK_RIGHT="▐"

# Border Characters
export UDOS_BORDER_H="─"
export UDOS_BORDER_V="│"
export UDOS_BORDER_TL="┌"
export UDOS_BORDER_TR="┐"
export UDOS_BORDER_BL="└"
export UDOS_BORDER_BR="┘"
export UDOS_BORDER_CROSS="┼"
export UDOS_BORDER_T="┬"
export UDOS_BORDER_B="┴"
export UDOS_BORDER_L="├"
export UDOS_BORDER_R="┤"

# Enhanced Border Characters
export UDOS_BORDER_DOUBLE_H="═"
export UDOS_BORDER_DOUBLE_V="║"
export UDOS_BORDER_DOUBLE_TL="╔"
export UDOS_BORDER_DOUBLE_TR="╗"
export UDOS_BORDER_DOUBLE_BL="╚"
export UDOS_BORDER_DOUBLE_BR="╝"
VARS_EOF
    
    # Substitute actual values
    sed -i.bak \
        -e "s/\$UDOS_TERMINAL_COLS/$UDOS_TERMINAL_COLS/g" \
        -e "s/\$UDOS_TERMINAL_ROWS/$UDOS_TERMINAL_ROWS/g" \
        -e "s/\$UDOS_DISPLAY_MODE/$UDOS_DISPLAY_MODE/g" \
        -e "s/\$UDOS_VIEWPORT_COLS/$UDOS_VIEWPORT_COLS/g" \
        -e "s/\$UDOS_VIEWPORT_ROWS/$UDOS_VIEWPORT_ROWS/g" \
        -e "s/\$UDOS_DASH_COLS/$UDOS_DASH_COLS/g" \
        -e "s/\$UDOS_DASH_ROWS/$UDOS_DASH_ROWS/g" \
        -e "s/\$UDOS_DASH_POSITION/$UDOS_DASH_POSITION/g" \
        -e "s/\$UDOS_GRID_COLS_MAX/$UDOS_GRID_COLS_MAX/g" \
        -e "s/\$UDOS_GRID_ROWS_MAX/$UDOS_GRID_ROWS_MAX/g" \
        -e "s/\$UDOS_GRID_FORMAT/$UDOS_GRID_FORMAT/g" \
        -e "s/\$UDOS_GRID_CELL_WIDTH/$UDOS_GRID_CELL_WIDTH/g" \
        -e "s/\$UDOS_GRID_CELL_HEIGHT/$UDOS_GRID_CELL_HEIGHT/g" \
        -e "s/\$UDOS_GRID_MODE/$UDOS_GRID_MODE/g" \
        -e "s/\$UDOS_BLOCK_WIDTH/$UDOS_BLOCK_WIDTH/g" \
        -e "s/\$UDOS_BLOCK_HEIGHT/$UDOS_BLOCK_HEIGHT/g" \
        -e "s/\$UDOS_BORDER_STYLE/$UDOS_BORDER_STYLE/g" \
        -e "s/\$UDOS_INPUT_WIDTH/$UDOS_INPUT_WIDTH/g" \
        -e "s/\$UDOS_BUTTON_WIDTH/$UDOS_BUTTON_WIDTH/g" \
        -e "s/\$UDOS_LABEL_WIDTH/$UDOS_LABEL_WIDTH/g" \
        -e "s/\$UDOS_PROGRESS_WIDTH/$UDOS_PROGRESS_WIDTH/g" \
        -e "s/\$UDOS_PROGRESS_CHARS/$UDOS_PROGRESS_CHARS/g" \
        "$DISPLAY_VARS"
    
    rm -f "${DISPLAY_VARS}.bak"
    
    # Also create structured configuration file
    cat > "$DISPLAY_CONFIG" << EOF
[terminal]
cols=$UDOS_TERMINAL_COLS
rows=$UDOS_TERMINAL_ROWS

[display_mode]
mode=$UDOS_DISPLAY_MODE
viewport_cols=$UDOS_VIEWPORT_COLS
viewport_rows=$UDOS_VIEWPORT_ROWS
dash_cols=$UDOS_DASH_COLS
dash_rows=$UDOS_DASH_ROWS
dash_position=$UDOS_DASH_POSITION

[grid_system]
cols_max=$UDOS_GRID_COLS_MAX
rows_max=$UDOS_GRID_ROWS_MAX
format=$UDOS_GRID_FORMAT
cell_width=$UDOS_GRID_CELL_WIDTH
cell_height=$UDOS_GRID_CELL_HEIGHT
mode=$UDOS_GRID_MODE

[ascii_interface]
block_width=$UDOS_BLOCK_WIDTH
block_height=$UDOS_BLOCK_HEIGHT
border_style=$UDOS_BORDER_STYLE
input_width=$UDOS_INPUT_WIDTH
button_width=$UDOS_BUTTON_WIDTH
label_width=$UDOS_LABEL_WIDTH
progress_width=$UDOS_PROGRESS_WIDTH

[generated]
timestamp=$(date -Iseconds)
version=2.0
EOF
    
    echo "  💾 Variables saved to: $DISPLAY_VARS"
    echo "  ⚙️  Configuration saved to: $DISPLAY_CONFIG"
}

# Show display configuration summary
show_display_summary() {
    echo
    bold "📊 uDOS Display Configuration Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Create summary box using detected configuration
    case "$UDOS_BORDER_STYLE" in
        "double")
            local tl="$BORDER_DOUBLE_TL" tr="$BORDER_DOUBLE_TR"
            local bl="$BORDER_DOUBLE_BL" br="$BORDER_DOUBLE_BR"
            local h="$BORDER_DOUBLE_H" v="$BORDER_DOUBLE_V"
            ;;
        "single")
            local tl="$BORDER_TL" tr="$BORDER_TR"
            local bl="$BORDER_BL" br="$BORDER_BR"
            local h="$BORDER_H" v="$BORDER_V"
            ;;
        "minimal")
            local tl="+" tr="+" bl="+" br="+"
            local h="-" v="|"
            ;;
    esac
    
    # Build summary display
    local width=70
    printf "%s" "$tl"
    printf "%*s" $((width-2)) "" | tr ' ' "$h"
    printf "%s\n" "$tr"
    
    printf "%s %-66s %s\n" "$v" "🖥️  Terminal Size: ${UDOS_TERMINAL_COLS} × ${UDOS_TERMINAL_ROWS}" "$v"
    printf "%s %-66s %s\n" "$v" "🎯 Display Mode: $UDOS_DISPLAY_MODE" "$v"
    printf "%s %-66s %s\n" "$v" "📱 Viewport: ${UDOS_VIEWPORT_COLS} × ${UDOS_VIEWPORT_ROWS}" "$v"
    printf "%s %-66s %s\n" "$v" "📊 Dashboard: ${UDOS_DASH_COLS} × ${UDOS_DASH_ROWS} ($UDOS_DASH_POSITION)" "$v"
    printf "%s %-66s %s\n" "$v" "🗺️  Grid System: $UDOS_GRID_MODE (${UDOS_GRID_COLS_MAX}×${UDOS_GRID_ROWS_MAX})" "$v"
    printf "%s %-66s %s\n" "$v" "🧱 Block Size: ${UDOS_BLOCK_WIDTH} × ${UDOS_BLOCK_HEIGHT}" "$v"
    printf "%s %-66s %s\n" "$v" "🎨 Border Style: $UDOS_BORDER_STYLE" "$v"
    
    printf "%s" "$bl"
    printf "%*s" $((width-2)) "" | tr ' ' "$h"
    printf "%s\n" "$br"
    
    echo
    cyan "💡 To apply these settings, run: source $DISPLAY_VARS"
    echo
}

# Utility functions for ASCII interface elements

# Create a block header
create_block_header() {
    local title="$1"
    local width="${2:-$UDOS_BLOCK_WIDTH}"
    
    case "${UDOS_BORDER_STYLE:-single}" in
        "double")
            printf "%s" "$BORDER_DOUBLE_TL"
            printf "%*s" $((width-2)) "" | tr ' ' "$BORDER_DOUBLE_H"
            printf "%s\n" "$BORDER_DOUBLE_TR"
            printf "%s %*s %s\n" "$BORDER_DOUBLE_V" $((width-4)) "$title" "$BORDER_DOUBLE_V"
            printf "%s" "$BORDER_DOUBLE_BL"
            printf "%*s" $((width-2)) "" | tr ' ' "$BORDER_DOUBLE_H"
            printf "%s\n" "$BORDER_DOUBLE_BR"
            ;;
        "single")
            printf "%s" "$BORDER_TL"
            printf "%*s" $((width-2)) "" | tr ' ' "$BORDER_H"
            printf "%s\n" "$BORDER_TR"
            printf "%s %*s %s\n" "$BORDER_V" $((width-4)) "$title" "$BORDER_V"
            printf "%s" "$BORDER_BL"
            printf "%*s" $((width-2)) "" | tr ' ' "$BORDER_H"
            printf "%s\n" "$BORDER_BR"
            ;;
        "minimal")
            printf "+%*s+\n" $((width-2)) "" | tr ' ' '-'
            printf "| %*s |\n" $((width-4)) "$title"
            printf "+%*s+\n" $((width-2)) "" | tr ' ' '-'
            ;;
    esac
}

# Create a progress bar
create_progress_bar() {
    local percent="$1"
    local width="${2:-$UDOS_PROGRESS_WIDTH}"
    local filled=$((percent * width / 100))
    local empty=$((width - filled))
    
    printf "["
    printf "%*s" "$filled" "" | tr ' ' "$BLOCK_DARK"
    printf "%*s" "$empty" "" | tr ' ' "$BLOCK_LIGHT"
    printf "] %d%%\n" "$percent"
}

# Create an input field
create_input_field() {
    local label="$1"
    local value="${2:-}"
    local width="${3:-$UDOS_INPUT_WIDTH}"
    
    printf "%-*s: [%*s]\n" "$UDOS_LABEL_WIDTH" "$label" "$width" "$value"
}

# Create a button
create_button() {
    local text="$1"
    local selected="${2:-false}"
    local width="${3:-$UDOS_BUTTON_WIDTH}"
    
    if [[ "$selected" == "true" ]]; then
        printf "[%s%*s%s]" "$BLOCK_MEDIUM" $((width-4)) "$text" "$BLOCK_MEDIUM"
    else
        printf "[%*s]" $((width-2)) "$text"
    fi
}

# Main execution
case "${1:-init}" in
    "init"|"setup"|"configure")
        init_display_config
        ;;
    "detect"|"size")
        detect_terminal_size
        echo "Terminal: ${UDOS_TERMINAL_COLS} × ${UDOS_TERMINAL_ROWS}"
        ;;
    "mode")
        source "$DISPLAY_VARS" 2>/dev/null || true
        determine_display_mode
        echo "Display mode: $UDOS_DISPLAY_MODE"
        ;;
    "summary"|"show")
        if [[ -f "$DISPLAY_VARS" ]]; then
            source "$DISPLAY_VARS"
            show_display_summary
        else
            red "❌ Display configuration not found. Run: $0 init"
        fi
        ;;
    "test")
        # Test ASCII interface elements
        if [[ -f "$DISPLAY_VARS" ]]; then
            source "$DISPLAY_VARS"
            echo
            bold "🧪 Testing ASCII Interface Elements"
            echo
            create_block_header "uDOS Test Interface" 60
            echo
            create_input_field "Username" "wizard"
            create_input_field "Location" "AA42"
            echo
            create_progress_bar 75 40
            echo
            echo "Buttons:"
            create_button "Continue" true
            echo "  "
            create_button "Cancel" false
            echo
        else
            red "❌ Display configuration not found. Run: $0 init"
        fi
        ;;
    "help"|"-h"|"--help")
        bold "🖥️  uDOS Display Configuration System v2.0"
        echo
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  init       Initialize display configuration (default)"
        echo "  detect     Detect current terminal size"
        echo "  mode       Determine optimal display mode"
        echo "  summary    Show configuration summary"
        echo "  test       Test ASCII interface elements"
        echo "  help       Show this help message"
        echo
        ;;
    *)
        red "❌ Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
