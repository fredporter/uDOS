#!/bin/bash
# install-urltomarkdown.sh - uDOS URL to Markdown Converter Installation
# Integrates urltomarkdown for web content extraction in uDOS

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGES_DIR="$SCRIPT_DIR"
URLTOMD_DIR="$PACKAGES_DIR/urltomarkdown"
UHOME="${HOME}/uDOS"
UCORE_BIN="$UHOME/uCORE/bin"

# Helper functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

show_header() {
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}             ${CYAN}🌐 uDOS URL to Markdown Integration${NC}              ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                  Web Content Extraction Tool                 ${BLUE}║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 >/dev/null 2>&1; then
        if ! command -v python >/dev/null 2>&1; then
            log_error "Python is required but not installed"
            log_info "Please install Python from https://python.org/"
            return 1
        else
            PYTHON_CMD="python"
        fi
    else
        PYTHON_CMD="python3"
    fi
    
    # Check pip
    if ! command -v pip3 >/dev/null 2>&1; then
        if ! command -v pip >/dev/null 2>&1; then
            log_error "pip is required but not installed"
            log_info "Please install pip: https://pip.pypa.io/en/stable/installation/"
            return 1
        else
            PIP_CMD="pip"
        fi
    else
        PIP_CMD="pip3"
    fi
    
    # Check git
    if ! command -v git >/dev/null 2>&1; then
        log_error "git is required but not installed"
        return 1
    fi
    
    log_success "All dependencies available"
    return 0
}

install_urltomarkdown() {
    log_info "Installing urltomarkdown..."
    
    # Create directories
    mkdir -p "$UCORE_BIN"
    
    # Clone or update repository
    if [[ -d "$URLTOMD_DIR" ]]; then
        log_info "Updating existing urltomarkdown repository..."
        cd "$URLTOMD_DIR"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || {
            log_warning "Could not update repository, using existing version"
        }
    else
        log_info "Cloning urltomarkdown repository..."
        cd "$PACKAGES_DIR"
        git clone https://github.com/macsplit/urltomarkdown.git || {
            log_error "Failed to clone urltomarkdown repository"
            return 1
        }
    fi
    
    cd "$URLTOMD_DIR"
    
    # Install Python dependencies
    if [[ -f "requirements.txt" ]]; then
        log_info "Installing Python dependencies..."
        $PIP_CMD install -r requirements.txt --user || {
            log_error "Failed to install Python dependencies"
            return 1
        }
    else
        log_warning "No requirements.txt found, installing common dependencies..."
        $PIP_CMD install --user requests beautifulsoup4 lxml html2text || {
            log_warning "Some dependencies may be missing"
        }
    fi
    
    log_success "urltomarkdown installed successfully"
    return 0
}

create_ucode_integration() {
    log_info "Creating uDOS integration scripts..."
    
    # Create uDOS wrapper script
    cat > "$UCORE_BIN/udos-url2md" << 'EOF'
#!/bin/bash
# udos-url2md - uDOS URL to Markdown Converter
# Wrapper for urltomarkdown with uDOS integration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
URLTOMD_DIR="$(dirname "$SCRIPT_DIR")/code/packages/urltomarkdown"
UHOME="${HOME}/uDOS"
OUTPUT_DIR="$UHOME/uMEMORY/datagets/active"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_help() {
    echo -e "${CYAN}🌐 uDOS URL to Markdown Converter${NC}"
    echo
    echo "Usage: udos-url2md [OPTIONS] <URL>"
    echo
    echo "Options:"
    echo "  -o, --output FILE    Save to specific file"
    echo "  -d, --dir DIR        Save to specific directory"
    echo "  -t, --title TITLE    Custom title for file"
    echo "  -h, --help           Show this help"
    echo
    echo "Examples:"
    echo "  udos-url2md https://example.com"
    echo "  udos-url2md -o article.md https://blog.example.com/post"
    echo "  udos-url2md -t \"My Article\" https://news.example.com"
}

# Default values
URL=""
OUTPUT_FILE=""
OUTPUT_DIR_CUSTOM=""
CUSTOM_TITLE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -d|--dir)
            OUTPUT_DIR_CUSTOM="$2"
            shift 2
            ;;
        -t|--title)
            CUSTOM_TITLE="$2"
            shift 2
            ;;
        -*)
            echo -e "${RED}❌ Unknown option: $1${NC}" >&2
            exit 1
            ;;
        *)
            URL="$1"
            shift
            ;;
    esac
done

# Validate URL
if [[ -z "$URL" ]]; then
    echo -e "${RED}❌ URL is required${NC}" >&2
    show_help
    exit 1
fi

# Ensure urltomarkdown is available
if [[ ! -f "$URLTOMD_DIR/urltomarkdown.py" ]]; then
    echo -e "${RED}❌ urltomarkdown not found. Please run: udos-install-packages urltomarkdown${NC}" >&2
    exit 1
fi

# Determine Python command
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found${NC}" >&2
    exit 1
fi

# Generate filename if not provided
if [[ -z "$OUTPUT_FILE" ]]; then
    if [[ -n "$CUSTOM_TITLE" ]]; then
        FILENAME=$(echo "$CUSTOM_TITLE" | sed 's/[^a-zA-Z0-9]/_/g').md
    else
        FILENAME=$(echo "$URL" | sed 's|https\?://||' | sed 's/[^a-zA-Z0-9]/_/g').md
    fi
    
    # Use custom directory or default
    if [[ -n "$OUTPUT_DIR_CUSTOM" ]]; then
        mkdir -p "$OUTPUT_DIR_CUSTOM"
        OUTPUT_FILE="$OUTPUT_DIR_CUSTOM/$FILENAME"
    else
        mkdir -p "$OUTPUT_DIR"
        OUTPUT_FILE="$OUTPUT_DIR/$FILENAME"
    fi
fi

# Convert URL to Markdown
echo -e "${CYAN}🌐 Converting URL to Markdown...${NC}"
echo -e "   URL: $URL"
echo -e "   Output: $OUTPUT_FILE"

cd "$URLTOMD_DIR"
if $PYTHON_CMD urltomarkdown.py "$URL" > "$OUTPUT_FILE" 2>/dev/null; then
    echo -e "${GREEN}✅ Successfully converted and saved to: $OUTPUT_FILE${NC}"
    
    # Add metadata header
    temp_file=$(mktemp)
    {
        echo "---"
        echo "source: $URL"
        echo "converted: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
        echo "tool: uDOS urltomarkdown"
        [[ -n "$CUSTOM_TITLE" ]] && echo "title: $CUSTOM_TITLE"
        echo "---"
        echo
        cat "$OUTPUT_FILE"
    } > "$temp_file"
    mv "$temp_file" "$OUTPUT_FILE"
    
    echo -e "${YELLOW}📝 Added metadata header${NC}"
else
    echo -e "${RED}❌ Failed to convert URL${NC}" >&2
    exit 1
fi
EOF

    chmod +x "$UCORE_BIN/udos-url2md"
    
    # Create batch processing script
    cat > "$UCORE_BIN/udos-url2md-batch" << 'EOF'
#!/bin/bash
# udos-url2md-batch - Batch URL to Markdown conversion

set -euo pipefail

UHOME="${HOME}/uDOS"
INPUT_FILE="$1"
OUTPUT_DIR="${2:-$UHOME/uMEMORY/datagets/active/batch_$(date +%Y%m%d_%H%M%S)}"

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "❌ Input file not found: $INPUT_FILE" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
echo "🔄 Processing URLs from: $INPUT_FILE"
echo "📁 Output directory: $OUTPUT_DIR"

count=0
while IFS= read -r url || [[ -n "$url" ]]; do
    [[ -z "$url" || "$url" =~ ^# ]] && continue
    
    ((count++))
    echo "[$count] Processing: $url"
    
    if udos-url2md -d "$OUTPUT_DIR" "$url"; then
        echo "  ✅ Success"
    else
        echo "  ❌ Failed"
    fi
    
    sleep 1  # Be respectful to servers
done < "$INPUT_FILE"

echo "✅ Batch processing completed: $count URLs processed"
echo "📁 Files saved to: $OUTPUT_DIR"
EOF

    chmod +x "$UCORE_BIN/udos-url2md-batch"
    
    log_success "uDOS integration scripts created"
}

update_package_manager() {
    log_info "Updating package manager..."
    
    # Add urltomarkdown to consolidated manager
    if [[ -f "$PACKAGES_DIR/consolidated-manager.sh" ]]; then
        if ! grep -q "urltomarkdown" "$PACKAGES_DIR/consolidated-manager.sh"; then
            log_info "Adding urltomarkdown to package manager..."
            # This would require more complex sed operations, for now just log
            log_warning "Manual addition to consolidated-manager.sh required"
        fi
    fi
    
    log_success "Package manager integration completed"
}

main() {
    show_header
    
    if ! check_dependencies; then
        exit 1
    fi
    
    if ! install_urltomarkdown; then
        exit 1
    fi
    
    create_ucode_integration
    update_package_manager
    
    echo
    log_success "🎉 urltomarkdown integration completed!"
    echo
    echo -e "${CYAN}Usage Examples:${NC}"
    echo -e "  ${YELLOW}udos-url2md https://example.com${NC}"
    echo -e "  ${YELLOW}udos-url2md -t \"My Article\" https://blog.example.com${NC}"
    echo -e "  ${YELLOW}udos-url2md-batch urls.txt${NC}"
    echo
}

# Run main function
main "$@"
