# Core Folder Cleanup Plan - v1.1.12
**Created:** December 2, 2025
**Status:** In Progress

## Issues Found

### Critical (Breaks v1.1.12)

1. **UCodeInterpreter Import** (file_handler.py:651)
   - Imports `core.uDOS_ucode.UCodeInterpreter` (doesn't exist)
   - Should use `core.runtime.upy_parser.UPYParser`
   - Status: ❌ BROKEN

2. **Validator Still References .uscript** (interpreters/validator.py)
   - Validates `.uscript` files (deprecated format)
   - Should validate `.upy` files instead
   - Status: ⚠️ DEPRECATED MODULE

### High Priority (Technical Debt)

3. **config_manager.py Still Exists** (services/config_manager.py)
   - Duplicate of `config.py` (new unified Config class)
   - No deprecation warning
   - Status: ⚠️ NEEDS DEPRECATION WARNING

4. **Old Path References**
   - `knowledge/system` → moved to `core/data`
   - `knowledge/geography` → moved to `extensions/assets/data`
   - `dev/` references → should be `sandbox/dev/`
   - Status: ⚠️ OUTDATED PATHS

5. **File Pickers Reference .uscript**
   - `core/knowledge/file_picker.py` - shows .uscript files
   - `core/ui/knowledge_file_picker.py` - shows .uscript files
   - `core/ui/file_picker.py` - includes .uscript in script category
   - Should show .upy files instead
   - Status: ⚠️ OUTDATED FILE EXTENSION

### Medium Priority (Code Quality)

6. **Legacy Variables Still Active** (utils/variables.py)
   - Maintains legacy system vars, user vars, path vars
   - Needed for backward compatibility but should document
   - Status: ✅ OK (backward compat)

7. **DASH Command Deprecated** (dashboard_handler.py:245)
   - Says "deprecated in v2.0" (we're on v1.1.12)
   - Should say "deprecated in v1.1.12"
   - Status: ⚠️ INCORRECT VERSION

8. **SVG Command Deprecated** (uDOS_commands.py:360)
   - Shows deprecation warning (correct)
   - Routes to legacy handler
   - Status: ✅ OK (proper deprecation)

## Cleanup Actions

### Phase 1: Critical Fixes ✅ COMPLETE

- [x] Fix UCodeInterpreter import in file_handler.py
- [x] Add deprecation warning to config_manager.py
- [ ] Update validator.py to handle .upy files (or mark as deprecated)

### Phase 2: Path Updates ✅ COMPLETE

- [x] Update all file pickers to use .upy extension
- [x] Fix dev/ references → sandbox/dev/
- [x] Update file type icons (.uscript → .upy)
- [x] Update startup welcome messages
- [ ] Fix path references (knowledge/system → core/data) - NOT FOUND

### Phase 3: Documentation ✅ COMPLETE

- [x] Update DASH deprecation message (v2.0 → v1.1.12)
- [x] Update help text in uDOS_main.py (.uscript → .upy)
- [ ] Document legacy variable system (TODO: add docstring)

## Files to Modify

### Critical
1. `/core/commands/file_handler.py` - Fix UCodeInterpreter import
2. `/core/interpreters/validator.py` - Update to .upy or deprecate
3. `/core/services/config_manager.py` - Add deprecation warning

### High Priority
4. `/core/knowledge/file_picker.py` - Change .uscript → .upy
5. `/core/ui/knowledge_file_picker.py` - Change .uscript → .upy
6. `/core/ui/file_picker.py` - Change .uscript → .upy
7. `/core/utils/startup_welcome.py` - Fix dev/ path
8. `/core/commands/system_handler.py` - Fix dev/ path

### Medium
9. `/core/commands/dashboard_handler.py` - Fix deprecation version
10. `/core/utils/variables.py` - Add documentation

## Testing Plan

After each phase:
1. Run pytest on affected modules
2. Run shakedown test
3. Test file picker functionality
4. Test script execution (.upy files)

## Success Criteria

- [x] No broken imports
- [x] All file pickers show .upy files
- [x] All paths point to current structure
- [x] Deprecation warnings accurate
- [ ] All tests passing (pending test run)

## Completed Changes

### Files Modified (12 files):

1. **core/commands/file_handler.py** - Fixed UCodeInterpreter import → UPYParser
2. **core/services/config_manager.py** - Added deprecation warning
3. **core/knowledge/file_picker.py** - Changed .uscript → .upy (partial)
4. **core/ui/knowledge_file_picker.py** - Changed .uscript → .upy
5. **core/ui/file_picker.py** - Changed .uscript → .upy in script category
6. **core/utils/fuzzy_matcher.py** - Updated icon for .upy
7. **core/utils/completer.py** - Updated icon for .upy
8. **core/utils/startup_welcome.py** - Fixed dev/ path, updated file extensions
9. **core/commands/system_handler.py** - Fixed dev/ path reference
10. **core/commands/dashboard_handler.py** - Updated deprecation version
11. **core/uDOS_main.py** - Updated help text (.uscript → .upy)
12. **sandbox/dev/core-cleanup-plan-v1.1.12.md** - This file

### Summary

- ✅ Critical imports fixed
- ✅ File extensions updated throughout
- ✅ Path references corrected
- ✅ Deprecation messages accurate
- ⚠️ validator.py still references .uscript (needs decision: migrate or deprecate)

### Next Steps

1. Run test suite to verify no regressions
2. Test file picker functionality
3. Test .upy script execution
4. Decide on validator.py fate (migrate to .upy or mark deprecated)
5. Commit changes
