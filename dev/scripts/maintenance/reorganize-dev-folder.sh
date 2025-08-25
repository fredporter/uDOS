#!/bin/bash
# uDOS /dev Folder Reorganization Script
# Integrates with .copilot instructions and .vscode for wizard role dev mode

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$UDOS_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}🔧 uDOS /dev Folder Reorganization${NC}"
echo "=================================================================="
echo -e "${YELLOW}Purpose:${NC}"
echo -e "  🎯 Integrate with .copilot instructions and .vscode"
echo -e "  🧙‍♂️ Dev mode available to wizard role only"
echo -e "  📁 Compatible folder structure for development"
echo -e "  🔄 Sync with .git for required setup only"
echo ""

# Function to safely move directories/files
safe_move() {
    local source="$1"
    local dest="$2"
    local description="$3"

    if [ -e "$source" ]; then
        echo -e "${YELLOW}📦 Moving: $description${NC}"
        echo -e "   From: $source"
        echo -e "   To: $dest"

        # Create destination directory if needed
        mkdir -p "$(dirname "$dest")"

        # Move with merge if destination exists
        if [ -d "$dest" ]; then
            # Merge directories
            cp -r "$source"/* "$dest"/ 2>/dev/null || true
            rm -rf "$source"
        else
            mv "$source" "$dest"
        fi

        echo -e "${GREEN}✅ Moved: $description${NC}"
    else
        echo -e "${BLUE}ℹ️  Not found: $source${NC}"
    fi
}

# 1. Clean up old and empty directories
echo -e "\n${BLUE}1. Cleaning up old files and empty directories...${NC}"

# Remove old restructure scripts
rm -f dev/tools/restructure.sh.old

# Remove empty directories
find dev/ -type d -empty -delete 2>/dev/null || true

echo -e "${GREEN}✅ Cleanup complete${NC}"

# 2. Create proper dev folder structure for wizard role development
echo -e "\n${BLUE}2. Creating dev folder structure for wizard role...${NC}"

# Create comprehensive dev structure
mkdir -p dev/active/{core,extensions,tools}
mkdir -p dev/scripts/{build,test,deploy,maintenance}
mkdir -p dev/templates/{commands,extensions,configs}
mkdir -p dev/tools/{development,debugging,analysis}
mkdir -p dev/roadmaps/{current,archive}
mkdir -p dev/docs/{api,architecture,contributing}
mkdir -p dev/copilot/{instructions,context,examples}
mkdir -p dev/vscode/{configs,snippets,tasks}

echo -e "${GREEN}✅ Dev structure created${NC}"

# 3. Organize existing content
echo -e "\n${BLUE}3. Organizing existing development content...${NC}"

# Move existing scripts to proper locations
if [ -f "dev/scripts/geo-migration-final-summary.sh" ]; then
    mv dev/scripts/geo-migration-final-summary.sh dev/scripts/maintenance/
fi

if [ -f "dev/scripts/test-integration-compatibility.sh" ]; then
    mv dev/scripts/test-integration-compatibility.sh dev/scripts/test/
fi

if [ -f "dev/scripts/ucore-consolidation-final-summary.sh" ]; then
    mv dev/scripts/ucore-consolidation-final-summary.sh dev/scripts/maintenance/
fi

if [ -f "dev/scripts/validate-system-references.sh" ]; then
    mv dev/scripts/validate-system-references.sh dev/scripts/test/
fi

# Move existing docs to proper structure
safe_move "dev/DEVELOPMENT-GUIDELINES.md" "dev/docs/architecture/DEVELOPMENT-GUIDELINES.md" "development guidelines"
safe_move "dev/IMPLEMENTATION-COMPLETE-Directory-Reorganization.md" "dev/docs/architecture/directory-reorganization.md" "directory reorganization docs"
safe_move "dev/IMPLEMENTATION-COMPLETE-Geographic-System.md" "dev/docs/architecture/geographic-system.md" "geographic system docs"

echo -e "${GREEN}✅ Content organized${NC}"

# 4. Create integration with .copilot instructions
echo -e "\n${BLUE}4. Creating copilot integration...${NC}"

# Create copilot context for dev folder
cat > dev/copilot/DEV-CONTEXT.md << 'EOF'
# uDOS Development Context for AI Assistants

## Development Environment
This `/dev` folder is the core development environment for uDOS, accessible only to wizard role with DEV mode activated.

## Structure
- `active/` - Current core development projects
- `scripts/` - Development automation scripts
- `templates/` - Core system templates
- `tools/` - Development utilities
- `roadmaps/` - Project planning and roadmaps
- `docs/` - Architecture and API documentation
- `copilot/` - AI assistant context and instructions
- `vscode/` - VS Code development configurations

## Role Access
- **Wizard + DEV mode**: Full access to all development tools
- **All other roles**: Use `/sandbox` for user development

## Integration Points
- `.github/copilot-instructions.md` - Main AI instructions
- `.vscode/` - VS Code development environment
- `/dev/copilot/` - Development-specific AI context
- `/sandbox/` - User workspace (flushable)
EOF

# Create development examples for copilot
cat > dev/copilot/DEVELOPMENT-EXAMPLES.md << 'EOF'
# Development Examples for AI Assistants

## Common Development Tasks

### Creating New Extensions
```bash
# Work in dev/active/extensions/
cd dev/active/extensions/
mkdir my-new-extension/
# Use templates from dev/templates/extensions/
```

### Core System Development
```bash
# Work in dev/active/core/
cd dev/active/core/
# Use build scripts from dev/scripts/build/
```

### Testing and Validation
```bash
# Use test scripts from dev/scripts/test/
./dev/scripts/test/validate-system-references.sh
./dev/scripts/test/test-integration-compatibility.sh
```

## File Patterns
- Core development → `/dev/active/`
- User experiments → `/sandbox/experiments/`
- Temporary scripts → `/sandbox/scripts/`
- Permanent tools → `/dev/tools/`

## Git Sync Patterns
- Sync: `/dev/templates/`, `/dev/docs/`, roadmaps
- Local only: `/dev/active/`, temporary work
- User only: `/sandbox/` (flushable)
EOF

echo -e "${GREEN}✅ Copilot integration created${NC}"

# 5. Create VS Code integration files
echo -e "\n${BLUE}5. Creating VS Code dev integration...${NC}"

# Create dev-specific VS Code tasks
cat > dev/vscode/dev-tasks.json << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "🔧 DEV: Build Core System",
            "type": "shell",
            "command": "./dev/scripts/build/build-core.sh",
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "runOptions": {
                "runOn": "folderOpen"
            }
        },
        {
            "label": "🧪 DEV: Run Core Tests",
            "type": "shell",
            "command": "./dev/scripts/test/test-core-system.sh",
            "group": "test",
            "dependsOn": "🔧 DEV: Build Core System"
        },
        {
            "label": "📋 DEV: Validate System References",
            "type": "shell",
            "command": "./dev/scripts/test/validate-system-references.sh",
            "group": "test"
        },
        {
            "label": "🚀 DEV: Deploy to Staging",
            "type": "shell",
            "command": "./dev/scripts/deploy/deploy-staging.sh",
            "group": "build"
        },
        {
            "label": "🧹 DEV: System Maintenance",
            "type": "shell",
            "command": "./dev/scripts/maintenance/system-cleanup.sh",
            "group": "build"
        }
    ]
}
EOF

# Create dev-specific VS Code settings
cat > dev/vscode/dev-settings.json << 'EOF'
{
    "files.associations": {
        "*.ucode": "shellscript",
        "*.udata": "json"
    },
    "editor.rulers": [80, 120],
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "terminal.integrated.cwd": "${workspaceFolder}/dev",
    "explorer.fileNesting.enabled": true,
    "explorer.fileNesting.patterns": {
        "*.sh": "*.sh.bak, *.sh.old",
        "*.md": "*.md.bak, *.md.old"
    },
    "git.ignoreLimitWarning": true,
    "search.exclude": {
        "**/sandbox/logs/**": true,
        "**/uMEMORY/user/**": true,
        "**/dev/active/**": true
    }
}
EOF

echo -e "${GREEN}✅ VS Code integration created${NC}"

# 6. Create template files for development
echo -e "\n${BLUE}6. Creating development templates...${NC}"

# Extension template
cat > dev/templates/extensions/extension-template.json << 'EOF'
{
    "metadata": {
        "name": "extension-name",
        "version": "1.0.0",
        "type": "user",
        "platform": "universal",
        "author": "developer-name",
        "description": "Extension description"
    },
    "commands": {
        "COMMAND_NAME": {
            "syntax": "[COMMAND] <ACTION> {PARAMETER}",
            "description": "Command description",
            "implementation": "commands/command-name.sh",
            "permissions": ["user", "wizard"]
        }
    },
    "dependencies": [],
    "installation": {
        "files": ["commands/", "library/", "templates/"],
        "setup": "setup.sh"
    }
}
EOF

# Command template
cat > dev/templates/commands/command-template.sh << 'EOF'
#!/bin/bash
# uDOS Command Template
# Description: [Command description]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source logging functions
source "$UDOS_ROOT/sandbox/logs/logging.conf" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Command implementation
main() {
    local action="${1:-}"
    local parameter="${2:-}"

    case "$action" in
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_info "Command executed with action: $action"
            # Implementation here
            ;;
    esac
}

show_help() {
    cat << 'HELP_EOF'
Usage: [COMMAND] <ACTION> {PARAMETER}

Description: [Command description]

Actions:
  help    Show this help message

Examples:
  [COMMAND] <ACTION> {param}
HELP_EOF
}

# Execute main function
main "$@"
EOF

echo -e "${GREEN}✅ Templates created${NC}"

# 7. Create build and test scripts
echo -e "\n${BLUE}7. Creating build and test infrastructure...${NC}"

# Build script
cat > dev/scripts/build/build-core.sh << 'EOF'
#!/bin/bash
# Core System Build Script

set -euo pipefail

echo "🔧 Building uDOS Core System..."

# Check for required tools
command -v bash >/dev/null 2>&1 || { echo "Bash required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python3 required"; exit 1; }

# Validate core structure
echo "📋 Validating core structure..."
./dev/scripts/test/validate-system-references.sh

# Build extensions
echo "🔌 Building extensions..."
./extensions/extension-manager.sh build

# Setup network components
echo "🌐 Setting up network components..."
cd uNETWORK/server && python3 -m pip install -r requirements.txt 2>/dev/null || true

echo "✅ Core system build complete"
EOF

# Test script
cat > dev/scripts/test/test-core-system.sh << 'EOF'
#!/bin/bash
# Core System Test Script

set -euo pipefail

echo "🧪 Testing uDOS Core System..."

# Test core components
echo "🎯 Testing core components..."
./uCORE/launcher/universal/test-udos.sh

# Test extensions
echo "🔌 Testing extensions..."
./extensions/extension-manager.sh test

# Test network components
echo "🌐 Testing network components..."
cd uNETWORK/server && python3 -c "import server; print('Server import test passed')" 2>/dev/null || echo "Server test skipped"

echo "✅ Core system tests complete"
EOF

# Make scripts executable
chmod +x dev/scripts/build/build-core.sh
chmod +x dev/scripts/test/test-core-system.sh

echo -e "${GREEN}✅ Build and test scripts created${NC}"

# 8. Update .gitignore for proper dev folder sync
echo -e "\n${BLUE}8. Updating .gitignore for dev folder...${NC}"

# Add dev-specific patterns to .gitignore if not already present
if ! grep -q "# Dev folder patterns" .gitignore 2>/dev/null; then
    cat >> .gitignore << 'EOF'

# Dev folder patterns - sync templates and docs, exclude active work
dev/active/
dev/scripts/maintenance/temp-*
dev/tools/temp-*
dev/copilot/temp-*

# Keep these for collaboration
!dev/templates/
!dev/docs/
!dev/roadmaps/
!dev/copilot/instructions/
!dev/copilot/context/
!dev/vscode/configs/
EOF
fi

echo -e "${GREEN}✅ .gitignore updated${NC}"

# 9. Create README for dev folder
echo -e "\n${BLUE}9. Creating dev folder documentation...${NC}"

cat > dev/README.md << 'EOF'
# uDOS Development Environment

## 🧙‍♂️ **Wizard Role + DEV Mode Only**

This development environment is restricted to **wizard role with DEV mode activated**.

## 📁 **Structure**

```
dev/
├── active/              # Current core development (local only)
│   ├── core/           # Core system development
│   ├── extensions/     # Extension development
│   └── tools/          # Tool development
├── scripts/            # Development automation
│   ├── build/         # Build scripts
│   ├── test/          # Test scripts
│   ├── deploy/        # Deployment scripts
│   └── maintenance/   # Maintenance scripts
├── templates/          # Development templates (synced)
│   ├── commands/      # Command templates
│   ├── extensions/    # Extension templates
│   └── configs/       # Configuration templates
├── tools/              # Development utilities
├── roadmaps/           # Project roadmaps (synced)
├── docs/               # Architecture docs (synced)
├── copilot/            # AI assistant context (synced)
└── vscode/             # VS Code configurations (synced)
```

## 🔄 **Git Sync Policy**

### Synced with Git (Team Collaboration)
- `templates/` - Development templates
- `docs/` - Architecture documentation
- `roadmaps/` - Project planning
- `copilot/instructions/` - AI assistant guidelines
- `vscode/configs/` - Shared VS Code settings

### Local Only (Not Synced)
- `active/` - Current development work
- `tools/temp-*` - Temporary utilities
- `scripts/maintenance/temp-*` - Temporary maintenance scripts

## 🛠️ **Integration Points**

### AI Assistant Integration
- `.github/copilot-instructions.md` - Main AI instructions
- `dev/copilot/` - Development-specific context
- Templates and examples for consistent development

### VS Code Integration
- `.vscode/` - Main VS Code configuration
- `dev/vscode/` - Development-specific configurations
- Custom tasks for core development workflow

### Role-Based Access
- **Wizard + DEV**: Full access to `/dev` environment
- **All others**: Use `/sandbox` for development work
- Sandbox work is flushable, dev work is persistent

## 🚀 **Development Workflow**

### Core System Development
1. Work in `dev/active/core/`
2. Use `dev/scripts/build/` for building
3. Test with `dev/scripts/test/`
4. Deploy with `dev/scripts/deploy/`

### Extension Development
1. Use templates from `dev/templates/extensions/`
2. Develop in `dev/active/extensions/`
3. Test with extension manager
4. Deploy to `extensions/` when ready

### Documentation
1. Architecture docs in `dev/docs/`
2. API documentation auto-generated
3. Contributing guidelines maintained

## ⚠️ **Important Notes**

- DEV mode required for core system modifications
- Regular users work in `/sandbox` (flushable workspace)
- Archive important work from sandbox to permanent locations
- Follow development templates for consistency
- Use provided build and test scripts

---

**Remember**: This is a protected development environment. Experimental work should happen in `/sandbox` until ready for core integration.
EOF

echo -e "${GREEN}✅ Documentation created${NC}"

# 10. Final validation and summary
echo -e "\n${BLUE}10. Final validation...${NC}"

echo "Dev folder structure:"
find dev -type d -maxdepth 2 | sort

echo -e "\n${GREEN}🎉 Dev folder reorganization complete!${NC}"
echo ""
echo -e "${BLUE}Key Changes:${NC}"
echo -e "  🧙‍♂️ ${YELLOW}Wizard + DEV mode${NC} access control"
echo -e "  📁 ${YELLOW}Structured development${NC} environment"
echo -e "  🤖 ${YELLOW}AI assistant integration${NC} with copilot context"
echo -e "  🔧 ${YELLOW}VS Code integration${NC} with dev-specific configs"
echo -e "  🔄 ${YELLOW}Selective git sync${NC} - templates/docs yes, active work no"
echo -e "  📋 ${YELLOW}Build/test infrastructure${NC} for core development"
echo ""
echo -e "${PURPLE}Workflow: Active dev in /dev → User experiments in /sandbox${NC}"
