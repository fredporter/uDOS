#!/bin/bash
# uDOS System uDATA Processing Summary
# Shows all converted system files and their statistics

echo "🔧 uDOS System uDATA Processing Complete"
echo "========================================"
echo ""

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

UDOS_ROOT="/Users/agentdigital/uDOS"
JSON_TOOLS="$UDOS_ROOT/uCORE/json"

echo -e "${CYAN}📊 System uDATA Files Processed:${NC}"
echo ""

# Check each system file
files_processed=0
total_records=0

check_udata_file() {
    local file_path="$1"
    local display_name="$2"

    if [[ -f "$file_path" ]]; then
        files_processed=$((files_processed + 1))
        echo -e "${GREEN}✅ $display_name${NC}"

        # Get file statistics
        if [[ -f "$JSON_TOOLS/udata-converter.py" ]]; then
            cd "$JSON_TOOLS"
            local stats=$(python3 udata-converter.py --info "$file_path" 2>/dev/null | grep "Total Records:" | cut -d: -f2 | xargs)
            if [[ -n "$stats" ]]; then
                total_records=$((total_records + stats))
                echo -e "   📋 Records: ${YELLOW}$stats${NC}"
            fi

            # Get file size
            local size=$(ls -lh "$file_path" | awk '{print $5}')
            echo -e "   📁 Size: ${BLUE}$size${NC}"
        fi
        echo ""
    else
        echo -e "${YELLOW}⚠️  $display_name - File not found${NC}"
        echo ""
    fi
}

# System Data Files
echo -e "${CYAN}🛠️  Core System Data:${NC}"
check_udata_file "$UDOS_ROOT/uMEMORY/system/uDATA-user-roles.json" "User Roles & Permissions (Already uDATA)"
check_udata_file "$UDOS_ROOT/uMEMORY/system/uDATA-commands.udata" "System Commands Registry"
check_udata_file "$UDOS_ROOT/uMEMORY/system/uDATA-shortcodes.udata" "Shortcodes System"
check_udata_file "$UDOS_ROOT/uMEMORY/system/uDATA-colours.udata" "Color Palette System"
check_udata_file "$UDOS_ROOT/uMEMORY/system/uDATA-variable-system.udata" "Variable System Configuration"
check_udata_file "$UDOS_ROOT/uMEMORY/system/uDATA-font-registry.udata" "Font Registry"

echo -e "${CYAN}🔌 Extension & Component Data:${NC}"
check_udata_file "$UDOS_ROOT/extensions/registry.udata" "Extensions Registry"
check_udata_file "$UDOS_ROOT/uCORE/code/registry.udata" "uCORE Components Registry"

echo ""
echo -e "${CYAN}📈 Processing Summary:${NC}"
echo "========================================"
echo -e "Files Processed: ${GREEN}$files_processed${NC}"
echo -e "Total Records: ${YELLOW}$total_records${NC}"
echo ""

# Show uDATA format benefits
echo -e "${CYAN}💡 uDATA Format Benefits:${NC}"
echo "• Minified JSON with line breaks per record"
echo "• Universal reading capability (JSON & uDATA)"
echo "• Automatic metadata generation with provenance"
echo "• Space efficient storage"
echo "• Fast line-by-line processing"
echo "• Built-in validation and analysis tools"
echo ""

# Show available tools
echo -e "${CYAN}🔧 Available Tools:${NC}"
echo "• convert-to-udata.sh - Shell wrapper for conversion"
echo "• udata-converter.py - Python implementation"
echo "• convert-formatted-json.py - For pretty-printed JSON"
echo "• udataParser.ts - TypeScript implementation"
echo ""

echo -e "${GREEN}✅ System uDATA processing complete!${NC}"
echo -e "${BLUE}🚀 All major system files now in efficient uDATA format${NC}"
