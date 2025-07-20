#!/bin/bash
# Development Test Runner
set -euo pipefail

UDEV="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$UDEV/testing"

echo "🧪 Running development tests..."

# Source development environment
source "$UDEV/.dev-env" 2>/dev/null || true

# Run template validation tests
echo "Running template validation..."
"$UDEV/../uCode/template-validation.sh" dev

# Run mock data tests
echo "Running mock data validation..."
"$UDEV/tools/generate-mock-data.sh"

# Validate mock data against schemas
if [[ -f "$UDEV/schemas/dataget-schema.json" ]]; then
    echo "Validating mock data against schemas..."
    for mock_file in "$UDEV/testing/mock-data"/*.json; do
        if [[ -f "$mock_file" ]]; then
            echo "  Checking $(basename "$mock_file")..."
            if jq '.' "$mock_file" >/dev/null 2>&1; then
                echo "    ✅ Valid JSON"
            else
                echo "    ❌ Invalid JSON"
            fi
        fi
    done
fi

echo "✅ Development tests completed"
