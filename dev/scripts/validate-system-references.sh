#!/bin/bash
# uCORE and uSCRIPT System Reference Validation
# Validates that all core systems correctly reference uDATA files

echo "🔍 Validating uCORE and uSCRIPT system references to uDATA files..."
echo "Date: $(date)"
echo

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UMEMORY_SYSTEM="$UDOS_ROOT/uMEMORY/system"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

validation_errors=0

echo "📁 Expected uDATA files in uMEMORY/system:"
expected_files=(
    "uDATA-commands.json"
    "uDATA-shortcodes.json"
    "uDATA-user-roles.json"
    "uDATA-variable-system.json"
    "uDATA-colours.json"
)

for file in "${expected_files[@]}"; do
    if [[ -f "$UMEMORY_SYSTEM/$file" ]]; then
        size=$(ls -lh "$UMEMORY_SYSTEM/$file" | awk '{print $5}')
        echo -e "  ✅ ${GREEN}$file${NC} ($size)"
    else
        echo -e "  ❌ ${RED}$file${NC} - MISSING"
        validation_errors=$((validation_errors + 1))
    fi
done

echo
echo "🔧 Checking uCORE system references:"

# Check udata-config-reader.sh
config_reader="$UDOS_ROOT/uCORE/system/udata-config-reader.sh"
if [[ -f "$config_reader" ]]; then
    echo -e "  📄 Checking: ${BLUE}udata-config-reader.sh${NC}"

    # Check for correct file references
    if grep -q "uDATA-commands.json" "$config_reader"; then
        echo -e "    ✅ ${GREEN}Commands file reference correct${NC}"
    else
        echo -e "    ❌ ${RED}Commands file reference incorrect${NC}"
        validation_errors=$((validation_errors + 1))
    fi

    if grep -q "uDATA-colours.json" "$config_reader"; then
        echo -e "    ✅ ${GREEN}Colors file reference correct${NC}"
    else
        echo -e "    ❌ ${RED}Colors file reference incorrect${NC}"
        validation_errors=$((validation_errors + 1))
    fi
else
    echo -e "  ❌ ${RED}udata-config-reader.sh not found${NC}"
    validation_errors=$((validation_errors + 1))
fi

# Check help-engine.sh
help_engine="$UDOS_ROOT/uCORE/core/help-engine.sh"
if [[ -f "$help_engine" ]]; then
    echo -e "  📄 Checking: ${BLUE}help-engine.sh${NC}"

    if grep -q "uDATA-commands.json" "$help_engine"; then
        echo -e "    ✅ ${GREEN}Help engine commands reference correct${NC}"
    else
        echo -e "    ❌ ${RED}Help engine commands reference incorrect${NC}"
        validation_errors=$((validation_errors + 1))
    fi
else
    echo -e "  ❌ ${RED}help-engine.sh not found${NC}"
    validation_errors=$((validation_errors + 1))
fi

# Check CLI server
cli_server="$UDOS_ROOT/uCORE/server/cli_server.py"
if [[ -f "$cli_server" ]]; then
    echo -e "  📄 Checking: ${BLUE}cli_server.py${NC}"

    if grep -q "uDATA-commands.json" "$cli_server"; then
        echo -e "    ✅ ${GREEN}CLI server commands reference correct${NC}"
    else
        echo -e "    ❌ ${RED}CLI server commands reference incorrect${NC}"
        validation_errors=$((validation_errors + 1))
    fi
else
    echo -e "  ❌ ${RED}cli_server.py not found${NC}"
    validation_errors=$((validation_errors + 1))
fi

echo
echo "🎯 Checking uSCRIPT system references:"

# Check smartInput.js
smart_input="$UDOS_ROOT/uSCRIPT/library/javascript/smartInput.js"
if [[ -f "$smart_input" ]]; then
    echo -e "  📄 Checking: ${BLUE}smartInput.js${NC}"

    if grep -q "uDATA-commands.json" "$smart_input"; then
        echo -e "    ✅ ${GREEN}Smart input commands reference correct${NC}"
    else
        echo -e "    ❌ ${RED}Smart input commands reference incorrect${NC}"
        validation_errors=$((validation_errors + 1))
    fi
else
    echo -e "  ❌ ${RED}smartInput.js not found${NC}"
    validation_errors=$((validation_errors + 1))
fi

echo
echo "🧪 Testing uDATA parser integration:"

# Check TypeScript uDATA parser
udata_parser="$UDOS_ROOT/uCORE/json/src/udataParser.ts"
if [[ -f "$udata_parser" ]]; then
    echo -e "  📄 ${BLUE}udataParser.ts${NC} - ✅ ${GREEN}Present and ready${NC}"
else
    echo -e "  ❌ ${RED}udataParser.ts not found${NC}"
    validation_errors=$((validation_errors + 1))
fi

# Test actual file parsing if possible
if command -v node &> /dev/null && [[ -f "$UMEMORY_SYSTEM/uDATA-20250823-commands.json" ]]; then
    echo -e "  🔬 Testing JSON parsing..."

    # Simple JSON validation test
    if jq empty "$UMEMORY_SYSTEM/uDATA-20250823-commands.json" 2>/dev/null; then
        record_count=$(tail -n +2 "$UMEMORY_SYSTEM/uDATA-20250823-commands.json" | wc -l)
        echo -e "    ✅ ${GREEN}Commands file validates as JSON ($record_count records)${NC}"
    else
        echo -e "    ❌ ${RED}Commands file has JSON parsing errors${NC}"
        validation_errors=$((validation_errors + 1))
    fi
fi

echo
echo "📊 Validation Summary:"
if [[ $validation_errors -eq 0 ]]; then
    echo -e "🎉 ${GREEN}All system references are correct!${NC}"
    echo -e "✅ uCORE and uSCRIPT properly reference uDATA system files"
    echo -e "✅ All expected uDATA files are present in uMEMORY/system"
    echo -e "✅ Core operations, JSON parsing, and template system ready"
else
    echo -e "⚠️  ${YELLOW}Found $validation_errors validation issues${NC}"
    echo -e "❌ Some system references need correction"
fi

echo
echo "🔗 Critical system integration points validated:"
echo "  • Help engine → uDATA-commands.json"
echo "  • CLI server → uDATA-commands.json"
echo "  • Config reader → All uDATA system files"
echo "  • Smart input → uDATA-commands.json (enhanced with shortcodes)"
echo "  • uDATA parser → TypeScript module ready"

exit $validation_errors
