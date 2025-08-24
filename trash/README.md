# 🗑️ uDOS Trash System

This directory contains deprecated files, cleaned up data, and backup files that are no longer needed but preserved for recovery purposes.

## 📁 Trash Organization

### Automated Moves to Trash
- **Deprecated files** - Replaced by consolidated uDATA files
- **Old backup files** - Replaced by newer backups (keeping 1 most recent)
- **Cleanup operations** - Files removed during system optimization
- **Legacy data** - Superseded formats and structures

### Trash Categories
```
trash/
├── deprecated/          # Files replaced by newer versions
├── backups/            # Old backup files (keeping latest + largest)
├── cleanup/            # Files removed during optimization
└── system/             # System-generated temporary files
```

## 🔧 Trash Management

### DESTROY Command Integration
- **TRASH EMPTY** - Complete trash folder cleanup
- **TRASH SELECTIVE** - Remove specific categories
- **TRASH ARCHIVE** - Compress old trash before deletion

### REBOOT Command Integration  
- **Auto-trash cleanup** - Removes files older than 30 days
- **Backup optimization** - Keeps 1 most recent + 1 largest backup
- **Space management** - Monitors trash folder size

### Smart Backup Enhancement
- **wizard/ folder included** - Development files backed up
- **Retention policy** - Latest backup + largest backup preserved
- **Auto-cleanup** - Old backups moved to trash automatically

## 📊 Trash Policies

### File Retention
- **Deprecated files**: 90 days (then auto-delete)
- **Old backups**: 30 days (then auto-delete)  
- **Cleanup files**: 7 days (then auto-delete)
- **System files**: 1 day (then auto-delete)

### Size Limits
- **Max trash size**: 500MB total
- **Auto-compress**: Files older than 7 days
- **Force cleanup**: When trash exceeds size limit

## 🚨 Recovery Options

### File Recovery
```bash
# List trash contents
ls -la trash/deprecated/
ls -la trash/backups/

# Recover specific file
cp trash/deprecated/filename.ext ./
```

### Backup Recovery
```bash
# Find latest backup
ls -lt trash/backups/ | head -5

# Restore from backup
# (Use standard backup restore procedures)
```

---

**Safety Note**: Files in trash are automatically deleted according to retention policies. Critical files should be explicitly backed up outside the trash system.
