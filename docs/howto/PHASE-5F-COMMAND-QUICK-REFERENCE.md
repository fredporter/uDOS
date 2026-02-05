# Phase 5F Command Quick Reference

**13 Python Commands | 8 TypeScript Blocks | 61/61 Tests Passing ✅**

---

## Navigation Commands (4)

### MAP

Display location tile grid (80×24)

```
MAP [location-id]
```

- Shows 80-column × 24-row grid
- Tile contents with priority rendering
- Column/row headers
- Region information

### PANEL

Show detailed location information

```
PANEL [location-id]
```

- Comprehensive metadata (type, region, continent)
- GPS coordinates with cardinal directions
- Timezone and local time
- Connection list with hints

### GOTO

Navigate to adjacent or specific location

```
GOTO [direction | location-id]
GOTO [north|south|east|west|up|down]
GOTO [n|s|e|w|u|d]
GOTO L300-BJ10
```

- Direction-based: north, south, east, west, up, down
- Direct navigation to location ID
- Validates connections
- Updates game state

### FIND

Search for locations

```
FIND [query]
FIND tokyo --type city
FIND --region asia --type capital
```

- Text search across all location attributes
- Filter by type (--type flag)
- Filter by region (--region flag)
- Returns up to 20 results with previews

---

## Information Commands (2)

### TELL

Display rich location descriptions

```
TELL [location-id]
TELL L300-BJ10
```

- Box-formatted output with Unicode borders
- Full location description
- Metadata and connections
- Text wrapping at 75 characters

### HELP

Get command reference

```
HELP
HELP MAP
HELP inventory
```

- List all 13 commands
- Show specific command details
- Display usage and examples
- Browse by category

---

## Game State Commands (5)

### BAG

Manage character inventory

```
BAG list
BAG add [item-name] [quantity]
BAG remove [item-name] [quantity]
BAG drop [item-name]
BAG equip [item-name]
```

- List inventory with weights
- Add items to inventory
- Remove specific quantity
- Drop entire item
- Toggle equipped status
- Capacity limit: 100

### GRAB

Pick up objects at location

```
GRAB [object-name]
GRAB key
GRAB potion
```

- Search current location tiles
- Case-insensitive matching
- Adds to inventory automatically
- Shows available objects if none match

### SPAWN

Create objects or sprites

```
SPAWN [type] [char] [name] at [location] [cell]
SPAWN object 🗝️ key at L300-BJ10 BJ10
SPAWN sprite 🧙 wizard at L300-BJ10 BJ15
```

- Types: object (static), sprite (dynamic)
- Specify character representation
- Place at specific cell
- Validates location and cell

### SAVE

Save current game state

```
SAVE
SAVE [slot-name]
SAVE checkpoint-1
```

- Default slot: "quicksave"
- Saves location, inventory, stats
- JSON format in `/memory/saved_games/`
- Named slots for multiple saves

### LOAD

Load saved game state

```
LOAD
LOAD [slot-name]
LOAD checkpoint-1
```

- Default slot: "quicksave"
- Restores complete game state
- Lists available saves if load fails
- Overrides current state

---

## System Commands (2)

### SHAKEDOWN

Validate system integrity

```
SHAKEDOWN
```

- 6-point system validation:
  1. Locations database check
  2. Core commands registration
  3. Memory directories verify
  4. TypeScript runtime verify
  5. Handler modules check
  6. Test suite verification
- Returns pass/fail/warning status

### REPAIR

System maintenance and healing

```
REPAIR
REPAIR --pull
REPAIR --install
REPAIR --check
REPAIR --upgrade
```

- `--pull` - Git synchronization
- `--install` - Dependency check/install
- `--check` - System health check (default)
- `--upgrade` - Full upgrade cycle

---

## TypeScript Runtime Blocks (8)

### state

Define variables and data structures

````markdown
​`state
$name = "Alice"
$level = 1
$inventory = ["sword", "shield"]
$player = {
  "name": "Alice",
  "health": 100,
  "mana": 50
}
​`
````

### set

Update variable values

````markdown
​`set
$level = $level + 1
$health = 100
$position.x = $position.x + 1
​`
````

### form

Create interactive input forms

````markdown
​`form
text: name | "Your Name?"
radio: class | ["Warrior", "Mage", "Rogue"]
checkbox: agree | "I accept terms"
​`
````

### if/else

Conditional execution

````markdown
​`if
$health <= 0
Your character has fallen!
​`else
You have $health health remaining.
​```
````

### nav

Navigate between sections

````markdown
​`nav
→ north | Skip to North Section
→ south | Go South
👈 back | Return to previous
​`
````

### panel

Display information panels

````markdown
​`panel
Status Panel
━━━━━━━━━━━━
Health: $health / 100
Mana: $mana / 50
Level: $level
​`
````

### map

Display grid-based maps

````markdown
​`map
40x25 grid
[A1] [A2] [A3]
[B1] [B2] [B3]
Player at B2 (🧙)
​`
````

---

## Examples

### Complete Game Sequence

```bash
# Start
MAP                           # Show current location

# Explore
FIND tokyo                    # Search for locations
TELL L300-BJ10              # Learn about location

# Game State
GRAB key                      # Pick up object
BAG list                      # Check inventory
SPAWN object 📦 package at L300-BJ10 BJ11

# Progression
SAVE checkpoint              # Save progress
LOAD checkpoint              # Restore state

# System
SHAKEDOWN                     # Verify all systems working
REPAIR --check               # Check system health
HELP                         # See all commands
```

### Example With Slots

```bash
SAVE game-1                  # Create slot "game-1"
GRAB sword                   # Modify state
SAVE game-2                  # Create slot "game-2"
LOAD game-1                  # Back to original state
```

### Example With Filters

```bash
FIND --type capital --region asia
FIND london --region europe
FIND --region africa
```

---

## Common Patterns

### Check System Health

```bash
SHAKEDOWN        # Full validation
REPAIR --check   # Current status
```

### Manage Saves

```bash
SAVE quicksave        # Auto-slot
SAVE before-boss      # Named slot
LOAD before-boss      # Restore
```

### Explore Locations

```bash
MAP L300-BJ10         # Tile grid
PANEL L300-BJ10       # Details
TELL L300-BJ10        # Description
```

### Inventory

```bash
BAG list              # Show all items
BAG add sword 1       # Add item
BAG equip sword       # Equip weapon
BAG remove sword 1    # Remove 1 sword
GRAB shield           # Pick up nearby
```

---

## Error Handling

All commands return structured responses:

```python
{
    "status": "success|error|warning",
    "message": "Human-readable message",
    # ... command-specific fields
}
```

### Common Errors

**Location Not Found**

```
TELL invalid-id
→ error: Location "invalid-id" not found
```

**Insufficient Inventory Space**

```
BAG add sword 50
→ error: Inventory full (capacity: 100)
```

**Invalid Game Slot**

```
LOAD nonexistent
→ error: Save slot "nonexistent" not found
→ Available slots: quicksave, game-1, game-2
```

---

## Integration Notes

### For Developers

**Import all commands:**

```python
from core.commands import (
    MapHandler, PanelHandler, GotoHandler, FindHandler, TellHandler,
    BagHandler, GrabHandler, SpawnHandler, SaveHandler, LoadHandler,
    HelpHandler, ShakedownHandler, RepairHandler
)
```

**Command routing:**

```python
handler = FindHandler()
result = handler.handle(
    command="FIND",
    params=["tokyo", "--type", "city"],
    grid=game_grid,
    parser=command_parser
)
```

### Handler Base Class

All handlers extend `BaseCommandHandler`:

- `handle(command, params, grid, parser)` - Main interface
- `set_state(key, value)` - Store handler state
- `get_state(key)` - Retrieve handler state
- `clear_state()` - Reset state

---

## Statistics

| Category          | Count                 |
| ----------------- | --------------------- |
| Python Commands   | 13                    |
| TypeScript Blocks | 8                     |
| Test Cases        | 61                    |
| Test Pass Rate    | 100%                  |
| Lines of Code     | 2,000+                |
| Handlers          | 13                    |
| Documentation     | This guide + API docs |

---

## Next Steps

**Phase 5G:** Integration with main TUI command router  
**Phase 6:** Advanced features (quests, NPCs, etc.)  
**Phase 7:** Graphics tier integration (ASCII → SVG)

---

_Quick reference for Phase 5F implementation_  
_For detailed docs, see devlog/2026-01-18-phase-5f-complete.md_
