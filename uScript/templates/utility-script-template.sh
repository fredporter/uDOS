#!/bin/bash
# {{SCRIPT_NAME}} - {{SCRIPT_DESCRIPTION}}
# Utility script for uDOS system
# Created: {{TIMESTAMP}}
# Author: {{USER}}
# Version: 1.0.0

set -euo pipefail

# Script metadata
SCRIPT_NAME="{{SCRIPT_NAME}}"
SCRIPT_VERSION="1.0.0"
SCRIPT_DESCRIPTION="{{SCRIPT_DESCRIPTION}}"

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Show help
show_help() {
    bold "$SCRIPT_NAME v$SCRIPT_VERSION"
    echo
    echo "$SCRIPT_DESCRIPTION"
    echo
    echo "Usage: $0 [options] [arguments]"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --version  Show version information"
    echo "  -q, --quiet    Quiet mode"
    echo "  -d, --debug    Debug mode"
    echo
    echo "Examples:"
    echo "  $0 --help"
    echo "  $0 argument1 argument2"
    echo
}

# Main utility function
main() {
    local quiet=false
    local debug=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                echo "$SCRIPT_NAME v$SCRIPT_VERSION"
                exit 0
                ;;
            -q|--quiet)
                quiet=true
                shift
                ;;
            -d|--debug)
                debug=true
                set -x
                shift
                ;;
            -*)
                red "❌ Unknown option: $1"
                echo "Use '$0 --help' for usage information"
                exit 1
                ;;
            *)
                # Positional arguments
                break
                ;;
        esac
    done
    
    if [[ "$quiet" == "false" ]]; then
        bold "🔧 $SCRIPT_NAME v$SCRIPT_VERSION"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo
    fi
    
    # Your utility logic here
    cyan "🛠️ Running utility..."
    
    if [[ "$quiet" == "false" ]]; then
        green "✅ Utility completed"
    fi
}

# Execute main function
main "$@"
