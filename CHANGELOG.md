# 📝 uDOS Changelog

## [1.7.1] ### 📖 Documentation Updates
- **Architecture Guide**: Complete reorganization documentation
- **Migration Process**: Automatic and manual migration steps
- **Updated References**: All path references updated throughout
- **Version Consistency**: All components updated to v1.7.1

### 🗑️ Cleanup & Modernization
- **REMOVED**: Obsolete `.devcontainer/` Docker configuration
- **REMOVED**: Redundant `.dockerignore` file
- **REMOVED**: Empty `roadmap/` directory from old structure
- **UPDATED**: All version references to v1.7.1
- **UPDATED**: Path references to new architecture
- **UPDATED**: .gitignore for reorganized structure07-13 - The Great Reorganization

### 🏗️ Architectural Restructuring
- **BREAKING**: Complete repository reorganization around clear architectural principles
- **NEW**: `uKnowledge` = Central shared knowledge bank (system docs only)
- **NEW**: `uMemory` = All user content storage (missions, scripts, sandbox)
- **NEW**: `uScript` = System scripts and bash execution environment
- **NEW**: `uTemplate` = System templates and datasets (read-only)
- **ENHANCED**: `uCode` = Complete command centre

### 📁 Directory Structure Changes
- **Moved**: `roadmap/` → `uKnowledge/roadmap/` (system documentation)
- **Moved**: `sandbox/` → `uMemory/sandbox/` (user workspace)
- **Moved**: User scripts → `uMemory/scripts/` (user content)
- **Moved**: System scripts → `uScript/system/` (system execution)
- **Moved**: Templates → `uTemplate/system/` (system templates)
- **Moved**: User identity → `uMemory/user/identity.md`

### ✨ New Features
- **Architecture Migration Script**: `./uCode/reorganize.sh`
- **VS Code Task**: "🏗️ Reorganize uDOS" for easy migration
- **Updated Help System**: Shows new architecture in uCode shell
- **Comprehensive Documentation**: `uKnowledge/ARCHITECTURE.md`

### 🔧 Technical Improvements
- **Clear Separation**: System vs user content completely separated
- **Logical Organization**: Related files grouped by architectural purpose
- **Enhanced Maintainability**: Easier to update system vs user content
- **Improved Security**: User content isolated from system files

### �️ Cleanup & Modernization
- **REMOVED**: Obsolete `.devcontainer/` Docker configuration
- **REMOVED**: Redundant `.dockerignore` file
- **REMOVED**: Empty `roadmap/` directory from old structure
- **UPDATED**: All version references to v1.7.1
- **UPDATED**: Path references to new architecture
- **UPDATED**: .gitignore for reorganized structure

---

## [1.7.0] - 2025-07-13 - The Great Optimization

### 🚀 Major Changes
- **BREAKING**: Removed Docker dependency completely
- **BREAKING**: Eliminated `scripts/` folder (renamed to `uCode/`)
- **NEW**: VS Code native integration with 6 pre-configured tasks
- **NEW**: Modern macOS launcher applications
- **NEW**: Enhanced VS Code + GitHub Copilot workflow

### ✨ Features Added
- VS Code tasks accessible via `Cmd+Shift+P`:
  - 🌀 Start uDOS
  - 🔍 Check uDOS Setup
  - 📊 Generate Dashboard
  - 🌳 Generate File Tree
  - 🧹 Clean uDOS (Destroy)
  - 📝 Create New Mission
- Native macOS app bundles in `launcher/`
- Simplified execution model (no containers)
- Enhanced shell script structure and error handling

### 🔧 Technical Improvements
- Fixed script shebang placement in `uCode/ucode.sh`
- Removed code duplication across shell scripts
- Updated all path references from `scripts/` to `uCode/`
- Corrected filename case sensitivity (`uCode.sh` → `ucode.sh`)
- Streamlined project structure for VS Code development

### 🗂️ File Organization
- Moved Docker components to legacy status
- Cleaned up redundant launcher files
- Updated .gitignore for modern workflow
- Removed unnecessary legacy directories

### 📖 Documentation
- Updated README.md with modern installation instructions
- Created OPTIMIZATION.md with migration strategy
- Enhanced roadmap documentation
- Added comprehensive setup guides

### 🐛 Bug Fixes
- Fixed "No such file or directory" errors in launcher scripts
- Resolved path resolution issues across all scripts
- Corrected VS Code task configurations
- Fixed macOS app bundle Info.plist structure

### 🗑️ Removed
- Docker Compose files and Dockerfile
- Legacy launcher complexity
- Redundant script copies
- Docker-based execution paths

---

## [1.6.1] - 2025-07-05 - Foundation Release

### 📚 Documentation
- Established core roadmap structure
- Created comprehensive uDOS foundation documentation
- Defined development cycle and methodology
- Added markdown templating system

### 🏗️ Architecture
- Defined uMemory, uKnowledge, uScript, uTemplate structure
- Established uCode shell command system
- Created markdown-native file organization
- Built mission/move/milestone tracking system

### 🔧 Core Features
- Basic uDOS shell (`ucode.sh`)
- Dashboard generation system
- File tree generation
- Memory and state tracking
- Template-based content creation

---

## Migration Guide

### From v1.6.1 to v1.7.0

#### For End Users:
1. **New Launch Method**: Use `Cmd+Shift+P` → "🌀 Start uDOS" in VS Code
2. **Alternative**: Double-click `launcher/uDOS-Modern.app`
3. **Terminal**: `./uCode/ucode.sh` (not `./scripts/uCode.sh`)

#### For Developers:
1. **Path Updates**: All `scripts/` references now point to `uCode/`
2. **Docker Removal**: No more `docker-compose up` - native execution only
3. **VS Code Tasks**: Access all uDOS operations via VS Code command palette
4. **Modern Workflow**: Leverage GitHub Copilot for uScript development

#### Breaking Changes:
- `scripts/` folder no longer exists
- Docker launcher removed
- Some shell script entry points changed
- Legacy launcher files removed

---

## Versioning Strategy

uDOS follows semantic versioning:
- **MAJOR**: Breaking changes to core architecture
- **MINOR**: New features, enhancements
- **PATCH**: Bug fixes, documentation updates

Current focus: Stability and VS Code integration for daily use.

---

*This changelog is maintained as part of the uDOS development cycle.*
