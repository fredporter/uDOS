#!/usr/bin/env bash
# sync-with-remote.sh — Keep local machine in sync with remote
# Part of uDOS-vibe development workflow

set -e

echo "🔄 Syncing with remote..."
echo

# Fetch all updates and prune deleted branches
echo "→ Fetching updates..."
git fetch --all --prune

# Check if there are local changes
if [[ -n $(git status --porcelain) ]]; then
    echo
    echo "⚠️  You have local changes:"
    git status --short | head -15
    echo
    read -p "Stash changes before syncing? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "→ Stashing local changes..."
        git stash push -m "Auto-stash before sync $(date +%Y-%m-%d_%H:%M:%S)"
    fi
fi

# Update main branch
echo
echo "→ Updating main branch..."
git checkout main
git pull --ff-only origin main

# Show status
echo
echo "✅ Sync complete!"
echo
git status --short --branch
echo

# Check for stashed changes
if git stash list | grep -q "Auto-stash"; then
    echo "💾 You have stashed changes. To restore them:"
    echo "   git stash pop"
    echo
fi
