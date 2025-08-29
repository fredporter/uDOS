# uDOS Documentation
Comprehensive documentation for v1.0.5.1 modular architecture

## Core Documentation

### System Architecture
- **ARCHITECTURE.md** - Complete modular system design and role capabilities (UPDATED v1.0.5.1)
- **DATA-SYSTEM.md** - Variable management, GET forms, and uDATA configuration
- **DISPLAY-SYSTEM.md** - Grid layout, input handling, and interface elements

### User Documentation
- **USER-GUIDE.md** - End user instructions and workflows
- **USER-COMMAND-MANUAL.md** - Complete command reference including module commands
- **TEMPLATES.md** - Template system and file generation

### Development Reference
- **STYLE-GUIDE.md** - Code and documentation standards
- **QUICK-STYLES.md** - Quick reference for naming and formatting

## What's New in v1.0.5.1

### Modular Architecture
- **6,431 lines moved** from uCORE to uSCRIPT modules
- **uCORE now 100% bash-only** (zero Python dependencies)
- **Module loader system** for clean core-to-module interface
- **File organization improvements** (installation.id → uMEMORY, trash → sandbox)

### Enhanced Features
- **Session Management**: Persistent state tracking via modules
- **Workflow Management**: User journey automation 
- **Story System**: Interactive variable collection
- **Backup System**: Comprehensive backup/restore functionality
- **Smart Input**: Advanced input processing modules

## Documentation Structure

### Updated for Modular Design
This documentation reflects the new modular architecture with clear separation between:

**Core System (uCORE):**
- Essential bash utilities and command routing
- Module loader interface system
- Role-based access control

**Feature Modules (uSCRIPT/modules):**
- Session management and workflow automation
- Story system and backup functionality  
- Smart input processing and notifications
- USER-GUIDE.md (workflows and getting started)
- USER-COMMAND-MANUAL.md (complete command syntax)
- TEMPLATES.md (file generation system)

**Development:**
- STYLE-GUIDE.md (comprehensive standards)
- QUICK-STYLES.md (quick reference)

### File Locations
- **All trash**: `/sandbox/trash/category-YYYYMMDD-HHMMSSTZCODE/`
- **All backups**: `/sandbox/backup/`
- **All logs**: `/sandbox/logs/`
- **Install script**: Root folder (`/install.sh`) for GitHub distribution

## Date and Time Format

### Visual Display (Human-Readable)
- **Dates**: 26 August 2025
- **Times**: 3:45 PM AEST

### Code/Filenames (Machine-Readable)
- **Dates**: 20250826
- **Times**: 154500AEST
- **Combined**: category-20250826-154500AEST/

## Quick Navigation

### For New Users
1. Start with **USER-GUIDE.md** for basic workflows
2. Reference **USER-COMMAND-MANUAL.md** for command syntax
3. Use **TEMPLATES.md** for file generation

### For Developers
1. Begin with **ARCHITECTURE.md** for system design
2. Follow **STYLE-GUIDE.md** for coding standards
3. Reference **DATA-SYSTEM.md** and **DISPLAY-SYSTEM.md** for implementation

---
*uDOS v1.0.5.1 Documentation - Modular, efficient, future-ready*
