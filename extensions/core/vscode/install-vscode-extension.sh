#!/bin/bash
# VS Code Extension Install Hook
# Integrates VS Code development environment with uDOS

set -euo pipefail

# Get paths
EXTENSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$EXTENSION_DIR/../../.." && pwd)"

echo "🔌 Installing VS Code integration extension..."

# Call the main setup script
if [ -f "$UDOS_ROOT/uSCRIPT/integration/vscode/setup-vscode.sh" ]; then
    "$UDOS_ROOT/uSCRIPT/integration/vscode/setup-vscode.sh"
else
    echo "❌ VS Code setup script not found"
    exit 1
fi

echo "✅ VS Code extension installed successfully"
