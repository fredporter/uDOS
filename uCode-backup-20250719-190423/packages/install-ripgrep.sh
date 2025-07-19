#!/bin/bash
# uDOS Package Installation Script for ripgrep
# Version: v2.0.0
# Purpose: Install ripgrep (rg) with uDOS integration and template support

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
PACKAGE_NAME="ripgrep"
COMMAND_NAME="rg"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
    [[ -d "$UHOME/uMemory/logs" ]] && echo "[$(date)] INFO: $1" >> "$UHOME/uMemory/logs/package-install.log"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    [[ -d "$UHOME/uMemory/logs" ]] && echo "[$(date)] SUCCESS: $1" >> "$UHOME/uMemory/logs/package-install.log"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" >&2
    [[ -d "$UHOME/uMemory/logs" ]] && echo "[$(date)] ERROR: $1" >> "$UHOME/uMemory/logs/package-install.log"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    [[ -d "$UHOME/uMemory/logs" ]] && echo "[$(date)] WARNING: $1" >> "$UHOME/uMemory/logs/package-install.log"
}

echo -e "${CYAN}📦 uDOS Package Installer: ripgrep v2.0.0${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create necessary directories
mkdir -p "$UHOME/uMemory/logs"
mkdir -p "$UHOME/uMemory/packages/installed"
mkdir -p "$UHOME/uMemory/packages/configs"

# Check if already installed
if command -v "$COMMAND_NAME" >/dev/null 2>&1; then
    existing_version=$($COMMAND_NAME --version | head -1)
    log_warning "$PACKAGE_NAME is already installed: $existing_version"
    
    # Ask if user wants to continue
    read -p "Continue with installation? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

log_info "Installing $PACKAGE_NAME for uDOS integration..."

# Detect OS and install
case "$(uname -s)" in
    Darwin)
        log_info "Detected macOS - installing via Homebrew or direct download"
        if command -v brew >/dev/null 2>&1; then
            log_info "Installing via Homebrew..."
            brew install ripgrep
        else
            log_warning "Homebrew not found - attempting direct download"
            # Get latest release info
            if command -v curl >/dev/null 2>&1; then
                latest_url=$(curl -s https://api.github.com/repos/BurntSushi/ripgrep/releases/latest | grep "browser_download_url.*apple-darwin.*tar.gz" | cut -d '"' -f 4)
                if [[ -n "$latest_url" ]]; then
                    log_info "Downloading from: $latest_url"
                    curl -L "$latest_url" | tar -xz -C /tmp
                    sudo cp /tmp/rg-*/rg /usr/local/bin/
                    log_success "Installed ripgrep via direct download"
                else
                    log_error "Failed to find download URL"
                    log_error "Please install Homebrew or download manually from: https://github.com/BurntSushi/ripgrep/releases"
                    exit 1
                fi
            else
                log_error "curl not available for download"
                log_error "Please install Homebrew or download manually from: https://github.com/BurntSushi/ripgrep/releases"
                exit 1
            fi
        fi
        ;;
    Linux)
        log_info "Detected Linux - installing ripgrep"
        # Try package managers in order of preference
        if command -v apt >/dev/null 2>&1; then
            log_info "Installing via apt..."
            sudo apt update && sudo apt install -y ripgrep
        elif command -v yum >/dev/null 2>&1; then
            log_info "Installing via yum..."
            sudo yum install -y ripgrep
        elif command -v dnf >/dev/null 2>&1; then
            log_info "Installing via dnf..."
            sudo dnf install -y ripgrep
        elif command -v pacman >/dev/null 2>&1; then
            log_info "Installing via pacman..."
            sudo pacman -S ripgrep
        elif command -v snap >/dev/null 2>&1; then
            log_info "Installing via snap..."
            sudo snap install ripgrep --classic
        else
            log_error "No compatible package manager found"
            log_error "Please install ripgrep manually from: https://github.com/BurntSushi/ripgrep/releases"
            exit 1
        fi
        ;;
    *)
        log_error "Unsupported operating system: $(uname -s)"
        log_error "Please install ripgrep manually from: https://github.com/BurntSushi/ripgrep/releases"
        exit 1
        ;;
esac

# Verify installation
if command -v "$COMMAND_NAME" >/dev/null 2>&1; then
    installed_version=$($COMMAND_NAME --version | head -1)
    log_success "$PACKAGE_NAME installed successfully: $installed_version"
else
    log_error "Installation failed - $COMMAND_NAME not found in PATH"
    exit 1
fi
        if command -v apt >/dev/null 2>&1; then
            sudo apt update && sudo apt install -y ripgrep
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y ripgrep
        else
            echo "⚠️  Package manager not found - please install ripgrep manually"
            exit 1
        fi
        ;;
    *)
        echo "❌ Unsupported OS: $(uname -s)"
        exit 1
        ;;
esac

# Verify installation
if command -v rg >/dev/null 2>&1; then
    echo "✅ ripgrep installed successfully: $(rg --version)"
    
    # Create uDOS integration wrapper
    mkdir -p "$(dirname "$0")"
    cat > "$(dirname "$0")/run-ripgrep.sh" << 'EOF'
#!/bin/bash
# uDOS ripgrep wrapper
# Usage: ./uCode/packages/run-ripgrep.sh [search term] [path]

SEARCH_TERM="${1:-TODO}"
SEARCH_PATH="${2:-./uMemory/}"

# Create uDOS integration
log_info "Setting up uDOS integration..."

# Create shortcode integration script
cat > "$SCRIPT_DIR/run-ripgrep.sh" << 'EOF'
#!/bin/bash
# uDOS ripgrep integration script
# Generated by package installer v2.0.0

SEARCH_TERM="${1:-}"
SEARCH_PATH="${2:-./}"
UHOME="${UHOME:-$HOME/uDOS}"

if [[ -z "$SEARCH_TERM" ]]; then
    echo "Usage: $0 'search term' '[path]'"
    echo "Example: $0 'function.*process' './uCode/'"
    exit 1
fi

echo "🔍 Searching for '$SEARCH_TERM' in $SEARCH_PATH"
rg "$SEARCH_TERM" "$SEARCH_PATH" --type md --context 2 --color always

# Log search to uMemory
mkdir -p "$UHOME/uMemory/logs"
echo "$(date): Searched for '$SEARCH_TERM' in $SEARCH_PATH" >> "$UHOME/uMemory/logs/package-usage.log"
EOF

chmod +x "$SCRIPT_DIR/run-ripgrep.sh"
log_success "Created uDOS wrapper: run-ripgrep.sh"

# Process configuration template if available
if [[ -f "$UHOME/uTemplate/package-config-ripgrep.md" ]]; then
    log_info "Processing configuration template..."
    
    # Create configuration directory
    mkdir -p "$UHOME/uMemory/packages/configs"
    
    # Copy and process template
    config_file="$UHOME/uMemory/packages/configs/ripgrep.md"
    cp "$UHOME/uTemplate/package-config-ripgrep.md" "$config_file"
    
    # Basic variable substitution
    sed -i.bak \
        -e "s/{{timestamp}}/$(date -Iseconds)/g" \
        -e "s/{{username}}/$(whoami)/g" \
        -e "s/{{package_version}}/$installed_version/g" \
        -e "s/{{location}}/$(pwd)/g" \
        "$config_file" && rm "$config_file.bak"
    
    log_success "Configuration created: $config_file"
    
    # Create ripgrep config file
    mkdir -p ~/.config/ripgrep
    cat > ~/.config/ripgrep/config << 'RGCONF'
# uDOS ripgrep configuration
# Generated by package installer v2.0.0

# Search behavior
--smart-case
--follow
--hidden

# Output formatting
--line-number
--column
--color=always
--heading

# File type associations
--type-add=ucode:*.md,*.ucode
--type-add=udos:*.udos,*.uds

# Ignore patterns
--glob=!.git/*
--glob=!node_modules/*
--glob=!target/*
--glob=!build/*
--glob=!dist/*
--glob=!*.log
--glob=!*.tmp
RGCONF
    
    log_success "Created ripgrep configuration: ~/.config/ripgrep/config"
fi

# Update package registry
log_info "Updating package registry..."
cat > "$UHOME/uMemory/packages/installed/ripgrep.json" << EOF
{
  "package": "ripgrep",
  "command": "rg",
  "status": "installed",
  "version": "$installed_version",
  "installed_at": "$(date -Iseconds)",
  "installer_version": "2.0.0",
  "config_file": "$UHOME/uMemory/packages/configs/ripgrep.md",
  "integration": {
    "shortcodes": ["search", "find"],
    "wrapper_script": "$SCRIPT_DIR/run-ripgrep.sh",
    "config_path": "~/.config/ripgrep/config"
  }
}
EOF

log_success "Package registry updated"

# Test basic functionality
log_info "Testing ripgrep functionality..."
echo ""
echo -e "${CYAN}📋 Version Information:${NC}"
$COMMAND_NAME --version

echo ""
echo -e "${CYAN}🎯 Integration Test:${NC}"
echo "Testing search functionality..."
if echo "test content for ripgrep" | $COMMAND_NAME "test.*ripgrep" --color=always; then
    log_success "Integration test passed"
else
    log_warning "Integration test failed - basic functionality may be limited"
fi

echo ""
echo -e "${GREEN}🎉 ripgrep installation and integration complete!${NC}"
echo ""
echo -e "${CYAN}📋 Available Commands:${NC}"
echo "  • rg 'search term' - Direct ripgrep usage"
echo "  • ./uCode/packages/run-ripgrep.sh 'term' 'path' - uDOS wrapper"
echo "  • [search:term] - Shortcode integration (requires shortcode processor)"
echo ""
echo -e "${CYAN}📄 Configuration:${NC}"
echo "  • Config file: ~/.config/ripgrep/config"
echo "  • uDOS config: $UHOME/uMemory/packages/configs/ripgrep.md"
echo "  • Usage logs: $UHOME/uMemory/logs/package-usage.log"
echo ""
echo -e "${CYAN}💡 Next Steps:${NC}"
echo "  1. Try: rg --help"
echo "  2. Search uDOS: rg 'shortcode' $UHOME"
echo "  3. Use shortcode: [search:function]"
