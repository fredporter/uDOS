# Theme System Redesign - Implementation Plan

**Version:** 1.0.0  
**Date:** 2026-01-14  
**Status:** READY FOR IMPLEMENTATION  

---

## Overview

Transform the current `theme_messenger.py` into a comprehensive **Theme Overlay System** that:

1. **Keeps debugging pure** - All logs and errors in canonical form
2. **Applies themes at display time** - Only affects what user sees
3. **Maps system variables** - `Sandbox` → `Dungeon`, `Plugin` → `Enchantment`, etc.
4. **Provides immersive UX** - Rich thematic presentation
5. **Stays extensible** - Easy to add new themes

---

## Current State

| Item | Location | Status |
|------|----------|--------|
| theme_messenger.py | core/services/ | ✅ Existing, can be upgraded |
| theme_manager.py | core/services/theme/ | ✅ Manages theme selection |
| theme_builder.py | core/services/theme/ | ✅ Creates custom themes |
| DEFAULT_VOCAB | theme_messenger.py | ⚠️ Partial, needs expansion |

---

## Phase 1: Theme Configuration System

### Create Theme Config Files

**Directory Structure:**

```
core/data/themes/
├── dungeon-adventure/
│   ├── theme-story.md          # Rich documentation
│   ├── variables.json          # System var → theme vocab mapping
│   └── messages.json           # Message templates
├── stranger-things/
│   ├── theme-story.md
│   ├── variables.json
│   └── messages.json
├── lonely-planet/
│   ├── theme-story.md
│   ├── variables.json
│   └── messages.json
├── retro-computing/
│   ├── theme-story.md
│   ├── variables.json
│   └── messages.json
├── fantasy-zelda/
│   ├── theme-story.md
│   ├── variables.json
│   └── messages.json
├── foundation-space/
│   ├── theme-story.md
│   ├── variables.json
│   └── messages.json
└── armageddon/
    ├── theme-story.md
    ├── variables.json
    └── messages.json
```

### Variables JSON Format

**File:** `dungeon-adventure/variables.json`

```json
{
  "theme_name": "Dungeon Adventure",
  "theme_id": "dungeon-adventure",
  "style": "Classic roguelike fantasy",
  "emoji_set": ["💀", "💎", "🗝️", "🧙", "⚔️", "🪦", "🧭", "📜"],
  "variables": {
    "Sandbox": "Dungeon",
    "Syntax Error": "Cursed Incantation",
    "Plugin": "Enchantment",
    "Drafts": "Unscribed Scrolls",
    "Folders": "Chambers",
    "Documents": "Scrolls",
    "Projects": "Quests",
    "Tasks": "Objectives",
    "Commands": "Incantations",
    "Error": "Trap Sprung",
    "Warning": "Eerie Feeling",
    "Success": "Treasure Found",
    "Status": "Divining",
    "Progress": "Labyrinth Progress",
    "Variables": "Magical Essences",
    "Functions": "Rituals",
    "Services": "Spirits",
    "Memory": "Enchanted Storage",
    "Cache": "Forgotten Caches",
    "Config": "Dungeon Settings",
    "Timeout": "Time Runs Out",
    "Interrupt": "Suddenly Interrupted",
    "Retry": "Attempt Again"
  }
}
```

### Messages JSON Format

**File:** `dungeon-adventure/messages.json`

```json
{
  "templates": {
    "error": {
      "prefix": "⚔️",
      "verb": "CURSED INCANTATION",
      "format": "{prefix} {verb}: {message}",
      "flavor": "The dungeon has deceived you..."
    },
    "success": {
      "prefix": "💎",
      "verb": "TREASURE FOUND",
      "format": "{prefix} {verb}: {message}",
      "flavor": "Your quest bears fruit!"
    },
    "warning": {
      "prefix": "🧙",
      "verb": "EERIE FEELING",
      "format": "{prefix} {verb}: {message}",
      "flavor": "Caution, brave adventurer..."
    },
    "status": {
      "prefix": "🧙",
      "verb": "DIVINING",
      "format": "{prefix} {verb}: {message}",
      "flavor": "The spirits guide your path..."
    }
  }
}
```

---

## Phase 2: Upgrade ThemeOverlay System

### New File: `core/services/theme_overlay.py`

```python
"""
Theme Overlay System

Applies theming AFTER execution/logging (display-only layer).
Maps system variables to theme-specific vocabulary.
"""

import json
from pathlib import Path
from typing import Dict, Optional


class ThemeOverlay:
    """
    Display overlay system for thematic presentation.
    Applied AFTER core execution - no impact on debugging.
    """
    
    def __init__(self, theme_id: str = "minimal"):
        self.theme_id = theme_id
        self.variables = self._load_variables()
        self.messages = self._load_messages()
    
    def apply(self, text: str, context: Dict = None) -> str:
        """
        Apply theme overlay to text.
        
        Args:
            text: Raw output text (from logs/execution)
            context: {
                'type': 'error'|'success'|'warning'|'status',
                'system_vars': set of variable names used,
                'level': 'critical'|'warning'|'info'
            }
        
        Returns:
            Themed text (raw text unchanged, only display changes)
        """
        context = context or {}
        output = text
        
        # Replace system variables with theme vocabulary
        output = self._map_variables(output)
        
        # Apply message formatting based on type
        msg_type = context.get('type', 'status')
        if msg_type in self.messages['templates']:
            output = self._format_message(output, msg_type)
        
        return output
    
    def _map_variables(self, text: str) -> str:
        """Replace system variable names with theme vocabulary."""
        for sys_var, theme_vocab in self.variables.items():
            # Use word boundaries to avoid partial replacements
            text = text.replace(f" {sys_var} ", f" {theme_vocab} ")
            text = text.replace(f"{sys_var}:", f"{theme_vocab}:")
        return text
    
    def _format_message(self, text: str, msg_type: str) -> str:
        """Apply message template formatting."""
        template = self.messages['templates'].get(msg_type, {})
        prefix = template.get('prefix', '•')
        verb = template.get('verb', 'INFO').upper()
        
        # Prepend theme formatting if not already present
        if not text.startswith(prefix):
            text = f"{prefix} {verb}: {text}"
        
        return text
    
    def _load_variables(self) -> Dict[str, str]:
        """Load variable mapping for current theme."""
        var_file = Path(__file__).parent.parent / "data" / "themes" / self.theme_id / "variables.json"
        
        try:
            with open(var_file) as f:
                data = json.load(f)
                return data.get('variables', {})
        except Exception:
            return {}  # Fallback to no mapping
    
    def _load_messages(self) -> Dict:
        """Load message templates for current theme."""
        msg_file = Path(__file__).parent.parent / "data" / "themes" / self.theme_id / "messages.json"
        
        try:
            with open(msg_file) as f:
                return json.load(f)
        except Exception:
            return {'templates': {}}  # Fallback to empty templates


def get_theme_overlay(theme_id: str = "minimal") -> ThemeOverlay:
    """Factory function to get theme overlay."""
    return ThemeOverlay(theme_id)
```

---

## Phase 3: Integration Points

### Where Themes Apply (Display-Only)

1. **User Output** - Command results shown to user
2. **Status Messages** - System status displays
3. **Error Prompts** - User-facing error messages
4. **Success Notifications** - Completion messages
5. **Interactive Prompts** - Question/confirmation prompts

### Where Themes DON'T Apply (Raw Logs)

1. ✅ Log files - Always canonical
2. ✅ Error reports - Pure system info
3. ✅ Debug output - Raw and complete
4. ✅ API responses - Unchanged JSON/data
5. ✅ File contents - Never modified

---

## Phase 4: Theme Selection

### User Preferences

```python
# Add to core/config.py
THEME_PREFERENCES = {
    'current_theme': 'minimal',        # Default minimal theme
    'available_themes': [
        'minimal',
        'dungeon-adventure',
        'stranger-things',
        'lonely-planet',
        'retro-computing',
        'fantasy-zelda',
        'foundation-space',
        'armageddon'
    ],
    'theme_enabled': True,
    'theme_color_enabled': True,
    'theme_emoji_enabled': True
}
```

### Commands to Support

```
THEME                          # Show current theme
THEME LIST                     # List available themes
THEME <name>                   # Switch to theme
THEME PREVIEW <name>           # Preview theme
THEME DISABLE                  # Turn off theming
THEME ENABLE                   # Turn on theming
THEME SHOW VARIABLES <name>    # Show variable mappings
```

---

## Phase 5: Implementation Roadmap

| Step | Task | Duration | Priority |
|------|------|----------|----------|
| 1 | Create 7 theme config directories | 1-2 hrs | 🔴 High |
| 2 | Write variables.json for each theme | 2-3 hrs | 🔴 High |
| 3 | Write messages.json for each theme | 1-2 hrs | 🔴 High |
| 4 | Create theme-story.md documentation | 2-3 hrs | 🟡 Medium |
| 5 | Build ThemeOverlay class | 2 hrs | 🔴 High |
| 6 | Integrate with display pipeline | 2-3 hrs | 🔴 High |
| 7 | Add theme selection commands | 1-2 hrs | 🟡 Medium |
| 8 | Test all themes, edge cases | 2-3 hrs | 🔴 High |
| 9 | Documentation + examples | 1-2 hrs | 🟡 Medium |

**Total Estimated Time:** 15-20 hours

---

## Success Criteria

✅ All 7 themes with complete variable mappings  
✅ ThemeOverlay system working (display-only)  
✅ Theme selection commands functional  
✅ Raw logs remain unchanged (canonical)  
✅ Themes can be disabled at any time  
✅ Easy to add new themes  
✅ No impact on system transparency/debugging  
✅ Theme documentation complete  

---

## Benefits

| Aspect | Benefit |
|--------|---------|
| **User Experience** | Immersive, themed presentation |
| **Debugging** | No impact - all logs are pure |
| **Extensibility** | Community can create themes |
| **Flexibility** | Easy to toggle on/off |
| **Architecture** | Clean separation of concerns |
| **Maintainability** | Config-driven, not code-driven |

---

## Next Action

Begin with Step 1: Create theme directory structure and starter files.

---

*This redesign makes themes an elegant display overlay, not a core system concern.*
