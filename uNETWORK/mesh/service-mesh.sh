#!/bin/bash
# uDOS Service Mesh v1.0.5.6
# Distributed service coordination and management layer

# Get script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Service Mesh Configuration
MESH_VERSION="1.0.5.6"
MESH_NAME="uDOS-ServiceMesh"
MESH_CONFIG_DIR="$UDOS_ROOT/uNETWORK/mesh"
SERVICE_REGISTRY="$MESH_CONFIG_DIR/service-registry.json"
ROUTING_TABLE="$MESH_CONFIG_DIR/routing-table.json"

# Initialize Service Mesh
init_service_mesh() {
    echo "🕸️ Initializing $MESH_NAME v$MESH_VERSION"
    
    # Create mesh directories
    mkdir -p "$MESH_CONFIG_DIR"
    mkdir -p "$MESH_CONFIG_DIR/services"
    mkdir -p "$MESH_CONFIG_DIR/policies"
    mkdir -p "$MESH_CONFIG_DIR/logs"
    
    # Initialize service registry
    create_service_registry
    
    # Setup routing table
    create_routing_table
    
    # Create service discovery mesh
    setup_service_discovery
    
    # Initialize load balancing
    setup_load_balancing
    
    echo "✅ Service Mesh initialized"
}

# Create service registry for mesh
create_service_registry() {
    cat > "$SERVICE_REGISTRY" << EOF
{
  "mesh": {
    "name": "$MESH_NAME",
    "version": "$MESH_VERSION",
    "created": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "topology": "single-node"
  },
  "services": {
    "core-foundation": {
      "module": "uCORE",
      "type": "foundation",
      "endpoints": ["/core/status", "/core/health", "/core/init"],
      "load_balancer": "round-robin",
      "health_check": "/core/health",
      "timeout": 30,
      "retries": 3,
      "active": true
    },
    "memory-data": {
      "module": "uMEMORY", 
      "type": "data",
      "endpoints": ["/memory/create", "/memory/read", "/memory/update", "/memory/delete"],
      "load_balancer": "least-connections",
      "health_check": "/memory/health",
      "timeout": 60,
      "retries": 2,
      "active": true
    },
    "knowledge-graph": {
      "module": "uKNOWLEDGE",
      "type": "graph",
      "endpoints": ["/knowledge/query", "/knowledge/traverse", "/knowledge/add"],
      "load_balancer": "weighted-round-robin",
      "health_check": "/knowledge/health", 
      "timeout": 45,
      "retries": 2,
      "active": true
    },
    "network-services": {
      "module": "uNETWORK",
      "type": "network",
      "endpoints": ["/network/discovery", "/network/routing", "/network/monitoring"],
      "load_balancer": "round-robin",
      "health_check": "/network/health",
      "timeout": 30,
      "retries": 3,
      "active": true
    },
    "script-automation": {
      "module": "uSCRIPT",
      "type": "automation", 
      "endpoints": ["/script/execute", "/script/register", "/script/list"],
      "load_balancer": "round-robin",
      "health_check": "/script/health",
      "timeout": 120,
      "retries": 1,
      "active": true
    }
  },
  "policies": {
    "circuit_breaker": {
      "failure_threshold": 5,
      "timeout": 60,
      "half_open_timeout": 30
    },
    "rate_limiting": {
      "requests_per_minute": 100,
      "burst_size": 20
    },
    "security": {
      "authentication_required": false,
      "encryption": false,
      "allowed_modules": ["uCORE", "uMEMORY", "uKNOWLEDGE", "uNETWORK", "uSCRIPT"]
    }
  }
}
EOF

    echo "📋 Service registry created"
}

# Create routing table
create_routing_table() {
    cat > "$ROUTING_TABLE" << EOF
{
  "routing": {
    "version": "$MESH_VERSION",
    "strategy": "priority-based",
    "created": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  },
  "routes": [
    {
      "pattern": "/core/*",
      "target": "core-foundation",
      "priority": 1,
      "backup": null,
      "middleware": ["auth", "logging"]
    },
    {
      "pattern": "/memory/*", 
      "target": "memory-data",
      "priority": 2,
      "backup": null,
      "middleware": ["auth", "logging", "caching"]
    },
    {
      "pattern": "/knowledge/*",
      "target": "knowledge-graph", 
      "priority": 2,
      "backup": null,
      "middleware": ["auth", "logging"]
    },
    {
      "pattern": "/network/*",
      "target": "network-services",
      "priority": 1,
      "backup": null,
      "middleware": ["logging"]
    },
    {
      "pattern": "/script/*",
      "target": "script-automation",
      "priority": 3,
      "backup": null,
      "middleware": ["auth", "logging", "timeout"]
    }
  ],
  "fallback": {
    "route": "/health",
    "response": {"status": "service_mesh_active", "version": "$MESH_VERSION"}
  }
}
EOF

    echo "🛤️ Routing table created"
}

# Setup service discovery for mesh
setup_service_discovery() {
    cat > "$MESH_CONFIG_DIR/services/discovery.sh" << 'EOF'
#!/bin/bash
# Service Discovery for Mesh

discover_services() {
    local service_type="$1"
    
    # Read service registry
    if [ ! -f "$SERVICE_REGISTRY" ]; then
        echo '{"error": "Service registry not found"}'
        return 1
    fi
    
    echo "🔍 Discovering services of type: ${service_type:-all}"
    
    # Simple discovery - list active services
    echo "{"
    echo "  \"discovered_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\","
    echo "  \"services\": ["
    
    local services=("core-foundation" "memory-data" "knowledge-graph" "network-services" "script-automation")
    local count=0
    
    for service in "${services[@]}"; do
        echo -n "    {\"name\": \"$service\", \"status\": \"active\", \"module\": \"$(echo $service | cut -d'-' -f1)\"}"
        
        count=$((count + 1))
        if [ $count -lt ${#services[@]} ]; then
            echo ","
        else
            echo ""
        fi
    done
    
    echo "  ]"
    echo "}"
}

register_service() {
    local service_name="$1"
    local service_config="$2"
    
    echo "📝 Registering service: $service_name"
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ"): $service_name registered" >> "$MESH_CONFIG_DIR/logs/service-discovery.log"
    echo '{"status": "registered", "service": "'$service_name'"}'
}

unregister_service() {
    local service_name="$1"
    
    echo "🗑️ Unregistering service: $service_name"
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ"): $service_name unregistered" >> "$MESH_CONFIG_DIR/logs/service-discovery.log"
    echo '{"status": "unregistered", "service": "'$service_name'"}'
}
EOF

    chmod +x "$MESH_CONFIG_DIR/services/discovery.sh"
    echo "🔍 Service discovery configured"
}

# Setup load balancing
setup_load_balancing() {
    cat > "$MESH_CONFIG_DIR/services/load-balancer.sh" << 'EOF'
#!/bin/bash
# Load Balancer for Service Mesh

# Round-robin load balancing
round_robin_balance() {
    local service="$1"
    local endpoints="$2"
    
    # Simple round-robin implementation
    local timestamp="$(date +%s)"
    local endpoint_count="$(echo "$endpoints" | tr ',' '\n' | wc -l)"
    local selected="$(( (timestamp % endpoint_count) + 1 ))"
    
    echo "$endpoints" | tr ',' '\n' | sed -n "${selected}p"
}

# Least connections load balancing  
least_connections_balance() {
    local service="$1"
    local endpoints="$2"
    
    # For now, return first endpoint (would track connections in real implementation)
    echo "$endpoints" | tr ',' '\n' | head -1
}

# Weighted round-robin
weighted_round_robin_balance() {
    local service="$1"
    local endpoints="$2"
    
    # Simple weighted selection (would use actual weights in real implementation)
    round_robin_balance "$service" "$endpoints"
}

# Main load balancing function
balance_request() {
    local service="$1"
    local strategy="$2"
    local endpoints="$3"
    
    case "$strategy" in
        "round-robin")
            round_robin_balance "$service" "$endpoints"
            ;;
        "least-connections")
            least_connections_balance "$service" "$endpoints"
            ;;
        "weighted-round-robin")
            weighted_round_robin_balance "$service" "$endpoints"
            ;;
        *)
            # Default to round-robin
            round_robin_balance "$service" "$endpoints"
            ;;
    esac
}
EOF

    chmod +x "$MESH_CONFIG_DIR/services/load-balancer.sh"
    echo "⚖️ Load balancer configured"
}

# Route request through service mesh
route_request() {
    local path="$1"
    local method="$2"
    local data="$3"
    
    echo "🛤️ Routing request: $method $path"
    
    # Determine target service based on path
    local target_service=""
    case "$path" in
        /core/*)
            target_service="core-foundation"
            ;;
        /memory/*)
            target_service="memory-data"
            ;;
        /knowledge/*)
            target_service="knowledge-graph"
            ;;
        /network/*)
            target_service="network-services"
            ;;
        /script/*)
            target_service="script-automation"
            ;;
        *)
            echo '{"error": "Route not found", "path": "'$path'"}'
            return 1
            ;;
    esac
    
    # Log the routing
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ"): $method $path -> $target_service" >> "$MESH_CONFIG_DIR/logs/routing.log"
    
    # Use load balancer if needed
    source "$MESH_CONFIG_DIR/services/load-balancer.sh"
    local selected_endpoint="$(balance_request "$target_service" "round-robin" "$path")"
    
    # Route to inter-module communication API
    source "$UDOS_ROOT/uNETWORK/api/inter-module-communication.sh"
    
    # Extract module from service name
    local module="$(echo "$target_service" | cut -d'-' -f1)"
    case "$module" in
        "core") module="uCORE" ;;
        "memory") module="uMEMORY" ;;
        "knowledge") module="uKNOWLEDGE" ;;
        "network") module="uNETWORK" ;;
        "script") module="uSCRIPT" ;;
    esac
    
    # Send request through API
    send_module_request "$module" "$method" "$data"
}

# Get mesh topology
get_mesh_topology() {
    echo "🕸️ Service Mesh Topology"
    echo "========================"
    echo "Mesh Name: $MESH_NAME"
    echo "Version: $MESH_VERSION"
    echo "Type: Single-node mesh"
    echo ""
    
    if [ -f "$SERVICE_REGISTRY" ]; then
        echo "📊 Active Services:"
        echo "  • core-foundation (uCORE)"
        echo "  • memory-data (uMEMORY)"
        echo "  • knowledge-graph (uKNOWLEDGE)"
        echo "  • network-services (uNETWORK)"
        echo "  • script-automation (uSCRIPT)"
        
        echo ""
        echo "🛤️ Routing Patterns:"
        echo "  • /core/* → core-foundation"
        echo "  • /memory/* → memory-data" 
        echo "  • /knowledge/* → knowledge-graph"
        echo "  • /network/* → network-services"
        echo "  • /script/* → script-automation"
    else
        echo "❌ Service registry not found"
    fi
}

# Test mesh routing
test_mesh_routing() {
    echo "🧪 Testing Service Mesh Routing"
    echo "==============================="
    
    local test_routes=("/core/health" "/memory/status" "/knowledge/status" "/network/status" "/script/status")
    
    for route in "${test_routes[@]}"; do
        echo ""
        echo "🧪 Testing route: $route"
        local response="$(route_request "$route" "status" "")"
        echo "   Response: $response"
    done
    
    echo ""
    echo "✅ Mesh routing test complete"
}

# Show mesh status
show_mesh_status() {
    echo "🕸️ $MESH_NAME Status"
    echo "===================="
    echo "Version: $MESH_VERSION"
    echo "Config: $MESH_CONFIG_DIR"
    echo ""
    
    # Service registry status
    if [ -f "$SERVICE_REGISTRY" ]; then
        echo "📋 Service Registry: ✅ Active"
        echo "📊 Services: 5 registered"
    else
        echo "📋 Service Registry: ❌ Not found"
    fi
    
    # Routing table status
    if [ -f "$ROUTING_TABLE" ]; then
        echo "🛤️ Routing Table: ✅ Active"
        echo "📍 Routes: 5 configured"
    else
        echo "🛤️ Routing Table: ❌ Not found"
    fi
    
    # Recent activity
    echo ""
    echo "📝 Recent Routing Activity:"
    if [ -f "$MESH_CONFIG_DIR/logs/routing.log" ]; then
        tail -3 "$MESH_CONFIG_DIR/logs/routing.log" 2>/dev/null || echo "   No recent activity"
    else
        echo "   No logs yet"
    fi
}

# Main command interface
main() {
    case "${1:-help}" in
        "init")
            init_service_mesh
            ;;
        "route")
            if [ $# -lt 3 ]; then
                echo "Usage: $0 route <path> <method> [data]"
                exit 1
            fi
            route_request "$2" "$3" "$4"
            ;;
        "topology")
            get_mesh_topology
            ;;
        "test")
            test_mesh_routing
            ;;
        "status")
            show_mesh_status
            ;;
        "help"|*)
            echo "$MESH_NAME v$MESH_VERSION"
            echo "Usage: $0 {init|route|topology|test|status}"
            echo ""
            echo "Commands:"
            echo "  init                    - Initialize service mesh"
            echo "  route <path> <method>   - Route request through mesh"
            echo "  topology                - Show mesh topology"
            echo "  test                    - Test mesh routing"
            echo "  status                  - Show mesh status"
            echo ""
            echo "Examples:"
            echo "  $0 init                 - Initialize service mesh"
            echo "  $0 route /core/health status - Route health check"
            echo "  $0 test                 - Test all routes"
            echo "  $0 topology             - Show service topology"
            ;;
    esac
}

# Execute if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
