# Gameplay Lens Architecture — v1.4.4

**Status:** Architecture Specification
**Target:** Game variant rendering abstraction layer
**Version:** v1.4.4

---

## Overview

A **Lens** is a rendering abstraction that translates game state from external TOYBOX containers (nethack, elite, rpgbbs, crawler3d) into uDOS viewport presentations. Each lens acts as an adapter between container output and TUI rendering.

### Design Goals

1. **Containment** — External game runtimes remain unmodified; translation happens in lens only
2. **Modularity** — Each game variant gets dedicated lens module; easy to add new variants
3. **Compatibility** — All lenses implement same interface; swappable at runtime
4. **Accessibility** — Fallback `simple_ascii_lens` works for all games without variant-specific logic
5. **Extensibility** — Community can create custom lenses without modifying Core

---

## Lens Interface Contract

### Input: Game State

```python
@dataclass
class GameState:
    """Container output state."""
    variant: str              # "nethack" | "elite" | "rpgbbs" | "crawler3d"
    raw_output: str          # Raw terminal/tty output from game
    player_pos: Optional[Tuple[int, int]]  # Position if parseable
    viewport_width: int      # Expected width
    viewport_height: int     # Expected height
    status_line: Optional[str]  # Status bar output (name, HP, etc.)
    message_queue: List[str] # Recent messages
    input_ready: bool        # Game awaiting input
```

### Output: Rendered View

```python
@dataclass
class LensOutput:
    """Rendered viewport for display."""
    view_name: str          # "nethack_ascii" | "elite_corridor" | "rpgbbs_term" | "generic_grid"
    rendered_frame: str     # ANSI-formatted TUI output
    dimensions: Tuple[int, int]  # Actual rendered size
    input_prompt: str       # Prompt for user input (e.g., "> ")
    metadata: Dict[str, Any]  # Lens-specific data
```

### Interface Method Signature

```python
class Lens(Protocol):
    """Lens interface."""

    def __init__(self, width: int = 80, height: int = 24):
        """Initialize lens with viewport dimensions."""
        ...

    def render(self, state: GameState) -> LensOutput:
        """Render game state to viewport output."""
        ...

    def translate_input(self, user_input: str) -> str:
        """Translate user input from uDOS format to game format."""
        ...

    def supports_variant(self, variant: str) -> bool:
        """Check if lens supports game variant."""
        ...

    def get_metadata(self) -> Dict[str, str]:
        """Return lens metadata (name, description, supported_variants)."""
        ...
```

---

## Lens Implementations

### 1. `SimpleAsciiLens` (Fallback)

**Supported:** All variants
**Approach:** Generic grid-based rendering (viewport + sidebar status)

```
Example output:
┌────────────────────────────────┐
│................                │
│.....@.................        │
│................                │
│................                │
│................                │
└────────────────────────────────┘
Status: HP 50/100 | Level 10 | Gold: 500
> _
```

**Features:**
- Renders game output as monospace grid
- Extracts status line if recognizable
- Shows all raw terminal output if needed
- Transparent fallback (no game-specific magic)

**Tests:** Basic viewport clipping, status extraction, input passthrough

### 2. `NethackLens`

**Supported:** nethack (classic roguelike)
**Approach:** Parse nethack-specific format (dungeon grid + status bar)

```
Example output:
┌───────────────────────────────────────────┐
│...................@..........            │
│......#####..................             │
│......#...#..................             │
│......#.*.#..................             │
│......#####..................             │
└───────────────────────────────────────────┘
Status: Dlvl:1 Hp:16(16) Pw:7(7) AC:7 Xp:1/0 T:0
Message: Welcome to NetHack!
> _
```

**Features:**
- Parse nethack dungeon (@, ., #, monsters)
- Extract hero position (@)
- Colorize terrain and creatures
- Parse status bar (Dlvl, Hp, Pw, AC, Xp, T)
- Queue messages from game output

**Input Translation:**
- Single char → pass through (a, s, d, w, etc.)
- `<` / `>` → stairs up/down
- `>` → loot/pickup
- `?` → help menu

**Tests:** Dungeon grid parsing, hero position, status line, color palette, input mapping

### 3. `EliteLens`

**Supported:** elite (space flight sim with 3D corridor view)
**Approach:** Procedural 3D corridor visualization + HUD

```
Example output (3D flight corridor):
                    ░
                 ░  ▓  ░
              ░  ▓▓▓▓▓  ░
           ░  ▓▓▓▓▓▓▓▓▓  ░
        ░  ▓▓▓▓▓▓▓▓▓▓▓▓▓  ░  <-- Player
           ░  ▓▓▓▓▓▓▓▓▓  ░
              ░  ▓▓▓▓▓  ░
                 ░  ▓  ░
                    ░

Shield: ▓▓▓▓▓░░░░░  Armor: ▓▓▓▓░░░░░░  Speed: 12c
Fire Control: Ready  | Cargo: 20t / 40t  | Altitude: 5000m
Target: Space Station Alpha | Distance: 250 km
> _
```

**Features:**
- Generate 3D ASCII corridor from game state (distance/speed data)
- Render HUD: shields, armor, speed, cargo, altitude
- Colorize corridor depth and targets
- Display current target and navigation data

**Input Translation:**
- Arrow keys → pitch/roll/yaw
- `j`/`h` → throttle up/down
- `f` → fire weapons
- `l` → hyperspace/launch

**Tests:** Corridor generation proceduralism, HUD formatting, input mapping, depth effect

### 4. `RPGBBSLens`

**Supported:** rpgbbs (BBS-style MUD/text adventure)
**Approach:** Preserve terminal lineage; wrap/format for modern terminal

```
Example output:
═══ The Tavern ═══════════════════════════════════════
Dim light filters through the tavern's smoky air.

People here:
  - Bartender (serving drinks)
  - Suspicious +Rogue (leaning in shadows)
  - Noble Lady (waiting for someone)

Exits:
  [N]orth → Town Square
  [E]ast  → Inn
  [W]est  → Blacksmith

Inventory (15/40): Sword, Rope, Potion (x3), Gold (x127)
Health: ████████░░ (80/100) | Mana: ██████░░░░ (60/100)

> attack rogue
You swing at the Rogue!
...
> _
```

**Features:**
- Preserve original text layout
- Parse room descriptions (header, exits, NPCs, items)
- Wrap long lines to viewport width
- Render inventory with item counts
- Show health/mana bars with progress format

**Input Translation:**
- `[N]orth` → `n` / `north`
- Commands parsed as natural language
- Preserve original input semantics

**Tests:** Text wrapping, NPC parsing, inventory display, health bar rendering

### 5. `Crawler3DLens`

**Supported:** crawler3d (procedural 3D dungeon crawler)
**Approach:** Generate 3D-like perspective view + mini-map

```
Example output (first-person 3D perspective):
              ╔═══════════╗
              ║     ▓     ║
              ║   ▓▓▓▓▓   ║
              ║ ▓▓▓▓▓▓▓▓▓ ║
═════════════╦╩═════════════╩═════════════
  ▓        ║ M          E ║        ▓
═════════════╦═════════════╩═════════════
              ║ ▓▓▓▓▓▓▓▓▓ ║
              ║   ▓▓▓▓▓   ║
              ║     ▓     ║
              ╚═══════════╝

[MiniMap]    Mini-map legend:
█ █ █ █ █    @ = You
█ . . . █    . = Empty
█ @ . . █    # = Wall
█ . . . █    M = Monster
█ █ █ █ █    E = Exit

Level: 3 | Monsters: 5 | Gold: 250 | HP: 45/80
Inventory: Sword, Shield, Potion (x2)
> move north
> _
```

**Features:**
- Generate first-person 3D perspective (depth layers)
- Render mini-map of current room
- Show visible monsters/items in FOV
- Track dungeon level
- Mosaic enemy positions (relative distance)

**Input Translation:**
- Arrow keys / `wasd` → movement
- `a` / `d` → strafe
- `space` → attack/interact
- `i` → inventory
- `e` → examine

**Tests:** 3D perspective generation, mini-map layout, enemy rendering, input binding

---

## Lens Registration & Selection

### Lens Registry

```python
LENS_REGISTRY: Dict[str, Lens] = {
    "simple_ascii": SimpleAsciiLens,
    "nethack": NethackLens,
    "elite": EliteLens,
    "rpgbbs": RPGBBSLens,
    "crawler3d": Crawler3DLens,
}

# Variant → default lens mapping
VARIANT_LENS_MAP: Dict[str, str] = {
    "nethack": "nethack",
    "elite": "elite",
    "rpgbbs": "rpgbbs",
    "crawler3d": "crawler3d",
}
```

### Lens Switching

```bash
# Show current lens
PLAY LENS

# Switch to specific lens
PLAY LENS nethack      # Use nethack-specific renderer
PLAY LENS elite_3d     # Use elite corridor view
PLAY LENS simple_ascii # Use generic fallback

# List available lenses
PLAY LENS --list
```

### Lens Selection Logic

1. **User explicit choice:** `PLAY LENS <name>` sets preferred lens for session
2. **Variant default:** If no preference, use VARIANT_LENS_MAP
3. **Fallback:** If variant lens unavailable, use `simple_ascii`

---

## Integration Points

### In `core/commands/play_handler.py`

```python
class PlayHandler:
    def handle_play(self, args):
        # ...
        if args.subcommand == "LENS":
            return self.handle_lens_command(args)
        # ...

    def handle_lens_command(self, args):
        if args.action == "SWITCH":
            lens = get_lens(args.lens_name)
            self.game_session.set_lens(lens)
        elif args.action == "LIST":
            return self.list_available_lenses()
        elif args.action == "STATUS":
            return self.current_lens.get_metadata()
```

### In Gameplay Service Loop

```python
def render_game_frame(self):
    game_state = self.container.capture_state()
    lens = self.game_session.current_lens
    rendered = lens.render(game_state)
    self.display_manager.render_frame(rendered.rendered_frame)
```

---

## Testing Strategy

### Unit Tests (per lens)

```python
# tests/v1_4_4_lens_nethack_test.py
- test_parse_dungeon_grid()
- test_extract_hero_position()
- test_parse_status_bar()
- test_color_terrain()
- test_translate_input_north()
- test_invalid_input_handling()

# tests/v1_4_4_lens_elite_test.py
- test_corridor_generation_distance()
- test_hud_rendering()
- test_speed_effects_visualization()
- test_input_pitch_roll()

# ... similar for rpgbbs, crawler3d
```

### Integration Tests

```python
# tests/v1_4_4_gameplay_lens_integration_test.py
- test_lens_switching_mid_game()
- test_fallback_lens_all_variants()
- test_input_translation_chain()
- test_state_preservation_lens_switch()
```

### Acceptance Tests

```bash
# Manual playthrough with each lens
PLAY @profile/nethack   # Start nethack
PLAY LENS simple_ascii  # Switch to fallback, verify playable
PLAY LENS nethack       # Switch back, verify artifacts gone
```

---

## Validation Criteria (v1.4.4)

- [ ] All 5 lenses implemented and compileable
- [ ] SimpleAsciiLens works with all 4 game variants
- [ ] Variant-specific lenses render without errors
- [ ] Lens switching works without game interruption
- [ ] Input translation maintains game semantics
- [ ] Unit tests: 85%+ coverage per lens
- [ ] Integration tests: all lens combinations pass
- [ ] Performance: lens rendering <100ms per frame
- [ ] Fallback: if lens crashes, auto-revert to simple_ascii

---

## Future Enhancements (post-v1.4.4)

- [ ] Custom lens creation guide (for community extensibility)
- [ ] Lens configuration schema (e.g., color overrides)
- [ ] Recording/replay of lens-rendered gameplay
- [ ] Lens performance profiling and optimization
- [ ] Network lens (multi-player game output synchronization)

---

## References

- [docs/roadmap.md#v1.4.4](../roadmap.md#v144--core-hardening-demo-scripts--educational-distribution)
- [core/commands/play_handler.py](../../core/commands/play_handler.py)
- [core/services/gameplay_service.py](../../core/services/gameplay_service.py)
- TOYBOX container specifications (see `docs/specs/TOYBOX-CONTAINER-*-v1.3.md`)
