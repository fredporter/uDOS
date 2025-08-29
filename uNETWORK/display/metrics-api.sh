#!/bin/bash
# Real-time Metrics API for uDOS Web Dashboard
# Provides live system data for the web interface

# Get script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Metrics configuration
METRICS_PORT="8082"
METRICS_UPDATE_INTERVAL=5

# Generate real-time system metrics
generate_metrics() {
    local timestamp=$(date +%s)
    local formatted_time=$(date '+%Y-%m-%d %H:%M:%S')
    
    # System metrics
    local cpu_usage=$(top -l 1 -n 0 | grep "CPU usage" | awk '{print $3}' | sed 's/%//' || echo "0")
    local memory_pressure=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//' || echo "100000")
    local disk_usage=$(df "$UDOS_ROOT" | tail -1 | awk '{print $5}' | sed 's/%//' || echo "0")
    
    # uDOS specific metrics
    local active_modules=0
    local modules=("uCORE" "uMEMORY" "uKNOWLEDGE" "uNETWORK" "uSCRIPT")
    for module in "${modules[@]}"; do
        if [ -d "$UDOS_ROOT/$module" ]; then
            active_modules=$((active_modules + 1))
        fi
    done
    
    # Service status
    local monitoring_status="stopped"
    if [ -f "$UDOS_ROOT/uNETWORK/monitoring/monitor.pid" ] && \
       kill -0 "$(cat "$UDOS_ROOT/uNETWORK/monitoring/monitor.pid")" 2>/dev/null; then
        monitoring_status="running"
    fi
    
    local shell_sessions=$(ps aux | grep "ushell" | grep -v grep | wc -l | tr -d ' ')
    
    # Generate JSON response
    cat << EOF
{
    "timestamp": $timestamp,
    "formatted_time": "$formatted_time",
    "system": {
        "cpu_usage": "${cpu_usage:-0}",
        "memory_pressure": "${memory_pressure:-100000}",
        "disk_usage": "${disk_usage:-0}",
        "uptime": "$(uptime | awk '{print $3, $4}' | sed 's/,//' || echo 'unknown')"
    },
    "uDOS": {
        "version": "1.0.5.7",
        "active_modules": $active_modules,
        "total_modules": 5,
        "shell_sessions": ${shell_sessions:-0},
        "monitoring_status": "$monitoring_status",
        "root_path": "$UDOS_ROOT"
    },
    "modules": {
        "uCORE": $([ -d "$UDOS_ROOT/uCORE" ] && echo "true" || echo "false"),
        "uMEMORY": $([ -d "$UDOS_ROOT/uMEMORY" ] && echo "true" || echo "false"),
        "uKNOWLEDGE": $([ -d "$UDOS_ROOT/uKNOWLEDGE" ] && echo "true" || echo "false"),
        "uNETWORK": $([ -d "$UDOS_ROOT/uNETWORK" ] && echo "true" || echo "false"),
        "uSCRIPT": $([ -d "$UDOS_ROOT/uSCRIPT" ] && echo "true" || echo "false")
    },
    "services": {
        "monitoring": "$monitoring_status",
        "web_ui": "running",
        "api_gateway": "$([ -f "$UDOS_ROOT/uNETWORK/api/api-gateway.sh" ] && echo 'available' || echo 'unavailable')"
    },
    "performance": {
        "cpu_load": "$(uptime | awk '{print $10}' | sed 's/,//' || echo '0.00')",
        "memory_free": "$(vm_stat | grep 'Pages free' | awk '{print $3}' | sed 's/\.//' || echo '0')",
        "processes": "$(ps aux | wc -l | tr -d ' ')"
    }
}
EOF
}

# Start metrics API server
start_metrics_server() {
    echo "🔥 Starting Real-time Metrics API on port $METRICS_PORT"
    
    # Simple HTTP server using netcat (for demo purposes)
    while true; do
        {
            echo "HTTP/1.1 200 OK"
            echo "Content-Type: application/json"
            echo "Access-Control-Allow-Origin: *"
            echo "Cache-Control: no-cache"
            echo ""
            generate_metrics
        } | nc -l "$METRICS_PORT" 2>/dev/null
        
        sleep 1
    done &
    
    local server_pid=$!
    echo "$server_pid" > "$UDOS_ROOT/uNETWORK/display/metrics.pid"
    echo "✅ Metrics API running (PID: $server_pid)"
}

# Stop metrics server
stop_metrics_server() {
    if [ -f "$UDOS_ROOT/uNETWORK/display/metrics.pid" ]; then
        local pid=$(cat "$UDOS_ROOT/uNETWORK/display/metrics.pid")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "🛑 Metrics API stopped"
        fi
        rm -f "$UDOS_ROOT/uNETWORK/display/metrics.pid"
    else
        echo "❌ Metrics API not running"
    fi
}

# Check metrics server status
metrics_status() {
    if [ -f "$UDOS_ROOT/uNETWORK/display/metrics.pid" ]; then
        local pid=$(cat "$UDOS_ROOT/uNETWORK/display/metrics.pid")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🟢 Metrics API running (PID: $pid, Port: $METRICS_PORT)"
            echo "📊 Endpoint: http://localhost:$METRICS_PORT"
        else
            echo "🔴 Metrics API not responding"
            rm -f "$UDOS_ROOT/uNETWORK/display/metrics.pid"
        fi
    else
        echo "🔴 Metrics API not running"
    fi
}

# Test metrics endpoint
test_metrics() {
    echo "🧪 Testing metrics endpoint..."
    curl -s "http://localhost:$METRICS_PORT" | jq . || {
        echo "❌ Metrics API not accessible"
        echo "💡 Try: $0 start"
        return 1
    }
}

# Main function
main() {
    case "${1:-status}" in
        "start")
            start_metrics_server
            ;;
        "stop")
            stop_metrics_server
            ;;
        "status")
            metrics_status
            ;;
        "test")
            test_metrics
            ;;
        "metrics")
            generate_metrics
            ;;
        *)
            echo "Usage: $0 {start|stop|status|test|metrics}"
            echo ""
            echo "Real-time Metrics API for uDOS Web Dashboard"
            echo "Provides live system data in JSON format"
            ;;
    esac
}

# Execute if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
