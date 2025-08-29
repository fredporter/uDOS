#!/bin/bash
# Script Version Cleanup Tool
# Removes version numbers from script filenames and creates backups

set -e

# Configuration
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKUP_DIR="$UDOS_ROOT/dev/backups/scripts"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_SUBDIR="$BACKUP_DIR/cleanup_$TIMESTAMP"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create backup subdirectory
echo -e "${BLUE}🗂️ Script Version Cleanup Tool${NC}"
echo "=================================="
echo ""
echo -e "${YELLOW}📁 Creating backup directory: $BACKUP_SUBDIR${NC}"
mkdir -p "$BACKUP_SUBDIR"

# Function to backup and rename a file
cleanup_script() {
    local file_path="$1"
    local dir_path=$(dirname "$file_path")
    local filename=$(basename "$file_path")
    
    # Extract base name without version
    local base_name=$(echo "$filename" | sed 's/-v[0-9]\+[0-9\.]*\.sh$/.sh/')
    local new_path="$dir_path/$base_name"
    
    # Create relative path for backup
    local rel_path=${file_path#$UDOS_ROOT/}
    local backup_path="$BACKUP_SUBDIR/$rel_path"
    local backup_dir=$(dirname "$backup_path")
    
    echo -e "${YELLOW}🔄 Processing: $filename${NC}"
    echo "  📂 Original: $file_path"
    echo "  💾 Backup:   $backup_path"
    echo "  ✨ New name: $new_path"
    
    # Create backup directory structure
    mkdir -p "$backup_dir"
    
    # Copy to backup
    cp "$file_path" "$backup_path"
    
    # Rename original
    mv "$file_path" "$new_path"
    
    echo -e "${GREEN}  ✅ Completed${NC}"
    echo ""
    
    return 0
}

# Find and process versioned scripts
echo -e "${BLUE}🔍 Finding versioned scripts...${NC}"
echo ""

# Process each versioned script
while IFS= read -r -d '' file; do
    cleanup_script "$file"
done < <(find "$UDOS_ROOT" -name "*-v[0-9]*.sh" -type f -print0)

# Update references in scripts
echo -e "${BLUE}🔧 Updating script references...${NC}"
echo ""

# Function to update references
update_references() {
    local old_name="$1"
    local new_name="$2"
    
    echo -e "${YELLOW}📝 Updating references: $old_name → $new_name${NC}"
    
    # Find and update references
    find "$UDOS_ROOT" -type f \( -name "*.sh" -o -name "udos" \) -exec grep -l "$old_name" {} \; | while read -r ref_file; do
        echo "  📄 Updating: $ref_file"
        sed -i.bak "s|$old_name|$new_name|g" "$ref_file"
        rm -f "$ref_file.bak"
    done
}

# Update specific references
update_references "foundation-init.sh" "foundation-init.sh"
update_references "network-foundation.sh" "network-foundation.sh"
update_references "network-integration.sh" "network-integration.sh"

# Create cleanup report
REPORT_FILE="$BACKUP_SUBDIR/cleanup_report.txt"
echo "Script Version Cleanup Report" > "$REPORT_FILE"
echo "=============================" >> "$REPORT_FILE"
echo "Date: $(date)" >> "$REPORT_FILE"
echo "Backup Location: $BACKUP_SUBDIR" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Files processed:" >> "$REPORT_FILE"
find "$BACKUP_SUBDIR" -name "*.sh" -type f | sed "s|$BACKUP_SUBDIR/||" >> "$REPORT_FILE"

echo -e "${GREEN}✅ Script cleanup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "  📁 Backups saved to: $BACKUP_SUBDIR"
echo "  📄 Report saved to: $REPORT_FILE"
echo "  🔧 References updated automatically"
echo ""
echo -e "${GREEN}🎯 Development process improved!${NC}"
echo "  • No more version numbers in script names"
echo "  • Clean development workflow"
echo "  • All backups preserved safely"
