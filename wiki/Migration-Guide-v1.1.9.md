# Migration Guide: uPY v1.1.9+

Complete guide for upgrading from v1.1.8 to v1.1.9+ with new Python-like syntax.

---

## Quick Reference

| Feature | Old Syntax (v1.1.8) | New Syntax (v1.1.9+) |
|---------|-------------------|-------------------|
| Variables | `{var}` or `$var` | `$VARIABLE-NAME` |
| Assignment | `SET var value` | `$VAR = value` |
| Print | `PRINT [message]` | `PRINT("message")` |
| Conditions | `IF {$HP = 0 ...}` | `IF {$HP == 0 \| ...}` |
| Emojis | Not supported | `:emoji:` (80+ codes) |
| Functions | Not supported | `FUNCTION [@NAME ...` |
| JSON | Not supported | `JSON.load/save` + dot notation |

---

## Variables

### Before ❌
```upy
SET HP 100
SET NAME "Hero"
SET HP-MAX 100
```

### After ✅
```upy
$HP = 100
$NAME = 'Hero'
$HP-MAX = 100
```

**Changes:**
- `$UPPERCASE-HYPHEN` naming convention
- Assignment operator `=` replaces `SET`
- Single quotes `'` for strings
- `SET` still works for backwards compatibility

---

## PRINT Statements

### Before ❌
```upy
PRINT [Hello World]
PRINT ('HP: {HP}')
PRINT ($HP)
```

### After ✅
```upy
PRINT("Hello World")
PRINT(":heart: HP: $HP")
PRINT($HP)
```

**Changes:**
- Double quotes `"` for PRINT
- Emoji codes: `:heart:` `:sword:` `:check:` etc.
- Variable interpolation: `$VAR` in strings
- Parentheses `()` instead of brackets `[]`

---

## Conditionals

### Before ❌
```upy
IF $HP = 0 THEN
    PRINT ('Game Over')
END

IF {$HP > 50 THEN PRINT ('Healthy')}
```

### After ✅
```upy
IF $HP == 0 THEN
    PRINT("Game Over")
END

IF {$HP > 50 | PRINT("Healthy")}
```

**Changes:**
- `==` for equality (Python standard)
- Pipe `|` separator for inline conditionals
- Double quotes in PRINT

---

## Functions (NEW! 🎉)

Functions are completely new in v1.1.9+.

### Basic Function

```upy
FUNCTION [@GREET($NAME)
    PRINT("Hello, $NAME!")
]

@GREET('Hero')  # Call function
```

### With Return Value

```upy
FUNCTION [@CHECK-HEALTH($HP)
    IF {$HP <= 0 | RETURN 'dead'}
    IF {$HP < 20 | RETURN 'critical'}
    IF {$HP < 50 | RETURN 'low'}
    RETURN 'healthy'
]

$STATUS = @CHECK-HEALTH($HP)
PRINT(":heart: Status: $STATUS")
```

### Multiple Parameters

```upy
FUNCTION [@CALCULATE-DAMAGE($BASE, $ARMOR)
    $DAMAGE = $BASE - $ARMOR
    IF {$DAMAGE < 0 | RETURN 0}
    RETURN $DAMAGE
]

$FINAL-DAMAGE = @CALCULATE-DAMAGE(50, 20)
PRINT(":sword: Damage: $FINAL-DAMAGE")
```

**Syntax:**
- Function names: `@UPPERCASE-HYPHEN`
- Parameters: `$PARAM1, $PARAM2`
- Body in brackets: `[ ... ]`
- Call: `@FUNCTION-NAME($ARGS)`

**See:** [Function Programming Guide](Function-Programming-Guide.md)

---

## Emojis (NEW! 🎉)

### Basic Usage

```upy
PRINT(":heart: Health: $HP")
PRINT(":sword: Attack :shield: Defense")
PRINT(":check: Quest Complete!")
PRINT(":warning: Low health!")
```

### Common Codes

**Status Indicators:**
- `:check:` ✓ - Success/completion
- `:cross:` ✗ - Failure/error
- `:warning:` ⚠ - Warning/caution
- `:info:` ⓘ - Information
- `:star:` ⭐ - Important/featured

**Game Items:**
- `:heart:` ♥ - Health/HP
- `:sword:` † - Attack/weapon
- `:shield:` ◊ - Defense/armor
- `:coin:` ⊚ - Currency/gold
- `:gem:` ◆ - Gems/jewels
- `:key:` ⚷ - Keys
- `:potion:` ⚗ - Potions

**Combat:**
- `:crossed_swords:` ⚔ - Combat
- `:boom:` ⚡ - Explosion
- `:fire:` ▲ - Fire
- `:bolt:` ↯ - Lightning
- `:skull:` ☠ - Death

**Directions:**
- `:up:` ↑ - North
- `:down:` ↓ - South
- `:left:` ← - West
- `:right:` → - East

**UI Elements:**
- `:menu:` ≡ - Menu
- `:home:` ⌂ - Home
- `:gear:` ⚙ - Settings
- `:search:` ⌕ - Search

**See:** [Emoji Reference](Emoji-Reference.md) for complete list (80+ codes)

---

## JSON Integration (NEW! 🎉)

### Load JSON File

```upy
JSON.load("player.json")
```

### Access Data (Dot Notation)

```upy
# Read nested fields
$HP = player.stats.health
$NAME = player.info.name
$LEVEL = player.info.level

# Access arrays
$FIRST-ITEM = player.inventory.items[0]
$QUEST-NAME = player.quests[1].name
```

### Modify Data

```upy
# Update fields
player.stats.health = 100
player.info.level = 5

# Modify arrays
player.inventory.items[0] = 'Magic Sword'
player.inventory.gold = player.inventory.gold + 100
```

### Save Changes

```upy
JSON.save("player.json")
```

### Complete Example

```upy
# Load player data
JSON.load("player.json")

# Check health
IF {player.stats.health < 50 | PRINT(":warning: Low health!")}

# Add quest reward
player.inventory.gold = player.inventory.gold + 100
player.inventory.items.append("Health Potion")

# Update stats
player.stats.level = player.stats.level + 1
player.stats.max_health = player.stats.max_health + 10

# Save
JSON.save("player.json")
PRINT(":check: Player data saved!")
```

---

## Complete Example: Before & After

### Before (v1.1.8) ❌

```upy
SET HP 100
SET NAME "Hero"
SET GOLD 50

PRINT [HP: {HP}]
PRINT [Player: {NAME}]
PRINT [Gold: {GOLD}]

IF $HP > 50 THEN
    PRINT [Healthy]
ELSE
    PRINT [Low Health]
END
```

### After (v1.1.9+) ✅

```upy
$HP = 100
$NAME = 'Hero'
$GOLD = 50

PRINT(":heart: HP: $HP")
PRINT(":shield: Player: $NAME")
PRINT(":coin: Gold: $GOLD")

IF $HP > 50 THEN
    PRINT(":check: Healthy")
ELSE
    PRINT(":warning: Low Health")
END
```

### With Functions ✅

```upy
$HP = 100
$NAME = 'Hero'
$GOLD = 50

FUNCTION [@CHECK-STATUS($HEALTH)
    IF {$HEALTH > 75 | RETURN ':check: excellent'}
    IF {$HEALTH > 50 | RETURN ':info: good'}
    IF {$HEALTH > 25 | RETURN ':warning: poor'}
    RETURN ':cross: critical'
]

FUNCTION [@CAN-AFFORD($PRICE, $CURRENT-GOLD)
    IF {$CURRENT-GOLD >= $PRICE | RETURN 'yes'}
    RETURN 'no'
]

$STATUS = @CHECK-STATUS($HP)
$CAN-BUY = @CAN-AFFORD(100, $GOLD)

PRINT(":heart: HP: $HP - Status: $STATUS")
PRINT(":coin: Gold: $GOLD")
PRINT("Can buy 100g item: $CAN-BUY")
```

---

## Backwards Compatibility

### Still Works ✅

- `SET var value` (but `$VAR = value` preferred)
- `IF condition THEN ... END` blocks
- `LABEL` and `GOTO`
- `ROLL`, `CHOICE`, `CALL` commands

### Breaking Changes ❌

- `{variable}` format → use `$VARIABLE`
- `PRINT [message]` → use `PRINT("message")`
- Single quotes in PRINT → use double quotes `"`

---

## Migration Checklist

When updating your .upy files:

1. ✅ Convert `SET var value` → `$VAR = value`
2. ✅ Convert `PRINT [...]` → `PRINT("...")`
3. ✅ Change variable names to `$UPPERCASE-HYPHEN`
4. ✅ Replace `=` with `==` in conditionals
5. ✅ Add emoji codes where appropriate
6. ✅ Consider converting logic to functions
7. ✅ Use JSON for complex data storage
8. ✅ Test with pytest

---

## Testing Your Migration

```bash
# Run v1.1.9+ test suite
pytest sandbox/tests/test_upy_v1_1_9.py -v

# Test your script
./start_udos.sh your_script.upy
```

### Test Results Expected

```
test_assignment_operator ✓
test_variable_syntax ✓
test_emoji_replacement ✓
test_function_definition ✓
test_function_call ✓
test_function_return ✓
test_nested_functions ✓
test_json_load ✓
test_json_dot_notation ✓
test_json_save ✓
test_inline_if ✓
test_print_with_emojis ✓
...
26/26 tests passing
```

---

## Common Migration Patterns

### Pattern 1: Health System

**Before:**
```upy
SET HP 100
SET MAX-HP 100
PRINT [HP: {HP}]
```

**After:**
```upy
$HP = 100
$MAX-HP = 100
PRINT(":heart: HP: $HP/$MAX-HP")
```

### Pattern 2: Inventory Check

**Before:**
```upy
SET GOLD 50
IF $GOLD > 100 THEN
    PRINT [Can afford item]
END
```

**After:**
```upy
$GOLD = 50
IF {$GOLD >= 100 | PRINT(":check: Can afford item")}
```

### Pattern 3: Combat System

**Before:**
```upy
SET DAMAGE 25
SET ARMOR 10
SET FINAL-DAMAGE {DAMAGE - ARMOR}
PRINT [Damage: {FINAL-DAMAGE}]
```

**After:**
```upy
FUNCTION [@CALCULATE-DAMAGE($BASE, $ARMOR)
    $DMG = $BASE - $ARMOR
    IF {$DMG < 0 | RETURN 0}
    RETURN $DMG
]

$FINAL-DAMAGE = @CALCULATE-DAMAGE(25, 10)
PRINT(":crossed_swords: Damage: $FINAL-DAMAGE")
```

---

## See Also

- [Emoji Reference](Emoji-Reference.md) - All 80+ emoji codes
- [Function Programming Guide](Function-Programming-Guide.md) - Complete function tutorial
- [uCODE Language Reference](uCODE-Language.md) - Full language specification
- [Command Reference](Command-Reference.md) - All commands

---

**Version**: uDOS v1.1.9+
**Date**: January 2025
**Status**: Production Ready ✅
