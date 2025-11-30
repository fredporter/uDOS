# uCODE Syntax Quick Reference

**Version:** 1.1.2 (Modern Syntax with @variables)
**Last Updated:** November 30, 2025

---

## Modern Syntax (v1.1.1+)

### Output Commands

```uscript
# Modern PRINT command with space (preferred)
PRINT [Hello World]
PRINT []
PRINT [System: @name]

# Traditional spacing (still supported)
PRINT[Hello World]

# With variables - BOTH syntaxes work:
PRINT [User: @username]           # Clean @ syntax (recommended)
PRINT [User: ${username}]         # Traditional ${} syntax

# Multiple variables
PRINT [Value: @x, Status: @status]
PRINT [Found @count @item in @location]
```

### Variable Commands

```uscript
# SET - Assign variables (with space)
SET [name = Alice]
SET [count = 42]
SET [status = active]

# Traditional (no space, still works)
SET[name=Alice]

# GET - Retrieve variable value
GET [name]
GET [count]

# Variable references in expressions:
SET [total = @count + 10]
SET [message = Hello @name]
```

### Variable Syntax - Two Options

uCODE supports **two variable syntaxes** for maximum readability:

| Syntax | Example | Use Case |
|--------|---------|----------|
| `@variable` | `PRINT [@username]` | **Recommended** - Cleaner, more visual |
| `${variable}` | `PRINT [${username}]` | Traditional - Shell-style compatibility |

**Both work identically!** Use `@var` for cleaner code.

```uscript
# Example comparison:
SET [name = Alice]
SET [age = 30]
SET [city = Brisbane]

# Clean @ syntax (recommended)
PRINT [@name is @age years old and lives in @city]

# Traditional ${} syntax
PRINT [${name} is ${age} years old and lives in ${city}]

# Mix them if you want (but stay consistent)
PRINT [@name (age: ${age}) - @city]
```

### Conditional Commands

```uscript
# One-line IF with space before brace
IF {@x > 5} THEN PRINT [x is large]
IF {@status == "active"} THEN PRINT [System running]
IF {@count == 0} THEN PRINT [Empty]

# Multi-line IF blocks (for complex logic)
IF @x > 5
    PRINT [x is large]
    SET [result = pass]
ENDIF

IF @status == "active"
    PRINT [System active]
ELSE
    PRINT [System inactive]
ENDIF
```

### Template Strings

```uscript
# Variable substitution - use @var or ${var}
SET [name = Alice]
SET [age = 30]

PRINT [User: @name]                          # Clean
PRINT [@name is @age years old]              # Multiple vars
PRINT [System: @name (${status})]            # Can mix styles
```

---

## Syntax Comparison

### Output: ECHO vs PRINT

| Old Syntax (v1.0.x) | Modern Syntax (v1.1.2) |
|---------------------|------------------------|
| `ECHO "Hello"` | `PRINT [Hello]` |
| `ECHO "Value: " + var` | `PRINT [Value: @var]` |
| `ECHO ""` | `PRINT []` |

**Note:** ECHO is deprecated but still works. Use PRINT for new code.

### Variables: SET/GET

| Old Syntax | Modern Syntax (v1.1.2) |
|------------|------------------------|
| `SET name = "Alice"` | `SET [name = Alice]` |
| `ECHO "${name}"` | `PRINT [@name]` |
| `GET name` | `GET [name]` |

### Variable References

| Style | Syntax | Example |
|-------|--------|---------|
| **Modern** | `@variable` | `PRINT [Hello @name]` |
| Traditional | `${variable}` | `PRINT [Hello ${name}]` |
| Old (deprecated) | `$variable` | `PRINT "Hello $name"` |

---

## Style Guide

### Recommended Modern Style (v1.1.2+)

```uscript
# 1. Always use spaces after commands
SET [count = 0]           # ✅ Good
SET[count=0]              # ❌ Old style

# 2. Use @var for variables (cleaner)
PRINT [@count items]      # ✅ Recommended
PRINT [${count} items]    # ✅ Works but verbose

# 3. Space before braces in IF
IF {@status == "ok"}      # ✅ Good
IF{@status == "ok"}       # ❌ Old style

# 4. Consistent naming
SET [user_name = Alice]   # ✅ snake_case
SET [userName = Alice]    # ⚠️  camelCase works but inconsistent
SET [CONSTANT_VAL = 100]  # ✅ UPPER for constants
```

### Complete Example

```uscript
# Modern uCODE v1.1.2+ style
SET [app_name = uDOS]
SET [version = 1.1.2]
SET [status = active]
SET [user_count = 42]

PRINT [==============================]
PRINT [@app_name v@version]
PRINT [==============================]
PRINT [Status: @status]
PRINT [Users: @user_count]

IF {@status == "active"}
    PRINT [✅ System operational]
    SET [message = All systems go!]
ELSE
    PRINT [⚠️  System offline]
    SET [message = Maintenance mode]
ENDIF

PRINT [@message]
```

---

## Migration Guide

### Updating Old Scripts

**Old (v1.0.x):**
```uscript
SET name "Alice"
SET score 85
ECHO "User: ${name}"
ECHO "Score: ${score}"
IF{score > 80} THEN ECHO "Pass"
```

**New (v1.1.2+):**
```uscript
SET [name = Alice]
SET [score = 85]
PRINT [User: @name]
PRINT [Score: @score]
IF {@score > 80} THEN PRINT [Pass]
```

### Quick Find/Replace

1. `SET name` → `SET [name`
2. `ECHO "` → `PRINT [`
3. `${var}` → `@var` (optional but cleaner)
4. `IF{` → `IF {` (add space)

---

## Summary

✅ **Use Modern Syntax:**
- `PRINT [...]` with spaces
- `SET [var = value]` with spaces
- `@variable` for cleaner variable references
- `IF {@condition}` with space before brace

📘 **Both syntaxes work:**
- `@var` (recommended) and `${var}` (traditional)
- Choose one style and stay consistent

🔄 **Migration:**
- Old scripts still work
- Update gradually to modern syntax
- Use style guide for new code
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
PRINT[Starting process...]
PRINT[Step 1: Initialize]
PRINT[Step 2: Execute]
PRINT[Done!]
```

### Variables and Output
```uscript
SET[user = Alice]
SET[score = 95]
PRINT[User ${user} scored ${score}]
```

### Conditional Logic
```uscript
SET[score = 85]

IF{score >= 90} THEN PRINT[Grade: A]
IF{score >= 80} THEN PRINT[Grade: B]
IF{score < 60} THEN PRINT[Grade: F]
```

### Loops with Variables
```uscript
FOR item IN water fire shelter
    PRINT[Processing ${item}...]
    [KNOWLEDGE|SEARCH|${item}]
ENDFOR
```

### Error Handling
```uscript
TRY
    SET[result = dangerous_operation()]
    PRINT[Success: ${result}]
CATCH error
    PRINT[Error: ${error}]
ENDTRY
```

---

## Best Practices

### ✅ Do

- Use `PRINT[]` for new scripts
- Use template strings `${var}` for variable substitution
- Use one-line `IF{}` for simple conditions
- Use bracket syntax for consistency
- Quote strings in conditions: `IF{name == "Alice"}`

### ❌ Don't

- Use `ECHO` in new code (deprecated)
- Use old-style string concatenation with `+`
- Mix bracket styles inconsistently
- Forget quotes in string comparisons

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
