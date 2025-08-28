#!/bin/bash

# uDOS Directory Structure Check
# Ensures flat-like structure and removes empty directories

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 uDOS Directory Structure Check${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for empty directories in uCORE
echo -e "\n${YELLOW}Checking for empty directories in uCORE...${NC}"
cd "$(dirname "$0")/../.."

empty_dirs=$(find uCORE -type d -empty 2>/dev/null || true)
if [[ -n "$empty_dirs" ]]; then
    echo -e "${RED}❌ Found empty directories:${NC}"
    echo "$empty_dirs"
    
    echo -e "\n${YELLOW}Removing empty directories...${NC}"
    find uCORE -type d -empty -delete 2>/dev/null || true
    echo -e "${GREEN}✅ Empty directories removed${NC}"
else
    echo -e "${GREEN}✅ No empty directories found${NC}"
fi

# Verify expected directory structure
echo -e "\n${YELLOW}Verifying expected structure...${NC}"

expected_dirs=(
    "uCORE/bin"
    "uCORE/cache" 
    "uCORE/code"
    "uCORE/config"
    "uCORE/distribution"
    "uCORE/json"
    "uCORE/launcher"
    "uCORE/mapping"
    "uMEMORY"
    "uMEMORY/templates"
    "uSCRIPT"
    "wizard"
    "sandbox"
)

missing_dirs=()
for dir in "${expected_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        echo -e "${GREEN}✅ $dir${NC}"
    else
        echo -e "${RED}❌ $dir (missing)${NC}"
        missing_dirs+=("$dir")
    fi
done

# Report unexpected directories in uCORE
echo -e "\n${YELLOW}Checking for unexpected directories in uCORE...${NC}"
unexpected_dirs=()
for dir in uCORE/*/; do
    dir_name=$(basename "$dir")
    case "$dir_name" in
        bin|cache|code|config|distribution|json|launcher|mapping)
            # Expected directories
            ;;
        *)
            unexpected_dirs+=("uCORE/$dir_name")
            ;;
    esac
done

if [[ ${#unexpected_dirs[@]} -gt 0 ]]; then
    echo -e "${YELLOW}⚠️  Unexpected directories found:${NC}"
    for dir in "${unexpected_dirs[@]}"; do
        echo "  - $dir"
    done
    echo -e "\n${YELLOW}Consider reviewing if these directories should be moved or removed.${NC}"
else
    echo -e "${GREEN}✅ No unexpected directories in uCORE${NC}"
fi

# Summary
echo -e "\n${BLUE}📊 Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ ${#missing_dirs[@]} -eq 0 ]] && [[ ${#unexpected_dirs[@]} -eq 0 ]] && [[ -z "$empty_dirs" ]]; then
    echo -e "${GREEN}✅ Directory structure is clean and follows flat-like principles${NC}"
else
    echo -e "${YELLOW}⚠️  Directory structure has issues that may need attention${NC}"
    
    if [[ ${#missing_dirs[@]} -gt 0 ]]; then
        echo -e "  ${RED}Missing:${NC} ${#missing_dirs[@]} expected directories"
    fi
    
    if [[ ${#unexpected_dirs[@]} -gt 0 ]]; then
        echo -e "  ${YELLOW}Unexpected:${NC} ${#unexpected_dirs[@]} directories in uCORE"
    fi
    
    if [[ -n "$empty_dirs" ]]; then
        echo -e "  ${RED}Empty directories:${NC} cleaned up"
    fi
fi

echo -e "\n${BLUE}Flat-like Structure Principles:${NC}"
echo "• uCORE: Core functionality with specific purpose directories"
echo "• uMEMORY: Data archive with templates and user content"  
echo "• uSCRIPT: Script management separate from core"
echo "• wizard: Development tools separate from core"
echo "• sandbox: User workspace separate from system"

echo ""
