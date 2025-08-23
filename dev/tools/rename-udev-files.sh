#!/bin/bash
# Script to rename uDEV files to new convention (no dash between timecode and timezone)

cd /Users/agentdigital/uDOS/wizard/notes

echo "Renaming uDEV files to new convention..."

# Rename files with old format: uDEV-YYYYMMDD-HHMM-TZ-* to uDEV-YYYYMMDD-HHMMTZ-*
for file in uDEV-????????-????-??-*.md; do
    if [[ -f "$file" ]]; then
        # Extract parts: uDEV-20250816-2255-28-00SS0816.md
        if [[ $file =~ uDEV-([0-9]{8})-([0-9]{4})-([0-9]{2})-(.+)\.md ]]; then
            date="${BASH_REMATCH[1]}"
            time="${BASH_REMATCH[2]}"
            tz="${BASH_REMATCH[3]}"
            rest="${BASH_REMATCH[4]}"
            
            # Convert timezone to 2-character format
            case "$tz" in
                "28") tz_code="C0" ;;  # UTC+8 assumption
                *) tz_code="C0" ;;     # Default to C0
            esac
            
            new_name="uDEV-${date}-${time}${tz_code}-${rest}.md"
            echo "Renaming: $file -> $new_name"
            mv "$file" "$new_name"
        fi
    fi
done

# Rename files with partial old format: uDEV-YYYYMMDD-HHMMSS-TZ-* to uDEV-YYYYMMDD-HHMMSSTZ-*
for file in uDEV-????????-??????-??-*.md; do
    if [[ -f "$file" ]]; then
        # Extract parts: uDEV-20250817-175538-C0-*
        if [[ $file =~ uDEV-([0-9]{8})-([0-9]{6})-([A-Z0-9]{2})-(.+)\.md ]]; then
            date="${BASH_REMATCH[1]}"
            time="${BASH_REMATCH[2]}"
            tz="${BASH_REMATCH[3]}"
            rest="${BASH_REMATCH[4]}"
            
            new_name="uDEV-${date}-${time}${tz}-${rest}.md"
            echo "Renaming: $file -> $new_name"
            mv "$file" "$new_name"
        fi
    fi
done

echo "Renaming complete!"
