#!/bin/bash
# uCORE-uMEMORY-uKNOWLEDGE Integration Layer - Bash 3.x Compatible
# Universal Device Operating System
# Version: 1.0.5.3

# Integration layer provides unified data operations across modules
# Fully compatible with bash 3.x

# Set up integration environment
INTEGRATION_ROOT="${UDOS_CORE}/code/integration"
INTEGRATION_CACHE="${UDOS_CORE}/cache/integration"

# Source required modules
source "${UDOS_ROOT}/uMEMORY/umemory-core.sh"
source "${UDOS_ROOT}/uKNOWLEDGE/uknowledge-core.sh"

# Initialize integration layer
init_integration() {
    echo "🔗 Initializing uCORE-uMEMORY-uKNOWLEDGE Integration..."
    
    # Create integration directories
    mkdir -p "$INTEGRATION_ROOT" "$INTEGRATION_CACHE"
    
    # Initialize uMEMORY
    init_umemory
    
    # Initialize uKNOWLEDGE
    init_uknowledge
    
    # Register integration modules
    register_integration_modules
    
    echo "✅ Integration layer initialization complete"
    return 0
}

# Register integration modules with uCORE
register_integration_modules() {
    # Source the service registry functions
    source "${UDOS_CORE}/code/service-registry.sh"
    
    # Register uMEMORY module
    if command -v register_module >/dev/null 2>&1; then
        register_module "uMEMORY" "1.0.5.3" "${UDOS_ROOT}/uMEMORY"
    fi
    
    # Register uKNOWLEDGE module
    if command -v register_module >/dev/null 2>&1; then
        register_module "uKNOWLEDGE" "1.0.5.3" "${UDOS_ROOT}/uKNOWLEDGE"
    fi
    
    echo "Integration modules registered with uCORE"
}

# Unified data operations
# ======================

# Store data with automatic knowledge graph creation
store_data_with_knowledge() {
    local data_id="$1"
    local data_type="$2"
    local data_content="$3"
    local create_knowledge="${4:-true}"
    local metadata="${5:-{}}"
    
    if [[ -z "$data_id" || -z "$data_type" || -z "$data_content" ]]; then
        echo "ERROR: Missing required parameters for store_data_with_knowledge"
        return 1
    fi
    
    echo "Storing data: $data_id ($data_type)"
    
    # Store in uMEMORY
    if create_object "$data_id" "$data_type" "$data_content" "$metadata"; then
        echo "✅ Data stored in uMEMORY"
    else
        echo "❌ Failed to store data in uMEMORY"
        return 1
    fi
    
    # Create knowledge graph node if requested
    if [[ "$create_knowledge" == "true" ]]; then
        local node_properties="{\"data_id\": \"$data_id\", \"data_type\": \"$data_type\"}"
        
        if create_node "$data_id" "$data_type" "default" "$node_properties"; then
            echo "✅ Knowledge node created"
        else
            echo "⚠️ Failed to create knowledge node (data still stored)"
        fi
    fi
    
    return 0
}

# Retrieve data with knowledge context
retrieve_data_with_context() {
    local data_id="$1"
    local include_context="${2:-true}"
    
    if [[ -z "$data_id" ]]; then
        echo "ERROR: Data ID required"
        return 1
    fi
    
    echo "Retrieving data: $data_id"
    
    # Get data from uMEMORY
    local data_content
    data_content="$(read_object "$data_id")"
    
    if [[ $? -ne 0 ]]; then
        echo "❌ Data not found in uMEMORY"
        return 1
    fi
    
    echo "✅ Data retrieved from uMEMORY"
    echo "$data_content"
    
    # Get knowledge context if requested
    if [[ "$include_context" == "true" ]] && node_exists "$data_id"; then
        echo ""
        echo "📊 Knowledge Context:"
        echo "===================="
        
        # Get connected nodes
        local connected_nodes
        connected_nodes="$(get_connected_nodes "$data_id" "both")"
        
        if [[ -n "$connected_nodes" ]]; then
            echo "Connected entities:"
            echo "$connected_nodes" | while read -r node; do
                if [[ -n "$node" ]]; then
                    echo "  - $node"
                fi
            done
        else
            echo "No connected entities found"
        fi
    fi
    
    return 0
}

# Create relationship between data entities
create_data_relationship() {
    local from_id="$1"
    local to_id="$2"
    local relationship="$3"
    local properties="${4:-{}}"
    
    if [[ -z "$from_id" || -z "$to_id" || -z "$relationship" ]]; then
        echo "ERROR: From ID, To ID, and relationship required"
        return 1
    fi
    
    # Check if both entities exist in uMEMORY
    if ! object_exists "$from_id"; then
        echo "ERROR: Source entity $from_id not found in uMEMORY"
        return 1
    fi
    
    if ! object_exists "$to_id"; then
        echo "ERROR: Target entity $to_id not found in uMEMORY"
        return 1
    fi
    
    # Create edge in knowledge graph
    local edge_id="${from_id}_${relationship}_${to_id}"
    
    if create_edge "$edge_id" "$from_id" "$to_id" "$relationship" "default" "$properties"; then
        echo "✅ Relationship created: $from_id -[$relationship]-> $to_id"
        return 0
    else
        echo "❌ Failed to create relationship"
        return 1
    fi
}

# Search data by type and properties
search_data() {
    local search_type="$1"
    local search_term="${2:-}"
    
    case "$search_type" in
        "by_type")
            if [[ -z "$search_term" ]]; then
                echo "ERROR: Object type required for by_type search"
                return 1
            fi
            echo "🔍 Searching for objects of type: $search_term"
            list_objects_by_type "$search_term"
            ;;
        "by_label")
            if [[ -z "$search_term" ]]; then
                echo "ERROR: Label required for by_label search"
                return 1
            fi
            echo "🔍 Searching for nodes with label: $search_term"
            find_nodes_by_label "$search_term"
            ;;
        "by_relationship")
            if [[ -z "$search_term" ]]; then
                echo "ERROR: Relationship required for by_relationship search"
                return 1
            fi
            echo "🔍 Searching for edges with relationship: $search_term"
            find_edges_by_relationship "$search_term"
            ;;
        "all_objects")
            echo "🔍 Listing all stored objects:"
            list_all_objects
            ;;
        *)
            echo "ERROR: Invalid search type. Use: by_type, by_label, by_relationship, all_objects"
            return 1
            ;;
    esac
}

# Get entity network (connected entities up to N degrees)
get_entity_network() {
    local entity_id="$1"
    local max_depth="${2:-2}"
    local current_depth="${3:-0}"
    local visited_file="${4:-}"
    
    if [[ -z "$entity_id" ]]; then
        echo "ERROR: Entity ID required"
        return 1
    fi
    
    # Create temporary file for visited nodes if not provided
    if [[ -z "$visited_file" ]]; then
        visited_file="/tmp/udos_visited_$$"
        echo "$entity_id" > "$visited_file"
    fi
    
    echo "Entity: $entity_id (depth: $current_depth)"
    
    # Stop if max depth reached
    if [[ $current_depth -ge $max_depth ]]; then
        if [[ $current_depth -eq 0 ]]; then
            rm -f "$visited_file"
        fi
        return 0
    fi
    
    # Get connected nodes
    local connected_nodes
    connected_nodes="$(get_connected_nodes "$entity_id" "both")"
    
    if [[ -n "$connected_nodes" ]]; then
        echo "$connected_nodes" | while read -r node; do
            if [[ -n "$node" ]] && ! grep -q "^${node}$" "$visited_file" 2>/dev/null; then
                echo "$node" >> "$visited_file"
                echo "  └─ Connected: $node"
                
                # Recurse for deeper connections
                if [[ $current_depth -lt $((max_depth - 1)) ]]; then
                    local sub_connected
                    sub_connected="$(get_connected_nodes "$node" "both")"
                    if [[ -n "$sub_connected" ]]; then
                        echo "$sub_connected" | while read -r sub_node; do
                            if [[ -n "$sub_node" ]] && ! grep -q "^${sub_node}$" "$visited_file" 2>/dev/null; then
                                echo "    └─ $sub_node"
                            fi
                        done
                    fi
                fi
            fi
        done
    fi
    
    # Clean up temp file if we created it
    if [[ $current_depth -eq 0 ]]; then
        rm -f "$visited_file"
    fi
}

# Integration statistics
integration_stats() {
    echo "🔗 Integration Layer Statistics"
    echo "==============================="
    
    echo ""
    echo "📊 uMEMORY Status:"
    memory_stats
    
    echo ""
    echo "🧠 uKNOWLEDGE Status:"
    knowledge_stats
    
    echo ""
    echo "🔗 Integration Status:"
    echo "Cache Directory: $INTEGRATION_CACHE"
    
    # Count synchronized entities (entities present in both uMEMORY and uKNOWLEDGE)
    local sync_count=0
    if [[ -f "${UMEMORY_DATA}/indexes/main.idx" ]] && [[ -f "${UKNOWLEDGE_DATA}/node_index.txt" ]]; then
        # This is a basic implementation - could be enhanced
        local memory_objects
        memory_objects="$(grep -v "^#" "${UMEMORY_DATA}/indexes/main.idx" | cut -d'|' -f1)"
        
        if [[ -n "$memory_objects" ]]; then
            echo "$memory_objects" | while read -r obj_id; do
                if [[ -n "$obj_id" ]] && node_exists "$obj_id"; then
                    sync_count=$((sync_count + 1))
                fi
            done
        fi
    fi
    
    echo "Synchronized Entities: $sync_count"
}

# Test integration functionality
test_integration() {
    echo "🧪 Testing Integration Layer..."
    echo "=============================="
    
    local test_failures=0
    
    # Test 1: Store data with knowledge
    echo "Test 1: Store data with knowledge creation"
    local test_data='{"name": "test_entity", "value": 42}'
    if store_data_with_knowledge "test_001" "test_object" "$test_data" "true" "{}"; then
        echo "✅ Test 1 passed"
    else
        echo "❌ Test 1 failed"
        test_failures=$((test_failures + 1))
    fi
    
    # Test 2: Retrieve data with context
    echo ""
    echo "Test 2: Retrieve data with context"
    if retrieve_data_with_context "test_001" "true" >/dev/null; then
        echo "✅ Test 2 passed"
    else
        echo "❌ Test 2 failed"
        test_failures=$((test_failures + 1))
    fi
    
    # Test 3: Create second entity and relationship
    echo ""
    echo "Test 3: Create relationship between entities"
    local test_data2='{"name": "related_entity", "value": 24}'
    store_data_with_knowledge "test_002" "test_object" "$test_data2" "true" "{}" >/dev/null
    
    if create_data_relationship "test_001" "test_002" "related_to" "{}"; then
        echo "✅ Test 3 passed"
    else
        echo "❌ Test 3 failed"
        test_failures=$((test_failures + 1))
    fi
    
    # Test 4: Search functionality
    echo ""
    echo "Test 4: Search functionality"
    if search_data "by_type" "test_object" >/dev/null; then
        echo "✅ Test 4 passed"
    else
        echo "❌ Test 4 failed"
        test_failures=$((test_failures + 1))
    fi
    
    # Cleanup test data
    echo ""
    echo "Cleaning up test data..."
    delete_object "test_001" >/dev/null 2>&1
    delete_object "test_002" >/dev/null 2>&1
    rm -f "${UKNOWLEDGE_NODES}/test_001.json" 2>/dev/null
    rm -f "${UKNOWLEDGE_NODES}/test_002.json" 2>/dev/null
    rm -f "${UKNOWLEDGE_EDGES}/test_001_related_to_test_002.json" 2>/dev/null
    
    # Summary
    echo ""
    if [[ $test_failures -eq 0 ]]; then
        echo "✅ All integration tests passed!"
        return 0
    else
        echo "❌ $test_failures integration tests failed"
        return 1
    fi
}

# Export functions
export -f init_integration store_data_with_knowledge retrieve_data_with_context
export -f create_data_relationship search_data get_entity_network
export -f integration_stats test_integration
