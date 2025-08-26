# uMEMORY Role Directory

This directory contains role-specific memory archives. Role data is automatically moved here from `/sandbox/sessions/` when sessions end.

## Session Archive Flow (Future Implementation)
```
[Session Active] → /sandbox/sessions/current/
[Session End] → Archive to /uMEMORY/role/{current_role}/
[Sandbox Flush] → Clear /sandbox/ (role memory preserved here)
```

## uDOS Role Hierarchy (8 Levels)

The uDOS system implements an 8-tier role hierarchy, from highest to lowest access:

### 🧙 **WIZARD** (Level 8 - Highest)
- **Access**: Full system control and administration
- **Capabilities**: All features, system configuration, user management
- **Description**: Master administrators with complete uDOS access
- **Folder Creation**: `/uMEMORY/role/wizard/` (created during installation)

### ⚔️ **KNIGHT** (Level 7)
- **Access**: Advanced development and system features
- **Capabilities**: Development tools, extension management, advanced operations
- **Description**: Senior developers and power users
- **Folder Creation**: `/uMEMORY/role/knight/` (created during installation)

### 🔮 **SORCERER** (Level 6)
- **Access**: Specialized system tools and data manipulation
- **Capabilities**: Data processing, template management, system utilities
- **Description**: Technical specialists with focused permissions
- **Folder Creation**: `/uMEMORY/role/sorcerer/` (created during installation)

### 👤 **CRYPT** (Level 5)
- **Access**: Secure operations and protected features
- **Capabilities**: Security-focused tools, encrypted operations
- **Description**: Security-oriented users with protected access
- **Folder Creation**: `/uMEMORY/role/crypt/` (created during installation)

### 👹 **IMP** (Level 4)
- **Access**: Intermediate features with moderate permissions
- **Capabilities**: Standard development tools, file operations
- **Description**: Intermediate users with balanced access
- **Folder Creation**: `/uMEMORY/role/imp/` (created during installation)

### 🤖 **DRONE** (Level 3)
- **Access**: Basic operations and standard features
- **Capabilities**: Core uDOS functionality, basic file operations
- **Description**: Standard users with essential access
- **Folder Creation**: `/uMEMORY/role/drone/` (created during installation)

### 👻 **GHOST** (Level 2)
- **Access**: Limited operations, read-focused
- **Capabilities**: View operations, limited interaction
- **Description**: Read-only users with minimal permissions
- **Folder Creation**: `/uMEMORY/role/ghost/` (created during installation)

### ⚰️ **TOMB** (Level 1 - Lowest)
- **Access**: Minimal CLI-only interface
- **Capabilities**: Basic CLI operations, emergency access
- **Description**: Emergency access level with minimal functionality
- **Folder Creation**: `/uMEMORY/role/tomb/` (created during installation)

## Directory Structure (Post-Installation)

After user installation, the role directory will contain:

```
role/
├── wizard/           # WIZARD role data and configurations
│   ├── setup/        # Role-specific setup files
│   ├── user/         # User data for this role
│   └── config/       # Role configuration files
├── knight/           # KNIGHT role data and configurations
├── sorcerer/         # SORCERER role data and configurations
├── crypt/            # CRYPT role data and configurations
├── imp/              # IMP role data and configurations
├── drone/            # DRONE role data and configurations
├── ghost/            # GHOST role data and configurations
└── tomb/             # TOMB role data and configurations
```

## Role Assignment

- **User Role**: Determined during installation and stored in `/uMEMORY/user/installation.md`
- **Role Data**: Specific permissions and configurations loaded from `/uMEMORY/system/uDATA-user-roles.json`
- **Role Memory**: User-specific data stored in appropriate role subfolder

## Installation Notes

- **Automatic Creation**: Role subdirectories are created automatically during user setup
- **Permission-Based**: Only relevant role folders are created based on user assignment
- **Dynamic Loading**: Role data is loaded dynamically based on current user role
- **Security**: Role-based access control enforced throughout the system

## Integration Points

- **Help System**: Role-based command filtering via `/uMEMORY/system/uDATA-commands.json`
- **CLI Server**: Role detection and permission enforcement
- **Template System**: Role-specific template access and rendering
- **Color System**: Role-based UI theming and customization

---

**Note**: This directory will be populated during installation. Do not manually create role subdirectories - they are managed by the uDOS installation and role assignment system.
