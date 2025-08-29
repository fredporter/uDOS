#!/bin/bash
# uCORE Foundation Initialization v1.0.5.3 - Bash 3.x Compatible
# Universal Device Operating System
# Version: 1.0.5.3

# Bash 3.x Compatibility Notes:
# - No associative arrays (declare -A)
# - No += for string concatenation
# - Limited parameter expansion

# Set script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_CORE="$(cd "${SCRIPT_DIR}/.." && pwd)"
UDOS_ROOT="$(cd "${UDOS_CORE}/.." && pwd)"
UDOS_MEMORY="${UDOS_ROOT}/uMEMORY"
UDOS_KNOWLEDGE="${UDOS_ROOT}/uKNOWLEDGE"

# Export environment variables
export UDOS_ROOT UDOS_CORE UDOS_MEMORY UDOS_KNOWLEDGE

# Simple logging for foundation init
foundation_log() {
    local level="$1"
    local message="$2"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$timestamp] [$level] [FOUNDATION] $message"
}

# Initialize foundation systems
init_foundation() {
    foundation_log "INFO" "Initializing uDOS v1.0.5.3 Foundation..."
    echo "============================================="
    
    # Create required directories
    foundation_log "INFO" "Creating directory structure..."
    mkdir -p "${UDOS_MEMORY}/logs"
    mkdir -p "${UDOS_CORE}/cache"
    mkdir -p "${UDOS_CORE}/config"
    mkdir -p "${UDOS_KNOWLEDGE}/data"
    
    # Initialize basic registry
    foundation_log "INFO" "Initializing service registry..."
    init_basic_registry
    
    # Check basic dependencies
    foundation_log "INFO" "Checking system dependencies..."
    check_basic_dependencies
    
    # Initialize integration layer
    foundation_log "INFO" "Initializing integration layer..."
    init_integration_layer
    
    # Register all modules
    foundation_log "INFO" "Registering modules..."
    register_all_modules
    
    foundation_log "INFO" "Foundation initialization complete!"
    
    # Display status
    show_foundation_status
    
    return 0
}

# Initialize basic registry (bash 3.x compatible)
init_basic_registry() {
    local registry_file="${UDOS_CORE}/code/registry.json"
    
    if [[ ! -f "$registry_file" ]]; then
        cat > "$registry_file" << 'EOF'
{
    "modules": {},
    "services": {},
    "dependencies": {},
    "metadata": {
        "version": "1.0.5.3",
        "created": "",
        "last_updated": ""
    }
}
EOF
        # Update timestamps (bash 3.x compatible)
        local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        if command -v python >/dev/null 2>&1; then
            python -c "
import json
with open('$registry_file', 'r') as f: data = json.load(f)
data['metadata']['created'] = '$timestamp'
data['metadata']['last_updated'] = '$timestamp'
with open('$registry_file', 'w') as f: json.dump(data, f, indent=2)
"
        elif command -v sed >/dev/null 2>&1; then
            sed -i.bak "s/\"created\": \"\"/\"created\": \"$timestamp\"/" "$registry_file"
            sed -i.bak "s/\"last_updated\": \"\"/\"last_updated\": \"$timestamp\"/" "$registry_file"
            rm -f "${registry_file}.bak"
        fi
    fi
}

# Check basic system dependencies
check_basic_dependencies() {
    local missing_deps=""
    local required_deps="bash"
    
    for dep in $required_deps; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            missing_deps="$missing_deps $dep"
        fi
    done
    
    if [[ -n "$missing_deps" ]]; then
        foundation_log "ERROR" "Missing required dependencies:$missing_deps"
        return 1
    fi
    
    foundation_log "INFO" "All required system dependencies satisfied"
    return 0
}

# Initialize integration layer
init_integration_layer() {
    local integration_script="${UDOS_CORE}/code/integration/memory-knowledge-integration.sh"
    
    if [[ -f "$integration_script" ]]; then
        foundation_log "INFO" "Loading integration layer..."
        source "$integration_script"
        
        if command -v init_integration >/dev/null 2>&1; then
            init_integration
        else
            foundation_log "WARN" "Integration layer functions not available"
        fi
    else
        foundation_log "WARN" "Integration script not found: $integration_script"
    fi
}

# Register all modules
register_all_modules() {
    local registry_file="${UDOS_CORE}/code/registry.json"
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    if command -v python >/dev/null 2>&1; then
        python -c "
import json
with open('$registry_file', 'r') as f: data = json.load(f)

# Register uCORE
data['modules']['uCORE'] = {
    'version': '1.0.5.3',
    'path': '$UDOS_CORE',
    'status': 'registered',
    'registered_at': '$timestamp',
    'health': 'unknown'
}

# Register uMEMORY
data['modules']['uMEMORY'] = {
    'version': '1.0.5.3',
    'path': '$UDOS_MEMORY',
    'status': 'registered',
    'registered_at': '$timestamp',
    'health': 'unknown'
}

# Register uKNOWLEDGE
data['modules']['uKNOWLEDGE'] = {
    'version': '1.0.5.3',
    'path': '$UDOS_KNOWLEDGE',
    'status': 'registered',
    'registered_at': '$timestamp',
    'health': 'unknown'
}

data['metadata']['last_updated'] = '$timestamp'
with open('$registry_file', 'w') as f: json.dump(data, f, indent=2)
"
        foundation_log "INFO" "All modules registered successfully"
    else
        foundation_log "WARN" "Python not available, module registration may not work properly"
    fi
}

# Show foundation status
show_foundation_status() {
    echo ""
    foundation_log "INFO" "Foundation Status Report"
    echo "======================="
    
    echo ""
    echo "📁 Directory Structure:"
    echo "  UDOS_ROOT: $UDOS_ROOT"
    echo "  UDOS_CORE: $UDOS_CORE"  
    echo "  UDOS_MEMORY: $UDOS_MEMORY"
    echo "  UDOS_KNOWLEDGE: $UDOS_KNOWLEDGE"
    
    echo ""
    echo "🔧 System Dependencies:"
    if check_basic_dependencies >/dev/null 2>&1; then
        echo "  ✅ All required dependencies satisfied"
    else
        echo "  ❌ Missing dependencies detected"
    fi
    
    echo ""
    echo "📋 Registry:"
    local registry_file="${UDOS_CORE}/code/registry.json"
    if [[ -f "$registry_file" ]]; then
        echo "  ✅ Registry initialized: $registry_file"
        
        # Show registered modules
        if command -v python >/dev/null 2>&1; then
            echo "  📦 Registered modules:"
            python -c "
import json
with open('$registry_file', 'r') as f: data = json.load(f)
for module, info in data['modules'].items():
    print('    - {}: v{} ({})'.format(module, info['version'], info['status']))
" 2>/dev/null || echo "    - Module info unavailable"
        fi
    else
        echo "  ❌ Registry not found"
    fi
    
    echo ""
    echo "💾 Data Systems:"
    if [[ -d "${UDOS_MEMORY}/data" ]]; then
        echo "  ✅ uMEMORY data layer ready"
    else
        echo "  ⚠️ uMEMORY data layer not initialized"
    fi
    
    if [[ -d "${UDOS_KNOWLEDGE}/data" ]]; then
        echo "  ✅ uKNOWLEDGE graph layer ready"
    else
        echo "  ⚠️ uKNOWLEDGE graph layer not initialized"
    fi
    
    echo ""
    echo "📝 Log Directory:"
    if [[ -d "${UDOS_MEMORY}/logs" ]]; then
        echo "  ✅ Log directory ready: ${UDOS_MEMORY}/logs"
    else
        echo "  ❌ Log directory not found"
    fi
}

# Test foundation functionality
test_foundation() {
    foundation_log "INFO" "Testing Foundation Components..."
    echo "================================"
    
    local test_failures=0
    
    # Test directory creation
    echo "Testing directory structure..."
    if [[ -d "${UDOS_MEMORY}/logs" && -d "${UDOS_CORE}/cache" && -d "${UDOS_KNOWLEDGE}/data" ]]; then
        echo "✅ Directory structure test passed"
    else
        echo "❌ Directory structure test failed"
        test_failures=$((test_failures + 1))
    fi
    
    # Test registry
    echo "Testing registry..."
    local registry_file="${UDOS_CORE}/code/registry.json"
    if [[ -f "$registry_file" ]]; then
        echo "✅ Registry test passed"
    else
        echo "❌ Registry test failed"
        test_failures=$((test_failures + 1))
    fi
    
    # Test dependencies
    echo "Testing dependencies..."
    if check_basic_dependencies >/dev/null 2>&1; then
        echo "✅ Dependencies test passed"
    else
        echo "❌ Dependencies test failed"
        test_failures=$((test_failures + 1))
    fi
    
    # Test integration layer
    echo "Testing integration layer..."
    if command -v test_integration >/dev/null 2>&1; then
        if test_integration >/dev/null 2>&1; then
            echo "✅ Integration layer test passed"
        else
            echo "⚠️ Integration layer test had issues (check logs)"
        fi
    else
        echo "⚠️ Integration layer functions not available"
    fi
    
    # Summary
    echo ""
    if [[ $test_failures -eq 0 ]]; then
        foundation_log "INFO" "All foundation tests passed!"
        return 0
    else
        foundation_log "ERROR" "$test_failures tests failed"
        return 1
    fi
}

# Clean foundation (reset to initial state)
clean_foundation() {
    foundation_log "INFO" "Cleaning Foundation..."
    echo "====================="
    
    # Remove registry file
    local registry_file="${UDOS_CORE}/code/registry.json"
    if [[ -f "$registry_file" ]]; then
        rm -f "$registry_file"
        echo "✅ Registry cleaned"
    fi
    
    # Clean log files
    if [[ -d "${UDOS_MEMORY}/logs" ]]; then
        rm -rf "${UDOS_MEMORY}/logs"
        echo "✅ Logs cleaned"
    fi
    
    # Clean cache
    if [[ -d "${UDOS_CORE}/cache" ]]; then
        rm -rf "${UDOS_CORE}/cache"
        echo "✅ Cache cleaned"
    fi
    
    # Clean uMEMORY data
    if [[ -d "${UDOS_MEMORY}/data" ]]; then
        rm -rf "${UDOS_MEMORY}/data"
        echo "✅ uMEMORY data cleaned"
    fi
    
    # Clean uKNOWLEDGE data
    if [[ -d "${UDOS_KNOWLEDGE}/data" ]]; then
        rm -rf "${UDOS_KNOWLEDGE}/data"
        echo "✅ uKNOWLEDGE data cleaned"
    fi
    
    foundation_log "INFO" "Foundation cleaned successfully"
}

# Main command handler
main() {
    local command="${1:-init}"
    
    case "$command" in
        "init")
            init_foundation
            ;;
        "status")
            show_foundation_status
            ;;
        "test")
            test_foundation
            ;;
        "clean")
            clean_foundation
            ;;
        "help")
            echo "uDOS Foundation v1.0.5.3 (Bash 3.x Compatible)"
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  init     - Initialize foundation systems (default)"
            echo "  status   - Show foundation status"
            echo "  test     - Test foundation components"
            echo "  clean    - Clean foundation data"
            echo "  help     - Show this help"
            ;;
        *)
            foundation_log "ERROR" "Unknown command: $command"
            echo "Use '$0 help' for usage information"
            return 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
