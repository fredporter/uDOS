# DEV MODE Guide - Master User Development Environment

**Version:** 1.0.0
**Target:** v1.5.0
**Created:** 2025-11-25
**Status:** 📋 Planned for v1.5.0 implementation

---

## 🎯 Overview

**DEV MODE** is a master-user-only development environment that enables live Gemini coding assistance, dangerous system operations, and advanced debugging tools directly within the uDOS TUI. It's designed for core developers and system administrators who need unrestricted access for development and troubleshooting.

### Key Features
- 🔐 **Master User Restrictions** - Password-protected access
- 🤖 **Gemini TUI Integration** - Live AI coding assistance
- 🛠️ **Development Tools** - Debugger, profiler, test runner
- ⚠️ **Dangerous Operations** - DELETE, DESTROY, system modifications
- 📊 **Activity Logging** - Complete audit trail
- 🔄 **Hot Reload** - Live code changes without restart

---

## 🚀 Quick Start

### Enable DEV MODE

```
uDOS> DEV MODE ON
🔐 Master User Authentication Required
Enter master password: ********

✅ DEV MODE ACTIVATED
⚠️  You now have unrestricted system access
⚠️  All actions are logged to memory/logs/dev_mode.log

📋 [MAIN] 🔧 DEV>
```

### Disable DEV MODE

```
📋 [MAIN] 🔧 DEV> DEV MODE OFF
✅ DEV MODE DEACTIVATED
Returned to standard user permissions

📋 [MAIN] 🌀>
```

---

## 🔐 Master User Setup

### Initial Configuration

**1. Set Master Password (First Run)**
```bash
# Run setup wizard
./start_udos.sh --setup-master

# Or configure via .env
echo "UDOS_MASTER_PASSWORD=your_secure_password" >> .env
echo "UDOS_MASTER_USER=Fred" >> .env
```

**2. Verify Master User**
```
uDOS> CONFIG SHOW
╔═══════════════════════════════════════╗
║  Master User: Fred                   ║
║  Status: ✅ Configured                ║
║  DEV MODE: ❌ Inactive                ║
╚═══════════════════════════════════════╝
```

### Security Best Practices

- ✅ Use strong password (12+ characters, mixed case, numbers, symbols)
- ✅ Store password securely (password manager, encrypted vault)
- ✅ Never commit `.env` to version control
- ✅ Rotate password every 90 days
- ✅ Review DEV MODE logs regularly
- ❌ Don't share master password
- ❌ Don't enable DEV MODE on production systems
- ❌ Don't leave DEV MODE active when unattended

---

## 🤖 Gemini TUI Integration

### Live Coding Assistance

**1. Ask Questions**
```
📋 [MAIN] 🔧 DEV> OK ASK how do I implement UNDO for file operations?
🤖 Gemini Response:
To implement UNDO for file operations:

1. Create a FileOperation class to track:
   - operation_type (create, delete, move, edit)
   - file_path (original location)
   - backup_data (file contents or metadata)
   - timestamp

2. Maintain an undo_stack in core/uDOS_main.py:
   undo_stack = []

3. For each file operation:
   - Save current state to stack
   - Perform operation
   - If operation fails, auto-rollback

Example implementation:
[code example follows...]
```

**2. Generate Code**
```
📋 [MAIN] 🔧 DEV> OK GENERATE create a new command handler for DIAGRAM SEARCH
🤖 Generating code...
✅ Created: core/commands/diagram_search_handler.py (245 lines)
✅ Created: core/tests/test_diagram_search.py (89 lines)
✅ Updated: core/uDOS_commands.py (registered new handler)

📋 Next steps:
1. Review generated code
2. Run tests: pytest core/tests/test_diagram_search.py
3. Test in TUI: DIAGRAM SEARCH "water filter"
```

**3. Refine Prompts**
```
📋 [MAIN] 🔧 DEV> OK REFINE improve GENERATE GUIDE prompt for technical accuracy
🤖 Analyzing current prompt...
✅ Identified improvements:
- Add "cite sources" instruction
- Specify "step-by-step format"
- Include "safety warnings" requirement
- Add "metric + imperial units" parameter

📋 Updated prompt saved to: core/knowledge/prompts/generate_guide_v2.txt
```

**4. Debug Code**
```
📋 [MAIN] 🔧 DEV> OK DEBUG why does PANEL FILL fail with empty character?
🤖 Debugging PANEL FILL command...
✅ Found issue: core/commands/panel_handler.py:156
   - Missing validation for empty character parameter
   - Should default to '█' if not provided

📋 Suggested fix:
[code diff follows...]
```

**5. Explain Code**
```
📋 [MAIN] 🔧 DEV> OK EXPLAIN core/uDOS_grid.py calculate_cell_position()
🤖 Explaining calculate_cell_position():

This method converts terminal coordinates (x, y) to grid cell positions
using the current viewport dimensions. It handles:

1. Coordinate validation (bounds checking)
2. Aspect ratio correction (4×8 cells)
3. Grid overflow (wrapping or clamping)

Parameters:
- x: Horizontal terminal column (0-based)
- y: Vertical terminal row (0-based)

Returns:
- (cell_x, cell_y): Grid cell coordinates

Example: Terminal (40, 20) → Grid (10, 5)
```

---

## 🛠️ Development Tools

### Interactive Debugger

**1. Set Breakpoints**
```
📋 [MAIN] 🔧 DEV> DEBUG BREAK core/commands/file_handler.py:234
✅ Breakpoint set at file_handler.py:234

📋 [MAIN] 🔧 DEV> DEBUG LIST
Breakpoints:
1. core/commands/file_handler.py:234 (enabled)
2. core/uDOS_parser.py:89 (enabled)
```

**2. Step Through Code**
```
📋 [MAIN] 🔧 DEV> FILE EDIT test.md
⏸️  Breakpoint hit: file_handler.py:234

>> 234:     if not file_path.exists():
   235:         print(f"Error: {file_path} not found")
   236:         return False

Commands: (s)tep, (n)ext, (c)ontinue, (p)rint, (q)uit
> s
```

**3. Inspect Variables**
```
> p file_path
PosixPath('/Users/fredbook/Code/uDOS/sandbox/test.md')

> p workspace
'sandbox'

> p self.editor
'micro'
```

### Performance Profiler

**1. Profile Command**
```
📋 [MAIN] 🔧 DEV> PROFILE BANK SEARCH "water"
⏱️  Profiling BANK SEARCH command...

Results:
  Total time: 1.234s

  Breakdown:
  - Index loading:     0.456s (37%)
  - Search execution:  0.678s (55%)
  - Result formatting: 0.100s (8%)

  Top 5 slowest functions:
  1. search_fulltext()     0.345s
  2. load_search_index()   0.234s
  3. rank_results()        0.123s
  4. format_output()       0.089s
  5. highlight_matches()   0.067s

💡 Suggestion: Cache search index (saves ~0.234s per search)
```

**2. Memory Profiling**
```
📋 [MAIN] 🔧 DEV> PROFILE MEMORY
📊 Memory Usage Report:

Current:     124.5 MB
Peak:        156.8 MB
Available:   7,892 MB

Top consumers:
1. Knowledge bank index:  45.2 MB
2. Diagram library:       23.4 MB
3. Command history:       12.3 MB
4. Theme cache:            8.9 MB
5. Session state:          6.7 MB
```

### Test Runner

**1. Run All Tests**
```
📋 [MAIN] 🔧 DEV> TEST RUN
🧪 Running test suite...

✅ 1,733 tests passed
❌ 2 tests failed
⏭️  5 tests skipped

Failed tests:
1. test_config_sync.py::test_env_path
2. test_gemini_service.py::test_api_key_validation

⏱️  Total time: 45.6s
```

**2. Run Specific Tests**
```
📋 [MAIN] 🔧 DEV> TEST RUN core/tests/test_config_sync.py
🧪 Running test_config_sync.py...

✅ test_env_path_correct
✅ test_username_sync
❌ test_gemini_api_key
✅ test_config_persistence

4 tests: 3 passed, 1 failed
```

**3. Watch Mode**
```
📋 [MAIN] 🔧 DEV> TEST WATCH core/commands/
🔄 Watching core/commands/ for changes...

File changed: core/commands/file_handler.py
🧪 Running affected tests...
✅ test_file_handler.py (12 tests passed)

File changed: core/commands/bank_handler.py
🧪 Running affected tests...
✅ test_bank_handler.py (28 tests passed)
```

### Code Generator

**1. Scaffold Command Handler**
```
📋 [MAIN] 🔧 DEV> GENERATE COMMAND mission
📝 Generating command handler for MISSION...

✅ Created: core/commands/mission_handler.py
   - handle_mission() - Main handler
   - handle_mission_create() - Create mission
   - handle_mission_list() - List missions
   - handle_mission_status() - Show status
   - handle_mission_complete() - Mark complete

✅ Created: core/tests/test_mission_handler.py
   - test_mission_create()
   - test_mission_list()
   - test_mission_status()
   - test_mission_complete()

✅ Updated: core/uDOS_commands.py
   - Registered MISSION command

✅ Updated: knowledge/system/commands.json
   - Added MISSION command metadata

📋 Next: Implement command logic in mission_handler.py
```

**2. Generate Extension**
```
📋 [MAIN] 🔧 DEV> GENERATE EXTENSION skill-tree
📝 Generating extension: skill-tree...

✅ Created: extensions/skill-tree/
   - server.py (Flask server)
   - static/ (CSS, JS, assets)
   - templates/ (HTML templates)
   - README.md
   - requirements.txt
   - setup.sh

📋 To install:
cd extensions/skill-tree && bash setup.sh
```

---

## ⚠️ Dangerous Operations

### Enabled in DEV MODE

**1. DELETE (No Confirmation)**
```
📋 [MAIN] 🔧 DEV> DELETE sandbox/old_data.json
⚠️  DEV MODE: Skipping confirmation
✅ Deleted: sandbox/old_data.json
```

**2. DESTROY (Workspace Reset)**
```
📋 [MAIN] 🔧 DEV> DESTROY SANDBOX
⚠️  DEV MODE: This will delete ALL sandbox files!
Type 'YES DELETE EVERYTHING' to confirm: YES DELETE EVERYTHING
✅ Sandbox destroyed (45 files deleted)
```

**3. Direct Database Access**
```
📋 [MAIN] 🔧 DEV> DB QUERY "DELETE FROM xp WHERE user_id=123"
⚠️  DEV MODE: Direct SQL execution
✅ Query executed (1 row affected)
```

**4. System Configuration Changes**
```
📋 [MAIN] 🔧 DEV> CONFIG SET SYSTEM.ALLOW_EXTERNAL_SCRIPTS true
⚠️  DEV MODE: Changing system security settings
✅ SYSTEM.ALLOW_EXTERNAL_SCRIPTS = true
```

**5. Hot Reload Code**
```
📋 [MAIN] 🔧 DEV> RELOAD core/commands/file_handler.py
⚠️  DEV MODE: Reloading Python module without restart
✅ Reloaded: file_handler.py
✅ Reloaded: 3 dependent modules
```

---

## 📊 Activity Logging

### Audit Trail

All DEV MODE actions are logged to `memory/logs/dev_mode.log`:

```
2025-11-25 14:30:45 [DEV MODE] Fred enabled DEV MODE
2025-11-25 14:31:12 [COMMAND] OK GENERATE create diagram handler
2025-11-25 14:32:34 [DANGEROUS] DELETE sandbox/test.md (no confirmation)
2025-11-25 14:33:56 [CODE RELOAD] core/commands/diagram_handler.py
2025-11-25 14:45:23 [DEV MODE] Fred disabled DEV MODE
```

### View Logs

```
📋 [MAIN] 🔧 DEV> DEV LOG
📋 DEV MODE Activity Log (last 24 hours):

14:30:45 - DEV MODE enabled by Fred
14:31:12 - OK GENERATE: create diagram handler
14:32:34 - DELETE: sandbox/test.md (bypassed confirmation)
14:33:56 - RELOAD: core/commands/diagram_handler.py
14:45:23 - DEV MODE disabled by Fred

Total actions: 5
Dangerous operations: 2
```

---

## 🔄 Hot Reload System

### Watch File Changes

```
📋 [MAIN] 🔧 DEV> DEV WATCH ON
🔄 Hot reload enabled
👀 Watching core/ for changes...

File changed: core/commands/bank_handler.py
✅ Reloaded: bank_handler.py (0.12s)

File changed: core/utils/formatter.py
✅ Reloaded: formatter.py + 4 dependents (0.34s)
```

### Manual Reload

```
📋 [MAIN] 🔧 DEV> RELOAD core/commands/
✅ Reloaded 45 modules in core/commands/ (1.23s)
```

---

## 🎯 Use Cases

### 1. Develop New Command

```
# 1. Enable DEV MODE
DEV MODE ON

# 2. Generate scaffolding
OK GENERATE create MISSION command handler

# 3. Edit code
EDIT core/commands/mission_handler.py

# 4. Hot reload (auto-detects changes)
# File saved → auto-reload

# 5. Test in TUI
MISSION CREATE test-mission

# 6. Run tests
TEST RUN core/tests/test_mission_handler.py

# 7. Debug if needed
DEBUG BREAK core/commands/mission_handler.py:45
MISSION CREATE test-mission

# 8. Disable DEV MODE when done
DEV MODE OFF
```

### 2. Fix Configuration Bug

```
# 1. Enable DEV MODE
DEV MODE ON

# 2. Investigate issue
OK DEBUG why does username not persist?

# 3. Profile to find slow code
PROFILE CONFIG SET username Fred

# 4. Edit configuration manager
EDIT core/config/config_manager.py

# 5. Test fix
CONFIG SET username Fred
REBOOT
DASH  # Check if username persists

# 6. Run config tests
TEST RUN core/tests/test_config_sync.py

# 7. Disable DEV MODE
DEV MODE OFF
```

### 3. Generate Content at Scale

```
# 1. Enable DEV MODE
DEV MODE ON

# 2. Refine prompts
OK REFINE improve GENERATE GUIDE prompt

# 3. Test generation
OK GENERATE create survival guide for water filtration

# 4. Review quality
GUIDE SHOW knowledge/water/filtration.md

# 5. Batch generate if satisfied
RUN memory/workflow/batch_generate_water.uscript

# 6. Monitor progress
TAIL memory/logs/generation.log

# 7. Disable DEV MODE
DEV MODE OFF
```

---

## 🔒 Restrictions & Permissions

### Standard User (DEV MODE OFF)

| Action | Allowed | Notes |
|--------|---------|-------|
| HELP, STATUS, DASH | ✅ Yes | Read-only commands |
| EDIT, NEW, SHOW | ✅ Yes | File operations with confirmation |
| DELETE, DESTROY | ⚠️ With confirmation | Destructive operations require explicit confirmation |
| OK ASK | ✅ Yes | AI assistance for questions |
| OK GENERATE | ❌ No | Content generation requires DEV MODE |
| CONFIG SET SYSTEM | ❌ No | System config changes require DEV MODE |
| DB QUERY | ❌ No | Direct database access requires DEV MODE |
| RELOAD, DEBUG, PROFILE | ❌ No | Development tools require DEV MODE |

### Master User (DEV MODE ON)

| Action | Allowed | Notes |
|--------|---------|-------|
| All standard commands | ✅ Yes | No restrictions |
| DELETE, DESTROY | ✅ Yes | Bypass confirmation (logged) |
| OK GENERATE | ✅ Yes | Full content generation |
| OK DEBUG, OK REFINE | ✅ Yes | Advanced AI features |
| CONFIG SET SYSTEM | ✅ Yes | System configuration changes |
| DB QUERY | ✅ Yes | Direct database access (DANGEROUS) |
| RELOAD, DEBUG, PROFILE | ✅ Yes | Full development tools |
| CODE EXECUTION | ✅ Yes | Run arbitrary Python code (VERY DANGEROUS) |

---

## 📚 Related Documentation

- `ROADMAP.MD` - v1.5.0 DEV MODE timeline
- `wiki/Configuration.md` - Master user setup
- `dev/planning/CONFIG_SYNC_ISSUES.md` - Configuration fixes
- `CONTRIBUTING.md` - Developer guide

---

## 🚨 Safety Warnings

### ⚠️ CRITICAL WARNINGS

1. **Never enable DEV MODE on production systems**
   - DEV MODE bypasses safety checks
   - Mistakes can cause data loss
   - Only use in development/testing

2. **Always review generated code**
   - AI-generated code may have bugs
   - Test thoroughly before deploying
   - Run test suite after changes

3. **Protect master password**
   - Store in password manager
   - Never commit to version control
   - Rotate regularly

4. **Monitor DEV MODE logs**
   - Review audit trail regularly
   - Investigate suspicious activity
   - Keep logs for security audits

5. **Disable DEV MODE when done**
   - Don't leave system in dev state
   - Reduces attack surface
   - Prevents accidental damage

---

**Status:** 📋 Planned for v1.5.0 (Week 1-2)
**Priority:** 🔴 HIGH (foundation for AI-assisted development)
**Est. Implementation:** 2 weeks
**Tests Required:** 25+ DEV MODE tests
