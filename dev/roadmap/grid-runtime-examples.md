# Grid Runtime Example Scripts

**Status:** v1.0.7.0 Integration Examples  
**Purpose:** Demonstrate teletext grid rendering, viewport management, and sprite animation

## Example 1: Simple Viewport Rendering

```markdown
# The Forest

You arrive at the forest entrance, where tall trees frame the path ahead.

\`\`\`teletext
████████████████████████████████████████
█ 🌲 🌲 🌲 🌲 🌲 █
█ █
█ PATH ░░░░░░░░░░░░ █
█ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ █
█ █
█ 🌲 🌲 ░░░░░░░░░░░░░ 🌲 █
█ █
█ @ (you are here) █
████████████████████████████████████████
\`\`\`

\`\`\`grid
baseLayer: 300
bounds:
minCol: 20
maxCol: 60
minRow: 10
maxRow: 20
renderMode: sextant
showTerrain: true
showSprites: true
\`\`\`

\`\`\`tiles

- id: forest-entrance-tree-1
  address: L300-AA10
  type: object
  static: true
  char: "🌲"
  palette: [2, 3, 1]

- id: forest-path
  address: L300-AA11
  type: object
  static: true
  char: "░"
  terrain: "grass"

- id: player
  address: L300-AA12
  type: sprite
  static: false
  char: "@"
  frames: 1
  facing: "N"
  \`\`\`

\`\`\`set
set $player.pos.layer 300
set $player.pos.tile "AA12"
set $world.renderMode "sextant"
\`\`\`
```

## Example 2: Sprite Animation & Movement

```markdown
# Woodland Clearing

A sprite (animated character) moves through the clearing.

\`\`\`teletext
┌────────────────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ ░░ ░░░░░░░░ │
│ ░░ > >> > ░░░░░░░░ │ ← sprite walking right
│ ░░ ░░░░░░░░ │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└────────────────────────────────────────┘
\`\`\`

\`\`\`tiles

- id: npc-walker
  address: L300-AB15
  type: sprite
  frames: 3
  currentFrame: 0
  facing: "E"
  chars: [">", ">>", ">"]
  animationSpeed: 500 # ms per frame
  metadata:
  name: "Woodland Sprite"
  behavior: "walk_east"
  path: ["AB15", "AC15", "AD15"]
  \`\`\`

\`\`\`state
$npc = {
id: "npc-walker",
address: "L300-AB15",
facing: "E",
currentFrame: 0,
nextFrame: 1
}

$animation = {
mode: "walking",
targetCell: "AD15",
speed: 500,
elapsed: 0
}
\`\`\`
```

## Example 3: Interactive Location with Connections

```markdown
# Town Square

The heart of the town. Four paths lead in cardinal directions.

\`\`\`grid
location:
id: "L300-AB10"
name: "Town Square"
kind: "landmark"
terrain: "stone"
connections:
N: "L300-AB09" # Town Hall
E: "L300-AC10" # Market
S: "L300-AB11" # Village Green
W: "L300-AA10" # Forest Path
\`\`\`

\`\`\`teletext
North ↑
│
West ← ─────●───── → East
│
South ↓

The town square is a bustling hub where travelers gather.
\`\`\`

\`\`\`set
set $world.currentLocation "L300-AB10"
set $movement.canMove ["N", "E", "S", "W"]
\`\`\`

\`\`\`if
if $player.input == "N"
set $player.pos.tile "AB09"
else if $player.input == "E"
set $player.pos.tile "AC10"
else if $player.input == "S"
set $player.pos.tile "AB11"
else if $player.input == "W"
set $player.pos.tile "AA10"
fi
\`\`\`
```

## Example 4: Layer Band Visualization

```markdown
# Underground Caverns (Multi-Layer)

Experience different layers: surface (SUR), cave system (UDN), deep substrate (SUB).

\`\`\`teletext
SURFACE (L300) │ CAVES (L299) │ SUBSTRATE (L293)
───────────────────├─────────────────────├──────────────────
█████████████████ │ ░░▒▒████░░▒▒ │  
█ 🌲 🌲 █ │ ▒▒ [cave] ▒▒ │ ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
█ @ █ │ ▓▓▓ │ (deep water layer)
████████████████ │ ░░▒▒░░▒▒░░▒▒ │ ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
\`\`\`

\`\`\`state
$world = {
layers: [300, 299, 293],
names: ["Surface", "Caves", "Substrate"],
currentLayer: 300,
currentDepth: 0
}

$ui = {
layerDisplay: "L300 (SUR) - Surface",
visible: ["L300", "L299"],
showSubstrateHint: false
}
\`\`\`

\`\`\`form
(input)
title: "Descend to caves?"
options: - "Go down (L300 → L299)" - "Stay on surface" - "Go deeper (L299 → L293)"
\`\`\`
```

## Example 5: Sky View Integration

```markdown
# Morning at the Summit

The time is dawn, and the sky reflects the location and time.

\`\`\`teletext
═════════════════════════════════════════
█ 🌅 horizon glowing with dawn █
█ █
█ The sky shifts from dark blue to █
█ warm orange as the sun rises. █
═════════════════════════════════════════
\`\`\`

\`\`\`state
$location = {
latitude: 45.5017,
longitude: -73.5673,
altitude: 1200
}

$time = {
hour: 6,
minute: 30,
season: "spring"
}

$sky = {
sunRise: "06:15",
sunSet: "19:45",
moonPhase: 0.25,
clouds: 15
}
\`\`\`

\`\`\`set
set $sky.current "dawn"
set $sky.color (hexColor "FF6B4A") # warm orange
set $sky.brightness 0.5
\`\`\`
```

---

## Integration Checklist for v1.0.7.0

- [ ] Parse `\`\`\`teletext` blocks (raw sextant grid text)
- [ ] Parse `\`\`\`grid` blocks (YAML location definitions)
- [ ] Parse `\`\`\`tiles` blocks (tile manifests with metadata)
- [ ] Implement ViewportManager for rendering composition
- [ ] Add sprite animation frame sequencing
- [ ] Implement pathfinding for location connections
- [ ] Wire into uDOS map blocks (set, form, panel)
- [ ] Test with example-script.md examples
- [ ] Validate fallback rendering (sextant → ASCII)

---

**Status:** Example Scripts (v1.0.7.0 Planning)  
**References:** [grid-runtime README](../core/grid-runtime/README.md)
