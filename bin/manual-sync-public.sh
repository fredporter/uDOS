#!/bin/bash
# Manual sync to public repository (for testing when workflow secrets aren't working)

set -euo pipefail

echo "🔄 Manual Public Repo Sync"
echo "=========================="

# Check environment variables
if [ -z "${PUBLIC_REPO:-}" ]; then
    echo "❌ Error: PUBLIC_REPO not set"
    echo "   Set it: export PUBLIC_REPO='fredporter/uDOS-core'"
    exit 1
fi

if [ -z "${PUBLIC_TOKEN:-}" ]; then
    echo "❌ Error: PUBLIC_TOKEN not set"
    echo "   Set it: export PUBLIC_TOKEN='your-github-token'"
    exit 1
fi

echo "✅ PUBLIC_REPO: $PUBLIC_REPO"
echo "✅ PUBLIC_TOKEN: (hidden)"
echo ""

# Create mirror directory
echo "📁 Preparing mirror..."
rm -rf mirror/
mkdir -p mirror

# Sync public folder
if [ -d "public" ]; then
    echo "📦 Syncing /public/..."
    rsync -av --delete \
        --exclude='.git' \
        --exclude='.DS_Store' \
        --exclude='node_modules' \
        --exclude='wizard/config/*.json' \
        --exclude='wizard/config/.*' \
        --exclude='**/*.env' \
        --exclude='**/.env*' \
        --exclude='**/secrets*' \
        --exclude='**/*_keys.json' \
        --exclude='**/*_token*' \
        public/ mirror/
    echo "✅ Synced /public/ (excluded secrets)"
fi

# Copy example configs
if [ -d "public/wizard/config" ]; then
    echo "📋 Adding example configs..."
    mkdir -p mirror/wizard/config
    cp -v public/wizard/config/*.example.json mirror/wizard/config/ 2>/dev/null || true
    echo "✅ Included example configs"
fi

# Sync core folder
if [ -d "core" ]; then
    echo "📦 Syncing /core/..."
    rsync -av --exclude='__pycache__' --exclude='*.pyc' --exclude='node_modules' --exclude='build' --exclude='dist' core/ mirror/core/
    echo "✅ Synced /core/"
fi

# Sync docs folder
if [ -d "docs" ]; then
    echo "📦 Syncing /docs/..."
    rsync -av docs/ mirror/docs/
    echo "✅ Synced /docs/"
fi

# Copy LICENSE files
if [ -f LICENSE ] || [ -f LICENSE.txt ] || [ -f LICENSE.md ]; then
    echo "📄 Syncing LICENSE..."
    cp -v LICENSE* mirror/ 2>/dev/null || true
    echo "✅ Synced LICENSE"
fi

# Generate README
echo "📝 Generating README..."
cat > mirror/README.md << 'EOF'
# uDOS Core

Offline-first, distributed OS layer combining Python TUI, TypeScript runtime, and Tauri GUI.

This is the public mirror of uDOS. For development and private components, see the private repository at https://github.com/fredporter/uDOS-dev.

## Contents

- **core** - TypeScript runtime for mobile/iPad offline execution
- **wizard** - AI routing services and always-on server
- **extensions** - API and transport layers
- **knowledge** - Knowledge articles and reference
- **docs** - Engineering documentation and specs

## Quick Start

See [INSTALLATION.md](./INSTALLATION.md) for setup instructions.

## Links

- **Public Repo**: https://github.com/fredporter/uDOS-core
- **Private Dev Repo**: https://github.com/fredporter/uDOS-dev
- **Issues**: https://github.com/fredporter/uDOS-dev/issues
- **Discussions**: https://github.com/fredporter/uDOS-dev/discussions

## Status

🟢 Stable alpha release (v1.0.6.0)
Actively developed with regular updates

---

Automated mirror synced from the private repository.
EOF
echo "✅ Generated public README"

echo ""
echo "📊 Mirror contents:"
ls -lah mirror/

# Git operations
echo ""
echo "🔐 Setting up git..."
cd mirror

git init
git config user.email "github-actions@github.com"
git config user.name "GitHub Actions"

echo "📝 Adding files..."
git add -A

if [ -z "$(git diff --cached --name-only)" ]; then
    echo "⚠️  No changes to sync"
    cd ..
    exit 0
fi

echo "💾 Committing..."
git commit -m "chore: sync from private repo ($(date +%Y-%m-%d))"

echo "🌳 Setting up branch..."
git branch -M main

echo "🔗 Adding remote..."
git remote add origin "https://x-access-token:${PUBLIC_TOKEN}@github.com/${PUBLIC_REPO}.git"

echo "🚀 Pushing to $PUBLIC_REPO..."
if git push -f origin main; then
    echo "✅ Successfully pushed to $PUBLIC_REPO"
else
    echo "❌ Push failed"
    exit 1
fi

cd ..
echo ""
echo "✅ Sync complete!"
echo ""
echo "View results at: https://github.com/${PUBLIC_REPO}"
