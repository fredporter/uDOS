#!/bin/bash
# make-tree.sh — Generate clean Alpha v1.0 tree with system folder filtering

UHOME="${HOME}/uDOS"
uDOS_ROOT="$UHOME"

if [ ! -d "$uDOS_ROOT" ]; then
  echo "❌ uDOS root directory not found at: $uDOS_ROOT"
  exit 1
fi

OUTPUT_FILE="$uDOS_ROOT/repo_structure.txt"
START_DIR="$uDOS_ROOT"
INDENT="  "

echo "🌳 Generating Alpha v1.0 project tree..."

generate_tree() {
  local dir=$1
  local prefix=$2

  find "$dir" -mindepth 1 -maxdepth 1 ! -name ".*" | sort | while read -r entry; do
    local name=$(basename "$entry")

    # Alpha v1.0: Exclude system folders and build artifacts
    case "$name" in
      # System and build artifacts
      "Contents"|"Icon"|"_CodeSignature"|*.lproj|*.car|*.icns|"Assets.car"|"Info.plist"|"document.wflow")
        continue
        ;;
      # Node.js and build folders
      "node_modules"|"dist"|"build"|"out"|".next"|"coverage")
        echo "${prefix}├── $name/ (excluded - build artifacts)" >> "$OUTPUT_FILE"
        continue
        ;;
      # Git and editor folders  
      ".git"|".vscode"|".DS_Store")
        continue
        ;;
      # Old/backup folders
      "uDOS-clean-dist"|"uDOS-Extension"|"uExtension")
        continue
        ;;
      # Logs and temporary files
      *.log|*.tmp|*.backup|*.bak)
        continue
        ;;
    esac

    # Skip inside .app bundles but show the .app itself
    if [[ "$entry" == *".app/"* ]]; then
      continue
    elif [[ "$entry" == *".app" && -d "$entry" ]]; then
      echo "${prefix}├── $name" >> "$OUTPUT_FILE"
      continue
    fi

    if [ -d "$entry" ]; then
      # Special handling for Alpha v1.0 new folders
      case "$name" in
        "extension")
          echo "${prefix}├── $name/ (VS Code extension - renamed from uExtension)" >> "$OUTPUT_FILE"
          ;;
        "package")
          echo "${prefix}├── $name/ (Package management system - NEW)" >> "$OUTPUT_FILE"
          ;;
        "install")
          echo "${prefix}├── $name/ (Installation and build scripts - NEW)" >> "$OUTPUT_FILE"
          ;;
        "sandbox")
          echo "${prefix}├── $name/ (Daily workspace - NEW)" >> "$OUTPUT_FILE"
          ;;
        "uMemory")
          echo "${prefix}├── $name/ (User data - gitignored)" >> "$OUTPUT_FILE"
          ;;
        *)
          echo "${prefix}├── $name/" >> "$OUTPUT_FILE"
          ;;
      esac
      
      # Only recurse 2 levels deep to keep output manageable
      local current_depth=$(echo "$prefix" | sed 's/[^├│]//g' | wc -c)
      if [ "$current_depth" -lt 4 ]; then
        generate_tree "$entry" "${prefix}│   "
      fi
    else
      # Show important files only
      case "$name" in
        "README.md"|"LICENSE"|"CHANGELOG.md"|"start-udos.sh"|"install-udos.sh")
          echo "${prefix}├── $name" >> "$OUTPUT_FILE"
          ;;
        "ucode.sh"|"developer-mode.sh"|"sandbox-manager.sh"|"package-manager.sh")
          echo "${prefix}├── $name" >> "$OUTPUT_FILE"
          ;;
        *.md|*.sh|*.json|*.js|*.ts)
          echo "${prefix}├── $name" >> "$OUTPUT_FILE"
          ;;
      esac
    fi
  done
}

# Clear file and add header
cat > "$OUTPUT_FILE" << EOF
# uDOS Alpha v1.0 - Clean Repository Structure
# Generated: $(date)
# Excludes: system folders, build artifacts, .git, node_modules, logs

uDOS/
EOF

generate_tree "$START_DIR" ""

echo ""
echo "✅ Alpha v1.0 clean tree written to $OUTPUT_FILE"
echo "🌳 Repository structure (system folders filtered):"
echo ""
cat "$OUTPUT_FILE"