# TUI GENRE Architecture — v1.4.4

**Status:** Architecture Specification
**Target:** Terminal UI theming system separate from Web GUI themes
**Version:** v1.4.4

---

## Overview

**GENRE** is uDOS's theming system for TUI (Terminal User Interface) styling. GENREs define:
- Color palettes (for ANSI output)
- Error/warning/success message formats
- ASCII art and border styles
- Typography conventions (bold, italic, underline)
- Logging output styles

This is **separate and distinct** from Wizard's web GUI themes (HTML/CSS in `wizard/web/themes/`).

### Design Goals

1. **Separation of Concerns** — TUI styling independent from web GUI
2. **Modularity** — Each GENRE is self-contained, easy to add/remove
3. **Consistency** — All error/system messages follow GENRE conventions
4. **Accessibility** — High-contrast genres for readability; colorblind-safe defaults
5. **Extensibility** — Users can create custom GENREs without core modifications

---

## GENRE Categories

### 1. Retro (Classic Computing)

**Vibe:** C64, Teletext, vintage terminals
**Palette:** Limited colors (16), monospace thick borders, pixel art

```yaml
name: retro
definition: |
  Colors: 16 VGA palette (black, red, green, yellow, blue, magenta, cyan, white × 2 brightness)
  Borders: ═══╔╗║╚╝ (box drawing)
  Text: ALL CAPS for headings, [BRACKETS] for commands
  Error: ▓▒░ ERROR ░▒▓ with red background
  Example:
    ╔════════════════════╗
    ║  WELCOME TO uDOS   ║
    ║  v1.4.4 RETRO      ║
    ╚════════════════════╝
```

**Use Cases:** Nostalgia, vintage aesthetic, performance-limited systems

### 2. Neon (Cyberpunk)

**Vibe:** Glowing lines, high contrast, 1980s hacker aesthetic
**Palette:** Bright neon colors (cyan, magenta, lime on black)

```yaml
name: neon
definition: |
  Colors: 256-color mode, high saturation, glow effects via bright white
  Borders: ╔════╗ with neon colors (bright cyan or magenta)
  Text: Lowercase with » and « brackets, monospace
  Error: ▀▄ ERROR ▄▀ with bright red and flashing (if terminal supports)
  Example:
    ╔════════════════════╗
    ║ » welcome to udos «║
    ║   v1.4.4 neon      ║
    ╚════════════════════╝
```

**Use Cases:** Modern terminals, attention-grabbing, gaming flavor

### 3. Minimal (Zen)

**Vibe:** Clean, simple, distraction-free
**Palette:** Grayscale (blacks/grays/whites), minimal color

```yaml
name: minimal
definition: |
  Colors: Mostly white/gray on black, rare accent color (blue)
  Borders: ─ and │ (thin lines), minimal enclosure
  Text: Regular case, clear typography, whitespace emphasis
  Error: ERROR: message in bold white, no decoration
  Example:
    welcome to udos
    v1.4.4 minimal

    Ready for input.
```

**Use Cases:** Focus/productivity, accessibility, low-bandwidth terminals

### 4. Dungeon (Fantasy/Roguelike)

**Vibe:** Fantasy game aesthetic (nethack, classic roguelike)
**Palette:** Earth tones, muted colors, dungeon-like

```yaml
name: dungeon
definition: |
  Colors: Brown, olive, rust, shadow (256-color mode)
  Borders: #+# (roguelike style), ASCII art walls
  Text: Serif-like effect via Unicode (𝒯𝒪𝓁𝓊𝒮), lowercase
  Error: → ERROR ← with brown background (torch-lit effect)
  Example:
    #+#+++#+#+#
    #          #
    # welcome to udos
    #  v1.4.4 dungeon
    #          #
    #+#+++#+#+#
```

**Use Cases:** Games, fantasy worldbuilding, roguelike players

---

## GENRE Definition Format

### File Structure

```
/themes/genre/
├── retro/
│   ├── genre.yaml        # GENRE definition
│   ├── palette.txt       # Color codes and meanings
│   ├── error_template.txt
│   ├── warning_template.txt
│   ├── success_template.txt
│   ├── borders.txt       # Box drawing chars
│   └── demo.txt          # Example rendering
├── neon/
│   ├── (same structure)
├── minimal/
│   ├── (same structure)
└── dungeon/
    ├── (same structure)
```

### Genre Definition Schema

```yaml
# themes/genre/retro/genre.yaml

metadata:
  name: "retro"
  display_name: "Retro (C64)"
  description: "Vintage computing aesthetic"
  version: "1.0.0"
  author: "uDOS Team"
  colorblind_safe: true

colors:
  # ANSI color codes (0-255 or named)
  primary:
    text: "white"          # \033[37m
    background: "black"    # \033[40m

  accent:
    success: "green"       # \033[32m
    warning: "yellow"      # \033[33m
    error: "red"           # \033[31m
    info: "cyan"           # \033[36m

  status_bar:
    background: "blue"
    text: "white"

borders:
  # Box drawing characters
  top_left: "╔"
  top_right: "╗"
  bottom_left: "╚"
  bottom_right: "╝"
  horizontal: "═"
  vertical: "║"
  corner_l: "╠"
  corner_r: "╣"
  corner_u: "╦"
  corner_d: "╩"
  cross: "╬"

text_styles:
  heading:
    prefix: "["
    suffix: "]"
    case: upper      # upper, lower, title, mixed
    bold: true
    color: accent.primary

  command:
    prefix: ">"
    suffix: ""
    color: accent.info
    bold: false

  error_section:
    prefix: "▓▒░ "
    suffix: " ░▒▓"
    color: accent.error
    background: "red"

messages:
  error_template: |
    {border_top}
    ▓▒░ ERROR ░▒▓
    {message}
    {recovery_hint}
    {border_bottom}

  warning_template: |
    ⚠ WARNING: {message}

  success_template: |
    ✓ {message}

compatibility:
  min_color_depth: "16"  # "16", "256", "24bit"
  unicode_required: false
  ansi_codes: true
```

---

## Integration Points

### 1. Core Configuration

```python
# core/config/config.json
{
  "display": {
    "tui_genre": "retro",      # Currently active GENRE
    "genre_path": "themes/genre/"
  }
}
```

### 2. Logging & Error Output

```python
# core/services/logging_manager.py
from core.services.tui_genre_manager import get_genre

logger = get_logger(__name__)

def log_error(message: str, recovery_hint: str = ""):
    genre = get_genre()  # Load current GENRE
    formatted = genre.format_error(message, recovery_hint)
    print(formatted)  # ANSI-formatted output
    logger.error(message)  # Plaintext to file
```

### 3. TUI Widget Rendering

```python
# core/tui/widgets.py
from core.services.tui_genre_manager import get_genre

class Box:
    def render(self):
        genre = get_genre()
        borders = genre.get_borders()
        # Use genre.colors and genre.borders for rendering
        ...
```

### 4. Display Showcase (Educational)

```bash
# Render the same widget in all GENREs
bin/display-showcase --by-genre

# Output:
# === RETRO GENRE ===
# ╔════════╗
# ║ Hello! ║
# ╚════════╝
#
# === NEON GENRE ===
# ╔════════╗
# ║ Hello! ║
# ╚════════╝
# (colors adjusted)
#
# === MINIMAL GENRE ===
# hello!
```

---

## Error Message Formatting

### Before (Plaintext, uDOS v1.4.3)

```
ERROR: Workspace not found @ vault
HINT: Run PLACE --list to see available workspaces
```

### After (GENRE-aware, v1.4.4)

#### Retro GENRE
```
▓▒░ ERROR ░▒▓
Workspace not found @ vault

HINT: Run PLACE --list to see available workspaces
```
(Red background, white text, all caps sections)

#### Neon GENRE
```
▀▄ ERROR ▄▀
» workspace not found @ vault «

⚙ hint: run PLACE --list to see available workspaces
```
(Bright red/cyan, flashing if supported)

#### Minimal GENRE
```
ERROR: Workspace not found @ vault

Hint: Run PLACE --list to see available workspaces
```
(White on black, minimal decoration)

---

## System Message Outputs

### Success Messages

```python
# Retro
✓ Workspace switched to @dev

# Neon
» switched to @dev «

# Minimal
Switched to @dev
```

### Warning Messages

```python
# Retro
⚠ WARNING: Cache may be stale (5+ minutes old)

# Neon
!!! cache may be stale (5+ minutes old) !!!

# Minimal
Warning: Cache may be stale (5+ minutes old)
```

### Status Bar (Persistent)

```python
# Retro
╔════════════════════════════════════╗
║ uDOS v1.4.4 | @vault | 42 docs   ║
╚════════════════════════════════════╝

# Neon
┤ uDOS v1.4.4 | @vault | 42 docs ├

# Minimal
uDOS v1.4.4 | @vault | 42 docs
```

---

## Logging Output Styles

### File Logging (Plain)
```
[2026-02-20 14:30:15] INFO: Command HEALTH executed
[2026-02-20 14:30:16] ERROR: Provider 'ollama' offline
[2026-02-20 14:30:17] DEBUG: Cache hit for workspace @vault
```

### Console Output (GENRE-aware, TUI)
```
# Retro GENRE
[INFO] Command HEALTH executed
▓▒░ ERROR ░▒▓
Provider 'ollama' offline

# Neon GENRE
» command HEALTH executed «
▀▄ ERROR ▄▀
provider 'ollama' offline

# Minimal GENRE
Command HEALTH executed
Error: Provider 'ollama' offline
```

---

## Validation Checklist (v1.4.4)

- [ ] 4 core GENREs defined (retro, neon, minimal, dungeon)
- [ ] Each GENRE has complete definition file (genre.yaml)
- [ ] Each GENRE includes palette, borders, text styles
- [ ] Error/warning/success templates defined for each GENRE
- [ ] `tui_genre_manager.py` service loads GENREs
- [ ] All error outputs use GENRE formatting
- [ ] All logging outputs use GENRE colors
- [ ] Display showcase includes GENRE variations
- [ ] Educational materials show GENRE examples
- [ ] Tests verify GENRE compatibility (all widgets render cleanly)

---

## Testing Strategy

### Unit Tests

```python
# tests/v1_4_4_tui_genre_test.py
- test_load_all_genres()
- test_genre_yaml_validation()
- test_color_code_generation(genre, color_name)
- test_border_character_availability()
- test_error_template_formatting()
- test_ansi_code_injection_safety()
```

### Integration Tests

```python
# tests/v1_4_4_tui_widget_genre_rendering_test.py
- test_box_all_genres()
- test_table_all_genres()
- test_grid_all_genres()
- test_status_bar_all_genres()
```

### Acceptance Tests

```bash
# Rendering showcase
bin/display-showcase --by-genre        # Verify all render correctly
bin/demo-tui-rendering --by-genre      # Verify consistency

# Error outputs
ucli PLACE --invalid-arg  # Verify error format per GENRE
ucli HEALTH --verbose     # Verify status bar per GENRE
```

---

## Future Enhancements (post-v1.4.4)

- [ ] Custom GENRE creation guide (for community extensions)
- [ ] GENRE inheritance/mixins (e.g., "neon-minimal" blend)
- [ ] Runtime GENRE switching (`ucli GENRE set <name>`)
- [ ] GENRE performance profiling (color overhead measurement)
- [ ] Accessibility checker (contrast ratios, colorblind simulation)
- [ ] Per-command GENRE overrides (e.g., `PLAY` uses dungeon GENRE)

---

## References

- [docs/roadmap.md#v1.4.4](../roadmap.md#v144--core-hardening-demo-scripts--educational-distribution)
- [Wizard Web Theme System](../../wizard/web/README.md#themes) (separate system, not GENRE)
- [ANSI Color Codes Reference](https://en.wikipedia.org/wiki/ANSI_escape_code#colors)
- [Terminal Capability Database](https://invisible-island.net/ncurses/terminfo.html)
