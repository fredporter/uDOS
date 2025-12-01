# .upy Adventure Script Format
## Round 2: STORY Command Extension

### Overview

The `.upy` adventure format is a human-readable scripting language for creating interactive narrative adventures in uDOS. It extends the uPY language with adventure-specific keywords for branching narratives, skill checks, choices, and gameplay integration.

### Core Keywords

#### 1. CHOICE - Present options to the player

```upy
CHOICE [Question text?]
  OPTION [Choice 1 text] → LABEL-NAME-1
  OPTION [Choice 2 text] → LABEL-NAME-2
  OPTION [Choice 3 text] → LABEL-NAME-3
```

**Behavior:**
- Displays question and numbered options
- Waits for player to select (STORY CHOICE 1, etc.)
- Jumps to the specified LABEL when chosen

#### 2. LABEL - Define jump destinations

```upy
LABEL [START]           # Main entry point
LABEL [BRANCH-SUCCESS]  # Success path
LABEL [BRANCH-FAILURE]  # Failure path
```

**Behavior:**
- Marks a position in the script
- Used as targets for BRANCH, OPTION, and IF jumps
- Convention: Use UPPER-CASE-WITH-DASHES

#### 3. BRANCH - Unconditional jump

```upy
BRANCH [TARGET-LABEL]
```

**Behavior:**
- Jumps immediately to specified LABEL
- No conditions, always executes

#### 4. ROLL - Dice rolls for skill checks

```upy
ROLL [1d20] → $RESULT
ROLL [2d6+3] → $DAMAGE
ROLL [1d100] → $LUCK
```

**Behavior:**
- Rolls dice using standard notation (XdY+Z)
- Stores result in variable
- Common patterns:
  - 1d20 - Standard skill check (D&D style)
  - 1d100 - Percentile rolls
  - 2d6 - Bell curve results

#### 5. IF - Conditional branching

```upy
IF [$VARIABLE >= 15]
  # Code executed if true
  PRINT [Success!]
  BRANCH [SUCCESS-PATH]
ENDIF

IF [$VARIABLE < 10]
  PRINT [Failure!]
  BRANCH [FAILURE-PATH]
ENDIF
```

**Operators:** `==`, `!=`, `>`, `<`, `>=`, `<=`

#### 6. FLAG - Set story flags

```upy
FLAG [found_water]
FLAG [defeated_boss]
FLAG [made_ally]
```

**Behavior:**
- Sets a boolean flag in story state
- Check flags with: `IF [FLAG:found_water]`
- Used for tracking player achievements/progress

#### 7. XP - Award experience points

```upy
XP [+50]   # Award XP
XP [-20]   # Penalize XP (rare)
```

**Behavior:**
- Updates player XP via XPService
- Integrates with SPRITE system
- Triggers level-ups when appropriate

#### 8. HP - Modify health points

```upy
HP [-15]   # Take damage
HP [+25]   # Heal
```

**Behavior:**
- Updates player HP via SurvivalService
- Integrates with SPRITE system
- Can trigger death/game over at 0 HP

#### 9. STAMINA - Modify stamina/energy

```upy
STAMINA [-20]   # Exhaust
STAMINA [+10]   # Rest
```

#### 10. GIVE - Add items to inventory

```upy
GIVE [water_bottle]
GIVE [fire_starter]
GIVE [first_aid_kit]
```

**Behavior:**
- Adds item to player inventory
- Integrates with OBJECT system
- Item properties defined in object database

#### 11. TAKE - Remove items from inventory

```upy
TAKE [food_ration]
TAKE [rope]
```

#### 12. PRINT - Display text

```upy
PRINT []   # Blank line
PRINT [You find a stream flowing through the rocks.]
PRINT [The water looks clear and cold.]
```

**Behavior:**
- Displays narrative text
- Supports emoji codes: `:heart:`, `:fire:`, `:water_drop:`

#### 13. SET - Variable assignment

```upy
SET [$SPRITE-NAME = "Wanderer"]
SET [$SPRITE-HP = 100]
SET [$COUNTER = 0]
```

### Story Structure

#### Typical Adventure Structure

```upy
#!/usr/bin/env python3
# Adventure Title
# Description

# ====================================
# INITIALIZATION
# ====================================

SET [$SPRITE-NAME = "Survivor"]
SET [$SPRITE-HP = 100]
SET [$SPRITE-HP-MAX = 100]
SET [$SPRITE-LEVEL = 1]
SET [$SPRITE-XP = 0]

SET [$STORY-CURRENT = "adventure_name"]
SET [$STORY-CHAPTER = 1]
SET [$STORY-FLAGS = []]

# ====================================
# INTRODUCTION
# ====================================

PRINT []
PRINT [==========================================]
PRINT [  ADVENTURE TITLE]
PRINT [==========================================]
PRINT []
PRINT [Opening narrative text...]
PRINT []

XP [+5]   # Award XP for starting

# ====================================
# MAIN STORY
# ====================================

LABEL [START]

CHOICE [What do you do?]
  OPTION [Option 1] → BRANCH-PATH-1
  OPTION [Option 2] → BRANCH-PATH-2
  OPTION [Option 3] → BRANCH-PATH-3

# ====================================
# PATH 1
# ====================================

LABEL [BRANCH-PATH-1]

PRINT [Path 1 narrative...]

ROLL [1d20] → $SKILL_CHECK

IF [$SKILL_CHECK >= 15]
  PRINT [Success!]
  XP [+50]
  FLAG [path1_success]
  BRANCH [CONVERGENCE]
ENDIF

IF [$SKILL_CHECK >= 10]
  PRINT [Partial success...]
  HP [-10]
  XP [+25]
  BRANCH [CONVERGENCE]
ENDIF

PRINT [Failure...]
HP [-25]
XP [+10]
BRANCH [CONVERGENCE]

# ====================================
# CONVERGENCE POINT
# ====================================

LABEL [CONVERGENCE]

PRINT [Paths converge here...]

# Check flags for different outcomes
IF [FLAG:path1_success]
  PRINT [You succeeded on path 1!]
ENDIF

CHOICE [What next?]
  OPTION [Continue] → BRANCH-FINALE
  OPTION [Go back] → START

# ====================================
# FINALE
# ====================================

LABEL [BRANCH-FINALE]

PRINT [Final narrative...]
PRINT []
PRINT [THE END]

XP [+100]
```

### Integration with Game Systems

#### SPRITE Integration

```upy
# Character stats updated automatically
HP [-20]          # Updates $SPRITE-HP
XP [+50]          # Updates $SPRITE-XP, may trigger level-up
STAMINA [-15]     # Updates $SPRITE-STAMINA
```

#### OBJECT Integration

```upy
# Inventory management
GIVE [torch]           # Adds to player inventory
GIVE [rope_50ft]       # Items have properties (length, etc.)

# Check inventory
IF [HAS:torch]
  PRINT [You light your torch...]
  BRANCH [LIT-PATH]
ENDIF
```

#### Survival Stats

```upy
# Track hunger/thirst/health
HUNGER [+10]    # Get hungrier
THIRST [+15]    # Get thirstier
HEALTH [-5]     # Take damage (different from HP)
```

### Best Practices

#### 1. Naming Conventions

- **LABELS**: `UPPER-CASE-WITH-DASHES`
  - Examples: `START`, `BRANCH-SUCCESS`, `FINALE`

- **Flags**: `lowercase_with_underscores`
  - Examples: `found_water`, `defeated_boss`, `made_ally`

- **Variables**: `$UPPER-CASE` or `$lowercase`
  - Examples: `$SPRITE-HP`, `$roll_result`, `$COUNTER`

#### 2. Skill Check Patterns

```upy
# Standard D20 skill check (D&D-style)
ROLL [1d20] → $CHECK

IF [$CHECK >= 18]
  PRINT [Critical success!]
  XP [+100]
  BRANCH [CRITICAL-PATH]
ENDIF

IF [$CHECK >= 12]
  PRINT [Success!]
  XP [+50]
  BRANCH [SUCCESS-PATH]
ENDIF

IF [$CHECK >= 6]
  PRINT [Partial success]
  XP [+25]
  HP [-10]
  BRANCH [PARTIAL-PATH]
ENDIF

PRINT [Failure...]
HP [-25]
XP [+10]
BRANCH [FAILURE-PATH]
```

#### 3. Branching Patterns

```upy
# Diamond pattern (converge after branches)
CHOICE [Choose:]
  OPTION [Path A] → BRANCH-A
  OPTION [Path B] → BRANCH-B

LABEL [BRANCH-A]
# ... path A content ...
BRANCH [CONVERGENCE]

LABEL [BRANCH-B]
# ... path B content ...
BRANCH [CONVERGENCE]

LABEL [CONVERGENCE]
# Paths merge here
```

#### 4. Loop Prevention

```upy
# Use counters to prevent infinite loops
SET [$LOOP-COUNT = 0]

LABEL [LOOP-START]

SET [$LOOP-COUNT = $LOOP-COUNT + 1]

IF [$LOOP-COUNT > 3]
  PRINT [You've tried enough times...]
  BRANCH [LOOP-END]
ENDIF

# ... loop content ...

BRANCH [LOOP-START]

LABEL [LOOP-END]
```

### File Format

**Extension:** `.upy`
**Encoding:** UTF-8
**Shebang:** `#!/usr/bin/env python3` (optional, for editor syntax highlighting)

### Comments

```upy
# Single-line comment

# Multi-line explanation:
# Line 1
# Line 2
# Line 3
```

### Example: Complete Mini-Adventure

```upy
#!/usr/bin/env python3
# Lost in the Woods - Tutorial Adventure

SET [$SPRITE-NAME = "Wanderer"]
SET [$SPRITE-HP = 100]
SET [$SPRITE-XP = 0]

PRINT [==========================================]
PRINT [  LOST IN THE WOODS]
PRINT [==========================================]
PRINT []
PRINT [You wake up disoriented in a dense forest.]
PRINT [Your last memory is the sound of thunder...]
PRINT []

XP [+5]

LABEL [START]

CHOICE [What do you do first?]
  OPTION [Look for water] → BRANCH-WATER
  OPTION [Build shelter] → BRANCH-SHELTER
  OPTION [Start a fire] → BRANCH-FIRE

LABEL [BRANCH-WATER]

PRINT []
PRINT [You search for signs of water...]

ROLL [1d20] → $SEARCH

IF [$SEARCH >= 12]
  PRINT [🎲 Search: $SEARCH - You find a stream!]
  XP [+50]
  GIVE [water_bottle]
  FLAG [found_water]
  BRANCH [SURVIVAL-CHECK]
ENDIF

PRINT [🎲 Search: $SEARCH - No water found...]
HP [-10]
XP [+10]
BRANCH [SURVIVAL-CHECK]

LABEL [BRANCH-SHELTER]

PRINT []
PRINT [You gather branches and leaves...]
PRINT [A basic lean-to takes shape.]
XP [+40]
FLAG [built_shelter]
BRANCH [SURVIVAL-CHECK]

LABEL [BRANCH-FIRE]

PRINT []
PRINT [You attempt to start a fire...]

ROLL [1d20] → $FIRE

IF [$FIRE >= 14]
  PRINT [🎲 Fire: $FIRE - Success! Warmth and light.]
  XP [+60]
  FLAG [made_fire]
  BRANCH [SURVIVAL-CHECK]
ENDIF

PRINT [🎲 Fire: $FIRE - The fire won't catch...]
HP [-5]
XP [+20]
BRANCH [SURVIVAL-CHECK]

LABEL [SURVIVAL-CHECK]

PRINT []
PRINT [As night falls, you assess your situation...]

IF [FLAG:found_water AND FLAG:built_shelter AND FLAG:made_fire]
  PRINT [You've secured water, shelter, and fire!]
  PRINT [You'll survive the night comfortably.]
  XP [+200]
  PRINT []
  PRINT [✅ SURVIVAL MASTERY ACHIEVED]
ENDIF

IF [FLAG:found_water OR FLAG:built_shelter OR FLAG:made_fire]
  PRINT [You've made progress, but survival is uncertain...]
  XP [+100]
  PRINT []
  PRINT [⚠️  SURVIVAL UNCERTAIN]
ENDIF

PRINT [You've only begun to understand the wilderness...]
XP [+50]

PRINT []
PRINT [THE END]
```

### Parser Implementation Notes

The `.upy` parser should:

1. **Tokenize** - Split into commands and parameters
2. **Validate** - Check syntax and label references
3. **Convert** - Transform to ScenarioEngine event format
4. **Execute** - Run through ScenarioEngine

See: `core/services/game/upy_adventure_parser.py` (to be implemented)

### Related Systems

- **ScenarioEngine**: Executes converted events
- **SPRITE**: Character stats integration
- **OBJECT**: Inventory integration
- **XPService**: Experience/leveling
- **SurvivalService**: Hunger/thirst/health

### Future Enhancements

1. **REQUIRE** - Prerequisite checks (level, items, flags)
2. **RANDOM** - Random events/encounters
3. **TIMER** - Time-based challenges
4. **COMPANION** - NPC allies/followers
5. **MERCHANT** - Trading/bartering
6. **COMBAT** - Turn-based combat system

---

*Version: 1.0 | Last Updated: 2025-12-02 | Round 2 STORY Command*
