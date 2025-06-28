#!/bin/bash

SETUP_FILE="$UHOME/uTemplate/input-user-setup.md"
OUTPUT_FILE="$UHOME/uMemory/input.md"

mkdir -p "$(dirname "$OUTPUT_FILE")"

echo "# 🧠 uDOS User Input Snapshot" > "$OUTPUT_FILE"
echo "_Generated on $(date)_" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

current_block=""

while IFS= read -r line || [ -n "$line" ]; do
  if [[ "$line" =~ ^## ]]; then
    [ -n "$current_block" ] && echo -e "$current_block\n" >> "$OUTPUT_FILE"
    current_block="$line"
  else
    current_block="$current_block"$'\n'"$line"
  fi
done < "$SETUP_FILE"

[ -n "$current_block" ] && echo -e "$current_block\n" >> "$OUTPUT_FILE"


#!/bin/bash

# Paths
TEMPLATE="$UHOME/uTemplate/input-template.md"
SETUP_FILE="$UHOME/uTemplate/input-user-setup.md"
OUTPUT="$UHOME/uMemory/input.md"

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT")"

# Start output file
echo "# 🧠 uDOS User Input Snapshot" > "$OUTPUT"
echo "_Generated on $(date)_" >> "$OUTPUT"
echo "" >> "$OUTPUT"

current_block=""

while IFS= read -r line || [ -n "$line" ]; do
  if [[ "$line" =~ ^## ]]; then
    # Write block if available
    [ -n "$current_block" ] && echo -e "$current_block\n" >> "$OUTPUT"
    current_block="$line"
  else
    current_block="$current_block"$'\n'"$line"
  fi
done < "$SETUP_FILE"

# Write last block
[ -n "$current_block" ] && echo -e "$current_block\n" >> "$OUTPUT"

echo "✅ Input file created at: $OUTPUT"