#!/usr/bin/env bash
# uDOS Development Round Completion Script
# Usage: ./complete_round.sh <round_number>

set -e

ROUND=$1
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$ROUND" ]; then
    echo "❌ Usage: ./complete_round.sh <1|2|3>"
    exit 1
fi

case $ROUND in
    1)
        BRANCH="round-1-variable-system"
        TITLE="Variable Definition System"
        VERSION="v1.1.9-alpha.1"
        ;;
    2)
        BRANCH="round-2-play-extension"
        TITLE="Play Extension Alignment"
        VERSION="v1.1.9-alpha.2"
        ;;
    3)
        BRANCH="round-3-upy-refactor"
        TITLE="uCODE → uPY Refactor"
        VERSION="v1.1.9"
        ;;
    *)
        echo "❌ Invalid round: $ROUND"
        exit 1
        ;;
esac

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              COMPLETING ROUND $ROUND - $TITLE              ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Verify on correct branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo "❌ Not on round branch!"
    echo "   Expected: $BRANCH"
    echo "   Current: $CURRENT_BRANCH"
    exit 1
fi

echo "🔍 Running final checks..."
echo ""

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Uncommitted changes detected:"
    git status --short
    echo ""
    read -p "Commit all changes before completing? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        read -p "Commit message: " COMMIT_MSG
        git add -A
        git commit -m "round $ROUND: $COMMIT_MSG"
        echo "✅ Changes committed"
    fi
fi

# Run tests
echo ""
echo "🧪 Running test suite..."
if command -v pytest &> /dev/null; then
    if pytest sandbox/tests/ -v --tb=short; then
        echo "✅ All tests passing"
    else
        echo "❌ Tests failing - fix before completing round"
        exit 1
    fi
else
    echo "⚠️  pytest not found - skipping tests"
fi

# Check success criteria
echo ""
echo "📋 Success Criteria Checklist:"
case $ROUND in
    1)
        echo "   1. All 5 JSON schema files created? (system, user, sprite, object, story)"
        echo "   2. VariableManager validates all types?"
        echo "   3. SPRITE HP/XP calculations working?"
        echo "   4. OBJECT inventory operations working?"
        echo "   5. 30+ unit tests passing?"
        ;;
    2)
        echo "   1. STORY command functional?"
        echo "   2. 3+ adventure scripts working?"
        echo "   3. SPRITE/OBJECT integration complete?"
        echo "   4. Map layer integration done?"
        echo "   5. 25+ integration tests passing?"
        ;;
    3)
        echo "   1. All commands use hyphenated names?"
        echo "   2. .upy preprocessor functional?"
        echo "   3. Command registry complete?"
        echo "   4. 4+ sample .upy scripts?"
        echo "   5. Shell integration working?"
        ;;
esac

echo ""
read -p "All criteria met? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "❌ Complete remaining tasks before finishing round"
    exit 1
fi

# Merge to main
echo ""
echo "🔀 Merging to main..."
git checkout main
git pull origin main
git merge "$BRANCH" --no-ff -m "feat: Complete Round $ROUND - $TITLE

$(cat sandbox/dev/round-${ROUND}-progress.md | grep -A 20 "## Success Criteria" | tail -n +2 | head -n 10)

Closes Round $ROUND
"

echo "✅ Merged to main"

# Tag release
echo ""
echo "🏷️  Tagging release: $VERSION"
git tag -a "$VERSION" -m "Round $ROUND Complete: $TITLE

Version: $VERSION
Branch: $BRANCH
Date: $(date '+%Y-%m-%d')
"

echo "✅ Tagged: $VERSION"

# Update CHANGELOG
echo ""
echo "📝 Updating CHANGELOG.md..."
CHANGELOG_ENTRY="
## [$VERSION] - $(date '+%Y-%m-%d')

### Added - Round $ROUND: $TITLE

"

# Prepend to CHANGELOG (after header)
if [ -f "CHANGELOG.md" ]; then
    # Create temp file with new entry
    {
        head -n 5 CHANGELOG.md
        echo "$CHANGELOG_ENTRY"
        tail -n +6 CHANGELOG.md
    } > CHANGELOG.tmp
    mv CHANGELOG.tmp CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "docs: Update CHANGELOG for $VERSION"
    echo "✅ CHANGELOG updated"
else
    echo "⚠️  CHANGELOG.md not found - skipping"
fi

# Update roadmap
echo ""
echo "📊 Updating roadmap status..."
ROADMAP_FILE="sandbox/dev/roadmap/ROADMAP.MD"
if [ -f "$ROADMAP_FILE" ]; then
    # Mark round as complete in roadmap
    # (This would need specific sed commands based on roadmap structure)
    echo "ℹ️  Manually update $ROADMAP_FILE to mark round complete"
fi

# Push everything
echo ""
read -p "Push to origin? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    git push origin main
    git push origin "$VERSION"
    echo "✅ Pushed to origin"
fi

# Archive progress tracker
echo ""
echo "📦 Archiving progress tracker..."
ARCHIVE_DIR="sandbox/dev/archive"
mkdir -p "$ARCHIVE_DIR"
mv "sandbox/dev/round-${ROUND}-progress.md" "$ARCHIVE_DIR/round-${ROUND}-progress-$(date '+%Y%m%d').md"
echo "✅ Archived to $ARCHIVE_DIR"

# Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                   ROUND $ROUND COMPLETE! 🎉                              ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Release: $VERSION"
echo "🌿 Branch: $BRANCH (merged to main)"
echo "📅 Completed: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "🎯 Next Steps:"
if [ "$ROUND" = "1" ]; then
    echo "   → Ready for Round 2: Play Extension Alignment"
    echo "   → Run: ./start_round.sh 2"
elif [ "$ROUND" = "2" ]; then
    echo "   → Ready for Round 3: uCODE → uPY Refactor"
    echo "   → Run: ./start_round.sh 3"
elif [ "$ROUND" = "3" ]; then
    echo "   → All rounds complete!"
    echo "   → Version 1.1.9 ready for release"
    echo "   → Update wiki documentation"
    echo "   → Announce new features to users"
fi
echo ""
echo "🚀 Great work!"
echo ""
