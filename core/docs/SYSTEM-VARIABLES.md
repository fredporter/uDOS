# uDOS System Variables - Standardized Reference

## Overview
This document defines the canonical system variables for uDOS v1.1.6+.

**Design Principle**: NO DUPLICATION - Each piece of data lives in exactly ONE place.

## File Responsibilities

### `.env` - System & Application Configuration
- API keys and credentials
- System preferences (editor, theme, defaults)
- Server configuration
- Installation-specific settings
- **Technical/system-level config only**

### `user.json` - User Data Only
- User identity and profile information
- Project details
- Location and geographic data
- Session history
- **Personal/user-specific data only**

---

## Environment Variables (.env)

**Purpose**: System configuration and API credentials

```bash
# Installation Identity
UDOS_INSTALLATION_ID='unique-id'        # Unique installation identifier (NOT username)

# API Keys (System Credentials)
GEMINI_API_KEY='your-key-here'          # Google Gemini API
OPENROUTER_API_KEY='your-key-here'      # OpenRouter API
ANTHROPIC_API_KEY='your-key-here'       # Anthropic Claude API
OPENAI_API_KEY='your-key-here'          # OpenAI API

# System Preferences
DEFAULT_WORKSPACE='sandbox'             # Default workspace directory
DEFAULT_MODEL='gemini'                  # Default AI model
THEME='dark'                            # Color theme
CLI_EDITOR='nano'                       # CLI text editor (nano, micro, vim, vi)
WEB_EDITOR='typo'                       # Web-based editor

# Server Configuration
AUTO_START_WEB='false'                  # Auto-start web dashboard
AUTO_START_SERVER='false'               # Auto-start HTTP server
HTTP_SERVER_PORT='5000'                 # HTTP server port

# Session Management
MAX_SESSION_HISTORY='100'               # Max session history entries
AUTO_SAVE_SESSION='true'                # Auto-save session state
```

**What NOT to put in .env**: Username, location, timezone, project name (those go in user.json)

---

## User Configuration (user.json)

**Purpose**: User personal data and project information

All keys use **UPPERCASE** for consistency:

```json
{
  "SYSTEM_NAME": "uDOS",
  "VERSION": "1.0.30",

  "USER_PROFILE": {
    "NAME": "Fred",                     // User's display name (ONLY HERE, not in .env)
    "LOCATION": "Brisbane, AU",         // User's location
    "TIMEZONE": "Australia/Brisbane",   // User's timezone
    "PASSWORD": "",                     // Optional password (hashed)
    "PREFERRED_MODE": "STANDARD"        // UI mode preference
  },

  "PROJECT": {
    "NAME": "uDOS Development",         // Current project name
    "DESCRIPTION": "...",               // Project description
    "START_DATE": "2025-01-01"          // Project start date
  },

  "LOCATION_DATA": {
    "CITY": "Brisbane",                 // City name
    "COUNTRY": "Australia",             // Country name
    "LATITUDE": -27.4698,               // Latitude coordinate
    "LONGITUDE": 153.0251,              // Longitude coordinate
    "MAP_POSITION": {
      "X": 0,                           // Grid X position
      "Y": 0                            // Grid Y position
    },
    "CURRENT_LAYER": "SURFACE"          // Current map layer
  },

  "SESSION_DATA": {
    "CURRENT_SESSION": "",              // Current session ID
    "SESSION_COUNT": 0,                 // Total session count
    "LAST_LOGIN": "",                   // Last login timestamp
    "VIEWPORT": {}                      // Viewport configuration
  }
}
```

**What NOT to put in user.json**: API keys, editor preferences, server config (those go in .env)

---

## Access Patterns

### Python Code

```python
from core.config import get_config

config = get_config()

# Environment variables (.env) - System config
installation_id = config.get_env('UDOS_INSTALLATION_ID', 'default')
api_key = config.get_env('GEMINI_API_KEY', '')
theme = config.get_env('THEME', 'dark')
editor = config.get_env('CLI_EDITOR', 'nano')

# User configuration (user.json) - User data
username = config.get_user('USER_PROFILE.NAME', 'user')
location = config.get_user('USER_PROFILE.LOCATION', '')
timezone = config.get_user('USER_PROFILE.TIMEZONE', 'UTC')
project_name = config.get_user('PROJECT.NAME', '')

# Set environment variables (system config)
config.set_env('THEME', 'synthwave')
config.set_env('CLI_EDITOR', 'micro')

# Set user configuration (user data)
config.set_user('USER_PROFILE.NAME', 'Fred')
config.set_user('USER_PROFILE.LOCATION', 'Brisbane, AU')
config.set_user('PROJECT.NAME', 'My Project')
```

### NO Duplication Rules

**❌ REMOVED** - No more username in .env:
- ~~`UDOS_USERNAME`~~ - Removed, use `USER_PROFILE.NAME` only

**Single Source of Truth**:
- Username → `user.json` only (`USER_PROFILE.NAME`)
- Location → `user.json` only (`USER_PROFILE.LOCATION`)
- Timezone → `user.json` only (`USER_PROFILE.TIMEZONE`)
- Project → `user.json` only (`PROJECT.NAME`)
- API Keys → `.env` only
- Editor → `.env` only
- Theme → `.env` only

---

## Migration Guide

### Removing Duplication

**Step 1**: Remove `UDOS_USERNAME` from `.env`
```bash
# Remove this line from .env:
# UDOS_USERNAME='fred'
```

**Step 2**: Ensure username is in `user.json`:
```json
{
  "USER_PROFILE": {
    "NAME": "Fred"  // ← Username lives HERE only
  }
}
```

### Old → New Variable Names

**Environment Variables:**
- ~~`USERNAME`~~ → REMOVED (use `USER_PROFILE.NAME` in user.json)
- ~~`UDOS_USERNAME`~~ → REMOVED (use `USER_PROFILE.NAME` in user.json)
- `INSTALLATION_ID` → `UDOS_INSTALLATION_ID`

**User JSON:**
- `user_profile.username` → `USER_PROFILE.NAME`
- `user_profile.location` → `USER_PROFILE.LOCATION`
- `user_profile.timezone` → `USER_PROFILE.TIMEZONE`
- `user_profile.password` → `USER_PROFILE.PASSWORD`

### Code Migration Examples

**Before (v1.1.5 and earlier):**
```python
# ❌ Old inconsistent access with duplication
username = config.get('USERNAME')           # .env
name = config.get_user('user_profile.username')  # user.json (lowercase)
config.set('UDOS_USERNAME', 'Fred')        # Duplicated to .env
```

**After (v1.1.6+):**
```python
# ✅ New single-source access
name = config.get_user('USER_PROFILE.NAME', '')  # ONLY source for username
location = config.get_user('USER_PROFILE.LOCATION', '')
timezone = config.get_user('USER_PROFILE.TIMEZONE', 'UTC')

# ✅ System config from .env only
api_key = config.get_env('GEMINI_API_KEY', '')
theme = config.get_env('UDOS_THEME', 'foundation')
```

## Validation

Required fields for a valid user profile:
- `user.json`: `USER_PROFILE.NAME` (must be set)
- `user.json`: `USER_PROFILE.TIMEZONE` (must be valid timezone)

Optional fields:
- `user.json`: `USER_PROFILE.PASSWORD`
- `user.json`: `USER_PROFILE.LOCATION`
- `.env`: All API keys (optional, system functions without them)

**Removed Fields:**
- ~~`.env`: `UDOS_USERNAME`~~ → Removed in v1.1.6 (use `USER_PROFILE.NAME` only)

## Best Practices

1. **Single source of truth**: Each data point lives in ONE place only
   - Username → `user.json` (`USER_PROFILE.NAME`)
   - API keys → `.env` (`GEMINI_API_KEY`, etc.)
   - System config → `.env` (`UDOS_THEME`, etc.)

2. **Use uppercase for user.json keys**: Follow the template schema
   ```python
   # ✅ Correct
   config.get_user('USER_PROFILE.NAME')

   # ❌ Wrong (old lowercase schema)
   config.get_user('user_profile.username')
   ```

3. **Use UDOS_ prefix for .env vars**: Avoid namespace collisions
   ```python
   # ✅ Correct
   UDOS_INSTALLATION_ID=abc123
   UDOS_THEME=foundation

   # ❌ Wrong (no prefix)
   INSTALLATION_ID=abc123
   THEME=foundation
   ```

4. **Never duplicate data**: If you're tempted to sync data between files, DON'T
   ```python
   # ❌ Wrong - duplication
   config.set_env('UDOS_USERNAME', value)
   config.set_user('USER_PROFILE.NAME', value)

   # ✅ Correct - single source
   config.set_user('USER_PROFILE.NAME', value)
   ```

5. **Validate on startup**: Check that required fields exist

## Testing

```bash
# Verify user.json (single source of truth)
python -c "from core.config import get_config; c = get_config(); print('Name:', c.get_user('USER_PROFILE.NAME'))"

# Verify username property (reads from user.json)
python -c "from core.config import get_config; c = get_config(); print('Username:', c.username)"

# Verify installation ID (reads from .env)
python -c "from core.config import get_config; c = get_config(); print('Install ID:', c.installation_id)"

# Verify system config (.env)
python -c "from core.config import get_config; c = get_config(); print('Theme:', c.get_env('THEME', 'foundation'))"
```

---

**Version**: 1.1.6
**Last Updated**: 2025-11-28
**Status**: CANONICAL REFERENCE
