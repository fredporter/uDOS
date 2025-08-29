#!/bin/bash
# Alert Manager for uDOS Monitoring

ALERT_LOG="$MONITOR_DIR/logs/alerts.log"

check_thresholds() {
    local metrics_file="$1"
    local alerts_triggered=0
    
    if [ ! -f "$metrics_file" ]; then
        return 0
    fi
    
    # Check CPU usage
    local cpu_usage="$(cat "$metrics_file" | grep -o '"cpu_usage":[0-9]*' | cut -d':' -f2 2>/dev/null || echo "0")"
    cpu_usage="${cpu_usage:-0}"  # Default to 0 if empty
    if [ -n "$cpu_usage" ] && [ "$cpu_usage" -gt 80 ] 2>/dev/null; then
        trigger_alert "HIGH_CPU" "CPU usage at ${cpu_usage}%" "warning"
        alerts_triggered=$((alerts_triggered + 1))
    fi
    
    # Check memory usage
    local memory_usage="$(cat "$metrics_file" | grep -o '"memory_usage":[0-9.]*' | cut -d':' -f2 | cut -d'.' -f1 2>/dev/null || echo "0")"
    memory_usage="${memory_usage:-0}"  # Default to 0 if empty
    if [ -n "$memory_usage" ] && [ "$memory_usage" -gt 85 ] 2>/dev/null; then
        trigger_alert "HIGH_MEMORY" "Memory usage at ${memory_usage}%" "warning"
        alerts_triggered=$((alerts_triggered + 1))
    fi
    
    # Check disk usage
    local disk_usage="$(cat "$metrics_file" | grep -o '"disk_usage":[0-9]*' | cut -d':' -f2 2>/dev/null || echo "0")"
    disk_usage="${disk_usage:-0}"  # Default to 0 if empty
    if [ -n "$disk_usage" ] && [ "$disk_usage" -gt 90 ] 2>/dev/null; then
        trigger_alert "HIGH_DISK" "Disk usage at ${disk_usage}%" "critical"
        alerts_triggered=$((alerts_triggered + 1))
    fi
    
    return $alerts_triggered
}

trigger_alert() {
    local alert_type="$1"
    local message="$2"
    local severity="$3"
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    # Log alert
    echo "$timestamp [$severity] $alert_type: $message" >> "$ALERT_LOG"
    
    # Could send to external systems here
    echo "🚨 ALERT [$severity]: $message"
}

# Execute if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    check_thresholds "$@"
fi
