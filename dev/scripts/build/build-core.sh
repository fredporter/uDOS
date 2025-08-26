#!/bin/bash
# Core System Build Script

set -euo pipefail

echo "🔧 Building uDOS Core System..."

# Check for required tools
command -v bash >/dev/null 2>&1 || { echo "Bash required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python3 required"; exit 1; }

# Validate core structure
echo "📋 Validating core structure..."
./dev/scripts/test/validate-system-references.sh

# Build extensions
echo "🔌 Building extensions..."
./extensions/extension-manager.sh build

# Setup network components
echo "🌐 Setting up network components..."
cd uNETWORK/server && python3 -m pip install -r requirements.txt 2>/dev/null || true

echo "✅ Core system build complete"
