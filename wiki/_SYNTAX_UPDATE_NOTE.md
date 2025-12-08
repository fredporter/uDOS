# uPY Syntax Update - December 5, 2025

## What Changed (v1.x → v2.0)

### Core Syntax Rules (v2.0)

1. **SET command**: `SET (var|value)` with | separator only
2. **PRINT command**: `PRINT ['text']` with single quotes default
3. **$ prefix**: Only for string interpolation, NOT in assignments/conditions
4. **Conditionals**: Inline `{IF condition: COMMAND()}` syntax

### Migration Examples

**Old (v1.1.9):**
```upy
$NAME = 'Hero'
$HP = 100
PRINT("Hello, $NAME!")
IF {$HP <= 0 | PRINT("Dead")}
```

**New (v2.0):**
```upy
SET (NAME|'Hero')
SET (HP|100)
PRINT ['Hello, $NAME!']
{IF HP <= 0: PRINT ['Dead']}
```

## Updated Documentation

✅ **Updated to v2.0:**
- `wiki/uPY-Syntax-v2.md` - Complete v2.0 reference
- `wiki/uPY-Command-Set-Analysis.md` - Command inventory
- `wiki/uPY-Syntax-Rules.md` - Quick syntax rules
- `wiki/Adventure-Scripting.md` - All examples updated
- `wiki/uCODE-Syntax-Quick-Reference.md` - Rewritten for v2.0

⏳ **Archived (old v1.1.9 syntax):**
- `wiki/.archive/Tutorial-uPY-Quick-Start.md.v1.1.9`
- `wiki/.archive/uPY-Cheat-Sheet.md.v1.1.9`
- `wiki/.archive/uCODE-Syntax-Quick-Reference.md.old`

📝 **To Be Updated:**
- `wiki/Tutorial-uPY-Quick-Start.md` - Needs v2.0 rewrite
- `wiki/uPY-Cheat-Sheet.md` - Needs v2.0 rewrite
- `wiki/uCODE-Language.md` - Needs partial updates

## Key References

**Primary v2.0 Documentation:**
1. `wiki/uPY-Syntax-v2.md` - **START HERE** for v2.0 syntax
2. `wiki/uPY-Syntax-Rules.md` - Quick 3-rule reference
3. `wiki/Adventure-Scripting.md` - Complete examples

**Templates (v2.0 compliant):**
- `core/data/templates/adventure.template.upy`
- `core/data/templates/menu_system.upy`
- `core/data/templates/crud_app.upy`
- `core/data/templates/form_validation.upy`

**Test Files (v2.0 compliant):**
- `extensions/vscode/test-examples/feature-test.upy`
- `extensions/vscode/test-examples/water-filter-mission.upy`

## Migration Path for Users

1. **New projects**: Use v2.0 syntax (see wiki/uPY-Syntax-v2.md)
2. **Existing scripts**: Continue working (backward compatible)
3. **Gradual migration**: Update scripts as you edit them
4. **Reference**: Use Adventure-Scripting.md for examples

## For Developers

- Follow v2.0 syntax for all new code
- Use template files as reference
- Run tests to validate syntax compliance
- Update old examples as you encounter them

---

**Version:** uPY v2.0
**Date:** December 5, 2025
**Status:** Active - v2.0 is production standard
