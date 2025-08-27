# uDOS Variable System Quick Reference

## 🎯 Quick Variable Access

### Bash/Shell (Commands & Functions)
```bash
# Variable Manager
./uCORE/code/variable-manager.sh SET USER-ROLE WIZARD
./uCORE/code/variable-manager.sh GET USER-ROLE
./uCORE/code/variable-manager.sh LIST system

# Environment Variables (auto-exported)
echo $UDOS_USER_ROLE      # Current user role
echo $UDOS_DISPLAY_MODE   # Current display mode
echo $UDOS_PROJECT_NAME   # Current project
```

### Python (uSCRIPTs)
```python
# Import
import sys
sys.path.insert(0, './uSCRIPT/library/python')
import udos_variables as uv

# Quick access functions
user_role = uv.get_user_role()        # "WIZARD"
user_level = uv.get_user_level()      # 100
display_mode = uv.get_display_mode()  # "CLI"
project_name = uv.get_project_name()  # "My Project"
is_dev = uv.is_dev_mode()             # True/False

# Generic access
value = uv.get_variable('ANY-VARIABLE')

# Scoped variables
core_vars = uv.udos_vars.get_scoped_variables('core_system')
all_vars = uv.udos_vars.get_all_variables()
```

### Templates
```markdown
# Basic substitution
{VARIABLE}

# With default fallback
{VARIABLE|Default Value}

# Conditional blocks
{#if VARIABLE}Content when true{/if}

# Common variables
{USER-ROLE} {USER-LEVEL} {DISPLAY-MODE} {PROJECT-NAME}
```

## 📋 Essential Variables

| Variable | Type | Default | Environment | Description |
|----------|------|---------|-------------|-------------|
| USER-ROLE | string | GHOST | UDOS_USER_ROLE | Current user role |
| USER-LEVEL | number | 10 | UDOS_USER_LEVEL | Numeric access level |
| DISPLAY-MODE | string | CLI | UDOS_DISPLAY_MODE | Display interface |
| PROJECT-NAME | string | "" | UDOS_PROJECT_NAME | Current project |
| DEV-MODE | boolean | false | UDOS_DEV_MODE | Development mode |
| SESSION-ID | string | "" | UDOS_SESSION_ID | Current session |

## 🔧 Common Patterns

### Role-Based Logic (Python)
```python
import udos_variables as uv

user_level = uv.get_user_level()

if user_level >= 100:    # Wizard
    # Full access
elif user_level >= 80:   # Sorcerer
    # Advanced access
elif user_level >= 60:   # Imp/Knight
    # Standard access
else:                    # Ghost-Drone
    # Basic access
```

### Project Context (Bash)
```bash
PROJECT=$(./uCORE/code/variable-manager.sh GET PROJECT-NAME)
if [[ -n "$PROJECT" ]]; then
    echo "Working on project: $PROJECT"
else
    echo "No active project"
fi
```

### Display Adaptation (Template)
```markdown
{#if DISPLAY-MODE == "CLI"}
## Terminal Interface
{/if}

{#if DISPLAY-MODE == "WEB"}
## Web Interface
{/if}

Current theme: {UI-THEME|polaroid}
```

## 📁 File Locations

- **System Variables**: `uMEMORY/system/variables/system-variables.json`
- **Variable Manager**: `uCORE/code/variable-manager.sh`
- **Python Library**: `uSCRIPT/library/python/udos_variables.py`
- **Export Script**: `uMEMORY/system/variables/export-variables.sh`
- **User Values**: `uMEMORY/user/variables/values-current.json`

## 🚀 Quick Setup

### Initialize System
```bash
# Run variable system optimizer
./uCORE/code/variable-system-optimizer.sh

# Initialize variables
source ./uMEMORY/system/variables/initialize-variables.sh
```

### Set User Context
```bash
./uCORE/code/variable-manager.sh SET USER-ROLE WIZARD
./uCORE/code/variable-manager.sh SET PROJECT-NAME "My-Project"
./uCORE/code/variable-manager.sh SET DEV-MODE true
```

### Test Python Access
```python
import sys
sys.path.insert(0, './uSCRIPT/library/python')
import udos_variables as uv
print(f"Role: {uv.get_user_role()} Level: {uv.get_user_level()}")
```

## 💡 Best Practices

1. **Always use defaults**: Variables have sensible defaults
2. **Check scope**: Use appropriate scope for variable access
3. **Validate values**: Use variable validation when setting
4. **Environment export**: Leverage auto-exported environment variables
5. **Session management**: Use session-specific values when needed
6. **Type awareness**: Respect variable types (string, number, boolean)
7. **Template fallbacks**: Always provide fallback values in templates

*For complete documentation, see: `docs/VARIABLE-SYSTEM-OPTIMIZATION.md`*
