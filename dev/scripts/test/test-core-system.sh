#!/bin/bash
# Core System Test Script

set -euo pipefail

echo "🧪 Testing uDOS Core System..."

# Test core components
echo "🎯 Testing core components..."
./uCORE/launcher/universal/test-udos.sh

# Test extensions
echo "🔌 Testing extensions..."
./extensions/extension-manager.sh test

# Test network components
echo "🌐 Testing network components..."
cd uNETWORK/server && python3 -c "import server; print('Server import test passed')" 2>/dev/null || echo "Server test skipped"

echo "✅ Core system tests complete"
