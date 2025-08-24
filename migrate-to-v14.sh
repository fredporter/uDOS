#!/bin/bash
# uDOS v1.4 Structure Migration Script
# Migrates current installation to clean role/user/backup isolation

set -euo pipefail

# Polaroid Colors — Foreground + Background (xterm-256 with ANSI fallback)
if [[ $TERM =~ 256color ]]; then
  # Foreground
  readonly RED='\033[38;5;203m'     # Orange Pop
  readonly GREEN='\033[38;5;154m'   # Lime Glow
  readonly YELLOW='\033[38;5;226m'  # Yellow Burst
  readonly BLUE='\033[38;5;33m'     # Cyan Flash
  readonly PURPLE='\033[38;5;198m'  # Magenta Snap
  readonly CYAN='\033[38;5;38m'     # Cyan Flash deeper
  readonly WHITE='\033[38;5;15m'    # Bright white
  readonly NC='\033[0m'

  # Background
  readonly BG_RED='\033[48;5;203m'
  readonly BG_GREEN='\033[48;5;154m'
  readonly BG_YELLOW='\033[48;5;226m'
  readonly BG_BLUE='\033[48;5;33m'
  readonly BG_PURPLE='\033[48;5;198m'
  readonly BG_CYAN='\033[48;5;38m'
  readonly BG_WHITE='\033[48;5;15m'
else
  # Classic ANSI fallback
  readonly RED='\033[0;31m'
  readonly GREEN='\033[1;32m'
  readonly YELLOW='\033[1;33m'
  readonly BLUE='\033[0;34m'
  readonly PURPLE='\033[0;35m'
  readonly CYAN='\033[0;36m'
  readonly WHITE='\033[1;37m'
  readonly NC='\033[0m'

  readonly BG_RED='\033[41m'
  readonly BG_GREEN='\033[42m'
  readonly BG_YELLOW='\033[43m'
  readonly BG_BLUE='\033[44m'
  readonly BG_PURPLE='\033[45m'
  readonly BG_CYAN='\033[46m'
  readonly BG_WHITE='\033[47m'
fi

# Configuration
readonly UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly BACKUP_PREFIX="migration-$(date +%Y%m%d-%H%M%S)"

# Migration state
DRY_RUN=false
BACKUP_EXISTING=true

show_banner() {
    clear
    echo -e "${CYAN}"
    echo "   ██╗   ██╗██████╗  ██████╗ ███████╗"
    echo "   ██║   ██║██╔══██╗██╔═══██╗██╔════╝"
    echo "   ██║   ██║██║  ██║██║   ██║███████╗"
    echo "   ██║   ██║██║  ██║██║   ██║╚════██║"
    echo "   ╚██████╔╝██████╔╝╚██████╔╝███████║"
    echo "    ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝"
    echo -e "${NC}"
    echo -e "${WHITE}uDOS v1.4 Structure Migration${NC}"
    echo -e "${CYAN}Role/User/Backup Isolation System${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

analyze_current_structure() {
    echo -e "${BLUE}🔍 Analyzing current structure...${NC}"
    echo ""

    # Check what needs to be migrated
    local user_data_found=false
    local role_data_found=false
    local backup_data_found=false

    # Check for user data in various locations
    if [[ -d "dev/notes" || -d "dev/briefings" || -f "dev/config.json" ]]; then
        echo -e "${YELLOW}📝 User development data found in dev/${NC}"
        user_data_found=true
    fi

    if [[ -d "sandbox/logs" || -d "sandbox/session" || -d "sandbox/workflow" ]]; then
        echo -e "${YELLOW}🧪 User sandbox data found in sandbox/${NC}"
        user_data_found=true
    fi

    if [[ -d "uMEMORY/user" || -d "uMEMORY/role" ]]; then
        echo -e "${YELLOW}💭 User memory data found in uMEMORY/${NC}"
        user_data_found=true
    fi

    # Check for scattered backups
    if [[ -d "backup" ]]; then
        echo -e "${YELLOW}💾 Backup directory found${NC}"
        backup_data_found=true
    fi

    # Check for role-specific installations
    if [[ -d "wizard" ]]; then
        echo -e "${YELLOW}🧙‍♂️ Wizard role data found${NC}"
        role_data_found=true
    fi

    echo ""

    if [[ "$user_data_found" == "true" || "$role_data_found" == "true" || "$backup_data_found" == "true" ]]; then
        echo -e "${GREEN}✅ Migration needed - data found to reorganize${NC}"
        return 0
    else
        echo -e "${GREEN}✅ Structure already clean - no migration needed${NC}"
        return 1
    fi
}

create_new_structure() {
    echo_header "🏗️  Creating v1.4 directory structure"
    
    # Create main directories under uMEMORY
    mkdir -p uMEMORY/role/wizard uMEMORY/role/sorcerer uMEMORY/role/imp uMEMORY/role/drone uMEMORY/role/tomb uMEMORY/role/ghost
    mkdir -p uMEMORY/user/dev uMEMORY/user/memory uMEMORY/user/sandbox uMEMORY/user/extensions
    mkdir -p BACKUP
    
    echo_success "✅ Directory structure created"
}

migrate_user_data() {
    echo_header "👤 Migrating user data"
    
    # Migrate user development files
    if [ -d "dev" ]; then
        echo_info "� Moving dev/ to uMEMORY/user/dev/"
        cp -r dev/* uMEMORY/user/dev/ 2>/dev/null || true
    fi
    
    # Migrate user sandbox
    if [ -d "sandbox" ]; then
        echo_info "🏖️  Moving sandbox/ to uMEMORY/user/sandbox/"
        cp -r sandbox/* uMEMORY/user/sandbox/ 2>/dev/null || true
    fi
    
    # Migrate user extensions
    if [ -d "USER/extensions" ]; then
        echo_info "� Moving USER/extensions/ to uMEMORY/user/extensions/"
        cp -r USER/extensions/* uMEMORY/user/extensions/ 2>/dev/null || true
    fi
    
    # Migrate user memory files
    find . -name "*user*" -o -name "*session*" -o -name "*memory*" | grep -v uMEMORY | while read file; do
        if [ -f "$file" ]; then
            echo_info "🧠 Moving memory file: $(basename "$file")"
            cp "$file" uMEMORY/user/memory/ 2>/dev/null || true
        fi
    done
    
    echo_success "✅ User data migration complete"
}

migrate_role_data() {
    echo_header "🎭 Migrating role data"
    
    # Migrate wizard data
    if [ -d "wizard" ]; then
        echo_info "🧙 Moving wizard/ to uMEMORY/role/wizard/"
        cp -r wizard/* uMEMORY/role/wizard/ 2>/dev/null || true
    fi
    
    # Migrate other role directories if they exist
    for role in sorcerer imp drone tomb ghost; do
        if [ -d "$role" ]; then
            echo_info "🎭 Moving $role/ to uMEMORY/role/$role/"
            cp -r "$role"/* "uMEMORY/role/$role/" 2>/dev/null || true
        fi
    done
    
    echo_success "✅ Role data migration complete"
}

migrate_backup_data() {
    echo -e "${BLUE}💾 Migrating backup data...${NC}"

    # Migrate main backup directory
    if [[ -d "backup" ]]; then
        echo "  📦 Moving backup/ → BACKUP/"
        [[ "$DRY_RUN" == "false" ]] && {
            cp -r backup/* BACKUP/system/ 2>/dev/null || true

            # Organize backups by type
            find BACKUP/system -name "*migration*" -exec mv {} BACKUP/migrations/ \; 2>/dev/null || true
            find BACKUP/system -name "*user*" -exec mv {} BACKUP/user-data/ \; 2>/dev/null || true
            find BACKUP/system -name "*role*" -exec mv {} BACKUP/role-configs/ \; 2>/dev/null || true
        }
    fi

    # Find and migrate scattered .backup files
    if [[ "$DRY_RUN" == "false" ]]; then
        find . -name "*.backup" -type f 2>/dev/null | while read -r backup_file; do
            echo "  🔍 Moving scattered backup: $backup_file → BACKUP/system/"
            mv "$backup_file" BACKUP/system/ 2>/dev/null || true
        done
    fi

    echo -e "${GREEN}✅ Backup data migration complete${NC}"
}

update_gitignore() {
    echo -e "${BLUE}📝 Updating .gitignore for new structure...${NC}"

    cat > .gitignore << 'EOF'
# ══════════════════════════════════════════════════
# uDOS v1.4 Clean Distribution .gitignore
# Role/User/Backup Isolation System
# ══════════════════════════════════════════════════

# ════════════════════════════════════════════════════════════════
# 🎯 uDOS DISTRIBUTION STRATEGY v1.4
# ════════════════════════════════════════════════════════════════
# ✅ Keep: Core system, role installers, shared frameworks
# 🚫 Exclude: User data, role installations, backup files
# 🔄 Sync: Only distribution components, no personal content

# ════════════════════════════════════════════════════════════════
# 🔒 COMPLETE LOCAL-ONLY EXCLUSIONS
# ════════════════════════════════════════════════════════════════

# Role installations (local only after install)
/ROLE/

# User data isolation (local only)
/USER/

# Centralized backup system (local only)
/BACKUP/

# ════════════════════════════════════════════════════════════════
# 🛠️ DEVELOPMENT FRAMEWORK EXCLUSIONS
# ════════════════════════════════════════════════════════════════

# Keep core dev tools, exclude user dev data
dev/USER/
dev/**/*.user.*
dev/**/*.personal.*
dev/**/*.working
dev/**/*.tmp

# Keep core sandbox framework, exclude user sandbox data
sandbox/USER/
sandbox/**/*.user.*
sandbox/**/*.personal.*
sandbox/**/*.working
sandbox/**/*.tmp

# ════════════════════════════════════════════════════════════════
# 🏗️ SYSTEM COMPONENT EXCLUSIONS
# ════════════════════════════════════════════════════════════════

# uMEMORY: Keep system templates, exclude user/role data
uMEMORY/user/
uMEMORY/role/
uMEMORY/**/*.user.*
uMEMORY/**/*.personal.*

# Wizard: Keep distribution notes/tools, exclude user sessions
wizard/USER/
wizard/**/*.user.*
wizard/**/*.personal.*
wizard/**/*.session.*

# ════════════════════════════════════════════════════════════════
# 🚫 STANDARD EXCLUSIONS
# ════════════════════════════════════════════════════════════════

# Logs and temporary files
**/*.log
**/*.tmp
**/*.working
**/*.cache
**/*.temp

# System files
.DS_Store
**/.DS_Store
node_modules/
__pycache__/
*.pyc

# Build artifacts
dist/
build/
out/
*.dmg
*.zip
*.tar.gz

# Personal configurations
.env
.env.local
*.user.*
*.personal.*
personal-*
user-*

# IDE configurations
.vscode/settings.json
.vscode/launch.json
.idea/

# ════════════════════════════════════════════════════════════════
# ✅ uDOS v1.4 DISTRIBUTION INCLUDES
# ════════════════════════════════════════════════════════════════
# ✅ uCORE/ - Core system with role installers
# ✅ dev/ - Development framework (core tools only)
# ✅ sandbox/ - Sandbox framework (core templates only)
# ✅ docs/ - Complete documentation
# ✅ shared/ - Shared resources and templates
# ✅ extensions/ - Core extensions
# ✅ wizard/ - Distribution notes and tools
# ✅ install.sh - Main installer
# ✅ README.md, LICENSE, documentation files

# ════════════════════════════════════════════════════════════════
# 🚫 uDOS v1.4 DISTRIBUTION EXCLUDES
# ════════════════════════════════════════════════════════════════
# 🚫 ROLE/ - All role installations (installed locally)
# 🚫 USER/ - All user data (personal content)
# 🚫 BACKUP/ - All backup files (local backup system)
# 🚫 Personal configurations and session data
# 🚫 Build artifacts and temporary files
# ════════════════════════════════════════════════════════════════
EOF

    echo -e "${GREEN}✅ .gitignore updated for v1.4 structure${NC}"
}

cleanup_empty_directories() {
    echo -e "${BLUE}🧹 Cleaning up empty directories...${NC}"

    if [[ "$DRY_RUN" == "false" ]]; then
        # Remove empty directories from old structure
        find dev sandbox uMEMORY -type d -empty -delete 2>/dev/null || true

        # Remove old backup directory if empty
        [[ -d "backup" ]] && rmdir backup 2>/dev/null || true
    fi

    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

show_migration_summary() {
    echo ""
    echo -e "${GREEN}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 uDOS v1.4 Migration Complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${NC}"

    echo -e "${WHITE}New Structure:${NC}"
    echo -e "  ${CYAN}📁 ROLE/${NC} - Role-specific installations & data"
    echo -e "  ${CYAN}👤 USER/${NC} - Personal user data & configurations"
    echo -e "  ${CYAN}💾 BACKUP/${NC} - Centralized backup system"
    echo ""

    echo -e "${WHITE}Distribution Clean:${NC}"
    echo -e "  ${GREEN}✅${NC} Core system preserved"
    echo -e "  ${GREEN}✅${NC} User data isolated"
    echo -e "  ${GREEN}✅${NC} Role data organized"
    echo -e "  ${GREEN}✅${NC} Backups centralized"
    echo -e "  ${GREEN}✅${NC} .gitignore updated"
    echo ""

    echo -e "${WHITE}Next Steps:${NC}"
    echo "1. Test that core functionality still works"
    echo "2. Commit the new structure to git"
    echo "3. Create clean distribution branch"
    echo "4. Update documentation"
    echo ""

    echo -e "${CYAN}💡 All personal data preserved in USER/ and ROLE/ folders${NC}"
    echo -e "${YELLOW}⚠️  Test thoroughly before pushing to GitHub!${NC}"
    echo ""
}

main() {
    show_banner

    # Parse command line arguments
    case "${1:-}" in
        --dry-run)
            DRY_RUN=true
            echo -e "${YELLOW}🔍 DRY RUN MODE - No files will be moved${NC}"
            echo ""
            ;;
        --help|-h)
            echo "uDOS v1.4 Structure Migration Script"
            echo ""
            echo "Usage: $0 [--dry-run] [--help]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Show what would be done without making changes"
            echo "  --help       Show this help message"
            echo ""
            echo "This script migrates your current uDOS installation to the new"
            echo "v1.4 structure with proper role/user/backup isolation."
            exit 0
            ;;
    esac

    # Check if migration is needed
    if ! analyze_current_structure; then
        echo -e "${GREEN}✨ Your installation is already using the v1.4 structure!${NC}"
        exit 0
    fi

    echo ""
    echo -e "${YELLOW}🚨 This will reorganize your uDOS installation${NC}"
    echo -e "${WHITE}Changes:${NC}"
    echo "  • Move user data to USER/ folder"
    echo "  • Move role data to ROLE/ folder"
    echo "  • Move backups to BACKUP/ folder"
    echo "  • Update .gitignore for clean distribution"
    echo ""

    if [[ "$DRY_RUN" == "false" ]]; then
        read -p "Continue with migration? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Migration cancelled${NC}"
            exit 0
        fi
    fi

    echo ""

    # Perform migration
    create_new_structure
    migrate_user_data
    migrate_role_data
    migrate_backup_data
    update_gitignore
    cleanup_empty_directories
    show_migration_summary
}

# Change to uDOS root directory
cd "$UDOS_ROOT"

# Run main function
main "$@"
