#!/bin/bash
# uDOS Enhanced Dashboard v2.0.0
# Description: Template-integrated dashboard with ASCII blocks and shortcode support

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
UMEM="$UHOME/uMemory"
UCODE="$UHOME/uCode"
UTEMPLATE="$UHOME/uTemplate"

# Dashboard Configuration
DASHBOARD_DIR="$UMEM/dashboard"
DASHBOARD_FILE="$DASHBOARD_DIR/current.md"
ASCII_DASHBOARD="$DASHBOARD_DIR/ascii.txt"
ANALYTICS_FILE="$UDEV/state/analytics.json"
CONFIG_FILE="$DASHBOARD_DIR/config.json"

# Template Files
DASHBOARD_TEMPLATE="$UTEMPLATE/dashboard-template.md"
ASCII_TEMPLATE="$UTEMPLATE/ascii-dashboard-template.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] [dash]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] [ERROR]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] [SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] [WARNING]${NC} $1"
}

# Initialize dashboard system
initialize_dashboard() {
    log_info "Initializing Enhanced Dashboard v2.0.0"
    
    # Create directories
    mkdir -p "$DASHBOARD_DIR"
    mkdir -p "$UDEV/state"
    mkdir -p "$UMEM/logs"
    
    # Create default configuration
    create_dashboard_config
    
    log_success "Dashboard system initialized"
}

# Create dashboard configuration
create_dashboard_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        cat > "$CONFIG_FILE" << 'EOF'
{
  "version": "2.0.0",
  "updated": "{{timestamp}}",
  "settings": {
    "refresh_interval": 300,
    "auto_refresh": true,
    "ascii_mode": true,
    "show_analytics": true,
    "max_recent_moves": 5,
    "max_recent_missions": 3
  },
  "display": {
    "title": "uDOS COMMAND CENTER",
    "subtitle": "Enhanced Dashboard v2.0.0",
    "theme": "default",
    "show_progress_bars": true,
    "show_ascii_art": true
  },
  "modules": {
    "system_status": true,
    "mission_summary": true,
    "recent_activity": true,
    "quick_actions": true,
    "analytics": true,
    "package_status": true
  }
}
EOF
        log_info "Created default dashboard configuration"
    fi
}

# Collect system metrics
collect_system_metrics() {
    log_info "Collecting system metrics..."
    
    local metrics_file="$UDEV/state/metrics-$(date +%Y%m%d-%H%M%S).json"
    
    # System information
    local hostname=$(hostname)
    local uptime_days=$(uptime | awk '{print $3}' | sed 's/,//')
    local current_user=$(whoami)
    local current_date=$(date -Iseconds)
    
    # uDOS statistics
    local missions_count=$(find "$UMEM/missions" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local moves_today=$(find "$UMEM/moves" -name "*$(date +%Y-%m-%d)*" 2>/dev/null | wc -l | tr -d ' ')
    local templates_count=$(find "$UTEMPLATE" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local errors_today=$(grep -c "ERROR" "$UMEM/logs"/*$(date +%Y-%m-%d)* 2>/dev/null || echo "0")
    
    # Package status
    local packages_installed=0
    local packages_total=0
    if [[ -f "$UMEM/packages/registry.json" ]]; then
        if command -v jq >/dev/null 2>&1; then
            packages_total=$(jq '.packages | length' "$UMEM/packages/registry.json" 2>/dev/null || echo "0")
            packages_installed=$(find "$UMEM/packages/installed" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
        fi
    fi
    
    # Storage information
    local storage_info=$(df -h "$UHOME" 2>/dev/null | tail -1)
    local storage_used=$(echo "$storage_info" | awk '{print $3}')
    local storage_total=$(echo "$storage_info" | awk '{print $2}')
    local storage_percent=$(echo "$storage_info" | awk '{print $5}' | sed 's/%//')
    
    # Memory information (macOS compatible)
    local memory_pressure=$(memory_pressure 2>/dev/null | grep "System" | awk '{print $5}' || echo "normal")
    
    # Create metrics JSON
    cat > "$metrics_file" << EOF
{
  "timestamp": "$current_date",
  "system": {
    "hostname": "$hostname",
    "user": "$current_user",
    "uptime_days": "$uptime_days",
    "memory_pressure": "$memory_pressure"
  },
  "storage": {
    "used": "$storage_used",
    "total": "$storage_total",
    "percent": "$storage_percent"
  },
  "udos": {
    "missions_count": $missions_count,
    "moves_today": $moves_today,
    "templates_count": $templates_count,
    "errors_today": $errors_today
  },
  "packages": {
    "installed": $packages_installed,
    "total": $packages_total,
    "install_rate": $(( packages_total > 0 ? (packages_installed * 100) / packages_total : 0 ))
  }
}
EOF
    
    # Update analytics file
    cp "$metrics_file" "$ANALYTICS_FILE"
    
    log_success "System metrics collected: $metrics_file"
}

# Generate template variables
generate_template_variables() {
    local analytics_data=""
    if [[ -f "$ANALYTICS_FILE" ]] && command -v jq >/dev/null 2>&1; then
        if jq empty "$ANALYTICS_FILE" 2>/dev/null; then
            analytics_data=$(cat "$ANALYTICS_FILE")
        else
            log_warning "Invalid JSON in analytics file, using defaults"
            analytics_data='{}'
        fi
    else
        analytics_data='{}'
    fi
    
    # Extract variables with defaults (using jq if available, otherwise defaults)
    local timestamp=$(date -Iseconds)
    local user_name=""
    local hostname=""
    local uptime=""
    local missions_count=0
    local moves_today=0
    local templates_count=0
    local errors_today=0
    local packages_installed=0
    local packages_total=0
    local storage_used="0GB"
    local storage_total="0GB"
    local storage_percent=0
    
    if command -v jq >/dev/null 2>&1 && [[ "$analytics_data" != "{}" ]]; then
        user_name=$(echo "$analytics_data" | jq -r '.system.user // "unknown"' 2>/dev/null || echo "unknown")
        hostname=$(echo "$analytics_data" | jq -r '.system.hostname // "localhost"' 2>/dev/null || echo "localhost")
        uptime=$(echo "$analytics_data" | jq -r '.system.uptime_days // "0"' 2>/dev/null || echo "0")
        missions_count=$(echo "$analytics_data" | jq -r '.udos.missions_count // 0' 2>/dev/null || echo "0")
        moves_today=$(echo "$analytics_data" | jq -r '.udos.moves_today // 0' 2>/dev/null || echo "0")
        templates_count=$(echo "$analytics_data" | jq -r '.udos.templates_count // 0' 2>/dev/null || echo "0")
        errors_today=$(echo "$analytics_data" | jq -r '.udos.errors_today // 0' 2>/dev/null || echo "0")
        packages_installed=$(echo "$analytics_data" | jq -r '.packages.installed // 0' 2>/dev/null || echo "0")
        packages_total=$(echo "$analytics_data" | jq -r '.packages.total // 0' 2>/dev/null || echo "0")
        storage_used=$(echo "$analytics_data" | jq -r '.storage.used // "0GB"' 2>/dev/null || echo "0GB")
        storage_total=$(echo "$analytics_data" | jq -r '.storage.total // "0GB"' 2>/dev/null || echo "0GB")
        storage_percent=$(echo "$analytics_data" | jq -r '.storage.percent // 0' 2>/dev/null || echo "0")
    else
        # Fallback values without jq
        user_name=$(whoami)
        hostname=$(hostname)
        uptime="0"
        missions_count=$(find "$UMEM/missions" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        moves_today=$(find "$UMEM/moves" -name "*$(date +%Y-%m-%d)*" 2>/dev/null | wc -l | tr -d ' ')
        templates_count=$(find "$UTEMPLATE" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        errors_today=0
        packages_installed=0
        packages_total=10
    fi
    
    # Health status calculation
    local health_status="🟢 HEALTHY"
    if [[ $errors_today -gt 5 ]]; then
        health_status="🟡 WARNING"
    fi
    if [[ $errors_today -gt 10 ]]; then
        health_status="🔴 CRITICAL"
    fi
    
    # Generate progress bars
    local mission_progress_bar=$(generate_progress_bar $missions_count 10)
    local storage_progress_bar=$(generate_progress_bar $storage_percent 100)
    local package_progress_bar=$(generate_progress_bar $packages_installed $packages_total)
    
    # Get recent activity
    local recent_move_1=$(get_recent_move 1)
    local recent_move_2=$(get_recent_move 2)
    local recent_move_3=$(get_recent_move 3)
    local current_mission=$(get_current_mission)
    
    # Create variables file
    cat > "$DASHBOARD_DIR/variables.json" << EOF
{
  "timestamp": "$timestamp",
  "generation_timestamp": "$(date '+%Y-%m-%d %H:%M:%S')",
  "user_name": "$user_name",
  "hostname": "$hostname",
  "location": "$hostname",
  "timezone": "$(date +%Z)",
  "current_time": "$(date '+%H:%M:%S')",
  "uptime": "$uptime",
  "health_status": "$health_status",
  "title": "uDOS COMMAND CENTER",
  "subtitle": "Enhanced Dashboard v2.0.0",
  "missions_count": "$missions_count",
  "moves_today": "$moves_today",
  "templates_count": "$templates_count",
  "errors_today": "$errors_today",
  "packages_installed": "$packages_installed",
  "packages_total": "$packages_total",
  "storage_used": "$storage_used",
  "storage_total": "$storage_total",
  "storage_percent": "$storage_percent",
  "mission_progress_bar": "$mission_progress_bar",
  "storage_progress_bar": "$storage_progress_bar",
  "package_progress_bar": "$package_progress_bar",
  "recent_move_1": "$recent_move_1",
  "recent_move_2": "$recent_move_2",
  "recent_move_3": "$recent_move_3",
  "current_mission": "$current_mission",
  "daily_progress": "75",
  "daily_progress_bar": "████████████████████████████░░░░░░░░░░",
  "mission_completion": "60",
  "mission_progress_bar": "████████████████████████░░░░░░░░░░░░░░░░",
  "error_rate": "5",
  "error_rate_bar": "██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
  "system_efficiency": "85",
  "efficiency_bar": "██████████████████████████████████░░░░░░",
  "dataset_records": "0",
  "datasets_count": "0",
  "total_files": "$(find "$UHOME" -type f 2>/dev/null | wc -l | tr -d ' ')",
  "total_directories": "$(find "$UHOME" -type d 2>/dev/null | wc -l | tr -d ' ')"
}
EOF
    
    log_success "Template variables generated"
}

# Generate progress bar
generate_progress_bar() {
    local current=${1:-0}
    local total=${2:-100}
    local width=40
    
    if [[ $total -eq 0 ]]; then
        echo "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"
        return
    fi
    
    local progress=$((current * width / total))
    local filled=$(printf "█%.0s" $(seq 1 $progress))
    local empty=$(printf "░%.0s" $(seq 1 $((width - progress))))
    echo "${filled}${empty}"
}

# Get recent move
get_recent_move() {
    local index=${1:-1}
    local today=$(date +%Y-%m-%d)
    local moves_file="$UMEM/moves/moves-$today.md"
    
    if [[ -f "$moves_file" ]]; then
        tail -n +$((index + 1)) "$moves_file" | head -1 | sed 's/^[#*-] *//' | cut -c1-75
    else
        echo "No recent activity recorded"
    fi
}

# Get current mission
get_current_mission() {
    local mission_file=$(find "$UMEM/missions" -name "*.md" -type f 2>/dev/null | head -1)
    if [[ -f "$mission_file" ]]; then
        local mission_name=$(basename "$mission_file" .md)
        echo "Mission: $mission_name (Active)"
    else
        echo "No active mission - Create new mission with [mission:create]"
    fi
}

# Process template with variables
process_template() {
    local template_file="$1"
    local output_file="$2"
    local variables_file="$DASHBOARD_DIR/variables.json"
    
    if [[ ! -f "$template_file" ]]; then
        log_error "Template file not found: $template_file"
        return 1
    fi
    
    if [[ ! -f "$variables_file" ]]; then
        log_error "Variables file not found: $variables_file"
        return 1
    fi
    
    log_info "Processing template: $(basename "$template_file")"
    
    # Simple variable substitution using sed
    local temp_output=$(mktemp)
    cp "$template_file" "$temp_output"
    
    # Process variables from JSON
    if command -v jq >/dev/null 2>&1; then
        jq -r 'to_entries[] | "\(.key)=\(.value)"' "$variables_file" | while IFS='=' read -r key value; do
            sed -i.bak "s/{{$key}}/$value/g" "$temp_output" && rm -f "$temp_output.bak"
        done
    else
        # Fallback without jq
        log_warning "jq not available, using basic variable substitution"
        sed -i.bak \
            -e "s/{{timestamp}}/$(date -Iseconds)/g" \
            -e "s/{{user_name}}/$(whoami)/g" \
            -e "s/{{hostname}}/$(hostname)/g" \
            "$temp_output" && rm -f "$temp_output.bak"
    fi
    
    mv "$temp_output" "$output_file"
    log_success "Template processed: $output_file"
}

# Generate ASCII dashboard
generate_ascii_dashboard() {
    log_info "Generating ASCII dashboard"
    
    if [[ -f "$ASCII_TEMPLATE" ]]; then
        process_template "$ASCII_TEMPLATE" "$ASCII_DASHBOARD"
    else
        # Create basic ASCII dashboard
        cat > "$ASCII_DASHBOARD" << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    🌀 uDOS COMMAND CENTER 🌀                                 ║
║                                   Enhanced Dashboard v2.0.0                                  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║ 👤 USER: {{user_name}}           │ 📍 LOCATION: {{hostname}}         │ ⏰ TIME: {{current_time}}     ║
║ 🏠 BASE: {{timezone}}            │ ⏳ UPTIME: {{uptime}} days       │ 💚 HEALTH: {{health_status}}  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║                                        📊 SYSTEM METRICS                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🎯 MISSIONS: {{missions_count}}     │ 🔄 TODAY'S MOVES: {{moves_today}}   │ 📋 TEMPLATES: {{templates_count}}    ║
║ ❌ ERRORS: {{errors_today}}       │ 📦 PACKAGES: {{packages_installed}}/{{packages_total}} │ 💾 STORAGE: {{storage_percent}}%     ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║                                      🎯 ACTIVE MISSION                                        ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║ {{current_mission}}                                                                           ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║                                       🔧 QUICK ACTIONS                                        ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║ [dash:refresh]  │ [check:health]  │ [package:list] │ [mission:list]  │ [error:stats]        ║
║ [run:backup]    │ [template:list] │ [log:today]    │ [tree:generate] │ [help]               ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║                               📅 Generated: {{generation_timestamp}}                         ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
EOF
        process_template "$ASCII_DASHBOARD" "$ASCII_DASHBOARD"
    fi
}

# Generate markdown dashboard
generate_markdown_dashboard() {
    log_info "Generating Markdown dashboard"
    
    if [[ -f "$DASHBOARD_TEMPLATE" ]]; then
        process_template "$DASHBOARD_TEMPLATE" "$DASHBOARD_FILE"
    else
        # Create basic markdown dashboard
        cat > "$DASHBOARD_FILE" << 'EOF'
# 🌀 uDOS Enhanced Dashboard v2.0.0

**Generated**: {{generation_timestamp}}  
**User**: {{user_name}}  
**Location**: {{hostname}}  
**Health**: {{health_status}}

---

## 📊 System Status

| Metric | Value | Status |
|--------|-------|--------|
| 🎯 Missions | {{missions_count}} | ✅ Active |
| 🔄 Today's Moves | {{moves_today}} | ✅ Tracked |
| 📋 Templates | {{templates_count}} | ✅ Available |
| ❌ Errors Today | {{errors_today}} | {{health_status}} |
| 📦 Packages | {{packages_installed}}/{{packages_total}} | ✅ Managed |
| 💾 Storage | {{storage_used}}/{{storage_total}} ({{storage_percent}}%) | ✅ Monitored |

---

## 🎯 Current Mission

{{current_mission}}

---

## 📝 Recent Activity

1. {{recent_move_1}}
2. {{recent_move_2}}
3. {{recent_move_3}}

---

## 🔧 Quick Actions

### Dashboard Commands
- `[dash:refresh]` - Refresh dashboard
- `[dash:ascii]` - Show ASCII dashboard
- `[dash:analytics]` - Show analytics
- `[dash:config]` - Show configuration

### System Commands
- `[check:health]` - System health check
- `[package:list]` - List packages
- `[mission:list]` - List missions
- `[template:list]` - List templates

### Utilities
- `[error:stats]` - Error statistics
- `[log:today]` - Today's logs
- `[tree:generate]` - File tree
- `[help]` - Show help

---

*Dashboard updated: {{generation_timestamp}}*  
*Next refresh: Automatic every 5 minutes*
EOF
        process_template "$DASHBOARD_FILE" "$DASHBOARD_FILE"
    fi
}

# Show ASCII dashboard
show_ascii_dashboard() {
    if [[ -f "$ASCII_DASHBOARD" ]]; then
        echo -e "${CYAN}"
        cat "$ASCII_DASHBOARD"
        echo -e "${NC}"
    else
        log_warning "ASCII dashboard not found, generating..."
        generate_ascii_dashboard
        show_ascii_dashboard
    fi
}

# Show markdown dashboard
show_markdown_dashboard() {
    if [[ -f "$DASHBOARD_FILE" ]]; then
        if command -v glow >/dev/null 2>&1; then
            glow "$DASHBOARD_FILE"
        else
            cat "$DASHBOARD_FILE"
        fi
    else
        log_warning "Markdown dashboard not found, generating..."
        generate_markdown_dashboard
        show_markdown_dashboard
    fi
}

# Process dash shortcode commands
process_dash_shortcode() {
    local action="$1"
    shift
    
    case "$action" in
        "refresh"|"generate"|"build")
            build_dashboard "$@"
            ;;
        "ascii"|"terminal")
            show_ascii_dashboard
            ;;
        "markdown"|"md")
            show_markdown_dashboard
            ;;
        "analytics"|"stats")
            show_analytics
            ;;
        "config"|"settings")
            show_config
            ;;
        "live"|"watch")
            start_live_dashboard
            ;;
        "export")
            export_dashboard "$@"
            ;;
        "metrics")
            collect_system_metrics
            ;;
        "help")
            show_dash_help
            ;;
        *)
            log_error "Unknown dash action: $action"
            show_dash_help
            return 1
            ;;
    esac
}

# Build complete dashboard
build_dashboard() {
    local mode="${1:-all}"
    
    log_info "Building dashboard (mode: $mode)"
    
    # Initialize if needed
    [[ ! -d "$DASHBOARD_DIR" ]] && initialize_dashboard
    
    # Collect metrics
    collect_system_metrics
    
    # Generate variables
    generate_template_variables
    
    case "$mode" in
        "ascii"|"terminal")
            generate_ascii_dashboard
            show_ascii_dashboard
            ;;
        "markdown"|"md")
            generate_markdown_dashboard
            show_markdown_dashboard
            ;;
        "all"|*)
            generate_ascii_dashboard
            generate_markdown_dashboard
            log_success "Dashboard built successfully"
            
            # Show ASCII by default
            show_ascii_dashboard
            ;;
    esac
}

# Show analytics
show_analytics() {
    if [[ -f "$ANALYTICS_FILE" ]]; then
        echo -e "${PURPLE}📊 Analytics Data${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        if command -v jq >/dev/null 2>&1; then
            jq '.' "$ANALYTICS_FILE"
        else
            cat "$ANALYTICS_FILE"
        fi
    else
        log_warning "Analytics data not available. Run [dash:refresh] to collect data."
    fi
}

# Show configuration
show_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        echo -e "${CYAN}⚙️ Dashboard Configuration${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        if command -v jq >/dev/null 2>&1; then
            jq '.' "$CONFIG_FILE"
        else
            cat "$CONFIG_FILE"
        fi
    else
        log_warning "Configuration not found. Initializing..."
        initialize_dashboard
        show_config
    fi
}

# Start live dashboard
start_live_dashboard() {
    log_info "Starting live dashboard (Ctrl+C to stop)"
    
    while true; do
        clear
        echo -e "${WHITE}🔴 LIVE DASHBOARD - $(date '+%H:%M:%S')${NC}"
        echo ""
        
        # Build and show ASCII dashboard
        collect_system_metrics > /dev/null 2>&1
        generate_template_variables > /dev/null 2>&1
        generate_ascii_dashboard > /dev/null 2>&1
        show_ascii_dashboard
        
        echo ""
        echo -e "${YELLOW}⏰ Auto-refresh in 5 seconds... (Ctrl+C to stop)${NC}"
        
        sleep 5
    done
}

# Export dashboard
export_dashboard() {
    local format="${1:-html}"
    local output_file="$DASHBOARD_DIR/dashboard-export-$(date +%Y%m%d-%H%M%S).$format"
    
    case "$format" in
        "html")
            if command -v pandoc >/dev/null 2>&1; then
                pandoc "$DASHBOARD_FILE" -o "$output_file"
                log_success "Dashboard exported to HTML: $output_file"
            else
                log_error "pandoc not available for HTML export"
                return 1
            fi
            ;;
        "pdf")
            if command -v pandoc >/dev/null 2>&1; then
                pandoc "$DASHBOARD_FILE" -o "$output_file"
                log_success "Dashboard exported to PDF: $output_file"
            else
                log_error "pandoc not available for PDF export"
                return 1
            fi
            ;;
        "txt")
            cp "$ASCII_DASHBOARD" "$output_file"
            log_success "ASCII dashboard exported: $output_file"
            ;;
        *)
            log_error "Unknown export format: $format"
            log_info "Available formats: html, pdf, txt"
            return 1
            ;;
    esac
}

# Show dash help
show_dash_help() {
    echo -e "${PURPLE}📊 uDOS Enhanced Dashboard v2.0.0${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BLUE}📋 Available Shortcodes${NC}"
    echo ""
    echo -e "${GREEN}Dashboard Commands:${NC}"
    echo "  [dash:refresh] - Refresh dashboard data"
    echo "  [dash:ascii] - Show ASCII dashboard"
    echo "  [dash:markdown] - Show Markdown dashboard"
    echo "  [dash:live] - Start live updating dashboard"
    echo ""
    echo -e "${GREEN}Analytics & Configuration:${NC}"
    echo "  [dash:analytics] - Show analytics data"
    echo "  [dash:config] - Show configuration"
    echo "  [dash:metrics] - Collect system metrics"
    echo ""
    echo -e "${GREEN}Export & Utilities:${NC}"
    echo "  [dash:export html] - Export to HTML"
    echo "  [dash:export pdf] - Export to PDF"
    echo "  [dash:export txt] - Export ASCII version"
    echo "  [dash:help] - Show this help"
    echo ""
    echo -e "${BLUE}📋 Examples:${NC}"
    echo "  [dash:refresh] - Build complete dashboard"
    echo "  [dash:ascii] - Quick ASCII view"
    echo "  [dash:live] - Real-time monitoring"
    echo "  [dash:export html] - Create HTML report"
    echo ""
    echo -e "${BLUE}📂 Files:${NC}"
    echo "  ASCII: $ASCII_DASHBOARD"
    echo "  Markdown: $DASHBOARD_FILE"
    echo "  Analytics: $ANALYTICS_FILE"
    echo "  Config: $CONFIG_FILE"
}

# Main command interface
main() {
    case "${1:-help}" in
        "shortcode")
            # For integration with shortcode processor
            process_dash_shortcode "${@:2}"
            ;;
        "build"|"generate"|"refresh")
            build_dashboard "${@:2}"
            ;;
        "ascii"|"terminal")
            show_ascii_dashboard
            ;;
        "markdown"|"md")
            show_markdown_dashboard
            ;;
        "live"|"watch")
            start_live_dashboard
            ;;
        "metrics")
            collect_system_metrics
            ;;
        "analytics"|"stats")
            show_analytics
            ;;
        "config")
            show_config
            ;;
        "export")
            export_dashboard "${@:2}"
            ;;
        "help"|*)
            show_dash_help
            ;;
    esac
}

# Initialize if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
