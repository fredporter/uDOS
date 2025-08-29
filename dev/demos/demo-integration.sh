#!/bin/bash
# Advanced Integration Demo - v1.0.5.3
# Version: 1.0.5.3

# Set up environment
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UDOS_CORE="$UDOS_ROOT/uCORE"
UDOS_MEMORY="$UDOS_ROOT/uMEMORY"
UDOS_KNOWLEDGE="$UDOS_ROOT/uKNOWLEDGE"

export UDOS_ROOT UDOS_CORE UDOS_MEMORY UDOS_KNOWLEDGE

# Source the integration layer
source "${UDOS_CORE}/code/integration/memory-knowledge-integration.sh"

echo "🚀 Advanced Integration Demo - v1.0.5.3"
echo "========================================"

echo ""
echo "1. Creating a knowledge network..."

# Create some sample entities
store_data_with_knowledge "user_001" "user" '{"name": "Alice", "role": "developer"}'
store_data_with_knowledge "project_001" "project" '{"name": "uDOS", "status": "active"}'
store_data_with_knowledge "task_001" "task" '{"title": "Memory Integration", "priority": "high"}'
store_data_with_knowledge "task_002" "task" '{"title": "Knowledge Graph", "priority": "medium"}'

echo ""
echo "2. Creating relationships..."

# Create relationships
create_data_relationship "user_001" "project_001" "works_on"
create_data_relationship "user_001" "task_001" "assigned_to"
create_data_relationship "user_001" "task_002" "assigned_to"
create_data_relationship "task_001" "project_001" "belongs_to"
create_data_relationship "task_002" "project_001" "belongs_to"

echo ""
echo "3. Querying the knowledge network..."

echo ""
echo "📋 All stored objects:"
search_data "all_objects"

echo ""
echo "🔍 Searching for users:"
search_data "by_type" "user"

echo ""
echo "🔍 Searching for tasks:"  
search_data "by_type" "task"

echo ""
echo "🔗 User network (entities connected to user_001):"
get_entity_network "user_001" 2

echo ""
echo "📊 Integration statistics:"
integration_stats

echo ""
echo "🧹 Cleaning up demo data..."
delete_object "user_001"
delete_object "project_001"
delete_object "task_001"
delete_object "task_002"

echo ""
echo "✅ Demo complete!"
