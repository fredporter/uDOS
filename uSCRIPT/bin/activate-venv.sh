#!/bin/bash
# Virtual Environment Activation Manager

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Get script directory and set paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USCRIPT="$(cd "$SCRIPT_DIR/.." && pwd)"

activate_venv() {
    local language="${1:-python}"
    local venv_path="$USCRIPT/venv/$language"
    
    case "$language" in
        python)
            if [[ ! -d "$venv_path" ]]; then
                log_info "Creating Python virtual environment..."
                python3 -m venv "$venv_path"
                source "$venv_path/bin/activate"
                pip install --upgrade pip
                pip install -r "$USCRIPT/config/requirements.txt"
                log_success "Python virtual environment created"
            else
                source "$venv_path/bin/activate"
                log_info "Python virtual environment activated"
            fi
            ;;
        *)
            log_warning "No virtual environment configuration for: $language"
            ;;
    esac
}

# Main execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    activate_venv "$@"
fi
