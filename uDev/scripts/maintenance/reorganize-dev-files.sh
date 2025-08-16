#!/bin/bash

# uDOS Development File Reorganization Script
# Moves development summaries to uDEV structure with proper uLOG naming

set -e

# Get current timezone code
TIMEZONE_CODE=$(./uCORE/scripts/timezone-mapper-v13.sh current 2>/dev/null | grep "2-digit code:" | cut -d: -f2 | tr -d ' ' || echo "28")
CURRENT_DATE=$(date +%Y%m%d-%H%M)

# Base directories
ROOT_DIR="/Users/agentdigital/uDOS"
DEV_DIR="$ROOT_DIR/uDEV"
SUMMARIES_DIR="$DEV_DIR/summaries"
LOGS_DIR="$DEV_DIR/logs"

echo "🔄 Starting uDOS Development File Reorganization..."
echo "📅 Timestamp: $CURRENT_DATE"
echo "🌍 Timezone: $TIMEZONE_CODE"

# Function to convert filename to uLOG format
convert_to_ulog() {
    local original_file="$1"
    local target_dir="$2"
    local basename=$(basename "$original_file" .md)
    
    # Determine file type and create appropriate uLOG name
    if [[ "$basename" == *"SUMMARY"* ]] || [[ "$basename" == *"Summary"* ]]; then
        local new_name="uLOG-$CURRENT_DATE-$TIMEZONE_CODE-00SY43.md"
    elif [[ "$basename" == *"PLAN"* ]] || [[ "$basename" == *"Plan"* ]]; then
        local new_name="uLOG-$CURRENT_DATE-$TIMEZONE_CODE-00PL43.md"
    elif [[ "$basename" == *"NOTES"* ]] || [[ "$basename" == *"Notes"* ]]; then
        local new_name="uLOG-$CURRENT_DATE-$TIMEZONE_CODE-00NT43.md"
    elif [[ "$basename" == *"CHANGELOG"* ]] || [[ "$basename" == *"Changelog"* ]]; then
        local new_name="uLOG-$CURRENT_DATE-$TIMEZONE_CODE-00CH43.md"
    else
        local new_name="uLOG-$CURRENT_DATE-$TIMEZONE_CODE-00DV43.md"
    fi
    
    # Check if target exists and increment if needed
    local counter=1
    local final_name="$new_name"
    while [[ -f "$target_dir/$final_name" ]]; do
        final_name="uLOG-$CURRENT_DATE-$TIMEZONE_CODE-00DV$(printf "%02d" $counter).md"
        ((counter++))
    done
    
    echo "📝 Moving: $original_file → $target_dir/$final_name"
    mv "$original_file" "$target_dir/$final_name"
}

# Development summary files to move
DEV_SUMMARIES=(
    "CONSOLIDATION_SUMMARY.md"
    "CROSS_PLATFORM_LAUNCHER_SUMMARY.md"
    "DOCUMENTATION_STANDARDS_SUMMARY.md"
    "enhanced-umap-test-summary.md"
    "FINAL_IMPLEMENTATION_PLAN.md"
    "FINAL_SUCCESS_SUMMARY.md"
    "GEMINI_CLI_INTEGRATION_SUMMARY.md"
    "REORGANIZATION_UPDATE.md"
    "REPOSITORY_OPTIMIZATION_SUMMARY.md"
    "RESTRUCTURE_COMPLETE.md"
    "RESTRUCTURE_PLAN.md"
    "UMEMORY_CONSOLIDATION_COMPLETE.md"
    "uDOS-v13-Implementation-Summary.md"
)

echo ""
echo "📁 Moving development summaries to: $SUMMARIES_DIR"
for file in "${DEV_SUMMARIES[@]}"; do
    if [[ -f "$ROOT_DIR/$file" ]]; then
        convert_to_ulog "$ROOT_DIR/$file" "$SUMMARIES_DIR"
    else
        echo "⚠️  File not found: $file"
    fi
done

# Move restructure script to development tools
if [[ -f "$ROOT_DIR/restructure.sh" ]]; then
    echo "🛠️  Moving restructure.sh to uDEV/tools/"
    mkdir -p "$DEV_DIR/tools"
    mv "$ROOT_DIR/restructure.sh" "$DEV_DIR/tools/"
fi

echo ""
echo "✅ Development file reorganization complete!"
echo "📍 VS Code config: $DEV_DIR/vscode/.vscode"
echo "📍 Development summaries: $SUMMARIES_DIR"
echo "📍 Development logs: $LOGS_DIR"
echo "📍 Development tools: $DEV_DIR/tools"
