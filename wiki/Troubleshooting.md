# Troubleshooting & Repair

Complete guide to diagnosing and fixing common uDOS issues

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Problems](#installation-problems)
3. [Runtime Errors](#runtime-errors)
4. [Performance Issues](#performance-issues)
5. [REPAIR Command Guide](#repair-command-guide)
6. [Debug Mode](#debug-mode)
7. [Common Error Messages](#common-error-messages)
8. [Getting Help](#getting-help)

---

## Quick Diagnostics

### Run System Check
```bash
STATUS              # Check system health
REPAIR MODE 1       # Run basic diagnostics
```

### Check Logs
```bash
# View recent errors
cat memory/logs/udos.log | tail -50

# Search for specific error
grep "ERROR" memory/logs/udos.log
```

### Verify Installation
```bash
# Check Python version
python3 --version        # Should be 3.8+

# Check dependencies
pip3 list | grep -i "sqlite\|google"

# Test basic functionality
./start_udos.sh
# Then run: HELP, STATUS, LIST
```

---

## Installation Problems

### Python Version Conflicts

**Problem**: `python3: command not found` or version < 3.8

**Solutions**:

**macOS**:
```bash
# Install Python via Homebrew
brew install python3

# Verify installation
python3 --version
which python3
```

**Linux (Ubuntu/Debian)**:
```bash
# Install Python 3.9+
sudo apt update
sudo apt install python3.9 python3-pip

# Set as default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
```

**Windows**:
```powershell
# Install via Microsoft Store or python.org
# Then verify in WSL:
wsl python3 --version
```

### Dependency Installation Failures

**Problem**: `pip install` fails or dependencies not found

**Solutions**:

```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Install requirements with verbose output
pip3 install -r requirements.txt -v

# If specific package fails, install individually:
pip3 install google-generativeai
pip3 install requests
pip3 install colorama
```

**Permission errors**:
```bash
# Install to user directory instead
pip3 install --user -r requirements.txt

# Or use virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Permission Errors

**Problem**: `Permission denied` when running start_udos.sh

**Solutions**:
```bash
# Make script executable
chmod +x start_udos.sh

# If still failing, run with bash explicitly
bash start_udos.sh
```

**Problem**: Can't write to `data/` or `memory/` directories

**Solutions**:
```bash
# Check ownership
ls -la data/ memory/

# Fix ownership
sudo chown -R $USER:$USER data/ memory/

# Fix permissions
chmod -R u+w data/ memory/
```

### Path Configuration Issues

**Problem**: `ModuleNotFoundError: No module named 'core'`

**Solutions**:
```bash
# Verify you're in uDOS directory
pwd
# Should show: /path/to/uDOS

# Check PYTHONPATH
echo $PYTHONPATH
# Should include: /path/to/uDOS/core

# Set temporarily
export PYTHONPATH="$PWD/core:$PYTHONPATH"

# Set permanently in ~/.zshrc or ~/.bashrc
echo 'export PYTHONPATH="/path/to/uDOS/core:$PYTHONPATH"' >> ~/.zshrc
```

---

## Runtime Errors

### Command Not Found

**Problem**: `❌ Unknown command: XYZ`

**Diagnosis**:
```bash
# Check available commands
HELP

# Check if command exists in specific version
HELP DETAILED
```

**Solutions**:
- Verify correct spelling (commands are case-sensitive)
- Check if command requires extension to be loaded
- Update to latest version if command is new
- Check [Command Reference](Command-Reference.md) for exact syntax

### File Not Accessible

**Problem**: `❌ File not found: /path/to/file`

**Diagnosis**:
```bash
# Verify file exists
ls -la /path/to/file

# Check current directory
pwd

# List available files
LIST
```

**Solutions**:
```bash
# Use absolute paths
LOAD /Users/username/uDOS/data/file.txt

# Or navigate to directory first
cd /Users/username/uDOS
LOAD data/file.txt

# Check file permissions
ls -la data/file.txt
# Should be readable: -rw-r--r--
```

### Memory Errors

**Problem**: `MemoryError` or `Out of memory`

**Diagnosis**:
```bash
# Check system memory
free -h        # Linux
vm_stat        # macOS

# Check uDOS memory usage
ps aux | grep python | grep uDOS
```

**Solutions**:
```bash
# Clear cache
REPAIR MODE 2

# Reduce cache size in USER.UDT
{
  "performance": {
    "cache_size_mb": 50  # Reduce from default 100
  }
}

# Disable preloading
{
  "performance": {
    "preload_modules": []
  }
}

# Close uDOS and restart
REBOOT
```

### Database Locked

**Problem**: `database is locked` error

**Diagnosis**:
```bash
# Check for stale locks
ls -la data/*.db-wal data/*.db-shm

# Check for multiple uDOS instances
ps aux | grep udos
```

**Solutions**:
```bash
# Stop all uDOS instances
pkill -f "python.*uDOS"

# Remove lock files
rm data/*.db-wal data/*.db-shm

# Restart uDOS
./start_udos.sh

# If persistent, repair database
REPAIR MODE 3
```

---

## Performance Issues

### Slow Command Execution

**Problem**: Commands take >500ms to execute

**Diagnosis**:
```bash
# Enable profiling
PROFILE ENABLE

# Run slow command
<slow_command>

# Check profile
PROFILE SHOW
```

**Solutions**:

1. **Enable caching**:
```json
{
  "performance": {
    "cache_enabled": true,
    "cache_size_mb": 100
  }
}
```

2. **Optimize database**:
```bash
REPAIR MODE 4
```

3. **Reduce search scope**:
```bash
# Instead of searching everything
KB SEARCH "water"

# Search specific category
KB SEARCH "water" --category=survival
```

### High Memory Usage

**Problem**: uDOS consuming >500MB RAM

**Diagnosis**:
```bash
# Monitor memory
ps aux | grep python | grep uDOS

# Check what's loaded
STATUS
```

**Solutions**:

1. **Disable preloading**:
```json
{
  "performance": {
    "preload_modules": []
  }
}
```

2. **Clear cache**:
```bash
REPAIR MODE 2
```

3. **Reduce history**:
```json
{
  "history": {
    "max_entries": 100
  }
}
```

### Slow Startup

**Problem**: uDOS takes >3 seconds to start

**Diagnosis**:
```bash
# Time the startup
time ./start_udos.sh
```

**Solutions**:

1. **Disable vacuum on startup**:
```json
{
  "database": {
    "vacuum_on_startup": false
  }
}
```

2. **Reduce preloading**:
```json
{
  "performance": {
    "preload_modules": ["commands"]
  }
}
```

3. **Optimize Python environment**:
```bash
# Use virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Slow Search

**Problem**: Knowledge base search takes >2 seconds

**Solutions**:

1. **Rebuild search index**:
```bash
REPAIR MODE 4
```

2. **Optimize database**:
```bash
# SQLite optimization
sqlite3 data/knowledge.db "PRAGMA optimize;"
sqlite3 data/knowledge.db "VACUUM;"
```

3. **Use specific search**:
```bash
# Instead of full-text search
KB SEARCH "water"

# Use exact match
KB LIST | grep "water"
```

---

## REPAIR Command Guide

The REPAIR command provides 5 diagnostic modes:

### MODE 1: Basic Diagnostics
```bash
REPAIR MODE 1
```

**Checks**:
- File system structure
- Required directories exist
- File permissions
- Python dependencies
- Database connectivity

**Output**:
```
🔧 REPAIR MODE 1: Basic Diagnostics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ File System: OK
✅ Permissions: OK
✅ Dependencies: OK
✅ Database: OK

System is healthy.
```

### MODE 2: Cache & Temporary Files
```bash
REPAIR MODE 2
```

**Actions**:
- Clears Python cache (`__pycache__/`)
- Removes temporary files
- Clears command cache
- Resets viewport cache

**When to use**:
- After updating code
- Commands behaving strangely
- Want to free up space

### MODE 3: Database Repair
```bash
REPAIR MODE 3
```

**Actions**:
- Closes all database connections
- Removes lock files
- Runs integrity check
- Rebuilds corrupted tables
- Backs up database first

**When to use**:
- "Database is locked" errors
- Corrupted data
- Missing entries after crash

### MODE 4: Full Optimization
```bash
REPAIR MODE 4
```

**Actions**:
- Vacuums all databases
- Rebuilds search indexes
- Analyzes query performance
- Optimizes table structures
- Updates statistics

**When to use**:
- Slow search performance
- Database grew too large
- After bulk data operations
- Monthly maintenance

### MODE 5: Complete Reset
```bash
REPAIR MODE 5
```

**⚠️ WARNING**: This will reset everything!

**Actions**:
- Backs up all data
- Resets configuration to defaults
- Clears all caches
- Rebuilds databases
- Reinitializes system

**When to use**:
- System completely broken
- Starting fresh
- Before major version upgrade

**Backup location**: `memory/backups/repair_<timestamp>/`

---

## Debug Mode

### Enable Debug Logging

**Temporary** (current session):
```bash
# Set in environment
export UDOS_DEBUG=1
./start_udos.sh
```

**Permanent** (in USER.UDT):
```json
{
  "logging": {
    "level": "DEBUG",
    "console": true,
    "file": "memory/logs/debug.log"
  }
}
```

### Reading Log Files

**View recent logs**:
```bash
# Last 50 lines
tail -50 memory/logs/udos.log

# Follow in real-time
tail -f memory/logs/udos.log

# Search for errors
grep "ERROR\|CRITICAL" memory/logs/udos.log

# Filter by date
grep "2025-11-17" memory/logs/udos.log
```

### Common Log Patterns

**Success pattern**:
```
2025-11-17 14:32:15 - INFO - Command executed: HELP
2025-11-17 14:32:15 - INFO - Response sent: 200 bytes
```

**Error pattern**:
```
2025-11-17 14:32:15 - ERROR - File not found: data/missing.txt
2025-11-17 14:32:15 - ERROR - Traceback (most recent call last):
...
```

**Performance pattern**:
```
2025-11-17 14:32:15 - DEBUG - Command parse: 2.3ms
2025-11-17 14:32:15 - DEBUG - Handler execution: 45.1ms
2025-11-17 14:32:15 - DEBUG - Response render: 3.8ms
```

---

## Common Error Messages

### `ImportError: No module named 'X'`

**Cause**: Missing Python dependency

**Fix**:
```bash
pip3 install X
# or
pip3 install -r requirements.txt
```

### `FileNotFoundError: [Errno 2] No such file or directory`

**Cause**: File path doesn't exist

**Fix**:
```bash
# Verify file location
ls -la /path/to/file

# Create missing directories
mkdir -p data/system/
```

### `PermissionError: [Errno 13] Permission denied`

**Cause**: Insufficient file permissions

**Fix**:
```bash
# Fix permissions
chmod u+w /path/to/file

# Or change ownership
sudo chown $USER:$USER /path/to/file
```

### `sqlite3.OperationalError: database is locked`

**Cause**: Multiple processes accessing database

**Fix**:
```bash
# Kill other instances
pkill -f "python.*uDOS"

# Remove locks
rm data/*.db-wal data/*.db-shm

# Restart
./start_udos.sh
```

### `KeyError: 'X'`

**Cause**: Missing configuration key

**Fix**:
```bash
# Reset configuration
SETUP RESET

# Or manually add key to USER.UDT
```

### `UnicodeDecodeError: 'utf-8' codec can't decode`

**Cause**: Non-UTF-8 file encoding

**Fix**:
```bash
# Convert file to UTF-8
iconv -f ISO-8859-1 -t UTF-8 file.txt > file_utf8.txt

# Or specify encoding in uDOS (future feature)
```

---

## Getting Help

### 1. Check Built-in Help
```bash
HELP                  # List all commands
HELP <command>        # Specific command help
HELP DETAILED         # Full documentation
```

### 2. Search Documentation
```bash
# Search wiki
cd wiki/
grep -r "your problem" .

# Search knowledge base
KB SEARCH "error message"
```

### 3. Check GitHub Issues
Visit: https://github.com/fredporter/uDOS/issues

Search for similar problems or create new issue

### 4. Check Logs
```bash
# View error logs
cat memory/logs/udos.log | grep ERROR

# Full debug log
cat memory/logs/debug.log
```

### 5. Report a Bug

When reporting issues, include:

1. **uDOS version**:
   ```bash
   STATUS
   # Look for version number
   ```

2. **Error message**:
   ```bash
   # Copy complete error from terminal
   ```

3. **Steps to reproduce**:
   ```
   1. Run command X
   2. Observe error Y
   3. Expected behavior Z
   ```

4. **System info**:
   ```bash
   # OS version
   uname -a              # Linux/macOS
   systeminfo            # Windows

   # Python version
   python3 --version

   # Dependencies
   pip3 list
   ```

5. **Relevant logs**:
   ```bash
   # Last 100 lines
   tail -100 memory/logs/udos.log
   ```

---

## Prevention Tips

### Regular Maintenance

**Weekly**:
```bash
# Clear cache
REPAIR MODE 2
```

**Monthly**:
```bash
# Optimize database
REPAIR MODE 4
```

**Before Major Updates**:
```bash
# Full backup
cp -r data/ data_backup_$(date +%Y%m%d)
cp -r memory/ memory_backup_$(date +%Y%m%d)
```

### Best Practices

1. **Keep backups**:
   ```bash
   # Automated backup script
   ./scripts/backup_udos.sh
   ```

2. **Monitor logs**:
   ```bash
   # Check for errors daily
   grep "ERROR" memory/logs/udos.log
   ```

3. **Update regularly**:
   ```bash
   git pull origin main
   pip3 install -r requirements.txt --upgrade
   ```

4. **Test changes**:
   ```bash
   # Test in separate environment first
   git clone https://github.com/fredporter/uDOS.git test_udos
   ```

5. **Document issues**:
   Keep a personal troubleshooting log in MEMORY/PRIVATE

---

## Related Pages

- [Configuration](Configuration.md) - Settings and customization
- [Getting Started](Getting-Started.md) - Installation guide  
- [Command Reference](Command-Reference.md) - All commands
- [Architecture](Architecture.md) - System design
- [FAQ](FAQ.md) - Frequently asked questions

---

**Last Updated**: November 17, 2025  
**Version**: v1.0.22  
**See Also**: [Documentation Handbook](Documentation-Handbook.md)
