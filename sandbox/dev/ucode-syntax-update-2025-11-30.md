# uCODE Syntax Update - November 30, 2025

## Overview

Updated uCODE to v1.1.2 with improved formatting and cleaner variable syntax.

---

## Changes Made

### 1. Spacing Standards (Mandatory)

**Before (v1.1.1):**
```uscript
SET[name=value]
PRINT[text]
IF{condition}
```

**After (v1.1.2):**
```uscript
SET [name = value]
PRINT [text]
IF {@condition}
```

**Key Points:**
- Space after command name: `PRINT [` not `PRINT[`
- Spaces around `=` in assignments: `name = value`
- Space before `{` in conditionals: `IF {` not `IF{`

### 2. Variable Syntax - Two Options

Introduced `@variable` syntax as a cleaner alternative to `${variable}`:

| Syntax | Example | Use Case |
|--------|---------|----------|
| **@var** | `PRINT [@username]` | **Recommended** - Cleaner, more visual |
| `${var}` | `PRINT [${username}]` | Traditional - Still fully supported |

**Both work identically!** The interpreter supports both syntaxes.

**Examples:**
```uscript
SET [name = Alice]
SET [age = 30]

# Modern @ syntax (recommended)
PRINT [@name is @age years old]

# Traditional ${} syntax (still works)
PRINT [${name} is ${age} years old]

# Can mix (but stay consistent)
PRINT [@name (${age})]
```

### 3. Implementation

**Updated File: `core/interpreters/ucode.py`**

```python
def substitute_variables(self, text: str) -> str:
    """
    Substitute variable placeholders in text.

    Supports two syntaxes:
    - ${variable} - Traditional shell-style (backward compatible)
    - @variable - Modern clean syntax (v1.1.2+)
    """
    def replacer(match):
        var_name = match.group(1)
        value = self.get_variable(var_name)
        if value is None:
            return match.group(0)
        return str(value)

    # Substitute ${variable} syntax
    text = re.sub(r'\$\{(\w+)\}', replacer, text)

    # Substitute @variable syntax (v1.1.2+)
    text = re.sub(r'@(\w+)', replacer, text)

    return text
```

---

## Files Updated

### Core Files
1. **`core/interpreters/ucode.py`**
   - Updated `substitute_variables()` method
   - Added support for `@variable` syntax
   - Maintains backward compatibility with `${variable}`

### Documentation
2. **`wiki/uCODE-Syntax-Quick-Reference.md`**
   - Complete rewrite for v1.1.2
   - Added `@variable` documentation
   - Added style guide section
   - Added migration guide
   - Added comparison tables

### Example Files
3. **`sandbox/tests/simple_shakedown.uscript`**
   - Updated all spacing: `SET [...]`, `PRINT [...]`
   - Changed all `${var}` to `@var`
   - Updated `IF [...]` syntax

4. **`sandbox/ucode/v1.1.1-modern-syntax-test.uscript`**
   - Updated to v1.1.2 standards
   - Added @ syntax examples
   - Added comparison section

5. **`sandbox/ucode/modern-style-showcase.uscript`** (NEW)
   - Comprehensive style guide examples
   - 10 sections demonstrating best practices
   - Shows both `@var` and `${var}` syntaxes

6. **`core/data/templates/menu_system.uscript`**
   - Updated spacing throughout
   - Changed to `@variable` syntax
   - Modernized all commands

### Archived Files
7. **Moved to `sandbox/trash/old-uscript-tests/`:**
   - `test_diagram_generate.uscript`
   - `test_draw_command.uscript`
   - `test_else_brackets.uscript`
   - `test_peek.uscript`
   - `test_poke.uscript`
   - `test_print.uscript`
   - `test_square_brackets.uscript`
   - `test_startup.uscript`

---

## Style Guide

### Recommended Modern Style (v1.1.2+)

```uscript
# ✅ GOOD - Modern v1.1.2+ style

# 1. Spacing
SET [count = 0]              # Space after command, around =
PRINT [Hello World]          # Space after command
IF {@status == "ok"}         # Space before brace

# 2. Variables
PRINT [@count items]         # @ syntax (recommended)
PRINT [User: @name]          # Clean and readable

# 3. Naming
SET [user_name = Alice]      # snake_case for variables
SET [MAX_SIZE = 100]         # UPPER for constants

# 4. Multi-line
IF @value > 10
    PRINT [Large value: @value]
    SET [category = high]
ENDIF
```

```uscript
# ❌ BAD - Old cramped style

SET[count=0]                 # No spaces
PRINT[text]                  # Cramped
IF{status == "ok"}           # No space before brace
PRINT[${count} items]        # Verbose ${} syntax
```

### Complete Example

```uscript
# Modern uCODE v1.1.2 Example
SET [app_name = uDOS]
SET [version = 1.1.2]
SET [user_count = 42]

PRINT [================================]
PRINT [@app_name v@version]
PRINT [================================]
PRINT [Active Users: @user_count]

IF {@user_count > 40}
    PRINT [✅ High activity!]
    SET [status = busy]
ELSE
    PRINT [📊 Normal load]
    SET [status = normal]
ENDIF

PRINT [Status: @status]
```

---

## Migration Guide

### Quick Find/Replace

For bulk updates of old scripts:

1. **Add spacing:**
   - `SET[` → `SET [`
   - `PRINT[` → `PRINT [`
   - `IF{` → `IF {`

2. **Modernize variables (optional):**
   - `${var}` → `@var`

3. **Add spaces in assignments:**
   - `name=value` → `name = value`

### Automated Script

```bash
# Quick sed replacements (macOS/Linux)
sed -i '' 's/SET\[/SET [/g' file.uscript
sed -i '' 's/PRINT\[/PRINT [/g' file.uscript
sed -i '' 's/IF{/IF {/g' file.uscript
sed -i '' 's/\${/\@/g; s/}//g' file.uscript  # ${var} → @var
```

### Manual Migration

**Before (v1.1.1):**
```uscript
SET name "Alice"
SET score 85
PRINT "User: ${name}"
PRINT "Score: ${score}"
IF{score > 80} THEN PRINT "Pass"
```

**After (v1.1.2):**
```uscript
SET [name = Alice]
SET [score = 85]
PRINT [User: @name]
PRINT [Score: @score]
IF {@score > 80} THEN PRINT [Pass]
```

---

## Backward Compatibility

✅ **Fully backward compatible!**

- Old `${variable}` syntax still works
- Old `SET[var=value]` still works (but discouraged)
- Old `PRINT[text]` still works (but discouraged)

**Recommendation:** Update new scripts to v1.1.2 style, migrate old scripts gradually.

---

## Testing

### Test Files

1. **`sandbox/tests/simple_shakedown.uscript`**
   - Tests basic commands with new syntax
   - Uses `@variable` throughout
   - Demonstrates modern spacing

2. **`sandbox/ucode/modern-style-showcase.uscript`**
   - Comprehensive demonstration
   - 10 sections covering all features
   - Shows both `@var` and `${var}` syntaxes

3. **`sandbox/ucode/v1.1.1-modern-syntax-test.uscript`**
   - Updated syntax test
   - Comparison examples
   - Escape sequence tests

### Run Tests

```bash
# Test modern syntax
./start_udos.sh sandbox/ucode/modern-style-showcase.uscript

# Test shakedown
./start_udos.sh sandbox/tests/simple_shakedown.uscript

# Test v1.1.1 compatibility
./start_udos.sh sandbox/ucode/v1.1.1-modern-syntax-test.uscript
```

---

## Benefits

### 1. Cleaner Code
```uscript
# Before
PRINT[Found ${count} ${item} in ${location}]

# After
PRINT [Found @count @item in @location]
```

### 2. Better Readability
- Space after commands makes code more scannable
- `@variable` is shorter and cleaner than `${variable}`
- Consistent spacing improves visual parsing

### 3. Modern Best Practices
- Follows contemporary scripting language conventions
- Similar to Ruby's `@instance_var` and PHP's `$var`
- More visual distinction between text and variables

### 4. Flexibility
- Both syntaxes supported
- Choose based on preference
- Can mix in same script (not recommended)

---

## Summary

✅ **Improvements:**
- Mandatory spacing for readability: `PRINT [text]`
- New `@variable` syntax (recommended)
- Traditional `${variable}` still works
- Updated all templates and examples
- Comprehensive documentation

📚 **Documentation:**
- Updated Quick Reference with v1.1.2 syntax
- Added style guide and migration guide
- Created modern-style-showcase.uscript

🔄 **Migration:**
- Fully backward compatible
- Update new scripts immediately
- Migrate old scripts gradually

🎯 **Next Steps:**
- Use `@var` syntax in all new scripts
- Update templates as needed
- Educate users via updated wiki

---

**Version:** uCODE v1.1.2
**Date:** November 30, 2025
**Status:** ✅ Complete & Tested
