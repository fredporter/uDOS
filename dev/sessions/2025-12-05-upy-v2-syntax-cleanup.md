# uPY v2.0 Syntax Refinement - Session Summary

**Date**: December 5, 2025
**Session Goal**: Clean up uPY syntax, review command set, define minimal educational core

---

## ✅ Completed Work

### 1. **uPY Syntax v2.0 Specification** ✓
**File**: `wiki/uPY-Syntax-v2.md` (600+ lines)

**Defined Official Syntax:**
- `SET ($variable|value)` - Pipe-separated assignment
- `PRINT("text with $vars")` - Parentheses for code output
- `PRINT [Narrative text]` - Brackets for story/narrative
- `{IF condition: COMMAND()}` - Inline conditionals
- `@function(args)` - Clean function calls
- No indentation required in control structures
- UPPERCASE commands, retro/minimal style

### 2. **Command Set Analysis & Recommendations** ✓
**File**: `wiki/uPY-Command-Set-Analysis.md` (500+ lines)

**Key Findings:**
- **27 Total Commands** (down from 40+)
  - 16 Core/Educational commands
  - 11 Adventure/Game-specific commands
- **Removed**: `EXPORT`, `JSON.*`, `SPRITE-SET/GET`, `CALL`
- **Delegated to Python**: Complex data structures, file I/O, modules
- **Kept Unique**: `ROLL`, `XP`, `HP`, `ITEM`, `FLAG`, `CHOICE`, `CHECKPOINT`

**Learning Path Defined:**
1. **Level 1**: Pure uPY (beginners learn logic)
2. **Level 2**: Hybrid uPY + Python (transition)
3. **Level 3**: Pure Python (advanced)

### 3. **Updated Test Files** ✓
**Files Modified:**
- `extensions/vscode/test-examples/feature-test.upy`
- `extensions/vscode/test-examples/water-filter-mission.upy`

**Changes Applied:**
- ✅ `SET ($var|'value')` syntax
- ✅ `PRINT("text")` with parentheses
- ✅ `{IF condition: COMMAND()}` inline conditionals
- ✅ Removed indentation
- ✅ No more `ECHO` command

---

## 📋 Command Set Summary

### **Core Commands (16)** - Entry-Level Gateway to Python

| uPY Command | Python Equivalent | Purpose |
|-------------|-------------------|---------|
| `SET ($var\|value)` | `var = value` | Variable assignment |
| `GET $var` | `var` or `print(var)` | Retrieve value |
| `PRINT("text $var")` | `print(f"text {var}")` | Output |
| `INPUT → $var` | `var = input()` | User input |
| `{IF cond: CMD()}` | `if cond: cmd()` | Inline conditional |
| `IF/END` | `if: ... else: ...` | Block conditional |
| `FOREACH/END` | `for item in list:` | Iteration |
| `WHILE/END` | `while condition:` | Loop |
| `FOR/END` | `for i in range():` | Range loop |
| `FUNCTION/ENDFUNCTION` | `def name():` | Define function |
| `@function()` | `function()` | Call function |
| `RETURN` | `return` | Return value |
| `TRY/CATCH` | `try: ... except:` | Error handling |
| `BREAK` | `break` | Exit loop |
| `CONTINUE` | `continue` | Skip iteration |
| `PASS` | `pass` | No-op |

### **Adventure Commands (11)** - Unique to uDOS

| uPY Command | Purpose | No Python Equivalent |
|-------------|---------|---------------------|
| `PRINT [text]` | Narrative display | ✓ Custom renderer |
| `ROLL [XdY] → $var` | Dice rolling | ✓ RPG mechanic |
| `XP [±N]` | Experience points | ✓ Game stat |
| `HP [±N]` | Health points | ✓ Game stat |
| `ITEM [id]` | Add to inventory | ✓ Game mechanic |
| `FLAG [name]` | Story state | ✓ Narrative tracking |
| `CHOICE/OPTION → LABEL` | Interactive branching | ✓ Choose-your-own |
| `LABEL [name]` | Jump destination | ✓ Narrative flow |
| `BRANCH [label]` | Unconditional jump | ✓ Story control |
| `CHECKPOINT SAVE` | Save game state | ✓ State management |
| `CHECKPOINT LOAD` | Load game state | ✓ State management |

---

## 🎯 Design Philosophy

### **uPY is NOT:**
- ❌ A replacement for Python
- ❌ A feature-complete programming language
- ❌ Required for advanced users

### **uPY IS:**
- ✅ Educational gateway to Python
- ✅ Beginner-friendly syntax for core concepts
- ✅ Domain-specific language for adventures/games
- ✅ Seamlessly integrated with full Python

### **Why uPY?**

**For Beginners:**
```upy
# ✅ Clearer for absolute beginners
SET ($name|'Hero')
SET ($hp|100)
PRINT("Welcome, $name! HP: $hp")
{IF $hp < 50: PRINT("⚠️  Low health!")}
```

vs

```python
# Requires understanding of = operator, f-strings, if syntax
name = 'Hero'
hp = 100
print(f"Welcome, {name}! HP: {hp}")
if hp < 50:
    print("⚠️  Low health!")
```

**For Game Developers:**
```upy
# ✅ Built-in RPG mechanics
ROLL [1d20] → $attack_roll
{IF $attack_roll >= 15: XP [+50]}
{IF $attack_roll >= 15: PRINT("Critical hit!")}

CHOICE [What do you do?]
  OPTION [Attack] → COMBAT
  OPTION [Defend] → BLOCK
  OPTION [Flee] → ESCAPE
```

vs

```python
# Requires custom implementation
import random
attack_roll = random.randint(1, 20)
if attack_roll >= 15:
    xp += 50
    print("Critical hit!")

# Would need custom choice/branching system
```

---

## 🔄 Migration Path Examples

### **Example 1: Hello World Progression**

**Level 1 - Pure uPY:**
```upy
SET ($name|'Alice')
PRINT("Hello, $name!")
```

**Level 2 - Hybrid:**
```python
name = 'Alice'  # Use Python
PRINT("Hello, $name!")  # Still use uPY
```

**Level 3 - Pure Python:**
```python
name = 'Alice'
print(f"Hello, {name}!")
```

### **Example 2: Conditional Logic Progression**

**Level 1 - Pure uPY:**
```upy
SET ($score|85)
{IF $score >= 90: PRINT("A grade!")}
{IF $score >= 80 AND $score < 90: PRINT("B grade!")}
{IF $score < 80: PRINT("Keep trying!")}
```

**Level 2 - Hybrid:**
```python
score = 85
if score >= 90:
    PRINT("A grade!")
elif score >= 80:
    PRINT("B grade!")
else:
    PRINT("Keep trying!")
```

**Level 3 - Pure Python:**
```python
score = 85
if score >= 90:
    print("A grade!")
elif score >= 80:
    print("B grade!")
else:
    print("Keep trying!")
```

### **Example 3: Adventure Scripting**

**Level 1 - Pure uPY:**
```upy
SET ($player_name|'Hero')
SET ($hp|100)

PRINT [You enter a dark cave...]
PRINT [What do you do?]

CHOICE [Choose wisely:]
  OPTION [Light a torch] → TORCH
  OPTION [Feel the walls] → WALLS

LABEL [TORCH]
PRINT [The torch reveals ancient paintings!]
XP [+50]
FLAG [saw_paintings]
END
```

**Level 2 - Hybrid (Use Python for complex logic):**
```python
import random

SET ($player_name|'Hero')
hp = 100  # Python variable

PRINT [You enter a dark cave...]

# Use Python for complex calculations
torch_success_rate = 0.8
if random.random() < torch_success_rate:
    PRINT [The torch lights successfully!]
    XP [+50]
else:
    PRINT [The torch sputters and dies...]
    HP [-10]
```

**Level 3 - Pure Python (Advanced users):**
```python
import random
import json

class Adventure:
    def __init__(self, player_name):
        self.player_name = player_name
        self.hp = 100
        self.xp = 0
        self.flags = set()

    def enter_cave(self):
        print(f"{self.player_name} enters a dark cave...")

        choice = input("Light torch (1) or feel walls (2)? ")

        if choice == "1":
            if random.random() < 0.8:
                print("The torch reveals paintings!")
                self.xp += 50
                self.flags.add('saw_paintings')
            else:
                print("Torch failed...")
                self.hp -= 10

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump({
                'name': self.player_name,
                'hp': self.hp,
                'xp': self.xp,
                'flags': list(self.flags)
            }, f)

adventure = Adventure('Hero')
adventure.enter_cave()
adventure.save('save.json')
```

---

## 📝 Syntax Quick Reference

### **Variables**
```upy
SET ($name|'Hero')          # String
SET ($hp|100)               # Number
SET ($level|1)              # Integer
SET ($ratio|3.14)           # Float
SET ($active|TRUE)          # Boolean
SET ($items|['sword', 'shield'])  # List
```

### **Output**
```upy
PRINT("Code output: $hp")   # For code/data
PRINT [Story narrative]     # For story/narrative text
```

### **Conditionals**
```upy
# Inline (single command)
{IF $hp < 50: PRINT("Low health!")}

# Block (multiple commands)
IF $hp < 50
PRINT("Low health!")
HP [+25]
PRINT("Healed!")
END
```

### **Loops**
```upy
# Iterate list
FOREACH $item IN $inventory
PRINT("Item: $item")
END

# While loop
WHILE $counter < 10
SET ($counter|$counter + 1)
PRINT("Count: $counter")
END

# Range loop
FOR $i IN RANGE(1, 11)
PRINT("Number: $i")
END
```

### **Functions**
```upy
# Define
FUNCTION calculate_damage(base, level)
SET ($multiplier|$level * 0.1)
SET ($total|$base * $multiplier)
RETURN $total
ENDFUNCTION

# Call
@calculate_damage(50, $player_level)
GET [RETURN_VALUE]
SET ($damage|RETURN_VALUE)
```

### **Game Mechanics**
```upy
ROLL [1d20] → $roll         # Dice roll
XP [+50]                    # Experience
HP [-25]                    # Health
ITEM [sword]                # Inventory
FLAG [quest_complete]       # Story state

CHOICE [What do you do?]
  OPTION [Fight] → COMBAT
  OPTION [Flee] → ESCAPE
```

---

## 🚀 Next Steps

### **Phase 1: Template Updates** (Priority)
- [ ] Update `adventure.template.upy` to v2.0 syntax
- [ ] Update all other `.upy` templates in `core/data/templates/`
- [ ] Remove deprecated commands (EXPORT, JSON.*, SPRITE-SET/GET)

### **Phase 2: Documentation Updates**
- [ ] Update `Adventure-Scripting.md` with v2.0 examples
- [ ] Update `uCODE-Syntax-Quick-Reference.md`
- [ ] Create tutorial: "From uPY to Python in 10 Steps"
- [ ] Add "When to use uPY vs Python" guide

### **Phase 3: VS Code Extension**
- [ ] Update syntax highlighting for v2.0
- [ ] Update IntelliSense to suggest only 27 commands
- [ ] Add code actions: "Convert to Python" refactoring
- [ ] Add snippets for all v2.0 patterns

### **Phase 4: Examples & Tutorials**
- [ ] Create 5 beginner adventures (pure uPY)
- [ ] Create 5 intermediate examples (hybrid)
- [ ] Create 2 advanced examples (pure Python)
- [ ] Document progression path clearly

---

## 📊 Impact Summary

### **Before (v1.x)**
- 40+ commands (confusing)
- Mixed syntax styles (`SET $var "value"`, `SET [$var = value]`)
- `ECHO` vs `PRINT` confusion
- Unclear when to use uPY vs Python
- No clear learning path

### **After (v2.0)**
- **27 commands** (focused & minimal)
- **Consistent syntax** (`SET ($|)`, `PRINT()`, `{IF:}`)
- **Clear purpose**: Educational gateway + game mechanics
- **Defined progression**: uPY → hybrid → Python
- **Full Python support**: Use anywhere, anytime

### **Benefits**
1. **Easier to learn** - Fewer commands, clearer purpose
2. **Natural progression** - Smooth path to Python
3. **Unique value** - Game mechanics not in Python stdlib
4. **Retro charm** - UPPERCASE, traditional, minimal
5. **Full power** - Can drop into Python for anything complex

---

## 📚 Documentation Created

1. **`wiki/uPY-Syntax-v2.md`** (600 lines)
   - Complete syntax reference
   - All 27 commands documented
   - Examples for every feature
   - Migration guide from old syntax

2. **`wiki/uPY-Command-Set-Analysis.md`** (500 lines)
   - Command inventory and analysis
   - Keep/remove/delegate decisions
   - Python equivalents for all commands
   - Learning path progression examples

3. **`dev/sessions/2025-12-05-upy-v2-syntax-cleanup.md`** (This file)
   - Session summary
   - Design philosophy
   - Next steps and priorities

---

**Total Lines Documented**: 1,100+
**Files Updated**: 2 test files + 3 reference docs
**Commands Simplified**: 40+ → 27
**Clear Learning Path**: ✅ Defined
**Python Integration**: ✅ Full support
**Retro Flavor**: ✅ Maintained

---

*Session completed: December 5, 2025*
