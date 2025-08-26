#!/bin/bash
# Test enhanced uDATA converter with improved output
# Location: sandbox/scripts/ (user testing scripts)

set -euo pipefail

# Simple logging functions
log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Geographic data directory
GEO_MAPS_DIR="$UDOS_ROOT/uMEMORY/system/geo/maps"

log_info "🧪 Testing Enhanced uDATA Converter"
echo "==================================="

# Test with one of the smaller files to see the enhanced output
test_file="$GEO_MAPS_DIR/uMAP-00UH04-Oceania.json"
test_output="$GEO_MAPS_DIR/test-enhanced-output.udata"

if [ -f "$test_file" ]; then
    log_info "Testing enhanced converter with: $(basename "$test_file")"
    echo "---"

    # Use enhanced uCORE conversion tool
    if bash "$UDOS_ROOT/uCORE/json/convert-to-udata.sh" "$test_file" "$test_output"; then
        log_success "✓ Enhanced conversion completed"

        # Show first few lines of result
        log_info "First 3 lines of converted uDATA:"
        head -3 "$test_output"

        # Clean up test file
        rm -f "$test_output"
    else
        log_error "✗ Enhanced conversion failed"
    fi
else
    log_error "Test file not found: $test_file"
fi

log_success "Enhanced uDATA converter testing complete"
