# uCORE/code/user-memory - User Memory Management Scripts

This directory contains the executable scripts for the uDOS User Memory Management System. Following uDOS architecture principles, scripts reside in `uCORE/code/` while data files are stored in `uMEMORY/user/`.

## Architecture Overview

- **Scripts**: `/uCORE/code/user-memory/` (this directory)
- **Data**: `/uMEMORY/user/` (missions, milestones, moves, legacy, explicit)
- **Integration**: Full compatibility with uCORE logging and backup systems

## Scripts

### user-memory-manager.sh
**Master coordination and management script**
- Unified interface for all user memory operations
- System overview and status dashboard
- Quick commands for mission, milestone, move, and legacy management
- Automated maintenance and reporting
- Integration with all component scripts

Usage:
```bash
./user-memory-manager.sh overview
./user-memory-manager.sh mission "Task Name" learning
./user-memory-manager.sh milestone "Achievement" "Description"
./user-memory-manager.sh move navigation "Action" "Location"
./user-memory-manager.sh legacy "Archive Name" "/path/to/files"
./user-memory-manager.sh report
./user-memory-manager.sh maintenance
```

### user-move-logger.sh
**Move tracking and session management**
- Personal move logging with session-based tracking
- Integration with uCORE session-moves.json
- Daily summaries and pattern analysis
- User activity analytics and trends

### mission-manager.sh
**Mission and milestone management**
- Mission creation and progress tracking
- Milestone achievement logging
- Dashboard visualization with status summaries
- Mission completion detection and reporting

### installation-lifespan.sh
**Installation lifecycle monitoring**
- Role-based lifespan management (wizard/student/user/admin)
- Phase tracking (trial/basic/full/extended)
- Expiration monitoring and notifications
- Extension request handling
- Maintenance logging and milestone integration

## Data Storage Locations

All scripts write data to corresponding directories in `/uMEMORY/user/`:

- **Moves**: `/uMEMORY/user/moves/` - Session logs, daily summaries, patterns
- **Missions**: `/uMEMORY/user/missions/` - Mission files with metadata
- **Milestones**: `/uMEMORY/user/milestones/` - Achievement records
- **Legacy**: `/uMEMORY/user/legacy/` - Archived content with metadata
- **Explicit**: `/uMEMORY/user/explicit/` - User-defined content

## Integration Points

### uCORE Integration
- Session management through `uCORE/session-moves.json`
- Installation tracking via `uMEMORY/system/installation-lifespan.json`
- Backup compatibility with smart backup undo/redo systems

### VS Code Integration
Available through wizard development environment:
- **🧠 User Memory Overview** - System status dashboard
- **🎯 Create Mission** - Quick mission creation
- **🏆 Add Milestone** - Achievement recording
- **📍 Log User Move** - Activity tracking
- **🗃️ Create Legacy Archive** - Content archival
- **📋 Generate Memory Report** - Comprehensive reporting

### Framework Integration
- Compatible with wizard development framework
- Integrates with smart backup checkpoint system
- Works with uSCRIPT execution tracking
- Supports cross-system data consistency

## System Features

### Intelligent Tracking
- Automatic pattern recognition in user behavior
- Smart categorization of moves and activities
- Trend analysis and productivity insights

### Mission Intelligence
- Progress-based milestone suggestions
- Dashboard visualization with real-time status
- Achievement statistics and completion tracking

### Lifecycle Management
- Installation phase progression monitoring
- Role-based feature access control
- Automated expiration handling and extension management

### Data Preservation
- Complete metadata preservation for all operations
- Legacy archival with restoration documentation
- Cross-session data persistence and integrity

## Usage Examples

### System Initialization
```bash
# Complete system setup
./user-memory-manager.sh init

# Individual component initialization
./user-move-logger.sh init
./installation-lifespan.sh init wizard full
./mission-manager.sh dashboard
```

### Daily Operations
```bash
# Quick status check
./user-memory-manager.sh overview

# Create and track missions
./user-memory-manager.sh mission "Learn uScript Syntax" learning
./user-memory-manager.sh milestone "First Script" "Created working script"

# Log development activities
./user-memory-manager.sh move development "Fixed bug in parser" "uSCRIPT/"

# Archive old projects
./user-memory-manager.sh legacy "2024 Projects" "/old/project/path"
```

### Maintenance and Reporting
```bash
# Generate comprehensive report
./user-memory-manager.sh report

# Perform system maintenance
./user-memory-manager.sh maintenance

# Check specific component status
./mission-manager.sh dashboard
./installation-lifespan.sh status
```

## File Naming Conventions

### Scripts (this directory)
- `user-memory-manager.sh` - Master coordination script
- `user-move-logger.sh` - Move tracking system
- `mission-manager.sh` - Mission and milestone management
- `installation-lifespan.sh` - Installation lifecycle monitoring

### Data Files (uMEMORY/user/)
- **Moves**: `session-YYYYMMDD.md`, `daily-summary-YYYYMMDD.md`
- **Missions**: `mission-name-YYYYMMDD.md`
- **Milestones**: `milestone-name-YYYYMMDD.md`
- **Legacy**: `legacy-name-YYYYMMDD.md`
- **Reports**: `user-memory-report-YYYYMMDD.md`

## Development Notes

### Architecture Compliance
This implementation follows uDOS core principles:
- Scripts in `uCORE/code/` for execution
- Data in `uMEMORY/` for storage
- Integration with core systems
- Compatibility with backup/restore operations

### Cross-System Compatibility
- All operations integrate with uCORE logging
- Smart backup system compatibility
- VS Code task integration
- Framework workflow compatibility

### Performance Considerations
- Efficient file operations with minimal I/O
- Pattern recognition for large datasets
- Automated cleanup and optimization
- Background maintenance operations

---

*uDOS User Memory Management System - Scripts v1.0*  
*Located in uCORE/code/user-memory/ - Data stored in uMEMORY/user/*
