#!/bin/bash
# uKNOWLEDGE Knowledge Graph - Bash 3.x Compatible
# Universal Device Operating System
# Version: 1.0.5.3

# uKNOWLEDGE provides knowledge graph and relationship management
# Fully compatible with bash 3.x (no associative arrays)

# Set up uKNOWLEDGE environment
UKNOWLEDGE_ROOT="${UDOS_ROOT}/uKNOWLEDGE"
UKNOWLEDGE_DATA="${UKNOWLEDGE_ROOT}/data"
UKNOWLEDGE_GRAPHS="${UKNOWLEDGE_DATA}/graphs"
UKNOWLEDGE_NODES="${UKNOWLEDGE_DATA}/nodes"
UKNOWLEDGE_EDGES="${UKNOWLEDGE_DATA}/edges"
UKNOWLEDGE_SCHEMAS="${UKNOWLEDGE_ROOT}/schemas"

# Initialize uKNOWLEDGE system
init_uknowledge() {
    echo "🧠 Initializing uKNOWLEDGE v1.0.5.3..."
    
    # Create directory structure
    mkdir -p "$UKNOWLEDGE_DATA" "$UKNOWLEDGE_GRAPHS" "$UKNOWLEDGE_NODES" "$UKNOWLEDGE_EDGES" "$UKNOWLEDGE_SCHEMAS"
    
    # Initialize knowledge schemas
    init_knowledge_schemas
    
    # Create default graph
    create_default_graph
    
    # Initialize node and edge indexes
    init_knowledge_indexes
    
    echo "✅ uKNOWLEDGE initialization complete"
    return 0
}

# Initialize knowledge schemas
init_knowledge_schemas() {
    # Node schema
    cat > "${UKNOWLEDGE_SCHEMAS}/node.json" << 'EOF'
{
    "type": "node",
    "version": "1.0",
    "fields": {
        "id": {"type": "string", "required": true, "unique": true},
        "label": {"type": "string", "required": true},
        "properties": {"type": "object", "required": false},
        "graph_id": {"type": "string", "required": true},
        "created_at": {"type": "timestamp", "required": true},
        "updated_at": {"type": "timestamp", "required": true}
    }
}
EOF

    # Edge schema
    cat > "${UKNOWLEDGE_SCHEMAS}/edge.json" << 'EOF'
{
    "type": "edge",
    "version": "1.0",
    "fields": {
        "id": {"type": "string", "required": true, "unique": true},
        "from_node": {"type": "string", "required": true},
        "to_node": {"type": "string", "required": true},
        "relationship": {"type": "string", "required": true},
        "properties": {"type": "object", "required": false},
        "graph_id": {"type": "string", "required": true},
        "created_at": {"type": "timestamp", "required": true},
        "updated_at": {"type": "timestamp", "required": true}
    }
}
EOF

    # Graph schema
    cat > "${UKNOWLEDGE_SCHEMAS}/graph.json" << 'EOF'
{
    "type": "graph",
    "version": "1.0",
    "fields": {
        "id": {"type": "string", "required": true, "unique": true},
        "name": {"type": "string", "required": true},
        "description": {"type": "string", "required": false},
        "node_count": {"type": "integer", "required": true},
        "edge_count": {"type": "integer", "required": true},
        "created_at": {"type": "timestamp", "required": true},
        "updated_at": {"type": "timestamp", "required": true}
    }
}
EOF
}

# Create default graph
create_default_graph() {
    local graph_id="default"
    local graph_name="Default Knowledge Graph"
    local description="Default knowledge graph for uDOS system"
    
    create_graph "$graph_id" "$graph_name" "$description"
}

# Initialize knowledge indexes
init_knowledge_indexes() {
    # Node index
    local node_index="${UKNOWLEDGE_DATA}/node_index.txt"
    if [[ ! -f "$node_index" ]]; then
        cat > "$node_index" << 'EOF'
# uKNOWLEDGE Node Index
# Format: node_id|label|graph_id|created_at|updated_at
EOF
    fi
    
    # Edge index
    local edge_index="${UKNOWLEDGE_DATA}/edge_index.txt"
    if [[ ! -f "$edge_index" ]]; then
        cat > "$edge_index" << 'EOF'
# uKNOWLEDGE Edge Index
# Format: edge_id|from_node|to_node|relationship|graph_id|created_at|updated_at
EOF
    fi
    
    # Graph index
    local graph_index="${UKNOWLEDGE_DATA}/graph_index.txt"
    if [[ ! -f "$graph_index" ]]; then
        cat > "$graph_index" << 'EOF'
# uKNOWLEDGE Graph Index
# Format: graph_id|name|node_count|edge_count|created_at|updated_at
EOF
    fi
}

# Create graph
create_graph() {
    local graph_id="$1"
    local name="$2"
    local description="${3:-}"
    
    if [[ -z "$graph_id" || -z "$name" ]]; then
        echo "ERROR: Graph ID and name required"
        return 1
    fi
    
    local graph_file="${UKNOWLEDGE_GRAPHS}/${graph_id}.json"
    
    if [[ -f "$graph_file" ]]; then
        echo "ERROR: Graph $graph_id already exists"
        return 1
    fi
    
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    cat > "$graph_file" << EOF
{
    "id": "$graph_id",
    "name": "$name",
    "description": "$description",
    "node_count": 0,
    "edge_count": 0,
    "created_at": "$timestamp",
    "updated_at": "$timestamp"
}
EOF
    
    # Update graph index
    echo "${graph_id}|${name}|0|0|${timestamp}|${timestamp}" >> "${UKNOWLEDGE_DATA}/graph_index.txt"
    
    echo "Graph $graph_id created successfully"
    return 0
}

# Create node
create_node() {
    local node_id="$1"
    local label="$2"
    local graph_id="${3:-default}"
    local properties="${4:-{}}"
    
    if [[ -z "$node_id" || -z "$label" ]]; then
        echo "ERROR: Node ID and label required"
        return 1
    fi
    
    local node_file="${UKNOWLEDGE_NODES}/${node_id}.json"
    
    if [[ -f "$node_file" ]]; then
        echo "ERROR: Node $node_id already exists"
        return 1
    fi
    
    # Check if graph exists
    if ! graph_exists "$graph_id"; then
        echo "ERROR: Graph $graph_id does not exist"
        return 1
    fi
    
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    cat > "$node_file" << EOF
{
    "id": "$node_id",
    "label": "$label",
    "properties": $properties,
    "graph_id": "$graph_id",
    "created_at": "$timestamp",
    "updated_at": "$timestamp"
}
EOF
    
    # Update node index
    echo "${node_id}|${label}|${graph_id}|${timestamp}|${timestamp}" >> "${UKNOWLEDGE_DATA}/node_index.txt"
    
    # Update graph node count
    increment_graph_node_count "$graph_id"
    
    echo "Node $node_id created successfully"
    return 0
}

# Create edge (relationship)
create_edge() {
    local edge_id="$1"
    local from_node="$2"
    local to_node="$3"
    local relationship="$4"
    local graph_id="${5:-default}"
    local properties="${6:-{}}"
    
    if [[ -z "$edge_id" || -z "$from_node" || -z "$to_node" || -z "$relationship" ]]; then
        echo "ERROR: Edge ID, from_node, to_node, and relationship required"
        return 1
    fi
    
    local edge_file="${UKNOWLEDGE_EDGES}/${edge_id}.json"
    
    if [[ -f "$edge_file" ]]; then
        echo "ERROR: Edge $edge_id already exists"
        return 1
    fi
    
    # Check if nodes exist
    if ! node_exists "$from_node"; then
        echo "ERROR: From node $from_node does not exist"
        return 1
    fi
    
    if ! node_exists "$to_node"; then
        echo "ERROR: To node $to_node does not exist"
        return 1
    fi
    
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    cat > "$edge_file" << EOF
{
    "id": "$edge_id",
    "from_node": "$from_node",
    "to_node": "$to_node",
    "relationship": "$relationship",
    "properties": $properties,
    "graph_id": "$graph_id",
    "created_at": "$timestamp",
    "updated_at": "$timestamp"
}
EOF
    
    # Update edge index
    echo "${edge_id}|${from_node}|${to_node}|${relationship}|${graph_id}|${timestamp}|${timestamp}" >> "${UKNOWLEDGE_DATA}/edge_index.txt"
    
    # Update graph edge count
    increment_graph_edge_count "$graph_id"
    
    echo "Edge $edge_id created successfully"
    return 0
}

# Check if graph exists
graph_exists() {
    local graph_id="$1"
    local graph_file="${UKNOWLEDGE_GRAPHS}/${graph_id}.json"
    [[ -f "$graph_file" ]]
}

# Check if node exists
node_exists() {
    local node_id="$1"
    local node_file="${UKNOWLEDGE_NODES}/${node_id}.json"
    [[ -f "$node_file" ]]
}

# Check if edge exists
edge_exists() {
    local edge_id="$1"
    local edge_file="${UKNOWLEDGE_EDGES}/${edge_id}.json"
    [[ -f "$edge_file" ]]
}

# Get node by ID
get_node() {
    local node_id="$1"
    
    if [[ -z "$node_id" ]]; then
        echo "ERROR: Node ID required"
        return 1
    fi
    
    local node_file="${UKNOWLEDGE_NODES}/${node_id}.json"
    
    if [[ ! -f "$node_file" ]]; then
        echo "ERROR: Node $node_id not found"
        return 1
    fi
    
    cat "$node_file"
}

# Get edge by ID
get_edge() {
    local edge_id="$1"
    
    if [[ -z "$edge_id" ]]; then
        echo "ERROR: Edge ID required"
        return 1
    fi
    
    local edge_file="${UKNOWLEDGE_EDGES}/${edge_id}.json"
    
    if [[ ! -f "$edge_file" ]]; then
        echo "ERROR: Edge $edge_id not found"
        return 1
    fi
    
    cat "$edge_file"
}

# Find nodes by label
find_nodes_by_label() {
    local label="$1"
    local graph_id="${2:-}"
    
    if [[ -z "$label" ]]; then
        echo "ERROR: Label required"
        return 1
    fi
    
    local node_index="${UKNOWLEDGE_DATA}/node_index.txt"
    
    if [[ ! -f "$node_index" ]]; then
        echo "No nodes found"
        return 0
    fi
    
    if [[ -n "$graph_id" ]]; then
        grep "|${label}|${graph_id}|" "$node_index" | cut -d'|' -f1
    else
        grep "|${label}|" "$node_index" | cut -d'|' -f1
    fi
}

# Find edges by relationship
find_edges_by_relationship() {
    local relationship="$1"
    local graph_id="${2:-}"
    
    if [[ -z "$relationship" ]]; then
        echo "ERROR: Relationship required"
        return 1
    fi
    
    local edge_index="${UKNOWLEDGE_DATA}/edge_index.txt"
    
    if [[ ! -f "$edge_index" ]]; then
        echo "No edges found"
        return 0
    fi
    
    if [[ -n "$graph_id" ]]; then
        grep "|${relationship}|${graph_id}|" "$edge_index" | cut -d'|' -f1
    else
        grep "|${relationship}|" "$edge_index" | cut -d'|' -f1
    fi
}

# Get connected nodes (neighbors)
get_connected_nodes() {
    local node_id="$1"
    local direction="${2:-both}"  # incoming, outgoing, both
    
    if [[ -z "$node_id" ]]; then
        echo "ERROR: Node ID required"
        return 1
    fi
    
    local edge_index="${UKNOWLEDGE_DATA}/edge_index.txt"
    
    if [[ ! -f "$edge_index" ]]; then
        echo "No connections found"
        return 0
    fi
    
    case "$direction" in
        "incoming")
            grep "|[^|]*|${node_id}|" "$edge_index" | cut -d'|' -f2
            ;;
        "outgoing")
            grep "|${node_id}|[^|]*|" "$edge_index" | cut -d'|' -f3
            ;;
        "both")
            grep "|${node_id}|[^|]*|" "$edge_index" | cut -d'|' -f3
            grep "|[^|]*|${node_id}|" "$edge_index" | cut -d'|' -f2
            ;;
        *)
            echo "ERROR: Invalid direction. Use: incoming, outgoing, or both"
            return 1
            ;;
    esac
}

# Increment graph node count
increment_graph_node_count() {
    local graph_id="$1"
    update_graph_count "$graph_id" "node" "+1"
}

# Increment graph edge count
increment_graph_edge_count() {
    local graph_id="$1"
    update_graph_count "$graph_id" "edge" "+1"
}

# Update graph counts (bash 3.x compatible)
update_graph_count() {
    local graph_id="$1"
    local count_type="$2"  # node or edge
    local change="$3"      # +1 or -1
    
    local graph_file="${UKNOWLEDGE_GRAPHS}/${graph_id}.json"
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    if command -v python >/dev/null 2>&1; then
        python -c "
import json
with open('$graph_file', 'r') as f: 
    graph = json.load(f)
count_field = '${count_type}_count'
current = graph[count_field]
if '$change' == '+1':
    graph[count_field] = current + 1
elif '$change' == '-1':
    graph[count_field] = max(0, current - 1)
graph['updated_at'] = '$timestamp'
with open('$graph_file', 'w') as f: 
    json.dump(graph, f, indent=2)
"
    else
        echo "WARNING: Python not available, graph count update may not work properly"
    fi
}

# Knowledge graph statistics
knowledge_stats() {
    echo "🧠 uKNOWLEDGE Statistics"
    echo "======================="
    
    local graph_count=0
    local total_nodes=0
    local total_edges=0
    
    if [[ -d "$UKNOWLEDGE_GRAPHS" ]]; then
        graph_count=$(find "$UKNOWLEDGE_GRAPHS" -name "*.json" | wc -l | tr -d ' ')
    fi
    
    if [[ -d "$UKNOWLEDGE_NODES" ]]; then
        total_nodes=$(find "$UKNOWLEDGE_NODES" -name "*.json" | wc -l | tr -d ' ')
    fi
    
    if [[ -d "$UKNOWLEDGE_EDGES" ]]; then
        total_edges=$(find "$UKNOWLEDGE_EDGES" -name "*.json" | wc -l | tr -d ' ')
    fi
    
    echo "Graphs: $graph_count"
    echo "Total Nodes: $total_nodes"
    echo "Total Edges: $total_edges"
    echo "Data Directory: $UKNOWLEDGE_DATA"
}

# Export functions
export -f init_uknowledge create_graph create_node create_edge
export -f graph_exists node_exists edge_exists get_node get_edge
export -f find_nodes_by_label find_edges_by_relationship get_connected_nodes
export -f knowledge_stats
