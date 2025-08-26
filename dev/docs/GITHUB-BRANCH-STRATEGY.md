# uDOS GitHub Branch Strategy Implementation

## Overview

This document outlines the implementation of uDOS's role-based GitHub branching strategy for distributable installations. Each role receives a clean, filtered installation with only the components appropriate for their permission level.

## Branch Architecture

### Main Branch (Complete Development Environment)
- **Purpose**: Full uDOS development with all components
- **Access**: WIZARD role + DEV mode
- **Components**: Everything including `/dev` folder
- **Use Case**: Core development, system administration, full feature access

### Role-Based Distribution Branches

Each role gets its own distribution branch with filtered components based on the role capability matrix:

#### Shared Components (Synced Across All Roles)
- **uCORE/core**: Essential system functions
- **uMEMORY/system**: System-level data management
- **uKNOWLEDGE/public**: General documentation and help

#### Role-Specific Component Matrix

| Component | GHOST | TOMB | CRYPT | DRONE | KNIGHT | IMP | SORCERER | WIZARD |
|-----------|-------|------|-------|-------|--------|-----|----------|--------|
| **uCORE** | launcher | full | full | full | full | full | full | full |
| **uMEMORY** | none | read-only | encrypted | full | full | full | full | full |
| **uKNOWLEDGE** | none | historical | full | full | full | full | full | full |
| **uNETWORK** | none | none | basic | full | full | full | full | full |
| **uSCRIPT** | none | none | basic | full | full | full | full | full |
| **sandbox** | demo | limited | full | full | full | full | full | full |
| **docs** | public | read-only | full | full | full | full | full | full |
| **extensions** | none | none | none | none | none | user | platform | all |
| **dev** | none | none | none | none | none | none | none | full |

## Implementation Strategy

### 1. Local Development (Overlay Mode)
In user local environments, roles operate as overlays to leverage shared components:

```
uDOS-Installation/
├── uCORE/           # Shared across all roles
├── uMEMORY/         # Role-filtered access
│   ├── system/      # Shared system data
│   └── user/        # Role-specific user data
├── uKNOWLEDGE/      # Role-filtered knowledge base
├── sandbox/         # Role-appropriate workspace
└── role-overlay/    # Role-specific components
    ├── permissions.json
    ├── capabilities.json
    └── role-scripts/
```

### 2. GitHub Distribution (Clean Branches)
Each role branch contains only the components that role should have access to:

```bash
# Role branches provide clean installations
git clone -b role-ghost https://github.com/fredporter/uDOS.git    # Demo only
git clone -b role-tomb https://github.com/fredporter/uDOS.git     # Archive access
git clone -b role-crypt https://github.com/fredporter/uDOS.git    # Crypto + basic network
git clone -b role-drone https://github.com/fredporter/uDOS.git    # Automation
git clone -b role-knight https://github.com/fredporter/uDOS.git   # Security ops
git clone -b role-imp https://github.com/fredporter/uDOS.git      # Development
git clone -b role-sorcerer https://github.com/fredporter/uDOS.git # Advanced mgmt
git clone -b role-wizard https://github.com/fredporter/uDOS.git   # Complete system
```

### 3. Component Synchronization Strategy

#### Automated Sync (CI/CD Pipeline)
```yaml
# .github/workflows/sync-role-branches.yml
name: Sync Role Branches
on:
  push:
    branches: [ main ]
    paths:
      - 'uCORE/core/**'
      - 'uMEMORY/system/**'
      - 'uKNOWLEDGE/public/**'

jobs:
  sync-shared-components:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        role: [ghost, tomb, crypt, drone, knight, imp, sorcerer, wizard]
    steps:
      - name: Sync shared components to role-${{ matrix.role }}
        run: ./dev/scripts/sync-role-components.sh ${{ matrix.role }}
```

#### Manual Sync for Role-Specific Updates
```bash
# Update specific role branch with new capabilities
./dev/scripts/create-role-branches.sh create
./dev/scripts/create-role-branches.sh push
```

## Role Branch Details

### role-ghost (Level 10) - Demo Installation
**Purpose**: Safe learning environment for new users

**Components Included**:
- `uCORE/launcher/` - System startup scripts
- `uCORE/code/basic/` - Basic command set
- `sandbox/demo/` - Demo workspace
- `docs/public/` - Public documentation
- `install-ghost.sh` - One-command installer

**What's Excluded**: All advanced components, no system access, no scripting

**Installation**:
```bash
curl -sSL https://raw.githubusercontent.com/fredporter/uDOS/role-ghost/install-ghost.sh | bash
```

### role-tomb (Level 20) - Archive Installation
**Purpose**: Data archaeology and historical analysis

**Components Included**:
- Full `uCORE` system
- `uMEMORY` (read-only archive access)
- `uKNOWLEDGE` (historical data)
- `sandbox` (limited workspace)
- `docs` (full documentation)

**What's Excluded**: uNETWORK, uSCRIPT, extensions, dev environment

### role-crypt (Level 30) - Cryptographic Installation
**Purpose**: Advanced encryption and security protocols

**Components Included**:
- Full `uCORE` system
- `uMEMORY` (encrypted storage)
- `uKNOWLEDGE` (security knowledge)
- `uNETWORK` (basic networking)
- `uSCRIPT` (basic scripting)
- `sandbox` (full workspace)

**What's Excluded**: Advanced extensions, dev environment

### role-drone (Level 40) - Automation Installation
**Purpose**: Automated task execution and monitoring

**Components Included**:
- Complete system minus development environment
- All core components with full access
- Automation-focused documentation

**What's Excluded**: User extensions, dev environment

### role-knight (Level 50) - Security Operations
**Purpose**: System defense and incident response

**Components Included**:
- Complete operational system
- Security-focused tools and documentation
- Full networking and scripting capabilities

**What's Excluded**: Development extensions, dev environment

### role-imp (Level 60) - Developer Installation
**Purpose**: Creative projects and API development

**Components Included**:
- Complete system functionality
- User extension system
- Development-focused documentation
- API integration tools

**What's Excluded**: Platform/core extensions, dev environment

### role-sorcerer (Level 80) - Advanced Management
**Purpose**: Team coordination and advanced workflows

**Components Included**:
- Complete system functionality
- User and platform extensions
- Advanced workflow management
- Team coordination tools

**What's Excluded**: Core extensions, dev environment

### role-wizard (Level 100) - Complete Installation
**Purpose**: Full system control and core development

**Components Included**:
- Complete uDOS installation
- All extensions (user, platform, core)
- Full development environment (`/dev` folder)
- System administration tools

**What's Excluded**: Nothing - complete access

## Installation and Upgrade Workflow

### New User Installation
1. **Role Assessment**: User determines appropriate starting role
2. **Branch Installation**: Clone and install from appropriate role branch
3. **Role Configuration**: System configures permissions and capabilities
4. **Local Overlay**: Role-specific overlay applied to shared components

### Role Progression (Upgrade Path)
```bash
# Upgrade from current role to higher role
[ROLE|UPGRADE*IMP]           # Upgrade to IMP from current role
[ROLE|MIGRATE*SORCERER]      # Migrate installation to SORCERER level
```

**Upgrade Process**:
1. **Backup Current**: System creates backup of current installation
2. **Component Addition**: New components added based on target role
3. **Permission Update**: Access controls updated to new role level
4. **Verification**: System verifies upgrade completion
5. **Migration**: User data migrated to new role structure

### Development Workflow

#### For Core Development (Main Branch)
```bash
# Work in main branch with full development environment
git clone https://github.com/fredporter/uDOS.git
cd uDOS
./dev/scripts/dev-mode-startup.sh   # Initialize development environment
[DEV|INIT]                          # Start development mode
```

#### For Role-Specific Testing
```bash
# Test role-specific functionality
./dev/scripts/create-role-branches.sh create    # Create test branches
git checkout role-imp                           # Test IMP installation
./install-imp.sh /tmp/test-imp                  # Test installation
```

#### For Distribution Updates
```bash
# Update all role branches with latest changes
./dev/scripts/create-role-branches.sh create    # Recreate role branches
./dev/scripts/create-role-branches.sh push      # Push to GitHub
```

## Benefits of This Strategy

### For End Users
- **Clean Installations**: No unnecessary components cluttering the system
- **Appropriate Complexity**: Interface matches user expertise level
- **Easy Discovery**: Clear documentation for each role's capabilities
- **Smooth Progression**: Natural upgrade path as skills develop

### For Developers
- **Maintainable**: Clear separation of concerns between roles
- **Testable**: Each role can be independently validated
- **Distributable**: Each role has its own clean installation package
- **Scalable**: Easy to add new roles or modify existing capabilities

### For System Architecture
- **Modular**: Components developed and tested independently
- **Consistent**: Shared core ensures uniform behavior
- **Secure**: Role-based access enforced at installation level
- **Flexible**: Overlay system allows customization without breaking core

## Implementation Commands

### Create All Role Branches
```bash
# Create complete role branch structure
./dev/scripts/create-role-branches.sh create
```

### Push Role Branches to GitHub
```bash
# Push all role branches to remote repository
./dev/scripts/create-role-branches.sh push
```

### List Available Role Branches
```bash
# Display all role branches and installation commands
./dev/scripts/create-role-branches.sh list
```

### Generate Documentation
```bash
# Create comprehensive branch strategy documentation
./dev/scripts/create-role-branches.sh docs
```

## Future Enhancements

### Automated CI/CD Pipeline
- **Component Sync**: Automatically sync shared components across role branches
- **Testing**: Automated testing of each role installation
- **Validation**: Verify role permissions and capabilities
- **Documentation**: Auto-generate role-specific documentation

### Enhanced Role Management
- **Dynamic Overlays**: Runtime role switching without reinstallation
- **Capability Tokens**: Fine-grained permission management
- **Role Inheritance**: Complex role hierarchies and combinations
- **Custom Roles**: User-defined role configurations

### Distribution Optimization
- **Container Images**: Docker containers for each role
- **Package Managers**: Integration with system package managers
- **Update System**: In-place role upgrades and component updates
- **Dependency Management**: Automatic dependency resolution per role

---

*GitHub Branch Strategy Implementation - uDOS v1.0.4.1*
