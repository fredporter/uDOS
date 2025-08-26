#!/bin/bash
# uCORE Version Standardization Script
# Updates all version references to v1.0.4.1 standard

set -euo pipefail

# Script metadata
SCRIPT_NAME="ucore-version-fix.sh"
TARGET_VERSION="v1.0.4.1"
TARGET_VERSION_NUMERIC="1.0.4"
UDOS_ROOT="/Users/agentdigital/uDOS"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Change to uDOS root directory
cd "$UDOS_ROOT"

log_info "🔧 Starting uCORE Version Standardization"
log_info "Target Version: $TARGET_VERSION"
log_info "Working Directory: $(pwd)"

# Create backup directory
BACKUP_DIR="sandbox/backup/version-fix-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
log_info "📁 Backup directory: $BACKUP_DIR"

# Counter for changes
CHANGES_MADE=0

# Function to backup and update file
update_file_version() {
    local file="$1"
    local search_pattern="$2"
    local replacement="$3"
    local description="$4"

    if [[ -f "$file" ]]; then
        # Create backup
        cp "$file" "$BACKUP_DIR/$(basename "$file").backup"

        # Check if pattern exists in file
        if grep -q "$search_pattern" "$file"; then
            log_info "📝 Updating $file - $description"

            # Perform replacement
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS sed
                sed -i '' "s/$search_pattern/$replacement/g" "$file"
            else
                # Linux sed
                sed -i "s/$search_pattern/$replacement/g" "$file"
            fi

            log_success "   ✅ Updated: $description"
            ((CHANGES_MADE++))
        else
            log_warning "   ⚠️  Pattern not found in $file"
        fi
    else
        log_error "   ❌ File not found: $file"
    fi
}

# Function to update specific version strings
update_specific_version() {
    local file="$1"
    local old_version="$2"
    local description="$3"

    update_file_version "$file" "$old_version" "$TARGET_VERSION" "$description"
}

log_info "🎯 Phase 1: Critical System Files"

# 1. Main ucode binary
update_specific_version "uCORE/bin/ucode" "v1\.3\.2" "Main ucode version header"

# 2. Environment script
update_specific_version "uCORE/core/environment.sh" "v1\.3\.1" "Environment UDOS_VERSION variable"

# 3. Process manager
update_specific_version "uCORE/system/process-manager.sh" "v1\.3\.1" "Process manager version header"

log_info "🛠️ Phase 2: Core Utilities"

# 4. POST handler
update_specific_version "uCORE/core/post-handler.sh" "v1\.3\.3" "POST handler version header"

# 5. Dashboard
update_specific_version "uCORE/core/utilities/dash.sh" "v1\.3\.2" "Dashboard version header"

# 6. Template utility
update_specific_version "uCORE/core/utilities/template.sh" "v1\.0\.0" "Template utility version"

log_info "🚀 Phase 3: Launchers and Platform Tools"

# 7. Development launcher
update_specific_version "uCORE/launcher/universal/start-dev.sh" "v1\.3\.1" "Development launcher version"

# 8. macOS installer
update_specific_version "uCORE/launcher/platform/macos/install-udos.sh" "v1\.3\.1" "macOS installer version"

# 9. Minimal ucode
update_file_version "uCORE/core/compat/ucode-minimal" "v1\.3\.1-minimal" "${TARGET_VERSION}-minimal" "Minimal ucode version"

log_info "📊 Phase 4: JSON/Data Systems"

# 10. Package.json (numeric version without 'v')
update_file_version "uCORE/json/package.json" '"version": "1\.3\.1"' "\"version\": \"$TARGET_VERSION_NUMERIC\"" "Package.json version"

# 11. Command integration Python script
update_specific_version "uCORE/json/integrate-commands.py" "v1\.4\.0" "Command integration version"

# 12. Template system files with v1.7.x
for file in uCORE/json/src/README.md uCORE/json/src/index.ts uCORE/json/src/utils/parser.ts uCORE/json/src/templates/uTEMPLATE-baseMap.md; do
    if [[ -f "$file" ]]; then
        update_file_version "$file" "v1\.7\.[0-9]" "$TARGET_VERSION" "Template system version in $(basename "$file")"
    fi
done

# 13. uDATA parser
update_specific_version "uCORE/json/src/udataParser.ts" "v1\.0\.0" "uDATA parser version"

log_info "🧪 Phase 5: Testing and Color Systems"

# 14. Test scripts
update_specific_version "uCORE/system/test-terminal-foundation.sh" "v1\.4" "Terminal foundation test version"

# 15. Color system
update_specific_version "uCORE/system/polaroid-colors.sh" "v1\.4" "Polaroid color system version"

log_info "🔍 Phase 6: Catch Remaining Version Patterns"

# Find and update any remaining version patterns
log_info "📋 Scanning for remaining version inconsistencies..."

# Create list of files to check
TEMP_FILE=$(mktemp)

# Find files with version patterns and update them
find uCORE -type f \( -name "*.sh" -o -name "*.py" -o -name "*.ts" -o -name "*.md" -o -name "*.json" \) \
    -exec grep -l "v1\.[1-9]\.[0-9]" {} \; > "$TEMP_FILE" 2>/dev/null || true

while IFS= read -r file; do
    if [[ -f "$file" && "$file" != *".backup" ]]; then
        # Skip if already processed or if it's our target version
        if ! grep -q "$TARGET_VERSION" "$file"; then
            log_info "🔍 Found additional version references in: $file"

            # Backup file
            cp "$file" "$BACKUP_DIR/$(basename "$file")-additional.backup"

            # Update various version patterns
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS sed - update various version patterns to target version
                sed -i '' -E "s/v1\.[1-9]\.[0-9]+/$TARGET_VERSION/g" "$file"
                sed -i '' -E "s/Version [1-9]\.[0-9]\.[0-9]+/Version $TARGET_VERSION_NUMERIC/g" "$file"
                sed -i '' -E "s/version [1-9]\.[0-9]\.[0-9]+/version $TARGET_VERSION_NUMERIC/g" "$file"
            else
                # Linux sed
                sed -i -E "s/v1\.[1-9]\.[0-9]+/$TARGET_VERSION/g" "$file"
                sed -i -E "s/Version [1-9]\.[0-9]\.[0-9]+/Version $TARGET_VERSION_NUMERIC/g" "$file"
                sed -i -E "s/version [1-9]\.[0-9]\.[0-9]+/version $TARGET_VERSION_NUMERIC/g" "$file"
            fi

            log_success "   ✅ Updated additional version references in: $file"
            ((CHANGES_MADE++))
        fi
    fi
done < "$TEMP_FILE"

# Clean up temp file
rm -f "$TEMP_FILE"

log_info "✅ Phase 7: Verification"

# Verify main system components show correct version
log_info "🔍 Verifying critical version updates..."

# Check ucode main binary
if grep -q "$TARGET_VERSION" "uCORE/bin/ucode"; then
    log_success "   ✅ ucode main binary shows $TARGET_VERSION"
else
    log_error "   ❌ ucode main binary still has incorrect version"
fi

# Check environment script
if grep -q "UDOS_VERSION=\"$TARGET_VERSION\"" "uCORE/core/environment.sh"; then
    log_success "   ✅ Environment script shows $TARGET_VERSION"
else
    log_error "   ❌ Environment script still has incorrect version"
fi

# Check package.json
if grep -q "\"version\": \"$TARGET_VERSION_NUMERIC\"" "uCORE/json/package.json"; then
    log_success "   ✅ Package.json shows $TARGET_VERSION_NUMERIC"
else
    log_error "   ❌ Package.json still has incorrect version"
fi

log_info "📊 Summary"
log_success "✅ Version standardization complete!"
log_success "📁 Backups saved to: $BACKUP_DIR"
log_success "🔢 Total files updated: $CHANGES_MADE"
log_success "🎯 Target version: $TARGET_VERSION"

log_info "🧪 Next Steps:"
log_info "1. Test main ucode command: ./uCORE/bin/ucode help"
log_info "2. Check environment: source uCORE/core/environment.sh && echo \$UDOS_VERSION"
log_info "3. Verify dashboard: ./uCORE/core/utilities/dash.sh"
log_info "4. Test development launcher: ./uCORE/launcher/universal/start-dev.sh"

log_success "🚀 uCORE version standardization completed successfully!"
