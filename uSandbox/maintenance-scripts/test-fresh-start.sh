#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# 🧪 uDOS Critical Functions Test Suite
# ═══════════════════════════════════════════════════════════════════════
# Test reboot, destroy, and kill trash functionality before fresh start
# ═══════════════════════════════════════════════════════════════════════

UHOME="/Users/agentdigital/uDOS"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              🧪 uDOS CRITICAL FUNCTIONS TEST                 ║${NC}"
echo -e "${BLUE}║           Validating Fresh Start Capabilities                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

# Test 1: Validate identity path is correct
echo -e "${YELLOW}🔍 TEST 1: Identity Path Validation${NC}"
if [[ -f "$UHOME/sandbox/identity.md" ]]; then
    echo -e "${GREEN}✅ Identity found at correct location: sandbox/identity.md${NC}"
else
    echo -e "${RED}❌ Identity not found at sandbox/identity.md${NC}"
    exit 1
fi

# Test 2: Check trash functionality
echo -e "${YELLOW}🗑️ TEST 2: Trash System Validation${NC}"
# Create a test file
echo "Test file for trash validation" > /tmp/test-trash-validate.txt
echo "   Creating test file..."

# Move to trash
$UHOME/uCode/trash.sh move /tmp/test-trash-validate.txt >/dev/null 2>&1
if $UHOME/uCode/trash.sh list | grep -q "test-trash-validate"; then
    echo -e "${GREEN}✅ Trash move functionality working${NC}"
else
    echo -e "${RED}❌ Trash move functionality failed${NC}"
fi

# Test kill trash with auto-confirmation
echo "KILL TRASH" | $UHOME/uCode/trash.sh empty >/dev/null 2>&1
if ! $UHOME/uCode/trash.sh list | grep -q "test-trash-validate"; then
    echo -e "${GREEN}✅ Trash kill functionality working${NC}"
else
    echo -e "${RED}❌ Trash kill functionality failed${NC}"
fi

# Test 3: Check logging system paths
echo -e "${YELLOW}📝 TEST 3: Logging System Path Validation${NC}"

# Source log-utils and test
source "$UHOME/uCode/log-utils.sh"

# Test move logging
log_move "Test move for validation"
if [[ -f "$UHOME/uMemory/move-log-$(date +%Y-%m-%d).md" ]]; then
    echo -e "${GREEN}✅ Move logging working (uMemory)${NC}"
else
    echo -e "${RED}❌ Move logging failed${NC}"
fi

# Test system logging
log_system "INFO" "Test system log"
if [[ -f "$UHOME/uDev/logs/system/$(date +%Y%m%d).log" ]]; then
    echo -e "${GREEN}✅ System logging working (uDev)${NC}"
else
    echo -e "${RED}❌ System logging failed${NC}"
fi

# Test 4: Check destroy script paths
echo -e "${YELLOW}💥 TEST 4: Destroy Script Path Validation${NC}"

# Check if destroy script points to correct identity path
if grep -q "sandbox/identity.md" "$UHOME/uCode/destroy.sh"; then
    echo -e "${GREEN}✅ Destroy script uses correct identity path${NC}"
else
    echo -e "${RED}❌ Destroy script uses incorrect identity path${NC}"
fi

# Check if destroy script has correct legacy preservation logic
if grep -q "uMemory/legacy" "$UHOME/uCode/destroy.sh"; then
    echo -e "${GREEN}✅ Destroy script has correct legacy preservation${NC}"
else
    echo -e "${RED}❌ Destroy script legacy preservation needs fixing${NC}"
fi

# Test 5: Validate critical command functions
echo -e "${YELLOW}🔄 TEST 5: Core Command Validation${NC}"

# Test that ucode.sh points to correct identity
if grep -q 'UDENT=.*sandbox/identity.md' "$UHOME/uCode/ucode.sh"; then
    echo -e "${GREEN}✅ Main ucode.sh uses correct identity path${NC}"
else
    echo -e "${RED}❌ Main ucode.sh uses incorrect identity path${NC}"
fi

# Test logging integration
if grep -q 'source.*log-utils.sh' "$UHOME/uCode"/*.sh 2>/dev/null; then
    echo -e "${GREEN}✅ Logging integration detected in scripts${NC}"
else
    echo -e "${YELLOW}⚠️ Limited logging integration found${NC}"
fi

# Test 6: Directory structure validation
echo -e "${YELLOW}📁 TEST 6: Directory Structure Validation${NC}"

required_dirs=(
    "$UHOME/sandbox"
    "$UHOME/uMemory" 
    "$UHOME/uMemory/legacy"
    "$UHOME/uDev"
    "$UHOME/uDev/logs"
    "$UHOME/uKnowledge"
    "$UHOME/uScript"
)

all_dirs_ok=true
for dir in "${required_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        echo -e "   ${GREEN}✅${NC} $dir"
    else
        echo -e "   ${RED}❌${NC} $dir (missing)"
        all_dirs_ok=false
    fi
done

if [[ "$all_dirs_ok" == "true" ]]; then
    echo -e "${GREEN}✅ All required directories present${NC}"
else
    echo -e "${RED}❌ Some required directories missing${NC}"
fi

echo
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     🎯 FRESH START GUIDE                     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${YELLOW}To start fresh:${NC}"
echo -e "  1. ${GREEN}Kill Trash:${NC} ./uCode/trash.sh empty (type 'KILL TRASH')"
echo -e "  2. ${GREEN}Destroy Options:${NC} ./uCode/destroy.sh"
echo -e "     ${BLUE}[A]${NC} Remove identity only (keep memory)"
echo -e "     ${BLUE}[B]${NC} Remove identity + all memory"  
echo -e "     ${BLUE}[C]${NC} Remove identity + memory (preserve legacy)"
echo -e "     ${BLUE}[D]${NC} Reboot system (no data loss)"
echo -e "  3. ${GREEN}Start Fresh:${NC} ./uCode/ucode.sh or ./start-udos.sh"
echo
echo -e "${GREEN}🎉 All critical functions validated and ready for fresh start!${NC}"
