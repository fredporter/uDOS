#!/bin/bash
# uMEMORY Persistence Layer - Bash 3.x Compatible
# Universal Device Operating System
# Version: 1.0.5.3

# uMEMORY provides data persistence and management services
# Fully compatible with bash 3.x (no associative arrays)

# Set up uMEMORY environment
UMEMORY_ROOT="${UDOS_ROOT}/uMEMORY"
UMEMORY_DATA="${UMEMORY_ROOT}/data"
UMEMORY_SCHEMAS="${UMEMORY_ROOT}/schemas"
UMEMORY_CACHE="${UMEMORY_ROOT}/cache"
UMEMORY_LOGS="${UMEMORY_ROOT}/logs"

# Initialize uMEMORY system
init_umemory() {
    echo "🧠 Initializing uMEMORY v1.0.5.3..."
    
    # Create directory structure
    mkdir -p "$UMEMORY_DATA" "$UMEMORY_SCHEMAS" "$UMEMORY_CACHE" "$UMEMORY_LOGS"
    
    # Create subdirectories for different data types
    mkdir -p "${UMEMORY_DATA}/objects"
    mkdir -p "${UMEMORY_DATA}/collections"
    mkdir -p "${UMEMORY_DATA}/indexes"
    mkdir -p "${UMEMORY_DATA}/metadata"
    
    # Initialize schemas
    init_default_schemas
    
    # Create memory index
    init_memory_index
    
    echo "✅ uMEMORY initialization complete"
    return 0
}

# Initialize default schemas
init_default_schemas() {
    # Object schema
    cat > "${UMEMORY_SCHEMAS}/object.json" << 'EOF'
{
    "type": "object",
    "version": "1.0",
    "fields": {
        "id": {"type": "string", "required": true, "unique": true},
        "type": {"type": "string", "required": true},
        "data": {"type": "object", "required": true},
        "created_at": {"type": "timestamp", "required": true},
        "updated_at": {"type": "timestamp", "required": true},
        "metadata": {"type": "object", "required": false}
    }
}
EOF

    # Collection schema
    cat > "${UMEMORY_SCHEMAS}/collection.json" << 'EOF'
{
    "type": "collection",
    "version": "1.0",
    "fields": {
        "name": {"type": "string", "required": true, "unique": true},
        "description": {"type": "string", "required": false},
        "objects": {"type": "array", "required": true},
        "created_at": {"type": "timestamp", "required": true},
        "updated_at": {"type": "timestamp", "required": true}
    }
}
EOF
}

# Initialize memory index
init_memory_index() {
    local index_file="${UMEMORY_DATA}/indexes/main.idx"
    
    if [[ ! -f "$index_file" ]]; then
        cat > "$index_file" << 'EOF'
# uMEMORY Main Index
# Format: object_id|type|file_path|created_at|updated_at
EOF
    fi
}

# Create object (bash 3.x compatible)
create_object() {
    local object_id="$1"
    local object_type="$2"
    local object_data="$3"
    local metadata="${4:-{}}"
    
    if [[ -z "$object_id" || -z "$object_type" || -z "$object_data" ]]; then
        echo "ERROR: Missing required parameters for create_object"
        return 1
    fi
    
    # Check if object already exists
    if object_exists "$object_id"; then
        echo "ERROR: Object $object_id already exists"
        return 1
    fi
    
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    local object_file="${UMEMORY_DATA}/objects/${object_id}.json"
    
    # Create object file
    cat > "$object_file" << EOF
{
    "id": "$object_id",
    "type": "$object_type",
    "data": $object_data,
    "created_at": "$timestamp",
    "updated_at": "$timestamp",
    "metadata": $metadata
}
EOF
    
    # Update index
    echo "${object_id}|${object_type}|${object_file}|${timestamp}|${timestamp}" >> "${UMEMORY_DATA}/indexes/main.idx"
    
    echo "Object $object_id created successfully"
    return 0
}

# Read object
read_object() {
    local object_id="$1"
    
    if [[ -z "$object_id" ]]; then
        echo "ERROR: Object ID required"
        return 1
    fi
    
    local object_file="${UMEMORY_DATA}/objects/${object_id}.json"
    
    if [[ ! -f "$object_file" ]]; then
        echo "ERROR: Object $object_id not found"
        return 1
    fi
    
    cat "$object_file"
    return 0
}

# Update object
update_object() {
    local object_id="$1"
    local new_data="$2"
    local new_metadata="${3:-}"
    
    if [[ -z "$object_id" || -z "$new_data" ]]; then
        echo "ERROR: Missing required parameters for update_object"
        return 1
    fi
    
    local object_file="${UMEMORY_DATA}/objects/${object_id}.json"
    
    if [[ ! -f "$object_file" ]]; then
        echo "ERROR: Object $object_id not found"
        return 1
    fi
    
    # Read existing object
    local existing_type existing_created_at existing_metadata
    
    if command -v python >/dev/null 2>&1; then
        existing_type="$(python -c "import json; obj=json.load(open('$object_file')); print(obj['type'])")"
        existing_created_at="$(python -c "import json; obj=json.load(open('$object_file')); print(obj['created_at'])")"
        if [[ -z "$new_metadata" ]]; then
            existing_metadata="$(python -c "import json; obj=json.load(open('$object_file')); print(json.dumps(obj['metadata']))")"
            new_metadata="$existing_metadata"
        fi
    else
        # Fallback for systems without Python
        existing_type="$(grep '"type"' "$object_file" | cut -d'"' -f4)"
        existing_created_at="$(grep '"created_at"' "$object_file" | cut -d'"' -f4)"
        if [[ -z "$new_metadata" ]]; then
            new_metadata="{}"
        fi
    fi
    
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    # Update object file
    cat > "$object_file" << EOF
{
    "id": "$object_id",
    "type": "$existing_type",
    "data": $new_data,
    "created_at": "$existing_created_at",
    "updated_at": "$timestamp",
    "metadata": $new_metadata
}
EOF
    
    # Update index
    update_index_entry "$object_id" "$timestamp"
    
    echo "Object $object_id updated successfully"
    return 0
}

# Delete object
delete_object() {
    local object_id="$1"
    
    if [[ -z "$object_id" ]]; then
        echo "ERROR: Object ID required"
        return 1
    fi
    
    local object_file="${UMEMORY_DATA}/objects/${object_id}.json"
    
    if [[ ! -f "$object_file" ]]; then
        echo "ERROR: Object $object_id not found"
        return 1
    fi
    
    # Remove object file
    rm "$object_file"
    
    # Remove from index
    remove_index_entry "$object_id"
    
    echo "Object $object_id deleted successfully"
    return 0
}

# Check if object exists
object_exists() {
    local object_id="$1"
    local object_file="${UMEMORY_DATA}/objects/${object_id}.json"
    [[ -f "$object_file" ]]
}

# List objects by type
list_objects_by_type() {
    local object_type="$1"
    
    if [[ -z "$object_type" ]]; then
        echo "ERROR: Object type required"
        return 1
    fi
    
    local index_file="${UMEMORY_DATA}/indexes/main.idx"
    
    if [[ ! -f "$index_file" ]]; then
        echo "No objects found"
        return 0
    fi
    
    grep "|${object_type}|" "$index_file" | cut -d'|' -f1
}

# List all objects
list_all_objects() {
    local index_file="${UMEMORY_DATA}/indexes/main.idx"
    
    if [[ ! -f "$index_file" ]]; then
        echo "No objects found"
        return 0
    fi
    
    grep -v "^#" "$index_file" | while IFS='|' read -r obj_id obj_type obj_file created updated; do
        if [[ -n "$obj_id" ]]; then
            echo "$obj_id ($obj_type)"
        fi
    done
}

# Update index entry
update_index_entry() {
    local object_id="$1"
    local updated_at="$2"
    local index_file="${UMEMORY_DATA}/indexes/main.idx"
    local temp_file="${index_file}.tmp"
    
    # Create updated index
    grep -v "^${object_id}|" "$index_file" > "$temp_file"
    grep "^${object_id}|" "$index_file" | sed "s/|[^|]*$/|${updated_at}/" >> "$temp_file"
    
    mv "$temp_file" "$index_file"
}

# Remove index entry
remove_index_entry() {
    local object_id="$1"
    local index_file="${UMEMORY_DATA}/indexes/main.idx"
    local temp_file="${index_file}.tmp"
    
    grep -v "^${object_id}|" "$index_file" > "$temp_file"
    mv "$temp_file" "$index_file"
}

# Create collection
create_collection() {
    local collection_name="$1"
    local description="${2:-}"
    
    if [[ -z "$collection_name" ]]; then
        echo "ERROR: Collection name required"
        return 1
    fi
    
    local collection_file="${UMEMORY_DATA}/collections/${collection_name}.json"
    
    if [[ -f "$collection_file" ]]; then
        echo "ERROR: Collection $collection_name already exists"
        return 1
    fi
    
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    cat > "$collection_file" << EOF
{
    "name": "$collection_name",
    "description": "$description",
    "objects": [],
    "created_at": "$timestamp",
    "updated_at": "$timestamp"
}
EOF
    
    echo "Collection $collection_name created successfully"
    return 0
}

# Add object to collection
add_to_collection() {
    local collection_name="$1"
    local object_id="$2"
    
    if [[ -z "$collection_name" || -z "$object_id" ]]; then
        echo "ERROR: Collection name and object ID required"
        return 1
    fi
    
    local collection_file="${UMEMORY_DATA}/collections/${collection_name}.json"
    
    if [[ ! -f "$collection_file" ]]; then
        echo "ERROR: Collection $collection_name not found"
        return 1
    fi
    
    if ! object_exists "$object_id"; then
        echo "ERROR: Object $object_id not found"
        return 1
    fi
    
    # For bash 3.x compatibility, use simple approach
    if command -v python >/dev/null 2>&1; then
        python -c "
import json
with open('$collection_file', 'r') as f: 
    collection = json.load(f)
if '$object_id' not in collection['objects']:
    collection['objects'].append('$object_id')
    collection['updated_at'] = '$(date -u +"%Y-%m-%dT%H:%M:%SZ")'
    with open('$collection_file', 'w') as f: 
        json.dump(collection, f, indent=2)
    print('Object added to collection')
else:
    print('Object already in collection')
"
    else
        echo "WARNING: Python not available, collection update may not work properly"
        return 1
    fi
}

# Memory statistics
memory_stats() {
    echo "📊 uMEMORY Statistics"
    echo "===================="
    
    local object_count=0
    local collection_count=0
    
    if [[ -d "${UMEMORY_DATA}/objects" ]]; then
        object_count=$(find "${UMEMORY_DATA}/objects" -name "*.json" | wc -l | tr -d ' ')
    fi
    
    if [[ -d "${UMEMORY_DATA}/collections" ]]; then
        collection_count=$(find "${UMEMORY_DATA}/collections" -name "*.json" | wc -l | tr -d ' ')
    fi
    
    echo "Objects: $object_count"
    echo "Collections: $collection_count"
    echo "Data Directory: $UMEMORY_DATA"
    echo "Cache Directory: $UMEMORY_CACHE"
}

# Export functions
export -f init_umemory create_object read_object update_object delete_object
export -f object_exists list_objects_by_type list_all_objects
export -f create_collection add_to_collection memory_stats
