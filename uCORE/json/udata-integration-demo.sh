#!/bin/bash
# uDOS uDATA System Integration Example
# Shows how uDATA files integrate with uDOS commands and workflows

echo "🔧 uDOS uDATA System Integration"
echo "==============================="
echo ""

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

UDOS_ROOT="/Users/agentdigital/uDOS"
JSON_TOOLS="$UDOS_ROOT/uCORE/json"

echo -e "${CYAN}📋 System Data Quick Access Examples:${NC}"
echo ""

# Example 1: Role Information
echo -e "${GREEN}1. User Role Information:${NC}"
echo -e "   Command: ${YELLOW}ROLE LIST${NC} (uses uDATA-user-roles.json)"
if [[ -f "$UDOS_ROOT/uMEMORY/system/uDATA-user-roles.json" ]]; then
    echo "   Available roles:"
    cd "$JSON_TOOLS"
    python3 -c "
import json
with open('$UDOS_ROOT/uMEMORY/system/uDATA-user-roles.json', 'r') as f:
    for line_num, line in enumerate(f, 1):
        try:
            obj = json.loads(line.strip())
            if 'role' in obj:
                print(f'   • {obj[\"role\"]} (Level {obj[\"level\"]}) - {obj[\"role_id\"]}')
        except: pass
" 2>/dev/null
fi
echo ""

# Example 2: Commands Registry
echo -e "${GREEN}2. System Commands:${NC}"
echo -e "   Source: ${YELLOW}uDATA-commands.udata${NC} (20 commands available)"
if [[ -f "$UDOS_ROOT/uMEMORY/system/uDATA-commands.udata" ]]; then
    echo "   Command categories:"
    cd "$JSON_TOOLS"
    python3 -c "
import json
categories = set()
with open('$UDOS_ROOT/uMEMORY/system/uDATA-commands.udata', 'r') as f:
    for line in f:
        try:
            obj = json.loads(line.strip())
            if 'category' in obj:
                categories.add(obj['category'])
        except: pass
for cat in sorted(categories):
    print(f'   • {cat}')
" 2>/dev/null
fi
echo ""

# Example 3: Extensions
echo -e "${GREEN}3. Extension System:${NC}"
echo -e "   Source: ${YELLOW}extensions/registry.udata${NC}"
if [[ -f "$UDOS_ROOT/extensions/registry.udata" ]]; then
    echo "   Active extensions:"
    cd "$JSON_TOOLS"
    python3 -c "
import json
with open('$UDOS_ROOT/extensions/registry.udata', 'r') as f:
    for line in f:
        try:
            obj = json.loads(line.strip())
            if 'name' in obj and 'status' in obj:
                status_icon = '🟢' if obj['status'] == 'active' else '🟡'
                print(f'   {status_icon} {obj[\"name\"]} v{obj[\"version\"]} ({obj[\"type\"]})')
        except: pass
" 2>/dev/null
fi
echo ""

# Example 4: Data Processing Benefits
echo -e "${CYAN}🚀 uDATA Processing Benefits:${NC}"
echo ""
echo -e "${PURPLE}Fast Line-by-Line Processing:${NC}"
echo "   • Each record is a complete JSON object"
echo "   • No need to parse entire files"
echo "   • Stream processing for large datasets"
echo ""

echo -e "${PURPLE}Memory Efficient:${NC}"
echo "   • Process one record at a time"
echo "   • Suitable for resource-constrained environments"
echo "   • Scalable to any dataset size"
echo ""

echo -e "${PURPLE}Universal Compatibility:${NC}"
echo "   • Readable by any JSON parser"
echo "   • Works with jq, Python, Node.js, etc."
echo "   • Backward compatible with existing tools"
echo ""

# Example 5: Integration with uDOS Commands
echo -e "${CYAN}🔗 Integration Examples:${NC}"
echo ""
echo -e "${GREEN}Command Integration:${NC}"
echo "   ROLE SWITCH wizard    → Reads uDATA-user-roles.json"
echo "   HELP COMMANDS         → Uses uDATA-commands.udata"
echo "   LIST EXTENSIONS       → Queries registry.udata"
echo "   SETUP SYSTEM          → Updates multiple uDATA files"
echo ""

echo -e "${GREEN}Workflow Integration:${NC}"
echo "   • Dashboard generation uses registry data"
echo "   • Role validation checks permissions"
echo "   • Command parsing uses structured data"
echo "   • Extension loading reads metadata"
echo ""

echo -e "${GREEN}Development Benefits:${NC}"
echo "   • Easy data manipulation with Python/TypeScript"
echo "   • Version control friendly (line-based diffs)"
echo "   • Human readable for debugging"
echo "   • Automatic validation and consistency checking"
echo ""

echo -e "${BLUE}✅ uDATA system provides efficient, scalable data management for uDOS${NC}"
echo -e "${YELLOW}🔧 All system components now use standardized uDATA format${NC}"
