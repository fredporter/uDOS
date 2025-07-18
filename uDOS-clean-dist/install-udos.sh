#!/bin/bash
# uDOS v1.0 Production Installer
# Self-contained installation script for wizard (primary) installations

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Installer configuration
UDOS_VERSION="v1.0.0"
UDOS_REPO="https://github.com/fredporter/uDOS.git"
INSTALL_DIR="$HOME/uDOS"
BACKUP_DIR="$HOME/uDOS-backup-$(date +%Y%m%d-%H%M%S)"

# Functions
print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    🧙‍♂️ uDOS v1.0 INSTALLER                        ║"
    echo "║              Markdown-Native Operating System                    ║"
    echo "║                   Wizard Installation                            ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# System requirements check
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        log_success "macOS detected"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "Linux detected"
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    # Check required commands
    local required_commands=("git" "bash" "curl")
    for cmd in "${required_commands[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            log_success "$cmd found"
        else
            log_error "$cmd is required but not installed"
            exit 1
        fi
    done
    
    # Check VS Code (optional but recommended)
    if command -v code &> /dev/null; then
        log_success "VS Code detected - optimal experience available"
        export UDOS_VSCODE_AVAILABLE=true
    else
        log_warning "VS Code not found - install for best experience"
        export UDOS_VSCODE_AVAILABLE=false
    fi
}

# Check for existing installation
check_existing_installation() {
    if [[ -d "$INSTALL_DIR" ]]; then
        log_warning "Existing uDOS installation found at $INSTALL_DIR"
        echo "Options:"
        echo "  1. Backup and reinstall (recommended)"
        echo "  2. Abort installation"
        echo "  3. Force reinstall (data loss risk)"
        
        read -p "Choose option (1-3): " choice
        case $choice in
            1)
                log_info "Creating backup at $BACKUP_DIR"
                cp -r "$INSTALL_DIR" "$BACKUP_DIR"
                log_success "Backup created"
                rm -rf "$INSTALL_DIR"
                ;;
            2)
                log_info "Installation aborted by user"
                exit 0
                ;;
            3)
                log_warning "Force reinstall selected - removing existing installation"
                rm -rf "$INSTALL_DIR"
                ;;
            *)
                log_error "Invalid choice"
                exit 1
                ;;
        esac
    fi
}

# Clone repository
install_udos() {
    log_info "Installing uDOS v1.0..."
    
    # Clone repository
    log_info "Cloning uDOS repository..."
    git clone "$UDOS_REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Checkout v1.0 tag if it exists
    if git tag | grep -q "v1.0"; then
        git checkout v1.0
        log_success "Checked out v1.0 release"
    else
        log_info "Using latest main branch"
    fi
    
    # Make scripts executable
    log_info "Setting up permissions..."
    chmod +x uCode/*.sh
    chmod +x start-udos.sh
    if [[ -d "launcher" ]]; then
        chmod +x launcher/*.sh
    fi
    log_success "Permissions configured"
}

# Setup VS Code integration
setup_vscode_integration() {
    if [[ "$UDOS_VSCODE_AVAILABLE" == "true" ]]; then
        log_info "Setting up VS Code integration..."
        
        # Install uDOS extension if available
        if [[ -f "uExtension/install-extension.sh" ]]; then
            log_info "Installing uDOS VS Code extension..."
            cd uExtension
            if ./install-extension.sh; then
                log_success "VS Code extension installed"
            else
                log_warning "Extension installation failed - can install manually later"
            fi
            cd ..
        fi
        
        log_success "VS Code integration configured"
    else
        log_info "Skipping VS Code integration (not installed)"
    fi
}

# Run first-time setup
run_first_time_setup() {
    log_info "Running first-time wizard setup..."
    
    echo ""
    echo -e "${BOLD}${GREEN}🧙‍♂️ WIZARD INITIALIZATION${NC}"
    echo "You are setting up the primary (wizard) installation of uDOS."
    echo "This gives you full system access and the ability to create child installations."
    echo ""
    
    # Run uDOS first-time setup
    if ./start-udos.sh; then
        log_success "Wizard setup completed successfully"
    else
        log_error "Setup failed - please check the logs"
        exit 1
    fi
}

# Validate installation
validate_installation() {
    log_info "Validating installation..."
    
    # Run validation script
    if [[ -f "uCode/validate-installation.sh" ]]; then
        if ./uCode/validate-installation.sh; then
            log_success "Installation validation passed"
        else
            log_warning "Some validation checks failed - see output above"
        fi
    else
        log_warning "Validation script not found"
    fi
    
    # Check key components
    local key_files=(
        "uCode/ucode.sh"
        "uMemory"
        "uKnowledge/roadmap"
        ".vscode/tasks.json"
    )
    
    for file in "${key_files[@]}"; do
        if [[ -e "$file" ]]; then
            log_success "$file exists"
        else
            log_error "$file missing"
        fi
    done
}

# Print post-installation information
print_post_install_info() {
    echo ""
    echo -e "${BOLD}${GREEN}🎉 uDOS v1.0 INSTALLATION COMPLETE!${NC}"
    echo ""
    echo -e "${BOLD}Next Steps:${NC}"
    echo "1. 📖 Read the documentation:"
    echo "   cat $INSTALL_DIR/README.md"
    echo ""
    echo "2. 🚀 Start uDOS:"
    echo "   cd $INSTALL_DIR && ./start-udos.sh"
    echo ""
    if [[ "$UDOS_VSCODE_AVAILABLE" == "true" ]]; then
        echo "3. 💻 Open in VS Code (recommended):"
        echo "   code $INSTALL_DIR"
        echo ""
        echo "4. 🔌 Use VS Code tasks (Cmd+Shift+P):"
        echo "   - 🌀 Start uDOS"
        echo "   - 🔍 Check uDOS Setup"
        echo "   - 📊 Generate Dashboard"
        echo ""
    fi
    echo "5. 👥 Create child installations:"
    echo "   Use wizard commands to create sorcerer/ghost/imp users"
    echo ""
    echo "6. 📚 Explore roadmaps:"
    echo "   Browse $INSTALL_DIR/uKnowledge/roadmap/"
    echo ""
    echo -e "${BOLD}Support:${NC}"
    echo "- 📖 Documentation: README.md and roadmap documents"
    echo "- 🤖 AI Companion: Chester is available for assistance"
    echo "- 🔍 Validation: Run 'CHECK SETUP' anytime"
    echo ""
    if [[ -d "$BACKUP_DIR" ]]; then
        echo -e "${YELLOW}📦 Backup created at: $BACKUP_DIR${NC}"
        echo ""
    fi
    echo -e "${BOLD}${BLUE}Welcome to uDOS - The Markdown-Native Operating System! 🌟${NC}"
}

# Main installation process
main() {
    print_header
    
    echo "This installer will set up uDOS v1.0 as a wizard (primary) installation."
    echo "The wizard role provides full system access and management capabilities."
    echo ""
    
    read -p "Continue with installation? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log_info "Installation cancelled by user"
        exit 0
    fi
    
    echo ""
    check_requirements
    echo ""
    check_existing_installation
    echo ""
    install_udos
    echo ""
    setup_vscode_integration
    echo ""
    run_first_time_setup
    echo ""
    validate_installation
    echo ""
    print_post_install_info
}

# Error handling
trap 'log_error "Installation failed on line $LINENO"' ERR

# Run main installation
main "$@"
