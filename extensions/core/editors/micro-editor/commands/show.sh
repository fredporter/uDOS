#!/bin/bash
# Show command handler for markdown viewing
# Usage: [SHOW] <filename.md>

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"

# Source logging functions (uCORE native bash)
log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# Check if server is running
check_server() {
    if curl -s "http://localhost:8080/api/system/status" >/dev/null 2>&1; then
        return 0
    else
        return 1
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
            return 1
        fi
    fi

    echo "$resolved_path"
}

# Show markdown file in browser
show_markdown() {
    local filename="${1:-}"

    if [[ -z "$filename" ]]; then
        log_error "Usage: [SHOW] <filename.md>"
        echo "Example: [SHOW] README.md"
        exit 1
    fi

    local file_path
    if ! file_path=$(resolve_file_path "$filename"); then
        log_error "File not found: $filename"
        echo "Searched in:"
        echo "  - Current directory: $PWD"
        echo "  - Documents: $UDOS_ROOT/sandbox/documents"
        echo "  - User memory: $UDOS_ROOT/uMEMORY/user"
        echo "  - Documentation: $UDOS_ROOT/docs"
        exit 1
    fi

    # Check if it's a markdown file
    case "$filename" in
        *.md|*.markdown)
            ;;
        *)
            log_warning "File doesn't appear to be markdown: $filename"
            ;;
    esac

    log_info "Showing markdown file: $file_path"

    # Check if server is running
    if ! check_server; then
        log_warning "uDOS server not running. Starting server..."
        if [[ -f "$UDOS_ROOT/uNETWORK/server/launch-with-venv.sh" ]]; then
            "$UDOS_ROOT/uNETWORK/server/launch-with-venv.sh" &
            sleep 3

            if ! check_server; then
                log_error "Failed to start uDOS server"
                exit 1
            fi
        else
            log_error "Server launch script not found"
            exit 1
        fi
    fi

    # URL encode the file path
    local encoded_path
    encoded_path=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$file_path'))" 2>/dev/null || echo "$file_path")

    # Open browser to markdown viewer
    local viewer_url="http://localhost:8080#markdown?file=$encoded_path"

    # Platform-specific browser opening
    case "$(uname -s)" in
        Darwin*)
            open "$viewer_url"
            ;;
        Linux*)
            if command -v xdg-open >/dev/null 2>&1; then
                xdg-open "$viewer_url"
            elif command -v firefox >/dev/null 2>&1; then
                firefox "$viewer_url" &
            elif command -v chromium >/dev/null 2>&1; then
                chromium "$viewer_url" &
            else
                log_warning "No suitable browser found. Please open: $viewer_url"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            start "$viewer_url"
            ;;
        *)
            log_warning "Unknown platform. Please open: $viewer_url"
            ;;
    esac

    log_success "Markdown viewer opened: $viewer_url"
}

# ASCII block output for uCORE command mode
show_status() {
    cat << 'EOF'
╔══════════════════════════════════════╗
║         📖 MARKDOWN VIEWER           ║
║      Browser-Based MD Display        ║
╠══════════════════════════════════════╣
║ Commands:                            ║
║ [SHOW] <file.md>  - View markdown    ║
║ [SHOW|LIST]       - List MD files    ║
║ [SHOW|DOCS]       - Show docs folder ║
║ [SHOW|HELP]       - Show this help   ║
╚══════════════════════════════════════╝
EOF
}

# List markdown files
list_markdown_files() {
    echo "📁 Available Markdown Files:"
    echo

    # Check common locations
    local locations=(
        "$PWD:Current Directory"
        "$UDOS_ROOT/sandbox/documents:Documents"
        "$UDOS_ROOT/uMEMORY/user:User Memory"
        "$UDOS_ROOT/docs:Documentation"
    )

    for location in "${locations[@]}"; do
        local path="${location%:*}"
        local name="${location#*:}"

        if [[ -d "$path" ]]; then
            local md_files
            md_files=$(find "$path" -maxdepth 2 -name "*.md" -o -name "*.markdown" 2>/dev/null | head -10)

            if [[ -n "$md_files" ]]; then
                echo "📂 $name:"
                echo "$md_files" | while read -r file; do
                    local basename_file
                    basename_file=$(basename "$file")
                    local relative_path
                    relative_path=${file#$UDOS_ROOT/}
                    echo "  📄 $basename_file ($relative_path)"
                done
                echo
            fi
        fi
    done
}

# Handle different argument patterns
case "${1:-help}" in
    --status)
        show_status
        ;;
    --help|help)
        show_status
        echo
        echo "Usage: [SHOW] <filename.md>"
        echo "Opens markdown files in browser-based viewer with syntax highlighting"
        ;;
    list|LIST)
        list_markdown_files
        ;;
    docs|DOCS)
        show_markdown "README.md" 2>/dev/null || {
            log_info "Opening documentation folder..."
            ls -la "$UDOS_ROOT/docs/"
        }
        ;;
    *)
        show_markdown "$1"
        ;;
esac
