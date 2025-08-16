#!/bin/bash

# Clean up incorrectly named development files and recreate with proper naming

set -e

SUMMARIES_DIR="/Users/agentdigital/uDOS/uDEV/summaries"
CURRENT_DATE=$(date +%Y%m%d-%H%M)
TIMEZONE_CODE="28"

echo "🧹 Cleaning up incorrectly named development files..."

cd "$SUMMARIES_DIR"

# Simple approach - rename files to proper format
counter=1
for old_file in *; do
    if [[ -f "$old_file" && "$old_file" != "README.md" ]]; then
        # Determine type based on content analysis
        if grep -q -i "summary\|consolidation\|optimization" "$old_file" 2>/dev/null; then
            new_name="uLOG-$CURRENT_DATE-$TIMEZONE_CODE-00SY$(printf "%02d" $counter).md"
        elif grep -q -i "plan\|implementation" "$old_file" 2>/dev/null; then
            new_name="uLOG-$CURRENT_DATE-$TIMEZONE_CODE-00PL$(printf "%02d" $counter).md"
        elif grep -q -i "complete\|restructure" "$old_file" 2>/dev/null; then
            new_name="uLOG-$CURRENT_DATE-$TIMEZONE_CODE-00RC$(printf "%02d" $counter).md"
        else
            new_name="uLOG-$CURRENT_DATE-$TIMEZONE_CODE-00DV$(printf "%02d" $counter).md"
        fi
        
        echo "📝 Renaming: $old_file → $new_name"
        mv "$old_file" "$new_name"
        ((counter++))
    fi
done

echo "✅ File cleanup complete!"
