# 🧙‍♂️ uDOS Enhanced Debugging & Self-Healing Guide

## 🎯 Overview

uDOS features an advanced debugging system with NetHack-inspired error messages and automatic self-healing capabilities that adapt to your user role.

## 🎭 Role-Based Debugging

### 👑 Wizard/Developer
- **Full debug info** with stack traces and performance monitoring
- **Enhanced error details** with technical information
- **Interactive debug shells** for investigation
- **NetHack commentary** with witty error messages
- **Self-healing** with retry mechanisms

### 🛡️ Admin/Power User
- **Moderate debug info** with helpful suggestions
- **Self-healing** with progress indicators
- **System health monitoring**
- **Adventure log** access

### 👤 Regular User
- **Friendly error messages** with simple explanations
- **Automatic self-healing** (invisible to user)
- **Helpful hints** based on error type
- **No technical jargon**

## 🎲 NetHack-Style Error Messages

The system provides entertaining error messages inspired by NetHack:

- **Permission errors**: "The door is locked. You need a key."
- **Missing files**: "You search the dungeon but find nothing here."
- **Network issues**: "Your carrier pigeon got lost in a storm."
- **Memory problems**: "Your brain is full. You forget something important."
- **Disk space**: "Your bag of holding is completely full."

## 🔧 Self-Healing Mechanisms

uDOS automatically attempts to fix common issues:

1. **Permission fixes**: Automatically chmod +x scripts
2. **File restoration**: Restore from backups or templates
3. **Network recovery**: Try alternative endpoints
4. **Memory cleanup**: Clear temporary files and caches
5. **Disk cleanup**: Remove old logs and temporary files

## 📊 Available Commands

### Command Line
```bash
DEBUG logs      # Show recent error logs
DEBUG health    # System health check
DEBUG reset     # Reset error counters
DEBUG test      # Run debug system test
ADVENTURE       # View NetHack-style adventure log
```

### VS Code Tasks
- 🧪 Test Debug System
- 🔍 Show Debug Logs  
- 🩺 System Health Check
- 🔄 Reset Debug Counters

## 📁 Log Files

- `sandbox/logs/error.log` - Technical error details
- `sandbox/logs/adventure.log` - NetHack-style commentary
- `sandbox/logs/debug.log` - Detailed debug information (dev only)
- `sandbox/logs/performance.log` - Performance metrics (dev only)

## 🎮 Adventure Log Examples

```
2025-08-27 21:30:09 You enter the debugging dungeon...
2025-08-27 21:30:09 A wild segfault appears!
2025-08-27 21:30:09 You cast self-healing. It's super effective!
2025-08-27 21:30:10 The CPU sprites are working overtime!
2025-08-27 21:30:15 Your bag of holding is getting heavy.
```

## 🚀 Integration

The enhanced debugging system is automatically integrated with:
- Core uDOS scripts (ucode.sh, start-udos.sh, uscript.sh)
- VS Code development environment
- User command interface
- Performance monitoring system

## 🔍 Troubleshooting

If you encounter issues:
1. Run `DEBUG test` to verify system integrity
2. Check `DEBUG health` for system status
3. Use `DEBUG reset` to clear error counters
4. View `ADVENTURE` for a summary of recent events

The system provides increasingly helpful messages with each retry attempt, and developers get access to interactive debug shells for investigation.
