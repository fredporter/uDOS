# uMEMORY Backup Directory

This directory contains compressed backups of the uMEMORY folder using the hex filename convention.

## Backup System Features

- **Automated backups**: Run using `uCORE/code/backup-umemory.sh`
- **Hex timestamp naming**: Files use format `HHHHHHHHH-TTTT-{role}-umemory-backup.tar.gz`
- **Compression**: All backups are compressed tar.gz files
- **Cleanup**: Automatically keeps only the last 5 backups per location
- **Flat structure**: Preserves uMEMORY's flat-like organization with hex filenames

## Usage

```bash
# Run full backup
./uCORE/code/backup-umemory.sh

# Clean old backups only  
./uCORE/code/backup-umemory.sh clean

# Generate backup report
./uCORE/code/backup-umemory.sh report

# Show help
./uCORE/code/backup-umemory.sh help
```

## File Naming Convention

Backup files follow this pattern:
```
HHHHHHHHH-TTTT-{role}-umemory-backup.tar.gz
```

Where:
- `HHHHHHHHH`: Hex-encoded date (YYYYMMDD)
- `TTTT`: Hex-encoded time (HHMM)
- `{role}`: Role name (ghost, drone, imp, sorcerer, tomb, wizard, sandbox)

## uMEMORY Structure

The backed up uMEMORY folder maintains a flat-like structure with:
- Hex filename convention for temporal-spatial organization
- Personal data archive (missions, moves, memories, milestones)
- Direct access to all user data without deep nesting
- Privacy protection (isolated from distributed system)

## Backup Report

View the latest backup status and statistics:
```bash
cat sandbox/backup/umemory-backup-report.md
```
