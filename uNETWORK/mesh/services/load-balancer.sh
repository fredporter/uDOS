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
