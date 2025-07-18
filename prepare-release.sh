#!/bin/bash
# uDOS v1.0 GitHub Release Preparation Script
# Prepares release artifacts and documentation

set -euo pipefail

# Configuration
VERSION="v1.0.0"
RELEASE_DIR="./release"
ARCHIVE_NAME="uDOS-$VERSION"
TEMP_DIR="./temp-release"

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
log_bold() { echo -e "${BOLD}$1${NC}"; }

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                🚀 uDOS v1.0 RELEASE PREPARATION                  ║"
    echo "║                   GitHub Release Builder                         ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Pre-flight checks
check_prerequisites() {
    log_info "Running pre-flight checks..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
        exit 1
    fi
    
    # Check if working directory is clean
    if ! git diff-index --quiet HEAD --; then
        log_warning "Working directory has uncommitted changes"
        echo "Uncommitted changes:"
        git status --porcelain
        echo ""
        read -p "Continue anyway? (y/N): " continue_dirty
        if [[ ! "$continue_dirty" =~ ^[Yy]$ ]]; then
            log_info "Release preparation cancelled"
            exit 0
        fi
    fi
    
    # Check required files
    local required_files=(
        "README.md"
        "CHANGELOG.md"
        "LICENSE"
        "uCode/ucode.sh"
        "start-udos.sh"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "$file found"
        else
            log_error "Required file missing: $file"
            exit 1
        fi
    done
    
    log_success "Pre-flight checks passed"
}

# Create release directory structure
setup_release_directory() {
    log_info "Setting up release directory..."
    
    if [[ -d "$RELEASE_DIR" ]]; then
        rm -rf "$RELEASE_DIR"
    fi
    
    mkdir -p "$RELEASE_DIR"
    mkdir -p "$TEMP_DIR"
    
    log_success "Release directory created"
}

# Create source archive
create_source_archive() {
    log_info "Creating source archive..."
    
    # Create clean copy of repository
    git archive --format=tar --prefix="$ARCHIVE_NAME/" HEAD | tar -x -C "$TEMP_DIR"
    
    # Remove development files from archive
    local dev_files=(
        ".git"
        ".github"
        ".vscode/settings.json"
        "uExtension"
        "build"
        "release"
        "temp-release"
        "*.log"
        ".DS_Store"
    )
    
    for pattern in "${dev_files[@]}"; do
        find "$TEMP_DIR/$ARCHIVE_NAME" -name "$pattern" -exec rm -rf {} + 2>/dev/null || true
    done
    
    # Create tarball
    cd "$TEMP_DIR"
    tar -czf "../$RELEASE_DIR/$ARCHIVE_NAME-source.tar.gz" "$ARCHIVE_NAME"
    cd ..
    
    # Create zip
    cd "$TEMP_DIR"
    zip -r "../$RELEASE_DIR/$ARCHIVE_NAME-source.zip" "$ARCHIVE_NAME" -q
    cd ..
    
    log_success "Source archives created"
}

# Create installer package
create_installer_package() {
    log_info "Creating installer package..."
    
    # Copy installer script
    cp "install-udos.sh" "$RELEASE_DIR/install-udos-$VERSION.sh"
    chmod +x "$RELEASE_DIR/install-udos-$VERSION.sh"
    
    # Create self-extracting installer (Unix)
    cat > "$RELEASE_DIR/uDOS-$VERSION-installer.sh" << 'EOF'
#!/bin/bash
# uDOS v1.0 Self-Extracting Installer
set -euo pipefail

# Extract embedded installer
INSTALLER_START_LINE=$(grep -n "^__INSTALLER_START__$" "$0" | cut -d: -f1)
INSTALLER_START_LINE=$((INSTALLER_START_LINE + 1))
tail -n +$INSTALLER_START_LINE "$0" > /tmp/install-udos.sh
chmod +x /tmp/install-udos.sh

# Run installer
echo "🧙‍♂️ Starting uDOS v1.0 installation..."
/tmp/install-udos.sh "$@"

# Cleanup
rm -f /tmp/install-udos.sh

exit 0

__INSTALLER_START__
EOF
    
    # Append installer script
    cat "install-udos.sh" >> "$RELEASE_DIR/uDOS-$VERSION-installer.sh"
    chmod +x "$RELEASE_DIR/uDOS-$VERSION-installer.sh"
    
    log_success "Installer package created"
}

# Build VS Code extension package
build_vscode_extension() {
    if [[ -d "uExtension" ]] && [[ -f "uExtension/package.json" ]]; then
        log_info "Building VS Code extension..."
        
        cd uExtension
        
        # Install dependencies if needed
        if [[ -f "package.json" ]] && command -v npm &> /dev/null; then
            if [[ ! -d "node_modules" ]]; then
                npm install
            fi
            
            # Build extension
            if command -v vsce &> /dev/null; then
                vsce package --out "../$RELEASE_DIR/uDOS-extension-$VERSION.vsix"
                log_success "VS Code extension packaged"
            else
                log_warning "vsce not found - install with: npm install -g vsce"
                log_info "Copying extension source instead"
                cp -r . "../$TEMP_DIR/uDOS-extension-$VERSION"
                cd "../$TEMP_DIR"
                zip -r "../$RELEASE_DIR/uDOS-extension-$VERSION-source.zip" "uDOS-extension-$VERSION" -q
                cd ..
            fi
        else
            log_warning "npm not found - copying extension source"
            cp -r uExtension "$TEMP_DIR/uDOS-extension-$VERSION"
            cd "$TEMP_DIR"
            zip -r "../$RELEASE_DIR/uDOS-extension-$VERSION-source.zip" "uDOS-extension-$VERSION" -q
            cd ..
        fi
        
        cd ..
    else
        log_info "No VS Code extension found - skipping"
    fi
}

# Create release notes
create_release_notes() {
    log_info "Creating release notes..."
    
    cat > "$RELEASE_DIR/RELEASE_NOTES.md" << EOF
# uDOS v1.0.0 - First Production Release

## 🧙‍♂️ The Markdown-Native Operating System

Welcome to uDOS v1.0 - the world's first markdown-native operating system! This milestone release represents a complete reimagining of how we interact with our digital environment through the power of markdown.

## ✨ Key Features

### 🏗️ Complete Architecture
- **Markdown-Native Environment**: Everything is markdown, from documentation to commands
- **Four-Tier User System**: wizard, sorcerer, ghost, and imp roles with granular permissions
- **Privacy-First Design**: Local-first operation with optional cloud sync
- **VS Code Integration**: Full development environment with custom extension

### 🤖 Chester AI Companion
- Personality-driven AI assistant with small dog characteristics
- Context-aware help and guidance
- Integrated throughout the uDOS experience
- Supports all user roles with appropriate permissions

### 📁 Organized Structure
- **uCode**: Core system scripts and executables
- **uMemory**: User data, logs, and state management
- **uKnowledge**: Documentation, roadmaps, and knowledge base
- **uScript**: Automation and scripting framework
- **uTemplate**: Standardized templates for all content types
- **uExtension**: VS Code extension for optimal development experience

### 🛠️ Developer Experience
- VS Code tasks for common operations
- Comprehensive validation and setup checking
- Rich template system for rapid development
- Integrated logging and debugging tools

## 📦 Installation Options

### Quick Install (Recommended)
\`\`\`bash
curl -fsSL https://github.com/fredporter/uDOS/releases/download/v1.0.0/uDOS-v1.0.0-installer.sh | bash
\`\`\`

### Manual Installation
1. Download source archive
2. Extract to desired location
3. Run \`./install-udos.sh\`

### macOS App Bundle
- Download \`uDOS-v1.0.0-macOS.app\`
- Drag to Applications folder
- Launch and follow setup wizard

### VS Code Extension
- Install from \`.vsix\` file or
- Search "uDOS" in VS Code marketplace

## 🎯 Getting Started

1. **Install uDOS** using your preferred method above
2. **Run initial setup** - the wizard will guide you through configuration
3. **Explore the roadmaps** in \`uKnowledge/roadmap/\` to understand the system
4. **Open in VS Code** for the optimal experience
5. **Create your first mission** using the provided templates

## 🔧 System Requirements

- **OS**: macOS 10.15+ or Linux
- **Dependencies**: Git, Bash, curl
- **Recommended**: VS Code, Node.js
- **Storage**: ~50MB for base installation

## 📚 Documentation

- **Complete roadmaps** covering all system aspects
- **Architecture documentation** in uKnowledge/
- **Template system** for consistent content creation
- **API documentation** for extension development

## 🆕 What's New in v1.0

- ✅ Complete architectural foundation
- ✅ Four-tier user permission system
- ✅ Chester AI companion integration
- ✅ VS Code extension with full language support
- ✅ Comprehensive template system
- ✅ Professional installer and distribution
- ✅ Complete documentation suite
- ✅ Validation and setup checking
- ✅ macOS app bundle support

## 🔮 Future Roadmap

- Web interface for browser-based access
- Mobile companion apps
- Plugin ecosystem expansion
- Enhanced AI capabilities
- Community marketplace

## 🤝 Contributing

uDOS is open source and welcomes contributions! See the roadmap documents for development priorities and architectural guidelines.

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

Built with love for the markdown community and inspired by the vision of a truly document-native computing experience.

---

**Welcome to the future of computing - markdown-native and human-friendly!** 🌟

For support, issues, or questions: https://github.com/fredporter/uDOS
EOF
    
    log_success "Release notes created"
}

# Generate checksums
generate_checksums() {
    log_info "Generating checksums..."
    
    cd "$RELEASE_DIR"
    
    # Generate SHA256 checksums
    if command -v sha256sum &> /dev/null; then
        sha256sum *.tar.gz *.zip *.sh > SHA256SUMS 2>/dev/null || true
        sha256sum *.vsix >> SHA256SUMS 2>/dev/null || true
    elif command -v shasum &> /dev/null; then
        shasum -a 256 *.tar.gz *.zip *.sh > SHA256SUMS 2>/dev/null || true
        shasum -a 256 *.vsix >> SHA256SUMS 2>/dev/null || true
    fi
    
    cd ..
    log_success "Checksums generated"
}

# Create GitHub release template
create_github_release_template() {
    log_info "Creating GitHub release template..."
    
    cat > "$RELEASE_DIR/github-release-template.md" << EOF
## Release Command Template

Use the GitHub CLI to create the release:

\`\`\`bash
gh release create $VERSION \\
  --title "uDOS $VERSION - First Production Release" \\
  --notes-file RELEASE_NOTES.md \\
  --discussion-category "Announcements" \\
  $ARCHIVE_NAME-source.tar.gz \\
  $ARCHIVE_NAME-source.zip \\
  uDOS-$VERSION-installer.sh \\
  install-udos-$VERSION.sh
EOF

    if [[ -f "$RELEASE_DIR"/*.vsix ]]; then
        echo "  uDOS-extension-$VERSION.vsix \\" >> "$RELEASE_DIR/github-release-template.md"
    fi

    cat >> "$RELEASE_DIR/github-release-template.md" << EOF
  SHA256SUMS
\`\`\`

## Manual Upload Files

If uploading manually through GitHub web interface:

1. Go to: https://github.com/fredporter/uDOS/releases/new
2. Tag: $VERSION
3. Title: uDOS $VERSION - First Production Release
4. Description: Copy content from RELEASE_NOTES.md
5. Upload files:
EOF

    for file in "$RELEASE_DIR"/*; do
        if [[ -f "$file" ]] && [[ "$(basename "$file")" != "github-release-template.md" ]]; then
            echo "   - $(basename "$file")" >> "$RELEASE_DIR/github-release-template.md"
        fi
    done

    echo "" >> "$RELEASE_DIR/github-release-template.md"
    echo "6. Mark as latest release" >> "$RELEASE_DIR/github-release-template.md"
    echo "7. Publish release" >> "$RELEASE_DIR/github-release-template.md"
    
    log_success "GitHub release template created"
}

# Show release summary
show_release_summary() {
    echo ""
    log_bold "🎉 RELEASE PREPARATION COMPLETE!"
    echo ""
    echo "📁 Release artifacts in: $RELEASE_DIR"
    echo ""
    echo "📦 Created packages:"
    
    for file in "$RELEASE_DIR"/*; do
        if [[ -f "$file" ]]; then
            local size=$(du -h "$file" | cut -f1)
            echo "   $(basename "$file") ($size)"
        fi
    done
    
    echo ""
    echo "🚀 Next steps:"
    echo "1. Review release notes in $RELEASE_DIR/RELEASE_NOTES.md"
    echo "2. Test installer: ./$RELEASE_DIR/uDOS-$VERSION-installer.sh"
    echo "3. Create GitHub release using template in $RELEASE_DIR/github-release-template.md"
    echo "4. Update package managers and distribution channels"
    echo ""
    echo "🔍 Quick test command:"
    echo "   cd /tmp && ./$PWD/$RELEASE_DIR/uDOS-$VERSION-installer.sh"
    echo ""
}

# Cleanup
cleanup() {
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
}

# Main preparation process
main() {
    print_header
    
    echo "This will prepare uDOS v1.0 for GitHub release distribution."
    echo "All release artifacts will be created in the release/ directory."
    echo ""
    
    read -p "Continue with release preparation? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log_info "Release preparation cancelled"
        exit 0
    fi
    
    echo ""
    check_prerequisites
    setup_release_directory
    create_source_archive
    create_installer_package
    build_vscode_extension
    create_release_notes
    generate_checksums
    create_github_release_template
    cleanup
    show_release_summary
}

# Error handling
trap 'log_error "Release preparation failed on line $LINENO"; cleanup' ERR
trap 'cleanup' EXIT

# Run main preparation
main "$@"
