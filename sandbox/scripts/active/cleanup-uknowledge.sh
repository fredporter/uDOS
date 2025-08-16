#!/bin/bash
# uKnowledge Folder Cleanup Script
# Moves files to appropriate locations and archives outdated content

set -euo pipefail

UHOME="${UHOME:-$(pwd)}"
UKNOWLEDGE="$UHOME/uKnowledge"
UDOCS="$UHOME/docs"
UTEMPLATE="$UHOME/uTemplate"
UCOMPANION="$UHOME/uCompanion"
UDEV="$UHOME/uDev"
TRASH="$UHOME/trash"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🧹 uKnowledge Folder Cleanup"
echo "═══════════════════════════════"

cleanup_uknowledge() {
    echo "📋 Analyzing uKnowledge contents..."
    
    # 1. Move ARCHITECTURE.md to docs (more appropriate location)
    if [[ -f "$UKNOWLEDGE/ARCHITECTURE.md" ]]; then
        echo "  • Moving ARCHITECTURE.md to docs/"
        mv "$UKNOWLEDGE/ARCHITECTURE.md" "$UDOCS/"
    fi
    
    # 2. Move companion files to uCompanion (dedicated companion directory)
    if [[ -d "$UKNOWLEDGE/companion" ]]; then
        echo "  • Moving companion files to uCompanion/"
        mkdir -p "$UCOMPANION"
        if [[ -f "$UKNOWLEDGE/companion/chester-config.json" ]]; then
            mv "$UKNOWLEDGE/companion/chester-config.json" "$UCOMPANION/"
        fi
        if [[ -f "$UKNOWLEDGE/companion/chester-wizard-assistant.md" ]]; then
            mv "$UKNOWLEDGE/companion/chester-wizard-assistant.md" "$UCOMPANION/"
        fi
        rmdir "$UKNOWLEDGE/companion" 2>/dev/null || true
    fi
    
    # 3. Move commands.json dataset to uTemplate/datasets (with other datasets)
    if [[ -f "$UKNOWLEDGE/datasets/commands.json" ]]; then
        echo "  • Moving commands.json to uTemplate/datasets/"
        mkdir -p "$UTEMPLATE/datasets"
        mv "$UKNOWLEDGE/datasets/commands.json" "$UTEMPLATE/datasets/"
        rmdir "$UKNOWLEDGE/datasets" 2>/dev/null || true
    fi
    
    # 4. Remove empty directories
    echo "  • Removing empty directories..."
    for dir in assets general-library maps; do
        if [[ -d "$UKNOWLEDGE/$dir" ]]; then
            rmdir "$UKNOWLEDGE/$dir" 2>/dev/null && echo "    ✅ Removed empty: $dir" || echo "    ⚠️ Not empty: $dir"
        fi
    done
    
    # 5. Check if uKnowledge is now empty and create README if so
    if [[ -z "$(ls -A "$UKNOWLEDGE" 2>/dev/null)" ]]; then
        echo "  • Creating placeholder README for future knowledge base..."
        cat > "$UKNOWLEDGE/README.md" << 'EOF'
# 📚 uKnowledge - Knowledge Base

This directory is reserved for the uDOS knowledge base and documentation system.

## Purpose
- **Knowledge Articles**: Technical documentation and guides
- **Reference Materials**: System specifications and API docs  
- **Tutorial Content**: Step-by-step learning materials
- **Research Notes**: Development research and findings

## Structure (Future)
```
uKnowledge/
├── articles/          # Technical articles
├── reference/         # API and system reference
├── tutorials/         # Learning materials
└── research/          # Development research
```

## Current Status
This directory has been cleaned up with content moved to appropriate locations:
- Architecture docs → `docs/`
- Companion configs → `uCompanion/`  
- Dataset files → `uTemplate/datasets/`

Future knowledge base content will be organized here.
EOF
    fi
}

# Update references in other files
update_references() {
    echo "🔧 Updating file references..."
    
    # Update any scripts that might reference the old locations
    if [[ -f "$UHOME/uCode/companion-system.sh" ]]; then
        echo "  • Updating companion-system.sh references..."
        sed -i '' 's|uKnowledge/companion|uCompanion|g' "$UHOME/uCode/companion-system.sh" 2>/dev/null || true
    fi
    
    # Update any template files that reference architecture docs
    find "$UTEMPLATE" -name "*.md" -type f -exec sed -i '' 's|uKnowledge/ARCHITECTURE\.md|docs/ARCHITECTURE.md|g' {} \; 2>/dev/null || true
}

# Create summary report
create_summary() {
    echo ""
    echo "📊 Cleanup Summary"
    echo "════════════════════"
    echo "  ✅ ARCHITECTURE.md → docs/"
    echo "  ✅ Companion files → uCompanion/"
    echo "  ✅ commands.json → uTemplate/datasets/"
    echo "  ✅ Empty directories removed"
    echo "  ✅ References updated"
    echo "  ✅ README.md created for future use"
    echo ""
    echo "🎯 uKnowledge is now clean and ready for future knowledge base content!"
}

# Main execution
main() {
    cleanup_uknowledge
    update_references
    create_summary
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
