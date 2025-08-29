#!/bin/bash
# Network API Endpoints v1.0.5.4
# RESTful API for network services integration

# API configuration
API_VERSION="1.0.5.4"
API_PREFIX="/api/v1"

# Source integration layer
source "$UDOS_ROOT/uNETWORK/integration/data-integration.sh"

# API: Get service status
api_service_status() {
    local service_name="$1"
    
    echo "Content-Type: application/json"
    echo ""
    
    if [ -n "$service_name" ]; then
        local service_data="$(get_service_data "$service_name" 2>/dev/null || echo '{}')"
        echo "{
            \"status\": \"success\",
            \"service\": \"$service_name\",
            \"data\": $service_data
        }"
    else
        echo "{
            \"status\": \"error\",
            \"message\": \"Service name required\"
        }"
    fi
}

# API: List all services
api_list_services() {
    echo "Content-Type: application/json"
    echo ""
    
    # Get all network services from uMEMORY
    local services="$(list_objects_by_type "network_service" 2>/dev/null || echo '[]')"
    echo "{
        \"status\": \"success\",
        \"services\": $services
    }"
}

# API: Get service connections
api_service_connections() {
    local service_name="$1"
    
    echo "Content-Type: application/json"
    echo ""
    
    if [ -n "$service_name" ]; then
        local connections="$(get_connected_services "$service_name" 2>/dev/null || echo '[]')"
        echo "{
            \"status\": \"success\",
            \"service\": \"$service_name\",
            \"connections\": $connections
        }"
    else
        echo "{
            \"status\": \"error\",
            \"message\": \"Service name required\"
        }"
    fi
}

# Main API router
handle_api_request() {
    local method="$1"
    local path="$2"
    local query="$3"
    
    case "$path" in
        "/api/v1/services")
            api_list_services
            ;;
        "/api/v1/service/"*)
            local service_name="$(echo "$path" | sed 's|/api/v1/service/||')"
            api_service_status "$service_name"
            ;;
        "/api/v1/connections/"*)
            local service_name="$(echo "$path" | sed 's|/api/v1/connections/||')"
            api_service_connections "$service_name"
            ;;
        *)
            echo "Content-Type: application/json"
            echo ""
            echo "{
                \"status\": \"error\",
                \"message\": \"API endpoint not found\",
                \"path\": \"$path\"
            }"
            ;;
    esac
}
