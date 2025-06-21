#!/bin/bash
# setup-check.sh — Check template, EDITOR, and uMemory structure

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
pass="✅"
fail="❌"

echo "🔍 Checking uOS setup..."

# Templates
echo ""
echo "📁 Templates:"
for t in move mission milestone legacy; do
  if [ -f "$BASE/templates/${t}-template.md" ]; then
    echo "$pass $t-template.md exists"
  else
    echo "$fail Missing $t-template.md"
  fi
done

# Folders
echo ""
echo "📂 Required directories:"
for d in logs logs/moves logs/errors milestones missions state; do
  if [ -d "$BASE/uMemory/$d" ]; then
    echo "$pass uMemory/$d/"
  else
    echo "$fail Missing uMemory/$d/"
  fi
done

# Editor
echo ""
echo "📝 Editor availability:"
if command -v ${EDITOR:-nano} >/dev/null 2>&1; then
  echo "$pass Editor found: ${EDITOR:-nano}"
else
  echo "$fail No editor found! Try setting EDITOR or installing nano/vi"
fi
