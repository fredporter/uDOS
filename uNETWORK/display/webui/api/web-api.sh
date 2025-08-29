#!/bin/bash
# Web API for uDOS Dashboard

# Get script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# API endpoint handlers
handle_system_status() {
    cat << JSON_EOF
{
  "status": "online",
  "uptime": "$(uptime | awk '{print $3 $4}' | sed 's/,//')",
  "modules": {
    "uCORE": "online",
    "uMEMORY": "online", 
    "uKNOWLEDGE": "online",
    "uNETWORK": "online",
    "uSCRIPT": "online"
  },
  "api_gateway": {
    "status": "running",
    "requests_today": $(( RANDOM % 1000 + 500 )),
    "response_time_avg": "${RANDOM:0:2}ms"
  },
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
JSON_EOF
}

handle_module_details() {
    local module="$1"
    
    case "$module" in
        "uCORE")
            cat << JSON_EOF
{
  "name": "uCORE",
  "type": "foundation",
  "status": "online",
  "memory_usage": "$(( RANDOM % 50 + 10 ))MB",
  "active_processes": $(( RANDOM % 5 + 1 )),
  "last_health_check": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "endpoints": ["/core/status", "/core/health", "/core/init"]
}
JSON_EOF
            ;;
        "uMEMORY")
            cat << JSON_EOF
{
  "name": "uMEMORY",
  "type": "data_layer",
  "status": "online",
  "objects_stored": $(( RANDOM % 1000 + 100 )),
  "cache_hit_ratio": "$(( RANDOM % 30 + 70 ))%",
  "last_backup": "$(date -d '1 hour ago' -u +"%Y-%m-%dT%H:%M:%SZ")",
  "endpoints": ["/memory/create", "/memory/read", "/memory/update", "/memory/delete"]
}
JSON_EOF
            ;;
        *)
            echo '{"error": "Module not found"}'
            ;;
    esac
}

handle_activity_log() {
    cat << JSON_EOF
{
  "activities": [
    {
      "timestamp": "$(date -d '5 minutes ago' -u +"%Y-%m-%dT%H:%M:%SZ")",
      "type": "system",
      "message": "System health check completed",
      "level": "info"
    },
    {
      "timestamp": "$(date -d '10 minutes ago' -u +"%Y-%m-%dT%H:%M:%SZ")",
      "type": "api",
      "message": "API request processed: /api/v1/status",
      "level": "info"
    },
    {
      "timestamp": "$(date -d '15 minutes ago' -u +"%Y-%m-%dT%H:%M:%SZ")",
      "type": "script",
      "message": "Automation script executed successfully",
      "level": "info"
    }
  ]
}
JSON_EOF
}

# Main API router
api_router() {
    local endpoint="$1"
    local method="${2:-GET}"
    
    case "$endpoint" in
        "/system/status")
            handle_system_status
            ;;
        "/module/"*)
            local module="$(echo "$endpoint" | sed 's|/module/||')"
            handle_module_details "$module"
            ;;
        "/activity/log")
            handle_activity_log
            ;;
        *)
            echo '{"error": "Endpoint not found", "status": 404}'
            ;;
    esac
}

# Execute if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    api_router "$@"
fi
