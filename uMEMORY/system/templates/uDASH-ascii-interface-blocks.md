# uDOS Block-Oriented ASCII Interface Template
# 🎨 Template System v2.0 - Enhanced Visual Display Components
# Variables processed by display-config.sh and template system

## 📱 Display Variables
[INPUT_DISPLAY_CONFIG]
# Auto-detected display configuration
Terminal Size: $UDOS_TERMINAL_COLS × $UDOS_TERMINAL_ROWS
Display Mode: $UDOS_DISPLAY_MODE
Viewport: $UDOS_VIEWPORT_COLS × $UDOS_VIEWPORT_ROWS  
Dashboard: $UDOS_DASH_COLS × $UDOS_DASH_ROWS ($UDOS_DASH_POSITION)
Grid System: $UDOS_GRID_MODE ($UDOS_GRID_COLS_MAX×$UDOS_GRID_ROWS_MAX)
Block Size: $UDOS_BLOCK_WIDTH × $UDOS_BLOCK_HEIGHT
Border Style: $UDOS_BORDER_STYLE
[/INPUT_DISPLAY_CONFIG]

## 🧱 Block Components

### Header Block
[BLOCK_HEADER]
$UDOS_BORDER_DOUBLE_TL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_DOUBLE_H")$UDOS_BORDER_DOUBLE_TR
$UDOS_BORDER_DOUBLE_V $(printf "%-*s" $((UDOS_BLOCK_WIDTH-4)) "$BLOCK_TITLE") $UDOS_BORDER_DOUBLE_V
$UDOS_BORDER_DOUBLE_BL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_DOUBLE_H")$UDOS_BORDER_DOUBLE_BR
[/BLOCK_HEADER]

### Status Block  
[BLOCK_STATUS]
$UDOS_BORDER_TL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_H")$UDOS_BORDER_TR
$UDOS_BORDER_V 🟢 $STATUS_LABEL: $STATUS_VALUE$(printf "%*s" $((UDOS_BLOCK_WIDTH-20)) "")$UDOS_BORDER_V
$UDOS_BORDER_V 📊 Progress: [$PROGRESS_BAR]$(printf "%*s" $((UDOS_BLOCK_WIDTH-30)) "")$UDOS_BORDER_V
$UDOS_BORDER_BL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_H")$UDOS_BORDER_BR
[/BLOCK_STATUS]

### Input Form Block
[BLOCK_INPUT_FORM]
$UDOS_BORDER_DOUBLE_TL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_DOUBLE_H")$UDOS_BORDER_DOUBLE_TR
$UDOS_BORDER_DOUBLE_V $(printf "%-*s" $((UDOS_BLOCK_WIDTH-4)) "$FORM_TITLE") $UDOS_BORDER_DOUBLE_V
$UDOS_BORDER_L$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_H")$UDOS_BORDER_R
$UDOS_BORDER_V                                                    $UDOS_BORDER_V
$UDOS_BORDER_V $INPUT_LABEL_1: [$INPUT_VALUE_1$(printf "%*s" $((UDOS_INPUT_WIDTH-${#INPUT_VALUE_1})) "")]$(printf "%*s" $((UDOS_BLOCK_WIDTH-UDOS_INPUT_WIDTH-${#INPUT_LABEL_1}-7)) "")$UDOS_BORDER_V
$UDOS_BORDER_V $INPUT_LABEL_2: [$INPUT_VALUE_2$(printf "%*s" $((UDOS_INPUT_WIDTH-${#INPUT_VALUE_2})) "")]$(printf "%*s" $((UDOS_BLOCK_WIDTH-UDOS_INPUT_WIDTH-${#INPUT_LABEL_2}-7)) "")$UDOS_BORDER_V
$UDOS_BORDER_V                                                    $UDOS_BORDER_V
$UDOS_BORDER_V   [$BUTTON_1$(printf "%*s" $((UDOS_BUTTON_WIDTH-${#BUTTON_1}-2)) "")]  [$BUTTON_2$(printf "%*s" $((UDOS_BUTTON_WIDTH-${#BUTTON_2}-2)) "")]$(printf "%*s" $((UDOS_BLOCK_WIDTH-UDOS_BUTTON_WIDTH*2-8)) "")$UDOS_BORDER_V
$UDOS_BORDER_V                                                    $UDOS_BORDER_V
$UDOS_BORDER_DOUBLE_BL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_DOUBLE_H")$UDOS_BORDER_DOUBLE_BR
[/BLOCK_INPUT_FORM]

### Grid Map Block
[BLOCK_GRID_MAP]
$UDOS_BORDER_TL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_H")$UDOS_BORDER_TR
$UDOS_BORDER_V 🗺️  Grid Position: $GRID_POSITION$(printf "%*s" $((UDOS_BLOCK_WIDTH-20-${#GRID_POSITION})) "")$UDOS_BORDER_V
$UDOS_BORDER_L$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_H")$UDOS_BORDER_R
$UDOS_BORDER_V                                                    $UDOS_BORDER_V
$UDOS_BORDER_V   $GRID_ROW_1                                     $UDOS_BORDER_V
$UDOS_BORDER_V   $GRID_ROW_2                                     $UDOS_BORDER_V
$UDOS_BORDER_V   $GRID_ROW_3                                     $UDOS_BORDER_V
$UDOS_BORDER_V                                                    $UDOS_BORDER_V
$UDOS_BORDER_BL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_H")$UDOS_BORDER_BR
[/BLOCK_GRID_MAP]

### Progress Meter Block
[BLOCK_PROGRESS]
$UDOS_BORDER_TL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_H")$UDOS_BORDER_TR
$UDOS_BORDER_V 📈 $PROGRESS_LABEL$(printf "%*s" $((UDOS_BLOCK_WIDTH-6-${#PROGRESS_LABEL})) "")$UDOS_BORDER_V
$UDOS_BORDER_V                                                    $UDOS_BORDER_V
$UDOS_BORDER_V [$PROGRESS_FILLED$(printf "%*s" $((UDOS_PROGRESS_WIDTH-PROGRESS_PERCENT*UDOS_PROGRESS_WIDTH/100)) "" | tr ' ' "$UDOS_BLOCK_LIGHT")] $PROGRESS_PERCENT%$(printf "%*s" $((UDOS_BLOCK_WIDTH-UDOS_PROGRESS_WIDTH-8)) "")$UDOS_BORDER_V
$UDOS_BORDER_V                                                    $UDOS_BORDER_V
$UDOS_BORDER_BL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_H")$UDOS_BORDER_BR
[/BLOCK_PROGRESS]

### Menu Selection Block
[BLOCK_MENU]
$UDOS_BORDER_DOUBLE_TL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_DOUBLE_H")$UDOS_BORDER_DOUBLE_TR
$UDOS_BORDER_DOUBLE_V 🎯 $MENU_TITLE$(printf "%*s" $((UDOS_BLOCK_WIDTH-6-${#MENU_TITLE})) "")$UDOS_BORDER_DOUBLE_V
$UDOS_BORDER_L$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_DOUBLE_H")$UDOS_BORDER_R
$UDOS_BORDER_V                                                    $UDOS_BORDER_V
$UDOS_BORDER_V $MENU_ITEM_1_SELECTED $MENU_ITEM_1$(printf "%*s" $((UDOS_BLOCK_WIDTH-6-${#MENU_ITEM_1})) "")$UDOS_BORDER_V
$UDOS_BORDER_V $MENU_ITEM_2_SELECTED $MENU_ITEM_2$(printf "%*s" $((UDOS_BLOCK_WIDTH-6-${#MENU_ITEM_2})) "")$UDOS_BORDER_V
$UDOS_BORDER_V $MENU_ITEM_3_SELECTED $MENU_ITEM_3$(printf "%*s" $((UDOS_BLOCK_WIDTH-6-${#MENU_ITEM_3})) "")$UDOS_BORDER_V
$UDOS_BORDER_V                                                    $UDOS_BORDER_V
$UDOS_BORDER_DOUBLE_BL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_DOUBLE_H")$UDOS_BORDER_DOUBLE_BR
[/BLOCK_MENU]

### Dashboard Summary Block
[BLOCK_DASHBOARD]
$UDOS_BORDER_DOUBLE_TL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_DOUBLE_H")$UDOS_BORDER_DOUBLE_TR
$UDOS_BORDER_DOUBLE_V 🌀 uDOS Dashboard$(printf "%*s" $((UDOS_BLOCK_WIDTH-18)) "")$UDOS_BORDER_DOUBLE_V
$UDOS_BORDER_L$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_DOUBLE_H")$UDOS_BORDER_R
$UDOS_BORDER_V 👤 User: $USERNAME$(printf "%*s" $((UDOS_BLOCK_WIDTH-10-${#USERNAME})) "")$UDOS_BORDER_V
$UDOS_BORDER_V 📍 Position: $GRID_POSITION$(printf "%*s" $((UDOS_BLOCK_WIDTH-15-${#GRID_POSITION})) "")$UDOS_BORDER_V
$UDOS_BORDER_V 🎯 Mission: $CURRENT_MISSION$(printf "%*s" $((UDOS_BLOCK_WIDTH-13-${#CURRENT_MISSION})) "")$UDOS_BORDER_V
$UDOS_BORDER_V 🧭 Moves: $TOTAL_MOVES$(printf "%*s" $((UDOS_BLOCK_WIDTH-12-${#TOTAL_MOVES})) "")$UDOS_BORDER_V
$UDOS_BORDER_V 💚 Health: [$HEALTH_BAR]$(printf "%*s" $((UDOS_BLOCK_WIDTH-HEALTH_BAR_WIDTH-13)) "")$UDOS_BORDER_V
$UDOS_BORDER_DOUBLE_BL$(printf "%*s" $((UDOS_BLOCK_WIDTH-2)) "" | tr ' ' "$UDOS_BORDER_DOUBLE_H")$UDOS_BORDER_DOUBLE_BR
[/BLOCK_DASHBOARD]

## 📏 Layout Templates

### Full Screen Layout (Dashboard Bottom)
[LAYOUT_FULL_SCREEN_BOTTOM]
# Viewport Area ($UDOS_VIEWPORT_COLS × $UDOS_VIEWPORT_ROWS)
$VIEWPORT_CONTENT

# Dashboard Area ($UDOS_DASH_COLS × $UDOS_DASH_ROWS)
$(printf "%*s" "$UDOS_DASH_COLS" "" | tr ' ' "─")
$DASHBOARD_CONTENT
[/LAYOUT_FULL_SCREEN_BOTTOM]

### Split Screen Layout (Dashboard Right)  
[LAYOUT_SPLIT_SCREEN_RIGHT]
# Combined Layout ($UDOS_VIEWPORT_COLS + $UDOS_DASH_COLS columns)
$VIEWPORT_LINE_1 $UDOS_BORDER_V $DASHBOARD_LINE_1
$VIEWPORT_LINE_2 $UDOS_BORDER_V $DASHBOARD_LINE_2
$VIEWPORT_LINE_3 $UDOS_BORDER_V $DASHBOARD_LINE_3
[/LAYOUT_SPLIT_SCREEN_RIGHT]

### Compact Layout (Minimal Dashboard)
[LAYOUT_COMPACT]
# Header
$HEADER_BLOCK

# Main Content Area
$MAIN_CONTENT

# Status Strip  
$STATUS_STRIP
[/LAYOUT_COMPACT]

## 🎨 Color and Style Templates

### Color Scheme Variables
[COLOR_SCHEME]
# ANSI Color Codes for enhanced visibility
HEADER_COLOR="\033[1;36m"     # Bright Cyan
STATUS_COLOR="\033[1;32m"     # Bright Green  
WARNING_COLOR="\033[1;33m"    # Bright Yellow
ERROR_COLOR="\033[1;31m"      # Bright Red
INFO_COLOR="\033[1;34m"       # Bright Blue
RESET_COLOR="\033[0m"         # Reset
BOLD="\033[1m"               # Bold
DIM="\033[2m"                # Dim
[/COLOR_SCHEME]

### Responsive Block Sizing
[RESPONSIVE_BLOCKS]
# Block dimensions based on display mode
if [ "$UDOS_DISPLAY_MODE" = "ultra" ] || [ "$UDOS_DISPLAY_MODE" = "mega" ]; then
    BLOCK_LARGE=80
    BLOCK_MEDIUM=60  
    BLOCK_SMALL=40
elif [ "$UDOS_DISPLAY_MODE" = "full" ] || [ "$UDOS_DISPLAY_MODE" = "wide" ]; then
    BLOCK_LARGE=60
    BLOCK_MEDIUM=40
    BLOCK_SMALL=30
else
    BLOCK_LARGE=40
    BLOCK_MEDIUM=30
    BLOCK_SMALL=20
fi
[/RESPONSIVE_BLOCKS]

## 📱 Template Processing Instructions

### Variable Substitution Rules
[PROCESSING_RULES]
1. **Display Variables**: All $UDOS_* variables from display-config.sh
2. **Content Variables**: User-provided $CONTENT, $TITLE, etc.
3. **Dynamic Variables**: Calculated values like progress bars, grid positions
4. **Border Characters**: Automatically selected based on $UDOS_BORDER_STYLE
5. **Responsive Sizing**: Block dimensions adapt to $UDOS_DISPLAY_MODE
[/PROCESSING_RULES]

### Template Activation
[TEMPLATE_ACTIVATION]
# To use this template system:
# 1. Initialize display configuration: ./uCode/display-config.sh init
# 2. Source display variables: source $UMEM/config/display-vars.sh  
# 3. Process template blocks: ./uCode/template-generator.sh process ascii-interface
# 4. Variables automatically replaced with current display settings
[/TEMPLATE_ACTIVATION]

## 🎯 Integration Points

### uCode Command Integration
[UCODE_INTEGRATION]
# Commands that use this template system:
ucode DASHBOARD          # Uses [BLOCK_DASHBOARD] template
ucode SETUP             # Uses [BLOCK_INPUT_FORM] template  
ucode MAP               # Uses [BLOCK_GRID_MAP] template
ucode STATUS            # Uses [BLOCK_STATUS] template
ucode MENU              # Uses [BLOCK_MENU] template
[/UCODE_INTEGRATION]

### VS Code Task Integration
[VSCODE_INTEGRATION]
# VS Code tasks automatically:
# - Detect terminal size changes
# - Refresh display configuration  
# - Re-render ASCII blocks with new dimensions
# - Maintain consistent visual appearance
[/VSCODE_INTEGRATION]

---

*This template provides a comprehensive block-oriented ASCII interface system that automatically adapts to terminal size and display configuration. All visual elements scale appropriately and maintain visual consistency across different screen sizes.*
