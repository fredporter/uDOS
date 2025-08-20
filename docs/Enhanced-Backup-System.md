# uDOS Backup/Restore & Destroy System Documentation
# v1.3 - Enhanced System Protection and Recovery

## Overview

The enhanced uDOS backup system provides comprehensive data protection with session-based undo/redo capabilities, role-based storage, and smart destruction options. All operations are logged and protected against data loss.

## System Components

### 1. backup-restore.sh - Core Backup System
- **Session-based undo/redo** with automatic move logging
- **Role-based encrypted backups** with 5-backup retention
- **Daily move tracking** for missions, milestones, and operations
- **Smart cleanup** keeping 4 most recent + 1 largest backup
- **Integration** with existing smart backup infrastructure

### 2. destroy.sh - Enhanced Destruction System
- **Emergency backups** before all destructive operations
- **User profile protection** prevents sandbox/user.md exposure
- **Role folder preservation** options for all destruction levels
- **Master archiving** for complete system preservation
- **Safe destruction** with comprehensive recovery options

## Key Features

### Session Management
- **Automatic session initialization** with unique session IDs
- **Move logging** captures every significant system change
- **Undo/Redo stack** with pre-move backups for instant recovery
- **Session reset** on startup, manual backup, or system exit

### Data Protection
- **Role-based storage** in user's role folder (tomb, sorcerer, wizard, imp, drone, ghost)
- **AES-256 encryption** when user password is set
- **User credential protection** during destruction operations
- **Emergency backups** created before any destructive action

### Smart Backup Management
- **Automated retention** keeps 5 backups maximum (4 recent + 1 largest)
- **Backup metadata** tracking with file info, encryption status, dates
- **Size optimization** with intelligent compression
- **Restoration validation** with proper file extraction verification

## Command Reference

### Backup Commands
```bash
# Create backups
backup-restore.sh backup                    # Manual backup
backup-restore.sh backup daily              # Daily backup  
backup-restore.sh backup startup            # Startup backup
backup-restore.sh backup exit               # Exit backup

# List and restore
backup-restore.sh list                      # List available backups
backup-restore.sh restore                   # Interactive restore
backup-restore.sh restore <file>            # Restore specific backup
```

### Undo/Redo Commands
```bash
# Session operations
backup-restore.sh undo                      # Undo last move
backup-restore.sh redo                      # Redo next move
backup-restore.sh history                   # Show session history
backup-restore.sh status                    # Show system status
```

### Tracking Commands
```bash
# Mission and milestone tracking
backup-restore.sh milestone "Title"         # Add milestone
backup-restore.sh mission "Name"            # Complete mission
backup-restore.sh log-move type "desc"      # Log custom move
```

### Destroy Commands
```bash
# Destruction options
destroy.sh                                  # Interactive menu
destroy.sh reset-identity                   # Reset identity only
destroy.sh fresh-start                      # Clear memory, preserve roles
destroy.sh archive-reset                    # Archive all, factory reset
destroy.sh reboot                          # Restart without changes
destroy.sh exit                           # Safe exit with backup
```

## Session Move Logging

### Automatic Logging
Every significant system change is automatically logged:
- **File operations** (create, edit, delete, move)
- **Backup/restore operations** 
- **System configuration changes**
- **Mission and milestone completion**
- **Identity and role changes**

### Move Structure
```json
{
    "id": "unique_move_id",
    "type": "move_type",
    "description": "Human readable description",
    "timestamp": "2025-01-20T15:30:45Z",
    "backup_file": "path/to/pre-move-backup.tar.gz",
    "data": { /* additional move-specific data */ }
}
```

### Undo/Redo Mechanism
- **Pre-move backups** created automatically before changes
- **Post-move backups** created for redo capability
- **Position tracking** maintains current location in move history
- **Session boundaries** reset undo/redo stack on session start/backup

## Destruction System Protection

### Security Levels

#### Level 1: Reset Identity
- **Preserves**: All data, role folders, system files
- **Clears**: User identity, session logs
- **Protection**: Emergency backup, identity recovery
- **Use Case**: Start fresh while keeping all work

#### Level 2: Fresh Start  
- **Preserves**: Role folders, system backups
- **Clears**: uMEMORY, sandbox (except user.md during operation)
- **Protection**: Emergency backup, role archive, user.md protection
- **Use Case**: Clean slate while preserving role-specific work

#### Level 3: Archive & Reset
- **Preserves**: Everything in master archive
- **Clears**: All role folders, memory, sandbox
- **Protection**: Master system archive, factory initialization
- **Use Case**: Complete reset with full recovery capability

#### Level 4: Reboot Only
- **Preserves**: All data exactly as-is
- **Clears**: Temporary files, session state
- **Protection**: No destructive changes
- **Use Case**: Fresh session without data loss

#### Level 5: Exit Safely
- **Preserves**: All data with exit backup
- **Clears**: Nothing
- **Protection**: Automatic backup, safe shutdown
- **Use Case**: Planned system shutdown

### User Protection Features
- **Credential isolation** during destruction operations
- **Temporary relocation** of user.md during risky operations
- **Automatic restoration** after operation completion
- **Access control** prevents unauthorized exposure

## File Organization

### Backup Storage Structure
```
uMEMORY/
├── backups/
│   ├── emergency/           # Emergency pre-destruction backups
│   ├── session/            # Session move backups (for undo/redo)
│   ├── daily/              # Daily backup archives
│   ├── manual/             # Manual backup archives
│   ├── role-archives/      # Pre-destruction role folder backups
│   └── master-archives/    # Complete system archives
└── system/
    ├── session-moves.json  # Current session move log
    ├── daily-moves-*.json  # Daily move logs with missions/milestones
    ├── backup-metadata.json # Backup file metadata and info
    └── .user-protected.md  # Temporary user profile protection
```

### Role-Based Storage
Each role has dedicated backup storage:
```
<role>/
└── backup/
    ├── [HEX]-backup.tar.gz     # Regular backups
    └── [HEX]-backup.tar.gz.enc # Encrypted backups (when password set)
```

## Integration Points

### Smart Backup System Integration
- **Leverages existing** role detection and encryption capabilities
- **Extends functionality** with session management and undo/redo
- **Maintains compatibility** with existing backup workflows
- **Enhances security** with user protection during operations

### uMAP System Integration
- **Geographic operations** logged with tile codes and coordinates
- **Mapping changes** tracked as moves with spatial context
- **Navigation history** preserved in session logs
- **Tile generation** logged with backup points for recovery

### Mission System Integration
- **Mission completion** automatically logged to daily moves
- **Milestone tracking** with timestamps and descriptions
- **Progress preservation** during destruction operations
- **Achievement recovery** from backup metadata

## Best Practices

### Daily Workflow
1. **Automatic session start** initializes move logging
2. **Work normally** - all significant changes logged automatically
3. **Use undo/redo** for immediate corrections within session
4. **Create manual backups** before major changes
5. **Safe exit** creates automatic backup and clears session

### Recovery Procedures
1. **Immediate undo** for recent mistakes (same session)
2. **Manual restore** for longer-term recovery needs
3. **Emergency restoration** from pre-destruction backups
4. **Master archive recovery** for complete system restoration

### Security Considerations
- **Enable password protection** for encrypted backups
- **Regular backup cleanup** maintains manageable storage
- **Verify restoration** test recovery procedures periodically
- **Monitor backup metadata** for system health

## Technical Implementation

### Backup Format
- **Compression**: gzip with optimal compression ratio
- **Encryption**: AES-256-CBC with PBKDF2 key derivation
- **Metadata**: JSON tracking with file verification
- **Integrity**: Hash verification for backup validation

### Session Management
- **Process tracking** via session IDs and PIDs
- **Atomic operations** ensure consistency during moves
- **Rollback capability** via pre-move backup restoration
- **State validation** confirms system integrity after operations

### Error Handling
- **Graceful degradation** when backup systems unavailable
- **Fallback procedures** for manual backup creation
- **Validation checks** before destructive operations
- **Recovery prompts** guide users through restoration

This enhanced system provides comprehensive protection while maintaining the flexibility and power users expect from uDOS, ensuring that no data is ever truly lost and all operations can be undone or recovered.
