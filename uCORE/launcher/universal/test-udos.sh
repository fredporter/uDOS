#!/bin/bash
# uDOS Quick Test Suite for Development

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🧪 uDOS Quick Test Suite${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

passed=0
total=0

# Test 1: Server Response
echo -n "1. Server Response: "
((total++))
if curl -s http://localhost:8080/api/status >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Pass${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Fail - Server not responding${NC}"
fi

# Test 2: UI Loading
echo -n "2. UI Loading: "
((total++))
if curl -s http://localhost:8080 | grep -q "uDOS" 2>/dev/null; then
    echo -e "${GREEN}✅ Pass${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Fail - UI not loading properly${NC}"
fi

# Test 3: API Status
echo -n "3. API Status: "
((total++))
if curl -s http://localhost:8080/api/status | grep -q "running" 2>/dev/null; then
    echo -e "${GREEN}✅ Pass${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Fail - API not returning proper status${NC}"
fi

# Test 4: File Structure
echo -n "4. File Structure: "
((total++))
if [ -f "$UDOS_ROOT/uSERVER/server.py" ] && [ -d "$UDOS_ROOT/uCORE" ]; then
    echo -e "${GREEN}✅ Pass${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Fail - Missing required files${NC}"
fi

# Test 5: Role System
echo -n "5. Role System: "
((total++))
role_dirs=("ghost" "tomb" "drone" "imp" "sorcerer" "wizard")
missing_roles=0
for role in "${role_dirs[@]}"; do
    if [ ! -d "$UDOS_ROOT/$role" ]; then
        ((missing_roles++))
    fi
done
if [ $missing_roles -eq 0 ]; then
    echo -e "${GREEN}✅ Pass${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Fail - Missing $missing_roles role directories${NC}"
fi

# Test 6: VS Code Integration
echo -n "6. VS Code Config: "
((total++))
if [ -f "$UDOS_ROOT/.vscode/settings.json" ] && [ -f "$UDOS_ROOT/.vscode/tasks.json" ]; then
    echo -e "${GREEN}✅ Pass${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Fail - VS Code configuration missing${NC}"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Summary
if [ $passed -eq $total ]; then
    echo -e "${GREEN}🎉 All tests passed! ($passed/$total)${NC}"
    exit 0
elif [ $passed -gt $((total / 2)) ]; then
    echo -e "${YELLOW}⚠️  Most tests passed ($passed/$total)${NC}"
    exit 1
else
    echo -e "${RED}❌ Many tests failed ($passed/$total)${NC}"
    exit 1
fi
