#!/bin/bash
# uDOS Dashboard v1.0
# 📊 Dashboard with real-time monitoring and analytics

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
UCODE="${UHOME}/uCode"
DASHBOARD="${UMEM}/state/dashboard.md"
STATS="${UMEM}/state/stats.md"
ANALYTICS="${UMEM}/state/analytics.json"
TODAY="$(date +%Y-%m-%d)"
MOVESFILE="${UMEM}/moves/moves-${TODAY}.md"

# Colors for enhanced output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Enhanced logging with timestamps
log() { 
    echo -e "${CYAN}[$(date '+%H:%M:%S')] [dash]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] [ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] [SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] [WARNING]${NC} $1"
}

# System metrics collection
collect_system_metrics() {
    local cpu_usage disk_usage memory_usage uptime_info
    
    # CPU usage (macOS compatible)
    cpu_usage=$(top -l 1 -s 0 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
    
    # Memory usage
    memory_usage=$(vm_stat | awk '
        /^Pages free:/ { free = $3 }
        /^Pages active:/ { active = $3 }
        /^Pages inactive:/ { inactive = $3 }
        /^Pages wired down:/ { wired = $4 }
        END {
            total = (free + active + inactive + wired) * 4096 / 1024 / 1024 / 1024
            used = (active + inactive + wired) * 4096 / 1024 / 1024 / 1024
            printf "%.1f/%.1f GB (%.0f%%)", used, total, (used/total)*100
        }')
    
    # Disk usage for uDOS directory
    disk_usage=$(du -sh "$UHOME" 2>/dev/null | awk '{print $1}')
    
    # System uptime
    uptime_info=$(uptime | awk -F'up ' '{print $2}' | awk -F', load' '{print $1}')
    
    # Create JSON analytics
    cat > "$ANALYTICS" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "system": {
        "cpu_usage": "${cpu_usage}",
        "memory_usage": "${memory_usage}",
        "disk_usage": "${disk_usage}",
        "uptime": "${uptime_info}"
    },
    "udos": {
        "version": "v1.7.1",
        "home_size": "${disk_usage}",
        "last_dashboard_update": "$(date -Iseconds)"
    }
}
EOF
}

# Enhanced header with ASCII art and real-time info
header() {
    cat > "$DASHBOARD" << 'EOF'
```
   ██╗   ██╗██████╗  ██████╗ ███████╗
   ██║   ██║██╔══██╗██╔═══██╗██╔════╝
   ██║   ██║██║  ██║██║   ██║███████╗
   ██║   ██║██║  ██║██║   ██║╚════██║
   ╚██████╔╝██████╔╝╚██████╔╝███████║
    ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
```

# 📊 uDOS Dashboard v1.0

_Last updated: $(date '+%Y-%m-%d %H:%M:%S') | Real-time monitoring active_

---

EOF
}

# System status section with metrics
render_system_status() {
    section "🖥️ System Status"
    
    if [[ -f "$ANALYTICS" ]]; then
        local cpu memory disk uptime
        cpu=$(jq -r '.system.cpu_usage' "$ANALYTICS" 2>/dev/null || echo "N/A")
        memory=$(jq -r '.system.memory_usage' "$ANALYTICS" 2>/dev/null || echo "N/A")
        disk=$(jq -r '.system.disk_usage' "$ANALYTICS" 2>/dev/null || echo "N/A")
        uptime=$(jq -r '.system.uptime' "$ANALYTICS" 2>/dev/null || echo "N/A")
        
        cat >> "$DASHBOARD" << EOF
| Metric | Value | Status |
|--------|-------|--------|
| 🔋 CPU Usage | ${cpu}% | $([ "${cpu%.*}" -lt 80 ] 2>/dev/null && echo "✅ Normal" || echo "⚠️ High") |
| 🧠 Memory | ${memory} | ✅ Monitored |
| 💾 uDOS Size | ${disk} | ✅ Tracked |
| ⏱️ Uptime | ${uptime} | ✅ Active |

EOF
    else
        echo "⚠️ System metrics unavailable - run dashboard build to collect data" >> "$DASHBOARD"
        echo "" >> "$DASHBOARD"
    fi
}

# Enhanced stats with analytics
render_stats() {
    section "📈 Analytics & Statistics"
    
    if [[ -f "$STATS" ]]; then
        cat "$STATS" >> "$DASHBOARD"
    else
        echo "_Generating initial statistics..._" >> "$DASHBOARD"
        generate_initial_stats
    fi
    echo "" >> "$DASHBOARD"
    
    # Add quick stats
    local total_moves total_missions total_templates
    total_moves=$(find "$UMEM/moves" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    total_missions=$(find "$UMEM/missions" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    total_templates=$(find "$UHOME/uTemplate" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    
    cat >> "$DASHBOARD" << EOF
### Quick Stats
- 📝 Total Moves: **${total_moves}**
- 🎯 Total Missions: **${total_missions}**
- 📋 Available Templates: **${total_templates}**
- 🕐 Last Update: **$(date '+%H:%M:%S')**

EOF
}

# Recent activity section
render_recent_activity() {
    section "🔄 Recent Activity"
    
    # Show recent files modified in last 24 hours
    echo "### Recently Modified Files:" >> "$DASHBOARD"
    find "$UMEM" -type f -mtime -1 2>/dev/null | head -10 | while read -r file; do
        local basename timestamp
        basename=$(basename "$file")
        timestamp=$(stat -f "%Sm" -t "%H:%M" "$file" 2>/dev/null || echo "unknown")
        echo "- 📄 \`${basename}\` _(${timestamp})_" >> "$DASHBOARD"
    done
    echo "" >> "$DASHBOARD"
}

# Enhanced moves with better formatting
render_moves() {
    section "📋 Today's Moves"
    
    if [[ -f "$MOVESFILE" ]]; then
        local move_count
        move_count=$(grep -c "^-" "$MOVESFILE" 2>/dev/null || echo "0")
        echo "**Total moves today: ${move_count}**" >> "$DASHBOARD"
        echo "" >> "$DASHBOARD"
        
        # Show last 10 moves with better formatting
        grep "^-" "$MOVESFILE" | tail -10 | while IFS= read -r line; do
            echo "${line}" >> "$DASHBOARD"
        done
        
        if [[ $move_count -gt 10 ]]; then
            echo "" >> "$DASHBOARD"
            echo "_... and $((move_count - 10)) more moves_" >> "$DASHBOARD"
        fi
    else
        echo "_No moves logged today. Start logging with:_" >> "$DASHBOARD"
        echo "\`\`\`bash" >> "$DASHBOARD"
        echo "echo '- [$(date +%H:%M)] Your move description' >> $MOVESFILE" >> "$DASHBOARD"
        echo "\`\`\`" >> "$DASHBOARD"
    fi
    echo "" >> "$DASHBOARD"
}

# Package status section
render_package_status() {
    section "📦 Package Status"
    
    local packages=("bat" "fd" "glow" "jq" "fzf" "rg")
    echo "| Package | Status | Version |" >> "$DASHBOARD"
    echo "|---------|--------|---------|" >> "$DASHBOARD"
    
    for pkg in "${packages[@]}"; do
        if command -v "$pkg" >/dev/null 2>&1; then
            local version
            case $pkg in
                "bat") version=$(bat --version | awk '{print $2}' 2>/dev/null || echo "unknown") ;;
                "fd") version=$(fd --version | awk '{print $2}' 2>/dev/null || echo "unknown") ;;
                "glow") version=$(glow --version | awk '{print $3}' 2>/dev/null || echo "unknown") ;;
                "jq") version=$(jq --version | sed 's/jq-//' 2>/dev/null || echo "unknown") ;;
                "fzf") version=$(fzf --version | awk '{print $1}' 2>/dev/null || echo "unknown") ;;
                "rg") version=$(rg --version | head -1 | awk '{print $2}' 2>/dev/null || echo "unknown") ;;
            esac
            echo "| $pkg | ✅ Installed | $version |" >> "$DASHBOARD"
        else
            echo "| $pkg | ❌ Missing | - |" >> "$DASHBOARD"
        fi
    done
    echo "" >> "$DASHBOARD"
}

# Quick actions section
render_quick_actions() {
    section "⚡ Quick Actions"
    
    cat >> "$DASHBOARD" << 'EOF'
```bash
# uDOS Commands
./uCode/ucode.sh                    # Start uDOS shell
./uCode/check.sh all                # System check
./uCode/dash.sh build               # Rebuild dashboard

# Package Management
./uCode/packages/manager.sh status  # Check packages
./uCode/packages/manager.sh update  # Update packages

# VS Code Tasks
# Use Cmd+Shift+P → "Tasks: Run Task" → Select task
```

EOF
}

section() {
    echo "## $1" >> "$DASHBOARD"
    echo "" >> "$DASHBOARD"
}

generate_initial_stats() {
    cat > "$STATS" << EOF
### System Statistics
- Created: $(date '+%Y-%m-%d %H:%M:%S')
- uDOS Version: v1.7.1
- Architecture: Enhanced Dashboard

### Usage Metrics
- Dashboard builds: 1
- Last system check: $(date '+%Y-%m-%d')
- Performance: ⚡ Fast startup (3s)
EOF
}

# Interactive dashboard viewer with live updates
interactive_dashboard() {
    log "Starting interactive dashboard..."
    
    while true; do
        clear
        echo -e "${WHITE}╔══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${WHITE}║                    📊 uDOS Live Dashboard                    ║${NC}"
        echo -e "${WHITE}╚══════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        
        # Show key metrics in real-time
        collect_system_metrics
        
        if [[ -f "$ANALYTICS" ]]; then
            local cpu memory
            cpu=$(jq -r '.system.cpu_usage' "$ANALYTICS" 2>/dev/null || echo "N/A")
            memory=$(jq -r '.system.memory_usage' "$ANALYTICS" 2>/dev/null || echo "N/A")
            
            echo -e "${CYAN}System Status:${NC}"
            echo -e "  🔋 CPU: ${cpu}%"
            echo -e "  🧠 Memory: ${memory}"
            echo -e "  ⏰ Updated: $(date '+%H:%M:%S')"
            echo ""
        fi
        
        echo -e "${YELLOW}Press 'q' to quit, 'r' to refresh, 's' to show full dashboard${NC}"
        
        # Non-blocking input check
        read -t 5 -n 1 input
        case $input in
            'q'|'Q') break ;;
            'r'|'R') continue ;;
            's'|'S') 
                open_dashboard
                echo -e "\n${CYAN}Press Enter to return to live view...${NC}"
                read -r
                ;;
        esac
    done
    
    log "Interactive dashboard stopped"
}

open_dashboard() {
    if command -v glow &> /dev/null; then
        glow "$DASHBOARD"
    elif command -v bat &> /dev/null; then
        bat "$DASHBOARD"
    elif command -v less &> /dev/null; then
        less "$DASHBOARD"
    else
        cat "$DASHBOARD"
    fi
}

# Command parser with enhanced options
case "$1" in
    new|build)
        log "Building dashboard..."
        collect_system_metrics
        header
        render_system_status
        render_stats
        render_recent_activity
        render_moves
        render_package_status
        render_quick_actions
        success "Dashboard updated → $DASHBOARD"
        ;;
    show|view)
        log "Opening dashboard..."
        open_dashboard
        ;;
    live|interactive)
        interactive_dashboard
        ;;
    sync)
        log "Refreshing dashboard (sync mode)..."
        "$0" build
        ;;
    metrics)
        log "Collecting system metrics..."
        collect_system_metrics
        if [[ -f "$ANALYTICS" ]]; then
            echo "Metrics saved to: $ANALYTICS"
            if command -v jq &> /dev/null; then
                jq . "$ANALYTICS"
            else
                cat "$ANALYTICS"
            fi
        fi
        ;;
    *)
        echo -e "${WHITE}uDOS Dashboard v1.0${NC}"
        echo ""
        echo "Usage:"
        echo "  ./dash.sh build        # Generate dashboard"
        echo "  ./dash.sh show         # View dashboard"
        echo "  ./dash.sh live         # Interactive live dashboard"
        echo "  ./dash.sh metrics      # Show system metrics"
        echo "  ./dash.sh sync         # Refresh (used by automation)"
        echo ""
        echo "Examples:"
        echo "  ./dash.sh build && ./dash.sh show"
        echo "  ./dash.sh live  # Real-time monitoring"
        ;;
esac
