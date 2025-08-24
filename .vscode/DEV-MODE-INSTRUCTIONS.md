# VS Code DEV Mode Instructions - uDOS v1.4

## Overview
These instructions are for **uDOS core system development** using VS Code in DEV mode. This is restricted to **Wizard role with DEV mode activated** only.

## 🔧 **DEV Mode Access Control**

### Who Can Access DEV Mode
- **Role Required**: Wizard role only
- **Mode Required**: DEV mode must be activated
- **Purpose**: Core uDOS system development and contributions

### What DEV Mode Provides Access To
- **`/dev/` workspace** - Protected core development environment
- **Core system files** - uCORE, uNETWORK, uSCRIPT, etc.
- **Build tools** - System compilation and testing
- **Advanced debugging** - Core system debugging capabilities

## 🚀 **Development Workspace Structure**

### Protected Development Environment (`/dev/`)
```
dev/
├── active/                 # Current core development projects
├── scripts/                # Core system development scripts
├── tools/                  # Development utilities and tools
├── templates/              # Core system templates
├── vscode-extension/       # VS Code extension development
└── workflow-manager.sh     # Core workflow management
```

### User Workspace (`/sandbox/`) - All Roles
```
sandbox/
├── scripts/                # User scripts (FLUSHABLE)
├── experiments/            # User experiments (FLUSHABLE)
├── tasks/                  # Current tasks (FLUSHABLE)
├── sessions/               # Session data (FLUSHABLE → archived)
└── logs/                   # Session logs (FLUSHABLE → archived)
```

## 🛡️ **Development Rules & Safety**

### Protected Areas (Never Flushed)
- **`/dev/`** - Core development work, always persistent
- **`/uCORE/`** - Core system files, protected
- **`/uMEMORY/`** - Memory archives, persistent

### Flushable Areas (Session-Based)
- **`/sandbox/`** - User workspace, designed to be flushed
- Session data archived to `/uMEMORY/` before flushing

### Access Restrictions
- **DEV workspace** - Only accessible with Wizard + DEV mode
- **Core files** - Requires DEV mode for modification
- **System builds** - DEV mode required for compilation

## 🌐 **Browser-UI Integration**

### DEV Mode Browser Interface
- **`/api/dev/*`** endpoints - DEV mode API access
- **Protected UI** - Core development interfaces
- **Build monitoring** - Visual build and test status
- **Code browsing** - Enhanced code navigation

### Terminal Integration
- **Full compatibility** - All terminal commands available in browser
- **Real-time updates** - Live development feedback
- **Session management** - Visual session controls

## 📋 **Development Workflow**

### 1. Activate DEV Mode
```bash
# Ensure you're in Wizard role with DEV mode activated
ucode dev status
```

### 2. Core Development Work
```bash
# Work in protected /dev/ directory
cd dev/active/
# Your core development work here
```

### 3. User/Experimental Work
```bash
# Use sandbox for experimental work
cd sandbox/experiments/
# This area is flushable - archive important work
```

### 4. Build & Test
```bash
# Core system builds (DEV mode required)
./dev/tools/build-system.sh
./dev/tools/test-core.sh
```

### 5. Session Management
```bash
# Archive session data before flushing sandbox
# (Automatic in future implementation)
```

## 🚨 **Important Notes**

### Data Protection
- **Core work** in `/dev/` is always protected
- **Experimental work** in `/sandbox/` may be flushed
- **Archive important discoveries** to `/uMEMORY/` or `/dev/`

### Role Limitations
- **Non-Wizard roles** cannot access `/dev/` or core system files
- **Regular users** work entirely in `/sandbox/` (which is flushable)
- **DEV mode** is required for any core system modifications

### VS Code Configuration
- **Settings** - Configured for uDOS development patterns
- **Extensions** - Core development extensions installed
- **Tasks** - Pre-configured build and test tasks
- **Launch** - Debugging configurations for core system

---

**Remember**: DEV mode is for core uDOS system development only. Regular user development happens in the flushable `/sandbox/` workspace with session archiving to `/uMEMORY/`.
