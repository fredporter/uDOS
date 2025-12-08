# uPY Migration Guide: Legacy to v1.2

**Last Updated:** December 8, 2025
**Target Version:** v1.2 (uDOS v1.2.21)
**Audience:** uPY script developers migrating from legacy syntax

## Table of Contents

1. [Overview](#overview)
2. [Key Syntax Changes](#key-syntax-changes)
3. [Migration Checklist](#migration-checklist)
4. [Automated Migration](#automated-migration)
5. [Step-by-Step Guide](#step-by-step-guide)
6. [Common Patterns](#common-patterns)
7. [Breaking Changes](#breaking-changes)
8. [Compatibility Mode](#compatibility-mode)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### What Changed in v1.2?

uPY v1.2 introduces **three-format syntax system** with a custom interpreter. The new syntax is designed to:
- ✅ Eliminate Python dependency (no `exec()`)
- ✅ Improve readability and consistency
- ✅ Enable better error messages
- ✅ Support type-safe operations
- ✅ Maintain full backward compatibility (legacy mode)

### Should You Migrate?

**✅ Yes, if you want:**
- Cleaner, more readable scripts
- Better error messages
- Type-safe math operations
- Future-proof syntax
- Access to new features (file I/O, JSON, etc.)

**⏸️ No rush, if:**
- Your v1.x scripts work fine
- You prefer existing syntax
- Scripts are complex and stable

**Note:** v1.x syntax still works! The runtime supports both versions with automatic detection.

---

## Key Syntax Changes

### Variable Syntax

| Feature | v1.x | v2.0.2 |
|---------|------|---------|
| Variable reference | `{var}` | `{$var}` |
| Variable assignment | `SET var value` | `(SET\|var\|value)` |

**Example:**
```python
# v1.x
SET name Alice
ECHO Hello, {name}!

# v2.0.2
(SET|name|Alice)
(ECHO|Hello, {$name}!)
```

### Command Syntax

| Feature | v1.x | v2.0.2 |
|---------|------|---------|
| Command format | `COMMAND param1 param2` | `(COMMAND\|param1\|param2)` |
| Nested commands | Limited | Full support |

**Example:**
```python
# v1.x
ECHO This is a message
FILE READ memory/notes.txt

# v2.0.2
(ECHO|This is a message)
(FILE READ|memory/notes.txt)
```

### Function Syntax

| Feature | v1.x | v2.0.2 |
|---------|------|---------|
| Function call | `function_name(args)` | `@function_name(args)` |
| Function definition | `DEF function_name(params):` | `FUNCTION function_name($params)` |
| Return | `return value` | `RETURN value` |

**Example:**
```python
# v1.x
DEF add(a, b):
    return a + b

result = add(5, 10)

# v2.0.2
FUNCTION add($a, $b)
    RETURN {$a} + {$b}
END FUNCTION

(SET|result|@add(5, 10))
```

### Conditional Syntax

| Feature | v1.x | v2.0.2 |
|---------|------|---------|
| If statement | `if condition:` | `IF condition` |
| Else if | `elif condition:` | `ELSE IF condition` |
| Else | `else:` | `ELSE` |
| End marker | Indentation | `END IF` |

**Example:**
```python
# v1.x
if hp > 50:
    ECHO Healthy
elif hp > 20:
    ECHO Injured
else:
    ECHO Critical

# v2.0.2
IF {$hp} > 50
    (ECHO|Healthy)
ELSE IF {$hp} > 20
    (ECHO|Injured)
ELSE
    (ECHO|Critical)
END IF
```

### Loop Syntax

| Feature | v1.x | v2.0.2 |
|---------|------|---------|
| While loop | `while condition:` | `WHILE condition` |
| For each | `for item in list:` | `FOREACH item IN list` |
| End marker | Indentation | `END WHILE` / `END FOREACH` |

**Example:**
```python
# v1.x
counter = 0
while counter < 5:
    ECHO Count: {counter}
    counter = counter + 1

# v2.0.2
(SET|counter|0)
WHILE {$counter} < 5
    (ECHO|Count: {$counter})
    (SET|counter|{$counter} + 1)
END WHILE
```

---

## Migration Checklist

### Before Migration

- [ ] **Backup scripts** - Copy to `.archive/` folder
- [ ] **Test v1.x scripts** - Ensure they work in current version
- [ ] **Document dependencies** - Note external files, variables
- [ ] **Review breaking changes** - Check list below

### During Migration

- [ ] **Update variable syntax** - `{var}` → `{$var}`
- [ ] **Convert commands** - `COMMAND args` → `(COMMAND|args)`
- [ ] **Update functions** - `function()` → `@function()`
- [ ] **Convert conditionals** - `if:` → `IF` / `END IF`
- [ ] **Convert loops** - `while:` → `WHILE` / `END WHILE`
- [ ] **Add $ to parameters** - `param` → `$param`
- [ ] **Update returns** - `return` → `RETURN`

### After Migration

- [ ] **Run validation** - `VALIDATE <script.upy>`
- [ ] **Test execution** - Run migrated scripts
- [ ] **Compare output** - Verify behavior matches v1.x
- [ ] **Update documentation** - Note changes in script comments
- [ ] **Commit changes** - Version control migration

---

## Automated Migration

### Migration Tool

Use the automated migration script to convert v1.x scripts:

```bash
# Migrate single file
python dev/tools/migrate_upy.py memory/scripts/my_script.upy

# Migrate directory
python dev/tools/migrate_upy.py memory/scripts/ --recursive

# Dry run (preview changes)
python dev/tools/migrate_upy.py memory/scripts/my_script.upy --dry-run

# Create backup before migration
python dev/tools/migrate_upy.py memory/scripts/my_script.upy --backup
```

### What the Tool Does

1. **Detects version** - Identifies v1.x syntax patterns
2. **Converts syntax:**
   - `{var}` → `{$var}`
   - `SET var value` → `(SET|var|value)`
   - `COMMAND args` → `(COMMAND|args)`
   - `function()` → `@function()`
   - `if:` → `IF` / `END IF`
   - `while:` → `WHILE` / `END WHILE`
3. **Preserves comments** - Keeps all # comments
4. **Creates backup** - Original saved to `.archive/`
5. **Validates output** - Checks syntax correctness

### Migration Report

The tool generates a report:

```
Migration Report: my_script.upy
================================

Changes Made:
- 15 variable references updated ({var} → {$var})
- 8 commands converted (COMMAND → (COMMAND|...))
- 3 functions updated (function() → @function())
- 2 conditionals converted (if: → IF/END IF)
- 1 loop converted (while: → WHILE/END WHILE)

Total Lines Modified: 29/150 (19.3%)

Warnings:
- Line 42: Complex nested command may need manual review
- Line 78: Indentation adjusted for END IF placement

Backup: memory/scripts/.archive/my_script_v1.upy_20251205_143022
Validation: PASSED ✓
```

---

## Step-by-Step Guide

### Example: Complete Script Migration

**Original v1.x script:**

```python
# inventory_system.upy (v1.x)

# Initialize inventory
inventory = []
gold = 100

# Item database
item_prices = {"sword": 50, "shield": 40, "potion": 10}

# Function to check affordability
DEF can_afford(item):
    price = item_prices[item]
    if gold >= price:
        return true
    else:
        return false

# Function to purchase item
DEF purchase(item):
    if can_afford(item):
        inventory.append(item)
        gold = gold - item_prices[item]
        ECHO Purchased {item}
        return true
    else:
        ECHO Cannot afford {item}
        return false

# Main execution
ECHO Starting inventory: {inventory}
ECHO Gold: {gold}

purchase("sword")
purchase("potion")
purchase("shield")

ECHO Final inventory: {inventory}
ECHO Remaining gold: {gold}
```

**Migrated v2.0.2 script:**

```python
# inventory_system.upy (v2.0.2)

# Initialize inventory
(SET|inventory|[])
(SET|gold|100)

# Item database (JSON)
(SET|item_prices|(JSON PARSE|{"sword": 50, "shield": 40, "potion": 10}))

# Function to check affordability
FUNCTION can_afford($item)
    # Get price from database
    (SET|price|(GET|{$item_prices}.{$item}))

    IF {$gold} >= {$price}
        RETURN true
    ELSE
        RETURN false
    END IF
END FUNCTION

# Function to purchase item
FUNCTION purchase($item)
    (SET|affordable|@can_afford({$item}))

    IF {$affordable} == true
        (LIST APPEND|inventory|{$item})
        (SET|price|(GET|{$item_prices}.{$item}))
        (SET|gold|{$gold} - {$price})
        (ECHO|Purchased {$item})
        RETURN true
    ELSE
        (ECHO|Cannot afford {$item})
        RETURN false
    END IF
END FUNCTION

# Main execution
(ECHO|Starting inventory: {$inventory})
(ECHO|Gold: {$gold})

@purchase(sword)
@purchase(potion)
@purchase(shield)

(ECHO|Final inventory: {$inventory})
(ECHO|Remaining gold: {$gold})
```

### Step-by-Step Changes

**Step 1: Variables**
```python
# Before
inventory = []
gold = 100

# After
(SET|inventory|[])
(SET|gold|100)
```

**Step 2: Function Definitions**
```python
# Before
DEF can_afford(item):
    # ...

# After
FUNCTION can_afford($item)
    # ...
END FUNCTION
```

**Step 3: Variable References**
```python
# Before
price = item_prices[item]
if gold >= price:

# After
(SET|price|(GET|{$item_prices}.{$item}))
IF {$gold} >= {$price}
```

**Step 4: Function Calls**
```python
# Before
purchase("sword")

# After
@purchase(sword)
```

**Step 5: Conditionals**
```python
# Before
if condition:
    action
else:
    other_action

# After
IF condition
    action
ELSE
    other_action
END IF
```

**Step 6: Commands**
```python
# Before
ECHO message

# After
(ECHO|message)
```

---

## Common Patterns

### Pattern 1: Simple Variable Updates

```python
# v1.x
SET counter 0
counter = counter + 1

# v2.0.2
(SET|counter|0)
(SET|counter|{$counter} + 1)
```

### Pattern 2: Conditional with Echo

```python
# v1.x
if hp < 20:
    ECHO Low health!

# v2.0.2
IF {$hp} < 20
    (ECHO|Low health!)
END IF
```

### Pattern 3: Loop with Counter

```python
# v1.x
i = 0
while i < 5:
    ECHO Count: {i}
    i = i + 1

# v2.0.2
(SET|i|0)
WHILE {$i} < 5
    (ECHO|Count: {$i})
    (SET|i|{$i} + 1)
END WHILE
```

### Pattern 4: Function with Return

```python
# v1.x
DEF double(x):
    return x * 2

result = double(10)

# v2.0.2
FUNCTION double($x)
    RETURN {$x} * 2
END FUNCTION

(SET|result|@double(10))
```

### Pattern 5: List Operations

```python
# v1.x
items = ["sword", "shield"]
items.append("potion")
for item in items:
    ECHO Item: {item}

# v2.0.2
(SET|items|[sword, shield])
(LIST APPEND|items|potion)
FOREACH item IN {$items}
    (ECHO|Item: {$item})
END FOREACH
```

### Pattern 6: File Operations

```python
# v1.x
# (Limited file support in v1.x)

# v2.0.2
(SET|content|(FILE READ|memory/notes.txt))
(FILE WRITE|memory/output.txt|{$content})
```

### Pattern 7: Nested Commands

```python
# v1.x
# (Limited nesting in v1.x)

# v2.0.2
(SET|data|(JSON PARSE|(FILE READ|memory/config.json)))
(SET|item|(LIST GET|inventory|(GET|index)))
```

---

## Breaking Changes

### 1. Variable Syntax (Required Change)

**v1.x:** `{var}`
**v2.0.2:** `{$var}`

**Impact:** All variable references must be updated.

**Migration:**
- Use find/replace: `{(\w+)}` → `{$\1}`
- Review system variables (MISSION, WORKFLOW, etc.)

### 2. Command Syntax (Required Change)

**v1.x:** Space-separated parameters
**v2.0.2:** Pipe-separated `(COMMAND|param1|param2)`

**Impact:** All commands must use new format.

**Migration:**
- Convert each command individually
- Check for nested commands (need proper parentheses)

### 3. Function Call Syntax (Required Change)

**v1.x:** `function_name(args)`
**v2.0.2:** `@function_name(args)`

**Impact:** All function calls need `@` prefix.

**Migration:**
- Add `@` before function names
- Update function definitions to `FUNCTION` / `END FUNCTION`

### 4. Parameter Naming (Required Change)

**v1.x:** `param`
**v2.0.2:** `$param`

**Impact:** Function parameters need `$` prefix.

**Migration:**
- Add `$` to parameter names in function definitions
- Update parameter references in function body

### 5. List Indexing (Behavior Change)

**v1.x:** `list[index]`
**v2.0.2:** `(LIST GET|list|index)`

**Impact:** Direct bracket access no longer supported.

**Migration:**
- Use `LIST GET` command
- Update all list access patterns

### 6. Math Operations (Improvement)

**v1.x:** Limited Python expressions
**v2.0.2:** Full PEMDAS support with `+`, `-`, `*`, `/`, `%`, `**`

**Impact:** Math expressions are more powerful but require explicit syntax.

**Migration:**
- Math expressions work better in v2.0.2
- Use parentheses for complex operations
- Variables auto-substitute in expressions

### 7. Conditionals (Syntax Change)

**v1.x:** Python-style indentation
**v2.0.2:** Explicit `END IF` markers

**Impact:** All conditionals need end markers.

**Migration:**
- Add `END IF` after conditional blocks
- Convert `elif` to `ELSE IF`
- No more indentation-based scoping

### 8. Loops (Syntax Change)

**v1.x:** Python-style `while` and `for`
**v2.0.2:** `WHILE` / `END WHILE` and `FOREACH` / `END FOREACH`

**Impact:** All loops need end markers.

**Migration:**
- Add `END WHILE` / `END FOREACH`
- Convert `for item in list:` to `FOREACH item IN list`

---

## Compatibility Mode

### Legacy v1.x Support

The v2.0.2 runtime **automatically detects** and supports v1.x syntax:

```python
# This v1.x script still works in v2.0.2!
SET name Alice
ECHO Hello, {name}!
```

**How it works:**
1. Runtime checks for v2.0.2 patterns (`{$var}`, `(COMMAND|...)`)
2. If none found, assumes v1.x syntax
3. Falls back to legacy interpreter
4. Executes with v1.x compatibility mode

**Limitations:**
- Legacy mode lacks new features (file I/O, enhanced lists, etc.)
- Error messages less detailed
- Performance slightly slower
- No access to v2.0.2 functions

### Gradual Migration

You can mix v1.x and v2.0.2 in separate files:

```
memory/scripts/
├── old_script.upy      # v1.x syntax (still works)
├── new_script.upy      # v2.0.2 syntax (new features)
└── hybrid_workflow.upy # Calls both (load separately)
```

**Best practice:** Migrate incrementally, one script at a time.

---

## Troubleshooting

### Common Errors

#### Error: "Variable 'var' not defined"

**Cause:** Forgot `$` prefix in variable reference.

```python
# Wrong
(ECHO|{var})

# Right
(ECHO|{$var})
```

#### Error: "Invalid command syntax"

**Cause:** Missing parentheses or pipes in command.

```python
# Wrong
ECHO message

# Right
(ECHO|message)
```

#### Error: "Function 'function' not found"

**Cause:** Missing `@` prefix in function call.

```python
# Wrong
function(args)

# Right
@function(args)
```

#### Error: "Unexpected END IF"

**Cause:** Mismatched conditional blocks.

```python
# Wrong
IF condition
    action
END WHILE  # Wrong end marker!

# Right
IF condition
    action
END IF
```

#### Error: "Invalid math expression"

**Cause:** Incorrect operator or syntax.

```python
# Wrong
(SET|result|{$x} plus {$y})

# Right
(SET|result|{$x} + {$y})
```

### Validation Tips

1. **Use VALIDATE command:**
   ```python
   VALIDATE memory/scripts/my_script.upy
   ```

2. **Check syntax patterns:**
   - All variables: `{$name}`
   - All commands: `(COMMAND|params)`
   - All functions: `@name()`
   - All blocks: END markers

3. **Test incrementally:**
   - Migrate one function at a time
   - Test after each change
   - Use version control

4. **Review logs:**
   - Check `memory/logs/runtime_errors.log`
   - Look for syntax warnings
   - Note deprecated patterns

### Getting Help

- **Documentation:** [uPY v2.0.2 Language Reference](uPY-v2.0.2-Language-Reference.md)
- **Examples:** `memory/ucode/examples/`
- **Tests:** `memory/ucode/test_upy_*.py` (see working patterns)
- **GitHub Issues:** Report migration bugs
- **Discord:** Ask in #upy-help channel

---

## Migration Timeline

### Recommended Schedule

**Week 1: Preparation**
- Backup all scripts
- Test current v1.x scripts
- Review migration guide
- Install migration tool

**Week 2: Small Scripts**
- Migrate simple scripts (<50 lines)
- Test and validate
- Get familiar with v2.0.2 syntax
- Document patterns

**Week 3: Medium Scripts**
- Migrate workflows and automation (50-200 lines)
- Use automated tool with review
- Test integrated functionality
- Update documentation

**Week 4: Large Scripts**
- Migrate complex scripts (200+ lines)
- Manual review required
- Extensive testing
- Performance validation

**Ongoing: Maintenance**
- Convert new scripts to v2.0.2
- Update old scripts as needed
- Monitor for issues
- Share migration experience

---

## Success Checklist

### Fully Migrated When:

- ✅ All variable references use `{$var}` syntax
- ✅ All commands use `(COMMAND|params)` format
- ✅ All functions use `@function()` calls
- ✅ All conditionals have `END IF` markers
- ✅ All loops have `END WHILE` / `END FOREACH` markers
- ✅ All function parameters have `$` prefix
- ✅ VALIDATE command passes
- ✅ Script execution matches v1.x behavior
- ✅ No warnings in runtime logs
- ✅ Documentation updated

---

## Additional Resources

- [uPY v2.0.2 Language Reference](uPY-v2.0.2-Language-Reference.md) - Complete syntax guide
- [uPY Runtime Architecture](uPY-Runtime-Architecture.md) - Technical implementation
- [Command Reference](Command-Reference.md) - All available commands
- [Function Programming Guide](Function-Programming-Guide.md) - Advanced patterns
- [Workflow System v2](Workflow-System-v2.md) - Mission automation

---

## Conclusion

Migrating to uPY v2.0.2 provides cleaner syntax, better performance, and access to new features. While the changes are significant, the automated migration tool and backward compatibility make the transition smooth.

**Key takeaways:**
- 🔄 Syntax changes are consistent and predictable
- 🤖 Automated tool handles most conversions
- 🔙 v1.x scripts still work (legacy mode)
- 📈 New features worth the migration effort
- 📚 Comprehensive documentation and examples available

**Happy migrating! 🚀**

---

**Version:** 2.0.2
**Last Updated:** December 5, 2025
**Maintainer:** @fredporter
**License:** MIT
