#!/bin/bash
# uDOS Inter-Module Communication API v1.0.5.6
# Unified communication layer for all uDOS modules

# Get script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# API Configuration
API_VERSION="1.0.5.6"
API_NAME="uDOS-InterModule-API"
API_PORT="8081"
API_HOST="localhost"
API_BASE_PATH="/api/v1"

# Communication protocol settings
IPC_METHOD="http"  # http, socket, pipe
IPC_TIMEOUT=30
IPC_RETRY_COUNT=3

# Module endpoints
MODULE_ENDPOINTS=()
MODULE_ENDPOINTS[0]="uCORE:foundation:/core"
MODULE_ENDPOINTS[1]="uMEMORY:data:/memory"
MODULE_ENDPOINTS[2]="uKNOWLEDGE:graph:/knowledge"
MODULE_ENDPOINTS[3]="uNETWORK:services:/network"
MODULE_ENDPOINTS[4]="uSCRIPT:automation:/script"

# Initialize Inter-Module Communication
init_imc_api() {
    echo "🔗 Initializing $API_NAME v$API_VERSION"
    
    # Create API directories
    mkdir -p "$UDOS_ROOT/uNETWORK/api/imc"
    mkdir -p "$UDOS_ROOT/uNETWORK/api/endpoints"
    mkdir -p "$UDOS_ROOT/uNETWORK/api/middleware"
    mkdir -p "$UDOS_ROOT/uNETWORK/api/logs"
    
    # Initialize service registry for modules
    init_module_registry
    
    # Create API gateway configuration
    create_api_config
    
    # Setup middleware components
    setup_api_middleware
    
    echo "✅ Inter-Module Communication API initialized"
}

# Initialize module registry
init_module_registry() {
    local registry_file="$UDOS_ROOT/uNETWORK/api/imc/module-registry.json"
    
    cat > "$registry_file" << EOF
{
  "api_version": "$API_VERSION",
  "created": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "modules": {
    "uCORE": {
      "name": "uCORE Foundation",
      "version": "1.0.5.6",
      "endpoint": "/core",
      "methods": ["status", "init", "test", "config"],
      "health_check": "/core/health",
      "active": true
    },
    "uMEMORY": {
      "name": "uMEMORY Data Layer",
      "version": "1.0.5.6", 
      "endpoint": "/memory",
      "methods": ["create", "read", "update", "delete", "query"],
      "health_check": "/memory/health",
      "active": true
    },
    "uKNOWLEDGE": {
      "name": "uKNOWLEDGE Graph System",
      "version": "1.0.5.6",
      "endpoint": "/knowledge", 
      "methods": ["add_node", "add_edge", "query_graph", "traverse"],
      "health_check": "/knowledge/health",
      "active": true
    },
    "uNETWORK": {
      "name": "uNETWORK Services",
      "version": "1.0.5.6",
      "endpoint": "/network",
      "methods": ["service_discovery", "routing", "monitoring"],
      "health_check": "/network/health", 
      "active": true
    },
    "uSCRIPT": {
      "name": "uSCRIPT Automation",
      "version": "1.0.5.6",
      "endpoint": "/script",
      "methods": ["execute", "register", "list", "status"],
      "health_check": "/script/health",
      "active": true
    }
  },
  "communication": {
    "protocol": "$IPC_METHOD",
    "timeout": $IPC_TIMEOUT,
    "retry_count": $IPC_RETRY_COUNT,
    "base_url": "http://$API_HOST:$API_PORT$API_BASE_PATH"
  }
}
EOF

    echo "📋 Module registry initialized"
}

# Create API gateway configuration
create_api_config() {
    local config_file="$UDOS_ROOT/uNETWORK/api/imc/api-config.json"
    
    cat > "$config_file" << EOF
{
  "gateway": {
    "name": "$API_NAME",
    "version": "$API_VERSION",
    "host": "$API_HOST",
    "port": $API_PORT,
    "base_path": "$API_BASE_PATH"
  },
  "security": {
    "authentication": false,
    "rate_limiting": true,
    "cors_enabled": true,
    "allowed_origins": ["http://localhost:*"]
  },
  "routing": {
    "enable_load_balancing": false,
    "circuit_breaker": true,
    "health_check_interval": 60
  },
  "logging": {
    "level": "info",
    "format": "json",
    "log_requests": true,
    "log_responses": true
  }
}
EOF

    echo "⚙️ API gateway configuration created"
}

# Setup API middleware
setup_api_middleware() {
    # Request logger middleware
    cat > "$UDOS_ROOT/uNETWORK/api/middleware/request-logger.sh" << 'EOF'
#!/bin/bash
# Request Logger Middleware
# Logs all API requests and responses

log_request() {
    local method="$1"
    local endpoint="$2" 
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    local log_file="$UDOS_ROOT/uNETWORK/api/logs/requests.log"
    
    echo "[$timestamp] $method $endpoint" >> "$log_file"
}

log_response() {
    local status="$1"
    local endpoint="$2"
    local duration="$3"
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    local log_file="$UDOS_ROOT/uNETWORK/api/logs/responses.log"
    
    echo "[$timestamp] $status $endpoint ${duration}ms" >> "$log_file"
}
EOF

    # Health check middleware
    cat > "$UDOS_ROOT/uNETWORK/api/middleware/health-check.sh" << 'EOF'
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
EOF

    chmod +x "$UDOS_ROOT/uNETWORK/api/middleware/request-logger.sh"
    chmod +x "$UDOS_ROOT/uNETWORK/api/middleware/health-check.sh"
    
    echo "🔧 API middleware components created"
}

# Module communication functions
send_module_request() {
    local target_module="$1"
    local method="$2"
    local data="$3"
    local request_id="$(date +%s)_$$"
    
    echo "📡 Sending request to $target_module: $method"
    
    # Log the request
    source "$UDOS_ROOT/uNETWORK/api/middleware/request-logger.sh"
    log_request "$method" "/$target_module"
    
    # Route request to appropriate module handler
    local response=""
    local start_time="$(date +%s)"
    
    case "$target_module" in
        "uCORE")
            response="$(handle_core_request "$method" "$data")"
            ;;
        "uMEMORY")
            response="$(handle_memory_request "$method" "$data")"
            ;;
        "uKNOWLEDGE") 
            response="$(handle_knowledge_request "$method" "$data")"
            ;;
        "uNETWORK")
            response="$(handle_network_request "$method" "$data")"
            ;;
        "uSCRIPT")
            response="$(handle_script_request "$method" "$data")"
            ;;
        *)
            response='{"error": "Unknown module", "code": 404}'
            ;;
    esac
    
    local end_time="$(date +%s)"
    local duration=$((end_time - start_time))
    
    # Log the response
    log_response "200" "/$target_module" "$duration"
    
    echo "$response"
}

# Module request handlers
handle_core_request() {
    local method="$1"
    local data="$2"
    
    case "$method" in
        "status")
            if [ -f "$UDOS_ROOT/uCORE/code/foundation.sh" ]; then
                echo '{"status": "active", "module": "uCORE", "version": "1.0.5.6"}'
            else
                echo '{"status": "inactive", "module": "uCORE", "error": "Foundation not found"}'
            fi
            ;;
        "health")
            source "$UDOS_ROOT/uNETWORK/api/middleware/health-check.sh"
            local health="$(check_module_health "uCORE")"
            echo '{"health": "'$health'", "module": "uCORE", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}'
            ;;
        *)
            echo '{"error": "Method not supported", "method": "'$method'", "module": "uCORE"}'
            ;;
    esac
}

handle_memory_request() {
    local method="$1"
    local data="$2"
    
    case "$method" in
        "status")
            if [ -d "$UDOS_ROOT/uMEMORY" ]; then
                echo '{"status": "active", "module": "uMEMORY", "version": "1.0.5.6"}'
            else
                echo '{"status": "inactive", "module": "uMEMORY", "error": "Module not found"}'
            fi
            ;;
        "health")
            source "$UDOS_ROOT/uNETWORK/api/middleware/health-check.sh"
            local health="$(check_module_health "uMEMORY")"
            echo '{"health": "'$health'", "module": "uMEMORY", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}'
            ;;
        "query")
            echo '{"result": "memory_query_result", "module": "uMEMORY", "data": "'$data'"}'
            ;;
        *)
            echo '{"error": "Method not supported", "method": "'$method'", "module": "uMEMORY"}'
            ;;
    esac
}

handle_knowledge_request() {
    local method="$1"
    local data="$2"
    
    case "$method" in
        "status")
            if [ -d "$UDOS_ROOT/uKNOWLEDGE" ]; then
                echo '{"status": "active", "module": "uKNOWLEDGE", "version": "1.0.5.6"}'
            else
                echo '{"status": "inactive", "module": "uKNOWLEDGE", "error": "Module not found"}'
            fi
            ;;
        "health")
            source "$UDOS_ROOT/uNETWORK/api/middleware/health-check.sh"
            local health="$(check_module_health "uKNOWLEDGE")"
            echo '{"health": "'$health'", "module": "uKNOWLEDGE", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}'
            ;;
        "query_graph")
            echo '{"result": "graph_query_result", "module": "uKNOWLEDGE", "query": "'$data'"}'
            ;;
        *)
            echo '{"error": "Method not supported", "method": "'$method'", "module": "uKNOWLEDGE"}'
            ;;
    esac
}

handle_network_request() {
    local method="$1"
    local data="$2"
    
    case "$method" in
        "status")
            echo '{"status": "active", "module": "uNETWORK", "version": "1.0.5.6"}'
            ;;
        "health")
            echo '{"health": "healthy", "module": "uNETWORK", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}'
            ;;
        "service_discovery")
            echo '{"services": ["api-gateway", "health-monitor"], "module": "uNETWORK"}'
            ;;
        *)
            echo '{"error": "Method not supported", "method": "'$method'", "module": "uNETWORK"}'
            ;;
    esac
}

handle_script_request() {
    local method="$1"
    local data="$2"
    
    case "$method" in
        "status")
            if [ -f "$UDOS_ROOT/uSCRIPT/uscript" ]; then
                echo '{"status": "active", "module": "uSCRIPT", "version": "1.0.5.6"}'
            else
                echo '{"status": "inactive", "module": "uSCRIPT", "error": "Script engine not found"}'
            fi
            ;;
        "health")
            source "$UDOS_ROOT/uNETWORK/api/middleware/health-check.sh"
            local health="$(check_module_health "uSCRIPT")"
            echo '{"health": "'$health'", "module": "uSCRIPT", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}'
            ;;
        "list")
            echo '{"scripts": ["system_health_check", "auto_backup"], "module": "uSCRIPT"}'
            ;;
        *)
            echo '{"error": "Method not supported", "method": "'$method'", "module": "uSCRIPT"}'
            ;;
    esac
}

# Get overall system health
get_system_health() {
    echo "🏥 System Health Check via Inter-Module API"
    echo "=========================================="
    
    source "$UDOS_ROOT/uNETWORK/api/middleware/health-check.sh"
    get_all_module_health
}

# Test inter-module communication
test_imc_communication() {
    echo "🧪 Testing Inter-Module Communication"
    echo "===================================="
    
    local modules=("uCORE" "uMEMORY" "uKNOWLEDGE" "uNETWORK" "uSCRIPT")
    
    for module in "${modules[@]}"; do
        echo ""
        echo "📡 Testing $module module:"
        
        # Test status
        local status_response="$(send_module_request "$module" "status")"
        echo "   Status: $status_response"
        
        # Test health
        local health_response="$(send_module_request "$module" "health")" 
        echo "   Health: $health_response"
    done
    
    echo ""
    echo "✅ Inter-module communication test complete"
}

# Show API status
show_api_status() {
    echo "🔗 $API_NAME Status"
    echo "===================="
    echo "Version: $API_VERSION"
    echo "Endpoint: http://$API_HOST:$API_PORT$API_BASE_PATH"
    echo "Protocol: $IPC_METHOD"
    echo ""
    
    # Show module registry
    if [ -f "$UDOS_ROOT/uNETWORK/api/imc/module-registry.json" ]; then
        echo "📋 Registered Modules: 5"
        echo "   • uCORE (Foundation)"
        echo "   • uMEMORY (Data Layer)"
        echo "   • uKNOWLEDGE (Graph System)"
        echo "   • uNETWORK (Services)"
        echo "   • uSCRIPT (Automation)"
    else
        echo "📋 Module registry not initialized"
    fi
    
    echo ""
    echo "🔧 Middleware:"
    echo "   • Request Logger"
    echo "   • Health Checker"
    
    # Show recent logs
    echo ""
    echo "📝 Recent API Activity:"
    if [ -f "$UDOS_ROOT/uNETWORK/api/logs/requests.log" ]; then
        tail -3 "$UDOS_ROOT/uNETWORK/api/logs/requests.log" 2>/dev/null || echo "   No recent requests"
    else
        echo "   No logs yet"
    fi
}

# Main command interface
main() {
    case "${1:-help}" in
        "init")
            init_imc_api
            ;;
        "test")
            test_imc_communication
            ;;
        "health")
            get_system_health
            ;;
        "status")
            show_api_status
            ;;
        "request")
            if [ $# -lt 3 ]; then
                echo "Usage: $0 request <module> <method> [data]"
                exit 1
            fi
            send_module_request "$2" "$3" "$4"
            ;;
        "help"|*)
            echo "$API_NAME v$API_VERSION"
            echo "Usage: $0 {init|test|health|status|request}"
            echo ""
            echo "Commands:"
            echo "  init                    - Initialize inter-module API"
            echo "  test                    - Test communication with all modules"
            echo "  health                  - Get system health status"
            echo "  status                  - Show API status"
            echo "  request <mod> <method>  - Send request to specific module"
            echo ""
            echo "Examples:"
            echo "  $0 init                 - Initialize API system"
            echo "  $0 test                 - Test all module communication"
            echo "  $0 request uCORE status - Get uCORE status"
            echo "  $0 health               - System health check"
            ;;
    esac
}

# Execute if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
