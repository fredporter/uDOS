# Adventure Scripting Guide - uPY Format

**Complete guide to creating interactive text adventures in uDOS using `.upy` scripts**

**Version:** v2.0.2 (uDOS v1.2.x)
**Last Updated:** December 7, 2025

## Table of Contents

1. [Quick Start](#quick-start)
2. [File Format](#file-format)
3. [Command Reference](#command-reference)
4. [Variables](#variables)
5. [Control Flow](#control-flow)
6. [Character System](#character-system)
7. [Story Progression](#story-progression)
8. [Examples](#examples)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Creating Your First Adventure

```bash
# In uDOS
STORY CREATE my_adventure

# Edit the generated file
# memory/ucode/adventures/my_adventure.upy

# Run your adventure
STORY RUN my_adventure
```

### Minimal Adventure Example

```python
#!/usr/bin/env udos
# Simple adventure script

# Initialize character
SET (SPRITE-NAME|'Hero')
SET (SPRITE-HP|100)
SET (SPRITE-XP|0)

# Story intro
PRINT ['Welcome to the adventure, $SPRITE-NAME!']
PRINT ['You stand at a crossroads...']

# Simple choice
CHOICE ['Which path do you take?']
  OPTION ['Go left'] → BRANCH-LEFT
  OPTION ['Go right'] → BRANCH-RIGHT

LABEL [BRANCH-LEFT]
PRINT ['You chose the left path and found treasure!']
XP [+50]
ITEM [treasure_chest]
END

LABEL [BRANCH-RIGHT]
PRINT ['You chose the right path and avoided danger!']
HP [+10]
END
```

---

## File Format

### File Structure

- **Extension**: `.upy` (uPython Adventure)
- **Encoding**: UTF-8
- **Shebang**: `#!/usr/bin/env python3` (optional)
- **Comments**: Lines starting with `#`
- **Blank lines**: Ignored

### Basic Anatomy

```python
#!/usr/bin/env python3
# Adventure title and description

# Section 1: Initialization
SET [$SPRITE-NAME = "Hero"]
SET [$SPRITE-HP = 100]

# Section 2: Story
PRINT [Story text here...]

# Section 3: Choices and branching
CHOICE [Question?]
  OPTION [Choice 1] → BRANCH-LABEL1
  OPTION [Choice 2] → BRANCH-LABEL2

# Section 4: Labels and branches
LABEL [BRANCH-LABEL1]
PRINT [Result of choice 1]
END

LABEL [BRANCH-LABEL2]
PRINT [Result of choice 2]
END
```

---

## Command Reference

### Text Output

#### PRINT

Display text to the player.

**Syntax:**
```python
PRINT ['text with $VARIABLES']
```

**Examples:**
```python
PRINT ['Welcome to the adventure!']
PRINT ['Your current HP: $SPRITE-HP/$SPRITE-HP-MAX']
PRINT ['You have $SPRITE-GOLD gold coins.']
PRINT []  # Blank line
```

**Variable Substitution:**
- `$VAR-NAME` - Replaced with variable value
- Works with all SPRITE, OBJECT, STORY variables

---

### Variables

#### SET

Set a variable value.

**Syntax:**
```python
SET (VARIABLE-NAME|value)
```

**Examples:**
```python
# Strings (use single quotes)
SET (SPRITE-NAME|'Alice')
SET (LOCATION|'forest')

# Numbers (no quotes)
SET (SPRITE-HP|100)
SET (SPRITE-LEVEL|1)
SET (COUNTER|0)

# Floats
SET (RATIO|0.75)
SET (MULTIPLIER|1.5)

# Arrays
SET (SPRITE-INVENTORY|[])
SET (STORY-FLAGS|[])
```

**Valid Variable Names:**
- Use UPPERCASE-HYPHEN format
- Start with letter
- Can contain numbers
- Example: `SPRITE-HP`, `QUEST-COUNTER`, `TEMP-VAR-1`

---

### Character Stats

#### XP

Modify experience points.

**Syntax:**
```python
XP [+amount]   # Gain XP
XP [-amount]   # Lose XP
```

**Examples:**
```python
XP [+50]       # Gain 50 XP
XP [+100]      # Gain 100 XP
XP [-25]       # Lose 25 XP
```

**Level Up System:**
- Automatic level up at `SPRITE-LEVEL * 100` XP
- Example: Level 1 → 2 requires 100 XP
- Example: Level 2 → 3 requires 200 XP
- On level up:
  - `SPRITE-LEVEL` increases by 1
  - `SPRITE-HP` restored to `SPRITE-HP-MAX`
  - Announcement displayed

#### HP

Modify health points.

**Syntax:**
```python
HP [+amount]   # Heal
HP [-amount]   # Take damage
```

**Examples:**
```python
HP [+20]       # Restore 20 HP
HP [-15]       # Take 15 damage
HP [+50]       # Restore 50 HP (capped at HP-MAX)
```

**HP Rules:**
- Cannot exceed `SPRITE-HP-MAX`
- Cannot go below 0
- Death occurs at 0 HP (adventure may end)

---

### Inventory

#### ITEM

Add item to inventory.

**Syntax:**
```python
ITEM [item_id]
```

**Examples:**
```python
ITEM [sword]
ITEM [health_potion]
ITEM [rusty_key]
ITEM [treasure_chest]
```

**Notes:**
- Items added to `SPRITE-INVENTORY` array
- Max 50 items (default)
- Item IDs should be lowercase with underscores
- Use with OBJECT variables for item properties

---

### Story Tracking

#### FLAG

Set a story flag (event marker).

**Syntax:**
```python
FLAG [flag_name]
```

**Examples:**
```python
FLAG [met_wizard]
FLAG [found_water_source]
FLAG [completed_quest_1]
FLAG [entered_cave]
```

**Uses:**
- Track player progress
- Check if events occurred
- Gate content (check flags in IF statements)
- Saved in `STORY-FLAGS` array

---

### Choices & Branching

#### CHOICE

Present options to the player.

**Syntax:**
```python
CHOICE [Question text?]
  OPTION [Choice 1 text] → BRANCH-LABEL1
  OPTION [Choice 2 text] → BRANCH-LABEL2
  OPTION [Choice 3 text] → BRANCH-LABEL3
```

**Examples:**
```python
CHOICE ['What do you do?']
  OPTION ['Fight the monster'] → BRANCH-COMBAT
  OPTION ['Try to sneak past'] → BRANCH-STEALTH
  OPTION ['Run away'] → BRANCH-FLEE

CHOICE ['Which path?']
  OPTION ['North (forest)'] → BRANCH-FOREST
  OPTION ['South (river)'] → BRANCH-RIVER
  OPTION ['East (mountain)'] → BRANCH-MOUNTAIN
```

**Rules:**
- Player enters number (1, 2, 3, etc.)
- Choice stored in `STORY-CHOICES`
- Invalid input prompts retry
- Can have 2-10 options

#### LABEL

Define a jump target.

**Syntax:**
```python
LABEL [LABEL-NAME]
```

**Examples:**
```python
LABEL [START]
LABEL [FOREST-PATH]
LABEL [COMBAT-VICTORY]
LABEL [ENDING-GOOD]
```

**Label Naming:**
- UPPERCASE with hyphens
- Descriptive names
- Must be unique per adventure

#### BRANCH

Jump to a label.

**Syntax:**
```python
BRANCH [LABEL-NAME]
```

**Examples:**
```python
BRANCH [START]
BRANCH [NEXT-CHAPTER]
BRANCH [ENDING]
```

---

### Dice Rolling

#### ROLL

Roll dice and store result.

**Syntax:**
```python
ROLL [dice] → VARIABLE
```

**Dice Notation:**
- `1d20` - One 20-sided die (1-20)
- `2d6` - Two 6-sided dice (2-12)
- `3d8` - Three 8-sided dice (3-24)
- `1d100` - Percentile die (1-100)

**Examples:**
```python
ROLL [1d20] → ATTACK-ROLL
ROLL [2d6] → DAMAGE
ROLL [1d100] → LUCK-CHECK
ROLL [3d8] → FIREBALL-DAMAGE
```

**Usage with IF:**
```python
ROLL [1d20] → SEARCH-ROLL
{IF SEARCH-ROLL >= 15: PRINT ['You found treasure!']}
{IF SEARCH-ROLL >= 15: ITEM [gold_coins]}
```

---

### Conditionals

#### IF / ENDIF

Conditional execution.

**Syntax:**
```python
{IF condition: COMMAND()}
```

**Comparisons:**
- `>` Greater than
- `<` Less than
- `>=` Greater than or equal
- `<=` Less than or equal
- `==` Equal
- `!=` Not equal

**Examples:**
```python
# Numeric comparison
{IF SPRITE-HP < 30: PRINT ['You’re badly wounded!']}
{IF SPRITE-HP < 30: HP [+10]}  # Emergency healing

# Greater than or equal
{IF SPRITE-LEVEL >= 5: PRINT ['You’re strong enough to enter!']}
{IF SPRITE-LEVEL >= 5: BRANCH [DUNGEON]}

# String comparison
{IF SPRITE-NAME == 'Alice': PRINT ['Hello, Alice!']}

# Multiple conditions
{IF ROLL-RESULT >= 18: PRINT ['Critical success!']}
{IF ROLL-RESULT >= 18: XP [+100]}

{IF ROLL-RESULT < 5: PRINT ['Critical failure!']}
{IF ROLL-RESULT < 5: HP [-20]}
```

---

### Flow Control

#### END

Terminate adventure.

**Syntax:**
```python
END
```

**Examples:**
```python
PRINT ['You have completed the quest!']
XP [+500]
FLAG [quest_complete]
END

# Multiple endings
LABEL [ENDING-VICTORY]
PRINT ['You saved the kingdom!']
END

LABEL [ENDING-DEFEAT]
PRINT ['You were defeated...']
END
```

---

## Variables

### SPRITE Variables (Character Stats)

Character-related variables (session scope).

#### Core Stats
```python
SPRITE-NAME          # String - Character name
SPRITE-HP            # Integer - Current health (0-999)
SPRITE-HP-MAX        # Integer - Maximum health (0-999)
SPRITE-XP            # Integer - Experience points (0-999999)
SPRITE-LEVEL         # Integer - Character level (1-99)
SPRITE-GOLD          # Integer - Gold/currency (0-999999)
```

#### Ability Scores
```python
SPRITE-STRENGTH      # Integer - Physical power (1-20)
SPRITE-DEXTERITY     # Integer - Agility/speed (1-20)
SPRITE-INTELLIGENCE  # Integer - Mental ability (1-20)
SPRITE-STAMINA       # Integer - Endurance (0-999)
```

#### Equipment & Status
```python
SPRITE-INVENTORY         # Array - Items held (max 50)
SPRITE-EQUIPPED-WEAPON   # String - Current weapon
SPRITE-EQUIPPED-ARMOR    # String - Current armor
SPRITE-STATUS            # String - Status effect
                         # (normal, poisoned, stunned, etc.)
SPRITE-LOCATION          # String - Current TILE code
```

**Example Usage:**
```python
# Initialize character
SET [$SPRITE-NAME = "Ranger"]
SET [$SPRITE-HP = 100]
SET [$SPRITE-HP-MAX = 100]
SET [$SPRITE-LEVEL = 1]
SET (SPRITE-STRENGTH|14)
SET (SPRITE-DEXTERITY|16)
SET (SPRITE-INTELLIGENCE|10)

# Use in gameplay
ROLL [1d20] → ATTACK-ROLL
{IF ATTACK-ROLL >= SPRITE-DEXTERITY: PRINT ['Your attack hits!']}
{IF ATTACK-ROLL >= SPRITE-DEXTERITY: HP [-10]}
```

### STORY Variables (Progression)

Story and quest tracking (session scope).

```python
STORY-CURRENT           # String - Current adventure name
STORY-CHAPTER           # Integer - Chapter number (1-99)
STORY-CHECKPOINT        # String - Last checkpoint
STORY-FLAGS             # Array - Event flags (max 100)
STORY-CHOICES           # Object - Player choices made
STORY-QUEST-ACTIVE      # Array - Active quests (max 20)
STORY-QUEST-COMPLETED   # Array - Completed quests (max 200)
STORY-NPC-MET           # Array - NPCs encountered (max 100)
STORY-LOCATIONS-VISITED # Array - Places visited (max 500)
STORY-DIALOGUE-SEEN     # Array - Dialogue IDs (max 500)
STORY-TIME-ELAPSED      # Integer - In-game time (minutes)
STORY-ENDING            # String - Ending achieved
STORY-DIFFICULTY        # String - Difficulty level
```

**Example Usage:**
```python
# Track progress
SET (STORY-CURRENT|'water_quest')
SET (STORY-CHAPTER|1)
FLAG [found_water_source]
FLAG [purified_water]

# Check progress
{IF STORY-CHAPTER >= 3: PRINT ['You’ve come far in your journey...']}
```

### OBJECT Variables (Items)

Item and equipment properties (local scope - per object).

```python
OBJECT-ID            # String - Unique item identifier
OBJECT-NAME          # String - Display name
OBJECT-TYPE          # String - weapon, armor, consumable, etc.
OBJECT-DESCRIPTION   # String - Item description
OBJECT-DAMAGE        # Integer - Weapon damage (0-999)
OBJECT-DEFENSE       # Integer - Armor value (0-999)
OBJECT-DURABILITY    # Integer - Item condition (0-100)
OBJECT-VALUE         # Integer - Gold value (0-999999)
OBJECT-WEIGHT        # Number - Item weight (0.0-999.9)
OBJECT-STACKABLE     # Boolean - Can stack
OBJECT-STACK-SIZE    # Integer - Items in stack (1-999)
OBJECT-EFFECT        # String - Special effect
OBJECT-EFFECT-VALUE  # Integer - Effect magnitude
OBJECT-REQUIRED-LEVEL # Integer - Level required (1-99)
OBJECT-LOCATION      # String - Current TILE code
OBJECT-OWNER         # String - Owner ID
```

**Example Usage:**
```python
# In future: Define items
# SET [$OBJECT-ID = "health_potion"]
# SET [$OBJECT-NAME = "Health Potion"]
# SET [$OBJECT-TYPE = "consumable"]
# SET [$OBJECT-EFFECT = "heal"]
# SET [$OBJECT-EFFECT-VALUE = 50]
```

---

## Control Flow

### Linear Story
```python
PRINT ['Part 1']
PRINT ['Part 2']
PRINT ['Part 3']
END
```

### Branching Story
```python
CHOICE ['Fork in the road?']
  OPTION ['Left'] → BRANCH-LEFT
  OPTION ['Right'] → BRANCH-RIGHT

LABEL [BRANCH-LEFT]
PRINT ['You went left...']
BRANCH [REUNION]

LABEL [BRANCH-RIGHT]
PRINT ['You went right...']
BRANCH [REUNION]

LABEL [REUNION]
PRINT ['The paths meet again.']
END
```

### Conditional Story
```python
ROLL [1d20] → LUCK
{IF LUCK >= 15: PRINT ['You got lucky!']}
{IF LUCK >= 15: BRANCH [SUCCESS]}

PRINT ['Not lucky this time.']
BRANCH [FAILURE]

LABEL [SUCCESS]
XP [+50]
END

LABEL [FAILURE]
HP [-10]
END
```

---

## Character System

### Character Creation

```python
# Full character setup
SET (SPRITE-NAME|'Aria')
SET (SPRITE-HP|100)
SET (SPRITE-HP-MAX|100)
SET (SPRITE-LEVEL|1)
SET (SPRITE-XP|0)
SET (SPRITE-GOLD|50)

# Ability scores
SET (SPRITE-STRENGTH|12)
SET (SPRITE-DEXTERITY|16)
SET (SPRITE-INTELLIGENCE|14)
SET (SPRITE-STAMINA|100)

# Starting equipment
SET (SPRITE-INVENTORY|[])
ITEM [short_sword]
ITEM [leather_armor]
ITEM [health_potion]
```

### Combat Example

```python
PRINT ['A goblin attacks!']
PRINT []

ROLL [1d20] → ATTACK-ROLL
PRINT [🎲 Attack roll: $ATTACK-ROLL]

{IF ATTACK-ROLL >= 12: PRINT ['You hit the goblin!']}
{IF ATTACK-ROLL >= 12: ROLL [1d8] → DAMAGE}
{IF ATTACK-ROLL >= 12: PRINT [💥 Damage: $DAMAGE]}
{IF ATTACK-ROLL >= 12: XP [+25]}
{IF ATTACK-ROLL >= 12: BRANCH [VICTORY]}

PRINT ['You missed!']
PRINT ['The goblin strikes back!']
HP [-8]

CHOICE ['What now?']
  OPTION ['Attack again'] → BRANCH-COMBAT
  OPTION ['Flee'] → BRANCH-FLEE

LABEL [VICTORY]
PRINT ['The goblin is defeated!']
ITEM [goblin_ear]
XP [+50]
END
```

### Leveling System

```python
# Award XP
XP [+100]

# System automatically checks:
# if XP >= (SPRITE-LEVEL * 100):
#   - Increase SPRITE-LEVEL
#   - Restore HP to max
#   - Display level up message

# After level 1→2 (100 XP threshold):
PRINT [🎉 Level up! Now level $SPRITE-LEVEL]
PRINT [❤️  HP fully restored!]
```

---

## Story Progression

### Checkpoints

```python
LABEL [CHAPTER-1]
SET (STORY-CHAPTER|1)
FLAG [chapter_1_started]
PRINT ['Chapter 1: The Beginning']
# ... story ...
BRANCH [CHAPTER-2]

LABEL [CHAPTER-2]
SET (STORY-CHAPTER|2)
FLAG [chapter_2_started]
PRINT ['Chapter 2: The Journey']
# ... story ...
END
```

### Quest Tracking

```python
# Start quest
PRINT ['A villager asks for your help...']
FLAG [water_quest_started]

# Quest progress
PRINT ['You found the well!']
FLAG [well_discovered]

# Quest completion
PRINT ['You purified the water!']
FLAG [water_quest_complete]
XP [+200]
```

### Multiple Endings

```python
LABEL [ENDING-CHECK]

{IF STORY-FLAGS-contains-'saved_village': BRANCH [ENDING-HERO]}
{IF SPRITE-LEVEL >= 10: BRANCH [ENDING-CHAMPION]}

BRANCH [ENDING-SURVIVOR]

LABEL [ENDING-HERO]
PRINT [==========================================]
PRINT [  ENDING: HERO OF THE PEOPLE]
PRINT [==========================================]
XP [+1000]
SET (STORY-ENDING|'hero')
END

LABEL [ENDING-CHAMPION]
PRINT [==========================================]
PRINT [  ENDING: LEGENDARY CHAMPION]
PRINT [==========================================]
XP [+500]
SET (STORY-ENDING|'champion')
END

LABEL [ENDING-SURVIVOR]
PRINT [==========================================]
PRINT [  ENDING: SURVIVOR]
PRINT [==========================================]
XP [+100]
SET (STORY-ENDING|'survivor')
END
```

---

## Examples

### Example 1: Simple Exploration

```python
#!/usr/bin/env udos
# Simple exploration adventure

SET (SPRITE-NAME|'Explorer')
SET (SPRITE-HP|100)
SET (SPRITE-XP|0)

PRINT ['You enter a dark cave...']
PRINT []

CHOICE ['What do you do?']
  OPTION ['Light a torch'] → BRANCH-TORCH
  OPTION ['Feel along the walls'] → BRANCH-WALLS

LABEL [BRANCH-TORCH]
PRINT ['The torch illuminates ancient paintings!']
XP [+30]
FLAG [saw_paintings]
END

LABEL [BRANCH-WALLS]
PRINT ['You feel smooth stone carved with symbols...']
ROLL [1d20] → PERCEPTION
{IF PERCEPTION >= 14: PRINT ['You found a secret passage!']}
{IF PERCEPTION >= 14: XP [+50]}
{IF PERCEPTION >= 14: FLAG [found_secret]}
END
```

### Example 2: Survival Challenge

```python
#!/usr/bin/env udos
# Survival challenge

SET (SPRITE-NAME|'Survivor')
SET (SPRITE-HP|80)  # Start damaged
SET (SPRITE-STAMINA|100)

PRINT ['You’re stranded with limited supplies...']
PRINT ['Current HP: $SPRITE-HP']
PRINT []

CHOICE ['Priorities?']
  OPTION ['Find water (critical)'] → BRANCH-WATER
  OPTION ['Build shelter (important)'] → BRANCH-SHELTER
  OPTION ['Find food (can wait)'] → BRANCH-FOOD

LABEL [BRANCH-WATER]
PRINT ['You search for water...']
ROLL [1d20] → SEARCH
{IF SEARCH >= 12: PRINT ['You found a stream!']}
{IF SEARCH >= 12: HP [+20]}
{IF SEARCH >= 12: XP [+40]}
{IF SEARCH >= 12: FLAG [found_water]}
{IF SEARCH < 12: PRINT ['No water found. Dehydration worsens.']}
{IF SEARCH < 12: HP [-10]}
END

LABEL [BRANCH-SHELTER]
PRINT ['You build a lean-to shelter...']
XP [+30]
FLAG [built_shelter]
END

LABEL [BRANCH-FOOD]
PRINT ['You search for food...']
ROLL [1d20] → FORAGE
{IF FORAGE >= 14: PRINT ['Found berries!']}
{IF FORAGE >= 14: HP [+5]}
{IF FORAGE >= 14: XP [+20]}
END
```

### Example 3: Skill Check Challenge

```python
#!/usr/bin/env udos
# Skill-based challenge

SET (SPRITE-NAME|'Rogue')
SET (SPRITE-DEXTERITY|16)
SET (SPRITE-HP|100)

PRINT ['You encounter a locked chest...']
PRINT []

CHOICE ['How do you open it?']
  OPTION ['Pick the lock (DEX check)'] → BRANCH-LOCKPICK
  OPTION ['Force it open (STR check)'] → BRANCH-FORCE
  OPTION ['Leave it alone'] → BRANCH-LEAVE

LABEL [BRANCH-LOCKPICK]
PRINT ['You attempt to pick the lock...']
ROLL [1d20] → LOCKPICK-ROLL

# Add DEX modifier
SET (TOTAL|LOCKPICK-ROLL)
PRINT [🎲 Roll: $LOCKPICK-ROLL + DEX ($SPRITE-DEXTERITY) = ???]

{IF LOCKPICK-ROLL >= 12: PRINT ['Success! The lock clicks open.']}
{IF LOCKPICK-ROLL >= 12: ITEM [treasure]}
{IF LOCKPICK-ROLL >= 12: XP [+60]}
{IF LOCKPICK-ROLL >= 12: FLAG [picked_lock]}

IF [$LOCKPICK-ROLL < 12]
  PRINT [Failed! The lock holds firm.]
  PRINT [You broke your lockpick.]
  HP [-5]
ENDIF
END

LABEL [BRANCH-FORCE]
PRINT [You smash the chest open!]
ITEM [treasure]
PRINT [But you damaged the contents...]
XP [+20]
END

LABEL [BRANCH-LEAVE]
PRINT ['You leave the chest unopened.']
XP [+5]
END
```

---

## Best Practices

### 1. Structure Your Adventure

```python
# Good: Clear sections
# ==========================================
# INITIALIZATION
# ==========================================
SET (SPRITE-HP|100)

# ==========================================
# CHAPTER 1
# ==========================================
LABEL [CHAPTER-1]
PRINT ['Story begins...']

# ==========================================
# ENDINGS
# ==========================================
LABEL [ENDING]
```

### 2. Use Meaningful Names

```python
# Good
LABEL [FOREST-ENCOUNTER]
FLAG [met_village_elder]
BRANCH [FINAL-BATTLE]

# Bad
LABEL [TEMP1]
FLAG [f1]
BRANCH [X]
```

### 3. Test All Paths

```python
# Ensure all branches lead somewhere
CHOICE [Direction?]
  OPTION [North] → BRANCH-NORTH  # Must exist
  OPTION [South] → BRANCH-SOUTH  # Must exist
  OPTION [East] → BRANCH-EAST    # Must exist
```

### 4. Balance Difficulty

```python
# Too easy: Everything succeeds
{IF ROLL >= 2: ...}  # 95% success rate

# Balanced: Challenging but fair
{IF ROLL >= 12: ...}  # 45% success rate

# Too hard: Almost always fails
{IF ROLL >= 19: ...}  # 10% success rate
```

### 5. Provide Feedback

```python
# Good: Player knows what happened
ROLL [1d20] → ATTACK
PRINT [🎲 Attack roll: $ATTACK]
{IF ATTACK >= 15: PRINT ['Critical hit! 20 damage!']}
{IF ATTACK >= 15: HP [-20]}

# Bad: Silent result
ROLL [1d20] → ATTACK
{IF ATTACK >= 15: HP [-20]}
```

### 6. Award Progress

```python
# Reward exploration
FLAG [explored_cave]
XP [+25]

# Reward problem solving
FLAG [solved_puzzle]
XP [+50]

# Reward completion
FLAG [quest_complete]
XP [+100]
```

### 7. Use Comments

```python
# Good: Explain complex logic
# Check if player found all 3 keys
# before allowing entry to vault
{IF KEY-COUNT >= 3: BRANCH [VAULT-ENTRY]}
```

---

## Troubleshooting

### Common Errors

#### 1. Label Not Found
```
⚠️  Label not found: MISSING-LABEL
```
**Fix:** Ensure label is defined with `LABEL [MISSING-LABEL]`

#### 2. Invalid Variable
```
Error: Variable 'INVALID VAR' contains spaces
```
**Fix:** Use UPPERCASE-HYPHEN format: `$INVALID-VAR`

#### 3. Dice Roll Error
```
ValueError: invalid literal for int()
```
**Fix:** Check dice notation: `1d20` not `1d20]` or `d20`

#### 4. IF Statement Never Ends
```
Error: IF without ENDIF
```
**Fix:** Every `IF` needs an `ENDIF`

#### 5. Infinite Loop
**Problem:** Adventure never ends
**Fix:** Ensure all paths lead to `END` or death

### Debugging Tips

#### Check Variable Values
```python
# Print variables for debugging
PRINT ['DEBUG: HP=$SPRITE-HP, XP=$SPRITE-XP']
PRINT ['DEBUG: ROLL=$ROLL-RESULT']
```

#### Test Specific Branches
```python
# Skip to specific section for testing
BRANCH [SECTION-TO-TEST]
```

#### Verify Flags
```python
# Check if flags are set
PRINT [FLAGS: $STORY-FLAGS]
```

#### Trace Execution
```python
# Add markers to see execution path
PRINT ['>>> Entering combat section']
PRINT ['>>> Combat complete']
```

---

## Advanced Techniques

### State Machine Pattern

```python
SET (GAME-STATE|'exploring')

LABEL [MAIN-LOOP]

{IF GAME-STATE == 'exploring': BRANCH [STATE-EXPLORING]}
{IF GAME-STATE == 'combat': BRANCH [STATE-COMBAT]}
{IF GAME-STATE == 'dialogue': BRANCH [STATE-DIALOGUE]}

END

LABEL [STATE-EXPLORING]
PRINT ['You explore the area...']
SET (GAME-STATE|'combat')
BRANCH [MAIN-LOOP]

LABEL [STATE-COMBAT]
PRINT ['A battle begins!']
SET (GAME-STATE|'exploring')
BRANCH [MAIN-LOOP]
```

### Random Events

```python
ROLL [1d100] → RANDOM-EVENT

{IF RANDOM-EVENT <= 20: PRINT ['A merchant appears!']}
{IF RANDOM-EVENT <= 20: BRANCH [EVENT-MERCHANT]}

{IF RANDOM-EVENT <= 40: PRINT ['You find a trap!']}
{IF RANDOM-EVENT <= 40: HP [-10]}

PRINT ['Nothing happens.']
```

### Inventory Checks (Future)

```python
# Check if item in inventory (future feature)
# IF [has-item sword]
#   PRINT [You draw your sword...]
# ENDIF
```

---

## See Also

- [Variable System](Variable-System.md) - Complete variable reference
- [Command Reference](Command-Reference.md) - All uDOS commands
- [Getting Started](Getting-Started.md) - Basic uDOS usage
- [Developers Guide](Developers-Guide.md) - Extension development

---

**Version:** v1.1.9 Round 2
**Last Updated:** November 2025
**Status:** Active Development
