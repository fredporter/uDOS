#!/bin/bash
# uDOS Beta v1.7.1 - Reorganized Architecture
# 📁 structure.sh — build and validate uDOS folder architecture

# Constants
UHOME="${HOME}/uDOS"
PATHS=(
  # uMemory = All user content storage
  "uMemory/user"
  "uMemory/scripts"
  "uMemory/templates"
  "uMemory/sandbox"
  "uMemory/missions"
  "uMemory/milestones"
  "uMemory/legacy"
  "uMemory/logs/moves"
  "uMemory/logs/errors"
  "uMemory/state"
  
  # uKnowledge = Central shared knowledge bank
  "uKnowledge/companion"
  "uKnowledge/general-library"
  "uKnowledge/maps"
  
  # uCode = Complete command centre (already exists)
  "uCode/packages"
  
  # uScript = System scripts and bash execution
  "uScript/system"
  "uScript/utilities"
  "uScript/automation"
  "uScript/examples"
  "uScript/extract"
  
  # uTemplate = System templates and datasets
  "uTemplate/system"
  "uTemplate/datasets"
  "uTemplate/variables"
  "uTemplate/system/dashboard.md"
)
FORCE=false
INCLUDE_INPUT=false

# Helpers
log() {
  echo "[structure] $1"
}

create_folder() {
  local dir="$1"
  if [[ -d "$UHOME/$dir" && "$FORCE" = false ]]; then
    log "exists: $dir"
  else
    if [[ "$dir" == *.md ]]; then
      touch "$UHOME/$dir"
      log "created file: $dir"
    else
      mkdir -p "$UHOME/$dir"
      log "created dir: $dir"
    fi
  fi
}

make_input() {
  local inputfile="$UHOME/uMemory/sandbox/input.md"
  if [[ -f "$inputfile" && "$FORCE" = false ]]; then
    log "input.md already exists"
  else
    cat <<EOF > "$inputfile"
# 📥 input.md
## Enter your uDOS move, mission or idea below:
EOF
    log "generated: sandbox/input.md"
  fi
}

# Commands
build_structure() {
  log "creating uDOS folder structure in $UHOME"
  mkdir -p "$UHOME"
  for path in "${PATHS[@]}"; do
    create_folder "$path"
  done

  [[ "$INCLUDE_INPUT" == true ]] && make_input
}

check_structure() {
  log "checking folder layout in $UHOME"
  for path in "${PATHS[@]}"; do
    if [[ -d "$UHOME/$path" ]]; then
      echo "✔ $path"
    else
      echo "✘ $path (missing)"
    fi
  done
}

# Parse Args
case "$1" in
  build)
    shift
    while [[ "$1" != "" ]]; do
      case "$1" in
        --force) FORCE=true ;;
        --input) INCLUDE_INPUT=true ;;
      esac
      shift
    done
    build_structure
    ;;
  check)
    check_structure
    ;;
  *)
    echo "Usage:"
    echo "  ./structure.sh build [--force] [--input]  # Create folders"
    echo "  ./structure.sh check                     # Verify folders"
    ;;
esac