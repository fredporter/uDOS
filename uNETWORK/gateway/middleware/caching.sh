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
