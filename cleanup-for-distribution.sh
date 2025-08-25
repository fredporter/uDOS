#!/bin/bash
# uDOS Distribution Cleanup Script
# Removes local development files, user data, and prepares for clean git distribution

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$UDOS_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧹 uDOS Distribution Cleanup v1.4${NC}"
echo "=================================================================="

# Function to safely remove files/directories
safe_remove() {
    local target="$1"
    local description="$2"
    
    if [ -e "$target" ]; then
        echo -e "${YELLOW}🗑️  Removing: $description${NC}"
        rm -rf "$target"
        echo -e "${GREEN}✅ Removed: $target${NC}"
    else
        echo -e "${BLUE}ℹ️  Already clean: $target${NC}"
    fi
}

# 1. Remove trash directory contents but keep structure
echo -e "\n${BLUE}1. Cleaning trash directory...${NC}"
if [ -d "trash" ]; then
    # Keep the trash directory but empty it completely
    echo -e "${YELLOW}🗑️  Emptying trash directory completely...${NC}"
    rm -rf trash/*
    echo -e "${GREEN}✅ Trash directory emptied${NC}"
else
    echo -e "${BLUE}ℹ️  No trash directory found${NC}"
fi

# 2. Remove empty files
echo -e "\n${BLUE}2. Removing empty files...${NC}"
find . -size 0 -type f -not -path "./.git/*" -print0 | while IFS= read -r -d '' file; do
    echo -e "${YELLOW}🗑️  Removing empty file: $file${NC}"
    rm -f "$file"
done

# 3. Remove system cache files
echo -e "\n${BLUE}3. Removing system cache files...${NC}"
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
find . -name "*.tmp" -type f -delete 2>/dev/null || true
find . -name "*.bak" -type f -delete 2>/dev/null || true
find . -name "*~" -type f -delete 2>/dev/null || true

# 4. Clean up user/role data directories (keep structure, remove content)
echo -e "\n${BLUE}4. Cleaning user/role data directories...${NC}"

# uMEMORY user data cleanup (keep framework structure)
if [ -d "uMEMORY/user" ]; then
    find uMEMORY/user -mindepth 2 -delete 2>/dev/null || true
    echo -e "${GREEN}✅ Cleaned uMEMORY/user content${NC}"
fi

# uMEMORY role data cleanup (keep framework structure)  
if [ -d "uMEMORY/role" ]; then
    find uMEMORY/role -mindepth 2 -delete 2>/dev/null || true
    echo -e "${GREEN}✅ Cleaned uMEMORY/role content${NC}"
fi

# 5. Clean sandbox user content (keep framework)
echo -e "\n${BLUE}5. Cleaning sandbox user content...${NC}"
safe_remove "sandbox/sessions" "sandbox sessions"
safe_remove "sandbox/experiments" "sandbox experiments"  
safe_remove "sandbox/development" "sandbox development work"
safe_remove "sandbox/tasks/in-progress" "sandbox active tasks"
safe_remove "sandbox/tasks/completed" "sandbox completed tasks"
safe_remove "sandbox/scripts" "sandbox user scripts"
safe_remove "sandbox/logs" "sandbox logs"

# 6. Clean development work (keep framework)
echo -e "\n${BLUE}6. Cleaning development work...${NC}"
if [ -d "dev" ]; then
    find dev -name "*.working" -delete 2>/dev/null || true
    find dev -name "*.tmp" -delete 2>/dev/null || true
    find dev -name "*.user.*" -delete 2>/dev/null || true
    find dev -name "*.personal.*" -delete 2>/dev/null || true
    echo -e "${GREEN}✅ Cleaned dev working files${NC}"
fi

# 7. Remove log files (keep structure)
echo -e "\n${BLUE}7. Cleaning log files...${NC}"
find . -name "*.log" -type f -not -path "./.git/*" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Removed log files${NC}"

# 8. Clean Python cache
echo -e "\n${BLUE}8. Cleaning Python cache...${NC}"
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f -delete 2>/dev/null || true
echo -e "${GREEN}✅ Cleaned Python cache${NC}"

# 9. Clean node modules if any
echo -e "\n${BLUE}9. Cleaning Node.js artifacts...${NC}"
find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✅ Cleaned Node.js artifacts${NC}"

# 10. Remove backup directories but keep main backup structure
echo -e "\n${BLUE}10. Cleaning backup directories...${NC}"
if [ -d "backup" ]; then
    # Remove all backup contents but keep the directory structure
    find backup -mindepth 1 -maxdepth 1 -name "*" -exec rm -rf {} + 2>/dev/null || true
    echo -e "${GREEN}✅ Cleaned backup contents${NC}"
fi

# 11. Create missing README files for preserved directory structure
echo -e "\n${BLUE}11. Creating README files for preserved structure...${NC}"

# Create sandbox README if missing
if [ ! -f "sandbox/README.md" ]; then
    cat > "sandbox/README.md" << 'EOF'
# uDOS Sandbox

User workspace for active development and experimentation.

## Structure
- `development/` - Active development work
- `experiments/` - User experiments and testing
- `sessions/` - Session tracking and logs
- `tasks/` - Task management and workflows
- `scripts/` - User scripts and utilities

All content in this directory is designed to be flushable and session-specific.
EOF
fi

# Create uMEMORY structure READMEs if missing
if [ ! -f "uMEMORY/user/README.md" ]; then
    mkdir -p "uMEMORY/user"
    cat > "uMEMORY/user/README.md" << 'EOF'
# uMEMORY User Data

User-specific memory and data storage.

This directory contains user sessions, preferences, and persistent data.
Content is local-only and not distributed with uDOS.
EOF
fi

if [ ! -f "uMEMORY/role/README.md" ]; then
    mkdir -p "uMEMORY/role"
    cat > "uMEMORY/role/README.md" << 'EOF'
# uMEMORY Role Data

Role-specific memory and configuration storage.

This directory contains role installations, configurations, and data.
Content is local-only and not distributed with uDOS.
EOF
fi

echo -e "${GREEN}✅ Structure README files created${NC}"

# 12. Final cleanup validation
echo -e "\n${BLUE}12. Final validation...${NC}"
echo "Repository size:"
du -sh . 2>/dev/null || echo "Size calculation not available"

echo -e "\n${GREEN}🎉 Distribution cleanup complete!${NC}"
echo ""
echo -e "${BLUE}Repository is now clean for distribution with:${NC}"
echo -e "  ✅ Core system files preserved"
echo -e "  ✅ Framework structure maintained"  
echo -e "  ✅ User data removed"
echo -e "  ✅ Development artifacts cleaned"
echo -e "  ✅ Cache and temporary files removed"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Review changes: ${BLUE}git status${NC}"
echo -e "  2. Add changes: ${BLUE}git add -A${NC}"
echo -e "  3. Commit: ${BLUE}git commit -m 'Clean repository for distribution'${NC}"
echo -e "  4. Push: ${BLUE}git push${NC}"
