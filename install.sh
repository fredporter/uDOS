#!/bin/bash
# uDOS v1.0.4.1 Universal Installer
# Clean distribution with role-based installation system

set -euo pipefail

# Configuration
readonly UDOS_GIT_URL="https://github.com/fredporter/uDOS.git"
readonly UDOS_VERSION="1.0.4.1"
readonly INSTALL_DIR="$HOME/uDOS"

# Polaroid Colors — Foreground + Background (xterm-256 with ANSI fallback)
if [[ $TERM =~ 256color ]]; then
  # Foreground
  readonly RED='\033[38;5;203m'     # Orange Pop
  readonly GREEN='\033[38;5;154m'   # Lime Glow
  readonly YELLOW='\033[38;5;226m'  # Yellow Burst
  readonly BLUE='\033[38;5;33m'     # Cyan Flash
  readonly PURPLE='\033[38;5;198m'  # Magenta Snap
  readonly CYAN='\033[38;5;38m'     # Cyan Flash deeper
  readonly WHITE='\033[38;5;15m'    # Bright white
  readonly NC='\033[0m'

  # Background
  readonly BG_RED='\033[48;5;203m'
  readonly BG_GREEN='\033[48;5;154m'
  readonly BG_YELLOW='\033[48;5;226m'
  readonly BG_BLUE='\033[48;5;33m'
  readonly BG_PURPLE='\033[48;5;198m'
  readonly BG_CYAN='\033[48;5;38m'
  readonly BG_WHITE='\033[48;5;15m'
else
  # Classic ANSI fallback
  readonly RED='\033[0;31m'
  readonly GREEN='\033[1;32m'
  readonly YELLOW='\033[1;33m'
  readonly BLUE='\033[0;34m'
  readonly PURPLE='\033[0;35m'
  readonly CYAN='\033[0;36m'
  readonly WHITE='\033[1;37m'
  readonly NC='\033[0m'

  readonly BG_RED='\033[41m'
  readonly BG_GREEN='\033[42m'
  readonly BG_YELLOW='\033[43m'
  readonly BG_BLUE='\033[44m'
  readonly BG_PURPLE='\033[45m'
  readonly BG_CYAN='\033[46m'
  readonly BG_WHITE='\033[47m'
fi

# Installation state
SELECTED_ROLES=()
VSCODE_DETECTED=false
GIT_AVAILABLE=false

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
    echo -e "${CYAN}Clean Distribution Installer v$UDOS_VERSION${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

check_prerequisites() {
    echo -e "${BLUE}🔍 Checking system prerequisites...${NC}"

    # Detect OS
    case "$(uname -s)" in
        Darwin)
            echo -e "${GREEN}✅ macOS detected${NC}"
            local os_version=$(sw_vers -productVersion)
            echo -e "${GREEN}   Version: $os_version${NC}"
            ;;
        Linux)
            echo -e "${GREEN}✅ Linux detected${NC}"
            if [[ -f /etc/os-release ]]; then
                local distro=$(grep '^NAME=' /etc/os-release | cut -d'"' -f2)
                echo -e "${GREEN}   Distribution: $distro${NC}"
            fi
            ;;
        *)
            echo -e "${YELLOW}⚠️  Unsupported OS detected${NC}"
            echo "This installer supports macOS and Linux only."
            ;;
    esac

    echo ""
    echo -e "${BLUE}🔧 Checking required dependencies...${NC}"
    
    # Check critical dependencies
    local missing_deps=()
    local optional_deps=()

    # Essential dependencies
    if command -v git >/dev/null 2>&1; then
        GIT_AVAILABLE=true
        local git_version=$(git --version | cut -d' ' -f3)
        echo -e "${GREEN}✅ Git $git_version${NC}"
    else
        echo -e "${RED}❌ Git - REQUIRED for installation${NC}"
        missing_deps+=("git")
    fi

    if command -v bash >/dev/null 2>&1; then
        local bash_version="${BASH_VERSION%%.*}"
        if [[ "$bash_version" -ge 4 ]]; then
            echo -e "${GREEN}✅ Bash $BASH_VERSION${NC}"
        else
            echo -e "${YELLOW}⚠️  Bash $BASH_VERSION (v4+ recommended)${NC}"
        fi
    fi

    if command -v jq >/dev/null 2>&1; then
        local jq_version=$(jq --version | cut -d'-' -f2)
        echo -e "${GREEN}✅ jq $jq_version${NC}"
    else
        echo -e "${YELLOW}⚠️  jq - REQUIRED for session management${NC}"
        missing_deps+=("jq")
    fi

    if command -v python3 >/dev/null 2>&1; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}✅ Python $python_version${NC}"
        
        # Check for python3-venv on Linux
        if [[ "$(uname -s)" == "Linux" ]]; then
            if python3 -c "import venv" 2>/dev/null; then
                echo -e "${GREEN}✅ python3-venv available${NC}"
            else
                echo -e "${YELLOW}⚠️  python3-venv - REQUIRED for virtual environments${NC}"
                missing_deps+=("python3-venv")
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Python 3 - REQUIRED for web features${NC}"
        missing_deps+=("python3")
    fi

    if command -v curl >/dev/null 2>&1; then
        echo -e "${GREEN}✅ curl available${NC}"
    else
        echo -e "${YELLOW}⚠️  curl - recommended for network operations${NC}"
        optional_deps+=("curl")
    fi

    # Optional but recommended
    if command -v code >/dev/null 2>&1; then
        VSCODE_DETECTED=true
        echo -e "${GREEN}✅ VS Code detected${NC}"
    else
        echo -e "${YELLOW}ℹ️  VS Code not detected (optional)${NC}"
    fi

    # Handle missing dependencies
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo ""
        echo -e "${RED}❌ Missing required dependencies: ${missing_deps[*]}${NC}"
        echo -e "${YELLOW}🔧 Install commands for your system:${NC}"
        
        case "$(uname -s)" in
            Darwin)
                echo "  macOS: brew install ${missing_deps[*]}"
                if [[ " ${missing_deps[*]} " =~ " git " ]]; then
                    echo "         or: xcode-select --install"
                fi
                ;;
            Linux)
                if command -v apt >/dev/null 2>&1; then
                    echo "  Ubuntu/Debian: sudo apt update && sudo apt install ${missing_deps[*]}"
                    # Handle python3-venv specifically
                    if [[ " ${missing_deps[*]} " =~ " python3-venv " ]]; then
                        local python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1-2)
                        echo "                 sudo apt install python${python_version}-venv"
                    fi
                elif command -v yum >/dev/null 2>&1; then
                    echo "  CentOS/RHEL: sudo yum install ${missing_deps[*]}"
                elif command -v dnf >/dev/null 2>&1; then
                    echo "  Fedora: sudo dnf install ${missing_deps[*]}"
                elif command -v pacman >/dev/null 2>&1; then
                    echo "  Arch: sudo pacman -S ${missing_deps[*]}"
                fi
                ;;
        esac
        echo ""
        echo -e "${BLUE}Would you like to install missing dependencies automatically? (y/N)${NC}"
        read -p "> " auto_install
        
        if [[ "$auto_install" =~ ^[Yy]$ ]]; then
            install_missing_dependencies "${missing_deps[@]}"
        else
            echo -e "${YELLOW}Please install missing dependencies and re-run the installer.${NC}"
            exit 1
        fi
    fi

    echo ""
}

install_missing_dependencies() {
    local deps=("$@")
    echo -e "${BLUE}📦 Installing missing dependencies: ${deps[*]}${NC}"
    
    case "$(uname -s)" in
        Darwin)
            if command -v brew >/dev/null 2>&1; then
                echo -e "${BLUE}Using Homebrew...${NC}"
                for dep in "${deps[@]}"; do
                    echo -e "${BLUE}Installing $dep...${NC}"
                    brew install "$dep" || echo -e "${YELLOW}Warning: Failed to install $dep${NC}"
                done
            else
                echo -e "${RED}Homebrew not found. Please install manually:${NC}"
                echo "  Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                echo "  Then run: brew install ${deps[*]}"
                exit 1
            fi
            ;;
        Linux)
            if command -v apt >/dev/null 2>&1; then
                echo -e "${BLUE}Using apt (Ubuntu/Debian)...${NC}"
                sudo apt update
                for dep in "${deps[@]}"; do
                    echo -e "${BLUE}Installing $dep...${NC}"
                    # Handle python3-venv specifically  
                    if [[ "$dep" == "python3-venv" ]]; then
                        local python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1-2)
                        sudo apt install -y "python${python_version}-venv" || echo -e "${YELLOW}Warning: Failed to install python${python_version}-venv${NC}"
                    else
                        sudo apt install -y "$dep" || echo -e "${YELLOW}Warning: Failed to install $dep${NC}"
                    fi
                done
            elif command -v yum >/dev/null 2>&1; then
                echo -e "${BLUE}Using yum (CentOS/RHEL)...${NC}"
                for dep in "${deps[@]}"; do
                    echo -e "${BLUE}Installing $dep...${NC}"
                    sudo yum install -y "$dep" || echo -e "${YELLOW}Warning: Failed to install $dep${NC}"
                done
            elif command -v dnf >/dev/null 2>&1; then
                echo -e "${BLUE}Using dnf (Fedora)...${NC}"
                for dep in "${deps[@]}"; do
                    echo -e "${BLUE}Installing $dep...${NC}"
                    sudo dnf install -y "$dep" || echo -e "${YELLOW}Warning: Failed to install $dep${NC}"
                done
            elif command -v pacman >/dev/null 2>&1; then
                echo -e "${BLUE}Using pacman (Arch)...${NC}"
                for dep in "${deps[@]}"; do
                    echo -e "${BLUE}Installing $dep...${NC}"
                    sudo pacman -S --noconfirm "$dep" || echo -e "${YELLOW}Warning: Failed to install $dep${NC}"
                done
            else
                echo -e "${RED}No supported package manager found.${NC}"
                echo "Please install manually: ${deps[*]}"
                exit 1
            fi
            ;;
    esac
    
    echo -e "${GREEN}✅ Dependency installation completed${NC}"
    echo ""
}

install_git_if_needed() {
    if [[ "$GIT_AVAILABLE" == "false" ]]; then
        echo -e "${YELLOW}📦 Git installation required${NC}"
        echo ""

        case "$(uname -s)" in
            Darwin)
                echo "Git installation options for macOS:"
                echo -e "  ${GREEN}[1]${NC} Install Xcode Command Line Tools (Recommended)"
                echo -e "  ${GREEN}[2]${NC} Install via Homebrew (if available)"
                echo -e "  ${GREEN}[3]${NC} Cancel installation"
                echo ""
                read -p "Choose installation method (1-3): " git_choice

                case "$git_choice" in
                    1)
                        echo -e "${BLUE}Installing Xcode Command Line Tools...${NC}"
                        xcode-select --install
                        echo -e "${YELLOW}Complete the installation and re-run this script.${NC}"
                        exit 0
                        ;;
                    2)
                        if command -v brew >/dev/null 2>&1; then
                            brew install git
                            GIT_AVAILABLE=true
                        else
                            echo -e "${RED}Homebrew not found${NC}"
                            exit 1
                        fi
                        ;;
                    *)
                        echo -e "${YELLOW}Installation cancelled${NC}"
                        exit 0
                        ;;
                esac
                ;;
            Linux)
                echo "Install Git using your distribution's package manager:"
                echo "  Ubuntu/Debian: sudo apt update && sudo apt install git"
                echo "  CentOS/RHEL:   sudo yum install git"
                echo "  Fedora:        sudo dnf install git"
                echo "  Arch:          sudo pacman -S git"
                exit 1
                ;;
        esac
    fi
}

show_role_selection() {
    echo -e "${WHITE}🎭 uDOS Role Selection${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${CYAN}NEW in v1.4: Multi-role installation system${NC}"
    echo "You can install multiple roles. Each role is installed separately in uMEMORY/role/ folder."
    echo ""

    echo -e "  ${GREEN}[1]${NC} 👻 ${CYAN}Ghost${NC} (Level 10) - Demo & Evaluation"
    echo "      └─ Limited demonstration environment"
    echo ""

    echo -e "  ${GREEN}[2]${NC} ⚰️  ${YELLOW}Tomb${NC} (Level 20) - Archive Management"
    echo "      └─ Archive browsing and backup tools"
    echo ""

    echo -e "  ${GREEN}[3]${NC} 🤖 ${BLUE}Drone${NC} (Level 40) - Task Automation"
    echo "      └─ Automation and monitoring tools"
    echo ""

    echo -e "  ${GREEN}[4]${NC} 👹 ${RED}Imp${NC} (Level 60) - Development Tools"
    echo "      └─ Script development and creative tools"
    echo ""

    echo -e "  ${GREEN}[5]${NC} 🔮 ${PURPLE}Sorcerer${NC} (Level 80) - Advanced User"
    echo "      └─ Project management and administration"
    echo ""

    echo -e "  ${GREEN}[6]${NC} 🧙‍♂️ ${WHITE}Wizard${NC} (Level 100) - Full Development"
    echo "      └─ Complete development environment"
    if [[ "$VSCODE_DETECTED" == "true" ]]; then
        echo "      └─ ✨ VS Code development mode included"
    fi
    echo ""

    echo -e "  ${GREEN}[A]${NC} 🌟 Install All Roles"
    echo -e "  ${GREEN}[Q]${NC} ❌ Quit Installation"
    echo ""

    echo -e "${YELLOW}💡 You can select multiple roles by entering numbers separated by spaces${NC}"
    echo -e "${YELLOW}   Example: '1 3 6' installs Ghost, Drone, and Wizard roles${NC}"
    echo ""

    read -p "👉 Select roles (1-6, A for all, Q to quit): " role_input

    case "$role_input" in
        [Qq])
            echo -e "${YELLOW}Installation cancelled${NC}"
            exit 0
            ;;
        [Aa])
            SELECTED_ROLES=("ghost" "tomb" "drone" "imp" "sorcerer" "wizard")
            echo -e "${GREEN}✅ All roles selected${NC}"
            ;;
        *)
            # Parse individual role selections
            for role_num in $role_input; do
                case "$role_num" in
                    1) SELECTED_ROLES+=("ghost") ;;
                    2) SELECTED_ROLES+=("tomb") ;;
                    3) SELECTED_ROLES+=("drone") ;;
                    4) SELECTED_ROLES+=("imp") ;;
                    5) SELECTED_ROLES+=("sorcerer") ;;
                    6) SELECTED_ROLES+=("wizard") ;;
                    *)
                        echo -e "${YELLOW}⚠️  Invalid role: $role_num (skipped)${NC}"
                        ;;
                esac
            done
            ;;
    esac

    if [[ ${#SELECTED_ROLES[@]} -eq 0 ]]; then
        echo -e "${RED}❌ No valid roles selected${NC}"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}✅ Selected roles: ${SELECTED_ROLES[*]}${NC}"
    echo ""
}

download_clean_distribution() {
    echo -e "${BLUE}📥 Downloading clean uDOS distribution...${NC}"

    # Remove existing directory if it exists but warn user
    if [[ -d "$INSTALL_DIR" ]]; then
        echo -e "${YELLOW}⚠️  Existing installation found at $INSTALL_DIR${NC}"
        echo ""
        echo "What would you like to do?"
        echo -e "  ${GREEN}[1]${NC} 💾 Backup existing installation and continue"
        echo -e "  ${GREEN}[2]${NC} 🔄 Remove existing installation and continue"
        echo -e "  ${GREEN}[3]${NC} ❌ Cancel installation"
        echo ""
        read -p "Your choice (1-3): " existing_choice

        case "$existing_choice" in
            1)
                local backup_dir="${INSTALL_DIR}.backup.$(date +%Y%m%d-%H%M%S)"
                echo -e "${BLUE}💾 Creating backup at $backup_dir...${NC}"
                mv "$INSTALL_DIR" "$backup_dir"
                echo -e "${GREEN}✅ Backup created${NC}"
                ;;
            2)
                echo -e "${YELLOW}🗑️  Removing existing installation...${NC}"
                rm -rf "$INSTALL_DIR"
                ;;
            3)
                echo -e "${YELLOW}Installation cancelled${NC}"
                exit 0
                ;;
        esac
    fi

    # Clone clean distribution
    echo -e "${BLUE}📡 Cloning from GitHub...${NC}"
    if git clone "$UDOS_GIT_URL" "$INSTALL_DIR"; then
        cd "$INSTALL_DIR"
        echo -e "${GREEN}✅ Clean distribution downloaded${NC}"

        # Show what we got
        echo -e "${CYAN}📦 Distribution contains:${NC}"
        echo "   • Core system (uCORE/)"
        echo "   • Development framework (dev/)"
        echo "   • Sandbox framework (sandbox/)"
        echo "   • Documentation (docs/)"
        echo "   • Role installers (uCORE/distribution/)"
    else
        echo -e "${RED}❌ Failed to download uDOS${NC}"
        exit 1
    fi
    echo ""
}

install_selected_roles() {
    echo -e "${BLUE}🎭 Installing selected roles...${NC}"

    for role in "${SELECTED_ROLES[@]}"; do
        echo ""
        echo -e "${CYAN}Installing ${role} role...${NC}"

        # Create role directory structure
        mkdir -p "uMEMORY/role/$role"/{config,data,projects,logs}

        # Run role-specific installer if it exists
        local role_installer="uCORE/distribution/$role/install.sh"
        if [[ -f "$role_installer" ]]; then
            bash "$role_installer" "uMEMORY/role/$role"
        else
            echo -e "${BLUE}  📁 Created basic role structure${NC}"
        fi

        # Set up role configuration
        cat > "uMEMORY/role/$role/config/role.conf" << EOF
# uDOS Role Configuration
ROLE_NAME="$role"
ROLE_LEVEL=$(case "$role" in
    ghost) echo "10" ;;
    tomb) echo "20" ;;
    drone) echo "40" ;;
    imp) echo "60" ;;
    sorcerer) echo "80" ;;
    wizard) echo "100" ;;
esac)
INSTALL_DATE="$(date)"
INSTALL_VERSION="$UDOS_VERSION"
EOF

        echo -e "${GREEN}  ✅ $role role installed${NC}"
    done

    # Set up Python environment for web display system
    echo ""
    echo -e "${BLUE}🐍 Setting up Python environment for display system...${NC}"
    if [[ -f "uSCRIPT/setup-environment.sh" ]]; then
        cd uSCRIPT && ./setup-environment.sh
        cd ..
        echo -e "${GREEN}  ✅ Python environment configured${NC}"
    else
        echo -e "${YELLOW}  ⚠️ Python environment setup skipped${NC}"
    fi

    echo ""
    echo -e "${GREEN}✅ All roles installed in uMEMORY/role/ directory${NC}"
}setup_user_directories() {
    echo -e "${BLUE}👤 Setting up user directories...${NC}"

    # Create user directory structure
    mkdir -p USER/{memory,sandbox,dev,extensions}
    mkdir -p USER/memory/{missions,moves,milestones,sessions}
    mkdir -p USER/sandbox/{experiments,projects,logs,temp}
    mkdir -p USER/dev/{notes,briefings,roadmaps,config}

    # Create user configuration
    cat > USER/config.json << EOF
{
    "user": {
        "install_date": "$(date -Iseconds)",
        "udos_version": "$UDOS_VERSION",
        "roles_installed": [$(printf '"%s",' "${SELECTED_ROLES[@]}" | sed 's/,$//')],
        "data_isolation": true
    }
}
EOF

    echo -e "${GREEN}✅ User directories created${NC}"
}

setup_vscode_development() {
    if [[ "$VSCODE_DETECTED" == "true" ]] && [[ " ${SELECTED_ROLES[*]} " == *" wizard "* ]]; then
        echo -e "${BLUE}🧙‍♂️ Setting up VS Code development environment...${NC}"
        
        # Run VS Code setup script
        if [ -f "$INSTALL_DIR/uCORE/launcher/vscode/setup-vscode.sh" ]; then
            cd "$INSTALL_DIR"
            "$INSTALL_DIR/uCORE/launcher/vscode/setup-vscode.sh" > /dev/null 2>&1
            
            echo -e "${GREEN}✅ VS Code workspace configured${NC}"
            echo -e "${GREEN}✅ Development extensions recommended${NC}"
            echo -e "${GREEN}✅ Debugging configurations ready${NC}"
            echo -e "${GREEN}✅ uDOS code snippets installed${NC}"
        else
            echo -e "${YELLOW}⚠️ VS Code setup script not found${NC}"
        fi
    fi
}

setup_backup_system() {
    echo -e "${BLUE}💾 Setting up centralized backup system...${NC}"

    # Create backup directory structure
    mkdir -p BACKUP/{daily,weekly,migrations,role-configs,user-data,system}

    # Create backup configuration
    cat > BACKUP/backup.conf << EOF
# uDOS Centralized Backup Configuration
BACKUP_ROOT="$INSTALL_DIR/BACKUP"
AUTO_BACKUP_ENABLED=true
DAILY_RETENTION_DAYS=7
WEEKLY_RETENTION_WEEKS=4
MIGRATION_RETENTION_MONTHS=6

# Backup schedule (if using cron)
# Daily:  0 2 * * * $INSTALL_DIR/uCORE/bin/backup.sh daily
# Weekly: 0 3 * * 0 $INSTALL_DIR/uCORE/bin/backup.sh weekly
EOF

    echo -e "${GREEN}✅ Backup system configured${NC}"
}

create_launch_scripts() {
    echo -e "${BLUE}🚀 Creating launch scripts...${NC}"

    # Create main launcher
    cat > udos.sh << 'EOF'
#!/bin/bash
# uDOS v1.4 Main Launcher
# Supports multi-role installations

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$UDOS_ROOT"

# Show role selection if multiple roles installed
if [[ $(ls uMEMORY/role/ 2>/dev/null | wc -l) -gt 1 ]]; then
    echo "Multiple roles installed. Select role to launch:"
    echo ""
    select role in $(ls uMEMORY/role/ 2>/dev/null) "System Menu"; do
        case "$role" in
            "System Menu")
                exec ./uCORE/launcher/universal/start-udos.sh
                ;;
            "")
                echo "Invalid selection"
                ;;
            *)
                if [[ -d "uMEMORY/role/$role" ]]; then
                    export UDOS_ACTIVE_ROLE="$role"
                    exec ./uCORE/launcher/universal/start-udos.sh
                else
                    echo "Role not found: $role"
                fi
                ;;
        esac
    done
else
    # Single role or no roles - use default launcher
    exec ./uCORE/launcher/universal/start-udos.sh
fi
EOF

    chmod +x udos.sh

    # Create role-specific launchers
    for role in "${SELECTED_ROLES[@]}"; do
        cat > "launch-$role.sh" << EOF
#!/bin/bash
# uDOS $role Role Launcher
export UDOS_ACTIVE_ROLE="$role"
cd "\$(dirname "\${BASH_SOURCE[0]}")"
exec ./uCORE/launcher/universal/start-udos.sh
EOF
        chmod +x "launch-$role.sh"
    done

    echo -e "${GREEN}✅ Launch scripts created${NC}"
}

setup_shell_integration() {
    echo -e "${BLUE}🐚 Setting up shell integration...${NC}"

    # Detect shell and create alias
    local shell_rc=""
    case "$SHELL" in
        */zsh) shell_rc="$HOME/.zshrc" ;;
        */bash) shell_rc="$HOME/.bash_profile" ;;
        *) shell_rc="$HOME/.profile" ;;
    esac

    if [[ -f "$shell_rc" ]] && ! grep -q "alias udos=" "$shell_rc" 2>/dev/null; then
        echo "" >> "$shell_rc"
        echo "# uDOS v1.4 integration" >> "$shell_rc"
        echo "alias udos='$INSTALL_DIR/udos.sh'" >> "$shell_rc"
        echo "export UDOS_ROOT='$INSTALL_DIR'" >> "$shell_rc"
        echo -e "${GREEN}✅ Shell integration added to $shell_rc${NC}"
    fi

    echo ""
}

show_installation_summary() {
    echo ""
    echo -e "${GREEN}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 uDOS v1.4 Installation Complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${NC}"

    echo -e "${WHITE}Installation Summary:${NC}"
    echo -e "  ${CYAN}📍 Location:${NC} $INSTALL_DIR"
    echo -e "  ${CYAN}🎭 Roles:${NC} ${SELECTED_ROLES[*]}"
    echo -e "  ${CYAN}📁 Structure:${NC} Role/User/Backup isolation"
    echo -e "  ${CYAN}🔄 Updates:${NC} Clean git distribution"
    echo ""

    echo -e "${WHITE}Directory Structure:${NC}"
    echo -e "  ${CYAN}uMEMORY/role/${NC} - Role installations ($(ls uMEMORY/role/ 2>/dev/null | wc -l) roles)"
    echo -e "  ${CYAN}USER/${NC} - Your personal data & configurations"
    echo -e "  ${CYAN}BACKUP/${NC} - Centralized backup system"
    echo -e "  ${CYAN}Core System${NC} - uCORE/, docs/, dev/, sandbox/"
    echo ""

    echo -e "${WHITE}Launch Options:${NC}"
    echo ""

    echo -e "  ${GREEN}🚀 Main Launcher:${NC}"
    echo "     └─ Command: udos"
    echo "     └─ Script: $INSTALL_DIR/udos.sh"

    if [[ ${#SELECTED_ROLES[@]} -gt 1 ]]; then
        echo -e "  ${GREEN}🎭 Role-specific Launchers:${NC}"
        for role in "${SELECTED_ROLES[@]}"; do
            echo "     └─ $role: ./launch-$role.sh"
        done
    fi

    if [[ "$VSCODE_DETECTED" == "true" ]] && [[ " ${SELECTED_ROLES[*]} " == *" wizard "* ]]; then
        echo -e "  ${GREEN}🧙‍♂️ VS Code Development:${NC}"
        echo "     └─ Launch udos → Choose VS Code mode"
    fi

    echo ""
    echo -e "${WHITE}Key Features:${NC}"
    echo -e "  ${GREEN}✅${NC} Clean distribution (no personal data on GitHub)"
    echo -e "  ${GREEN}✅${NC} Multi-role support with isolation"
    echo -e "  ${GREEN}✅${NC} Centralized backup system"
    echo -e "  ${GREEN}✅${NC} Easy updates via git"
    echo -e "  ${GREEN}✅${NC} Personal data preserved locally"
    echo ""

    echo -e "${CYAN}💡 Your personal data stays in uMEMORY/user/ and uMEMORY/role/ folders${NC}"
    echo -e "${CYAN}💡 Updates only affect core system, preserving your data${NC}"
    echo ""
}

main() {
    show_banner
    check_prerequisites
    install_git_if_needed
    show_role_selection
    download_clean_distribution
    install_selected_roles
    setup_user_directories
    setup_vscode_development
    setup_backup_system
    create_launch_scripts
    setup_shell_integration
    show_installation_summary

    echo -e "${YELLOW}Would you like to launch uDOS now? [y/N]:${NC} "
    read -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}🚀 Launching uDOS...${NC}"
        exec ./udos.sh
    else
        echo -e "${CYAN}👋 Installation complete. Type 'udos' to launch!${NC}"
    fi
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "uDOS v1.4 Universal Installer"
        echo ""
        echo "Clean distribution installer with role-based isolation system."
        echo ""
        echo "Usage: $0 [--help]"
        echo ""
        echo "Features:"
        echo "  • Clean Git distribution (no personal data)"
        echo "  • Multi-role installation system"
        echo "  • Role/User/Backup data isolation"
        echo "  • Centralized backup management"
        echo "  • Easy updates preserving personal data"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
