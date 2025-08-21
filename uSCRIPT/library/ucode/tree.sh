#!/bin/bash
# uDOS Tree Generator - Repository Structure Documentation
# Generates comprehensive repository structure with modular architecture
# Usage: tree [generate|view|help]

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
OUTPUT_FILE="$UDOS_ROOT/repo_structure.txt"
VERSION="v1.3"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Generate repository structure documentation
generate_repository_structure() {
    echo -e "${CYAN}🌳 Generating uDOS repository structure documentation...${NC}"
    
    # Count directories and files for statistics
    local dir_count=$(find "$UDOS_ROOT" -type d | wc -l | tr -d ' ')
    local file_count=$(find "$UDOS_ROOT" -type f | wc -l | tr -d ' ')
    
    # Start generating the structure file
    cat > "$OUTPUT_FILE" << EOF
# uDOS Repository Structure
*Generated: $(date)*  
*Version: $VERSION*  
*Root: $UDOS_ROOT*

## Repository Overview
This is the complete uDOS (Universal Development Operating System) repository structure.
Total directories: $dir_count | Total files: $file_count

## Directory Structure

EOF
    
    # Generate directory structure using tree command or find fallback
    if command -v tree >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Using tree command for structure generation${NC}"
        echo "\`\`\`" >> "$OUTPUT_FILE"
        tree -a -I '.git|node_modules|*.log|*.tmp' "$UDOS_ROOT" >> "$OUTPUT_FILE"
        echo "\`\`\`" >> "$OUTPUT_FILE"
    else
        echo -e "${YELLOW}⚠️  tree command not found, using find fallback${NC}"
        echo "\`\`\`" >> "$OUTPUT_FILE"
        generate_with_find_command >> "$OUTPUT_FILE"
        echo "\`\`\`" >> "$OUTPUT_FILE"
    fi
    
    # Add comprehensive documentation sections
    write_architecture_overview
    write_file_naming_conventions
    write_security_model
    write_system_statistics "$dir_count" "$file_count"
    write_footer
    
    echo -e "${GREEN}✅ Repository structure generated: $OUTPUT_FILE${NC}"
    echo -e "${CYAN}📊 Scanned $dir_count directories and $file_count files${NC}"
    
    # Offer to view the generated file
    echo ""
    read -p "View the generated structure? [Y/n]: " view_choice
    view_choice=$(echo "$view_choice" | tr '[:upper:]' '[:lower:]')
    if [[ "$view_choice" != "n" ]]; then
        echo ""
        view_structure
    fi
}

# Generate structure using find command (fallback)
generate_with_find_command() {
    (
        cd "$UDOS_ROOT"
        echo "$(basename "$UDOS_ROOT")/"
        
        # Generate ASCII tree structure with proper indentation and tree characters
        find . -type d -name '.git' -prune -o -type d -print | 
        grep -v '^\.$' |
        sed 's|^\./||' | 
        sort | 
        while IFS= read -r dir; do
            if [ -z "$dir" ]; then continue; fi
            
            # Count directory depth
            depth=$(echo "$dir" | tr -cd '/' | wc -c)
            dirname=$(basename "$dir")
            
            # Build tree prefix based on depth
            prefix=""
            for ((i=0; i<depth; i++)); do
                if [ $i -eq $((depth-1)) ]; then
                    prefix="${prefix}├── "
                else
                    prefix="${prefix}│   "
                fi
            done
            
            echo "$prefix$dirname/"
        done
        
        echo ""
        echo "📄 Key configuration files:"
        find . -maxdepth 2 -type f \( -name "*.md" -o -name "*.json" -o -name "*.yml" -o -name "*.yaml" \) |
        grep -v '.git' |
        sort |
        head -15 |
        while IFS= read -r file; do
            filename=$(echo "$file" | sed 's|^\./||')
            echo "├── 📄 $filename"
        done
        
        echo ""
        echo "🔧 Main executable scripts:"
        find . -maxdepth 3 -type f -name "*.sh" -perm +111 |
        grep -v '.git' |
        head -15 |
        sort |
        while IFS= read -r file; do
            filename=$(echo "$file" | sed 's|^\./||')
            echo "├── 🔧 $filename"
        done
        
        echo ""
        echo "📁 Directory summary (first 3 levels):"
        find . -maxdepth 3 -type d -name '.git' -prune -o -type d -print |
        grep -v '^\.$' |
        sed 's|^\./||' |
        sort |
        head -30 |
        while IFS= read -r dir; do
            depth=$(echo "$dir" | tr -cd '/' | wc -c)
            if [ $depth -le 2 ]; then
                dirname=$(basename "$dir")
                indent=""
                for ((i=0; i<depth; i++)); do
                    indent="$indent  "
                done
                echo "├──$indent📁 $dirname/"
            fi
        done
    )
}

# Write architecture overview
write_architecture_overview() {
    cat >> "$OUTPUT_FILE" << 'EOF'

## System Architecture Overview

### Multi-Role Framework
uDOS supports a 6-tier installation hierarchy:
- **Level 0**: drone (Basic automation, read-only)
- **Level 1**: imp (Script execution, sandbox access)
- **Level 2**: ghost (Advanced scripting, memory access)
- **Level 3**: sorcerer (System administration, core access)
- **Level 4**: tomb (Archive management, backup access)
- **Level 5**: wizard (Full development, all access)

### Core Components

#### uCORE/ - Core System
- **bin/**: Essential executables and utilities
- **code/**: Core system scripts and modules
- **mapping/**: uMAP location and navigation system
- **templates/**: System configuration templates
- **launcher/**: Application launch framework
- **distribution/**: Multi-platform deployment assets

#### uMEMORY/ - User Memory System
- **user/**: User data with uHEX filename convention
  - missions/: uTASK-uHEXcode-Title.md (mission tracking)
  - milestones/: uTASK-uHEXcode-Title.md (achievement records)
  - moves/: uLOG-uHEXcode-Title.md (activity logs)
  - legacy/: uDOC-uHEXcode-Title.md (archived content)
- **system/**: Core system memory and session data
- **templates/**: Memory structure templates

#### wizard/ - Development Environment (Level 5)
- **vscode/**: VS Code workspace and extensions
- **notes/**: Development documentation (uDEV/uDOC format)
- **workflows/**: Development workflow automation
- **sessions/**: Development session tracking
- **analytics/**: Development metrics and insights

#### uSCRIPT/ - Script Management
- **library/**: Modular script library
- **extensions/**: Enhanced functionality modules
- **runtime/**: Script execution environment
- **templates/**: Script generation templates

#### sandbox/ - User Workspace
- **user/**: Active development and experimentation
- **scripts/**: User-created scripts
- **tasks/**: Task automation and scheduling

#### uKNOWLEDGE/ - Knowledge Base
- Shared resources and documentation
- Community-contributed content
- Tutorial and learning materials

#### docs/ - Documentation System
- **technical/**: Technical documentation
- **user-guides/**: End-user documentation
- **development/**: Development guidelines
- **reference/**: API and system references

EOF
}

# Write file naming conventions
write_file_naming_conventions() {
    cat >> "$OUTPUT_FILE" << 'EOF'

## File Naming Conventions

### uHEX Naming System
All user files follow standardized uHEX naming patterns:

#### Mission Files (uTASK)
- **Format**: `uTASK-uHEXcode-Title.md`
- **Purpose**: Mission tracking, objectives, milestones
- **Example**: `uTASK-F8A4B2E1-Learn-uScript-Advanced-Features.md`

#### Activity Logs (uLOG)
- **Format**: `uLOG-uHEXcode-Title.md` or `uLOG-YYYYMMDD-Title.md`
- **Purpose**: Session logs, move tracking, activity records
- **Example**: `uLOG-E4F5A6B7-session-20250821.md`

#### Data Files (uDATA)
- **Format**: `uDATA-YYYYMMDD-Title.json`
- **Purpose**: Structured data, patterns, configurations
- **Example**: `uDATA-20250821-move-patterns.json`

#### Documentation (uDOC)
- **Format**: `uDOC-uHEXcode-Title.md`
- **Purpose**: Documentation, legacy archives, reports
- **Example**: `uDOC-7A8B9C0D-Development-Notes.md`

#### Development Files (uDEV)
- **Format**: `uDEV-uHEXcode-Title.md`
- **Purpose**: Development notes, session logs, system documentation
- **Example**: `uDEV-E8012004-System-Implementation.md`

### uHEX Code Generation
- **Length**: 8 characters (uppercase hexadecimal)
- **Generation**: `openssl rand -hex 4 | tr '[:lower:]' '[:upper:]'`
- **Purpose**: Unique identification and temporal encoding

EOF
}

# Write security model
write_security_model() {
    cat >> "$OUTPUT_FILE" << 'EOF'

## Security Model

### Multi-Level Access Control
Different installation levels have varying access to system components:

#### Distribution Exclusions
The following are excluded from standard distribution packages:
- **wizard/**: Full development environment (Level 5 only)
- **uMEMORY/user/**: Personal user data and memories
- **sandbox/user/**: Personal development workspace
- **Sensitive configuration files**: API keys, personal settings

#### Role-Based File Access
- **drone (Level 0)**: Read-only access to public documentation
- **imp (Level 1)**: Execute scripts, access sandbox
- **ghost (Level 2)**: Advanced scripting, limited memory access
- **sorcerer (Level 3)**: System administration, core access
- **tomb (Level 4)**: Archive management, backup systems
- **wizard (Level 5)**: Full system access, development tools

### File Permissions
- **Executable scripts**: 755 permissions for system scripts
- **User data**: 600-644 permissions for personal files
- **Configuration**: 644 permissions for system configs
- **Sensitive data**: 600 permissions, user-only access

EOF
}

# Write system statistics
write_system_statistics() {
    local dir_count="$1"
    local file_count="$2"
    
    cat >> "$OUTPUT_FILE" << EOF

## System Statistics

### Repository Metrics
- **Total Directories**: $dir_count
- **Total Files**: $file_count
- **Generated**: $(date)
- **Version**: $VERSION

### Directory Breakdown
$(find "$UDOS_ROOT" -maxdepth 1 -type d | wc -l | sed 's/^/- Root level directories: /')
$(find "$UDOS_ROOT/uCORE" -type d 2>/dev/null | wc -l | sed 's/^/- uCORE directories: /' || echo "- uCORE directories: 0")
$(find "$UDOS_ROOT/uMEMORY" -type d 2>/dev/null | wc -l | sed 's/^/- uMEMORY directories: /' || echo "- uMEMORY directories: 0")
$(find "$UDOS_ROOT/uSCRIPT" -type d 2>/dev/null | wc -l | sed 's/^/- uSCRIPT directories: /' || echo "- uSCRIPT directories: 0")
$(find "$UDOS_ROOT/wizard" -type d 2>/dev/null | wc -l | sed 's/^/- wizard directories: /' || echo "- wizard directories: 0")

### File Type Distribution
$(find "$UDOS_ROOT" -name "*.sh" -type f | wc -l | sed 's/^/- Shell scripts: /')
$(find "$UDOS_ROOT" -name "*.md" -type f | wc -l | sed 's/^/- Markdown files: /')
$(find "$UDOS_ROOT" -name "*.json" -type f | wc -l | sed 's/^/- JSON files: /')
$(find "$UDOS_ROOT" -name "*.yml" -o -name "*.yaml" -type f | wc -l | sed 's/^/- YAML files: /')

EOF
}

# Write footer
write_footer() {
    cat >> "$OUTPUT_FILE" << EOF

---

*This repository structure was generated automatically by the uDOS TREE command.*  
*For more information about uDOS, visit: https://github.com/fredporter/uDOS*  
*Last updated: $(date)*

EOF
}

# View existing structure
view_structure() {
    if [[ -f "$OUTPUT_FILE" ]]; then
        if command -v less >/dev/null 2>&1; then
            less "$OUTPUT_FILE"
        elif command -v more >/dev/null 2>&1; then
            more "$OUTPUT_FILE"
        else
            cat "$OUTPUT_FILE"
        fi
    else
        echo -e "${RED}❌ Repository structure file not found.${NC}"
        echo -e "${YELLOW}💡 Run 'tree generate' to create it.${NC}"
        return 1
    fi
}

# Show help
show_tree_help() {
    cat << EOF

🌳 TREE Command - Repository Structure Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
  tree           - Generate repository structure documentation
  tree generate  - Same as tree (explicit)
  tree view      - View existing structure documentation
  tree help      - Show this help

Description:
Generates comprehensive repository structure documentation including:
  • Complete directory tree - All folders with descriptions
  • Multi-installation overview - 6-tier role hierarchy
  • Security model - What's included vs excluded from distribution
  • File naming conventions - uHEX filename system and standards
  • System statistics - Current directory/file counts

Output:
  Creates $OUTPUT_FILE in the uDOS root directory
  Automatically detects available tools (tree vs find commands)
  Updates timestamps and statistics on each generation

💡 Tip: Run 'tree' after major structural changes to keep documentation current

Examples:
  ucode tree                    # Generate structure documentation
  ucode tree generate           # Same as above (explicit)
  ucode tree view               # View existing documentation
  ucode tree help               # Show this help

EOF
}

# Main function
main() {
    local command="${1:-generate}"
    
    case "$command" in
        "generate"|"update"|"")
            generate_repository_structure
            ;;
        "view"|"show"|"cat")
            view_structure
            ;;
        "help"|"-h"|"--help")
            show_tree_help
            ;;
        *)
            echo -e "${RED}❌ Unknown tree command: $command${NC}"
            show_tree_help
            return 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
