# uCODE Python-First Guide (v1.2.24+)

**Version:** v1.2.24 (Python-First Architecture)  
**Status:** Production Ready  
**Last Updated:** December 13, 2025

---

## Overview

As of **v1.2.24**, uCODE uses a **Python-first architecture**. This means:

1. **Write valid Python** - Your scripts are real Python code
2. **Visual .upy rendering** - Smart editor displays user-friendly syntax
3. **Native performance** - 100x faster than old parser (925,078 ops/sec)
4. **Full Python ecosystem** - Import any package, use debuggers, AI tools

### Architecture Flow

```
.upy file on disk → Smart Editor → Python execution → Native speed
      ↓                   ↓              ↓
  Standard format   Visual render   Real Python
```

---

## Two Command Sets

### 1. uCODE Commands (Beginner-Friendly)

**Purpose:** High-level operations for survival, mapping, content generation

**Format:** `COMMAND[ arg1 | arg2 | arg3 ]`

**Syntax Rules:**
- **Tags:** Use asterisk (`*`) not underscores: `CHECKPOINT*SAVE` not `CHECKPOINT_SAVE`
- **Variables:** Use dollar prefix (`$`): `$water-level` not `water-level`
- **No empty brackets:** `STATUS` not `STATUS[]` when no arguments needed

**Examples:**
```python
from udos_core import *

# Knowledge access
GUIDE[ water/purification | detailed ]

# Sprite healing  
HEAL*SPRITE[ player | 20 | bandage ]

# Checkpoint management
CHECKPOINT*SAVE[ camp-established ]

# Variable access
GET[ $water-level ]
SET[ $water-level | 50 ]

# Tag rendering (visual emphasis)
CLONE*DEV  # Asterisk shows tag relationship
MISSION*START[find-water]  # Tag separates command components
```

**System variables:**
- `$MISSION.STATUS` - Current mission state
- `$SPRITE.HP` - Sprite health
- `$WORKFLOW.PHASE` - Workflow execution phase

**Emoji escapes for special chars in output:**
- `:pipe:` → | (pipe character)
- `:dollar:` → $ (dollar sign)
- `:sb:` / `:eb:` → [ / ] (square brackets)

---

### 2. Python Commands (Advanced)

**Purpose:** Full Python programming capabilities

**Format:** Standard Python syntax (lowercase)

**Examples:**
```python
# Variables and data structures
player_hp = 100
inventory = ["axe", "rope", "water"]
location = {"x": 10, "y": 20, "layer": 100}

# Control flow
if player_hp < 50:
    HEAL*SPRITE[player|30|bandage]
    print("Emergency healing applied")

# Functions
def check_resources(water, food):
    """Check if resources are adequate."""
    total = water + food
    return total > 50

# Loops
for item in inventory:
    print(f"Checking {item}...")

# List comprehensions
low_resources = [r for r in resources if r < 20]

# Import any Python package
import json
import datetime
from pathlib import Path
```

---

## Understanding the Transition

### UPPERCASE in uCODE Context (Beginner Level)

When learning uCODE, basic Python commands are shown in UPPERCASE for consistency:

```python
# Beginner syntax - UPPERCASE for visual consistency with uCODE
PRINT[ Hello, world! ]
IF GET[ $player-hp ] < 50 THEN HEAL*SPRITE[ player | 30 | medkit ]
FUNCTION[ @daily*check ]
```

These are actually Python commands (`print`, `if/then`, `def`) but shown in UPPERCASE to match uCODE command style.

### Lowercase Python (Intermediate → Advanced)

As you progress, you transition to standard lowercase Python:

```python
# Intermediate: Mix UPPERCASE uCODE with lowercase Python
from udos_core import *

# Python variables (lowercase)
player_hp = get_var("player-hp", 100)
water_level = 50

# Python control flow (lowercase)
if player_hp < 50:
    # uCODE commands (UPPERCASE)
    HEAL*SPRITE[ player | 30 | medkit ]
    GUIDE[ medical/wounds | detailed ]

# Python function (lowercase)
def check_status():
    return player_hp, water_level
```

### Pure Python (Advanced)

Eventually, you'll write standard Python with uCODE commands as function calls:

```python
# Advanced: Pure Python with uCODE as imported functions
from udos_core import GUIDE, HEAL_SPRITE, CHECKPOINT_SAVE

player_hp = 100
inventory = []

def daily_check():
    """Run daily survival checks."""
    if player_hp < 50:
        HEAL_SPRITE("player", 30, "medkit")
        GUIDE("medical/wounds", "detailed")
    
    CHECKPOINT_SAVE("daily-check-complete")
    return True
```

**See [Python Advanced Guide](uCODE-Python-Advanced.md) for complete lowercase Python features.**

---

## Writing Scripts

### File Format: `.upy` (Standard)

All scripts are saved as `.upy` files:

```
memory/ucode/scripts/water_check.upy
memory/ucode/examples/demo.upy
memory/workflows/missions/establish_camp.upy
```

### Basic Structure

```python
# water_check.upy - Monitor water resources
from udos_core import *

# Python variables
water_level = get_var("water-level", 100)
min_threshold = 30

# uCODE commands
print(f"Current water level: {water_level}")

# Python control flow
if water_level < min_threshold:
    print("⚠️ Low water warning!")
    GUIDE("water/collection", "quick")
else:
    print("Water level OK")

# Update user variable
set_var("water-level", water_level)
```

### Smart Editor Rendering

The smart editor displays this as user-friendly uCODE:

```upy
# water_check.upy - Monitor water resources
from udos_core import *

# Python variables (shown with dashes)
water-level = get_var[ water-level | 100 ]
min-threshold = 30

# uCODE commands (brackets, pipes visible)
PRINT[ Current water level: {water-level} ]

# Python control flow  
if water-level < min-threshold:
    PRINT[ :warning: Low water warning! ]
    GUIDE[ water/collection | quick ]
else:
    PRINT[ Water level OK ]

# Update user variable
set_var[ water-level | water-level ]
```

**Key Visual Transformations:**
- `_` → `-` (underscores become dashes in display)
- `()` → `[]` (parentheses become brackets for uCODE commands)
- `,` → `|` (commas become pipes in command arguments)

**Note:** These are visual only - the actual Python code remains unchanged.

---

## Command Reference

### uCODE Commands (from udos_core)

#### Knowledge Access

```python
GUIDE[ category | complexity ]
# Examples:
GUIDE[ water/purification | detailed ]
GUIDE[ fire/friction | simple ]
GUIDE[ medical/wounds | technical ]
```

#### Sprite Management

```python
HEAL*SPRITE[ sprite_id | amount | item ]
# Examples:
HEAL*SPRITE[ player | 20 | bandage ]
HEAL*SPRITE[ companion | 50 | medkit ]
```

#### Checkpoint System

```python
CHECKPOINT*SAVE[ checkpoint_id ]
CHECKPOINT*LOAD[ checkpoint_id ]
# Examples:
CHECKPOINT*SAVE[ camp-established ]
CHECKPOINT*LOAD[ before-storm ]
```

#### Variable Management

```python
GET[ $variable_name ]
SET[ $variable_name | value ]
# Examples:
GET[ $player-hp ]
SET[ $water-level | 50 ]
```

#### Mission System

```python
MISSION*START[ mission_id ]
MISSION*COMPLETE[ mission_id ]
MISSION*STATUS
# Examples:
MISSION*START[ establish-camp ]
MISSION*COMPLETE[ find-water ]
MISSION*STATUS
```

#### Inventory

```python
ITEM[ item_name ]
INVENTORY
# Examples:
ITEM[ axe ]
ITEM[ water-filter ]
INVENTORY
```

#### Experience

```python
XP[ amount ]
LEVEL*UP
# Examples:
XP[ +100 ]
LEVEL*UP
```

#### System Commands

```python
STATUS
STATUS*HEALTH
TREE
TREE[ path ]
# Examples:
STATUS
STATUS*HEALTH
TREE[ knowledge/water ]
```

---

## Practical Examples

### Example 1: Water Monitor Script

```python
# water_monitor.upy
from udos_core import *

# Get current water level
water_level = get_var("water-level", 100)
daily_consumption = 5

# Calculate days remaining
days_remaining = water_level / daily_consumption

# Display status
print(f"Water level: {water_level} liters")
print(f"Days remaining: {days_remaining:.1f}")

# Warning if low
if water_level < 30:
    print("⚠️ CRITICAL: Water running low!")
    GUIDE("water/collection", "detailed")  # Python function call
    CHECKPOINT*SAVE("low-water-alert")  # Python function call
elif water_level < 50:
    print("⚠️ WARNING: Water below 50 liters")
    GUIDE("water/storage", "simple")  # Python function call

# Update tracking
set_var("last-water-check", datetime.now().isoformat())
```

### Example 2: Health Check System

```python
# health_check.upy
from udos_core import *

def check_health(sprite_id):
    """Check and heal sprite if needed."""
    hp = get_var(f"{sprite_id}-hp", 100)
    max_hp = 100
    hp_percent = (hp / max_hp) * 100
    
    print(f"{sprite_id} HP: {hp}/{max_hp} ({hp_percent:.0f}%)")
    
    if hp < 30:
        print("  CRITICAL - Emergency healing!")
        HEAL*SPRITE(sprite_id, 50, "emergency-kit")  # Python function call
        GUIDE("medical/wounds", "detailed")  # Python function call
    elif hp < 60:
        print("  Low - Healing recommended")
        HEAL*SPRITE(sprite_id, 20, "bandage")  # Python function call
    else:
        print("  Healthy")
    
    return hp

# Check all sprites
check_health("player")
check_health("companion")

# Save checkpoint
CHECKPOINT*SAVE("health-check-complete")  # Python function call
```

### Example 3: Resource Inventory

```python
# inventory_check.upy
from udos_core import *
import json

# Define resources
resources = {
    "water": get_var("water-level", 100),
    "food": get_var("food-supply", 50),
    "wood": get_var("wood-count", 30),
    "tools": ["axe", "knife", "rope"]
}

# Display inventory
print("=== Resource Inventory ===")
for name, value in resources.items():
    if isinstance(value, list):
        print(f"{name}: {len(value)} items")
        for item in value:
            print(f"  - {item}")
    else:
        print(f"{name}: {value}")
        
        # Check thresholds
        if value < 25:
            print(f"  ⚠️ {name} is running low!")
            if name == "water":
                GUIDE("water/collection", "simple")  # Python function call
            elif name == "food":
                GUIDE("food/foraging", "simple")  # Python function call

# Save inventory snapshot
set_var("inventory-snapshot", json.dumps(resources))
CHECKPOINT*SAVE("inventory-recorded")  # Python function call
```

### Example 4: Mission Workflow

```python
# establish_camp.upy - Complete camp setup mission
from udos_core import *

print("=== Establish Camp Mission ===")

# Start mission
MISSION*START("establish-camp")  # Python function call

# Phase 1: Find location
print("\nPhase 1: Location")
location = "AA340"  # Sydney grid
SET("$camp-location", location)  # Python function call
CHECKPOINT*SAVE("location-selected")  # Python function call
XP(+50)  # Python function call

# Phase 2: Build shelter
print("\nPhase 2: Shelter")
GUIDE("shelter/lean-to", "detailed")  # Python function call
ITEM("tarp")  # Python function call
ITEM("rope")  # Python function call
CHECKPOINT*SAVE("shelter-built")  # Python function call
XP(+100)  # Python function call

# Phase 3: Water source
print("\nPhase 3: Water")
GUIDE("water/collection", "simple")  # Python function call
SET("$water-level", 100)  # Python function call
CHECKPOINT*SAVE("water-secured")  # Python function call
XP(+50)  # Python function call

# Phase 4: Fire
print("\nPhase 4: Fire")
GUIDE("fire/bow-drill", "detailed")  # Python function call
ITEM("firestarter")  # Python function call
CHECKPOINT*SAVE("fire-started")  # Python function call
XP(+100)  # Python function call

# Complete mission
print("\n✅ Camp established!")
MISSION*COMPLETE("establish-camp")  # Python function call
XP(+500)  # Python function call
LEVEL*UP()  # Python function call
```

---

## System Variables

### Mission Variables
- `$MISSION.ID` - Current mission identifier
- `$MISSION.NAME` - Mission display name
- `$MISSION.STATUS` - DRAFT | ACTIVE | PAUSED | COMPLETED | FAILED
- `$MISSION.PROGRESS` - Progress indicator (e.g., "3/5" or "60%")
- `$MISSION.START_TIME` - ISO timestamp
- `$MISSION.OBJECTIVE` - Mission goal description

### Workflow Variables
- `$WORKFLOW.NAME` - Current workflow script name
- `$WORKFLOW.PHASE` - INIT | SETUP | EXECUTE | MONITOR | COMPLETE
- `$WORKFLOW.ITERATION` - Current loop iteration count
- `$WORKFLOW.ERRORS` - Error count
- `$WORKFLOW.ELAPSED_TIME` - Seconds since workflow start

### Sprite Variables
- `$SPRITE.HP` - Health points
- `$SPRITE.MAX_HP` - Maximum health
- `$SPRITE.LEVEL` - Current level
- `$SPRITE.XP` - Experience points
- `$SPRITE.LOCATION` - Grid position

### System Variables
- `$SYSTEM.VERSION` - uDOS version (e.g., "1.2.24")
- `$SYSTEM.MEMORY_USED` - Memory usage percentage
- `$SYSTEM.FILE_COUNT` - Total file count
- `$SYSTEM.UPTIME` - System uptime in seconds

---

## Debugging Tips

### 1. Print Variables

```python
# Check variable values
water_level = get_var("water-level", 100)
print(f"Debug: water_level = {water_level}")
```

### 2. Use Checkpoints

```python
# Save state for debugging
CHECKPOINT*SAVE("debug-point-1")  # Python function call
# ... test code ...
CHECKPOINT*LOAD("debug-point-1")  # Python function call - Restore if needed
```

### 3. Status Checks

```python
# Monitor system health
STATUS*HEALTH  # Python function call

# Check specific resources
print(GET("$player-hp"))  # Python function call
print(GET("$water-level"))  # Python function call
```

### 4. Mission Progress

```python
# Track mission state
MISSION*STATUS  # Python function call
print(GET("$MISSION.PROGRESS"))  # Python function call
```

---

## Performance Notes

### v1.2.24 Benchmarks

**Python-First Architecture:**
- **Speed:** 925,078 operations/second
- **Improvement:** 100x faster than v1.2.23 parser
- **Memory:** 45% reduction in runtime overhead
- **Startup:** Instant (no parsing phase)

**Why It's Fast:**
- Native Python execution (no interpretation layer)
- Direct function calls (no command string parsing)
- Compiled bytecode (standard .pyc optimization)
- Zero-overhead abstractions

**Comparison:**
```
v1.2.23 Parser:  9,250 ops/sec  (string → AST → execute)
v1.2.24 Python:  925,078 ops/sec  (direct Python execution)
                 ─────────────────
                 100x faster
```

---

## Migration from v1.2.23

### Old Parser Syntax (v1.2.23)

```
# Old .uscript format
PRINT["Hello, world!"]
IF {$hp} < 50 THEN:
  HEAL_SPRITE["player"|"30"|"medkit"]
END IF
```

### New Python Syntax (v1.2.24+)

```python
# New .upy format
from udos_core import *

print("Hello, world!")
hp = get_var("player-hp", 100)
if hp < 50:
    HEAL*SPRITE("player", 30, "medkit")
```

**Migration Tool:** Use `memory/ucode/tools/migrate_upy.py` to convert old scripts

```bash
python memory/ucode/tools/migrate_upy.py input.uscript output.upy
```

---

## Best Practices

### 1. Import udos_core

Always start scripts with:
```python
from udos_core import *
```

This provides all uCODE commands as Python functions.

### 2. Use Python Standard Library

Leverage Python's rich ecosystem:
```python
import json          # Data serialization
import datetime      # Timestamps
from pathlib import Path  # File operations
import math          # Calculations
```

### 3. Document Your Code

```python
# water_manager.upy - Advanced water resource management
"""
This script monitors water levels, predicts consumption,
and triggers alerts when resources run low.

Features:
- Daily consumption tracking
- Weather-based predictions
- Automatic guide lookup
- Emergency alerts
"""

from udos_core import *

def calculate_water_needs(days, people, climate):
    """Calculate water requirements.
    
    Args:
        days: Number of days to plan for
        people: Number of people
        climate: hot | temperate | cold
    
    Returns:
        Total liters needed
    """
    # Implementation...
```

### 4. Error Handling

```python
# Robust error handling
try:
    water_level = get_var("water-level")
    if water_level < 30:
        GUIDE("water/collection", "detailed")
except ValueError:
    print("Error: Invalid water level")
    set_var("water-level", 100)  # Reset to default
```

### 5. Modular Functions

```python
def heal_if_needed(sprite_id, threshold=50):
    """Heal sprite if below threshold."""
    hp = get_var(f"{sprite_id}-hp", 100)
    if hp < threshold:
        HEAL*SPRITE(sprite_id, 30, "medkit")
        return True
    return False

# Reuse across scripts
heal_if_needed("player")
heal_if_needed("companion", threshold=60)
```

---

## Next Steps

Once comfortable with Python-first uCODE:

1. **Learn Advanced Python** → [Python Advanced Guide](uCODE-Python-Advanced.md)
2. **Create Workflows** → Automate complex tasks
3. **Build Extensions** → Extend uDOS functionality
4. **Contribute Code** → Share your scripts

---

## Quick Reference

### Command Syntax

```python
# uCODE commands (UPPERCASE, brackets, pipes)
GUIDE[ topic | level ]
HEAL*SPRITE[ id | amount | item ]
CHECKPOINT*SAVE[ name ]
GET[ $variable ]
SET[ $variable | value ]

# Python basics (lowercase)
print("message")
if condition:
    action()
for item in items:
    process(item)
```

### Common Patterns

```python
# Check and heal
hp = get_var("player-hp", 100)
if hp < 50:
    HEAL*SPRITE("player", 30, "medkit")  # Python function call

# Monitor resources
water = get_var("water-level", 100)
if water < 30:
    GUIDE("water/collection", "quick")  # Python function call

# Save progress
CHECKPOINT*SAVE("milestone-reached")  # Python function call
XP(+100)  # Python function call
```

---

## Need Help?

- **Beginner:** Start with [uCODE Beginner Commands](uCODE-Beginner-Commands.md)
- **Advanced:** See [uCODE Python Advanced](uCODE-Python-Advanced.md)
- **Quick Lookup:** Use [uCODE Quick Reference](uCODE-Quick-Reference.md)
- **Status:** Run `STATUS*HEALTH` in uDOS
- **Examples:** Browse `memory/ucode/examples/`

---

**Level:** Intermediate  
**Prerequisites:** [uCODE Beginner Commands](uCODE-Beginner-Commands.md)  
**Next:** [uCODE Python Advanced](uCODE-Python-Advanced.md)  
**Version:** v1.2.24
