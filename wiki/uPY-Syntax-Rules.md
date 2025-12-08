# uPY v2.0.2 Syntax Rules

**Quick Reference Card** - Clean, minimal, Python-aligned syntax

**Version:** v2.0.2 (uDOS v1.2.x) | **Date:** December 7, 2025

---

## The 3 Rules

### Rule 1: Three Bracket Types

Each bracket type has a distinct purpose:

```upy
{$variable}      # All variables (always)
(command|params) # Commands and functions
[condition]      # Conditionals only
```

**Examples:**
```upy
✅ SET {$name|'Alice'}              # Variable in {}
✅ PRINT ('Hello {$name}!')          # Command in (), var in {}
✅ [IF {$hp} < 30: HP (+20)]        # Condition in [], var in {}, cmd in ()

❌ SET (name|'Alice')               # Wrong: var needs {}
❌ PRINT ['Hello $name!']           # Wrong: cmd needs (), var needs {}
❌ {IF hp < 30: HP [+20]}          # Wrong: condition needs [], var needs {}
```

---

### Rule 2: Pipe Separator Only

Use `|` to separate multiple parameters. **No spaces, commas, or asterisks.**

```upy
✅ SET {$name|'Alice'}
✅ @function({$arg1}|{$arg2}|{$arg3})
✅ TILE NEARBY (Sydney) (500)

❌ SET {$name, 'Alice'}             # Wrong: comma
❌ SET {$name * 'Alice'}            # Wrong: asterisk
❌ SET {$name | 'Alice'}            # Wrong: spaces around |
```

---

### Rule 3: Variables Always {$ }

**All variables use {$ }** - assignment, interpolation, conditions, system vars:

```upy
# Assignment
✅ SET {$hp|100}
❌ SET (hp|100)                     # Wrong: needs {$}

# Interpolation
✅ PRINT ('HP: {$hp}')
❌ PRINT ('HP: $hp')                # Wrong: needs {}

# Conditions
✅ [IF {$hp} < 30: PRINT ('Low!')]
❌ [IF hp < 30: PRINT ('Low!')]    # Wrong: needs {$}

# System variables
✅ PRINT ('Level: {$SPRITE-LEVEL}')
❌ PRINT ('Level: $SPRITE-LEVEL')  # Wrong: needs {}
```

---

## Quick Reference

### Variables

```upy
SET {$name|'Hero'}                  # Assignment
SET {$hp|100}                       # Number
SET {$active|true}                  # Boolean
```

### Output

```upy
PRINT ('text')                      # Simple text
PRINT ('HP: {$hp}')                 # With variable
PRINT ()                            # Blank line
```

### Conditionals

```upy
# Short form (1-2 actions)
[IF {$hp} < 30: PRINT ('Low!')]
[IF {$hp} < 30: HP (+20) | PRINT ('Healed!')]

# Medium form (inline THEN/ELSE)
[IF {$gold} >= 100 THEN: ITEM (sword) ELSE: PRINT ('Need gold')]
[{$hp} < 30 ? HP (+20) : PRINT ('OK')]  # Ternary

# Long form (complex logic)
IF {$hp} < 30
  HP (+50)
  PRINT ('Emergency!')
  FLAG (critical)
ELSE IF {$hp} < 60
  HP (+20)
ELSE
  PRINT ('Healthy')
END IF
```

### Commands

```upy
XP (+50)                            # Gain XP
HP (-10)                            # Lose HP
ITEM (sword)                        # Add item
FLAG (event)                        # Set flag
ROLL (1d20) → {$result}            # Dice roll
```

### Functions

```upy
# Short form
@greet({$name}): PRINT ('Hello {$name}!')
@add({$a}|{$b}): RETURN {$a} + {$b}

# Medium form
@heal({$amt}): SET {$SPRITE-HP|{$SPRITE-HP} + {$amt}} | PRINT ('Healed!')

# Long form
FUNCTION check_battle({$level})
  ROLL (1d20) → {$roll}
  IF {$roll} >= 15
    XP (+50)
    RETURN true
  ELSE
    RETURN false
  END IF
END FUNCTION

# Calling
@greet('Hero')
SET {$sum|@add(5|3)}
```

### Branching

```upy
LABEL (FOREST)                      # Define label
BRANCH (FOREST)                     # Jump to label

CHOICE ('Which path?')              # Present choice
  OPTION ('Left') → LEFT
  OPTION ('Right') → RIGHT
```

---

## Syntax Patterns

### Character Setup

```upy
SET {$SPRITE-NAME|'Survivor'}
SET {$SPRITE-HP|100}
SET {$SPRITE-HP-MAX|100}
SET {$SPRITE-LEVEL|1}
SET {$SPRITE-XP|0}
SET {$SPRITE-LOCATION|'AA340'}      # Sydney
```

### Skill Checks

```upy
ROLL (1d20) → {$skill_check}
[IF {$skill_check} >= 15: PRINT ('Success!')]
[IF {$skill_check} >= 15: XP (+30)]
[IF {$skill_check} < 15: PRINT ('Failed!')]
[IF {$skill_check} < 15: HP (-10)]
```

### Combat Sequence

```upy
PRINT ('Combat begins!')
ROLL (1d20) → {$attack}
ROLL (1d20) → {$defense}

[IF {$attack} > {$defense}: PRINT ('Hit!')]
[IF {$attack} > {$defense}: HP (-15)]
[IF {$attack} <= {$defense}: PRINT ('Miss!')]
```

---

## Comparison Table

| Element | v2.0.1 | v2.0.0 | Notes |
|:--------|:-------|:-------|:------|
| Variable | `{$name}` | `(name)` or `$name` | Always {$ } |
| Command | `(param)` | `[param]` or `(param)` | Parentheses |
| Condition | `[IF ...]` | `{IF ...}` | Square brackets |
| String | `'text'` | `'text'` | Same |
| Separator | `\|` | `\|` | Same |
| Interpolation | `'{$var}'` | `'$var'` | Needs {} |
| System var | `{$SPRITE-HP}` | `$SPRITE-HP` | Needs {} |

---

## Complete Example

```upy
#!/usr/bin/env udos
# Simple adventure

# Setup character (variables in {})
SET {$SPRITE-NAME|'Hero'}
SET {$SPRITE-HP|100}
SET {$SPRITE-LEVEL|1}

# Output (commands in (), vars in {})
PRINT ('Welcome, {$SPRITE-NAME}!')
PRINT ('HP: {$SPRITE-HP}')
PRINT ()

# Present choice (commands in ())
CHOICE ('What do you do?')
  OPTION ('Explore') → EXPLORE
  OPTION ('Rest') → REST

# Exploration (label in ())
LABEL (EXPLORE)
PRINT ('You venture forth...')
ROLL (1d20) → {$roll}                    # Result to variable
[IF {$roll} >= 15: PRINT ('Treasure!')]  # Condition in []
[IF {$roll} >= 15: XP (+50)]             # Command in ()
[IF {$roll} < 15: PRINT ('Nothing.')]
END

# Resting (label in ())
LABEL (REST)
PRINT ('You rest...')
HP (+20)                                  # Command in ()
XP (+10)
END
```

---

## Why v2.0.1?

### Visual Distinction

- `{$variable}` - Curly = data container
- `(command)` - Parentheses = action/function call
- `[condition]` - Square = control flow

### Consistent Variables

- **Always `{$}`** - No confusion about when to use $
- Assignment: `SET {$hp|100}`
- Interpolation: `PRINT ('{$hp}')`
- Conditions: `[IF {$hp} < 30]`
- System vars: `{$SPRITE-HP}`

### Parser-Friendly

Clear delimiters for different syntactic elements:
- `{` starts variable
- `(` starts command/parameter list
- `[` starts conditional

### Human-Readable

Each bracket type has distinct, obvious purpose:
- Want a variable? Use `{$name}`
- Want a command? Use `(command)`
- Want a condition? Use `[IF ...]`

---

## Migration from v2.0.0

### Quick Find/Replace

```bash
# Variables
SET (name|           →  SET {$name|
SET (hp|             →  SET {$hp|

# In strings
'$var'               →  '{$var}'
"$var"               →  "{$var}"

# In conditions
{IF hp               →  [IF {$hp}
{IF level            →  [IF {$level}

# Commands
XP [+50]             →  XP (+50)
HP [-10]             →  HP (-10)
ITEM [sword]         →  ITEM (sword)
PRINT ['text']       →  PRINT ('text')
```

### Automated Migration

```bash
python dev/tools/migrate_to_v2_0_1.py <directory>
```

---

## See Also

- **[uPY-Syntax-v2.0.1.md](uPY-Syntax-v2.0.1.md)** - Complete syntax reference
- **[uCODE-Language.md](uCODE-Language.md)** - Full language spec with HELP system
- **[Adventure-Scripting.md](Adventure-Scripting.md)** - Interactive storytelling guide
- **[Command-Reference.md](Command-Reference.md)** - All commands documented

---

## Remember

**Three bracket types:**
- `{$variable}` for all variables
- `(command|params)` for commands/functions
- `[condition]` for conditionals only

**Pipe separator:** `|` only (no spaces, commas, asterisks)

**Variables:** Always `{$}` - assignment, interpolation, conditions, system vars

---

**Version:** uPY v2.0.1
**Last Updated:** December 5, 2025
**Maintainer:** @fredporter
