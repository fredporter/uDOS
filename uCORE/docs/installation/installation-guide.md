# 🚀 uDOS Installation System v1.0

**Purpose**: Centralized installation and setup management for uDOS Alpha v1.0.

## 📁 Installation Structure

```
install/
├── README.md           # This file
├── install-udos.sh     # Main installation script
├── setup-wizard.sh     # First-time setup wizard
├── validate-system.sh  # System validation
├── user-provisioning.sh # User role setup
└── assets/            # Installation assets
```

## 🎯 Installation Workflow

### 1. **System Installation**
```bash
./install/install-udos.sh
```
- Validates system requirements
- Creates directory structure  
- Sets up core components
- Installs VS Code extension
- Configures package system

### 2. **User Setup Wizard**
```bash
./install/setup-wizard.sh
```
- First-time user configuration
- Role selection (wizard/sorcerer/ghost/imp)
- Privacy settings
- Initial knowledge base setup
- Sandbox initialization

### 3. **System Validation**
```bash
./install/validate-system.sh
```
- Comprehensive system checks
- Permission validation
- Package installation verification
- Extension functionality test

## 🔐 User Role Provisioning

The installation system supports the complete user role hierarchy:

| Role | Access Level | Permissions |
|------|-------------|-------------|
| **👑 Wizard** | Full system | All uCode, uTemplate, uKnowledge |
| **🧙 Sorcerer** | Developer | uCode backups, limited modifications |
| **👻 Ghost** | Standard | Read uKnowledge, sandbox access |
| **😈 Imp** | Restricted | Sandbox only |

## 🎮 Developer Mode

**Single Developer Mode** includes:
- ✅ Limited backups of modified core scripts (ucode.sh)
- ✅ Ability to modify uKnowledge folder
- ✅ Full access to uTemplates
- ✅ uCode script editing capabilities

**Wizard Mode** (when developer off):
- ✅ Can still run all wizard functions
- ❌ Cannot edit uCode or uTemplate
- ✅ Always maintains uKnowledge read/write access

## 📦 Package Integration

Installation automatically:
- Sets up package management system
- Installs essential tools (nano, ripgrep, fd, bat)
- Creates uCode command mappings
- Configures startup auto-installation

*Installation follows uDOS filename conventions - no complex folder structures required.*
