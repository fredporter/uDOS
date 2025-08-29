#!/bin/bash
# Health Check Middleware
# Monitors module health and availability

check_module_health() {
    local module="$1"
    local health_endpoint="$2"
    
    # Simple health check - verify module directory exists and is accessible
    case "$module" in
        "uCORE")
            if [ -f "$UDOS_ROOT/uCORE/code/foundation.sh" ]; then
                echo "healthy"
            else
                echo "unhealthy"
            fi
            ;;
        "uMEMORY")
            if [ -d "$UDOS_ROOT/uMEMORY" ] && [ -f "$UDOS_ROOT/uMEMORY/umemory-core.sh" ]; then
                echo "healthy"
            else
                echo "unhealthy" 
            fi
            ;;
        "uKNOWLEDGE")
            if [ -d "$UDOS_ROOT/uKNOWLEDGE" ] && [ -f "$UDOS_ROOT/uKNOWLEDGE/uknowledge-core.sh" ]; then
                echo "healthy"
            else
                echo "unhealthy"
            fi
            ;;
        "uNETWORK")
            if [ -d "$UDOS_ROOT/uNETWORK" ] && [ -f "$UDOS_ROOT/uNETWORK/network-foundation.sh" ]; then
                echo "healthy"
            else
                echo "unhealthy"
            fi
            ;;
        "uSCRIPT")
            if [ -d "$UDOS_ROOT/uSCRIPT" ] && [ -f "$UDOS_ROOT/uSCRIPT/uscript" ]; then
                echo "healthy"
            else
                echo "unhealthy"
            fi
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

get_all_module_health() {
    echo "{"
    echo "  \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\","
    echo "  \"modules\": {"
    
    local modules=("uCORE" "uMEMORY" "uKNOWLEDGE" "uNETWORK" "uSCRIPT")
    local count=0
    
    for module in "${modules[@]}"; do
        local health="$(check_module_health "$module")"
        echo -n "    \"$module\": \"$health\""
        
        count=$((count + 1))
        if [ $count -lt ${#modules[@]} ]; then
            echo ","
        else
            echo ""
        fi
    done
    
    echo "  }"
    echo "}"
}
