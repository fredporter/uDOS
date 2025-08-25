#!/bin/bash
# uDOS Memory/Sandbox Reorganization Script
# Moves all logging to sandbox, keeps uMEMORY for data only

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

echo -e "${BLUE}🔄 uDOS Memory/Sandbox Reorganization${NC}"
echo "=================================================================="
echo -e "${YELLOW}Philosophy:${NC}"
echo -e "  📁 uMEMORY = User and system data files only"
echo -e "  🛠️  sandbox = Active workspace, logging, processing, temp scripts"
echo -e "  🔄 sandbox = Where you collate/edit/process before filing in uMEMORY"
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

# 1. Move ALL logging from uMEMORY to sandbox
echo -e "\n${BLUE}1. Moving all logging to sandbox...${NC}"

# Create sandbox logging structure
mkdir -p sandbox/logs/{system,user,network,errors,debug,crashes,runtime}

# Move all log directories from uMEMORY to sandbox
if [ -d "uMEMORY/logs" ]; then
    echo -e "${YELLOW}📋 Moving all uMEMORY logs to sandbox...${NC}"

    # Move each log category
    safe_move "uMEMORY/logs/crashes" "sandbox/logs/crashes" "crash logs"
    safe_move "uMEMORY/logs/debug" "sandbox/logs/debug" "debug logs"
    safe_move "uMEMORY/logs/errors" "sandbox/logs/errors" "error logs"
    safe_move "uMEMORY/logs/network" "sandbox/logs/network" "network logs"
    safe_move "uMEMORY/logs/uMEMORY-role-wizard-logs" "sandbox/logs/user/wizard" "wizard role logs"
    safe_move "uMEMORY/logs/uMEMORY-user-sandbox-logs" "sandbox/logs/user/sandbox" "user sandbox logs"
    safe_move "uMEMORY/logs/uNETWORK-wizard-logs" "sandbox/logs/network/wizard" "network wizard logs"
    safe_move "uMEMORY/logs/uSCRIPT-runtime-logs" "sandbox/logs/runtime" "script runtime logs"

    # Remove the now-empty logs directory
    rmdir "uMEMORY/logs" 2>/dev/null || rm -rf "uMEMORY/logs"

    echo -e "${GREEN}✅ All logging moved to sandbox${NC}"
fi

# 2. Create proper sandbox workspace structure
echo -e "\n${BLUE}2. Setting up sandbox workspace structure...${NC}"

# Create comprehensive sandbox structure for active work
mkdir -p sandbox/logs/{system,user,network,errors,debug,crashes,runtime}
mkdir -p sandbox/sessions/{current,archive}
mkdir -p sandbox/scripts/{temp,utils,dev}
mkdir -p sandbox/documents/{drafts,processing,ready}
mkdir -p sandbox/data/{incoming,processing,staging}
mkdir -p sandbox/tasks/{active,completed}
mkdir -p sandbox/experiments
mkdir -p sandbox/backup

# Create workspace README files
cat > sandbox/sessions/README.md << 'EOF'
# Sandbox Sessions

Active session work and session archives.

## Structure
- `current/` - Current active session data
- `archive/` - Completed session archives

All session work happens here before being filed in uMEMORY.
EOF

cat > sandbox/scripts/README.md << 'EOF'
# Sandbox Scripts

Temporary scripts, utilities, and development work.

## Structure
- `temp/` - Temporary scripts and one-off utilities
- `utils/` - Reusable utility scripts
- `dev/` - Development and experimental scripts

All script development happens here before moving to permanent locations.
EOF

cat > sandbox/documents/README.md << 'EOF'
# Sandbox Documents

Document processing workspace.

## Structure
- `drafts/` - Working document drafts
- `processing/` - Documents being edited/collated
- `ready/` - Documents ready to file in uMEMORY

Documents flow: drafts → processing → ready → uMEMORY
EOF

cat > sandbox/data/README.md << 'EOF'
# Sandbox Data Processing

Data collation and processing workspace.

## Structure
- `incoming/` - New data to be processed
- `processing/` - Data being collated/cleaned
- `staging/` - Data ready for uMEMORY filing

Data flow: incoming → processing → staging → uMEMORY
EOF

echo -e "${GREEN}✅ Sandbox workspace structure created${NC}"

# 3. Clean up uMEMORY to be data-only
echo -e "\n${BLUE}3. Cleaning uMEMORY to be data-only...${NC}"

# Remove any development artifacts from uMEMORY
find uMEMORY -name "*.tmp" -delete 2>/dev/null || true
find uMEMORY -name "*.working" -delete 2>/dev/null || true
find uMEMORY -name "*.dev" -delete 2>/dev/null || true

# Update uMEMORY README to reflect new purpose
cat > uMEMORY/README.md << 'EOF'
# uMEMORY - Universal Memory Archive

Persistent storage for user and system data files.

## Philosophy
uMEMORY is a **data archive only** - no active work, no scripts, no development.
All active work happens in `/sandbox` before being filed here.

## Structure
- `user/` - User-specific data archives
- `role/` - Role-specific configurations and data
- `system/` - System configuration and reference data
- `core/` - Core system memory components
- `templates/` - Data templates and formats

## Workflow
1. **Active work** → happens in `/sandbox`
2. **Processing** → collate/edit/organize in `/sandbox`
3. **Filing** → move completed data to `/uMEMORY`

uMEMORY is the "filing cabinet" - sandbox is the "desk".
EOF

echo -e "${GREEN}✅ uMEMORY cleaned and documentation updated${NC}"

# 4. Update system references to new logging location
echo -e "\n${BLUE}4. Updating system references...${NC}"

# Create a reference file for the new structure
cat > sandbox/STRUCTURE.md << 'EOF'
# uDOS Sandbox Structure v1.4

## Purpose
Sandbox is the active workspace for all uDOS activities:
- Session work and logging
- Document processing
- Data collation
- Script development
- Temporary files

## Directory Structure

### Logging (All logs go here)
```
sandbox/logs/
├── system/          # System logs
├── user/           # User activity logs
├── network/        # Network and server logs
├── errors/         # Error logs
├── debug/          # Debug information
├── crashes/        # Crash reports
└── runtime/        # Runtime logs
```

### Active Workspace
```
sandbox/
├── sessions/       # Session management
├── scripts/        # Temporary and development scripts
├── documents/      # Document processing workspace
├── data/          # Data processing workspace
├── tasks/         # Task management
├── experiments/   # Experimentation area
└── backup/        # Local backups
```

## Workflow
1. **Work** in sandbox (logging, scripting, processing)
2. **Organize** useful results in sandbox
3. **File** completed data in uMEMORY when ready

Sandbox is flushable - uMEMORY is permanent.
EOF

echo -e "${GREEN}✅ Structure documentation created${NC}"

# 5. Set up logging redirection
echo -e "\n${BLUE}5. Creating logging configuration...${NC}"

# Create logging configuration that points to sandbox
cat > sandbox/logs/logging.conf << 'EOF'
# uDOS Logging Configuration
# All logging redirected to sandbox

[LOGGING]
LOG_ROOT="sandbox/logs"
SYSTEM_LOGS="sandbox/logs/system"
USER_LOGS="sandbox/logs/user"
NETWORK_LOGS="sandbox/logs/network"
ERROR_LOGS="sandbox/logs/errors"
DEBUG_LOGS="sandbox/logs/debug"
CRASH_LOGS="sandbox/logs/crashes"
RUNTIME_LOGS="sandbox/logs/runtime"

[PHILOSOPHY]
# All active logging happens in sandbox
# uMEMORY is for data archival only
# Logs can be processed and archived from sandbox to uMEMORY when needed
EOF

echo -e "${GREEN}✅ Logging configuration created${NC}"

# 6. Final validation
echo -e "\n${BLUE}6. Final validation...${NC}"

echo "uMEMORY structure (data only):"
find uMEMORY -type d -maxdepth 2 | sort

echo -e "\nSandbox structure (active workspace):"
find sandbox -type d -maxdepth 2 | sort

echo -e "\n${GREEN}🎉 Memory/Sandbox reorganization complete!${NC}"
echo ""
echo -e "${BLUE}New Philosophy:${NC}"
echo -e "  📁 ${YELLOW}uMEMORY${NC} = Permanent data archive (filing cabinet)"
echo -e "  🛠️  ${YELLOW}sandbox${NC} = Active workspace (desk)"
echo -e "  📋 ${YELLOW}All logging${NC} → sandbox/logs/"
echo -e "  📝 ${YELLOW}All scripts${NC} → sandbox/scripts/"
echo -e "  📄 ${YELLOW}All processing${NC} → sandbox/"
echo ""
echo -e "${PURPLE}Workflow: Work in sandbox → Process in sandbox → File in uMEMORY${NC}"
