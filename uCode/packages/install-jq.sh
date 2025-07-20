#!/bin/bash
# uDOS Package Installer: jq (JSON processor)
# Command-line JSON processor and formatter

set -euo pipefail

PACKAGE_NAME="jq"
PACKAGE_DESC="Command-line JSON processor"
UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# Simple logging"
log_info() { echo "ℹ️  $*"; }; log_success() { echo "✅ $*"; }; log_warn() { echo "⚠️  $*"; }; log_error() { echo "❌ $*"; }"

# Package information
GITHUB_REPO="jqlang/jq"
HOMEBREW_FORMULA="jq"
APT_PACKAGE="jq"

log_info "Installing ${PACKAGE_NAME}: ${PACKAGE_DESC}"

# Detect platform and install
case "$(uname -s)" in
    Darwin*)
        log_info "Detected macOS - using Homebrew"
        if command -v brew >/dev/null 2>&1; then
            if ! brew list jq >/dev/null 2>&1; then
                log_info "Installing jq via Homebrew..."
                brew install jq
            else
                log_info "jq already installed via Homebrew"
            fi
        else
            log_warn "Homebrew not found - manual installation required"
            echo "Please install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
        ;;
    Linux*)
        log_info "Detected Linux - using package manager"
        if command -v apt-get >/dev/null 2>&1; then
            log_info "Installing jq via apt..."
            sudo apt-get update && sudo apt-get install -y jq
        elif command -v yum >/dev/null 2>&1; then
            log_info "Installing jq via yum..."
            sudo yum install -y jq
        elif command -v dnf >/dev/null 2>&1; then
            log_info "Installing jq via dnf..."
            sudo dnf install -y jq
        else
            log_warn "No supported package manager found"
            echo "Please install jq manually from: https://github.com/${GITHUB_REPO}"
            exit 1
        fi
        ;;
    *)
        log_error "Unsupported platform: $(uname -s)"
        exit 1
        ;;
esac

# Verify installation
if command -v jq >/dev/null 2>&1; then
    JQ_VERSION=$(jq --version)
    log_success "Successfully installed: ${JQ_VERSION}"
    
    # Update package registry
    PACKAGE_FILE="${UDOS_ROOT}/uMemory/state/packages.json"
    mkdir -p "$(dirname "$PACKAGE_FILE")"
    
    # Create or update package registry
    if [[ ! -f "$PACKAGE_FILE" ]]; then
        echo '{}' > "$PACKAGE_FILE"
    fi
    
    # Add package info
    jq --arg name "$PACKAGE_NAME" \
       --arg desc "$PACKAGE_DESC" \
       --arg version "$JQ_VERSION" \
       --arg installed "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.[$name] = {description: $desc, version: $version, installed: $installed, status: "active"}' \
       "$PACKAGE_FILE" > "$PACKAGE_FILE.tmp" && mv "$PACKAGE_FILE.tmp" "$PACKAGE_FILE"
    
    # Create usage examples
    cat > "${UDOS_ROOT}/package/utils/jq.md" << 'EOF'
# jq - JSON Processor

## Overview
`jq` is a lightweight and flexible command-line JSON processor.

## Usage Examples

```bash
# Pretty print JSON
echo '{"name":"uDOS","version":"1.0"}' | jq .

# Extract specific field
echo '{"name":"uDOS","version":"1.0"}' | jq .name

# Filter arrays
echo '[{"name":"file1.txt"},{"name":"file2.md"}]' | jq '.[].name'

# Complex filtering
jq '.datasets[] | select(.records > 50)' datasets.json

# Transform data
jq '.[] | {filename: .name, size: .size}' files.json

# Count items
jq 'length' array.json

# Sort array
jq 'sort_by(.name)' datasets.json
```

## uDOS Integration

Critical for uDOS JSON processing:
- Dataset manipulation and validation
- Package registry management
- Configuration file processing
- Dashboard data generation
- Template variable processing

## uDOS Specific Usage

```bash
# Process uDOS datasets
jq '.cityMap[] | select(.country == "US")' uMapping/datasets/cityMap.json

# Update package registry
jq --arg pkg "newpackage" '.[$pkg] = {"status": "installed"}' uMemory/state/packages.json

# Generate dashboard stats
jq '{total: length, active: [.[] | select(.status == "active")] | length}' uMemory/state/packages.json

# Validate template variables
# Display variable structure
jq 'keys' uTemplate/variables/user-vars.json

# Extract mission data
jq '.missions[] | select(.status == "active")' uMemory/state/missions.json
```

## Advanced Features

```bash
# Conditional operations
jq 'if .status == "active" then .name else empty end'

# Mathematical operations
jq '.datasets | map(.records) | add'

# String manipulation
jq '.name | ascii_downcase'

# Date formatting
jq '.timestamp | strftime("%Y-%m-%d")'

# Group by
jq 'group_by(.category) | map({category: .[0].category, count: length})'
```

## Error Handling

```bash
# Handle missing fields
jq '.field // "default_value"'

# Try alternative
jq '.primary // .secondary // "fallback"'

# Check type
jq 'if type == "array" then length else "not an array" end'
```
EOF

    log_success "Package documentation created: package/utils/jq.md"
    log_success "jq installation complete and ready for use!"
    
else
    log_error "Installation failed - jq command not found"
    exit 1
fi
