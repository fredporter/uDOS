# uCODE Beginner Commands (v1.2.24)

**Level:** Beginner  
**Focus:** High-level uCODE commands only  
**Last Updated:** December 13, 2025

---

## What is uCODE?

uCODE is uDOS's beginner-friendly command language for survival tasks. Think of it as simple instructions for:

- 🔍 **Finding information** (water guides, fire techniques, medical help)
- 🗺️ **Navigation** (checking your location, moving around the grid)
- ❤️ **Healing** (restoring health, using items)
- 💾 **Saving progress** (checkpoints, mission milestones)
- 📊 **Checking status** (health, resources, mission progress)

**No programming experience needed!** Just follow the examples.

---

## Command Format

uCODE commands use square brackets `[...]` with pipe separators `|` when they need arguments:

```
COMMAND[argument1|argument2|argument3]
```

**Commands without arguments don't use brackets:**
```
STATUS          # Check system status
HELP            # Show available commands
TREE            # Show directory structure
INVENTORY       # Show your items
```

**Example with arguments:**
```
GUIDE[shelter/lean-to|detailed]
     └─────┬──────┘  └────┬────┘
      Guide topic    Detail level
```

**Tags use asterisk (*) notation:**
```
CHECKPOINT*SAVE[materials-gathered]
          ↑
    Tag separator (like command-line flags)
```

**Variables use dollar sign ($) prefix:**
```
SET[$water-level|45]
    ↑
Variable prefix
```

---

## Knowledge Commands

### GUIDE - Get Survival Information

**Format:** `GUIDE[topic|complexity]`

**Complexity levels:**
- `simple` - Basic overview
- `detailed` - Step-by-step instructions
- `technical` - Advanced information

**Examples:**

```
# Water guides
GUIDE[water/purification|detailed]
GUIDE[water/collection|simple]
GUIDE[water/storage|technical]

# Fire guides
GUIDE[fire/friction|detailed]
GUIDE[fire/bow-drill|simple]
GUIDE[fire/safety|detailed]

# Shelter guides
GUIDE[shelter/lean-to|detailed]
GUIDE[shelter/debris-hut|simple]

# Medical guides
GUIDE[medical/wounds|detailed]
GUIDE[medical/burns|simple]
GUIDE[medical/hypothermia|technical]

# Food guides
GUIDE[food/foraging|detailed]
GUIDE[food/preservation|simple]

# Navigation guides
GUIDE[navigation/stars|detailed]
GUIDE[navigation/sun|simple]
```

**Available categories:**
- `water/` - Water collection, purification, storage (26 guides)
- `fire/` - Fire making techniques (20 guides)
- `shelter/` - Shelter construction (20 guides)
- `food/` - Food gathering and preparation (23 guides)
- `medical/` - First aid and health (27 guides)
- `navigation/` - Finding your way (20 guides)

---

## Output Commands

### PRINT - Display Messages

**Format:** `PRINT[message1|message2|...]`

**Note:** PRINT is a basic Python command used in UPPERCASE within uCODE for consistency.

**Examples:**

```
# Simple message
PRINT[Hello, world!]

# Multiple messages (shown on separate lines)
PRINT[Water level: 50 liters|Food: adequate|Shelter: complete]

# Blank line
PRINT[]

# With special characters (use emoji codes)
PRINT[Score: :sb:100:eb:]           # Shows: Score: [100]
PRINT[Price: :dollar:50]             # Shows: Price: $50
PRINT[Use :pipe: to separate]       # Shows: Use | to separate
```

**Special Characters in Output:**

When you need to show special characters, use emoji codes:

| Character | Emoji Code | Example Output |
|-----------|------------|----------------|
| [ | `:sb:` | [100] |
| ] | `:eb:` | [100] |
| \| | `:pipe:` | Use \| here |
| $ | `:dollar:` | $50 |
| # | `:hash:` | #tag |
| @ | `:at:` | user@domain |
| * | `:star:` | * bullet |
| _ | `:underscore:` | snake_case |

**Common emoji codes:**
```
PRINT[Array: :sb:1, 2, 3:eb:]              # Array: [1, 2, 3]
PRINT[Email: admin:at:udos.com]            # Email: admin@udos.com
PRINT[Tag: :hash:important]                # Tag: #important
PRINT[Math: 2:caret:8 = 256]               # Math: 2^8 = 256
```

---

## Sprite Commands

### HEAL*SPRITE - Restore Health

**Format:** `HEAL*SPRITE[sprite_id|amount|item]`

**Examples:**

```
# Heal yourself
HEAL*SPRITE[player|20|bandage]
HEAL*SPRITE[player|50|medkit]

# Heal a companion
HEAL*SPRITE[companion|30|potion]

# Emergency healing
HEAL*SPRITE[player|100|emergency-kit]
```

**Common items:**
- `bandage` - +20 HP
- `medkit` - +50 HP
- `potion` - +30 HP
- `emergency-kit` - +100 HP

---

## Checkpoint Commands

### CHECKPOINT*SAVE - Save Your Progress

**Format:** `CHECKPOINT*SAVE[checkpoint_name]`

**Note:** The asterisk (*) is used as a tag separator, similar to command-line flags.

**Examples:**

```
# Save after major milestones
CHECKPOINT*SAVE[camp-established]
CHECKPOINT*SAVE[water-source-found]
CHECKPOINT*SAVE[shelter-built]
CHECKPOINT*SAVE[fire-started]

# Save before risky actions
CHECKPOINT*SAVE[before-storm]
CHECKPOINT*SAVE[before-exploration]
```

**Naming tips:**
- Use dashes, not spaces: `camp-established` not `camp established`
- Be descriptive: `shelter-built` not `checkpoint1`
- Use lowercase: `water-found` not `Water-Found`

### CHECKPOINT*LOAD - Restore Previous State

**Format:** `CHECKPOINT*LOAD[checkpoint_name]`

**Examples:**

```
# Return to previous checkpoint
CHECKPOINT*LOAD[camp-established]
CHECKPOINT*LOAD[before-storm]
```

---

## Variable Commands

### GET - Read Saved Values

**Format:** `GET[$variable_name]`

**Note:** Variables use the `$` prefix to distinguish them from plain text.

**Examples:**

```
# Check your stats
GET[$player-hp]
GET[$player-name]
GET[$player-level]

# Check resources
GET[$water-level]
GET[$food-supply]
GET[$wood-count]

# Check location
GET[$camp-location]
GET[$current-grid]
```

### SET - Save Values

**Format:** `SET[$variable_name|value]`

**Examples:**

```
# Set your info
SET[$player-name|Hero]
SET[$player-level|5]

# Set resources
SET[$water-level|50]
SET[$food-supply|30]

# Set location
SET[$camp-location|AA340]
```

**Variable naming rules:**
- Use $ prefix: `$player-hp` not `player-hp`
- Use dashes: `$player-hp` not `$player_hp` (no underscores)
- Only letters, numbers, dashes: `$camp-1` not `$camp#1`
- No spaces: `$player-name` not `$player name`

---

## Mission Commands

### MISSION*START - Begin a Mission

**Format:** `MISSION*START[mission_name]`

**Examples:**

```
MISSION*START[establish-camp]
MISSION*START[find-water]
MISSION*START[build-shelter]
```

### MISSION*COMPLETE - Finish a Mission

**Format:** `MISSION*COMPLETE[mission_name]`

**Examples:**

```
MISSION*COMPLETE[establish-camp]
MISSION*COMPLETE[find-water]
```

### MISSION*STATUS - Check Progress

**Format:** `MISSION*STATUS` (no brackets needed)

**Example:**

```
MISSION*STATUS
# Shows: Mission: establish-camp | Status: ACTIVE | Progress: 3/5
```

---

## Experience Commands

### XP - Gain Experience Points

**Format:** `XP[amount]`

**Examples:**

```
# Earn XP for accomplishments
XP[+10]   # Small task
XP[+50]   # Medium task
XP[+100]  # Major achievement
XP[+500]  # Mission complete
```

### LEVEL*UP - Increase Level

**Format:** `LEVEL*UP` (no brackets needed)

**Example:**

```
LEVEL*UP
# Shows: Level up! Now level 6
```

---

## Inventory Commands

### ITEM - Add Item to Inventory

**Format:** `ITEM[item_name]`

**Examples:**

```
ITEM[axe]
ITEM[rope]
ITEM[water-filter]
ITEM[knife]
ITEM[firestarter]
```

### INVENTORY - Show Items

**Format:** `INVENTORY` (no brackets needed)

**Example:**

```
INVENTORY
# Shows list of all items you have
```

---

## System Commands

### STATUS - Check System Health

**Format:** `STATUS` or `STATUS*HEALTH`

**Examples:**

```
# Basic status
STATUS

# Detailed health check
STATUS*HEALTH
# Shows: System OK | Memory: 45% | Files: 1,234 | Errors: 0
```

### TREE - Show File Structure

**Format:** `TREE` or `TREE[path]`

**Examples:**

```
# Show all files
TREE

# Show specific folder
TREE[memory/ucode/scripts]
TREE[knowledge/water]
```

---

## Basic Python Commands in uCODE

These Python basics are shown in UPPERCASE when used in uCODE context:

### IF/THEN - Conditional Logic

**Format:** `IF condition THEN action`

**Examples:**

```
# Check health and heal if needed
IF GET[$player-hp] < 50 THEN HEAL*SPRITE[player|30|medkit]

# Check resources
IF GET[$water-level] < 20 THEN PRINT[Warning: Water low!]

# Multiple conditions
IF GET[$player-level] > 5 THEN XP[+100]
IF GET[$camp-location] == AA340 THEN PRINT[You are at base camp]
```

### FUNCTION - Reusable Code Blocks

**Format:** `FUNCTION[@function*tag]`

**Examples:**

```
# Define a function for daily routine
FUNCTION[@daily*check]
  PRINT[Starting daily check...]
  GET[$water-level]
  GET[$food-supply]
  IF GET[$water-level] < 30 THEN PRINT[Collect water today]
  IF GET[$food-supply] < 20 THEN PRINT[Gather food today]
  CHECKPOINT*SAVE[daily-check-complete]
END FUNCTION

# Call the function
@daily*check
```

**Note:** As you progress, you'll learn to use lowercase Python syntax for more advanced programming. See the [Python Advanced Guide](uCODE-Python-Advanced.md) for details.

---

## Practical Examples

### Example 1: Starting Your Day

```
# Check your status
MISSION*STATUS
GET[$water-level]
GET[$player-hp]

# If low on water, get guidance
GUIDE[water/collection|simple]

# Save checkpoint
CHECKPOINT*SAVE[morning-start]
```

### Example 2: Building a Shelter

```
# Start mission
MISSION*START[build-shelter]

# Get instructions
GUIDE[shelter/lean-to|detailed]

# Save progress checkpoints
CHECKPOINT*SAVE[materials-gathered]
CHECKPOINT*SAVE[frame-built]
CHECKPOINT*SAVE[cover-complete]

# Complete mission
MISSION*COMPLETE[build-shelter]
XP[+100]
```

### Example 3: Emergency Healing

```
# Check current health
GET[$player-hp]

# If low, heal immediately
IF GET[$player-hp] < 50 THEN HEAL*SPRITE[player|50|medkit]

# Check medical guide if needed
GUIDE[medical/wounds|detailed]

# Update status
PRINT[Healing complete]
```

### Example 4: Resource Management

```
# Check resources
GET[$water-level]
GET[$food-supply]
GET[$wood-count]

# Update after use
SET[$water-level|45]
SET[$food-supply|28]

# Get help if running low
IF GET[$water-level] < 30 THEN GUIDE[water/collection|simple]
IF GET[$food-supply] < 25 THEN GUIDE[food/foraging|simple]
```

---

## Tips for Beginners

### 1. Start Simple

Begin with basic commands:
```
PRINT[Hello!]
STATUS
GUIDE[water/purification|simple]
```

### 2. Save Often

Create checkpoints regularly:
```
CHECKPOINT*SAVE[after-water-collection]
CHECKPOINT*SAVE[shelter-complete]
CHECKPOINT*SAVE[before-exploration]
```

### 3. Use Guides

The knowledge bank has everything you need:
```
GUIDE[fire/bow-drill|detailed]
GUIDE[shelter/debris-hut|simple]
GUIDE[medical/hypothermia|technical]
```

### 4. Check Status

Monitor your progress:
```
MISSION*STATUS
GET[$player-hp]
INVENTORY
```

### 5. Name Things Clearly

Use descriptive names with dashes:
```
✅ Good: CHECKPOINT*SAVE[camp-established]
❌ Bad: CHECKPOINT*SAVE[cp1]

✅ Good: SET[$water-level|50]
❌ Bad: SET[$w|50]
```

---

## Common Mistakes

### Mistake 1: Using Commas

**Wrong:**
```
PRINT[Water, Food, Shelter]
GUIDE[water/purification, detailed]
```

**Correct:**
```
PRINT[Water|Food|Shelter]
GUIDE[water/purification|detailed]
```

**Rule:** Use pipes `|` not commas `,`

### Mistake 2: Using Spaces in Names

**Wrong:**
```
CHECKPOINT*SAVE[camp established]
SET[$player name|Hero]
```

**Correct:**
```
CHECKPOINT*SAVE[camp-established]
SET[$player-name|Hero]
```

**Rule:** Use dashes `-` not spaces

### Mistake 3: Underscores Instead of Asterisks

**Wrong:**
```
CHECKPOINT_SAVE[camp-established]
MISSION_START[find-water]
LEVEL_UP
```

**Correct:**
```
CHECKPOINT*SAVE[camp-established]
MISSION*START[find-water]
LEVEL*UP
```

**Rule:** Use asterisks `*` not underscores `_` for tags

### Mistake 4: Missing $ Prefix on Variables

**Wrong:**
```
SET[player-hp|100]
GET[water-level]
```

**Correct:**
```
SET[$player-hp|100]
GET[$water-level]
```

**Rule:** Always use `$` prefix for variables

### Mistake 5: Empty Brackets on Commands

**Wrong:**
```
STATUS[]
INVENTORY[]
TREE[]
```

**Correct:**
```
STATUS
INVENTORY
TREE
```

**Rule:** Don't use empty brackets - commands work without them

---

## Quick Command Reference

### Most Used Commands

```
# Information
GUIDE[topic|level]
STATUS
TREE

# Output
PRINT[message]

# Player
HEAL*SPRITE[player|amount|item]
XP[+points]
LEVEL*UP

# Inventory
ITEM[name]
INVENTORY

# Checkpoints
CHECKPOINT*SAVE[name]
CHECKPOINT*LOAD[name]

# Variables
GET[$name]
SET[$name|value]

# Missions
MISSION*START[name]
MISSION*COMPLETE[name]
MISSION*STATUS

# Basic Python (UPPERCASE in uCODE)
IF condition THEN action
FUNCTION[@name*tag]
```

---

## Getting More Advanced

Once you're comfortable with these commands, you can:

1. **Learn Python Integration** - Combine uCODE with Python logic
2. **Create Scripts** - Save sequences of commands in `.upy` files
3. **Build Workflows** - Automate complex tasks
4. **Use Advanced Features** - Loops, functions, classes

### Learning Path

1. **You are here:** Beginner Commands (UPPERCASE uCODE)
2. **Next:** [Python-First Guide](uCODE-Python-First-Guide.md) (Integration layer)
3. **Advanced:** [Python Advanced](uCODE-Python-Advanced.md) (Full Python, lowercase)

---

## Need Help?

- **Status check:** `STATUS*HEALTH`
- **File structure:** `TREE`
- **Command list:** `HELP`
- **Guides:** Browse `knowledge/` folder with `TREE[knowledge]`
- **Quick Reference:** [uCODE Quick Reference](uCODE-Quick-Reference.md)

---

**Level:** Beginner  
**Next:** [uCODE Python-First Guide](uCODE-Python-First-Guide.md)  
**Version:** v1.2.24
