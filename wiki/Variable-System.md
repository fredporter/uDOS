# Variable System (v1.2.x)

**Status**: Stable
**Version**: v1.2.x (uDOS)
**Last Updated**: December 7, 2025
**Schema-Based**: Yes (JSON validation)
**Test Coverage**: 42 tests, 100% passing

The uDOS Variable System provides schema-validated variables with scope management for system configuration, user preferences, character stats (SPRITE), item properties (OBJECT), and story progression.

---

## Quick Start

```python
from core.utils.variables import VariableManager

# Create manager
vm = VariableManager()

# Set a variable (with validation)
vm.set_variable('SPRITE-HP', 100, 'session')
vm.set_variable('USER-NAME', 'survivor', 'global')

# Get a variable (checks all scopes)
hp = vm.get_variable('SPRITE-HP')  # Returns 100

# Use in templates
template = "Welcome, {USER-NAME}! HP: $SPRITE-HP"
result = vm.resolve(template)  # "Welcome, survivor! HP: 100"
```

---

## Variable Schemas

The system uses **5 JSON schemas** located in `core/data/variables/`:

| Schema | Variables | Scope | Purpose |
|--------|-----------|-------|---------|
| **system.json** | 12 | global/session | Core system settings |
| **user.json** | 10 | global/script | User preferences |
| **sprite.json** | 15 | session | Character/player stats |
| **object.json** | 16 | local | Item/equipment properties |
| **story.json** | 13 | session | Adventure progression |

**Total**: 66 predefined variables with validation rules.

---

## Scope System

Variables are organized by **scope**, which determines their lifecycle and visibility:

| Scope | Lifecycle | Persistence | Use Case |
|-------|-----------|-------------|----------|
| **global** | Forever | Saved to `user.json` | User preferences, system config |
| **session** | Current uDOS session | Memory only | Character stats, active story |
| **script** | .upy script execution | Script duration | Temporary calculations |
| **local** | Function/block | Block scope | Loop variables, temp values |

### Scope Priority

When retrieving a variable, the system checks scopes in this order:
1. **local** (highest priority)
2. **script**
3. **session**
4. **global** (lowest priority)

```python
vm.set_variable('TEST', 'global value', 'global')
vm.set_variable('TEST', 'session value', 'session')
vm.set_variable('TEST', 'local value', 'local')

vm.get_variable('TEST')  # Returns 'local value'

vm.clear_scope('local')
vm.get_variable('TEST')  # Now returns 'session value'
```

---

## System Variables (system.json)

Core system configuration and runtime state.

### Key Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CURRENT-PATH` | string | "sandbox" | Current working directory |
| `CURRENT-MODE` | enum | "PROD" | System mode (PROD/DEV/OFFLINE) |
| `USER-NAME` | string | "survivor" | Active user name |
| `SYSTEM-VERSION` | string | "1.1.9" | uDOS version (readonly) |
| `THEME-CURRENT` | enum | "foundation" | Active theme |
| `LOG-LEVEL` | enum | "INFO" | Logging level |
| `LAST-LOCATION` | string | "" | Last TILE code visited |
| `OFFLINE-MODE` | boolean | false | Offline mode status |

### Example Usage

```python
# Check system mode
mode = vm.get_variable('CURRENT-MODE')

# Set theme
vm.set_variable('THEME-CURRENT', 'galaxy')

# Get last location
location = vm.get_variable('LAST-LOCATION')  # e.g., "AA340-100"
```

---

## User Variables (user.json)

User preferences and custom settings.

### Key Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `USER-EMAIL` | string | "" | User email (optional) |
| `USER-LOCATION` | string | "" | Home TILE code |
| `USER-SKILL-LEVEL` | enum | "beginner" | Skill level |
| `USER-PREFERENCES` | object | {...} | Nested preferences |
| `PROJECT-NAME` | string | "" | Current project |
| `CUSTOM-VAR-1/2/3` | string | "" | User-defined variables |

### User Preferences Object

```json
{
  "auto-save": true,
  "show-tips": true,
  "color-mode": "auto"
}
```

### Example Usage

```python
# Set user location
vm.set_variable('USER-LOCATION', 'AA340-100')

# Get skill level
skill = vm.get_variable('USER-SKILL-LEVEL')  # "beginner"

# Custom variables
vm.set_variable('CUSTOM-VAR-1', 'my custom data')
```

---

## SPRITE Variables (sprite.json)

Character/player statistics for adventure gameplay.

### Character Stats

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| `SPRITE-NAME` | string | 1-50 chars | Character name |
| `SPRITE-HP` | integer | 0-999 | Current hit points |
| `SPRITE-HP-MAX` | integer | 1-999 | Maximum hit points |
| `SPRITE-XP` | integer | 0-999999 | Experience points |
| `SPRITE-LEVEL` | integer | 1-99 | Character level |
| `SPRITE-GOLD` | integer | 0-999999 | Currency amount |

### Ability Stats

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| `SPRITE-STRENGTH` | integer | 1-99 | Strength stat |
| `SPRITE-DEXTERITY` | integer | 1-99 | Dexterity stat |
| `SPRITE-INTELLIGENCE` | integer | 1-99 | Intelligence stat |
| `SPRITE-STAMINA` | integer | 1-99 | Stamina/endurance |

### Equipment & Inventory

| Variable | Type | Description |
|----------|------|-------------|
| `SPRITE-INVENTORY` | array | Item IDs (max 50) |
| `SPRITE-EQUIPPED-WEAPON` | string | Equipped weapon ID |
| `SPRITE-EQUIPPED-ARMOR` | string | Equipped armor ID |

### Status & Location

| Variable | Type | Values | Description |
|----------|------|--------|-------------|
| `SPRITE-STATUS` | enum | normal, poisoned, stunned, etc. | Current status |
| `SPRITE-LOCATION` | string | TILE code | Current location |

### Example: Character System

```python
# Create a character
vm.set_variable('SPRITE-NAME', 'Aragorn', 'session')
vm.set_variable('SPRITE-LEVEL', 12, 'session')
vm.set_variable('SPRITE-HP', 85, 'session')
vm.set_variable('SPRITE-HP-MAX', 100, 'session')

# Set stats
vm.set_variable('SPRITE-STRENGTH', 18, 'session')
vm.set_variable('SPRITE-DEXTERITY', 14, 'session')
vm.set_variable('SPRITE-INTELLIGENCE', 12, 'session')

# Add to inventory
inventory = vm.get_variable('SPRITE-INVENTORY') or []
inventory.append('sword_longsword')
inventory.append('potion_health')
vm.set_variable('SPRITE-INVENTORY', inventory, 'session')

# Equip weapon
vm.set_variable('SPRITE-EQUIPPED-WEAPON', 'sword_longsword', 'session')

# Display status
status = "Character: $SPRITE-NAME (Lvl $SPRITE-LEVEL) - HP: $SPRITE-HP/$SPRITE-HP-MAX"
print(vm.resolve(status))
# Output: "Character: Aragorn (Lvl 12) - HP: 85/100"
```

### Leveling System

```python
def gain_xp(vm, amount):
    """Award XP and handle leveling."""
    current_xp = vm.get_variable('SPRITE-XP')
    current_level = vm.get_variable('SPRITE-LEVEL')

    new_xp = current_xp + amount
    vm.set_variable('SPRITE-XP', new_xp, 'session')

    # Check for level up (100 XP per level)
    xp_for_next = current_level * 100
    if new_xp >= xp_for_next:
        vm.set_variable('SPRITE-LEVEL', current_level + 1, 'session')

        # Restore HP on level up
        max_hp = vm.get_variable('SPRITE-HP-MAX')
        vm.set_variable('SPRITE-HP', max_hp, 'session')

        print(f"Level up! Now level {current_level + 1}")
```

---

## OBJECT Variables (object.json)

Item and equipment properties.

### Core Properties

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| `OBJECT-ID` | string | 1-50 chars | Unique identifier |
| `OBJECT-NAME` | string | 1-100 chars | Display name |
| `OBJECT-TYPE` | enum | weapon/armor/consumable/etc. | Item category |
| `OBJECT-DESCRIPTION` | string | 0-500 chars | Description text |

### Stats

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| `OBJECT-VALUE` | integer | 0-99999 | Gold value |
| `OBJECT-WEIGHT` | number | 0-999.99 | Weight in kg |
| `OBJECT-DAMAGE` | integer | 0-999 | Weapon damage |
| `OBJECT-DEFENSE` | integer | 0-999 | Armor defense |
| `OBJECT-DURABILITY` | integer | 0-100 | Condition % |

### Special Properties

| Variable | Type | Description |
|----------|------|-------------|
| `OBJECT-STACKABLE` | boolean | Can stack in inventory |
| `OBJECT-STACK-SIZE` | integer | Current stack count |
| `OBJECT-EFFECT` | enum | Special effect type |
| `OBJECT-EFFECT-VALUE` | integer | Effect magnitude |
| `OBJECT-REQUIRED-LEVEL` | integer | Minimum level to use |

### Object Types

- `weapon` - Swords, axes, bows
- `armor` - Shields, helmets, boots
- `consumable` - Potions, food
- `quest` - Quest items
- `tool` - Rope, lantern, compass
- `item` - Generic items
- `resource` - Crafting materials

### Effect Types

- `heal` - Restore HP
- `poison` - Damage over time
- `boost-strength` - Temporary stat boost
- `boost-dexterity` - Dexterity boost
- `boost-intelligence` - Intelligence boost
- `restore-hp` - Instant HP restoration
- `restore-stamina` - Stamina restoration

### Example: Weapon Creation

```python
# Create a longsword
vm.set_variable('OBJECT-ID', 'sword_longsword_001', 'local')
vm.set_variable('OBJECT-NAME', 'Steel Longsword', 'local')
vm.set_variable('OBJECT-TYPE', 'weapon', 'local')
vm.set_variable('OBJECT-DESCRIPTION', 'A well-crafted steel blade', 'local')

# Set stats
vm.set_variable('OBJECT-DAMAGE', 25, 'local')
vm.set_variable('OBJECT-VALUE', 150, 'local')
vm.set_variable('OBJECT-WEIGHT', 3.5, 'local')
vm.set_variable('OBJECT-DURABILITY', 100, 'local')

# Requirements
vm.set_variable('OBJECT-REQUIRED-LEVEL', 5, 'local')

# Display
info = "$OBJECT-NAME - Damage: $OBJECT-DAMAGE, Value: $OBJECT-VALUE gold"
print(vm.resolve(info))
# Output: "Steel Longsword - Damage: 25, Value: 150 gold"
```

### Example: Health Potion

```python
# Create healing potion
vm.set_variable('OBJECT-ID', 'potion_health_minor', 'local')
vm.set_variable('OBJECT-NAME', 'Minor Health Potion', 'local')
vm.set_variable('OBJECT-TYPE', 'consumable', 'local')
vm.set_variable('OBJECT-STACKABLE', True, 'local')
vm.set_variable('OBJECT-STACK-SIZE', 3, 'local')

# Effect
vm.set_variable('OBJECT-EFFECT', 'heal', 'local')
vm.set_variable('OBJECT-EFFECT-VALUE', 50, 'local')  # Restore 50 HP
```

---

## STORY Variables (story.json)

Adventure progression and narrative state.

### Progression Tracking

| Variable | Type | Description |
|----------|------|-------------|
| `STORY-CURRENT` | string | Active story/adventure ID |
| `STORY-CHAPTER` | integer | Current chapter (1-99) |
| `STORY-CHECKPOINT` | string | Last save point |
| `STORY-FLAGS` | array | Completed events (max 100) |
| `STORY-CHOICES` | object | Player decisions |

### Quest System

| Variable | Type | Description |
|----------|------|-------------|
| `STORY-QUEST-ACTIVE` | array | Active quests (max 20) |
| `STORY-QUEST-COMPLETED` | array | Finished quests (max 200) |

### World State

| Variable | Type | Description |
|----------|------|-------------|
| `STORY-NPC-MET` | array | NPCs encountered (max 100) |
| `STORY-LOCATIONS-VISITED` | array | TILE codes visited (max 500) |
| `STORY-DIALOGUE-SEEN` | array | Dialogue IDs shown (max 1000) |
| `STORY-TIME-ELAPSED` | integer | In-game time (minutes) |

### Completion

| Variable | Type | Values |
|----------|------|--------|
| `STORY-ENDING` | enum | good/bad/neutral/secret/true |
| `STORY-DIFFICULTY` | enum | easy/normal/hard/nightmare |

### Example: Story Progression

```python
# Start a new adventure
vm.set_variable('STORY-CURRENT', 'water_quest', 'session')
vm.set_variable('STORY-CHAPTER', 1, 'session')
vm.set_variable('STORY-DIFFICULTY', 'normal', 'session')

# Track progress
flags = vm.get_variable('STORY-FLAGS') or []
flags.append('met_elder')
flags.append('learned_water_purification')
vm.set_variable('STORY-FLAGS', flags, 'session')

# Active quests
active_quests = ['find_water_source', 'gather_firewood']
vm.set_variable('STORY-QUEST-ACTIVE', active_quests, 'session')

# Complete a quest
active = vm.get_variable('STORY-QUEST-ACTIVE')
completed = vm.get_variable('STORY-QUEST-COMPLETED') or []

quest_id = 'find_water_source'
active.remove(quest_id)
completed.append(quest_id)

vm.set_variable('STORY-QUEST-ACTIVE', active, 'session')
vm.set_variable('STORY-QUEST-COMPLETED', completed, 'session')

# Award XP for quest completion
gain_xp(vm, 100)
```

---

## Validation Rules

All variables are validated before being set.

### Type Validation

```python
# Correct type
vm.set_variable('SPRITE-HP', 100, 'session')  # ✅ Integer accepted

# Wrong type
vm.set_variable('SPRITE-HP', "hundred", 'session')  # ❌ Validation error
```

### Range Validation

```python
# Within range
vm.set_variable('SPRITE-HP', 500, 'session')  # ✅ Valid (0-999)

# Out of range
vm.set_variable('SPRITE-HP', 1500, 'session')  # ❌ Max is 999
vm.set_variable('SPRITE-HP', -10, 'session')   # ❌ Min is 0
```

### Pattern Validation

```python
# Valid pattern
vm.set_variable('USER-NAME', 'survivor_123', 'global')  # ✅ Alphanumeric + underscore

# Invalid pattern
vm.set_variable('USER-NAME', 'user@name', 'global')  # ❌ Contains @
```

### Enum Validation

```python
# Valid enum value
vm.set_variable('CURRENT-MODE', 'DEV', 'global')  # ✅ One of: PROD, DEV, OFFLINE

# Invalid enum value
vm.set_variable('CURRENT-MODE', 'TESTING', 'global')  # ❌ Not in enum list
```

### Readonly Protection

```python
# Readonly variable
vm.set_variable('SYSTEM-VERSION', '2.0.0', 'global')  # ❌ Read-only
```

---

## Template Resolution

Variables can be used in templates with **two syntaxes**:

| Syntax | Example | Use Case |
|--------|---------|----------|
| `{VAR}` | `{USER-NAME}` | Legacy format, uCODE templates |
| `$VAR` | `$SPRITE-HP` | New format, .upy scripts |

### Basic Resolution

```python
template = "User: {USER-NAME}, HP: $SPRITE-HP"
result = vm.resolve(template)
```

### With Extra Variables

```python
extra = {"QUEST": "Find Water", "REWARD": "100 XP"}
template = "Quest: {QUEST} - Reward: {REWARD}"
result = vm.resolve(template, extra)
```

### Complex Templates

```python
# Character status display
status = """
Character: $SPRITE-NAME (Level $SPRITE-LEVEL)
HP: $SPRITE-HP / $SPRITE-HP-MAX
XP: $SPRITE-XP
Gold: $SPRITE-GOLD
Location: $SPRITE-LOCATION

Equipped:
  Weapon: $SPRITE-EQUIPPED-WEAPON
  Armor: $SPRITE-EQUIPPED-ARMOR

Active Quest: {QUEST-NAME}
"""

result = vm.resolve(status, {"QUEST-NAME": "Water Purification"})
```

---

## API Reference

### VariableManager Methods

```python
# Initialization
vm = VariableManager(components=None)

# Setting variables
vm.set_variable(var_name: str, value: Any, scope: str = None) -> bool

# Getting variables
vm.get_variable(var_name: str, default: Any = None) -> Any

# Validation
vm.validate_variable(var_name: str, value: Any, schema_type: str = None) -> tuple[bool, str]

# Scope management
vm.clear_scope(scope: str)
vm.get_scope_variables(scope: str) -> Dict[str, Any]

# Template resolution
vm.resolve(template: str, extra_vars: Dict[str, Any] = None) -> str

# Utilities
vm.get_all_vars() -> Dict[str, str]
vm.add_custom_var(name: str, value: Any, scope: str = 'global')
```

---

## Best Practices

### 1. Use Appropriate Scopes

```python
# ✅ Good: User preferences in global scope
vm.set_variable('USER-NAME', 'fred', 'global')

# ✅ Good: Character stats in session scope
vm.set_variable('SPRITE-HP', 100, 'session')

# ✅ Good: Temporary calculations in local scope
vm.set_variable('TEMP-RESULT', calc_value(), 'local')
```

### 2. Validate Before Use

```python
# ✅ Good: Check validation result
success = vm.set_variable('SPRITE-HP', user_input)
if not success:
    print("Invalid HP value")
```

### 3. Clear Scopes When Done

```python
# ✅ Good: Clean up after script execution
vm.clear_scope('script')

# ✅ Good: Reset session on new game
vm.clear_scope('session')
```

### 4. Use Schema-Defined Variables

```python
# ✅ Good: Use predefined SPRITE variables
vm.set_variable('SPRITE-NAME', 'Hero')

# ⚠️ Acceptable: Custom variables for special cases
vm.set_variable('CUSTOM-VAR-1', 'special data')
```

### 5. Leverage Type Safety

```python
# ✅ Good: Let validation catch errors
is_valid, error = vm.validate_variable('SPRITE-LEVEL', "not a number")
if not is_valid:
    print(f"Error: {error}")
```

---

## Migration from v1.0.x

The v1.1.9 variable system is **backward compatible** with legacy variables.

### Legacy Variables Still Work

```python
# Old style (still works)
template = "Welcome {USERNAME}!"  # Uses legacy system vars

# New style (preferred)
template = "Welcome {USER-NAME}!"  # Uses schema-based vars
```

### Migrating to New Variables

1. **System config**: Use `system.json` variables
2. **User preferences**: Use `user.json` variables
3. **Character data**: Use `sprite.json` variables
4. **Items**: Use `object.json` variables
5. **Story state**: Use `story.json` variables

---

## Troubleshooting

### Variables Not Resolving

**Problem**: `{VAR}` shows up literally in output

**Solution**:
```python
# Check if variable exists
value = vm.get_variable('VAR')
if value is None:
    print("Variable not set")

# Set the variable
vm.set_variable('VAR', 'value', 'global')
```

### Validation Errors

**Problem**: `set_variable()` returns `False`

**Solution**:
```python
# Check what's wrong
is_valid, error = vm.validate_variable('SPRITE-HP', your_value)
print(f"Validation error: {error}")

# Fix the value
if "must be an integer" in error:
    your_value = int(your_value)
```

### Scope Issues

**Problem**: Variable shows wrong value

**Solution**:
```python
# Check all scopes
for scope in ['global', 'session', 'script', 'local']:
    scope_vars = vm.get_scope_variables(scope)
    if 'VAR' in scope_vars:
        print(f"{scope}: {scope_vars['VAR']}")
```

---

## See Also

- [uPY Language Reference](uCODE-Language.md) - Variable usage in .upy scripts
- [Adventure Scripting](Adventure-Scripting.md) - SPRITE/OBJECT in gameplay (Round 2)
- [Developers Guide](Developers-Guide.md) - Variable system integration
- [COPILOT-BRIEF.md](../dev/roadmap/COPILOT-BRIEF.py) - uPY refactor reference

---

**Last Updated**: December 1, 2025
**Version**: v1.2.20 (System Variables Complete)
