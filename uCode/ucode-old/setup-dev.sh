#!/usr/bin/env bash
set -e

echo "🔧 Starting uDOS Dev Environment Setup..."

# Print system and Git info
echo "🖥️  Hostname: $(hostname)"
echo "🌿 Git Version: $(git --version)"
echo "🐚 Shell: $SHELL"
echo "📂 Working Dir: $(pwd)"

# Optional setup actions
echo "📦 Installing optional tools (if any)..."
# Add optional dev tools installation here

# Setup complete
echo "✅ uDOS development container is ready to use."