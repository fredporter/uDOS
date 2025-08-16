# 🍎 uDOS macOS VS Code Installer Template

**Template Version**: v2.0.0  
**Platform**: macOS (Intel/Apple Silicon)  
**Method**: VS Code Native Integration  
**User Role**: {{user_role}}  
**Generated**: {{timestamp}}

---

## 📋 Installation Configuration

### System Requirements
- **OS**: macOS 10.15+ (Catalina or later)
- **Architecture**: {{architecture}}
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for initial setup

### Software Dependencies
- **VS Code**: {{vs_code_variant}} (auto-installed if missing)
- **Git**: Version 2.0+ (auto-installed via Xcode CLI tools)
- **Homebrew**: {{package_manager}} (auto-installed if missing)
- **Node.js**: 18+ (auto-installed via Homebrew)

### Installation Settings
- **Install Directory**: {{install_directory}}
- **Backup Directory**: {{backup_directory}}
- **Chester AI**: {{enable_chester}}
- **Package Installation**: {{install_packages}}
- **Privacy Mode**: {{privacy_mode}}

---

## 🚀 Installation Script

```bash
#!/bin/bash
# uDOS {{udos_version}} Installer - macOS VS Code Edition
# Generated from template: {{template_name}}
# Target Platform: macOS {{os_version}}

set -euo pipefail

# Configuration from template
UDOS_VERSION="{{udos_version}}"
USER_ROLE="{{user_role}}"
INSTALL_DIR="{{install_directory}}"
BACKUP_DIR="{{backup_directory}}"
ENABLE_CHESTER="{{enable_chester}}"
PRIVACY_MODE="{{privacy_mode}}"
VS_CODE_VARIANT="{{vs_code_variant}}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                🍎 uDOS macOS VS Code Installer                   ║"
    echo "║              User Role: {{user_role}}                           ║"
    echo "║               Generated: {{timestamp}}                          ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# System detection
detect_system() {
    log_info "Detecting macOS system configuration..."
    
    # Architecture detection
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ]; then
        log_info "Detected Apple Silicon (M1/M2)"
        HOMEBREW_PREFIX="/opt/homebrew"
    else
        log_info "Detected Intel architecture"
        HOMEBREW_PREFIX="/usr/local"
    fi
    
    # macOS version
    MACOS_VERSION=$(sw_vers -productVersion)
    log_info "macOS version: $MACOS_VERSION"
    
    # VS Code detection
    if command -v code &> /dev/null; then
        VS_CODE_INSTALLED=true
        VS_CODE_VERSION=$(code --version | head -n1)
        log_info "VS Code found: $VS_CODE_VERSION"
    else
        VS_CODE_INSTALLED=false
        log_warning "VS Code not found - will install"
    fi
}

# Install Homebrew if needed
install_homebrew() {
    if ! command -v brew &> /dev/null; then
        log_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add to PATH
        echo 'eval "$($HOMEBREW_PREFIX/bin/brew shellenv)"' >> ~/.zprofile
        eval "$($HOMEBREW_PREFIX/bin/brew shellenv)"
        
        log_success "Homebrew installed successfully"
    else
        log_info "Homebrew already installed"
        brew update
    fi
}

# Install VS Code if needed
install_vscode() {
    if [ "$VS_CODE_INSTALLED" = false ]; then
        log_info "Installing VS Code..."
        
        case "$VS_CODE_VARIANT" in
            "code-insiders")
                brew install --cask visual-studio-code-insiders
                ;;
            "vscodium")
                brew install --cask vscodium
                ;;
            *)
                brew install --cask visual-studio-code
                ;;
        esac
        
        log_success "VS Code installed successfully"
    fi
}

# Install system dependencies
install_dependencies() {
    log_info "Installing system dependencies..."
    
    # Core tools
    brew install git node
    
    # Optional tools based on package selection
    if [[ "{{install_packages}}" == *"ripgrep"* ]]; then
        brew install ripgrep
    fi
    
    if [[ "{{install_packages}}" == *"fd"* ]]; then
        brew install fd
    fi
    
    if [[ "{{install_packages}}" == *"bat"* ]]; then
        brew install bat
    fi
    
    if [[ "{{install_packages}}" == *"glow"* ]]; then
        brew install glow
    fi
    
    log_success "Dependencies installed"
}

# Clone uDOS repository
clone_udos() {
    log_info "Cloning uDOS repository..."
    
    # Backup existing installation if present
    if [ -d "$INSTALL_DIR" ]; then
        log_warning "Existing uDOS installation found - creating backup"
        mv "$INSTALL_DIR" "$BACKUP_DIR"
        log_info "Backup created at: $BACKUP_DIR"
    fi
    
    # Clone repository
    git clone https://github.com/fredporter/uDOS.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    log_success "uDOS repository cloned"
}

# Configure VS Code integration
configure_vscode() {
    log_info "Configuring VS Code integration..."
    
    # Install uDOS extension
    cd "$INSTALL_DIR"
    ./extension/install-extension.sh
    
    # Configure workspace settings
    mkdir -p .vscode
    cat > .vscode/settings.json << EOF
{
    "terminal.integrated.defaultProfile.osx": "zsh",
    "terminal.integrated.cwd": "\${workspaceFolder}",
    "files.watcherExclude": {
        "**/uMemory/**": true
    },
    "search.exclude": {
        "**/uMemory/**": true
    },
    "markdown.preview.theme": "dark"
}
EOF
    
    log_success "VS Code configuration complete"
}

# Setup user role and permissions
setup_user_role() {
    log_info "Setting up user role: $USER_ROLE"
    
    # Create user configuration
    mkdir -p uMemory/config
    cat > uMemory/config/user.json << EOF
{
    "role": "$USER_ROLE",
    "username": "$(whoami)",
    "hostname": "$(hostname)",
    "install_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "platform": "macOS",
    "architecture": "$ARCH",
    "privacy_mode": "$PRIVACY_MODE"
}
EOF
    
    # Role-specific setup
    case "$USER_ROLE" in
        "wizard")
            log_info "Configuring wizard (full) access..."
            # Full system access, all features enabled
            ;;
        "sorcerer")
            log_info "Configuring sorcerer (advanced) access..."
            # Advanced features, limited system access
            ;;
        "ghost")
            log_info "Configuring ghost (standard) access..."
            # Standard features, user-level access
            ;;
        "imp")
            log_info "Configuring imp (basic) access..."
            # Basic features, sandbox access
            ;;
    esac
    
    log_success "User role configured: $USER_ROLE"
}

# Setup Chester AI companion
setup_chester() {
    if [ "$ENABLE_CHESTER" = "true" ]; then
        log_info "Setting up Chester AI companion..."
        
        # Install Gemini CLI if needed
        ./uCode/packages/install-gemini.sh
        
        # Initialize Chester
        ./uCode/companion-system.sh init-chester
        
        log_success "Chester AI companion configured"
    else
        log_info "Skipping Chester AI setup (disabled in template)"
    fi
}

# Run installation validation
run_validation() {
    log_info "Running installation validation..."
    
    # Quick validation
    ./uCode/validate-installation.sh quick
    
    # Full validation for wizard role
    if [ "$USER_ROLE" = "wizard" ]; then
        ./uCode/validate-installation.sh full
    fi
    
    log_success "Installation validation complete"
}

# Configure shell integration
configure_shell() {
    log_info "Configuring shell integration..."
    
    # Add uDOS to PATH
    SHELL_RC="$HOME/.zshrc"
    if [ -f "$HOME/.bash_profile" ]; then
        SHELL_RC="$HOME/.bash_profile"
    fi
    
    # Add uDOS paths and aliases
    cat >> "$SHELL_RC" << EOF

# uDOS Configuration (added by installer)
export UDOS_HOME="$INSTALL_DIR"
export PATH="\$UDOS_HOME/uCode:\$PATH"
alias udos="cd \$UDOS_HOME && code ."
alias ucode="\$UDOS_HOME/uCode/ucode.sh"

EOF
    
    log_success "Shell integration configured"
}

# Main installation process
main() {
    print_header
    
    log_info "Starting uDOS installation for macOS..."
    log_info "Target role: $USER_ROLE"
    log_info "Installation directory: $INSTALL_DIR"
    
    detect_system
    install_homebrew
    install_vscode
    install_dependencies
    clone_udos
    configure_vscode
    setup_user_role
    setup_chester
    configure_shell
    run_validation
    
    echo
    log_success "🎉 uDOS installation complete!"
    echo
    echo -e "${BOLD}${GREEN}Next steps:${NC}"
    echo "1. Restart your terminal or run: source ~/.zshrc"
    echo "2. Open uDOS: udos"
    echo "3. Start exploring: ucode help"
    
    if [ "$ENABLE_CHESTER" = "true" ]; then
        echo "4. Meet Chester: ucode CHESTER start"
    fi
    
    echo
    echo -e "${BLUE}Documentation: $INSTALL_DIR/docs/README.md${NC}"
    echo -e "${BLUE}Support: https://github.com/fredporter/uDOS${NC}"
}

# Error handling
trap 'log_error "Installation failed at line $LINENO"' ERR

# Run installation
main "$@"
```

---

## 🔧 Template Variables Used

### System Configuration
- `{{udos_version}}` - uDOS version to install
- `{{template_name}}` - Name of this template
- `{{timestamp}}` - Generation timestamp
- `{{architecture}}` - System architecture (arm64/x86_64)
- `{{os_version}}` - macOS version

### User Configuration
- `{{user_role}}` - Target user role (wizard/sorcerer/ghost/imp)
- `{{install_directory}}` - Installation path
- `{{backup_directory}}` - Backup location
- `{{privacy_mode}}` - Privacy configuration level

### Software Configuration
- `{{vs_code_variant}}` - VS Code edition (code/code-insiders/vscodium)
- `{{enable_chester}}` - Chester AI companion (true/false)
- `{{install_packages}}` - Package selection list

---

## 📋 Post-Installation

### Verification Steps
1. **System Integration**: Verify shell integration and PATH
2. **VS Code Extension**: Confirm uDOS extension installation
3. **Role Configuration**: Validate user role and permissions
4. **Package Availability**: Test installed packages
5. **Chester Integration**: Verify AI companion setup (if enabled)

### Troubleshooting
- **Homebrew Issues**: Check architecture and permissions
- **VS Code Integration**: Verify extension installation
- **Permission Errors**: Ensure proper user role configuration
- **Network Issues**: Check internet connectivity for downloads

---

*This template generates a complete macOS installer with VS Code integration, user role configuration, and optional Chester AI companion setup.*
