# Theme Architecture: Display Overlay System

**Version:** 1.0.0  
**Date:** 2026-01-14  
**Status:** DESIGN (ready for implementation)  

---

## Overview

Themes are a **display overlay layer** applied AFTER runtime execution, error logging, and debugging. This keeps the system clean and transparent while enabling immersive, thematic presentation.

### Architecture Layers

```
Runtime/Execution/Logging (CORE - unchanged)
          ↓
    [System Output]
    (raw debug info)
          ↓
    Theme Overlay Layer
    (vocabulary mapping)
          ↓
    [Themed Output]
    (immersive presentation)
```

**Key Principle:** Themes never interfere with debugging, logging, or system transparency.

---

## Core Concept: Variable Mapping

Each theme maps **system variable names** to **theme-specific vocabulary**.

### System Variables (Canonical)

These are the core system terms that appear in logs, errors, and output:

```
SYSTEM VARIABLES:
  Sandbox         - Execution environment
  Syntax Error    - Code/command parsing failure
  Plugin          - Extension or module
  Drafts          - Work-in-progress files
  Folders         - Directory containers
  Documents       - Saved content
  Projects        - Workspace containers
  Tasks           - Executable units
  Commands        - User input
  Variables       - Data storage
  Functions       - Callable code
  Modules         - Code packages
  Services        - Background processes
  Sessions        - User work periods
  Memory          - Storage/RAM
  Cache           - Temporary storage
  Config          - Settings
  State           - Current system status
  Error           - Failure condition
  Warning         - Caution condition
  Success         - Completion
  Status          - Current state
  Progress        - Completion percentage
  Timeout         - Execution timeout
  Interrupt       - User cancellation
  Retry           - Attempt repetition
  Confirm         - User approval
  Input           - User entry
  Output          - System result
```

---

## Theme Configurations

Each theme provides a **-story.md or -config.md file** with:

1. **Theme Metadata** - Name, author, description, emoji set
2. **Variable Mapping** - System var → Theme verb/noun
3. **Message Templates** - Context-specific formatting
4. **Style Guides** - Tone, punctuation, emoji usage

### Theme File Structure

```
core/data/themes/
├── dungeon-adventure/
│   ├── theme-config.md
│   ├── theme-story.md
│   ├── variables.json
│   └── messages.json
├── stranger-things/
│   ├── theme-config.md
│   ├── variables.json
│   └── messages.json
├── lonely-planet/
│   ├── theme-config.md
│   ├── variables.json
│   └── messages.json
├── retro-computing/
│   └── ...
├── fantasy-zelda/
│   └── ...
├── foundation-space/
│   └── ...
└── armageddon/
    └── ...
```

---

## Theme Designs

### 1. Dungeon Adventure (Nethack)

**Atmosphere:** Classic roguelike, medieval fantasy, discovery  
**Emoji Set:** 💀 💎 🗝️ 🧙 ⚔️ 🪦 🧭 📜  

**Variable Mapping:**

```
Sandbox      → Dungeon
Syntax Error → Cursed Incantation / Invalid Spell
Plugin       → Enchantment / Artifact
Drafts       → Unscribed Scrolls
Folders      → Chambers / Vaults
Documents    → Scrolls / Codices
Projects     → Quests
Tasks        → Objectives
Commands     → Incantations / Spells
Error        → Trap Sprung / Curse
Warning      → Eerie Feeling / Omen
Success      → Treasure Found / Quest Complete
Status       → Divining the Dungeon State
Progress     → Progress Through the Labyrinth
Variables    → Magical Essences
Functions    → Rituals / Spellcasting
Services     → Spirits / Guardians
Memory       → Enchanted Storage
Cache        → Forgotten Caches
Config       → Dungeon Settings
Timeout      → Time Runs Out (sand timer)
Interrupt    → Suddenly Interrupted
Retry        → Attempt Again
```

**Example Output:**
```
⚔️ CURSED INCANTATION: The spell failed to compile
🧙 ATTEMPTING AGAIN...
💎 TREASURE FOUND: Project "dragon-slayer" created
```

---

### 2. Stranger Things (Upside Down, D&D, 80s)

**Atmosphere:** 80s nostalgia, D&D references, supernatural  
**Emoji Set:** 📺 🎲 🕯️ ☠️ 🌀 🎸 ❌ 🪡  

**Variable Mapping:**

```
Sandbox      → The Upside Down / Demogorgon's Lair
Syntax Error → Roll Failed / Critical Miss
Plugin       → Ally Creature / Party Member
Drafts       → Unread Scrolls
Folders      → Treasure Chest Compartments
Documents    → Campaign Notes / Monster Manual Pages
Projects     → Campaigns
Tasks        → Monster Hunts / Quests
Commands     → Incantations / D20 Rolls
Error        → Demogorgon Appears! / You Died!
Warning      → Strange Sounds in the Distance
Success      → Enemy Defeated / Secret Found
Status       → Checking Your Vitals
Progress     → Party Marches Forward
Variables    → Mysterious Artifacts
Functions    → Spell Incantations
Services     → Helpful Wizards / Companions
Memory       → Crystal Ball Visions
Cache        → Hidden Stashes
Config       → Campaign Settings
Timeout      → The Sun Is Setting
Interrupt    → STRANGER ALERT!
Retry        → Roll Again
```

**Example Output:**
```
🎲 CRITICAL MISS: Syntax error in line 42
🕯️ SHADOWS GATHER - Retrying...
📺 SECRET FOUND: Module "wizard-tower" loaded
```

---

### 3. Lonely Planet Guide / Hitchhiker's Guide to the Galaxy

**Atmosphere:** Travel guide, adventure, dry wit, cosmic humor  
**Emoji Set:** 🗺️ 🚀 ✨ 📖 🌍 ☕ 🛸 🧳  

**Variable Mapping:**

```
Sandbox      → Planetary Environment / Local System
Syntax Error → Miscommunication / Babel Fish Fails
Plugin       → Local Guide / Useful Companion
Drafts       → Travel Notes
Folders      → Regions / Provinces
Documents    → Guidebook Entries / Travel Logs
Projects     → Expeditions / Journeys
Tasks        → Local Attractions to Visit
Commands     → Questions to Ask the Guide
Error        → Lost in Translation / Map Outdated
Warning      → Beware of Pickpockets
Success      → Discovered a Wonderful Place
Status       → Checking Our Location
Progress     → Miles Traveled
Variables    → Interesting Local Customs
Functions    → Local Traditions / Customs
Services     → Helpful Local Guides
Memory       → Travel Memories
Cache        → Rest Stop Souvenirs
Config       → Trip Preferences
Timeout      → The Tour Ends
Interrupt    → Bus Is Leaving!
Retry        → Ask Again, More Carefully
```

**Example Output:**
```
🗺️ LOST IN TRANSLATION: The code didn't parse correctly
☕ SO LONG AND THANKS FOR ALL THE FISH... retrying
✨ WONDERFUL DISCOVERY: New module "babel-fish" added
```

---

### 4. Retro Computing (80s/90s Computer)

**Atmosphere:** Vintage computer aesthetic, DOS/Apple II era  
**Emoji Set:** 💾 🖥️ ⌨️ 🔌 📠 🎮 ▓ █  

**Variable Mapping:**

```
Sandbox      → Boot Environment
Syntax Error → Parse Error / Invalid Token
Plugin       → Driver / Peripheral
Drafts       → Temp Files
Folders      → Directories
Documents    → Files
Projects     → Disks / Programs
Tasks        → Processes / Jobs
Commands     → Commands
Error        → ERROR: System Fault
Warning      → WARNING: Check Disk
Success      → DONE
Status       → System Status
Progress     → File Copy Progress
Variables    → Variables in Memory
Functions    → Subroutines
Services     → Daemons / TSRs
Memory       → RAM Available
Cache        → Disk Cache
Config       → CONFIG.SYS
Timeout      → Timeout Waiting for Input
Interrupt    → CTRL+C: User Abort
Retry        → Retry: Y/N?
```

**Example Output:**
```
💾 ERROR: Syntax Error at line 42
⌨️ Retry: Y/N?
🖥️ DONE: Program "WIZARD.EXE" loaded
```

---

### 5. Fantasy Zelda / Storytelling

**Atmosphere:** Storybook fantasy, hero's journey, treasure  
**Emoji Set:** ⚔️ 🗝️ 💛 🌳 🏰 👑 ✨ 🧝  

**Variable Mapping:**

```
Sandbox      → The Realm / Kingdom
Syntax Error → Curse Upon Your Quest / Riddle Unsolved
Plugin       → Magical Item / Artifact
Drafts       → Unwritten Pages
Folders      → Kingdoms / Regions
Documents    → Ancient Texts / Prophecies
Projects     → Epic Quests
Tasks        → Adventures / Trials
Commands     → Invocations / Wishes
Error        → The Dark Lord's Curse / Quest Failed
Warning      → A Dark Shadow Looms
Success      → You Have Triumphed / Treasure Obtained
Status       → The Tale Continues...
Progress     → Your Journey Advances
Variables    → Magical Stones / Runes
Functions    → Ancient Magic / Spells
Services     → Guardian Spirits / Helpful Fairies
Memory       → Memories of Legends
Cache        → Hidden Treasures
Config       → The Hero's Destiny
Timeout      → Time Runs Short
Interrupt    → Your Adventure Ends
Retry        → Try Once More
```

**Example Output:**
```
⚔️ CURSE UPON YOUR QUEST: Parsing failed
✨ YOU MAY TRY AGAIN...
💛 TREASURE FOUND: "dragon-sword" module acquired
```

---

### 6. Foundation / Space Colonization

**Atmosphere:** SciFi epic, space exploration, civilization building  
**Emoji Set:** 🌌 🚀 🔬 🔭 🪐 ⚛️ 👽 🌠  

**Variable Mapping:**

```
Sandbox      → Spacecraft / Outpost
Syntax Error → Navigation Error / Signal Loss
Plugin       → Ship Module / System Component
Drafts       → Science Officer's Notes
Folders      → Ship Sections
Documents    → Scientific Data / Logs
Projects     → Missions / Expeditions
Tasks        → Scientific Objectives
Commands     → Ship Commands / Orders
Error        → Hull Breach / System Failure
Warning      → Radiation Alert / Anomaly Detected
Success      → Mission Accomplished / New World Found
Status       → Transmission Status
Progress     → Distance to Destination
Variables    → Stellar Coordinates / Measurements
Functions    → Ship Systems / Protocols
Services     → AI Assistants / Drones
Memory       → Archived Knowledge
Cache        → Ship Library
Config       → Mission Parameters
Timeout      → Fuel Reserves Critical
Interrupt    → Emergency Stop
Retry        → Transmitting Again
```

**Example Output:**
```
⚛️ SIGNAL LOST: Error in propulsion system
🚀 RETRANSMITTING...
🌌 MISSION ACCOMPLISHED: New colony "terra-nova" established
```

---

### 7. Armageddon / Doomsday

**Atmosphere:** Post-apocalyptic, survival, grim reality, dark humor  
**Emoji Set:** ☢️ 🔥 💀 🏚️ 🧟 ⚰️ 🌪️ 👹  

**Variable Mapping:**

```
Sandbox      → Fallout Shelter / Bunker
Syntax Error → Geiger Counter Clicks / Corrupted Data
Plugin       → Salvaged Device / Makeshift Tool
Drafts       → Crumpled Notes
Folders      → Bunker Compartments
Documents    → Survivor's Journal / Map
Projects     → Survival Plans
Tasks        → Scavenging Missions
Commands     → Desperate Actions
Error        → CONTAMINATION / Systems Down
Warning      → Radiation Spiking / Danger Nearby
Success      → Food Found / Shelter Secured
Status       → Survival Status Report
Progress     → Miles to Sanctuary
Variables    → Radiation Levels / Supplies
Functions    → Jury-Rigged Contraptions
Services     → Other Survivors / Allies
Memory       → Memories of Before
Cache        → Emergency Supplies
Config       → Shelter Settings
Timeout      → Oxygen Running Out
Interrupt    → RUN NOW
Retry        → Try to Survive Again
```

**Example Output:**
```
☢️ CONTAMINATION: System error detected
🔥 ATTEMPTING SURVIVAL...
💀 SHELTER SECURED: Safe zone "new-eden" created
```

---

## Implementation Architecture

### Theme Overlay Layer

```python
class ThemeOverlay:
    """
    Display overlay system - applies theming AFTER core execution.
    """
    
    def __init__(self, theme_name: str):
        self.theme_name = theme_name
        self.variables = self._load_variables()  # System var → theme vocab
        self.messages = self._load_messages()    # Message templates
        self.config = self._load_config()        # Theme settings
    
    def apply(self, output: str, context: dict) -> str:
        """
        Apply theme overlay to system output.
        
        AFTER: Execution, logging, debugging
        BEFORE: Display to user
        
        Context keys:
          - output_type: 'error', 'success', 'status', 'log'
          - system_vars: Dict of variable names used
          - message_level: 'critical', 'warning', 'info'
        """
        # Replace system variables with theme vocabulary
        themed = self._map_variables(output)
        
        # Apply message templates
        themed = self._apply_templates(themed, context)
        
        # Add theme-specific formatting (emoji, color, style)
        themed = self._format_output(themed, context)
        
        return themed
    
    def _map_variables(self, text: str) -> str:
        """Replace system variable names with theme vocabulary."""
        for sys_var, theme_vocab in self.variables.items():
            text = text.replace(sys_var, theme_vocab)
        return text
```

### File Structure: `dungeon-adventure/theme-story.md`

```markdown
# Dungeon Adventure Theme

Welcome, brave adventurer, to the depths of the uDOS Dungeon!

## Theme Overview
- **Style:** Classic roguelike fantasy (Nethack)
- **Emoji Set:** 💀 💎 🗝️ 🧙 ⚔️ 🪦 🧭 📜
- **Tone:** Mysterious, challenging, discovery-oriented

## Variable Mapping

When the system says "Sandbox", you'll see "Dungeon" instead.
When the system says "Plugin", you'll see "Enchantment" instead.

| System Variable | Dungeon Adventure | Example |
|---|---|---|
| Sandbox | Dungeon | "Entering the Dungeon..." |
| Syntax Error | Cursed Incantation | "⚔️ CURSED INCANTATION: Invalid spell at line 42" |
| Plugin | Enchantment | "The Enchantment of Auto-Save activated" |
| Error | Trap Sprung | "💀 TRAP SPRUNG: File not found" |
| Success | Treasure Found | "💎 TREASURE FOUND: Project saved successfully" |

## Message Templates

### Errors
```
⚔️ [THEME_VERB_ERROR]: [description]
→ The dungeon has played a trick on you...
```

### Success
```
💎 TREASURE FOUND: [what was found]
→ Your quest has borne fruit!
```

### Status
```
🧙 [THEME_VERB_STATUS]: [status message]
→ The spirits guide your way...
```

## Style Guide

- **Punctuation:** Ellipses (...) for mystery, exclamation points for action
- **Tone:** Mysterious, encouraging, whimsical
- **Additional Context:** Include thematic flavor text where appropriate

---

## How It Works

All debug output remains **pure and unchanged** in logs.
The theme overlay applies **only at display time**, transforming:

```
RAW (in logs):
ERROR: Syntax error in function parse_command at line 42

THEMED (to user):
⚔️ CURSED INCANTATION: The spell failed to parse
→ The dungeon jeers at your magical attempts...
→ Line 42 of the incantation is corrupt
```
```

---

## Implementation Steps

1. **Create Theme Config System**
   - Separate config/story files for each theme
   - JSON for variable mapping
   - Markdown for documentation/style guides

2. **Build Theme Overlay Layer**
   - Standalone module (no core dependencies)
   - Applied AFTER logging/execution
   - Variable substitution engine
   - Message template system

3. **Preserve Debugging**
   - All raw output in logs unchanged
   - Theme overlay happens at display-only
   - Easy to toggle themes on/off
   - No impact on error tracking

4. **Theme Extensibility**
   - Easy to add new themes
   - Clear variable mapping structure
   - Reusable message templates
   - Community-contributed themes supported

---

## Benefits

✅ **Immersive UX** - Fun, thematic presentation  
✅ **Clean Debugging** - Logs stay pure and transparent  
✅ **Extensible** - Easy to add new themes  
✅ **Non-invasive** - Theme layer isolated from core  
✅ **Optional** - Users can disable themes anytime  
✅ **Creative** - Themes can tell stories, educate, entertain  

---

## Next Steps

1. Design detailed config/story files for each theme
2. Build the ThemeOverlay layer
3. Create variable mapping system
4. Integrate with display pipeline
5. Add theme selection to user preferences

---

*Themes as an overlay layer: Pure debugging + immersive experience = best of both worlds*
