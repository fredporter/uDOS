#!/bin/bash
# uDOS Enhanced Monitoring Control Panel
# Provides centralized monitoring and analytics

# Get script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Control panel configuration
PANEL_VERSION="1.0.5.7"
LOG_DIR="$UDOS_ROOT/uMEMORY/logs"
METRICS_DIR="$UDOS_ROOT/uNETWORK/monitoring/metrics"

# Initialize monitoring control panel
init_control_panel() {
    echo "🎛️ uDOS Monitoring Control Panel v$PANEL_VERSION"
    echo "================================================"
    
    # Create necessary directories
    mkdir -p "$LOG_DIR"
    mkdir -p "$METRICS_DIR"
    
    # Show system overview
    show_system_overview
    
    echo ""
    echo "💡 Available Commands:"
    echo "  status    - Show detailed system status"
    echo "  metrics   - Display live metrics"
    echo "  alerts    - Show recent alerts"
    echo "  logs      - View system logs"
    echo "  health    - Run comprehensive health check"
    echo "  services  - Manage system services"
    echo "  dashboard - Open web dashboard"
    echo "  help      - Show this help"
}

# Show comprehensive system overview
show_system_overview() {
    echo ""
    echo "📊 SYSTEM OVERVIEW"
    echo "=================="
    
    # System basics
    echo "🖥️  System: $(uname -s) $(uname -m)"
    echo "📅 Date: $(date)"
    echo "⏰ Uptime: $(uptime | awk '{print $3, $4}' | sed 's/,//')"
    
    # uDOS status
    echo ""
    echo "🌀 uDOS Status:"
    echo "   Version: v$PANEL_VERSION"
    echo "   Root: $UDOS_ROOT"
    
    # Module status
    echo "   Modules:"
    local modules=("uCORE" "uMEMORY" "uKNOWLEDGE" "uNETWORK" "uSCRIPT")
    for module in "${modules[@]}"; do
        if [ -d "$UDOS_ROOT/$module" ]; then
            echo "     ✅ $module"
        else
            echo "     ❌ $module (missing)"
        fi
    done
    
    # Service status
    echo "   Services:"
    check_service_status "Monitoring" "$UDOS_ROOT/uNETWORK/monitoring/monitor.pid"
    check_service_status "Metrics API" "$UDOS_ROOT/uNETWORK/display/metrics.pid"
    check_service_status "Web UI" "webui"
    
    # Quick metrics
    local shell_count=$(ps aux | grep -c "[u]shell" || echo "0")
    echo "   Active Shell Sessions: $shell_count"
}

# Check individual service status
check_service_status() {
    local service_name="$1"
    local pid_file="$2"
    
    if [ "$service_name" = "Web UI" ]; then
        # Special check for web UI
        if [ -f "$UDOS_ROOT/uNETWORK/display/webui/index.html" ]; then
            echo "     🟢 $service_name (Ready)"
        else
            echo "     🟡 $service_name (Not configured)"
        fi
    elif [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "     🟢 $service_name (Running - PID: $pid)"
        else
            echo "     🔴 $service_name (Stopped)"
            rm -f "$pid_file" 2>/dev/null
        fi
    else
        echo "     🔴 $service_name (Stopped)"
    fi
}

# Display live metrics
show_live_metrics() {
    echo "📊 LIVE SYSTEM METRICS"
    echo "======================"
    
    # Get metrics from API if available
    if command -v curl >/dev/null && curl -s "http://localhost:8082" >/dev/null 2>&1; then
        echo "📡 Fetching from Metrics API..."
        curl -s "http://localhost:8082" | jq . 2>/dev/null || {
            echo "❌ Failed to parse metrics data"
            show_basic_metrics
        }
    else
        echo "📊 Basic System Metrics:"
        show_basic_metrics
    fi
}

# Show basic metrics when API is not available
show_basic_metrics() {
    echo ""
    echo "🖥️  CPU Usage: $(top -l 1 -n 0 | grep "CPU usage" | awk '{print $3}' || echo "N/A")"
    echo "💾 Memory: $(vm_stat | head -5 | tail -1 | awk '{print $3}' || echo "N/A") pages free"
    echo "💿 Disk: $(df "$UDOS_ROOT" | tail -1 | awk '{print $5}') used"
    echo "🔄 Processes: $(ps aux | wc -l | tr -d ' ') total"
    echo "📡 Network: $(netstat -an | grep LISTEN | wc -l | tr -d ' ') listening ports"
}

# Show recent alerts
show_alerts() {
    echo "🚨 RECENT ALERTS"
    echo "================"
    
    local alert_log="$UDOS_ROOT/uNETWORK/monitoring/logs/alerts.log"
    if [ -f "$alert_log" ]; then
        echo "📋 Last 10 alerts:"
        tail -10 "$alert_log" | while read -r line; do
            echo "  $line"
        done
    else
        echo "✅ No alerts found"
    fi
}

# View system logs
show_logs() {
    echo "📝 SYSTEM LOGS"
    echo "=============="
    
    echo "📂 Available log files:"
    find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | head -5 | while read -r log_file; do
        local file_name=$(basename "$log_file")
        local file_size=$(ls -lh "$log_file" | awk '{print $5}')
        local mod_time=$(ls -l "$log_file" | awk '{print $6, $7, $8}')
        echo "  📄 $file_name ($file_size) - $mod_time"
    done
    
    echo ""
    echo "💡 To view a specific log: tail -f $LOG_DIR/[logfile]"
}

# Comprehensive health check
health_check() {
    echo "🏥 COMPREHENSIVE HEALTH CHECK"
    echo "============================="
    
    local health_score=0
    local total_checks=0
    
    # Check critical components
    echo "🔍 Checking critical components..."
    
    # Foundation check
    total_checks=$((total_checks + 1))
    if [ -f "$UDOS_ROOT/uCORE/code/foundation-init.sh" ]; then
        echo "  ✅ uCORE Foundation"
        health_score=$((health_score + 1))
    else
        echo "  ❌ uCORE Foundation (missing)"
    fi
    
    # Shell check
    total_checks=$((total_checks + 1))
    if [ -f "$UDOS_ROOT/uCORE/bin/ushell" ] && [ -x "$UDOS_ROOT/uCORE/bin/ushell" ]; then
        echo "  ✅ Interactive Shell"
        health_score=$((health_score + 1))
    else
        echo "  ❌ Interactive Shell (missing or not executable)"
    fi
    
    # Web UI check
    total_checks=$((total_checks + 1))
    if [ -f "$UDOS_ROOT/demo/simple-demo.html" ]; then
        echo "  ✅ Web Interface"
        health_score=$((health_score + 1))
    else
        echo "  ❌ Web Interface (missing)"
    fi
    
    # Metrics API check
    total_checks=$((total_checks + 1))
    if [ -f "$UDOS_ROOT/uNETWORK/display/metrics-api.sh" ]; then
        echo "  ✅ Metrics API"
        health_score=$((health_score + 1))
    else
        echo "  ❌ Metrics API (missing)"
    fi
    
    # Monitoring system check
    total_checks=$((total_checks + 1))
    if [ -f "$UDOS_ROOT/uNETWORK/monitoring/monitor.sh" ]; then
        echo "  ✅ Monitoring System"
        health_score=$((health_score + 1))
    else
        echo "  ❌ Monitoring System (missing)"
    fi
    
    # Calculate health percentage
    local health_percentage=$((health_score * 100 / total_checks))
    
    echo ""
    echo "🎯 HEALTH SUMMARY:"
    echo "   Score: $health_score/$total_checks ($health_percentage%)"
    
    if [ $health_percentage -ge 90 ]; then
        echo "   Status: 💚 Excellent"
    elif [ $health_percentage -ge 75 ]; then
        echo "   Status: 💛 Good"
    elif [ $health_percentage -ge 50 ]; then
        echo "   Status: 🧡 Fair"
    else
        echo "   Status: ❤️ Needs Attention"
    fi
}

# Service management
manage_services() {
    echo "🔧 SERVICE MANAGEMENT"
    echo "===================="
    
    echo "📋 Available services:"
    echo "  1. Monitoring System"
    echo "  2. Metrics API"
    echo "  3. Web Dashboard"
    echo ""
    
    read -p "🎛️ Select service (1-3) or 'q' to quit: " choice
    
    case "$choice" in
        "1")
            echo "🔄 Monitoring System:"
            "$UDOS_ROOT/uNETWORK/monitoring/monitor.sh" status
            ;;
        "2")
            echo "📊 Metrics API:"
            "$UDOS_ROOT/uNETWORK/display/metrics-api.sh" status
            ;;
        "3")
            echo "🌐 Web Dashboard:"
            if [ -f "$UDOS_ROOT/demo/simple-demo.html" ]; then
                echo "✅ Dashboard available at: file://$UDOS_ROOT/demo/simple-demo.html"
            else
                echo "❌ Dashboard not found"
            fi
            ;;
        "q"|"Q")
            echo "👋 Exiting service management"
            ;;
        *)
            echo "❌ Invalid choice"
            ;;
    esac
}

# Main control panel loop
main() {
    case "${1:-init}" in
        "init")
            init_control_panel
            ;;
        "status")
            show_system_overview
            ;;
        "metrics")
            show_live_metrics
            ;;
        "alerts")
            show_alerts
            ;;
        "logs")
            show_logs
            ;;
        "health")
            health_check
            ;;
        "services")
            manage_services
            ;;
        "dashboard")
            echo "🌐 Opening web dashboard..."
            if command -v open >/dev/null; then
                open "file://$UDOS_ROOT/demo/simple-demo.html"
            else
                echo "📱 Dashboard: file://$UDOS_ROOT/demo/simple-demo.html"
            fi
            ;;
        "help")
            init_control_panel
            ;;
        *)
            echo "Usage: $0 {init|status|metrics|alerts|logs|health|services|dashboard|help}"
            ;;
    esac
}

# Execute if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
