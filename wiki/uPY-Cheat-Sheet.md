# uPY Syntax Cheat Sheet

**Quick reference for uPY v1.1.9+ syntax**

---

## 📋 Variables

```upy
# Assignment
$NAME = 'Hero'              # String (single quotes)
$HP = 100                   # Number
$ACTIVE = true              # Boolean
$TOTAL = $A + $B            # Expression

# Naming convention
$PLAYER-HP                  # ✅ UPPERCASE-HYPHEN
$max_health                 # ✅ lowercase_underscore
$ItemCount                  # ✅ PascalCase

# Using variables
PRINT("Name: $NAME")        # In strings
$NEW = $OLD + 10            # In expressions
```

---

## 🎨 Emojis

```upy
# Syntax
PRINT(":emoji: text")       # Use in PRINT with double quotes

# Common codes
:heart:    ♥   Health       :sword:    †   Attack
:shield:   ◊   Defense      :coin:     ⊚   Gold
:check:    ✓   Success      :cross:    ✗   Failure
:warning:  ⚠   Warning      :info:     ⓘ   Info
:star:     ⭐  Important    :fire:     ▲   Fire
:bolt:     ↯   Lightning    :skull:    ☠   Death

# Directions
:up:       ↑   North        :down:     ↓   South
:left:     ←   West         :right:    →   East

# UI
:menu:     ≡   Menu         :home:     ⌂   Home
:gear:     ⚙   Settings     :search:   ⌕   Search
```

**[See all 80+ codes →](Emoji-Reference.md)**

---

## 🔧 Functions

```upy
# Definition
FUNCTION [@FUNCTION-NAME($PARAM1, $PARAM2)
    # Function body
    RETURN value
]

# Examples
FUNCTION [@GREET($NAME)
    PRINT("Hello, $NAME!")
]

FUNCTION [@ADD($A, $B)
    RETURN $A + $B
]

FUNCTION [@CHECK-HP($HP, $MAX)
    IF {$HP <= 0 | RETURN 'dead'}
    RETURN 'alive'
]

# Calling
@GREET('Hero')
$SUM = @ADD(10, 20)
$STATUS = @CHECK-HP($HP, 100)
```

**[Complete guide →](Function-Programming-Guide.md)**

---

## 📄 JSON

```upy
# Load file
JSON.load("file.json")

# Read data
$NAME = player.name                    # Dot notation
$HP = player.stats.health             # Nested fields
$ITEM = player.inventory.items[0]     # Array access

# Write data
player.name = 'NewName'               # Simple field
player.stats.health = 100             # Nested field
player.inventory.items[0] = 'Sword'   # Array element

# Modify arrays
player.inventory.items.append("Potion")

# Save file
JSON.save("file.json")
```

---

## 🔀 Conditionals

```upy
# Inline IF (one-line)
IF {$HP <= 0 | PRINT("Dead")}
IF {$GOLD >= 100 | $CAN-BUY = 'yes'}
IF {$X < 0 | RETURN 0}

# Block IF (multi-line)
IF $HP > 50 THEN
    PRINT("Healthy")
ELSE
    PRINT("Low health")
END

# Operators
==    Equal              !=    Not equal
<     Less than          >     Greater than
<=    Less or equal      >=    Greater or equal
and   Logical AND        or    Logical OR
```

---

## 💬 PRINT

```upy
# Basic
PRINT("Hello, world!")

# With variables
PRINT("Name: $NAME")
PRINT("HP: $HP/$MAX-HP")

# With emojis
PRINT(":heart: Health: $HP")
PRINT(":coin: Gold: $GOLD")

# Multiple values
PRINT("Level $LEVEL - XP: $XP")

# Expression results
$TOTAL = $A + $B
PRINT("Total: $TOTAL")
```

---

## 📊 Common Patterns

### Health Check
```upy
FUNCTION [@CHECK-HEALTH($HP, $MAX)
    $PERCENT = ($HP / $MAX) * 100
    IF {$PERCENT >= 75 | RETURN ':heart: healthy'}
    IF {$PERCENT >= 50 | RETURN ':warning: moderate'}
    IF {$PERCENT >= 25 | RETURN ':cross: low'}
    RETURN ':skull: critical'
]
```

### Damage Calculation
```upy
FUNCTION [@CALCULATE-DAMAGE($BASE, $ARMOR)
    $DMG = $BASE - $ARMOR
    IF {$DMG < 0 | RETURN 0}
    RETURN $DMG
]
```

### Item Check
```upy
FUNCTION [@HAS-ITEM($INVENTORY, $ITEM)
    # Check if item exists
    IF {$ITEM in $INVENTORY | RETURN 'yes'}
    RETURN 'no'
]
```

### Gold Transaction
```upy
FUNCTION [@CAN-AFFORD($GOLD, $COST)
    IF {$GOLD >= $COST | RETURN 'yes'}
    RETURN 'no'
]
```

---

## 🎯 Quick Examples

### Character Display
```upy
$NAME = 'Hero'
$HP = 85
$GOLD = 150

PRINT(":shield: === CHARACTER ===")
PRINT(":person: Name: $NAME")
PRINT(":heart: HP: $HP/100")
PRINT(":coin: Gold: $GOLD")
```

### Combat
```upy
FUNCTION [@ATTACK($DMG, $DEF)
    $FINAL = $DMG - $DEF
    IF {$FINAL < 0 | RETURN 0}
    RETURN $FINAL
]

$DAMAGE = @ATTACK(25, 10)
PRINT(":crossed_swords: Damage: $DAMAGE")
```

### Save Game
```upy
JSON.load("player.json")
player.stats.health = $HP
player.inventory.gold = $GOLD
JSON.save("player.json")
PRINT(":check: Saved!")
```

---

## ⚡ Shortcuts

| Old (v1.1.8) | New (v1.1.9+) |
|:-------------|:--------------|
| `SET HP 100` | `$HP = 100` |
| `PRINT [Hello]` | `PRINT("Hello")` |
| `{variable}` | `$VARIABLE` |
| `IF $HP = 0` | `IF $HP == 0` |
| No emojis | `:heart:` `:sword:` etc. |
| No functions | `FUNCTION [@NAME ...` |
| No JSON | `JSON.load/save` |

---

## 🐛 Common Mistakes

### ❌ Wrong
```upy
# Missing $ prefix
HP = 100

# Single quotes in PRINT
PRINT(':heart: HP')

# Missing @ in function call
GREET('Hero')

# Missing brackets in function
FUNCTION @NAME($PARAM)
    RETURN $PARAM
END

# = instead of == in condition
IF {$HP = 0 | ...}
```

### ✅ Correct
```upy
# With $ prefix
$HP = 100

# Double quotes in PRINT
PRINT(":heart: HP")

# With @ in function call
@GREET('Hero')

# With brackets in function
FUNCTION [@NAME($PARAM)
    RETURN $PARAM
]

# == in condition
IF {$HP == 0 | ...}
```

---

## 📚 See Also

- **[Full Tutorial](Tutorial-uPY-Quick-Start.md)** - Step-by-step guide
- **[Language Reference](uCODE-Language.md#upy-syntax-v119)** - Complete syntax
- **[Emoji Reference](Emoji-Reference.md)** - All emoji codes
- **[Function Guide](Function-Programming-Guide.md)** - Advanced functions
- **[Command Reference](Command-Reference.md#upy-commands-v119)** - All commands

---

**Version:** uDOS v1.1.9+
**Print this:** Keep as quick reference
**Next:** [Start the tutorial →](Tutorial-uPY-Quick-Start.md)
