#!/usr/bin/env bash
# [20-80-01] uDOS Memory Structure Compliance Script
# Location: uCORE/scripts/memory-compliance.sh
# Purpose: Migrate uMEMORY to proper private structure with user levels

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 uDOS Memory Structure Compliance${NC}"
echo "======================================"

# Check current state
echo -e "\n${YELLOW}📋 Checking Current Memory Structure...${NC}"

if [[ -d "$UDOS_ROOT/uMEMORY" ]]; then
    echo -e "${YELLOW}⚠️  uMEMORY found in repository (should be private)${NC}"
    IN_REPO=true
else
    echo -e "${GREEN}✅ uMEMORY not in repository${NC}"
    IN_REPO=false
fi

# Create proper private uMEMORY structure
PRIVATE_MEMORY="$HOME/.uDOS/uMEMORY"
echo -e "\n${YELLOW}🏗️  Creating Private uMEMORY Structure...${NC}"

# Create the private directory structure according to memory-structure.md
mkdir -p "$PRIVATE_MEMORY"/{user,sandbox,state,logs,missions,moves,milestones,scripts,templates,generated}

# Create explicit/public subdirectories for data sovereignty
for dir in user sandbox state logs missions moves milestones scripts templates generated; do
    mkdir -p "$PRIVATE_MEMORY/$dir"/{explicit,public}
done

echo -e "${GREEN}✅ Private uMEMORY structure created at: $PRIVATE_MEMORY${NC}"

# Migrate existing data if repository version exists
if [[ "$IN_REPO" == true ]]; then
    echo -e "\n${YELLOW}📦 Migrating Repository uMEMORY to Private Location...${NC}"
    
    # Backup current repository uMEMORY
    if [[ -d "$UDOS_ROOT/uMEMORY.backup" ]]; then
        rm -rf "$UDOS_ROOT/uMEMORY.backup"
    fi
    cp -r "$UDOS_ROOT/uMEMORY" "$UDOS_ROOT/uMEMORY.backup"
    echo -e "${GREEN}✅ Backup created: uMEMORY.backup${NC}"
    
    # Migrate data to appropriate private locations
    echo -e "${YELLOW}📋 Migrating data by type...${NC}"
    
    # Scripts go to scripts/explicit (private by default)
    if [[ -d "$UDOS_ROOT/uMEMORY/scripts" ]]; then
        cp -r "$UDOS_ROOT/uMEMORY/scripts"/* "$PRIVATE_MEMORY/scripts/explicit/" 2>/dev/null || true
        echo -e "${GREEN}  ✅ Scripts migrated to private${NC}"
    fi
    
    # Datasets go to generated/explicit
    if [[ -d "$UDOS_ROOT/uMEMORY/datasets" ]]; then
        cp -r "$UDOS_ROOT/uMEMORY/datasets"/* "$PRIVATE_MEMORY/generated/explicit/" 2>/dev/null || true
        echo -e "${GREEN}  ✅ Datasets migrated to private${NC}"
    fi
    
    # Logs go to logs/explicit
    if [[ -d "$UDOS_ROOT/uMEMORY/logs" ]]; then
        cp -r "$UDOS_ROOT/uMEMORY/logs"/* "$PRIVATE_MEMORY/logs/explicit/" 2>/dev/null || true
        echo -e "${GREEN}  ✅ Logs migrated to private${NC}"
    fi
    
    # User files go to user/explicit
    for file in "$UDOS_ROOT/uMEMORY"/*.md; do
        if [[ -f "$file" ]]; then
            cp "$file" "$PRIVATE_MEMORY/user/explicit/"
        fi
    done
    echo -e "${GREEN}  ✅ User files migrated to private${NC}"
    
    # Templates go to templates/explicit
    if [[ -d "$UDOS_ROOT/uMEMORY/templates" ]]; then
        cp -r "$UDOS_ROOT/uMEMORY/templates"/* "$PRIVATE_MEMORY/templates/explicit/" 2>/dev/null || true
        echo -e "${GREEN}  ✅ Templates migrated to private${NC}"
    fi
    
    # Configs go to user/explicit
    if [[ -d "$UDOS_ROOT/uMEMORY/configs" ]]; then
        cp -r "$UDOS_ROOT/uMEMORY/configs"/* "$PRIVATE_MEMORY/user/explicit/" 2>/dev/null || true
        echo -e "${GREEN}  ✅ Configs migrated to private${NC}"
    fi
fi

# Create user role access structure
echo -e "\n${YELLOW}👥 Setting Up User Role Access...${NC}"

# Create role-specific access files
cat > "$PRIVATE_MEMORY/user/explicit/user-roles.md" << 'EOF'
# uDOS User Roles and Access Levels
[20-80-01] user-roles.md

## Access Matrix

### 🧙 wizard (Full Access)
- **uMEMORY**: Full read/write access to all directories
- **Data Sovereignty**: Can create both explicit and public content
- **Permissions**: All operations, system administration
- **Sharing**: Can configure sharing policies for all users

### 🔮 sorcerer (Advanced User)
- **uMEMORY**: Read/write access to sandbox/, scripts/, templates/
- **Data Sovereignty**: Can create explicit and public content in allowed areas
- **Permissions**: Development, scripting, advanced configuration
- **Sharing**: Can share their own content, limited admin functions

### 👻 ghost (Observer)
- **uMEMORY**: Read-only access to public/ subdirectories only
- **Data Sovereignty**: Can only view public content
- **Permissions**: View public documentation, logs, shared resources
- **Sharing**: Cannot create or modify content

### 😈 imp (Guided User)
- **uMEMORY**: No direct access, operates through guided interfaces
- **Data Sovereignty**: All content private (explicit) by default
- **Permissions**: Basic operations through UI only
- **Sharing**: Requires wizard assistance for any sharing

## Data Sovereignty Levels

### explicit (Default - Private)
- User-controlled private data
- Never shared or synchronized
- Maximum privacy protection
- Default for all new content

### public (Opt-in Sharing)
- User explicitly chooses to make content shareable
- Requires conscious decision to share
- User maintains control and can revoke
- Only applies to non-sensitive content

## Implementation

User role is stored in: `~/.uDOS/uMEMORY/user/explicit/identity.md`
Access is enforced by file permissions and script validation.
EOF

# Set up access permissions based on current user
echo -e "\n${YELLOW}🔒 Configuring Access Permissions...${NC}"

# Get current user role (default to wizard for now)
CURRENT_ROLE="wizard"
if [[ -f "$PRIVATE_MEMORY/user/explicit/identity.md" ]]; then
    CURRENT_ROLE=$(grep -o 'role.*' "$PRIVATE_MEMORY/user/explicit/identity.md" | cut -d: -f2 | xargs) || echo "wizard"
fi

echo -e "${BLUE}Current user role: $CURRENT_ROLE${NC}"

# Set appropriate permissions based on role
case "$CURRENT_ROLE" in
    "wizard")
        chmod -R 700 "$PRIVATE_MEMORY"
        echo -e "${GREEN}✅ Wizard permissions set (full access)${NC}"
        ;;
    "sorcerer")
        chmod -R 700 "$PRIVATE_MEMORY"/{sandbox,scripts,templates}
        chmod -R 500 "$PRIVATE_MEMORY"/{user,state,logs,missions,moves,milestones,generated}
        echo -e "${GREEN}✅ Sorcerer permissions set (limited access)${NC}"
        ;;
    "ghost")
        chmod -R 500 "$PRIVATE_MEMORY"/*/public
        chmod -R 000 "$PRIVATE_MEMORY"/*/explicit
        echo -e "${GREEN}✅ Ghost permissions set (read-only public)${NC}"
        ;;
    "imp")
        chmod -R 000 "$PRIVATE_MEMORY"
        chmod 700 "$PRIVATE_MEMORY/user/explicit"  # Allow guided access
        echo -e "${GREEN}✅ Imp permissions set (guided access only)${NC}"
        ;;
esac

# Create symlink for easy access
if [[ ! -L "$UDOS_ROOT/uMEMORY" ]] && [[ "$IN_REPO" == true ]]; then
    echo -e "\n${YELLOW}🔗 Creating Symlink...${NC}"
    rm -rf "$UDOS_ROOT/uMEMORY"
    ln -s "$PRIVATE_MEMORY" "$UDOS_ROOT/uMEMORY"
    echo -e "${GREEN}✅ Symlink created: uMEMORY -> $PRIVATE_MEMORY${NC}"
fi

# Update .gitignore to ensure proper exclusion
echo -e "\n${YELLOW}📝 Updating .gitignore...${NC}"
if ! grep -q "^uMEMORY/$" "$UDOS_ROOT/.gitignore" 2>/dev/null; then
    echo "uMEMORY/" >> "$UDOS_ROOT/.gitignore"
    echo -e "${GREEN}✅ .gitignore updated${NC}"
fi

# Create access validation script
cat > "$PRIVATE_MEMORY/scripts/explicit/validate-access.sh" << 'EOF'
#!/usr/bin/env bash
# Validate user access permissions for uMEMORY
ROLE=$(grep -o 'role.*' ~/.uDOS/uMEMORY/user/explicit/identity.md | cut -d: -f2 | xargs 2>/dev/null || echo "imp")

case "$1" in
    "read")
        case "$ROLE" in
            "wizard"|"sorcerer") exit 0 ;;
            "ghost") [[ "$2" == *"/public"* ]] && exit 0 || exit 1 ;;
            "imp") [[ "$2" == *"/guided"* ]] && exit 0 || exit 1 ;;
        esac
        ;;
    "write")
        case "$ROLE" in
            "wizard") exit 0 ;;
            "sorcerer") [[ "$2" == *"/sandbox/"* || "$2" == *"/scripts/"* || "$2" == *"/templates/"* ]] && exit 0 || exit 1 ;;
            *) exit 1 ;;
        esac
        ;;
esac
exit 1
EOF

chmod +x "$PRIVATE_MEMORY/scripts/explicit/validate-access.sh"

echo -e "\n${GREEN}🎉 uMEMORY Compliance Complete!${NC}"
echo "=================================="
echo -e "${BLUE}📍 Private Location:${NC} $PRIVATE_MEMORY"
echo -e "${BLUE}🔗 Symlink:${NC} $UDOS_ROOT/uMEMORY -> $PRIVATE_MEMORY"
echo -e "${BLUE}👤 Current Role:${NC} $CURRENT_ROLE"
echo -e "${BLUE}🔒 Data Sovereignty:${NC} explicit (private) by default"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Repository uMEMORY will be excluded from git"
echo "2. All user data is now private by default"
echo "3. Use 'public' subdirectories for shareable content"
echo "4. Role-based access is enforced"
