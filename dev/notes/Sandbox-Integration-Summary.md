# Sandbox & Backup Integration Summary

## Overview
Successfully reorganized uDOS backup and logging as core uCORE functions, with /sandbox as the primary session-based development workspace.

## Key Changes Made

### 1. **Moved Core Functions to uCORE**
- `uSCRIPT/library/backup-restore.sh` → `uCORE/core/backup-restore.sh`
- `uSCRIPT/library/logging.sh` → `uCORE/core/logging.sh`
- Created `uCORE/core/backup-handler.sh` - Central backup command interface
- Created `uCORE/core/session-manager.sh` - Session management system
- Created `uCORE/core/sandbox.sh` - Unified sandbox environment

### 2. **Restructured /sandbox as Session Workspace**
```
sandbox/
├── dev/                    # Development files, scripts being worked on
├── temp/                   # Temporary files (auto-cleaned every hour)
├── session/                # Session management and logging
│   ├── logs/               # Session logs and daily summaries
│   ├── moves/              # Session move tracking
│   ├── undo-stack/         # Undo/redo stack
│   └── archive/            # Archived session data
├── experiments/            # Experimental features and tests
├── tests/                  # Test scripts and validation
├── scripts/                # User scripts and utilities
└── README.md              # Documentation
```

### 3. **Session-Based Development Flow**
- **Session Start**: Auto-creates session tracking, initializes undo/redo stack
- **Development Work**: All moves logged in real-time for undo/redo
- **Session End**: Compiles session summary, archives to daily log
- **Daily Archive**: Daily summaries moved to uMEMORY/user/{role}/daily-logs
- **Cleanup**: Old session files cleaned (3+ days), temp files hourly

### 4. **Centralized Backup System**
- **Location**: All backups stored in `/backup` with organized subdirectories
- **Encryption**: AES-256-CBC with PBKDF2 key derivation (role-based)
- **Types**: Manual, session, daily, emergency backups
- **Retention**: Automatic cleanup based on backup type and role permissions
- **Integration**: Backup commands aligned with uDATA-commands.json

## Command Interface

### Sandbox Commands
```bash
# Development
sandbox DEV CREATE <file> [template]    # Create dev file (script/experiment/test)
sandbox DEV LIST                        # List development files
sandbox DEV RUN <file>                   # Run development file

# Testing
sandbox TEST CREATE <name>               # Create test file
sandbox TEST RUN [name]                  # Run test(s)
sandbox TEST LIST                        # List test files

# Experiments
sandbox EXPERIMENT CREATE <name>         # Create experiment
sandbox EXPERIMENT RUN <name>            # Run experiment
sandbox EXPERIMENT LIST                  # List experiments

# Session Management
sandbox SESSION START/END               # Manage sessions
sandbox SESSION SAVE                    # Create save point
sandbox SESSION UNDO/REDO              # Undo/redo operations
sandbox SESSION HISTORY                # Show session history

# Environment
sandbox STATUS                          # Show overall status
sandbox SANDBOX INIT                    # Initialize environment
sandbox SANDBOX CLEAN                   # Clean environment
sandbox SANDBOX BACKUP                  # Create sandbox backup
```

### Backup Commands (via uDATA)
```bash
BACKUP CREATE [type] [description]      # Create backup
BACKUP LIST                             # List available backups
BACKUP RESTORE [file]                   # Restore from backup
BACKUP STATUS                           # Show backup system status
BACKUP HISTORY                          # Show backup history
BACKUP CLEANUP                          # Clean old backups
```

## Integration with uDATA Commands

The system now fully integrates with the uDATA command structure:

### BACKUP Command
- **BACKUP CREATE** → Creates encrypted, role-based backup
- **BACKUP LIST** → Shows available backups with metadata
- **BACKUP RESTORE** → Interactive or direct restore
- **BACKUP STATUS** → Shows system status, encryption, role info

### SESSION Command
- **SESSION SAVE** → Creates session save point
- **SESSION UNDO** → Undoes last operation
- **SESSION REDO** → Redoes undone operation
- **SESSION HISTORY** → Shows session timeline

## Benefits

### 1. **Session-Based Development**
- All work tracked for undo/redo within session
- Clean separation of development vs production
- Automatic compilation to daily summaries
- Historical tracking without clutter

### 2. **Centralized Backup**
- Single `/backup` location for all backups
- Role-based access and encryption
- Automatic retention and cleanup
- Integration with session save points

### 3. **Development Workflow**
- Create/test/experiment in sandbox
- Session-based undo/redo
- Move finalized work to production locations
- Automatic daily archival to uMEMORY

### 4. **File Organization**
- Development files: `/sandbox/dev/`
- Session data: `/sandbox/session/` (temporary)
- Daily summaries: `uMEMORY/user/{role}/daily-logs/` (permanent)
- Backups: `/backup/` (centralized, encrypted)

## File Lifecycle

1. **Development**: Create/edit files in `/sandbox/dev/`
2. **Testing**: Test in sandbox environment with session tracking
3. **Session Data**: Real-time logging in `/sandbox/session/`
4. **Session End**: Compile to daily summary
5. **Daily Archive**: Move summary to `uMEMORY/user/{role}/daily-logs/`
6. **Cleanup**: Remove old session files, keep daily summaries

## Technical Implementation

### Session Management
- JSON-based session tracking with metadata
- Real-time move logging for undo/redo
- Automatic session initialization
- Daily compilation with statistics

### Backup System
- Role-based directory structure
- AES-256-CBC encryption with user passwords
- Metadata tracking for all backups
- Automatic cleanup and retention policies

### Integration
- uCORE functions accessible system-wide
- uDATA command alignment
- Session hooks for backup triggers
- Unified command interface via sandbox.sh

This implementation provides a robust, session-based development environment with comprehensive backup and logging capabilities, all integrated with the existing uDOS command structure.
