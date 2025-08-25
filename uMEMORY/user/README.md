# uMEMORY/user - User Memory Archive

This directory contains user-specific memory archives. User data is automatically moved here from `/sandbox/sessions/` when sessions end.

## Session Archive Flow (Future Implementation)
```
[Session Active] → /sandbox/sessions/current/
[Session End] → Archive to /uMEMORY/user/
[Sandbox Flush] → Clear /sandbox/ (user memory preserved here)
```

## Architecture

- **Scripts**: Located in `/uCORE/code/user-memory/` (executable components)
- **Data**: Located in `/uMEMORY/user/` (storage and data files)

## Quick Start

Initialize the complete user memory system:
```bash
/uCORE/code/user-memory/user-memory-manager.sh init
```

Check system status:
```bash
/uCORE/code/user-memory/user-memory-manager.sh overview
```

## Master Memory Manager

The `user-memory-manager.sh` script provides unified access to all user memory components:

### Quick Commands
- `/uCORE/code/user-memory/user-memory-manager.sh mission "Task Name" learning` - Create mission
- `/uCORE/code/user-memory/user-memory-manager.sh milestone "Achievement" "Description"` - Log milestone
- `/uCORE/code/user-memory/user-memory-manager.sh move navigation "Action" "Location"` - Log move
- `/uCORE/code/user-memory/user-memory-manager.sh legacy "Archive Name" "/path/to/files"` - Archive legacy
- `/uCORE/code/user-memory/user-memory-manager.sh report` - Generate comprehensive report
- `/uCORE/code/user-memory/user-memory-manager.sh maintenance` - Perform system maintenance

## Directory Structure

### /moves/
**Personal move logging and session tracking**
- Session logs and activity tracking
- Daily move summaries and patterns
- Installation and system logs (moved from uMEMORY root)
- Files: `uLOG-uHEXcode-Title.md` format

### /missions/
**User missions, goals, and objectives**
- Mission creation and progress tracking
- Priority-based organization (high/medium/low)
- Type categorization (learning/work/personal/system)
- Files: `uTASK-uHEXcode-Title.md` format

### /milestones/
**Achievement tracking and progress markers**
- Milestone logging with timestamps
- Achievement categories and descriptions
- Progress visualization and statistics
- Files: `uTASK-uHEXcode-Title.md` format

### /legacy/
**Archived user data and historical content**
- Automated legacy archival with metadata
- Original content preservation
- Restoration documentation
- Files: `uDOC-uHEXcode-Title.md` format

### /explicit/
**User-defined explicit content and instructions**
- Personal preferences and configurations
- Custom workflows and procedures
- User-specific documentation
- Explicit memory declarations

## Script Components (Located in uCORE/code/user-memory/)

### user-memory-manager.sh
**Master coordination script in uCORE**
- Unified interface for all user memory operations
- System overview and status reporting
- Quick commands for common operations
- Maintenance and analytics

### user-move-logger.sh
**Move tracking system in uCORE**
- Session initialization and management
- Daily move summaries and analytics
- Pattern recognition and trends
- Integration with uCORE session-moves.json
- Support for multiple move types and contexts

### mission-manager.sh
**Mission and milestone management in uCORE**
- Mission creation with type and priority
- Progress tracking and status updates
- Milestone achievement logging
- Dashboard visualization
- Mission completion detection
- Timeline and deadline management

### installation-lifespan.sh
**Installation lifecycle monitoring in uCORE**
- Role-based lifespan management (wizard/student/user/admin)
- Phase tracking (trial/basic/full/extended)
- Expiration monitoring and notifications
- Extension request handling
- Maintenance logging and history

## Integration with uCORE

### Session Management
- Seamless integration with uCORE's session-moves.json
- Real-time synchronization of user moves
- Core system compatibility for all logging

### Backup Integration
- All user data compatible with uCORE backup systems
- Smart backup undo/redo support
- Automatic archival and restoration

### System Synchronization
- Daily maintenance routines
- Cross-system data consistency
- Automated cleanup and optimization

## Usage Examples

### Initialize System
```bash
# Complete system initialization
/uCORE/code/user-memory/user-memory-manager.sh init

# Initialize individual components
/uCORE/code/user-memory/user-move-logger.sh init
/uCORE/code/user-memory/installation-lifespan.sh init wizard full
/uCORE/code/user-memory/mission-manager.sh dashboard
```

### Daily Workflow
```bash
# Log a development move
/uCORE/code/user-memory/user-memory-manager.sh move development "Implemented new feature" "uScript/"

# Create learning mission
/uCORE/code/user-memory/user-memory-manager.sh mission "Master uScript Syntax" learning

# Record achievement
/uCORE/code/user-memory/user-memory-manager.sh milestone "First Script" "Successfully created first working script"

# Check progress
/uCORE/code/user-memory/user-memory-manager.sh overview
```

### Maintenance
```bash
# Daily maintenance
/uCORE/code/user-memory/user-memory-manager.sh maintenance

# Generate comprehensive report
/uCORE/code/user-memory/user-memory-manager.sh report

# Archive old projects
/uCORE/code/user-memory/user-memory-manager.sh legacy "2024 Projects" "/path/to/old/projects"
```

## System Features

### Intelligent Tracking
- Automatic pattern recognition in user behavior
- Smart categorization of moves and activities
- Trend analysis and productivity insights

### Mission Intelligence
- Progress-based milestone suggestion
- Deadline tracking and notifications
- Achievement statistics and visualization

### Lifecycle Management
- Installation phase progression tracking
- Role-based feature access control
- Expiration handling and extension management

### Legacy Preservation
- Automated archival with complete metadata
- Original content preservation
- Restoration documentation and procedures

## File Naming Conventions

All user memory files now follow the uDOS hex-based naming convention:

### uTASK Files (Missions and Milestones)
- **Format**: `uTASK-uHEXcode-Title.md`
- **Example**: `uTASK-F8A4B2E1-uDOS-System-Setup.md`
- **Used for**: Mission files and milestone records

### uLOG Files (Moves and Activity Logs)
- **Format**: `uLOG-uHEXcode-Title.md` or `uLOG-YYYYMMDD-uHEXcode-Title.md`
- **Example**: `uLOG-E4F5A6B7-session-20250821.md`
- **Used for**: Session logs, daily summaries, move patterns, installation logs

### uDOC Files (Legacy and Documentation)
- **Format**: `uDOC-uHEXcode-Title.md`
- **Example**: `uDOC-7A8B9C0D-Development-Notes.md`
- **Used for**: Archived content, legacy documentation

### uHEX Code Format
- **8-character hexadecimal identifier**
- **Encodes**: Date, time, timezone, role, and location
- **Example**: `F8A4B2E1` represents specific timestamp and context

## Advanced Features

### Analytics Dashboard
The system provides comprehensive analytics including:
- Daily/weekly/monthly move summaries
- Mission completion rates and trends
- Milestone achievement timelines
- Installation lifespan utilization

### Integration Points
- **uCORE**: Session management and logging
- **uSCRIPT**: Development move tracking
- **Ghost**: Spectral error handling integration
- **Wizard**: Development framework coordination

### Backup Compatibility
All user memory data is fully compatible with:
- Smart backup system undo/redo
- uCORE backup and restoration
- Legacy archival and retrieval
- Cross-session data persistence

## Monitoring and Alerts

### Installation Lifespan
- Phase transition notifications
- Expiration warnings (30, 7, 1 day)
- Extension request automation
- Maintenance reminders

### Mission Tracking
- Deadline approach notifications
- Progress milestone alerts
- Achievement celebrations
- Completion confirmations

### System Health
- Daily maintenance status
- Storage utilization monitoring
- Integration health checks
- Performance optimization alerts

---

*uDOS User Memory Management System v1.0*
*Integrated with uCORE, compatible with smart backup systems*
