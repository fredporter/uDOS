# uDOS STORY Architecture - Unified Configuration System

**Version:** 1.1.0
**Date:** 22 November 2025
**Status:** Design Proposal

## Vision

Unify CONFIG, SETUP, GET, and SET commands into a coherent STORY-based architecture where configuration is treated as narrative data collection, influenced by theme lexicon and stored as executable uSCRIPT.

## Current State Analysis

### Existing Commands
- **CONFIG** - Interactive menu for config files, API keys, user profile
- **SETUP** - Wizard-style verbal setup (more narrative)
- **SETTINGS** - View/modify system settings
- **GET** - Retrieve field values (STORY.*, CONFIG.*, SYSTEM.*)
- **SET** - Modify field values (STORY.*, CONFIG.*)

### Data Storage Locations

```
/knowledge/system/          # System configuration (read-only reference data)
├── commands.json           # Command definitions
├── palette.json            # Color palettes
├── themes/                 # Theme definitions with lexicons
│   ├── dungeon.json       # "Greetings, adventurer..."
│   ├── foundation.json    # "Welcome, citizen..."
│   └── galaxy.json        # "Hail, commander..."
└── templates/             # Default configurations

/memory/sandbox/           # User workspace (read-write user data)
├── user.json             # Current active user data
│   ├── STORY section     # Narrative user profile (SET/GET/CONFIG)
│   └── user_profile section  # Legacy structure
└── workspace files
```

## Proposed STORY Architecture

### Core Concept

**STORY** = A collection of IO data represented as an executable uSCRIPT that:
1. **SETs** variables (system provides default values)
2. **GETs** variables (requests input from user)
3. Uses verbal, theme-influenced prompts
4. Generates reproducible configuration state

### STORY as uSCRIPT Format

```uscript
# story.uscript - User narrative configuration
# Generated: 2025-11-22 20:15:00
# Theme: dungeon
# Mode: interactive

# === IDENTITY ===
# The wizard asks for your name...
GET STORY.USER_NAME "What name shall I inscribe in the guild ledger?"

# Optional password for future authentication
GET STORY.PASSWORD "Enter a password to protect your account (or leave blank)"

# === LOCATION & TIME ===
# Auto-detect from system, user can override
SET STORY.TIMEZONE "Australia/Sydney"  # Auto-detected
SET STORY.LOCATION "Sydney"            # Derived from timezone

GET STORY.LOCATION "Your location (city, realm)?"  # User can override
GET STORY.TIMEZONE "Your timezone?"                # User can override

# === PROJECT CONTEXT ===
GET STORY.PROJECT_NAME "What quest are you embarking upon?"

# === PREFERENCES ===
SET STORY.THEME "dungeon"              # Active theme
SET STORY.WORKSPACE "sandbox"          # Active workspace
SET STORY.OFFLINE_MODE false           # Connection preference

# === METADATA ===
SET STORY.CREATED "2025-11-22T20:15:00"
SET STORY.LAST_SESSION "session_1763802900"
SET STORY.TOTAL_SESSIONS 42
SET STORY.TOTAL_MOVES 1337
```

### Theme-Influenced Prompts

Each theme provides a lexicon that transforms generic prompts:

**Generic:** "Enter your name"

**Theme Transformations:**
- `dungeon`: "What name shall I inscribe in the guild ledger?"
- `foundation`: "Please state your designation for Foundation records"
- `galaxy`: "Commander, state your identification for Imperial logs"
- `science`: "Enter subject identifier for research database"

**Lexicon Structure:**
```json
{
  "theme": "dungeon",
  "lexicon": {
    "prompts": {
      "username": "What name shall I inscribe in the guild ledger?",
      "password": "Speak the secret phrase, or press onward",
      "location": "From which realm do you hail?",
      "timezone": "Which temporal region governs your quest?",
      "project": "What quest are you embarking upon?"
    },
    "responses": {
      "success": "✅ The chronicles have been updated!",
      "error": "⚠️ The scribes report an error in the ledger",
      "saved": "💾 Your progress has been inscribed in the tome"
    },
    "terms": {
      "user": "adventurer",
      "system": "dungeon",
      "file": "scroll",
      "directory": "chamber"
    }
  }
}
```

## Unified Command Structure

### Single Entry Point: STORY Command

```bash
# Interactive narrative setup
STORY                      # Full wizard with theme-influenced prompts

# Explicit field operations (falls back to GET/SET)
STORY GET USER_NAME        # Retrieve value
STORY SET USER_NAME Fred   # Set value

# Story management
STORY SHOW                 # Display current story as formatted output
STORY SCRIPT               # Show story as executable uSCRIPT
STORY EXPORT story.uscript # Export to file
STORY IMPORT story.uscript # Import from file
STORY RESET                # Reset to defaults (with confirmation)
```

### Backward Compatibility

Existing commands become aliases/shortcuts:
- `CONFIG` → `STORY` (interactive mode)
- `SETUP` → `STORY` (with wizard flow)
- `GET field` → `STORY GET field`
- `SET field value` → `STORY SET field value`
- `SETTINGS USER` → `STORY SHOW USER`

## Data Architecture

### Unified user.json Structure

```json
{
  "STORY": {
    "USER_NAME": "Fred",
    "PASSWORD": "",
    "LOCATION": "Sydney",
    "TIMEZONE": "Australia/Sydney",
    "PROJECT_NAME": "Wizard",
    "THEME": "dungeon",
    "WORKSPACE": "sandbox",
    "OFFLINE_MODE": false,
    "CREATED": "2025-11-22T20:15:00",
    "LAST_UPDATED": "2025-11-22T20:15:00",
    "LAST_SESSION": "session_1763802900",
    "TOTAL_SESSIONS": 42,
    "TOTAL_MOVES": 1337
  },
  "OPTIONS": {
    "AUTO_SAVE": true,
    "LOG_LEVEL": "INFO",
    "ENABLE_AI": true,
    "FLASH_PROMPT": false
  },
  "METADATA": {
    "VERSION": "1.1.0",
    "FORMAT": "STORY_USCRIPT",
    "GENERATED_BY": "uDOS v1.0.29"
  }
}
```

### Field Categories

**STORY Fields** (user narrative):
- `USER_NAME` - User's name/handle
- `PASSWORD` - Optional authentication
- `LOCATION` - Physical location/city
- `TIMEZONE` - Timezone identifier
- `PROJECT_NAME` - Current project/quest (REMOVED from required)
- `THEME` - Active theme
- `WORKSPACE` - Active workspace

**OPTIONS Fields** (system preferences):
- `AUTO_SAVE` - Auto-save behavior
- `LOG_LEVEL` - Logging verbosity
- `ENABLE_AI` - AI features toggle
- `FLASH_PROMPT` - Prompt animation

**METADATA Fields** (read-only tracking):
- `CREATED` - Initial setup timestamp
- `LAST_UPDATED` - Last modification
- `LAST_SESSION` - Last session ID
- `TOTAL_SESSIONS` - Session counter
- `TOTAL_MOVES` - Command counter

## Implementation Plan

### Phase 1: Core Refactoring
1. ✅ Create `system_info.py` with timezone detection
2. ✅ Update CONFIG to use STORY fields
3. ✅ Update SETTINGS to read from STORY
4. 🔄 Consolidate SETUP to match CONFIG variables
5. 🔄 Enhance GET/SET to support smart mode

### Phase 2: Theme Lexicon System
1. Add lexicon to theme JSON files
2. Create `ThemeLexicon` service
3. Implement prompt transformation
4. Add response transformation

### Phase 3: STORY Command
1. Create `story_handler.py`
2. Implement STORY GET/SET/SHOW/SCRIPT
3. Add uSCRIPT export/import
4. Migrate CONFIG/SETUP to call STORY

### Phase 4: Integration
1. Update user_manager to use STORY format
2. Remove PROJECT_NAME requirement
3. Consolidate duplicate code
4. Add migration path for old configs

## Benefits

### For Users
- **Coherent narrative** - Configuration feels like part of the experience
- **Theme consistency** - Prompts match theme personality
- **Reproducibility** - Export/import story scripts
- **Simplicity** - One command (STORY) vs four (CONFIG/SETUP/GET/SET)

### For Developers
- **Single source of truth** - STORY section in user.json
- **DRY principle** - No duplicate field logic
- **Extensibility** - Easy to add new fields
- **Testability** - uSCRIPT format is testable

### For the System
- **Type safety** - Fields defined in one place
- **Validation** - Central validation logic
- **Versioning** - Story format version tracking
- **Migration** - Clear upgrade paths

## Example User Flow

### First-Time Setup (STORY Wizard)

```
uDOS> story

╔═══════════════════════════════════════════════════════════════╗
║              🏰 Welcome to the Dungeon, Adventurer!           ║
╠═══════════════════════════════════════════════════════════════╣
║  Before we begin your quest, I need to know a few things...  ║
╚═══════════════════════════════════════════════════════════════╝

🧙 What name shall I inscribe in the guild ledger?
> Fred

🔐 Speak the secret phrase, or press onward (leave blank to skip)
>

🌍 I sense you're in Sydney (Australia/Sydney timezone)
   From which realm do you hail? [Sydney]
>

⏰ Which temporal region governs your quest? [Australia/Sydney]
>

🎨 Choose your theme:
  1. Dungeon Crawler (classic adventure)
  2. Foundation (sci-fi bureaucracy)
  3. Galaxy Command (space opera)
> 1

╔═══════════════════════════════════════════════════════════════╗
║                    ✅ Your Story Begins!                      ║
╠═══════════════════════════════════════════════════════════════╣
║  Adventurer: Fred                                             ║
║  Realm: Sydney (Australia/Sydney)                             ║
║  Theme: Dungeon Crawler                                       ║
║                                                               ║
║  💾 Your tale has been inscribed in the chronicles            ║
╚═══════════════════════════════════════════════════════════════╝
```

### Quick Field Access

```bash
# Get field
uDOS> story get location
Sydney

# Set field (theme-aware response)
uDOS> story set location Melbourne
✅ The chronicles have been updated! Location: Melbourne

# View full story
uDOS> story show
╔═══════════════════════════════════════════════════════════════╗
║                        📖 Your Story                          ║
╠═══════════════════════════════════════════════════════════════╣
║  Adventurer: Fred                                             ║
║  Realm: Melbourne (Australia/Sydney)                          ║
║  Quest: Wizard                                                ║
║  Theme: Dungeon Crawler                                       ║
║  Chronicles: 42 sessions, 1337 commands                       ║
╚═══════════════════════════════════════════════════════════════╝

# Export story script
uDOS> story export my-config.uscript
✅ Story exported to: memory/user/my-config.uscript

# Import story script (on another machine)
uDOS> story import my-config.uscript
✅ Story imported successfully! Welcome back, Fred!
```

## Migration Strategy

### Backward Compatibility

All existing commands continue to work:
- `CONFIG` still works, calls STORY internally
- `SETUP` still works, calls STORY wizard
- `GET`/`SET` still work, delegate to STORY
- Old user.json files auto-migrate on load

### Migration Code

```python
def migrate_user_json(data: dict) -> dict:
    """Migrate old user.json to STORY format."""
    if 'STORY' in data and data.get('METADATA', {}).get('FORMAT') == 'STORY_USCRIPT':
        return data  # Already migrated

    # Migrate from old format
    migrated = {
        'STORY': {},
        'OPTIONS': {},
        'METADATA': {
            'VERSION': '1.1.0',
            'FORMAT': 'STORY_USCRIPT',
            'MIGRATED_FROM': data.get('METADATA', {}).get('VERSION', 'unknown'),
            'MIGRATED_AT': datetime.now().isoformat()
        }
    }

    # Copy user_profile fields to STORY
    if 'user_profile' in data:
        profile = data['user_profile']
        migrated['STORY']['USER_NAME'] = profile.get('username', '')
        migrated['STORY']['PROJECT_NAME'] = profile.get('project_name', '')
        # ... etc

    # Copy existing STORY fields
    if 'STORY' in data:
        migrated['STORY'].update(data['STORY'])

    return migrated
```

## Technical Specifications

### StoryManager API

```python
class StoryManager:
    """Unified story/configuration manager."""

    def get_field(self, path: str, default=None) -> Any:
        """Get field value: STORY.USER_NAME"""

    def set_field(self, path: str, value: Any, save=True) -> bool:
        """Set field value with optional auto-save"""

    def get_prompt(self, field: str) -> str:
        """Get theme-aware prompt for field"""

    def to_uscript(self) -> str:
        """Export story as executable uSCRIPT"""

    def from_uscript(self, script: str) -> bool:
        """Import story from uSCRIPT"""

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate story completeness"""
```

### Theme Lexicon API

```python
class ThemeLexicon:
    """Theme-aware text transformation."""

    def transform_prompt(self, generic: str, field: str) -> str:
        """Transform generic prompt using theme lexicon"""

    def transform_response(self, response_type: str) -> str:
        """Get theme-specific response message"""

    def get_term(self, generic_term: str) -> str:
        """Get theme-specific term (file→scroll, user→adventurer)"""
```

## Success Criteria

1. ✅ Single source of truth for user configuration
2. ✅ Theme-consistent user experience
3. ✅ Backward compatible with existing configs
4. ✅ Export/import story scripts work
5. ✅ No duplicate code between CONFIG/SETUP/GET/SET
6. ✅ User can change any field without full wizard
7. ✅ System auto-detects sensible defaults

## Next Steps

1. Review and approve this design
2. Implement Phase 1 (core refactoring)
3. Add theme lexicons to existing themes
4. Create STORY command handler
5. Migrate CONFIG/SETUP to use STORY
6. Update documentation
7. Release as uDOS v1.1.0

---

**End of Design Document**
