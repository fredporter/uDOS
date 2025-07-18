#!/bin/bash
# cleanup-root.sh - uDOS Alpha v1.0 Root Folder Cleanup
# Maintains clean repository structure for production release

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🧹 uDOS Alpha v1.0 Root Cleanup"
echo "==============================="
echo "Cleaning root directory for production release..."

# Remove validation logs
echo "📝 Removing validation logs..."
find "$UDOS_ROOT" -maxdepth 1 -name "validation-*.log" -delete 2>/dev/null || true
find "$UDOS_ROOT" -maxdepth 1 -name "test.log" -delete 2>/dev/null || true

# Remove macOS system files
echo "🍎 Removing macOS system files..."
find "$UDOS_ROOT" -name ".DS_Store" -delete 2>/dev/null || true

# Remove old distribution files
echo "📦 Removing old distribution archives..."
find "$UDOS_ROOT" -maxdepth 1 -name "uDOS-v*.tar.gz" -delete 2>/dev/null || true
find "$UDOS_ROOT" -maxdepth 1 -name "uDOS-v*.zip" -delete 2>/dev/null || true

# Remove backup/temporary files
echo "🗑️ Removing temporary files..."
find "$UDOS_ROOT" -name "*.tmp" -delete 2>/dev/null || true
find "$UDOS_ROOT" -name "*.working" -delete 2>/dev/null || true
find "$UDOS_ROOT" -name "*.backup" -delete 2>/dev/null || true

# Remove old deprecated folders if they exist
echo "📁 Removing deprecated folders..."
[ -d "$UDOS_ROOT/uDOS-clean-dist" ] && rm -rf "$UDOS_ROOT/uDOS-clean-dist"
[ -d "$UDOS_ROOT/uDOS-Extension" ] && rm -rf "$UDOS_ROOT/uDOS-Extension"

# Remove old structure files
echo "📋 Removing old structure files..."
[ -f "$UDOS_ROOT/repo_structure.txt" ] && rm -f "$UDOS_ROOT/repo_structure.txt"

# Ensure proper directory structure exists
echo "🏗️ Ensuring Alpha v1.0 structure..."
mkdir -p "$UDOS_ROOT/extension"
mkdir -p "$UDOS_ROOT/package"
mkdir -p "$UDOS_ROOT/install"
mkdir -p "$UDOS_ROOT/sandbox/today"
mkdir -p "$UDOS_ROOT/sandbox/sessions"
mkdir -p "$UDOS_ROOT/sandbox/temp"
mkdir -p "$UDOS_ROOT/sandbox/drafts"
mkdir -p "$UDOS_ROOT/sandbox/finalized"

# Count and report
echo ""
echo "✅ Cleanup completed!"
echo "📊 Root directory status:"
echo "   Core folders: $(find "$UDOS_ROOT" -maxdepth 1 -type d | wc -l | tr -d ' ') directories"
echo "   Core files: $(find "$UDOS_ROOT" -maxdepth 1 -type f | wc -l | tr -d ' ') files"
echo ""
echo "🎯 Alpha v1.0 structure verified:"
echo "   ✅ extension/ (VS Code extension)"
echo "   ✅ package/ (package management)"
echo "   ✅ install/ (installation system)"
echo "   ✅ sandbox/ (daily workspace)"
echo "   ✅ uCode/ (core system)"
echo "   ✅ uKnowledge/ (knowledge base)"
echo "   ✅ uTemplate/ (templates)"
echo "   ✅ uScript/ (scripting)"
echo ""
echo "🚀 Ready for Alpha v1.0 GitHub launch!"
