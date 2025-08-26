# uDOS GitHub Role-Based Branch Strategy

## Executive Summary

uDOS implements a sophisticated GitHub branching strategy that provides clean, role-appropriate installations for users at different capability levels. This strategy enables:

- **Clean Distributions**: Each role receives only the components they need
- **Overlay Architecture**: Local installations use overlay mode for efficiency
- **Shared Core Components**: Critical components sync across all role branches
- **Progressive Capabilities**: Natural upgrade path from basic to advanced usage

## Branch Architecture Overview

### Main Branch (Development)
- **Repository**: `main` branch
- **Purpose**: Complete development environment
- **Access**: WIZARD role + DEV mode
- **Components**: Full uDOS including `/dev` development environment

### Role Distribution Branches

Each role receives its own GitHub branch with filtered, appropriate components:

```
role-ghost     (Level 10)  → Demo installation, learning environment
role-tomb      (Level 20)  → Archive access, data archaeology  
role-crypt     (Level 30)  → Cryptographic operations, basic networking
role-drone     (Level 40)  → Automation, monitoring, task scheduling
role-knight    (Level 50)  → Security operations, threat detection
role-imp       (Level 60)  → Development tools, API integration
role-sorcerer  (Level 80)  → Advanced management, team coordination  
role-wizard    (Level 100) → Complete system access, development environment
```

## Component Distribution Matrix

### Shared Components (Synchronized Across All Roles)
These components are maintained consistently across all role branches:

- **uCORE/core**: Essential system functions and command processing
- **uMEMORY/system**: System-level data management and configuration
- **uKNOWLEDGE/public**: General documentation and help systems

### Role-Filtered Components

| Component | GHOST | TOMB | CRYPT | DRONE | KNIGHT | IMP | SORCERER | WIZARD |
|-----------|-------|------|-------|-------|--------|-----|----------|--------|
| **uCORE** | launcher only | full | full | full | full | full | full | full |
| **uMEMORY** | none | read-only | encrypted | full | full | full | full | full |
| **uKNOWLEDGE** | none | historical | security | full | full | full | full | full |
| **uNETWORK** | none | none | basic | full | full | full | full | full |
| **uSCRIPT** | none | none | basic | full | full | full | full | full |
| **sandbox** | demo | limited | full | full | full | full | full | full |
| **docs** | public | read-only | security | full | full | full | full | full |
| **extensions** | none | none | none | none | none | user | platform | all |
| **dev** | none | none | none | none | none | none | none | full |

## Detailed Role Specifications

### GHOST Role (Level 10) - Demo Installation
**Branch**: `role-ghost`  
**Purpose**: Safe learning environment for newcomers

**Included Components**:
- `uCORE/launcher/` - Basic system startup
- `uCORE/code/basic/` - Essential commands only
- `sandbox/demo/` - Protected demo workspace
- `docs/public/` - Public documentation and tutorials
- `install-ghost.sh` - Automated installer

**Installation Command**:
```bash
git clone -b role-ghost https://github.com/fredporter/uDOS.git uDOS-GHOST
cd uDOS-GHOST && ./install-ghost.sh
```

**Capabilities**:
- Read-only system exploration
- Basic uCODE syntax learning
- Temporary session data (non-persistent)
- Guided tutorials and help system

### TOMB Role (Level 20) - Archive Installation
**Branch**: `role-tomb`  
**Purpose**: Data archaeology and historical analysis

**Included Components**:
- Complete `uCORE` system
- `uMEMORY` with read-only archive access
- `uKNOWLEDGE` historical database
- `sandbox` with limited workspace
- Complete documentation system

**Installation Command**:
```bash
git clone -b role-tomb https://github.com/fredporter/uDOS.git uDOS-TOMB
cd uDOS-TOMB && ./install-tomb.sh
```

**Capabilities**:
- Archive search and data mining
- Historical data analysis
- Backup system access
- Encrypted archive decryption

### CRYPT Role (Level 30) - Cryptographic Installation
**Branch**: `role-crypt`  
**Purpose**: Advanced encryption and security protocols

**Included Components**:
- Complete `uCORE` system
- `uMEMORY` with encrypted storage
- `uKNOWLEDGE` security documentation
- `uNETWORK` basic networking capabilities
- `uSCRIPT` basic scripting environment
- Full `sandbox` workspace

**Installation Command**:
```bash
git clone -b role-crypt https://github.com/fredporter/uDOS.git uDOS-CRYPT
cd uDOS-CRYPT && ./install-crypt.sh
```

**Capabilities**:
- Advanced encryption/decryption
- Key management and rotation
- Secure communications
- Security auditing tools

### DRONE Role (Level 40) - Automation Installation
**Branch**: `role-drone`  
**Purpose**: Automated task execution and system monitoring

**Included Components**:
- Complete operational system (minus development environment)
- Full networking and scripting capabilities
- Automation-focused tools and documentation
- Complete workspace access

**Installation Command**:
```bash
git clone -b role-drone https://github.com/fredporter/uDOS.git uDOS-DRONE
cd uDOS-DRONE && ./install-drone.sh
```

**Capabilities**:
- Task scheduling and automation
- System monitoring and maintenance
- Automated backup systems
- Workflow orchestration

### KNIGHT Role (Level 50) - Security Operations
**Branch**: `role-knight`  
**Purpose**: System defense, threat detection, incident response

**Included Components**:
- Complete operational system
- Security-focused tools and monitoring
- Threat intelligence integration
- Incident response capabilities

**Installation Command**:
```bash
git clone -b role-knight https://github.com/fredporter/uDOS.git uDOS-KNIGHT
cd uDOS-KNIGHT && ./install-knight.sh
```

**Capabilities**:
- Real-time threat monitoring
- Automated threat blocking
- Incident response protocols
- Security forensics and analysis

### IMP Role (Level 60) - Developer Installation
**Branch**: `role-imp`  
**Purpose**: Creative development and API integration

**Included Components**:
- Complete system functionality
- User extension system
- Development tools and libraries
- API integration capabilities

**Installation Command**:
```bash
git clone -b role-imp https://github.com/fredporter/uDOS.git uDOS-IMP
cd uDOS-IMP && ./install-imp.sh
```

**Capabilities**:
- API development and integration
- User extension development
- Project scaffolding and templates
- Creative development tools

### SORCERER Role (Level 80) - Advanced Management
**Branch**: `role-sorcerer`  
**Purpose**: Team coordination and advanced workflow management

**Included Components**:
- Complete system functionality
- User and platform extensions
- Advanced workflow management
- Team coordination tools

**Installation Command**:
```bash
git clone -b role-sorcerer https://github.com/fredporter/uDOS.git uDOS-SORCERER
cd uDOS-SORCERER && ./install-sorcerer.sh
```

**Capabilities**:
- Advanced workflow management
- Team coordination and collaboration
- Multi-role session management
- Complex project orchestration

### WIZARD Role (Level 100) - Complete Installation
**Branch**: `role-wizard`  
**Purpose**: Full system control and core development

**Included Components**:
- Complete uDOS installation
- All extension categories (user, platform, core)
- Full development environment (`/dev` folder)
- System administration tools

**Installation Command**:
```bash
git clone -b role-wizard https://github.com/fredporter/uDOS.git uDOS-WIZARD
cd uDOS-WIZARD && ./install-wizard.sh
```

**Capabilities**:
- Complete system access and control
- Core system development
- All lower-role capabilities
- System configuration and administration

## Local Implementation Strategy

### Overlay Architecture
In local environments, uDOS uses an overlay system for efficiency:

```
Local uDOS Installation/
├── shared-core/              # Shared components (uCORE/core, uMEMORY/system)
├── role-layer/               # Role-specific components and permissions
│   ├── capabilities.json    # Role capability definitions
│   ├── permissions.json     # Access control matrix
│   └── components/          # Role-specific additions
├── user-layer/              # User customizations and data
│   ├── uMEMORY/user/       # Personal data and configurations
│   ├── sandbox/            # User workspace
│   └── extensions/user/    # User-installed extensions
└── session-layer/           # Temporary session data
    ├── logs/               # Session logging
    ├── cache/              # Temporary files
    └── state/              # Session state management
```

### Role Switching and Upgrades
Users can upgrade their role level without complete reinstallation:

```bash
# Check current role and available upgrades
[ROLE|STATUS]
[ROLE|UPGRADE-OPTIONS]

# Upgrade to higher role (downloads additional components)
[ROLE|UPGRADE*IMP]
[ROLE|UPGRADE*SORCERER]
[ROLE|UPGRADE*WIZARD]

# Temporary role elevation for specific tasks
[ROLE|ELEVATE*KNIGHT] <SECURITY-SCAN>
[ROLE|ELEVATE*SORCERER] <TEAM-COORDINATION>
```

## GitHub Branch Management

### Automated Synchronization
Core components are automatically synchronized across role branches:

```yaml
# .github/workflows/sync-role-branches.yml
name: Sync Shared Components
on:
  push:
    branches: [main]
    paths: ['uCORE/core/**', 'uMEMORY/system/**', 'uKNOWLEDGE/public/**']

jobs:
  sync-components:
    strategy:
      matrix:
        role: [ghost, tomb, crypt, drone, knight, imp, sorcerer, wizard]
    steps:
      - name: Sync shared components to role-${{ matrix.role }}
        run: |
          git checkout role-${{ matrix.role }}
          git merge main --strategy-option=subtree=uCORE/core/
          git merge main --strategy-option=subtree=uMEMORY/system/
          git merge main --strategy-option=subtree=uKNOWLEDGE/public/
```

### Manual Branch Updates
For role-specific updates and new capabilities:

```bash
# Create/update all role branches
./dev/scripts/create-role-branches.sh create

# Push role branches to GitHub
./dev/scripts/create-role-branches.sh push

# Test specific role installation
./dev/scripts/test-role-installation.sh imp

# Validate all role branches
./dev/scripts/validate-role-branches.sh all
```

## Installation Examples

### Quick Installation (Recommended)
Each role provides a one-command installation:

```bash
# GHOST - Demo and learning
curl -sSL https://raw.githubusercontent.com/fredporter/uDOS/role-ghost/install-ghost.sh | bash

# IMP - Development
curl -sSL https://raw.githubusercontent.com/fredporter/uDOS/role-imp/install-imp.sh | bash

# WIZARD - Complete system
curl -sSL https://raw.githubusercontent.com/fredporter/uDOS/role-wizard/install-wizard.sh | bash
```

### Manual Installation
For customized installation paths:

```bash
# Clone specific role branch
git clone -b role-imp https://github.com/fredporter/uDOS.git ~/Development/uDOS-IMP

# Install with custom configuration
cd ~/Development/uDOS-IMP
./install-imp.sh --install-dir=/opt/udos --user-space=/home/$USER/.udos
```

### Container Installation
For isolated environments:

```bash
# Run uDOS in Docker container (role-specific)
docker run -it udos:role-imp
docker run -it udos:role-wizard
```

## Development and Testing Workflow

### Core Development (Main Branch)
```bash
# Full development environment
git clone https://github.com/fredporter/uDOS.git
cd uDOS
./dev/scripts/dev-mode-startup.sh
[DEV|INIT]
```

### Role-Specific Development
```bash
# Test role implementations
./dev/scripts/create-role-branches.sh create
./dev/scripts/test-all-roles.sh

# Debug specific role
git checkout role-imp
./debug/test-role-capabilities.sh imp
```

### Distribution Preparation
```bash
# Prepare all role distributions
./dev/scripts/prepare-distributions.sh

# Validate installations
./dev/scripts/validate-all-roles.sh

# Create release tags
./dev/scripts/tag-role-releases.sh v1.0.4.1
```

## Security and Access Control

### Branch-Level Security
Each role branch enforces access controls at installation time:

```json
{
  "role": "IMP",
  "level": 60,
  "permissions": {
    "system_access": "limited",
    "memory_access": "user_space",
    "script_execution": true,
    "network_access": true,
    "development_access": "user_extensions"
  },
  "restrictions": {
    "core_modification": false,
    "system_configuration": false,
    "platform_extensions": false,
    "dev_environment": false
  }
}
```

### Runtime Permission Enforcement
Permissions are enforced during command execution:

```bash
# Permission check before command execution
if ! check_role_permission "$CURRENT_ROLE" "$COMMAND_CATEGORY"; then
    echo "❌ Command requires higher role level"
    echo "Current: $CURRENT_ROLE, Required: $REQUIRED_ROLE"
    exit 1
fi
```

## Benefits and Advantages

### For End Users
- **Simplicity**: Clean installation with only needed components
- **Security**: Role-based access prevents accidental system damage
- **Learning**: Gradual complexity introduction as skills develop
- **Performance**: Smaller installation footprint and faster startup

### For System Administrators
- **Maintenance**: Clear component separation and update paths
- **Security**: Granular access control and audit capabilities
- **Deployment**: Role-specific installations for different user types
- **Scaling**: Easy to deploy appropriate role for each user's needs

### for Developers
- **Testing**: Independent testing of each role's capabilities
- **Distribution**: Clean packaging for different user types
- **Maintenance**: Clear component ownership and update procedures
- **Architecture**: Modular design enables independent development

## Future Roadmap

### Enhanced Role Management
- **Dynamic Capabilities**: Runtime role switching without reinstallation
- **Custom Roles**: User-defined role configurations and permissions
- **Role Inheritance**: Complex role hierarchies and combinations
- **Capability Tokens**: Fine-grained permission management

### Improved Distribution
- **Package Managers**: Integration with system package managers
- **Container Images**: Pre-built Docker/Podman images for each role
- **Cloud Deployment**: One-click cloud instance deployment per role
- **Mobile Versions**: Role-appropriate mobile application packages

### Advanced Features
- **Multi-Role Sessions**: Concurrent role capabilities in single session
- **Role Collaboration**: Cross-role workflow and data sharing
- **Audit System**: Comprehensive role-based activity logging
- **Analytics**: Usage patterns and capability utilization analysis

---

*Comprehensive GitHub Branch Strategy - uDOS v1.0.4.1*
