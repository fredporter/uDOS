# Function Programming Guide

**Complete guide to writing functions in uPY v2.0.2 (uDOS v1.2.x)**

**Last Updated:** December 7, 2025

## Overview

Functions allow you to create reusable blocks of code with parameters and return values. This guide covers everything from basic syntax to advanced patterns.

---

## Basic Syntax

### Function Definition

```upy
FUNCTION [@FUNCTION-NAME($PARAM1, $PARAM2)
    # Function body
    RETURN value
]
```

**Components:**
- `FUNCTION` keyword
- `[@NAME($PARAMS)` - Function signature with @ prefix
- Square brackets `[ ... ]` - Function body
- `RETURN` statement - Optional return value
- `]` - Closing bracket

### Function Call

```upy
$RESULT = @FUNCTION-NAME($ARG1, $ARG2)
```

**Components:**
- `@` prefix before function name
- Parentheses with arguments
- Can assign result to variable

---

## Simple Examples

### Hello World Function

```upy
FUNCTION [@GREET($NAME)
    PRINT("Hello, $NAME!")
]

@GREET('Hero')        # Output: Hello, Hero!
@GREET('Traveler')    # Output: Hello, Traveler!
```

### Function with Return Value

```upy
FUNCTION [@DOUBLE($VALUE)
    $RESULT = $VALUE * 2
    RETURN $RESULT
]

$X = @DOUBLE(10)      # $X = 20
$Y = @DOUBLE(25)      # $Y = 50
PRINT("Doubled: $X, $Y")
```

### No Parameters

```upy
FUNCTION [@GET-RANDOM-GREETING()
    $GREETINGS = ['Hello', 'Hi', 'Greetings', 'Welcome']
    ROLL 1d4
    RETURN $GREETINGS[result - 1]
]

$GREETING = @GET-RANDOM-GREETING()
PRINT("$GREETING, traveler!")
```

---

## Function Parameters

### Single Parameter

```upy
FUNCTION [@SQUARE($N)
    RETURN $N * $N
]

$RESULT = @SQUARE(5)  # 25
```

### Multiple Parameters

```upy
FUNCTION [@ADD($A, $B)
    RETURN $A + $B
]

FUNCTION [@MULTIPLY($X, $Y, $Z)
    RETURN $X * $Y * $Z
]

$SUM = @ADD(10, 20)              # 30
$PRODUCT = @MULTIPLY(2, 3, 4)    # 24
```

### Using Variables as Arguments

```upy
$PLAYER-HP = 75
$MAX-HP = 100

FUNCTION [@CALCULATE-HP-PERCENT($CURRENT, $MAX)
    $PERCENT = ($CURRENT / $MAX) * 100
    RETURN $PERCENT
]

$HP-PERCENT = @CALCULATE-HP-PERCENT($PLAYER-HP, $MAX-HP)
PRINT("HP: $HP-PERCENT%")
```

---

## Return Statements

### Simple Return

```upy
FUNCTION [@IS-POSITIVE($N)
    IF {$N > 0 | RETURN 'yes'}
    RETURN 'no'
]
```

### Return Expressions

```upy
FUNCTION [@MAX($A, $B)
    IF {$A > $B | RETURN $A}
    RETURN $B
]

$HIGHEST = @MAX(15, 23)  # 23
```

### Early Returns

```upy
FUNCTION [@VALIDATE-HP($HP, $MAX)
    IF {$HP < 0 | RETURN 0}
    IF {$HP > $MAX | RETURN $MAX}
    RETURN $HP
]

$HP = @VALIDATE-HP(-10, 100)  # Returns 0
$HP = @VALIDATE-HP(150, 100)  # Returns 100
$HP = @VALIDATE-HP(75, 100)   # Returns 75
```

---

## Conditional Logic in Functions

### Using Inline IF

```upy
FUNCTION [@CHECK-STATUS($HP)
    IF {$HP <= 0 | RETURN 'dead'}
    IF {$HP < 20 | RETURN 'critical'}
    IF {$HP < 50 | RETURN 'low'}
    IF {$HP < 75 | RETURN 'moderate'}
    RETURN 'healthy'
]

$STATUS = @CHECK-STATUS(30)
PRINT(":heart: Status: $STATUS")
```

### Using Block IF

```upy
FUNCTION [@CALCULATE-DAMAGE($BASE-DAMAGE, $ARMOR)
    $DAMAGE = $BASE-DAMAGE - $ARMOR

    IF $DAMAGE < 0 THEN
        RETURN 0
    ELSE
        RETURN $DAMAGE
    END
]

$FINAL-DAMAGE = @CALCULATE-DAMAGE(50, 20)  # 30
```

### Multiple Conditions

```upy
FUNCTION [@GET-RANK($LEVEL, $XP)
    IF $LEVEL >= 10 THEN
        IF {$XP > 10000 | RETURN 'Master'}
        RETURN 'Expert'
    END

    IF $LEVEL >= 5 THEN
        RETURN 'Advanced'
    END

    RETURN 'Novice'
]
```

---

## Working with Emojis

```upy
FUNCTION [@DISPLAY-HP($HP, $MAX-HP)
    $PERCENT = ($HP / $MAX-HP) * 100

    IF {$PERCENT >= 75 | PRINT(":heart: HP: $HP/$MAX-HP (Healthy)")}
    IF {$PERCENT >= 50 | PRINT(":warning: HP: $HP/$MAX-HP (Moderate)")}
    IF {$PERCENT >= 25 | PRINT(":cross: HP: $HP/$MAX-HP (Low)")}
    PRINT(":skull: HP: $HP/$MAX-HP (Critical)")
]

@DISPLAY-HP(80, 100)   # :heart: HP: 80/100 (Healthy)
@DISPLAY-HP(30, 100)   # :cross: HP: 30/100 (Low)
```

---

## Nested Function Calls

### Basic Nesting

```upy
FUNCTION [@ADD($A, $B)
    RETURN $A + $B
]

FUNCTION [@MULTIPLY($X, $Y)
    RETURN $X * $Y
]

# Nested calls
$RESULT = @MULTIPLY(@ADD(2, 3), @ADD(4, 5))
# @ADD(2, 3) = 5
# @ADD(4, 5) = 9
# @MULTIPLY(5, 9) = 45
```

### Complex Nesting

```upy
FUNCTION [@VALIDATE($VALUE, $MIN, $MAX)
    IF {$VALUE < $MIN | RETURN $MIN}
    IF {$VALUE > $MAX | RETURN $MAX}
    RETURN $VALUE
]

FUNCTION [@CALCULATE-FINAL-HP($CURRENT, $CHANGE, $MAX)
    $NEW-HP = $CURRENT + $CHANGE
    RETURN @VALIDATE($NEW-HP, 0, $MAX)
]

$HP = 75
$HP = @CALCULATE-FINAL-HP($HP, -100, 100)  # 0 (validated)
$HP = @CALCULATE-FINAL-HP($HP, 50, 100)    # 50
```

---

## Common Patterns

### Calculator Functions

```upy
FUNCTION [@ADD($A, $B)
    RETURN $A + $B
]

FUNCTION [@SUBTRACT($A, $B)
    RETURN $A - $B
]

FUNCTION [@MULTIPLY($A, $B)
    RETURN $A * $B
]

FUNCTION [@DIVIDE($A, $B)
    IF {$B == 0 | RETURN 0}
    RETURN $A / $B
]
```

### Validation Functions

```upy
FUNCTION [@IS-VALID-HP($HP)
    IF {$HP >= 0 | RETURN 'valid'}
    RETURN 'invalid'
]

FUNCTION [@CLAMP($VALUE, $MIN, $MAX)
    IF {$VALUE < $MIN | RETURN $MIN}
    IF {$VALUE > $MAX | RETURN $MAX}
    RETURN $VALUE
]

FUNCTION [@IS-ALIVE($HP)
    IF {$HP > 0 | RETURN 'alive'}
    RETURN 'dead'
]
```

### State Checkers

```upy
FUNCTION [@CAN-AFFORD($GOLD, $COST)
    IF {$GOLD >= $COST | RETURN 'yes'}
    RETURN 'no'
]

FUNCTION [@HAS-ITEM($INVENTORY, $ITEM-NAME)
    # Check if item exists in inventory
    IF {$ITEM-NAME in $INVENTORY | RETURN 'yes'}
    RETURN 'no'
]

FUNCTION [@MEETS-REQUIREMENT($PLAYER-LEVEL, $REQUIRED-LEVEL)
    IF {$PLAYER-LEVEL >= $REQUIRED-LEVEL | RETURN 'yes'}
    RETURN 'no'
]
```

### Formatters

```upy
FUNCTION [@FORMAT-HP-BAR($HP, $MAX-HP)
    $PERCENT = ($HP / $MAX-HP) * 100
    $BARS = $PERCENT / 10

    $BAR-STRING = ''
    # Build bar visualization
    RETURN $BAR-STRING
]

FUNCTION [@FORMAT-CURRENCY($AMOUNT)
    IF {$AMOUNT >= 1000 | RETURN "$AMOUNT :coin:"}
    RETURN "$AMOUNT copper"
]
```

---

## RPG Combat Example

Complete combat system using functions:

```upy
# Character stats
$PLAYER-HP = 100
$PLAYER-HP-MAX = 100
$PLAYER-ATTACK = 25

$ENEMY-HP = 50
$ENEMY-HP-MAX = 50
$ENEMY-ATTACK = 15

# Damage calculation with critical hits
FUNCTION [@CALCULATE-DAMAGE($BASE-DAMAGE)
    ROLL 1d100
    IF {result <= 20 | RETURN $BASE-DAMAGE * 2}  # 20% crit chance
    RETURN $BASE-DAMAGE
]

# Apply damage to target
FUNCTION [@TAKE-DAMAGE($CURRENT-HP, $DAMAGE)
    $NEW-HP = $CURRENT-HP - $DAMAGE
    IF {$NEW-HP < 0 | RETURN 0}
    RETURN $NEW-HP
]

# Check if character is alive
FUNCTION [@IS-ALIVE($HP)
    IF {$HP > 0 | RETURN 'alive'}
    RETURN 'dead'
]

# Display HP with emoji
FUNCTION [@SHOW-HP($NAME, $HP, $MAX-HP)
    $PERCENT = ($HP / $MAX-HP) * 100
    IF {$PERCENT >= 50 | PRINT(":heart: $NAME: $HP/$MAX-HP")}
    IF {$PERCENT >= 25 | PRINT(":warning: $NAME: $HP/$MAX-HP")}
    PRINT(":skull: $NAME: $HP/$MAX-HP")
]

# Combat loop
PRINT(":crossed_swords: COMBAT BEGIN!")
PRINT("")

# Player attacks
$DAMAGE = @CALCULATE-DAMAGE($PLAYER-ATTACK)
IF {$DAMAGE > $PLAYER-ATTACK | PRINT(":boom: CRITICAL HIT!")}
PRINT(":sword: You attack for $DAMAGE damage")
$ENEMY-HP = @TAKE-DAMAGE($ENEMY-HP, $DAMAGE)
@SHOW-HP('Enemy', $ENEMY-HP, $ENEMY-HP-MAX)

# Check if enemy defeated
$ENEMY-STATUS = @IS-ALIVE($ENEMY-HP)
IF {$ENEMY-STATUS == 'dead' | PRINT(":check: Victory!")}
```

---

## Best Practices

### Naming Conventions

✅ **Good:**
```upy
@CHECK-HEALTH
@CALCULATE-DAMAGE
@IS-VALID
@GET-PLAYER-NAME
```

❌ **Bad:**
```upy
@ch        # Too short
@myFunc    # Wrong case
@check_hp  # Underscores instead of hyphens
```

### Keep Functions Focused

✅ **Good:**
```upy
FUNCTION [@VALIDATE-HP($HP, $MAX)
    IF {$HP < 0 | RETURN 0}
    IF {$HP > $MAX | RETURN $MAX}
    RETURN $HP
]

FUNCTION [@DISPLAY-HP($HP, $MAX)
    PRINT(":heart: HP: $HP/$MAX")
]
```

❌ **Bad:**
```upy
FUNCTION [@DO-EVERYTHING($HP, $MAX, $DAMAGE, $NAME)
    # Validates, calculates, displays, and more...
    # Too many responsibilities
]
```

### Use Descriptive Names

✅ **Good:**
```upy
@CALCULATE-TOTAL-DAMAGE
@CHECK-INVENTORY-FOR-ITEM
@VALIDATE-PLAYER-LEVEL
```

❌ **Bad:**
```upy
@CALC
@CHECK
@VAL
```

### Document Complex Functions

```upy
# Calculate final damage after armor and resistances
# Parameters: base damage, armor value, resistance %
# Returns: Final damage (minimum 0)
FUNCTION [@CALCULATE-FINAL-DAMAGE($BASE, $ARMOR, $RESIST)
    $ARMOR-REDUCTION = $BASE * ($ARMOR / 100)
    $AFTER-ARMOR = $BASE - $ARMOR-REDUCTION
    $RESIST-REDUCTION = $AFTER-ARMOR * ($RESIST / 100)
    $FINAL = $AFTER-ARMOR - $RESIST-REDUCTION

    IF {$FINAL < 0 | RETURN 0}
    RETURN $FINAL
]
```

---

## Common Pitfalls

### 1. Forgetting @ Prefix

❌ **Wrong:**
```upy
$RESULT = CHECK-HEALTH($HP)  # Missing @
```

✅ **Correct:**
```upy
$RESULT = @CHECK-HEALTH($HP)
```

### 2. Wrong Bracket Type

❌ **Wrong:**
```upy
FUNCTION (@NAME($PARAM)  # Missing [
    RETURN $PARAM
)  # Wrong closing bracket
```

✅ **Correct:**
```upy
FUNCTION [@NAME($PARAM)
    RETURN $PARAM
]
```

### 3. Missing $ on Parameters

❌ **Wrong:**
```upy
FUNCTION [@ADD(A, B)  # Missing $
    RETURN A + B
]
```

✅ **Correct:**
```upy
FUNCTION [@ADD($A, $B)
    RETURN $A + $B
]
```

---

## Advanced Techniques

### Function Composition

```upy
FUNCTION [@ADD-TEN($N)
    RETURN $N + 10
]

FUNCTION [@DOUBLE($N)
    RETURN $N * 2
]

FUNCTION [@ADD-TEN-THEN-DOUBLE($N)
    $WITH-TEN = @ADD-TEN($N)
    RETURN @DOUBLE($WITH-TEN)
]

$RESULT = @ADD-TEN-THEN-DOUBLE(5)  # (5 + 10) * 2 = 30
```

### Recursive Patterns (with limit)

```upy
FUNCTION [@COUNTDOWN($N)
    IF {$N <= 0 | RETURN 'Done!'}
    PRINT("$N...")
    RETURN @COUNTDOWN($N - 1)
]

@COUNTDOWN(5)  # Prints: 5... 4... 3... 2... 1... Done!
```

---

## See Also

- [Emoji Reference](Emoji-Reference.md) - All emoji codes
- [uCODE Language Reference](uCODE-Language.md) - Complete language guide
- [Command Reference](Command-Reference.md) - All commands

---

**Version**: uDOS v1.1.9+
**Feature**: Functions with @ prefix
**Syntax**: `FUNCTION [@NAME($PARAMS) ... ]`
