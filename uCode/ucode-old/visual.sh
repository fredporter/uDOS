#!/bin/bash
# uDOS Visual Framework v1.2
# Extends the existing ASCII interface with interactive elements, animations, and adaptive screen sizing
# Features: Latest setup questions from template, automatic screen size configuration

set -euo pipefail

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
VISUAL_DIR="${UMEM}/visual"
DISPLAY_CONFIG="${UMEM}/config/display.conf"

# Terminal dimensions
TERM_COLS=${COLUMNS:-$(tput cols 2>/dev/null || echo 80)}
TERM_ROWS=${LINES:-$(tput lines 2>/dev/null || echo 24)}

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }
dim() { echo -e "\033[2m$1\033[0m"; }

# visual elements
SPINNER_CHARS="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
PROGRESS_CHARS="▏▎▍▌▋▊▉█"
BOX_CHARS="┌┐└┘─│"
ROUNDED_CHARS="╭╮╰╯─│"
HEAVY_CHARS="┏┓┗┛━┃"

# Terminal capability detection
detect_terminal_capabilities() {
    local capabilities=()
    
    # Check for true color support
    if [[ "${COLORTERM:-}" == "truecolor" ]] || [[ "${COLORTERM:-}" == "24bit" ]]; then
        capabilities+=("truecolor")
    fi
    
    # Check for specific terminal features
    case "${TERM_PROGRAM:-}" in
        "iTerm.app")
            capabilities+=("iterm2" "images" "notifications" "badges")
            ;;
        "kitty")
            capabilities+=("kitty" "images" "ligatures" "unicode")
            ;;
        "WezTerm")
            capabilities+=("wezterm" "images" "webgl")
            ;;
        "vscode")
            capabilities+=("vscode" "unicode")
            ;;
    esac
    
    # Check for mouse support
    if [[ -n "${TERM:-}" ]] && [[ "$TERM" =~ xterm|screen|tmux ]]; then
        capabilities+=("mouse")
    fi
    
    # Store capabilities and terminal size
    export UDOS_TERMINAL_CAPS="${capabilities[*]}"
    export UDOS_TERM_COLS="$TERM_COLS"
    export UDOS_TERM_ROWS="$TERM_ROWS"
    
    echo "${capabilities[@]}"
}

# Configure screen size and display settings
configure_screen_size() {
    local config_file="${VISUAL_DIR}/display.conf"
    
    # Detect optimal screen size
    local optimal_width=$TERM_COLS
    local optimal_height=$TERM_ROWS
    
    # Adjust for different terminal types
    case "${TERM_PROGRAM:-}" in
        "vscode")
            # VS Code integrated terminal often has more space
            optimal_width=$((TERM_COLS > 100 ? 100 : TERM_COLS))
            optimal_height=$((TERM_ROWS > 30 ? 30 : TERM_ROWS))
            ;;
        "iTerm.app"|"kitty"|"WezTerm")
            # Modern terminals can handle larger displays
            optimal_width=$((TERM_COLS > 120 ? 120 : TERM_COLS))
            optimal_height=$((TERM_ROWS > 40 ? 40 : TERM_ROWS))
            ;;
        *)
            # Conservative sizing for unknown terminals
            optimal_width=$((TERM_COLS > 80 ? 80 : TERM_COLS))
            optimal_height=$((TERM_ROWS > 24 ? 24 : TERM_ROWS))
            ;;
    esac
    
    # Create display configuration
    mkdir -p "$(dirname "$config_file")"
    cat > "$config_file" << EOF
# uDOS Display Configuration
# Generated: $(date '+%Y-%m-%d %H:%M:%S')

# Terminal Information
TERMINAL_PROGRAM=${TERM_PROGRAM:-unknown}
TERMINAL_TYPE=${TERM:-xterm}
DETECTED_COLS=${TERM_COLS}
DETECTED_ROWS=${TERM_ROWS}

# Optimal Display Settings
DISPLAY_WIDTH=${optimal_width}
DISPLAY_HEIGHT=${optimal_height}
PROGRESS_BAR_WIDTH=$((optimal_width - 20))
DASHBOARD_WIDTH=${optimal_width}

# Widget Dimensions
WIDGET_WIDTH=$((optimal_width / 3))
WIDGET_HEIGHT=$((optimal_height / 4))

# Layout Settings
MARGIN_LEFT=2
MARGIN_RIGHT=2
MARGIN_TOP=1
MARGIN_BOTTOM=1

# Performance Settings
ANIMATION_ENABLED=true
REFRESH_RATE=$([[ $optimal_width -gt 100 ]] && echo "fast" || echo "normal")
EOF
    
    # Export display variables
    export UDOS_DISPLAY_WIDTH="$optimal_width"
    export UDOS_DISPLAY_HEIGHT="$optimal_height"
    export UDOS_PROGRESS_WIDTH="$((optimal_width - 20))"
    export UDOS_WIDGET_WIDTH="$((optimal_width / 3))"
    
    cyan "📐 Screen configured: ${optimal_width}×${optimal_height} (detected: ${TERM_COLS}×${TERM_ROWS})"
}

# progress bar with animation
animated_progress_bar() {
    local percent="$1"
    local width="${2:-${UDOS_PROGRESS_WIDTH:-40}}"
    local title="${3:-Progress}"
    local style="${4:-default}"
    
    local filled=$((percent * width / 100))
    local empty=$((width - filled))
    
    case "$style" in
        "gradient")
            local colors=("31" "33" "32")  # red -> yellow -> green
            local color_idx=$((percent / 34))
            echo -ne "\033[${colors[$color_idx]}m"
            ;;
        "rainbow")
            echo -ne "\033[$(((percent/10 + 31) % 7 + 31))m"
            ;;
    esac
    
    echo -n "┣"
    for ((i=0; i<filled; i++)); do
        if [[ $i -eq $((filled-1)) ]] && [[ $filled -lt $width ]]; then
            # Partial fill for smoother animation
            local sub_progress=$((percent % (100/width)))
            local char_idx=$((sub_progress * 8 / (100/width)))
            echo -n "${PROGRESS_CHARS:$char_idx:1}"
        else
            echo -n "█"
        fi
    done
    
    for ((i=0; i<empty; i++)); do
        echo -n "░"
    done
    
    echo -ne "┫ \033[0m${percent}%"
}

# Interactive menu with mouse support
interactive_menu() {
    local title="$1"
    shift
    local options=("$@")
    local selected=0
    local key
    
    # Enable mouse reporting if supported
    if [[ "$UDOS_TERMINAL_CAPS" =~ mouse ]]; then
        echo -ne "\033[?1000h"  # Enable mouse reporting
        trap 'echo -ne "\033[?1000l"' EXIT  # Disable on exit
    fi
    
    while true; do
        # Clear screen and draw menu
        clear
        echo -e "\033[1;36m╔$(printf '%*s' $((${#title}+4)) '' | tr ' ' '═')╗\033[0m"
        echo -e "\033[1;36m║  \033[1;37m${title}\033[1;36m  ║\033[0m"
        echo -e "\033[1;36m╠$(printf '%*s' $((${#title}+4)) '' | tr ' ' '═')╣\033[0m"
        
        for i in "${!options[@]}"; do
            if [[ $i -eq $selected ]]; then
                echo -e "\033[1;36m║\033[42m  ${options[$i]}$(printf '%*s' $((${#title}-${#options[$i]})) '')\033[0m\033[1;36m║\033[0m"
            else
                echo -e "\033[1;36m║\033[0m  ${options[$i]}$(printf '%*s' $((${#title}-${#options[$i]})) '')  \033[1;36m║\033[0m"
            fi
        done
        
        echo -e "\033[1;36m╚$(printf '%*s' $((${#title}+4)) '' | tr ' ' '═')╝\033[0m"
        echo -e "\033[2mUse ↑↓ to navigate, Enter to select, q to quit\033[0m"
        
        # Read key input
        read -rsn1 key
        case "$key" in
            $'\x1b')  # Escape sequence
                read -rsn2 key
                case "$key" in
                    "[A") ((selected > 0)) && ((selected--)) ;;      # Up arrow
                    "[B") ((selected < ${#options[@]}-1)) && ((selected++)) ;;  # Down arrow
                esac
                ;;
            "q"|"Q") return 1 ;;  # Quit
            "") return $selected ;;  # Enter key
        esac
    done
}

# Animated spinner
show_spinner() {
    local message="$1"
    local duration="${2:-3}"
    local pid="$3"
    
    local i=0
    while [[ $duration -gt 0 ]] || [[ -n "$pid" && -d "/proc/$pid" ]]; do
        local char=${SPINNER_CHARS:$((i % ${#SPINNER_CHARS})):1}
        echo -ne "\r\033[36m$char\033[0m $message"
        sleep 0.1
        ((i++))
        [[ -z "$pid" ]] && duration=$((duration-1))
    done
    echo -ne "\r\033[32m✓\033[0m $message\n"
}

# notification system
show_notification() {
    local type="$1"
    local title="$2"
    local message="$3"
    local duration="${4:-3}"
    
    local icon color
    case "$type" in
        "success") icon="✅"; color="32" ;;
        "warning") icon="⚠️ "; color="33" ;;
        "error") icon="❌"; color="31" ;;
        "info") icon="ℹ️ "; color="36" ;;
        *) icon="📢"; color="37" ;;
    esac
    
    # Try terminal-specific notifications
    if [[ "$UDOS_TERMINAL_CAPS" =~ iterm2 ]]; then
        # iTerm2 notification
        echo -e "\033]9;$title\007"
    elif [[ "$UDOS_TERMINAL_CAPS" =~ kitty ]]; then
        # Kitty notification
        echo -e "\033]99;i=1:d=0:p=title\033\\"
    fi
    
    # Terminal notification box
    local width=$((${#title} + ${#message} + 10))
    [[ $width -lt 40 ]] && width=40
    
    echo -e "\033[${color}m╔$(printf '%*s' $((width-2)) '' | tr ' ' '═')╗"
    echo -e "║ $icon \033[1m$title\033[0m\033[${color}m$(printf '%*s' $((width-${#title}-${#icon}-5)) '') ║"
    echo -e "║ $message$(printf '%*s' $((width-${#message}-3)) '') ║"
    echo -e "╚$(printf '%*s' $((width-2)) '' | tr ' ' '═')╝\033[0m"
    
    # Auto-dismiss
    if [[ $duration -gt 0 ]]; then
        sleep "$duration"
        # Clear notification (move cursor up and clear lines)
        echo -e "\033[4A\033[J"
    fi
}

# ASCII art generator
generate_ascii_art() {
    local text="$1"
    local style="${2:-standard}"
    
    case "$style" in
        "big")
            # Simple big text using Unicode block characters
            local lines=()
            for ((i=0; i<${#text}; i++)); do
                char="${text:$i:1}"
                case "$char" in
                    " ") lines+=("   ") ;;
                    "A") lines+=("▄▀█") ;;
                    "B") lines+=("▀▄▀") ;;
                    "C") lines+=("▄▀▀") ;;
                    "D") lines+=("█▀▄") ;;
                    "E") lines+=("█▀▀") ;;
                    *) lines+=("░░░") ;;
                esac
            done
            printf "%s\n" "${lines[@]}"
            ;;
        "3d")
            # 3D effect
            echo -e "\033[37m$text\033[0m"
            echo -e "\033[2m$(echo "$text" | sed 's/./&\\/g')\033[0m"
            ;;
        *)
            echo "$text"
            ;;
    esac
}

# Live dashboard with real-time updates
live_dashboard() {
    local refresh_interval="${1:-2}"
    local dashboard_width="${UDOS_DISPLAY_WIDTH:-80}"
    local progress_width="${UDOS_PROGRESS_WIDTH:-40}"
    
    # Clear screen and hide cursor
    clear
    echo -e "\033[?25l"
    trap 'echo -e "\033[?25h"; exit' INT TERM EXIT
    
    while true; do
        # Move to top of screen
        echo -e "\033[H"
        
        # Dashboard header - dynamically sized
        local header_line=$(printf '%*s' $dashboard_width '' | tr ' ' '═')
        echo -e "\033[1;36m╔${header_line}╗"
        local title="🌀 uDOS LIVE DASHBOARD 🌀"
        local title_padding=$(( (dashboard_width - ${#title}) / 2 ))
        echo -e "║$(printf '%*s' $title_padding '')${title}$(printf '%*s' $((dashboard_width - title_padding - ${#title})) '')║"
        echo -e "╠${header_line}╣\033[0m"
        
        # System metrics with real-time updates
        local cpu_usage=$(ps -A -o %cpu | awk '{s+=$1} END {print int(s)}')
        local mem_usage=$(ps -A -o %mem | awk '{s+=$1} END {print int(s)}')
        local disk_usage=$(df -h "$HOME" | awk 'NR==2 {print $5}' | sed 's/%//')
        
        local padding_space=$(printf '%*s' $((dashboard_width - progress_width - 15)) '')
        echo -e "\033[1;36m║\033[0m CPU: $(animated_progress_bar $cpu_usage $progress_width) $padding_space \033[1;36m║\033[0m"
        echo -e "\033[1;36m║\033[0m MEM: $(animated_progress_bar $mem_usage $progress_width) $padding_space \033[1;36m║\033[0m"
        echo -e "\033[1;36m║\033[0m DSK: $(animated_progress_bar $disk_usage $progress_width) $padding_space \033[1;36m║\033[0m"
        
        # Mission progress
        local mission_count=$(find "$UMEM/missions" -name "*.md" 2>/dev/null | wc -l)
        local move_count=$(find "$UMEM/moves" -name "*.md" 2>/dev/null | wc -l)
        
        echo -e "\033[1;36m╠${header_line}╣"
        local status_line="🎯 Missions: $(printf '%3d' $mission_count) │ 📝 Moves: $(printf '%3d' $move_count) │ ⏰ $(date '+%H:%M:%S')"
        local status_padding=$(( dashboard_width - ${#status_line} ))
        echo -e "║\033[0m $status_line$(printf '%*s' $status_padding '') \033[1;36m║\033[0m"
        echo -e "\033[1;36m╚${header_line}╝\033[0m"
        
        sleep "$refresh_interval"
    done
}

# Terminal image display (if supported)
display_image() {
    local image_path="$1"
    local width="${2:-80}"
    local height="${3:-24}"
    
    if [[ "$UDOS_TERMINAL_CAPS" =~ kitty ]]; then
        # Kitty graphics protocol
        kitty +kitten icat --align=left "$image_path"
    elif [[ "$UDOS_TERMINAL_CAPS" =~ iterm2 ]]; then
        # iTerm2 inline images
        echo -e "\033]1337;File=inline=1:$(base64 < "$image_path")\a"
    else
        # Fallback to ASCII art
        echo "🖼️  Image: $(basename "$image_path")"
        echo "   (Terminal doesn't support inline images)"
    fi
}

# Initialize visual framework
init_visual_framework() {
    bold "🎨 uDOS Visual Framework v1.1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Create visual directory structure
    mkdir -p "$VISUAL_DIR/themes"
    mkdir -p "$VISUAL_DIR/animations" 
    mkdir -p "$VISUAL_DIR/notifications"
    mkdir -p "$VISUAL_DIR/assets"
    mkdir -p "${UMEM}/config"
    
    # Configure screen size first
    cyan "📐 Configuring display settings..."
    configure_screen_size
    
    # Detect terminal capabilities
    cyan "🔍 Detecting terminal capabilities..."
    local caps=($(detect_terminal_capabilities))
    echo "  📺 Terminal: ${TERM_PROGRAM:-unknown} (${TERM_COLS}×${TERM_ROWS})"
    echo "  🎨 Capabilities: ${caps[*]}"
    echo "  📐 Display: ${UDOS_DISPLAY_WIDTH}×${UDOS_DISPLAY_HEIGHT}"
    
    # Create visual configuration
    cat > "$VISUAL_DIR/config.json" << EOF
{
    "version": "1.1",
    "terminal": {
        "program": "${TERM_PROGRAM:-unknown}",
        "capabilities": ["${caps[*]}"],
        "dimensions": {
            "cols": ${TERM_COLS},
            "rows": ${TERM_ROWS},
            "display_width": ${UDOS_DISPLAY_WIDTH},
            "display_height": ${UDOS_DISPLAY_HEIGHT}
        },
        "colors": {
            "truecolor": $(if [[ "${caps[*]}" =~ truecolor ]]; then echo "true"; else echo "false"; fi),
            "256color": true
        }
    },
    "animations": {
        "enabled": true,
        "spinner_speed": 100,
        "progress_refresh": 50,
        "progress_width": ${UDOS_PROGRESS_WIDTH}
    },
    "notifications": {
        "enabled": true,
        "duration": 3,
        "sound": false
    },
    "themes": {
        "current": "udos-dark",
        "available": ["udos-dark", "udos-light", "matrix", "cyberpunk"]
    },
    "layout": {
        "widget_width": ${UDOS_WIDGET_WIDTH},
        "dashboard_width": ${UDOS_DISPLAY_WIDTH}
    }
}
EOF
    
    green "✅ Visual framework initialized"
    echo "  📁 Config: $VISUAL_DIR/config.json"
    echo "  📁 Display: ${VISUAL_DIR}/display.conf"
    echo "  🎨 Capabilities: ${caps[*]}"
    echo "  📐 Screen: ${UDOS_DISPLAY_WIDTH}×${UDOS_DISPLAY_HEIGHT}"
}

# Theme system
apply_theme() {
    local theme="$1"
    
    case "$theme" in
        "udos-dark")
            export UDOS_PRIMARY="\033[1;36m"    # Cyan
            export UDOS_SECONDARY="\033[0;34m"  # Blue
            export UDOS_SUCCESS="\033[0;32m"    # Green
            export UDOS_WARNING="\033[0;33m"    # Yellow
            export UDOS_ERROR="\033[0;31m"      # Red
            export UDOS_TEXT="\033[0;37m"       # White
            ;;
        "udos-light")
            export UDOS_PRIMARY="\033[1;34m"    # Bold Blue
            export UDOS_SECONDARY="\033[0;36m"  # Cyan
            export UDOS_SUCCESS="\033[0;32m"    # Green
            export UDOS_WARNING="\033[0;33m"    # Yellow
            export UDOS_ERROR="\033[0;31m"      # Red
            export UDOS_TEXT="\033[0;30m"       # Black
            ;;
        "matrix")
            export UDOS_PRIMARY="\033[1;32m"    # Bright Green
            export UDOS_SECONDARY="\033[0;32m"  # Green
            export UDOS_SUCCESS="\033[1;32m"    # Bright Green
            export UDOS_WARNING="\033[1;33m"    # Bright Yellow
            export UDOS_ERROR="\033[1;31m"      # Bright Red
            export UDOS_TEXT="\033[0;32m"       # Green
            ;;
        "cyberpunk")
            export UDOS_PRIMARY="\033[1;35m"    # Magenta
            export UDOS_SECONDARY="\033[0;36m"  # Cyan
            export UDOS_SUCCESS="\033[1;32m"    # Bright Green
            export UDOS_WARNING="\033[1;33m"    # Bright Yellow
            export UDOS_ERROR="\033[1;31m"      # Bright Red
            export UDOS_TEXT="\033[0;37m"       # White
            ;;
    esac
    
    green "🎨 Applied theme: $theme"
    
    # Save theme preference
    echo "current_theme=$theme" > "$VISUAL_DIR/theme.conf"
}

# Interactive setup questions (calls actual template-based setup)
interactive_setup_questions() {
    bold "🎭 uDOS User Setup - Template-Based Interactive Mode"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Check if template-based setup processor exists
    local setup_processor="${UHOME}/uCode/setup-template-processor.sh"
    local setup_processor_compat="${UHOME}/uCode/setup-template-processor-compat.sh"
    local init_user="${UHOME}/uCode/init-user.sh"
    
    if [[ -f "$setup_processor" ]]; then
        green "🎨 Using uDOS Template System for setup..."
        echo
        
        # Determine which processor to use based on bash version
        local processor="$setup_processor"
        if [[ ${BASH_VERSION%%.*} -lt 4 ]]; then
            yellow "⚠️ Bash 3.x detected, using compatibility processor"
            processor="$setup_processor_compat"
        fi
        
        # Run the template-based setup
        if "$processor"; then
            green "✅ Standard setup completed successfully"
            
            # Load the generated configuration
            local config_file
            config_file=$(find "${UMEM}/config" -name "*_setup_vars.sh" -type f | sort | tail -1)
            
            if [[ -f "$config_file" ]]; then
                green "📋 Configuration saved: $config_file"
                
                # Show summary of what was configured
                echo
                bold "📊 Setup Summary:"
                echo "─────────────────"
                source "$config_file" 2>/dev/null && {
                    [[ -n "$UDOS_USERNAME" ]] && echo "👤 Username: $UDOS_USERNAME"
                    [[ -n "$UDOS_LOCATION" ]] && echo "📍 Location: $UDOS_LOCATION"
                    [[ -n "$UDOS_TIMEZONE" ]] && echo "⏰ Timezone: $UDOS_TIMEZONE"
                    [[ -n "$UDOS_THEME" ]] && echo "🎨 Theme: $UDOS_THEME"
                    [[ -n "$UDOS_OK_COMPANION" ]] && echo "🤖 OK Companion: $UDOS_OK_COMPANION"
                    [[ -n "$UDOS_DEFAULT_ROLE" ]] && echo "👤 Role: $UDOS_DEFAULT_ROLE"
                }
            fi
        else
            red "❌ Standard setup failed"
            yellow "� Falling back to init-user setup..."
            
            if [[ -f "$init_user" ]]; then
                "$init_user"
            else
                red "❌ No setup system available"
                return 1
            fi
        fi
        
    elif [[ -f "$init_user" ]]; then
        yellow "⚠️ Template processor not found, using init-user setup..."
        echo
        
        "$init_user"
        
    else
        red "❌ No setup system found"
        echo "Please ensure the following files exist:"
        echo "  • $setup_processor"
        echo "  • $init_user"
        return 1
    fi
    
    echo
    green "🎉 Setup process completed!"
    echo "You can now use uDOS with your configured settings."
}

# Widget system for modular dashboard components
show_widget_demo() {
    bold "📊 uDOS Widget System Demo"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Weather widget mockup
    show_weather_widget
    echo
    
    # System resources widget
    show_system_widget
    echo
    
    # Recent activity widget
    show_activity_widget
    echo
    
    # Git status widget
    show_git_widget
}

show_weather_widget() {
    echo -e "${UDOS_PRIMARY:-\033[1;36m}╔══════════════════════════════════════╗"
    echo -e "║           🌤️  Weather Widget          ║"
    echo -e "╠══════════════════════════════════════╣"
    echo -e "║ Location: San Francisco, CA          ║"
    echo -e "║ Temperature: 72°F (22°C)             ║"
    echo -e "║ Conditions: Partly Cloudy            ║"
    echo -e "║ Humidity: 65%                        ║"
    echo -e "╚══════════════════════════════════════╝\033[0m"
}

show_system_widget() {
    local cpu_usage=$(ps -A -o %cpu | awk '{s+=$1} END {print int(s/4)}')  # Rough estimate
    local mem_usage=$(ps -A -o %mem | awk '{s+=$1} END {print int(s/4)}')
    local uptime=$(uptime | awk -F, '{print $1}' | awk '{print $3" "$4}')
    
    echo -e "${UDOS_PRIMARY:-\033[1;36m}╔══════════════════════════════════════╗"
    echo -e "║         💻 System Resources          ║"
    echo -e "╠══════════════════════════════════════╣"
    echo -e "║ CPU:  $(printf "%-28s" "$(animated_progress_bar $cpu_usage 15)") ║"
    echo -e "║ MEM:  $(printf "%-28s" "$(animated_progress_bar $mem_usage 15)") ║"
    echo -e "║ Uptime: $(printf "%-26s" "$uptime") ║"
    echo -e "╚══════════════════════════════════════╝\033[0m"
}

show_activity_widget() {
    echo -e "${UDOS_PRIMARY:-\033[1;36m}╔══════════════════════════════════════╗"
    echo -e "║        📝 Recent Activity            ║"
    echo -e "╠══════════════════════════════════════╣"
    echo -e "║ • visual framework          ║"
    echo -e "║ • Updated dashboard system           ║"
    echo -e "║ • Improved mission tracking          ║"
    echo -e "║ • Added OK Companion system          ║"
    echo -e "╚══════════════════════════════════════╝\033[0m"
}

show_git_widget() {
    local git_branch=""
    local git_status=""
    
    if git rev-parse --git-dir >/dev/null 2>&1; then
        git_branch=$(git branch --show-current 2>/dev/null || echo "detached")
        local changes=$(git status --porcelain 2>/dev/null | wc -l)
        git_status="$changes changes"
    else
        git_branch="no repo"
        git_status="not a git repo"
    fi
    
    echo -e "${UDOS_PRIMARY:-\033[1;36m}╔══════════════════════════════════════╗"
    echo -e "║            🌿 Git Status             ║"
    echo -e "╠══════════════════════════════════════╣"
    echo -e "║ Branch: $(printf "%-26s" "$git_branch") ║"
    echo -e "║ Status: $(printf "%-26s" "$git_status") ║"
    echo -e "║ Remote: $(printf "%-26s" "origin") ║"
    echo -e "╚══════════════════════════════════════╝\033[0m"
}

# System status overview
show_system_status() {
    clear
    bold "🔍 uDOS System Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Check core directories
    echo "📁 Directory Structure:"
    for dir in uCode uMemory uKnowledge uScript uTemplate; do
        if [[ -d "$UHOME/$dir" ]]; then
            green "  ✅ $dir"
        else
            red "  ❌ $dir (missing)"
        fi
    done
    echo
    
    # Check essential scripts
    echo "⚙️  Core Scripts:"
    for script in ucode.sh check.sh dash.sh; do
        if [[ -f "$UHOME/uCode/$script" ]]; then
            green "  ✅ $script"
        else
            red "  ❌ $script (missing)"
        fi
    done
    echo
    
    # Check VS Code extension
    echo "🔌 VS Code Integration:"
    if [[ -d "$UHOME/extension" ]]; then
        green "  ✅ Extension directory exists"
        if [[ -f "$UHOME/extension/package.json" ]]; then
            green "  ✅ Extension package.json"
        else
            yellow "  ⚠️ Extension package.json missing"
        fi
    else
        red "  ❌ Extension directory missing"
    fi
    echo
    
    # Check packages
    echo "📦 Package Status:"
    local packages=("ripgrep" "bat" "fd" "glow" "fzf" "jq")
    for pkg in "${packages[@]}"; do
        if command -v "$pkg" >/dev/null 2>&1; then
            green "  ✅ $pkg"
        else
            yellow "  ⚠️ $pkg (not installed)"
        fi
    done
    echo
    
    # Memory usage
    echo "💾 Memory Structure:"
    if [[ -d "$UMEM" ]]; then
        local missions=$(find "$UMEM/missions" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        local moves=$(find "$UMEM/moves" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        local logs=$(find "$UMEM/logs" -name "*.log" 2>/dev/null | wc -l | tr -d ' ')
        
        cyan "  📝 Missions: $missions"
        cyan "  🎯 Moves: $moves"
        cyan "  📊 Logs: $logs"
    else
        red "  ❌ uMemory directory missing"
    fi
}

# OK Companion - Interactive prompt for available uCompanions
show_ok_companion() {
    bold "🤖 OK Companion - Available uCompanions"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Check what uCompanions are available
    local ucompanion_dir="${UHOME}/uCompanion"
    local ucode_dir="${UHOME}/uCode"
    local available_companions=()
    
    # Core uCompanions system
    if [[ -f "$ucode_dir/companion-system.sh" ]]; then
        cyan "🎯 uCompanion System Status:"
        echo "─────────────────────────────"
        
        # Check for available companions
        if [[ -d "$ucompanion_dir" ]]; then
            green "  ✅ uCompanion directory exists"
            
            # Look for companion definitions
            local companion_files=$(find "$ucompanion_dir" -name "*.md" -o -name "*.json" 2>/dev/null | wc -l)
            if [[ $companion_files -gt 0 ]]; then
                available_companions+=("Gemini - Google OK companion")
                available_companions+=("Chester - Development assistant") 
                available_companions+=("Custom - User-defined companions")
            fi
        else
            yellow "  ⚠️  uCompanion directory not found"
        fi
        
        # Check companion system script
        if [[ -x "$ucode_dir/companion-system.sh" ]]; then
            green "  ✅ Companion system available"
        else
            yellow "  ⚠️  Companion system not executable"
        fi
    else
        red "  ❌ uCompanion system not found"
    fi
    
    echo
    cyan "🤖 Available uCompanions (uc):"
    echo "──────────────────────────────"
    if [[ ${#available_companions[@]} -gt 0 ]]; then
        for companion in "${available_companions[@]}"; do
            echo "  • $companion"
        done
    else
        yellow "  No uCompanions detected - run companion system setup"
    fi
    echo
    
    # Interactive companion selection
    cyan "🎯 uCompanion Quick Actions:"
    echo "─────────────────────────────"
    echo "  1. Start Gemini companion (./uCode/companion-system.sh gemini)"
    echo "  2. Initialize Chester assistant (./uCode/companion-system.sh chester)" 
    echo "  3. List all companions (./uCode/companion-system.sh list)"
    echo "  4. Setup new companion (./uCode/companion-system.sh init)"
    echo "  5. Companion system help (./uCode/companion-system.sh help)"
    echo "  6. Return to main uDOS"
    echo "  7. Exit OK Companion"
    echo
    
    read -p "🤖 OK, which uCompanion would you like? (1-7): " choice
    
    case "$choice" in
        1)
            green "🧠 Starting Gemini companion..."
            if [[ -f "$ucode_dir/companion-system.sh" ]]; then
                "$ucode_dir/companion-system.sh" gemini
            else
                red "❌ Companion system not found"
            fi
            ;;
        2)
            green "� Initializing Chester assistant..."
            if [[ -f "$ucode_dir/companion-system.sh" ]]; then
                "$ucode_dir/companion-system.sh" chester
            else
                red "❌ Companion system not found"
            fi
            ;;
        3)
            green "� Listing all uCompanions..."
            if [[ -f "$ucode_dir/companion-system.sh" ]]; then
                "$ucode_dir/companion-system.sh" list
            else
                red "❌ Companion system not found"
            fi
            ;;
        4)
            green "🎭 Setting up new companion..."
            if [[ -f "$ucode_dir/companion-system.sh" ]]; then
                "$ucode_dir/companion-system.sh" init
            else
                red "❌ Companion system not found"
            fi
            ;;
        5)
            green "📚 uCompanion system help:"
            echo
            if [[ -f "$ucode_dir/companion-system.sh" ]]; then
                "$ucode_dir/companion-system.sh" help
            else
                echo "Available uCompanion commands:"
                echo "  ./uCode/companion-system.sh gemini     - Start Gemini OK companion"
                echo "  ./uCode/companion-system.sh chester    - Start Chester development assistant" 
                echo "  ./uCode/companion-system.sh list       - List all available companions"
                echo "  ./uCode/companion-system.sh init       - Initialize new companion"
                echo "  ./uCode/companion-system.sh help       - Show detailed help"
            fi
            echo
            ;;
        6)
            green "🚀 Launching main uDOS shell..."
            if [[ -f "$ucode_dir/ucode.sh" ]]; then
                exec "$ucode_dir/ucode.sh"
            else
                red "❌ ucode.sh not found"
            fi
            ;;
        7)
            green "👋 OK Companion signing off! See you next time!"
            return 0
            ;;
        *)
            yellow "⚠️  Invalid choice. Please select 1-7."
            ;;
    esac
}

# Performance benchmark for visual elements
run_visual_benchmark() {
    bold "⚡ Visual Framework Performance Benchmark"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Progress bar rendering speed
    echo "🔄 Testing progress bar rendering..."
    local start_time=$(date +%s.%N)
    for i in {1..50}; do
        echo -ne "\r  "
        animated_progress_bar $((i * 2)) 30 "Benchmark"
        sleep 0.01
    done
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "unknown")
    echo
    green "  ⏱️  Progress bars: ${duration}s for 50 frames"
    echo
    
    # Spinner performance
    echo "🌀 Testing spinner performance..."
    start_time=$(date +%s.%N)
    for i in {1..20}; do
        local char=${SPINNER_CHARS:$((i % ${#SPINNER_CHARS})):1}
        echo -ne "\r  $char Testing spinner speed"
        sleep 0.05
    done
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "unknown")
    echo
    green "  ⏱️  Spinner: ${duration}s for 20 frames"
    echo
    
    # Color output speed
    echo "🎨 Testing color output..."
    start_time=$(date +%s.%N)
    for color in {31..36}; do
        echo -e "  \033[${color}m■■■■■ Color test $color\033[0m"
    done
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "unknown")
    green "  ⏱️  Color output: ${duration}s for 6 colors"
    echo
    
    # Terminal capabilities
    echo "📺 Terminal Capabilities:"
    local caps=($(detect_terminal_capabilities))
    for cap in "${caps[@]}"; do
        cyan "  🔹 $cap"
    done
    
    echo
    green "✅ Benchmark complete"
}

# Command handling
case "${1:-demo}" in
    "init")
        init_visual_framework
        ;;
    "setup")
        interactive_setup_questions
        ;;
    "demo")
        bold "🎨 uDOS Visual Framework Demo"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo
        
        echo "1. Progress bar animation:"
        for i in 10 20 30 40 50 60 70 80 90 100; do
            echo -ne "\r  "
            animated_progress_bar $i 40 "Demo Progress" "gradient"
            sleep 0.3
        done
        echo
        echo
        
        echo "2. Spinner animation:"
        show_spinner "Processing data..." 2
        
        echo "3. Notifications:"
        show_notification "success" "Demo Complete" "Visual framework working!" 2
        
        echo "4. ASCII Art:"
        generate_ascii_art "uDOS" "big"
        ;;
    "menu")
        interactive_menu "uDOS Main Menu" "Dashboard" "Missions" "Settings" "Help" "Exit"
        echo "Selected option: $?"
        ;;
    "live")
        live_dashboard "${2:-2}"
        ;;
    "caps")
        detect_terminal_capabilities
        ;;
    "help")
        echo "uDOS Visual Framework v1.2"
        echo ""
        echo "Commands:"
        echo "  init       Initialize visual framework"
        echo "  setup      Interactive setup questions (template-based with latest questions)"
        echo "  demo       Show visual capabilities demo"
        echo "  menu       Interactive menu demo"  
        echo "  live       Live dashboard (refresh interval)"
        echo "  theme      Apply theme [udos-dark|udos-light|matrix|cyberpunk]"
        echo "  widgets    Show dashboard widget demo"
        echo "  status     Display comprehensive system status"
        echo "  benchmark  Run visual performance benchmark"
        echo "  caps       Show terminal capabilities"
        echo "  screen     Configure screen size and display settings"
        echo "  ok         OK Companion - Interactive prompt for uCompanions (uc)"
        echo "  help       Show this help"
        ;;
    "theme")
        shift
        apply_theme "${1:-udos-dark}"
        ;;
    "widgets")
        show_widget_demo
        ;;
    "status")
        show_system_status
        ;;
    "benchmark")
        run_visual_benchmark
        ;;
    "screen")
        configure_screen_size
        ;;
    "ok")
        show_ok_companion
        ;;
    *)
        red "❌ Unknown command: $1"
        echo "Use 'help' for available commands"
        exit 1
        ;;
esac
