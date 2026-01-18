# uPY Syntax Migration Tool (v1.2.24)

Automated tool to upgrade existing `.upy` files from legacy syntax to Python-first format.

## What Gets Upgraded

### 1. Command Arguments: Commas → Pipes

**Old syntax:**
```upy
PRINT["Water level", "at", "50%"]
GUIDE["water/purification", "detailed"]
```

**New syntax:**
```upy
PRINT["Water level"|"at"|"50%"]
GUIDE["water/purification"|"detailed"]
```

### 2. Tags: Double-dash → Asterisk

**Old syntax:**
```upy
CLONE--dev
BACKUP--auto
CHECKPOINT--save
```

**New syntax:**
```upy
CLONE*DEV
BACKUP*AUTO
CHECKPOINT*SAVE
```

Note: Tags are automatically UPPERCASED for visual prominence.

### 3. Variable Name Validation

The tool checks for forbidden characters in variable names:

**Forbidden:** `` `~@#$%^&*[]{}'"<>\|_ ``

**Common issues:**
- Underscores: `{$player_name}` → Should be `{$player-name}`
- Special chars: `{$level#1}` → Should be `{$level-1}`

**Note:** uCODE uses dashes (`-`) not underscores (`_`). The smart editor automatically converts:
- `.upy` format: `{$player-hp}`
- Python execution: `player_hp`

## Usage

### Basic Usage

```bash
# Upgrade a single file
python dev/tools/upgrade_upy_syntax.py memory/ucode/scripts/water.upy

# Upgrade entire directory (recursive)
python dev/tools/upgrade_upy_syntax.py memory/ucode/scripts/

# Upgrade all ucode files
python dev/tools/upgrade_upy_syntax.py memory/ucode/
```

### Dry-Run Mode (Preview Changes)

**Always test first with dry-run:**

```bash
# Preview changes without modifying files
python dev/tools/upgrade_upy_syntax.py --dry-run memory/ucode/scripts/

# Check specific file
python dev/tools/upgrade_upy_syntax.py --dry-run memory/ucode/scripts/water.upy
```

Output shows:
- Files that would be upgraded
- Number of commas/tags to convert
- Warnings about forbidden characters
- No files are modified

### Non-Recursive Mode

```bash
# Only scan current directory (not subdirectories)
python dev/tools/upgrade_upy_syntax.py --no-recursive memory/ucode/scripts/
```

## Output Example

```
============================================================
uPY SYNTAX MIGRATION TOOL (v1.2.24)
============================================================
Target: /Users/fredbook/Code/uDOS/memory/ucode/scripts/
Mode: DRY RUN
============================================================

🔍 Would upgrade: scripts/water.upy
🔍 Would upgrade: scripts/fire.upy
✓ Already up-to-date: scripts/shelter.upy

============================================================
UPGRADE STATISTICS
============================================================
Files scanned:      3
Files modified:     2
Commas converted:   12
Tags converted:     8
Warnings:           3

============================================================
WARNINGS
============================================================
⚠️  scripts/water.upy: Variable '{$player_name}' uses underscores - 
    uCODE uses dashes: {$player-name}
⚠️  scripts/fire.upy: Variable '{$fire_level}' uses underscores - 
    uCODE uses dashes: {$fire-level}
⚠️  scripts/fire.upy: Variable '{$temp#1}' contains forbidden characters: ['#']

============================================================
DRY RUN - No files were modified
Run without --dry-run to apply changes
============================================================
```

## Safety Features

### 1. Backup Files

Original files are backed up with `.bak` extension:

```
water.upy      ← Upgraded version
water.upy.bak  ← Original backup
```

**To restore:**
```bash
mv water.upy.bak water.upy
```

### 2. Warning System

The tool warns about:
- Variables with forbidden characters
- Underscores in variable names (should use dashes)
- Python functions with dashes (should use underscores)

### 3. Quote-Aware Parsing

The tool ONLY replaces commas outside of quotes:

```upy
# This comma stays (inside quotes)
PRINT["Hello, world!"]

# These commas convert (command arguments)
PRINT["Hello", "world"]  →  PRINT["Hello"|"world"]
```

## What Doesn't Need Upgrading

### 1. Emoji Codes

Emoji codes are already in the new format:

```upy
PRINT["Score: :sb:100:eb: | Health: :dollar:50"]
```

These are preserved as-is.

### 2. Python Code

Pure Python code is not modified:

```python
# This stays unchanged
def check_status():
    hp = get_var("player_hp", 100)
    return hp
```

### 3. Comments and Strings

Comments and string content are preserved:

```upy
# This is a comment with commas, dashes, and other chars
PRINT["This string has commas, too"]  # But args are converted
```

## Common Issues

### Issue 1: Variables with Underscores

**Problem:**
```
⚠️ Variable '{$player_name}' uses underscores
```

**Solution:**
Manually rename in your .upy file:
```upy
# Before
{$player_name} = "Hero"

# After
{$player-name} = "Hero"
```

The smart editor will convert to `player_name` for Python execution.

### Issue 2: Forbidden Characters

**Problem:**
```
⚠️ Variable '{$level#1}' contains forbidden characters: ['#']
```

**Solution:**
Use only alphanumeric + dash:
```upy
# Before
{$level#1} = 10

# After
{$level-1} = 10
```

### Issue 3: Mixed Old/New Syntax

If a file already has some new syntax, the tool safely upgrades only the old parts:

```upy
# Already upgraded (no change)
PRINT["Water"|"50%"]

# Needs upgrade
PRINT["Fire", "80%"]  →  PRINT["Fire"|"80%"]
```

## Migration Workflow

### Step 1: Dry-Run Entire Codebase

```bash
python dev/tools/upgrade_upy_syntax.py --dry-run memory/ucode/
```

Review the output and warnings.

### Step 2: Fix Critical Issues

Address warnings about forbidden characters manually.

### Step 3: Upgrade Scripts Directory

```bash
# Backup first (optional)
cp -r memory/ucode/scripts memory/ucode/scripts.backup

# Upgrade
python dev/tools/upgrade_upy_syntax.py memory/ucode/scripts/
```

### Step 4: Test Upgraded Files

```bash
./start_udos.sh memory/ucode/scripts/water.upy
```

Verify the script runs correctly.

### Step 5: Upgrade Other Directories

```bash
python dev/tools/upgrade_upy_syntax.py memory/ucode/examples/
python dev/tools/upgrade_upy_syntax.py memory/ucode/adventures/
```

## Advanced Usage

### Upgrade and Capture Report

```bash
python dev/tools/upgrade_upy_syntax.py memory/ucode/ > migration-report.txt 2>&1
```

### Find Files with Specific Issues

```bash
# Find files with underscores
python dev/tools/upgrade_upy_syntax.py --dry-run memory/ucode/ | grep underscore

# Find files needing upgrade
python dev/tools/upgrade_upy_syntax.py --dry-run memory/ucode/ | grep "Would upgrade"
```

## Performance

The migration tool is fast:
- **~100 files/second** on typical hardware
- **Smart parsing** (only processes .upy files)
- **Minimal memory** (processes one file at a time)

## Getting Help

```bash
python dev/tools/upgrade_upy_syntax.py --help
```

## Related Documentation

- **ROADMAP.md** - v1.2.24 Python-first architecture
- **wiki/uCODE-Python-Guide.md** - Complete Python syntax guide
- **core/ui/ucode_editor.py** - Smart editor implementation
- **core/udos_core.py** - Python-first core API

## Quick Reference

| Old Syntax | New Syntax | Example |
|------------|------------|---------|
| Commas in commands | Pipes | `PRINT["a", "b"]` → `PRINT["a"\|"b"]` |
| Double-dash tags | Asterisk tags | `CLONE--dev` → `CLONE*DEV` |
| Underscores in vars | Dashes | `{$player_name}` → `{$player-name}` |
| Forbidden chars | Alphanumeric + dash | `{$level#1}` → `{$level-1}` |

## Support

If you encounter issues:

1. Check the warnings output
2. Review this README
3. Test with `--dry-run` first
4. Keep `.bak` backups for safety
5. Report bugs in GitHub issues

---

**Version:** v1.2.24 Week 3  
**Status:** ✅ Production Ready  
**Last Updated:** December 13, 2025
