#!/bin/bash
# setup-check.sh – Verifies uOS environment integrity

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MEM="$ROOT/uMemory"
TEMPLATES="$ROOT/templates"
EDITOR_DEFAULT="${EDITOR:-nano}"

echo "🔍 Running setup check..."

# Template check
echo ""
echo "📂 Template Files:"
for t in move-template.md mission-template.md milestone-template.md legacy-template.md; do
  if [ -f "$TEMPLATES/$t" ]; then
    echo "✅ $t found"
  else
    echo "❌ $t missing"
  fi
done

# Directory structure
echo ""
echo "🧠 uMemory structure:"
for d in logs logs/moves logs/errors state missions milestones legacy; do
  if [ -d "$MEM/$d" ]; then
    echo "✅ $d exists"
  else
    echo "❌ $d missing"
  fi
done

# Editor
echo ""
echo "✏️ Editor:"
if command -v "$EDITOR_DEFAULT" >/dev/null 2>&1; then
  echo "✅ Editor '$EDITOR_DEFAULT' available"
else
  echo "⚠️  Editor '$EDITOR_DEFAULT' not found"
fi
