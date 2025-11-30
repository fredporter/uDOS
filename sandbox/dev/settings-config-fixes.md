# SETUP/CONFIG Command Fixes (renamed from SETTINGS)

**Date**: 2025-11-30
**Version**: v1.1.6 (post-release fixes)
**Status**: ✅ COMPLETE

## Command Rename

**SETTINGS → SETUP**
- `SETTINGS` command renamed to `SETUP` for clarity
- `SETTINGS` kept as an alias for backward compatibility
- `SETUP` added as menu item in CONFIG interactive menu: "Quick Setup (View/Edit All Settings)"## Issues Fixed

### 1. ConfigManager API Errors
**Problem**: `'ConfigManager' object has no attribute 'get_user'`

**Root Cause**:
- configuration_handler.py was calling non-existent methods:
  - `config.get_user('USER_PROFILE.NAME')` ❌
  - `config.set_user('USER_PROFILE.PASSWORD')` ❌

**Solution**:
- Replaced with proper ConfigManager API:
  - `config.get('username')` ✅
  - `config.set('PASSWORD', value, persist=True)` ✅

**Files Modified**:
- `core/commands/configuration_handler.py` (lines 1111-1235)

**Changes**:
```python
# OLD (BROKEN):
user_name = config.get_user('USER_PROFILE.NAME', '')
config.set_user('USER_PROFILE.PASSWORD', new_password)

# NEW (FIXED):
user_name = config.get('username', '')
config.set('PASSWORD', new_password, persist=True)
```

**Key Mappings**:
- `USER_PROFILE.NAME` → `'username'` (from user.json)
- `USER_PROFILE.PASSWORD` → `'PASSWORD'` (from .env)
- `USER_PROFILE.LOCATION` → `'location'` (from user.json)
- `USER_PROFILE.TIMEZONE` → `'timezone'` (from user.json)

### 2. SETUP Default Behavior Error (renamed from SETTINGS)
**Problem**: Typing "settings" returned "❌ Unknown setting: SHOW"

**Root Cause**:
- commands.json defines `DEFAULT_PARAMS: {"$1": "SHOW"}`
- When no params provided, command system adds "SHOW" as $1
- `handle_settings(["SHOW"])` called `_show_setting("SHOW")`
- "SHOW" not recognized as valid setting key (only THEME, GRID, USER, DEBUG)

**Solution**:
- Added special case handling in `_show_setting()`:
  - `SHOW` → calls `_show_all_settings()`
  - `EDIT` → calls `handle_config([])` (interactive menu)
  - `RESET` → calls `_reset_configs()`

**Files Modified**:
- `core/commands/configuration_handler.py` (lines 140-155)

**Changes**:
```python
def _show_setting(self, key):
    """Show a specific setting value."""
    key_upper = key.upper()

    # Special case: SHOW (from default params) means show all settings
    if key_upper == 'SHOW':
        return self._show_all_settings()

    # Special case: EDIT means launch interactive editor
    elif key_upper == 'EDIT':
        return self.handle_config([])  # Launch interactive CONFIG menu

    # Special case: RESET means reset to defaults
    elif key_upper == 'RESET':
        return self._reset_configs()

    # Check different setting categories
    if key_upper == 'THEME':
        # ...existing code...
```

## Command Behavior (FIXED)

### SETUP Command (renamed from SETTINGS)
```bash
# All these now work correctly:
setup                 # Shows all settings (via SHOW default)
setup show            # Shows all settings (explicit)
setup edit            # Interactive menu (same as CONFIG)
setup reset           # Reset to defaults
setup theme           # Show theme setting
setup user            # Show user settings
setup grid            # Show grid settings

# Backward compatibility:
settings              # Alias for SETUP (works identically)
```

### CONFIG Command
```bash
# Interactive menu (enhanced):
config                # Interactive configuration menu
                      # Now includes "Quick Setup (View/Edit All Settings)" option

# Direct commands (already working):
config env            # Edit .env file
config user           # Manage user profile
config theme          # Manage theme
config system         # Manage system settings
config reset          # Reset to defaults
```

## Testing

### Manual Tests
1. **Type "setup"** → Should show all settings (not error)
2. **Type "setup edit"** → Should launch interactive CONFIG menu
3. **Type "settings"** → Should work as alias (backward compatibility)
4. **Type "config"** → Should show "Quick Setup" as menu option
5. **Update username via CONFIG** → Should save to user.json

### Expected Output (setup)
```
⚙️ uDOS SYSTEM SETTINGS
============================================================

🎨 THEME SETTINGS:
----------------------------------------
  Current Theme: Dungeon Crawler
  Color Mode: AUTO

📐 GRID SETTINGS:
----------------------------------------
  Terminal: 90×30
  Grid: 90×30
  Device: TERMINAL

👤 USER SETTINGS:
----------------------------------------
  Username: testuser
  Password: Not set
  Location: Sydney
  Timezone: AEST

⚙️ SYSTEM SETTINGS:
----------------------------------------
  CLI Editor: nano
  Debug Mode: Enabled
  Offline Mode: Disabled
```

## Impact Assessment

### ✅ Fixed
- ✅ CONFIG command interactive menu (get_user() error)
- ✅ SETUP command default behavior (SHOW error)
- ✅ SETUP renamed from SETTINGS (with backward compatibility)
- ✅ SETUP added to CONFIG menu as "Quick Setup (View/Edit All Settings)"
- ✅ User profile updates (username, password, location, timezone)
- ✅ Consistent command behavior (SETUP EDIT = CONFIG)

### 🔍 Not Changed
- Commands.json structure (DEFAULT_PARAMS still valid)
- ConfigManager API (already correct)
- User.json schema (unchanged)
- .env schema (unchanged)

### 📝 Future Improvements
1. **Consolidate SETTINGS into CONFIG** (future):
   - `CONFIG GET <key>` - Show setting value
   - `CONFIG SET <key> <value>` - Change setting
   - `CONFIG SHOW` - Show all settings
   - Deprecate SETTINGS command (redirect to CONFIG)

2. **Add CONFIG validation**:
   - Validate TILE codes before saving
   - Check timezone format
   - Verify location exists

3. **Improve error messages**:
   - Better hints for invalid setting keys
   - Suggest similar keys (fuzzy matching)

## Files Changed

### Modified
1. `core/commands/configuration_handler.py`
   - Renamed `handle_settings()` → `handle_setup()`
   - Lines 1111-1114: Replace `get_user()` with `get()`
   - Lines 1150-1235: Replace `set_user()` with `set()`
   - Lines 140-155: Add special case handling for SHOW/EDIT/RESET
   - Added "Quick Setup (View/Edit All Settings)" to CONFIG menu

2. `core/commands/system_handler.py`
   - Renamed `handle_settings()` → `handle_setup()`
   - Updated routing: `'SETTINGS'` → `'SETUP'`
   - Updated docstring

3. `core/data/commands.json`
   - Renamed command: `SETTINGS` → `SETUP`
   - Added `"ALIASES": ["SETTINGS"]` for backward compatibility
   - Updated description and notes

### Documentation
1. `sandbox/dev/settings-config-fixes.md` (this file)
2. `sandbox/tests/test_settings_config_fixes.py` (updated for SETUP rename)

## Verification

```bash
# Test in uDOS:
> setup                     # Should show all settings
> setup edit                # Should launch CONFIG menu
> settings                  # Should work as alias (backward compatibility)
> config                    # Should show "Quick Setup" option in menu
> setup user                # Should show user info
```

## Related Issues

- Fixes error handling from previous session (get_message enhancement)
- Improves STATUS command reliability (user data from user.json)
- Part of v1.1.6 post-release polish

## Success Metrics

- ✅ No more `'ConfigManager' object has no attribute 'get_user'` errors
- ✅ No more "Unknown setting: SHOW" errors
- ✅ SETUP and CONFIG commands work consistently
- ✅ SETTINGS works as backward-compatible alias
- ✅ CONFIG menu includes "Quick Setup" option
- ✅ User profile updates persist correctly

---

**Status**: ✅ COMPLETE
**Command Rename**: SETTINGS → SETUP (with SETTINGS as alias)
**Next**: Ready for use in v1.1.6+
