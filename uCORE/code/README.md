# 🔧 uCode — Unified Command System v1.2

**Purpose**: Minimal, efficient command system for uDOS v1.2 with flat structure design.

---

## 📁 Structure (Minimal & Efficient)

```
uCode/
├── README.md           # This file
├── ucode.sh            # 🌀 Main unified command system
├── log.sh              # 📊 Logging and activity tracking
├── dash.sh             # 📈 Dashboard generation
├── setup.sh            # ⚙️ System setup utilities
├── destroy.sh          # 🧹 System cleanup utilities
├── packages/           # 📦 Package management scripts
└── archive-old/        # 📦 Legacy scripts (archived)
```

---

## 🚀 Core Scripts

### 🌀 `ucode.sh` — Main Command System
**Purpose**: Unified command interface for all uDOS operations
- Interactive mode: `./ucode.sh`
- Command mode: `./ucode.sh COMMAND args`
- Shortcode support: `[COMMAND:args]` format

**Key Features**:
- Flat uMemory integration
- Template processing
- Mission management
- Package operations
- Development tools

### 📊 `log.sh` — Activity Logging
**Purpose**: Track system activity and generate reports
- Move logging with metadata
- Daily activity reports
- Statistics and analytics
- Error tracking

### 📈 `dash.sh` — Dashboard System
**Purpose**: Generate visual dashboards and status reports
- ASCII-based visualizations
- System status overview
- Activity summaries

### ⚙️ `setup.sh` — System Setup
**Purpose**: Initialize and configure uDOS system
- First-time setup
- User configuration
- Directory structure

### 🧹 `destroy.sh` — Cleanup Utilities
**Purpose**: System maintenance and cleanup
- Legacy file archiving
- Temporary file cleanup
- System reset capabilities

---

## 📦 Integration Points

### With uMemory (Flat Structure)
- Direct file access to `$UHOME/uMemory/`
- Standardized naming conventions
- No subdirectory navigation required

### With uTemplate System
- Template processing integration
- Shortcode expansion
- Dynamic content generation

### With uDev System
- Development report creation
- Migration documentation
- System analysis tools

---

## 🎯 Design Principles

### Minimal Complexity
- **5 Core Scripts**: Only essential functionality
- **Flat Integration**: Direct uMemory access
- **Single Entry Point**: ucode.sh handles all commands

### Maximum Efficiency
- **Fast Execution**: Minimal script loading
- **Clear Purpose**: Each script has focused responsibility
- **Modular Design**: Scripts work independently

### User-Friendly
- **Consistent Interface**: All commands through ucode.sh
- **Shortcode Support**: Modern `[COMMAND:args]` syntax
- **Help Integration**: Built-in help system

---

## 🔧 Usage Examples

```bash
# Interactive mode
./uCode/ucode.sh

# Direct commands
./uCode/ucode.sh STATUS
./uCode/ucode.sh MISSION list
./uCode/ucode.sh PACKAGE install ripgrep

# Shortcode format
./uCode/ucode.sh "[MEMORY:list]"
./uCode/ucode.sh "[MISSION:create:test-mission]"
./uCode/ucode.sh "[PACKAGE:install:fd]"

# Logging and reporting
./uCode/log.sh report
./uCode/dash.sh build
```

---

## 📋 Migration from Old System

### Archived Scripts
All legacy scripts moved to `archive-old/` directory:
- Complex multi-file systems consolidated
- Redundant functionality eliminated
- Legacy compatibility maintained in archive

### Functionality Preservation
- All essential features retained in new unified system
- Command compatibility maintained
- Template processing preserved
- Package management enhanced

---

*uCode v1.2 represents a complete redesign focused on simplicity, efficiency, and user experience while maintaining full functionality.*
