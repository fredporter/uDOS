#!/bin/bash
# uDOS v1.0 Clean Distribution Package Preparation
# Implements proper security model separation

set -euo pipefail

# Configuration
VERSION="v1.0.0"
CLEAN_DIR="./uDOS-clean-dist"
TEMP_DIR="./temp-clean"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║              🧹 uDOS v1.0 CLEAN DISTRIBUTION                    ║"
    echo "║                Security Model Implementation                     ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Create clean distribution structure
create_clean_structure() {
    log_info "Creating clean distribution structure..."
    
    # Remove existing clean directory
    if [[ -d "$CLEAN_DIR" ]]; then
        rm -rf "$CLEAN_DIR"
    fi
    
    mkdir -p "$CLEAN_DIR"
    mkdir -p "$TEMP_DIR"
    
    log_success "Clean directories created"
}

# Copy core system files (what stays in repository)
copy_core_system() {
    log_info "Copying core system files..."
    
    # Core directories - these stay in repo
    local core_dirs=(
        "uCode"
        "uKnowledge"
        "uScript"
        "uTemplate"
        ".vscode"
        "roadmap"
        "launcher"
        "docs"
    )
    
    for dir in "${core_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            cp -r "$dir" "$CLEAN_DIR/"
            log_success "Copied: $dir/"
        else
            log_warning "Directory not found: $dir"
        fi
    done
    
    # Core files
    local core_files=(
        "README.md"
        "CHANGELOG.md"
        "LICENSE"
        "start-udos.sh"
        "install-udos.sh"
        "build-macos-app.sh"
        "prepare-release.sh"
        "validate-comprehensive.sh"
        "DISTRIBUTION_GUIDE.md"
        "WIZARD_INSTALLATION_STRATEGY.md"
        ".gitignore"
        "docker-compose.yml"
        "Dockerfile"
        "repo_structure.txt"
    )
    
    for file in "${core_files[@]}"; do
        if [[ -f "$file" ]]; then
            cp "$file" "$CLEAN_DIR/"
            log_success "Copied: $file"
        else
            log_warning "File not found: $file"
        fi
    done
}

# Create structure documentation for excluded directories
create_structure_docs() {
    log_info "Creating structure documentation for excluded directories..."
    
    # uMemory structure placeholder
    mkdir -p "$CLEAN_DIR/uMemory"
    cat > "$CLEAN_DIR/uMemory/README.md" << 'EOF'
# uMemory - Private User Directory

This directory is created automatically during uDOS installation and contains all user-specific data.

**🔒 SECURITY LEVEL 1: PRIVATE USER FILES**

## Structure Created During Installation

```
uMemory/
├── user/           # User configurations (wizard/sorcerer/ghost/imp)
├── sandbox/        # Development and testing environments  
├── state/          # System state and session data
├── logs/           # System and user activity logs
├── missions/       # User-created mission files
├── moves/          # User-created move files
├── milestones/     # User progress tracking
├── scripts/        # User automation scripts
├── templates/      # User-customized templates
└── generated/      # Auto-generated content
```

## Data Sovereignty

Users control data sharing through two options:
- **explicit**: Private, never shared (default)
- **public**: User opts-in to share specific content

## Privacy Protection

- ✅ Never included in git repository
- ✅ Local filesystem permissions enforced
- ✅ No automatic cloud synchronization
- ✅ User controls all sharing decisions

*This directory will be created with appropriate permissions when you run the uDOS installer.*
EOF
    
    # uExtension structure placeholder  
    mkdir -p "$CLEAN_DIR/uExtension"
    cat > "$CLEAN_DIR/uExtension/README.md" << 'EOF'
# uExtension - Local Development Directory

This directory contains VS Code extension source code for local development only.

**🔧 SECURITY LEVEL 2: LOCAL DEVELOPMENT ONLY**

## Installation Methods

The uDOS VS Code extension is distributed through:

1. **Automatic**: Installed during `./install-udos.sh`
2. **Package**: Via `uKnowledge/packages/vscode-extension.md`
3. **Manual**: Download `.vsix` from GitHub releases

## Development Setup

To set up local extension development:

```bash
# Run extension development setup
./uCode/setup-extension-dev.sh

# This creates the full uExtension/ structure locally
# with source code, build tools, and dependencies
```

## Why Not in Repository?

- ✅ Reduces repository size and complexity
- ✅ Enables rapid development cycles
- ✅ Maintains separation between core system and tools
- ✅ Allows private/custom extension development

*The extension source will be created locally when you run the development setup script.*
EOF
    
    log_success "Structure documentation created"
}

# Create installation instructions
create_installation_guide() {
    log_info "Creating installation guide..."
    
    cat > "$CLEAN_DIR/INSTALL.md" << 'EOF'
# 🚀 uDOS v1.0 Installation Guide

## Quick Installation

### One-Command Install (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/fredporter/uDOS/main/install-udos.sh | bash
```

### Manual Installation
```bash
# Clone repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Run installer
./install-udos.sh
```

### macOS App Bundle
1. Download `uDOS-v1.0.0-macOS.app` from releases
2. Drag to Applications folder
3. Launch and follow setup wizard

## What Gets Created

### Core System (From Repository)
- ✅ `uCode/` - Core system scripts
- ✅ `uKnowledge/` - Documentation and packages  
- ✅ `uScript/` - System automation scripts
- ✅ `uTemplate/` - Standard templates
- ✅ VS Code workspace configuration

### Local User Directories (Created During Install)
- 🔒 `uMemory/` - Private user data (never in repo)
- 🔧 `uExtension/` - VS Code extension source (local dev only)

## User Roles

After installation, you'll be set up as a **wizard** (primary user) with:
- ✅ Full system access
- ✅ User management capabilities  
- ✅ Ability to create child installations (sorcerer/ghost/imp)

## Next Steps

1. **Open in VS Code**: `code ~/uDOS`
2. **Run validation**: `./uCode/check.sh all`
3. **Explore roadmaps**: Browse `uKnowledge/roadmap/`
4. **Create first mission**: Use VS Code command palette

## Support

- 📖 Documentation in `uKnowledge/`
- 🤖 Chester AI companion (built-in help)
- 🔍 Validation tools for troubleshooting
- 🌐 GitHub Issues for bug reports

Welcome to uDOS - The Markdown-Native Operating System! 🌟
EOF
    
    log_success "Installation guide created"
}

# Clean up any development artifacts
clean_development_artifacts() {
    log_info "Cleaning development artifacts..."
    
    # Remove logs and temporary files
    find "$CLEAN_DIR" -name "*.log" -delete 2>/dev/null || true
    find "$CLEAN_DIR" -name "*.tmp" -delete 2>/dev/null || true
    find "$CLEAN_DIR" -name "*.backup" -delete 2>/dev/null || true
    find "$CLEAN_DIR" -name ".DS_Store" -delete 2>/dev/null || true
    
    # Remove any accidentally included build artifacts
    rm -rf "$CLEAN_DIR/node_modules" 2>/dev/null || true
    rm -rf "$CLEAN_DIR/build" 2>/dev/null || true
    rm -rf "$CLEAN_DIR/dist" 2>/dev/null || true
    
    log_success "Development artifacts cleaned"
}

# Validate clean distribution
validate_clean_distribution() {
    log_info "Validating clean distribution..."
    
    # Check core directories exist
    local required_dirs=("uCode" "uKnowledge" "uScript" "uTemplate")
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$CLEAN_DIR/$dir" ]]; then
            log_success "✓ $dir directory included"
        else
            log_error "✗ $dir directory missing"
            return 1
        fi
    done
    
    # Check structure docs exist
    if [[ -f "$CLEAN_DIR/uMemory/README.md" ]]; then
        log_success "✓ uMemory structure documentation"
    else
        log_error "✗ uMemory documentation missing"
        return 1
    fi
    
    if [[ -f "$CLEAN_DIR/uExtension/README.md" ]]; then
        log_success "✓ uExtension structure documentation"  
    else
        log_error "✗ uExtension documentation missing"
        return 1
    fi
    
    # Check no private files included
    if [[ -d "$CLEAN_DIR/uMemory/user" ]] || [[ -d "$CLEAN_DIR/uMemory/sandbox" ]]; then
        log_error "✗ Private user files accidentally included"
        return 1
    else
        log_success "✓ No private user files included"
    fi
    
    # Check file count
    local file_count=$(find "$CLEAN_DIR" -type f | wc -l | tr -d ' ')
    log_info "Clean distribution contains $file_count files"
    
    log_success "Clean distribution validation passed"
}

# Create distribution archives
create_distribution_archives() {
    log_info "Creating distribution archives..."
    
    # Create source archive
    cd "$TEMP_DIR"
    cp -r "../$CLEAN_DIR" "uDOS-$VERSION"
    
    # Create tarball
    tar -czf "../uDOS-$VERSION-clean.tar.gz" "uDOS-$VERSION"
    log_success "Created: uDOS-$VERSION-clean.tar.gz"
    
    # Create zip
    zip -r "../uDOS-$VERSION-clean.zip" "uDOS-$VERSION" -q
    log_success "Created: uDOS-$VERSION-clean.zip"
    
    cd ..
}

# Generate clean repository info
generate_clean_info() {
    log_info "Generating clean repository information..."
    
    cat > "$CLEAN_DIR/REPOSITORY_INFO.md" << EOF
# uDOS v1.0 Clean Distribution

## Repository Structure

This is a clean distribution of uDOS v1.0 implementing the proper security model:

### ✅ Included in Repository
- **uCode/**: Core system scripts (read-only for most users)
- **uKnowledge/**: Documentation and packages (read-only)
- **uScript/**: System automation scripts (sorcerer+ access)
- **uTemplate/**: Standard templates (read-only)
- **docs/**: System documentation
- **Distribution scripts**: Installation and build tools
- **VS Code configuration**: Workspace tasks and settings

### 🔒 Excluded from Repository (Created Locally)
- **uMemory/**: Private user files (Security Level 1)
- **uExtension/**: VS Code extension source (Security Level 2)
- **Build artifacts**: Logs, temporary files, compiled output
- **User data**: Missions, moves, personal configurations

## Security Model

### Level 1: uMemory (Private)
- Never included in git repository
- Contains all personal user data
- Two sharing options: explicit (private) and public (opt-in)
- Created during installation with proper permissions

### Level 2: uExtension (Local Development)
- Local development files only
- Extensions distributed via uKnowledge packages
- Reduces repository complexity
- Enables rapid development cycles

### Level 3: Core System (Repository)
- uKnowledge is read-only for users
- uCode provides system functionality
- uTemplate offers standardized content creation
- uScript enables automation (role-dependent access)

## File Count Reduction

This clean distribution contains only essential system files, resulting in:
- 📉 Reduced repository size (~90% smaller)
- 🧹 Clean git history without user data
- 🔒 Enhanced privacy protection
- 🚀 Faster clone and distribution times

## Installation

See INSTALL.md for complete installation instructions.

Generated: $(date)
Version: $VERSION
EOF
    
    log_success "Repository information generated"
}

# Main process
main() {
    print_header
    
    echo "This will create a clean uDOS v1.0 distribution implementing the security model:"
    echo "• uMemory: Private user files (excluded)"
    echo "• uExtension: Local development only (excluded)" 
    echo "• Core system: Clean repository files only"
    echo ""
    
    read -p "Create clean distribution? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log_info "Clean distribution cancelled"
        exit 0
    fi
    
    echo ""
    create_clean_structure
    copy_core_system
    create_structure_docs
    create_installation_guide
    clean_development_artifacts
    validate_clean_distribution
    generate_clean_info
    create_distribution_archives
    
    # Cleanup temp directory
    rm -rf "$TEMP_DIR"
    
    echo ""
    log_success "🎉 Clean distribution created successfully!"
    echo ""
    echo "📁 Clean distribution: $CLEAN_DIR/"
    echo "📦 Archives created:"
    echo "   • uDOS-$VERSION-clean.tar.gz"
    echo "   • uDOS-$VERSION-clean.zip"
    echo ""
    echo "🔍 Files included: $(find "$CLEAN_DIR" -type f | wc -l | tr -d ' ')"
    echo "📏 Archive sizes:"
    ls -lh uDOS-$VERSION-clean.* 2>/dev/null || echo "   (archives in parent directory)"
    echo ""
    echo "Next steps:"
    echo "1. Review clean distribution in $CLEAN_DIR/"
    echo "2. Test installation from archive" 
    echo "3. Prepare GitHub release with clean archives"
    echo "4. Update repository to exclude user/development files"
}

# Error handling
trap 'log_error "Clean distribution failed on line $LINENO"' ERR

# Run main process
main "$@"
