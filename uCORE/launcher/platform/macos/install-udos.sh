#!/bin/bash
# uDOS macOS Installer and Distribution Manager v1.0.4.1
# Complete macOS installation with role selection and terminal configuration

set -euo pipefail

# Configuration
readonly UDOS_GIT_URL="https://github.com/fredporter/uDOS.git"
readonly INSTALL_DIR="$HOME/uDOS"
readonly UDOS_VERSION="1.0.4.1"

# Color definitions
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

# Installation state
SELECTED_ROLE="wizard"
VSCODE_DETECTED=false
GIT_AVAILABLE=false

# Show installation banner
show_banner() {
    clear
    echo -e "${CYAN}"
    echo "   ██╗   ██╗██████╗  ██████╗ ███████╗"
    echo "   ██║   ██║██╔══██╗██╔═══██╗██╔════╝"
    echo "   ██║   ██║██║  ██║██║   ██║███████╗"
    echo "   ██║   ██║██║  ██║██║   ██║╚════██║"
    echo "   ╚██████╔╝██████╔╝╚██████╔╝███████║"
    echo "    ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝"
    echo -e "${NC}"
    echo -e "${WHITE}Universal Development Operating System${NC}"
    echo -e "${CYAN}macOS Distribution & Installation Manager v$UDOS_VERSION${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Check system prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking system prerequisites...${NC}"
    
    # Check macOS version
    local macos_version=$(sw_vers -productVersion)
    echo -e "${GREEN}✅ macOS $macos_version${NC}"
    
    # Check for git
    if command -v git >/dev/null 2>&1; then
        GIT_AVAILABLE=true
        local git_version=$(git --version | cut -d' ' -f3)
        echo -e "${GREEN}✅ Git $git_version${NC}"
    else
        echo -e "${YELLOW}⚠️  Git not found${NC}"
    fi
    
    # Check for VS Code
    if command -v code >/dev/null 2>&1; then
        VSCODE_DETECTED=true
        echo -e "${GREEN}✅ VS Code detected${NC}"
    else
        echo -e "${YELLOW}ℹ️  VS Code not detected${NC}"
    fi
    
    # Check for Terminal
    if command -v open >/dev/null 2>&1; then
        echo -e "${GREEN}✅ macOS Terminal support${NC}"
    fi
    
    echo ""
}

# Install Git if needed
install_git_if_needed() {
    if [[ "$GIT_AVAILABLE" == "false" ]]; then
        echo -e "${YELLOW}📦 Git installation required${NC}"
        echo ""
        echo "Git is required for uDOS installation and updates."
        echo ""
        echo -e "${WHITE}Installation options:${NC}"
        echo -e "  ${GREEN}[1]${NC} 🛠️  Install Xcode Command Line Tools (Recommended)"
        echo -e "  ${GREEN}[2]${NC} 🍺 Install via Homebrew (if available)"
        echo -e "  ${GREEN}[3]${NC} ❌ Cancel installation"
        echo ""
        read -p "👉 Choose installation method (1-3): " git_choice
        
        case "$git_choice" in
            1)
                echo -e "${BLUE}🛠️  Installing Xcode Command Line Tools...${NC}"
                xcode-select --install
                echo ""
                echo -e "${YELLOW}⏳ Please complete the Xcode installation in the popup window.${NC}"
                echo "After installation completes, run this installer again."
                echo ""
                read -p "Press Enter to exit..."
                exit 0
                ;;
            2)
                if command -v brew >/dev/null 2>&1; then
                    echo -e "${BLUE}🍺 Installing Git via Homebrew...${NC}"
                    brew install git
                    GIT_AVAILABLE=true
                else
                    echo -e "${RED}❌ Homebrew not found${NC}"
                    echo "Please install Homebrew first or choose option 1."
                    exit 1
                fi
                ;;
            3)
                echo -e "${YELLOW}Installation cancelled${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                exit 1
                ;;
        esac
    fi
}

# Show role selection menu
show_role_selection() {
    echo -e "${WHITE}🎭 uDOS Role Selection${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Choose your uDOS role based on your intended use:"
    echo ""
    
    echo -e "  ${GREEN}[1]${NC} 👻 ${CYAN}Ghost${NC} (Level 10) - Demo & Evaluation"
    echo "      └─ Limited demonstration and evaluation environment"
    echo ""
    
    echo -e "  ${GREEN}[2]${NC} ⚰️  ${YELLOW}Tomb${NC} (Level 20) - Archive Management"
    echo "      └─ Archive browsing and backup management tools"
    echo ""
    
    echo -e "  ${GREEN}[3]${NC} 🤖 ${BLUE}Drone${NC} (Level 40) - Task Automation"
    echo "      └─ Task automation and system monitoring"
    echo ""
    
    echo -e "  ${GREEN}[4]${NC} 👹 ${RED}Imp${NC} (Level 60) - Development Tools"
    echo "      └─ Script development and creative tools"
    echo ""
    
    echo -e "  ${GREEN}[5]${NC} 🔮 ${PURPLE}Sorcerer${NC} (Level 80) - Advanced User"
    echo "      └─ Advanced project management and administration"
    echo ""
    
    echo -e "  ${GREEN}[6]${NC} 🧙‍♂️ ${WHITE}Wizard${NC} (Level 100) - Full Development"
    echo "      └─ Complete system access and development tools"
    if [[ "$VSCODE_DETECTED" == "true" ]]; then
        echo "      └─ ✨ VS Code development mode available"
    fi
    echo ""
    
    read -p "👉 Select your role (1-6, default: 6): " role_choice
    
    case "$role_choice" in
        1) SELECTED_ROLE="ghost" ;;
        2) SELECTED_ROLE="tomb" ;;
        3) SELECTED_ROLE="drone" ;;
        4) SELECTED_ROLE="imp" ;;
        5) SELECTED_ROLE="sorcerer" ;;
        6|"") SELECTED_ROLE="wizard" ;;
        *)
            echo -e "${RED}Invalid choice, using Wizard role${NC}"
            SELECTED_ROLE="wizard"
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}✅ Selected role: ${SELECTED_ROLE}${NC}"
    echo ""
}

# Download or update uDOS from Git
download_or_update_udos() {
    if [[ -d "$INSTALL_DIR/.git" ]]; then
        echo -e "${BLUE}📥 Updating existing uDOS installation...${NC}"
        cd "$INSTALL_DIR"
        
        # Check for local changes
        if ! git diff --quiet || ! git diff --cached --quiet; then
            echo -e "${YELLOW}⚠️  Local changes detected${NC}"
            echo ""
            echo "Your installation has local changes. What would you like to do?"
            echo -e "  ${GREEN}[1]${NC} 💾 Backup changes and update"
            echo -e "  ${GREEN}[2]${NC} 🔄 Reset and update (discard changes)"
            echo -e "  ${GREEN}[3]${NC} ❌ Cancel update"
            echo ""
            read -p "👉 Your choice (1-3): " update_choice
            
            case "$update_choice" in
                1)
                    echo -e "${BLUE}💾 Creating backup branch...${NC}"
                    local backup_branch="backup-$(date +%Y%m%d-%H%M%S)"
                    git checkout -b "$backup_branch"
                    git add -A
                    git commit -m "Backup before update $(date)"
                    git checkout main
                    ;;
                2)
                    echo -e "${YELLOW}🔄 Resetting local changes...${NC}"
                    git reset --hard HEAD
                    git clean -fd
                    ;;
                3)
                    echo -e "${YELLOW}Update cancelled${NC}"
                    return
                    ;;
            esac
        fi
        
        # Perform update
        git fetch origin
        git reset --hard origin/main
        echo -e "${GREEN}✅ Update complete${NC}"
        
    else
        echo -e "${BLUE}📥 Downloading uDOS from Git...${NC}"
        
        # Remove existing directory if it exists but isn't a git repo
        if [[ -d "$INSTALL_DIR" ]]; then
            echo -e "${YELLOW}⚠️  Existing directory found, backing up...${NC}"
            mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d-%H%M%S)"
        fi
        
        # Clone repository
        if git clone "$UDOS_GIT_URL" "$INSTALL_DIR"; then
            cd "$INSTALL_DIR"
            echo -e "${GREEN}✅ Download complete${NC}"
        else
            echo -e "${RED}❌ Failed to download uDOS${NC}"
            echo "Please check your internet connection and try again."
            exit 1
        fi
    fi
    echo ""
}

# Setup role installation
setup_role_installation() {
    echo -e "${BLUE}🏗️  Setting up $SELECTED_ROLE installation...${NC}"
    
    cd "$INSTALL_DIR"
    
    # Ensure role directory exists
    if [[ ! -d "$SELECTED_ROLE" ]]; then
        echo -e "${YELLOW}⚠️  Role directory not found, creating...${NC}"
        mkdir -p "$SELECTED_ROLE"
    fi
    
    # Set up role-specific configuration
    if [[ -f "uCORE/distribution/roles/$SELECTED_ROLE/setup.sh" ]]; then
        echo -e "${BLUE}🔧 Running role-specific setup...${NC}"
        bash "uCORE/distribution/roles/$SELECTED_ROLE/setup.sh"
    fi
    
    # Set permissions
    find "$INSTALL_DIR" -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    chmod +x "$INSTALL_DIR/uDOS.app/Contents/MacOS/uDOS" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Role installation complete${NC}"
    echo ""
}

# Configure terminal settings
configure_terminal_settings() {
    echo -e "${BLUE}🎨 Configuring macOS Terminal settings...${NC}"
    
    # Copy uDOS terminal profile to user's home
    if [[ -f "$INSTALL_DIR/uDOS.terminal" ]]; then
        cp "$INSTALL_DIR/uDOS.terminal" "$HOME/Desktop/uDOS.terminal"
        echo -e "${GREEN}✅ uDOS terminal profile copied to Desktop${NC}"
        echo -e "${CYAN}💡 Double-click Desktop/uDOS.terminal to install the profile${NC}"
    fi
    
    echo ""
}

# Create desktop launchers
create_desktop_launchers() {
    echo -e "${BLUE}🚀 Creating desktop launchers...${NC}"
    
    # Copy .app bundle to Applications if desired
    echo ""
    echo "Would you like to install uDOS.app to Applications folder?"
    echo -e "  ${GREEN}[1]${NC} ✅ Yes, install to Applications"
    echo -e "  ${GREEN}[2]${NC} 🏠 No, keep in uDOS directory only"
    echo ""
    read -p "👉 Your choice (1-2, default: 1): " app_choice
    
    case "$app_choice" in
        1|"")
            if [[ -d "$INSTALL_DIR/uDOS.app" ]]; then
                echo -e "${BLUE}📱 Installing uDOS.app to Applications...${NC}"
                cp -R "$INSTALL_DIR/uDOS.app" "/Applications/"
                echo -e "${GREEN}✅ uDOS.app installed to Applications${NC}"
            fi
            ;;
        2)
            echo -e "${YELLOW}ℹ️  App bundle remains in uDOS directory${NC}"
            ;;
    esac
    
    # Create alias for command line access
    local shell_rc=""
    case "$SHELL" in
        */zsh) shell_rc="$HOME/.zshrc" ;;
        */bash) shell_rc="$HOME/.bash_profile" ;;
        *) shell_rc="$HOME/.profile" ;;
    esac
    
    if [[ -f "$shell_rc" ]]; then
        if ! grep -q "alias udos=" "$shell_rc"; then
            echo "" >> "$shell_rc"
            echo "# uDOS alias" >> "$shell_rc"
            echo "alias udos='$INSTALL_DIR/uCORE/launcher/universal/start-udos.sh'" >> "$shell_rc"
            echo -e "${GREEN}✅ Added 'udos' command alias to $shell_rc${NC}"
        fi
    fi
    
    echo ""
}

# Show completion summary
show_completion_summary() {
    echo -e "${GREEN}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 uDOS Installation Complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${NC}"
    
    echo -e "${WHITE}Installation Summary:${NC}"
    echo -e "  ${CYAN}📍 Location:${NC} $INSTALL_DIR"
    echo -e "  ${CYAN}🎭 Role:${NC} $SELECTED_ROLE"
    echo -e "  ${CYAN}📱 App Bundle:${NC} Available"
    echo -e "  ${CYAN}🎨 Terminal Profile:${NC} Available on Desktop"
    echo ""
    
    echo -e "${WHITE}Launch Options:${NC}"
    echo ""
    
    # Applications folder launcher
    if [[ -f "/Applications/uDOS.app/Contents/MacOS/uDOS" ]]; then
        echo -e "  ${GREEN}🍎 Applications Folder:${NC}"
        echo "     └─ Open Applications → uDOS.app"
    fi
    
    echo -e "  ${GREEN}🚀 Desktop App:${NC}"
    echo "     └─ Double-click: $INSTALL_DIR/uDOS.app"
    
    echo -e "  ${GREEN}🖥️  Command Line:${NC}"
    echo "     └─ Type: udos"
    echo "     └─ Or: $INSTALL_DIR/uCORE/launcher/universal/start-udos.sh"
    
    if [[ "$VSCODE_DETECTED" == "true" ]] && [[ "$SELECTED_ROLE" == "wizard" ]]; then
        echo -e "  ${GREEN}🧙‍♂️ VS Code Development:${NC}"
        echo "     └─ Launch app → Choose 'VS Code DEV Mode'"
        echo "     └─ Or: $INSTALL_DIR/uCORE/launcher/universal/start-dev.sh"
    fi
    
    echo ""
    echo -e "${WHITE}Quick Start:${NC}"
    echo "1. Install terminal profile: Double-click Desktop/uDOS.terminal"
    echo "2. Launch uDOS: Double-click uDOS.app or type 'udos'"
    echo "3. Choose your launch mode from the startup menu"
    echo ""
    
    echo -e "${CYAN}💡 For updates: Launch uDOS → System Update${NC}"
    echo ""
}

# Main installation process
main() {
    show_banner
    check_prerequisites
    install_git_if_needed
    show_role_selection
    download_or_update_udos
    setup_role_installation
    configure_terminal_settings
    create_desktop_launchers
    show_completion_summary
    
    echo -e "${YELLOW}Would you like to launch uDOS now? [y/N]:${NC} "
    read -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}🚀 Launching uDOS...${NC}"
        exec "$INSTALL_DIR/uDOS.app/Contents/MacOS/uDOS"
    else
        echo -e "${CYAN}👋 Installation complete. Launch uDOS anytime!${NC}"
    fi
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "uDOS macOS Installer v$UDOS_VERSION"
        echo ""
        echo "This installer downloads, configures, and sets up uDOS on macOS"
        echo "with full role-based access control and native app integration."
        echo ""
        echo "Usage: $0 [--help]"
        echo ""
        echo "Features:"
        echo "  • Git-based installation and updates"
        echo "  • Role-based permission system (6 roles)"
        echo "  • Native macOS app bundle"
        echo "  • Terminal profile configuration"
        echo "  • VS Code development mode (wizard only)"
        echo "  • Desktop and command-line launchers"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
