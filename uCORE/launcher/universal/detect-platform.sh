#!/bin/bash
# Universal Platform Detection for uDOS
# Detects the current platform and sets appropriate variables

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect platform
detect_platform() {
    case "$(uname -s)" in
        Darwin*)
            PLATFORM="macos"
            PLATFORM_NAME="macOS"
            ;;
        MINGW*|CYGWIN*|MSYS*)
            PLATFORM="windows"
            PLATFORM_NAME="Windows"
            ;;
        Linux*)
            PLATFORM="linux"
            PLATFORM_NAME="Linux"
            ;;
        *)
            PLATFORM="unknown"
            PLATFORM_NAME="Unknown"
            ;;
    esac
}

# Detect VS Code installation
detect_vscode() {
    VSCODE_AVAILABLE=false
    
    case "$PLATFORM" in
        macos)
            if command -v code >/dev/null 2>&1 || [ -d "/Applications/Visual Studio Code.app" ]; then
                VSCODE_AVAILABLE=true
            fi
            ;;
        windows)
            if command -v code >/dev/null 2>&1; then
                VSCODE_AVAILABLE=true
            fi
            ;;
        linux)
            if command -v code >/dev/null 2>&1; then
                VSCODE_AVAILABLE=true
            fi
            ;;
    esac
}

# Detect terminal capabilities
detect_terminal() {
    TERMINAL_AVAILABLE=true
    TERMINAL_TYPE="basic"
    
    if [ -n "$TERM" ]; then
        case "$TERM" in
            *color*|*256*|xterm-*)
                TERMINAL_TYPE="enhanced"
                ;;
        esac
    fi
}

# Get uDOS root directory
get_udos_root() {
    # Try to find uDOS directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Navigate up from launcher/universal to find uDOS root
    if [[ "$SCRIPT_DIR" == */uCORE/launcher/universal ]]; then
        UDOS_ROOT="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"
    elif [[ "$SCRIPT_DIR" == */uCORE/launcher ]]; then
        UDOS_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
    else
        # Fallback: look for uCORE directory
        current_dir="$SCRIPT_DIR"
        while [ "$current_dir" != "/" ]; do
            if [ -d "$current_dir/uCORE" ]; then
                UDOS_ROOT="$current_dir"
                break
            fi
            current_dir="$(dirname "$current_dir")"
        done
    fi
    
    # Final fallback
    if [ -z "$UDOS_ROOT" ] || [ ! -d "$UDOS_ROOT/uCORE" ]; then
        UDOS_ROOT="$HOME/uDOS"
    fi
}

# Print detection results
print_detection_results() {
    echo -e "${BLUE}🔍 Platform Detection Results${NC}"
    echo -e "Platform: ${GREEN}$PLATFORM_NAME${NC} ($PLATFORM)"
    echo -e "uDOS Root: ${GREEN}$UDOS_ROOT${NC}"
    echo -e "VS Code: $([ "$VSCODE_AVAILABLE" = true ] && echo -e "${GREEN}Available${NC}" || echo -e "${YELLOW}Not Found${NC}")"
    echo -e "Terminal: ${GREEN}$TERMINAL_TYPE${NC}"
    echo ""
}

# Main detection function
run_detection() {
    detect_platform
    get_udos_root
    detect_vscode
    detect_terminal
    
    if [ "$1" = "--verbose" ] || [ "$1" = "-v" ]; then
        print_detection_results
    fi
}

# Export functions and variables for sourcing
export -f detect_platform detect_vscode detect_terminal get_udos_root print_detection_results run_detection

# Run detection if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    run_detection "$@"
fi
