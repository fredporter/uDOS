# SHAKEDOWN & DESTROY Quick Reference

**Version:** v1.1.0  
**Updated:** 2026-01-29

---

## SHAKEDOWN Command

### Basic Validation
```bash
SHAKEDOWN
```
Runs 9 core checks:
- Framework initialization ✓
- Component availability ✓
- Locations database ✓
- Commands registered ✓
- Memory directories ✓
- TypeScript runtime ✓
- Handler modules ✓
- Services layer ✓
- User manager ✓

### Fresh Install Validation
```bash
SHAKEDOWN --fresh
```
Validates framework ready for first-time use:
1. Memory structure exists
2. All subdirectories present
3. Admin user registered
4. Admin initialized properly
5. Logging service ready
6. User manager ready
7. Critical handlers registered
8. Dispatcher ready (≥10 handlers)
9. GameState initializes

**Output Example:**
```
✓ Memory structure exists (logs, bank, private, wizard)
✓ Admin user initialized
✓ Services layer ready (logging, user manager)
✓ Framework ready (dispatcher, state, smartprompt)
Summary: 9/9 checks passed
```

### DESTROY Verification
```bash
SHAKEDOWN --destroy-verify
```
Verifies DESTROY command is safe to run:
1. Handler imports successfully
2. User manager functional
3. Current user exists
4. Has DESTROY permission
5. Memory directory writable
6. Archive directory accessible
7. Compost directory creatable
8. Audit logging available

**Output Example:**
```
✓ DESTROY handler ready
✓ User manager functional
✓ Current user: admin
✓ DESTROY permission: YES
✓ Memory writable: YES
✓ Archive ready: YES
Summary: 8/8 checks passed
```

### Detailed Output
```bash
SHAKEDOWN --detailed
```
Shows additional details for each check.

---

## DESTROY Command

### Interactive Menu (Recommended)
```bash
DESTROY
```
Shows an **interactive menu** that guides you through cleanup options step-by-step:

```
╔════════════════════════════════════════╗
║      DESTROY/CLEANUP OPTIONS           ║
╚════════════════════════════════════════╝

  1. Wipe User Data (clear users, API keys)
  2. Archive Memory (compost /memory)
  3. Wipe + Archive + Reload (complete cleanup)
  4. Nuclear Reset (factory defaults - DANGER!)
  0. Help

Choose an option [0-4]
```

Just **type the number** and press Enter. The TUI will confirm before executing.

### Direct Options (Legacy)
```bash
DESTROY 1                    # Wipe user data
DESTROY 2                    # Archive memory
DESTROY 3                    # Wipe + archive + reload
DESTROY 4                    # Nuclear reset
DESTROY --help               # Show help
```

### Show Detailed Help
```bash
DESTROY 0                    # Show help from menu
DESTROY --help               # Show help directly
```

---

## Cleanup Operations

### Option 1: Wipe User Data Only
```bash
DESTROY 1
```
**What it does:**
- Deletes all user profiles except admin
- Clears all API keys and credentials
- Removes OAuth tokens
- Resets to default admin user

**Safe:** Users can be recreated with `USER create [name] [role]`

### Option 2: Archive Memory (COMPOST)
```bash
DESTROY 2
```
**What it does:**
- Archives entire `/memory` to `.archive/compost/YYYY-MM-DD`
- Preserves data history
- Frees up `/memory` space
- Keeps users intact

**Safe:** Original data preserved in `.archive/`

### Option 3: Wipe + Archive + Reload
```bash
DESTROY 3
```
**What it does:**
- Wipes all user data and API keys
- Archives `/memory` to compost
- Hot reloads handlers
- Runs repair checks

**Safe:** Complete fresh start (keeps framework)

### Option 4: Nuclear Reset (FACTORY DEFAULT)
```bash
DESTROY 4
```
**⚠️ DANGER:** Complete system wipe:
- Deletes: users, memory, config, logs, API keys
- Resets: system to factory defaults
- **Requires additional confirmation**
- **Admin only** - cannot be undone easily

**Confirmation:**
```
Are you absolutely sure? [Yes/No/OK] (Enter=NO)
```

Type `yes` or `ok` to proceed.

---

## Examples

**Interactive (Recommended):**
```
DESTROY
Choose an option [0-4]  1
```

**Direct (Legacy):**
```
DESTROY 1
DESTROY 2
DESTROY 3
DESTROY 4
```

**With Flags (Legacy):**
```
DESTROY --wipe-user --compost
DESTROY --reset-all --confirm
```

---```bash
DESTROY --wipe-user
```
**Clears:**
- All non-admin users
- Admin user variables
- Admin environment
- API keys/credentials
- User config

**Preserves:**
- Memory (logs, bank, private, wizard)
- Core system files
- Framework

**Use Case:** Clean user data but keep system logs

---

### Option 2: Archive Memory Only
```bash
DESTROY --compost
```
**Archives to:** `.archive/compost/YYYY-MM-DD_HHMMSS/`

**Includes:**
- All logs
- Bank data
- Private files
- Wizard cache
- Archive metadata JSON

**Preserves:**
- Users and permissions
- Core system
- Core configuration

**Use Case:** Free up /memory space, preserve history

---

### Option 3: Wipe Users + Archive Memory
```bash
DESTROY --wipe-user --compost
```
**Combines both operations:**
1. Deletes all non-admin users
2. Resets admin variables
3. Archives entire /memory

**Result:** Clean slate for users, preserved history

---

### Option 4: Nuclear Reset (FACTORY DEFAULTS)
```bash
DESTROY --reset-all --confirm
```
⚠️ **WARNING: IRREVERSIBLE** (except .archive/ is preserved)

**Wipes:**
- All user profiles (except admin)
- All variables and environment
- All memory (logs, bank, private, wizard)
- All custom configuration
- All API keys/credentials

**Preserves:**
- .archive/ folder (history)
- Admin user (factory default, blank)
- Core framework
- Version information

**Output:** Shows what was deleted and provides recovery info

**Use Case:** Complete factory reset to defaults

---

## Combinations

### Wipe + Reload + Repair
```bash
DESTROY --wipe-user --compost --reload-repair
```
1. Delete non-admin users
2. Reset admin variables
3. Archive memory
4. Hot reload handlers
5. Run repair checks

---

## Safety Features

### Required for Nuclear Reset
```bash
DESTROY --reset-all --confirm
```
- Must have admin or destroy permission
- Must provide explicit `--confirm` flag
- Creates audit trail entry
- Preserves metadata of what was deleted

### Audit Trail
All operations logged to:
- `memory/logs/session-commands-YYYY-MM-DD.log`
- Unified logging with metadata

### Archive Metadata
Each compost entry includes:
```json
{
  "archived_at": "2026-01-29T15:30:45.123456",
  "archived_by": "admin",
  "action": "compost|nuclear_reset",
  "reason": "DESTROY operation type"
}
```

---

## Recovery

### Restore from Compost
```bash
# Find archived data
ls -lh .archive/compost/

# Browse content
ls -lh .archive/compost/2026-01-29_153045/memory/

# Manually restore if needed
cp -r .archive/compost/2026-01-29_153045/memory/* memory/
```

### After Factory Reset
1. Check system status: `SHAKEDOWN`
2. Recreate users: `USER create [name] [role]`
3. Reconfigure: `SETUP`
4. Verify ready: `SHAKEDOWN --fresh`

---

## Testing

### Run Full Test Suite
```bash
pytest core/tests/test_shakedown_destroy_v1_1_0.py -v
```

### Run Specific Tests
```bash
# Framework initialization
pytest core/tests/test_shakedown_destroy_v1_1_0.py::TestFrameworkInitialization -v

# SHAKEDOWN command
pytest core/tests/test_shakedown_destroy_v1_1_0.py::TestShakedownCommand -v

# DESTROY command
pytest core/tests/test_shakedown_destroy_v1_1_0.py::TestDestroyCommand -v

# Integration tests
pytest core/tests/test_shakedown_destroy_v1_1_0.py::TestIntegration -v
```

---

## Common Workflows

### 1. Fresh Install Verification
```bash
SHAKEDOWN --fresh
# Then: USER create [name] [role]
```

### 2. Pre-Reset Backup
```bash
DESTROY --compost
# Archives memory before other operations
```

### 3. User Cleanup
```bash
DESTROY --wipe-user
# Reset user data but keep system state
```

### 4. Full Factory Reset
```bash
DESTROY --reset-all --confirm
RESTART --full
SETUP
SHAKEDOWN --fresh
```

### 5. System Verification
```bash
SHAKEDOWN
SHAKEDOWN --fresh
SHAKEDOWN --destroy-verify
# All three should pass
```

---

## Troubleshooting

### SHAKEDOWN shows failures
1. Check: `SHAKEDOWN --detailed`
2. Run: `REPAIR` to fix issues
3. Verify: `SHAKEDOWN` again

### DESTROY verify fails
1. Check permissions: `USER current` (should be admin)
2. Check paths: `ls -la memory/ .archive/`
3. Check perms: `ls -la core/commands/ | grep destroy`

### Can't archive memory
1. Check space: `df -h memory/`
2. Check perms: `ls -la | grep archive`
3. Create manually: `mkdir -p .archive/compost`

---

## Key Concepts

| Term | Meaning |
|------|---------|
| **Wipe** | Delete file/data, cannot recover |
| **Compost** | Archive to .archive/compost/, preserves history |
| **Reset** | Return to factory defaults |
| **Nuclear** | Complete wipe (compost preserved) |
| **Factory** | Default admin user, blank variables |
| **Audit** | Logged event with metadata |

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `SHAKEDOWN` | Validate system |
| `DESTROY` | Cleanup/reset |
| `REPAIR` | Fix issues |
| `RESTART` | Reload system |
| `SETUP` | Configure system |
| `USER` | Manage users |
| `LOGS` | View activity |

---

## References

- Full docs: [SHAKEDOWN-DESTROY-UPDATES.md](SHAKEDOWN-DESTROY-UPDATES.md)
- Test suite: [test_shakedown_destroy_v1_1_0.py](../core/tests/test_shakedown_destroy_v1_1_0.py)
- Handler code: [shakedown_handler.py](../core/commands/shakedown_handler.py)
- Handler code: [destroy_handler.py](../core/commands/destroy_handler.py)
