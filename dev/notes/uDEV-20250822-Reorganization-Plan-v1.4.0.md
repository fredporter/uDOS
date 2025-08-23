# uMEMORY Reorganization Plan v1.4.0
# Multi-Role Data Architecture with Centralized Logging
# Updated: datagets → get terminology, modes → role, logging → log

# ═══════════════════════════════════════════════════════════════════════
# NEW uMEMORY STRUCTURE
# ═══════════════════════════════════════════════════════════════════════

# ROOT LEVEL (System-wide)
uMEMORY/
├── system/                    # System data (unchanged location)
│   ├── config/               # System configurations
│   ├── templates/            # System templates
│   ├── post/                 # System post data
│   └── get/                  # System GET data
├── log/                      # 🆕 Centralized logging for all roles
│   ├── errors/               # Error logs from all roles
│   ├── debug/                # Debug logs from all roles
│   ├── daily/                # Daily activity logs
│   ├── missions/             # Mission logs from all roles
│   ├── milestones/           # Milestone logs from all roles
│   ├── moves/                # Move logs from all roles
│   └── legacy/               # Legacy mission data
├── role/                     # 🆕 Role-specific data organization
│   ├── wizard/               # Wizard role data
│   ├── sorcerer/             # Sorcerer role data
│   ├── imp/                  # Imp role data
│   ├── knight/               # 🆕 Knight role data (after Imp)
│   ├── ghost/                # Ghost role data
│   ├── drone/                # Drone role data
│   ├── tomb/                 # Tomb role data
│   └── crypt/                # 🆕 Crypt role data (after Tomb)
└── shared/                   # 🆕 Shared resources across roles
    ├── templates/            # Role-agnostic templates
    ├── utilities/            # Shared scripts and tools
    └── cache/                # Shared cache data

# ═══════════════════════════════════════════════════════════════════════
# ROLE-SPECIFIC STRUCTURE (Each role follows this pattern)
# ═══════════════════════════════════════════════════════════════════════

role/{role_name}/
├── setup/                    # Role setup and configuration
│   ├── GET                   # Role-specific GET file
│   ├── installation.id       # Unique installation ID
│   ├── setup-vars.sh         # Role-specific variables
│   └── config.json          # Role configuration
├── user/                     # User data for this role
│   ├── missions/             # Mission data
│   ├── milestones/          # Milestone data
│   ├── moves/               # Move data
│   ├── sessions/            # Session data
│   └── preferences/         # User preferences
├── log/                      # Role-specific logs (symlinked to central)
│   ├── errors/              # → ../../log/errors/{role}/
│   ├── debug/               # → ../../log/debug/{role}/
│   ├── daily/               # → ../../log/daily/{role}/
│   └── missions/            # → ../../log/missions/{role}/
└── cache/                    # Role-specific cache
    ├── temp/                # Temporary files
    └── processed/           # Processed data

# ═══════════════════════════════════════════════════════════════════════
# NEW SANDBOX STRUCTURE (Multi-Role Support)
# ═══════════════════════════════════════════════════════════════════════

sandbox/
├── backup/                   # Centralized backup configs
│   ├── config.json          # Backup configuration
│   ├── retention.json       # Retention policies
│   └── encryption.conf      # Encryption settings
├── role/                     # Role-specific user files
│   ├── wizard/
│   │   ├── user.md          # Wizard user identity
│   │   ├── permissions.json # Wizard permissions
│   │   └── workspace.conf   # Wizard workspace config
│   ├── sorcerer/
│   │   ├── user.md          # Sorcerer user identity
│   │   └── permissions.json # Sorcerer permissions
│   ├── imp/
│   │   ├── user.md          # Imp user identity
│   │   └── permissions.json # Imp permissions
│   ├── knight/              # 🆕 Knight role
│   │   ├── user.md          # Knight user identity
│   │   └── permissions.json # Knight permissions
│   ├── ghost/
│   │   ├── user.md          # Ghost user identity
│   │   └── permissions.json # Ghost permissions
│   ├── drone/
│   │   ├── user.md          # Drone user identity
│   │   └── permissions.json # Drone permissions
│   ├── tomb/
│   │   ├── user.md          # Tomb user identity
│   │   └── permissions.json # Tomb permissions
│   └── crypt/               # 🆕 Crypt role
│       ├── user.md          # Crypt user identity
│       └── permissions.json # Crypt permissions
├── current-role.conf         # Active role configuration
├── user.md                   # Current active user (symlink)
└── shared/                   # Shared sandbox resources
    ├── scripts/              # Role-agnostic scripts
    ├── tasks/                # Shared tasks
    └── get/                  # Shared data templates

# ═══════════════════════════════════════════════════════════════════════
# ROLE HIERARCHY AND PERMISSIONS
# ═══════════════════════════════════════════════════════════════════════

# Level 1-3: Learning Roles
wizard:    Level 10 (Full system access)
sorcerer:  Level 8  (Advanced scripting and automation)
imp:       Level 6  (File system manipulation)

# Level 4: New Knight Role
knight:    Level 5  (Security and protection operations)

# Level 5-7: System Roles
ghost:     Level 4  (System monitoring and analytics)
drone:     Level 3  (Automated task execution)
tomb:      Level 2  (Archive and recovery operations)

# Level 8: New Crypt Role
crypt:     Level 1  (Encryption and security vault)

# ═══════════════════════════════════════════════════════════════════════
# MIGRATION PRIORITIES
# ═══════════════════════════════════════════════════════════════════════

PHASE 1: Core Structure
- Create new uMEMORY/log/ structure
- Create new uMEMORY/role/ structure
- Create new sandbox/role/ structure

PHASE 2: Logging Migration
- Move all error logs to uMEMORY/log/errors/
- Move all debug logs to uMEMORY/log/debug/
- Move all daily logs to uMEMORY/log/daily/
- Move mission/milestone/move logs to uMEMORY/log/

PHASE 3: User Data Migration
- Move user missions/milestones/moves to role-specific locations
- Create role-specific user.md files
- Set up proper symlinking structure

PHASE 4: New Role Setup
- Create Knight role (Level 5)
- Create Crypt role (Level 1)
- Set up GET files and installation.id for all roles

PHASE 5: Integration
- Update backup system for new structure
- Update scripts to use centralized logging
- Update role detection and switching logic
