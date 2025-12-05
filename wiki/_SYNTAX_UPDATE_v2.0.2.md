# uPY v2.0.2 Syntax Update

**Date:** December 5, 2025
**Status:** Complete

---

## What's New in v2.0.2

**Three-Format System** - Choose complexity level for conditionals and functions

### Key Changes

| Feature | v2.0.1 | v2.0.2 | Benefit |
|:--------|:-------|:-------|:--------|
| **Conditionals** | One format only | Short/Medium/Long | Flexibility |
| **Functions** | One format only | Short/Medium/Long | Progressive complexity |
| **Delimiters** | `:` only | `:` `\|` `?` `THEN` `ELSE` | Human-readable |
| **Multi-line** | Indents required | No indents, line-by-line | Simpler parsing |

---

## Conditional System

### 1. Short Form (1-2 actions)

**Use when:** Simple checks, quick actions

```upy
[IF {$hp} < 30: PRINT ('Low!')]
[IF {$hp} < 30: HP (+20) | PRINT ('Healed!')]
```

### 2. Medium Form (inline branching)

**Use when:** Need THEN/ELSE, keep it on one line

```upy
[IF {$hp} < 30 THEN: HP (+20) ELSE: PRINT ('OK')]
[IF {$gold} >= 100 THEN: ITEM (sword) ELSE: PRINT ('Need gold')]
[{$hp} < 30 ? HP (+20) : PRINT ('OK')]  # Ternary style
```

### 3. Long Form (complex logic)

**Use when:** Multiple branches, 3+ actions, complex logic

```upy
IF {$hp} < 30
  PRINT ('⚠️  CRITICAL!')
  HP (+50)
  ITEM (emergency_kit)
  FLAG (critical_state)
ELSE IF {$hp} < 60
  HP (+20)
  PRINT ('Minor heal')
ELSE
  PRINT ('Healthy')
  XP (+10)
END IF
```

---

## Function System

### 1. Short Form (single expression)

**Use when:** Simple one-liner, single action

```upy
@add({$a}|{$b}): RETURN {$a} + {$b}
@greet({$name}): PRINT ('Hello {$name}!')
```

### 2. Medium Form (multi-action one-liner)

**Use when:** 2-3 actions, keep compact

```upy
@heal({$amount}): SET {$SPRITE-HP|{$SPRITE-HP} + {$amount}} | PRINT ('Healed {$amount}!')
@award({$xp}): XP (+{$xp}) | PRINT ('Earned {$xp} XP!')
```

### 3. Long Form (multi-line function)

**Use when:** Complex logic, conditionals, multiple steps

```upy
FUNCTION battle_check({$enemy_level})
  ROLL (1d20) → {$attack}
  SET {$defense|{$SPRITE-LEVEL} + 10}
  
  IF {$attack} > {$defense}
    PRINT ('Hit! Damage dealt.')
    XP (+25)
    RETURN true
  ELSE IF {$attack} == {$defense}
    PRINT ('Blocked!')
    RETURN false
  ELSE
    PRINT ('Missed!')
    HP (-5)
    RETURN false
  END IF
END FUNCTION
```

---

## Delimiter Reference

| Symbol | Purpose | Example |
|:-------|:--------|:--------|
| `:` | THEN separator | `[IF {$hp} < 30: PRINT ('Low')]` |
| `\|` | Multiple actions | `HP (+20) \| PRINT ('Healed!')` |
| `\|` | Function params | `@func({$a}\|{$b}\|{$c})` |
| `?` | Ternary condition | `[{$hp} < 30 ? HP (+20) : PRINT ('OK')]` |
| `→` | Result assignment | `ROLL (1d20) → {$result}` |
| `THEN` | Explicit branch | `[IF ... THEN: ... ELSE: ...]` |
| `ELSE` | Alternative branch | Long form conditionals |
| `END IF` | Close conditional | Long form only |
| `END FUNCTION` | Close function | Long form only |

---

## Format Selection Guide

### Conditionals

| Complexity | Use Format | Example |
|:-----------|:-----------|:--------|
| 1 action | Short `[IF ...]` | `[IF {$hp} < 30: HP (+20)]` |
| 2-3 actions | Short with `\|` | `[IF {$hp} < 30: HP (+20) \| PRINT ('Healed!')]` |
| Binary choice | Medium `THEN/ELSE` | `[IF {$gold} >= 100 THEN: ITEM (sword) ELSE: PRINT ('Poor')]` |
| Ternary | Medium `? :` | `[{$hp} < 30 ? HP (+20) : PRINT ('OK')]` |
| 3+ branches | Long `IF/ELSE IF/END IF` | See long form example above |
| Complex logic | Long form | Multiple conditions, nested logic |

### Functions

| Complexity | Use Format | Example |
|:-----------|:-----------|:--------|
| Single expression | Short `@name(...):` | `@add({$a}\|{$b}): RETURN {$a} + {$b}` |
| 2-3 actions | Medium with `\|` | `@heal({$amt}): SET {$hp\|{$hp} + {$amt}} \| PRINT ('Healed!')` |
| Conditionals inside | Long `FUNCTION/END FUNCTION` | See battle_check example |
| Multiple returns | Long form | Different return paths |
| Complex state | Long form | Multiple variables, validation |

---

## Migration from v2.0.1

### Conditionals

```bash
# v2.0.1 (multiple lines)
[IF {$hp} < 30: PRINT ('Low!')]
[IF {$hp} < 30: HP (+20)]
[IF {$hp} < 30: FLAG (critical)]

# v2.0.2 (one line with |)
[IF {$hp} < 30: PRINT ('Low!') | HP (+20) | FLAG (critical)]

# OR use long form
IF {$hp} < 30
  PRINT ('Low!')
  HP (+20)
  FLAG (critical)
END IF
```

### Functions

```bash
# v2.0.1
@greet({$name})
  PRINT ('Hello {$name}!')
END_FUNC

# v2.0.2 Short Form
@greet({$name}): PRINT ('Hello {$name}!')

# v2.0.2 Long Form (unchanged)
FUNCTION greet({$name})
  PRINT ('Hello {$name}!')
END FUNCTION
```

---

## Complete Example

```upy
#!/usr/bin/env udos
# v2.0.2 Comprehensive Example

# === SHORT FORM ===
SET {$hp|45}
SET {$gold|150}

# Quick checks
[IF {$hp} < 50: PRINT ('Low health!')]
[IF {$gold} >= 100: ITEM (potion)]

# Short function
@check({$val}): PRINT ('Value: {$val}')
@check({$hp})

# === MEDIUM FORM ===
# Inline branching
[IF {$hp} < 30 THEN: HP (+50) | PRINT ('Emergency!') ELSE: PRINT ('OK')]

# Ternary
[{$gold} >= 100 ? ITEM (sword) : PRINT ('Need gold')]

# Medium function
@award_xp({$amount}): XP (+{$amount}) | PRINT ('Earned {$amount} XP!')
@award_xp(25)

# === LONG FORM ===
# Complex conditional
IF {$hp} < 30
  PRINT ('⚠️  CRITICAL!')
  HP (+50)
  ITEM (emergency_kit)
  FLAG (critical_state)
ELSE IF {$hp} < 60
  HP (+20)
  PRINT ('Minor heal')
ELSE
  PRINT ('Healthy')
  XP (+10)
END IF

# Complex function
FUNCTION battle_round({$enemy})
  ROLL (1d20) → {$roll}
  
  IF {$roll} >= 18
    PRINT ('Critical hit!')
    SET {$damage|30}
    XP (+75)
  ELSE IF {$roll} >= 15
    PRINT ('Hit!')
    SET {$damage|20}
    XP (+50)
  ELSE IF {$roll} >= 10
    PRINT ('Glancing blow')
    SET {$damage|10}
    XP (+25)
  ELSE
    PRINT ('Miss!')
    SET {$damage|0}
    HP (-5)
  END IF
  
  RETURN {$damage}
END FUNCTION

# Use function
SET {$damage_dealt|@battle_round('goblin')}
PRINT ('Damage: {$damage_dealt}')
```

---

## Benefits

### 1. Progressive Complexity

Start simple, grow as needed:
- **Beginners**: Short form only
- **Intermediate**: Add medium form for branching
- **Advanced**: Long form for complex logic

### 2. Readability

Choose the most readable format:
- Short = compact, scannable
- Medium = clear branching
- Long = step-by-step logic

### 3. No Indentation

All formats work line-by-line:
- No tab/space confusion
- Easier to parse
- Copy-paste friendly

### 4. Human-Friendly Keywords

Explicit keywords aid understanding:
- `THEN` shows consequence
- `ELSE` shows alternative
- `END IF` closes block
- `END FUNCTION` closes function

---

## Updated Files

### Documentation ✅

- **wiki/uCODE-Language.md** - v2.0.2, comprehensive examples
- **wiki/uPY-Syntax-v2.0.1.md** - Updated to v2.0.2
- **wiki/uPY-Syntax-Rules.md** - Quick ref v2.0.2
- **wiki/_SYNTAX_UPDATE_v2.0.2.md** - This file

### Pending Updates

#### Templates (Priority 1)
- [ ] `core/data/templates/adventure.template.upy`
- [ ] `core/data/templates/menu_system.upy`
- [ ] `core/data/templates/crud_app.upy`
- [ ] `core/data/templates/form_validation.upy`

#### Test Files (Priority 1)
- [ ] `extensions/vscode/test-examples/feature-test.upy`
- [ ] `extensions/vscode/test-examples/water-filter-mission.upy`

#### Wiki Documentation (Priority 2)
- [ ] `wiki/Adventure-Scripting.md`
- [ ] `wiki/Function-Programming-Guide.md`

---

## Version History

**v2.0.2** (Dec 5, 2025)
- Three-format system (short/medium/long)
- Enhanced delimiters (`:` `|` `?` `THEN` `ELSE`)
- No indentation required
- Human-readable keywords

**v2.0.1** (Dec 5, 2025)
- Distinct brackets: `{$var}`, `(cmd)`, `[cond]`
- Consistent variable syntax

**v2.0.0** (Dec 5, 2025)
- Clean syntax with `|` separator
- Minimal symbols

---

**Remember:**
- **Short** = 1-2 actions, quick checks
- **Medium** = Inline branching, THEN/ELSE
- **Long** = Complex logic, 3+ branches
- **Choose the format that fits!**

---

**Version:** uPY v2.0.2
**Maintainer:** @fredporter
**License:** See LICENSE.txt
