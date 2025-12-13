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

**Format:** `COMMAND[arg1|arg2|arg3]`

**Examples:**
```python
from udos_core import *

# Knowledge access
GUIDE["water/purification"|"detailed"]

# Sprite healing
HEAL_SPRITE["player"|"20"|"potion"]

# Checkpoint management
CHECKPOINT_SAVE["camp-established"]

# Tag rendering (visual only)
CLONE*DEV  # Displays as CLONE*DEV, executes as function call
```

**Features:**
- Pipe separator (`|`) for visual clarity
- Asterisk tags (`*`) for visual prominence
- System variables: `{$MISSION.STATUS}`, `{$SPRITE.HP}`
- User variables: `{$player-name}`, `{$camp-location}`
- Emoji escapes for special chars in output: `:pipe:`, `:dollar:`, `:sb:`

---

### 2. Python Commands (Advanced)

**Purpose:** Full Python programming capabilities

**Format:** Standard Python syntax

**Examples:**
```python
# Variables and data structures
player_hp = 100
inventory = ["axe", "rope", "water"]
location = {"x": 10, "y": 20, "layer": 100}

# Control flow
if player_hp < 50:
    HEAL_SPRITE["player"|"30"|"bandage"]
    print("Emergency healing applied")

# Functions
def check_resources(water, food):
    """Check if resources are adequate."""
    total = water + food
    return total > 50

# Loops
for item in inventory:
    PRINT[f"Checking {item}..."]

# List comprehensions
low_resources = [r for r in resources if r < 20]

# Import any Python package
import json
import datetime
from pathlib import Path
```

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

# Python variables (converted to dashes in .upy display)
water_level = get_var("water-level", 100)
min_threshold = 30

# uCODE commands
PRINT["Current water level: {water_level}"]

# Python control flow
if water_level < min_threshold:
    PRINT[":warning: Low water warning!"]
    GUIDE["water/collection"|"quick"]
else:
    PRINT["Water level OK"]

# Update user variable
set_var("water-level", water_level)
```

### Smart Editor Rendering

The smart editor displays this as:

```upy
# water_check.upy - Monitor water resources
from udos_core import *

# Python variables (shown with dashes)
water-level = get_var["water-level"| 100]
min-threshold = 30

# uCODE commands (brackets, pipes visible)
PRINT["Current water level: {water-level}"]

# Python control flow (unchanged)
if water-level < min-threshold:
    PRINT[":warning: Low water warning!"]
    GUIDE["water/collection"|"quick"]
else:
    PRINT["Water level OK"]

# Update user variable
set_var["water-level"| water-level]
```

**Key Transformations:**
- `_` → `-` (underscores become dashes)
- `()` → `[]` (parentheses become brackets for uCODE commands)
- `,` → `|` (commas become pipes in command arguments)

---

## Command Reference

### uCODE Commands (from udos_core)

#### Knowledge Access

```python
GUIDE[category|complexity]
# Examples:
GUIDE["water/purification"|"detailed"]
GUIDE["fire/friction"|"simple"]
GUIDE["medical/wounds"|"technical"]
```

#### Sprite Management

```python
HEAL_SPRITE[sprite_id|amount|item]
# Examples:
HEAL_SPRITE["player"|"20"|"bandage"]
HEAL_SPRITE["companion"|"50"|"medkit"]
```

#### Checkpoint System

```python
CHECKPOINT_SAVE[checkpoint_id]
CHECKPOINT_LOAD[checkpoint_id]
# Examples:
CHECKPOINT_SAVE["camp-established"]
CHECKPOINT_LOAD["before-storm"]
```

#### Output (Emoji-Aware)

```python
PRINT[*messages]
# Examples:
PRINT["Hello, world!"]
PRINT["Score: :sb:100:eb: | Health: :dollar:50"]
PRINT["Use :pipe: separator"]  # Shows actual | character
```

---

### Python Built-ins

Use any Python built-in functions and features:

```python
# String operations
name = "Alice"
greeting = f"Hello {name}".upper()

# Math
import math
distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)

# File operations
from pathlib import Path
config = Path("memory/bank/user/settings.json")

# Data structures
inventory = {"water": 50, "food": 30, "wood": 20}
sorted_items = sorted(inventory.items(), key=lambda x: x[1])

# Comprehensions
resources = [r for r in all_resources if r.amount > 0]

# Error handling
try:
    level = int(user_input)
except ValueError:
    PRINT["Invalid level number"]
```

---

## Variable Systems

### 1. User Variables (Persistent)

Stored in `memory/bank/user/variables.json`, shared across all scripts:

```python
# Set/get with helper functions
set_var("player-name", "Hero")
name = get_var("player-name", "Unknown")

# Or use UserVars class
from udos_core import UserVars
uv = UserVars()
uv.set("camp-location", "AA340")
location = uv.get("camp-location")
```

**Naming Rules:**
- Use dashes, not underscores: `player-hp` not `player_hp`
- Alphanumeric + dash only: `camp-1` not `camp#1`
- Visual in .upy: `{$player-name}`
- Python execution: Auto-converted to `player_name`

### 2. System Variables (Read-Only)

Built-in variables for mission/workflow context:

```python
# Mission variables
mission_id = SystemVars.MISSION_ID
mission_status = SystemVars.MISSION_STATUS  # ACTIVE | PAUSED | COMPLETED
progress = SystemVars.MISSION_PROGRESS

# Workflow variables
workflow_name = SystemVars.WORKFLOW_NAME
phase = SystemVars.WORKFLOW_PHASE  # INIT | EXECUTE | COMPLETE

# Sprite variables (runtime)
sprite_hp = SystemVars.SPRITE_HP
sprite_location = SystemVars.SPRITE_LOCATION
```

### 3. Python Variables (Local)

Standard Python variables in your script:

```python
# Local variables (not persistent)
current_hp = 100
inventory = ["axe", "rope"]
timestamp = datetime.now()

# These exist only during script execution
# Use set_var() to persist across runs
```

---

## Special Characters in Output

Use emoji escape codes for special characters in command arguments:

### Emoji Code Table

| Character | Emoji Code | Example |
|-----------|------------|---------|
| ` | `:backtick:` | PRINT["Code: :backtick:text:backtick:"] |
| ~ | `:tilde:` | PRINT["Path: :tilde:/home"] |
| @ | `:at:` | PRINT["Email: user:at:domain.com"] |
| # | `:hash:` | PRINT["Tag: :hash:important"] |
| $ | `:dollar:` | PRINT["Price: :dollar:50"] |
| % | `:percent:` | PRINT["Rate: 50:percent:"] |
| ^ | `:caret:` | PRINT["Power: 2:caret:8"] |
| & | `:amp:` | PRINT["Logic: A :amp: B"] |
| * | `:star:` | PRINT["Bullet: :star: Item"] |
| [ | `:sb:` | PRINT["Array: :sb:1,2,3:eb:"] |
| ] | `:eb:` | PRINT["End bracket: :eb:"] |
| { | `:lcb:` | PRINT["Object: :lcb:key:rcb:"] |
| } | `:rcb:` | PRINT["End brace: :rcb:"] |
| ' | `:sq:` | PRINT["Quote: :sq:text:sq:"] |
| " | `:dq:` | PRINT["Quote: :dq:text:dq:"] |
| < | `:lt:` | PRINT["Less than: :lt:"] |
| > | `:gt:` | PRINT["Greater than: :gt:"] |
| \ | `:bs:` | PRINT["Path: C::bs:Users"] |
| \| | `:pipe:` | PRINT["Separator: :pipe:"] |
| _ | `:underscore:` | PRINT["Snake_case: :underscore:"] |

**Scope:** Emoji codes are **only for COMMAND[...] arguments**, not entire script.

**Example:**
```python
# Output text with special characters
PRINT["Score: :sb:100:eb: | Health: :dollar:50"]
# Renders as: Score: [100] | Health: $50

# Variable/function names: Use dashes
player-hp = 100  # Visual in .upy
# Executes as: player_hp = 100 (Python)
```

---

## Migration from Old Syntax

Use the migration tool to upgrade existing scripts:

```bash
# Preview changes
python dev/tools/upgrade_upy_syntax.py --dry-run memory/ucode/

# Upgrade scripts
python dev/tools/upgrade_upy_syntax.py memory/ucode/scripts/
```

**Conversions:**
- `PRINT["a", "b"]` → `PRINT["a"|"b"]` (commas to pipes)
- `CLONE--dev` → `CLONE*DEV` (double-dash to asterisk)
- `{$player_name}` → `{$player-name}` (underscores to dashes)

See **[Migration Tool Guide](dev/tools/README-MIGRATION.md)** for details.

---

## Editor Modes

The smart editor has three display modes:

### 1. Pythonic Mode (Default)

Shows pure Python syntax:
```python
player_hp = 100
PRINT("Health:", player_hp)
```

### 2. Symbolic Mode

Shows .upy visual syntax:
```upy
player-hp = 100
PRINT["Health:"| player-hp]
```

### 3. Typo Mode (Optional)

Beautiful typography (requires Typo extension):
```
ᴘʟᴀʏᴇʀ-ʜᴘ = 100
ᴘʀɪɴᴛ[ʜᴇᴀʟᴛʜ: | ᴘʟᴀʏᴇʀ-ʜᴘ]
```

**Switch modes:**
```python
from core.ui.ucode_editor import UCODEEditor

editor = UCODEEditor()
editor.set_mode("pythonic")  # or "symbolic" or "typo"
```

---

## Best Practices

### 1. Use Python Features

Don't reinvent the wheel - use Python's built-ins:

```python
# ✅ Good: Use Python datetime
from datetime import datetime
timestamp = datetime.now().isoformat()

# ❌ Bad: Custom time formatting
# timestamp = custom_time_format()
```

### 2. Persistent vs Local Variables

```python
# ✅ Good: Persist important data
set_var("camp-location", "AA340")
set_var("water-supply", 50)

# ✅ Good: Local for temporary calculations
distance = calculate_distance(start, end)
total = water + food + wood
```

### 3. Error Handling

```python
# ✅ Good: Handle errors gracefully
try:
    level = int(user_input)
    if level < 1:
        raise ValueError("Level must be positive")
except ValueError as e:
    PRINT[f"Error: {e}"]
    level = 1  # Safe default
```

### 4. Naming Conventions

```python
# ✅ Good: uCODE style (dashes in .upy)
player-hp = 100
camp-location = "AA340"

# ✅ Good: Python style (underscores in execution)
# Smart editor converts automatically

# ❌ Bad: Forbidden characters
# player#hp = 100
# camp$location = "AA340"
```

---

## Examples

### Example 1: Water Resource Check

```python
# water_check.upy
from udos_core import *

# Get current water level (persistent)
water = get_var("water-level", 100)
min_safe = 30

PRINT[f"Water level: {water} liters"]

if water < min_safe:
    PRINT[":warning: Low water - consulting guide"]
    GUIDE["water/collection"|"quick"]
    
    # Mark as critical
    set_var("water-critical", True)
else:
    PRINT["Water supply adequate"]
    set_var("water-critical", False)

# Update level
new_level = water - 5  # Daily consumption
set_var("water-level", new_level)
```

### Example 2: Mission Progress

```python
# mission_progress.upy
from udos_core import *

# Check mission status
if SystemVars.MISSION_STATUS == "ACTIVE":
    progress = SystemVars.MISSION_PROGRESS
    PRINT[f"Mission: {SystemVars.MISSION_NAME}"]
    PRINT[f"Progress: {progress}"]
    
    # Parse progress (e.g., "45/55")
    current, total = map(int, progress.split("/"))
    percent = (current / total) * 100
    
    if percent > 75:
        PRINT["Almost complete!"]
        XP["+50"]
    
    # Save checkpoint
    CHECKPOINT_SAVE[f"mission-{current}"]
else:
    PRINT["No active mission"]
```

### Example 3: Inventory Management

```python
# inventory.upy
from udos_core import *
import json

# Load inventory (persistent)
inv_str = get_var("inventory", "[]")
inventory = json.loads(inv_str)

PRINT["Current inventory:"]
for item in inventory:
    PRINT[f"- {item}"]

# Add new item
new_item = "water-filter"
if new_item not in inventory:
    inventory.append(new_item)
    PRINT[f"Added: {new_item}"]
    
    # Save back
    set_var("inventory", json.dumps(inventory))
else:
    PRINT[f"Already have: {new_item}"]
```

---

## Performance

### Benchmarks

**Python-First (v1.2.24+):**
- 925,078 operations/second
- No parser overhead
- Native Python speed

**Old Parser (v1.2.0-1.2.23):**
- ~9,250 operations/second
- Parser interpretation overhead
- 100x slower

### Optimization Tips

```python
# ✅ Good: Direct Python
result = sum(values)

# ❌ Avoid: Unnecessary abstraction
# result = custom_sum_function(values)

# ✅ Good: List comprehension
filtered = [x for x in items if x > 10]

# ❌ Slower: Manual loop
# filtered = []
# for x in items:
#     if x > 10:
#         filtered.append(x)
```

---

## Debugging

### Python Debugger

Use standard Python debugging tools:

```python
# Insert breakpoint
breakpoint()

# Or use pdb
import pdb; pdb.set_trace()

# Step through code
# n (next), s (step), c (continue), p var (print)
```

### Print Debugging

```python
# ✅ Good: Use PRINT for user output
PRINT["Water level: {water}"]

# ✅ Good: Use print() for debugging
print(f"DEBUG: water={water}, min={min_safe}")
```

### Error Messages

```python
try:
    result = risky_operation()
except Exception as e:
    PRINT[f"Error: {e}"]
    print(f"DEBUG: {type(e).__name__}: {e}")
    # Log to file for later review
    with open("memory/logs/errors.log", "a") as f:
        f.write(f"{datetime.now()}: {e}\n")
```

---

## Testing

### Unit Tests

Write pytest tests for your functions:

```python
# test_water_check.py
import pytest
from udos_core import *

def test_water_check():
    """Test water level checking."""
    set_var("water-level", 25)
    
    # Your script logic
    water = get_var("water-level", 100)
    assert water == 25
    
    # Test threshold
    assert water < 30  # Should trigger warning
```

Run tests:
```bash
pytest memory/ucode/tests/ -v
```

---

## Related Documentation

- **[uCODE Beginner Commands](uCODE-Beginner-Commands.md)** - High-level command reference
- **[Python Advanced Features](uCODE-Python-Advanced.md)** - Full Python capabilities
- **[Migration Guide](dev/tools/README-MIGRATION.md)** - Upgrade old scripts
- **[Smart Editor Guide](core/ui/ucode_editor.py)** - Editor implementation
- **[System Variables](Variable-System.md)** - Built-in variables reference

---

## Quick Reference

### Command Format

```python
# uCODE commands (high-level)
COMMAND[arg1|arg2|arg3]

# Python (full language)
standard_python_syntax()
```

### Variable Types

```python
# User variables (persistent)
set_var("key", value)

# System variables (read-only)
SystemVars.MISSION_STATUS

# Python variables (local)
my_var = 100
```

### File Format

```python
# Always save as .upy
memory/ucode/scripts/my_script.upy

# Smart editor renders for display
# Python executes for performance
```

---

**Version:** v1.2.24+  
**Performance:** 925,078 ops/sec  
**Status:** Production Ready
