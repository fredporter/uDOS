#!/bin/bash
# Mistral Vibe CLI Installation Script for uDOS
# ==============================================
# Installs Mistral Vibe - the official CLI coding assistant from Mistral AI
#
# WIZARD ONLY - Requires API key and network access

set -e

echo "🎸 Mistral Vibe CLI Installation for uDOS"
echo "=========================================="
echo ""
echo "Mistral Vibe is a CLI coding assistant powered by Mistral AI."
echo "It provides conversational interaction with your codebase."
echo ""
echo "⚠️  REQUIRES: Mistral API key (get one at https://console.mistral.ai)"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.12+ required. Please install Python first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ "$(echo "$PYTHON_VERSION < 3.12" | bc)" -eq 1 ]]; then
    echo "⚠️  Python 3.12+ recommended. You have $PYTHON_VERSION"
fi

# Install method selection
echo "Installation method:"
echo "  1) One-liner (recommended)"
echo "  2) pip install"
echo "  3) uv tool install"
echo ""
read -p "Select (1-3): " method

case $method in
    1)
        echo "📥 Installing via one-liner..."
        curl -LsSf https://mistral.ai/vibe/install.sh | bash
        ;;
    2)
        echo "📥 Installing via pip..."
        pip install mistral-vibe
        ;;
    3)
        if ! command -v uv &> /dev/null; then
            echo "Installing uv first..."
            curl -LsSf https://astral.sh/uv/install.sh | sh
        fi
        echo "📥 Installing via uv..."
        uv tool install mistral-vibe
        ;;
    *)
        echo "Invalid choice, using one-liner..."
        curl -LsSf https://mistral.ai/vibe/install.sh | bash
        ;;
esac

# Verify installation
if command -v vibe &> /dev/null; then
    echo ""
    echo "✅ Mistral Vibe installed successfully!"
    vibe --version
    
    # Check for API key
    if [ -z "$MISTRAL_API_KEY" ] && [ ! -f ~/.vibe/.env ]; then
        echo ""
        echo "🔑 API Key Setup"
        echo "================"
        echo ""
        echo "Vibe needs a Mistral API key to work."
        echo "Get your key at: https://console.mistral.ai/api-keys"
        echo ""
        read -p "Enter your Mistral API key (or press Enter to skip): " api_key
        
        if [ -n "$api_key" ]; then
            mkdir -p ~/.vibe
            echo "MISTRAL_API_KEY=$api_key" > ~/.vibe/.env
            echo "✅ API key saved to ~/.vibe/.env"
        else
            echo "⏭️  Skipped. Run 'vibe' later and it will prompt for your key."
        fi
    fi
    
    # Create uDOS custom prompts
    echo ""
    echo "📝 Setting up uDOS integration..."
    
    mkdir -p ~/.vibe/prompts
    mkdir -p ~/.vibe/agents
    
    # Create uDOS-specific system prompt
    cat > ~/.vibe/prompts/udos.md << 'UDOS_PROMPT'
# uDOS Development Assistant

You are an AI coding assistant integrated with uDOS, an offline-first knowledge system.

## Context
- uDOS is a Python-venv OS layer for Tiny Core Linux
- Two-Realm Architecture: Device Mesh (offline) vs Wizard Server (online)
- Transport Policy: MeshCore, Bluetooth Private, NFC, QR, Audio (private only)
- Bluetooth Public = SIGNAL ONLY, never data

## Code Standards
- Always use version.json for versions (never hardcode)
- Route commands through uDOS_commands.py
- Use logging tags: [LOCAL] [MESH] [WIZ] [BT-PRIV] etc.
- Tiny Core compatible (no systemd assumptions)

## Key Paths
- core/ - Python TUI system
- extensions/ - API, transport, cloud
- knowledge/ - Markdown knowledge bank
- memory/ - User workspace (gitignored)

## When Fixing Code
1. Check session-commands log first for errors
2. Verify imports and method signatures
3. Consider offline/online separation
4. Test with OK FIX shakedown
UDOS_PROMPT

    # Create uDOS agent config
    cat > ~/.vibe/agents/udos.toml << 'UDOS_AGENT'
# uDOS Development Agent
# Usage: vibe --agent udos

active_model = "devstral-small"
system_prompt_id = "udos"

# Enable all dev tools
[tools.bash]
permission = "ask"

[tools.write_file]
permission = "ask"

[tools.search_replace]
permission = "ask"
UDOS_AGENT

    echo "✅ Created ~/.vibe/prompts/udos.md"
    echo "✅ Created ~/.vibe/agents/udos.toml"
    
    echo ""
    echo "🎉 Installation complete!"
    echo ""
    echo "Quick start:"
    echo "  vibe                    # Start interactive session"
    echo "  vibe --agent udos       # Use uDOS-specific agent"
    echo "  vibe \"Fix the bug\"      # Direct prompt"
    echo ""
    echo "In uDOS TUI:"
    echo "  OK FIX <file>           # Analyze code with Vibe"
    echo "  OK ASK <question>       # Ask coding questions"
else
    echo ""
    echo "❌ Installation failed. Please try manually:"
    echo "   pip install mistral-vibe"
    echo "   # or"
    echo "   curl -LsSf https://mistral.ai/vibe/install.sh | bash"
fi
