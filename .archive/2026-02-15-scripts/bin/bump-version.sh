#!/usr/bin/env bash
# bump-version.sh - Coordinate version bumps across all uDOS components
#
# Usage:
#   bin/bump-version.sh patch          # Bump patch version (1.3.12 -> 1.3.13)
#   bin/bump-version.sh minor          # Bump minor version (1.3.12 -> 1.4.0)
#   bin/bump-version.sh major          # Bump major version (1.3.12 -> 2.0.0)
#   bin/bump-version.sh patch --tag    # Bump + create git tag
#   bin/bump-version.sh patch --push   # Bump + tag + push (triggers release)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse arguments
PART="${1:-}"
DO_TAG=false
DO_PUSH=false

shift || true
for arg in "$@"; do
    case "$arg" in
        --tag)  DO_TAG=true ;;
        --push) DO_TAG=true; DO_PUSH=true ;;
        *)      echo "Unknown option: $arg"; exit 1 ;;
    esac
done

if [[ -z "$PART" ]] || [[ ! "$PART" =~ ^(major|minor|patch)$ ]]; then
    echo "Usage: $0 <major|minor|patch> [--tag] [--push]"
    echo ""
    echo "Options:"
    echo "  --tag   Create a git tag after bumping"
    echo "  --push  Create tag and push to remote (triggers release workflow)"
    exit 1
fi

cd "$PROJECT_ROOT"

# Use the existing Python version manager to bump the root version
echo "Bumping uDOS $PART version..."
echo ""

# Read current root version
ROOT_VERSION_FILE="$PROJECT_ROOT/version.json"
if [[ ! -f "$ROOT_VERSION_FILE" ]]; then
    echo "ERROR: version.json not found at project root"
    exit 1
fi

# Parse current version
CURRENT=$(python3 -c "
import json
with open('$ROOT_VERSION_FILE') as f:
    v = json.load(f)['version']
print(f\"{v['major']}.{v['minor']}.{v['patch']}\")
")

echo "Current version: v$CURRENT"

# Calculate new version
NEW=$(python3 -c "
parts = '$CURRENT'.split('.')
major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
if '$PART' == 'major':
    major += 1; minor = 0; patch = 0
elif '$PART' == 'minor':
    minor += 1; patch = 0
elif '$PART' == 'patch':
    patch += 1
print(f'{major}.{minor}.{patch}')
")

echo "New version:     v$NEW"
echo ""

# Update root version.json
python3 -c "
import json
from datetime import datetime

with open('$ROOT_VERSION_FILE') as f:
    data = json.load(f)

parts = '$NEW'.split('.')
data['version'] = {'major': int(parts[0]), 'minor': int(parts[1]), 'patch': int(parts[2])}
data['display'] = 'v$NEW'
data['released'] = datetime.now().strftime('%Y-%m-%d')

with open('$ROOT_VERSION_FILE', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')

print('  Updated version.json')
"

# Bump component versions using existing version manager
COMPONENTS=("core" "wizard" "api" "transport" "knowledge")
for comp in "${COMPONENTS[@]}"; do
    COMP_FILE="$PROJECT_ROOT/$(python3 -c "
from core.version import COMPONENT_PATHS
print(COMPONENT_PATHS.get('$comp', ''))
" 2>/dev/null || echo "")"

    if [[ -n "$COMP_FILE" ]] && [[ -f "$COMP_FILE" ]]; then
        python3 -m core.version bump "$comp" "$PART" 2>/dev/null && \
            echo "  Updated $comp" || \
            echo "  Skipped $comp (bump failed)"
    else
        echo "  Skipped $comp (not found)"
    fi
done

echo ""
echo "Version bumped to v$NEW"

# Git operations
if $DO_TAG; then
    echo ""
    echo "Creating git commit and tag..."
    git add -A '*.json'
    git commit -m "chore: bump version to v$NEW"
    git tag -a "v$NEW" -m "Release v$NEW"
    echo "Created tag v$NEW"

    if $DO_PUSH; then
        echo "Pushing to remote..."
        git push origin HEAD
        git push origin "v$NEW"
        echo ""
        echo "Tag pushed. Release workflow will trigger automatically."
    else
        echo ""
        echo "To trigger a release, run:"
        echo "  git push origin HEAD && git push origin v$NEW"
    fi
fi
