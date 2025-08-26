#!/bin/bash
# Simple uCORE Version Fix Script
# Updates specific files with version inconsistencies

set -euo pipefail

TARGET_VERSION="v1.0.4.1"
UDOS_ROOT="/Users/agentdigital/uDOS"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

cd "$UDOS_ROOT"

log_info "🔧 Fixing specific version inconsistencies to $TARGET_VERSION"

# Create backup
BACKUP_DIR="sandbox/backup/version-fix-targeted-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
log_info "📁 Backup: $BACKUP_DIR"

# Function to update file with backup
fix_version() {
    local file="$1"
    local old_pattern="$2"
    local new_version="$3"
    local description="$4"

    if [[ -f "$file" ]]; then
        if grep -q "$old_pattern" "$file"; then
            cp "$file" "$BACKUP_DIR/$(basename "$file")"
            sed -i '' "s/$old_pattern/$new_version/g" "$file"
            log_success "✅ Fixed $description in $file"
        else
            log_warning "⚠️  Pattern not found in $file"
        fi
    else
        log_warning "⚠️  File not found: $file"
    fi
}

# Fix specific files identified in scan
log_info "🎯 Fixing identified version inconsistencies..."

# Process Manager
fix_version "uCORE/system/process-manager.sh" "v1\.3\.1" "v1.0.4.1" "Process manager version"

# POST Handler
fix_version "uCORE/core/post-handler.sh" "v1\.3\.3" "v1.0.4.1" "POST handler version"

# Dashboard
fix_version "uCORE/core/utilities/dash.sh" "v1\.3\.2" "v1.0.4.1" "Dashboard version"

# Template System (v1.7.x files)
fix_version "uCORE/json/src/index.ts" "v1\.7\.[0-9]" "v1.0.4.1" "Map generator version"
fix_version "uCORE/json/src/utils/parser.ts" "v1\.7\.[0-9]" "v1.0.4.1" "Parser utilities version"
fix_version "uCORE/json/src/templates/uTEMPLATE-baseMap.md" "v1\.7\.[0-9]" "v1.0.4.1" "Base map template version"
fix_version "uCORE/json/src/README.md" "v1\.7\.[0-9]" "v1.0.4.1" "JSON system README version"

# Command Integration
fix_version "uCORE/json/integrate-commands.py" "v1\.4\.0" "v1.0.4.1" "Command integration version"

# Geographic System
fix_version "uCORE/geo/engines/geo-map-engine.sh" "v1\.4\.0" "v1.0.4.1" "Geo map engine version"
fix_version "uCORE/geo/engines/geo-core-engine.sh" "v1\.4\.0" "v1.0.4.1" "Geo core engine version"
fix_version "uCORE/geo/README.md" "v1\.4\.0" "v1.0.4.1" "Geographic system README version"

# Core README
fix_version "uCORE/core/README.md" "v1\.4\.0" "v1.0.4.1" "Core system README version"

log_info "🔍 Verification - checking for remaining inconsistencies..."

# Quick check for remaining issues
REMAINING=$(find uCORE -type f \( -name "*.sh" -o -name "*.py" -o -name "*.ts" -o -name "*.md" \) \
    -exec grep -l "v1\.[2-9]\.[0-9]\|v1\.[0-9]\.[5-9]" {} \; 2>/dev/null | wc -l || echo "0")

if [[ "$REMAINING" -eq 0 ]]; then
    log_success "🎉 All major version inconsistencies fixed!"
else
    log_warning "⚠️  $REMAINING files may still have version inconsistencies"
fi

log_success "✅ Version fix complete - backups in $BACKUP_DIR"
