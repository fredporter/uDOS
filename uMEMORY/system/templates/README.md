# uDOS Template System

**Location**: `uMEMORY/system/templates/`
**Version**: v2.2
**Reorganized**: August 23, 2025

## 📁 Template Organization

### 🎨 Dashboard/Interface Components
- `uDASH-ascii-dashboard.txt` - Comprehensive ASCII dashboard with metrics and status blocks
- `uDASH-ascii-interface-blocks.md` - Block-oriented interface system with responsive components

### 📋 Document Templates (uDOT)
- `uDOT-project-management.md` - Comprehensive project management template
- `uDOT-mission-brief.md` - Advanced mission management with cross-references and datasets
- `uDOT-package-definition.md` - Package management template with shortcode integration
- `uDOT-milestone-tracker.md` - Milestone tracking template
- `uDOT-legacy-migration.md` - Legacy system compatibility template
- `uDOT-command-help.md` - Command documentation template
- `uDOT-dashboard-layout.md` - Dashboard layout template

### 🤖 Script Templates (uSCT)
- `uSCT-assistant-workflow.md` - Assistant interaction script template

### 📖 Documentation (uDOC)
- `uDOC-command-help.md` - Command documentation template
- `uDOC-dashboard-layout.md` - Dashboard layout template## 🔄 Usage

Templates in this directory are part of the uDOS v1.3.3 template infrastructure. They use:

- **Variable Substitution**: `[get:variable_name]` and `[process:variable_name]`
- **Conditional Logic**: `[conditional:condition]...[/conditional]`
- **Get Integration**: `[get:name.field]` for data retrieval
- **Cross-References**: `[ref:type.id](path)`
- **Shortcode Support**: `[shortcode:args]`
- **Timestamp Functions**: `[timestamp]`, `[date:iso]`, `[date:+7days]`

## 🛠️ Template Processing

Templates are processed by the uDOS v1.3.3 template system which:
1. Resolves all variables and get data
2. Processes conditional logic and functions
3. Generates final documents with proper formatting
4. Integrates with uCORE systems and uMEMORY storage

## 📝 Naming Convention

- **`uDOT-`** = Document templates (content generation)
- **`uSCT-`** = Script templates
- **`uDASH-`** = Dashboard/interface components
- **`uDOC-`** = Documentation/specifications
- **`uDEV-`** = Development tools/builders

### 🔗 Related Directories

- **`/system/get/`** - Interactive forms and data collection (uGET files)
- **`/system/config/`** - Configuration templates (uCFT files)
- **`/system/data/`** - Data files and datasets (uDATA files)

---

*Part of uDOS v1.3.3 Template System Reorganization*
