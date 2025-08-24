#!/bin/bash
# uDATA System Demonstration Script
# Shows the capabilities of the uCORE JSON/uDATA parser system

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

echo -e "${CYAN}🔧 uDOS JSON/uDATA Parser System Demonstration${NC}"
echo "=" * 60

echo -e "\n${BLUE}📁 Current System Files:${NC}"
ls -la *.json *.udata *.py 2>/dev/null || echo "No demo files found yet"

echo -e "\n${BLUE}🔄 Converting JSON to uDATA format...${NC}"
python3 udata-converter.py test-sample.json test-sample.udata

echo -e "\n${BLUE}📊 Analyzing uDATA file...${NC}"
python3 udata-converter.py --info test-sample.udata

echo -e "\n${BLUE}✅ Validating uDATA format...${NC}"
python3 udata-converter.py --validate test-sample.udata

echo -e "\n${BLUE}📖 Reading uDATA content:${NC}"
echo "First 5 lines of uDATA file:"
head -5 test-sample.udata | nl

echo -e "\n${BLUE}🧮 uDATA Format Characteristics:${NC}"
echo "• Minified JSON (no unnecessary spaces)"
echo "• One record per line"
echo "• Preserves all original data structure"
echo "• Includes metadata for provenance"
echo "• Human-readable with line breaks"

echo -e "\n${BLUE}💾 File Comparison:${NC}"
echo "Original JSON size: $(wc -c < test-sample.json) bytes"
echo "uDATA size:         $(wc -c < test-sample.udata) bytes"
echo "Original JSON lines: $(wc -l < test-sample.json) lines"
echo "uDATA lines:         $(wc -l < test-sample.udata) lines"

echo -e "\n${GREEN}✅ uDATA System Features Demonstrated:${NC}"
echo "✓ JSON to uDATA conversion"
echo "✓ Minified format with line breaks per record"
echo "✓ Automatic metadata generation"
echo "✓ File validation"
echo "✓ Statistical analysis"
echo "✓ Universal format reading"

echo -e "\n${YELLOW}💡 Usage Examples:${NC}"
echo "Convert:     python3 udata-converter.py input.json output.udata"
echo "Validate:    python3 udata-converter.py --validate file.udata"
echo "Analyze:     python3 udata-converter.py --info file.udata"
echo "Shell tool:  ./convert-to-udata.sh input.json [output.udata]"
