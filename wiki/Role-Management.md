# Role Management System

**Version:** v1.2.22  
**Status:** Production Ready

The Role Management System provides secure, bcrypt-protected role-based permissions with automatic wizard detection for project contributors.

## Overview

uDOS v1.2.22 introduces five permission levels:

| Role | Level | Typical User | Permissions |
|------|-------|--------------|-------------|
| **Viewer** | 0 | Guest, observer | Read-only access |
| **User** | 1 | Standard user | Basic commands |
| **Contributor** | 2 | Power user | Advanced features |
| **Admin** | 3 | System admin | Configuration access |
| **Wizard** | 4 | Developer | Full system access |

## Quick Start

### First Time Setup

```bash
# Set up initial password protection
ROLE SETUP

# Follow prompts:
# 1. Enter new password (min 8 chars)
# 2. Confirm password
# 3. System sets your role to ADMIN
```

### Check Current Role

```bash
ROLE STATUS
```

**Output:**
```
🎭 Current Role: ADMIN (Level 3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Permissions:
  ✅ Read knowledge guides
  ✅ Execute basic commands
  ✅ Manage files and workflows
  ✅ Modify system configuration
  ✅ Clear system logs
  ✅ Manage user profiles
  ❌ Access developer tools (requires WIZARD)

Security:
  🔒 Password protected (bcrypt)
  🔐 Cost factor: 12 rounds
  🛡️ Last role change: 2025-12-12 14:30:45

Commands:
  • ROLE SET <level> - Change your role
  • ROLE SETUP - Reset password protection
```

### Change Your Role

```bash
# Downgrade for safety (recommended for daily use)
ROLE SET user

# Upgrade for admin tasks (requires password)
ROLE SET admin
# Enter password: ********
```

## Commands

### ROLE SETUP

Initialize or reset password protection:

```bash
ROLE SETUP
```

**Process:**
1. Enter new password (min 8 characters)
2. Confirm password
3. System generates bcrypt hash (cost factor 12)
4. Saves to `memory/bank/user/user.json`
5. Sets your role to ADMIN

**Security:** Passwords are hashed with bcrypt (12 rounds). Never stored in plaintext.

### ROLE SET

Change your permission level:

```bash
ROLE SET <level>

# Examples:
ROLE SET viewer    # Read-only mode
ROLE SET user      # Standard user
ROLE SET contributor  # Power user
ROLE SET admin     # Administrator
ROLE SET wizard    # Developer (auto-detected or password-protected)
```

**Password Required For:**
- Upgrading to ADMIN or WIZARD
- Any upgrade beyond single level (viewer→contributor requires password)

**No Password Required For:**
- Downgrading (admin→user, user→viewer)
- Auto-detected wizard (git author in CREDITS.md)

### ROLE STATUS

View current role and permissions:

```bash
ROLE STATUS
```

Shows:
- Current role and level
- Permission matrix (✅ allowed, ❌ denied)
- Security information
- Available commands

### ROLE CHECK

Check required role for command (internal use):

```python
from core.services.role_manager import get_role_manager

role_mgr = get_role_manager()
if not role_mgr.check_permission('config', 'write'):
    return "❌ Permission denied. Requires ADMIN role."
```

## Permission Levels

### Viewer (Level 0)

**Purpose:** Guest access, safe exploration

**Can Do:**
- ✅ Read knowledge guides (`GUIDE`)
- ✅ View help (`HELP`, `COMMANDS`)
- ✅ Check status (`STATUS`)
- ✅ List files (`TREE`, `LIST`)
- ✅ View themes (`CONFIG` read-only)

**Cannot Do:**
- ❌ Create/modify files
- ❌ Execute workflows
- ❌ Change configuration
- ❌ Install extensions
- ❌ Access sensitive data

**Use Case:** Public demonstrations, kiosk mode, untrusted environments

### User (Level 1)

**Purpose:** Standard daily use

**Can Do (in addition to Viewer):**
- ✅ Create/edit files (`NEW`, `EDIT`, `DELETE`)
- ✅ Execute scripts (`RUN`)
- ✅ Manage workflows (`MISSION`)
- ✅ Use OK assistant (`OK ASK`, `OK MAKE`)
- ✅ Basic cleanup (`CLEAN`, `TIDY`)

**Cannot Do:**
- ❌ Modify system configuration
- ❌ Install extensions
- ❌ Clear system logs
- ❌ Access developer tools

**Use Case:** Daily work, script development, content creation

### Contributor (Level 2)

**Purpose:** Power users, advanced features

**Can Do (in addition to User):**
- ✅ Install extensions (`EXTENSION INSTALL`)
- ✅ Manage themes (`THEME SET`, `THEME CREATE`)
- ✅ Advanced workflows (`WORKFLOW ADVANCED`)
- ✅ Pattern management (`PATTERNS EXPORT`)
- ✅ Error diagnostics (`ERROR SHOW`)

**Cannot Do:**
- ❌ Modify core configuration
- ❌ Clear system logs
- ❌ Access dev mode

**Use Case:** Extension developers, advanced automation, system customization

### Admin (Level 3)

**Purpose:** System administration

**Can Do (in addition to Contributor):**
- ✅ Modify configuration (`CONFIG` write)
- ✅ Clear system logs (`PATTERNS CLEAR`, `ERROR CLEAR`)
- ✅ Manage user profiles (`ROLE SETUP`)
- ✅ Backup/restore system (`BACKUP`, `RESTORE`)
- ✅ Advanced diagnostics (`STATUS --health`)

**Cannot Do:**
- ❌ Access developer tools
- ❌ Modify core system files
- ❌ Debug internal code

**Use Case:** System maintenance, configuration management, user administration

### Wizard (Level 4)

**Purpose:** Core developers only

**Can Do (everything):**
- ✅ Full system access
- ✅ Developer tools (`DEV MODE`)
- ✅ Hot reload (`RELOAD`)
- ✅ Core file modification
- ✅ Debug internal code

**How to Get:**
1. **Auto-detection:** Git author matches name in `CREDITS.md`
2. **Manual:** Use password with `ROLE SET wizard`

**Use Case:** uDOS core development, debugging, system internals

## Auto-Detection

### Wizard Detection

System automatically grants wizard role if:

1. Git is configured:
   ```bash
   git config user.name
   # Returns: "Fred Porter" (example)
   ```

2. Name matches entry in `CREDITS.md`:
   ```markdown
   # Credits
   
   ## Core Development
   - Fred Porter (@fredporter) - Creator, lead developer
   ```

3. System checks on startup and role changes

**Security:**
- Requires valid git configuration
- Matches against project credits file
- Can be overridden with password protection
- Logged in system history

## Security Best Practices

### 1. Use Minimum Required Role

```bash
# Daily work
ROLE SET user

# Admin tasks
ROLE SET admin
# Do admin work...
ROLE SET user  # Downgrade when done
```

**Why:** Limits damage from mistakes or compromised sessions.

### 2. Set Strong Password

```bash
ROLE SETUP
# Password requirements:
# - Minimum 8 characters
# - Recommended: 12+ characters
# - Mix letters, numbers, symbols
```

**Why:** Bcrypt is strong, but only with good passwords.

### 3. Protect user.json

```bash
# Verify permissions
ls -la memory/bank/user/user.json
# Should be: -rw------- (600)

# If not, fix it:
chmod 600 memory/bank/user/user.json
```

**Why:** Contains bcrypt hash - should only be readable by you.

### 4. Regular Password Rotation

```bash
# Every 90 days
ROLE SETUP
# Enter new password
```

**Why:** Reduces risk from old password exposure.

### 5. Audit Role Changes

```bash
# Check history
HISTORY
# Look for: "Role changed from X to Y"
```

**Why:** Detect unauthorized role escalation.

## Integration Examples

### In Command Handlers

```python
from core.services.role_manager import get_role_manager, UserRole

class MyCommandHandler:
    def handle_sensitive_operation(self):
        role_mgr = get_role_manager()
        
        # Check required role
        if not role_mgr.has_permission(UserRole.ADMIN):
            return "❌ Permission denied. Requires ADMIN role."
        
        # Perform operation
        return "✅ Operation complete"
```

### In uPY Scripts

```upy
# Check role before sensitive operations
GET (role) → {$current_role}

IF {$current_role} < 3
  PRINT ('❌ Admin role required')
  EXIT
END IF

# Continue with admin operations
CONFIG (backup_all)
```

### In Workflows

```json
{
  "mission": "system-backup",
  "requirements": {
    "min_role": 3,
    "role_name": "admin"
  },
  "steps": [
    {"command": "BACKUP", "target": "system"},
    {"command": "BACKUP", "target": "user"}
  ]
}
```

## Configuration

Role settings in `memory/bank/user/user.json`:

```json
{
  "role": {
    "level": 3,
    "name": "admin",
    "password_hash": "$2b$12$...",
    "last_change": "2025-12-12T14:30:45Z",
    "wizard_detected": false
  }
}
```

**Fields:**
- `level`: Numeric role level (0-4)
- `name`: Role name (viewer, user, contributor, admin, wizard)
- `password_hash`: Bcrypt hash (cost factor 12)
- `last_change`: ISO timestamp of last role change
- `wizard_detected`: Boolean for auto-detected wizard status

## Permission Matrix

| Command Category | Viewer | User | Contributor | Admin | Wizard |
|-----------------|--------|------|-------------|-------|--------|
| Knowledge (GUIDE) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Help (HELP, COMMANDS) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Status (STATUS) | ✅ | ✅ | ✅ | ✅ | ✅ |
| File List (TREE, LIST) | ✅ | ✅ | ✅ | ✅ | ✅ |
| File Create/Edit | ❌ | ✅ | ✅ | ✅ | ✅ |
| Scripts (RUN) | ❌ | ✅ | ✅ | ✅ | ✅ |
| Workflows (MISSION) | ❌ | ✅ | ✅ | ✅ | ✅ |
| OK Assistant | ❌ | ✅ | ✅ | ✅ | ✅ |
| Extensions | ❌ | ❌ | ✅ | ✅ | ✅ |
| Themes | ❌ | ❌ | ✅ | ✅ | ✅ |
| Patterns | ❌ | ❌ | ✅ | ✅ | ✅ |
| Config (read) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Config (write) | ❌ | ❌ | ❌ | ✅ | ✅ |
| System Logs | ❌ | ❌ | ❌ | ✅ | ✅ |
| User Management | ❌ | ❌ | ❌ | ✅ | ✅ |
| Developer Tools | ❌ | ❌ | ❌ | ❌ | ✅ |
| Hot Reload | ❌ | ❌ | ❌ | ❌ | ✅ |
| Core Files | ❌ | ❌ | ❌ | ❌ | ✅ |

## Troubleshooting

### "Password incorrect"

1. Check caps lock
2. Try `ROLE SETUP` to reset password
3. Check `memory/bank/user/user.json` exists and is readable

### "Permission denied"

Check required role:
```bash
ROLE STATUS  # View your current role
ROLE SET admin  # Upgrade if needed (requires password)
```

### "Wizard auto-detection failed"

Verify git configuration:
```bash
git config user.name
# Should match name in CREDITS.md
```

Or set wizard manually:
```bash
ROLE SET wizard
# Enter password when prompted
```

### "Cannot downgrade from wizard"

Wizard role is permanent (for safety):
- Once auto-detected, stays wizard
- Manual wizard (via password) can downgrade
- Edit `user.json` manually to force change (advanced)

### Lost password

1. Backup current `user.json`:
   ```bash
   cp memory/bank/user/user.json memory/bank/user/user.json.backup
   ```

2. Delete role settings:
   ```bash
   # Edit user.json, remove "role" section
   ```

3. Restart uDOS and run:
   ```bash
   ROLE SETUP
   # Set new password
   ```

## Technical Details

### Bcrypt Implementation

```python
import bcrypt

# Hash password (cost factor 12)
password_hash = bcrypt.hashpw(
    password.encode('utf-8'),
    bcrypt.gensalt(rounds=12)
)

# Verify password
is_valid = bcrypt.checkpw(
    password.encode('utf-8'),
    stored_hash
)
```

**Cost Factor 12:** Approximately 250-300ms per hash verification on typical hardware. Protects against brute-force attacks.

### Role Level Hierarchy

```python
class UserRole(Enum):
    VIEWER = 0
    USER = 1
    CONTRIBUTOR = 2
    ADMIN = 3
    WIZARD = 4

def has_permission(self, required_role: UserRole) -> bool:
    return self.current_role.value >= required_role.value
```

### Wizard Detection Algorithm

```python
def is_wizard(self) -> bool:
    # 1. Check git config
    git_name = subprocess.check_output(
        ['git', 'config', 'user.name']
    ).decode().strip()
    
    # 2. Load CREDITS.md
    with open('CREDITS.md') as f:
        credits = f.read()
    
    # 3. Match name (case-insensitive)
    return git_name.lower() in credits.lower()
```

## See Also

- [Error Handling](Error-Handling.md) - Error management system
- [Configuration Guide](Getting-Started.md#configuration) - System setup
- [DEV MODE Guide](DEV-MODE-GUIDE.md) - Developer tools (wizard only)
- [Security Best Practices](Philosophy.md#security) - Overall security approach

## Version History

- **v1.2.22** (Dec 2025) - Initial release with bcrypt protection
  - Five-level role hierarchy
  - Password protection with bcrypt (cost factor 12)
  - Auto-detection for project wizards
  - Integration with all command handlers
  - Comprehensive permission matrix
