# Gemini API Instructions for uDOS Development

**For:** OK FIX, OK ASK, and other AI-assisted commands
**Context:** This file provides guidance for Gemini API when helping develop uDOS
**See Also:** `.github/copilot-instructions.md` for complete project context

## Quick Reference

**uDOS Version:** v1.2.28 (Story Engine + Error Handling)
**Purpose:** Offline-first survival knowledge system with dual CLI/Web interface
**Language:** Python 3.8+, uPY v1.2 scripting
**Architecture:** Command Router → Handlers → Services → Extensions

## Critical First Steps

When assisting with uDOS development:

1. **Always check virtual environment**: `.venv/bin/activate`
2. **Entry point**: `core/uDOS_main.py` → `core/uDOS_commands.py` (router)
3. **Command flow**: Router → Handler (`core/commands/*_handler.py`) → Service
4. **Configuration**: `core/config.py` (unified .env + user.json)
5. **Test validation**: Run `./start_udos.sh memory/tests/shakedown-script.md`

## Workspace Structure (v1.2.21)

```
/
├── core/                   # Core system (Python, tracked)
│   ├── commands/           # Command handlers (40+ handlers)
│   ├── services/           # Core services (config, knowledge, etc.)
│   ├── ui/                 # TUI components
│   └── utils/              # Utilities
├── extensions/             # Extension system
│   ├── assistant/          # AI assistant (Gemini integration)
│   ├── play/               # Gameplay extensions
│   └── web/                # Web interfaces
├── knowledge/              # 230+ survival guides (tracked, read-only)
├── memory/                 # User workspace (gitignored except ucode/)
│   ├── ucode/              # uPY scripts + tests
│   │   ├── scripts/        # User scripts (ignored)
│   │   ├── tests/          # Test suites (tracked)
│   │   └── sandbox/        # Experimentation (ignored)
│   ├── workflows/          # Workflow automation
│   ├── logs/               # System logs (check here for errors!)
│   └── bank/               # User data
├── dev/                    # Development tools (git submodule)
└── wiki/                   # Documentation (tracked)
```

## Development Patterns

### File Type Separation

**Python (.py) - System Code (tracked):**
- Core system: `core/`, `extensions/`
- Developers only
- Full git tracking
- Examples: handlers, services, utilities

**TypeScript Scripts (embedded in .md files):**
- User automation: `memory/bank/scripts/`, `memory/sandbox/`
- Format: TypeScript embedded in Markdown (e.g., `workflow-script.md`, `quest-template.md`)
- Users edit directly
- Gitignored (except stdlib/examples/adventures)
- Examples: workflows, missions, game scripts

**CRITICAL: Never mix Python system code with uPY user scripts!**

### Command Handler Pattern

```python
# 1. Create handler in core/commands/my_handler.py
from core.commands.base_handler import BaseCommandHandler

class MyHandler(BaseCommandHandler):
    def handle_command(self, params):
        if params[0].upper() == 'MYCOMMAND':
            return self._do_something(params[1:])

# 2. Register in core/uDOS_commands.py
from core.commands.my_handler import MyHandler
self.my_handler = MyHandler(**handler_kwargs)

# In execute():
elif cmd in ['MYCOMMAND']:
    return self.my_handler.handle_command(cmd_parts)

# 3. Add to core/data/commands.json
"MYCOMMAND": {
  "syntax": "MYCOMMAND <arg>",
  "description": "Does something useful",
  "category": "utility"
}
```

### Error Handling (v1.2.28+)

**ALWAYS use error_helper for exceptions:**

```python
from core.utils.error_helper import format_system_error, format_command_error

try:
    result = risky_operation()
except Exception as e:
    error_msg = format_command_error(e, command=cmd, show_traceback=True)
    print(error_msg)
```

**Error messages automatically suggest:**
- DEV MODE - Advanced debugging
- OK FIX - AI assistance (you!)
- DEBUG STATUS - System diagnostics
- REPAIR - Automated fixes

## Log Files (CRITICAL FOR DEBUGGING)

**Location:** `memory/logs/auto/`
**Format:** Timestamped `.log` files
**Content:** Commands, errors, system events

**When helping with errors:**
1. Check `get_error_logs()` in context
2. Look for ERROR, CATASTROPHIC, Failed patterns
3. Check recent commands in `get_recent_logs()`
4. Cross-reference with git status

## uPY Scripting (v1.2)

**Three bracket types:**
- `$variable` - Variables (no braces in v1.2.24+)
- `COMMAND[ arg1 | arg2 ]` - Commands
- `[IF condition...]` - Conditionals

**Three complexity levels:**
```upy
# SHORT: [IF $hp < 30: HP (+20) | PRINT ('Healed!')]
# MEDIUM: [IF $gold >= 100 THEN: ITEM (sword) ELSE: PRINT ('Need gold')]
# LONG: Full IF/ELSE IF/ELSE/END IF blocks
```

**Runtime:** `core/runtime/upy_runtime.py` (1,179 lines)

## Common Tasks

### Debugging Extension Errors

```bash
# Check extension status
POKE STATUS desktop

# View logs
cat memory/logs/auto/latest.log | grep ERROR

# Check server health
POKE HEALTH

# Restart extension
POKE RESTART desktop
```

### Analyzing System State

Context available in OK commands includes:
- ✅ Workspace path & current file
- ✅ TILE location (grid system)
- ✅ Last 5 commands with status
- ✅ Last 5 error messages
- ✅ Git status (modified/added files)
- ✅ Recent log entries (30 lines)
- ✅ Recent error logs (5 errors)

### Suggesting Fixes

**Priority order:**
1. Check logs for root cause
2. Verify file paths exist
3. Check git status for conflicts
4. Test in sandbox first
5. Use SHAKEDOWN for validation

## Key Design Principles

1. **Minimal Design** - No bloat, essential features only
2. **Offline-First** - Full functionality without internet
3. **Human-Centric** - Clear language, practical focus
4. **Text-First** - Terminal-based, ASCII graphics
5. **Modular** - Clean separation (core → services → extensions)

## Anti-Patterns to Avoid

❌ **Don't:**
- Create files outside `/dev/` or `/memory/`
- Store sensitive data in git (use `.env`)
- Hardcode paths (use Config)
- Mix user data with system files
- Use lat/long coordinates (TILE codes only)
- Manually manage `.archive/` folders

✅ **Do:**
- Use error_helper for all exceptions
- Check logs before suggesting fixes
- Test with `./start_udos.sh script-example.md`
- Run SHAKEDOWN after changes
- Follow handler pattern for commands
- Document all public APIs

## Testing & Validation

```bash
# Core validation
./start_udos.sh memory/tests/shakedown-script.md

# Unit tests
pytest core/memory/tests/ -v

# Quick smoke test
echo -e "STATUS\nTREE\nEXIT" | python uDOS.py
```

## When Helping Users

**For "OK FIX" commands:**
1. ✅ Read recent logs automatically (included in context)
2. ✅ Check error messages in context
3. ✅ Review recent commands for patterns
4. ✅ Analyze git status for related changes
5. Suggest specific commands to run
6. Provide code fixes with explanations
7. Recommend SHAKEDOWN after fixes

**For "OK ASK" commands:**
1. Use workspace context
2. Reference project files when relevant
3. Suggest related commands
4. Link to wiki documentation

## Version Context

**Current:** v1.2.28
**Recent features:**
- v1.2.21: OK Assistant integration
- v1.2.15: TUI system (keypad, predictor, pager)
- v1.2.14: Grid-First development
- v1.2.12: Folder structure refactoring
- v1.1.16: Archive system

**Next priorities (v1.3.0+):**
- Community features
- Knowledge bank expansion
- Enhanced extension system

## Related Files

- `.github/copilot-instructions.md` - Complete project documentation
- `core/docs/ERROR-HANDLING.md` - Error system details
- `wiki/OK-Assistant-Guide.md` - OK command documentation
- `wiki/Developers-Guide.md` - Full developer reference

---

**Remember:** You have access to logs, error messages, recent commands, and git status. Use this context to provide accurate, actionable fixes!
