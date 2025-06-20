#!/bin/bash

# === uOS Move 008: Draft a New File in Sandbox from Template ===

SANDBOX="$HOME/uOS/sandbox"
TEMPLATES="$HOME/uOS/templates"

echo "📘 Available Templates:"
select type in "move" "mission" "milestone" "legacy" "custom"; do
  case $type in
    move)      TEMPLATE="$TEMPLATES/move-template.md"; PREFIX="draft-move" ;;
    mission)   TEMPLATE="$TEMPLATES/mission-template.md"; PREFIX="draft-mission" ;;
    milestone) TEMPLATE="$TEMPLATES/milestone-template.md"; PREFIX="draft-milestone" ;;
    legacy)    TEMPLATE="$TEMPLATES/legacy-template.md"; PREFIX="draft-legacy" ;;
    custom)    read -p "🔧 Enter path to custom template: " TEMPLATE; PREFIX="draft-custom" ;;
    *) echo "❌ Invalid choice"; exit 1 ;;
  esac
  break
done

if [[ ! -f "$TEMPLATE" ]]; then
  echo "❌ Template not found: $TEMPLATE"
  exit 1
fi

DATESTAMP=$(date '+%Y-%m-%d')
EPOCH=$(date '+%s')
FILENAME="${PREFIX}-${DATESTAMP}-${EPOCH}.md"
DEST="$SANDBOX/$FILENAME"

echo "📄 Creating sandbox draft: $FILENAME"
cp "$TEMPLATE" "$DEST"

echo "📝 Opening with nano (press Ctrl+O, then Ctrl+X to save and exit)..."
nano "$DEST"

echo "🎉 Draft ready: $DEST"