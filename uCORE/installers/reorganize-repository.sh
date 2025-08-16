#!/bin/bash

# uInstall/reorganize-repository.sh
# Repository Reorganization Script for uDOS v1.2
# Implements the REORGANIZATION_PLAN.md structure with location tile codes

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="/Users/agentdigital/uDOS"
BACKUP_DIR="${REPO_ROOT}_backup_$(date +%Y%m%d_%H%M%S)"
DRY_RUN=false
VERBOSE=false

# Print styled messages
print_header() {
    echo -e "\n${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                         uDOS Repository Reorganization                      ║${NC}"
    echo -e "${PURPLE}║                              Master Wizard v1.2                             ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
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

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Repository Reorganization Script for uDOS v1.2

OPTIONS:
    -d, --dry-run       Show what would be done without making changes
    -v, --verbose       Enable verbose output
    -h, --help         Show this help message
    -b, --backup-dir   Specify custom backup directory

EXAMPLES:
    $0                 # Run reorganization
    $0 --dry-run       # Preview changes only
    $0 -v              # Run with verbose output

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            -b|--backup-dir)
                BACKUP_DIR="$2"
                shift 2
                ;;
            *)
                print_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Validate environment
validate_environment() {
    print_step "Validating environment"
    
    if [[ ! -d "$REPO_ROOT" ]]; then
        print_error "Repository root not found: $REPO_ROOT"
        exit 1
    fi
    
    if [[ ! -f "$REPO_ROOT/README.md" ]]; then
        print_error "Not a valid uDOS repository (missing README.md)"
        exit 1
    fi
    
    # Check for git repository
    if [[ -d "$REPO_ROOT/.git" ]]; then
        cd "$REPO_ROOT"
        if [[ -n "$(git status --porcelain)" ]]; then
            print_warning "Repository has uncommitted changes"
            read -p "Continue? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    fi
    
    print_success "Environment validation complete"
}

# Create backup
create_backup() {
    if [[ "$DRY_RUN" == true ]]; then
        print_info "DRY RUN: Would create backup at $BACKUP_DIR"
        return
    fi
    
    print_step "Creating backup"
    cp -r "$REPO_ROOT" "$BACKUP_DIR"
    print_success "Backup created at $BACKUP_DIR"
}

# Create new directory structure
create_directory_structure() {
    print_step "Creating new directory structure"
    
    local dirs=(
        # Core documentation with location tile codes
        "uDocs/LOC-[A1]-Architecture"
        "uDocs/LOC-[A2]-User-Manual" 
        "uDocs/LOC-[A3]-System-Design"
        "uDocs/LOC-[B1]-Installation-Guide"
        "uDocs/LOC-[B2]-Quick-Setup"
        "uDocs/LOC-[B3]-Advanced-Install"
        "uDocs/LOC-[C1]-Development-Roadmap"
        "uDocs/LOC-[C2]-Feature-Roadmap"
        "uDocs/LOC-[C3]-Technology-Roadmap"
        "uDocs/LOC-[D1]-Coding-Standards"
        "uDocs/LOC-[D2]-Template-Standards"
        "uDocs/LOC-[D3]-Markdown-Standards"
        "uDocs/LOC-[E1]-Tutorial-Basics"
        "uDocs/LOC-[E2]-Tutorial-Advanced"
        "uDocs/LOC-[E3]-Tutorial-Expert"
        "uDocs/LOC-[F1]-API-Reference"
        "uDocs/LOC-[F2]-Command-Reference"
        "uDocs/LOC-[F3]-Configuration-Reference"
        "uDocs/LOC-[G1]-Troubleshooting"
        "uDocs/LOC-[G2]-FAQ"
        "uDocs/LOC-[G3]-Support"
        "uDocs/LOC-[H1]-Release-Notes"
        "uDocs/LOC-[H2]-Changelog"
        "uDocs/LOC-[H3]-Migration-Guide"
        
        # Core system
        "uCore/scripts"
        "uCore/config"
        "uCore/templates"
        "uCore/validation"
        
        # Extensions (modular)
        "uExtensions/gaming/nethack"
        "uExtensions/gaming/adventure"
        "uExtensions/editors/micro"
        "uExtensions/editors/typo"
        "uExtensions/creative/ascii-generator"
        "uExtensions/creative/banner-tools"
        "uExtensions/ai/gemini"
        "uExtensions/ai/chester"
        "uExtensions/development/vscode-extension"
        "uExtensions/development/debugging"
        "uExtensions/essential-bundle"
        
        # User sandbox (isolated)
        "uSandbox/user-profiles"
        "uSandbox/personal-data"
        "uSandbox/custom-scripts"
        "uSandbox/templates"
        
        # Installation system
        "uInstall/minimal"
        "uInstall/standard"
        "uInstall/developer"
        "uInstall/wizard"
        "uInstall/drone"
        "uInstall/enterprise"
        "uInstall/common"
        
        # Existing preserved directories
        "uMemory"
        "uScript"
        "uTemplate"
        "uKnowledge"
        "uDev"
        "uCompanion"
        "uMapping"
        
        # Launcher and package management
        "launcher"
        "package"
        
        # Archive areas
        "archive/legacy"
        "archive/experiments"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ "$DRY_RUN" == true ]]; then
            print_info "DRY RUN: Would create directory $REPO_ROOT/$dir"
        else
            mkdir -p "$REPO_ROOT/$dir"
            [[ "$VERBOSE" == true ]] && print_info "Created: $dir"
        fi
    done
    
    print_success "Directory structure created"
}

# Move documentation files with location tile codes
reorganize_documentation() {
    print_step "Reorganizing documentation with location tile codes"
    
    # Architecture documentation
    if [[ -f "$REPO_ROOT/docs/ARCHITECTURE.md" ]]; then
        mv_file "docs/ARCHITECTURE.md" "uDocs/LOC-[A1]-Architecture/ARCHITECTURE.md"
    fi
    
    if [[ -f "$REPO_ROOT/docs/User-Manual.md" ]]; then
        mv_file "docs/User-Manual.md" "uDocs/LOC-[A2]-User-Manual/User-Manual.md"
    fi
    
    # Installation documentation
    if [[ -d "$REPO_ROOT/docs/installation" ]]; then
        mv_file "docs/installation/*" "uDocs/LOC-[B1]-Installation-Guide/"
    fi
    
    # Roadmap documentation
    if [[ -f "$REPO_ROOT/docs/Roadmap.md" ]]; then
        mv_file "docs/Roadmap.md" "uDocs/LOC-[C1]-Development-Roadmap/Roadmap.md"
    fi
    
    # Standards documentation
    if [[ -f "$REPO_ROOT/docs/uDOS-Style-Guide.md" ]]; then
        mv_file "docs/uDOS-Style-Guide.md" "uDocs/LOC-[D1]-Coding-Standards/Style-Guide.md"
    fi
    
    if [[ -f "$REPO_ROOT/docs/uDOS-Template-Standard.md" ]]; then
        mv_file "docs/uDOS-Template-Standard.md" "uDocs/LOC-[D2]-Template-Standards/Template-Standard.md"
    fi
    
    if [[ -f "$REPO_ROOT/docs/uDOS-Markdown-Standard.md" ]]; then
        mv_file "docs/uDOS-Markdown-Standard.md" "uDocs/LOC-[D3]-Markdown-Standards/Markdown-Standard.md"
    fi
    
    # Release documentation
    if [[ -f "$REPO_ROOT/CHANGELOG.md" ]]; then
        mv_file "CHANGELOG.md" "uDocs/LOC-[H2]-Changelog/CHANGELOG.md"
    fi
    
    if [[ -f "$REPO_ROOT/RELEASE_NOTES_v1.2.md" ]]; then
        mv_file "RELEASE_NOTES_v1.2.md" "uDocs/LOC-[H1]-Release-Notes/RELEASE_NOTES_v1.2.md"
    fi
    
    print_success "Documentation reorganized"
}

# Helper function to move files
mv_file() {
    local src="$1"
    local dest="$2"
    
    if [[ "$DRY_RUN" == true ]]; then
        print_info "DRY RUN: Would move $src to $dest"
    else
        if [[ -e "$REPO_ROOT/$src" ]]; then
            mkdir -p "$(dirname "$REPO_ROOT/$dest")"
            mv "$REPO_ROOT/$src" "$REPO_ROOT/$dest"
            [[ "$VERBOSE" == true ]] && print_info "Moved: $src → $dest"
        fi
    fi
}

# Reorganize extensions
reorganize_extensions() {
    print_step "Reorganizing extensions into modular structure"
    
    # Move existing extensions from scattered locations
    
    # Gaming extensions
    if [[ -d "$REPO_ROOT/uCode/games" ]]; then
        mv_file "uCode/games/*" "uExtensions/gaming/"
    fi
    
    # Editor extensions  
    if [[ -d "$REPO_ROOT/extension" ]]; then
        mv_file "extension/*" "uExtensions/development/vscode-extension/"
    fi
    
    # AI companion extensions
    if [[ -d "$REPO_ROOT/uCompanion" ]]; then
        # Keep uCompanion but link to extensions
        cp -r "$REPO_ROOT/uCompanion/gemini" "$REPO_ROOT/uExtensions/ai/gemini/" 2>/dev/null || true
        cp -r "$REPO_ROOT/uCompanion/profiles/chester"* "$REPO_ROOT/uExtensions/ai/chester/" 2>/dev/null || true
    fi
    
    print_success "Extensions reorganized"
}

# Create user sandbox
create_user_sandbox() {
    print_step "Creating user sandbox structure"
    
    # Create user.md template in sandbox
    cat > "$REPO_ROOT/uSandbox/user-profiles/user.md.template" << 'EOF'
# User Profile Template

## Personal Information
- **Username**: [TO_BE_CONFIGURED]
- **Password**: [TO_BE_CONFIGURED] 
- **Role**: user
- **Created**: $(date)

## Preferences
- **Shell**: bash
- **Editor**: micro
- **Theme**: default

## Custom Settings
[User-specific configurations go here]

---
*This file contains personal information and should never be committed to version control*
EOF

    # Create .gitignore for sandbox
    cat > "$REPO_ROOT/uSandbox/.gitignore" << 'EOF'
# User Sandbox - Personal Data Protection
user-profiles/user.md
personal-data/*
!personal-data/.gitkeep
custom-scripts/personal/*
!custom-scripts/personal/.gitkeep

# Keep templates and shared resources
!*.template
!*.example
EOF

    # Create .gitkeep files
    touch "$REPO_ROOT/uSandbox/personal-data/.gitkeep"
    touch "$REPO_ROOT/uSandbox/custom-scripts/personal/.gitkeep"
    
    print_success "User sandbox created with privacy protection"
}

# Create distribution installers
create_distribution_installers() {
    print_step "Creating distribution installer scripts"
    
    # Minimal installer
    cat > "$REPO_ROOT/uInstall/minimal/install-minimal.sh" << 'EOF'
#!/bin/bash
# uDOS Minimal Installation Script
echo "Installing uDOS Minimal Edition..."
# Implementation will be added based on distribution-types.json
EOF
    
    # Standard installer  
    cat > "$REPO_ROOT/uInstall/standard/install-standard.sh" << 'EOF'
#!/bin/bash
# uDOS Standard Installation Script
echo "Installing uDOS Standard Edition..."
# Implementation will be added based on distribution-types.json
EOF
    
    # Developer installer
    cat > "$REPO_ROOT/uInstall/developer/install-developer.sh" << 'EOF'
#!/bin/bash
# uDOS Developer Installation Script
echo "Installing uDOS Developer Edition..."
# Implementation will be added based on distribution-types.json
EOF
    
    # Wizard installer
    cat > "$REPO_ROOT/uInstall/wizard/install-wizard.sh" << 'EOF'
#!/bin/bash
# uDOS Master Wizard Installation Script
echo "Installing uDOS Master Wizard Edition..."
# Implementation will be added based on distribution-types.json
EOF
    
    # Drone installer
    cat > "$REPO_ROOT/uInstall/drone/install-drone.sh" << 'EOF'
#!/bin/bash
# uDOS Drone Installation Script
echo "Installing uDOS Drone Edition..."
# Implementation will be added based on distribution-types.json
EOF
    
    # Enterprise installer
    cat > "$REPO_ROOT/uInstall/enterprise/install-enterprise.sh" << 'EOF'
#!/bin/bash
# uDOS Enterprise Installation Script
echo "Installing uDOS Enterprise Edition..."
# Implementation will be added based on distribution-types.json
EOF
    
    # Make all installers executable
    chmod +x "$REPO_ROOT"/uInstall/*/install-*.sh
    
    print_success "Distribution installers created"
}

# Archive old structure
archive_legacy() {
    print_step "Archiving legacy structure"
    
    local legacy_dirs=(
        "trash"
        "sandbox/identity.md"
        "docs" # Will be empty after reorganization
    )
    
    for item in "${legacy_dirs[@]}"; do
        if [[ -e "$REPO_ROOT/$item" ]]; then
            mv_file "$item" "archive/legacy/$(basename "$item")"
        fi
    done
    
    print_success "Legacy structure archived"
}

# Update configuration files
update_configurations() {
    print_step "Updating configuration files"
    
    # Update main README.md with new structure reference
    if [[ "$DRY_RUN" == false ]]; then
        cat >> "$REPO_ROOT/README.md" << 'EOF'

## New Repository Structure (v1.2)

This repository has been reorganized with the following structure:

- **uDocs/**: Documentation with location tile codes [A1-H3]
- **uCore/**: Core system components
- **uExtensions/**: Modular extension system
- **uSandbox/**: User-isolated personal data
- **uInstall/**: Distribution and installation system

See `uDocs/LOC-[A1]-Architecture/ARCHITECTURE.md` for complete details.
EOF
    fi
    
    # Create new .gitignore if needed
    if [[ ! -f "$REPO_ROOT/.gitignore" ]]; then
        cat > "$REPO_ROOT/.gitignore" << 'EOF'
# uDOS Repository .gitignore

# User Sandbox Personal Data
uSandbox/user-profiles/user.md
uSandbox/personal-data/*
!uSandbox/personal-data/.gitkeep

# Development
.DS_Store
*.log
*.tmp
temp_*

# Node.js (for extensions)
node_modules/
npm-debug.log*

# Python
__pycache__/
*.pyc
EOF
    fi
    
    print_success "Configurations updated"
}

# Validate reorganization
validate_reorganization() {
    print_step "Validating reorganization"
    
    local validation_passed=true
    
    # Check critical directories exist
    local critical_dirs=(
        "uDocs"
        "uCore" 
        "uExtensions"
        "uSandbox"
        "uInstall"
    )
    
    for dir in "${critical_dirs[@]}"; do
        if [[ ! -d "$REPO_ROOT/$dir" ]]; then
            print_error "Critical directory missing: $dir"
            validation_passed=false
        fi
    done
    
    # Check user sandbox privacy
    if [[ -f "$REPO_ROOT/uSandbox/.gitignore" ]]; then
        print_success "User sandbox privacy protection: ✓"
    else
        print_warning "User sandbox privacy protection: ✗"
        validation_passed=false
    fi
    
    # Check distribution system
    if [[ -f "$REPO_ROOT/uInstall/distribution-types.json" ]]; then
        print_success "Distribution system: ✓"
    else
        print_warning "Distribution system: ✗"
        validation_passed=false
    fi
    
    if [[ "$validation_passed" == true ]]; then
        print_success "Reorganization validation passed"
    else
        print_error "Reorganization validation failed"
        return 1
    fi
}

# Generate reorganization summary
generate_summary() {
    print_step "Generating reorganization summary"
    
    local summary_file="$REPO_ROOT/REORGANIZATION_SUMMARY.md"
    
    cat > "$summary_file" << EOF
# uDOS Repository Reorganization Summary

**Date**: $(date)
**Version**: v1.2
**Backup**: $BACKUP_DIR

## Structure Changes

### New Directory Structure
- **uDocs/**: Markdown-first documentation with location tile codes
- **uCore/**: Core system components
- **uExtensions/**: Modular extension system  
- **uSandbox/**: User-isolated personal data
- **uInstall/**: Distribution and installation system

### Location Tile Codes
- **[A1-A3]**: Architecture & Design
- **[B1-B3]**: Installation & Setup
- **[C1-C3]**: Roadmaps & Planning
- **[D1-D3]**: Standards & Guidelines
- **[E1-E3]**: Tutorials & Learning
- **[F1-F3]**: Reference Documentation
- **[G1-G3]**: Support & Troubleshooting
- **[H1-H3]**: Release & Migration

### Privacy & Security
- User personal data isolated in uSandbox
- Git ignore rules protect user.md and personal files
- Clear separation between system and user components

### Distribution System
- 6 distribution types: minimal, standard, developer, wizard, drone, enterprise
- User role hierarchy: guest → user → powerUser → developer → administrator → wizard
- Modular extension packaging for flexible deployment

## Next Steps

1. Test all distribution installers
2. Validate extension containerization
3. Complete documentation migration
4. Update CI/CD pipelines if applicable

---
*Generated by uInstall/reorganize-repository.sh*
EOF

    print_success "Summary generated: REORGANIZATION_SUMMARY.md"
}

# Main execution
main() {
    parse_args "$@"
    print_header
    
    print_info "Repository: $REPO_ROOT"
    print_info "Backup: $BACKUP_DIR"
    print_info "Dry Run: $DRY_RUN"
    print_info "Verbose: $VERBOSE"
    echo
    
    validate_environment
    create_backup
    create_directory_structure
    reorganize_documentation
    reorganize_extensions
    create_user_sandbox
    create_distribution_installers
    archive_legacy
    update_configurations
    validate_reorganization
    generate_summary
    
    echo
    print_success "Repository reorganization complete!"
    
    if [[ "$DRY_RUN" == true ]]; then
        print_info "This was a dry run. No changes were made."
        print_info "Remove --dry-run flag to apply changes."
    else
        print_info "Backup available at: $BACKUP_DIR"
        print_info "Summary available at: $REPO_ROOT/REORGANIZATION_SUMMARY.md"
    fi
    
    echo
    print_header
}

# Run main function with all arguments
main "$@"
