# uPY v2.0.1 Syntax Update

**Date:** December 5, 2025
**Status:** Complete

---

## What Changed

**v2.0.0 → v2.0.1**: Distinct bracket types for clarity

### New Syntax

```upy
{$variable}      # All variables (assignment, interpolation, system)
(command|params) # Commands and functions
[condition]      # Conditionals only
```

### Key Differences from v2.0.0

| Element | v2.0.0 | v2.0.1 | Why |
|:--------|:-------|:-------|:----|
| **Variables** | `SET (name\|'Alice')` | `SET {$name\|'Alice'}` | Consistent $ prefix |
| **Interpolation** | `PRINT ['text $var']` | `PRINT ('text {$var}')` | Clear delimiter |
| **Conditionals** | `{IF hp < 30: ...}` | `[IF {$hp} < 30: ...]` | Distinct brackets |
| **Commands** | `PRINT ['text']` | `PRINT ('text')` | Simpler quotes |
| **System vars** | `$SPRITE-HP` | `{$SPRITE-HP}` | Consistent with user vars |

---

## Rationale

### 1. Visual Distinction

Three bracket types = three syntactic purposes:

- **`{$variable}`** - Curly braces = data containers
- **`(command)`** - Parentheses = actions/functions (Python-like)
- **`[condition]`** - Square brackets = control flow

### 2. Consistent Variables

**Always `{$}`** - No confusion:

```upy
SET {$hp|100}                    # Assignment
PRINT ('HP: {$hp}')              # Interpolation
[IF {$hp} < 30: PRINT ('Low!')]  # Condition
PRINT ('{$SPRITE-HP}')           # System var
```

### 3. Parser-Friendly

Clear delimiters for different states:
- `{` → variable mode
- `(` → parameter/command mode
- `[` → conditional mode

### 4. Human-Readable

Obvious bracket purpose:
- Need a variable? **`{$name}`**
- Need a command? **`(command)`**
- Need a condition? **`[IF ...]`**

---

## Migration Guide

### Automated Migration

```bash
python dev/tools/migrate_to_v2_0_1.py memory/ucode/
```

### Manual Find/Replace

#### Variables in Assignments

```bash
# Before (v2.0.0)
SET (name|'Hero')
SET (hp|100)
SET (level|1)

# After (v2.0.1)
SET {$name|'Hero'}
SET {$hp|100}
SET {$level|1}
```

#### Variables in Strings

```bash
# Before (v2.0.0)
PRINT ['Hello $name!']
PRINT ['HP: $hp/$max_hp']

# After (v2.0.1)
PRINT ('Hello {$name}!')
PRINT ('HP: {$hp}/{$max_hp}')
```

#### Conditionals

```bash
# Before (v2.0.0)
{IF hp < 30: PRINT ['Low!']}
{IF level >= 5: XP [+50]}

# After (v2.0.1)
[IF {$hp} < 30: PRINT ('Low!')]
[IF {$level} >= 5: XP (+50)]
```

#### Commands

```bash
# Before (v2.0.0)
XP [+50]
HP [-10]
ITEM [sword]
PRINT ['text']

# After (v2.0.1)
XP (+50)
HP (-10)
ITEM (sword)
PRINT ('text')
```

#### System Variables

```bash
# Before (v2.0.0)
PRINT ['Location: $SPRITE-LOCATION']
PRINT ['Mission: $MISSION.NAME']

# After (v2.0.1)
PRINT ('Location: {$SPRITE-LOCATION}')
PRINT ('Mission: {$MISSION.NAME}')
```

---

## Updated Files

### Documentation (Complete ✅)

- **wiki/uCODE-Language.md** - Complete language spec (v2.0.1, 975 lines)
- **wiki/uPY-Syntax-v2.0.1.md** - NEW complete syntax reference
- **wiki/uPY-Syntax-Rules.md** - NEW quick reference card

### Archived (v2.0.0)

- **wiki/.archive/uCODE-Language.md.v1.1.9** - Old v1.1.9 version
- **wiki/.archive/uPY-Syntax-v2.0.0.md** - Old v2.0.0 syntax guide
- **wiki/.archive/uPY-Syntax-Rules.v2.0.0.md** - Old v2.0.0 quick ref

### Pending Updates

These files still need v2.0.1 migration:

#### Templates
- [ ] `core/data/templates/adventure.template.upy`
- [ ] `core/data/templates/menu_system.upy`
- [ ] `core/data/templates/crud_app.upy`
- [ ] `core/data/templates/form_validation.upy`

#### Test Files
- [ ] `extensions/vscode/test-examples/feature-test.upy`
- [ ] `extensions/vscode/test-examples/water-filter-mission.upy`

#### Wiki Documentation
- [ ] `wiki/Adventure-Scripting.md` - All 30+ examples
- [ ] `wiki/Function-Programming-Guide.md` - Function examples
- [ ] `wiki/uCODE-Syntax-Quick-Reference.md` - Quick ref

#### Development Files
- [ ] `memory/ucode/**/*.upy` - Core distributable scripts
- [ ] `dev/sessions/**/*.md` - Session notes with examples

---

## Testing Plan

### 1. Syntax Validation

```bash
# Test parser with new syntax
python -m pytest memory/tests/test_upy_parser_v2_0_1.py -v
```

### 2. Template Validation

```bash
# Validate all templates parse correctly
for file in core/data/templates/*.upy; do
    echo "Testing $file"
    ./start_udos.sh RUN "$file"
done
```

### 3. Example Scripts

```bash
# Run test examples
./start_udos.sh RUN extensions/vscode/test-examples/feature-test.upy
./start_udos.sh RUN extensions/vscode/test-examples/water-filter-mission.upy
```

---

## Next Steps

### Phase 1: Core Templates (Priority 1)

Update 4 template files in `core/data/templates/`:
1. adventure.template.upy
2. menu_system.upy
3. crud_app.upy
4. form_validation.upy

**Command:**
```bash
python dev/tools/migrate_to_v2_0_1.py core/data/templates/
```

### Phase 2: Test Files (Priority 1)

Update 2 test files in `extensions/vscode/test-examples/`:
1. feature-test.upy
2. water-filter-mission.upy

**Command:**
```bash
python dev/tools/migrate_to_v2_0_1.py extensions/vscode/test-examples/
```

### Phase 3: Wiki Examples (Priority 2)

Update wiki documentation files:
1. Adventure-Scripting.md (30+ examples)
2. Function-Programming-Guide.md
3. uCODE-Syntax-Quick-Reference.md

**Manual update recommended** (more nuanced, prose text)

### Phase 4: Development Files (Priority 3)

Update development workspace:
1. memory/ucode/**/*.upy
2. dev/sessions/**/*.md (examples only)

**Command:**
```bash
python dev/tools/migrate_to_v2_0_1.py memory/ucode/
```

---

## Backward Compatibility

### Parser Support

The uPY parser should support **both** v2.0.0 and v2.0.1 during transition:

```python
# In core/interpreters/upy_parser.py
class UPYParser:
    def __init__(self, strict_mode=False):
        self.strict_mode = strict_mode  # False = accept both, True = v2.0.1 only
```

### Version Detection

```python
def detect_syntax_version(script_content):
    """Auto-detect v2.0.0 vs v2.0.1 syntax."""
    if re.search(r'SET \{\$\w+\|', script_content):
        return '2.0.1'
    elif re.search(r'SET \(\w+\|', script_content):
        return '2.0.0'
    else:
        return 'unknown'
```

### Migration Warnings

```bash
# When running old syntax
> RUN old_script.upy

⚠️  Warning: Script uses v2.0.0 syntax
   Consider migrating to v2.0.1
   Run: python dev/tools/migrate_to_v2_0_1.py old_script.upy
```

---

## Benefits

### 1. Clarity

Three distinct bracket types eliminate ambiguity:
- Variables? `{$var}`
- Commands? `(cmd)`
- Conditions? `[IF]`

### 2. Consistency

Variables always use `{$}` - no exceptions:
- Assignment: `SET {$hp|100}`
- Interpolation: `'{$hp}'`
- Conditions: `[IF {$hp} < 30]`
- System: `{$SPRITE-HP}`

### 3. Learnability

Simple mental model:
- **Curly** = holds data
- **Parentheses** = does actions
- **Square** = controls flow

### 4. Tooling

Easier syntax highlighting, linting, formatting:
```regex
{$\w+}         # Variables (green)
\(\w+\)        # Commands (yellow)
\[IF.*?\]      # Conditionals (blue)
```

---

## Summary

✅ **Completed:**
- uCODE-Language.md updated (975 lines, v2.0.1)
- uPY-Syntax-v2.0.1.md created (complete reference)
- uPY-Syntax-Rules.md created (quick card)
- Old files archived

⏳ **Pending:**
- 4 template files
- 2 test files
- 3 wiki documentation files
- Development workspace files

🎯 **Goal:**
Clean, consistent, learnable syntax with distinct visual markers for different language elements.

---

**Version:** uPY v2.0.1
**Date:** December 5, 2025
**Maintainer:** @fredporter
