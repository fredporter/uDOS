# uCODE Language Specification

**Version:** v1.2 (uPY v1.2 Three-Format Syntax)
**Status:** Production
**Last Updated:** December 8, 2025

---

## Overview

uCODE is uDOS's command language and scripting system. It provides both interactive commands and programmable scripts for survival knowledge, mapping, content generation, and system automation.

**uPY (uPython)** is the scripting extension with variables, functions, and control flow - designed as a minimal, educational gateway to Python.

### Design Principles

1. **Minimal Design**: Essential features only, no bloat
2. **Offline-First**: Full functionality without internet/API
3. **Human-Centric**: Clear language, practical focus
4. **Text-First**: Terminal-based, ASCII graphics
5. **Educational**: Gateway to Python programming

---

## uPY v1.2 Syntax

Three-format system with distinct brackets for variables, commands, and conditionals.

### Variables

**Always use {$var}** - Clear, consistent variable syntax:

```upy
# Assignment
SET {$name|'Alice'}
SET {$count|42}
SET {$active|true}

# Using in strings (interpolation)
PRINT ('Hello {$name}!')
PRINT ('Count: {$count}')

# Conditions
[IF {$count} > 5: PRINT ('Large')]
[IF {$name} == 'Alice': XP (+10)]
```

### Output

**Single quotes in (parentheses)** - Clean output with interpolation:

```upy
PRINT ('Hello, world!')
PRINT ('HP: {$hp}/{$max_hp}')
PRINT ()  # Blank line

# System variables use {$}
PRINT ('Location: {$SPRITE-LOCATION}')
PRINT ('Mission: {$MISSION.NAME}')
```

### Conditionals

**Three formats** - Choose based on complexity:

**1. Short form (one-line):**
```upy
[IF {$hp} < 30: PRINT ('Low health!')]
[IF {$hp} < 30: HP (+20) | PRINT ('Healed!')]  # Multiple actions with |
```

**2. Medium form (inline THEN/ELSE):**
```upy
[IF {$hp} < 30 THEN: HP (+20) ELSE: PRINT ('Healthy')]
[IF {$gold} >= 100 THEN: ITEM (sword) ELSE: PRINT ('Need more gold')]
[{$hp} < 30 ? HP (+20) : PRINT ('OK')]  # Ternary style
```

**3. Long form (multi-line, no indents):**
```upy
IF {$hp} < 30
  HP (+20)
  PRINT ('Emergency healing!')
  FLAG (used_healing)
ELSE IF {$hp} < 60
  HP (+10)
  PRINT ('Minor healing')
ELSE
  PRINT ('Health is fine')
END IF
```

**Delimiters:**
- `:` - THEN separator
- `|` - Multiple actions
- `?` - Ternary condition
- `THEN/ELSE` - Explicit keywords

### Functions

**Three formats** - Choose based on complexity:

**1. Short form (single expression):**
```upy
@add({$a}|{$b}): RETURN {$a} + {$b}
@greet({$name}): PRINT ('Hello {$name}!')
```

**2. Medium form (one-line multi-action):**
```upy
@heal({$amount}): SET {$SPRITE-HP|{$SPRITE-HP} + {$amount}} | PRINT ('Healed {$amount}!')
```

**3. Long form (multi-line, no indents):**
```upy
FUNCTION heal_player({$amount})
  SET {$old_hp|{$SPRITE-HP}}
  SET {$SPRITE-HP|{$SPRITE-HP} + {$amount}}
  [IF {$SPRITE-HP} > {$SPRITE-HP-MAX}: SET {$SPRITE-HP|{$SPRITE-HP-MAX}}]
  SET {$healed|{$SPRITE-HP} - {$old_hp}}
  PRINT ('Healed {$healed} HP!')
  RETURN {$healed}
END FUNCTION
```

**Calling:**
```upy
@greet('Hero')           # Short form
SET {$result|@add(5|3)}  # With return value
```

### Loops

**FOREACH** - Iterate over collections:

```upy
FOREACH {$item} IN {$items}
  PRINT ('Processing {$item}...')
END_FOR
```

### Bracket & Separator Rules

**Three bracket types:**
- `{$variable}` - All variables (assignment, interpolation, system)
- `(command|params)` - Commands and functions
- `[condition]` - Short-form conditionals (one-line only)

**Delimiters:**
- `|` - Separator for params/multiple actions (no spaces)
- `:` - THEN separator in conditionals
- `?` - Ternary condition marker
- `→` - Result assignment (ROLL, function returns)

```upy
# Good
SET {$var|value}
@function({$arg1}|{$arg2}|{$arg3})
[IF {$hp} < 30: HP (+20) | PRINT ('Healed!')]
[{$hp} < 30 ? HP (+20) : PRINT ('OK')]

# Bad
SET {$var, value}     # No commas
SET {$var * value}    # No asterisks
SET {$var | value}    # No spaces around |
```

**Format choice:**
- **Short `[...]`**: 1-2 actions, simple conditions
- **Medium `[... THEN: ... ELSE: ...]`**: Branching logic, inline
- **Long `IF/END IF`**: 3+ lines, complex logic, multiple branches

**Complete syntax reference:** [uPY-Syntax-v2.md](uPY-Syntax-v2.md)

---

---

## HELP System

Interactive help with command categories, examples, and navigation.

### HELP Navigation

```bash
HELP                    # Main menu with categories
HELP <category>         # List commands in category
HELP <command>          # Detailed command help
HELP <command> examples # Usage examples
```

### Main Menu

```
╔═══════════════════════════════════════════════════════════════════════╗
║                        uDOS v1.1.16 - HELP SYSTEM                      ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  📚 COMMAND CATEGORIES                                                 ║
║                                                                        ║
║  1. 🎓 KNOWLEDGE        - Guides, learning, skills (GUIDE, LEARN)     ║
║  2. 🗺️  MAPPING          - Navigation, terrain, routes (TILE, MAP)     ║
║  3. 🎮 ADVENTURE        - RPG system, quests (XP, HP, ITEM, ROLL)     ║
║  4. 🎨 GRAPHICS         - Diagrams, panels, sprites (PANEL, DRAW)     ║
║  5. 💾 MEMORY           - 4-tier storage (MEMORY, PRIVATE, SHARED)    ║
║  6. 📁 FILES            - File operations (NEW, DELETE, COPY, MOVE)   ║
║  7. ⚙️  SYSTEM          - Settings, backup, repair (STATUS, CLEAN)    ║
║  8. 🌐 SERVERS          - Web interfaces (POKE, dashboard, teletext)  ║
║  9. 🤖 ASSISTANT        - AI helper (GENERATE, ASK, ANALYZE)          ║
║  10. 🔧 WORKFLOWS       - Automation, missions (WORKFLOW, MISSION)    ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║  USAGE                                                                 ║
║    HELP <category>     - List commands in category (e.g., HELP KNOWLEDGE) ║
║    HELP <command>      - Show detailed help (e.g., HELP GUIDE)        ║
║    HELP <cmd> examples - Show usage examples                          ║
║                                                                        ║
║  NAVIGATION                                                            ║
║    [1-10]   Select category    [Q] Quit                               ║
║    [N]ext   Previous page      [S]earch commands                      ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Category View - Example: HELP KNOWLEDGE

```
╔═══════════════════════════════════════════════════════════════════════╗
║                     📚 KNOWLEDGE COMMANDS (6)                          ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  GUIDE (category/topic)         - Interactive survival guides         ║
║    Example: GUIDE (water/purification)                                ║
║    Categories: water, fire, shelter, food, medical, navigation        ║
║                                                                        ║
║  LEARN (topic)                  - Quick reference cards                ║
║    Example: LEARN (knots)                                             ║
║    Shows: Essential steps, safety warnings, skill level               ║
║                                                                        ║
║  SEARCH (query)                 - Search knowledge bank                ║
║    Example: SEARCH (emergency first aid)                              ║
║    Filters: category, complexity, tags                                ║
║                                                                        ║
║  LIST (category)                - Browse available content             ║
║    Example: LIST (medical)                                            ║
║    Shows: Title, complexity, last updated                             ║
║                                                                        ║
║  PROGRESS                       - Track learning progress              ║
║    Shows completed guides, skill levels, achievements                 ║
║                                                                        ║
║  BOOKMARK (guide)               - Save guide for quick access          ║
║    Example: BOOKMARK (water/purification)                             ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║  TIPS                                                                  ║
║    • All guides work offline - no internet required                   ║
║    • Use GUIDE --interactive for step-by-step walkthroughs           ║
║    • Track progress across all 6 survival categories                  ║
║                                                                        ║
║  [B]ack to menu    [1-6] Select command    [Q]uit                     ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Command Detail - Example: HELP GUIDE

```
╔═══════════════════════════════════════════════════════════════════════╗
║                          GUIDE - Interactive Guides                    ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  DESCRIPTION                                                           ║
║    Access interactive survival guides with progress tracking and      ║
║    step-by-step instructions. All content works offline.              ║
║                                                                        ║
║  SYNTAX                                                                ║
║    GUIDE (category/topic)                                             ║
║    GUIDE (category/topic) --interactive                               ║
║    GUIDE (category/topic) --complexity <simple|detailed|technical>    ║
║                                                                        ║
║  PARAMETERS                                                            ║
║    category     - water, fire, shelter, food, medical, navigation     ║
║    topic        - Specific guide (e.g., purification, knots, triage)  ║
║    --interactive - Step-by-step walkthrough mode                      ║
║    --complexity  - Guide detail level (default: detailed)             ║
║                                                                        ║
║  EXAMPLES                                                              ║
║    GUIDE (water/purification)                                         ║
║      → Boiling, filtration, chemical treatment methods                ║
║                                                                        ║
║    GUIDE (fire/friction) --interactive                                ║
║      → Step-by-step fire-starting with bow drill                      ║
║                                                                        ║
║    GUIDE (medical/triage) --complexity technical                      ║
║      → Advanced triage protocols and decision trees                   ║
║                                                                        ║
║    GUIDE (shelter)                                                     ║
║      → List all shelter guides (lean-to, debris hut, etc.)            ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║  RELATED COMMANDS                                                      ║
║    LEARN (topic)      - Quick reference cards                         ║
║    SEARCH (query)     - Find guides by keyword                        ║
║    PROGRESS           - Track completed guides                        ║
║                                                                        ║
║  [E]xamples    [B]ack to category    [Q]uit                           ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Examples View - HELP GUIDE examples

```
╔═══════════════════════════════════════════════════════════════════════╗
║                      GUIDE - Usage Examples                            ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  EXAMPLE 1: Basic Guide Access                                        ║
║    GUIDE (water/purification)                                         ║
║                                                                        ║
║    Output:                                                             ║
║    ┌─────────────────────────────────────────────────┐                ║
║    │ 💧 Water Purification Guide                     │                ║
║    │ Complexity: Detailed | Duration: 15 min         │                ║
║    ├─────────────────────────────────────────────────┤                ║
║    │ Methods:                                        │                ║
║    │ 1. Boiling (most reliable)                     │                ║
║    │ 2. Filtration (portable)                       │                ║
║    │ 3. Chemical treatment (iodine/chlorine)        │                ║
║    │ 4. UV purification (equipment required)        │                ║
║    └─────────────────────────────────────────────────┘                ║
║                                                                        ║
║  EXAMPLE 2: Interactive Walkthrough                                   ║
║    GUIDE (fire/friction) --interactive                                ║
║                                                                        ║
║    → Guides you through bow drill fire-starting with:                 ║
║      • Step-by-step instructions                                      ║
║      • Progress checkpoints                                           ║
║      • Troubleshooting tips                                           ║
║      • Mark completion for XP                                         ║
║                                                                        ║
║  EXAMPLE 3: Technical Depth                                           ║
║    GUIDE (medical/wound-care) --complexity technical                  ║
║                                                                        ║
║    → Advanced content with:                                           ║
║      • Medical terminology                                            ║
║      • Detailed procedures                                            ║
║      • Decision trees                                                 ║
║      • Contraindications                                              ║
║                                                                        ║
║  EXAMPLE 4: Browse Category                                           ║
║    GUIDE (shelter)                                                     ║
║                                                                        ║
║    → Lists all 20 shelter guides:                                     ║
║      • Lean-to construction                                           ║
║      • Debris hut                                                     ║
║      • Snow cave                                                      ║
║      • Tarp shelters                                                  ║
║      • ... and 16 more                                                ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║  [B]ack to command help    [Q]uit                                      ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Pagination System

Commands with many results auto-paginate:

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    🗺️  MAPPING COMMANDS (Page 1/2)                     ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  TILE INFO <location>           - City/country information             ║
║  TILE SEARCH <query>            - Find cities/countries                ║
║  TILE NEARBY <location> [km]    - Cities within radius                 ║
║  TILE WEATHER <location>        - Climate zone (Köppen)                ║
║  TILE TIMEZONE <location>       - Timezone + DST                       ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║  [N]ext page    [P]revious    [B]ack to menu    [Q]uit                ║
╚═══════════════════════════════════════════════════════════════════════╝

(Press N for next page...)

╔═══════════════════════════════════════════════════════════════════════╗
║                    🗺️  MAPPING COMMANDS (Page 2/2)                     ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  TILE TERRAIN [type]            - Terrain definitions (24 types)       ║
║  TILE ROUTE <from> <to>         - Calculate distance + bearing        ║
║  TILE CONVERT <val> <from> <to> - Unit conversion (temp, dist, mass)  ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║  [P]revious page    [B]ack to menu    [Q]uit                          ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Search Functionality

```bash
HELP --search <query>
HELP /search <query>
```

Example:

```
> HELP --search water

╔═══════════════════════════════════════════════════════════════════════╗
║                    🔍 Search Results: "water" (8 matches)              ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  1. GUIDE water/purification    - Water purification methods           ║
║  2. GUIDE water/collection      - Collecting water sources             ║
║  3. GUIDE water/storage         - Safe water storage                   ║
║  4. TILE WEATHER                - Climate (includes rainfall)          ║
║  5. DRAW water-cycle            - Diagram: water cycle                 ║
║  6. GENERATE guide water        - Generate water guides                ║
║  7. MEMORY tier1                - Includes water guides                ║
║  8. LEARN hydration             - Hydration best practices             ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║  [1-8] Select    [R]efine search    [B]ack    [Q]uit                  ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Syntax Highlighting (Terminal Colors)

When terminal supports ANSI colors:

```bash
# Command syntax highlighting
GUIDE (water/purification) --interactive
│     │                  └─ Option (cyan)
│     └─ Parameter (green)
└─ Command (yellow bold)

# Code examples in HELP
SET {$hp|100}
│    │   └─ Value (magenta)
│    └─ Variable (green)
└─ Command (yellow)

[IF {$hp} < 30: PRINT ('Low health!')]
│   │    │  │        │
│   │    │  │        └─ String (cyan)
│   │    │  └─ Command (yellow)
│   │    └─ Operator (red)
│   └─ Variable (green)
└─ Keyword (blue bold)
```

### Quick Reference Cards

Compact command summaries:

```bash
HELP --quick <command>
```

Example:

```
┌─────────────────────────────────────────────────┐
│ GUIDE - Quick Reference                         │
├─────────────────────────────────────────────────┤
│ Purpose: Interactive survival guides            │
│                                                 │
│ Basic:   GUIDE (water/purification)             │
│ Options: --interactive, --complexity <level>    │
│                                                 │
│ Common:                                         │
│   GUIDE fire      List fire guides              │
│   GUIDE --help    Full documentation            │
└─────────────────────────────────────────────────┘
```

---

---

## Command Categories

Complete reference for all uDOS commands organized by category.

### 1. 🎓 KNOWLEDGE Commands

Access survival guides, learning resources, and skill tracking.

| Command | Description | Example |
|:--------|:------------|:--------|
| `GUIDE (cat/topic)` | Interactive survival guides | `GUIDE (water/purification)` |
| `LEARN (topic)` | Quick reference cards | `LEARN (knots)` |
| `SEARCH (query)` | Search knowledge bank | `SEARCH (first aid)` |
| `LIST (category)` | Browse available content | `LIST (medical)` |
| `PROGRESS` | Track learning progress | `PROGRESS` |
| `BOOKMARK (guide)` | Save for quick access | `BOOKMARK (fire/friction)` |

**Categories:** water, fire, shelter, food, medical, navigation, tools, communication

### 2. 🗺️ MAPPING Commands

Geographic data, terrain, navigation, and routing.

| Command | Description | Example |
|:--------|:------------|:--------|
| `TILE INFO (loc)` | City/country information | `TILE INFO (Tokyo)` |
| `TILE SEARCH (q)` | Find cities/countries | `TILE SEARCH (Paris)` |
| `TILE NEARBY (loc) (km)` | Cities within radius | `TILE NEARBY (Sydney) (500)` |
| `TILE WEATHER (loc)` | Climate zone (Köppen) | `TILE WEATHER (Brisbane)` |
| `TILE TIMEZONE (loc)` | Timezone + DST | `TILE TIMEZONE (London)` |
| `TILE TERRAIN (type)` | Terrain definitions | `TILE TERRAIN (forest)` |
| `TILE ROUTE (from) (to)` | Distance + bearing | `TILE ROUTE (NYC) (London)` |
| `TILE CONVERT (v) (f) (t)` | Unit conversion | `TILE CONVERT (100) (C) (F)` |

**Data:** 250 cities, 50 countries, 120 timezones, 24 terrain types

### 3. 🎮 ADVENTURE Commands

RPG system for interactive storytelling and missions.

| Command | Description | Example |
|:--------|:------------|:--------|
| `XP (+/-amount)` | Gain/lose experience | `XP (+50)` |
| `HP (+/-amount)` | Modify health | `HP (-10)` |
| `ITEM (item_id)` | Add to inventory | `ITEM (sword)` |
| `FLAG (event)` | Set story flag | `FLAG (met_wizard)` |
| `ROLL (dice)` | Roll dice | `ROLL (1d20)` |
| `CHOICE (text)` | Present options | `CHOICE ('Which path?')` |
| `LABEL (name)` | Define jump point | `LABEL (FOREST)` |
| `BRANCH (label)` | Jump to label | `BRANCH (COMBAT)` |
| `END` | Terminate adventure | `END` |

**System Variables:** `$SPRITE-NAME`, `$SPRITE-HP`, `$SPRITE-LEVEL`, `$SPRITE-XP`

### 4. 🎨 GRAPHICS Commands

Create diagrams, panels, and ASCII art.

| Command | Description | Example |
|:--------|:------------|:--------|
| `PANEL CREATE (n) (w) (h) (t)` | Create display panel | `PANEL CREATE (map) (80) (40) (4)` |
| `PANEL WRITE (n) (x) (y) (t)` | Write text at position | `PANEL WRITE (map) (10) (5) ('Hello')` |
| `PANEL BLOCK (n) (x) (y) (b)` | Place block graphic | `PANEL BLOCK (map) (0) (0) (full)` |
| `PANEL TERRAIN (n) (x) (y) (w) (h) (t)` | Fill with terrain | `PANEL TERRAIN (map) (0) (0) (40) (20) (forest)` |
| `PANEL SHOW (n)` | Display panel | `PANEL SHOW (map)` |
| `DRAW (type) (desc)` | Generate diagram | `DRAW (water) (filter)` |
| `SPRITE (name)` | ASCII character art | `SPRITE (hero)` |

**Panel Tiers:** 0-14 (Watch to 8K displays)

### 5. 💾 MEMORY Commands

4-tier knowledge storage system.

| Command | Description | Example |
|:--------|:------------|:--------|
| `MEMORY` | Access public tier | `MEMORY` |
| `PRIVATE` | Personal tier | `PRIVATE` |
| `SHARED` | Community tier | `SHARED` |
| `COMMUNITY` | Global tier | `COMMUNITY` |

**Tiers:**
- **Tier 1 (Public)**: General knowledge, read-only
- **Tier 2 (Private)**: Personal notes, full access
- **Tier 3 (Shared)**: Team collaboration
- **Tier 4 (Community)**: Global contributions

### 6. 📁 FILE Commands

File system operations.

| Command | Description | Example |
|:--------|:------------|:--------|
| `NEW (file)` | Create new file | `NEW (script.upy)` |
| `DELETE (file)` | Delete file (soft) | `DELETE (old.txt)` |
| `COPY (src) (dst)` | Copy file | `COPY (a.txt) (b.txt)` |
| `MOVE (src) (dst)` | Move/rename file | `MOVE (old.txt) (new.txt)` |
| `SHOW (file)` | Display contents | `SHOW (config.json)` |
| `EDIT (file)` | Open in editor | `EDIT (script.upy)` |
| `RUN (file)` | Execute script | `RUN (adventure.upy)` |

**Note:** DELETE uses soft-delete with 7-day recovery window (`.archive/deleted/`)

### 7. ⚙️ SYSTEM Commands

System settings, maintenance, and diagnostics.

| Command | Description | Example |
|:--------|:------------|:--------|
| `STATUS` | System status | `STATUS` |
| `CLEAN` | Remove temp files | `CLEAN` |
| `CLEAN --scan` | Archive health metrics | `CLEAN --scan` |
| `BACKUP (file)` | Create backup | `BACKUP (config.json)` |
| `UNDO (file)` | Revert to previous | `UNDO (script.upy)` |
| `REDO (file)` | Re-apply changes | `REDO (script.upy)` |
| `REPAIR` | Diagnose issues | `REPAIR` |
| `REPAIR RECOVER (f)` | Restore deleted file | `REPAIR RECOVER (data.txt)` |
| `SETTINGS` | View/edit settings | `SETTINGS` |
| `DEV MODE` | Toggle dev mode | `DEV MODE` |

**Archive System:** Universal `.archive/` folders for version history and backups

### 8. 🌐 SERVER Commands

Web-based extension servers.

| Command | Description | Example |
|:--------|:------------|:--------|
| `POKE START (name)` | Start server | `POKE START (dashboard)` |
| `POKE STOP (name)` | Stop server | `POKE STOP (terminal)` |
| `POKE STATUS (name)` | Check server health | `POKE STATUS` |
| `POKE RESTART (name)` | Restart server | `POKE RESTART (typo)` |
| `POKE LIST` | List available servers | `POKE LIST` |
| `POKE HEALTH` | System-wide health | `POKE HEALTH` |

**Available Servers:**
- `dashboard` - NES-style dashboard (8887)
- `terminal` - C64 PETSCII terminal (8890)
- `teletext` - BBC Teletext viewer (9002)
- `markdown` - Knowledge viewer (9000)
- `character` - Pixel art editor (8891)
- `typo` - Web markdown editor (5173)

### 9. 🤖 ASSISTANT Commands

AI-powered content generation and analysis (requires Gemini API key).

| Command | Description | Example |
|:--------|:------------|:--------|
| `GENERATE guide (topic)` | Generate survival guide | `GENERATE guide (water filter)` |
| `GENERATE diagram (desc)` | Create diagram | `GENERATE diagram (fire triangle)` |
| `ASK (question)` | Ask AI assistant | `ASK (how to purify water)` |
| `ANALYZE (file)` | Analyze content | `ANALYZE (guide.md)` |
| `EXPLAIN (topic)` | Get explanation | `EXPLAIN (friction fire)` |

**Note:** Works offline without API key (limited functionality)

### 10. 🔧 WORKFLOW Commands

Automation, missions, and task management.

| Command | Description | Example |
|:--------|:------------|:--------|
| `WORKFLOW (script)` | Run workflow | `WORKFLOW (setup.upy)` |
| `MISSION (name)` | Start mission | `MISSION (water_quest)` |
| `MISSION STATUS` | Check progress | `MISSION STATUS` |
| `MISSION COMPLETE` | Mark complete | `MISSION COMPLETE` |
| `CHECKPOINT` | Save state | `CHECKPOINT` |
| `CHECKPOINT LOAD (id)` | Restore state | `CHECKPOINT LOAD (1)` |

**Workflow Files:** `.upy` scripts in `memory/workflows/`

---

## Script Files (.upy)

uPY adventure and workflow scripts.

### File Structure

```upy
#!/usr/bin/env udos
# Adventure Title
# Description of what this script does

# Initialization
SET {$SPRITE-NAME|'Hero'}
SET {$SPRITE-HP|100}
SET {$SPRITE-LEVEL|1}

# Story content
PRINT ('Welcome to the adventure, {$SPRITE-NAME}!')
PRINT ()

# Choices and branching
CHOICE ('Which path?')
  OPTION ('Forest') → FOREST
  OPTION ('Cave') → CAVE

LABEL (FOREST)
PRINT ('You enter the forest...')
ROLL (1d20) → {$perception}

# Short form conditional
[IF {$perception} >= 15: PRINT ('You found treasure!') | XP (+50)]

# Medium form conditional
[IF {$perception} < 15 THEN: PRINT ('Nothing here.') ELSE: PRINT ('Keep searching...')]
END

LABEL (CAVE)
PRINT ('You enter the dark cave...')

# Long form conditional
IF {$SPRITE-HP} > 50
  PRINT ('You feel confident')
  HP (-10)
ELSE
  PRINT ('Too risky!')
  BRANCH (FOREST)
END IF
END
```

### Metadata Comments

Use comments for script metadata:

```upy
#!/usr/bin/env udos
# Title: Water Quest
# Author: uDOS
# Version: 1.0.0
# Description: Learn water purification through interactive adventure
# Category: water
# Difficulty: beginner
# Duration: 15 minutes
```

### Common Patterns

**Character Setup:**
```upy
SET {$SPRITE-NAME|'Survivor'}
SET {$SPRITE-HP|100}
SET {$SPRITE-HP-MAX|100}
SET {$SPRITE-LEVEL|1}
SET {$SPRITE-XP|0}
SET {$SPRITE-LOCATION|'AA340'}  # Sydney grid tile
```

**Skill Checks:**
```upy
# Short form
ROLL (1d20) → {$skill_check}
[IF {$skill_check} >= 15: PRINT ('Success!') | XP (+30)]
[IF {$skill_check} < 15: PRINT ('Failed!') | HP (-10)]

# Medium form (inline)
[IF {$skill_check} >= 15 THEN: PRINT ('Success!') | XP (+30) ELSE: PRINT ('Failed!') | HP (-10)]

# Long form (complex logic)
ROLL (1d20) → {$skill_check}
IF {$skill_check} >= 18
  PRINT ('Critical success!')
  XP (+50)
  ITEM (rare_loot)
ELSE IF {$skill_check} >= 15
  PRINT ('Success!')
  XP (+30)
ELSE IF {$skill_check} >= 10
  PRINT ('Partial success')
  XP (+10)
ELSE
  PRINT ('Failed!')
  HP (-10)
END IF
```

**Inventory Management:**
```upy
ITEM (water_bottle)
ITEM (first_aid_kit)
ITEM (compass)

# Shop system with conditionals
[IF {$gold} >= 100 THEN: ITEM (sword) | SET {$gold|{$gold} - 100} ELSE: PRINT ('Not enough gold!')]

# Ternary style
[{$gold} >= 50 ? ITEM (potion) : PRINT ('Need 50 gold')]
```

**Progress Tracking:**
```upy
FLAG (started_quest)
FLAG (found_water_source)
FLAG (purified_water)
FLAG (quest_complete)
```

---

## System Variables

Built-in variables (always use $ prefix).

### Character System

```upy
{$SPRITE-NAME}          # Character name
{$SPRITE-HP}            # Current health
{$SPRITE-HP-MAX}        # Maximum health
{$SPRITE-LEVEL}         # Character level
{$SPRITE-XP}            # Experience points
{$SPRITE-GOLD}          # Currency
{$SPRITE-LOCATION}      # Current TILE code
{$SPRITE-INVENTORY}     # Items array
```

### Mission System

```upy
{$MISSION.ID}           # Mission identifier
{$MISSION.NAME}         # Mission title
{$MISSION.STATUS}       # DRAFT|ACTIVE|PAUSED|COMPLETED|FAILED
{$MISSION.PROGRESS}     # Progress string (e.g., "45/55")
{$MISSION.START_TIME}   # ISO timestamp
{$MISSION.OBJECTIVE}    # Mission goal
```

### Workflow System

```upy
{$WORKFLOW.NAME}        # Current workflow script
{$WORKFLOW.PHASE}       # INIT|SETUP|EXECUTE|MONITOR|COMPLETE
{$WORKFLOW.ITERATION}   # Loop iteration count
{$WORKFLOW.ERRORS}      # Error count
{$WORKFLOW.ELAPSED_TIME} # Seconds since start
```

### Checkpoint System

```upy
{$CHECKPOINT.ID}        # Checkpoint identifier
{$CHECKPOINT.TIMESTAMP} # When saved
{$CHECKPOINT.DATA}      # Serialized state
{$CHECKPOINT.PREVIOUS}  # Previous checkpoint (linked list)
{$CHECKPOINT.NEXT}      # Next checkpoint
```

### Environment

```upy
{$USER}                 # Current username
{$HOME}                 # Home directory
{$DATE}                 # Current date (YYYY-MM-DD)
{$TIME}                 # Current time (HH:MM:SS)
{$WORKSPACE}            # Workspace root path
{$THEME}                # Active theme name
```

---

## Best Practices

### 1. Clear Variable Names

```upy
# Good
SET {$player_health|100}
SET {$quest_status|'active'}
SET {$water_sources_found|3}

# Bad
SET {$h|100}
SET {$s|'active'}
SET {$x|3}
```

### 2. Use Comments

```upy
# Check health before combat
[IF {$SPRITE-HP} < 30: PRINT ('⚠️  Low health!')]
[IF {$SPRITE-HP} < 30: HP (+20)]  # Emergency healing

# Award experience for discovery
XP (+50)
```

### 3. Consistent Formatting

```upy
# Good: Consistent spacing and structure
SET {$name|'Hero'}
SET {$hp|100}
SET {$level|1}

PRINT ('Character: {$name}')
PRINT ('HP: {$hp}')
PRINT ('Level: {$level}')

# Bad: Inconsistent
SET{$name|'Hero'}
SET {$hp|100}
  SET {$level|1}
PRINT ('Character: {$name}')
   PRINT('HP: {$hp}')
```

### 4. Error Handling

```upy
# Short form - quick checks
[IF {$SPRITE-HP} <= 0: PRINT ('Game Over!') | END]

# Medium form - branching
[IF {$SPRITE-HP} <= 0 THEN: PRINT ('Game Over!') | END ELSE: PRINT ('Still alive!')]

# Long form - complex validation
ROLL (1d20) → {$attack}
PRINT ('Attack roll: {$attack}')

IF {$attack} >= 18
  PRINT ('Critical hit!')
  SET {$damage|{$damage} * 2}
ELSE IF {$attack} >= 15
  PRINT ('Hit!')
ELSE IF {$attack} >= 10
  PRINT ('Glancing blow')
  SET {$damage|{$damage} / 2}
ELSE
  PRINT ('Miss!')
  SET {$damage|0}
END IF
```

### 5. Modular Design

```upy
# Break scripts into labeled sections
LABEL (INIT)
# Initialization code
BRANCH (START)

LABEL (START)
# Main story
BRANCH (CHOICE1)

LABEL (CHOICE1)
# First decision point
CHOICE ('What do you do?')
  OPTION ('Fight') → COMBAT
  OPTION ('Flee') → ESCAPE
```

---

## Examples

### Simple Adventure Script

```upy
#!/usr/bin/env udos
# Quick survival scenario

SET {$SPRITE-NAME|'Survivor'}
SET {$SPRITE-HP|80}

PRINT ('You wake up in the wilderness...')
PRINT ('HP: {$SPRITE-HP}/100')
PRINT ()

CHOICE ('Your priority?')
  OPTION ('Find water') → WATER
  OPTION ('Build shelter') → SHELTER
  OPTION ('Make fire') → FIRE

LABEL (WATER)
PRINT ('You search for water...')
ROLL (1d20) → {$search}

# Medium form with THEN/ELSE
[IF {$search} >= 12 THEN: PRINT ('Found a stream!') | HP (+15) | XP (+40) ELSE: PRINT ('No water found.') | HP (-5)]
END

LABEL (SHELTER)
PRINT ('You build a lean-to shelter...')
XP (+30)
FLAG (shelter_built)
PRINT ('You feel safer.')
END

LABEL (FIRE)
PRINT ('You attempt to start a fire...')
ROLL (1d20) → {$fire_check}

# Long form with ELSE IF
IF {$fire_check} >= 18
  PRINT ('Perfect fire! Warm and bright.')
  XP (+75)
  HP (+10)
ELSE IF {$fire_check} >= 14
  PRINT ('Success! Fire lit.')
  XP (+50)
ELSE IF {$fire_check} >= 10
  PRINT ('Smoking... keep trying.')
  XP (+10)
ELSE
  PRINT ('Failed. No fire.')
END IF
END
```

### Workflow Script

```upy
#!/usr/bin/env udos
# Daily maintenance workflow

PRINT ('Starting daily maintenance...')
PRINT ()

# Check system health
STATUS

# Clean temporary files
CLEAN

# Create backup
SET {$backup_date|{$DATE}}
BACKUP (memory/user/config.json)

# Scan archives
CLEAN --scan

# Report
PRINT ()
PRINT ('Maintenance complete!')
PRINT ('Backup: backup_{$backup_date}')
```

### Interactive Learning Script

```upy
#!/usr/bin/env udos
# Water purification tutorial

SET {$knowledge_level|0}

# Define helper function (short form)
@award_xp({$amount}): XP (+{$amount}) | PRINT ('Earned {$amount} XP!')

# Define completion checker (long form)
FUNCTION check_completion({$current}|{$total})
  SET {$percent|({$current} / {$total}) * 100}
  PRINT ('Progress: {$current}/{$total} ({$percent}%)')
  [IF {$current} >= {$total}: RETURN true ELSE: RETURN false]
END FUNCTION

PRINT ('===========================================')
PRINT ('  Water Purification Tutorial')
PRINT ('===========================================')
PRINT ()

# Step 1: Boiling
PRINT ('Step 1: Boiling Water')
GUIDE (water/boiling) --interactive
SET {$knowledge_level|{$knowledge_level} + 1}
@award_xp(25)

# Step 2: Filtration
PRINT ()
PRINT ('Step 2: Water Filtration')
GUIDE (water/filtration) --interactive
SET {$knowledge_level|{$knowledge_level} + 1}
@award_xp(25)

# Step 3: Chemical Treatment
PRINT ()
PRINT ('Step 3: Chemical Treatment')
GUIDE (water/chemical) --interactive
SET {$knowledge_level|{$knowledge_level} + 1}
@award_xp(25)

# Completion
PRINT ()
SET {$complete|@check_completion({$knowledge_level}|3)}

IF {$complete}
  PRINT ('===========================================')
  PRINT ('  Tutorial Complete!')
  PRINT ('===========================================')
  PRINT ('Total XP Gained: 75')
  FLAG (water_tutorial_complete)
  ITEM (water_expert_badge)
ELSE
  PRINT ('Tutorial incomplete. Review lessons.')
END IF
```

---

## See Also

- **[uPY-Syntax-v2.md](uPY-Syntax-v2.md)** - Complete v2.0 syntax reference
- **[uPY-Syntax-Rules.md](uPY-Syntax-Rules.md)** - Quick 3-rule guide
- **[Adventure-Scripting.md](Adventure-Scripting.md)** - Interactive storytelling
- **[Command-Reference.md](Command-Reference.md)** - All commands
- **[Function-Programming-Guide.md](Function-Programming-Guide.md)** - Advanced functions

---

**Version:** uCODE v2.0 / uPY v2.0
**Last Updated:** December 5, 2025
**Maintainer:** @fredporter
**License:** See LICENSE.txt
