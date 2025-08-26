````markdown
# uDOS ASCII Dashboard Display Template

**Template**: uDISPLAY-ascii-dashboard.md
**Version**: v1.0.4.1
**Purpose**: Comprehensive ASCII-based system dashboards with real-time metrics and visual indicators
**Integration**: uGRID, uCELL, three-mode display architecture (CLI, Desktop, Web)

---

## 🎯 Dashboard Configuration Variables

### User Information
```bash
# User context variables
DASHBOARD_TITLE="${DASHBOARD_TITLE:-uDOS Control Center}"
DASHBOARD_SUBTITLE="${DASHBOARD_SUBTITLE:-Universal Device Operating System}"
USER_NAME="${USER_NAME:-$(whoami)}"
USER_LOCATION="${USER_LOCATION:-Unknown}"
USER_TIMEZONE="${USER_TIMEZONE:-$(date +%Z)}"
CURRENT_TIME="${CURRENT_TIME:-$(date '+%H:%M:%S')}"
SYSTEM_UPTIME="${SYSTEM_UPTIME:-$(uptime | grep -o '[0-9]* day' | cut -d' ' -f1 || echo 0)}"
HEALTH_STATUS="${HEALTH_STATUS:-💚 Healthy}"
```

### System Metrics
```bash
# Real-time system metrics
MISSIONS_COUNT="${MISSIONS_COUNT:-0}"
MOVES_TODAY="${MOVES_TODAY:-0}"
TEMPLATES_COUNT="${TEMPLATES_COUNT:-0}"
ERRORS_TODAY="${ERRORS_TODAY:-0}"
DATASETS_COUNT="${DATASETS_COUNT:-0}"
DATASET_RECORDS="${DATASET_RECORDS:-0}"
```

### Mission Tracking
```bash
# Active mission information
CURRENT_MISSION="${CURRENT_MISSION:-No active mission}"
RECENT_MOVE_1="${RECENT_MOVE_1:-System initialization}"
RECENT_MOVE_2="${RECENT_MOVE_2:-Dashboard loaded}"
RECENT_MOVE_3="${RECENT_MOVE_3:-Ready for operations}"
```

### Performance Metrics
```bash
# Progress and efficiency tracking
DAILY_PROGRESS="${DAILY_PROGRESS:-0}"
MISSION_COMPLETION="${MISSION_COMPLETION:-0}"
ERROR_RATE="${ERROR_RATE:-0}"
SYSTEM_EFFICIENCY="${SYSTEM_EFFICIENCY:-100}"
```

### Resource Usage
```bash
# System resource monitoring
STORAGE_USED="${STORAGE_USED:-0}"
STORAGE_TOTAL="${STORAGE_TOTAL:-100}"
STORAGE_PERCENT="${STORAGE_PERCENT:-0}"
MEMORY_USED="${MEMORY_USED:-0}"
MEMORY_TOTAL="${MEMORY_TOTAL:-8192}"
MEMORY_PERCENT="${MEMORY_PERCENT:-0}"
CPU_USAGE="${CPU_USAGE:-0}"
TOTAL_FILES="${TOTAL_FILES:-0}"
TOTAL_DIRECTORIES="${TOTAL_DIRECTORIES:-0}"
```

---

## 🧮 Dashboard Generation Functions

### Progress Bar Generator
```bash
# Usage: generate_progress_bar "percentage" "width"
generate_progress_bar() {
    local percentage="$1"
    local width="${2:-20}"
    local filled=$(( percentage * width / 100 ))
    local empty=$(( width - filled ))

    printf "█%.0s" $(seq 1 $filled)
    printf "░%.0s" $(seq 1 $empty)
}

# Usage: generate_detailed_progress_bar "percentage" "width"
generate_detailed_progress_bar() {
    local percentage="$1"
    local width="${2:-30}"
    local filled=$(( percentage * width / 100 ))
    local partial=$(( (percentage * width % 100) / 12 ))
    local empty=$(( width - filled - (partial > 0 ? 1 : 0) ))

    printf "█%.0s" $(seq 1 $filled)
    [[ $partial -gt 0 ]] && printf "%s" "▉▊▋▌▍▎▏" | cut -c$partial
    printf "░%.0s" $(seq 1 $empty)
}
```

### Status Indicator Generator
```bash
# Usage: get_status_indicator "percentage"
get_status_indicator() {
    local value="$1"
    if (( value >= 80 )); then
        echo "💚"
    elif (( value >= 60 )); then
        echo "🟡"
    else
        echo "🔴"
    fi
}

# Usage: format_metric "label" "value" "unit" "width"
format_metric() {
    local label="$1"
    local value="$2"
    local unit="$3"
    local width="${4:-20}"

    printf "%-*s %s%s" $((width-${#value}-${#unit})) "$label:" "$value" "$unit"
}
```

### System Data Collection
```bash
# Collect real-time system metrics
collect_system_metrics() {
    # CPU usage
    CPU_USAGE=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//' 2>/dev/null || echo "0")

    # Memory usage
    local memory_info=$(vm_stat 2>/dev/null || echo "")
    if [[ -n "$memory_info" ]]; then
        local page_size=$(vm_stat | grep "page size" | awk '{print $8}' || echo "4096")
        local pages_free=$(echo "$memory_info" | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
        local pages_active=$(echo "$memory_info" | grep "Pages active" | awk '{print $3}' | sed 's/\.//')
        MEMORY_USED=$(( (pages_active * page_size) / 1024 / 1024 ))
        MEMORY_TOTAL=$(( ((pages_free + pages_active) * page_size) / 1024 / 1024 ))
        MEMORY_PERCENT=$(( pages_active * 100 / (pages_free + pages_active) ))
    fi

    # Storage usage
    local storage_info=$(df -h / 2>/dev/null | tail -1)
    if [[ -n "$storage_info" ]]; then
        STORAGE_USED=$(echo "$storage_info" | awk '{print $3}' | sed 's/G//')
        STORAGE_TOTAL=$(echo "$storage_info" | awk '{print $2}' | sed 's/G//')
        STORAGE_PERCENT=$(echo "$storage_info" | awk '{print $5}' | sed 's/%//')
    fi

    # File counts
    TOTAL_FILES=$(find . -type f 2>/dev/null | wc -l | tr -d ' ')
    TOTAL_DIRECTORIES=$(find . -type d 2>/dev/null | wc -l | tr -d ' ')
}
```

---

## 🎨 Dashboard Layout Templates

### Main Dashboard Header
```bash
render_dashboard_header() {
    local width="${UDOS_TERMINAL_COLS:-94}"
    local title_padding=$(( (width - ${#DASHBOARD_TITLE} - 4) / 2 ))
    local subtitle_padding=$(( (width - ${#DASHBOARD_SUBTITLE} - 2) / 2 ))

    echo "╔$(printf "%*s" $((width-2)) "" | tr ' ' "═")╗"
    echo "║$(printf "%*s" $title_padding "")🌀 ${DASHBOARD_TITLE} 🌀$(printf "%*s" $((width-${#DASHBOARD_TITLE}-title_padding-6)) "")║"
    echo "║$(printf "%*s" $subtitle_padding "")${DASHBOARD_SUBTITLE}$(printf "%*s" $((width-${#DASHBOARD_SUBTITLE}-subtitle_padding-2)) "")║"
    echo "╠$(printf "%*s" $((width-2)) "" | tr ' ' "═")╣"
}
```

### User Information Section
```bash
render_user_info() {
    local width="${UDOS_TERMINAL_COLS:-94}"

    echo "║ 👤 USER: ${USER_NAME}$(printf "%*s" $((20-${#USER_NAME})) "")│ 📍 LOCATION: ${USER_LOCATION}$(printf "%*s" $((20-${#USER_LOCATION})) "")│ ⏰ TIME: ${CURRENT_TIME}$(printf "%*s" $((width-80)) "")║"
    echo "║ 🏠 BASE: ${USER_TIMEZONE}$(printf "%*s" $((20-${#USER_TIMEZONE})) "")│ ⏳ UPTIME: ${SYSTEM_UPTIME} days$(printf "%*s" $((15-${#SYSTEM_UPTIME})) "")│ 💚 HEALTH: ${HEALTH_STATUS}$(printf "%*s" $((width-80)) "")║"
}
```

### System Metrics Section
```bash
render_system_metrics() {
    local width="${UDOS_TERMINAL_COLS:-94}"

    echo "╠$(printf "%*s" $((width-2)) "" | tr ' ' "═")╣"
    echo "║$(printf "%*s" $(((width-20)/2)) "")📊 SYSTEM METRICS$(printf "%*s" $(((width-20)/2)) "")║"
    echo "╠$(printf "%*s" $((width-2)) "" | tr ' ' "═")╣"
    echo "║ 🎯 MISSIONS: ${MISSIONS_COUNT}$(printf "%*s" $((15-${#MISSIONS_COUNT})) "")│ 🔄 TODAY'S MOVES: ${MOVES_TODAY}$(printf "%*s" $((15-${#MOVES_TODAY})) "")│ 📋 TEMPLATES: ${TEMPLATES_COUNT}$(printf "%*s" $((width-65)) "")║"
    echo "║ ❌ ERRORS: ${ERRORS_TODAY}$(printf "%*s" $((17-${#ERRORS_TODAY})) "")│ 📊 DATASETS: ${DATASETS_COUNT}$(printf "%*s" $((17-${#DATASETS_COUNT})) "")│ 📦 RECORDS: ${DATASET_RECORDS}$(printf "%*s" $((width-65)) "")║"
}
```

### Performance Dashboard Section
```bash
render_performance_dashboard() {
    local width="${UDOS_TERMINAL_COLS:-95}"

    # Collect current metrics
    collect_system_metrics

    # Generate progress bars
    local daily_bar="$(generate_progress_bar "$DAILY_PROGRESS" 20)"
    local mission_bar="$(generate_progress_bar "$MISSION_COMPLETION" 20)"
    local error_bar="$(generate_progress_bar "$ERROR_RATE" 20)"
    local efficiency_bar="$(generate_progress_bar "$SYSTEM_EFFICIENCY" 20)"

    echo ""
    echo "$(printf "%*s" $(((width-30)/2)) "")🌟 PERFORMANCE DASHBOARD 🌟"
    echo ""
    echo "┌$(printf "%*s" $((width-2)) "" | tr ' ' "─")┐"
    echo "│$(printf "%*s" $(((width-23)/2)) "")📈 ANALYTICS OVERVIEW$(printf "%*s" $(((width-23)/2)) "")│"
    echo "├$(printf "%*s" $((width-2)) "" | tr ' ' "─")┤"
    echo "│ Daily Progress:     [${daily_bar}] ${DAILY_PROGRESS}%$(printf "%*s" $((width-50)) "")│"
    echo "│ Mission Completion: [${mission_bar}] ${MISSION_COMPLETION}%$(printf "%*s" $((width-50)) "")│"
    echo "│ Error Rate:         [${error_bar}] ${ERROR_RATE}%$(printf "%*s" $((width-50)) "")│"
    echo "│ System Efficiency:  [${efficiency_bar}] ${SYSTEM_EFFICIENCY}%$(printf "%*s" $((width-50)) "")│"
    echo "├$(printf "%*s" $((width-2)) "" | tr ' ' "─")┤"
    echo "│$(printf "%*s" $(((width-18)/2)) "")📊 RESOURCE USAGE$(printf "%*s" $(((width-18)/2)) "")│"
    echo "├$(printf "%*s" $((width-2)) "" | tr ' ' "─")┤"
    echo "│ 💾 Storage:         ${STORAGE_USED}GB / ${STORAGE_TOTAL}GB (${STORAGE_PERCENT}%)$(printf "%*s" $((width-40)) "")│"
    echo "│ 🧠 Memory:          ${MEMORY_USED}MB / ${MEMORY_TOTAL}MB (${MEMORY_PERCENT}%)$(printf "%*s" $((width-40)) "")│"
    echo "│ ⚡ CPU:             ${CPU_USAGE}% average$(printf "%*s" $((width-25)) "")│"
    echo "│ 📁 Files:           ${TOTAL_FILES} files in ${TOTAL_DIRECTORIES} directories$(printf "%*s" $((width-35)) "")│"
    echo "└$(printf "%*s" $((width-2)) "" | tr ' ' "─")┘"
}
```

### Quick Actions Section
```bash
render_quick_actions() {
    local width="${UDOS_TERMINAL_COLS:-94}"

    echo "╠$(printf "%*s" $((width-2)) "" | tr ' ' "═")╣"
    echo "║$(printf "%*s" $(((width-15)/2)) "")🔧 QUICK ACTIONS$(printf "%*s" $(((width-15)/2)) "")║"
    echo "╠$(printf "%*s" $((width-2)) "" | tr ' ' "═")╣"
    echo "║ [check:health]  │ [json:stats]    │ [error:stats]   │ [mission:list]  │ [template:list]$(printf "%*s" $((width-85)) "")║"
    echo "║ [run:backup]    │ [dash:refresh]  │ [log:today]     │ [tree:generate] │ [help]$(printf "%*s" $((width-75)) "")║"
}
```

### Dashboard Footer
```bash
render_dashboard_footer() {
    local width="${UDOS_TERMINAL_COLS:-94}"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S %Z')"
    local footer_text="📅 Generated: ${timestamp}"
    local footer_padding=$(( (width - ${#footer_text} - 2) / 2 ))

    echo "╠$(printf "%*s" $((width-2)) "" | tr ' ' "═")╣"
    echo "║$(printf "%*s" $footer_padding "")${footer_text}$(printf "%*s" $((width-${#footer_text}-footer_padding-2)) "")║"
    echo "╚$(printf "%*s" $((width-2)) "" | tr ' ' "═")╝"
}
```

---

## 🚀 Complete Dashboard Renderer

### Main Dashboard Function
```bash
# Usage: render_complete_dashboard
render_complete_dashboard() {
    # Initialize display configuration
    source "$UMEMORY/config/display-vars.sh" 2>/dev/null || true

    # Collect real-time metrics
    collect_system_metrics

    # Clear screen for full dashboard
    clear

    # Render complete dashboard
    render_dashboard_header
    render_user_info
    render_system_metrics

    echo "╠$(printf "%*s" $((UDOS_TERMINAL_COLS-2)) "" | tr ' ' "═")╣"
    echo "║$(printf "%*s" $(((UDOS_TERMINAL_COLS-16)/2)) "")🎯 ACTIVE MISSION$(printf "%*s" $(((UDOS_TERMINAL_COLS-16)/2)) "")║"
    echo "╠$(printf "%*s" $((UDOS_TERMINAL_COLS-2)) "" | tr ' ' "═")╣"
    echo "║ ${CURRENT_MISSION}$(printf "%*s" $((UDOS_TERMINAL_COLS-${#CURRENT_MISSION}-3)) "")║"

    echo "╠$(printf "%*s" $((UDOS_TERMINAL_COLS-2)) "" | tr ' ' "═")╣"
    echo "║$(printf "%*s" $(((UDOS_TERMINAL_COLS-17)/2)) "")📝 RECENT ACTIVITY$(printf "%*s" $(((UDOS_TERMINAL_COLS-17)/2)) "")║"
    echo "╠$(printf "%*s" $((UDOS_TERMINAL_COLS-2)) "" | tr ' ' "═")╣"
    echo "║ ${RECENT_MOVE_1}$(printf "%*s" $((UDOS_TERMINAL_COLS-${#RECENT_MOVE_1}-3)) "")║"
    echo "║ ${RECENT_MOVE_2}$(printf "%*s" $((UDOS_TERMINAL_COLS-${#RECENT_MOVE_2}-3)) "")║"
    echo "║ ${RECENT_MOVE_3}$(printf "%*s" $((UDOS_TERMINAL_COLS-${#RECENT_MOVE_3}-3)) "")║"

    render_quick_actions
    render_dashboard_footer

    # Render performance section
    render_performance_dashboard

    echo ""
    echo "$(printf "%*s" $(((UDOS_TERMINAL_COLS-50)/2)) "")═$(printf "%*s" 48 "" | tr ' ' "═")═"
    echo ""
    echo "🌀 uDOS ASCII Dashboard v1.0.4.1 | Generated: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "📊 Three-Mode Display: CLI Terminal | Desktop App | Web Export"
    echo ""
    echo "$(printf "%*s" $(((UDOS_TERMINAL_COLS-50)/2)) "")═$(printf "%*s" 48 "" | tr ' ' "═")═"
}
```

### Compact Dashboard Function
```bash
# Usage: render_compact_dashboard
render_compact_dashboard() {
    local width="${UDOS_COMPACT_WIDTH:-60}"

    collect_system_metrics

    echo "┌$(printf "%*s" $((width-2)) "" | tr ' ' "─")┐"
    echo "│$(printf "%*s" $(((width-16)/2)) "")🌀 uDOS Dashboard$(printf "%*s" $(((width-16)/2)) "")│"
    echo "├$(printf "%*s" $((width-2)) "" | tr ' ' "─")┤"
    echo "│ 👤 ${USER_NAME} | 📍 ${USER_LOCATION} | ⏰ ${CURRENT_TIME}$(printf "%*s" $((width-35)) "")│"
    echo "│ 🎯 ${MISSIONS_COUNT} missions | 🔄 ${MOVES_TODAY} moves | ❌ ${ERRORS_TODAY} errors$(printf "%*s" $((width-35)) "")│"
    echo "│ 💾 ${STORAGE_PERCENT}% storage | 🧠 ${MEMORY_PERCENT}% memory | ⚡ ${CPU_USAGE}% CPU$(printf "%*s" $((width-35)) "")│"
    echo "└$(printf "%*s" $((width-2)) "" | tr ' ' "─")┘"
}
```

---

## 🎨 Three-Mode Display Integration

### CLI Terminal Mode
```bash
render_cli_dashboard() {
    # Pure ASCII for terminal compatibility
    render_complete_dashboard
}
```

### Desktop Application Mode
```bash
render_desktop_dashboard() {
    # Enhanced ASCII with better fonts and spacing
    echo -e "\033[1;36m"  # Enable color
    render_complete_dashboard
    echo -e "\033[0m"     # Reset color
}
```

### Web Export Mode
```bash
render_web_dashboard() {
    # HTML-compatible ASCII for web display
    echo "<pre class='udos-dashboard'>"
    render_complete_dashboard | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g'
    echo "</pre>"
}
```

---

## 🔧 Usage Examples

### Quick Status Check
```bash
# Show compact dashboard
render_compact_dashboard
```

### Full System Dashboard
```bash
# Show complete dashboard with all metrics
render_complete_dashboard
```

### Export for Web Sharing
```bash
# Generate web-compatible dashboard
render_web_dashboard > dashboard.html
```

### Real-time Monitoring
```bash
# Continuous dashboard updates
while true; do
    render_complete_dashboard
    sleep 30
done
```

---

## 📱 Template Integration

### uCode Command Integration
```bash
# Dashboard commands that use this template:
# ucode DASHBOARD        → render_complete_dashboard
# ucode DASHBOARD COMPACT → render_compact_dashboard
# ucode STATUS          → render_compact_dashboard
# ucode MONITOR         → continuous dashboard updates
```

### Display System Integration
```bash
# Three-mode display support:
# ./udos-display.sh dashboard cli     → CLI terminal mode
# ./udos-display.sh dashboard app     → Desktop application mode
# ./udos-display.sh dashboard export  → Web export mode
```

### Data Collection Integration
```bash
# Automatic metric collection from:
# - System resources (CPU, memory, storage)
# - uDOS mission tracking system
# - Template generation statistics
# - Error logging and monitoring
# - User activity and progress tracking
```

---

*uDOS v1.0.4.1 Display Template - ASCII Dashboard*
*Comprehensive system monitoring with three-mode display architecture*

````
