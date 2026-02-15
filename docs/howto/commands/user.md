# User Commands

> [!WARNING]
> Archived legacy page (v1.1). User/location/wellbeing command sections here are historical and may conflict with current command contracts.
> For current canonical command names, use `/Users/fredbook/Code/uDOS/docs/howto/UCODE-COMMAND-REFERENCE.md`.

> **Version:** Core v1.1.0.0

Commands for user preferences, location, and wellbeing.

---

## WELLBEING

Holistic user wellness system with astrological mood, energy balance, and mindfulness tracking.

**Full documentation:** [WELLBEING Reference](wellbeing.md)

### Quick Reference

```bash
WELLBEING                  # Show holistic status
WELLBEING ENERGY low       # Set energy level
WELLBEING MOOD 3           # Set mood (1-5)
WELLBEING MIND focused     # Set mind state
WELLBEING CELESTIAL        # Show astrological influences
WELLBEING BREAK            # Log a break
WELLBEING SUGGEST          # Get task suggestions
RUOK                       # System checks on you
```

### Philosophy

> Conservation over performance  
> Mindfulness over productivity  
> Balance over optimization

### Key Features (v2.0.0)

| Feature | Description |
|---------|-------------|
| **Mood** | Influenced by zodiac, moon phase, time of day |
| **Energy** | Balance of user enthusiasm, system load, workflow |
| **Mind** | Mindfulness states (focused/resting/wandering) |
| **RUOK?** | Mutual wellbeing checks (system ↔ user) |

---

## LOCATION

Set your current location for map and local content features.

### Syntax

```bash
LOCATION [subcommand] [args]
```

### Subcommands

| Command | Description |
| ------- | ----------- |
| `STATUS` | Show current location |
| `SET <coords>` | Set coordinates |
| `CLEAR` | Remove location |

### Examples

```bash
# Set location
LOCATION SET 51.5074,-0.1278

# Check status
LOCATION STATUS
```

---

## PROFILE

User configuration and preferences using udos.md format.

**Full documentation:** [Configuration Guide](CONFIGURATION.md)

### Quick Reference

```bash
PROFILE                    # Show current profile
PROFILE SETUP              # Interactive setup
PROFILE EDIT               # Open profile in editor
PROFILE SET var value      # Set a variable
PROFILE GET var            # Get a variable value
PROFILE EXPORT             # Export settings
```

### Key Variables

| Variable | Description |
|----------|-------------|
| `$USER_NAME` | Display name |
| `$BIRTH_DATE` | For zodiac calculation |
| `$THEME` | UI theme preference |
| `$ENERGY` | Default energy level |

---

*See also: [WELLBEING](wellbeing.md), [CONFIGURATION](CONFIGURATION.md)*# Set energy/mood
WELLBEING ENERGY low
WELLBEING MOOD focused

# Get suggestions
WELLBEING SUGGEST

# Log break
WELLBEING BREAK

# View history
WELLBEING HISTORY

# Initial setup
WELLBEING SETUP

# Reset data
WELLBEING RESET
```

### Integration with BUNDLE

WELLBEING integrates with the BUNDLE command:

- **BUNDLE NEXT** costs wellbeing energy
- Low energy may slow down drip delivery
- High energy unlocks bonus content
- Break suggestions align with bundle pacing

### Data Storage

```
memory/private/wellbeing/
├── state.json          # Current state
├── history.json        # Historical data
└── preferences.json    # User settings
```

### Privacy

- **Local-only**: Never synced to cloud or mesh
- **Private folder**: Stored in `memory/private/`
- **No tracking**: No external analytics
- **User control**: Reset anytime with `WELLBEING RESET`

---

## LOCATION

Privacy-first location and celestial navigation.

### Syntax

```bash
LOCATION [subcommand] [args]
```

### Subcommands

| Command | Description |
| ------- | ----------- |
| `STATUS` | Show current location status (default) |
| `SET <lat> <lon>` | Set coordinates manually |
| `SKY` | View current sky (sun, moon, planets) |
| `STARS` | View visible navigation stars |
| `NAVIGATE <star>` | Navigate by specific star |
| `ALIGN` | Show Solar System aligned to sky |
| `PRIVACY <level>` | Set privacy level |
| `CONSENT` | Manage location consent |
| `CLEAR` | Clear all location data |

### Privacy Levels

| Level | Description |
| ----- | ----------- |
| `none` | Full coordinates in logs |
| `hashed` | Hashed coordinates (default) |
| `regional` | City-level only |
| `full` | No location data logged |

### Examples

```bash
# Check status
LOCATION
LOCATION STATUS

# Set location manually
LOCATION SET -33.8688 151.2093

# View sky
LOCATION SKY
LOCATION STARS

# Navigate by star
LOCATION NAVIGATE Polaris

# Privacy settings
LOCATION PRIVACY regional
LOCATION CONSENT
LOCATION CLEAR
```

### Shortcuts

```bash
SKY              # Same as LOCATION SKY
STARS            # Same as LOCATION STARS
```

### Privacy Features

- **Masked in logs**: `L300:BD14-####` format
- **Hashed by default**: Coordinates hashed before logging
- **Consent-based**: Explicit opt-in required
- **Clear anytime**: `LOCATION CLEAR` removes all data

### Celestial Navigation

- **Polaris altitude** ≈ your latitude
- **Sun position** for time and direction
- **Moon phase** for calendar
- **Star patterns** for orientation

---

## Related Commands

- [BUNDLE](content.md#bundle) - Content packages (uses wellbeing)
- [SYSTEM](system.md#system) - System preferences
- [MODE](interface.md#mode) - Interface modes

---

*Part of the [Command Reference](README.md)*
