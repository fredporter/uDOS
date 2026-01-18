#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                     uDOS Vibe Setup (Offline-First)                      ║
# ║                Mistral Vibe CLI + Devstral Small 2 via Ollama            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

# Navigate to root directory if running from bin/
cd "$(dirname "$0")/.."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                     uDOS Vibe Setup (Offline-First)                      ║"
echo "║                Mistral Vibe CLI + Devstral Small 2 via Ollama            ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Step 1: Install Ollama
echo -e "${BLUE}Step 1: Installing Ollama${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama already installed${NC}"
    ollama --version
else
    echo -e "${YELLOW}Installing Ollama...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ollama
        else
            echo -e "${RED}✗ Homebrew not found. Please install from https://brew.sh${NC}"
            echo "  Then run: brew install ollama"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo -e "${RED}✗ Unsupported OS: $OSTYPE${NC}"
        echo "  Please install Ollama manually from https://ollama.com"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Ollama installed${NC}"
fi

echo ""

# Step 2: Start Ollama service
echo -e "${BLUE}Step 2: Starting Ollama service${NC}"
if pgrep -x "ollama" > /dev/null; then
    echo -e "${GREEN}✓ Ollama service already running${NC}"
else
    echo -e "${YELLOW}Starting Ollama service...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - start as background service
        brew services start ollama 2>/dev/null || ollama serve &
    else
        # Linux - start in background
        ollama serve &
    fi
    
    sleep 2
    echo -e "${GREEN}✓ Ollama service started${NC}"
fi

echo ""

# Step 3: Pull Devstral Small 2 model
echo -e "${BLUE}Step 3: Pulling Devstral Small 2 model${NC}"
echo -e "${YELLOW}⚠️  This may take a while (model size: ~7.7GB)${NC}"

if ollama list | grep -q "mistral-small2"; then
    echo -e "${GREEN}✓ mistral-small2 model already available${NC}"
else
    echo -e "${CYAN}Pulling mistral-small2 from Ollama...${NC}"
    ollama pull mistral-small2
    echo -e "${GREEN}✓ mistral-small2 model downloaded${NC}"
fi

# Also check for devstral-small-2 alias
if ollama list | grep -q "devstral-small-2"; then
    echo -e "${GREEN}✓ devstral-small-2 alias available${NC}"
else
    echo -e "${YELLOW}Note: Using 'mistral-small2' (Devstral Small 2)${NC}"
    echo -e "${YELLOW}You can create alias: ollama cp mistral-small2 devstral-small-2${NC}"
fi

echo ""

# Step 4: Test Ollama
echo -e "${BLUE}Step 4: Testing Ollama connection${NC}"
if curl -s http://127.0.0.1:11434/api/tags &> /dev/null; then
    echo -e "${GREEN}✓ Ollama API responding at http://127.0.0.1:11434${NC}"
    
    # Show available models
    echo -e "\n${CYAN}Available models:${NC}"
    ollama list
else
    echo -e "${RED}✗ Ollama API not responding${NC}"
    echo "  Try: ollama serve"
    exit 1
fi

echo ""

# Step 5: Install Vibe CLI
echo -e "${BLUE}Step 5: Installing Mistral Vibe CLI${NC}"

# Check if vibe exists in library/mistral-vibe
if [ -d "library/mistral-vibe" ]; then
    echo -e "${GREEN}✓ Vibe CLI already cloned in library/mistral-vibe${NC}"
    cd library/mistral-vibe
    git pull --quiet || echo -e "${YELLOW}⚠️  Could not update (no internet or no git)${NC}"
    cd ../..
else
    echo -e "${YELLOW}Cloning Vibe CLI repository...${NC}"
    mkdir -p library
    cd library
    
    if git clone https://github.com/mistralai/vibe.git mistral-vibe 2>/dev/null; then
        echo -e "${GREEN}✓ Vibe CLI cloned${NC}"
    else
        echo -e "${RED}✗ Could not clone Vibe CLI (check internet connection)${NC}"
        echo "  Manual: cd library && git clone https://github.com/mistralai/vibe.git mistral-vibe"
        exit 1
    fi
    
    cd ..
fi

# Install Vibe CLI
if [ -f "library/mistral-vibe/setup.py" ] || [ -f "library/mistral-vibe/pyproject.toml" ]; then
    echo -e "${CYAN}Installing Vibe CLI to venv...${NC}"
    
    # Activate venv
    if [ ! -d ".venv" ]; then
        echo -e "${RED}✗ Virtual environment not found${NC}"
        echo "  Run: python3 -m venv .venv"
        exit 1
    fi
    
    source .venv/bin/activate
    
    # Install vibe
    cd library/mistral-vibe
    pip install -e . --quiet || pip install .
    cd ../..
    
    if command -v vibe &> /dev/null; then
        echo -e "${GREEN}✓ Vibe CLI installed${NC}"
        vibe --version
    else
        echo -e "${RED}✗ Vibe CLI installation failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Vibe CLI not found in expected location${NC}"
    echo "  Check: library/mistral-vibe/"
fi

echo ""

# Step 6: Configure Vibe for uDOS
echo -e "${BLUE}Step 6: Configuring Vibe for uDOS${NC}"

if [ -f ".vibe/config.toml" ]; then
    echo -e "${GREEN}✓ .vibe/config.toml already exists${NC}"
else
    echo -e "${YELLOW}Creating .vibe/config.toml...${NC}"
    mkdir -p .vibe
    cat > .vibe/config.toml << 'EOF'
# uDOS Vibe Configuration

[project]
name = "uDOS"
version = "1.0.2.0"
description = "Offline-first OS layer for Tiny Core Linux"

[model]
provider = "ollama"
model = "mistral-small2"
endpoint = "http://127.0.0.1:11434"
cloud_enabled = false

[context]
context_files = [
    "AGENTS.md",
    "docs/_index.md",
    "docs/roadmap.md",
    ".vibe/CONTEXT.md"
]
EOF
    echo -e "${GREEN}✓ Configuration created${NC}"
fi

if [ -f ".vibe/CONTEXT.md" ]; then
    echo -e "${GREEN}✓ .vibe/CONTEXT.md already exists${NC}"
else
    echo -e "${YELLOW}⚠️  .vibe/CONTEXT.md missing - please create it${NC}"
fi

echo ""

# Step 7: Test Vibe
echo -e "${BLUE}Step 7: Testing Vibe with uDOS context${NC}"

if command -v vibe &> /dev/null; then
    echo -e "${CYAN}Running test query...${NC}"
    
    # Simple test
    echo "Test: 'What is uDOS?'" | vibe chat --no-stream 2>/dev/null || \
        echo -e "${YELLOW}⚠️  Vibe test skipped (may require additional setup)${NC}"
else
    echo -e "${YELLOW}⚠️  Vibe CLI not available for testing${NC}"
fi

echo ""

# Final summary
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                        ✅ Setup Complete!                                 ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}Next steps:${NC}"
echo "  1. Test Vibe: ${YELLOW}vibe chat${NC}"
echo "  2. Ask about uDOS: ${YELLOW}\"What is the command routing architecture?\"${NC}"
echo "  3. Check model: ${YELLOW}ollama list${NC}"
echo "  4. View context: ${YELLOW}cat .vibe/CONTEXT.md${NC}"
echo ""
echo -e "${CYAN}Usage:${NC}"
echo "  ${YELLOW}vibe chat${NC}                 # Interactive chat"
echo "  ${YELLOW}vibe chat \"your question\"${NC}  # Single query"
echo "  ${YELLOW}vibe --help${NC}               # Full help"
echo ""
echo -e "${GREEN}🎉 Vibe is ready for offline-first development!${NC}"
echo ""
