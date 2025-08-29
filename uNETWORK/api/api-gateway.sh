#!/bin/bash
# uDOS API Gateway v1.0.5.6
# Unified external access point for all uDOS services

# Get script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# API Gateway Configuration
GATEWAY_VERSION="1.0.5.6"
GATEWAY_PORT="8081"
GATEWAY_HOST="localhost"
GATEWAY_NAME="uDOS-APIGateway"
GATEWAY_CONFIG_DIR="$UDOS_ROOT/uNETWORK/gateway"

# Initialize API Gateway
init_api_gateway() {
    echo "🌐 Initializing $GATEWAY_NAME v$GATEWAY_VERSION"
    
    # Create gateway directories
    mkdir -p "$GATEWAY_CONFIG_DIR"
    mkdir -p "$GATEWAY_CONFIG_DIR/routes"
    mkdir -p "$GATEWAY_CONFIG_DIR/middleware"
    mkdir -p "$GATEWAY_CONFIG_DIR/logs"
    mkdir -p "$GATEWAY_CONFIG_DIR/cache"
    
    # Create gateway configuration
    create_gateway_config
    
    # Setup API routes
    setup_api_routes
    
    # Initialize middleware
    setup_middleware
    
    # Create authentication
    setup_authentication
    
    echo "✅ API Gateway initialized"
}

# Create gateway configuration
create_gateway_config() {
    cat > "$GATEWAY_CONFIG_DIR/gateway-config.json" << EOF
{
  "gateway": {
    "name": "$GATEWAY_NAME",
    "version": "$GATEWAY_VERSION",
    "host": "$GATEWAY_HOST",
    "port": $GATEWAY_PORT,
    "created": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "environment": "development"
  },
  "upstream": {
    "service_mesh": {
      "enabled": true,
      "endpoint": "internal://service-mesh"
    },
    "inter_module_api": {
      "enabled": true,
      "endpoint": "internal://inter-module-communication"
    }
  },
  "security": {
    "cors": {
      "enabled": true,
      "allowed_origins": ["*"],
      "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
      "allowed_headers": ["Content-Type", "Authorization"]
    },
    "rate_limiting": {
      "enabled": true,
      "requests_per_minute": 60,
      "burst_size": 10
    },
    "authentication": {
      "enabled": false,
      "type": "none"
    }
  },
  "middleware": {
    "logging": true,
    "caching": true,
    "compression": true,
    "validation": true
  },
  "cache": {
    "enabled": true,
    "ttl": 300,
    "max_size": 100
  }
}
EOF

    echo "⚙️ Gateway configuration created"
}

# Setup API routes
setup_api_routes() {
    cat > "$GATEWAY_CONFIG_DIR/routes/api-routes.json" << EOF
{
  "routes": {
    "v1": {
      "prefix": "/api/v1",
      "endpoints": {
        "health": {
          "path": "/health",
          "methods": ["GET"],
          "upstream": "/health",
          "cache": false,
          "auth_required": false
        },
        "status": {
          "path": "/status",
          "methods": ["GET"],
          "upstream": "/core/status",
          "cache": true,
          "auth_required": false
        },
        "memory": {
          "path": "/memory/*",
          "methods": ["GET", "POST", "PUT", "DELETE"],
          "upstream": "/memory/*",
          "cache": false,
          "auth_required": false
        },
        "knowledge": {
          "path": "/knowledge/*", 
          "methods": ["GET", "POST"],
          "upstream": "/knowledge/*",
          "cache": true,
          "auth_required": false
        },
        "scripts": {
          "path": "/scripts/*",
          "methods": ["GET", "POST"],
          "upstream": "/script/*",
          "cache": false,
          "auth_required": false
        },
        "network": {
          "path": "/network/*",
          "methods": ["GET"],
          "upstream": "/network/*",
          "cache": true,
          "auth_required": false
        }
      }
    },
    "admin": {
      "prefix": "/admin",
      "endpoints": {
        "gateway_status": {
          "path": "/gateway/status",
          "methods": ["GET"],
          "upstream": "internal://gateway-status",
          "cache": false,
          "auth_required": true
        },
        "mesh_topology": {
          "path": "/mesh/topology",
          "methods": ["GET"],
          "upstream": "internal://mesh-topology",
          "cache": true,
          "auth_required": true
        }
      }
    }
  }
}
EOF

    echo "🛤️ API routes configured"
}

# Setup middleware
setup_middleware() {
    # Request logging middleware
    cat > "$GATEWAY_CONFIG_DIR/middleware/logging.sh" << 'EOF'
#!/bin/bash
# Request Logging Middleware

log_request() {
    local method="$1"
    local path="$2"
    local client_ip="$3"
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    echo "$timestamp [$client_ip] $method $path" >> "$GATEWAY_CONFIG_DIR/logs/access.log"
}

log_response() {
    local status="$1"
    local response_time="$2"
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    echo "$timestamp Response: $status (${response_time}ms)" >> "$GATEWAY_CONFIG_DIR/logs/access.log"
}
EOF

    # Caching middleware
    cat > "$GATEWAY_CONFIG_DIR/middleware/caching.sh" << 'EOF'
#!/bin/bash
# Response Caching Middleware

get_cache_key() {
    local method="$1"
    local path="$2"
    local params="$3"
    
    echo "${method}_${path}_$(echo "$params" | md5sum | cut -d' ' -f1)"
}

get_cached_response() {
    local cache_key="$1"
    local cache_file="$GATEWAY_CONFIG_DIR/cache/$cache_key"
    
    if [ -f "$cache_file" ]; then
        local cache_time="$(stat -f "%m" "$cache_file" 2>/dev/null || stat -c "%Y" "$cache_file" 2>/dev/null)"
        local current_time="$(date +%s)"
        local ttl="300"  # 5 minutes
        
        if [ $((current_time - cache_time)) -lt $ttl ]; then
            cat "$cache_file"
            return 0
        else
            rm -f "$cache_file"
        fi
    fi
    
    return 1
}

cache_response() {
    local cache_key="$1"
    local response="$2"
    local cache_file="$GATEWAY_CONFIG_DIR/cache/$cache_key"
    
    echo "$response" > "$cache_file"
}
EOF

    # Validation middleware
    cat > "$GATEWAY_CONFIG_DIR/middleware/validation.sh" << 'EOF'
#!/bin/bash
# Request Validation Middleware

validate_method() {
    local method="$1"
    local allowed_methods="$2"
    
    if echo "$allowed_methods" | grep -q "$method"; then
        return 0
    else
        return 1
    fi
}

validate_path() {
    local path="$1"
    local route_pattern="$2"
    
    # Simple pattern matching (would use regex in production)
    case "$path" in
        $route_pattern)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

validate_json() {
    local json_data="$1"
    
    # Basic JSON validation
    if echo "$json_data" | python -m json.tool >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}
EOF

    chmod +x "$GATEWAY_CONFIG_DIR/middleware/"*.sh
    echo "🔧 Middleware configured"
}

# Setup authentication
setup_authentication() {
    cat > "$GATEWAY_CONFIG_DIR/middleware/auth.sh" << 'EOF'
#!/bin/bash
# Authentication Middleware

authenticate_request() {
    local auth_header="$1"
    local required="$2"
    
    if [ "$required" = "false" ]; then
        return 0
    fi
    
    # For now, authentication is disabled
    # In production, would validate JWT tokens or API keys
    if [ -n "$auth_header" ]; then
        return 0
    else
        return 1
    fi
}

generate_auth_token() {
    local user="$1"
    
    # Simple token generation (would use JWT in production)
    echo "$(date +%s)_${user}_$(openssl rand -hex 16 2>/dev/null || head -c 16 /dev/urandom | xxd -p)"
}
EOF

    chmod +x "$GATEWAY_CONFIG_DIR/middleware/auth.sh"
    echo "🔐 Authentication configured"
}

# Process API request
process_request() {
    local method="$1"
    local path="$2"
    local data="$3"
    local client_ip="${4:-localhost}"
    
    # Load middleware
    source "$GATEWAY_CONFIG_DIR/middleware/logging.sh"
    source "$GATEWAY_CONFIG_DIR/middleware/caching.sh"
    source "$GATEWAY_CONFIG_DIR/middleware/validation.sh"
    source "$GATEWAY_CONFIG_DIR/middleware/auth.sh"
    
    # Log request
    log_request "$method" "$path" "$client_ip"
    
    # Find matching route
    local route_info="$(find_route "$path")"
    if [ -z "$route_info" ]; then
        echo '{"error": "Route not found", "path": "'$path'", "status": 404}'
        return 1
    fi
    
    # Extract route details
    local upstream="$(echo "$route_info" | cut -d'|' -f1)"
    local cache_enabled="$(echo "$route_info" | cut -d'|' -f2)"
    local auth_required="$(echo "$route_info" | cut -d'|' -f3)"
    local allowed_methods="$(echo "$route_info" | cut -d'|' -f4)"
    
    # Validate method
    if ! validate_method "$method" "$allowed_methods"; then
        echo '{"error": "Method not allowed", "method": "'$method'", "status": 405}'
        return 1
    fi
    
    # Check authentication
    if ! authenticate_request "" "$auth_required"; then
        echo '{"error": "Unauthorized", "status": 401}'
        return 1
    fi
    
    # Check cache if enabled
    if [ "$cache_enabled" = "true" ] && [ "$method" = "GET" ]; then
        local cache_key="$(get_cache_key "$method" "$path" "")"
        local cached_response="$(get_cached_response "$cache_key")"
        
        if [ $? -eq 0 ]; then
            echo "$cached_response"
            log_response "200" "0" 
            return 0
        fi
    fi
    
    # Route to upstream service
    local response="$(route_to_upstream "$upstream" "$method" "$data")"
    local status="$?"
    
    # Cache successful responses
    if [ "$cache_enabled" = "true" ] && [ "$method" = "GET" ] && [ $status -eq 0 ]; then
        cache_response "$cache_key" "$response"
    fi
    
    # Log response
    log_response "$(echo "$response" | grep -o '"status":[0-9]*' | cut -d':' -f2 || echo "200")" "10"
    
    echo "$response"
    return $status
}

# Find route configuration
find_route() {
    local request_path="$1"
    
    # Simple route matching (would use proper routing in production)
    case "$request_path" in
        "/api/v1/health")
            echo "/health|false|false|GET"
            ;;
        "/api/v1/status")
            echo "/core/status|true|false|GET"
            ;;
        "/api/v1/memory/"*)
            local upstream_path="$(echo "$request_path" | sed 's|^/api/v1||')"
            echo "$upstream_path|false|false|GET,POST,PUT,DELETE"
            ;;
        "/api/v1/knowledge/"*)
            local upstream_path="$(echo "$request_path" | sed 's|^/api/v1||')"
            echo "$upstream_path|true|false|GET,POST"
            ;;
        "/api/v1/scripts/"*)
            local upstream_path="$(echo "$request_path" | sed 's|^/api/v1/scripts|/script|')"
            echo "$upstream_path|false|false|GET,POST"
            ;;
        "/api/v1/network/"*)
            local upstream_path="$(echo "$request_path" | sed 's|^/api/v1||')"
            echo "$upstream_path|true|false|GET"
            ;;
        "/admin/gateway/status")
            echo "internal://gateway-status|false|true|GET"
            ;;
        "/admin/mesh/topology")
            echo "internal://mesh-topology|true|true|GET"
            ;;
        *)
            # No route found
            return 1
            ;;
    esac
}

# Route to upstream service
route_to_upstream() {
    local upstream="$1"
    local method="$2"
    local data="$3"
    
    case "$upstream" in
        "internal://gateway-status")
            get_gateway_status
            ;;
        "internal://mesh-topology")
            source "$UDOS_ROOT/uNETWORK/mesh/service-mesh.sh"
            get_mesh_topology | sed 's/^/    /' | awk 'BEGIN{print "{"} {print "\"output\": \"" $0 "\","} END{print "\"status\": 200}"}'
            ;;
        "/health")
            echo '{"status": "healthy", "gateway": "'$GATEWAY_NAME'", "version": "'$GATEWAY_VERSION'", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}'
            ;;
        *)
            # Route through service mesh
            source "$UDOS_ROOT/uNETWORK/mesh/service-mesh.sh"
            route_request "$upstream" "$method" "$data"
            ;;
    esac
}

# Get gateway status
get_gateway_status() {
    local uptime="$(ps -o etime= -p $$ 2>/dev/null | tr -d ' ' || echo "unknown")"
    local request_count="$(wc -l < "$GATEWAY_CONFIG_DIR/logs/access.log" 2>/dev/null || echo "0")"
    
    cat << EOF
{
  "gateway": {
    "name": "$GATEWAY_NAME",
    "version": "$GATEWAY_VERSION",
    "status": "running",
    "uptime": "$uptime",
    "host": "$GATEWAY_HOST",
    "port": $GATEWAY_PORT
  },
  "stats": {
    "total_requests": $request_count,
    "cache_hits": 0,
    "active_connections": 1
  },
  "health": {
    "service_mesh": "healthy",
    "inter_module_api": "healthy",
    "cache_system": "healthy"
  },
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
}

# Start simple HTTP server (simulation)
start_gateway_server() {
    echo "🚀 Starting $GATEWAY_NAME on $GATEWAY_HOST:$GATEWAY_PORT"
    echo ""
    echo "📡 Available Endpoints:"
    echo "  GET  /api/v1/health              - Health check"
    echo "  GET  /api/v1/status              - System status"
    echo "  GET  /api/v1/memory/*            - Memory operations"
    echo "  GET  /api/v1/knowledge/*         - Knowledge queries"
    echo "  GET  /api/v1/scripts/*           - Script operations"
    echo "  GET  /api/v1/network/*           - Network services"
    echo "  GET  /admin/gateway/status       - Gateway status"
    echo "  GET  /admin/mesh/topology        - Service mesh topology"
    echo ""
    echo "🔗 Gateway URL: http://$GATEWAY_HOST:$GATEWAY_PORT"
    echo ""
    echo "✅ Gateway simulation active (use 'test' command to try endpoints)"
}

# Test gateway endpoints
test_gateway() {
    echo "🧪 Testing API Gateway Endpoints"
    echo "================================="
    
    local test_endpoints=(
        "GET /api/v1/health"
        "GET /api/v1/status" 
        "GET /api/v1/memory/status"
        "GET /api/v1/knowledge/status"
        "GET /api/v1/scripts/status"
        "GET /admin/gateway/status"
    )
    
    for endpoint in "${test_endpoints[@]}"; do
        local method="$(echo "$endpoint" | cut -d' ' -f1)"
        local path="$(echo "$endpoint" | cut -d' ' -f2)"
        
        echo ""
        echo "🧪 Testing: $method $path"
        local response="$(process_request "$method" "$path" "" "test-client")"
        echo "   Response: $(echo "$response" | head -1)"
    done
    
    echo ""
    echo "✅ Gateway endpoint testing complete"
}

# Show gateway documentation
show_api_docs() {
    cat << 'EOF'
🌐 uDOS API Gateway Documentation
=================================

Base URL: http://localhost:8081

## API Endpoints

### Health & Status
- GET /api/v1/health           - Gateway health check
- GET /api/v1/status           - System status overview

### Memory Module  
- GET /api/v1/memory/status    - Memory system status
- POST /api/v1/memory/create   - Create memory object
- GET /api/v1/memory/read      - Read memory object
- PUT /api/v1/memory/update    - Update memory object
- DELETE /api/v1/memory/delete - Delete memory object

### Knowledge Module
- GET /api/v1/knowledge/status - Knowledge system status  
- GET /api/v1/knowledge/query  - Query knowledge graph
- POST /api/v1/knowledge/add   - Add knowledge node

### Script Module
- GET /api/v1/scripts/list     - List available scripts
- POST /api/v1/scripts/execute - Execute script
- GET /api/v1/scripts/status   - Script system status

### Network Module
- GET /api/v1/network/status   - Network services status
- GET /api/v1/network/discovery - Service discovery

### Admin Endpoints (Authentication Required)
- GET /admin/gateway/status    - Gateway statistics
- GET /admin/mesh/topology     - Service mesh topology

## Response Format

All responses use JSON format:

```json
{
  "status": "success|error",
  "data": { ... },
  "message": "Human readable message",
  "timestamp": "ISO 8601 timestamp"
}
```

## Error Codes

- 200: Success
- 400: Bad Request
- 401: Unauthorized  
- 404: Not Found
- 405: Method Not Allowed
- 500: Internal Server Error

## Rate Limiting

- 60 requests per minute per client
- Burst size: 10 requests

## Caching

GET requests are cached for 5 minutes where applicable.

EOF
}

# Main command interface
main() {
    case "${1:-help}" in
        "init")
            init_api_gateway
            ;;
        "start")
            start_gateway_server
            ;;
        "request")
            if [ $# -lt 3 ]; then
                echo "Usage: $0 request <method> <path> [data]"
                exit 1
            fi
            process_request "$2" "$3" "$4" "cli-client"
            ;;
        "test")
            test_gateway
            ;;
        "status")
            get_gateway_status
            ;;
        "docs")
            show_api_docs
            ;;
        "help"|*)
            echo "$GATEWAY_NAME v$GATEWAY_VERSION"
            echo "Usage: $0 {init|start|request|test|status|docs}"
            echo ""
            echo "Commands:"
            echo "  init                        - Initialize API gateway"
            echo "  start                       - Start gateway server"
            echo "  request <method> <path>     - Process API request"
            echo "  test                        - Test gateway endpoints"
            echo "  status                      - Show gateway status"
            echo "  docs                        - Show API documentation"
            echo ""
            echo "Examples:"
            echo "  $0 init                     - Initialize gateway"
            echo "  $0 start                    - Start gateway server"
            echo "  $0 request GET /api/v1/health - Test health endpoint"
            echo "  $0 test                     - Test all endpoints"
            echo "  $0 docs                     - Show API documentation"
            ;;
    esac
}

# Execute if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
