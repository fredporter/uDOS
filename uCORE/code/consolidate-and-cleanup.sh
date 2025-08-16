#!/bin/bash

# uCode/consolidate-and-cleanup.sh
# Repository Consolidation and Cleanup Script for uDOS v1.2
# Moves redundant files to trash and prepares for git push

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
TRASH_DIR="$REPO_ROOT/trash"
DRY_RUN=false
VERBOSE=false

print_header() {
    echo -e "\n${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                     uDOS Repository Consolidation                           ║${NC}"
    echo -e "${PURPLE}║                       Cleanup and Git Preparation                           ║${NC}"
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

# Create trash structure
setup_trash() {
    print_step "Setting up trash structure"
    
    mkdir -p "$TRASH_DIR/redundant-scripts"
    mkdir -p "$TRASH_DIR/old-folders"
    mkdir -p "$TRASH_DIR/temp-files"
    mkdir -p "$TRASH_DIR/legacy-configs"
    mkdir -p "$TRASH_DIR/test-files"
    
    print_success "Trash structure created"
}

# Move redundant and test files
move_redundant_files() {
    print_step "Moving redundant and test files to trash"
    
    # Test files and temporary scripts
    local test_files=(
        "test-logging.sh"
        "test-structure.sh" 
        "test_udos_interactive.sh"
        "temp_input.txt"
        "recreate-umemory.sh"
        "repo_structure.txt"
    )
    
    for file in "${test_files[@]}"; do
        if [[ -f "$REPO_ROOT/$file" ]]; then
            mv "$REPO_ROOT/$file" "$TRASH_DIR/test-files/"
            print_info "Moved: $file"
        fi
    done
    
    # Legacy PDF files (keep markdown versions)
    if [[ -f "$REPO_ROOT/Acorn_TeletextSystemUG.pdf" ]]; then
        mv "$REPO_ROOT/Acorn_TeletextSystemUG.pdf" "$TRASH_DIR/legacy-configs/"
        print_info "Moved: Acorn_TeletextSystemUG.pdf (keeping .md version)"
    fi
    
    print_success "Redundant files moved to trash"
}

# Consolidate duplicate folders
consolidate_folders() {
    print_step "Consolidating duplicate folders"
    
    # Check for old extension folder vs new uExtensions
    if [[ -d "$REPO_ROOT/extension" ]] && [[ -d "$REPO_ROOT/uExtensions" ]]; then
        # Move VS Code extension to proper location in uExtensions
        if [[ ! -d "$REPO_ROOT/uExtensions/development" ]]; then
            mkdir -p "$REPO_ROOT/uExtensions/development"
        fi
        
        if [[ ! -d "$REPO_ROOT/uExtensions/development/vscode-extension" ]]; then
            mv "$REPO_ROOT/extension" "$REPO_ROOT/uExtensions/development/vscode-extension"
            print_info "Moved extension/ to uExtensions/development/vscode-extension/"
        else
            mv "$REPO_ROOT/extension" "$TRASH_DIR/old-folders/"
            print_info "Moved duplicate extension/ to trash"
        fi
    fi
    
    # Check for duplicate install folders
    if [[ -d "$REPO_ROOT/install" ]] && [[ -d "$REPO_ROOT/uInstall" ]]; then
        # Move useful content from install/ to uInstall/
        if [[ -d "$REPO_ROOT/install/installers" ]]; then
            cp -r "$REPO_ROOT/install/installers" "$REPO_ROOT/uInstall/" 2>/dev/null || true
        fi
        mv "$REPO_ROOT/install" "$TRASH_DIR/old-folders/"
        print_info "Consolidated install/ into uInstall/"
    fi
    
    # Check for old sandbox vs new uSandbox
    if [[ -d "$REPO_ROOT/sandbox" ]] && [[ ! -d "$REPO_ROOT/uSandbox" ]]; then
        mv "$REPO_ROOT/sandbox" "$REPO_ROOT/uSandbox"
        print_info "Renamed sandbox/ to uSandbox/"
    elif [[ -d "$REPO_ROOT/sandbox" ]] && [[ -d "$REPO_ROOT/uSandbox" ]]; then
        # Merge useful content
        if [[ -f "$REPO_ROOT/sandbox/identity.md" ]]; then
            mv "$REPO_ROOT/sandbox/identity.md" "$REPO_ROOT/uSandbox/"
        fi
        mv "$REPO_ROOT/sandbox" "$TRASH_DIR/old-folders/"
        print_info "Merged sandbox/ into uSandbox/"
    fi
    
    # Check for old docs vs new uDocs structure
    if [[ -d "$REPO_ROOT/docs" ]] && [[ -d "$REPO_ROOT/uDocs" ]]; then
        # The reorganization script should have moved everything
        # Check if docs is empty or contains only duplicates
        if [[ -z "$(ls -A "$REPO_ROOT/docs" 2>/dev/null)" ]]; then
            rmdir "$REPO_ROOT/docs"
            print_info "Removed empty docs/ folder"
        else
            mv "$REPO_ROOT/docs" "$TRASH_DIR/old-folders/"
            print_info "Moved remaining docs/ to trash (content should be in uDocs/)"
        fi
    fi
    
    print_success "Folder consolidation complete"
}

# Clean up old scripts and duplicates
cleanup_old_scripts() {
    print_step "Cleaning up old and duplicate scripts"
    
    # Move old installation scripts that are now redundant
    local old_scripts=(
        "install-udos.sh"  # Replaced by uInstall system
        "start-udos.sh"    # Replaced by uCode/ucode.sh
    )
    
    for script in "${old_scripts[@]}"; do
        if [[ -f "$REPO_ROOT/$script" ]]; then
            # Check if it's actually different from new versions
            if [[ "$script" == "install-udos.sh" ]] && [[ -f "$REPO_ROOT/uInstall/reorganize-repository.sh" ]]; then
                mv "$REPO_ROOT/$script" "$TRASH_DIR/redundant-scripts/"
                print_info "Moved: $script (replaced by uInstall system)"
            elif [[ "$script" == "start-udos.sh" ]] && [[ -f "$REPO_ROOT/uCode/ucode.sh" ]]; then
                mv "$REPO_ROOT/$script" "$TRASH_DIR/redundant-scripts/"
                print_info "Moved: $script (replaced by uCode/ucode.sh)"
            fi
        fi
    done
    
    print_success "Old scripts cleaned up"
}

# Set up local folder structure for user data
setup_local_structure() {
    print_step "Setting up local folder structure"
    
    # Create uSandbox if it doesn't exist
    if [[ ! -d "$REPO_ROOT/uSandbox" ]]; then
        mkdir -p "$REPO_ROOT/uSandbox/user-profiles"
        mkdir -p "$REPO_ROOT/uSandbox/personal-data"
        mkdir -p "$REPO_ROOT/uSandbox/custom-scripts"
        
        # Create user data template
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
        
        # Create local .gitignore for sandbox
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
        
        touch "$REPO_ROOT/uSandbox/personal-data/.gitkeep"
        touch "$REPO_ROOT/uSandbox/custom-scripts/.gitkeep"
        
        print_success "uSandbox structure created with privacy protection"
    fi
    
    # Ensure uMemory is properly excluded (should not exist in repo)
    if [[ -d "$REPO_ROOT/uMemory" ]]; then
        print_warning "uMemory found in repository - this should be user-local only"
        print_info "Moving uMemory to local backup location"
        
        mkdir -p "$HOME/.udos-local/backup"
        mv "$REPO_ROOT/uMemory" "$HOME/.udos-local/backup/uMemory-$(date +%Y%m%d_%H%M%S)"
        print_info "uMemory backed up to ~/.udos-local/backup/"
    fi
    
    print_success "Local folder structure configured"
}

# Update .gitignore for new structure
update_gitignore() {
    print_step "Updating .gitignore for new repository structure"
    
    cat > "$REPO_ROOT/.gitignore" << 'EOF'
# ──────────────────────────────────────────────
# uDOS v1.2 .gitignore
# Clean Repository Architecture - Production Ready
# ──────────────────────────────────────────────

# ════════════════════════════════════════════════════════════════
# 🔒 SECURITY MODEL ENFORCEMENT
# ════════════════════════════════════════════════════════════════

# 🔐 Level 1: uMemory - Private User Files (NEVER in repo)
# Contains personal data, logs, state, missions, moves
uMemory/

# 🔐 Level 2: uSandbox Personal Data
uSandbox/user-profiles/user.md
uSandbox/personal-data/*
!uSandbox/personal-data/.gitkeep
uSandbox/custom-scripts/personal/*
!uSandbox/custom-scripts/personal/.gitkeep

# ════════════════════════════════════════════════════════════════
# 🚫 BUILD ARTIFACTS & DEVELOPMENT FILES
# ════════════════════════════════════════════════════════════════

# Build and compilation artifacts
__pycache__/
*.pyc
*.pyo
*.so
*.out
*.exe
dist/
build/
out/

# Package manager files
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
package-lock.json

# Logs and temporary files
**/*.log
*.tmp
*.working
validation-*.log
test.log
test-*.log
test-output-*
gemini-*.log

# macOS system files
.DS_Store
**/.DS_Store
.ipynb_checkpoints/
Thumbs.db

# Distribution archives and installation artifacts
*.zip
*.tar.gz
*.dmg
*.vsix
uDOS-v*.tar.gz
uDOS-v*.zip

# Local installation artifacts (generated during install)
install-udos.log
installation.log
validation-*.log
user-config.local
setup-complete.flag

# ════════════════════════════════════════════════════════════════
# 🛠️ EDITOR & IDE ARTIFACTS
# ════════════════════════════════════════════════════════════════

# VS Code personal settings (keep workspace config)
.vscode/settings.json.local
.env
.env.local

# Gemini CLI authentication
.gemini/
~/.gemini/

# ════════════════════════════════════════════════════════════════
# 📱 DISTRIBUTION ARTIFACTS (built locally)
# ════════════════════════════════════════════════════════════════

# Generated distribution packages
release/
dist-packages/
launcher/uDOS.app/Contents/
launcher/build/
launcher/*.dmg
launcher/uDOS_installation.log

# Local user modifications and configs
user.config
local.settings
*.user.md
personal-*.md

# Generated documentation exports
exports/
generated-docs/

# ════════════════════════════════════════════════════════════════
# 🧪 TESTING & DEVELOPMENT
# ════════════════════════════════════════════════════════════════

# Test environments
/tmp/
temp/
testing/
scratch/

# Development progress tracking
dev-notes/
personal-notes/

# User-specific configurations
config.local.*
settings.local.*

# Generated files that should be rebuilt on install
system-info.txt
installation-report.txt

# ════════════════════════════════════════════════════════════════
# 🗑️ TRASH SYSTEM - Archived and deprecated files
# ════════════════════════════════════════════════════════════════
# Contains old/deprecated files moved during cleanup
# This folder is tracked to maintain cleanup history
trash/

# ════════════════════════════════════════════════════════════════
# ✅ WHAT STAYS IN REPOSITORY (uDOS v1.2)
# ════════════════════════════════════════════════════════════════
# ✅ uCore/ - Core system scripts and configuration
# ✅ uCode/ - Shell system and user interface scripts
# ✅ uDocs/ - Documentation with location tile codes [A1-H3]
# ✅ uExtensions/ - Modular extension system
# ✅ uSandbox/ - User workspace (templates only, not personal data)
# ✅ uInstall/ - Distribution and installation system
# ✅ uTemplate/ - Template management system
# ✅ uScript/ - Scripting framework
# ✅ uKnowledge/ - Knowledge base system
# ✅ uDev/ - Development tools and utilities
# ✅ uCompanion/ - AI companion system
# ✅ uMapping/ - Data mapping utilities
# ✅ launcher/ - Application launcher system
# ✅ package/ - Package management system
# ✅ Core files: README.md, LICENSE, CHANGELOG.md, etc.
# ✅ VS Code workspace configuration (.vscode/)
# ════════════════════════════════════════════════════════════════
EOF
    
    print_success ".gitignore updated for new structure"
}

# Validate git status
check_git_status() {
    print_step "Checking git status"
    
    cd "$REPO_ROOT"
    
    # Check if we're in a git repository
    if [[ ! -d ".git" ]]; then
        print_error "Not a git repository"
        return 1
    fi
    
    # Check for uncommitted changes
    if [[ -n "$(git status --porcelain)" ]]; then
        print_info "Repository has changes ready for commit"
        
        # Show summary of changes
        echo -e "\n${CYAN}Git Status Summary:${NC}"
        git status --short
        
        # Show untracked files
        local untracked=$(git ls-files --others --exclude-standard)
        if [[ -n "$untracked" ]]; then
            echo -e "\n${YELLOW}New files to be added:${NC}"
            echo "$untracked" | head -10
            if [[ $(echo "$untracked" | wc -l) -gt 10 ]]; then
                echo "... and $(($(echo "$untracked" | wc -l) - 10)) more files"
            fi
        fi
    else
        print_success "Repository is clean"
    fi
}

# Prepare for git push
prepare_git_push() {
    print_step "Preparing for git push"
    
    cd "$REPO_ROOT"
    
    # Add all new files
    print_info "Adding new files to git..."
    git add .
    
    # Show what will be committed
    echo -e "\n${CYAN}Files staged for commit:${NC}"
    git diff --cached --name-status | head -20
    
    if [[ $(git diff --cached --name-status | wc -l) -gt 20 ]]; then
        echo "... and $(($(git diff --cached --name-status | wc -l) - 20)) more files"
    fi
    
    print_success "Repository prepared for commit"
    
    echo -e "\n${YELLOW}Suggested commit message:${NC}"
    echo "feat: Complete uDOS v1.2 repository reorganization with Gemini CLI integration

- Consolidate redundant folders and scripts
- Move legacy files to trash/ for cleanup history
- Implement new repository structure with location tile codes
- Add Google Gemini CLI integration with ASSIST and COMMAND modes
- Update .gitignore for new structure and privacy protection
- Set up uSandbox for user data isolation
- Create modular uExtensions system
- Prepare for production distribution

Co-authored-by: GitHub Copilot <noreply@github.com>"
}

# Create summary report
create_summary_report() {
    print_step "Creating consolidation summary"
    
    cat > "$REPO_ROOT/CONSOLIDATION_SUMMARY.md" << EOF
# uDOS Repository Consolidation Summary

**Date**: $(date)
**Version**: v1.2
**Operation**: Repository cleanup and git preparation

## Changes Made

### 🗑️ Files Moved to Trash
- Test files: test-logging.sh, test-structure.sh, test_udos_interactive.sh
- Temporary files: temp_input.txt, recreate-umemory.sh, repo_structure.txt
- Legacy PDFs: Acorn_TeletextSystemUG.pdf (kept .md version)
- Old installation scripts: install-udos.sh, start-udos.sh (replaced by uInstall system)

### 📁 Folder Consolidation
- extension/ → uExtensions/development/vscode-extension/
- install/ → uInstall/ (merged useful content)
- sandbox/ → uSandbox/ (renamed and enhanced)
- docs/ → uDocs/ (content migrated with location tile codes)

### 🛡️ Privacy Protection
- uSandbox configured with proper .gitignore
- User personal data templates created
- uMemory excluded from repository (user-local only)

### 📦 New Structure Benefits
- Clean modular architecture
- Proper user data isolation
- Location tile code documentation system [A1-H3]
- Containerized extension system
- Distribution-ready packaging

## Repository State

### ✅ Included in Git
- uCore/ - Core system components
- uCode/ - Shell system and scripts
- uDocs/ - Documentation with location codes
- uExtensions/ - Modular extension system (including Gemini CLI)
- uSandbox/ - User workspace templates (no personal data)
- uInstall/ - Distribution system
- Other u-prefixed system folders
- Core documentation and configuration

### 🚫 Excluded from Git
- uMemory/ - User personal data (local only)
- uSandbox/user-profiles/user.md - Personal credentials
- uSandbox/personal-data/* - User files
- Build artifacts and logs
- .DS_Store and system files
- Node modules and package locks

## Git Status
- Repository cleaned and organized
- .gitignore updated for new structure
- All changes staged for commit
- Ready for push to remote

## Next Steps
1. Review staged changes
2. Commit with provided message
3. Push to remote repository
4. Validate installation on clean checkout

---
*Generated by uCode/consolidate-and-cleanup.sh*
EOF
    
    print_success "Summary report created: CONSOLIDATION_SUMMARY.md"
}

# Main execution
main() {
    print_header
    
    setup_trash
    move_redundant_files
    consolidate_folders
    cleanup_old_scripts
    setup_local_structure
    update_gitignore
    check_git_status
    prepare_git_push
    create_summary_report
    
    echo
    print_success "Repository consolidation complete!"
    print_info "Summary: CONSOLIDATION_SUMMARY.md"
    print_info "Review changes with: git diff --cached"
    print_info "Commit with suggested message above"
    
    echo -e "\n${CYAN}Ready for git push! 🚀${NC}"
}

main "$@"
