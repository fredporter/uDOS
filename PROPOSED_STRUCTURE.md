# uDOS v1.4 Structure - DEV/Sandbox/uMEMORY + Browser-UI

## Overview
uDOS v1.4 introduces a comprehensive restructuring with protected development environments, flushable user workspaces, persistent memory archives, and a modern Browser-UI system.

## Core Architectural Principles

### 🔧 **Protected DEV Environment**
- **Purpose**: Core uDOS system development (Wizard + DEV mode only)
- **Location**: `/dev/` - Never flushed, persistent development workspace
- **Access**: Restricted to Wizard role with DEV mode activated

### 🚀 **Flushable Sandbox Workspace**
- **Purpose**: User development, testing, experimentation (all roles)
- **Location**: `/sandbox/` - Designed to be flushed at session end
- **Flow**: Active work → Archive to uMEMORY → Flush → Fresh workspace

### 🧠 **Persistent Memory Archives**
- **Purpose**: Long-term storage of role/user data and session archives
- **Location**: `/uMEMORY/` - Permanent storage, never flushed
- **Organization**: Role-specific and user-specific memory isolation

### 🌐 **Browser-UI System** (NEW in v1.4)
- **Purpose**: Modern web interface for uDOS with full terminal compatibility
- **Location**: `/uNETWORK/display/` - Complete browser-based experience
- **Features**: Terminal emulation, memory browsing, visual session management

## Directory Structure

```
uDOS/
├── dev/                        # 🔧 CORE uDOS DEVELOPMENT (Protected)
│   ├── README.md              # ✅ DEV mode guide
│   ├── active/                # 🚫 Local (persistent core dev work)
│   ├── scripts/               # 🚫 Local (core system scripts)
│   ├── tools/                 # ✅ Framework + 🚫 Local tools
│   ├── templates/             # ✅ Core templates
│   ├── vscode-extension/      # ✅ Framework + 🚫 Local dev
│   └── workflow-manager.sh    # ✅ Core workflow tools
├──
├── sandbox/                   # 🚀 USER WORKSPACE (Flushable)
│   ├── README.md             # ✅ User workspace guide
│   ├── current-session.md    # 🚫 Local (FLUSHABLE)
│   ├── scripts/              # 🚫 Local (FLUSHABLE user scripts)
│   ├── experiments/          # 🚫 Local (FLUSHABLE experiments)
│   ├── tasks/                # 🚫 Local (FLUSHABLE current tasks)
│   ├── sessions/             # 🚫 Local (FLUSHABLE → archived)
│   │   ├── README.md         # ✅ Session system guide
│   │   ├── current/          # 🚫 Active session data
│   │   └── archive/          # 🚫 Pre-archive staging
│   └── logs/                 # 🚫 Local (FLUSHABLE → archived)
├──
├── uMEMORY/                  # 🧠 MEMORY ARCHIVE SYSTEM
│   ├── README.md             # ✅ Memory system guide
│   ├── role/                 # 🚫 Local (role memory archives)
│   │   ├── README.md         # ✅ Role memory guide
│   │   ├── wizard/           # 🚫 Wizard role memory
│   │   ├── sorcerer/         # 🚫 Sorcerer role memory
│   │   └── [other roles]/    # 🚫 Role-specific archives
│   ├── user/                 # 🚫 Local (user memory archives)
│   │   └── README.md         # ✅ User memory guide
│   ├── core/                 # ✅ Core memory templates
│   └── system/               # ✅ System memory
├──
├── uNETWORK/                 # 🌐 NETWORK & BROWSER-UI
│   ├── display/              # 🌐 NEW: Browser-UI System
│   │   ├── README.md         # ✅ Browser-UI guide
│   │   ├── ui_server.py      # ✅ Main UI server
│   │   ├── components/       # ✅ UI components framework
│   │   ├── assets/           # ✅ Static assets (CSS, JS)
│   │   ├── templates/        # ✅ HTML templates
│   │   ├── api/              # ✅ REST API endpoints
│   │   └── static/           # 🚫 Generated assets
│   └── server/               # ✅ Network server components
├──
├── uCORE/                    # ✅ Core system (protected)
├── docs/                     # ✅ Documentation
├── extensions/               # ✅ Extension framework
└── [other core folders]/     # ✅ Distribution framework
```
│   ├── wizard/                # Wizard role data (if installed)
│   │   ├── projects/          # Wizard-specific projects
│   │   ├── sessions/          # Development sessions
│   │   ├── notes/             # Role-specific notes
│   │   └── config/            # Role configuration
│   ├── sorcerer/              # Sorcerer role data (if installed)
│   ├── imp/                   # Imp role data (if installed)
│   └── [other roles as installed]
│
├── USER/                      # ✨ NEW: User-specific data isolation
│   ├── memory/                # Personal uMEMORY data
│   │   ├── missions/          # User missions
│   │   ├── moves/             # User activity logs
│   │   ├── milestones/        # User achievements
│   │   └── sessions/          # User sessions
│   ├── sandbox/               # Personal sandbox data
│   │   ├── experiments/       # User experiments
│   │   ├── projects/          # Sandbox projects
│   │   ├── logs/              # Activity logs
│   │   └── temp/              # Temporary files
│   ├── dev/                   # Personal development data
│   │   ├── notes/             # Development notes
│   │   ├── briefings/         # AI briefings
│   │   ├── roadmaps/          # Personal roadmaps
│   │   └── config/            # Dev configuration
│   └── extensions/            # User-installed extensions
│
└── BACKUP/                    # ✨ NEW: Centralized backup system
    ├── daily/                 # Daily backups
    ├── weekly/                # Weekly backups
    ├── migrations/            # Migration backups
    ├── role-configs/          # Role configuration backups
    ├── user-data/             # User data backups
    └── system/                # System backups
```

## 🎯 **Installation Strategy:**

### **Distribution Download (GitHub):**
- Clean, minimal system with core functionality only
- No user data, no role-specific installations
- All install scripts for each role included

### **Role Installation Process:**
1. **Base System**: Always installs core uDOS framework
2. **Role Selection**: User chooses role(s) to install locally
3. **Data Isolation**: Each role installs to `ROLE/[role-name]/`
4. **User Data**: All personal data goes to `USER/`

### **Branch Strategy for Sandbox/Experiments:**
- **main**: Clean distribution
- **experimental**: Active experiments and sandbox content
- **roles/[role-name]**: Role-specific development branches
- **user/[username]**: Personal development branches (optional)

### **Backup Strategy:**
- All backups centralized in `/BACKUP/`
- No `.backup` folders in core directories
- Automated backup organization by type and date
- Migration backups preserved separately

## 🔧 **Updated .gitignore Strategy:**

```ignore
# ══════════════════════════════════════════════════
# uDOS v1.4 Clean Distribution .gitignore
# ══════════════════════════════════════════════════

# Complete local-only exclusions
/ROLE/                         # All role installations (local only)
/USER/                         # All user data (local only)
/BACKUP/                       # All backups (local only)

# Selective core exclusions
dev/USER/                      # User dev data (if any exists)
sandbox/USER/                  # User sandbox data (if any exists)
uMEMORY/user/                  # User memory data
uMEMORY/role/                  # Role-specific memory data

# System exclusions
**/*.log
**/*.tmp
**/*.working
.DS_Store
node_modules/
*.user.*
*.personal.*
```

## 📋 **Migration Plan:**

1. **Restructure current installation**
2. **Move user data to USER/ folders**
3. **Move role data to ROLE/ folders**
4. **Move all backups to BACKUP/**
5. **Update install scripts for new structure**
6. **Test clean distribution download**
7. **Update documentation**

This structure provides:
- ✅ Clean GitHub distribution
- ✅ Logical user/role/system separation
- ✅ Centralized backup management
- ✅ Easy branch management for experiments
- ✅ Simple .gitignore rules
- ✅ Scalable role installation system
