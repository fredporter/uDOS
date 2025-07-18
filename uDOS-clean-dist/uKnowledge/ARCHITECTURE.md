# 🏗️ uDOS Architecture Reorganization Guide

## Overview

uDOS v1.7.0 introduces a major architectural reorganization that clarifies the separation between system components and user content. This guide explains the new structure and migration process.

## 🎯 New Architecture Principles

### 📚 uKnowledge - Central Shared Knowledge Bank
- **Purpose**: System documentation that doesn't update with user info
- **Contents**: Roadmap documents, package docs, AI guides, system maps
- **Characteristics**: Read-only for users, version-controlled system knowledge

### 🧠 uMemory - User Content Storage
- **Purpose**: All user content storage, including user scripts
- **Contents**: Missions, moves, logs, user scripts, templates, sandbox
- **Characteristics**: User-writable, personal data, backed up/synced

### ⚙️ uCode - Complete Command Centre  
- **Purpose**: System command and control interface
- **Contents**: Shell scripts, utilities, package integrations
- **Characteristics**: System control layer, CLI interface

### 🔧 uScript - System Script Execution
- **Purpose**: System scripts and bash execution environment
- **Contents**: Core system scripts, utilities, automation tools
- **Characteristics**: System-level execution, not user scripts

### 📋 uTemplate - System Templates & Datasets
- **Purpose**: System templates, datasets, and variables
- **Contents**: Read-only templates, system datasets, configuration
- **Characteristics**: User customizations go to uMemory/templates/

## 📁 Directory Structure

```
uDOS/
├── uKnowledge/               # 📚 Shared knowledge (system)
│   ├── roadmap/             # System roadmap documents
│   ├── packages/            # Package documentation  
│   ├── companion/           # AI assistance guides
│   ├── general-library/     # General documentation
│   └── maps/                # System maps
│
├── uMemory/                 # 🧠 User content storage
│   ├── user/                # User identity and settings
│   ├── scripts/             # User-created scripts
│   ├── templates/           # User-customized templates
│   ├── sandbox/             # User workspace
│   ├── missions/            # User missions
│   ├── milestones/          # User milestones
│   ├── legacy/              # User legacy items
│   ├── logs/                # User activity logs
│   └── state/               # User state data
│
├── uCode/                   # ⚙️ Command centre
│   ├── ucode.sh            # Main shell interface
│   ├── packages/           # Package integration scripts
│   └── *.sh                # System utilities
│
├── uScript/                 # 🔧 System scripts
│   ├── system/             # Core system scripts
│   ├── utilities/          # Utility scripts  
│   ├── automation/         # Automation scripts
│   ├── examples/           # Example scripts
│   └── extract/            # Data extraction tools
│
└── uTemplate/              # 📋 System templates
    ├── system/             # System templates
    ├── datasets/           # System datasets
    └── variables/          # System variables
```

## 🔄 Migration Process

### Automatic Migration
Run the reorganization script:
```bash
./uCode/reorganize.sh
```

This script will:
1. Create the new directory structure
2. Move existing content to appropriate locations
3. Update file paths in system scripts
4. Preserve all user data and content

### Manual Updates Required
After running the reorganization:

1. **Update custom scripts** that reference old paths
2. **Check user identity** location: `uMemory/user/identity.md`
3. **Verify user scripts** are in: `uMemory/scripts/`
4. **Review templates** in: `uMemory/templates/`

## 🔧 System Updates

### uCode Shell Changes
- User identity now in: `uMemory/user/identity.md`
- Sandbox moved to: `uMemory/sandbox/`
- Enhanced help shows new architecture

### VS Code Tasks
- New task: "🏗️ Reorganize uDOS"
- Updated search paths to reflect new structure
- Package tasks updated for new architecture

### Path References Updated
- All system scripts now reference correct paths
- Environment variables updated
- Log paths corrected

## ✅ Benefits of Reorganization

### Clear Separation of Concerns
- **System vs User**: Clear distinction between system and user content
- **Read-Only vs Writable**: System knowledge vs user memory
- **Shared vs Personal**: Documentation vs user data

### Improved Organization
- **Logical Grouping**: Related files grouped by purpose
- **Scalability**: Structure supports growth and new features
- **Maintainability**: Easier to update system vs user content

### Enhanced Security
- **Isolation**: User content isolated from system files
- **Backup Strategy**: Clear understanding of what to backup
- **Version Control**: System docs separate from user data

## 🚀 Next Steps

1. **Test the new structure**: Run `./uCode/ucode.sh`
2. **Update any custom scripts**: Check for old path references
3. **Verify migrations**: Ensure all content migrated correctly
4. **Update documentation**: Any custom docs with old paths

## 📋 Compatibility

- **Backward Compatibility**: Old paths are migrated automatically
- **VS Code Integration**: All tasks updated for new structure
- **Package System**: Packages work with new organization
- **AI Integration**: GitHub Copilot aware of new structure

---

This reorganization creates a more maintainable, scalable, and logical structure for uDOS while preserving all existing functionality and user data.
