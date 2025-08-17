#!/bin/bash
# package-cleanup.sh - Clean up broken installers and implement distribution strategy
# Based on PACKAGE_ANALYSIS.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

show_header() {
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}                 ${YELLOW}📦 Package Distribution Cleanup${NC}                ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}              Implementing PACKAGE_ANALYSIS strategy           ${CYAN}║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

remove_broken_installers() {
    log_info "Removing broken package installers based on analysis..."
    
    # External tools with broken installers - remove and mark as external
    local broken_external=(
        "install-ripgrep.sh"
        "install-bat.sh" 
        "install-fd.sh"
        "install-fzf.sh"
        "install-glow.sh"
        "install-gemini.sh"
        "install-gemini-cli.sh"
    )
    
    for installer in "${broken_external[@]}"; do
        if [[ -f "$SCRIPT_DIR/$installer" ]]; then
            log_warning "Removing broken installer: $installer"
            rm -f "$SCRIPT_DIR/$installer"
        fi
    done
}

create_external_package_info() {
    log_info "Creating installation guide for external packages..."
    
    cat > "$SCRIPT_DIR/EXTERNAL_PACKAGES.md" << 'EOF'
# External Package Installation Guide

These packages are valuable but not bundled with uDOS. Install them manually for enhanced functionality.

## 🚀 Performance Tools (Recommended)

### ripgrep - Fast text search
```bash
# macOS with Homebrew
brew install ripgrep

# Ubuntu/Debian  
sudo apt install ripgrep

# Usage in uDOS
rg "search term" ./uMemory/
```

### bat - Syntax highlighted file viewer
```bash
# macOS with Homebrew
brew install bat

# Ubuntu/Debian
sudo apt install bat

# Usage in uDOS  
bat README.md
bat -n script.sh  # with line numbers
```

### fd - Fast file finder
```bash
# macOS with Homebrew
brew install fd

# Ubuntu/Debian
sudo apt install fd-find

# Usage in uDOS
fd ".md" ./docs/
fd "script" ./uCORE/
```

### fzf - Fuzzy finder
```bash
# macOS with Homebrew
brew install fzf

# Ubuntu/Debian
sudo apt install fzf

# Usage in uDOS
find . -name "*.sh" | fzf
```

## 💡 Enhancement Tools (Optional)

### glow - Terminal markdown renderer
```bash
# macOS with Homebrew  
brew install glow

# Usage in uDOS
glow README.md
glow docs/*.md
```

## 🔧 Installation Tips

1. **macOS**: Install Homebrew first - https://brew.sh
2. **Linux**: Use your distribution's package manager
3. **Windows**: Use Windows Subsystem for Linux (WSL)

## ✅ Verification

After installation, verify with:
```bash
which rg bat fd fzf glow
```

These tools integrate seamlessly with uDOS workflows once installed.
EOF

    log_success "Created EXTERNAL_PACKAGES.md installation guide"
}

update_consolidated_manager() {
    log_info "Updating consolidated manager to reflect new strategy..."
    
    # Update the consolidated manager to remove broken packages
    local packages_to_remove=("ripgrep" "bat" "fd" "fzf" "glow" "gemini")
    
    for package in "${packages_to_remove[@]}"; do
        log_info "Marking $package as external (install manually)"
        
        # Comment out in consolidated manager (we'll leave for reference but mark as external)
        if grep -q "PACKAGE_$package=" "$SCRIPT_DIR/consolidated-manager.sh"; then
            sed -i.bak "s/PACKAGE_$package=/# EXTERNAL: PACKAGE_$package=/" "$SCRIPT_DIR/consolidated-manager.sh"
        fi
    done
}

show_current_status() {
    log_info "Current uDOS Package Status:"
    echo
    echo -e "${GREEN}✅ CORE INTEGRATED PACKAGES (Bundled):${NC}"
    echo "  🌐 urltomarkdown - Web content extraction"
    echo "  🎨 ascii-generator - Visual rendering tools" 
    echo "  📄 jq - JSON processing (system installed)"
    echo
    echo -e "${YELLOW}⚠️  EXTERNAL PACKAGES (Manual install):${NC}"
    echo "  🔍 ripgrep - Fast text search"
    echo "  🦇 bat - Syntax highlighted viewer"  
    echo "  📁 fd - Fast file finder"
    echo "  🔮 fzf - Fuzzy finder"
    echo "  ✨ glow - Markdown renderer"
    echo
    echo -e "${BLUE}📋 See EXTERNAL_PACKAGES.md for installation instructions${NC}"
}

main() {
    show_header
    
    remove_broken_installers
    create_external_package_info
    update_consolidated_manager
    
    echo
    log_success "🎉 Package cleanup completed!"
    echo
    show_current_status
    echo
    log_info "Strategy: Focus on core integrated packages, provide guides for external tools"
}

main "$@"
