# uCODE Quick Reference (v1.2.24)

**Version:** v1.2.24 (Python-First Architecture)  
**Last Updated:** December 13, 2025

---

## Syntax Rules

### Command Format

```
COMMAND[arg1|arg2|arg3]     # With arguments
COMMAND                      # Without arguments (no empty brackets)
```

### Tag Notation

Use **asterisk (*)** for tags, not underscores:

```
✅ CORRECT:
CHECKPOINT*SAVE[name]
MISSION*START[id]
HEAL*SPRITE[id|amount|item]
STATUS*HEALTH

❌ WRONG:
CHECKPOINT_SAVE[name]       # Don't use underscores
MISSION_START[id]
HEAL_SPRITE[id|amount|item]
STATUS_HEALTH
```

### Variable Syntax

Use **dollar sign ($)** prefix for variables:

```
✅ CORRECT:
GET[$water-level]
SET[$player-hp|100]
IF GET[$food-supply] < 30

❌ WRONG:
GET[water-level]            # Missing $ prefix
SET[player-hp|100]
IF GET[food-supply] < 30
```

### Empty Brackets

**Don't use empty brackets** when no arguments needed:

```
✅ CORRECT:
STATUS
INVENTORY
TREE
LEVEL*UP
MISSION*STATUS

❌ WRONG:
STATUS[]
INVENTORY[]
TREE[]
LEVEL*UP[]
MISSION*STATUS[]
```

---

## Core Commands

### Knowledge

```
GUIDE[topic|complexity]              # Get survival guide
GUIDE[water/purification|detailed]
GUIDE[fire/bow-drill|simple]
GUIDE[medical/wounds|technical]
```

### Output

```
PRINT[message]                       # Display message
PRINT[Hello, world!]
PRINT[Water: 50L|Food: 30 days]     # Columns (pipe = column separator)

# Pipe creates columns, not new lines
PRINT[Col1|Col2|Col3]                # Three columns side-by-side
PRINT[Name: Alice|Age: 25|HP: 100]  # Data in columns

# Special characters (use emoji codes)
PRINT[Score: :sb:100:eb:]            # [100]
PRINT[Price: :dollar:50]             # $50
PRINT[Use :pipe: separator]          # To display actual | character
```

### Variables

```
GET[$variable]                       # Read variable
SET[$variable|value]                 # Write variable

GET[$player-hp]
SET[$water-level|50]
SET[$camp-location|AA340]
```

### Checkpoints

```
CHECKPOINT*SAVE[name]                # Save progress
CHECKPOINT*LOAD[name]                # Load progress

CHECKPOINT*SAVE[camp-established]
CHECKPOINT*LOAD[before-storm]
```

### Missions

```
MISSION*START[id]                    # Start mission
MISSION*COMPLETE[id]                 # Complete mission
MISSION*STATUS                       # Check status

MISSION*START[establish-camp]
MISSION*COMPLETE[find-water]
MISSION*STATUS
```

### Sprites

```
HEAL*SPRITE[id|amount|item]          # Heal sprite

HEAL*SPRITE[player|20|bandage]
HEAL*SPRITE[companion|50|medkit]
```

### Experience

```
XP[amount]                           # Gain experience
LEVEL*UP                             # Level up

XP[+100]
XP[+500]
LEVEL*UP
```

### Inventory

```
ITEM[name]                           # Add item
INVENTORY                            # Show items

ITEM[axe]
ITEM[water-filter]
INVENTORY
```

### System

```
STATUS                               # Basic status
STATUS*HEALTH                        # Detailed health
TREE                                 # Show all files
TREE[path]                           # Show specific path
CONFIG                               # Show configuration
CONFIG[setting|value]                # Set configuration
VIEWPORT                             # Show viewport settings
VIEWPORT[width|height]               # Set viewport size

STATUS
STATUS*HEALTH
TREE[knowledge/water]
CONFIG[theme|galaxy]
VIEWPORT[80|24]
```

---

## Python Integration

### Basic Python (UPPERCASE in uCODE)

```python
# Beginner level - UPPERCASE for consistency
PRINT[Hello, world!]
IF GET[$player-hp] < 50 THEN HEAL*SPRITE[player|30|medkit]

FUNCTION[@daily*check]
  PRINT[Checking resources...]
  GET[$water-level]
  GET[$food-supply]
END FUNCTION
```

### Intermediate Python (Mixed)

```python
# Mix UPPERCASE uCODE with lowercase Python
from udos_core import *

player_hp = get_var("player-hp", 100)

if player_hp < 50:
    HEAL*SPRITE("player", 30, "medkit")  # uCODE command
    print("Healed player")               # Python
```

### Advanced Python (Lowercase)

```python
# Pure Python with uCODE as imports
from udos_core import guide, heal_sprite, checkpoint_save

player_hp = 100

if player_hp < 50:
    heal_sprite("player", 30, "medkit")
    guide("medical/wounds", "detailed")
    checkpoint_save("emergency-heal")
```

---

## System Variables

### Mission

```
$MISSION.ID              # Mission identifier
$MISSION.NAME            # Mission name
$MISSION.STATUS          # DRAFT|ACTIVE|PAUSED|COMPLETED|FAILED
$MISSION.PROGRESS        # Progress (e.g., "3/5" or "60%")
$MISSION.START_TIME      # ISO timestamp
$MISSION.OBJECTIVE       # Mission goal
```

### Workflow

```
$WORKFLOW.NAME           # Workflow name
$WORKFLOW.PHASE          # INIT|SETUP|EXECUTE|MONITOR|COMPLETE
$WORKFLOW.ITERATION      # Loop iteration
$WORKFLOW.ERRORS         # Error count
$WORKFLOW.ELAPSED_TIME   # Seconds elapsed
```

### Sprite

```
$SPRITE.HP               # Health points
$SPRITE.MAX_HP           # Maximum health
$SPRITE.LEVEL            # Current level
$SPRITE.XP               # Experience points
$SPRITE.LOCATION         # Grid position
```

### System

```
$SYSTEM.VERSION          # uDOS version
$SYSTEM.MEMORY_USED      # Memory usage %
$SYSTEM.FILE_COUNT       # File count
$SYSTEM.UPTIME           # Uptime seconds
```

### Config & Viewport

```
$CONFIG.THEME            # Current theme
$CONFIG.LANGUAGE         # Language setting
$CONFIG.TIMEZONE         # Timezone
$CONFIG.LOCATION         # Current location (TILE code)
$VIEWPORT.WIDTH          # Viewport width (columns)
$VIEWPORT.HEIGHT         # Viewport height (rows)
$VIEWPORT.MODE           # Display mode (terminal|web|mobile)
```

---

## Special Characters (Emoji Codes)

### In Output (PRINT commands)

```
:sb:         → [          # Square bracket open
:eb:         → ]          # Square bracket close
:pipe:       → |          # Pipe
:dollar:     → $          # Dollar sign
:hash:       → #          # Hash
:at:         → @          # At sign
:star:       → *          # Asterisk
:underscore: → _          # Underscore
:caret:      → ^          # Caret

# Examples:
PRINT[Array: :sb:1, 2, 3:eb:]        # Array: [1, 2, 3]
PRINT[Email: admin:at:udos.com]      # Email: admin@udos.com
PRINT[Tag: :hash:important]          # Tag: #important
PRINT[Price: :dollar:50]             # Price: $50
```

---

## Common Patterns

### Health Check

```python
# Get health
hp = GET[$player-hp]

# Heal if needed
IF hp < 50 THEN HEAL*SPRITE[player|30|medkit]

# Save checkpoint
CHECKPOINT*SAVE[health-check-complete]
```

### Resource Monitor

```python
# Check resources
water = GET[$water-level]
food = GET[$food-supply]

# Display in columns (pipe = column separator)
PRINT[Water: {water}L | Food: {food} days | Status: OK]

# Alert if low
IF water < 30 THEN PRINT[⚠️ Water low!]
IF food < 20 THEN PRINT[⚠️ Food low!]

# Get guides
IF water < 30 THEN GUIDE[water/collection|detailed]
IF food < 20 THEN GUIDE[food/foraging|detailed]
```

### Mission Workflow

```python
# Start mission
MISSION*START[establish-camp]

# Execute steps with checkpoints
PRINT[Phase 1: Location]
SET[$camp-location|AA340]
CHECKPOINT*SAVE[location-selected]
XP[+50]

PRINT[Phase 2: Shelter]
GUIDE[shelter/lean-to|detailed]
CHECKPOINT*SAVE[shelter-built]
XP[+100]

# Complete mission
MISSION*COMPLETE[establish-camp]
XP[+500]
LEVEL*UP
```

---

## Naming Conventions

### Variables

```
✅ CORRECT:
$player-hp              # Use dashes
$water-level
$camp-location
$food-supply-1

❌ WRONG:
$player_hp              # Don't use underscores
$water level            # Don't use spaces
$camp#location          # Don't use special chars
```

### Checkpoints

```
✅ CORRECT:
camp-established        # Use dashes, lowercase
water-source-found
shelter-built
before-storm

❌ WRONG:
Camp_Established        # Don't use underscores or capital
water source found      # Don't use spaces
checkpoint1             # Be descriptive
```

### Missions

```
✅ CORRECT:
establish-camp          # Use dashes, lowercase
find-water
build-shelter

❌ WRONG:
Establish_Camp          # Don't use underscores or capital
find water              # Don't use spaces
mission1                # Be descriptive
```

---

## Error Prevention

### Mistake 1: Wrong Separator

```
❌ WRONG:
PRINT[Water, Food, Shelter]        # Commas
GUIDE[water/purification, detailed]

✅ CORRECT:
PRINT[Water|Food|Shelter]          # Pipes
GUIDE[water/purification|detailed]
```

### Mistake 2: Underscores in Tags

```
❌ WRONG:
CHECKPOINT_SAVE[name]
MISSION_START[id]
LEVEL_UP

✅ CORRECT:
CHECKPOINT*SAVE[name]              # Asterisks
MISSION*START[id]
LEVEL*UP
```

### Mistake 3: Missing $ on Variables

```
❌ WRONG:
GET[water-level]
SET[player-hp|100]

✅ CORRECT:
GET[$water-level]                  # $ prefix
SET[$player-hp|100]
```

### Mistake 4: Empty Brackets

```
❌ WRONG:
STATUS[]
INVENTORY[]
TREE[]

✅ CORRECT:
STATUS                             # No brackets
INVENTORY
TREE
```

### Mistake 5: Quotes in Arguments

```
❌ WRONG (usually):
GUIDE["water/purification"|"detailed"]
PRINT["Hello, world!"]

✅ CORRECT (usually):
GUIDE[water/purification|detailed]  # No quotes
PRINT[Hello, world!]

✅ ALSO CORRECT (in Python):
guide("water/purification", "detailed")  # Python style
print("Hello, world!")
```

---

## Learning Path

### 1. Beginner → [Beginner Commands](uCODE-Beginner-Commands.md)

- **Focus:** UPPERCASE uCODE commands only
- **Syntax:** `COMMAND[args]`, asterisks for tags, $ for variables
- **Examples:** GUIDE, PRINT, CHECKPOINT*SAVE, GET, SET
- **Goal:** Learn basic survival commands without programming

### 2. Intermediate → [Python-First Guide](uCODE-Python-First-Guide.md)

- **Focus:** Mixing uCODE with Python
- **Syntax:** UPPERCASE uCODE + lowercase Python
- **Examples:** Loops, conditionals, functions with uCODE commands
- **Goal:** Add programming logic to uCODE scripts

### 3. Advanced → [Python Advanced](uCODE-Python-Advanced.md)

- **Focus:** Full Python programming
- **Syntax:** Lowercase Python with uCODE as imports
- **Examples:** Classes, decorators, async, full Python ecosystem
- **Goal:** Master Python with uCODE integration

---

## Quick Command Lookup

```
# Knowledge & Help
GUIDE[topic|level]
HELP
STATUS
STATUS*HEALTH
TREE
TREE[path]
CONFIG
CONFIG[setting|value]
VIEWPORT
VIEWPORT[width|height]

# Output
PRINT[message|message...]

# Player
HEAL*SPRITE[id|amount|item]
XP[+amount]
LEVEL*UP

# Inventory
ITEM[name]
INVENTORY

# Variables
GET[$name]
SET[$name|value]

# Checkpoints
CHECKPOINT*SAVE[name]
CHECKPOINT*LOAD[name]

# Missions
MISSION*START[id]
MISSION*COMPLETE[id]
MISSION*STATUS

# Python Basics (UPPERCASE in uCODE)
PRINT[message]
IF condition THEN action
FUNCTION[@name*tag]
```

---

## File Locations

```
memory/ucode/scripts/       # User scripts (.upy)
memory/ucode/examples/      # Example scripts
memory/ucode/stdlib/        # Standard library
memory/ucode/tests/         # Test scripts
memory/workflows/missions/  # Mission scripts

knowledge/water/            # Water guides
knowledge/fire/             # Fire guides
knowledge/shelter/          # Shelter guides
knowledge/food/             # Food guides
knowledge/medical/          # Medical guides
knowledge/navigation/       # Navigation guides
```

---

## Need Help?

- **Beginner Guide:** [uCODE Beginner Commands](uCODE-Beginner-Commands.md)
- **Intermediate Guide:** [uCODE Python-First Guide](uCODE-Python-First-Guide.md)
- **Advanced Guide:** [uCODE Python Advanced](uCODE-Python-Advanced.md)
- **In uDOS:** Type `HELP` or `STATUS*HEALTH`
- **Examples:** Browse `memory/ucode/examples/`

---

**Version:** v1.2.24  
**Type:** Quick Reference  
**Updated:** December 13, 2025
