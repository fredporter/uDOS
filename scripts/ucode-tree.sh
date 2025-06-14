#!/bin/bash
# Generate repo_structure.txt skipping dotfiles

OUTPUT_FILE="repo_structure.txt"
START_DIR="."
INDENT="  "

echo "📦 Generating project tree..."

generate_tree() {
  local dir=$1
  local prefix=$2

  find "$dir" -mindepth 1 -maxdepth 1 ! -name ".*" | sort | while read -r entry; do
    local name=$(basename "$entry")
    if [ -d "$entry" ]; then
      echo "${prefix}|-- $name" >> "$OUTPUT_FILE"
      generate_tree "$entry" "$prefix$INDENT"
    else
      echo "${prefix}|  |-- $name" >> "$OUTPUT_FILE"
    fi
  done
}

# Clear and start
echo "." > "$OUTPUT_FILE"
generate_tree "$START_DIR" "$INDENT"

echo "✅ Repo tree written to $OUTPUT_FILE"
cat "$OUTPUT_FILE"

# Log the move
echo "📌 $(date +"%Y-%m-%d %H:%M:%S") - Move: tree (generate repo_structure)" >> /uMemory/logs/moves.md