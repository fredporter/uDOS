#!/bin/bash
# Edit command handler for micro editor
# Usage: [EDIT] <filename>

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
EXTENSION_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source logging functions (uCORE native bash)
log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# Check if micro is installed (native system approach)
check_micro_installation() {
    # Use system micro if available (brew/system package)
    if command -v micro >/dev/null 2>&1; then
        MICRO_BIN="micro"
        return 0
    else
        log_error "Micro editor not found. Please install via:"
        echo "  macOS: brew install micro"
        echo "  Linux: curl https://getmic.ro | bash"
        echo "  Manual: https://github.com/zyedidia/micro/releases"
        exit 1
    fi
}

# Resolve file path
resolve_file_path() {
    local filename="$1"
    local resolved_path
    
    # Check if absolute path
    if [[ "$filename" = /* ]]; then
        resolved_path="$filename"
    else
        # Check common locations
        if [[ -f "$PWD/$filename" ]]; then
            resolved_path="$PWD/$filename"
        elif [[ -f "$UDOS_ROOT/sandbox/documents/$filename" ]]; then
            resolved_path="$UDOS_ROOT/sandbox/documents/$filename"
        elif [[ -f "$UDOS_ROOT/uMEMORY/user/$filename" ]]; then
            resolved_path="$UDOS_ROOT/uMEMORY/user/$filename"
        elif [[ -f "$UDOS_ROOT/docs/$filename" ]]; then
            resolved_path="$UDOS_ROOT/docs/$filename"
        else
            # Create in sandbox/documents if doesn't exist
            resolved_path="$UDOS_ROOT/sandbox/documents/$filename"
            mkdir -p "$(dirname "$resolved_path")"
        fi
    fi
    
    echo "$resolved_path"
}

# Main edit function
edit_file() {
    local filename="${1:-}"
    
    if [[ -z "$filename" ]]; then
        log_error "Usage: [EDIT] <filename>"
        echo "Example: [EDIT] README.md"
        exit 1
    fi
    
    check_micro_installation
    
    local file_path
    file_path=$(resolve_file_path "$filename")
    
    log_info "Opening file: $file_path"
    
    # Launch micro editor (native system tool)
    if [[ -t 0 && -t 1 ]]; then
        # Interactive terminal
        micro "$file_path"
        log_success "File edited: $file_path"
    else
        # Non-interactive mode
        log_warning "Non-interactive terminal detected. Use [EDIT|BROWSER] for web-based editing."
        exit 1
    fi
}

# ASCII block output for uCORE command mode
show_status() {
    cat << 'EOF'
╔══════════════════════════════════════╗
║            📝 MICRO EDITOR           ║
║        Terminal Text Editor          ║
╠══════════════════════════════════════╣
║ Commands:                            ║
║ [EDIT] <file>     - Edit file        ║
║ [EDIT|NEW] <file> - Create new file  ║
║ [EDIT|BROWSER]    - Web editor       ║
║ [EDIT|CONFIG]     - Configure        ║
╚══════════════════════════════════════╝
EOF
}

# Handle different argument patterns
case "${1:-help}" in
    --status)
        show_status
        ;;
    --help|help)
        show_status
        echo
        echo "Usage: [EDIT] <filename>"
        echo "Opens the specified file in micro editor"
        ;;
    *)
        edit_file "$1"
        ;;
esac
