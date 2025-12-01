# Configuration System Review - December 1, 2025

## Summary

The configuration system has **dual implementations** that need consolidation:

1. **core/config.py** (Config class) - Modern, clean, v2.0-aligned ✅
2. **core/config_manager.py** (ConfigManager class) - Deprecated, complex, marked for removal ⚠️

## Current State

### ✅ GOOD: core/config.py (Recommended)
```python
from core.config import Config, get_config

config = get_config()
# Simple, clean API:
value = config.get_env('THEME', 'dungeon')
config.set_env('THEME', 'cyberpunk')
value = config.get_user('USER_PROFILE.NAME', 'user')
config.set_user('SYSTEM.GALAXY', 'Milky Way')
```

**Strengths:**
- Clean separation: `.env` (system) vs `user.json` (user data)
- Simple API with clear sources
- Singleton pattern via `get_config()`
- No bidirectional sync complexity
- Already supports SYSTEM section (Galaxy/Planet/City)
- Used by: extensions, wiki docs, copilot instructions

**Weaknesses:**
- Missing color palette getter/setter
- Default CLI_EDITOR still 'nano' in some fallbacks (should be 'micro')
- No DEV_MODE helper property

### ⚠️ DEPRECATED: core/config_manager.py (Remove in v2.1.0)
```python
from core.config_manager import ConfigManager  # DEPRECATED!
```

**Issues:**
- 1200+ lines of complex code
- Bidirectional sync creates confusion
- Duplicate username fields (USERNAME vs username)
- Old TILE code format (tile_code vs grid_cell + layer)
- Deprecated warning added but still functional
- Only used in old dev notes (not production)

**Migration Status:**
- ✅ Wiki updated to use `core.config`
- ✅ Extensions use `core.config`
- ✅ Copilot instructions use `core.config`
- ❌ Still imported in some places (needs cleanup)

## Alignment Issues

### 1. CLI_EDITOR Default Mismatch
- `.env.example`: `CLI_EDITOR=micro` ✅
- `core/config.py`: Falls back to `'nano'` in some code ❌
- `configuration_handler.py`: Now uses `'micro'` with fallback message ✅
- **Fix**: Update all `get_env('CLI_EDITOR', 'nano')` → `'micro'`

### 2. Color Palette Support
- User wants: Palette selection in CONFIG menu
- `user.json`: Has `system_settings.interface.color_palette` field
- `core/config.py`: No helper property for color_palette
- `configuration_handler.py`: Now reads/writes palette ✅
- **Fix**: Add `@property color_palette` to Config class

### 3. DEV_MODE Access
- `user.json`: Can store DEV_MODE flag
- `core/config.py`: No DEV_MODE property
- `configuration_handler.py`: Uses `config.get('DEV_MODE', False)` ✅
- **Fix**: Add `@property dev_mode` to Config class

### 4. Connection Status
- User wants: Internet availability check in CONFIG
- Current: Uses `self.connection.is_online()` if available
- Better: Check cloud extension API (`poke_online`) for tunnel status
- **Fix**: Already implemented in configuration_handler.py ✅

## Recommended Actions

### IMMEDIATE (Before v1.1.8 release)

1. **Update core/config.py**:
   ```python
   # Add helper properties:
   @property
   def color_palette(self) -> str:
       return self.get_user('system_settings.interface.color_palette', 'polaroid')

   @property
   def dev_mode(self) -> bool:
       return self.get('DEV_MODE', False) or self.get_user('DEV_MODE', False)

   @property
   def cli_editor(self) -> str:
       return self.get_env('CLI_EDITOR', 'micro')  # Default: micro, not nano
   ```

2. **Remove config_manager.py imports**:
   - Search: `from core.config_manager import`
   - Replace with: `from core.config import get_config`
   - Only in `sandbox/dev/` notes (not production code)

3. **Update CLI_EDITOR defaults**:
   - `core/config.py` line 147: Change default from `'nano'` to `'micro'`
   - Already done in `configuration_handler.py` ✅

### SOON (v2.0.1 cleanup)

4. **Delete core/config_manager.py**:
   - Already deprecated with warning
   - Not used in production
   - Schedule removal for v2.1.0

5. **Standardize config access patterns**:
   - Core system: Always use `from core.config import get_config`
   - Extensions: Can use Config directly or get_config singleton
   - No more ConfigManager usage

6. **Document extension config pattern**:
   - Extension `extension.json` defines config schema
   - Extension code uses `get_config()` for system settings
   - Extension stores own data in `extensions/<name>/data/`

## Extension Configuration Pattern

### Standard Approach (Recommended)
```python
# In extension code:
from core.config import get_config

class MyExtension:
    def __init__(self):
        self.config = get_config()

        # System settings (shared):
        self.api_key = self.config.get_env('GEMINI_API_KEY')
        self.theme = self.config.theme

        # Extension-specific (own file):
        self.ext_config_path = Path('extensions/my-ext/config.json')
        self.ext_settings = self._load_ext_config()

    def _load_ext_config(self):
        if self.ext_config_path.exists():
            return json.loads(self.ext_config_path.read_text())
        return self._get_defaults()
```

### extension.json Schema
```json
{
  "id": "my-extension",
  "config": {
    "default_value": "something",
    "max_items": 100
  },
  "requires_config": ["GEMINI_API_KEY"],
  "optional_config": ["THEME"]
}
```

## Testing Checklist

- [x] CONFIG command shows all new fields
- [x] SETUP command interactive menu works
- [x] Color palette selection functional
- [x] Dev Mode toggle works
- [x] CLI Editor defaults to micro
- [x] System location (Galaxy/Planet/City) displays
- [x] Connection status checks cloud extension
- [ ] Update core/config.py with helper properties
- [ ] Remove config_manager imports from dev notes
- [ ] Test extension config access patterns

## Files Modified This Session

1. `core/commands/configuration_handler.py` - Enhanced settings display
2. `.env.example` - Already has CLI_EDITOR=micro ✅
3. `core/commands/configuration_handler.py` - Added palette/dev mode support

## Next Steps

1. Add helper properties to `core/config.py` (color_palette, dev_mode, cli_editor)
2. Update CLI_EDITOR default from 'nano' to 'micro' in core/config.py
3. Test CONFIG command end-to-end
4. Document extension config pattern in wiki
5. Schedule config_manager.py removal for v2.1.0

---

**Conclusion**: The configuration system is **mostly aligned** with one clear path forward (core/config.py). Minor tweaks needed for helper properties and default values. The deprecated config_manager.py should be removed in next major version.
