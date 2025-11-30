# User Configuration System Fix - November 30, 2025

## Problem

The DASH command and other parts of uDOS were showing default values instead of actual user configuration:
- Name: "user" instead of actual username from user.json
- Location: "Unknown" instead of location from planets.json/user.json
- Timezone: "UTC" instead of user's timezone
- Planet/Project info not displayed

## Root Cause Analysis

1. **Wrong File Path**: ConfigManager was calculating base path incorrectly
   - Used `.parent.parent.parent` which went too far up the directory tree
   - Result: `/Users/fredbook/Code/` instead of `/Users/fredbook/Code/uDOS/`
   - Files weren't being found at expected paths

2. **Schema Mismatch**: Dashboard used lowercase keys (`username`, `location`) but schema only had uppercase (`USERNAME`, `LOCATION`)

3. **Format Inconsistency**: user.json uses lowercase fields (`user_profile.username`) but old code expected uppercase (`USER_PROFILE.NAME`)

## Solution

### 1. Fixed Base Path Calculation

**File**: `core/config_manager.py` (line 61)

```python
# BEFORE (incorrect - went up 3 levels)
base_path = Path(__file__).parent.parent.parent

# AFTER (correct - goes up 2 levels from core/config_manager.py)
base_path = Path(__file__).parent.parent
```

**Result**: Now correctly resolves to `/Users/fredbook/Code/uDOS/`

### 2. Added Lowercase Schema Keys

**File**: `core/config_manager.py` (lines 199-255)

Added dashboard-compatible fields to schema:
- `username` (from user.json user_profile.username)
- `location` (from planets.json or user.json location data)
- `timezone` (from user.json user_profile.timezone)
- `planet` (from planets.json current_planet)
- `project_name` (from user.json user_profile.project_name)
- `project_description` (from user.json PROJECT.DESCRIPTION)
- `mode` (from user.json user_profile.mode)

### 3. Updated load_user_json() Method

**File**: `core/config_manager.py` (lines 338-380)

Now handles both old and new JSON formats:

```python
# Supports both formats
profile = user_data.get('USER_PROFILE') or user_data.get('user_profile', {})

# Maps both uppercase and lowercase field names
if 'NAME' in profile:
    self._config['username'] = profile['NAME']
elif 'username' in profile:
    self._config['username'] = profile['username']
```

### 4. Added load_planet_data() Method

**File**: `core/config_manager.py` (lines 383-424)

Loads planet and location data from `sandbox/user/planets.json`:
- Current planet name
- Location from planet's location field
- Coordinates (latitude/longitude)

### 5. Updated Dashboard Display

**File**: `core/commands/dashboard_handler.py` (lines 240-262)

Now reads from unified ConfigManager:
- Shows actual username, location, timezone
- Displays current planet
- Shows project name from user.json

## File Structure

### Configuration Sources (Priority Order)

1. **Defaults** (lowest priority)
   - Defined in schema

2. **.env file**
   - System-level config
   - API keys, installation settings

3. **sandbox/user.json**
   - User profile (username, project, timezone)
   - Location data (city, country, coordinates)

4. **sandbox/user/planets.json**
   - Current planet selection
   - Planet-specific location overrides

5. **Runtime modifications** (highest priority)
   - In-memory changes via CONFIG command

## Testing Results

### Before Fix
```
Name: user                 Location: Unknown
Timezone: UTC              Mode: STANDARD
Project: uDOS              Type: CLI Framework
```

### After Fix
```
Name: testuser             Location: London, England, UK
Timezone: UTC              Mode: STANDARD
Planet: Earth              Project: uDOS_dev
Type: Offline-first OS for survival knowledge
```

## Verification

Run test script:
```bash
python3 sandbox/scripts/test_config_load.py
```

Expected output:
```
✓ username: testuser
✓ location: London (or Sydney from planets.json)
✓ timezone: UTC
✓ planet: Earth
✓ project_name: uDOS_dev
```

## Files Modified

1. `core/config_manager.py` - Fixed path calculation, added schema fields, updated loaders
2. `core/commands/dashboard_handler.py` - Updated to use ConfigManager properly
3. `sandbox/scripts/test_config_load.py` - NEW test script

## Benefits

1. **Unified Configuration**: Single source of truth across all commands
2. **Format Flexibility**: Supports both old (uppercase) and new (lowercase) JSON formats
3. **Correct Path Resolution**: Works from any working directory
4. **Planet Integration**: Seamlessly integrates planet system with user profile
5. **Easy Testing**: Simple test script to verify configuration loading

## Next Steps

1. Update other commands to use ConfigManager (if not already)
2. Consider migrating all uppercase JSON fields to lowercase for consistency
3. Add CONFIG command to update user.json fields directly
4. Document configuration file formats in wiki

---

**Status**: ✅ Complete
**Date**: November 30, 2025
**Version**: 2.0.0
