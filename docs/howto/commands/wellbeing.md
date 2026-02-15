# WELLBEING - Holistic User Wellness

> [!WARNING]
> Archived legacy page (v1.1-era feature doc). Keep for historical design reference only.
> Check `/Users/fredbook/Code/uDOS/docs/howto/UCODE-COMMAND-REFERENCE.md` for canonical current command surface.

**Version:** 2.0.0 (Alpha v1.1.0.0)  
**Handler:** `core/commands/wellbeing_handler.py`  
**Service:** `core/services/wellbeing_service.py`

---

## Philosophy

> **Conservation over performance**  
> **Mindfulness over productivity**  
> **Balance over optimization**  
> **Variety for wellness**

uDOS seeks to always conserve energy and resources, providing variety of tasks that self-serve the user's wellness. Rest is more important than high energy/pressure situations.

---

## Commands

### Basic Commands

```bash
WELLBEING                  # Show holistic status
WELLBEING STATUS           # Current state summary
WELLBEING SETUP            # Initial preferences questionnaire
WELLBEING CHECK            # Quick check-in prompt
WELLBEING RESET            # Reset all tracking data
```

### Energy (User Enthusiasm)

```bash
WELLBEING ENERGY low       # Set energy level (affects task suggestions)
WELLBEING ENERGY medium    # ...
WELLBEING ENERGY high      # ...
WELLBEING low              # Shorthand
```

Energy represents **user enthusiasm** - your reported energy level. This is combined with system load and workflow load to calculate the **task execution pace**.

| Level | Emoji | Session Length | Best For |
|-------|-------|----------------|----------|
| Low | 😴 | 20 min | Light review, organizing |
| Medium | 😊 | 35 min | Steady progress, learning |
| High | ⚡ | 50 min | Complex tasks, deep work |

### Mood (1-5 Scale)

```bash
WELLBEING MOOD 1           # 😢 Struggling
WELLBEING MOOD 2           # 😔 Low
WELLBEING MOOD 3           # 😐 Neutral
WELLBEING MOOD 4           # 😊 Good
WELLBEING MOOD 5           # 😄 Excellent
WELLBEING 3                # Shorthand
```

Mood is influenced by:
- 🌙 **Moon phase** - Current lunar cycle
- ☀️ **Zodiac sign** - Your star sign compatibility with the day
- 🕐 **Time of day** - Morning boost, afternoon dip
- 🌤️ **Weather** (future) - Home Assistant integration
- 📡 **Sensors** (future) - Environmental data

### Mind State (Mindfulness)

```bash
WELLBEING MIND             # Show current mind state
WELLBEING MIND focused     # 🎯 Deep concentration mode
WELLBEING MIND flowing     # 🌊 Creative, open state
WELLBEING MIND steady      # ⚖️ Balanced, stable
WELLBEING MIND wandering   # 🦋 Mind drifting, needs grounding
WELLBEING MIND scattered   # 💫 Fragmented attention
WELLBEING MIND resting     # 🌙 Recovery mode
WELLBEING MIND drifting    # ☁️ Mindfulness prompt needed
```

The `$MIND` variable encourages mindfulness, breaks, and rest. Setting lower mind states triggers gentle suggestions for grounding exercises.

### Celestial Influences

```bash
WELLBEING CELESTIAL        # Show all astrological influences
WELLBEING CELESTIAL sign   # Your zodiac sign details
WELLBEING CELESTIAL moon   # Current moon phase
```

The celestial system aligns with:
- User's star sign (from `$BIRTH_DATE` in profile)
- Current moon phase (calculated automatically)
- Future: planetary hours for task timing

### RUOK? - Mutual Wellbeing Check

```bash
WELLBEING RUOK             # System checks on YOU
RUOK                       # Alias (standalone command)
RUOK?                      # Alias (standalone command)
WELLBEING RUOK SYS         # YOU check on the SYSTEM
```

**RUOK?** inverts the traditional "OK FIX/ASSIST" pattern:
- The system proactively asks if you're okay
- Analyzes current mood, energy, mind state, session length
- Offers pathways and commands to support wellness
- Mutual: user can also check on system health

### Breaks & Suggestions

```bash
WELLBEING BREAK            # Log a break, get refreshment tips
WELLBEING SUGGEST          # Get task suggestions based on state
WELLBEING HISTORY          # View recent wellbeing logs
```

---

## Energy Balance System

Energy is calculated from three sources:

```
┌─────────────────────────────────────────────────────┐
│                  ENERGY BALANCE                     │
├─────────────────────────────────────────────────────┤
│  User Enthusiasm (0-100%)    ████████░░░░  75%     │
│  System Load                 ██░░░░░░░░░░  20%     │
│  Workflow Load               ████░░░░░░░░  35%     │
├─────────────────────────────────────────────────────┤
│  Calculated Pace             🏃 Active (65%)        │
│  "Good pace - balanced workload"                    │
└─────────────────────────────────────────────────────┘
```

**Pace affects:**
- Task complexity suggestions
- Session length recommendations
- Break reminder frequency
- UI animation speed (future)
- Message tone

---

## Configuration Variables

Set these in your profile (`PROFILE EDIT`):

```markdown
## Wellbeing

$BIRTH_DATE = "1990-03-15"  # For zodiac sign calculation
$WELLBEING_REMINDERS = "on"  # Break reminders
$WELLBEING_HISTORY = "30"    # Days to keep history
```

---

## Example Session

```bash
# Start of day
WELLBEING CHECK              # How are you feeling?
WELLBEING ENERGY medium      # Decent energy today
WELLBEING MOOD 4             # Feeling good

# Check celestial influences
WELLBEING CELESTIAL
# Shows: ♋ Cancer (water), 🌓 First Quarter Moon, +10% mood

# Set focus mode
WELLBEING MIND focused       # Deep work mode

# After 90 minutes...
RUOK                         # System checks on you
# "Long session detected, break recommended"

WELLBEING BREAK              # Take a break

# Afternoon slump
WELLBEING MIND wandering     # Acknowledge drifting
# Suggestions for grounding exercises

WELLBEING SUGGEST            # What should I work on?
# Tailored suggestions based on current state
```

---

## Logging Tags

All wellbeing operations use the `[LOCAL]` tag:

```
[LOCAL] Energy logged: medium
[LOCAL] Mood logged: 4
[LOCAL] Mind state set: focused
[LOCAL] RUOK user check: 85%
[LOCAL] Break logged
```

---

## Future Integrations

- **Home Assistant:** Weather and sensor influences
- **Map Layers:** Celestial positioning from star layers
- **Task System:** Auto-adjust task priorities based on state
- **UI Theming:** Mood affects color palette and animations

---

*Last Updated: 2026-01-07*
