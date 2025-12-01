# User Configuration Consolidation Fix

**Date:** December 1, 2025
**Issue:** Multiple conflicting user data sources in user.json
**Impact:** STATUS/DASH show wrong user info, wizard flow is overcomplic

ated

## Problem Analysis

### Current State (BROKEN)

user.json has **3 conflicting sections**:

```json
{
  "user_profile": {
    "username": "Fred",
    "timezone": "UTC",  // WRONG - not updated by wizard
    ...
  },
  "STORY": {
    "USER_NAME": "Fred",
    "TIMEZONE": "Australia/Sydney",  // CORRECT
    "LOCATION": "Byron Bay",  // CORRECT
    "THEME": "dungeon"
  },
  "system_settings": { ... }
}
```

### Code Reading Wrong Locations

1. **Config.username** → reads `USER_PROFILE.NAME` (doesn't exist!)
2. **STATUS** → reads from multiple sources (inconsistent)
3. **DASH** → reads `user_profile` (has wrong timezone)
4. **Wizard** → writes to `STORY` section (correct)

## Solution: Single Source of Truth

### New Structure

```json
{
  "user": {
    "name": "Fred",
    "password": "",
    "location": "Brisbane, AU",
    "timezone": "Australia/Brisbane"
  },
  "system": {
    "theme": "dungeon",
    "viewport": "auto",
    "installation_id": "udos_default"
  },
  "session": {
    "last_updated": "2025-12-01T...",
    "project_name": "uDOS_dev",
    "mode": "STANDARD"
  }
}
```

### Changes Required

1. **core/config.py** - Fix `username` property:
   ```python
   @property
   def username(self) -> str:
       return self.get_user('user.name', 'user')

   @property
   def timezone(self) -> str:
       return self.get_user('user.timezone', 'UTC')

   @property
   def location(self) -> str:
       return self.get_user('user.location', 'Unknown')
   ```

2. **core/services/setup_wizard.py** - Simplify to 4 fields:
   - Remove duplicate prompts
   - Write to `user` section only
   - Skip if already configured

3. **core/commands/system_handler.py** - Fix STATUS/DASH:
   - Read from `config.username`, `config.timezone`, `config.location`
   - Remove hardcoded "user", "Unknown", "UTC"

4. **Migration** - Update existing user.json:
   - Copy STORY.* → user.*
   - Remove user_profile, STORY sections
   - Add system, session sections

## Implementation Steps

1. Create migration script
2. Update Config properties
3. Simplify wizard
4. Update STATUS/DASH
5. Test full flow
6. Commit changes

## Expected Result

After fix:
- Wizard asks for 4 fields ONCE
- Data saves to user.json `user` section
- STATUS shows correct name, location, timezone
- DASH shows correct data
- CONFIG can update individual fields
- No more "user", "Unknown", "UTC" defaults
