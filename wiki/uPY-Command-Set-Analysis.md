# uPY Command Set Analysis & Recommendations

**Date**: December 5, 2025
**Version**: v2.0 Review
**Purpose**: Define minimal, learner-friendly uPY commands as gateway to Python

---

## Current uPY Command Inventory

### Category 1: **Entry-Level Logic** (Unique to uDOS)
These commands provide a simplified, educational introduction to programming concepts.

| Command | Current Syntax | Python Equivalent | Keep? | Notes |
|---------|---------------|-------------------|-------|-------|
| `SET` | `SET (var|value)` | `var = value` | **YES** | Entry-level variable assignment |
| `GET` | `GET var` or `GET (var)` | `print(var)` or `var` | **YES** | Explicit value retrieval |
| `PRINT` | `PRINT('text $var')` | `print(f'text {var}')` | **YES** | Output with substitution |
| `INPUT` | `INPUT → var` | `var = input()` | **YES** | Get user input |
| `IF` (inline) | `{IF cond: CMD()}` | `if cond: cmd()` | **YES** | Quick conditionals |
| `IF/END` (block) | `IF cond ... END` | `if cond: ...` | **YES** | Multi-line logic |
| `FOREACH` | `FOREACH item IN list ... END` | `for i in list: ...` | **YES** | Iteration |
| `WHILE` | `WHILE cond ... END` | `while cond: ...` | **YES** | Loops |
| `FUNCTION` | `FUNCTION name(args) ... ENDFUNCTION` | `def name(args): ...` | **YES** | Define functions |
| `@function` | `@function(args)` | `function(args)` | **YES** | Call functions |
| `RETURN` | `RETURN value` | `return value` | **YES** | Return from function |
| `TRY/CATCH` | `TRY ... CATCH error ... ENDTRY` | `try: ... except: ...` | **YES** | Error handling |

**Recommendation**: **KEEP ALL** - These are core learning constructs that map 1:1 to Python.

---

### Category 2: **Adventure/Game Commands** (Unique to uDOS)
Special commands for interactive storytelling and game mechanics.

| Command | Current Syntax | Python Equivalent | Keep? | Notes |
|---------|---------------|-------------------|-------|-------|
| `PRINT []` | `PRINT [Narrative text]` | Custom narrative renderer | **YES** | Story/narrative display |
| `ROLL` | `ROLL [1d20] → var` | `var = randint(1,20)` | **YES** | Dice rolling (RPG staple) |
| `XP` | `XP [+50]` | `xp += 50` | **YES** | Experience points |
| `HP` | `HP [+10]` | `hp += 10` | **YES** | Health points |
| `ITEM` | `ITEM [sword]` | `inventory.append('sword')` | **YES** | Add to inventory |
| `FLAG` | `FLAG [quest_done]` | `flags['quest_done'] = True` | **YES** | Story state |
| `CHOICE` | `CHOICE [Q?] OPTION [...] → LABEL` | Custom choice renderer | **YES** | Branching narrative |
| `LABEL` | `LABEL [name]` | `# label (goto)` | **YES** | Jump destinations |
| `BRANCH` | `BRANCH [label]` | `goto label` | **YES** | Unconditional jump |
| `SPRITE-SET` | `SPRITE-SET('HP'\|100)` | `sprite.hp = 100` | **MAYBE** | Character properties |
| `SPRITE-GET` | `SPRITE-GET('HP')` | `sprite.hp` | **MAYBE** | Get character property |

**Recommendation**:
- **KEEP**: `ROLL`, `XP`, `HP`, `ITEM`, `FLAG`, `CHOICE`, `LABEL`, `BRANCH`, `PRINT []`
- **SIMPLIFY**: `SPRITE-SET/GET` → Use regular Python objects in advanced mode

---

### Category 3: **System Commands** (Hybrid - uDOS + Python)
Commands that bridge uDOS functionality with Python.

| Command | Current Syntax | Python Equivalent | Keep? | Notes |
|---------|---------------|-------------------|-------|-------|
| `IMPORT` | `IMPORT module` | `import module` | **DELEGATE** | Use Python directly |
| `EXPORT` | `EXPORT func` | N/A (Python handles this) | **REMOVE** | Not needed |
| `CALL` | `CALL func(args)` | `func(args)` or `@func()` | **KEEP @** | Keep `@func()` style only |
| `JSON.load` | `JSON.load('file')` | `json.load(open('file'))` | **DELEGATE** | Use Python json module |
| `JSON.save` | `JSON.save(data, 'file')` | `json.dump(data, open('file'))` | **DELEGATE** | Use Python json module |

**Recommendation**:
- **KEEP**: `@function()` calling syntax (cleaner than CALL)
- **REMOVE**: `EXPORT`, `JSON.*` commands (use Python directly)
- **DELEGATE**: `IMPORT` → just use Python `import`

---

### Category 4: **uDOS-Specific Commands** (Not uPY)
These are uDOS system commands, NOT part of uPY scripting language.

| Command | Purpose | Keep in uPY? | Notes |
|---------|---------|--------------|-------|
| `GUIDE` | Knowledge system | **NO** | System command only |
| `MAP` | Navigation | **NO** | System command only |
| `MISSION` | Mission management | **NO** | System command only |
| `CHECKPOINT` | Save state | **YES** | Useful in adventures |
| `STATUS` | System status | **NO** | System command only |
| `SETTINGS` | Configuration | **NO** | System command only |
| `GENERATE` | Content generation | **NO** | System command only |
| `WORKFLOW` | Automation | **NO** | System command only |

**Recommendation**:
- **KEEP in uPY**: `CHECKPOINT` (useful for save/load in adventures)
- **Remove from uPY**: All other system commands (call via Python if needed)

---

## Proposed uPY v2.0 Command Set (Minimal & Educational)

### **Core Commands** (16 total - Entry Level)

#### **Variables & Output**
1. `SET ($var|value)` - Assign variable
2. `GET $var` - Retrieve variable value
3. `PRINT("text $var")` - Output with substitution
4. `INPUT → $var` - Get user input

#### **Control Flow**
5. `{IF condition: COMMAND()}` - Inline conditional
6. `IF condition ... END` - Block conditional
7. `FOREACH $item IN $list ... END` - Iterate list
8. `WHILE condition ... END` - While loop
9. `FOR $i IN RANGE(1, 10) ... END` - For loop

#### **Functions**
10. `FUNCTION name(args) ... ENDFUNCTION` - Define function
11. `@function(args)` - Call function
12. `RETURN value` - Return from function

#### **Error Handling**
13. `TRY ... CATCH error ... ENDTRY` - Exception handling

#### **Advanced Control**
14. `BREAK` - Exit loop
15. `CONTINUE` - Skip to next iteration
16. `PASS` - No-op placeholder

### **Adventure Commands** (11 total - uDOS Unique)

#### **Narrative**
17. `PRINT [Narrative text with $vars]` - Story text display

#### **Game Mechanics**
18. `ROLL [XdY] → $var` - Dice rolling (1d20, 2d6+3, etc.)
19. `XP [±amount]` - Modify experience points
20. `HP [±amount]` - Modify health points
21. `ITEM [item_id]` - Add item to inventory
22. `FLAG [flag_name]` - Set story flag

#### **Branching**
23. `CHOICE [Question?] OPTION [...] → LABEL` - Player decisions
24. `LABEL [name]` - Define jump point
25. `BRANCH [label]` - Jump to label

#### **State Management**
26. `CHECKPOINT SAVE "name"` - Save game state
27. `CHECKPOINT LOAD "name"` - Load game state

---

## What Can Be Pure Python?

### **Use Python Directly For:**

```python
# ✅ Lists and data structures
inventory = ['sword', 'shield', 'potion']
stats = {'hp': 100, 'mp': 50, 'level': 5}

# ✅ Math and calculations
damage = base_damage * (1 + level * 0.1)
total_xp = sum([quest.xp for quest in completed_quests])

# ✅ String manipulation
message = f"Welcome, {player_name}!"
uppercase_name = player_name.upper()

# ✅ File I/O
with open('save.json', 'r') as f:
    data = json.load(f)

# ✅ Imports and modules
import random
import json
from pathlib import Path

# ✅ Classes and objects
class Character:
    def __init__(self, name):
        self.name = name
        self.hp = 100

player = Character("Hero")
player.hp -= 10

# ✅ List comprehensions
even_numbers = [x for x in range(10) if x % 2 == 0]
damaged_enemies = [e for e in enemies if e.hp < 50]

# ✅ Lambda functions
sorted_items = sorted(inventory, key=lambda x: x.weight)

# ✅ Decorators
@property
def is_alive(self):
    return self.hp > 0
```

### **Use uPY Commands For:**

```upy
# ✅ Beginner-friendly variable assignment
SET ($player_name|'Hero')
SET ($hp|100)
SET ($level|1)

# ✅ Simple output with variable substitution
PRINT("Welcome, $player_name!")
PRINT("HP: $hp / Level: $level")

# ✅ Narrative story text
PRINT [You enter a dark cave...]
PRINT [The air is thick with moisture.]
PRINT [What do you do?]

# ✅ Inline conditionals for quick checks
{IF $hp < 50: PRINT("⚠️  Low health!")}
{IF $gold >= 100: PRINT("💰 You can afford it!")}

# ✅ Dice rolling (RPG mechanics)
ROLL [1d20] → $attack_roll
ROLL [2d6+3] → $damage

# ✅ Game stat tracking
XP [+50]
HP [-25]
ITEM [health_potion]
FLAG [quest_complete]

# ✅ Interactive choices
CHOICE [What do you do?]
  OPTION [Attack] → COMBAT
  OPTION [Defend] → DEFEND
  OPTION [Flee] → ESCAPE

# ✅ Story branching
LABEL [COMBAT]
PRINT [You draw your sword...]
BRANCH [COMBAT_SEQUENCE]
```

---

## Migration Path: uPY → Python

### **Level 1: Pure uPY** (Beginners)
```upy
SET (name|'Alice')                       # No $ in assignment
SET (score|0)

PRINT('Welcome, $name!')                 # $ in string interpolation

{IF score > 100: PRINT('High score!')}   # No $ in condition

FUNCTION greet(player_name)              # Params no $
PRINT('Hello, $player_name!')            # $ for substitution
ENDFUNCTION

@greet(name)                             # Pass variable
```

### **Level 2: Hybrid uPY + Python** (Intermediate)
```python
# Mix uPY commands with Python

import random

SET (name|'Alice')                       # uPY assignment
score = 0                                # Python variable

PRINT('Welcome, $name!')                 # uPY output

# Use Python for complex logic
if score > 100:
    bonus = score * 0.1
    PRINT(f'Bonus: {bonus}')             # Mix f-strings with uPY

# Use uPY for game mechanics
ROLL [1d20] → attack                     # Dice roll
{IF attack >= 15: XP [+50]}              # Quick XP award
```

### **Level 3: Pure Python** (Advanced)
```python
# Full Python - no uPY commands needed

import random
import json

class Character:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.xp = 0

    def attack(self):
        roll = random.randint(1, 20)
        if roll >= 15:
            self.xp += 50
            return "Hit!"
        return "Miss!"

player = Character("Alice")
print(f"Welcome, {player.name}!")
result = player.attack()
print(f"Attack result: {result}")
```

---

## Recommended Changes

### **1. Remove These Commands** (Use Python Instead)

```upy
# ❌ Remove
EXPORT function_name
JSON.load('file')
JSON.save(data, 'file')
SPRITE-SET('HP'|100)  # Use Python objects instead
SPRITE-GET('HP')

# ✅ Use Python
def function_name(): pass  # Python handles exports
data = json.load(open('file'))
json.dump(data, open('file', 'w'))
player.hp = 100  # Python objects
hp = player.hp
```

### **2. Simplify These Commands**

```upy
# ❌ Old verbose syntax
CALL function_name(args)

# ✅ New clean syntax
@function_name(args)
```

### **3. Keep These Unique Features**

```upy
# ✅ Educational entry-level syntax
SET (var|value)                          # | separator, no spaces/commas/*
PRINT('text $var')                       # Single quotes default, $ for vars

# ✅ Game/adventure specific
ROLL [1d20] → var                        # No Python equivalent
XP [+50]                                 # Game mechanic shorthand
HP [-10]                                 # Health tracking
ITEM [sword]                             # Inventory management
FLAG [quest_done]                        # Story state
CHOICE [...] OPTION [...] → LABEL        # Interactive narrative
PRINT [Story text...]                    # Narrative rendering

# ✅ Save state management
CHECKPOINT SAVE 'name'
CHECKPOINT LOAD 'name'
```

---

## Final uPY v2.0 Command Set

### **Total: 27 Commands**

**Core (16)**: SET, GET, PRINT, INPUT, IF (inline), IF/END, FOREACH, WHILE, FOR, FUNCTION, @call, RETURN, TRY/CATCH, BREAK, CONTINUE, PASS

**Adventure (11)**: PRINT [], ROLL, XP, HP, ITEM, FLAG, CHOICE/OPTION, LABEL, BRANCH, CHECKPOINT

### **Rationale**

1. **Entry-Level Gateway**: uPY commands are **easier to learn** than Python equivalents
   - `SET ($hp|100)` is clearer than `hp = 100` for absolute beginners
   - `PRINT("HP: $hp")` is simpler than `print(f"HP: {hp}")`
   - `{IF $hp < 50: PRINT("Low!")}` is more explicit than Python's inline if

2. **Unique uDOS Features**: Game mechanics have no direct Python equivalent
   - `ROLL [1d20] → $attack` (dice rolling)
   - `CHOICE/OPTION` (interactive narrative)
   - `PRINT [Story text]` (narrative rendering)

3. **Natural Progression**: Students graduate from uPY → Python seamlessly
   - Level 1: Pure uPY (learn logic)
   - Level 2: Mix uPY + Python (transition)
   - Level 3: Pure Python (advanced)

4. **Full Python Support**: Advanced users can use Python anywhere
   - Import any module
   - Define classes
   - Use comprehensions
   - Leverage full Python stdlib

---

## Implementation Priority

### **Phase 1: Core Cleanup** (Immediate)
- ✅ Remove `EXPORT` command
- ✅ Remove `JSON.*` commands (use Python `json` module)
- ✅ Remove `SPRITE-SET/GET` (use Python objects)
- ✅ Standardize on `@function()` calling (remove `CALL`)

### **Phase 2: Documentation** (Week 1)
- Update all wiki examples to v2.0 syntax
- Create beginner tutorials (uPY → Python progression)
- Document all 27 commands with examples
- Create "When to use uPY vs Python" guide

### **Phase 3: Template Updates** (Week 2)
- Update all `.upy` templates
- Migrate `adventure.template.upy` to v2.0
- Create example adventures showing progression path
- Add Python integration examples

### **Phase 4: VS Code Extension** (Week 3)
- Update syntax highlighting for v2.0
- Add IntelliSense for 27 commands only
- Remove deprecated command suggestions
- Add quick fixes: "Convert to Python" refactoring

---

## Summary

**uPY v2.0 Philosophy:**
- **Minimal** (27 commands total)
- **Educational** (gateway to Python)
- **Retro** (UPPERCASE, traditional feel)
- **Unique** (game mechanics not in Python)
- **Progressive** (natural path to full Python)

**What Makes uPY Special:**
1. Beginner-friendly syntax for core programming concepts
2. Built-in game/adventure mechanics (ROLL, XP, CHOICE, etc.)
3. Seamless Python integration (use both in same file)
4. Clear migration path (uPY → hybrid → Python)

**What uPY Is NOT:**
- A replacement for Python (it's a teaching tool & game DSL)
- Feature-complete programming language (by design)
- Required for advanced users (use Python directly)

---

See also:
- [uPY Syntax v2.0](uPY-Syntax-v2.md) - Complete syntax reference
- [Adventure Scripting Guide](Adventure-Scripting.md) - Game mechanics
- [Function Programming Guide](Function-Programming-Guide.md) - Python integration
