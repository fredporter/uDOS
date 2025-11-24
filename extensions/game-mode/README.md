# uDOS Game Mode Extension

Game mechanics and exploration features for uDOS - opt-in extension for users who want interactive gaming elements.

## Features

### Map Navigation System
- **MAP** - Display current location map
- **STEP** - Move in a direction
- **ASCEND** - Move up a level
- **DESCEND** - Move down a level
- **GOTO** - Teleport to location
- **LAYER** - Switch map layers
- **LOCATE** - Find items/locations

### Scenario System
Interactive stories and survival scenarios with branching choices.

### Resource Management
- **INVENTORY** - View items
- **TRADE** - Exchange resources
- **BARTER** - Negotiate trades

### Progression System
- **XP** - Experience points tracking
- Level-based progression
- Skill development

## Installation

Game mode is included with uDOS but disabled by default.

**Enable:**
```
POKE START game-mode
```

**Disable:**
```
POKE STOP game-mode
```

## Philosophy

Game mechanics are awesome but not essential for core text-first computing workflow. This extension keeps them optional while maintaining full functionality for users who enjoy them.

## Commands Moved to Extension

From `core/commands/`:
- `map_handler.py`
- `scenario_handler.py`
- `scenario_play_handler.py`
- `survival_handler.py`
- `resource_handler.py`
- `xp_handler.py`

From `core/services/`:
- `scenario_service.py`
- `scenario_engine.py`
- `survival_service.py`

## Version

v1.0.29 - Extracted from core as optional extension
