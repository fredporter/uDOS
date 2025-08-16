# uDOS Display Configuration Template
# 🖥️ Template System v2.0 - Display, Grid, and ASCII Interface Configuration
# Variables processed by display-config.sh template processor

## 📱 Input Configuration Detection
[INPUT_TERMINAL_DETECTION]
# Terminal size detection methods
Terminal Columns: $DETECTED_COLS
Terminal Rows: $DETECTED_ROWS
Detection Method: $DETECTION_METHOD
Environment COLUMNS: $ENV_COLUMNS
Environment LINES: $ENV_LINES
tput Available: $TPUT_AVAILABLE
stty Available: $STTY_AVAILABLE
[/INPUT_TERMINAL_DETECTION]

[INPUT_DISPLAY_CONSTRAINTS]
# Display constraints and preferences
Minimum Width: $MIN_COLS
Minimum Height: $MIN_ROWS
Maximum Width: $MAX_COLS
Maximum Height: $MAX_ROWS
Preferred Ratio: $PREFERRED_RATIO
Dashboard Position: $PREFERRED_DASH_POSITION
[/INPUT_DISPLAY_CONSTRAINTS]

[INPUT_USER_PREFERENCES]
# User interface preferences
Border Style: $PREFERRED_BORDER_STYLE
Block Size: $PREFERRED_BLOCK_SIZE
Grid Format: $PREFERRED_GRID_FORMAT
Color Support: $COLOR_SUPPORT
ASCII Support: $ASCII_SUPPORT
[/INPUT_USER_PREFERENCES]

## 🎯 Processing Rules
[PROCESS_DISPLAY_MODE]
# Display mode determination logic
if [ $DETECTED_COLS -ge 640 ] && [ $DETECTED_ROWS -ge 480 ]; then
    DISPLAY_MODE="ultra"
    VIEWPORT_COLS=640
    VIEWPORT_ROWS=420
    DASH_COLS=640
    DASH_ROWS=60
    DASH_POSITION="bottom"
elif [ $DETECTED_COLS -ge 640 ] && [ $DETECTED_ROWS -ge 360 ]; then
    DISPLAY_MODE="mega"
    VIEWPORT_COLS=560
    VIEWPORT_ROWS=360
    DASH_COLS=80
    DASH_ROWS=360
    DASH_POSITION="right"
elif [ $DETECTED_COLS -ge 320 ] && [ $DETECTED_ROWS -ge 240 ]; then
    DISPLAY_MODE="full"
    VIEWPORT_COLS=320
    VIEWPORT_ROWS=180
    DASH_COLS=320
    DASH_ROWS=60
    DASH_POSITION="bottom"
elif [ $DETECTED_COLS -ge 320 ] && [ $DETECTED_ROWS -ge 180 ]; then
    DISPLAY_MODE="wide"
    VIEWPORT_COLS=240
    VIEWPORT_ROWS=180
    DASH_COLS=80
    DASH_ROWS=180
    DASH_POSITION="right"
elif [ $DETECTED_COLS -ge 160 ] && [ $DETECTED_ROWS -ge 120 ]; then
    DISPLAY_MODE="console"
    VIEWPORT_COLS=160
    VIEWPORT_ROWS=90
    DASH_COLS=160
    DASH_ROWS=30
    DASH_POSITION="bottom"
elif [ $DETECTED_COLS -ge 160 ] && [ $DETECTED_ROWS -ge 90 ]; then
    DISPLAY_MODE="compact"
    VIEWPORT_COLS=120
    VIEWPORT_ROWS=90
    DASH_COLS=40
    DASH_ROWS=90
    DASH_POSITION="right"
elif [ $DETECTED_COLS -ge 80 ] && [ $DETECTED_ROWS -ge 60 ]; then
    DISPLAY_MODE="mini"
    VIEWPORT_COLS=80
    VIEWPORT_ROWS=45
    DASH_COLS=80
    DASH_ROWS=15
    DASH_POSITION="bottom"
else
    DISPLAY_MODE="micro"
    VIEWPORT_COLS=80
    VIEWPORT_ROWS=30
    DASH_COLS=80
    DASH_ROWS=15
    DASH_POSITION="bottom"
fi
[/PROCESS_DISPLAY_MODE]

[PROCESS_GRID_SYSTEM]
# Grid coordinate system configuration
if [ $VIEWPORT_COLS -ge 320 ]; then
    GRID_MODE="extended"
    GRID_COLS_MAX=676
    GRID_ROWS_MAX=99
    GRID_FORMAT="extended"
else
    GRID_MODE="standard"
    GRID_COLS_MAX=26
    GRID_ROWS_MAX=99
    GRID_FORMAT="standard"
fi

GRID_CELL_WIDTH=$((VIEWPORT_COLS / 20))
GRID_CELL_HEIGHT=$((VIEWPORT_ROWS / 15))
[/PROCESS_GRID_SYSTEM]

[PROCESS_ASCII_INTERFACE]
# ASCII interface element sizing
case $DISPLAY_MODE in
    "ultra"|"mega"|"full"|"wide")
        BLOCK_WIDTH=60
        BLOCK_HEIGHT=8
        BORDER_STYLE="double"
        ;;
    "console"|"compact")
        BLOCK_WIDTH=40
        BLOCK_HEIGHT=6
        BORDER_STYLE="single"
        ;;
    "mini"|"micro")
        BLOCK_WIDTH=30
        BLOCK_HEIGHT=4
        BORDER_STYLE="minimal"
        ;;
    *)
        BLOCK_WIDTH=40
        BLOCK_HEIGHT=6
        BORDER_STYLE="single"
        ;;
esac

INPUT_WIDTH=$((BLOCK_WIDTH - 4))
BUTTON_WIDTH=12
LABEL_WIDTH=20
PROGRESS_WIDTH=$((BLOCK_WIDTH - 8))
PROGRESS_CHARS="▓▒░"
[/PROCESS_ASCII_INTERFACE]

## 📄 Output Files

[OUTPUT_DISPLAY_VARS]
#!/bin/bash
# uDOS Display Configuration Variables
# Generated automatically by display-config-template.sh
# Template System v2.0 - DO NOT EDIT MANUALLY

# === TERMINAL DETECTION ===
export UDOS_TERMINAL_COLS="$DETECTED_COLS"
export UDOS_TERMINAL_ROWS="$DETECTED_ROWS"
export UDOS_DETECTION_METHOD="$DETECTION_METHOD"

# === DISPLAY MODE CONFIGURATION ===
export UDOS_DISPLAY_MODE="$DISPLAY_MODE"
export UDOS_VIEWPORT_COLS="$VIEWPORT_COLS"
export UDOS_VIEWPORT_ROWS="$VIEWPORT_ROWS"
export UDOS_DASH_COLS="$DASH_COLS"
export UDOS_DASH_ROWS="$DASH_ROWS"
export UDOS_DASH_POSITION="$DASH_POSITION"

# === GRID SYSTEM CONFIGURATION ===
export UDOS_GRID_COLS_MAX="$GRID_COLS_MAX"
export UDOS_GRID_ROWS_MAX="$GRID_ROWS_MAX"
export UDOS_GRID_FORMAT="$GRID_FORMAT"
export UDOS_GRID_CELL_WIDTH="$GRID_CELL_WIDTH"
export UDOS_GRID_CELL_HEIGHT="$GRID_CELL_HEIGHT"
export UDOS_GRID_MODE="$GRID_MODE"

# === ASCII INTERFACE CONFIGURATION ===
export UDOS_BLOCK_WIDTH="$BLOCK_WIDTH"
export UDOS_BLOCK_HEIGHT="$BLOCK_HEIGHT"
export UDOS_BORDER_STYLE="$BORDER_STYLE"
export UDOS_INPUT_WIDTH="$INPUT_WIDTH"
export UDOS_BUTTON_WIDTH="$BUTTON_WIDTH"
export UDOS_LABEL_WIDTH="$LABEL_WIDTH"
export UDOS_PROGRESS_WIDTH="$PROGRESS_WIDTH"
export UDOS_PROGRESS_CHARS="$PROGRESS_CHARS"

# === BLOCK CHARACTERS ===
export UDOS_BLOCK_FULL="█"
export UDOS_BLOCK_LIGHT="░"
export UDOS_BLOCK_MEDIUM="▒"
export UDOS_BLOCK_DARK="▓"
export UDOS_BLOCK_TOP="▀"
export UDOS_BLOCK_BOTTOM="▄"
export UDOS_BLOCK_LEFT="▌"
export UDOS_BLOCK_RIGHT="▐"

# === BORDER CHARACTERS ===
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

# === ENHANCED BORDER CHARACTERS ===
export UDOS_BORDER_DOUBLE_H="═"
export UDOS_BORDER_DOUBLE_V="║"
export UDOS_BORDER_DOUBLE_TL="╔"
export UDOS_BORDER_DOUBLE_TR="╗"
export UDOS_BORDER_DOUBLE_BL="╚"
export UDOS_BORDER_DOUBLE_BR="╝"

# === UTILITY FUNCTIONS ===
udos_create_block_header() {
    local title="$1"
    local width="${2:-$UDOS_BLOCK_WIDTH}"
    
    case "$UDOS_BORDER_STYLE" in
        "double")
            printf "%s" "$UDOS_BORDER_DOUBLE_TL"
            printf "%*s" $((width-2)) "" | tr ' ' "$UDOS_BORDER_DOUBLE_H"
            printf "%s\n" "$UDOS_BORDER_DOUBLE_TR"
            printf "%s %*s %s\n" "$UDOS_BORDER_DOUBLE_V" $((width-4)) "$title" "$UDOS_BORDER_DOUBLE_V"
            printf "%s" "$UDOS_BORDER_DOUBLE_BL"
            printf "%*s" $((width-2)) "" | tr ' ' "$UDOS_BORDER_DOUBLE_H"
            printf "%s\n" "$UDOS_BORDER_DOUBLE_BR"
            ;;
        "single")
            printf "%s" "$UDOS_BORDER_TL"
            printf "%*s" $((width-2)) "" | tr ' ' "$UDOS_BORDER_H"
            printf "%s\n" "$UDOS_BORDER_TR"
            printf "%s %*s %s\n" "$UDOS_BORDER_V" $((width-4)) "$title" "$UDOS_BORDER_V"
            printf "%s" "$UDOS_BORDER_BL"
            printf "%*s" $((width-2)) "" | tr ' ' "$UDOS_BORDER_H"
            printf "%s\n" "$UDOS_BORDER_BR"
            ;;
        "minimal")
            printf "+%*s+\n" $((width-2)) "" | tr ' ' '-'
            printf "| %*s |\n" $((width-4)) "$title"
            printf "+%*s+\n" $((width-2)) "" | tr ' ' '-'
            ;;
    esac
}

udos_create_progress_bar() {
    local percent="$1"
    local width="${2:-$UDOS_PROGRESS_WIDTH}"
    local filled=$((percent * width / 100))
    local empty=$((width - filled))
    
    printf "["
    printf "%*s" "$filled" "" | tr ' ' "$UDOS_BLOCK_DARK"
    printf "%*s" "$empty" "" | tr ' ' "$UDOS_BLOCK_LIGHT"
    printf "] %d%%\n" "$percent"
}

udos_create_input_field() {
    local label="$1"
    local value="${2:-}"
    local width="${3:-$UDOS_INPUT_WIDTH}"
    
    printf "%-*s: [%*s]\n" "$UDOS_LABEL_WIDTH" "$label" "$width" "$value"
}

udos_create_button() {
    local text="$1"
    local selected="${2:-false}"
    local width="${3:-$UDOS_BUTTON_WIDTH}"
    
    if [[ "$selected" == "true" ]]; then
        printf "[%s%*s%s]" "$UDOS_BLOCK_MEDIUM" $((width-4)) "$text" "$UDOS_BLOCK_MEDIUM"
    else
        printf "[%*s]" $((width-2)) "$text"
    fi
}

# === METADATA ===
export UDOS_DISPLAY_CONFIG_VERSION="2.0"
export UDOS_DISPLAY_CONFIG_GENERATED="$(date -Iseconds)"
export UDOS_DISPLAY_CONFIG_TEMPLATE="display-config-template.md"
[/OUTPUT_DISPLAY_VARS]

[OUTPUT_DISPLAY_CONFIG]
# uDOS Display Configuration File
# Template System v2.0 - Structured Configuration

[meta]
version=2.0
generated=$UDOS_DISPLAY_CONFIG_GENERATED
template=display-config-template.md

[terminal]
cols=$DETECTED_COLS
rows=$DETECTED_ROWS
detection_method=$DETECTION_METHOD

[display_mode]
mode=$DISPLAY_MODE
viewport_cols=$VIEWPORT_COLS
viewport_rows=$VIEWPORT_ROWS
dash_cols=$DASH_COLS
dash_rows=$DASH_ROWS
dash_position=$DASH_POSITION

[grid_system]
cols_max=$GRID_COLS_MAX
rows_max=$GRID_ROWS_MAX
format=$GRID_FORMAT
cell_width=$GRID_CELL_WIDTH
cell_height=$GRID_CELL_HEIGHT
mode=$GRID_MODE

[ascii_interface]
block_width=$BLOCK_WIDTH
block_height=$BLOCK_HEIGHT
border_style=$BORDER_STYLE
input_width=$INPUT_WIDTH
button_width=$BUTTON_WIDTH
label_width=$LABEL_WIDTH
progress_width=$PROGRESS_WIDTH
progress_chars=$PROGRESS_CHARS

[constraints]
min_cols=$MIN_COLS
min_rows=$MIN_ROWS
max_cols=$MAX_COLS
max_rows=$MAX_ROWS

[capabilities]
color_support=$COLOR_SUPPORT
ascii_support=$ASCII_SUPPORT
tput_available=$TPUT_AVAILABLE
stty_available=$STTY_AVAILABLE
[/OUTPUT_DISPLAY_CONFIG]

[OUTPUT_DISPLAY_SUMMARY]
# 🖥️  uDOS Display Configuration Summary
**Generated**: $UDOS_DISPLAY_CONFIG_GENERATED  
**Template**: display-config-template.md v2.0

## 📱 Terminal Configuration
- **Size**: $DETECTED_COLS × $DETECTED_ROWS characters
- **Detection Method**: $DETECTION_METHOD
- **Display Mode**: $DISPLAY_MODE
- **Viewport**: $VIEWPORT_COLS × $VIEWPORT_ROWS
- **Dashboard**: $DASH_COLS × $DASH_ROWS ($DASH_POSITION)

## 🗺️  Grid System
- **Mode**: $GRID_MODE
- **Coordinates**: $GRID_COLS_MAX × $GRID_ROWS_MAX positions
- **Format**: $GRID_FORMAT
- **Cell Size**: $GRID_CELL_WIDTH × $GRID_CELL_HEIGHT characters

## 🎨 ASCII Interface
- **Block Size**: $BLOCK_WIDTH × $BLOCK_HEIGHT
- **Border Style**: $BORDER_STYLE
- **Input Width**: $INPUT_WIDTH characters
- **Button Width**: $BUTTON_WIDTH characters
- **Progress Width**: $PROGRESS_WIDTH characters

## ⚙️  System Capabilities
- **Color Support**: $COLOR_SUPPORT
- **ASCII Support**: $ASCII_SUPPORT
- **tput Available**: $TPUT_AVAILABLE
- **stty Available**: $STTY_AVAILABLE

---

*This configuration optimizes uDOS display for your terminal size and capabilities.*
[/OUTPUT_DISPLAY_SUMMARY]

## 🔄 Template Processing Instructions

### Variable Collection Phase
1. **Terminal Detection**: Detect current terminal size using tput, stty, environment variables
2. **Capability Detection**: Check for color support, ASCII support, available tools
3. **User Preferences**: Load any saved display preferences from uMemory

### Processing Phase  
1. **Display Mode Logic**: Run [PROCESS_DISPLAY_MODE] to determine optimal configuration
2. **Grid System Setup**: Execute [PROCESS_GRID_SYSTEM] for coordinate mapping
3. **Interface Configuration**: Process [PROCESS_ASCII_INTERFACE] for element sizing

### Output Generation Phase
1. **Variables File**: Generate executable shell script with all display variables
2. **Configuration File**: Create structured config file for system integration
3. **Summary Report**: Generate human-readable markdown summary

### Integration Points
- **ucode.sh**: Sources display variables on startup
- **Dashboard System**: Uses display configuration for layout
- **Template System**: All templates can access display variables
- **ASCII Interface**: All interface elements use consistent sizing

### Template Activation
```bash
# Initialize display configuration using template system
./uCode/display-template-processor.sh process

# Generated files:
# - uMemory/config/display-vars.sh (executable variables)
# - uMemory/config/display.conf (structured config)  
# - uMemory/config/display-summary.md (human summary)
```

---

*This template system ensures all display configuration follows the unified [shortcode] and $Variable format established in uDOS v2.0.*
