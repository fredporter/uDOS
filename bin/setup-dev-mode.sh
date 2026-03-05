#!/bin/bash
# uDOS Dev Mode tooling bridge setup
#
# This script ensures the repo's custom tools and skills are discoverable
# by the globally-installed vibe runtime used for Dev Mode.
#
# Usage: ./bin/setup-dev-mode.sh

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔧 Setting up uDOS Dev Mode tooling bridge..."
echo "📁 Repo root: $REPO_ROOT"

# Verify directory structure
if [ ! -d "$REPO_ROOT/vibe/core/tools/ucode" ]; then
    echo "❌ Error: vibe/core/tools/ucode not found"
    exit 1
fi

if [ ! -d "$REPO_ROOT/vibe/core/skills/ucode" ]; then
    echo "❌ Error: vibe/core/skills/ucode not found"
    exit 1
fi

# Create symlinks in .vibe/
mkdir -p "$REPO_ROOT/.vibe"

echo "✓ Creating symlinks..."
rm -f "$REPO_ROOT/.vibe/tools"
rm -f "$REPO_ROOT/.vibe/skills"

ln -s ../vibe/core/tools/ucode "$REPO_ROOT/.vibe/tools"
ln -s ../vibe/core/skills/ucode "$REPO_ROOT/.vibe/skills"

echo "✓ Symlinks created:"
echo "  .vibe/tools -> $(readlink "$REPO_ROOT/.vibe/tools")"
echo "  .vibe/skills -> $(readlink "$REPO_ROOT/.vibe/skills")"

echo ""
cd "$REPO_ROOT"
if vibe --version >/dev/null 2>&1; then
    echo "✓ Dev Mode tooling detected and ready"
else
    echo "⚠️  Dev Mode tooling not found in PATH"
fi

echo ""
# ── Patch global vibe app.py ─────────────────────────────────
# Symlinks the globally-installed vibe's app.py to our repo's version
# so that ucode direct dispatch (: / prefix) works inside vibe CLI.
# Must be re-run after `curl … | sh` vibe updates.
echo "🔧 Patching global vibe app.py for ucode dispatch..."
if bash "$REPO_ROOT/bin/patch-vibe-app.sh"; then
    echo "✓ Global vibe app.py patched"
else
    echo "⚠️  patch-vibe-app.sh failed — ucode : / prefixes may not work in vibe"
    echo "   Re-run manually: ./bin/patch-vibe-app.sh"
fi

echo ""
echo "✅ Dev Mode bridge setup complete!"
echo ""
echo "📖 To use uDOS commands (recommended):"
echo "   cd $REPO_ROOT"
echo "   ./bin/udos"
echo ""
echo "💬 Raw Dev Mode tooling (optional):"
echo "   vibe"
echo "   (non-blocking defaults; MCP is opt-in in .vibe/config.toml)"
echo "   enable MCP tools: uv run --project . scripts/mcp_activation.py enable"
echo ""
echo "💡 Your custom tools are now available:"
echo "   $(ls .vibe/tools/ | grep -v '^__' | tr '\n' ' ')"
echo ""
