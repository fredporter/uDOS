#!/bin/bash
# Convert geographic JSON files to uDATA format
# Location: sandbox/scripts/ (user processing scripts)

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

log_info "🔄 Converting Geographic Files to uDATA Format"
echo "=============================================="

cd "$GEO_MAPS_DIR"

# Convert each JSON file to uDATA format
for file in *.json; do
    if [ -f "$file" ]; then
        basename="${file%.json}"
        output_file="${basename}.udata"

        log_info "Converting: $file → $output_file"

        # Use uCORE conversion tool
        if bash "$UDOS_ROOT/uCORE/json/convert-to-udata.sh" "$file" "$output_file"; then
            log_success "✓ Converted: $output_file"

            # Validate the conversion
            if bash "$UDOS_ROOT/uCORE/json/convert-to-udata.sh" --validate "$output_file" >/dev/null 2>&1; then
                log_success "✓ Validated: $output_file"
            else
                log_warning "⚠ Validation issues: $output_file"
            fi
        else
            log_error "✗ Conversion failed: $file"
        fi

        echo "---"
    fi
done

# Show final results
log_info "Final geographic data files:"
ls -la *.json *.udata

log_success "Geographic uDATA conversion complete"
