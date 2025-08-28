#!/bin/bash
# uCORE Dependency Management
# Universal Device Operating System
# Version: 1.0.5.2

# Dependency Management System
# ===========================

DEPENDENCY_FILE="${UDOS_CORE}/config/dependencies.json"

# Initialize dependency system
init_dependency_system() {
    local deps_dir="$(dirname "$DEPENDENCY_FILE")"
    
    mkdir -p "$deps_dir"
    
    if [[ ! -f "$DEPENDENCY_FILE" ]]; then
        echo '{
    "system_dependencies": {
        "required": ["bash", "jq", "curl"],
        "optional": ["git", "python3", "node"]
    },
    "module_dependencies": {},
    "dependency_graph": {},
    "metadata": {
        "version": "1.0.5.2",
        "created": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
    }
}' > "$DEPENDENCY_FILE"
    fi
    
    return 0
}

# Add module dependency
add_module_dependency() {
    local module_name="$1"
    local dependency="$2"
    local version_constraint="${3:-*}"
    
    local temp_file="${DEPENDENCY_FILE}.tmp"
    
    jq --arg module "$module_name" \
       --arg dep "$dependency" \
       --arg version "$version_constraint" \
       '.module_dependencies[$module] = (.module_dependencies[$module] // {}) | 
        .module_dependencies[$module][$dep] = $version' \
       "$DEPENDENCY_FILE" > "$temp_file"
    
    mv "$temp_file" "$DEPENDENCY_FILE"
    
    log_info "DEPS" "Added dependency $dependency ($version_constraint) for module $module_name"
}

# Check system dependencies
check_system_dependencies() {
    local missing_deps=()
    local optional_missing=()
    
    # Check required dependencies
    local required_deps=($(jq -r '.system_dependencies.required[]' "$DEPENDENCY_FILE" 2>/dev/null || echo "bash jq curl"))
    
    for dep in "${required_deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            missing_deps+=("$dep")
        fi
    done
    
    # Check optional dependencies
    local optional_deps=($(jq -r '.system_dependencies.optional[]' "$DEPENDENCY_FILE" 2>/dev/null || echo "git python3 node"))
    
    for dep in "${optional_deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            optional_missing+=("$dep")
        fi
    done
    
    # Report results
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "DEPS" "Missing required dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    if [[ ${#optional_missing[@]} -gt 0 ]]; then
        log_warn "DEPS" "Missing optional dependencies: ${optional_missing[*]}"
    fi
    
    log_info "DEPS" "All required system dependencies satisfied"
    return 0
}

# Check module dependencies
check_module_dependencies() {
    local module_name="$1"
    
    if [[ ! -f "$DEPENDENCY_FILE" ]]; then
        log_warn "DEPS" "Dependency file not found, skipping dependency check"
        return 0
    fi
    
    # Get module dependencies
    local deps=$(jq -r --arg module "$module_name" '.module_dependencies[$module] // {} | keys[]' "$DEPENDENCY_FILE" 2>/dev/null)
    
    if [[ -z "$deps" ]]; then
        log_debug "DEPS" "No dependencies defined for module $module_name"
        return 0
    fi
    
    local missing_deps=()
    
    for dep in $deps; do
        if ! is_module_registered "$dep"; then
            missing_deps+=("$dep")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "DEPS" "Module $module_name missing dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    log_info "DEPS" "All dependencies satisfied for module $module_name"
    return 0
}

# Resolve dependency order
resolve_dependency_order() {
    local modules=("$@")
    local resolved=()
    local resolving=()
    
    resolve_module() {
        local module="$1"
        
        # Check for circular dependency
        if [[ " ${resolving[*]} " =~ " ${module} " ]]; then
            log_error "DEPS" "Circular dependency detected: ${resolving[*]} -> $module"
            return 1
        fi
        
        # Skip if already resolved
        if [[ " ${resolved[*]} " =~ " ${module} " ]]; then
            return 0
        fi
        
        resolving+=("$module")
        
        # Get module dependencies
        local deps=$(jq -r --arg module "$module" '.module_dependencies[$module] // {} | keys[]' "$DEPENDENCY_FILE" 2>/dev/null)
        
        # Resolve dependencies first
        for dep in $deps; do
            resolve_module "$dep"
        done
        
        # Remove from resolving and add to resolved
        resolving=("${resolving[@]/$module}")
        resolved+=("$module")
    }
    
    # Resolve all modules
    for module in "${modules[@]}"; do
        resolve_module "$module"
    done
    
    # Output resolved order
    printf '%s\n' "${resolved[@]}"
}

# Install system dependency
install_system_dependency() {
    local dep="$1"
    local force="${2:-false}"
    
    # Check if already available
    if command -v "$dep" >/dev/null 2>&1 && [[ "$force" != "true" ]]; then
        log_info "DEPS" "Dependency $dep already available"
        return 0
    fi
    
    log_info "DEPS" "Installing system dependency: $dep"
    
    # Detect package manager and install
    if command -v brew >/dev/null 2>&1; then
        brew install "$dep"
    elif command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update && sudo apt-get install -y "$dep"
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y "$dep"
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -S --noconfirm "$dep"
    else
        log_error "DEPS" "No supported package manager found"
        return 1
    fi
    
    # Verify installation
    if command -v "$dep" >/dev/null 2>&1; then
        log_info "DEPS" "Successfully installed $dep"
        return 0
    else
        log_error "DEPS" "Failed to install $dep"
        return 1
    fi
}

# Generate dependency graph
generate_dependency_graph() {
    local output_file="${1:-/tmp/udos-dependency-graph.dot}"
    
    echo "digraph udos_dependencies {" > "$output_file"
    echo "  rankdir=LR;" >> "$output_file"
    echo "  node [shape=box];" >> "$output_file"
    echo "" >> "$output_file"
    
    # Add modules and their dependencies
    jq -r '.module_dependencies | to_entries[] | "\(.key) -> \(.value | keys[])"' "$DEPENDENCY_FILE" >> "$output_file"
    
    echo "}" >> "$output_file"
    
    log_info "DEPS" "Dependency graph generated: $output_file"
    
    # Generate PNG if graphviz is available
    if command -v dot >/dev/null 2>&1; then
        dot -Tpng "$output_file" -o "${output_file%.dot}.png"
        log_info "DEPS" "Dependency graph image: ${output_file%.dot}.png"
    fi
}

# List all dependencies
list_dependencies() {
    local module_name="${1:-}"
    
    if [[ -n "$module_name" ]]; then
        echo "Dependencies for module: $module_name"
        echo "=================================="
        jq -r --arg module "$module_name" '.module_dependencies[$module] // {} | to_entries[] | "\(.key): \(.value)"' "$DEPENDENCY_FILE"
    else
        echo "All module dependencies:"
        echo "======================="
        jq -r '.module_dependencies | to_entries[] | "\(.key):"' "$DEPENDENCY_FILE"
        jq -r '.module_dependencies | to_entries[] | "  \(.value | to_entries[] | "  \(.key): \(.value)")"' "$DEPENDENCY_FILE"
    fi
}

# Export functions
export -f init_dependency_system add_module_dependency check_system_dependencies
export -f check_module_dependencies resolve_dependency_order install_system_dependency
export -f generate_dependency_graph list_dependencies
