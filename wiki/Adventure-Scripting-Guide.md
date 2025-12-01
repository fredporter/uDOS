# Adventure Scripting Guide (.upy Format)

Complete guide to creating interactive adventures using the `.upy` (uDOS Python-like) format.

## Table of Contents
- [Quick Start](#quick-start)
- [File Format](#file-format)
- [Command Reference](#command-reference)
- [Event Types](#event-types)
- [Choice System](#choice-system)
- [Labels & Branching](#labels--branching)
- [Game Integration](#game-integration)
- [Best Practices](#best-practices)
- [Example Adventures](#example-adventures)

---

## Quick Start

### Minimal Adventure

```python
# metadata.name: "My First Adventure"
# metadata.description: "A simple test adventure"

# Event 1: Start
NARRATIVE
You wake up in a strange place.
END

# Event 2: First choice
CHOICE
What do you do?
1. Look around
2. Call for help
END
```

### Running Adventures

```bash
# In uDOS
STORY START my-adventure
STORY CONTINUE
STORY CHOICE 1
STORY STATUS
STORY SAVE progress
STORY LOAD progress
```

---

## File Format

### File Structure

```python
# ========================================
# METADATA (Optional but recommended)
# ========================================
# metadata.name: "Adventure Title"
# metadata.description: "Brief description"
# metadata.author: "Your Name"
# metadata.version: "1.0.0"
# metadata.difficulty: "beginner"

# ========================================
# LABELS (Optional - for branching)
# ========================================
@start
@cave_entrance
@forest_path
@victory

# ========================================
# EVENTS
# ========================================
# Event 1: Opening
NARRATIVE
Event text here
END

# Event 2: First choice
CHOICE
Question?
1. Option A
2. Option B
END
```

### Metadata Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | string | Adventure title | "First Steps" |
| `description` | string | Brief summary | "Learn the basics" |
| `author` | string | Creator name | "uDOS Team" |
| `version` | string | Version number | "1.0.0" |
| `difficulty` | string | beginner/intermediate/advanced | "beginner" |

---

## Command Reference

### 15 Command Types

| Command | Purpose | Syntax |
|---------|---------|--------|
| `NARRATIVE` | Story text | `NARRATIVE\ntext\nEND` |
| `CHOICE` | Player decision | `CHOICE\nquestion\n1. opt\nEND` |
| `GOTO` | Jump to label | `GOTO @label` |
| `SET_STAT` | Modify stat | `SET_STAT health 90` |
| `AWARD_XP` | Give experience | `AWARD_XP survival 50 "reason"` |
| `ADD_ITEM` | Give item | `ADD_ITEM "Rope" TOOL 1 0.5` |
| `REMOVE_ITEM` | Take item | `REMOVE_ITEM "Rope" 1` |
| `CHECK_STAT` | Conditional | `CHECK_STAT health > 50` |
| `CHECK_ITEM` | Item check | `CHECK_ITEM "Rope"` |
| `CHECK_XP` | XP check | `CHECK_XP > 100` |
| `SPRITE` | Show stats UI | `SPRITE` |
| `OBJECT` | Show inventory | `OBJECT` |
| `VARIABLE` | Set var | `VARIABLE x 10` |
| `CONDITION` | If statement | `CONDITION x > 5` |
| `SCRIPT` | Run code | `SCRIPT\ncode\nEND` |

---

## Event Types

### 1. NARRATIVE - Story Text

```python
NARRATIVE
You enter the dark cave. Water drips from stalactites above.
The air is cold and damp.
END
```

**Features:**
- Multi-line text
- Automatic wrapping
- Markdown support (planned)

### 2. CHOICE - Player Decisions

```python
CHOICE
You see two paths ahead. Which way?
1. Take the left path (steep climb)
2. Take the right path (through water)
3. Turn back
END
```

**Features:**
- 2-9 options supported
- Automatic branching
- Validation built-in

**Next Events After Choice:**
- Option 1 → Event N+1
- Option 2 → Event N+2
- Option 3 → Event N+3

### 3. GOTO - Jump to Label

```python
GOTO @cave_entrance
```

**Usage:**
```python
# Event 10
CHOICE
Enter the cave?
1. Yes
2. No
END

# Event 11: Yes path
GOTO @cave_entrance

# Event 12: No path
GOTO @forest_path
```

### 4. SET_STAT - Modify Survival Stats

```python
# Reduce health
SET_STAT health 80

# Increase thirst
SET_STAT thirst 30

# Full heal
SET_STAT health 100
```

**Available Stats:**
- `health` (0-100)
- `thirst` (0-100, higher = thirstier)
- `hunger` (0-100, higher = hungrier)
- `fatigue` (0-100, higher = more tired)

### 5. AWARD_XP - Give Experience

```python
# Basic award
AWARD_XP survival 50 "Found water source"

# Different categories
AWARD_XP shelter 100 "Built first shelter"
AWARD_XP fire 75 "Started fire with friction"
AWARD_XP navigation 25 "Found compass"
```

**XP Categories:**
- `survival` - General survival skills
- `shelter` - Shelter building
- `fire` - Fire making
- `water` - Water purification
- `food` - Foraging/hunting
- `navigation` - Navigation
- `medical` - First aid
- `tools` - Tool crafting
- `information` - Knowledge gained

### 6. ADD_ITEM - Give Items

```python
# Basic item
ADD_ITEM "Water Bottle" CONTAINER 1 0.5

# Multiple items
ADD_ITEM "Rope" TOOL 3 1.5
ADD_ITEM "Compass" NAVIGATION 1 0.2
```

**Item Categories:**
- `TOOL` - Tools and equipment
- `FOOD` - Food items
- `WATER` - Water sources
- `MEDICAL` - Medical supplies
- `CONTAINER` - Storage items
- `NAVIGATION` - Navigation aids
- `FIRE` - Fire-making items
- `SHELTER` - Shelter materials
- `CLOTHING` - Clothing items
- `MISC` - Miscellaneous

**Syntax:** `ADD_ITEM "name" CATEGORY quantity weight`

### 7. REMOVE_ITEM - Take Items

```python
# Remove one item
REMOVE_ITEM "Water Bottle" 1

# Remove all of item
REMOVE_ITEM "Rope" 999
```

### 8. CHECK_STAT - Conditional Stat Check

```python
CHECK_STAT health > 50
```

**Operators:** `>`, `<`, `>=`, `<=`, `==`, `!=`

**Usage Pattern:**
```python
# Event 15: Check if healthy enough
CHECK_STAT health > 70

# Event 16: Healthy path
NARRATIVE
You feel strong enough to climb.
END

# Event 17: Weak path
NARRATIVE
You're too weak to climb.
END
```

### 9. CHECK_ITEM - Item Possession Check

```python
CHECK_ITEM "Rope"
```

**Usage:**
```python
# Event 20: Check for rope
CHECK_ITEM "Rope"

# Event 21: Has rope
NARRATIVE
You use the rope to descend safely.
END

# Event 22: No rope
NARRATIVE
Without rope, you can't climb down.
END
```

### 10. CHECK_XP - Experience Check

```python
CHECK_XP > 500
```

**Usage:**
```python
# Event 25: Check experience
CHECK_XP > 1000

# Event 26: Experienced
NARRATIVE
Your survival training kicks in.
END

# Event 27: Inexperienced
NARRATIVE
You're not sure what to do.
END
```

### 11. SPRITE - Show Character Stats

```python
SPRITE
```

**Displays:**
```
┌─ CHARACTER ────────────┐
│ Health:  ████████░░ 80 │
│ Thirst:  ███░░░░░░░ 30 │
│ Hunger:  ██░░░░░░░░ 20 │
│ Fatigue: █████░░░░░ 50 │
│                        │
│ XP:      2,450 Total   │
│ Level:   3             │
└────────────────────────┘
```

### 12. OBJECT - Show Inventory

```python
OBJECT
```

**Displays:**
```
┌─ INVENTORY ────────────┐
│ [TOOL]                 │
│  • Knife (1) 0.3kg    │
│  • Rope (2) 3.0kg     │
│ [CONTAINER]            │
│  • Water Bottle (1)    │
│                        │
│ Total: 4 items, 3.8kg  │
└────────────────────────┘
```

### 13. VARIABLE - Set Variable

```python
# Set number
VARIABLE stream_followed 1

# Set string
VARIABLE path_taken "forest"
```

### 14. CONDITION - If Statement

```python
CONDITION stream_followed == 1
```

### 15. SCRIPT - Custom Code

```python
SCRIPT
# Custom logic here
print("Debug message")
END
```

---

## Choice System

### Basic Choice

```python
CHOICE
What's your priority?
1. Find water
2. Build shelter
3. Start fire
END
```

**Automatic Branching:**
- Choice creates 3 paths
- Events N+1, N+2, N+3 handle each option
- Use GOTO to merge paths later

### Choice with Consequences

```python
# Event 10: Decision point
CHOICE
The stream splits. Which way?
1. Follow upstream (harder climb)
2. Follow downstream (easier)
END

# Event 11: Upstream (Option 1)
NARRATIVE
You climb the steep rocks.
END
SET_STAT fatigue 80
AWARD_XP navigation 100 "Found source"

# Event 12: Downstream (Option 2)
NARRATIVE
You walk along the gentle slope.
END
SET_STAT fatigue 40
AWARD_XP navigation 50 "Explored creek"

# Event 13: Paths converge
NARRATIVE
The stream leads to a waterfall.
END
```

### Multi-Path Choice

```python
# Event 5: Three-way split
CHOICE
Three paths diverge:
1. Forest path (safe)
2. Mountain path (challenging)
3. Cave path (mysterious)
END

# Event 6: Forest (easy)
@forest_path
NARRATIVE
You walk through peaceful woods.
END
SET_STAT fatigue 10

# Event 7: Mountain (hard)
@mountain_path
CHECK_STAT health > 70

# Event 8: Mountain success
NARRATIVE
You summit the peak!
END
AWARD_XP navigation 200 "Reached summit"

# Event 9: Mountain failure
NARRATIVE
Too weak to climb.
END
GOTO @forest_path

# Event 10: Cave (mystery)
@cave_path
CHECK_ITEM "Torch"

# Event 11: Has torch
NARRATIVE
You light the way.
END
ADD_ITEM "Crystal" MISC 1 0.1

# Event 12: No torch
NARRATIVE
Too dark to explore.
END
GOTO @forest_path
```

---

## Labels & Branching

### Defining Labels

```python
# At any event position
@start
@water_found
@shelter_complete
@victory
@game_over
```

### Using GOTO

```python
# Jump to label
GOTO @water_found

# Conditional jump
CHECK_STAT health < 20
GOTO @game_over  # If health too low
```

### Common Patterns

**Convergence Pattern:**
```python
# Event 10: Choice
CHOICE
Which approach?
1. Stealth
2. Direct
END

# Event 11: Stealth path
NARRATIVE
You sneak quietly.
END
GOTO @after_approach

# Event 12: Direct path
NARRATIVE
You walk boldly forward.
END
GOTO @after_approach

# Event 13: Converge
@after_approach
NARRATIVE
You reach the clearing.
END
```

**Loop Pattern:**
```python
# Event 20: Loop start
@gather_loop
CHOICE
Continue gathering?
1. Yes, keep gathering
2. No, move on
END

# Event 21: Keep gathering
ADD_ITEM "Berries" FOOD 1 0.1
AWARD_XP food 10 "Gathered berries"
GOTO @gather_loop

# Event 22: Move on
NARRATIVE
You have enough supplies.
END
```

---

## Game Integration

### Complete Event Example

```python
# Event 1: Opening
NARRATIVE
You wake up beside a stream in unfamiliar wilderness.
The sun is high. You're thirsty and tired.
END

# Event 2: Show status
SPRITE

# Event 3: First decision
CHOICE
What's your first priority?
1. Find water source
2. Build shelter
3. Explore surroundings
END

# Event 4: Find water (Option 1)
NARRATIVE
You follow the stream upstream.
After 30 minutes, you find a clear spring.
END
SET_STAT thirst 0
ADD_ITEM "Water Bottle" CONTAINER 1 0.5
AWARD_XP water 100 "Found clean water"

# Event 5: Build shelter (Option 2)
NARRATIVE
You gather branches and build a lean-to.
It takes 2 hours. You're exhausted but protected.
END
SET_STAT fatigue 70
ADD_ITEM "Shelter" SHELTER 1 0.0
AWARD_XP shelter 150 "Built first shelter"

# Event 6: Explore (Option 3)
NARRATIVE
You explore the area and find:
- A rocky outcrop
- Dense forest
- Open meadow
END
AWARD_XP navigation 50 "Scouted area"

# Event 7: Convergence
NARRATIVE
As evening approaches, you need to make camp.
END
SPRITE
OBJECT
```

### Survival Stats Integration

```python
# Gradual stat changes
SET_STAT thirst 20   # Slightly thirsty
SET_STAT hunger 30   # Getting hungry
SET_STAT fatigue 40  # Somewhat tired

# Emergency situations
CHECK_STAT health < 30
NARRATIVE
WARNING: Your health is critical!
END

# Recovery
SET_STAT health 100
SET_STAT thirst 0
SET_STAT hunger 0
```

### XP Progression

```python
# Tutorial (small rewards)
AWARD_XP survival 25 "Completed tutorial"

# Skill accomplishment (medium rewards)
AWARD_XP fire 100 "Started fire with bow drill"

# Major achievement (large rewards)
AWARD_XP survival 500 "Survived first week"
```

### Inventory Management

```python
# Essential items
ADD_ITEM "Knife" TOOL 1 0.3
ADD_ITEM "Rope" TOOL 1 1.5
ADD_ITEM "Water Bottle" CONTAINER 1 0.5

# Consumables
ADD_ITEM "Berries" FOOD 1 0.1
ADD_ITEM "Water" WATER 1 0.5

# Equipment check
CHECK_ITEM "Knife"
NARRATIVE
You use your knife to cut branches.
END
```

---

## Best Practices

### 1. File Organization

```python
# ========================================
# METADATA
# ========================================
# metadata.name: "Clear Title"
# metadata.description: "Concise description"

# ========================================
# LABELS (Group by section)
# ========================================
# Tutorial section
@tutorial_start
@tutorial_complete

# Main quest
@quest_start
@quest_checkpoint_1
@quest_complete

# Endings
@victory
@defeat
@neutral_end

# ========================================
# EVENTS (Comment liberally)
# ========================================
# === TUTORIAL SECTION ===
# Event 1: Welcome message
NARRATIVE
Welcome to the adventure!
END
```

### 2. Choice Design

**Good Choice:**
```python
CHOICE
You find a stream. What do you do?
1. Drink immediately (risky - might be contaminated)
2. Boil water first (safe - takes time)
3. Use filter (requires item)
END
```

**Bad Choice:**
```python
CHOICE
What now?
1. Option A
2. Option B
END
```

**Why Good:**
- Context clear
- Consequences hinted
- Trade-offs obvious

### 3. Stat Balance

```python
# Gradual drain (realistic)
SET_STAT thirst 10  # +10 every hour
SET_STAT hunger 5   # +5 every 2 hours
SET_STAT fatigue 15 # +15 per activity

# Recovery (also gradual)
SET_STAT thirst 0   # Full drink
SET_STAT health 90  # First aid (not full heal)
SET_STAT fatigue 20 # Short rest (not full)
```

### 4. XP Rewards

| Action | XP Range | Example |
|--------|----------|---------|
| Tutorial | 10-50 | "Learned to filter water" |
| Basic Skill | 50-150 | "Built simple shelter" |
| Challenge | 150-300 | "Started fire without matches" |
| Achievement | 300-500 | "Survived 3 days" |

### 5. Pacing

```python
# Good pacing pattern:
# 1. Narrative (context)
# 2. Choice (decision)
# 3. Consequences (results)
# 4. Status update (SPRITE/OBJECT)
# 5. Next situation

# Example:
NARRATIVE
The storm is getting worse.
END

CHOICE
Your shelter is weak. What do you do?
1. Reinforce it (takes time)
2. Find better location
END

# Option 1 path
NARRATIVE
You gather more branches.
The shelter holds!
END
SET_STAT fatigue 60
AWARD_XP shelter 100 "Reinforced shelter"
SPRITE

NARRATIVE
The storm passes by morning.
END
```

### 6. Testing Checklist

- [ ] All paths reachable
- [ ] No dead ends (unless intentional)
- [ ] Stats balanced (not too easy/hard)
- [ ] XP rewards fair
- [ ] Items make sense
- [ ] Labels used correctly
- [ ] GOTO targets exist
- [ ] Choices have 2-9 options
- [ ] Narrative flows naturally
- [ ] Complete victory/defeat paths

---

## Example Adventures

### Minimal Tutorial (10 events)

```python
# metadata.name: "Quick Start"
# metadata.description: "5-minute tutorial"

@start
NARRATIVE
Welcome to wilderness survival!
This tutorial teaches the basics.
END

CHOICE
First priority in survival?
1. Water (Correct!)
2. Food
3. Shelter
END

# Water path (correct)
NARRATIVE
Correct! Water is top priority.
You can survive 3 days without water,
but 3 weeks without food.
END
AWARD_XP survival 50 "Learned priorities"
GOTO @shelter_lesson

# Food/Shelter paths (redirect)
NARRATIVE
Not quite. Let's learn about water first.
END
GOTO @shelter_lesson

@shelter_lesson
NARRATIVE
Now you know the survival priorities:
1. Water (3 days)
2. Shelter (protection)
3. Fire (warmth/signals)
4. Food (3 weeks)
END
SPRITE
AWARD_XP survival 100 "Completed tutorial"
```

### Medium Adventure (30 events)

See `sandbox/ucode/adventures/first-steps.upy` for complete example.

### Advanced Adventure (100+ events)

```python
# Features:
# - Multiple endings
# - Complex branching
# - Skill checks
# - Inventory puzzles
# - Dynamic difficulty
# - Achievement tracking
```

---

## Common Patterns Library

### Safe/Risky Choice

```python
CHOICE
Drink the water?
1. Drink immediately (risky)
2. Boil first (safe)
END

# Risky path
CHECK_STAT health > 80
# Success: No illness
# Failure: Get sick
SET_STAT health 50

# Safe path
SET_STAT fatigue 20
SET_STAT thirst 0
```

### Resource Management

```python
CHECK_ITEM "Rope"
NARRATIVE
You use rope to cross the gap.
END
REMOVE_ITEM "Rope" 1

# No rope
NARRATIVE
You need rope to cross.
END
GOTO @find_alternative
```

### Skill Progression

```python
CHECK_XP > 500
# Experienced
NARRATIVE
Your training pays off.
END
AWARD_XP survival 100 "Expert move"

# Novice
NARRATIVE
You struggle but learn.
END
AWARD_XP survival 25 "Learning"
```

---

## Troubleshooting

### Common Errors

**"Missing label"**
- Label used in GOTO doesn't exist
- Check spelling: `@water_source` vs `@water-source`

**"Invalid choice range"**
- Choice needs 2-9 options
- Check numbering: Must be 1, 2, 3... (not 0, 1, 2)

**"Event index out of range"**
- Choice creates paths that don't exist
- 3-option choice needs 3 events after it

**"Unknown command"**
- Command misspelled
- Check uppercase: `NARRATIVE` not `narrative`

### Debugging Tips

```python
# Add debug messages
NARRATIVE
[DEBUG] Event 25 reached
[DEBUG] Health: should be < 50
END

# Use SPRITE/OBJECT to check state
SPRITE
OBJECT

# Test paths individually
# Comment out other paths
```

---

## Next Steps

1. **Read Examples:** Study `first-steps.upy`
2. **Write Simple Adventure:** Start with 10 events
3. **Test Thoroughly:** Try all paths
4. **Expand Gradually:** Add complexity slowly
5. **Share & Iterate:** Get feedback, improve

**Related Docs:**
- [Command Reference](Command-Reference.md#story) - STORY commands
- [Getting Started](Getting-Started.md) - Basic uDOS usage
- [uCODE Language](uCODE-Language.md) - Script automation

---

**Version:** 2.0.0 (Round 2)
**Last Updated:** Dec 2024
**Maintainer:** uDOS Team
