# uDOS User Guide - Multi-Role Edition

---

**Foreword**

Welcome to uDOS with multi-role architecture and centralized data management. This manual is written in the tradition of classic home computer guides — direct, practical, and nostalgic. Following the design principles from [BBC BASIC for Windows Manual](https://www.bbcbasic.co.uk/bbcwin/manual/bbcwinh.html), uDOS features an authentic Mode 7 teletext interface with chunky block graphics, backup system, and comprehensive role-based data organization.

```
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ██║   ██║██║  ██║██║   ██║███████╗
    ██║   ██║██║  ██║██║   ██║╚════██║
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

    Universal Data Operating System
    ═══════════════ v1.0.4.1 ═══════════════
```

**Edition**: v1.0.4.1 Development Guide - Multi-Role Architecture
**Published**: August 2025
**System**: Universal Device Operating System v1.0.4.1
**Features**: 8-Role Architecture, Centralized Logging, Backup System, uMEMORY Organization, Security Roles

---

## BBC Mode 7 Interface

### What's New: Multi-Role Architecture

#### uMEMORY Organization
uDOS features **comprehensive data reorganization**:
- **Centralized logging** in `uMEMORY/log/` with role-specific organization
- **Role-based data** in `uMEMORY/role/` for 8 distinct user roles
- **Backup system** with password encryption and centralized storage
- **Terminology consistency** using `get` (not datagets), `role` (not modes), `log` (not logging)

#### 8-Role Security Architecture
**Complete role hierarchy** from security vault to full system access:
- **Crypt (Level 1)**: Encryption vault and cryptographic operations
- **Tomb (Level 2)**: Archive operations and long-term storage
- **Drone (Level 3)**: Automated tasks and system processes
- **Ghost (Level 4)**: System monitoring and transparency
- **Knight (Level 5)**: Security operations and threat protection
- **Imp (Level 6)**: File system manipulation and data management
- **Sorcerer (Level 8)**: Advanced scripting and system configuration
- **Wizard (Level 10)**: Full system access and administration

#### Backup System
**Centralized backup management** with security features:
- **Root backup storage** in `/backup/` folder for clean organization
- **Password encryption** using OpenSSL AES-256-CBC for sensitive data
- **Role-specific policies** with retention and access controls
- **Metadata tracking** with backup indexing and migration logs

### Multi-Role Interface Layout

```ascii
┌─── uDOS MULTI-ROLE INTERFACE ────────────────┐
│                                                     │
│  ██ uDOS v1.0.4.1 ██  ROLE-BASED OPERATING SYSTEM    │
│                                                     │
│  Role Hierarchy (8 Levels):                        │
│  ┌─ WIZARD (10) ─┐ ┌─ SORCERER (8) ─┐              │
│  │  FULL ACCESS  │ │  ADVANCED TOOLS │              │
│  └───────────────┘ └─────────────────┘              │
│                                                     │
│  ┌─ IMP (6) ─────┐ ┌─ KNIGHT (5) ───┐              │
│  │  FILE SYSTEM  │ │  SECURITY OPS  │              │
│  └───────────────┘ └────────────────┘              │
│                                                     │
│  ┌─ GHOST (4) ───┐ ┌─ DRONE (3) ────┐              │
│  │  MONITORING   │ │  AUTOMATION    │              │
│  └───────────────┘ └────────────────┘              │
│                                                     │
│  ┌─ TOMB (2) ────┐ ┌─ CRYPT (1) ────┐              │
│  │  ARCHIVING    │ │  ENCRYPTION    │              │
│  └───────────────┘ └────────────────┘              │
│                                                     │
│  Current Role: WIZARD | Logs: Centralized          │
│  Backup: v1.0.4.1 | Data: Role-Separated    │
└─────────────────────────────────────────────────────┘
```

### Data Architecture
Following the reorganization principles:
- **Role-based separation**: Each role has dedicated data spaces
- **Centralized logging**: All logs organized by role in `uMEMORY/log/`
- **Secure backup storage**: Encryption and centralized location
- **Clean terminology**: Consistent use of `get`, `role`, and `log` naming

---

## Getting Started Quickly

### What's New

#### Data Organization
uDOS introduces **comprehensive data reorganization**:
- **Centralized Logging**: All logs moved to `uMEMORY/log/` with role-specific organization
- **Role-Based Data**: Complete separation of data by role in `uMEMORY/role/`
- **Backup System**: Centralized storage with encryption and retention policies
- **Clean Architecture**: Streamlined structure with consistent terminology

#### 8-Role Security System
**Complete role hierarchy** with security-focused additions:
- **Knight (Level 5)**: New security operations role for threat protection and access control
- **Crypt (Level 1)**: New encryption vault role for cryptographic operations only
- **Role hierarchy**: Each role has specific permissions and data separation
- **Role switching**: Dynamic role management with proper user identity handling

#### Terminology Standardization
**Consistent naming** throughout the system:
- **get** (formerly datagets): Simplified configuration files
- **role** (formerly modes): User roles and permission levels
- **log** (formerly logging): Centralized logging directories
- **Backup integration**: Role-aware backup policies and encryption requirements

---

## Getting Started

### First Time Setup

When you start uDOS, the system automatically:

1. **Initializes role-based architecture** with centralized data organization
2. **Sets up current role** (default: wizard) with proper user identity
3. **Configures centralized logging** in `uMEMORY/log/` with role separation
4. **Enables backup system** with encryption and retention policies
5. **Loads uCode script library** with consistent `get`/`role`/`log` terminology

### [ ] Role Management Commands

```ascii
┌─── ROLE SYSTEM COMMANDS ───────────────────────────┐
│                                                     │
│  ROLE             [ ] Show current role and level   │
│  ROLE SWITCH      [ ] Change to different role      │
│  ROLE LIST        [ ] List available roles          │
│  ROLE INFO        [ ] Detailed role information     │
│  GET              [ ] Show role configuration       │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─── BACKUP COMMANDS ───────────────────────┐
│                                                     │
│  BACKUP CREATE    * Create encrypted backup         │
│  BACKUP LIST      [ ] List available backups        │
│  BACKUP RESTORE   * Restore from backup             │
│  BACKUP STATUS    [ ] Show backup system status     │
│  BACKUP CLEANUP   * Remove old backups              │
│                                                     │
└─────────────────────────────────────────────────────┘

### Architecture

uDOS features a comprehensive role-based design:

#### uMEMORY Reorganization
- **Centralized logging** in `uMEMORY/log/` with role-specific subdirectories
- **Role data separation** in `uMEMORY/role/` for clean organization
- **Backup system** with encryption and centralized storage
- **Terminology consistency** using get/role/log naming

#### 8-Role Security Architecture
Located in `/uMEMORY/role/` with complete separation:

| Role | Level | Purpose | Key Features |
|------|-------|---------|--------------|
| `wizard` | 10 | Full system access | Complete administration rights |
| `sorcerer` | 8 | Advanced scripting | System configuration and automation |
| `imp` | 6 | File manipulation | Data management and file operations |
| `knight` | 5 | Security operations | Threat protection and access control |
| `ghost` | 4 | System monitoring | Transparency and system observation |
| `drone` | 3 | Automated tasks | Background processes and automation |
| `tomb` | 2 | Archive operations | Long-term storage and archiving |
| `crypt` | 1 | Encryption vault | Cryptographic operations only |

#### Backup System
```
backup/
├── backup-metadata.json          # Centralized backup tracking
├── backup-index.json            # Backup file indexing
├── migration-*.json             # Migration logs
└── *.tar.gz.enc                # Encrypted backup archives
```

---

## System Architecture

### (M) Core Components

#### uMEMORY - Centralized Data Management
```
uMEMORY/
├── system/                    # Core system data
├── log/                       # Centralized logging
│   ├── errors/{role}/        # Role-specific error logs
│   ├── debug/{role}/         # Role-specific debug logs
│   ├── daily/{role}/         # Role-specific daily logs
│   ├── missions/{role}/      # Role-specific mission logs
│   ├── milestones/{role}/    # Role-specific milestone logs
│   ├── moves/{role}/         # Role-specific move logs
│   └── legacy/               # Legacy data migration
├── role/                     # Role-based data separation
│   ├── wizard/               # Level 10 - Full access
│   ├── sorcerer/             # Level 8 - Advanced tools
│   ├── imp/                  # Level 6 - File operations
│   ├── knight/               # Level 5 - Security operations
│   ├── ghost/                # Level 4 - System monitoring
│   ├── drone/                # Level 3 - Automation
│   ├── tomb/                 # Level 2 - Archiving
│   └── crypt/                # Level 1 - Encryption
└── shared/                   # Shared resources
    ├── templates/
    ├── utilities/
    └── cache/
```

#### sandbox - Role-Specific Configuration
```
sandbox/
├── backup/                   # Centralized backup configs
├── role/                     # Role-specific user files
│   ├── wizard/user.md       # Role-specific identities
│   ├── sorcerer/user.md     # Each role has its own config
│   └── {role}/user.md       # Dynamic role support
├── current-role.conf         # Active role tracking
├── user.md                   # Current user (symlink)
└── shared/                   # Shared resources
    ├── scripts/
    ├── tasks/
    └── get/
```

### * Role Management Flow

1. **User Input** → System determines current role from `sandbox/current-role.conf`
2. **Role Validation** → Check role permissions and access levels
3. **Data Routing** → Route to role-specific data in `uMEMORY/role/{role}/`
4. **Logging** → Log activity to `uMEMORY/log/{category}/{role}/`
5. **Result Display** → Format output according to role permissions

### [ ] Backup Flow

1. **Backup Request** → System checks role permissions and encryption requirements
2. **Data Collection** → Gather role-specific data from appropriate directories
3. **Encryption** → Apply AES-256-CBC encryption if required by role policy
4. **Storage** → Store in centralized `/backup/` directory with metadata
5. **Indexing** → Update backup index and metadata for tracking

---

## Security & Backup System

### * KNIGHT Role - Security Operations (Level 5)

The KNIGHT role provides comprehensive security management:

```bash
# Security Monitoring
KNIGHT monitor threats      # Monitor system threats
KNIGHT scan vulnerabilities # Vulnerability scanning
KNIGHT check firewall      # Firewall status and rules

# Access Control
KNIGHT manage access       # User access management
KNIGHT audit permissions   # Permission auditing
KNIGHT review logs         # Security log analysis

# Encryption Management
KNIGHT encrypt data        # Data encryption operations
KNIGHT manage keys         # Cryptographic key management
KNIGHT verify signatures   # Digital signature verification
```

### (Secure) CRYPT Role - Encryption Vault (Level 1)

The CRYPT role provides secure cryptographic operations:

```bash
# Encryption Operations
CRYPT encrypt "file"       # Encrypt files with AES-256
CRYPT decrypt "file.enc"   # Decrypt encrypted files
CRYPT hash "data"          # Generate cryptographic hashes

# Key Management
CRYPT generate key         # Generate new encryption keys
CRYPT store key "name"     # Store keys in secure vault
CRYPT retrieve key "name"  # Retrieve keys from vault

# Vault Operations
CRYPT status               # Show vault status
CRYPT backup               # Backup vault (encrypted only)
CRYPT verify               # Verify vault integrity
```

### * Backup System

The backup system now includes role-aware features:

```bash
# Backup Operations
BACKUP create [role]       # Create role-specific backup
BACKUP list [role]         # List backups for specific role
BACKUP restore "backup"    # Restore with role validation
BACKUP encrypt "backup"    # Add encryption to existing backup

# Advanced Features
BACKUP migrate from-old    # Migrate from old backup format
BACKUP verify "backup"     # Verify backup integrity
BACKUP cleanup old        # Remove old backups per retention policy
BACKUP metadata           # Show backup metadata and statistics
```

---

## ASSIST Mode Enhancement

### (M) AI-Powered Task Management

ASSIST mode now integrates with the sandbox task system:

#### Task Creation
```bash
# Create ASSIST mode task
ASSIST CREATE TASK "Implement new feature"

# Natural language task creation
ASSIST "I need help organizing my development workflow"
```

#### Task Management
Tasks are stored in the sandbox with standard naming:
```
sandbox/tasks/assist-mode/uTASK-20250816-1600-28-00AI01.md
```

#### ASSIST Integration Points
- **Development Sessions**: AI assists with coding workflows
- **Documentation**: Automated documentation generation
- **Code Review**: AI code analysis
- **Task Automation**: Intelligent task scheduling

---

## Dashboard

### [ ] Multi-Role Dashboard

The dashboard reflects the role-based architecture:

```ascii
┌─── uDOS MULTI-ROLE DASHBOARD ──────────────────┐
│                                                        │
│  *  Architecture: Multi-Role [ ] Date: 2025-08-22     │
│  (M) Current: WIZARD         [ ] Uptime: 2h 34m       │
│                                                        │
│  [ ] Role System Status       * Backup System │
│  ══════════════════           ═══════════════════       │
│  WIZARD   (10) [x]            Centralized    [x]      │
│  SORCERER (8)  [x]            Encrypted      [x]      │
│  IMP      (6)  [x]            Metadata       [x]      │
│  KNIGHT   (5)  [x]            Role-Aware     [x]      │
│  GHOST    (4)  [x]                                    │
│  DRONE    (3)  [x]            * Centralized Logging    │
│  TOMB     (2)  [x]            ═══════════════════       │
│  CRYPT    (1)  [x]            Errors: By Role [x]     │
│                               Debug: By Role  [x]      │
│  [ ] Data Organization        Daily: By Role  [x]     │
│  ═══════════════════          Mission Logs   [x]      │
│  uMEMORY: Reorganized [x]     Clean Structure [x]     │
│  Logs: Centralized    [x]                             │
│  Backup: System       [x]     * Terminology    │
│  Roles: 8 Levels      [x]     ═══════════════════      │
│                               get (not datagets) [x]   │
│                               role (not modes)   [x]   │
│                               log (not logging)  [x]   │
└────────────────────────────────────────────────────────┘
```

### * Dashboard Commands
```bash
DASH                    # Main multi-role dashboard
DASH ROLES              # Role hierarchy overview
DASH BACKUP             # Backup status
DASH LOGS              # Centralized logging status
DASH SECURITY          # Knight and Crypt role status
```

---

## Data & Role Management

### (M) Data Management

The data system provides role-based organization:

```bash
# Role-Based Data Access
DATA list [role]                     # List data for specific role
DATA search "keyword" [role]         # Search within role data
DATA organize                        # Auto-organize by role hierarchy
DATA migrate "from-role" "to-role"   # Migrate data between roles

# Centralized Logging
LOG view [role] [category]           # View logs by role and category
LOG search "pattern" [role]          # Search logs for specific role
LOG analyze [role]                   # Analyze log patterns by role
LOG archive [role] [date]            # Archive old logs by role

# Shortcode Examples
[DATA|LIST] wizard                   # Quick data listing for wizard
[LOG|VIEW] knight errors             # Quick error log view for knight
[DATA|SEARCH] "security" knight      # Quick security search in knight data
```

### * Role Management

The role system handles 8 levels with security focus:

```bash
# Role Operations
ROLE status                          # Show current role and permissions
ROLE switch "target-role"            # Switch to different role
ROLE permissions [role]              # Show role permissions
ROLE hierarchy                       # Display complete role hierarchy

# Role Data Management
ROLE backup "role-name"              # Backup specific role data
ROLE restore "role-name" "backup"    # Restore role from backup
ROLE clean "role-name"               # Clean temporary role data
ROLE migrate "source" "target"       # Migrate between roles

# Security Role Operations
ROLE security status                 # Security roles (knight/crypt) status
ROLE encrypt "role-name"             # Enable encryption for role
ROLE audit "role-name"               # Audit role permissions and access

# Shortcode Examples
[ROLE|STATUS]                        # Quick role status
[ROLE|SWITCH] knight                 # Quick switch to knight role
[ROLE|BACKUP] wizard                 # Quick wizard backup
```

---

## Command Reference

### * Core System Commands

| Command | Description | Example |
|---------|-------------|---------|
| `STATUS` | System overview and role status | `STATUS` |
| `HELP` | Complete command reference | `HELP` |
| `EXIT` | Clean system shutdown | `EXIT` |
| `RESTART` | Restart uDOS session | `RESTART` |
| `ROLE` | Role management and switching | `ROLE switch knight` |

### * Role Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ROLE` | Role management | `ROLE switch sorcerer` |
| `DATA` | Role-based data access | `DATA list wizard` |
| `LOG` | Centralized logging | `LOG view knight errors` |
| `BACKUP` | Backup system | `BACKUP create knight` |
| `KNIGHT` | Security operations | `KNIGHT monitor threats` |
| `CRYPT` | Encryption vault | `CRYPT encrypt secrets.txt` |
| `GET` | Role configuration | `GET wizard` |

### [ ] Role-Specific Commands

| Role | Level | Commands | Example |
|------|-------|----------|---------|
| `wizard` | 10 | All commands available | `wizard deploy production` |
| `sorcerer` | 8 | Advanced scripting | `sorcerer configure system` |
| `imp` | 6 | File operations | `imp organize files` |
| `knight` | 5 | Security operations | `knight scan vulnerabilities` |
| `ghost` | 4 | System monitoring | `ghost monitor processes` |
| `drone` | 3 | Automation tasks | `drone schedule backup` |
| `tomb` | 2 | Archive operations | `tomb archive old-data` |
| `crypt` | 1 | Encryption only | `crypt encrypt vault-data` |

---

## Advanced Features

### * Role Security System

#### Comprehensive Role Hierarchy
```bash
# Role Information
ROLE hierarchy                   # Show complete 8-role hierarchy
ROLE info knight               # Detailed information about Knight role
ROLE permissions crypt          # Show Crypt role permissions
ROLE security status            # Security roles status

# Role Switching with Security
ROLE switch knight              # Switch to Knight security role
ROLE switch crypt              # Switch to Crypt encryption role
ROLE validate "target-role"     # Validate role switch permissions
ROLE audit current             # Audit current role access
```

#### Security-Focused Operations
```bash
# Knight Role Security Management
KNIGHT scan system             # Full system security scan
KNIGHT monitor real-time       # Real-time threat monitoring
KNIGHT access review           # Review access permissions
KNIGHT firewall status         # Firewall configuration and status

# Crypt Role Encryption Management
CRYPT vault status            # Show encryption vault status
CRYPT secure "sensitive-data" # Encrypt sensitive data
CRYPT keys list               # List available encryption keys
CRYPT integrity check         # Verify vault integrity
```

### (Secure) Backup & Data Protection

#### Role-Aware Backup System
```bash
# Advanced Backup Operations
BACKUP create wizard --encrypt        # Create encrypted wizard backup
BACKUP restore knight "backup-name"   # Restore knight role data
BACKUP schedule daily knight         # Schedule daily knight backups
BACKUP policy show crypt             # Show crypt backup policy

# Cross-Role Backup Management
BACKUP migrate wizard sorcerer       # Migrate data between roles
BACKUP compare "backup1" "backup2"   # Compare backup differences
BACKUP verify integrity "backup"     # Verify backup integrity
BACKUP export "backup" encrypted     # Export with additional encryption
```

#### Centralized Data Organization
```bash
# Data Management
DATA organize by-role                # Organize all data by role hierarchy
DATA migrate legacy                  # Migrate legacy data to new structure
DATA clean orphaned                  # Remove orphaned data files
DATA index rebuild                   # Rebuild data index system

# Logging & Audit Management
LOG centralize all                   # Ensure all logs are centralized
LOG audit knight                     # Audit knight role activities
LOG security report                  # Generate security activity report
LOG cleanup by-retention             # Clean logs per retention policies
```

### [ ] Monitoring & Analytics

#### Multi-Role System Health Monitoring
- **Role-Based Performance**: Track performance by role level and permissions
- **Centralized Logging**: Monitor all logs from unified `uMEMORY/log/` location
- **Security Analytics**: Dedicated monitoring for Knight and Crypt roles
- **Backup Efficiency**: Track backup performance and encryption overhead

#### Security Analytics
- **Role Switch Auditing**: Monitor role switching patterns and security
- **Permission Tracking**: Track role permissions and access patterns
- **Encryption Usage**: Monitor Crypt role encryption operations
- **Security Incident**: Knight role threat detection and response tracking

#### Data Organization Metrics
- **Storage Efficiency**: Monitor role-based data organization benefits
- **Migration Success**: Track legacy data migration and cleanup progress
- **Retention Compliance**: Monitor backup retention policy compliance
- **Centralization Benefits**: Measure improvements from centralized logging

---

## Troubleshooting

### * Common Issues

#### Role Management Problems
```
❌ Cannot switch to target role
✅ Solution: Check role permissions with ROLE permissions command
✅ Solution: Verify role exists with ROLE hierarchy command
✅ Solution: Ensure proper role configuration with GET command
```

#### Centralized Logging Issues
```
❌ Logs not appearing in expected location
✅ Solution: Check centralized logging in uMEMORY/log/{category}/{role}/
✅ Solution: Verify current role with ROLE status command
✅ Solution: Use LOG centralize all to ensure proper logging setup
```

#### Backup Problems
```
❌ Backup creation fails with encryption
✅ Solution: Verify role encryption requirements in backup config
✅ Solution: Check password in role-specific user.md file
✅ Solution: Use BACKUP policy show [role] to check requirements
```

#### Security Role Access
```
❌ Cannot access Knight or Crypt role functions
✅ Solution: Ensure proper role switch with ROLE switch knight/crypt
✅ Solution: Verify security role permissions with ROLE security status
✅ Solution: Check role installation with GET knight/crypt commands
```

### * Diagnostic Commands

```bash
STATUS                      # Core system and role overview
ROLE status                 # Current role and permissions
DASH ROLES                  # Role hierarchy status
BACKUP status               # Backup system status
LOG centralize verify       # Verify centralized logging setup
[DATA|STATUS]              # Quick data organization status
[ROLE|HIERARCHY]           # Quick role hierarchy display
```

---

## Best Practices

### * Architecture
1. **Use role-based access** for proper data separation and security
2. **Leverage centralized logging** for better system monitoring and debugging
3. **Apply role-specific backups** with appropriate encryption for sensitive roles
4. **Monitor role switching** to ensure proper security and access control

### * Data & Security Management
1. **Organize data by role** for cleaner separation and faster access
2. **Use centralized logging** to consolidate all system activity tracking
3. **Implement security roles** (Knight/Crypt) for sensitive operations
4. **Regular backup validation** with role-specific retention policies

### (Secure) Security Best Practices
1. **Switch to Knight role** for security operations and threat monitoring
2. **Use Crypt role** for encryption operations and sensitive data handling
3. **Monitor role permissions** regularly with ROLE audit commands
4. **Encrypt sensitive backups** using backup system with passwords

### * Development & Operations Workflow
1. **Start with ROLE status** to verify current permissions and access
2. **Use centralized logging** with LOG commands for better debugging
3. **Create role-specific backups** before making significant changes
4. **Validate data organization** with DATA commands for clean structure

---

### * Role & Data Architecture

### * Role-Based Data Organization

uDOS features a comprehensive role-based architecture:

#### Role System (8 Levels)
- **WIZARD (10)**: Complete system administration with full access to all functions
- **SORCERER (8)**: Advanced system configuration and scripting capabilities
- **IMP (6)**: File system manipulation and comprehensive data management
- **KNIGHT (5)**: Security operations, threat monitoring, and access control
- **GHOST (4)**: System monitoring, transparency, and process observation
- **DRONE (3)**: Automated tasks, background processes, and scheduled operations
- **TOMB (2)**: Archive operations, long-term storage, and data preservation
- **CRYPT (1)**: Encryption vault, cryptographic operations, and secure storage

#### Centralized Data Architecture
Each role follows consistent data organization in `uMEMORY/role/{role}/`:

```
role/{role}/
├── setup/                    # Role configuration
│   ├── GET                  # Role configuration file
│   ├── installation.id      # Unique role installation ID
│   └── setup-vars.sh        # Environment variables
├── user/                    # Role-specific user data
│   ├── missions/            # Role-specific missions
│   ├── milestones/          # Role-specific milestones
│   ├── moves/               # Role-specific moves
│   ├── sessions/            # Role-specific sessions
│   └── preferences/         # Role-specific preferences
├── log/                     # Role-specific logging (deprecated - moved to centralized)
└── cache/                   # Role-specific cache data
```

### * Centralized Logging System

All logging now centralized in `uMEMORY/log/` with role separation:

```
log/
├── errors/{role}/           # Role-specific error logs
├── debug/{role}/            # Role-specific debug logs
├── daily/{role}/            # Role-specific daily activity logs
├── missions/{role}/         # Role-specific mission logs
├── milestones/{role}/       # Role-specific milestone logs
├── moves/{role}/            # Role-specific move logs
└── legacy/                  # Legacy data migration area
```

### [ ] Backup Integration

Role-aware backup system with security features:

```
backup/
├── backup-metadata.json     # Centralized backup tracking
├── backup-index.json       # Backup file indexing system
├── migration-*.json        # Data migration tracking
└── {backup-files}.tar.gz.enc  # Encrypted backup archives
```

Each role has specific backup policies:
- **Encryption requirements**: Crypt, Knight, Tomb require encryption
- **Retention policies**: Different retention periods by role level
- **Access control**: Role-specific backup and restore permissions
- **Migration support**: Legacy backup format migration capabilities

---

## Support & Resources

### [ ] Documentation
- **Architecture Guide**: `/docs/ARCHITECTURE.md` - Complete system architecture with role hierarchy
- **uMEMORY Guide**: `/docs/uMEMORY-Reorganization-Complete.md` - Comprehensive data reorganization
- **Style Guide**: `/docs/Style-Guide.md` - Coding and documentation standards with terminology
- **Backup Guide**: Backup system documentation with encryption and role policies

### * Core System Tools
- **Role Management**: Role switching, permissions, and hierarchy management
- **Backup System**: `/backup/` centralized storage with encryption and metadata
- **Centralized Logging**: `/uMEMORY/log/` organization with role-specific subdirectories
- **Data Organization**: `/uMEMORY/role/` structure for clean role-based separation

### * Security & Operations
- **Knight Role**: Security operations, threat monitoring, and access control
- **Crypt Role**: Encryption vault, cryptographic operations, and secure storage
- **Backup**: Password encryption with AES-256-CBC for sensitive data
- **Audit System**: Role-based activity tracking and security monitoring

### * Community & Support
- **GitHub Repository**: uDOS project repository with multi-role architecture
- **Development Discussions**: Community development forum for role system
- **Issue Tracking**: Bug reports and feature requests for role-based functionality
- **Knowledge Base**: Community-contributed documentation for multi-role operations

### * Quick Reference Commands
```bash
# System Overview
STATUS                  # Complete system health and role status
ROLE status            # Current role and permissions overview

# Role Management
ROLE hierarchy         # Complete 8-role hierarchy display
ROLE switch knight     # Switch to Knight security role

# Features
BACKUP status          # Backup system status
LOG centralize verify  # Verify centralized logging setup
KNIGHT monitor         # Security monitoring (Knight role)
CRYPT vault status     # Encryption vault status (Crypt role)
```


---

**Notes**

This guide is designed to be read like the early home computer manuals — direct, practical, and a little nostalgic. Explore, make mistakes, and enjoy learning uDOS.

---

**Document Status**: Production Ready - Multi-Role Architecture v1.0.4.1
**Version**: v1.0.4.1 Development
**Last Updated**: August 26, 2025
**Next Review**: September 26, 2025

---

*uDOS v1.0.4.1 User Guide - Universal Device Operating System*
*Multi-Role Architecture • Centralized Logging • Backup System • Security Roles*
