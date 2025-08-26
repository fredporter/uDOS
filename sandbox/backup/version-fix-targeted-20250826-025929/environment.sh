#!/bin/bash
# Environment Detection and Setup

# Detect system capabilities
detect_environment() {
    # Platform detection
    case "$(uname -s)" in
        Darwin) export UDOS_PLATFORM="macos" ;;
        Linux)  export UDOS_PLATFORM="linux" ;;
        CYGWIN*|MINGW*) export UDOS_PLATFORM="windows" ;;
        *) export UDOS_PLATFORM="unknown" ;;
    esac
    
    # Architecture detection
    export UDOS_ARCH="$(uname -m)"
    
    # Bash version compatibility
    local bash_version="${BASH_VERSION%%.*}"
    if [[ "$bash_version" -lt 4 ]]; then
        export UDOS_COMPAT_MODE="bash3"
        log_warning "Bash 3.x detected - using compatibility mode"
    else
        export UDOS_COMPAT_MODE="modern"
    fi
    
    # Python availability
    if command -v python3 >/dev/null 2>&1; then
        export UDOS_PYTHON_AVAILABLE="true"
        export UDOS_PYTHON_VERSION="$(python3 --version 2>&1 | cut -d' ' -f2)"
    else
        export UDOS_PYTHON_AVAILABLE="false"
        log_warning "Python 3 not available - some features will be limited"
    fi
    
    log_info "Environment: $UDOS_PLATFORM/$UDOS_ARCH, Bash: $UDOS_COMPAT_MODE, Python: $UDOS_PYTHON_AVAILABLE"
}

# Setup environment variables
setup_environment() {
    # Core paths
    export UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    export UCORE="$UDOS_ROOT/uCORE"
    export USCRIPT="$UDOS_ROOT/uSCRIPT"
    export UMEMORY="$UDOS_ROOT/uMEMORY"
    
    # Version
    export UDOS_VERSION="v1.3.1"
    
    # Mode
    export UDOS_MODE="${UDOS_MODE:-COMMAND}"
    
    # Detect environment
    detect_environment
}
