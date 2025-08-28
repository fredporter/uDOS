#!/bin/bash
# uDOS Advanced Variable Resolver v1.0.5
# Dynamic variable resolution with caching, scoping, and advanced types

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Core components
VARIABLE_MANAGER="$UDOS_ROOT/uCORE/code/variable-manager.sh"
VARIABLE_CACHE_DIR="$UDOS_ROOT/sandbox/cache/variables"
VARIABLE_SCOPES_DIR="$UDOS_ROOT/uMEMORY/system/variable-scopes"

# Create required directories
mkdir -p "$VARIABLE_CACHE_DIR" "$VARIABLE_SCOPES_DIR"

# Source logging
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# ════════════════════════════════════════════════════════════════
# 🎯 VARIABLE SCOPING SYSTEM
# ════════════════════════════════════════════════════════════════

# Variable scope hierarchy: GLOBAL -> SYSTEM -> USER -> SESSION -> LOCAL
declare -A VARIABLE_SCOPES=(
    ["GLOBAL"]="1"
    ["SYSTEM"]="2" 
    ["USER"]="3"
    ["SESSION"]="4"
    ["LOCAL"]="5"
)

# Get variable scope priority
get_scope_priority() {
    local scope="$1"
    echo "${VARIABLE_SCOPES[$scope]:-999}"
}

# Resolve variable with scope hierarchy
resolve_variable_with_scope() {
    local var_name="$1"
    local current_scope="${2:-SESSION}"
    local cache_key="${var_name}_${current_scope}_$(date +%s%N | cut -c1-13)"
    
    # Check cache first
    local cached_value
    if cached_value=$(get_cached_variable "$var_name" "$current_scope"); then
        echo "$cached_value"
        return 0
    fi
    
    # Search through scope hierarchy
    local scopes=("LOCAL" "SESSION" "USER" "SYSTEM" "GLOBAL")
    local value=""
    
    for scope in "${scopes[@]}"; do
        # Skip scopes lower than current scope
        if [[ $(get_scope_priority "$scope") -lt $(get_scope_priority "$current_scope") ]]; then
            continue
        fi
        
        value=$(get_variable_from_scope "$var_name" "$scope")
        if [[ -n "$value" ]]; then
            # Cache the resolved value
            cache_variable "$var_name" "$current_scope" "$value"
            echo "$value"
            return 0
        fi
    done
    
    # Variable not found in any scope
    return 1
}

# Get variable from specific scope
get_variable_from_scope() {
    local var_name="$1"
    local scope="$2"
    local scope_file="$VARIABLE_SCOPES_DIR/${scope,,}.json"
    
    if [[ -f "$scope_file" ]]; then
        jq -r ".variables[\"$var_name\"] // empty" "$scope_file" 2>/dev/null || echo ""
    fi
}

# Set variable in specific scope
set_variable_in_scope() {
    local var_name="$1"
    local value="$2"
    local scope="${3:-SESSION}"
    local scope_file="$VARIABLE_SCOPES_DIR/${scope,,}.json"
    
    # Create scope file if it doesn't exist
    if [[ ! -f "$scope_file" ]]; then
        echo '{"variables": {}, "metadata": {"created": "'$(date -Iseconds)'", "scope": "'$scope'"}}' > "$scope_file"
    fi
    
    # Update variable
    local temp_file=$(mktemp)
    jq ".variables[\"$var_name\"] = \"$value\" | .metadata.updated = \"$(date -Iseconds)\"" "$scope_file" > "$temp_file"
    mv "$temp_file" "$scope_file"
    
    # Invalidate cache
    invalidate_variable_cache "$var_name"
}

# ════════════════════════════════════════════════════════════════
# 🚀 VARIABLE CACHING SYSTEM
# ════════════════════════════════════════════════════════════════

# Cache variable value
cache_variable() {
    local var_name="$1"
    local scope="$2"
    local value="$3"
    local cache_file="$VARIABLE_CACHE_DIR/${var_name}_${scope}.cache"
    local timestamp=$(date +%s)
    
    echo "{\"value\": \"$value\", \"timestamp\": $timestamp, \"scope\": \"$scope\"}" > "$cache_file"
}

# Get cached variable
get_cached_variable() {
    local var_name="$1"
    local scope="$2"
    local cache_file="$VARIABLE_CACHE_DIR/${var_name}_${scope}.cache"
    local max_age="${UDOS_CACHE_TTL:-300}"  # 5 minutes default
    
    if [[ -f "$cache_file" ]]; then
        local cache_timestamp=$(jq -r '.timestamp' "$cache_file" 2>/dev/null || echo "0")
        local current_timestamp=$(date +%s)
        local age=$((current_timestamp - cache_timestamp))
        
        if [[ $age -lt $max_age ]]; then
            jq -r '.value' "$cache_file" 2>/dev/null
            return 0
        fi
    fi
    
    return 1
}

# Invalidate variable cache
invalidate_variable_cache() {
    local var_name="$1"
    rm -f "$VARIABLE_CACHE_DIR/${var_name}_"*.cache 2>/dev/null || true
}

# Clear all variable cache
clear_variable_cache() {
    rm -f "$VARIABLE_CACHE_DIR"/*.cache 2>/dev/null || true
    log_info "Variable cache cleared"
}

# ════════════════════════════════════════════════════════════════
# 🧠 DYNAMIC VARIABLE COMPUTATION
# ════════════════════════════════════════════════════════════════

# Compute dynamic variables
compute_dynamic_variable() {
    local var_name="$1"
    local context="${2:-default}"
    
    case "$var_name" in
        "TIMESTAMP")
            date -Iseconds
            ;;
        "TIMESTAMP-SHORT")
            date "+%Y-%m-%d %H:%M:%S"
            ;;
        "USER-ROLE")
            # Check environment variables first (from authentication)
            if [[ -n "$UDOS_AUTH_ROLE" ]]; then
                echo "$UDOS_AUTH_ROLE"
            elif [[ -f "$UDOS_ROOT/sandbox/user.md" ]]; then
                grep "^Role:" "$UDOS_ROOT/sandbox/user.md" 2>/dev/null | cut -d' ' -f2 || echo "GHOST"
            else
                echo "GHOST"
            fi
            ;;
        "USER-LEVEL")
            # Check environment variables first (from authentication)
            if [[ -n "$UDOS_AUTH_LEVEL" ]]; then
                echo "$UDOS_AUTH_LEVEL"
            elif [[ -f "$UDOS_ROOT/sandbox/user.md" ]]; then
                grep "^Level:" "$UDOS_ROOT/sandbox/user.md" 2>/dev/null | cut -d' ' -f2 || echo "0"
            else
                echo "0"
            fi
            ;;
        "USER-NAME")
            # Check environment variables first (from authentication)
            if [[ -n "$UDOS_AUTH_USER" ]]; then
                echo "$UDOS_AUTH_USER"
            elif [[ -f "$UDOS_ROOT/sandbox/user.md" ]]; then
                grep "^Username:" "$UDOS_ROOT/sandbox/user.md" 2>/dev/null | cut -d' ' -f2 || echo "anonymous"
            else
                echo "anonymous"
            fi
            ;;
        "SYSTEM-STATUS")
            # Compute current system health
            local issues=0
            for dir in "uCORE" "uMEMORY" "sandbox"; do
                [[ ! -d "$UDOS_ROOT/$dir" ]] && ((issues++))
            done
            [[ $issues -eq 0 ]] && echo "healthy" || echo "degraded"
            ;;
        "DEPENDENCY-STATUS")
            # Check critical dependencies
            local deps=("bash" "jq" "python3")
            local missing=0
            for dep in "${deps[@]}"; do
                command -v "$dep" >/dev/null || ((missing++))
            done
            [[ $missing -eq 0 ]] && echo "satisfied" || echo "missing-$missing"
            ;;
        "TEMPLATE-COUNT")
            find "$UDOS_ROOT/uMEMORY/system/templates" -name "*.md" 2>/dev/null | wc -l
            ;;
        "SESSION-ID")
            # Generate or retrieve session ID
            local session_file="$UDOS_ROOT/sandbox/session/current.id"
            if [[ -f "$session_file" ]]; then
                cat "$session_file"
            else
                local session_id="session-$(date +%Y%m%d-%H%M%S)-$$"
                mkdir -p "$(dirname "$session_file")"
                echo "$session_id" > "$session_file"
                echo "$session_id"
            fi
            ;;
        "WORKSPACE-PATH")
            echo "$UDOS_ROOT"
            ;;
        "UDOS-VERSION")
            if [[ -f "$UDOS_ROOT/VERSION" ]]; then
                cat "$UDOS_ROOT/VERSION"
            else
                echo "1.0.5-dev"
            fi
            ;;
        *)
            return 1
            ;;
    esac
}

# ════════════════════════════════════════════════════════════════
# 🎨 VARIABLE FORMATTING FUNCTIONS
# ════════════════════════════════════════════════════════════════

# Apply formatting to variable values
format_variable_value() {
    local value="$1"
    local format="${2:-raw}"
    
    case "$format" in
        "upper"|"uppercase")
            echo "${value^^}"
            ;;
        "lower"|"lowercase")
            echo "${value,,}"
            ;;
        "title"|"titlecase")
            echo "${value^}"
            ;;
        "truncate:"*)
            local length="${format#truncate:}"
            echo "${value:0:$length}$([ ${#value} -gt $length ] && echo '...')"
            ;;
        "pad:"*)
            local width="${format#pad:}"
            printf "%-${width}s" "$value"
            ;;
        "number")
            if [[ "$value" =~ ^[0-9]+$ ]]; then
                printf "%'d" "$value"  # Add thousands separator
            else
                echo "$value"
            fi
            ;;
        "boolean")
            case "${value,,}" in
                "true"|"1"|"yes"|"on"|"healthy"|"satisfied"|"available"|"active") echo "✅" ;;
                "false"|"0"|"no"|"off"|"unhealthy"|"missing"|"degraded"|"inactive") echo "❌" ;;
                *) echo "➖" ;;
            esac
            ;;
        "raw"|*)
            echo "$value"
            ;;
    esac
}

# ════════════════════════════════════════════════════════════════
# 🔧 MAIN RESOLUTION INTERFACE
# ════════════════════════════════════════════════════════════════

# Main variable resolution function
resolve_advanced_variable() {
    local var_spec="$1"
    local context="${2:-default}"
    local scope="${3:-SESSION}"
    
    # Parse variable specification: VARIABLE:format
    local var_name format
    if [[ "$var_spec" =~ ^([^:]+):(.+)$ ]]; then
        var_name="${BASH_REMATCH[1]}"
        format="${BASH_REMATCH[2]}"
    else
        var_name="$var_spec"
        format="raw"
    fi
    
    local value=""
    
    # Try dynamic computation first
    if value=$(compute_dynamic_variable "$var_name" "$context"); then
        format_variable_value "$value" "$format"
        return 0
    fi
    
    # Try scoped resolution
    if value=$(resolve_variable_with_scope "$var_name" "$scope"); then
        format_variable_value "$value" "$format"
        return 0
    fi
    
    # Fallback to variable manager
    if [[ -f "$VARIABLE_MANAGER" ]] && value=$("$VARIABLE_MANAGER" GET "$var_name" 2>/dev/null); then
        if [[ -n "$value" && "$value" != "Variable not found" ]]; then
            format_variable_value "$value" "$format"
            return 0
        fi
    fi
    
    # Variable not found
    return 1
}

# ════════════════════════════════════════════════════════════════
# 🎪 COMMAND LINE INTERFACE
# ════════════════════════════════════════════════════════════════

show_help() {
    echo "🧠 uDOS Advanced Variable Resolver v1.0.5"
    echo ""
    echo "Usage: $0 COMMAND [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  resolve VAR [CONTEXT] [SCOPE]  - Resolve variable with advanced features"
    echo "  set VAR VALUE [SCOPE]          - Set variable in specific scope"
    echo "  get VAR [SCOPE]                - Get variable from specific scope"
    echo "  cache-clear                    - Clear variable cache"
    echo "  cache-status                   - Show cache statistics"
    echo "  scopes                         - List available scopes"
    echo "  test                           - Test variable resolution"
    echo ""
    echo "Variable Formats:"
    echo "  VAR:upper                      - Uppercase value"
    echo "  VAR:lower                      - Lowercase value" 
    echo "  VAR:title                      - Title case value"
    echo "  VAR:truncate:N                 - Truncate to N characters"
    echo "  VAR:pad:N                      - Pad to N characters"
    echo "  VAR:number                     - Format as number"
    echo "  VAR:boolean                    - Format as boolean icon"
    echo ""
    echo "Dynamic Variables:"
    echo "  TIMESTAMP, USER-ROLE, USER-LEVEL, SYSTEM-STATUS"
    echo "  DEPENDENCY-STATUS, TEMPLATE-COUNT, SESSION-ID"
    echo "  WORKSPACE-PATH, UDOS-VERSION"
    echo ""
    echo "Scopes (priority order):"
    echo "  LOCAL > SESSION > USER > SYSTEM > GLOBAL"
}

# Main execution
main() {
    case "${1:-help}" in
        "resolve")
            resolve_advanced_variable "${2:-}" "${3:-default}" "${4:-SESSION}"
            ;;
        "set")
            set_variable_in_scope "${2:-}" "${3:-}" "${4:-SESSION}"
            ;;
        "get")
            get_variable_from_scope "${2:-}" "${3:-SESSION}"
            ;;
        "cache-clear")
            clear_variable_cache
            ;;
        "cache-status")
            echo "🗂️ Variable Cache Status:"
            echo "Cache directory: $VARIABLE_CACHE_DIR"
            echo "Cached variables: $(ls -1 "$VARIABLE_CACHE_DIR"/*.cache 2>/dev/null | wc -l)"
            echo "Cache TTL: ${UDOS_CACHE_TTL:-300} seconds"
            ;;
        "scopes")
            echo "📊 Variable Scopes:"
            for scope in "${!VARIABLE_SCOPES[@]}"; do
                local priority="${VARIABLE_SCOPES[$scope]}"
                local scope_file="$VARIABLE_SCOPES_DIR/${scope,,}.json"
                local var_count=0
                if [[ -f "$scope_file" ]]; then
                    var_count=$(jq '.variables | length' "$scope_file" 2>/dev/null || echo "0")
                fi
                echo "  $priority. $scope ($var_count variables)"
            done
            ;;
        "test")
            echo "🧪 Testing Advanced Variable Resolution:"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            local test_vars=("TIMESTAMP" "USER-ROLE:upper" "SYSTEM-STATUS:boolean" "UDOS-VERSION")
            for var in "${test_vars[@]}"; do
                echo -n "  $var: "
                resolve_advanced_variable "$var" "test" || echo "❌ Failed"
            done
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
