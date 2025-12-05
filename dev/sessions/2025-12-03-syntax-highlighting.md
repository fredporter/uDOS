# Syntax Highlighting System - Implementation Session

**Date:** December 3, 2025
**Version:** uDOS v1.1.16
**Developer:** Fred Porter

## Session Summary

Successfully implemented system-wide ANSI-based syntax highlighting for uPY/uCODE commands across the TUI.

## What Was Delivered

### Core Infrastructure

**New ANSISyntaxHighlighter class** (`core/output/syntax_highlighter.py`):
- 180+ lines of ANSI-based syntax highlighting
- Pattern matching for uPY/uCODE syntax
- No Rich dependency - pure ANSI escape codes
- Reliable terminal output (tested across all scenarios)

**Syntax Support:**
```
COMMAND(param|param)       - Green command, cyan params
[MODULE|COMMAND*PARAM]     - Bracket notation for uCODE
$VARIABLES                 - Yellow system variables
--flags                    - Magenta command flags
'strings'                  - White quoted strings
| separators               - Cyan pipe characters
```

**Color Scheme:**
- Commands: Bright green (`\033[1;32m`)
- Parameters: Cyan (`\033[36m`)
- Variables: Bright yellow (`\033[1;33m`)
- Flags: Magenta (`\033[35m`)
- Strings: White (`\033[37m`)
- Brackets/Pipes: Dim gray/cyan

### Convenience Functions

**highlight_syntax(text: str) -> str**
```python
from core.output.syntax_highlighter import highlight_syntax

help_text = "Use RESOURCE(STATUS) or RESOURCE(QUOTA|provider)"
print(highlight_syntax(help_text))
```

**format_error(title, reason, hint) -> str**
```python
from core.output.syntax_highlighter import format_error

error = format_error(
    "CORRUPTED SPELL",
    "[RESOURCE|HELP]",
    "Type RESOURCE(HELP) for available commands"
)
print(error)
```

### Refactored Files

**resource_handler.py:**
- Removed local `_highlight_upy_syntax()` function (83 lines)
- Now imports `highlight_syntax()` from shared module
- All HELP output uses consistent highlighting
- All tests passing ✅

## Technical Details

### Pattern Matching Strategy

Original approach used variable-width lookbehinds which failed:
```python
# ❌ FAILED: variable-width lookbehind
pattern = r'(?<!\033\[[\d;]*m)(\$[A-Z_][A-Z0-9_]*)(?!\033)'
```

Fixed with context-aware replacement:
```python
# ✅ WORKS: check preceding context in replace function
def replace_var(match):
    var = match.group(1)
    start_pos = match.start()
    if start_pos > 0:
        preceding = text[max(0, start_pos-10):start_pos]
        if '\033[' in preceding and '\033[0m' not in preceding:
            return var  # Already colored
    return f"{cls.VARIABLE}{var}{cls.RESET}"
```

### Multi-Phase Highlighting

Highlighting is applied in phases to avoid conflicts:

1. **COMMAND(params)** - Parenthesis syntax
2. **[MODULE|CMD]** - Bracket syntax
3. **$VARIABLES** - System variables
4. **--flags** - Command flags
5. **'strings'** - Quoted strings

Each phase checks if text is already colored to avoid double-encoding.

## Testing

**Test Suite:** `dev/tools/test_resource_help.py`

All 4 tests passing:
- ✅ ANSI color codes render correctly
- ✅ Direct handler import and call
- ✅ Command routing via CommandHandler
- ✅ ANSI code preservation in strings

**VS Code Debug Config:** "Debug: RESOURCE HELP Colors"

## Usage Examples

### In Command Handlers

```python
from core.output.syntax_highlighter import highlight_syntax

def _handle_help(self):
    help_lines = []
    help_lines.append("Commands:")
    help_lines.append(f"  {highlight_syntax('MISSION(CREATE|title)')}")
    help_lines.append(f"  {highlight_syntax('MISSION(LIST|--active)')}")
    return '\n'.join(help_lines)
```

### Error Messages

```python
from core.output.syntax_highlighter import format_error

if not mission_id:
    return format_error(
        "MISSING PARAMETER",
        "$MISSION_ID required",
        "Use MISSION(CREATE|'My Mission') to create one"
    )
```

### Variable Output

```python
from core.output.syntax_highlighter import ANSISyntaxHighlighter as ASH

status = f"{ASH.GREEN}Active{ASH.RESET}"
progress = f"{ASH.YELLOW}{percent}%{ASH.RESET}"
warning = f"{ASH.RED}⚠️  Critical{ASH.RESET}"
```

## Migration Guide

### For Existing Command Handlers

**Step 1: Import the utility**
```python
from core.output.syntax_highlighter import highlight_syntax
```

**Step 2: Wrap command syntax in help text**
```python
# Before
help_text = "  COMMAND(SUBCOMMAND|param)"

# After
help_text = f"  {highlight_syntax('COMMAND(SUBCOMMAND|param)')}"
```

**Step 3: Apply to error messages**
```python
# Before
error = f"💀 Invalid command: [MODULE|COMMAND]"

# After
from core.output.syntax_highlighter import format_error
error = format_error(
    "Invalid Command",
    "[MODULE|COMMAND]",
    "Type HELP for available commands"
)
```

## Next Steps

### Immediate (Priority 1)
- [ ] Apply `highlight_syntax()` to all HELP commands in `core/commands/`
- [ ] Update `mission_handler.py` HELP output
- [ ] Update `workflow_handler.py` HELP output
- [ ] Update `schedule_handler.py` HELP output

### Short-term (Priority 2)
- [ ] Migrate error messages to use `format_error()`
- [ ] Add syntax highlighting to hint messages
- [ ] Update command documentation with colored examples

### Long-term (Priority 3)
- [ ] Add syntax highlighting to interactive prompts
- [ ] Highlight uPY code blocks in knowledge guides
- [ ] Create theme-aware color scheme (galaxy, foundation, etc.)

## Files Changed

```
core/output/syntax_highlighter.py   +180 lines
  - ANSISyntaxHighlighter class
  - highlight_syntax() convenience function
  - format_error() utility function

core/commands/resource_handler.py   -83 lines
  - Removed _highlight_upy_syntax()
  - Import highlight_syntax from shared module
  - All HELP output migrated

dev/tools/test_resource_help.py     (unchanged)
  - All tests passing ✅
```

## Lessons Learned

1. **ANSI codes > Rich markup** for command output
   - Rich markup gets stripped in some output contexts
   - ANSI codes are universally supported

2. **Variable-width regex lookbehinds** don't work in Python
   - Use context-aware replacement functions instead
   - Check preceding text manually

3. **Multi-phase highlighting** prevents conflicts
   - Apply highlighting in specific order
   - Check if text already colored before applying

4. **Test early, test often**
   - Debug tools caught issues immediately
   - VS Code debugger invaluable for regex debugging

## Git Commits

```bash
c22a275b - feat: Add uPY syntax highlighting to RESOURCE HELP
d4aa0940 - feat: System-wide ANSI syntax highlighting utility
```

## Developer Notes

**Why ANSI instead of Rich?**
- Rich Console markup `[cyan]text[/]` was being stripped in output
- ColorUI is designed for rich features (panels, tables), not simple coloring
- ANSI escape codes work reliably across all output contexts
- No additional dependencies needed

**Why separate ANSISyntaxHighlighter from UPYHighlighter?**
- UPYHighlighter is Rich-based for file viewing
- ANSISyntaxHighlighter is ANSI-based for terminal output
- Two different use cases, two different tools
- Gives flexibility based on context

**Performance Considerations:**
- Regex matching is fast for short strings (HELP text)
- Context checking adds minimal overhead
- No noticeable performance impact

---

**Status:** ✅ Complete and tested
**Next Session:** Apply to all command HELP outputs
