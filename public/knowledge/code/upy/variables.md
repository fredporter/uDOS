---
title: "uPY Variables and Data"
category: code
subcategory: upy
tags: [upy, variables, tutorial]
db_link:
  database: core.db
  table: scripts
  link_type: documentation
---

# uPY Variables Guide

Variables in uPY use the `$` prefix and support simple types, nested access,
and system variables.

---

## Variable Declaration

```upy
# Simple variables
$name = "Hero"
$score = 100
$is_active = True

# Strings with interpolation
$greeting = "Hello, $name!"

# Numbers
$water_level = 50
$temperature = 23.5
```

---

## Variable Naming

- **Prefix:** Always `$`
- **Style:** `snake_case` preferred
- **Characters:** Letters, numbers, underscores
- **Case:** Case-sensitive (`$Name` ≠ `$name`)

```upy
# Good names
$player_hp = 100
$current_location = "AB34"
$mission_step_1 = "Begin"

# Avoid
$x = 100              # Not descriptive
$PlayerHP = 100       # Use snake_case
$step-1 = "Begin"     # No hyphens in variable names
```

---

## System Variables (Read-Only)

Access system state through namespaced variables:

```upy
# Mission context
$MISSION.ID              # Current mission ID
$MISSION.STATUS          # DRAFT|ACTIVE|PAUSED|COMPLETED|FAILED
$MISSION.PROGRESS        # 0-100 percentage

# Workflow context
$WORKFLOW.NAME           # Current workflow script
$WORKFLOW.PHASE          # INIT|SETUP|EXECUTE|MONITOR|COMPLETE
$WORKFLOW.ITERATION      # Loop counter

# User/Sprite
$SPRITE.NAME             # Player name
$SPRITE.HP               # Health points
$SPRITE.LEVEL            # Experience level

# Location
$TILE.CELL               # Current TILE code (e.g., "AB34")
$TILE.LAYER              # Current layer (e.g., 100)
$TILE.REGION             # Region code (e.g., "OC")

# Configuration
$CONFIG.THEME            # Current theme
$CONFIG.EDITOR           # Editor preference
```

---

## Nested Access

Access dictionary/object properties with dot notation:

```upy
# Define nested data
$player = {
    "name": "Hero",
    "stats": {
        "hp": 100,
        "mp": 50
    },
    "inventory": ["sword", "potion"]
}

# Access nested values
$hp = $player.stats.hp       # 100
$weapon = $player.inventory[0]  # "sword"
```

---

## Variable Scope

```upy
# Global scope (file level)
$global_var = "I'm global"

# Function scope
FUNCTION [@calc($x, $y)
    $result = $x + $y    # Local to function
    RETURN $result
]

# Block scope
IF $condition THEN
    $block_var = "I'm in this block"
ENDIF
```

---

## String Interpolation

Variables expand automatically in strings:

```upy
$name = "Fred"
$city = "Sydney"

PRINT("Hello, $name!")           # Hello, Fred!
PRINT("Welcome to $city")        # Welcome to Sydney

# Escape with backslash
PRINT("Use \$name for variables")  # Use $name for variables
```

---

## Type Conversion

```upy
# String to number
$text = "42"
$number = INT($text)       # 42
$decimal = FLOAT("3.14")   # 3.14

# Number to string
$num = 100
$str = STR($num)           # "100"

# Boolean checks
$is_empty = BOOL("")       # False
$has_value = BOOL("yes")   # True
```

---

## Related

- [uPY Functions](functions.md)
- [uPY Conditionals](conditionals.md)
- [uPY Commands](commands.md)
- [uCODE Syntax](../ucode/syntax.md)

---

*Part of uDOS Knowledge Bank - Code Category*
