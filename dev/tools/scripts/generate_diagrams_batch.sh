#!/bin/bash
# Batch generate Mac OS System 1 style diagrams
# Usage: ./generate_diagrams_batch.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PYTHON="${PROJECT_ROOT}/.venv/bin/python"
GENERATOR="${PROJECT_ROOT}/dev/tools/generate_example_diagrams.py"

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║           Mac OS System 1 Diagram Batch Generator                       ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -f "$PYTHON" ]; then
    echo "❌ Virtual environment not found at: $PYTHON"
    exit 1
fi

# Generate example diagrams
echo "📊 Generating example diagrams..."
"$PYTHON" "$GENERATOR"

# Count total diagrams
TOTAL_FIRE=$(find "$PROJECT_ROOT/knowledge/diagrams/fire" -name "*.svg" 2>/dev/null | wc -l | tr -d ' ')
TOTAL_WATER=$(find "$PROJECT_ROOT/knowledge/diagrams/water" -name "*.svg" 2>/dev/null | wc -l | tr -d ' ')
TOTAL_MEDICAL=$(find "$PROJECT_ROOT/knowledge/diagrams/medical" -name "*.svg" 2>/dev/null | wc -l | tr -d ' ')
TOTAL_FOOD=$(find "$PROJECT_ROOT/knowledge/diagrams/food" -name "*.svg" 2>/dev/null | wc -l | tr -d ' ')
TOTAL_SHELTER=$(find "$PROJECT_ROOT/knowledge/diagrams/shelter" -name "*.svg" 2>/dev/null | wc -l | tr -d ' ')
TOTAL_TOOLS=$(find "$PROJECT_ROOT/knowledge/diagrams/tools" -name "*.svg" 2>/dev/null | wc -l | tr -d ' ')
TOTAL=$(($TOTAL_FIRE + $TOTAL_WATER + $TOTAL_MEDICAL + $TOTAL_FOOD + $TOTAL_SHELTER + $TOTAL_TOOLS))

echo ""
echo "✅ Batch generation complete!"
echo ""
echo "📈 DIAGRAM INVENTORY:"
echo "   Fire:    $TOTAL_FIRE diagrams"
echo "   Water:   $TOTAL_WATER diagrams"
echo "   Medical: $TOTAL_MEDICAL diagrams"
echo "   Food:    $TOTAL_FOOD diagrams"
echo "   Shelter: $TOTAL_SHELTER diagrams"
echo "   Tools:   $TOTAL_TOOLS diagrams"
echo "   ────────────────────"
echo "   Total:   $TOTAL diagrams"
echo ""

# Calculate percentage
PERCENT=$((TOTAL * 100 / 500))
echo "📊 Progress: $TOTAL/500 diagrams ($PERCENT%)"

# Show recent files
echo ""
echo "📁 Recent files:"
find "$PROJECT_ROOT/knowledge/diagrams" -name "*.svg" -type f -exec ls -lht {} + 2>/dev/null | head -5 | awk '{print "   " $9 " (" $5 ")"}'

echo ""
echo "🎨 All diagrams use Mac OS System 1 patterns:"
echo "   • Bold 2-3px strokes"
echo "   • 8×8 bitmap patterns"
echo "   • Generic monospace fonts"
echo "   • Monochrome only (no solid grays)"
