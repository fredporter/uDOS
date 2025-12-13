# uDOS Examples Directory

Complete example scripts demonstrating correct uCODE syntax at all three learning levels.

## 🎯 Quick Start

Choose your experience level:

| Level | File | Description | Syntax Style |
|-------|------|-------------|-------------|
| **Beginner** | `beginner_daily_check.upy` | Daily survival check with basic commands | UPPERCASE only |
| **Beginner** | `beginner_shelter_mission.upy` | Complete shelter building walkthrough | UPPERCASE only |
| **Intermediate** | `intermediate_resource_manager.upy` | Resource tracking with Python integration | Mixed UPPERCASE + lowercase |
| **Advanced** | `advanced_survival_system.upy` | Full survival system with classes | lowercase Python + uCODE library |

## 📚 Learning Path

### Level 1: Beginner (UPPERCASE uCODE)

**What you'll learn:**
- Basic uCODE commands in UPPERCASE
- Correct syntax patterns (asterisks for tags, $ for variables)
- PRINT with column formatting (pipe separator)
- Variables, checkpoints, missions, XP system
- Interactive guides (GUIDE command)

**Files:**
- `beginner_daily_check.upy` - Simple daily routine script
- `beginner_shelter_mission.upy` - Complete mission walkthrough

**Correct Syntax Examples:**
```upy
PRINT[ Water: 50L | Food: 30 days | Health: 85% ]  # Columns with pipe
SET[ $water-level | 45 ]                            # $ prefix for variables
CHECKPOINT*SAVE[ materials-gathered ]               # Asterisk for tags
STATUS                                              # No empty brackets
IF {$water-level} < 30 THEN
  GUIDE[ water/purification | detailed ]
END IF
```

**Common Mistakes to Avoid:**
```upy
# ❌ WRONG:
CHECKPOINT_SAVE[ data ]        # Underscore (wrong)
SET[ water-level | 45 ]        # Missing $ prefix (wrong)
STATUS[]                       # Empty brackets (wrong)
PRINT[ Line 1\nLine 2 ]        # \n creates lines (wrong for columns)

# ✅ CORRECT:
CHECKPOINT*SAVE[ data ]        # Asterisk (correct)
SET[ $water-level | 45 ]       # $ prefix (correct)
STATUS                         # No brackets (correct)
PRINT[ Col1 | Col2 | Col3 ]    # Pipe creates columns (correct)
```

### Level 2: Intermediate (Mixed Syntax)

**What you'll learn:**
- Mixing UPPERCASE uCODE with lowercase Python
- Python functions alongside uCODE commands
- Variable interpolation between systems
- Loops, conditionals, and data structures
- When to use UPPERCASE vs lowercase

**Files:**
- `intermediate_resource_manager.upy` - Resource management with Python logic

**Syntax Mixing Example:**
```upy
# UPPERCASE uCODE for commands
SET[ $water-level | 100 ]
MISSION*START[ resource-management ]

# lowercase Python for logic
def check_resource(name, level, threshold):
    status = "OK" if level > threshold else "LOW"
    return f"{name}: {level}% ({status})"

# Get uCODE variable in Python
water = GET[ $water-level ]

# Use Python result in uCODE
PRINT[ {check_resource('Water', water, 30)} ]

# Python loop with uCODE commands
for day in range(1, 4):
    PRINT[ Day {day} complete ]
    CHECKPOINT*SAVE[ day-{day} ]
```

**Understanding the Transition:**
- uCODE commands stay UPPERCASE (PRINT, SET, CHECKPOINT*SAVE)
- Python code uses lowercase (def, for, if)
- Variables use $ prefix in uCODE context
- Python variables don't need $ prefix
- Interpolation works: `{python_var}` in uCODE strings

### Level 3: Advanced (Pure Python + uCODE Library)

**What you'll learn:**
- Full Python with uCODE as imported functions
- Classes, dataclasses, decorators
- Type hints and modern Python features
- JSON export, file I/O, datetime handling
- Professional code organization

**Files:**
- `advanced_survival_system.upy` - Complete survival system with classes

**Advanced Pattern:**
```python
# Import uCODE as lowercase library
from ucode import (
    print_output, set_var, get_var, checkpoint_save,
    mission_start, mission_complete, xp_award
)

# Pure Python classes
@dataclass
class Resource:
    name: str
    current: float
    maximum: float
    
    @property
    def percentage(self) -> float:
        return (self.current / self.maximum) * 100

# Use uCODE functions in Python context
class SurvivalSystem:
    def __init__(self):
        mission_start('advanced-survival')
        self.resources = {}
    
    def save_checkpoint(self, name: str) -> None:
        checkpoint_save(name)
        xp_award(100)

# Standard Python entry point
if __name__ == "__main__":
    main()
```

**Key Differences:**
- uCODE functions are lowercase: `print_output()` not `PRINT[]`
- Standard Python imports and libraries
- Type hints and decorators
- Classes with methods and properties
- No $ prefix in Python variable names
- Function call syntax: `set_var('name', value)` not `SET[$name|value]`

## 🔧 Syntax Reference

### Variables
```upy
# Beginner/Intermediate (UPPERCASE context)
SET[ $water-level | 50 ]       # Set variable
GET[ $water-level ]            # Get variable
{$water-level}                 # Use in string

# Advanced (lowercase Python)
set_var('water-level', 50)     # Set variable
level = get_var('water-level') # Get variable
f"Level: {level}"              # Normal Python string
```

### Commands vs Functions
```upy
# Beginner/Intermediate (command syntax)
PRINT[ Message ]
CHECKPOINT*SAVE[ name ]
MISSION*START[ id ]
XP[ +100 ]

# Advanced (function syntax)
print_output("Message")
checkpoint_save("name")
mission_start("id")
xp_award(100)
```

### Tags (Asterisks vs Underscores)
```upy
# ✅ CORRECT - Asterisk for tags
CHECKPOINT*SAVE[ data ]
CHECKPOINT*RESTORE[ data ]
MISSION*START[ id ]
MISSION*COMPLETE[ id ]
HEAL*SPRITE
LEVEL*UP

# ❌ WRONG - Never use underscores
CHECKPOINT_SAVE[ data ]    # Wrong!
MISSION_START[ id ]        # Wrong!
```

### PRINT Columns (Pipes vs Newlines)
```upy
# ✅ CORRECT - Pipe creates columns
PRINT[ Water: 50L | Food: 30 days | Health: 85% ]
# Output: Water: 50L  Food: 30 days  Health: 85%  (side-by-side)

# ✅ CORRECT - Multiple PRINT for lines
PRINT[ Water: 50L ]
PRINT[ Food: 30 days ]
PRINT[ Health: 85% ]
# Output:
# Water: 50L
# Food: 30 days
# Health: 85%

# ❌ WRONG - \n doesn't create columns
PRINT[ Water: 50L\nFood: 30 days ]  # Creates lines, not columns
```

### Empty Brackets (Don't Use Them)
```upy
# ✅ CORRECT - No brackets for no-arg commands
STATUS
INVENTORY
REBOOT
TREE

# ❌ WRONG - Empty brackets
STATUS[]        # Wrong!
INVENTORY[]     # Wrong!
```

## 🎮 System Variables

All system variables are read-only and use $ prefix:

### Config
```upy
{$CONFIG.THEME}           # Current theme
{$CONFIG.EDITOR}          # Editor setting
{$CONFIG.GRID_SIZE}       # Grid dimensions
```

### Viewport
```upy
{$VIEWPORT.WIDTH}         # Terminal width
{$VIEWPORT.HEIGHT}        # Terminal height
{$VIEWPORT.SCROLL_POS}    # Scroll position
```

### Mission
```upy
{$MISSION.ID}             # Current mission ID
{$MISSION.STATUS}         # DRAFT/ACTIVE/PAUSED/COMPLETED/FAILED
{$MISSION.PROGRESS}       # Progress percentage
{$MISSION.XP_EARNED}      # XP from this mission
```

### Workflow
```upy
{$WORKFLOW.NAME}          # Current workflow script
{$WORKFLOW.PHASE}         # INIT/SETUP/EXECUTE/MONITOR/COMPLETE
{$WORKFLOW.ITERATION}     # Current loop number
{$WORKFLOW.ERRORS}        # Error count
```

### Sprite (Player)
```upy
{$SPRITE.HP}              # Health points
{$SPRITE.LEVEL}           # Current level
{$SPRITE.XP}              # Experience points
{$SPRITE.POSITION}        # Grid position (e.g., AA340)
```

### System
```upy
{$SYSTEM.VERSION}         # uDOS version
{$SYSTEM.UPTIME}          # System uptime
{$SYSTEM.OFFLINE_MODE}    # true/false
```

## 🚀 Running Examples

### Interactive Mode
```bash
# Activate virtual environment first
source .venv/bin/activate

# Run any example
./start_udos.sh memory/ucode/examples/beginner_daily_check.upy
./start_udos.sh memory/ucode/examples/intermediate_resource_manager.upy
./start_udos.sh memory/ucode/examples/advanced_survival_system.upy
```

### From uDOS Prompt
```upy
uDOS> RUN[ memory/ucode/examples/beginner_daily_check.upy ]
uDOS> EXECUTE[ intermediate_resource_manager.upy ]
```

## 📖 Documentation

For complete documentation, see:

- **Beginner Guide**: `wiki/uCODE-Beginner-Commands.md`
- **Intermediate Guide**: `wiki/uCODE-Python-First-Guide.md`
- **Advanced Guide**: `wiki/uCODE-Python-Advanced.md`
- **Quick Reference**: `wiki/uCODE-Quick-Reference.md`

## 🆘 Getting Help

If you encounter syntax errors:

1. Check the Quick Reference: `wiki/uCODE-Quick-Reference.md`
2. Compare your code to examples in this directory
3. Remember the key rules:
   - Tags use asterisks (*) not underscores
   - Variables need $ prefix
   - No empty brackets on commands
   - PRINT pipes create columns, not lines
   - UPPERCASE for beginner uCODE, lowercase for Python

## 🔄 Version

These examples are for **uDOS v1.2.24** (Python-First Architecture)

**Performance**: 925,078 operations/second (100x faster than v1.2.23)

Last Updated: December 2025
