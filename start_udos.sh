#!/bin/bash

# uDOS Launcher Script v1.1.6
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
echo -e "${CYAN}║${NC}  🌀 ${GREEN}uDOS v1.1.6 Startup${NC}            ${CYAN}║${NC}"
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

# If venv exists, check its Python version instead of system Python
if [ -d ".venv" ]; then
    VENV_PYTHON_VERSION=$(.venv/bin/python3 --version 2>&1 | cut -d' ' -f2)
    VENV_PYTHON_MAJOR=$(echo $VENV_PYTHON_VERSION | cut -d'.' -f1)
    VENV_PYTHON_MINOR=$(echo $VENV_PYTHON_VERSION | cut -d'.' -f2)

    if [ "$VENV_PYTHON_MAJOR" -eq 3 ] && [ "$VENV_PYTHON_MINOR" -ge 12 ]; then
        print_success "Python ${VENV_PYTHON_VERSION} (from virtual environment)"
        PYTHON_VERSION=$VENV_PYTHON_VERSION
        PYTHON_MAJOR=$VENV_PYTHON_MAJOR
        PYTHON_MINOR=$VENV_PYTHON_MINOR
        SKIP_PYTHON_CHECK=true
    fi
fi

if [ "$SKIP_PYTHON_CHECK" != "true" ] && command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python $PYTHON_VERSION is too old (minimum: 3.8)"
        print_error "Please upgrade Python and try again"
        exit 1
    elif [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -eq 9 ]; then
        print_warning "Python $PYTHON_VERSION is end-of-life (EOL October 2025)"
        print_warning "Security updates are no longer available for this version"
        echo ""
        echo -e "${YELLOW}Would you like to upgrade Python now?${NC}"
        echo -e "  ${CYAN}1)${NC} Yes - Auto-install Python 3.12 (Homebrew required)"
        echo -e "  ${CYAN}2)${NC} Show manual upgrade instructions"
        echo -e "  ${CYAN}3)${NC} Continue with Python 3.9.6 (not recommended)"
        echo -e "  ${CYAN}4)${NC} Remind me later"
        read -p "> " choice

        case $choice in
            1)
                # Auto-install using Homebrew
                echo ""
                if command -v brew &> /dev/null; then
                    print_status "Homebrew detected - installing Python 3.12..."
                    echo ""

                    if brew install python@3.12; then
                        print_success "Python 3.12 installed successfully!"

                        # Add Python 3.12 to shell PATH permanently
                        print_status "Updating shell configuration..."
                        PYTHON_PATH='export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"'

                        # Add to .zshrc if not already present
                        if ! grep -q "python@3.12" ~/.zshrc 2>/dev/null; then
                            echo "" >> ~/.zshrc
                            echo "# Python 3.12 from Homebrew (added by uDOS)" >> ~/.zshrc
                            echo "$PYTHON_PATH" >> ~/.zshrc
                            print_success "Added Python 3.12 to ~/.zshrc"
                        fi

                        # Link the new Python
                        print_status "Linking Python 3.12..."
                        brew link python@3.12 --overwrite --force

                        # Use explicit path for new Python
                        PYTHON_BIN="/opt/homebrew/bin/python3.12"

                        # Verify new version
                        NEW_VERSION=$($PYTHON_BIN --version 2>&1 | cut -d' ' -f2)
                        print_success "Python available at version $NEW_VERSION"

                        # Recreate virtual environment with Python 3.12
                        echo ""
                        print_status "Recreating virtual environment with Python 3.12..."
                        rm -rf .venv
                        $PYTHON_BIN -m venv .venv
                        source .venv/bin/activate

                        print_status "Installing dependencies..."
                        pip install --upgrade pip -q
                        pip install -r requirements.txt -q

                        print_success "Setup complete! Python upgraded successfully."
                        echo ""
                        echo -e "${GREEN}✓ Ready to continue startup${NC}"
                        echo -e "${CYAN}💡 Restart your terminal for PATH changes to take effect${NC}"
                        echo ""

                        # Update PYTHON_VERSION to reflect the upgrade
                        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
                        print_success "Python ${PYTHON_VERSION} now active in virtual environment"
                    else
                        print_error "Installation failed. Try manual installation instead."
                        exit 1
                    fi
                else
                    print_error "Homebrew not found!"
                    echo ""
                    echo -e "${YELLOW}Install Homebrew first:${NC}"
                    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                    echo ""
                    echo -e "${YELLOW}Or use manual installation (option 2)${NC}"
                    exit 1
                fi
                ;;
            2)
                # Manual instructions
                echo ""
                echo -e "${GREEN}Python Upgrade Instructions:${NC}"
                echo ""
                echo -e "${CYAN}Option 1: Using Homebrew (recommended for macOS)${NC}"
                echo "  brew install python@3.12"
                echo "  brew link python@3.12"
                echo ""
                echo -e "${CYAN}Option 2: Using pyenv (cross-platform)${NC}"
                echo "  brew install pyenv  # macOS"
                echo "  pyenv install 3.12.0"
                echo "  pyenv global 3.12.0"
                echo ""
                echo -e "${CYAN}Option 3: Official installer${NC}"
                echo "  Download from: https://www.python.org/downloads/"
                echo ""
                echo -e "${YELLOW}After upgrading, recreate the virtual environment:${NC}"
                echo "  rm -rf .venv"
                echo "  python3 -m venv .venv"
                echo "  source .venv/bin/activate"
                echo "  pip install -r requirements.txt"
                echo ""
                exit 0
                ;;
            3)
                print_warning "Continuing with Python $PYTHON_VERSION (security risks apply)"
                print_success "Python $PYTHON_VERSION (will work with warnings)"
                ;;
            4)
                print_status "Reminder set - continuing with Python $PYTHON_VERSION"
                print_success "Python $PYTHON_VERSION (will work with warnings)"
                ;;
            *)
                print_warning "Invalid choice - continuing with Python $PYTHON_VERSION"
                print_success "Python $PYTHON_VERSION (will work with warnings)"
                ;;
        esac
    else
        print_success "Python ${PYTHON_VERSION} found"
    fi
elif [ "$SKIP_PYTHON_CHECK" != "true" ]; then
    print_error "Python 3 not found!"
    print_error "Install Python 3.8+ and try again"
    exit 1
fi

# Check Node.js version (for web extensions)
print_status "Checking Node.js version..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)

    if [ "$NODE_MAJOR" -lt 18 ]; then
        print_warning "Node.js $NODE_VERSION found (minimum: 18 for typo editor)"
        print_status "  Some web extensions may not work. Upgrade recommended."
        echo -e "  ${BLUE}└─${NC} Download: ${CYAN}https://nodejs.org${NC}"
    elif [ "$NODE_MAJOR" -eq 18 ]; then
        print_warning "Node.js $NODE_VERSION (EOL: April 2025)"
        print_status "  Consider upgrading to Node.js 20 LTS or 22 LTS"
        print_success "Node.js ${NODE_VERSION} (compatible)"
    else
        print_success "Node.js ${NODE_VERSION} found"
    fi
else
    print_warning "Node.js not found (optional for web extensions)"
    print_status "  Install Node.js 18+ to enable typo editor"
    echo -e "  ${BLUE}└─${NC} Download: ${CYAN}https://nodejs.org${NC}"
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

    # Suppress Python 3.9 EOL warnings - check if import succeeds
    if ! python3 -W ignore::DeprecationWarning -c "import $module_name" 2>&1 | grep -v "packages_distributions" > /dev/null; then
        # Import failed
        if python3 -c "import $module_name" 2>&1 | grep -q "ModuleNotFoundError\|ImportError"; then
            MISSING_DEPS=1
            if [ -z "$MISSING_LIST" ]; then
                MISSING_LIST="$package"
            else
                MISSING_LIST="$MISSING_LIST, $package"
            fi
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
if command -v node &> /dev/null; then
    # Quick check only - skip prompts on startup for speed
    if [ -f "extensions/cloned/micro/micro" ] && [ -d "extensions/cloned/typo" ]; then
        # Both installed - skip
        :
    else
        print_status "Web extensions available (use POKE to install)"
    fi
fi

# Check data directories (v2.0: sandbox-based structure) - silent creation
for dir in sandbox/logs sandbox/drafts sandbox/workflow sandbox/scripts sandbox/ucode sandbox/tests memory/user memory/planet memory/community memory/shared memory/groups; do
    mkdir -p "$dir" 2>/dev/null
done

# Skip slow file existence checks - files will be created on first run if needed

# Skip JSON validation - Python will handle errors at runtime

# Display startup summary
echo ""
print_success "System ready"
echo ""

# Run the main application with any provided arguments
python uDOS.py "$@"

# Deactivate the virtual environment on exit
deactivate
