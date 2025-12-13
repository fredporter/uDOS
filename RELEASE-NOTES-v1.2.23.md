# uDOS v1.2.23 Release Notes

**Release Date:** December 13, 2025  
**Status:** Production Ready ✅  
**Package Size:** 7.3MB (lite tier)  

---

## 🎉 Major Features

### 📋 Unified Task Management System (1,215 lines)
**Single source of truth** for all tasks and projects in `memory/bank/user/unified_tasks.json`

**Features:**
- Rich task metadata: priorities, tags, dependencies, progress tracking
- Project management with location tracking (TILE codes)
- Automatic migration from legacy task systems
- Filtering by status, project, tags

**Commands:**
```bash
TASK CREATE "description" [--project <id>]
TASK LIST [--project <id>] [--status <status>]
TASK DONE <id>
TASK DELETE <id>
TASK EDIT <id> <field> <value>

PROJECT CREATE "name" [--location <tile>]
PROJECT LIST [--status <status>]
PROJECT STATUS <id>
```

---

### 📝 Compact Filename Standard (455 lines)
**uDOS ID Format:** `YYYYMMDD-HHMMSSTZ-TILE-name.ext`

**Benefits:**
- ✅ Sortable by date/time
- ✅ Globally unique with timezone + location
- ✅ Human-readable (no milliseconds)
- ✅ Compact (no internal dashes in timestamp)

**4 Format Types:**
```bash
20251213-backup.json                    # Date only
20251213-164500UTC-workflow.upy         # Session (with time)
20251213-164500UTC-123-error.json       # Instance (with counter)
20251213-164500UTC-AA340-mission.upy    # Located (with TILE code)
```

**Integration:**
```bash
FILE NEW myfile.txt --dated              # Creates: 20251213-myfile.txt
FILE NEW script.upy --timed              # Creates: 20251213-164500UTC-script.upy
FILE NEW mission.upy --located --tile AA340  # Creates: 20251213-164500UTC-AA340-mission.upy
```

---

### 🔄 Version Control System (319 lines)
**Complete UNDO/REDO** with automatic version history

**Features:**
- Automatic version saving to `.archive/versions/`
- 10 versions per file, 90-day retention (configurable)
- Special handling for critical files (confirmation prompts)
- Version format: `YYYYMMDD_HHMMSS_filename.ext`

**Commands:**
```bash
UNDO <file>                              # Revert to previous version
UNDO --list <file>                       # Show version history
UNDO --to-version <version> <file>       # Revert to specific version
REDO <file>                              # Re-apply undone changes
```

---

### 🗂️ Intelligent File Organization (285 lines)
**Smart TIDY** with duplicate detection and automatic archiving

**Features:**
- MD5-based duplicate detection with interactive resolution
- Old version pattern recognition (`_vN`, `_YYYYMMDD_`, `.bak`, `.old`, `_backup`)
- Date-based organization into monthly folders (`YYYY-MM/`)
- Location-based grouping by TILE codes

**Commands:**
```bash
TIDY [folder]                            # Organize folder intelligently
TIDY --by-date                           # Workspace-wide date organization
TIDY --by-location                       # Group by TILE codes
TIDY --report                            # Dry-run preview
```

---

### 📦 Archive System (569 lines)
**Unified archiving** for tasks, projects, and workflows

**Features:**
- Archives completed tasks from UnifiedTaskManager
- Project archiving with all linked tasks
- Workflow archiving with metadata
- Automatic completion marking and timestamping

**Commands:**
```bash
ARCHIVE task <id>                        # Archive completed task
ARCHIVE project <id>                     # Archive project + tasks
ARCHIVE workflow                         # Archive workflow
ARCHIVE --list                           # Show archived items
```

---

### 🧹 Enhanced CLEAN (250 lines)
**Recursive .archive/ cleanup** with safety features

**Features:**
- CLEAN --archives: Empty all `.archive/` folders recursively
- Interactive confirmation prompts (unless --force)
- Dry-run preview mode (--dry-run)
- Statistics: file count, size, directories scanned

**Commands:**
```bash
CLEAN                                    # Standard cleanup (trash/temp)
CLEAN --archives                         # Clean all .archive/ folders
CLEAN --dry-run                          # Preview what would be cleaned
CLEAN --archives --force                 # Clean archives without prompts
```

---

### 💾 User Content Packaging (600 lines)
**CLONE and BUILD** commands for backup and distribution

**CLONE Command (250 lines):**
- Package user content: docs, drafts, scripts, workflows, settings
- Smart exclusions: `.archive/`, logs, `*.pyc`, `__pycache__`
- Output: `udos-clone-YYYYMMDD_HHMMSS.tar.gz` with `metadata.json`

**BUILD Command (350 lines):**
- Create offline installation packages
- Optional downloads: MeshCore, CoreUI Icons
- Three tiers: lite (7.3MB), standard (~45MB), full (~120MB)
- Output: `udos-build-YYYYMMDD_HHMMSS.tar.gz`

**Commands:**
```bash
CLONE                                    # Package user content
CLONE --check                            # Preview package contents

BUILD --lite                             # Build lite package (7.3MB)
BUILD --full                             # Build full package (~120MB)
BUILD --check                            # Validate build requirements
```

---

## 🐛 Bug Fixes

### Critical Issues Resolved

**1. archive_handler.py - Escaped Quotes**
- **Issue:** `SyntaxError: unexpected character after line continuation`
- **Cause:** Backslash-escaped quotes (`\"`) in 21 locations
- **Fix:** Replaced with normal quotes
- **Commit:** 026ec26

**2. undo_handler.py - UTF-8 Box-Drawing Characters**
- **Issue:** `SyntaxError: invalid character '╔' (U+2554)`
- **Cause:** Box-drawing characters incompatible with Python parser
- **Fix:** Replaced with ASCII equivalents, rewrote `_show_help()` method
- **Commit:** 9be521e

**3. undo_handler.py - Missing Factory Function**
- **Issue:** `ImportError: cannot import name 'create_handler'`
- **Cause:** Missing factory function expected by command router
- **Fix:** Added `create_handler(**kwargs)` factory function
- **Commit:** 1abe292

**4. UNDO/REDO Command Routing**
- **Issue:** Commands not recognized in standard syntax
- **Cause:** Missing routing in `system_handler.py`
- **Fix:** Added `handle_undo()` and `handle_redo()` delegation methods
- **Commit:** 109b86c

---

## 📊 Metrics

### Implementation
- **Total Lines:** 6,205 lines across 8 files
- **New Services:** UnifiedTaskManager (1,215 lines)
- **New Utilities:** FilenameGenerator (455 lines)
- **New Handlers:** UndoHandler (319 lines), enhanced TIDY/CLEAN/ARCHIVE

### Package Size
- **Lite Tier:** 7.3MB (54% under 16MB target) ✅
- **Standard Tier:** ~45MB (with web extensions)
- **Full Tier:** ~120MB (with optional repos)

### Testing
- **Automated Tests:** 5 new tests
- **Manual Tests:** 18 test cases
- **SHAKEDOWN Suite:** 184 checks passing
- **Total Coverage:** 50+ tests passing

### Documentation
- **Wiki Pages:** 1,700 lines across 5 pages
  - Task-Management.md (650 lines)
  - Filename-Convention.md (420 lines)
  - Archive-System.md (+250 lines)
  - Installation-Guide.md (380 lines)
- **CHANGELOG:** Complete v1.2.23 entry
- **README:** Updated with package tiers

---

## 🔄 Migration Guide

### From v1.2.22 to v1.2.23

**Automatic Migration:**
The system will automatically detect legacy task files and offer migration.

**Manual Migration:**
```bash
# Run migration tool
python dev/tools/migrate_to_unified_tasks.py

# Rename files to uDOS ID format
python dev/tools/rename_distributable_files.py
```

**What Changes:**
- Old task files → `memory/bank/user/unified_tasks.json`
- Scattered tasks → Single centralized database
- Legacy filenames → Compact uDOS ID format
- Version history → `.archive/versions/` structure

**Backwards Compatibility:**
- ✅ Old commands still work (mapped to new system)
- ✅ Legacy files preserved in `.archive/`
- ✅ Manual rollback possible via UNDO system

---

## 📦 Installation

### New Installation
```bash
# Standard installation (lite tier, 7.3MB)
git clone https://github.com/fredporter/uDOS.git
cd uDOS
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python uDOS.py
```

### Upgrading from v1.2.22
```bash
cd uDOS
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt --upgrade
python uDOS.py  # Auto-migration will run if needed
```

### Contributors (with dev tools)
```bash
git clone --recurse-submodules https://github.com/fredporter/uDOS.git
```

---

## 🎯 What's Next?

### v1.2.24 Roadmap
Planned features for next release:

1. **Error Interceptor Enhancement** - Theme-aware error prompts ✅ (already complete from v1.2.22)
2. **Role-Based Permissions** - 5-level access control (300 lines)
3. **Pattern Learning System** - Local error pattern recognition (350 lines)
4. **Theme-Aware Messaging** - Universal themed output (250 lines)
5. **Device Monitoring** - Disk/RAM/CPU tracking (400 lines)
6. **Enhanced Time System** - Complete timezone management (350 lines)
7. **JSON Viewer/Editor** - Interactive tree navigation (500 lines)

**Estimated:** ~2,150 lines remaining for v1.2.24

---

## 🙏 Acknowledgments

**Core Team:**
- Task system design and implementation
- Filename standard specification
- Archive system architecture
- Bug fixes and testing

**Community:**
- Beta testing and feedback
- Bug reports and feature requests
- Documentation improvements

**Special Thanks:**
- All contributors to v1.2.22 (Self-Healing System foundation)
- Early adopters testing v1.2.23 features
- Community members providing use cases and feedback

---

## 📚 Resources

### Documentation
- [Task Management Guide](wiki/Task-Management.md)
- [Filename Convention](wiki/Filename-Convention.md)
- [Archive System](wiki/Archive-System.md)
- [Installation Guide](wiki/Installation-Guide.md)
- [Getting Started](wiki/Getting-Started.md)

### Support
- [GitHub Issues](https://github.com/fredporter/uDOS/issues)
- [GitHub Discussions](https://github.com/fredporter/uDOS/discussions)
- [Contributing Guide](CONTRIBUTING.md)

### Links
- **Repository:** https://github.com/fredporter/uDOS
- **Wiki:** https://github.com/fredporter/uDOS/wiki
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
- **Roadmap:** [dev/roadmap/ROADMAP.md](dev/roadmap/ROADMAP.md)

---

**Happy organizing! 🎉**

*uDOS v1.2.23 - Unified Task Management & File Organization System*  
*Production Ready - December 13, 2025*
