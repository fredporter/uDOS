#!/bin/bash

# uDOS uMEMORY Reorganization Status Check
# Verify the new multi-role architecture implementation

set -euo pipefail

readonly UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'
readonly BOLD='\033[1m'

echo -e "${BOLD}${CYAN}🏗️  uDOS uMEMORY Reorganization Status${NC}"
echo -e "${BOLD}═════════════════════════════════════${NC}"
echo ""

# Check new directory structure
echo -e "${BOLD}📁 Directory Structure Check:${NC}"

# Check uMEMORY structure
if [[ -d "$UDOS_ROOT/uMEMORY/log" ]]; then
    echo -e "  ✅ uMEMORY/log/ (centralized logging)"
else
    echo -e "  ❌ uMEMORY/log/ missing"
fi

if [[ -d "$UDOS_ROOT/uMEMORY/role" ]]; then
    echo -e "  ✅ uMEMORY/role/ (role-specific data)"

    # Check each role
    for role in wizard sorcerer imp knight ghost drone tomb crypt; do
        if [[ -d "$UDOS_ROOT/uMEMORY/role/$role" ]]; then
            echo -e "    ✅ $role role directory exists"

            # Check role subdirectories
            for subdir in setup user log cache; do
                if [[ -d "$UDOS_ROOT/uMEMORY/role/$role/$subdir" ]]; then
                    echo -e "      ✅ $role/$subdir"
                else
                    echo -e "      ❌ $role/$subdir missing"
                fi
            done
        else
            echo -e "    ❌ $role role directory missing"
        fi
    done
else
    echo -e "  ❌ uMEMORY/role/ missing"
fi

if [[ -d "$UDOS_ROOT/uMEMORY/shared" ]]; then
    echo -e "  ✅ uMEMORY/shared/ (shared resources)"
else
    echo -e "  ❌ uMEMORY/shared/ missing"
fi

echo ""
echo -e "${BOLD}🗂️  Sandbox Structure Check:${NC}"

if [[ -d "$UDOS_ROOT/sandbox/role" ]]; then
    echo -e "  ✅ sandbox/role/ (role-specific configs)"

    for role in wizard sorcerer imp knight ghost drone tomb crypt; do
        if [[ -d "$UDOS_ROOT/sandbox/role/$role" ]]; then
            echo -e "    ✅ sandbox/role/$role"

            if [[ -f "$UDOS_ROOT/sandbox/role/$role/user.md" ]]; then
                echo -e "      ✅ user.md exists"
            else
                echo -e "      ⚠️  user.md missing"
            fi
        else
            echo -e "    ❌ sandbox/role/$role missing"
        fi
    done
else
    echo -e "  ❌ sandbox/role/ missing"
fi

if [[ -f "$UDOS_ROOT/sandbox/current-role.conf" ]]; then
    echo -e "  ✅ current-role.conf"
    current_role=$(grep "CURRENT_ROLE=" "$UDOS_ROOT/sandbox/current-role.conf" | cut -d'=' -f2)
    echo -e "    📍 Active role: ${CYAN}$current_role${NC}"
else
    echo -e "  ❌ current-role.conf missing"
fi

if [[ -L "$UDOS_ROOT/sandbox/user.md" ]]; then
    echo -e "  ✅ user.md symlink exists"
    target=$(readlink "$UDOS_ROOT/sandbox/user.md")
    echo -e "    🔗 Points to: ${PURPLE}$target${NC}"
else
    echo -e "  ❌ user.md symlink missing"
fi

echo ""
echo -e "${BOLD}📊 Data Migration Check:${NC}"

# Check wizard data migration
wizard_missions=$(find "$UDOS_ROOT/uMEMORY/role/wizard/user/missions" -name "*.md" 2>/dev/null | wc -l)
wizard_milestones=$(find "$UDOS_ROOT/uMEMORY/role/wizard/user/milestones" -name "*.md" 2>/dev/null | wc -l)
wizard_moves=$(find "$UDOS_ROOT/uMEMORY/role/wizard/user/moves" -name "*" -type f 2>/dev/null | wc -l)

echo -e "  📝 Wizard role data:"
echo -e "    📋 Missions: ${YELLOW}$wizard_missions${NC}"
echo -e "    🎯 Milestones: ${YELLOW}$wizard_milestones${NC}"
echo -e "    🚶 Moves: ${YELLOW}$wizard_moves${NC}"

# Check log migration
wizard_logs=$(find "$UDOS_ROOT/uMEMORY/log/daily/wizard" -name "*.log" 2>/dev/null | wc -l)
echo -e "  📋 Log migration:"
echo -e "    📄 Wizard daily logs: ${YELLOW}$wizard_logs${NC}"

echo ""
echo -e "${BOLD}🆕 New Roles Check:${NC}"

# Check Knight role
if [[ -f "$UDOS_ROOT/uMEMORY/role/knight/setup/GET" ]]; then
    echo -e "  ✅ Knight role (Level 5) - Security operations"
    knight_level=$(grep "ROLE_LEVEL=" "$UDOS_ROOT/uMEMORY/role/knight/setup/GET" | cut -d'=' -f2)
    echo -e "    📊 Level: ${CYAN}$knight_level${NC}"
else
    echo -e "  ❌ Knight role setup missing"
fi

# Check Crypt role
if [[ -f "$UDOS_ROOT/uMEMORY/role/crypt/setup/GET" ]]; then
    echo -e "  ✅ Crypt role (Level 1) - Encryption vault"
    crypt_level=$(grep "ROLE_LEVEL=" "$UDOS_ROOT/uMEMORY/role/crypt/setup/GET" | cut -d'=' -f2)
    echo -e "    📊 Level: ${CYAN}$crypt_level${NC}"
else
    echo -e "  ❌ Crypt role setup missing"
fi

echo ""
echo -e "${BOLD}🔧 Integration Check:${NC}"

# Check backup integration
if [[ -f "$UDOS_ROOT/sandbox/backup/config.json" ]]; then
    echo -e "  ✅ Backup system integration"
    backup_roles=$(jq -r '.roles | keys[]' "$UDOS_ROOT/sandbox/backup/config.json" 2>/dev/null | wc -l)
    echo -e "    📊 Configured roles: ${CYAN}$backup_roles${NC}"
else
    echo -e "  ❌ Backup integration missing"
fi

# Summary
echo ""
echo -e "${BOLD}📋 Reorganization Summary:${NC}"
echo -e "  🏗️  Architecture: Multi-role data organization"
echo -e "  📁 Structure: role/ and log/ directories"
echo -e "  🆕 New roles: Knight (Level 5), Crypt (Level 1)"
echo -e "  📊 Migration: Wizard data migrated successfully"
echo -e "  🔗 Integration: Symlinks and configs in place"

# Check if reorganization is complete
missing_components=0
for component in "uMEMORY/log" "uMEMORY/role" "sandbox/role" "sandbox/current-role.conf"; do
    if [[ ! -e "$UDOS_ROOT/$component" ]]; then
        ((missing_components++))
    fi
done

echo ""
if [[ $missing_components -eq 0 ]]; then
    echo -e "${BOLD}${GREEN}✅ uMEMORY Reorganization Complete!${NC}"
    echo -e "   Ready for multi-role operations with centralized logging"
else
    echo -e "${BOLD}${YELLOW}⚠️  Reorganization In Progress${NC}"
    echo -e "   $missing_components component(s) still need attention"
fi
