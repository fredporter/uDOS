#!/bin/bash
# Network Service Monitoring v1.0.5.4
# Health monitoring and status tracking for network services

# Monitoring configuration
MONITOR_INTERVAL=30
MONITOR_LOG="$UDOS_ROOT/uNETWORK/monitoring/health.log"

# Source integration layer
source "$UDOS_ROOT/uNETWORK/integration/data-integration.sh"

# Check service health
check_service_health() {
    local service_name="$1"
    local service_port="$2"
    
    echo "🔍 Checking health of service: $service_name"
    
    # Basic port check (simplified)
    if command -v nc >/dev/null 2>&1; then
        if nc -z localhost "$service_port" 2>/dev/null; then
            echo "✅ Service $service_name is healthy (port $service_port open)"
            log_health_status "$service_name" "healthy" "Port $service_port responding"
            return 0
        else
            echo "❌ Service $service_name is unhealthy (port $service_port closed)"
            log_health_status "$service_name" "unhealthy" "Port $service_port not responding"
            return 1
        fi
    else
        echo "⚠️ Cannot check port status (nc not available)"
        log_health_status "$service_name" "unknown" "Cannot verify port status"
        return 2
    fi
}

# Log health status
log_health_status() {
    local service_name="$1"
    local status="$2"
    local details="$3"
    
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$timestamp] $service_name: $status - $details" >> "$MONITOR_LOG"
    
    # Store health data in uMEMORY
    local health_data="{
        \"service\": \"$service_name\",
        \"status\": \"$status\",
        \"details\": \"$details\",
        \"timestamp\": \"$timestamp\"
    }"
    
    store_service_data "${service_name}_health" "$health_data"
}

# Monitor all registered services
monitor_all_services() {
    echo "🔍 Monitoring all registered services..."
    
    # Get services from registry (simplified)
    if [ -f "$UDOS_ROOT/uNETWORK/services/discovery.log" ]; then
        while IFS= read -r line; do
            if [[ "$line" =~ Registered:\ ([^:]+):([0-9]+) ]]; then
                local service_name="${BASH_REMATCH[1]}"
                local service_port="${BASH_REMATCH[2]}"
                check_service_health "$service_name" "$service_port"
            fi
        done < "$UDOS_ROOT/uNETWORK/services/discovery.log"
    else
        echo "📭 No services registered for monitoring"
    fi
}

# Start monitoring daemon
start_monitoring() {
    echo "🚀 Starting network service monitoring (interval: ${MONITOR_INTERVAL}s)"
    
    while true; do
        monitor_all_services
        sleep "$MONITOR_INTERVAL"
    done
}

# Main monitoring control
case "${1:-help}" in
    check)
        check_service_health "$2" "$3"
        ;;
    monitor)
        monitor_all_services
        ;;
    daemon)
        start_monitoring
        ;;
    *)
        echo "Usage: $0 {check <name> <port>|monitor|daemon}"
        ;;
esac
