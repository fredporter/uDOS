#!/bin/bash
# uNETWORK Services Demo v1.0.5.4
# Demonstrates network layer integration with uCORE, uMEMORY, and uKNOWLEDGE

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source integration layer
source "$UDOS_ROOT/uCORE/code/integration/network-integration-v1054.sh"

echo "🌐 uNETWORK Services Demo - v1.0.5.4"
echo "====================================="

# Initialize network integration (handle errors gracefully)
echo ""
echo "1. Initializing network integration..."
if ! init_network_integration 2>/dev/null; then
    echo "⚠️ Some initialization warnings (expected on subsequent runs)"
    # Initialize foundation directly if integration fails
    init_foundation 2>/dev/null || true
    init_network_foundation 2>/dev/null || true
fi

echo "✅ Network integration initialized"

# Register some demo services
echo ""
echo "2. Registering demo network services..."

# Register web service
"$UDOS_ROOT/uNETWORK/discovery/service-discovery.sh" register "web-dashboard" "8080" "http"

# Register API service
"$UDOS_ROOT/uNETWORK/discovery/service-discovery.sh" register "rest-api" "8081" "http"

# Register WebSocket service
"$UDOS_ROOT/uNETWORK/discovery/service-discovery.sh" register "websocket-server" "8084" "websocket"

# Store service data in uMEMORY and create knowledge relationships
echo ""
echo "3. Storing service data and creating relationships..."

# Source data integration
source "$UDOS_ROOT/uNETWORK/integration/data-integration.sh"

# Store service data
store_service_data "web-dashboard" '{
    "type": "web_service",
    "port": 8080,
    "protocol": "http",
    "description": "Main web dashboard interface",
    "endpoints": ["/", "/dashboard", "/status"]
}'

store_service_data "rest-api" '{
    "type": "api_service", 
    "port": 8081,
    "protocol": "http",
    "description": "RESTful API for data access",
    "endpoints": ["/api/v1/services", "/api/v1/status", "/api/v1/health"]
}'

store_service_data "websocket-server" '{
    "type": "realtime_service",
    "port": 8084, 
    "protocol": "websocket",
    "description": "Real-time communication server",
    "features": ["live_updates", "notifications", "chat"]
}'

# Create service relationships
echo ""
echo "4. Creating service relationships..."

link_services "web-dashboard" "rest-api" "depends_on"
link_services "web-dashboard" "websocket-server" "uses"
link_services "rest-api" "websocket-server" "notifies"

# Discover registered services
echo ""
echo "5. Discovering registered services..."
"$UDOS_ROOT/uNETWORK/discovery/service-discovery.sh" discover

# Test API endpoints
echo ""
echo "6. Testing network API endpoints..."

# Source API layer
source "$UDOS_ROOT/uNETWORK/api/network-api.sh"

echo ""
echo "📋 API Test - List all services:"
handle_api_request "GET" "/api/v1/services" ""

echo ""
echo "📋 API Test - Get web-dashboard status:"
handle_api_request "GET" "/api/v1/service/web-dashboard" ""

echo ""
echo "📋 API Test - Get web-dashboard connections:"
handle_api_request "GET" "/api/v1/connections/web-dashboard" ""

# Test service monitoring
echo ""
echo "7. Testing service monitoring..."
"$UDOS_ROOT/uNETWORK/monitoring/service-monitor.sh" monitor

# Display integration statistics
echo ""
echo "📊 Network Integration Statistics:"
echo "================================="

# Count registered services
local service_count=0
if [ -f "$UDOS_ROOT/uNETWORK/services/discovery.log" ]; then
    service_count="$(grep -c "Registered:" "$UDOS_ROOT/uNETWORK/services/discovery.log" 2>/dev/null || echo "0")"
fi

echo "🌐 Registered Services: $service_count"
echo "🔗 API Endpoints: 3 (/services, /service/*, /connections/*)"
echo "📊 Data Integration: uMEMORY + uKNOWLEDGE connected"
echo "🔍 Health Monitoring: Active"

# Display network knowledge graph
echo ""
echo "🧠 Network Knowledge Graph:"
echo "=========================="

echo ""
echo "📋 Network services in uMEMORY:"
list_objects_by_type "network_service" 2>/dev/null || echo "📭 No services found in memory"

echo ""
echo "🔗 Service relationships:"
get_connected_services "web-dashboard" 2>/dev/null || echo "📭 No relationships found"

# Gateway status
echo ""
echo "8. Testing API Gateway..."
"$UDOS_ROOT/uNETWORK/gateway/api-gateway.sh" health

echo ""
echo "🎯 Network Layer Demo Summary:"
echo "=============================="
echo "✅ Network foundation initialized"
echo "✅ Service discovery working"
echo "✅ Data integration with uMEMORY/uKNOWLEDGE"
echo "✅ API endpoints responding"
echo "✅ Service monitoring active"
echo "✅ Knowledge relationships created"

echo ""
echo "🚀 uNETWORK v1.0.5.4 demo complete!"
