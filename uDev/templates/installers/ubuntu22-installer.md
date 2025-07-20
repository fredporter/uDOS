# 🐧 uDOS Ubuntu 22.04 LTS Installer Template

**Template Version**: v2.0.0  
**Platform**: Ubuntu 22.04 LTS (Jammy Jellyfish)  
**Method**: APT Package + VS Code Integration  
**User Role**: {{user_role}}  
**Generated**: {{timestamp}}

---

## 📋 Installation Configuration

### System Requirements
- **OS**: Ubuntu 22.04 LTS or compatible
- **Architecture**: {{architecture}}
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 3GB free space
- **Network**: Internet connection for package downloads

### Software Dependencies
- **VS Code**: {{vs_code_variant}} (installed via Microsoft repository)
- **Git**: Version 2.0+ (installed via APT)
- **Node.js**: 18+ (installed via NodeSource repository)
- **Build Essential**: GCC compiler and tools

### Installation Settings
- **Install Directory**: {{install_directory}}
- **Package Manager**: {{package_manager}}
- **Desktop Environment**: {{desktop_environment}}
- **Chester AI**: {{enable_chester}}
- **Package Selection**: {{install_packages}}

---

## 🚀 Installation Script

```bash
#!/bin/bash
# uDOS {{udos_version}} Installer - Ubuntu 22.04 LTS Edition
# Generated from template: {{template_name}}
# Target Platform: Ubuntu {{os_version}}

set -euo pipefail

# Configuration from template
UDOS_VERSION="{{udos_version}}"
USER_ROLE="{{user_role}}"
INSTALL_DIR="{{install_directory}}"
BACKUP_DIR="{{backup_directory}}"
ENABLE_CHESTER="{{enable_chester}}"
DESKTOP_ENV="{{desktop_environment}}"
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
    echo "║              🐧 uDOS Ubuntu 22.04 LTS Installer                 ║"
    echo "║              User Role: {{user_role}}                           ║"
    echo "║               Generated: {{timestamp}}                          ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_error "Please do not run this installer as root"
        log_info "This installer will prompt for sudo when needed"
        exit 1
    fi
}

# System detection and validation
detect_system() {
    log_info "Detecting Ubuntu system configuration..."
    
    # OS version check
    if [ -f /etc/os-release ]; then
        source /etc/os-release
        if [ "$ID" != "ubuntu" ]; then
            log_warning "Not running on Ubuntu - proceeding with caution"
        fi
        log_info "OS: $PRETTY_NAME"
    fi
    
    # Architecture detection
    ARCH=$(uname -m)
    log_info "Architecture: $ARCH"
    
    # Desktop environment detection
    if [ -n "${XDG_CURRENT_DESKTOP:-}" ]; then
        DETECTED_DE="$XDG_CURRENT_DESKTOP"
        log_info "Desktop Environment: $DETECTED_DE"
    else
        log_info "No desktop environment detected (headless mode)"
        DETECTED_DE="headless"
    fi
    
    # Check internet connectivity
    if ping -c 1 google.com &> /dev/null; then
        log_success "Internet connectivity confirmed"
    else
        log_error "No internet connection - installation cannot proceed"
        exit 1
    fi
}

# Update system packages
update_system() {
    log_info "Updating system packages..."
    
    sudo apt update
    sudo apt upgrade -y
    
    log_success "System packages updated"
}

# Install system dependencies
install_dependencies() {
    log_info "Installing system dependencies..."
    
    # Essential packages
    sudo apt install -y \
        curl \
        wget \
        git \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        figlet \
        tree
    
    # Install Node.js 18+
    log_info "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
    
    # Optional packages based on selection
    if [[ "{{install_packages}}" == *"ripgrep"* ]]; then
        sudo apt install -y ripgrep
    fi
    
    if [[ "{{install_packages}}" == *"fd"* ]]; then
        sudo apt install -y fd-find
        # Create fd symlink for compatibility
        sudo ln -sf /usr/bin/fdfind /usr/local/bin/fd
    fi
    
    if [[ "{{install_packages}}" == *"bat"* ]]; then
        sudo apt install -y bat
        # Create bat symlink for compatibility
        sudo ln -sf /usr/bin/batcat /usr/local/bin/bat
    fi
    
    if [[ "{{install_packages}}" == *"glow"* ]]; then
        # Install glow from GitHub releases
        GLOW_VERSION=$(curl -s https://api.github.com/repos/charmbracelet/glow/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
        wget -O /tmp/glow.deb "https://github.com/charmbracelet/glow/releases/download/$GLOW_VERSION/glow_${GLOW_VERSION#v}_linux_amd64.deb"
        sudo dpkg -i /tmp/glow.deb
        rm /tmp/glow.deb
    fi
    
    log_success "Dependencies installed"
}

# Install VS Code
install_vscode() {
    log_info "Installing VS Code..."
    
    # Add Microsoft repository
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
    sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
    
    case "$VS_CODE_VARIANT" in
        "code-insiders")
            echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
            sudo apt update
            sudo apt install -y code-insiders
            ;;
        "vscodium")
            # Add VSCodium repository
            wget -qO - https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg | gpg --dearmor | sudo dd of=/usr/share/keyrings/vscodium-archive-keyring.gpg
            echo 'deb [ signed-by=/usr/share/keyrings/vscodium-archive-keyring.gpg ] https://download.vscodium.com/debs vscodium main' | sudo tee /etc/apt/sources.list.d/vscodium.list
            sudo apt update
            sudo apt install -y codium
            ;;
        *)
            echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
            sudo apt update
            sudo apt install -y code
            ;;
    esac
    
    rm packages.microsoft.gpg
    log_success "VS Code installed successfully"
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
    
    # Set permissions
    chmod +x uCode/*.sh
    chmod +x uCode/packages/*.sh
    chmod +x extension/*.sh
    
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
    "terminal.integrated.defaultProfile.linux": "bash",
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
    
    # Create desktop entry if GUI environment
    if [ "$DETECTED_DE" != "headless" ]; then
        create_desktop_entry
    fi
    
    log_success "VS Code configuration complete"
}

# Create desktop entry
create_desktop_entry() {
    log_info "Creating desktop entry..."
    
    mkdir -p ~/.local/share/applications
    cat > ~/.local/share/applications/udos.desktop << EOF
[Desktop Entry]
Name=uDOS
Comment=Markdown-Native Operating System
Exec=code "$INSTALL_DIR"
Icon=$INSTALL_DIR/docs/assets/udos-icon.png
Terminal=false
Type=Application
Categories=Development;
StartupWMClass=Code
EOF
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database ~/.local/share/applications
    fi
    
    log_success "Desktop entry created"
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
    "platform": "Ubuntu",
    "version": "$VERSION_ID",
    "architecture": "$ARCH",
    "desktop_environment": "$DETECTED_DE"
}
EOF
    
    log_success "User role configured: $USER_ROLE"
}

# Setup Chester AI companion
setup_chester() {
    if [ "$ENABLE_CHESTER" = "true" ]; then
        log_info "Setting up Chester AI companion..."
        
        # Check if Google AI SDK can be installed
        if command -v npm &> /dev/null; then
            ./uCode/packages/install-gemini.sh
            ./uCode/companion-system.sh init-chester
            log_success "Chester AI companion configured"
        else
            log_warning "NPM not available - Chester setup skipped"
        fi
    else
        log_info "Skipping Chester AI setup (disabled)"
    fi
}

# Configure shell integration
configure_shell() {
    log_info "Configuring shell integration..."
    
    # Determine shell config file
    SHELL_RC="$HOME/.bashrc"
    if [ -n "${ZSH_VERSION:-}" ]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    
    # Add uDOS configuration
    cat >> "$SHELL_RC" << EOF

# uDOS Configuration (added by installer)
export UDOS_HOME="$INSTALL_DIR"
export PATH="\$UDOS_HOME/uCode:\$PATH"
alias udos="cd \$UDOS_HOME && code ."
alias ucode="\$UDOS_HOME/uCode/ucode.sh"

EOF
    
    log_success "Shell integration configured"
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

# Main installation process
main() {
    print_header
    
    log_info "Starting uDOS installation for Ubuntu 22.04 LTS..."
    log_info "Target role: $USER_ROLE"
    log_info "Installation directory: $INSTALL_DIR"
    
    check_root
    detect_system
    update_system
    install_dependencies
    install_vscode
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
    echo "1. Restart your terminal or run: source ~/.bashrc"
    echo "2. Open uDOS: udos"
    echo "3. Start exploring: ucode help"
    
    if [ "$ENABLE_CHESTER" = "true" ]; then
        echo "4. Meet Chester: ucode CHESTER start"
    fi
    
    if [ "$DETECTED_DE" != "headless" ]; then
        echo "5. Desktop shortcut available in applications menu"
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

## 🔧 Ubuntu-Specific Features

### Package Management
- **APT Integration**: Uses native Ubuntu package manager
- **Repository Setup**: Adds official Microsoft VS Code repository
- **Dependency Resolution**: Handles Ubuntu-specific package names
- **Service Integration**: Systemd service support for background processes

### Desktop Environment Support
- **GNOME Integration**: Native integration with default Ubuntu desktop
- **Desktop Entries**: Creates application menu shortcuts
- **File Associations**: Configures markdown file handling
- **Theming**: Adapts to system theme preferences

### Security Considerations
- **No Root Execution**: Installer runs as regular user
- **Sudo Prompts**: Explicit permission requests for system changes
- **Package Verification**: GPG signature verification for repositories
- **Permission Settings**: Proper file and directory permissions

---

## 📋 Post-Installation

### System Integration
1. **Application Menu**: uDOS appears in development applications
2. **File Manager**: Right-click "Open with uDOS" for markdown files
3. **Terminal Integration**: ucode command available system-wide
4. **Update Mechanism**: Git-based updates through VS Code

### Troubleshooting
- **VS Code Repository**: Check repository key installation
- **Node.js Issues**: Verify NodeSource repository setup
- **Permission Errors**: Ensure user has sudo privileges
- **Desktop Entry**: Check XDG desktop environment variables

---

*This template generates a complete Ubuntu 22.04 LTS installer with native package management, desktop integration, and VS Code setup.*
