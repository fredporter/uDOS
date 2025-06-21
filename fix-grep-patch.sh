#!/bin/bash
# fix-grep-patch.sh — Replace grep -E with grep -E in all .sh files to fix BusyBox compatibility

echo "🔍 Scanning for 'grep -E' usage in .sh files..."

shopt -s globstar
files=()
while IFS= read -r -d $'\0' file; do
  files+=("$file")
done < <(grep -rl --include='*.sh' 'grep -E' . --null)

if [ ${#files[@]} -eq 0 ]; then
  echo "✅ No 'grep -E' usage found in .sh files."
  exit 0
fi

echo "⚠️ Found 'grep -E' in the following files:"
printf '%s\n' "${files[@]}"

for file in "${files[@]}"; do
  echo "🛠 Patching $file ..."
  cp "$file" "$file.bak" && \
  sed -i.bak 's/grep -E/grep -E/g' "$file"
  if [ $? -eq 0 ]; then
    echo "✔️ Patched and backup saved as $file.bak"
  else
    echo "❌ Failed to patch $file"
  fi
done

echo "✅ Patch complete. Review backups (*.bak) before committing."