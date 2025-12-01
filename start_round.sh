#!/usr/bin/env bash
# uDOS Development Round Launcher
# Usage: ./start_round.sh <round_number>

set -e

ROUND=$1
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_DOC="$PROJECT_ROOT/sandbox/dev/implementation-rounds-dec-2025.md"

if [ -z "$ROUND" ]; then
    echo "❌ Usage: ./start_round.sh <1|2|3>"
    echo ""
    echo "Available rounds:"
    echo "  1 - Variable Definition System (3-5 days)"
    echo "  2 - Play Extension Alignment (4-6 days)"
    echo "  3 - uCODE → uPY Refactor (5-7 days)"
    exit 1
fi

case $ROUND in
    1)
        BRANCH="round-1-variable-system"
        TITLE="Variable Definition System"
        DURATION="3-5 days"
        ;;
    2)
        BRANCH="round-2-play-extension"
        TITLE="Play Extension Alignment"
        DURATION="4-6 days"
        ;;
    3)
        BRANCH="round-3-upy-refactor"
        TITLE="uCODE → uPY Refactor"
        DURATION="5-7 days"
        ;;
    *)
        echo "❌ Invalid round: $ROUND (use 1, 2, or 3)"
        exit 1
        ;;
esac

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    uDOS DEVELOPMENT ROUND $ROUND                          ║"
echo "╠══════════════════════════════════════════════════════════════════════╣"
echo "║  Title: $TITLE"
echo "║  Duration: $DURATION"
echo "║  Branch: $BRANCH"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Pre-flight checks
echo "🔍 Pre-flight checks..."

# Check if on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Warning: Not on main branch (currently on: $CURRENT_BRANCH)"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: Uncommitted changes detected"
    git status --short
    read -p "Stash changes and continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git stash push -m "Pre-round $ROUND stash"
        echo "✅ Changes stashed"
    else
        exit 1
    fi
fi

# Check dependencies for Round 2 and 3
if [ "$ROUND" = "2" ] || [ "$ROUND" = "3" ]; then
    if [ "$ROUND" = "2" ]; then
        echo "📋 Checking Round 1 dependency (SPRITE/OBJECT variables)..."
        if [ ! -f "$PROJECT_ROOT/core/data/variables/sprite.json" ]; then
            echo "❌ Round 1 not complete: sprite.json not found"
            echo "   Complete Round 1 first (Variable Definition System)"
            exit 1
        fi
    fi
fi

echo "✅ Pre-flight checks passed"
echo ""

# Create feature branch
echo "🌿 Creating feature branch: $BRANCH"
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    echo "⚠️  Branch $BRANCH already exists"
    read -p "Switch to existing branch? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout "$BRANCH"
    else
        exit 1
    fi
else
    git checkout -b "$BRANCH"
fi

echo "✅ Branch ready: $BRANCH"
echo ""

# Clean sandbox
echo "🧹 Cleaning sandbox..."
rm -rf sandbox/trash/* 2>/dev/null || true
rm -rf sandbox/logs/*.log 2>/dev/null || true
rm -rf sandbox/.pytest_cache 2>/dev/null || true
echo "✅ Sandbox cleaned"
echo ""

# Create round tracking file
ROUND_FILE="$PROJECT_ROOT/sandbox/dev/round-${ROUND}-progress.md"
if [ ! -f "$ROUND_FILE" ]; then
    echo "📝 Creating progress tracker: $ROUND_FILE"
    cat > "$ROUND_FILE" << EOF
# Round $ROUND Progress - $TITLE

**Started**: $(date '+%Y-%m-%d %H:%M:%S')
**Branch**: $BRANCH
**Estimated Duration**: $DURATION

---

## Tasks

EOF

    # Extract tasks from main doc
    case $ROUND in
        1)
            cat >> "$ROUND_FILE" << 'EOF'
- [ ] 1.1 Create Variable Schema Files
- [ ] 1.2 Extend VariableManager
- [ ] 1.3 SPRITE Variable System
- [ ] 1.4 OBJECT Variable System
- [ ] 1.5 Testing & Documentation

## Success Criteria

- [ ] All 5 JSON schema files created
- [ ] VariableManager loads and validates from schemas
- [ ] SPRITE and OBJECT variables functional
- [ ] 95%+ test coverage
- [ ] Documentation complete
EOF
            ;;
        2)
            cat >> "$ROUND_FILE" << 'EOF'
- [ ] 2.1 STORY Command Integration
- [ ] 2.2 .upy Adventure Scripts
- [ ] 2.3 Sprite/Object Integration
- [ ] 2.4 Map Layer Integration
- [ ] 2.5 Testing & Examples

## Success Criteria

- [ ] STORY command fully functional
- [ ] .upy adventures run with IF/THEN/CHOICE
- [ ] SPRITE variables track HP/XP correctly
- [ ] OBJECT variables work in inventory
- [ ] Map integration complete
- [ ] 3+ example adventures working
EOF
            ;;
        3)
            cat >> "$ROUND_FILE" << 'EOF'
- [ ] 3.1 Naming Convention Implementation
- [ ] 3.2 Command Registry System
- [ ] 3.3 .upy Preprocessor
- [ ] 3.4 Sample .upy Scripts
- [ ] 3.5 Command Handler Modules
- [ ] 3.6 Shell Integration
- [ ] 3.7 Testing & Migration

## Success Criteria

- [ ] All commands use UPPERCASE-HYPHEN naming
- [ ] .upy preprocessor functional
- [ ] Command registry complete
- [ ] 4+ sample .upy scripts
- [ ] Shell integration working
- [ ] Backward compatible with .uscript
- [ ] 95%+ test coverage
EOF
            ;;
    esac

    cat >> "$ROUND_FILE" << EOF

---

## Session Log

### $(date '+%Y-%m-%d')
- Round $ROUND started
- Branch created: $BRANCH
EOF

    echo "✅ Progress tracker created"
else
    echo "ℹ️  Progress tracker exists: $ROUND_FILE"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                      ROUND $ROUND READY TO START                          ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📖 Documentation:"
echo "   - Implementation Plan: sandbox/dev/implementation-rounds-dec-2025.md"
echo "   - Progress Tracker: $ROUND_FILE"
echo ""
echo "🎯 Next Steps:"
case $ROUND in
    1)
        echo "   1. Create core/data/variables/ directory"
        echo "   2. Define system.json schema"
        echo "   3. Define user.json schema"
        echo "   4. Define sprite.json schema"
        echo "   5. Define object.json schema"
        ;;
    2)
        echo "   1. Create extensions/play/commands/story_handler.py"
        echo "   2. Create sandbox/workflow/adventures/ directory"
        echo "   3. Write water_quest.upy adventure"
        echo "   4. Implement SPRITE CREATE command"
        echo "   5. Test STORY + SPRITE integration"
        ;;
    3)
        echo "   1. Create core/data/naming_rules.json"
        echo "   2. Create core/runtime/commands.py registry"
        echo "   3. Create core/interpreters/upy_preprocessor.py"
        echo "   4. Write sample .upy scripts"
        echo "   5. Create bin/udos launcher"
        ;;
esac

echo ""
echo "💡 Tips:"
echo "   - Update progress: edit $ROUND_FILE"
echo "   - Run tests frequently: pytest sandbox/tests/ -v"
echo "   - Commit often: git commit -am \"round $ROUND: task description\""
echo ""
echo "🚀 Ready to code! Good luck!"
echo ""
