# Error Handling System Improvements

**Date:** November 30, 2025
**Issue:** Empty variable placeholders in error messages (`<VARIABLES>`)
**Status:** ✅ Fixed

---

## Problem Statement

User encountered an error when typing `resource` without a subcommand:

```
🌀> resource
<ERROR_INVALID_UCODE_FORMAT>
```

**Root Causes:**
1. RESOURCE command had no default subcommand in `commands.json`
2. Parser created malformed uCODE: `[RESOURCE|**]` (empty $1, $2, $3)
3. Error message template had variables (`{ucode}`, `{error}`) that weren't provided
4. `get_message()` method returned template as-is without handling missing variables
5. Result: User saw literal `<ERROR_INVALID_UCODE_FORMAT>` instead of helpful error

---

## Solutions Implemented

### 1. RESOURCE Command Fix

**File:** `core/data/commands.json`

**Before:**
```json
{
  "NAME": "RESOURCE",
  "UCODE_TEMPLATE": "[RESOURCE|$1*$2*$3]",
  "DEFAULT_PARAMS": {}
}
```

**After:**
```json
{
  "NAME": "RESOURCE",
  "UCODE_TEMPLATE": "[RESOURCE|$1*$2*$3]",
  "DEFAULT_PARAMS": {
    "$1": "HELP"
  },
  "SUBCOMMANDS": {
    "STATUS": "Show resource usage dashboard",
    "QUOTA": "Check API quotas",
    "ALLOCATE": "Allocate resources for mission",
    "RELEASE": "Release mission resources",
    "THROTTLE": "Check throttling status",
    "SUMMARY": "Complete resource dashboard",
    "HELP": "Show resource command help"
  }
}
```

**Result:** Typing `resource` now defaults to `RESOURCE HELP` and shows command documentation.

---

### 2. Command Router Validation

**File:** `core/uDOS_commands.py`

**Added validation in RESOURCE handler:**
```python
elif module == "RESOURCE":
    # If no command provided, show help
    if not command or command.strip() == '':
        result = handle_resource_command('HELP')
        return result.get('output', str(result))
    # ... rest of handler
```

**Result:** Empty commands caught and redirected to HELP before processing.

---

### 3. Improved `get_message()` Method

**File:** `core/uDOS_commands.py`

**Before:**
```python
def get_message(self, key, **kwargs):
    template = self.messages.get(key) or self.lexicon.get(key) or f"<{key}>"
    try:
        return template.format(**kwargs)
    except Exception:
        return template  # Returns template with {placeholders} intact
```

**After:**
```python
def get_message(self, key, **kwargs):
    template = self.messages.get(key) or self.lexicon.get(key) or f"<{key}>"
    try:
        return template.format(**kwargs)
    except KeyError as e:
        # Missing template variable - provide better context
        missing_var = str(e).strip("'")
        if self.logger:
            self.logger.warning(f"Template '{key}' missing variable: {missing_var}")
        # Replace missing variable with visible placeholder
        return template.replace(f"{{{missing_var}}}", f"<{missing_var.upper()}>")
    except Exception as e:
        # Other formatting errors - log and return template
        if self.logger:
            self.logger.warning(f"Error formatting message '{key}': {e}")
        return template
```

**Result:** Missing variables now show as `<VARIABLE_NAME>` instead of breaking formatting.

---

### 4. Enhanced Theme Error Messages

**Files:** `core/data/themes/*.json`

**Improvements:**
- Added helpful hints (💡) to error messages
- Listed valid options when user provides invalid input
- Provided next steps and related commands
- Multi-line formatting for clarity
- Quoted variable values for visibility

**Example - Dungeon Theme:**

**Before:**
```json
"ERROR_INVALID_UCODE_FORMAT": "💀 CORRUPTED SPELL: {ucode} ({error})",
"ERROR_UNKNOWN_MODULE": "💀 UNKNOWN CHAMBER: {module}",
"ERROR_COMMAND_NOT_FOUND": "💀 SPELL '{command}' NOT IN SPELLBOOK"
```

**After:**
```json
"ERROR_INVALID_UCODE_FORMAT": "💀 CORRUPTED SPELL: {ucode}\n   Reason: {error}\n   💡 Type HELP for spell list",
"ERROR_UNKNOWN_MODULE": "💀 UNKNOWN CHAMBER: '{module}'\n   💡 Valid chambers: FILE, SYSTEM, ASSISTANT, RESOURCE\n   Type HELP for complete list",
"ERROR_COMMAND_NOT_FOUND": "💀 SPELL '{command}' NOT IN SPELLBOOK\n   💡 Type HELP to see all available spells"
```

**Example - Foundation Theme:**

**Before:**
```json
"ERROR_UNKNOWN_MODULE": "⚠️ UNKNOWN MODULE: {module}",
"ERROR_COMMAND_NOT_FOUND": "⚠️ COMMAND '{command}' NOT IN REGISTRY"
```

**After:**
```json
"ERROR_UNKNOWN_MODULE": "⚠️ UNKNOWN MODULE: '{module}'\n   💡 Valid modules: FILE, SYSTEM, ASSISTANT, RESOURCE\n   Type HELP for complete list",
"ERROR_COMMAND_NOT_FOUND": "⚠️ COMMAND '{command}' NOT IN REGISTRY\n   💡 Type HELP to see all commands"
```

---

## Testing

### Test Case 1: `resource` (empty command)

**Before:**
```
🌀> resource
<ERROR_INVALID_UCODE_FORMAT>
```

**After:**
```
🌀> resource
📊 RESOURCE Commands - Resource Monitoring & Management

═══════════════════════════════════════════════════════════════

Commands:

  RESOURCE STATUS
    Show overview of all resources (quotas, disk, CPU, memory)

  RESOURCE QUOTA [provider]
    Check API quota for specific provider (gemini, github)
    ...

[Full help documentation displayed]
```

### Test Case 2: Invalid command

**Before:**
```
🌀> foo
<ERROR_COMMAND_NOT_FOUND>
```

**After (Dungeon theme):**
```
🌀> foo
💀 SPELL 'FOO' NOT IN SPELLBOOK
   💡 Type HELP to see all available spells
```

**After (Foundation theme):**
```
🌀> foo
⚠️ COMMAND 'FOO' NOT IN REGISTRY
   💡 Type HELP to see all commands
```

### Test Case 3: Invalid module

**Before:**
```
[INVALID|STATUS]
💀 UNKNOWN CHAMBER: <MODULE>
```

**After:**
```
[INVALID|STATUS]
💀 UNKNOWN CHAMBER: 'INVALID'
   💡 Valid chambers: FILE, SYSTEM, ASSISTANT, RESOURCE
   Type HELP for complete list
```

---

## Benefits

### 1. User Experience
- ✅ No more cryptic `<ERROR_NAME>` messages
- ✅ Clear explanation of what went wrong
- ✅ Helpful suggestions for next steps
- ✅ Listed valid options when available
- ✅ Consistent error formatting across themes

### 2. Developer Experience
- ✅ Warnings logged for missing template variables
- ✅ Easy to debug template issues
- ✅ Graceful degradation (shows placeholder instead of breaking)
- ✅ Theme-aware error messages

### 3. System Robustness
- ✅ Handles empty commands gracefully
- ✅ Validates input before processing
- ✅ Provides default behaviors for incomplete input
- ✅ Prevents cascading errors

---

## Error Message Design Principles

### 1. Structure
```
[EMOJI] ERROR TYPE: 'value'
   Reason: detailed explanation
   💡 Suggestion: helpful next step
```

### 2. Components
- **Emoji:** Visual indicator (💀 dungeon, ⚠️ foundation, etc.)
- **Error Type:** What category of error
- **Value:** Quoted user input that caused error
- **Reason:** Why it failed
- **Suggestion (💡):** What to do next

### 3. Guidelines
- Always quote user input: `'{value}'` not `{value}`
- Provide actionable next steps
- List valid options when possible
- Use multi-line formatting for readability
- Maintain theme voice (dungeon, foundation, etc.)

---

## Files Modified

### Core System
1. `core/uDOS_commands.py`
   - Enhanced `get_message()` with KeyError handling
   - Added RESOURCE command validation
   - Added logger warnings for missing variables

2. `core/data/commands.json`
   - Added `DEFAULT_PARAMS` to RESOURCE command
   - Listed all subcommands
   - Improved syntax documentation

### Theme Files
3. `core/data/themes/dungeon.json`
   - Enhanced all error messages with hints
   - Added multi-line formatting
   - Listed valid options in errors

4. `core/data/themes/foundation.json`
   - Enhanced error messages with suggestions
   - Added multi-line formatting
   - Improved clarity and actionability

---

## Future Improvements

### Short Term
- [ ] Update remaining theme files (galaxy, science, teletext, project)
- [ ] Add command suggestion system (fuzzy matching)
- [ ] Implement error tracking/analytics
- [ ] Create error message testing suite

### Medium Term
- [ ] Add context-aware error recovery
- [ ] Implement "Did you mean?" suggestions
- [ ] Create error message style guide
- [ ] Add localization support for errors

### Long Term
- [ ] AI-powered error explanations
- [ ] Interactive error resolution
- [ ] Error message A/B testing
- [ ] User-customizable error verbosity

---

## Lessons Learned

1. **Always validate input** - Catch empty/malformed input before processing
2. **Provide defaults** - Use sensible defaults (like HELP) for incomplete commands
3. **Handle missing variables** - Template formatting can fail gracefully
4. **Be helpful** - Error messages should guide users to success
5. **Test edge cases** - Empty strings, missing params, malformed input
6. **Theme consistency** - Error messages should match theme voice
7. **Log for developers** - Warnings help debug template issues
8. **Quote user input** - Makes errors clearer and more professional

---

## Related Documentation

- [Theme System](../../core/docs/THEME-SYSTEM.md)
- [Command Reference](../../wiki/Command-Reference.md)
- [RESOURCE Command](../../core/commands/resource_handler.py)
- [Error Message Validator](../../core/theme_loader.py)

---

**Status:** ✅ Complete
**Impact:** High - Improves UX for all users
**Rollout:** Immediate (core system changes)
**Follow-up:** Update remaining theme files in next session
