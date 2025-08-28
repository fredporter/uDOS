#!/bin/bash
# uNETWORK Integration Layer v1.0.5.4
# Connects uNETWORK with uCORE, uMEMORY, and uKNOWLEDGE systems

set -e

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Source required modules
source "$UDOS_ROOT/uCORE/code/foundation-init-v1053.sh"
source "$UDOS_ROOT/uNETWORK/network-foundation-v1054.sh"

# Integration configuration
INTEGRATION_VERSION="1.0.5.4"
INTEGRATION_LOG_PREFIX="[NET-INTEGRATION]"

# ════════════════════════════════════════════════════════════════
# 🔗 NETWORK INTEGRATION CORE FUNCTIONS
# ════════════════════════════════════════════════════════════════

# Initialize complete network integration
init_network_integration() {
    # Initialize base foundation first (this loads log_info function)
    init_foundation
    
    # Source network foundation after logging is available
    log_info "$INTEGRATION_LOG_PREFIX" "Initializing uNETWORK Integration v$INTEGRATION_VERSION..."
    
    # Initialize network foundation
    init_network_foundation
    
    # Create network-specific integrations
    create_network_data_integration
    create_network_api_endpoints
    create_network_service_monitoring
    
    # Register network services with uCORE
    register_network_with_core
    
    log_info "$INTEGRATION_LOG_PREFIX" "Network integration complete!"
}

# Create network data integration with uMEMORY and uKNOWLEDGE
create_network_data_integration() {
    log_info "$INTEGRATION_LOG_PREFIX" "Creating network data integration..."
    
    local integration_file="$UNETWORK_ROOT/integration/data-integration.sh"
    mkdir -p "$UNETWORK_ROOT/integration"
    
    cat > "$integration_file" << 'EOF'
#!/bin/bash
# Network Data Integration v1.0.5.4
# Connects network services with uMEMORY and uKNOWLEDGE

# Source required systems
source "$UDOS_ROOT/uMEMORY/umemory-core.sh"
source "$UDOS_ROOT/uKNOWLEDGE/uknowledge-core.sh"

# Store network service data
store_service_data() {
    local service_name="$1"
    local service_data="$2"
    
    echo "📊 Storing network service data: $service_name"
    
    # Store in uMEMORY
    local service_object="{
        \"name\": \"$service_name\",
        \"type\": \"network_service\",
        \"data\": $service_data,
        \"created_at\": \"$(date '+%Y-%m-%d %H:%M:%S')\"
    }"
    
    create_object "$service_name" "$service_object"
    
    # Create knowledge relationships
    create_node "$service_name" "network_service" "$service_object"
    
    echo "✅ Service data stored and indexed"
}

# Retrieve service network data
get_service_data() {
    local service_name="$1"
    
    echo "📥 Retrieving network service data: $service_name"
    read_object "$service_name"
}

# Create service relationships
link_services() {
    local service_a="$1"
    local service_b="$2"
    local relationship="$3"
    
    echo "🔗 Creating service relationship: $service_a -> $service_b ($relationship)"
    create_edge "${service_a}_${relationship}_${service_b}" "$service_a" "$service_b" "$relationship"
}

# Get connected services
get_connected_services() {
    local service_name="$1"
    
    echo "🌐 Finding services connected to: $service_name"
    get_connected_nodes "$service_name"
}
EOF
    chmod +x "$integration_file"
    
    log_info "$INTEGRATION_LOG_PREFIX" "Network data integration created"
}

# Create network API endpoints
create_network_api_endpoints() {
    log_info "$INTEGRATION_LOG_PREFIX" "Creating network API endpoints..."
    
    local api_file="$UNETWORK_ROOT/api/network-api.sh"
    mkdir -p "$UNETWORK_ROOT/api"
    
    cat > "$api_file" << 'EOF'
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
EOF
    chmod +x "$api_file"
    
    log_info "$INTEGRATION_LOG_PREFIX" "Network API endpoints created"
}

# Create network service monitoring
create_network_service_monitoring() {
    log_info "$INTEGRATION_LOG_PREFIX" "Creating network service monitoring..."
    
    local monitor_file="$UNETWORK_ROOT/monitoring/service-monitor.sh"
    mkdir -p "$UNETWORK_ROOT/monitoring"
    
    cat > "$monitor_file" << 'EOF'
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
EOF
    chmod +x "$monitor_file"
    
    log_info "$INTEGRATION_LOG_PREFIX" "Network service monitoring created"
}

# Register network services with uCORE
register_network_with_core() {
    log_info "$INTEGRATION_LOG_PREFIX" "Registering network services with uCORE..."
    
    # Register network module with uCORE service registry
    register_service "uNETWORK" "network" "$UNETWORK_ROOT/network-foundation-v1054.sh" "Network layer and services"
    
    # Register specific network services
    register_service "network-api" "api" "$UNETWORK_ROOT/api/network-api.sh" "Network REST API"
    register_service "service-discovery" "discovery" "$UNETWORK_ROOT/discovery/service-discovery.sh" "Service discovery and registration"
    register_service "api-gateway" "gateway" "$UNETWORK_ROOT/gateway/api-gateway.sh" "API gateway and routing"
    register_service "service-monitor" "monitoring" "$UNETWORK_ROOT/monitoring/service-monitor.sh" "Service health monitoring"
    
    log_info "$INTEGRATION_LOG_PREFIX" "Network services registered with uCORE"
}

# ════════════════════════════════════════════════════════════════
# 🧪 NETWORK INTEGRATION TESTING
# ════════════════════════════════════════════════════════════════

# Test network integration
test_network_integration() {
    echo "🧪 Testing uNETWORK Integration v$INTEGRATION_VERSION"
    echo "=================================================="
    
    # Test 1: Foundation systems
    echo "1. Testing foundation systems..."
    if init_foundation && init_network_foundation; then
        echo "✅ Foundation systems initialized"
    else
        echo "❌ Foundation systems failed"
        return 1
    fi
    
    # Test 2: Service registration
    echo "2. Testing service registration..."
    register_network_service "test-service" "http" "8080" "/test"
    if [ $? -eq 0 ]; then
        echo "✅ Service registration works"
    else
        echo "❌ Service registration failed"
        return 1
    fi
    
    # Test 3: Data integration
    echo "3. Testing data integration..."
    if [ -f "$UNETWORK_ROOT/integration/data-integration.sh" ]; then
        echo "✅ Data integration layer created"
    else
        echo "❌ Data integration layer missing"
        return 1
    fi
    
    # Test 4: API endpoints
    echo "4. Testing API endpoints..."
    if [ -f "$UNETWORK_ROOT/api/network-api.sh" ]; then
        echo "✅ API endpoints created"
    else
        echo "❌ API endpoints missing"
        return 1
    fi
    
    # Test 5: Service monitoring
    echo "5. Testing service monitoring..."
    if [ -f "$UNETWORK_ROOT/monitoring/service-monitor.sh" ]; then
        echo "✅ Service monitoring created"
    else
        echo "❌ Service monitoring missing"
        return 1
    fi
    
    echo ""
    echo "🎯 Network Integration Statistics:"
    echo "================================="
    echo "📊 Network Services: $(find "$UNETWORK_ROOT" -name "*.sh" | wc -l | tr -d ' ')"
    echo "📋 API Endpoints: 3 (status, list, connections)"
    echo "🔍 Monitoring: Health checks with uMEMORY integration"
    echo "🔗 Integration: uCORE + uMEMORY + uKNOWLEDGE connected"
    
    echo ""
    echo "✅ Network integration test complete!"
}

# ════════════════════════════════════════════════════════════════
# 🚀 MAIN INTEGRATION EXECUTION
# ════════════════════════════════════════════════════════════════

# Main function
main() {
    case "${1:-init}" in
        init)
            init_network_integration
            ;;
        test)
            test_network_integration
            ;;
        register)
            register_network_service "$2" "$3" "$4" "$5"
            ;;
        *)
            echo "Usage: $0 {init|test|register <name> <type> <port> <path>}"
            exit 1
            ;;
    esac
}

# Execute if run directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
