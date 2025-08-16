#!/bin/bash
# Install Gemini CLI - Google's advanced language model CLI
# Part of uDOS Companion System

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📦 Installing Gemini CLI...${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found. Installing Node.js first...${NC}"
    if command -v brew &> /dev/null; then
        brew install node
    else
        echo -e "${RED}❌ Homebrew not found. Please install Node.js 20+ manually:${NC}"
        echo "   https://nodejs.org/en/download"
        exit 1
    fi
fi

# Check Node.js version
NODE_VERSION=$(node --version | sed 's/v//' | cut -d. -f1)
if [[ $NODE_VERSION -lt 20 ]]; then
    echo -e "${YELLOW}⚠️  Node.js version $NODE_VERSION found. Gemini CLI requires Node.js 20+${NC}"
    echo -e "${BLUE}📦 Upgrading Node.js...${NC}"
    if command -v brew &> /dev/null; then
        brew upgrade node
    else
        echo -e "${RED}❌ Please upgrade Node.js manually to version 20+${NC}"
        exit 1
    fi
fi

# Install Gemini CLI globally
echo -e "${BLUE}📦 Installing @google/gemini-cli globally...${NC}"
if npm install -g @google/gemini-cli; then
    echo -e "${GREEN}✅ Gemini CLI installed successfully!${NC}"
    
    # Verify installation
    if command -v gemini &> /dev/null; then
        echo -e "${GREEN}✅ Gemini CLI is ready to use${NC}"
        echo -e "${BLUE}🚀 Quick start:${NC}"
        echo "   1. Run: gemini"
        echo "   2. Sign in with your Google account"
        echo "   3. Start chatting with Gemini!"
        echo ""
        echo -e "${BLUE}📖 For uDOS integration:${NC}"
        echo "   ./uCode/companion-system.sh init"
        echo "   ./uCode/companion-system.sh gemini"
    else
        echo -e "${YELLOW}⚠️  Installation completed but 'gemini' command not found${NC}"
        echo "   Try: npm install -g @google/gemini-cli"
    fi
else
    echo -e "${RED}❌ Failed to install Gemini CLI${NC}"
    echo "   You can try installing manually:"
    echo "   npm install -g @google/gemini-cli"
    exit 1
fi

# Create integration note
echo ""
echo -e "${BLUE}🔗 Integration with uDOS:${NC}"
echo "   • Use ./uCode/companion-system.sh for uDOS-aware interactions"
echo "   • Gemini CLI provides context-aware code analysis"
echo "   • Supports project analysis, code generation, and workflow optimization"
echo "   • Authentication: Google account or API key"
echo ""
echo -e "${GREEN}✅ Gemini CLI installation complete!${NC}"
