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
