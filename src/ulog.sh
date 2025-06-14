#!/bin/bash
ulog_path="/uKnowledge/logs/ulog-$(date +%Y-%m-%d).md"
mkdir -p "$(dirname "$ulog_path")"

echo "# 🌀 uLog — $(date +%Y-%m-%d)" >> "$ulog_path"
echo "" >> "$ulog_path"

while true; do
  echo -n "uShell > "
  read user_cmd

  # Skip empty input
  [[ -z "$user_cmd" ]] && continue

  echo "## 🔹 Move @ $(date '+%H:%M:%S')" >> "$ulog_path"
  echo "\`\`\`bash" >> "$ulog_path"
  echo "$user_cmd" >> "$ulog_path"
  echo "\`\`\`" >> "$ulog_path"

  # Execute and capture output
  echo "### 🔸 Output:" >> "$ulog_path"
  echo "\`\`\`" >> "$ulog_path"
  eval "$user_cmd" 2>&1 | tee -a "$ulog_path"
  echo "\`\`\`" >> "$ulog_path"

  echo "" >> "$ulog_path"
done