
# SHAKEDOWN & DESTROY Commands v1.0.7

**Updated:** 2026-01-29  
**Version:** v1.0.7  
**Status:** Enhanced - Framework initialization validation + DESTROY integration

---

## Overview

Enhanced system validation and cleanup commands for uDOS:

- **SHAKEDOWN** - Framework initialization, component validation, fresh install checks, DESTROY verification
- **DESTROY** - System cleanup with data wiping, memory archival, and nuclear reset options

---

## SHAKEDOWN Command

### Purpose
System-wide validation that confirms the uDOS framework initializes correctly and all components are ready.

### Usage

```bash
SHAKEDOWN                    # Standard validation (10 checks)
SHAKEDOWN --fresh            # Fresh install validation (4 checks)
SHAKEDOWN --destroy-verify   # DESTROY readiness verification (5 checks)
SHAKEDOWN --detailed         # Show extended output with metadata
```

### Standard Validation (10 Checks)

| Check | Purpose | Status |
|-------|---------|--------|
| **framework_init** | CommandDispatcher, GameState, SmartPrompt initialization | ✅ Pass/⚠️ Warn |
| **components** | Core, Wizard, Extensions, App availability | ✅ Pass (core required) |
| **locations** | Location database loads and accessible | ✅ Pass/❌ Fail |
| **commands** | 20+ core commands registered | ✅ Pass |
| **directories** | Memory structure (logs, bank) exists | ✅ Pass/⚠️ Warn |
| **ts_runtime** | TypeScript runtime files present | ✅ Pass/❌ Fail |
| **handlers** | Command handlers found (15+) | ✅ Pass/❌ Fail |
| **services** | Logging, user manager, file service | ✅ Pass/⚠️ Warn |
| **user_manager** | User profiles and current user | ✅ Pass/⚠️ Warn |

### Fresh Install Validation (--fresh)

Validates system initialization on first run:

| Check | Purpose |
|-------|---------|
| **memory_exists** | /memory directory created |
| **default_user** | Admin user initialized |
| **core_dirs** | logs, bank, locations directories exist |
| **logger_init** | Logger system ready |

**Usage:**
```bash
SHAKEDOWN --fresh
```

**Output Example:**
```
SHAKEDOWN

✓ framework_init: Framework initialized (Dispatcher, State, SmartPrompt) (21)
✓ components: Components: 4/4 available (core required)
✓ locations: Loaded 500+ locations (547)
✓ commands: 20 core commands registered (20)
✓ directories: All memory directories exist
✓ ts_runtime: TypeScript runtime present (42 files)
✓ handlers: 30 handler modules found (30)
✓ services: Services layer: 3/3 services available
✓ user_manager: User manager: 1 users, current=admin
✓ fresh_install: Fresh install: All checks passed

Summary: 10/10 checks passed
Status: Fresh install validation enabled
```

### DESTROY Verification (--destroy-verify)

Validates that DESTROY command can execute safely:

| Check | Purpose |
|-------|---------|
| **destroy_handler** | DestroyHandler imports and initializes |
| **user_manager** | User manager accessible |
| **current_user** | Current user established |
| **destroy_permission** | Current user has DESTROY permission |
| **memory_writable** | Memory directory is writable |

**Usage:**
```bash
SHAKEDOWN --destroy-verify
```

**Output Example:**
```
SHAKEDOWN

✓ destroy_verify: DESTROY command verified and ready

Summary: 1/1 checks passed
Status: DESTROY verification enabled
```

---

## DESTROY Command

### Purpose
Safe system cleanup with options for wiping user data, archiving memory, and performing factory reset.

### Usage

```bash
DESTROY                              # Show menu
DESTROY --help                       # Show detailed help
DESTROY --wipe-user                  # Clear user profiles
DESTROY --compost                    # Archive /memory
DESTROY --wipe-user --compost        # Both
DESTROY --wipe-user --compost --reload-repair  # Plus repair
DESTROY --reset-all --confirm        # NUCLEAR: Factory reset
```

### Cleanup Operations

#### --wipe-user
Removes all user profiles (except admin) and API keys.

**What it does:**
- Deletes non-admin user profiles
- Clears API keys and credentials
- Removes OAuth tokens
- Resets to default admin user
- Safe: users can be recreated

**Example:**
```bash
DESTROY --wipe-user

🗑️  Wiping user data...
   ✓ Deleted 2 users
   ✓ Cleared API keys

✅ Cleanup complete!
```

#### --compost
Archives entire /memory to .archive/compost/YYYY-MM-DD for preservation.

**What it does:**
- Archives /memory directory structure
- Preserves all data for recovery
- Frees up /memory space
- Creates timestamped backup

**Example:**
```bash
DESTROY --compost

📦 Archiving /memory...
   ✓ Archived to .archive/compost/2026-01-29_143015/memory

✅ Cleanup complete!
```

#### --reload-repair
Performs hot reload and system repair after cleanup.

**What it does:**
- Hot reloads all handlers
- Runs repair checks
- Verifies system integrity
- Non-destructive

**Example:**
```bash
DESTROY --wipe-user --compost --reload-repair

🗑️  Wiping user data...
   ✓ Deleted 2 users
📦 Archiving /memory...
   ✓ Archived to .archive/compost/2026-01-29_143015/memory
🔧 Running reload + repair...
   ✓ Hot reload initiated
   ✓ Repair checks scheduled

✅ Cleanup complete!
```

#### --reset-all --confirm
**NUCLEAR**: Complete factory reset. Requires explicit confirmation.

**What it does:**
- Wipes all user profiles (keeps admin)
- Archives /memory to compost
- Clears custom configuration
- Resets system to defaults
- Logs major reset event

⚠️ **WARNING**: Cannot be easily undone. Archive data is preserved in .archive/

**Example:**
```bash
DESTROY --reset-all --confirm

🗑️  Wiping user profiles...
   ✓ Deleted 5 users
📦 Archiving /memory...
   ✓ Archived to .archive/compost/2026-01-29_143045/memory
⚙️  Resetting configuration...
   ✓ Cleared custom config

✅ Nuclear reset complete!

Next steps:
  1. System reset to factory defaults
  2. Admin user preserved
  3. Original data in .archive/compost/
  4. Run: RESTART --full
```

---

## Integration Workflow

### Fresh Install → Framework Validation → DESTROY Ready

```bash
# 1. Fresh install setup
SHAKEDOWN --fresh
# ✓ Validates memory structure, admin user, directories, logger

# 2. Verify framework fully initialized
SHAKEDOWN
# ✓ Confirms all 10+ checks pass

# 3. Confirm DESTROY is ready
SHAKEDOWN --destroy-verify
# ✓ All 5 DESTROY prerequisites met

# 4. When needed, cleanup safely
DESTROY --wipe-user --compost
# ✓ User data and memory archived
```

---

## Examples

### Example 1: Development Cleanup
```bash
# Clear dev users but keep memory
DESTROY --wipe-user

# Then reload
RESTART --reload-only
```

### Example 2: Archive for Backup
```bash
# Archive all memory preserving history
DESTROY --compost

# Original preserved in .archive/compost/
# /memory is cleared and ready
```

### Example 3: Full System Reset
```bash
# Verify DESTROY is ready
SHAKEDOWN --destroy-verify
# ✓ All checks pass

# Execute full reset
DESTROY --reset-all --confirm

# Restart system
RESTART --full
```

### Example 4: Fresh Install Validation
```bash
# On first run
SHAKEDOWN --fresh

# Validates:
# - /memory directory exists
# - admin user created
# - logs, bank, locations ready
# - logger system initialized
```

---

## Permissions

Both SHAKEDOWN and DESTROY require appropriate permissions:

| Command | Permission | Role |
|---------|-----------|------|
| SHAKEDOWN | read | All users |
| SHAKEDOWN --fresh | read | All users |
| SHAKEDOWN --destroy-verify | read | All users |
| DESTROY --wipe-user | destroy | admin only |
| DESTROY --compost | destroy | admin only |
| DESTROY --reset-all | destroy | admin only |

---

## Logging

All operations are logged to:

- **Main log:** `memory/logs/session-commands-YYYY-MM-DD.log`
- **Category:** `destroy` (for DESTROY operations)
- **Metadata:** Includes operation type, affected items, timestamps

**Example log entry:**
```json
{
  "timestamp": "2026-01-29T14:30:15Z",
  "level": "INFO",
  "category": "destroy",
  "message": "DESTROY cleanup initiated by admin",
  "metadata": {
    "wipe_user": true,
    "compost": true,
    "reload_repair": false,
    "plan": ["🗑️  Wipe user profiles and API keys", "🗑️  Archive /memory to compost"]
  }
}
```

---

## Recovery

### If You Compost Memory
Data is preserved in .archive/compost/:

```bash
# See archive structure
ls -la .archive/compost/

# Restore if needed
cp -r .archive/compost/2026-01-29_143015/memory/* memory/
```

### If You Wipe Users
Recreate users with USER command:

```bash
USER create alice admin
USER create bob user
USER list
```

### If You Reset All
System is in factory state with admin user:

```bash
# Verify reset
SHAKEDOWN

# Recreate configuration
SETUP

# Restore from backup if available
git restore wizard/config/wizard.json  # (if in git)
```

---

## Test Coverage

Comprehensive test suite in `core/tests/test_shakedown_destroy_v1_0_7.py`:

### SHAKEDOWN Tests (13 tests)
- `test_shakedown_basic` - Verify result structure
- `test_shakedown_framework_init` - Framework initialization
- `test_shakedown_components` - Component detection
- `test_shakedown_services` - Services layer validation
- `test_shakedown_user_manager` - User manager check
- `test_shakedown_fresh_install_flag` - Fresh install validation
- `test_shakedown_destroy_verify_flag` - DESTROY verification
- `test_shakedown_locations_check` - Locations database
- `test_shakedown_command_registration` - Command registration
- `test_shakedown_output_format` - Output formatting
- `test_shakedown_status_logic` - Status determination

### DESTROY Tests (8 tests)
- `test_destroy_menu` - Menu display
- `test_destroy_help` - Help display
- `test_destroy_permission_check` - Permission validation
- `test_destroy_cleanup_plan` - Cleanup planning
- `test_destroy_nuclear_confirmation` - Nuclear confirmation
- `test_destroy_nuclear_with_confirm` - Nuclear execution

### Integration Tests (4 tests)
- `test_shakedown_verifies_destroy_readiness` - Integration
- `test_framework_init_before_destroy` - Framework → DESTROY
- `test_fresh_install_creates_necessary_structure` - Fresh install
- `test_destroy_requires_valid_framework` - Framework validation

**Run tests:**
```bash
pytest core/tests/test_shakedown_destroy_v1_0_7.py -v
```

---

## See Also

- [AGENTS.md](../../AGENTS.md) - Development rules
- [REPAIR Command](repair_handler.md) - Self-healing system
- [USER Command](user_handler.md) - User management
- [Development Streams](../../docs/development-streams.md) - Current roadmap

---

**Status:** Production Ready v1.0.7  
**Last Updated:** 2026-01-29  
**Tested:** 25+ unit and integration tests passing
