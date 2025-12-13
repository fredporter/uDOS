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

All uCODE commands use square brackets `[...]` with pipe separators `|`:

```
COMMAND[argument1|argument2|argument3]
```

**Example:**
```
GUIDE["water/purification"|"detailed"]
     └─────┬──────┘  └────┬────┘
         Guide topic    Detail level
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
GUIDE["water/purification"|"detailed"]
GUIDE["water/collection"|"simple"]
GUIDE["water/storage"|"technical"]

# Fire guides
GUIDE["fire/friction"|"detailed"]
GUIDE["fire/bow-drill"|"simple"]
GUIDE["fire/safety"|"detailed"]

# Shelter guides
GUIDE["shelter/lean-to"|"detailed"]
GUIDE["shelter/debris-hut"|"simple"]

# Medical guides
GUIDE["medical/wounds"|"detailed"]
GUIDE["medical/burns"|"simple"]
GUIDE["medical/hypothermia"|"technical"]

# Food guides
GUIDE["food/foraging"|"detailed"]
GUIDE["food/preservation"|"simple"]

# Navigation guides
GUIDE["navigation/stars"|"detailed"]
GUIDE["navigation/sun"|"simple"]
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

**Examples:**

```
# Simple message
PRINT["Hello, world!"]

# Multiple messages (shown on separate lines)
PRINT["Water level: 50 liters"|"Food: adequate"|"Shelter: complete"]

# Blank line
PRINT[]

# With special characters (use emoji codes)
PRINT["Score: :sb:100:eb:"]           # Shows: Score: [100]
PRINT["Price: :dollar:50"]             # Shows: Price: $50
PRINT["Use :pipe: to separate"]       # Shows: Use | to separate
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
PRINT["Array: :sb:1, 2, 3:eb:"]              # Array: [1, 2, 3]
PRINT["Email: admin:at:udos.com"]            # Email: admin@udos.com
PRINT["Tag: :hash:important"]                # Tag: #important
PRINT["Math: 2:caret:8 = 256"]               # Math: 2^8 = 256
```

---

## Sprite Commands

### HEAL_SPRITE - Restore Health

**Format:** `HEAL_SPRITE[sprite_id|amount|item]`

**Examples:**

```
# Heal yourself
HEAL_SPRITE["player"|"20"|"bandage"]
HEAL_SPRITE["player"|"50"|"medkit"]

# Heal a companion
HEAL_SPRITE["companion"|"30"|"potion"]

# Emergency healing
HEAL_SPRITE["player"|"100"|"emergency-kit"]
```

**Common items:**
- `bandage` - +20 HP
- `medkit` - +50 HP
- `potion` - +30 HP
- `emergency-kit` - +100 HP

---

## Checkpoint Commands

### CHECKPOINT_SAVE - Save Your Progress

**Format:** `CHECKPOINT_SAVE[checkpoint_name]`

**Examples:**

```
# Save after major milestones
CHECKPOINT_SAVE["camp-established"]
CHECKPOINT_SAVE["water-source-found"]
CHECKPOINT_SAVE["shelter-built"]
CHECKPOINT_SAVE["fire-started"]

# Save before risky actions
CHECKPOINT_SAVE["before-storm"]
CHECKPOINT_SAVE["before-exploration"]
```

**Naming tips:**
- Use dashes, not spaces: `camp-established` not `camp established`
- Be descriptive: `shelter-built` not `checkpoint1`
- Use lowercase: `water-found` not `Water-Found`

### CHECKPOINT_LOAD - Restore Previous State

**Format:** `CHECKPOINT_LOAD[checkpoint_name]`

**Examples:**

```
# Return to previous checkpoint
CHECKPOINT_LOAD["camp-established"]
CHECKPOINT_LOAD["before-storm"]
```

---

## Variable Commands

### GET - Read Saved Values

**Format:** `GET[variable_name]`

**Examples:**

```
# Check your stats
GET["player-hp"]
GET["player-name"]
GET["player-level"]

# Check resources
GET["water-level"]
GET["food-supply"]
GET["wood-count"]

# Check location
GET["camp-location"]
GET["current-grid"]
```

### SET - Save Values

**Format:** `SET[variable_name|value]`

**Examples:**

```
# Set your info
SET["player-name"|"Hero"]
SET["player-level"|"5"]

# Set resources
SET["water-level"|"50"]
SET["food-supply"|"30"]

# Set location
SET["camp-location"|"AA340"]
```

**Variable naming rules:**
- Use dashes: `player-hp` not `player_hp`
- Only letters, numbers, dashes: `camp-1` not `camp#1`
- No spaces: `player-name` not `player name`

---

## Mission Commands

### MISSION_START - Begin a Mission

**Format:** `MISSION_START[mission_name]`

**Examples:**

```
MISSION_START["establish-camp"]
MISSION_START["find-water"]
MISSION_START["build-shelter"]
```

### MISSION_COMPLETE - Finish a Mission

**Format:** `MISSION_COMPLETE[mission_name]`

**Examples:**

```
MISSION_COMPLETE["establish-camp"]
MISSION_COMPLETE["find-water"]
```

### MISSION_STATUS - Check Progress

**Format:** `MISSION_STATUS[]`

**Example:**

```
MISSION_STATUS[]
# Shows: Mission: establish-camp | Status: ACTIVE | Progress: 3/5
```

---

## Experience Commands

### XP - Gain Experience Points

**Format:** `XP[amount]`

**Examples:**

```
# Earn XP for accomplishments
XP["+10"]   # Small task
XP["+50"]   # Medium task
XP["+100"]  # Major achievement
XP["+500"]  # Mission complete
```

### LEVEL_UP - Increase Level

**Format:** `LEVEL_UP[]`

**Example:**

```
LEVEL_UP[]
# Shows: Level up! Now level 6
```

---

## Inventory Commands

### ITEM - Add Item to Inventory

**Format:** `ITEM[item_name]`

**Examples:**

```
ITEM["axe"]
ITEM["rope"]
ITEM["water-filter"]
ITEM["knife"]
ITEM["firestarter"]
```

### INVENTORY - Show Items

**Format:** `INVENTORY[]`

**Example:**

```
INVENTORY[]
# Shows list of all items you have
```

---

## System Commands

### STATUS - Check System Health

**Format:** `STATUS[]` or `STATUS["--health"]`

**Examples:**

```
# Basic status
STATUS[]

# Detailed health check
STATUS["--health"]
# Shows: System OK | Memory: 45% | Files: 1,234 | Errors: 0
```

### TREE - Show File Structure

**Format:** `TREE[]` or `TREE[path]`

**Examples:**

```
# Show all files
TREE[]

# Show specific folder
TREE["memory/ucode/scripts"]
TREE["knowledge/water"]
```

---

## Practical Examples

### Example 1: Starting Your Day

```
# Check your status
MISSION_STATUS[]
GET["water-level"]
GET["player-hp"]

# If low on water, get guidance
GUIDE["water/collection"|"simple"]

# Save checkpoint
CHECKPOINT_SAVE["morning-start"]
```

### Example 2: Building a Shelter

```
# Start mission
MISSION_START["build-shelter"]

# Get instructions
GUIDE["shelter/lean-to"|"detailed"]

# Save progress checkpoints
CHECKPOINT_SAVE["materials-gathered"]
CHECKPOINT_SAVE["frame-built"]
CHECKPOINT_SAVE["cover-complete"]

# Complete mission
MISSION_COMPLETE["build-shelter"]
XP["+100"]
```

### Example 3: Emergency Healing

```
# Check current health
GET["player-hp"]

# If low, heal immediately
HEAL_SPRITE["player"|"50"|"medkit"]

# Check medical guide if needed
GUIDE["medical/wounds"|"detailed"]

# Update status
PRINT["Healing complete"]
```

### Example 4: Resource Management

```
# Check resources
GET["water-level"]
GET["food-supply"]
GET["wood-count"]

# Update after use
SET["water-level"|"45"]
SET["food-supply"|"28"]

# Get help if running low
GUIDE["water/collection"|"quick"]
GUIDE["food/foraging"|"simple"]
```

---

## Tips for Beginners

### 1. Start Simple

Begin with basic commands:
```
PRINT["Hello!"]
STATUS[]
GUIDE["water/purification"|"simple"]
```

### 2. Save Often

Create checkpoints regularly:
```
CHECKPOINT_SAVE["after-water-collection"]
CHECKPOINT_SAVE["shelter-complete"]
CHECKPOINT_SAVE["before-exploration"]
```

### 3. Use Guides

The knowledge bank has everything you need:
```
GUIDE["fire/bow-drill"|"detailed"]
GUIDE["shelter/debris-hut"|"simple"]
GUIDE["medical/hypothermia"|"technical"]
```

### 4. Check Status

Monitor your progress:
```
MISSION_STATUS[]
GET["player-hp"]
INVENTORY[]
```

### 5. Name Things Clearly

Use descriptive names with dashes:
```
✅ Good: CHECKPOINT_SAVE["camp-established"]
❌ Bad: CHECKPOINT_SAVE["cp1"]

✅ Good: SET["water-level"|"50"]
❌ Bad: SET["w"|"50"]
```

---

## Common Mistakes

### Mistake 1: Using Commas

**Wrong:**
```
PRINT["Water", "Food", "Shelter"]
GUIDE["water/purification", "detailed"]
```

**Correct:**
```
PRINT["Water"|"Food"|"Shelter"]
GUIDE["water/purification"|"detailed"]
```

**Rule:** Use pipes `|` not commas `,`

### Mistake 2: Using Spaces in Names

**Wrong:**
```
CHECKPOINT_SAVE["camp established"]
SET["player name"|"Hero"]
```

**Correct:**
```
CHECKPOINT_SAVE["camp-established"]
SET["player-name"|"Hero"]
```

**Rule:** Use dashes `-` not spaces

### Mistake 3: Underscores in Variables

**Wrong:**
```
SET["player_hp"|"100"]
GET["water_level"]
```

**Correct:**
```
SET["player-hp"|"100"]
GET["water-level"]
```

**Rule:** Use dashes `-` not underscores `_`

### Mistake 4: Special Characters Without Codes

**Wrong:**
```
PRINT["Score: [100]"]
PRINT["Price: $50"]
```

**Correct:**
```
PRINT["Score: :sb:100:eb:"]
PRINT["Price: :dollar:50"]
```

**Rule:** Use emoji codes for special characters in output

---

## Quick Command Reference

### Most Used Commands

```
# Information
GUIDE[topic|level]
STATUS[]
TREE[]

# Output
PRINT[message]

# Player
HEAL_SPRITE["player"|amount|item]
XP["+points"]
LEVEL_UP[]

# Inventory
ITEM[name]
INVENTORY[]

# Checkpoints
CHECKPOINT_SAVE[name]
CHECKPOINT_LOAD[name]

# Variables
GET[name]
SET[name|value]

# Missions
MISSION_START[name]
MISSION_COMPLETE[name]
MISSION_STATUS[]
```

---

## Getting More Advanced

Once you're comfortable with these commands, you can:

1. **Learn Python** - Add programming logic (if/else, loops, functions)
2. **Create Scripts** - Save sequences of commands in `.upy` files
3. **Build Workflows** - Automate complex tasks
4. **Use Variables** - Track multiple values and calculations

See **[Python-First Guide](uCODE-Python-First-Guide.md)** for advanced features.

---

## Need Help?

- **Status check:** `STATUS["--health"]`
- **File structure:** `TREE[]`
- **Command list:** `HELP[]`
- **Guides:** Browse `knowledge/` folder with `TREE["knowledge"]`

---

**Level:** Beginner  
**Next:** [uCODE Python-First Guide](uCODE-Python-First-Guide.md)  
**Version:** v1.2.24
