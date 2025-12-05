# uCODE Syntax Quick Reference

**Version:** 2.0.0 (uPY v2.0 - Clean Minimal Syntax)
**Last Updated:** December 5, 2025

---

## Modern Syntax (v2.0)

### Output Commands

```uscript
# PRINT command with single quotes (preferred)
PRINT ['Hello World']
PRINT []
PRINT ['System: $name']

# With variables - $ for interpolation only:
PRINT ['User: $username']           # Clean syntax (recommended)
PRINT ['Value: $x, Status: $status']

# Multiple variables
PRINT ['Found $count $item in $location']
```

### Variable Commands

```uscript
# SET - Assign variables (| separator, no $ in assignment)
SET (name|'Alice')
SET (count|42)
SET (status|'active')

# GET - Retrieve variable value
GET [name]
GET [count]

# Variable references in expressions:
SET (total|count + 10)
SET (message|'Hello $name')
```

### Variable Syntax - Single Style

uPY v2.0 uses **$ only for string interpolation**:

| Context | Syntax | Example |
|---------|--------|---------|
| **Assignment** | No $ | `SET (username|'Alice')` |
| **Interpolation** | Use $ | `PRINT ['Hello $username']` |
| **Conditions** | No $ | `{IF count > 5: ...}` |

**Rule:** $ only when interpolating into strings.

```uscript
# Example:
SET (name|'Alice')
SET (age|30)
SET (city|'Brisbane')

# Clean $ syntax (interpolation only)
PRINT ['$name is $age years old and lives in $city']
```

### Conditional Commands

```uscript
# Inline IF with curly braces
{IF x > 5: PRINT ['x is large']}
{IF status == 'active': PRINT ['System running']}
{IF count == 0: PRINT ['Empty']}
```

### Template Strings

# Variable substitution - use $ for interpolation
SET (name|'Alice')
SET (age|30)

PRINT ['User: $name']                       # Clean
PRINT ['$name is $age years old']           # Multiple vars
```

---

## Syntax Comparison

### Output: ECHO vs PRINT

| Old Syntax (v1.x) | Modern Syntax (v2.0) |
|-------------------|----------------------|
| `ECHO "Hello"` | `PRINT ['Hello']` |
| `ECHO "Value: " + var` | `PRINT ['Value: $var']` |
| `ECHO ""` | `PRINT []` |

**Note:** ECHO is deprecated. Use PRINT.

### Variables: SET/GET

| Old Syntax | Modern Syntax (v2.0) |
|------------|----------------------|
| `SET name = "Alice"` | `SET (name|'Alice')` |
| `ECHO "${name}"` | `PRINT ['$name']` |
| `GET name` | `GET [name]` |

### Variable References

| Style | Syntax | Example |
|-------|--------|---------|
| **v2.0** | `$variable` | `PRINT ['Hello $name']` |
| Old (v1.x) | `@variable` | Deprecated |
| Old (v1.x) | `${variable}` | Deprecated |---

## Style Guide

### Recommended Modern Style (v2.0)

```uscript
# 1. Use | separator in SET (no spaces/commas/asterisks)
SET (count|0)             # ✅ Good
SET (count | 0)           # ❌ No spaces around |
SET (count, 0)            # ❌ No commas

# 2. Use $ only for interpolation
PRINT ['$count items']    # ✅ Recommended
SET (count|42)            # ✅ No $ in assignment
{IF count > 5: ...}       # ✅ No $ in conditions

# 3. Use single quotes (default)
PRINT ['Hello']           # ✅ Good
PRINT ["Hello"]           # ✅ Works but prefer '

# 4. Consistent naming
SET (user_name|'Alice')   # ✅ snake_case
SET (CONSTANT_VAL|100)    # ✅ UPPER for constants
```

### Complete Example

```uscript
# Modern uPY v2.0 style
SET (app_name|'uDOS')
SET (version|'2.0')
SET (status|'active')
SET (user_count|42)

PRINT [==============================]
PRINT ['$app_name v$version']
PRINT [==============================]
PRINT ['Status: $status']
PRINT ['Users: $user_count']

{IF status == 'active': PRINT ['✅ System operational']}
{IF status == 'active': SET (message|'All systems go!')}
{IF status != 'active': PRINT ['⚠️  System offline']}
{IF status != 'active': SET (message|'Maintenance mode')}

PRINT ['$message']
```

---

## Migration Guide

### Updating Old Scripts

**Old (v1.x):**
```uscript
SET name "Alice"
SET score 85
ECHO "User: ${name}"
ECHO "Score: ${score}"
IF{score > 80} THEN ECHO "Pass"
```

**New (v2.0):**
```uscript
SET (name|'Alice')
SET (score|85)
PRINT ['User: $name']
PRINT ['Score: $score']
{IF score > 80: PRINT ['Pass']}
```

### Quick Find/Replace

1. `SET [name = value]` → `SET (name|value)`
2. `ECHO "text"` → `PRINT ['text']`
3. `@var` → `$var` (in interpolation)
4. `${var}` → `$var` (simpler)
5. `IF {condition}` → `{IF condition: COMMAND()}`

---

## Summary

✅ **Use v2.0 Syntax:**
- `PRINT ['...']` with single quotes
- `SET (var|value)` with | separator
- `$variable` for string interpolation only
- `{IF condition: COMMAND()}` inline conditionals

📘 **Key Rules:**
- No $ in assignments: `SET (name|'Alice')` not `SET ($name|'Alice')`
- No $ in conditions: `{IF count > 5: ...}` not `{IF $count > 5: ...}`
- $ only for interpolation: `PRINT ['Hello $name']`

🔄 **Migration:**
- Old scripts may need syntax updates
- Use v2.0 syntax for all new code
- Follow minimal Python-like style
| `SET var = "value"` | `SET[var = value]` |
| `SET count = 10` | `SET[count = 10]` |
| `GET var` | `GET[var]` |

### Conditionals: IF

| Old Syntax | Modern Syntax |
|------------|---------------|
| Multi-line only | `IF{x > 5} THEN PRINT[Large]` |
| `IF x > 5`<br>`  ECHO "Large"`<br>`ENDIF` | `IF{x > 5} THEN PRINT[Large]` |

---

## Module/Extension Syntax

```uscript
# Standard module command syntax
[MODULE|COMMAND|param1|param2]
[MODULE|COMMAND*param1*param2]

# Examples
[SYSTEM|STATUS]
[FILE|READ|path/to/file.txt]
[PANEL|CREATE*map*120*60*9]
[KNOWLEDGE|SEARCH|water purification]
```

---

## Bracket Notation Styles

uCODE supports three equivalent bracket formats:

### Format 1: COMMAND[params]
```uscript
PRINT[Hello World]
SET[x = 10]
GET[name]
```

### Format 2: COMMAND [params]
```uscript
PRINT [Hello World]
SET [x = 10]
GET [name]
```

### Format 3: [COMMAND|params]
```uscript
[PRINT|Hello World]
[SET|x = 10]
[GET|name]
```

**All three formats are equivalent** - use what feels most readable for your use case.

---

## Special Characters

### Reserved for uCODE Syntax
- `~` Tilde
- `^` Caret
- `-` Hyphen/minus (in expressions)
- `+` Plus (in expressions)
- `=` Equals (in SET)
- `|` Pipe (in module commands)
- `<` `>` Less/greater than (in comparisons)
- `*` Asterisk (in module params)

### Variable Substitution
- `$` Dollar sign (for variables)
- `{` `}` Curly braces (for ${var} templates)

---

## Common Patterns

### Simple Output
```uscript
PRINT ['Starting process...']
PRINT ['Step 1: Initialize']
PRINT ['Step 2: Execute']
PRINT ['Done!']
```

### Variables and Output
```uscript
SET (user|'Alice')
SET (score|95)
PRINT ['User $user scored $score']
```

### Conditional Logic
```uscript
SET (score|85)

{IF score >= 90: PRINT ['Grade: A']}
{IF score >= 80: PRINT ['Grade: B']}
{IF score < 60: PRINT ['Grade: F']}
```

### Loops with Variables
```uscript
FOREACH item IN ['water'|'fire'|'shelter']
  PRINT ['Processing $item...']
  [KNOWLEDGE|SEARCH|$item]
END_FOR
```

---

## Best Practices

### ✅ Do

- Use `PRINT ['...']` with single quotes
- Use `SET (var|value)` with | separator
- Use $ only for string interpolation: `'$var'`
- Use inline `{IF condition: CMD()}` for simple logic
- Quote strings in conditions: `{IF name == 'Alice': ...}`

### ❌ Don't

- Use `ECHO` (deprecated, use PRINT)
- Use $ in assignments: `SET ($var|...)` is wrong
- Use $ in conditions: `{IF $count > 5: ...}` is wrong
- Mix separators: use | only (no commas, spaces, asterisks)
- Use complex nested conditionals (use BRANCH/LABEL instead)

---

## Migration Guide

### From v1.0.x to v1.1.1

1. **Replace ECHO with PRINT:**
   ```uscript
   # Old
   ECHO "Hello World"

   # New
   PRINT[Hello World]
   ```

2. **Use bracket syntax for SET/GET:**
   ```uscript
   # Old
   SET name = "Alice"
   GET name

   # New
   SET[name = Alice]
   GET[name]
   ```

3. **Use template strings:**
   ```uscript
   # Old
   ECHO "User: " + name

   # New
   PRINT[User: ${name}]
   ```

4. **Simplify single-line conditionals:**
   ```uscript
   # Old
   IF x > 5
       ECHO "Large"
   ENDIF

   # New
   IF{x > 5} THEN PRINT[Large]
   ```

---

## Version History

- **v1.1.1** (Nov 2025): Modern syntax - PRINT[], SET[], GET[], IF{}, template strings
- **v1.0.x** (2024-2025): Classic syntax - ECHO, traditional IF/ENDIF
- **v0.x** (2024): Early development

---

## See Also

- [uCODE Language Specification](uCODE-Language.md)
- [Command Reference](Command-Reference.md)
- [Getting Started](Getting-Started.md)
- [Template Examples](../core/data/templates/)
