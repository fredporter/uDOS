# uPY Quick Start Tutorial

**Version:** v1.2.x
**Time to Complete:** 10-15 minutes
**Difficulty:** Beginner
**Prerequisites:** uDOS installed, basic programming knowledge

Learn uPY scripting through hands-on examples!

---

## What You'll Learn

✅ Variables with `$` prefix
✅ Emoji codes for better output
✅ Functions for reusable code
✅ JSON for data persistence
✅ Building a simple RPG character system

---

## Step 1: Your First uPY Script (2 minutes)

Create a new file `memory/ucode/scripts/my_first.upy`:

```upy
# My First uPY Script
$NAME = 'Hero'
$HP = 100
PRINT(":wave: Hello, $NAME!")
PRINT(":heart: HP: $HP")
```

**Run it:**
```bash
./start_udos.sh memory/ucode/scripts/my_first.upy
# Or use RUN command inside uDOS:
RUN my_first
```

**Expected Output:**
```
👋 Hello, Hero!
♥ HP: 100
```

**What You Learned:**
- `$VARIABLE = value` - Clean variable assignment
- `PRINT("text")` - Enhanced print with double quotes
- `:emoji:` - Emoji codes (`:wave:` = 👋, `:heart:` = ♥)
- `$VAR` in strings - Automatic variable substitution

---

## Step 2: Adding Emojis (3 minutes)

Emojis make your output more engaging! Try these:

```upy
# Character Status Display
$NAME = 'Hero'
$HP = 85
$GOLD = 50
$LEVEL = 3

PRINT(":shield: === CHARACTER STATUS ===")
PRINT(":person: Name: $NAME")
PRINT(":heart: Health: $HP/100")
PRINT(":coin: Gold: $GOLD coins")
PRINT(":star: Level: $LEVEL")
PRINT("")
PRINT(":check: All systems ready!")
```

**Output:**
```
🛡 === CHARACTER STATUS ===
👤 Name: Hero
♥ Health: 85/100
⊚ Gold: 50 coins
⭐ Level: 3

✓ All systems ready!
```

**Common Emoji Codes:**

| Code | Symbol | Use |
|:-----|:------:|:----|
| `:heart:` | ♥ | Health/HP |
| `:coin:` | ⊚ | Currency |
| `:sword:` | † | Attack |
| `:shield:` | ◊ | Defense |
| `:check:` | ✓ | Success |
| `:cross:` | ✗ | Failure |
| `:warning:` | ⚠ | Warning |
| `:star:` | ⭐ | Important |

[See all 80+ emoji codes →](Emoji-Reference.md)

---

## Step 3: Your First Function (4 minutes)

Functions let you reuse code. Let's create a health checker:

```upy
# Define the function
FUNCTION [@CHECK-HEALTH($HP, $MAX-HP)
    $PERCENT = ($HP / $MAX-HP) * 100

    IF {$PERCENT >= 75 | RETURN ':heart: Healthy'}
    IF {$PERCENT >= 50 | RETURN ':warning: Moderate'}
    IF {$PERCENT >= 25 | RETURN ':cross: Low'}
    RETURN ':skull: Critical'
]

# Use the function
$PLAYER-HP = 85
$MAX-HP = 100

$STATUS = @CHECK-HEALTH($PLAYER-HP, $MAX-HP)
PRINT("Health Status: $STATUS")
```

**Output:**
```
Health Status: ♥ Healthy
```

**Try changing the HP:**
```upy
$PLAYER-HP = 30  # Low health
$STATUS = @CHECK-HEALTH($PLAYER-HP, $MAX-HP)
PRINT("Health Status: $STATUS")
# Output: Health Status: ✗ Low
```

**Function Syntax:**
- `FUNCTION [@NAME($PARAMS) ... ]` - Define function
- `@NAME($ARGS)` - Call function
- `RETURN value` - Return result
- `IF {condition | statement}` - Inline conditional

---

## Step 4: JSON Data Persistence (5 minutes)

Save and load data with JSON:

**Create `sandbox/user/player.json`:**
```json
{
  "name": "Hero",
  "stats": {
    "level": 1,
    "health": 100,
    "max_health": 100,
    "attack": 10,
    "defense": 5
  },
  "inventory": {
    "gold": 0,
    "items": []
  }
}
```

**Load and modify in uPY:**
```upy
# Load player data
JSON.load("sandbox/user/player.json")

# Read data
$NAME = player.name
$HP = player.stats.health
$GOLD = player.inventory.gold

PRINT(":shield: Player: $NAME")
PRINT(":heart: HP: $HP")
PRINT(":coin: Gold: $GOLD")

# Modify data
player.stats.health = player.stats.health - 20
player.inventory.gold = player.inventory.gold + 100
player.inventory.items.append("Health Potion")

# Save changes
JSON.save("sandbox/user/player.json")
PRINT(":check: Progress saved!")
```

**JSON Features:**
- `JSON.load("file.json")` - Load file
- `object.field` - Dot notation access
- `array[0]` - Array indexing
- `array.append(item)` - Add to array
- `JSON.save("file.json")` - Save changes

---

## Step 5: Complete Character System (5 minutes)

Combine everything into a complete system:

**Create `memory/ucode/scripts/character_demo.upy`:**

```upy
# Load player data
JSON.load("sandbox/user/player.json")

# Health check function
FUNCTION [@CHECK-HEALTH($HP, $MAX)
    $PERCENT = ($HP / $MAX) * 100
    IF {$PERCENT >= 75 | RETURN ':heart: Healthy'}
    IF {$PERCENT >= 50 | RETURN ':warning: Moderate'}
    IF {$PERCENT >= 25 | RETURN ':cross: Low'}
    RETURN ':skull: Critical'
]

# Display character
PRINT(":crossed_swords: === ADVENTURE LOG ===")
PRINT("")
PRINT(":person: Hero: " + player.name)
PRINT(":star: Level: " + player.stats.level)
PRINT("")

# Check health
$STATUS = @CHECK-HEALTH(player.stats.health, player.stats.max_health)
PRINT($STATUS + " HP: " + player.stats.health + "/" + player.stats.max_health)
PRINT(":sword: Attack: " + player.stats.attack)
PRINT(":shield: Defense: " + player.stats.defense)
PRINT("")

# Show inventory
PRINT(":coin: Gold: " + player.inventory.gold)
PRINT(":bag: Items: " + player.inventory.items.length + " items")
PRINT("")

# Simulate quest reward
PRINT(":trophy: Quest Complete!")
player.inventory.gold = player.inventory.gold + 50
player.stats.level = player.stats.level + 1
player.inventory.items.append("Magic Sword")

PRINT(":check: Earned 50 gold")
PRINT(":check: Level up!")
PRINT(":check: Found Magic Sword")
PRINT("")

# Save progress
JSON.save("sandbox/user/player.json")
PRINT(":floppy_disk: Progress saved!")
```

**Run it:**
```bash
./start_udos.sh memory/ucode/scripts/character_demo.upy
# Or: RUN character_demo
```

---

## 🎓 What You've Learned

### Variables
```upy
$NAME = 'Hero'           # String
$HP = 100                # Number
$ACTIVE = true           # Boolean
$TOTAL = $A + $B         # Expression
```

### Emojis
```upy
PRINT(":heart: HP: $HP")         # ♥ HP: 100
PRINT(":check: Success!")        # ✓ Success!
PRINT(":warning: Low health!")   # ⚠ Low health!
```

### Functions
```upy
FUNCTION [@GREET($NAME)
    PRINT("Hello, $NAME!")
]

@GREET('Hero')  # Call it
```

### JSON
```upy
JSON.load("data.json")           # Load
$VALUE = object.field            # Read
object.field = 100               # Write
JSON.save("data.json")           # Save
```

---

## 🚀 Next Steps

### More Tutorials
- [Function Programming Guide](Function-Programming-Guide.md) - Deep dive into functions
- [Emoji Reference](Emoji-Reference.md) - All 80+ emoji codes

### Example Projects
Try building:
1. **Inventory Manager** - Track items with JSON
2. **Quest Log** - Complete quests, earn rewards
3. **Combat Simulator** - Turn-based battles
4. **Character Creator** - Build custom heroes

### Advanced Features
- Nested function calls
- Complex JSON structures
- Array manipulation
- Conditional logic patterns

---

## 💡 Quick Tips

### Tip 1: Use Descriptive Variable Names
```upy
# ✅ Good
$PLAYER-HP = 100
$MAX-HEALTH = 100

# ❌ Bad
$X = 100
$Y = 100
```

### Tip 2: Add Emoji for Context
```upy
# ✅ Good - Clear what each stat means
PRINT(":heart: HP: $HP")
PRINT(":sword: Attack: $ATTACK")

# ❌ Less clear
PRINT("HP: $HP")
PRINT("Attack: $ATTACK")
```

### Tip 3: Use Functions for Repeated Logic
```upy
# ✅ Good - Reusable
FUNCTION [@CALCULATE-DAMAGE($BASE, $ARMOR)
    $DMG = $BASE - $ARMOR
    IF {$DMG < 0 | RETURN 0}
    RETURN $DMG
]

# ❌ Repeated code
$DMG1 = $ATK1 - $DEF1
IF {$DMG1 < 0 | $DMG1 = 0}
$DMG2 = $ATK2 - $DEF2
IF {$DMG2 < 0 | $DMG2 = 0}
```

### Tip 4: Save JSON Regularly
```upy
# After important changes
player.inventory.gold = player.inventory.gold + 100
JSON.save("player.json")  # ✅ Save immediately
```

---

## ❓ Troubleshooting

### Script Won't Run
```bash
# Check file extension
mv my_script.txt my_script.upy

# Run with correct path
./start_udos.sh sandbox/ucode/my_script.upy
```

### Emoji Not Showing
```upy
# Use double quotes for PRINT
PRINT(":heart: HP")  # ✅ Works
PRINT(':heart: HP')  # ❌ Won't work
```

### Function Not Found
```upy
# Define before calling
FUNCTION [@GREET($NAME)
    PRINT("Hello, $NAME!")
]

@GREET('Hero')  # ✅ Defined first

# ❌ Calling before definition won't work
```

### JSON File Not Found
```upy
# Use correct path from uDOS root
JSON.load("sandbox/user/player.json")  # ✅ Correct

# Check file exists
# ls sandbox/user/player.json
```

---

## 🎯 Challenge: Build Your Own

Try creating a simple game system with:

1. **Character stats** (HP, attack, defense)
2. **Inventory** (gold, items)
3. **Combat function** (calculate damage)
4. **Quest rewards** (gold, items, XP)
5. **Save/load** (JSON persistence)

**Starter template:**
```upy
# Load or create character
JSON.load("sandbox/user/my_character.json")

# Define combat function
FUNCTION [@ATTACK($ATTACKER-DMG, $DEFENDER-DEF)
    # Your code here
]

# Main game loop
PRINT(":crossed_swords: Adventure begins!")

# Your game logic here

# Save progress
JSON.save("sandbox/user/my_character.json")
PRINT(":check: Game saved!")
```

---

## 📚 Reference

- **[Complete uPY Syntax](uCODE-Language.md#upy-syntax-v119)** - Full language reference
- **[All Commands](Command-Reference.md#upy-commands-v119)** - Command documentation
- **[Emoji Codes](Emoji-Reference.md)** - All 80+ emojis
- **[Functions Guide](Function-Programming-Guide.md)** - Advanced functions

---

**Congratulations!** 🎉 You now know the basics of uPY v1.1.9+ syntax!

**Time Spent:** ~15 minutes
**Skills Gained:** Variables, Emojis, Functions, JSON
**Ready For:** Building your own uPY projects!
