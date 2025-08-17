#!/bin/bash
# Script to rename uDEV files to proper filename convention v2.0
# Fixes: 4-digit time to 6-digit HHMMSS, removes invalid suffixes, applies proper naming

cd /Users/agentdigital/uDOS/wizard/notes

echo "🔄 Renaming uDEV files to filename convention v2.0..."
echo "=============================================="

# Function to generate a proper timestamp
generate_proper_timestamp() {
    local original_date="$1"
    local original_time="$2"
    
    # If time is 4 digits, pad with 00 seconds
    if [[ ${#original_time} -eq 4 ]]; then
        echo "${original_time}00"
    elif [[ ${#original_time} -eq 6 ]]; then
        echo "$original_time"
    else
        # Default to current time if invalid
        echo "$(date +%H%M%S)"
    fi
}

# Function to create proper description from old suffix
generate_description() {
    local suffix="$1"
    
    case "$suffix" in
        00PL*) echo "Development-Planning" ;;
        00SY*) echo "System-Development" ;;
        WFCLEA*) echo "Workflow-Cleanup" ;;
        SCCLEANU*) echo "Source-Code-Cleanup" ;;
        00SS*) echo "System-Session" ;;
        *) 
            # Try to extract meaningful description
            if [[ $suffix =~ [A-Z]{2,} ]]; then
                echo "Development-Session"
            else
                echo "Dev-Activity"
            fi
            ;;
    esac
}

renamed_count=0
error_count=0

# Process files with old format patterns
for file in uDEV-*.md; do
    if [[ -f "$file" ]]; then
        # Check if file needs renaming (has problematic patterns)
        if [[ $file =~ uDEV-([0-9]{8})-([0-9]{4})C0-(.+)\.md ]] || 
           [[ $file =~ uDEV-([0-9]{8})-([0-9]{4})-(.+)\.md ]] ||
           [[ $file =~ uDEV-([0-9]{8})-([0-9]{6})C0-([0-9]{2}[A-Z]{2}[0-9]{2})\.md ]]; then
            
            # Extract components
            date_part="${BASH_REMATCH[1]}"
            time_part="${BASH_REMATCH[2]}"
            suffix="${BASH_REMATCH[3]}"
            
            # Generate proper timestamp
            proper_time=$(generate_proper_timestamp "$date_part" "$time_part")
            
            # Generate proper description
            description=$(generate_description "$suffix")
            
            # Create new filename with proper format
            new_name="uDEV-${date_part}-${proper_time}C0-${description}.md"
            
            # Check if new name already exists
            if [[ -f "$new_name" ]]; then
                # Add sequence number to avoid conflicts
                counter=1
                while [[ -f "${new_name%.md}-${counter}.md" ]]; do
                    ((counter++))
                done
                new_name="${new_name%.md}-${counter}.md"
            fi
            
            # Perform rename
            if mv "$file" "$new_name" 2>/dev/null; then
                echo "✅ $file → $new_name"
                ((renamed_count++))
            else
                echo "❌ Failed to rename: $file"
                ((error_count++))
            fi
        fi
    fi
done

echo ""
echo "=============================================="
echo "📊 Renaming Summary:"
echo "  ✅ Successfully renamed: $renamed_count files"
if [[ $error_count -gt 0 ]]; then
    echo "  ❌ Errors encountered: $error_count files"
fi
echo ""

# Show some examples of the new naming
echo "📋 Recent renamed files (sample):"
ls uDEV-*Development*.md 2>/dev/null | head -5 | while read -r file; do
    echo "  📄 $file"
done

echo ""
echo "🎯 Filename Convention v2.0 Applied:"
echo "  Format: uDEV-YYYYMMDD-HHMMSSTZ-Description.md"
echo "  Time: 6-digit HHMMSS format (with seconds)"
echo "  Timezone: C0 (UTC+8)"
echo "  Description: Meaningful, hyphen-separated titles"
echo ""
echo "Status: COMPLETE ✅"
