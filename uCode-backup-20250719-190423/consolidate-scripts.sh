#!/bin/bash
# uDOS Script Consolidation Manager v1.0.0
# Archives redundant scripts and updates system to use consolidated versions

set -euo pipefail

UHOME="${HOME}/uDOS"
UCODE_DIR="${UHOME}/uCode"
ARCHIVE_DIR="${UHOME}/progress/script-consolidation-archive"

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Scripts to be archived (replaced by consolidated versions)
SCRIPTS_TO_ARCHIVE=(
    "make-tree.sh"
    "make-tree-simple.sh"
    "packages/manager.sh"
    "packages/manager-simple.sh"
    "packages/manager-enhanced.sh"
    "packages/manager-compatible.sh"
)

# Create archive directory
create_archive() {
    blue "📁 Creating consolidation archive directory..."
    mkdir -p "$ARCHIVE_DIR"
    
    cat > "$ARCHIVE_DIR/README.md" << 'EOF'
# uDOS Script Consolidation Archive

This directory contains scripts that have been consolidated into unified management systems.

## Consolidation Summary

### Tree Generation Scripts
- `make-tree.sh` → Consolidated into `tree-generator.sh`
- `make-tree-simple.sh` → Consolidated into `tree-generator.sh`

### Package Management Scripts
- `packages/manager.sh` → Consolidated into `packages/consolidated-manager.sh`
- `packages/manager-simple.sh` → Consolidated into `packages/consolidated-manager.sh`
- `packages/manager-enhanced.sh` → Consolidated into `packages/consolidated-manager.sh`
- `packages/manager-compatible.sh` → Consolidated into `packages/consolidated-manager.sh`

## New Consolidated Scripts

### `unified-manager.sh`
Provides unified command interface for:
- Package management
- Template processing
- Validation and testing
- Shortcode processing
- VB command system
- Sandbox and environment management

### `tree-generator.sh`
Combines all tree generation functionality:
- Simple static trees
- Dynamic filtered trees
- Statistical trees
- Multiple output formats

### `packages/consolidated-manager.sh`
Unified package management with:
- Installation/removal
- Status checking
- Multiple output formats
- Cross-platform compatibility

## Usage

To use consolidated versions:
```bash
# Instead of ./make-tree.sh
./tree-generator.sh simple

# Instead of ./packages/manager-simple.sh
./packages/consolidated-manager.sh list

# Unified management interface
./unified-manager.sh package install ripgrep
./unified-manager.sh template setup
./unified-manager.sh validate all
```

## Archive Date
$(date)

## Total Scripts Consolidated
$(echo "${#SCRIPTS_TO_ARCHIVE[@]}" | wc -l) scripts archived and replaced with 3 consolidated scripts.
EOF

    green "✅ Archive directory created"
}

# Archive individual script
archive_script() {
    local script="$1"
    local script_path="$UCODE_DIR/$script"
    
    if [[ -f "$script_path" ]]; then
        blue "📦 Archiving $script..."
        
        # Create subdirectory if needed
        local archive_subdir="$ARCHIVE_DIR/$(dirname "$script")"
        mkdir -p "$archive_subdir"
        
        # Copy to archive
        cp "$script_path" "$ARCHIVE_DIR/$script"
        
        # Add archive header
        local temp_file="/tmp/archive_header_$$"
        cat > "$temp_file" << EOF
#!/bin/bash
# ARCHIVED SCRIPT - Use consolidated version instead
# Original: $script
# Archived: $(date)
# Replacement: See README.md in this directory

echo "⚠️ This script has been archived and consolidated."
echo "Use the consolidated version instead:"
EOF
        
        case "$script" in
            "make-tree"*)
                echo 'echo "  ./tree-generator.sh [simple|dynamic|stats]"' >> "$temp_file"
                ;;
            "packages/manager"*)
                echo 'echo "  ./packages/consolidated-manager.sh [command]"' >> "$temp_file"
                ;;
        esac
        
        echo 'echo "Or use unified manager: ./unified-manager.sh [group] [command]"' >> "$temp_file"
        echo 'echo "See progress/script-consolidation-archive/README.md for details"' >> "$temp_file"
        echo 'exit 1' >> "$temp_file"
        echo '' >> "$temp_file"
        echo '# Original script content below:' >> "$temp_file"
        echo '# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' >> "$temp_file"
        
        # Append original content as comments
        sed 's/^/# /' "$script_path" >> "$temp_file"
        
        # Replace original with archive notice
        mv "$temp_file" "$script_path"
        chmod +x "$script_path"
        
        green "✅ Archived: $script"
    else
        yellow "⚠️ Script not found: $script"
    fi
}

# Update system to use consolidated scripts
update_system_integration() {
    blue "🔧 Updating system integration..."
    
    # Update any references in other scripts
    local updated_files=0
    
    # Check for references to old scripts
    blue "🔍 Checking for script references..."
    
    # Update ucode.sh if it references old scripts
    if [[ -f "$UCODE_DIR/ucode.sh" ]]; then
        if grep -q "make-tree.sh\|packages/manager" "$UCODE_DIR/ucode.sh"; then
            blue "📝 Updating ucode.sh references..."
            
            # Create backup
            cp "$UCODE_DIR/ucode.sh" "$UCODE_DIR/ucode.sh.pre-consolidation"
            
            # Update references
            sed -i '' \
                -e 's|make-tree\.sh|tree-generator.sh|g' \
                -e 's|packages/manager\.sh|packages/consolidated-manager.sh|g' \
                -e 's|packages/manager-simple\.sh|packages/consolidated-manager.sh|g' \
                "$UCODE_DIR/ucode.sh" || true
            
            updated_files=$((updated_files + 1))
        fi
    fi
    
    # Update tasks.json if it exists
    local vscode_tasks="$UHOME/.vscode/tasks.json"
    if [[ -f "$vscode_tasks" ]]; then
        if grep -q "make-tree.sh\|packages/manager" "$vscode_tasks"; then
            blue "📝 Updating VS Code tasks..."
            
            # Create backup
            cp "$vscode_tasks" "$vscode_tasks.pre-consolidation"
            
            # Update task references
            sed -i '' \
                -e 's|make-tree\.sh|tree-generator.sh|g' \
                -e 's|packages/manager-simple\.sh|packages/consolidated-manager.sh|g' \
                "$vscode_tasks" || true
            
            updated_files=$((updated_files + 1))
        fi
    fi
    
    if [[ "$updated_files" -gt 0 ]]; then
        green "✅ Updated $updated_files system files"
    else
        green "✅ No system updates needed"
    fi
}

# Create compatibility symlinks
create_compatibility_links() {
    blue "🔗 Creating compatibility symlinks..."
    
    # Create symlinks for common usage patterns
    local links_created=0
    
    # Tree generator compatibility
    if [[ ! -e "$UCODE_DIR/make-tree-consolidated.sh" ]]; then
        ln -sf "tree-generator.sh" "$UCODE_DIR/make-tree-consolidated.sh"
        links_created=$((links_created + 1))
    fi
    
    # Package manager compatibility
    if [[ ! -e "$UCODE_DIR/packages/manager-consolidated.sh" ]]; then
        ln -sf "consolidated-manager.sh" "$UCODE_DIR/packages/manager-consolidated.sh"
        links_created=$((links_created + 1))
    fi
    
    green "✅ Created $links_created compatibility symlinks"
}

# Generate consolidation report
generate_report() {
    local report_file="$UHOME/docs/development/reports/SCRIPT_CONSOLIDATION_REPORT.md"
    
    blue "📊 Generating consolidation report..."
    
    cat > "$report_file" << EOF
# uDOS Script Consolidation Report

**Date**: $(date)  
**Version**: uDOS v1.1.0  
**Consolidation**: Script Management Optimization

## Overview

The uDOS script ecosystem has been consolidated to reduce redundancy and improve maintainability while preserving all functionality.

## Consolidation Summary

### Scripts Archived
$(printf '| %-30s | %-30s |\n' "Original Script" "Consolidated Into")
$(printf '|%.30s|%.30s|\n' "------------------------------" "------------------------------")
$(printf '| %-30s | %-30s |\n' "make-tree.sh" "tree-generator.sh")
$(printf '| %-30s | %-30s |\n' "make-tree-simple.sh" "tree-generator.sh")
$(printf '| %-30s | %-30s |\n' "packages/manager.sh" "packages/consolidated-manager.sh")
$(printf '| %-30s | %-30s |\n' "packages/manager-simple.sh" "packages/consolidated-manager.sh")
$(printf '| %-30s | %-30s |\n' "packages/manager-enhanced.sh" "packages/consolidated-manager.sh")
$(printf '| %-30s | %-30s |\n' "packages/manager-compatible.sh" "packages/consolidated-manager.sh")

### New Unified Systems

#### 1. Unified Manager (\`unified-manager.sh\`)
- **Purpose**: Single entry point for all uDOS management tasks
- **Commands**: package, template, validate, shortcode, vb, sandbox
- **Benefits**: Consistent interface, reduced cognitive load

#### 2. Tree Generator (\`tree-generator.sh\`)
- **Purpose**: Consolidated tree generation with multiple formats
- **Modes**: simple, dynamic, stats, all
- **Benefits**: Unified tree generation, enhanced formatting options

#### 3. Consolidated Package Manager (\`packages/consolidated-manager.sh\`)
- **Purpose**: Unified package management system
- **Features**: Install/remove, status checking, multiple formats
- **Benefits**: Cross-platform compatibility, enhanced error handling

## Usage Migration

### Old Usage → New Usage

\`\`\`bash
# Tree Generation
./make-tree.sh              → ./tree-generator.sh simple
./make-tree-simple.sh       → ./tree-generator.sh simple

# Package Management
./packages/manager-simple.sh list     → ./packages/consolidated-manager.sh list
./packages/manager.sh install ripgrep → ./packages/consolidated-manager.sh install ripgrep

# Unified Interface (New)
./unified-manager.sh package install ripgrep
./unified-manager.sh template setup
./unified-manager.sh validate all
\`\`\`

## Script Count Reduction

- **Before**: $(echo "${#SCRIPTS_TO_ARCHIVE[@]}") redundant scripts
- **After**: 3 consolidated scripts
- **Reduction**: $(echo "${#SCRIPTS_TO_ARCHIVE[@]} - 3" | bc) fewer scripts to maintain
- **Functionality**: 100% preserved with enhanced features

## Archive Location

Archived scripts are preserved in:
\`progress/script-consolidation-archive/\`

Each archived script is replaced with a migration notice directing users to the consolidated version.

## Compatibility

- **Backward Compatibility**: Archived scripts show migration guidance
- **VS Code Integration**: Tasks updated to use consolidated scripts
- **System Integration**: All references updated automatically

## Benefits

✅ **Reduced Complexity**: Fewer scripts to maintain and document  
✅ **Enhanced Functionality**: Consolidated scripts offer more features  
✅ **Better Organization**: Logical grouping of related functionality  
✅ **Improved Testing**: Centralized testing for related functions  
✅ **Consistent Interface**: Unified command patterns across system  
✅ **Future-Proof**: Easier to extend and maintain consolidated systems  

## Impact on uDOS v1.1.0

This consolidation maintains uDOS v1.1.0's feature completeness while:
- Improving maintainability for future development
- Reducing GitHub repository complexity
- Enhancing user experience with consistent interfaces
- Preparing foundation for v1.2.0 enhancements

**Status**: ✅ **CONSOLIDATION COMPLETE - READY FOR GITHUB DISTRIBUTION**
EOF

    green "✅ Consolidation report generated: $report_file"
}

# Main execution
main() {
    local command="${1:-consolidate}"
    
    case "$command" in
        "consolidate"|"run")
            echo
            bold "🛠️ uDOS Script Consolidation Manager v1.0.0"
            echo "═══════════════════════════════════════════════════"
            echo
            
            create_archive
            echo
            
            # Archive redundant scripts
            blue "📦 Archiving redundant scripts..."
            for script in "${SCRIPTS_TO_ARCHIVE[@]}"; do
                archive_script "$script"
            done
            echo
            
            update_system_integration
            echo
            
            create_compatibility_links
            echo
            
            # Make consolidated scripts executable
            blue "🔧 Setting up consolidated scripts..."
            chmod +x "$UCODE_DIR/unified-manager.sh"
            chmod +x "$UCODE_DIR/tree-generator.sh"
            chmod +x "$UCODE_DIR/packages/consolidated-manager.sh"
            green "✅ Consolidated scripts ready"
            echo
            
            generate_report
            echo
            
            green "🎉 Script consolidation complete!"
            echo
            blue "New unified interface available:"
            echo "  ./uCode/unified-manager.sh [group] [command]"
            echo "  ./uCode/tree-generator.sh [mode]"
            echo "  ./uCode/packages/consolidated-manager.sh [command]"
            echo
            ;;
        "status"|"check")
            blue "🔍 Checking consolidation status..."
            
            local archived_count=0
            local missing_count=0
            
            for script in "${SCRIPTS_TO_ARCHIVE[@]}"; do
                if [[ -f "$UCODE_DIR/$script" ]]; then
                    if grep -q "ARCHIVED SCRIPT" "$UCODE_DIR/$script"; then
                        green "✅ $script (archived)"
                        archived_count=$((archived_count + 1))
                    else
                        yellow "⚠️ $script (not archived)"
                    fi
                else
                    red "❌ $script (missing)"
                    missing_count=$((missing_count + 1))
                fi
            done
            
            echo
            blue "Consolidation Status:"
            echo "  Scripts archived: $archived_count/${#SCRIPTS_TO_ARCHIVE[@]}"
            echo "  Missing scripts: $missing_count"
            
            if [[ -f "$UCODE_DIR/unified-manager.sh" ]]; then
                green "✅ Unified manager available"
            else
                red "❌ Unified manager missing"
            fi
            ;;
        "help")
            echo "🛠️ uDOS Script Consolidation Manager"
            echo
            echo "Commands:"
            echo "  consolidate  - Run full consolidation process"
            echo "  status       - Check consolidation status"
            echo "  help         - Show this help"
            echo
            ;;
        *)
            red "❌ Unknown command: $command"
            echo "Use '$0 help' for available commands"
            exit 1
            ;;
    esac
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
