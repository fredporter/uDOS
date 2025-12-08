# uPY v2.0.2 Language Reference

**Version:** v2.0.2 (aligned with uDOS v1.2.x)
**Last Updated:** December 7, 2025
**Status:** Production Ready

## Table of Contents

1. [Introduction](#introduction)
2. [Basic Syntax](#basic-syntax)
3. [Variables](#variables)
4. [Data Types](#data-types)
5. [Math Operations](#math-operations)
6. [Lists](#lists)
7. [File I/O](#file-io)
8. [Functions](#functions)
9. [Conditionals](#conditionals)
10. [Loops](#loops)
11. [Commands](#commands)
12. [System Variables](#system-variables)
13. [Best Practices](#best-practices)

---

## Introduction

uPY (micro-Python) v2.0.2 is a lightweight scripting language designed for uDOS mission workflows, automation, and knowledge scripting. It provides clean, readable syntax with powerful features for text processing, file manipulation, and system interaction.

**Design Goals:**
- 📖 **Human-readable** - Clear syntax, minimal punctuation
- 🚀 **Fast execution** - Direct interpretation, no compilation
- 🔒 **Type-safe** - Explicit types, clear errors
- 🧩 **Modular** - Functions, lists, file I/O
- 🌐 **Integrated** - Full uDOS command access
- 📁 **Organized** - Scripts in `memory/ucode/` structure

---

## Basic Syntax

### Script Structure

```python
# Comments start with # (ignored by interpreter)

# Simple command
(ECHO|Hello, world!)

# Variable assignment
(SET|name|Alice)

# Variable usage
(ECHO|Welcome, {$name}!)
```

### Command Format

All commands use pipe-separated syntax:
```
(COMMAND|param1|param2|param3)
```

**Examples:**
```python
(ECHO|This is a message)
(SET|counter|10)
(FILE READ|memory/config.json)
(LIST CREATE|fruits|[apple, banana, cherry])
```

### Line Structure

- One command per line
- Indentation optional (for readability)
- Comments start with `#`
- Empty lines ignored

---

## Variables

### Variable Declaration

```python
# SET command creates or updates variables
(SET|name|value)

# Examples
(SET|hp|100)
(SET|player_name|Alice)
(SET|is_active|true)
```

### Variable Substitution

Use `{$name}` syntax to reference variables:

```python
(SET|greeting|Hello)
(SET|name|Bob)
(ECHO|{$greeting}, {$name}!)
# Output: Hello, Bob!
```

### Variable Naming Rules

- Start with letter or underscore: `name`, `_count`
- Can contain letters, numbers, underscores: `player_hp`, `item_1`
- Case-sensitive: `Name` ≠ `name`
- Use dot notation for nested access: `MISSION.ID`, `SPRITE.x`

**Valid:**
```python
{$name}
{$player_hp}
{$_counter}
{$item1}
{$MISSION.ID}
```

**Invalid:**
```python
{$1name}       # Can't start with number
{$player-hp}   # Hyphens not allowed
{$my variable} # Spaces not allowed
```

### Variable Scope

1. **Global scope** - Variables set in main script
2. **Function scope** - Variables set inside functions (isolated)
3. **Loop scope** - Variables set in loops (global, unless in function)

```python
(SET|x|10)  # Global

FUNCTION test()
    (SET|x|20)  # Local (shadows global)
    (ECHO|{$x})  # Prints 20
END FUNCTION

@test()
(ECHO|{$x})  # Prints 10 (global unchanged)
```

---

## Data Types

uPY v2.0.2 supports several data types with automatic coercion:

### String

Text values (default type):
```python
(SET|name|Alice)
(SET|message|Hello, world!)
(SET|empty|)
```

### Number

Integer or floating-point:
```python
(SET|count|42)
(SET|price|19.99)
(SET|negative|-10)
```

### Boolean

True/false values (stored as strings):
```python
(SET|is_active|true)
(SET|is_complete|false)
```

### List

Ordered collection of items:
```python
(SET|fruits|[apple, banana, cherry])
(SET|numbers|[1, 2, 3, 4, 5])
(SET|mixed|[text, 42, {$var}])
```

### Object (JSON)

Structured data (via JSON commands):
```python
(SET|config|(JSON PARSE|{"name": "Alice", "level": 10}))
```

### Type Coercion

Variables automatically convert between types:

```python
# String to number (in math)
(SET|x|10)
(SET|result|{$x} + 5)  # 15

# Number to string (in ECHO)
(SET|count|42)
(ECHO|Count: {$count})  # "Count: 42"

# Boolean to string
(SET|active|true)
(ECHO|Active: {$active})  # "Active: true"
```

---

## Math Operations

### Arithmetic Operators

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `+` | Addition | `5 + 3` | `8` |
| `-` | Subtraction | `10 - 4` | `6` |
| `*` | Multiplication | `6 * 7` | `42` |
| `/` | Division | `15 / 3` | `5` |
| `%` | Modulo (remainder) | `17 % 5` | `2` |
| `**` | Power | `2 ** 3` | `8` |

### Basic Math

```python
(SET|a|10)
(SET|b|5)

# Addition
(SET|sum|{$a} + {$b})  # 15

# Subtraction
(SET|diff|{$a} - {$b})  # 5

# Multiplication
(SET|product|{$a} * {$b})  # 50

# Division
(SET|quotient|{$a} / {$b})  # 2

# Modulo
(SET|remainder|{$a} % {$b})  # 0

# Power
(SET|squared|{$a} ** 2)  # 100
```

### Order of Operations (PEMDAS)

Math expressions follow standard precedence:

1. **P**arentheses `()`
2. **E**xponents `**`
3. **M**ultiplication `*`, **D**ivision `/`, **M**odulo `%` (left-to-right)
4. **A**ddition `+`, **S**ubtraction `-` (left-to-right)

```python
# Without parentheses
(SET|result|2 + 3 * 4)  # 14 (3*4=12, then 2+12=14)

# With parentheses
(SET|result|(2 + 3) * 4)  # 20 (2+3=5, then 5*4=20)

# Complex expression
(SET|result|{$a} ** 2 + {$b} * 3 - 10 / 2)
# If a=5, b=4: 5**2 + 4*3 - 10/2 = 25 + 12 - 5 = 32
```

### Practical Examples

**Loop counter:**
```python
(SET|counter|0)
WHILE {$counter} < 5
    (ECHO|Count: {$counter})
    (SET|counter|{$counter} + 1)
END WHILE
```

**Damage calculation:**
```python
(SET|attack|50)
(SET|defense|15)
(SET|multiplier|1.5)

(SET|base_damage|{$attack} * {$multiplier})  # 75
(SET|reduction|{$defense} / 10)  # 1.5
(SET|final_damage|{$base_damage} - {$reduction})  # 73.5
```

**Health percentage:**
```python
(SET|current_hp|75)
(SET|max_hp|100)
(SET|percentage|({$current_hp} / {$max_hp}) * 100)  # 75
```

---

## Lists

### List Literals

Create lists using square brackets:

```python
# Basic list
(SET|fruits|[apple, banana, cherry])

# With variables
(SET|item1|sword)
(SET|item2|shield)
(SET|inventory|[{$item1}, {$item2}, potion])

# Numbers
(SET|scores|[100, 95, 88, 92])

# Empty list
(SET|empty_list|[])
```

### LIST Commands

#### CREATE

Create a new list:
```python
(LIST CREATE|fruits|[apple, banana, cherry])
# OR
(SET|fruits|[apple, banana, cherry])
```

#### APPEND

Add item to end:
```python
(LIST APPEND|fruits|orange)
# fruits: [apple, banana, cherry, orange]
```

#### REMOVE

Remove item by index:
```python
(LIST REMOVE|fruits|1)
# fruits: [apple, cherry, orange] (removed banana at index 1)
```

#### INSERT

Insert item at position:
```python
(LIST INSERT|fruits|1|mango)
# fruits: [apple, mango, cherry, orange]
```

#### GET

Retrieve item by index:
```python
(SET|fruit|(LIST GET|fruits|0))
# fruit: "apple"
```

#### SET

Update item at index:
```python
(LIST SET|fruits|2|grape)
# fruits: [apple, mango, grape, orange]
```

#### SIZE

Get list length:
```python
(SET|count|(LIST SIZE|fruits))
# count: 4
```

#### SLICE

Extract portion of list:
```python
(SET|subset|(LIST SLICE|fruits|1|3))
# subset: [mango, grape] (indices 1-2, end exclusive)
```

#### CONTAINS

Check if item exists:
```python
(SET|has_apple|(LIST CONTAINS|fruits|apple))
# has_apple: "true"
```

#### INDEX

Find item position:
```python
(SET|position|(LIST INDEX|fruits|grape))
# position: 2
```

#### CLEAR

Empty list:
```python
(LIST CLEAR|fruits)
# fruits: []
```

#### JOIN

Convert list to string:
```python
(SET|text|(LIST JOIN|fruits|, ))
# text: "apple, mango, grape, orange"
```

#### SPLIT

Convert string to list:
```python
(SET|fruits|(LIST SPLIT|apple,banana,cherry|,))
# fruits: [apple, banana, cherry]
```

### Negative Indexing

Access items from end of list:

```python
(SET|fruits|[apple, banana, cherry, orange])

(SET|last|(LIST GET|fruits|-1))      # orange
(SET|second_last|(LIST GET|fruits|-2))  # cherry
```

### Iterating Lists

Use FOREACH to iterate:

```python
(SET|fruits|[apple, banana, cherry])

FOREACH fruit IN {$fruits}
    (ECHO|Fruit: {$fruit})
END FOREACH

# Output:
# Fruit: apple
# Fruit: banana
# Fruit: cherry
```

---

## File I/O

### FILE Commands

#### READ

Read entire file:
```python
(SET|content|(FILE READ|memory/notes.txt))
```

#### WRITE

Write file (overwrite):
```python
(FILE WRITE|memory/notes.txt|This is new content)
```

#### EXISTS

Check if file exists:
```python
(SET|exists|(FILE EXISTS|memory/config.json))
# exists: "true" or "false"
```

#### DELETE

Remove file:
```python
(FILE DELETE|memory/old_data.txt)
```

#### SIZE

Get file size in bytes:
```python
(SET|bytes|(FILE SIZE|memory/data.json))
```

#### LIST

List directory contents:
```python
(SET|files|(FILE LIST|memory/))
# Returns list: [notes.txt, config.json, data.json]
```

### JSON Commands

#### PARSE

Convert JSON string to object:
```python
(SET|data|(JSON PARSE|{"name": "Alice", "level": 10}))
```

#### STRINGIFY

Convert object to JSON string:
```python
(SET|json|(JSON STRINGIFY|{$data}))
```

#### READ

Load JSON file:
```python
(SET|config|(JSON READ|memory/config.json))
```

#### WRITE

Save JSON file:
```python
(JSON WRITE|memory/config.json|{$config})
```

### Practical Examples

**Load and modify config:**
```python
# Load config
(SET|config|(JSON READ|memory/config.json))

# Modify (assuming config has 'volume' field)
(SET|volume|75)
# ... (would need JSON object manipulation - future feature)

# Save
(JSON WRITE|memory/config.json|{$config})
```

**Read lines from file:**
```python
# Read file
(SET|content|(FILE READ|memory/log.txt))

# Split into lines
(SET|lines|(LIST SPLIT|{$content}|\n))

# Iterate
FOREACH line IN {$lines}
    (ECHO|{$line})
END FOREACH
```

**Conditional file creation:**
```python
(SET|path|memory/data.txt)
(SET|exists|(FILE EXISTS|{$path}))

IF {$exists} == false
    (FILE WRITE|{$path}|Default content)
    (ECHO|File created)
ELSE
    (ECHO|File already exists)
END IF
```

---

## Functions

### Short Functions (Inline)

One-line function definitions:

```python
# Definition
@add(a, b): {$a} + {$b}
@greet(name): Hello, {$name}!
@double(x): {$x} * 2

# Call
(SET|sum|@add(5, 10))          # 15
(SET|msg|@greet(Alice))         # "Hello, Alice!"
(SET|result|@double(7))         # 14
```

### Long Functions (Block)

Multi-line function definitions:

```python
FUNCTION calculate_damage($attack, $defense)
    (SET|base_damage|{$attack} * 2)
    (SET|reduction|{$defense} / 10)
    (SET|final_damage|{$base_damage} - {$reduction})
    RETURN {$final_damage}
END FUNCTION

# Call
(SET|damage|@calculate_damage(50, 20))
# damage: 98
```

### Function Parameters

**Parameter Binding:**
- Parameters prefixed with `$` in definition
- Arguments passed by position
- Variables use function scope (isolated from global)

```python
FUNCTION example($param1, $param2)
    (ECHO|Param 1: {$param1})
    (ECHO|Param 2: {$param2})
END FUNCTION

@example(hello, world)
# Output:
# Param 1: hello
# Param 2: world
```

**Variable Arguments:**
```python
# Comma-separated
@add(5, 10)

# Pipe-separated (alternative)
@add(5|10)
```

### Return Values

**RETURN statement:**
```python
FUNCTION is_valid($value)
    IF {$value} > 0
        RETURN true
    ELSE
        RETURN false
    END IF
END FUNCTION

(SET|valid|@is_valid(10))
# valid: "true"
```

**Early return:**
```python
FUNCTION check_status($hp)
    IF {$hp} <= 0
        RETURN dead
    END IF

    IF {$hp} < 20
        RETURN critical
    END IF

    RETURN healthy
END FUNCTION

(SET|status|@check_status(15))
# status: "critical"
```

### Nested Functions

Functions can call other functions:

```python
@add(a, b): {$a} + {$b}
@multiply(x, y): {$x} * {$y}

@complex(a, b, c): @add(@multiply({$a}, {$b}), {$c})

(SET|result|@complex(5, 3, 2))
# Steps: 5*3=15, 15+2=17
# result: 17
```

### Scope Isolation

Function variables don't affect global scope:

```python
(SET|x|100)

FUNCTION test()
    (SET|x|20)      # Local x
    (SET|y|30)      # Local y
    (ECHO|Inside: {$x}, {$y})
END FUNCTION

@test()
# Output: Inside: 20, 30

(ECHO|Outside: {$x})
# Output: Outside: 100

(ECHO|Y: {$y})
# Output: Y: {$y} (undefined, not set globally)
```

### Practical Examples

**Validation function:**
```python
FUNCTION validate_input($value, $min, $max)
    IF {$value} < {$min}
        RETURN Value too low
    ELSE IF {$value} > {$max}
        RETURN Value too high
    ELSE
        RETURN Valid
    END IF
END FUNCTION

(SET|result|@validate_input(75, 0, 100))
# result: "Valid"
```

**Math helper:**
```python
@clamp(value, min, max): {$value} < {$min} ? {$min} : ({$value} > {$max} ? {$max} : {$value})

# Usage
(SET|clamped|@clamp(150, 0, 100))
# clamped: 100
```

---

## Conditionals

### Short Conditionals (Inline)

Single-line if statement:

```python
[IF {$hp} < 20: (ECHO|Low health!)]
[IF {$score} > 100: (SET|bonus|true)]
```

### Medium Conditionals (Ternary)

If-else in one line:

```python
[IF {$hp} > 50 THEN: (ECHO|Healthy) ELSE: (ECHO|Damaged)]
[IF {$count} > 0 THEN: (SET|status|active) ELSE: (SET|status|inactive)]
```

### Long Conditionals (Block)

Multi-line if-else-if chains:

```python
IF {$hp} > 80
    (ECHO|Excellent health)
    (SET|color|green)
ELSE IF {$hp} > 50
    (ECHO|Good health)
    (SET|color|yellow)
ELSE IF {$hp} > 20
    (ECHO|Low health)
    (SET|color|orange)
ELSE
    (ECHO|Critical!)
    (SET|color|red)
END IF
```

### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `>` | Greater than | `{$x} > 10` |
| `<` | Less than | `{$y} < 5` |
| `>=` | Greater or equal | `{$score} >= 100` |
| `<=` | Less or equal | `{$hp} <= 0` |
| `==` | Equal to | `{$status} == active` |
| `!=` | Not equal to | `{$mode} != paused` |

### Nested Conditionals

Conditionals can be nested:

```python
IF {$hp} > 0
    (ECHO|Player is alive)

    IF {$hp} < 20
        (ECHO|WARNING: Low health!)

        IF {$potions} > 0
            (ECHO|Use a potion!)
        ELSE
            (ECHO|Find a potion!)
        END IF
    END IF
ELSE
    (ECHO|Game Over)
END IF
```

### Practical Examples

**Difficulty scaling:**
```python
(SET|level|15)

IF {$level} < 5
    (SET|difficulty|easy)
    (SET|enemy_hp|50)
ELSE IF {$level} < 10
    (SET|difficulty|medium)
    (SET|enemy_hp|100)
ELSE IF {$level} < 20
    (SET|difficulty|hard)
    (SET|enemy_hp|200)
ELSE
    (SET|difficulty|extreme)
    (SET|enemy_hp|500)
END IF
```

**Inventory check:**
```python
(SET|gold|150)
(SET|item_price|100)

IF {$gold} >= {$item_price}
    (SET|gold|{$gold} - {$item_price})
    (ECHO|Purchase successful!)
    (ECHO|Remaining gold: {$gold})
ELSE
    (ECHO|Not enough gold!)
    (SET|needed|{$item_price} - {$gold})
    (ECHO|Need {$needed} more gold)
END IF
```

---

## Loops

### WHILE Loop

Condition-based iteration:

```python
(SET|counter|0)

WHILE {$counter} < 5
    (ECHO|Count: {$counter})
    (SET|counter|{$counter} + 1)
END WHILE

# Output:
# Count: 0
# Count: 1
# Count: 2
# Count: 3
# Count: 4
```

### FOREACH Loop

Iterate over list items:

```python
(SET|fruits|[apple, banana, cherry])

FOREACH fruit IN {$fruits}
    (ECHO|Fruit: {$fruit})
END FOREACH

# Output:
# Fruit: apple
# Fruit: banana
# Fruit: cherry
```

**With literal list:**
```python
FOREACH item IN [sword, shield, potion]
    (ECHO|Item: {$item})
END FOREACH
```

### Nested Loops

Loops can be nested:

```python
(SET|rows|3)
(SET|cols|3)

(SET|r|0)
WHILE {$r} < {$rows}
    (SET|c|0)
    WHILE {$c} < {$cols}
        (ECHO|Cell [{$r}, {$c}])
        (SET|c|{$c} + 1)
    END WHILE
    (SET|r|{$r} + 1)
END WHILE
```

### Practical Examples

**Sum list:**
```python
(SET|numbers|[10, 20, 30, 40, 50])
(SET|sum|0)

FOREACH num IN {$numbers}
    (SET|sum|{$sum} + {$num})
END FOREACH

(ECHO|Total: {$sum})
# Output: Total: 150
```

**Find maximum:**
```python
(SET|scores|[85, 92, 78, 95, 88])
(SET|max|0)

FOREACH score IN {$scores}
    IF {$score} > {$max}
        (SET|max|{$score})
    END IF
END FOREACH

(ECHO|Highest score: {$max})
# Output: Highest score: 95
```

**Countdown:**
```python
(SET|countdown|10)

WHILE {$countdown} > 0
    (ECHO|{$countdown}...)
    (SET|countdown|{$countdown} - 1)
END WHILE

(ECHO|Liftoff!)
```

---

## Commands

### Command Syntax

All uDOS commands are accessible using pipe syntax:

```
(COMMAND|param1|param2|param3)
```

### Common Commands

#### ECHO
Print message to console:
```python
(ECHO|Hello, world!)
(ECHO|Value: {$x})
```

#### SET
Create or update variable:
```python
(SET|name|value)
```

#### GET
Retrieve system variable:
```python
(SET|mission_id|(GET|MISSION.ID))
```

### Nested Commands

Commands can be nested:

```python
# Read and parse JSON
(SET|data|(JSON PARSE|(FILE READ|memory/config.json)))

# Get list item and echo
(ECHO|(LIST GET|fruits|0))

# Triple nesting
(SET|value|(JSON PARSE|(FILE READ|(GET|CONFIG.PATH))))
```

### Extension Commands

Access extension functionality:

```python
# Graphics
(DRAW FLOW|water purification process)
(SPRITE CREATE|player|{x: 10, y: 20})

# Knowledge
(GUIDE|water/boiling)
(SEARCH|fire starting methods)

# Mapping
(MAP SHOW|AA340)
(NAVIGATE TO|JF57)
```

See [Command Reference](Command-Reference.md) for complete command list.

---

## System Variables

### Mission Variables

```python
{$MISSION.ID}           # Current mission identifier
{$MISSION.NAME}         # Mission name
{$MISSION.STATUS}       # DRAFT | ACTIVE | PAUSED | COMPLETED | FAILED
{$MISSION.PROGRESS}     # Progress (e.g., "45/55" or "82%")
{$MISSION.START_TIME}   # ISO timestamp
{$MISSION.OBJECTIVE}    # Mission goal
```

### Workflow Variables

```python
{$WORKFLOW.NAME}        # Current workflow script name
{$WORKFLOW.PHASE}       # INIT | SETUP | EXECUTE | MONITOR | COMPLETE
{$WORKFLOW.ITERATION}   # Current loop iteration
{$WORKFLOW.ERRORS}      # Error count
{$WORKFLOW.ELAPSED_TIME}# Seconds since start
```

### Sprite Variables

```python
{$SPRITE.x}             # X coordinate
{$SPRITE.y}             # Y coordinate
{$SPRITE.character}     # Display character
{$SPRITE.color}         # Color code
{$SPRITE.state}         # Current state
```

### Checkpoint Variables

```python
{$CHECKPOINT.ID}        # Unique identifier
{$CHECKPOINT.TIMESTAMP} # When saved
{$CHECKPOINT.DATA}      # Serialized state
{$CHECKPOINT.PREVIOUS}  # Previous checkpoint
{$CHECKPOINT.NEXT}      # Next checkpoint
```

### Usage Example

```python
(ECHO|Mission: {$MISSION.NAME})
(ECHO|Status: {$MISSION.STATUS})
(ECHO|Progress: {$MISSION.PROGRESS})

IF {$MISSION.STATUS} == ACTIVE
    (ECHO|Mission in progress...)
ELSE IF {$MISSION.STATUS} == COMPLETED
    (ECHO|Mission complete!)
END IF
```

---

## Best Practices

### Code Style

**1. Use descriptive variable names:**
```python
# Good
(SET|player_health|100)
(SET|enemy_damage|25)

# Bad
(SET|h|100)
(SET|d|25)
```

**2. Add comments for complex logic:**
```python
# Calculate damage reduction based on armor
(SET|armor_rating|50)
(SET|reduction|{$armor_rating} / 100)  # Convert to percentage
(SET|final_damage|{$base_damage} * (1 - {$reduction}))
```

**3. Use functions for reusable code:**
```python
# Good - Define once, use many times
FUNCTION calculate_xp($level)
    RETURN {$level} ** 2 * 100
END FUNCTION

(SET|xp_required|@calculate_xp({$player_level}))

# Bad - Repeat calculation
(SET|xp_required|{$player_level} ** 2 * 100)
```

**4. Validate inputs:**
```python
FUNCTION set_health($value)
    IF {$value} < 0
        (SET|hp|0)
    ELSE IF {$value} > 100
        (SET|hp|100)
    ELSE
        (SET|hp|{$value})
    END IF
END FUNCTION
```

### Performance Tips

**1. Cache expensive operations:**
```python
# Good - Calculate once
(SET|list_size|(LIST SIZE|items))
IF {$list_size} > 0
    # Use {$list_size}
END IF

# Bad - Calculate twice
IF (LIST SIZE|items) > 0
    (SET|size|(LIST SIZE|items))
END IF
```

**2. Use early returns in functions:**
```python
FUNCTION process_item($item)
    # Check validity first
    IF {$item} == null
        RETURN error
    END IF

    # Process only if valid
    # ... rest of logic ...
END FUNCTION
```

**3. Minimize file I/O:**
```python
# Good - Read once, process in memory
(SET|data|(FILE READ|large_file.txt))
(SET|lines|(LIST SPLIT|{$data}|\n))
FOREACH line IN {$lines}
    # Process line
END FOREACH

# Bad - Read multiple times
FOREACH i IN [1, 2, 3, 4, 5]
    (SET|data|(FILE READ|large_file.txt))
    # Process
END FOREACH
```

### Error Handling

**1. Check file existence:**
```python
(SET|path|memory/config.json)
(SET|exists|(FILE EXISTS|{$path}))

IF {$exists} == true
    (SET|config|(JSON READ|{$path}))
ELSE
    (ECHO|Config not found, using defaults)
    (SET|config|{})
END IF
```

**2. Validate list indices:**
```python
(SET|index|5)
(SET|size|(LIST SIZE|items))

IF {$index} < {$size}
    (SET|item|(LIST GET|items|{$index}))
ELSE
    (ECHO|Index out of bounds)
END IF
```

**3. Handle division by zero:**
```python
IF {$divisor} != 0
    (SET|result|{$dividend} / {$divisor})
ELSE
    (ECHO|Cannot divide by zero)
    (SET|result|0)
END IF
```

### Organization

**1. Group related logic:**
```python
# === INITIALIZATION ===
(SET|hp|100)
(SET|attack|25)
(SET|defense|15)

# === COMBAT LOGIC ===
FUNCTION calculate_damage($attacker_power, $defender_armor)
    # ...
END FUNCTION

# === MAIN EXECUTION ===
(SET|damage|@calculate_damage({$attack}, {$defense}))
```

**2. Use meaningful sections:**
```python
# ============================================
# CONFIGURATION
# ============================================
(SET|max_retries|3)
(SET|timeout|5000)

# ============================================
# HELPER FUNCTIONS
# ============================================
FUNCTION retry_operation($operation)
    # ...
END FUNCTION

# ============================================
# MAIN WORKFLOW
# ============================================
@retry_operation(fetch_data)
```

---

## Complete Example Script

Here's a complete example demonstrating many v2.0.2 features:

```python
# ============================================
# INVENTORY MANAGEMENT SYSTEM
# ============================================

# === CONFIGURATION ===
(SET|max_items|10)
(SET|starting_gold|100)

# === INITIALIZE INVENTORY ===
(SET|inventory|[sword, shield, potion])
(SET|gold|{$starting_gold})

# === ITEM DATABASE (JSON) ===
(SET|item_db|(JSON PARSE|{
    "sword": {"price": 50, "damage": 10},
    "shield": {"price": 40, "defense": 5},
    "potion": {"price": 10, "heal": 25}
}))

# === HELPER FUNCTIONS ===

FUNCTION can_afford($item_name)
    # Get item price from database
    (SET|price|(GET|{$item_db}.{$item_name}.price))

    IF {$gold} >= {$price}
        RETURN true
    ELSE
        RETURN false
    END IF
END FUNCTION

FUNCTION purchase_item($item_name)
    # Check if can afford
    (SET|affordable|@can_afford({$item_name}))

    IF {$affordable} == false
        RETURN insufficient_gold
    END IF

    # Check inventory space
    (SET|inv_size|(LIST SIZE|inventory))
    IF {$inv_size} >= {$max_items}
        RETURN inventory_full
    END IF

    # Process purchase
    (SET|price|(GET|{$item_db}.{$item_name}.price))
    (SET|gold|{$gold} - {$price})
    (LIST APPEND|inventory|{$item_name})

    RETURN success
END FUNCTION

FUNCTION list_inventory()
    (ECHO|=== INVENTORY ===)
    (SET|count|(LIST SIZE|inventory))
    (ECHO|Items: {$count}/{$max_items})

    FOREACH item IN {$inventory}
        (ECHO|- {$item})
    END FOREACH

    (ECHO|Gold: {$gold})
END FUNCTION

# === MAIN EXECUTION ===

# Show starting inventory
@list_inventory()

# Attempt purchases
(ECHO|\n=== PURCHASING ===)

(SET|result|@purchase_item(potion))
IF {$result} == success
    (ECHO|✓ Purchased potion)
ELSE
    (ECHO|✗ Failed: {$result})
END IF

(SET|result|@purchase_item(sword))
IF {$result} == success
    (ECHO|✓ Purchased sword)
ELSE
    (ECHO|✗ Failed: {$result})
END IF

# Show final inventory
(ECHO|\n=== FINAL INVENTORY ===)
@list_inventory()

# Save to file
(SET|inv_text|(LIST JOIN|inventory|, ))
(FILE WRITE|memory/inventory.txt|{$inv_text})
(ECHO|\nInventory saved to memory/inventory.txt)
```

**Expected Output:**
```
=== INVENTORY ===
Items: 3/10
- sword
- shield
- potion
Gold: 100

=== PURCHASING ===
✓ Purchased potion
✗ Failed: insufficient_gold

=== FINAL INVENTORY ===
Items: 4/10
- sword
- shield
- potion
- potion
Gold: 90

Inventory saved to memory/inventory.txt
```

---

## Migration from v1.x

See [uPY Migration Guide](uPY-Migration-Guide.md) for detailed migration instructions.

**Quick Reference:**

| v1.x Syntax | v2.0.2 Syntax |
|-------------|---------------|
| `{var}` | `{$var}` |
| `SET var value` | `(SET\|var\|value)` |
| `ECHO message` | `(ECHO\|message)` |
| `if condition:` | `IF condition` |
| `name(args)` | `@name(args)` |
| `[item1, item2]` | `[item1, item2]` (same) |

---

## Additional Resources

- [uPY Runtime Architecture](uPY-Runtime-Architecture.md) - Technical implementation details
- [uPY Migration Guide](uPY-Migration-Guide.md) - Migrate from v1.x to v2.0.2
- [Command Reference](Command-Reference.md) - All uDOS commands
- [Workflow System](Workflow-System-v2.md) - Mission and workflow automation
- [Function Programming Guide](Function-Programming-Guide.md) - Advanced function patterns

---

**Version:** 2.0.2
**Last Updated:** December 5, 2025
**Maintainer:** @fredporter
**License:** MIT
