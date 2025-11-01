#!/bin/bash

# uDOS Launcher Script v1.0.0
# Enhanced startup with health checks, auto-repair, and user-friendly error handling

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Startup banner
echo -e "${CYAN}╔═══════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  🌀 ${GREEN}uDOS v1.0.0 Startup System${NC}     ${CYAN}║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════╝${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python $PYTHON_VERSION is too old (minimum: 3.8)"
        print_error "Please upgrade Python and try again"
        exit 1
    elif [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -eq 9 ]; then
        print_warning "Python $PYTHON_VERSION is end-of-life (EOL October 2025)"
        print_warning "Consider upgrading to Python 3.10+ for security updates"
        print_success "Python $PYTHON_VERSION (will work with warnings)"
    else
        print_success "Python ${PYTHON_VERSION} found"
    fi
else
    print_error "Python 3 not found!"
    print_error "Install Python 3.8+ and try again"
    exit 1
fi

# Check/Create virtual environment
print_status "Checking virtual environment..."
if [ ! -d ".venv" ]; then
    print_warning "Virtual environment not found. Creating..."
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment found"
fi

# Activate the virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate
print_success "Virtual environment activated"

# Explicitly check and install dependencies if needed
print_status "Checking Python dependencies..."
MISSING_DEPS=0
MISSING_LIST=""
for package in "google-generativeai" "python-dotenv" "prompt_toolkit" "requests" "psutil"; do
    # Convert package name to module name for import check
    if [[ "$package" == "google-generativeai" ]]; then
        module_name="google.generativeai"
    elif [[ "$package" == "python-dotenv" ]]; then
        module_name="dotenv"
    elif [[ "$package" == "prompt_toolkit" ]]; then
        module_name="prompt_toolkit"
    else
        module_name="$package"
    fi

    if ! python3 -c "import $module_name" 2>/dev/null; then
        MISSING_DEPS=1
        if [ -z "$MISSING_LIST" ]; then
            MISSING_LIST="$package"
        else
            MISSING_LIST="$MISSING_LIST, $package"
        fi
    fi
done

if [ $MISSING_DEPS -eq 1 ]; then
    print_warning "Missing packages: $MISSING_LIST"
    print_status "Installing missing dependencies..."
    if [ -f "requirements.txt" ]; then
        python3 -m pip install -q -r requirements.txt 2>&1 | grep -v "WARNING: You are using pip" | grep -v "You should consider upgrading" || true
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
    fi
else
    print_success "All dependencies satisfied"
fi

# Check for pip upgrades (non-blocking)
if python3 -m pip list --outdated 2>/dev/null | grep -q "^pip "; then
    print_warning "Pip upgrade available (non-critical)"
    echo -e "  ${BLUE}└─${NC} Run: ${CYAN}python3 -m pip install --upgrade pip${NC}"
fi

# Check/Install web extensions
print_status "Checking web extensions..."

# Function to check and install extension with better feedback
check_extension() {
    local ext_name=$1
    local setup_script=$2

    if [ -f "extensions/${setup_script}" ]; then
        # Check if extension is installed (look for specific files/dirs)
        case $ext_name in
            "typo")
                if [ ! -d "extensions/clone/typo" ]; then
                    print_warning "${ext_name} not installed. Installing..."
                    UDOS_AUTO_INSTALL=1 bash "extensions/${setup_script}" 2>&1 | grep -E "(Cloning|Installing|Installed)" || true
                    if [ -d "extensions/clone/typo" ]; then
                        print_success "${ext_name} installed"
                    else
                        print_warning "${ext_name} installation may have failed"
                    fi
                else
                    print_success "${ext_name} ready"
                fi
                ;;
            "micro")
                if [ ! -f "extensions/clone/native/micro/micro" ]; then
                    print_warning "${ext_name} not installed. Installing..."
                    UDOS_AUTO_INSTALL=1 bash "extensions/${setup_script}" 2>&1 | grep -E "(Downloading|Installing|Installed)" || true
                    if [ -f "extensions/clone/native/micro/micro" ]; then
                        print_success "${ext_name} installed"
                    else
                        print_warning "${ext_name} installation may have failed"
                    fi
                else
                    print_success "${ext_name} ready"
                fi
                ;;
            "monaspace")
                if [ ! -d "extensions/clone/monaspace-fonts" ]; then
                    print_warning "${ext_name} fonts not installed. Installing..."
                    UDOS_AUTO_INSTALL=1 bash "extensions/${setup_script}" 2>&1 | grep -E "(Cloning|Installing|Installed)" || true
                    if [ -d "extensions/clone/monaspace-fonts" ]; then
                        print_success "${ext_name} fonts installed"
                    else
                        print_warning "${ext_name} fonts installation may have failed"
                    fi
                else
                    print_success "${ext_name} fonts ready"
                fi
                ;;
        esac
    else
        print_warning "${setup_script} not found - skipping ${ext_name}"
    fi
}

# Check core extensions
check_extension "typo" "setup_typo.sh"
check_extension "micro" "setup_micro.sh"
check_extension "monaspace" "setup_monaspace.sh"

# Check data directories
print_status "Checking data directories..."
for dir in data memory/logs memory/logs/sessions memory/logs/servers output sandbox; do
    if [ ! -d "$dir" ]; then
        print_warning "Creating directory: $dir"
        mkdir -p "$dir"
    fi
done
print_success "Data directories verified"

# Check critical data files
print_status "Checking critical data files..."
DATA_FILES_OK=1
for file in "system/commands.json" "themes/dungeon.json" "themes/_index.json" "templates/story.template.json"; do
    if [ ! -f "data/$file" ]; then
        print_warning "data/$file not found"
        DATA_FILES_OK=0
    fi
done

if [ $DATA_FILES_OK -eq 1 ]; then
    print_success "All critical data files present"
else
    print_warning "Some data files missing - will be created on first run"
fi

# Validate JSON in critical files
print_status "Validating configuration files..."
JSON_OK=1
for file in "system/commands.json" "system/palette.json" "themes/dungeon.json" "themes/_index.json"; do
    if [ -f "data/$file" ]; then
        if ! python3 -c "import json; json.load(open('data/$file'))" 2>/dev/null; then
            print_error "data/$file has invalid JSON"
            JSON_OK=0
        fi
    fi
done

if [ $JSON_OK -eq 1 ]; then
    print_success "Configuration files validated"
else
    print_error "Configuration validation failed - run 'python3 -m core.uDOS_health' for details"
fi

# Display startup summary
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}✓ System Check Complete${NC}            ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ${MAGENTA}🤖 AI Mode Ready${NC}                  ${CYAN}║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Quick Tips:${NC}"
echo -e "  • Type ${CYAN}HELP${NC} for command reference"
echo -e "  • Type ${CYAN}ASK \"question\"${NC} for AI assistance"
echo -e "  • Type ${CYAN}CONFIG list${NC} to view settings"
echo -e "  • Type ${CYAN}DASH WEB${NC} to open dashboard"
echo ""

# Run the main application with any provided arguments
print_status "Starting uDOS..."
python uDOS.py "$@"

# Deactivate the virtual environment on exit
deactivate
