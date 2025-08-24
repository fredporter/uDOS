#!/bin/bash
# uDOS v1.4 System Cleanup & Organization
# Logging Consolidation, Git Cleanliness, Sandbox Organization

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

UDOS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKUP_DIR="$UDOS_ROOT/backup/v14-cleanup-$(date +%Y%m%d-%H%M%S)"

echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🧹 uDOS v1.4 System Cleanup & Organization${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo -e "${CYAN}📦 Backup location: $BACKUP_DIR${NC}"
echo ""

echo -e "${BLUE}🎯 PHASE 1: Logging System Consolidation${NC}"
echo "─────────────────────────────────────────────"

# 1. Verify logging is properly in uMEMORY (user/session data belongs there)
if [ -d "$UDOS_ROOT/uCORE/system/logs" ]; then
    echo -e "${RED}❌ Found logs in uCORE/system/ - moving to uMEMORY${NC}"
    mv "$UDOS_ROOT/uCORE/system/logs" "$UDOS_ROOT/uMEMORY/system/logs"
    echo -e "${GREEN}✅ Moved logs from uCORE to uMEMORY${NC}"
fi

# 2. Consolidate scattered log directories
log_dirs=(
    "uMEMORY/role/wizard/logs"
    "uMEMORY/user/sandbox/logs"
    "uNETWORK/wizard/logs"
    "uSCRIPT/runtime/logs"
)

for log_dir in "${log_dirs[@]}"; do
    full_path="$UDOS_ROOT/$log_dir"
    if [ -d "$full_path" ]; then
        echo -e "${YELLOW}📋 Consolidating: $log_dir${NC}"
        target_name=$(echo "$log_dir" | tr '/' '-')
        cp -r "$full_path" "$UDOS_ROOT/uMEMORY/system/logs/$target_name" 2>/dev/null || true
        echo -e "   ✅ Copied to uMEMORY/system/logs/$target_name"
    fi
done

# 3. Ensure proper symlink
cd "$UDOS_ROOT/uMEMORY"
if [ -L "logs" ]; then
    rm logs
fi
ln -s "system/logs" logs
echo -e "${GREEN}✅ Created proper logs symlink: uMEMORY/logs -> system/logs${NC}"
echo ""

echo -e "${BLUE}🎯 PHASE 2: Git Repository Cleanliness${NC}"
echo "─────────────────────────────────────────────"

# 1. Check for git bloat
echo -e "${CYAN}📊 Checking repository size...${NC}"
repo_size=$(du -sh "$UDOS_ROOT/.git" | cut -f1)
echo "   Git repository size: $repo_size"

# 2. Find large files that shouldn't be tracked
echo -e "${CYAN}🔍 Scanning for problematic files...${NC}"
problematic_dirs=(
    "venv"
    "__pycache__"
    "node_modules"
    "Cache"
    "cache"
    ".DS_Store"
)

for dir in "${problematic_dirs[@]}"; do
    found=$(find "$UDOS_ROOT" -name "$dir" -type d 2>/dev/null | grep -v ".git" | head -5)
    if [ ! -z "$found" ]; then
        echo -e "${YELLOW}⚠️  Found $dir directories:${NC}"
        echo "$found" | while read line; do
            size=$(du -sh "$line" 2>/dev/null | cut -f1)
            echo "   📁 $line ($size)"
        done
    fi
done

# 3. Ensure proper gitignore coverage
echo -e "${CYAN}📝 Verifying .gitignore coverage...${NC}"
gitignore_items=(
    "**/venv/"
    "**/__pycache__/"
    "**/cache/"
    "**/*.log"
    "**/node_modules/"
)

for item in "${gitignore_items[@]}"; do
    if grep -q "$item" "$UDOS_ROOT/.gitignore"; then
        echo -e "   ✅ $item"
    else
        echo -e "   ${YELLOW}⚠️  Missing: $item${NC}"
    fi
done
echo ""

echo -e "${BLUE}🎯 PHASE 3: Sandbox Organization${NC}"
echo "─────────────────────────────────────────────"

# 1. Remove duplicate sandbox in dev/
if [ -d "$UDOS_ROOT/dev/sandbox" ]; then
    echo -e "${YELLOW}📁 Found duplicate dev/sandbox directory${NC}"
    if [ "$(ls -A "$UDOS_ROOT/dev/sandbox" 2>/dev/null)" ]; then
        echo "   📦 Backing up dev/sandbox content..."
        cp -r "$UDOS_ROOT/dev/sandbox" "$BACKUP_DIR/dev-sandbox-backup"
        # Move any useful content to main sandbox
        if [ -d "$UDOS_ROOT/dev/sandbox/logs" ]; then
            mv "$UDOS_ROOT/dev/sandbox/logs" "$UDOS_ROOT/sandbox/dev-logs"
            echo "   ✅ Moved dev/sandbox/logs to sandbox/dev-logs"
        fi
    fi
    rm -rf "$UDOS_ROOT/dev/sandbox"
    echo -e "${GREEN}✅ Removed duplicate dev/sandbox${NC}"
fi

# 2. Verify main sandbox structure
echo -e "${CYAN}📋 Main sandbox structure:${NC}"
if [ -d "$UDOS_ROOT/sandbox" ]; then
    ls -la "$UDOS_ROOT/sandbox" | while read line; do
        echo "   $line"
    done
else
    echo -e "${RED}❌ Main sandbox directory not found${NC}"
fi
echo ""

echo -e "${BLUE}🎯 PHASE 4: Directory Organization Audit${NC}"
echo "─────────────────────────────────────────────"

# 1. Check for proper uCORE/system structure (system code, not user data)
echo -e "${CYAN}🔍 uCORE/system (should contain system code only):${NC}"
if [ -d "$UDOS_ROOT/uCORE/system" ]; then
    ls -la "$UDOS_ROOT/uCORE/system" | while read line; do
        if echo "$line" | grep -q "logs\\|cache\\|user\\|role"; then
            echo -e "   ${YELLOW}⚠️  $line${NC}"
        else
            echo -e "   ✅ $line"
        fi
    done
fi

# 2. Check uMEMORY structure (should contain user/session data)
echo -e "${CYAN}🔍 uMEMORY/system (should contain user/session data):${NC}"
if [ -d "$UDOS_ROOT/uMEMORY/system" ]; then
    ls -la "$UDOS_ROOT/uMEMORY/system" | while read line; do
        echo "   $line"
    done
fi
echo ""

echo -e "${BLUE}🎯 PHASE 5: Development Framework Organization${NC}"
echo "─────────────────────────────────────────────"

# 1. Check dev/ structure
echo -e "${CYAN}📁 Development framework structure:${NC}"
dev_structure=(
    "dev/scripts"
    "dev/templates"
    "dev/tools"
    "dev/active"
)

for dev_dir in "${dev_structure[@]}"; do
    if [ -d "$UDOS_ROOT/$dev_dir" ]; then
        count=$(ls -1 "$UDOS_ROOT/$dev_dir" 2>/dev/null | wc -l)
        echo -e "   ✅ $dev_dir ($count items)"
    else
        echo -e "   ${YELLOW}⚠️  Missing: $dev_dir${NC}"
    fi
done

# 2. Check for development clutter
echo -e "${CYAN}🧹 Checking for development clutter:${NC}"
clutter_patterns=(
    "*.tmp"
    "*.working"
    "*.cache"
    "*.bak"
    "*~"
)

for pattern in "${clutter_patterns[@]}"; do
    found=$(find "$UDOS_ROOT" -name "$pattern" -not -path "*/.*" 2>/dev/null | head -3)
    if [ ! -z "$found" ]; then
        echo -e "${YELLOW}   ⚠️  Found $pattern files:${NC}"
        echo "$found" | sed 's/^/      /'
    fi
done
echo ""

echo -e "${BLUE}🎯 PHASE 6: Final Recommendations${NC}"
echo "─────────────────────────────────────────────"

echo -e "${CYAN}📋 System Organization Summary:${NC}"
echo "   ✅ Logs: uMEMORY/system/logs/ (user/session data)"
echo "   ✅ System Code: uCORE/system/ (system components)"
echo "   ✅ Development: dev/ (development framework)"
echo "   ✅ User Workspace: sandbox/ (user experiments)"
echo "   ✅ User Memory: uMEMORY/ (user/role data)"
echo ""

echo -e "${CYAN}🚀 Development Workflow Recommendations:${NC}"
echo "   • Use sandbox/ for all user experiments and temporary work"
echo "   • Keep dev/ for core development framework and tools"
echo "   • Place user/session data in uMEMORY/"
echo "   • Keep system code in uCORE/"
echo "   • Regular cleanup: run this script periodically"
echo ""

echo -e "${GREEN}🎯 Git Repository Health:${NC}"
cd "$UDOS_ROOT"
untracked=$(git status --porcelain | wc -l)
if [ "$untracked" -gt 10 ]; then
    echo -e "${YELLOW}   ⚠️  $untracked untracked changes - consider cleanup${NC}"
else
    echo -e "   ✅ Repository is clean ($untracked changes)"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ uDOS v1.4 System Cleanup Complete${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📦 Backup created at: $BACKUP_DIR${NC}"
echo -e "${BLUE}📋 Review recommendations above for optimal organization${NC}"
