#!/bin/bash
# Integration Layer Test - Standalone
# Version: 1.0.5.3

# Set up environment
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UDOS_CORE="$UDOS_ROOT/uCORE"
UDOS_MEMORY="$UDOS_ROOT/uMEMORY"
UDOS_KNOWLEDGE="$UDOS_ROOT/uKNOWLEDGE"

export UDOS_ROOT UDOS_CORE UDOS_MEMORY UDOS_KNOWLEDGE

# Source the integration layer
source "${UDOS_CORE}/code/integration/memory-knowledge-integration.sh"

echo "🔬 Standalone Integration Test"
echo "=============================="

echo ""
echo "Environment Check:"
echo "UDOS_ROOT: $UDOS_ROOT"
echo "UDOS_CORE: $UDOS_CORE"
echo "UDOS_MEMORY: $UDOS_MEMORY"
echo "UDOS_KNOWLEDGE: $UDOS_KNOWLEDGE"

echo ""
echo "Testing integration functionality..."
test_integration
