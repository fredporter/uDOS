# 🏗️ uDOS v1.0.4.1 Multi-Installation Architecture

This directory contains role-specific installations for the uDOS system, supporting the 6-tier mystical role hierarchy. Each installation provides a tailored environment with appropriate capabilities and restrictions based on the user's role.

## 📁 Installation Directory Structure

```
installations/
├── ghost/              # Level 10 - Demo and evaluation access
├── tomb/               # Level 20 - Archive and backup management
├── drone/              # Level 40 - Task automation and monitoring
├── imp/                # Level 60 - Development and creative tools
├── sorcerer/           # Level 80 - Advanced user management
└── wizard/             # Level 100 - Complete system access (symlink)
```

## 🎭 Installation Types

### 👻 Ghost Installation (Level 10)
**Purpose**: Demo and evaluation environment
- Limited demonstration capabilities
- Public documentation access
- Temporary session-based operations
- Evaluation mode for prospective users

### ⚰️ Tomb Installation (Level 20)
**Purpose**: Archive and historical data management
- Archive browsing and retrieval tools
- Backup creation and restoration
- Historical data analysis
- Long-term data preservation

### 🤖 Drone Installation (Level 40)
**Purpose**: Automated task execution and monitoring
- Task automation and scheduling
- System monitoring and logging
- Automated operations management
- Status reporting and health monitoring

### 👹 Imp Installation (Level 60)
**Purpose**: Development and creative environment
- Script and template development
- Creative editing and authoring tools
- Personal project management
- Template system access

### 🔮 Sorcerer Installation (Level 80)
**Purpose**: Advanced user management and administration
- Enhanced project management tools
- User administration capabilities
- Advanced workflows and collaboration
- Resource allocation and management

### 🧙‍♂️ Wizard Installation (Level 100)
**Purpose**: Complete system development and administration
- Full uDOS system access and control
- Development environment with Git integration
- System administration and configuration
- Permission and installation management

## 🔐 Shared Resources

The `../shared/` directory contains:
- **permissions/**: Role-based access control configurations
- **configs/**: Shared system configurations
- **resources/**: Common resources and assets

## 🚀 Installation Management

### Quick Start
```bash
# List available installations
ls installations/

# Install specific role environment
./install-role.sh [role-name]

# Switch between installations
./switch-role.sh [role-name]

# Manage installation permissions
./manage-installations.sh permissions
```

### Installation Commands
Each installation includes role-specific scripts and tools located in their respective directories. Refer to individual installation README files for detailed usage instructions.

## 📊 Access Matrix

| Resource | Ghost | Tomb | Drone | Imp | Sorcerer | Wizard |
|----------|--------|------|--------|-----|----------|--------|
| Demo Interface | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Archive Access | ❌ | ✅ | ❌ | ❌ | 📖 | ✅ |
| Task Automation | ❌ | ❌ | ✅ | ❌ | 📖 | ✅ |
| Development Tools | ❌ | ❌ | ❌ | ✅ | 📖 | ✅ |
| User Management | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| System Admin | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

**Legend**: ✅ Full Access | 📖 Read Only | ❌ No Access

## 🛡️ Security Model

Each installation operates within strict permission boundaries:
- **Sandboxed Environment**: Role-specific access controls
- **Resource Isolation**: Appropriate separation of capabilities
- **Upgrade Paths**: Clear progression from lower to higher roles
- **Audit Logging**: All actions logged for security and monitoring

---

*uDOS v1.0.4.1 Multi-Installation Architecture - Supporting all mystical roles with appropriate capabilities and security*
