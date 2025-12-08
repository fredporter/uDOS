# uPY Syntax v2.0.2 - Complete Reference

**Version:** 2.0.2
**Date:** December 5, 2025
**Status:** Production

---

## Core Syntax Rules

### 1. Three Bracket Types

```upy
{$variable}      # All variables (assignment, interpolation, system)
(command|params) # Commands and functions
[condition]      # Conditionals only
```

### 2. Variable Syntax

**Always use {$ }** - Consistent across all contexts:

```upy
# Assignment
SET {$name|'Alice'}
SET {$hp|100}
SET {$active|true}

# Interpolation in strings
PRINT ('Hello {$name}!')
PRINT ('HP: {$hp}/{$max_hp}')

# In conditionals
[IF {$hp} < 30: PRINT ('Low health!')]
[IF {$name} == 'Alice': XP (+10)]

# System variables
PRINT ('Mission: {$MISSION.NAME}')
PRINT ('Location: {$SPRITE-LOCATION}')
```

### 3. Command Syntax

**Parentheses (command|params)** - All commands and functions:

```upy
# Basic commands
PRINT ('text')
XP (+50)
HP (-10)

# Commands with parameters
SET {$var|value}
ITEM (sword)
FLAG (event_complete)

# Multi-parameter commands
TILE NEARBY (Sydney) (500)
PANEL CREATE (map) (80) (40) (4)

# Functions
@greet({$name})
@calculate({$a}|{$b}|{$c})
```

### 4. Conditional Syntax

**Three formats** - Choose based on complexity:

**Short form (one-line):**
```upy
[IF {$hp} < 30: PRINT ('Low!')]
[IF {$hp} < 30: HP (+20) | PRINT ('Healed!')]  # Multiple actions
```

**Medium form (inline THEN/ELSE):**
```upy
[IF {$hp} < 30 THEN: HP (+20) ELSE: PRINT ('Healthy')]
[IF {$gold} >= 100 THEN: ITEM (sword) ELSE: PRINT ('Need gold')]
[{$hp} < 30 ? HP (+20) : PRINT ('OK')]  # Ternary style
```

**Long form (multi-line, no indents):**
```upy
IF {$hp} < 30
  HP (+20)
  PRINT ('Emergency!')
  FLAG (critical)
ELSE IF {$hp} < 60
  HP (+10)
  PRINT ('Minor heal')
ELSE
  PRINT ('Healthy')
END IF
```

**Delimiters:**
- `:` for THEN
- `|` for multiple actions
- `?` for ternary conditions
- `THEN/ELSE/END IF` for readability

### 5. Separator

**| only** - No spaces, commas, or asterisks:

```upy
# Good
SET {$var|value}
@func({$a}|{$b}|{$c})

# Bad
SET {$var, value}     # No commas
SET {$var * value}    # No asterisks
SET {$var | value}    # No spaces around |
```

---

## Complete Examples

### Variable Operations

```upy
# Assignment
SET {$player_name|'Hero'}
SET {$current_hp|85}
SET {$max_hp|100}
SET {$level|5}
SET {$gold|250}

# Math operations
SET {$new_hp|{$current_hp} + 15}
SET {$total|{$a} * {$b}}

# String building
SET {$greeting|'Hello {$player_name}!'}
```

### Output

```upy
# Simple text
PRINT ('Welcome to uDOS!')

# Variable interpolation
PRINT ('HP: {$current_hp}/{$max_hp}')
PRINT ('Name: {$player_name} | Level: {$level}')

# Blank lines
PRINT ()

# System variables
PRINT ('Location: {$SPRITE-LOCATION}')
PRINT ('Mission: {$MISSION.NAME}')
PRINT ('Time: {$TIME}')
```

### Conditionals

```upy
# Short form (1-2 actions)
[IF {$hp} < 30: PRINT ('Low health!')]\n[IF {$hp} < 30: HP (+20) | PRINT ('Healed!')]\n\n# Medium form (inline branching)
[IF {$gold} >= 100 THEN: ITEM (sword) ELSE: PRINT ('Need more gold')]
[{$hp} < 30 ? HP (+20) : PRINT ('OK')]  # Ternary

# Long form (complex logic)
IF {$hp} < 30
  PRINT ('⚠️  Critical!')
  HP (+50)
  FLAG (emergency)
ELSE IF {$hp} < 60
  HP (+20)
  PRINT ('Minor heal')
ELSE
  PRINT ('Healthy')
  XP (+10)
END IF
```

### Functions

```upy
# Short form (single expression)
@add({$a}|{$b}): RETURN {$a} + {$b}
@greet({$name}): PRINT ('Hello {$name}!')

# Medium form (one-line multi-action)
@heal({$amount}): SET {$SPRITE-HP|{$SPRITE-HP} + {$amount}} | PRINT ('Healed!')

# Long form (multi-line)
FUNCTION battle_check({$enemy_level})
  ROLL (1d20) → {$attack}
  SET {$defense|{$SPRITE-LEVEL} + 10}

  IF {$attack} > {$defense}
    PRINT ('Hit!')
    XP (+25)
    RETURN true
  ELSE
    PRINT ('Miss!')
    RETURN false
  END IF
END FUNCTION

# Calling
@greet('Hero')
SET {$result|@add(5|3)}
SET {$hit|@battle_check(5)}
```

### Loops

```upy
# Iterate over items
FOREACH {$item} IN {$inventory}
  PRINT ('You have: {$item}')
END_FOR

# Iterate over numbers
FOREACH {$i} IN {$quest_ids}
  PRINT ('Quest {$i}: {$quest_names[{$i}]}')
END_FOR
```

### Adventure Script Pattern

```upy
#!/usr/bin/env udos
# Example adventure

# Setup
SET {$SPRITE-NAME|'Adventurer'}
SET {$SPRITE-HP|100}
SET {$SPRITE-LEVEL|1}

PRINT ('Welcome, {$SPRITE-NAME}!')
PRINT ()

# Choice
CHOICE ('What do you do?')
  OPTION ('Explore') → EXPLORE
  OPTION ('Rest') → REST
  OPTION ('Quit') → END

LABEL (EXPLORE)
PRINT ('You venture forth...')
ROLL (1d20) → {$discovery}
[IF {$discovery} >= 15: PRINT ('You found treasure!')]
[IF {$discovery} >= 15: XP (+50)]
[IF {$discovery} < 15: PRINT ('Nothing here.')]
END

LABEL (REST)
PRINT ('You rest and recover.')
HP (+20)
XP (+10)
END
```

---

## Comparison with v2.0.0

### What Changed

| v2.0.0 | v2.0.1 | Reason |
|:-------|:-------|:-------|
| `SET (name\|'Alice')` | `SET {$name\|'Alice'}` | Consistent $ for all vars |
| `PRINT ['text']` | `PRINT ('text')` | Simpler quotes |
| `{IF hp < 30: ...}` | `[IF {$hp} < 30: ...]` | Distinct conditional brackets |
| `$hp` in strings | `{$hp}` in strings | Clear interpolation syntax |
| `$SPRITE-HP` | `{$SPRITE-HP}` | Consistent system vars |

### Why v2.0.1?

1. **Visual distinction**: `{$var}` vs `(command)` vs `[condition]`
2. **Consistent variables**: Always `{$}` - no confusion
3. **Parser-friendly**: Clear delimiters for different syntactic elements
4. **Human-readable**: Each bracket type has distinct purpose
5. **Python-like**: Minimal symbols, clear structure

---

## Migration from v2.0.0

### Quick Replace Pattern

```bash
# Variables in assignments
SET (name|     →  SET {$name|
SET (hp|       →  SET {$hp|
SET (level|    →  SET {$level|

# Variables in strings
PRINT ['$var']     →  PRINT ('{$var}')
PRINT ["$var"]     →  PRINT ('{$var}')

# Variables in conditions
{IF hp <           →  [IF {$hp} <
{IF level >=       →  [IF {$level} >=

# Commands
XP [+50]           →  XP (+50)
HP [-10]           →  HP (-10)
ITEM [sword]       →  ITEM (sword)
FLAG [event]       →  FLAG (event)
```

### Automated Migration

Use the migration script:

```bash
python dev/tools/migrate_to_v2_0_1.py memory/ucode/
```

---

## Syntax Highlighting

### Terminal Colors (ANSI)

```upy
SET {$hp|100}
│    │  └─ Value (magenta)
│    └─ Variable (green)
└─ Command (yellow)

PRINT ('Hello {$name}!')
│      │       │
│      │       └─ Variable (green)
│      └─ String (cyan)
└─ Command (yellow)

[IF {$hp} < 30: PRINT ('Low!')]
│   │    │  │         │
│   │    │  │         └─ String (cyan)
│   │    │  └─ Comparison (red)
│   │    └─ Variable (green)
│   └─ Keyword (blue bold)
└─ Bracket (white)
```

---

## Best Practices

### 1. Clear Variable Names

```upy
# Good
SET {$player_health|100}
SET {$quest_status|'active'}

# Bad
SET {$h|100}
SET {$s|'active'}
```

### 2. Consistent Spacing

```upy
# Good
SET {$name|'Hero'}
PRINT ('HP: {$hp}')
[IF {$level} >= 5: XP (+10)]

# Bad
SET{$name|'Hero'}
PRINT('HP:{$hp}')
[IF{$level}>=5:XP(+10)]
```

### 3. Comment Your Code

```upy
# Initialize player
SET {$SPRITE-NAME|'Survivor'}
SET {$SPRITE-HP|100}

# Check critical health
[IF {$SPRITE-HP} < 20: PRINT ('⚠️  Critical!')]
```

---

## System Variables Reference

All system variables use `{$}` syntax:

```upy
# Character
{$SPRITE-NAME}
{$SPRITE-HP}
{$SPRITE-LEVEL}
{$SPRITE-XP}
{$SPRITE-LOCATION}

# Mission
{$MISSION.ID}
{$MISSION.NAME}
{$MISSION.STATUS}
{$MISSION.PROGRESS}

# Workflow
{$WORKFLOW.NAME}
{$WORKFLOW.PHASE}
{$WORKFLOW.ITERATION}

# Environment
{$USER}
{$HOME}
{$DATE}
{$TIME}
{$THEME}
```

---

## See Also

- [uCODE-Language.md](uCODE-Language.md) - Complete language specification
- [Adventure-Scripting.md](Adventure-Scripting.md) - Interactive storytelling guide
- [Command-Reference.md](Command-Reference.md) - All commands documented
- [Function-Programming-Guide.md](Function-Programming-Guide.md) - Advanced features

---

**Version History:**
- **v2.0.1** (Dec 5, 2025) - Distinct brackets: `{$var}`, `(cmd)`, `[cond]`
- **v2.0.0** (Dec 5, 2025) - Clean syntax: `|` separator, minimal symbols
- **v1.1.x** - Mixed syntax (deprecated)

**Maintainer:** @fredporter
**License:** See LICENSE.txt
