#!/bin/bash
# uCORE Service Registry
# Universal Device Operating System
# Version: 1.0.5.2

# Service Registry Management
# ==========================

REGISTRY_FILE="${UDOS_CORE}/code/registry.json"
REGISTRY_LOCK="${UDOS_CORE}/code/.registry.lock"

# Initialize service registry
init_service_registry() {
    local registry_dir="$(dirname "$REGISTRY_FILE")"
    
    # Create registry directory if it doesn't exist
    mkdir -p "$registry_dir"
    
    # Initialize empty registry if it doesn't exist
    if [[ ! -f "$REGISTRY_FILE" ]]; then
        echo '{
    "modules": {},
    "services": {},
    "dependencies": {},
    "metadata": {
        "version": "1.0.5.2",
        "created": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
        "last_updated": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
    }
}' > "$REGISTRY_FILE"
    fi
    
    return 0
}

# Register a module
register_module() {
    local module_name="$1"
    local module_version="$2"
    local module_path="$3"
    
    acquire_registry_lock
    
    # Create temporary file for atomic update
    local temp_file="${REGISTRY_FILE}.tmp"
    
    # Update registry with new module
    jq --arg name "$module_name" \
       --arg version "$module_version" \
       --arg path "$module_path" \
       --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
       '.modules[$name] = {
           "version": $version,
           "path": $path,
           "status": "registered",
           "registered_at": $timestamp,
           "health": "unknown"
       } | .metadata.last_updated = $timestamp' \
       "$REGISTRY_FILE" > "$temp_file"
    
    # Atomically replace registry file
    mv "$temp_file" "$REGISTRY_FILE"
    
    release_registry_lock
    
    echo "Module $module_name registered successfully"
    return 0
}

# Unregister a module
unregister_module() {
    local module_name="$1"
    
    acquire_registry_lock
    
    local temp_file="${REGISTRY_FILE}.tmp"
    
    # Remove module from registry
    jq --arg name "$module_name" \
       --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
       'del(.modules[$name]) | .metadata.last_updated = $timestamp' \
       "$REGISTRY_FILE" > "$temp_file"
    
    mv "$temp_file" "$REGISTRY_FILE"
    
    release_registry_lock
    
    echo "Module $module_name unregistered"
    return 0
}

# Check if module is registered
is_module_registered() {
    local module_name="$1"
    
    if [[ ! -f "$REGISTRY_FILE" ]]; then
        return 1
    fi
    
    jq -e --arg name "$module_name" '.modules[$name] != null' "$REGISTRY_FILE" >/dev/null
}

# Get module status
get_module_status() {
    local module_name="$1"
    
    if ! is_module_registered "$module_name"; then
        echo "unregistered"
        return 1
    fi
    
    jq -r --arg name "$module_name" '.modules[$name].status // "unknown"' "$REGISTRY_FILE"
}

# Update module status
update_module_status() {
    local module_name="$1"
    local status="$2"
    
    acquire_registry_lock
    
    local temp_file="${REGISTRY_FILE}.tmp"
    
    jq --arg name "$module_name" \
       --arg status "$status" \
       --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
       '.modules[$name].status = $status | 
        .modules[$name].last_status_update = $timestamp |
        .metadata.last_updated = $timestamp' \
       "$REGISTRY_FILE" > "$temp_file"
    
    mv "$temp_file" "$REGISTRY_FILE"
    
    release_registry_lock
    
    return 0
}

# List all registered modules
list_modules() {
    if [[ ! -f "$REGISTRY_FILE" ]]; then
        echo "No modules registered"
        return 0
    fi
    
    jq -r '.modules | to_entries[] | "\(.key): \(.value.status) (v\(.value.version))"' "$REGISTRY_FILE"
}

# Get registry stats
registry_stats() {
    if [[ ! -f "$REGISTRY_FILE" ]]; then
        echo "Registry not initialized"
        return 1
    fi
    
    echo "Registry Statistics:"
    echo "==================="
    echo "Modules: $(jq '.modules | length' "$REGISTRY_FILE")"
    echo "Services: $(jq '.services | length' "$REGISTRY_FILE")"
    echo "Last Updated: $(jq -r '.metadata.last_updated' "$REGISTRY_FILE")"
}

# Registry locking functions
acquire_registry_lock() {
    local timeout=30
    local wait_time=0
    
    while [[ -f "$REGISTRY_LOCK" ]]; do
        if [[ $wait_time -ge $timeout ]]; then
            echo "ERROR: Registry lock timeout"
            return 1
        fi
        sleep 0.1
        ((wait_time++))
    done
    
    echo $$ > "$REGISTRY_LOCK"
}

release_registry_lock() {
    rm -f "$REGISTRY_LOCK"
}

# Validate dependencies
validate_dependencies() {
    local module_name="$1"
    
    # TODO: Implement dependency validation
    # This will check module dependencies and ensure they're available
    
    return 0
}

# Initialize module resources
init_module_resources() {
    local module_name="$1"
    
    # Create module-specific directories
    local module_cache="${UDOS_CORE}/cache/${module_name}"
    local module_logs="${UDOS_MEMORY}/logs/${module_name}"
    
    mkdir -p "$module_cache" "$module_logs"
    
    return 0
}

# Export functions
export -f init_service_registry register_module unregister_module
export -f is_module_registered get_module_status update_module_status
export -f list_modules registry_stats validate_dependencies init_module_resources
