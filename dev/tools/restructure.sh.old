#!/bin/bash

# uDOS Root Directory Restructure Script
# Reorganizes uDOS into uCORE, uMEMORY, uKNOWLEDGE, uSANDBOX, assistant/

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "\n${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                     uDOS Root Directory Restructure                          ║${NC}"
    echo -e "${CYAN}║                  Reorganizing into Modern Architecture                       ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
check_location() {
    if [[ ! -f "README.md" ]] || [[ ! -d "uCode" ]]; then
        print_error "Please run this script from the uDOS root directory"
        exit 1
    fi
    print_success "Confirmed uDOS root directory"
}

# Create backup
create_backup() {
    print_step "Creating backup before restructure..."
    local backup_dir="../uDOS-backup-$(date +%Y%m%d-%H%M%S)"
    cp -r . "$backup_dir"
    print_success "Backup created at: $backup_dir"
}

# Create new directory structure
create_structure() {
    print_step "Creating new directory structure..."
    
    # Main directories
    mkdir -p uCORE/{bin,cache,code,config,datagets,datasets,distribution,install,launcher,templates}
    mkdir -p uMEMORY/{templates,scripts,datasets,configs,projects,extensions}
    mkdir -p uSANDBOX/{scripts,drafts,experiments}
    mkdir -p assistant
    
    print_success "New directory structure created"
}

# Migrate to uCORE
migrate_to_ucore() {
    print_step "Migrating core system files to uCORE/..."
    
    # Move core directories
    [[ -d "uCode" ]] && mv uCode uCORE/code
    [[ -d "uCore" ]] && mv uCore uCORE/system
    [[ -d "uExtensions" ]] && mv uExtensions uCORE/extensions
    [[ -d "uInstall" ]] && mv uInstall uCORE/installers
    [[ -d "uTemplate" ]] && mv uTemplate uCORE/templates
    [[ -d "package" ]] && mv package uCORE/package
    [[ -d "launcher" ]] && mv launcher uCORE/launcher
    [[ -d "docs" ]] && mv docs uCORE/docs
    [[ -d "uDev" ]] && mv uDev uCORE/development
    
    # Move mapping to datasets
    [[ -d "uMapping" ]] && mv uMapping uCORE/datasets/mapping
    
    print_success "Core files migrated to uCORE/"
}

# Setup uMEMORY
setup_umemory() {
    print_step "Setting up uMEMORY structure..."
    
    # Create README for each section
    cat > uMEMORY/README.md << 'EOF'
# uMEMORY - User Data & Customizations

This directory contains all user-generated and customized content.

## Structure
- `templates/` - Your custom templates
- `scripts/` - Your custom scripts
- `datasets/` - Your personal datasets
- `configs/` - Your configuration files
- `projects/` - Your project files
- `extensions/` - Your personal extensions

## Security
This directory is automatically excluded from core system backups
and can be backed up separately for user data protection.
EOF

    # Create placeholder files
    touch uMEMORY/templates/.gitkeep
    touch uMEMORY/scripts/.gitkeep
    touch uMEMORY/datasets/.gitkeep
    touch uMEMORY/configs/.gitkeep
    touch uMEMORY/projects/.gitkeep
    touch uMEMORY/extensions/.gitkeep
    
    print_success "uMEMORY structure created"
}

# Reorganize uKNOWLEDGE
reorganize_uknowledge() {
    print_step "Reorganizing uKNOWLEDGE..."
    
    if [[ -d "uKnowledge" ]]; then
        # Rename to match new convention
        mv uKnowledge uKNOWLEDGE
        
        # Update README
        cat > uKNOWLEDGE/README.md << 'EOF'
# uKNOWLEDGE - Shared Public Knowledge Bank

**Managed by Wizard | Read-Only in Production | Editable in Dev Mode**

This directory contains the shared public knowledge base that powers
uDOS intelligence and provides context for AI companions.

## Access Levels
- **Production**: Read-only access
- **Dev Mode**: Full edit access for Wizards
- **User Mode**: Read-only with suggestion system

## Content
- System architecture documentation
- Best practices and patterns
- Reference materials
- Shared datasets and examples
EOF
        
        print_success "uKNOWLEDGE reorganized"
    else
        print_warning "uKnowledge directory not found"
    fi
}

# Consolidate uSANDBOX
consolidate_usandbox() {
    print_step "Consolidating uSANDBOX..."
    
    # Move existing uSandbox content
    if [[ -d "uSandbox" ]]; then
        cp -r uSandbox/* uSANDBOX/ 2>/dev/null || true
        rm -rf uSandbox
    fi
    
    # Move uScript to sandbox
    if [[ -d "uScript" ]]; then
        cp -r uScript/* uSANDBOX/scripts/ 2>/dev/null || true
        rm -rf uScript
    fi
    
    # Create user.md
    cat > uSANDBOX/user.md << 'EOF'
# User Workspace

**Personal sandbox for experiments, drafts, and development**

## About This Space
This is your personal workspace within uDOS. Use it for:
- Experimenting with new ideas
- Drafting scripts and templates
- Testing configurations
- Personal notes and documentation

## Structure
- `scripts/` - Your experimental scripts
- `drafts/` - Work-in-progress files
- `experiments/` - Testing and prototyping
- `user.md` - This file (your personal notes)

## Privacy
Files in uSANDBOX are excluded from system backups and can be
configured for complete privacy or selective sharing.

---

## Your Notes
Add your personal notes, todo lists, and project ideas below:

### Current Projects
- [ ] 

### Ideas & Todo
- [ ] 

### Learning Notes
- 

EOF

    # Create structure
    mkdir -p uSANDBOX/{scripts,drafts,experiments}
    touch uSANDBOX/scripts/.gitkeep
    touch uSANDBOX/drafts/.gitkeep
    touch uSANDBOX/experiments/.gitkeep
    
    print_success "uSANDBOX consolidated"
}

# Setup assistant
setup_assistant() {
    print_step "Setting up assistant/ (AI companion system)..."
    
    if [[ -d "uCompanion" ]]; then
        cp -r uCompanion/* assistant/ 2>/dev/null || true
        rm -rf uCompanion
        
        # Update README
        cat > assistant/README.md << 'EOF'
# Assistant - AI Companion System

**Google Gemini CLI Integration & uDOS Intelligence**

## Components
- **Gemini CLI**: Natural language interface
- **Context System**: uDOS project awareness
- **Reasoning Engine**: Intelligent assistance
- **Profiles**: Different AI personalities

## Usage
```bash
# Start general assistant
./uCORE/code/ucode.sh assistant

# Start specific modes
./uCORE/code/ucode.sh assist    # Development assistance
./uCORE/code/ucode.sh command   # Natural language commands
```

## Files
- `gemini/` - Gemini CLI integration
- `context/` - Project context system
- `profiles/` - AI personality profiles
- `reasoning/` - Intelligence frameworks
EOF

        print_success "Assistant system configured"
    else
        # Create basic structure
        mkdir -p assistant/{gemini,context,profiles,reasoning}
        touch assistant/README.md
        print_warning "uCompanion not found, created basic assistant structure"
    fi
}

# Update references and paths
update_references() {
    print_step "Updating file references and paths..."
    
    # Update main ucode.sh if it exists
    if [[ -f "uCORE/code/ucode.sh" ]]; then
        # Update paths in the main script
        sed -i.bak 's|uExtensions/|uCORE/extensions/|g' uCORE/code/ucode.sh
        sed -i.bak 's|uTemplate/|uCORE/templates/|g' uCORE/code/ucode.sh
        sed -i.bak 's|uCompanion/|assistant/|g' uCORE/code/ucode.sh
        rm uCORE/code/ucode.sh.bak 2>/dev/null || true
    fi
    
    # Update .gitignore
    if [[ -f ".gitignore" ]]; then
        cat >> .gitignore << 'EOF'

# User data directories
uMEMORY/
uSANDBOX/user-data/
uSANDBOX/experiments/
EOF
    fi
    
    print_success "References updated"
}

# Update documentation
update_documentation() {
    print_step "Updating documentation..."
    
    # Create new root README
    cat > README.md << 'EOF'
# uDOS v1.2 - Universal Data Operating System
**Master Wizard Edition with Modern Architecture**

## 🏗️ Architecture

### Directory Structure
```
uDOS/
├── uCORE/          # Core system files (read-only)
├── uMEMORY/        # User data & customizations  
├── uKNOWLEDGE/     # Shared knowledge bank
├── uSANDBOX/       # User workspace & drafts
└── assistant/      # AI companion system
```

### Components

#### 🔧 uCORE/ - Core System
- **code/**: Main uDOS scripts and logic
- **system/**: Core system files
- **extensions/**: System extensions
- **installers/**: Installation systems
- **templates/**: Core templates
- **docs/**: System documentation

#### 💾 uMEMORY/ - User Data
- **templates/**: Your custom templates
- **scripts/**: Your custom scripts
- **datasets/**: Your datasets
- **configs/**: Your configurations
- **projects/**: Your projects

#### 📚 uKNOWLEDGE/ - Knowledge Bank
- Shared public knowledge (Wizard managed)
- Read-only in production
- Editable in Dev mode

#### 🧪 uSANDBOX/ - User Workspace
- **user.md**: Your personal notes
- **scripts/**: Experimental scripts
- **drafts/**: Work in progress
- **experiments/**: Testing area

#### 🤖 assistant/ - AI Companion
- Google Gemini CLI integration
- Natural language interface
- Context-aware assistance

## 🚀 Quick Start

```bash
# Start uDOS
./uCORE/code/ucode.sh

# Start AI assistant
./uCORE/code/ucode.sh assistant

# Check system
./uCORE/code/check.sh all
```

## 📖 Documentation
- [Installation Guide](uCORE/docs/installation/)
- [User Manual](uCORE/docs/user/)
- [Development Guide](uCORE/docs/development/)

---
*uDOS - Where Data Meets Intelligence* ✨
EOF

    print_success "Documentation updated"
}

# Clean up old directories
cleanup() {
    print_step "Cleaning up old directories..."
    
    # Remove empty directories
    [[ -d "trash" ]] && rm -rf trash
    
    # Remove any remaining empty directories
    find . -name ".DS_Store" -delete 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Test functionality
test_functionality() {
    print_step "Testing restructured system..."
    
    # Check if main script exists and is executable
    if [[ -x "uCORE/code/ucode.sh" ]]; then
        print_success "Main ucode.sh found and executable"
    else
        print_warning "Main script may need path updates"
    fi
    
    # Check directory structure
    for dir in uCORE uMEMORY uKNOWLEDGE uSANDBOX assistant; do
        if [[ -d "$dir" ]]; then
            print_success "$dir/ directory created"
        else
            print_error "$dir/ directory missing"
        fi
    done
}

# Main execution
main() {
    print_header
    
    echo -e "${YELLOW}This will restructure the uDOS root directory.${NC}"
    echo -e "${YELLOW}A backup will be created automatically.${NC}"
    echo ""
    read -p "Continue with restructure? [y/N]: " confirm
    
    if [[ "$confirm" != "y" ]] && [[ "$confirm" != "Y" ]]; then
        echo "Restructure cancelled."
        exit 0
    fi
    
    echo ""
    check_location
    create_backup
    create_structure
    migrate_to_ucore
    setup_umemory
    reorganize_uknowledge
    consolidate_usandbox
    setup_assistant
    update_references
    update_documentation
    cleanup
    test_functionality
    
    echo -e "\n${GREEN}🎉 uDOS restructure completed successfully!${NC}"
    echo -e "${CYAN}New architecture:${NC}"
    echo "├── uCORE/      - Core system files"
    echo "├── uMEMORY/    - User data & customizations"
    echo "├── uKNOWLEDGE/ - Shared knowledge bank"
    echo "├── uSANDBOX/   - User workspace"
    echo "└── assistant/  - AI companion system"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Test functionality: ./uCORE/code/ucode.sh"
    echo "2. Review configuration files"
    echo "3. Update any custom scripts with new paths"
}

# Handle command line arguments
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    echo "uDOS Root Directory Restructure Script"
    echo ""
    echo "Usage: $0 [--help|--dry-run]"
    echo ""
    echo "Options:"
    echo "  --help     Show this help"
    echo "  --dry-run  Show what would be done without making changes"
    echo ""
    echo "This script reorganizes uDOS into a modern architecture:"
    echo "- uCORE/      Core system files"
    echo "- uMEMORY/    User data & customizations"
    echo "- uKNOWLEDGE/ Shared knowledge bank"
    echo "- uSANDBOX/   User workspace"
    echo "- assistant/  AI companion system"
    exit 0
elif [[ "${1:-}" == "--dry-run" ]]; then
    echo "DRY RUN - Would perform these actions:"
    echo "1. Create backup"
    echo "2. Create new directory structure"
    echo "3. Move uCode → uCORE/code/"
    echo "4. Move uExtensions → uCORE/extensions/"
    echo "5. Move uTemplate → uCORE/templates/"
    echo "6. Move docs → uCORE/docs/"
    echo "7. Rename uKnowledge → uKNOWLEDGE/"
    echo "8. Consolidate uSandbox + uScript → uSANDBOX/"
    echo "9. Rename uCompanion → assistant/"
    echo "10. Update all references and documentation"
    exit 0
else
    main "$@"
fi
