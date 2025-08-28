#!/bin/bash
# Network Data Integration v1.0.5.4
# Connects network services with uMEMORY and uKNOWLEDGE

# Source required systems
source "$UDOS_ROOT/uMEMORY/umemory-core.sh"
source "$UDOS_ROOT/uKNOWLEDGE/uknowledge-core.sh"

# Store network service data
store_service_data() {
    local service_name="$1"
    local service_data="$2"
    
    echo "📊 Storing network service data: $service_name"
    
    # Store in uMEMORY
    local service_object="{
        \"name\": \"$service_name\",
        \"type\": \"network_service\",
        \"data\": $service_data,
        \"created_at\": \"$(date '+%Y-%m-%d %H:%M:%S')\"
    }"
    
    create_object "$service_name" "$service_object"
    
    # Create knowledge relationships
    create_node "$service_name" "network_service" "$service_object"
    
    echo "✅ Service data stored and indexed"
}

# Retrieve service network data
get_service_data() {
    local service_name="$1"
    
    echo "📥 Retrieving network service data: $service_name"
    read_object "$service_name"
}

# Create service relationships
link_services() {
    local service_a="$1"
    local service_b="$2"
    local relationship="$3"
    
    echo "🔗 Creating service relationship: $service_a -> $service_b ($relationship)"
    create_edge "${service_a}_${relationship}_${service_b}" "$service_a" "$service_b" "$relationship"
}

# Get connected services
get_connected_services() {
    local service_name="$1"
    
    echo "🌐 Finding services connected to: $service_name"
    get_connected_nodes "$service_name"
}
