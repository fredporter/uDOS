#!/bin/bash

# uCode Tree: Generates a tree-like view of the repo into repo_structure.txt

# Go to uOS repo root from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTFILE="$ROOT_DIR/repo_structure.txt"

# Config
OUTFILE="repo_structure.txt"
EXCLUDES=(
  ".git"
  "node_modules"
  "__pycache__"
  "venv"
  ".idea"
  ".vscode"
  "repo_structure.txt"
)

# Build find command with exclusions
FIND_CMD="find ."
for EX in "${EXCLUDES[@]}"; do
  FIND_CMD+=" -path \"./$EX\" -prune -o"
done
FIND_CMD+=" -print"

# Execute and format output
eval $FIND_CMD | sed -e 's/[^-][^\/]*\//  |/g' -e 's/|\([^ ]\)/|-- \1/' > "$OUTFILE"

echo "[uCode] Repo structure written to $OUTFILE"