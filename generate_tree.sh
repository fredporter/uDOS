#!/bin/bash

# uDOS System Tree Generator v1.3
# Generates comprehensive repository structure documentation

set -euo pipefail

# Configuration
readonly OUTPUT_FILE="repo_structure.txt"
readonly TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
readonly VERSION="1.3"

# Colors for terminal output
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Generate comprehensive tree structure
generate_tree() {
    log "Generating uDOS v$VERSION repository structure..."
    
    cat > "$OUTPUT_FILE" << EOF
# uDOS v$VERSION Repository Structure
Generated: $TIMESTAMP

## Repository Overview
\`\`\`
$(pwd | sed 's|.*/||')/ - uDOS Universal Development Operating System
├── Core Architecture & Documentation
├── Extension System & Development Tools  
├── User Memory & Workspace Management
└── Installation & Distribution System
\`\`\`

## Complete Directory Structure

EOF

    # Use tree if available, otherwise use find
    if command -v tree >/dev/null 2>&1; then
        log "Using tree command for structure generation..."
        echo '```' >> "$OUTPUT_FILE"
        tree -a -I '.git|node_modules|__pycache__|*.pyc|.DS_Store' -L 4 >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
    else
        log "Using find command for structure generation..."
        echo '```' >> "$OUTPUT_FILE"
        find . -type d -not -path "./.git*" -not -path "./node_modules*" -not -path "./__pycache__*" | \
        head -100 | \
        sort | \
        sed 's|^\./||' | \
        awk '{
            depth = gsub(/\//, "/")
            indent = ""
            for(i=0; i<depth; i++) indent = indent "    "
            name = $0
            gsub(/.*\//, "", name)
            if(depth == 0) print name "/"
            else print indent "├── " name "/"
        }' >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
    fi

    # Add detailed folder descriptions
    cat >> "$OUTPUT_FILE" << 'EOF'

## Folder Descriptions

### Core System (`uCORE/`)
- **`code/`** - Core utilities and micro-syntax definitions
- **`datasets/`** - Location, mapping, and system data files
- **`extensions/`** - Extension development templates and VS Code integration
- **`launcher/`** - Platform-specific application launchers
- **`scripts/`** - Core system maintenance and utility scripts
- **`templates/`** - System templates for forms, variables, and configurations

### Development Environment (`wizard/`)
- **`tools/`** - Development utilities and script executors
- **`workflows/`** - Automated development workflow definitions
- **`vscode/`** - VS Code integration and configuration
- **`logs/`** - Development session logs (gitignored)
- **`reports/`** - Generated development reports

### Memory System (`uMEMORY/`)
- **`datasets/`** - User-specific data collections
- **`forms/`** - User interaction templates
- **`missions/`** - Task and goal management
- **`state/`** - System state persistence
- **`user/`** - Personal user configurations

### User Workspace (`sandbox/`)
- **`tasks/`** - Task management and templates
- **`scripts/`** - User development scripts
- **`experiments/`** - Development experimentation area
- **`test-deployment/`** - Testing environments

### Documentation (`docs/`)
- **Core documentation, architecture guides, and user manuals**
- **Style guides and development standards**
- **API documentation and integration guides**

### Extension System (`uExtensions/`)
- **`ai/`** - AI integration extensions (Gemini CLI, etc.)
- **Extension registry and management**

### Installation (`install/` & `uInstall/`)
- **Platform-specific installation scripts**
- **Distribution configurations and user roles**
- **System setup and deployment tools**

### Development Code (`uCode/`)
- **`micro-syntax/`** - Language syntax definitions
- **`packages/`** - Installable component packages
- **Core development utilities and scripts**

### Templates (`uTemplate/`)
- **System-wide template definitions**
- **Project scaffolding and boilerplate code**

## File Naming Conventions

### Core System Files
- **Scripts**: `kebab-case.sh` (e.g., `cleanup-filenames.sh`)
- **Configs**: `kebab-case.json` (e.g., `template-system-config.json`)
- **Data**: `camelCase.json` (e.g., `locationMap.json`, `timezoneMap.json`)

### Log Files
- **Format**: `uLOG-YYYYMMDD-HHMM-TZ-TYPE.md`
- **Example**: `uLOG-20250817-1045-28-00SY01.md`
- **Components**:
  - `YYYYMMDD-HHMM`: Timestamp
  - `TZ`: Timezone code (28 = UTC+8)
  - `TYPE`: Operation type code

### Documentation
- **Guides**: `TITLE-Guide.md` (e.g., `USER-GUIDE.md`)
- **Standards**: `TITLE-Standard.md` (e.g., `Template-Standard.md`)
- **Architecture**: `ARCHITECTURE.md`, `ROADMAP.md`

### Memory System
- **Missions**: `NNN-mission-name.md` (e.g., `001-welcome-mission.md`)
- **State files**: `snake_case.conf` (e.g., `terminal_size.conf`)
- **User data**: `user-*.md` format

## Security Model

### Public Repository (uDOS Core)
- ✅ Core system architecture
- ✅ Documentation and guides  
- ✅ Extension framework
- ✅ Installation tools
- ✅ Development utilities

### Private/Local Only (.gitignored)
- 🔒 `uMEMORY/` - User personal data
- 🔒 `wizard/logs/` - Development session logs
- 🔒 `sandbox/user.md` - Personal workspace files
- 🔒 `.vscode/` - Editor configurations
- 🔒 Authentication tokens and local configs

## Extension Architecture

The uDOS v1.3 extension system provides:
- **Modular plugin architecture**
- **VS Code integration templates**
- **AI service integrations (Gemini CLI)**
- **Custom syntax highlighting**
- **Development workflow automation**

---

*Generated by uDOS Tree Generator v1.3*  
*Repository: $(git remote get-url origin 2>/dev/null || echo "Local repository")*  
*Branch: $(git branch --show-current 2>/dev/null || echo "Unknown")*  
*Last Updated: $TIMESTAMP*
EOF

    success "Repository structure generated: $OUTPUT_FILE"
}

# Show current directory info
show_info() {
    log "Repository Information:"
    echo "  📁 Location: $(pwd)"
    echo "  🌿 Branch: $(git branch --show-current 2>/dev/null || echo "Not a git repository")"
    echo "  📊 Folders: $(find . -type d -not -path "./.git*" | wc -l | tr -d ' ') directories"
    echo "  📄 Files: $(find . -type f -not -path "./.git*" | wc -l | tr -d ' ') files"
}

# Main execution
main() {
    show_info
    echo ""
    generate_tree
    echo ""
    log "Repository structure documentation complete!"
    echo ""
    echo -e "${YELLOW}📖 View the generated structure:${NC}"
    echo "   cat $OUTPUT_FILE"
    echo ""
    echo -e "${YELLOW}🔄 To regenerate:${NC}"
    echo "   ./generate_tree.sh"
}

# Execute main function
main "$@"
