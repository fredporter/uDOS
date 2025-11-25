# DEV MODE Guide

**Version:** v1.5.3+
**Status:** Production Ready
**Author:** uDOS Development Team

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Master User Setup](#master-user-setup)
4. [Commands](#commands)
5. [Permission System](#permission-system)
6. [Session Management](#session-management)
7. [Security](#security)
8. [Activity Logging](#activity-logging)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [API Reference](#api-reference)

---

## Overview

DEV MODE is a secure development environment for uDOS master users. It provides:

- **Master User Authentication** - Password-based access control
- **Dangerous Command Protection** - Whitelisting system for risky operations
- **Session Management** - Auto-save, restore, timeout (1 hour)
- **Activity Logging** - Comprehensive audit trail (text + JSON)
- **Development Tools** - Hot reload, debugging, system access

### When to Use DEV MODE

✅ **Use DEV MODE for:**
- System configuration changes
- Database operations (DELETE, WIPE, RESET)
- Direct code execution (EXECUTE, SHELL, EVAL)
- Extension development and testing
- Advanced troubleshooting

❌ **Don't Use DEV MODE for:**
- Regular daily usage
- Learning uDOS commands
- Creating content (guides, diagrams, checklists)
- Standard knowledge bank operations

---

## Quick Start

### 1. Enable DEV MODE

```
uDOS> DEV MODE ON
🔐 Master user password: ********
✅ DEV MODE activated
🔧 DEV>
```

### 2. Check Status

```
🔧 DEV> DEV MODE STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DEV MODE Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status:           ✅ ACTIVE
User:             fred (master)
Session Started:  2025-11-25 14:30:22
Commands Run:     42
Session File:     memory/logs/dev_mode_session.json

⚠️  Dangerous commands are ENABLED. Use caution.
```

### 3. Disable DEV MODE

```
🔧 DEV> DEV MODE OFF
✅ DEV MODE deactivated
Session saved to: memory/logs/dev_mode_session.json
uDOS>
```

---

## Master User Setup

### Configuration (.env)

Add these lines to your `.env` file:

```bash
# Master User Configuration (DEV MODE)
UDOS_MASTER_USER=your_username
UDOS_MASTER_PASSWORD=your_secure_password
```

**Important:**
- Use a **strong password** (12+ characters, mixed case, numbers, symbols)
- Keep `.env` secure and **never commit to git** (already in .gitignore)
- Password is hashed with SHA256 before storage

### Verification

Test your master user configuration:

```bash
# In uDOS
uDOS> DEV MODE ON
🔐 Master user password: ********

# If successful:
✅ DEV MODE activated
🔧 DEV>

# If failed:
❌ Authentication failed. Incorrect password or not configured as master user.
```

---

## Commands

### DEV MODE ON

**Description:** Enable DEV MODE (master user only)

**Syntax:**
```
DEV MODE ON
```

**Behavior:**
- Prompts for master user password
- Verifies credentials against .env configuration
- Activates session with 1-hour timeout
- Changes prompt to `🔧 DEV>`
- Enables dangerous commands

**Example:**
```
uDOS> DEV MODE ON
🔐 Master user password: ********
✅ DEV MODE activated
🔧 DEV>
```

---

### DEV MODE OFF

**Description:** Disable DEV MODE and save session

**Syntax:**
```
DEV MODE OFF
```

**Behavior:**
- Saves current session to disk
- Logs activity summary
- Resets prompt to `uDOS>`
- Blocks dangerous commands

**Example:**
```
🔧 DEV> DEV MODE OFF
💾 Saving DEV MODE session...
✅ Session saved (42 commands, 28 min active)
uDOS>
```

---

### DEV MODE STATUS

**Description:** Show current DEV MODE status

**Syntax:**
```
DEV MODE STATUS
```

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DEV MODE Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status:           ✅ ACTIVE
User:             fred (master)
Session Started:  2025-11-25 14:30:22
Uptime:           28 minutes
Commands Run:     42
Last Activity:    2025-11-25 14:58:10
Session File:     memory/logs/dev_mode_session.json
Timeout:          60 minutes (32 min remaining)

Dangerous Commands Enabled:
  • DELETE    • DESTROY   • REPAIR
  • RESET     • WIPE      • EXECUTE
  • SHELL     • EVAL      • IMPORT
  • LOAD

⚠️  DEV MODE grants elevated privileges. Use caution.
```

---

### DEV MODE HELP

**Description:** Show DEV MODE help information

**Syntax:**
```
DEV MODE HELP
```

**Output:**
- Command reference
- Permission system explanation
- Security warnings
- Examples

---

## Permission System

### Dangerous Commands

These commands require DEV MODE to be active:

| Command | Risk Level | Description |
|---------|-----------|-------------|
| `DELETE` | 🔴 HIGH | Permanently delete files/data |
| `DESTROY` | 🔴 HIGH | Remove database records |
| `REPAIR` | 🟡 MEDIUM | Auto-repair system (can overwrite) |
| `RESET` | 🔴 HIGH | Reset configuration to defaults |
| `WIPE` | 🔴 HIGH | Clear entire memory/database |
| `EXECUTE` | 🔴 HIGH | Run arbitrary code |
| `SHELL` | 🔴 HIGH | Execute shell commands |
| `EVAL` | 🔴 HIGH | Evaluate Python expressions |
| `IMPORT` | 🟡 MEDIUM | Load external modules |
| `LOAD` | 🟡 MEDIUM | Load and execute scripts |

### Permission Checks

When DEV MODE is **OFF:**
```
uDOS> DELETE knowledge/test.md
❌ Permission denied: DELETE requires DEV MODE
   Use 'DEV MODE ON' to enable (master user only)
```

When DEV MODE is **ON:**
```
🔧 DEV> DELETE knowledge/test.md
⚠️  DANGEROUS OPERATION: DELETE
Continue? (yes/no): yes
✅ Deleted: knowledge/test.md
```

### Bypassing Checks

For automation/scripting:
```bash
# Force mode (skip confirmation)
🔧 DEV> DELETE knowledge/test.md --force

# Dry run (preview without execution)
🔧 DEV> DELETE knowledge/*.md --dry-run
```

---

## Session Management

### Session Lifecycle

1. **Activation** - `DEV MODE ON` creates new session
2. **Activity** - Commands logged, timeout refreshed
3. **Persistence** - Auto-saved to `dev_mode_session.json`
4. **Timeout** - 1 hour inactivity = auto-disable
5. **Deactivation** - `DEV MODE OFF` saves and exits

### Session File

**Location:** `memory/logs/dev_mode_session.json`

**Format:**
```json
{
  "is_active": true,
  "session_start": "2025-11-25T14:30:22",
  "authenticated_user": "fred",
  "command_count": 42,
  "last_activity": "2025-11-25T14:58:10",
  "timeout_minutes": 60
}
```

### Timeout Behavior

**Default:** 1 hour (60 minutes)

**Inactivity Auto-Disable:**
```
🔧 DEV> [61 minutes of inactivity]
⏱️  DEV MODE timeout (60 min exceeded)
💾 Session saved automatically
uDOS>
```

**Configurable Timeout:**
```bash
# In .env
UDOS_DEV_MODE_TIMEOUT=120  # 2 hours
```

### Session Restore

On startup, DEV MODE checks for active sessions:
```
🌀 uDOS v1.5.3 Startup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 Previous DEV MODE session found (started 28 min ago)
   Restore session? (yes/no): yes
✅ DEV MODE session restored
🔧 DEV>
```

---

## Security

### Authentication

**Method:** Password-based with SHA256 hashing

**Process:**
1. User enters password
2. System hashes input with SHA256
3. Compares hash against `UDOS_MASTER_PASSWORD` in .env
4. Grants access only on exact match

**Security Features:**
- Password not stored in plaintext
- Password not logged
- Failed attempts logged to audit trail
- No password hints or recovery (by design)

### Best Practices

✅ **DO:**
- Use strong passwords (12+ characters)
- Keep `.env` secure and private
- Log out when finished (`DEV MODE OFF`)
- Review activity logs regularly
- Limit DEV MODE sessions to necessary operations

❌ **DON'T:**
- Share master password
- Commit `.env` to version control
- Leave DEV MODE active unattended
- Use simple/common passwords
- Run untrusted code in DEV MODE

### Threat Model

**Protected Against:**
- ✅ Accidental dangerous operations (normal users)
- ✅ Unauthorized access (password required)
- ✅ Privilege escalation (master user only)
- ✅ Untracked changes (full audit logging)

**Not Protected Against:**
- ❌ Compromised .env file
- ❌ Physical access to system
- ❌ Master user malicious actions
- ❌ Social engineering

---

## Activity Logging

### Log Files

**Text Log:** `memory/logs/dev_mode.log`
```
[2025-11-25 14:30:22] DEV MODE ACTIVATED - User: fred
[2025-11-25 14:32:15] COMMAND: DELETE knowledge/test.md
[2025-11-25 14:35:08] COMMAND: RESET config --force
[2025-11-25 14:58:10] DEV MODE DEACTIVATED - Session: 42 commands, 28 min
```

**JSON Log:** `memory/logs/dev_mode.json`
```json
[
  {
    "timestamp": "2025-11-25T14:30:22",
    "event": "ACTIVATED",
    "user": "fred",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  {
    "timestamp": "2025-11-25T14:32:15",
    "event": "COMMAND",
    "command": "DELETE",
    "params": ["knowledge/test.md"],
    "user": "fred"
  }
]
```

### Log Rotation

**Automatic:** Daily rotation at midnight
- Old logs archived to `memory/logs/archive/`
- Format: `dev_mode_YYYYMMDD.log`
- Retention: 30 days (configurable)

**Manual:**
```
🔧 DEV> LOGS ROTATE
✅ Rotated dev_mode.log → dev_mode_20251125.log
```

### Audit Trail

All DEV MODE activity is logged:
- ✅ Authentication attempts (success/failure)
- ✅ Session start/stop
- ✅ All dangerous commands
- ✅ Configuration changes
- ✅ Timeout events
- ✅ Errors and warnings

**Review Logs:**
```
🔧 DEV> LOGS SHOW --last 50
# Shows last 50 DEV MODE log entries
```

---

## Best Practices

### Development Workflow

**1. Enable DEV MODE Only When Needed**
```
# Good:
uDOS> DEV MODE ON
🔧 DEV> DELETE old_files/*.md
🔧 DEV> RESET config
🔧 DEV> DEV MODE OFF

# Bad:
uDOS> DEV MODE ON
🔧 DEV> [leave active all day]
```

**2. Use Dry Runs for Safety**
```
# Preview before execution
🔧 DEV> DELETE knowledge/*.md --dry-run
Would delete:
  - knowledge/test1.md
  - knowledge/test2.md
  - knowledge/test3.md

# Confirm and execute
🔧 DEV> DELETE knowledge/*.md
```

**3. Review Changes Before Committing**
```
# Check what changed
🔧 DEV> git diff

# Review DEV MODE logs
🔧 DEV> LOGS SHOW --today
```

### Security Checklist

- [ ] Strong master password configured (.env)
- [ ] `.env` file in `.gitignore`
- [ ] DEV MODE disabled when not in use
- [ ] Activity logs reviewed regularly
- [ ] Session timeout configured (1 hour default)
- [ ] Backup created before major changes
- [ ] Changes tested in sandbox first

---

## Troubleshooting

### Authentication Failed

**Problem:**
```
uDOS> DEV MODE ON
🔐 Master user password: ********
❌ Authentication failed
```

**Solutions:**
1. Check `.env` file exists at project root
2. Verify `UDOS_MASTER_USER` matches current username
3. Confirm `UDOS_MASTER_PASSWORD` is correct
4. Check file permissions on `.env` (should be readable)

**Debug:**
```python
# Test config loading
from core.config.config_manager import get_config_manager
config = get_config_manager()
print(config.get('UDOS_MASTER_USER'))  # Should match your username
print(bool(config.get('UDOS_MASTER_PASSWORD')))  # Should be True
```

---

### Session Not Saving

**Problem:**
```
🔧 DEV> DEV MODE OFF
❌ Error: Could not save session
```

**Solutions:**
1. Check `memory/logs/` directory exists
2. Verify write permissions
3. Check disk space

**Fix:**
```bash
# Create logs directory
mkdir -p memory/logs

# Set permissions
chmod 755 memory/logs
```

---

### Dangerous Commands Still Blocked

**Problem:**
```
🔧 DEV> DELETE test.md
❌ Permission denied: DELETE requires DEV MODE
```

**Solutions:**
1. Verify DEV MODE is actually active (`DEV MODE STATUS`)
2. Check prompt shows `🔧 DEV>` (not `uDOS>`)
3. Session may have timed out - re-enable DEV MODE

---

### Timeout Too Short/Long

**Problem:**
```
⏱️  DEV MODE timeout (60 min exceeded)
```

**Solution:**

Edit `.env`:
```bash
# Extend timeout to 2 hours
UDOS_DEV_MODE_TIMEOUT=120

# Or disable timeout (not recommended)
UDOS_DEV_MODE_TIMEOUT=0
```

---

## API Reference

### DevModeManager Class

**Location:** `core/services/dev_mode_manager.py`

#### Methods

**`authenticate(password: str) -> bool`**
- Authenticate master user with password
- Returns True if successful, False otherwise

**`enable() -> bool`**
- Enable DEV MODE (after successful authentication)
- Creates session and starts logging
- Returns True if enabled, False on error

**`disable() -> bool`**
- Disable DEV MODE
- Saves session to disk
- Returns True if disabled, False on error

**`check_permission(command: str) -> bool`**
- Check if command requires DEV MODE
- Returns True if allowed, False if blocked

**`log_activity(message: str, level: str = 'INFO')`**
- Log DEV MODE activity to files
- Writes to both text and JSON logs

**`get_status() -> Dict[str, Any]`**
- Get current DEV MODE status
- Returns dict with session info

#### Properties

**`is_active: bool`**
- Current DEV MODE state (True/False)

**`session_start: datetime`**
- When current session started

**`authenticated_user: str`**
- Username of authenticated master user

**`command_count: int`**
- Number of commands run in session

**`dangerous_commands: Set[str]`**
- Set of commands requiring DEV MODE

### Singleton Pattern

```python
from core.services.dev_mode_manager import get_dev_mode_manager

# Get global instance
dev = get_dev_mode_manager()

# Check status
if dev.is_active:
    print("DEV MODE active")

# Check permission
if dev.check_permission('DELETE'):
    # Execute dangerous operation
    pass
else:
    print("Permission denied")
```

### Integration Example

```python
from core.services.dev_mode_manager import get_dev_mode_manager

def handle_delete_command(params, grid, parser):
    """Handle DELETE command with DEV MODE check."""
    dev = get_dev_mode_manager()

    # Check permission
    if not dev.check_permission('DELETE'):
        return "❌ Permission denied: DELETE requires DEV MODE"

    # Confirm dangerous operation
    if not confirm_delete():
        return "❌ Delete cancelled"

    # Log activity
    dev.log_activity(f"DELETE: {params}", level='WARNING')

    # Execute delete
    try:
        result = perform_delete(params)
        dev.log_activity(f"DELETE successful: {params}", level='INFO')
        return f"✅ Deleted: {params}"
    except Exception as e:
        dev.log_activity(f"DELETE failed: {e}", level='ERROR')
        return f"❌ Delete failed: {e}"
```

---

## Appendix

### Command Comparison

| Command | Normal User | DEV MODE User |
|---------|------------|---------------|
| `HELP` | ✅ Allowed | ✅ Allowed |
| `SEARCH` | ✅ Allowed | ✅ Allowed |
| `GENERATE GUIDE` | ✅ Allowed | ✅ Allowed |
| `DELETE` | ❌ Blocked | ✅ Allowed |
| `RESET` | ❌ Blocked | ✅ Allowed |
| `EXECUTE` | ❌ Blocked | ✅ Allowed |

### Related Documentation

- **Configuration Sync:** See `CONFIG-SYNC-GUIDE.md`
- **Asset Management:** See `ASSETS-GUIDE.md`
- **uCODE Language:** See `UCODE_LANGUAGE.md`
- **Architecture:** See `wiki/Architecture.md`

---

**Version:** v1.5.3
**Last Updated:** 2025-11-25
**Maintainer:** uDOS Development Team
**License:** See LICENSE.txt
