#!/bin/bash

# === uDOS Draft Generator: Create New File in Sandbox from Template ===

UDOSE_HOME="/root/uDOS"
SANDBOX="$UDOSE_HOME/sandbox"
UTEMPLATE="$UDOSE_HOME/uTemplate"

echo "📘 Available Templates:"
select type in "mission" "milestone" "legacy" "custom"; do
  case $type in
    mission)   TEMPLATE="$UTEMPLATE/mission-template.md";   PREFIX="draft-mission" ;;
    milestone) TEMPLATE="$UTEMPLATE/milestone-template.md"; PREFIX="draft-milestone" ;;
    legacy)    TEMPLATE="$UTEMPLATE/legacy-template.md";    PREFIX="draft-legacy" ;;
    custom)    
      read -p "🔧 Enter full path to custom template: " TEMPLATE
      PREFIX="draft-custom"
      ;;
    *) 
      echo "❌ Invalid choice"
      exit 1
      ;;
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

echo "📝 Opening with nano..."
nano "$DEST"

echo "🎉 Draft saved to: $DEST"
