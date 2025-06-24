#!/bin/bash
# system-tree.sh — Generate repo_structure.txt with filtered output

UDOSE_HOME="/root/uDOS"
uDOS_ROOT="$UDOSE_HOME"

if [ ! -d "$uDOS_ROOT" ]; then
  echo "❌ uDOS root directory not found at: $uDOS_ROOT"
  exit 1
fi

OUTPUT_FILE="$uDOS_ROOT/repo_structure.txt"
START_DIR="$uDOS_ROOT"
INDENT="  "

echo "📦 Generating project tree..."

generate_tree() {
  local dir=$1
  local prefix=$2

  find "$dir" -mindepth 1 -maxdepth 1 ! -name ".*" | sort | while read -r entry; do
    local name=$(basename "$entry")

    # Exclude specific macOS or unwanted system internals
    case "$name" in
      "Contents"|"Icon"|"_CodeSignature"|*.lproj|*.car|*.icns|"Assets.car"|"Info.plist"|"document.wflow")
        continue
        ;;
    esac

    # Skip inside .app bundles
    if [[ "$entry" == *".app/"* ]] || [[ "$entry" == *".app"* && -d "$entry" ]]; then
      echo "${prefix}|-- $name" >> "$OUTPUT_FILE"
      continue
    fi

    if [ -d "$entry" ]; then
      echo "${prefix}|-- $name" >> "$OUTPUT_FILE"
      generate_tree "$entry" "$prefix$INDENT"
    else
      echo "${prefix}|  |-- $name" >> "$OUTPUT_FILE"
    fi
  done
}

# Clear file
echo "." > "$OUTPUT_FILE"
generate_tree "$START_DIR" "$INDENT"

echo "✅ Repo tree written to $OUTPUT_FILE"
cat "$OUTPUT_FILE"

# Log the move
MOVE_LOG="$uDOS_ROOT/uMemory/logs/moves-$(date +%Y-%m-%d).md"
mkdir -p "$(dirname "$MOVE_LOG")"
echo "📌 $(date +"%Y-%m-%d %H:%M:%S") - Move: tree (generate repo_structure)" >> "$MOVE_LOG"