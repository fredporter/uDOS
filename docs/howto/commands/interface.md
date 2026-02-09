# Interface Commands

> **Version:** Core v1.1.0.0

Commands for customizing the TUI appearance and interaction.

---

## COLOR

Color theme management.

### Syntax

```bash
COLOR [theme|STATUS|LIST]
```

### Available Themes

| Theme | Description |
| ----- | ----------- |
| `rainbow` | Animated rainbow splash |
| `teletext` | Classic teletext colors |
| `dark` | Dark mode |
| `light` | Light mode |
| `retro` | CRT-style green |
| `amber` | Amber monochrome |

### Examples

```bash
COLOR                 # Show current theme
COLOR rainbow         # Enable rainbow mode
COLOR teletext        # Classic teletext
COLOR dark            # Dark theme
COLOR LIST            # List available themes
COLOR STATUS          # Current color status
```

---

## PALETTE

Color palette editor and management.

### Syntax

```bash
PALETTE [LIST|SHOW <name>|SET <name>|EDIT|EXPORT|IMPORT]
```

### Examples

```bash
PALETTE               # Show current palette
PALETTE LIST          # List available palettes
PALETTE SHOW retro    # Preview palette
PALETTE SET retro     # Apply palette
PALETTE EDIT          # Open palette editor
PALETTE EXPORT my-theme.json
PALETTE IMPORT custom.json
```

### Palette Format

```json
{
  "name": "custom",
  "colors": {
    "background": "#000000",
    "foreground": "#FFFFFF",
    "primary": "#00FF00",
    "secondary": "#0000FF",
    "accent": "#FF0000",
    "error": "#FF0000",
    "warning": "#FFFF00",
    "success": "#00FF00"
  }
}
```

---

## MODE

Prompt mode switching.

### Syntax

```bash
MODE [mode_name]
```

### Available Modes

| Mode | Prompt Style | Description |
| ---- | ------------ | ----------- |
| `DEFAULT` | `> █` | Standard prompt |
| `GHOST` | `_ ` | Minimal, quiet |
| `TOMB` | `⚰ ` | Gothic style |
| `CRYPT` | `🔐 ` | Encrypted look |

### Examples

```bash
MODE                  # Show current mode
MODE GHOST            # Switch to ghost mode
MODE TOMB             # Switch to tomb mode
MODE DEFAULT          # Return to default
```

---

## SOUND

System sound effects and alerts.

### Syntax

```bash
SOUND [pattern|PLAY <mml>|STATUS|OFF|ON]
```

### Patterns

| Pattern | Trigger |
| ------- | ------- |
| `startup` | System boot |
| `success` | Command success |
| `error` | Command failure |
| `alert` | Notification |
| `receive` | Data incoming |
| `transmit` | Data sending |

### Examples

```bash
SOUND startup         # Play startup sound
SOUND success         # Play success chime
SOUND PLAY "o4 c4 e4 g4"  # Play custom MML
SOUND STATUS          # Check sound status
SOUND OFF             # Disable sounds
SOUND ON              # Enable sounds
```

---

## PROMPT

Customize the input prompt.

### Syntax

```bash
PROMPT [template]
```

### Template Variables

| Variable | Description |
| -------- | ----------- |
| `{tile}` | Current tile number |
| `{mode}` | Current mode |
| `{user}` | Username |
| `{time}` | Current time |

### Examples

```bash
PROMPT                # Show current prompt
PROMPT "> "           # Simple prompt
PROMPT "{tile}> "     # Show tile number
PROMPT "[{mode}] > "  # Show mode
```

---

## SCREEN

Screen and display settings.

### Syntax

```bash
SCREEN [CLEAR|SIZE|REFRESH]
```

### Examples

```bash
SCREEN CLEAR          # Clear screen
SCREEN SIZE           # Show dimensions
SCREEN REFRESH        # Force redraw
```

---

## Related

- [TUI Guide](../tui/README.md) - Full TUI documentation
- [Groovebox](../groovebox/README.md) - Sound system
- [System Commands](system.md) - Configuration

---

*Part of the [Command Reference](README.md)*
