#!/bin/bash

# uCode/packages/download-assets.sh
# Download optional assets for uDOS extensions that were excluded from repository

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "\n${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                          uDOS Asset Downloader                              ║${NC}"
    echo -e "${CYAN}║                    Download Optional Extension Assets                        ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Download ASCII Generator assets
download_ascii_assets() {
    echo -e "${CYAN}[ASCII GENERATOR]${NC} Downloading demo assets, fonts, and data files..."
    
    local ascii_dir="$(dirname "$0")/ascii-generator"
    
    if [[ -d "$ascii_dir" ]]; then
        cd "$ascii_dir"
        
        # Create temporary download directory
        mkdir -p temp-download
        cd temp-download
        
        print_info "Cloning ASCII Generator repository for assets..."
        git clone https://github.com/vietnh1009/ASCII-generator.git . --quiet
        
        # Copy assets to parent directory
        print_info "Copying demo files (~500MB)..."
        cp -r demo ../
        
        print_info "Copying font files (~38MB)..."
        cp -r fonts ../
        
        print_info "Copying data files (~25MB)..."
        cp -r data ../
        
        # Clean up
        cd ..
        rm -rf temp-download
        
        print_success "ASCII Generator assets downloaded (~563MB total)"
        print_info "Assets location: $ascii_dir/"
    else
        print_warning "ASCII Generator not found at $ascii_dir"
    fi
}

# Download VS Code extension dependencies
download_vscode_deps() {
    echo -e "${CYAN}[VS CODE EXTENSION]${NC} Installing Node.js dependencies..."
    
    local vscode_dir="$(dirname "$0")/../uExtensions/development/vscode-extension"
    
    if [[ -d "$vscode_dir" ]] && [[ -f "$vscode_dir/package.json" ]]; then
        cd "$vscode_dir"
        
        if command -v npm >/dev/null 2>&1; then
            print_info "Installing node_modules..."
            npm install --silent
            print_success "VS Code extension dependencies installed"
        else
            print_warning "npm not found - please install Node.js first"
        fi
    else
        print_warning "VS Code extension not found"
    fi
}

# Show download summary
show_summary() {
    echo -e "\n${CYAN}Download Summary:${NC}"
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│ These assets were excluded from the git repository to keep it lightweight:  │"
    echo "│                                                                             │"
    echo "│ 📁 ASCII Generator Assets (~563MB):                                        │"
    echo "│   • demo/ - Sample images and generated ASCII art examples                 │"
    echo "│   • fonts/ - TrueType fonts for enhanced output                           │"
    echo "│   • data/ - Input media files for testing                                 │"
    echo "│                                                                             │"
    echo "│ 📦 VS Code Extension Dependencies (~164MB):                                │"
    echo "│   • node_modules/ - TypeScript compilation and extension dependencies      │"
    echo "│                                                                             │"
    echo "│ These are optional - extensions work without them!                         │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
}

# Main function
main() {
    print_header
    show_summary
    
    echo -e "\n${YELLOW}What would you like to download?${NC}"
    echo "1) ASCII Generator assets (~563MB)"
    echo "2) VS Code extension dependencies (~164MB)" 
    echo "3) Both"
    echo "4) Skip (exit)"
    
    read -p "Choice [1-4]: " choice
    
    case $choice in
        1)
            download_ascii_assets
            ;;
        2)
            download_vscode_deps
            ;;
        3)
            download_ascii_assets
            download_vscode_deps
            ;;
        4)
            print_info "Skipping asset download"
            exit 0
            ;;
        *)
            print_warning "Invalid choice"
            exit 1
            ;;
    esac
    
    echo -e "\n${GREEN}✨ Asset download complete!${NC}"
    print_info "The repository remains lightweight while providing full functionality"
}

# Show usage if called with --help
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    print_header
    echo "Usage: $0 [--ascii|--vscode|--all|--help]"
    echo ""
    echo "Options:"
    echo "  --ascii    Download ASCII generator assets only"
    echo "  --vscode   Download VS Code extension dependencies only"
    echo "  --all      Download everything"
    echo "  --help     Show this help"
    echo ""
    echo "Interactive mode will run if no options provided."
    exit 0
elif [[ "${1:-}" == "--ascii" ]]; then
    download_ascii_assets
elif [[ "${1:-}" == "--vscode" ]]; then
    download_vscode_deps
elif [[ "${1:-}" == "--all" ]]; then
    download_ascii_assets
    download_vscode_deps
else
    main
fi
