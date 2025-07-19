#!/bin/bash
# uDOS v2.0 - Display Configuration Template Processor
# 🖥️ display-template-processor.sh — Template-driven display configuration
# Processes display-config-template.md using [shortcode] and $Variable system

set -euo pipefail

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
DISPLAY_TEMPLATE="${UHOME}/uTemplate/display-config-template.md"
DISPLAY_VARS="${UMEM}/config/display-vars.sh"
DISPLAY_CONFIG="${UMEM}/config/display.conf"
DISPLAY_SUMMARY="${UMEM}/config/display-summary.md"

# Color helpers for enhanced visibility
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }
dim() { echo -e "\033[2m$1\033[0m"; }

# Initialize template processing
init_template_processing() {
    bold "🖥️  uDOS Display Configuration Template Processor v2.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔧 Using [shortcode] and \$Variable template system"
    echo
    
    # Create config directory if needed
    mkdir -p "${UMEM}/config"
    
    # Verify template exists
    if [[ ! -f "$DISPLAY_TEMPLATE" ]]; then
        red "❌ Display template not found: $DISPLAY_TEMPLATE"
        exit 1
    fi
    
    green "✅ Display template found: $DISPLAY_TEMPLATE"
}

# Collect input variables
collect_input_variables() {
    cyan "📝 Collecting input variables..."
    
    # Terminal size detection using multiple methods
    local cols rows detection_method
    
    # Method 1: tput (most reliable)
    if command -v tput >/dev/null 2>&1; then
        cols=$(tput cols 2>/dev/null || echo "")
        rows=$(tput lines 2>/dev/null || echo "")
        if [[ -n "$cols" ]] && [[ -n "$rows" ]]; then
            detection_method="tput"
        fi
    fi
    
    # Method 2: stty size (fallback)
    if [[ -z "${cols:-}" ]] || [[ -z "${rows:-}" ]]; then
        if command -v stty >/dev/null 2>&1; then
            local size_info
            size_info=$(stty size 2>/dev/null || echo "")
            if [[ -n "$size_info" ]]; then
                rows=$(echo "$size_info" | cut -d' ' -f1)
                cols=$(echo "$size_info" | cut -d' ' -f2)
                detection_method="stty"
            fi
        fi
    fi
    
    # Method 3: Environment variables (second fallback)
    if [[ -z "${cols:-}" ]] || [[ -z "${rows:-}" ]]; then
        cols="${COLUMNS:-80}"
        rows="${LINES:-24}"
        detection_method="environment"
    fi
    
    # Method 4: Default minimums (final fallback)
    cols="${cols:-80}"
    rows="${rows:-24}"
    detection_method="${detection_method:-default}"
    
    # Validate and constrain values
    if [[ "$cols" -lt 40 ]]; then
        yellow "⚠️  Terminal width too small ($cols), setting minimum: 40"
        cols=40
    fi
    
    if [[ "$rows" -lt 20 ]]; then
        yellow "⚠️  Terminal height too small ($rows), setting minimum: 20"
        rows=20
    fi
    
    # Capability detection
    local tput_available stty_available color_support ascii_support
    tput_available=$(command -v tput >/dev/null 2>&1 && echo "true" || echo "false")
    stty_available=$(command -v stty >/dev/null 2>&1 && echo "true" || echo "false")
    
    # Check color support
    if [[ -n "${TERM:-}" ]] && [[ "$TERM" != "dumb" ]]; then
        color_support="true"
    else
        color_support="false"
    fi
    
    # Check ASCII support (assume true unless proven otherwise)
    ascii_support="true"
    
    # Store all input variables
    export DETECTED_COLS="$cols"
    export DETECTED_ROWS="$rows"
    export DETECTION_METHOD="$detection_method"
    export ENV_COLUMNS="${COLUMNS:-unset}"
    export ENV_LINES="${LINES:-unset}"
    export TPUT_AVAILABLE="$tput_available"
    export STTY_AVAILABLE="$stty_available"
    export COLOR_SUPPORT="$color_support"
    export ASCII_SUPPORT="$ascii_support"
    
    # Set constraints and preferences
    export MIN_COLS="40"
    export MIN_ROWS="20"
    export MAX_COLS="1920"
    export MAX_ROWS="1080"
    export PREFERRED_RATIO="16:9"
    export PREFERRED_DASH_POSITION="auto"
    export PREFERRED_BORDER_STYLE="auto"
    export PREFERRED_BLOCK_SIZE="auto"
    export PREFERRED_GRID_FORMAT="auto"
    
    echo "  📐 Detected: ${cols} × ${rows} (via $detection_method)"
    echo "  🎨 Color support: $color_support"
    echo "  📦 ASCII support: $ascii_support"
}

# Process template logic
process_template_logic() {
    cyan "⚙️  Processing template logic..."
    
    # Process display mode selection
    local display_mode viewport_cols viewport_rows dash_cols dash_rows dash_position
    
    if [[ "$DETECTED_COLS" -ge 640 ]] && [[ "$DETECTED_ROWS" -ge 480 ]]; then
        display_mode="ultra"
        viewport_cols=640
        viewport_rows=420
        dash_cols=640
        dash_rows=60
        dash_position="bottom"
    elif [[ "$DETECTED_COLS" -ge 640 ]] && [[ "$DETECTED_ROWS" -ge 360 ]]; then
        display_mode="mega"
        viewport_cols=560
        viewport_rows=360
        dash_cols=80
        dash_rows=360
        dash_position="right"
    elif [[ "$DETECTED_COLS" -ge 320 ]] && [[ "$DETECTED_ROWS" -ge 240 ]]; then
        display_mode="full"
        viewport_cols=320
        viewport_rows=180
        dash_cols=320
        dash_rows=60
        dash_position="bottom"
    elif [[ "$DETECTED_COLS" -ge 320 ]] && [[ "$DETECTED_ROWS" -ge 180 ]]; then
        display_mode="wide"
        viewport_cols=240
        viewport_rows=180
        dash_cols=80
        dash_rows=180
        dash_position="right"
    elif [[ "$DETECTED_COLS" -ge 160 ]] && [[ "$DETECTED_ROWS" -ge 120 ]]; then
        display_mode="console"
        viewport_cols=160
        viewport_rows=90
        dash_cols=160
        dash_rows=30
        dash_position="bottom"
    elif [[ "$DETECTED_COLS" -ge 160 ]] && [[ "$DETECTED_ROWS" -ge 90 ]]; then
        display_mode="compact"
        viewport_cols=120
        viewport_rows=90
        dash_cols=40
        dash_rows=90
        dash_position="right"
    elif [[ "$DETECTED_COLS" -ge 80 ]] && [[ "$DETECTED_ROWS" -ge 60 ]]; then
        display_mode="mini"
        viewport_cols=80
        viewport_rows=45
        dash_cols=80
        dash_rows=15
        dash_position="bottom"
    else
        display_mode="micro"
        viewport_cols=80
        viewport_rows=30
        dash_cols=80
        dash_rows=15
        dash_position="bottom"
    fi
    
    export DISPLAY_MODE="$display_mode"
    export VIEWPORT_COLS="$viewport_cols"
    export VIEWPORT_ROWS="$viewport_rows"
    export DASH_COLS="$dash_cols"
    export DASH_ROWS="$dash_rows"
    export DASH_POSITION="$dash_position"
    
    # Process grid system
    local grid_mode grid_cols_max grid_rows_max grid_format grid_cell_width grid_cell_height
    
    if [[ "$viewport_cols" -ge 320 ]]; then
        grid_mode="extended"
        grid_cols_max=676
        grid_rows_max=99
        grid_format="extended"
    else
        grid_mode="standard"
        grid_cols_max=26
        grid_rows_max=99
        grid_format="standard"
    fi
    
    grid_cell_width=$((viewport_cols / 20))
    grid_cell_height=$((viewport_rows / 15))
    
    export GRID_MODE="$grid_mode"
    export GRID_COLS_MAX="$grid_cols_max"
    export GRID_ROWS_MAX="$grid_rows_max"
    export GRID_FORMAT="$grid_format"
    export GRID_CELL_WIDTH="$grid_cell_width"
    export GRID_CELL_HEIGHT="$grid_cell_height"
    
    # Process ASCII interface configuration
    local block_width block_height border_style input_width button_width label_width progress_width progress_chars
    
    case "$display_mode" in
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
    
    input_width=$((block_width - 4))
    button_width=12
    label_width=20
    progress_width=$((block_width - 8))
    progress_chars="▓▒░"
    
    export BLOCK_WIDTH="$block_width"
    export BLOCK_HEIGHT="$block_height"
    export BORDER_STYLE="$border_style"
    export INPUT_WIDTH="$input_width"
    export BUTTON_WIDTH="$button_width"
    export LABEL_WIDTH="$label_width"
    export PROGRESS_WIDTH="$progress_width"
    export PROGRESS_CHARS="$progress_chars"
    
    # Generate timestamp
    export UDOS_DISPLAY_CONFIG_GENERATED="$(date -Iseconds)"
    
    echo "  🎯 Display mode: $display_mode"
    echo "  🗺️  Grid system: $grid_mode"
    echo "  🧱 Block style: $border_style (${block_width}×${block_height})"
}

# Generate output from template
generate_output() {
    local output_name="$1"
    local output_file="$2"
    
    cyan "📄 Generating $output_name..."
    
    # Extract output template
    local template_content
    template_content=$(sed -n "/\[OUTPUT_${output_name}\]/,/\[\/OUTPUT_${output_name}\]/p" "$DISPLAY_TEMPLATE" | sed '1d;$d')
    
    if [[ -z "$template_content" ]]; then
        red "❌ Template block [OUTPUT_${output_name}] not found"
        return 1
    fi
    
    # Process variable substitutions
    local processed_content="$template_content"
    
    # Substitute all known variables
    processed_content=$(echo "$processed_content" | envsubst)
    
    # Create output directory if needed
    mkdir -p "$(dirname "$output_file")"
    
    # Write processed content to file
    echo "$processed_content" > "$output_file"
    
    green "✅ $output_name saved to: $output_file"
    echo "  📊 Size: $(wc -l < "$output_file") lines"
}

# Main processing function
process_display_template() {
    init_template_processing
    collect_input_variables
    process_template_logic
    
    cyan "📦 Generating output files..."
    
    # Generate all output files
    generate_output "DISPLAY_VARS" "$DISPLAY_VARS"
    generate_output "DISPLAY_CONFIG" "$DISPLAY_CONFIG"
    generate_output "DISPLAY_SUMMARY" "$DISPLAY_SUMMARY"
    
    # Make variables file executable
    chmod +x "$DISPLAY_VARS"
    
    echo
    green "✅ Display configuration template processing completed!"
    
    # Show summary
    show_configuration_summary
}

# Show configuration summary
show_configuration_summary() {
    echo
    bold "📊 uDOS Display Configuration Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Create summary box
    printf "╔════════════════════════════════════════════════════════════════════╗\n"
    printf "║ 🖥️  Terminal Size: %-50s ║\n" "${DETECTED_COLS} × ${DETECTED_ROWS}"
    printf "║ 🎯 Display Mode: %-52s ║\n" "$DISPLAY_MODE"
    printf "║ 📱 Viewport: %-56s ║\n" "${VIEWPORT_COLS} × ${VIEWPORT_ROWS}"
    printf "║ 📊 Dashboard: %-55s ║\n" "${DASH_COLS} × ${DASH_ROWS} ($DASH_POSITION)"
    printf "║ 🗺️  Grid System: %-53s ║\n" "$GRID_MODE (${GRID_COLS_MAX}×${GRID_ROWS_MAX})"
    printf "║ 🧱 Block Size: %-54s ║\n" "${BLOCK_WIDTH} × ${BLOCK_HEIGHT}"
    printf "║ 🎨 Border Style: %-52s ║\n" "$BORDER_STYLE"
    printf "╚════════════════════════════════════════════════════════════════════╝\n"
    
    echo
    echo "📁 Generated Files:"
    echo "  • $DISPLAY_VARS"
    echo "  • $DISPLAY_CONFIG"
    echo "  • $DISPLAY_SUMMARY"
    echo
    cyan "💡 To apply these settings, run: source $DISPLAY_VARS"
    echo
}

# Test display configuration
test_display_config() {
    if [[ ! -f "$DISPLAY_VARS" ]]; then
        red "❌ Display configuration not found. Run 'process' first."
        return 1
    fi
    
    # Source the configuration
    source "$DISPLAY_VARS"
    
    bold "🧪 Testing Display Configuration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Test header block
    udos_create_block_header "uDOS Test Interface" "$UDOS_BLOCK_WIDTH"
    echo
    
    # Test input fields
    udos_create_input_field "Username" "wizard"
    udos_create_input_field "Location" "AA42"
    udos_create_input_field "Mission" "test-display"
    echo
    
    # Test progress bar
    echo "Progress Examples:"
    udos_create_progress_bar 25
    udos_create_progress_bar 50
    udos_create_progress_bar 75
    udos_create_progress_bar 100
    echo
    
    # Test buttons
    echo "Button Examples:"
    udos_create_button "Continue" true
    echo "  "
    udos_create_button "Cancel" false
    echo "  "
    udos_create_button "Help" false
    echo
    echo
    
    green "✅ Display configuration test completed"
}

# Main execution
case "${1:-process}" in
    "process"|"generate"|"init")
        process_display_template
        ;;
    "test"|"demo")
        test_display_config
        ;;
    "summary"|"show")
        if [[ -f "$DISPLAY_SUMMARY" ]]; then
            cat "$DISPLAY_SUMMARY"
        else
            red "❌ Display summary not found. Run 'process' first."
        fi
        ;;
    "vars"|"variables")
        if [[ -f "$DISPLAY_VARS" ]]; then
            cat "$DISPLAY_VARS"
        else
            red "❌ Display variables not found. Run 'process' first."
        fi
        ;;
    "config"|"configuration")
        if [[ -f "$DISPLAY_CONFIG" ]]; then
            cat "$DISPLAY_CONFIG"
        else
            red "❌ Display config not found. Run 'process' first."
        fi
        ;;
    "help"|"-h"|"--help")
        bold "🖥️  uDOS Display Configuration Template Processor v2.0"
        echo
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  process    Process display template and generate configuration (default)"
        echo "  test       Test generated display configuration"
        echo "  summary    Show configuration summary"
        echo "  vars       Show generated variables file"
        echo "  config     Show generated config file"
        echo "  help       Show this help message"
        echo
        echo "Template System:"
        echo "  🔧 Uses [shortcode] and \$Variable format"
        echo "  📝 Processes display-config-template.md"
        echo "  📦 Generates executable configuration files"
        echo
        ;;
    *)
        red "❌ Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
