# uDATA System Configuration

## Overview
The uDOS system now uses a simplified uDATA-based configuration system instead of complex JSON structures and Python loaders.

## Current Structure

### Core uDATA Files in `/uMEMORY/system/`:

1. **uDATA-system-config.json** (16 lines) - Base system configuration for distribution
   - Display modes, interface settings, default values
   - Feature flags (smart terminal, auto-complete, etc.)
   - Performance settings (cache limits, history)
   - All settings use simple key-value format with uCODE naming

2. **uDATA-config.json** (14 lines) - Core system variables
   - System version, uDATA format version
   - Reference to system config file
   - Runtime variables and session data

3. **uDATA-colours.json** (9 lines) - Color palette definitions
   - Polaroid Colors as default palette
   - All color palettes in unified format

4. **uDATA-commands.json** (26 lines) - Unified command system
   - All commands use [COMMAND|SYNTAX] format
   - Replaces separate shortcodes/commands files

5. **uDATA-user-roles.json** (9 lines) - User role hierarchy
   - 8-role system from wizard to ghost
   - Simplified permission structure

## Configuration Reader

### Shell-based Reader: `/uCORE/system/udata-config-reader.sh`

Replaces the Python `config_loader.py` with a simple shell script that can:

- Read uDATA values by name
- Get display defaults
- Check feature flags
- Validate uDATA files
- Generate CSS variables
- List commands and syntax

### Usage Examples:

```bash
# Get display defaults
./uCORE/system/udata-config-reader.sh get-display-defaults

# Check a specific system setting
./uCORE/system/udata-config-reader.sh get-system-config DEFAULT_FONT

# Validate all uDATA files
./uCORE/system/udata-config-reader.sh validate

# Generate CSS for color palette
./uCORE/system/udata-config-reader.sh generate-css polaroid_colors
```

## Removed/Deprecated

- `/uMEMORY/system/config/` folder → moved to `legacy-config-backup/`
- `config_loader.py` → replaced with shell script
- Complex nested JSON configurations → simplified uDATA format
- Date stamps in filenames → clean naming for compatibility

## User Settings

Current system settings should be stored in:
- `/uMEMORY/user/` - user-specific overrides
- `/uMEMORY/role/` - role-based configurations
- `/sandbox/` - temporary/session settings

The files in `/uMEMORY/system/` are the distributable base reference settings.

## Benefits

1. **Simplified Configuration**: No Python dependencies for config reading
2. **uCODE Compatibility**: Settings use standard uCODE formatting
3. **Better Distribution**: Clean base settings for packaging
4. **Extensible**: Can easily add more settings later
5. **Shell Integration**: Works with existing shell-based tools
