1. example.sqlite.db — Schema + Seed (SQL)

Copy-paste this into a SQLite client (or your app’s DB initialiser) to create and seed the database.

-- example.sqlite.db
-- Schema + seed data for uDOS script runtime external DB binding

PRAGMA foreign_keys = ON;

-- Simple key/value facts
CREATE TABLE IF NOT EXISTS facts (
key TEXT PRIMARY KEY,
value TEXT NOT NULL
);

-- NPC directory (for DB-backed narrative content)
CREATE TABLE IF NOT EXISTS npc (
id TEXT PRIMARY KEY,
name TEXT NOT NULL,
bio TEXT NOT NULL,
tile TEXT NOT NULL,
layer INTEGER NOT NULL
);

-- Points of interest (POIs) per map layer
CREATE TABLE IF NOT EXISTS poi (
id TEXT PRIMARY KEY,
name TEXT NOT NULL,
kind TEXT NOT NULL, -- e.g. "shop", "garden", "gate", "landmark"
tile TEXT NOT NULL,
layer INTEGER NOT NULL,
note TEXT DEFAULT ""
);

-- Optional: tile adjacency graph (for movement demo)
-- This allows deterministic moves without needing to compute coordinates.
CREATE TABLE IF NOT EXISTS tile_edges (
layer INTEGER NOT NULL,
from_tile TEXT NOT NULL,
dir TEXT NOT NULL, -- "N","S","E","W"
to_tile TEXT NOT NULL,
PRIMARY KEY (layer, from_tile, dir)
);

-- Seed facts
INSERT OR REPLACE INTO facts (key, value) VALUES
('weather', 'Clear skies. Light breeze. Good walking weather.'),
('notice', 'Market toll: 10 coins. Key required.'),
('tip', 'Try the Garden first if you need coins.');

-- Seed NPCs
INSERT OR REPLACE INTO npc (id, name, bio, tile, layer) VALUES
('npc_merchant', 'Mara the Merchant', 'A meticulous trader who keeps a ledger of every deal. Knows every rumour in town.', 'AA341-100', 300),
('npc_guard', 'Gate Guard', 'A stoic guard who only respects preparation: a key, and the market toll.', 'AA339-100', 300);

-- Seed POIs (layer 300)
INSERT OR REPLACE INTO poi (id, name, kind, tile, layer, note) VALUES
('poi_garden', 'Garden', 'garden', 'AA340-100', 300, 'You can scavenge here.'),
('poi_market_gate', 'Market Gate', 'gate', 'AA342-100', 300, 'Locked unless you have a key + 10 coins.'),
('poi_market', 'Market District', 'shop', 'AA343-100', 300, 'Busy stalls and traders.'),
('poi_square', 'Town Square', 'landmark', 'AA341-100', 300, 'A good place to meet people.');

-- Seed adjacency edges for layer 300 (a tiny 1D strip for demo)
-- AA339-100 <-> AA340-100 <-> AA341-100 <-> AA342-100 <-> AA343-100
INSERT OR REPLACE INTO tile_edges (layer, from_tile, dir, to_tile) VALUES
(300, 'AA339-100', 'E', 'AA340-100'),
(300, 'AA340-100', 'W', 'AA339-100'),

(300, 'AA340-100', 'E', 'AA341-100'),
(300, 'AA341-100', 'W', 'AA340-100'),

(300, 'AA341-100', 'E', 'AA342-100'),
(300, 'AA342-100', 'W', 'AA341-100'),

(300, 'AA342-100', 'E', 'AA343-100'),
(300, 'AA343-100', 'W', 'AA342-100');

-- Optional: vertical edges (if you want N/S too)
-- INSERT OR REPLACE INTO tile_edges (layer, from_tile, dir, to_tile) VALUES
-- (300, 'AA340-100', 'N', 'AA340-101'),
-- (300, 'AA340-101', 'S', 'AA340-100');

This matches the db binding pattern in your earlier example (facts, npc, poi).
The tile_edges table is included specifically to make movement deterministic without needing coordinate maths.

⸻

2. movement-demo-script.md — Sprite Movement Demo

This demonstrates:
• structured state for player + sprites
• $variables inside panels
• map viewport rendering
• movement via nav + set
• optional DB-backed move resolution (via tile_edges)
• a simple “blocked gate” rule with if/else

Copy-paste as movement-demo-script.md:

---

title: "Movement Demo (Sprites + Map)"
id: "movement-demo"
version: "1.0.0"
runtime: "udos-md-runtime"
mode: "teletext"
stateDefaults: "preserve"
data:
db:
primary: "./data/example.sqlite.db"

---

# Movement Demo (Sprites + Map)

This script demonstrates **movement** using only:

- `state`, `set`, `if/else`, `nav`, `panel`, `map`
- optional DB edges lookup for neighbour tiles

No uPY. No loops. Deterministic behaviour.

---

## Boot

````state
$player = {
  name: "Traveller",
  coins: 0,
  has_key: false,
  pos: { tile: "AA340-100", layer: 300 },
  sprite: { ch: "@", z: 10 }
}

$sprites = [
  { id: "player", ch: "@", z: 10, pos: { tile: "AA340-100", layer: 300 } },
  { id: "npc_guard", ch: "G", z: 5, pos: { tile: "AA342-100", layer: 300 } },
  { id: "poi_gate",  ch: "█", z: 1, pos: { tile: "AA342-100", layer: 300 } }
]

$world = {
  layer: 300,
  gate_tile: "AA342-100",
  market_tile: "AA343-100"
}

$ui = {
  msg: "Use the movement buttons.",
  last_move: "none"
}


⸻

DB edges (optional)

If your runtime supports DB binding (read-only), bind the next tile in each direction.
This uses the tile_edges table from example.sqlite.db.

provider: sqlite
path: "./data/example.sqlite.db"
namespace: "$db"

bind:
  - var: "$db.move.E"
    query: "SELECT to_tile FROM tile_edges WHERE layer = 300 AND from_tile = '${player.pos.tile}' AND dir = 'E' LIMIT 1;"
  - var: "$db.move.W"
    query: "SELECT to_tile FROM tile_edges WHERE layer = 300 AND from_tile = '${player.pos.tile}' AND dir = 'W' LIMIT 1;"

Note: ${player.pos.tile} is a placeholder for parameter substitution.
If you don’t support SQL parameters yet, skip DB movement and use fixed nav choices below.

⸻

HUD

[STATUS]
████████████████████████████
█ Name:  $player.name       █
█ Coins: $player.coins      █
█ Key:   $player.has_key    █
█ Tile:  $player.pos.tile   █
█ Msg:   $ui.msg            █
████████████████████████████


⸻

Map

center: $player.pos.tile
layer: $player.pos.layer
viewport: "15x9"
style: "teletext"
show:
  terrain: true
  poi: true
  sprites: true
sprites: $sprites


⸻

Movement controls (simple, deterministic)

Option A: Fixed movement (no DB)

Use these if you want the simplest possible implementation.

- label: Move West
  to: "#move-west"
- label: Move East
  to: "#move-east"
- label: Toggle Key
  to: "#toggle-key"
- label: Add 10 coins
  to: "#add-coins"


⸻

Move-west

# Move along our demo strip: AA343 -> AA342 -> AA341 -> AA340 -> AA339
# This is intentionally simple and deterministic.
# If you prefer DB-based edges, replace this section with a DB-derived assignment.

set $ui.last_move "W"

# Manual mapping (no conditionals-within-set; keep it simple with if/else blocks below)

```set
set $player.pos.tile "AA342-100"
set $ui.msg "You moved West."

```else
```if $player.pos.tile == 'AA342-100'
```set
set $player.pos.tile "AA341-100"
set $ui.msg "You moved West."

```else
```if $player.pos.tile == 'AA341-100'
```set
set $player.pos.tile "AA340-100"
set $ui.msg "You moved West."

```else
```if $player.pos.tile == 'AA340-100'
```set
set $player.pos.tile "AA339-100"
set $ui.msg "You moved West."

```else
```set
set $ui.msg "You can’t move further West."





```nav
- label: Back
  to: "#hud"


⸻

Move-east

set $ui.last_move "E"

```set
set $player.pos.tile "AA340-100"
set $ui.msg "You moved East."

```else
```if $player.pos.tile == 'AA340-100'
```set
set $player.pos.tile "AA341-100"
set $ui.msg "You moved East."

```else
```if $player.pos.tile == 'AA341-100'
```set
set $player.pos.tile "AA342-100"
set $ui.msg "You moved East."

```else
```if $player.pos.tile == 'AA342-100'
```if $player.has_key == true and $player.coins >= 10
```set
set $player.pos.tile "AA343-100"
set $player.coins 0
set $ui.msg "You paid the toll and entered the Market."

```else
```set
set $ui.msg "Gate blocked: need a key + 10 coins."



```else
```set
set $ui.msg "You can’t move further East."





```nav
- label: Back
  to: "#hud"


⸻

Toggle-key

toggle $player.has_key
set $ui.msg "Key state toggled."

- label: Back
  to: "#hud"


⸻

Add-coins

inc $player.coins 10
set $ui.msg "Added 10 coins."

- label: Back
  to: "#hud"


⸻

HUD (anchor)



[STATUS]
████████████████████████████
█ Name:  $player.name       █
█ Coins: $player.coins      █
█ Key:   $player.has_key    █
█ Tile:  $player.pos.tile   █
█ Msg:   $ui.msg            █
████████████████████████████

### Notes on the movement demo
- This demo uses **explicit IF ladders** to avoid introducing loops.
- Once your runtime supports DB parameter binding cleanly, movement can be simplified:
  - query `$db.move.E` / `$db.move.W`
  - `set $player.pos.tile $db.move.E`
- Gate logic is shown as a simple conditional at the boundary tile.

---

#Usege Example-V2

Here’s the third script (interaction + pickup + DB-backed POIs/NPCs) and the DB binding convention I recommend so the DB-based movement variant becomes clean and deterministic.

⸻

DB binding convention (locked recommendation)

1) Parameter binding syntax

Use named parameters inside SQL, sourced from runtime state:
	•	In SQL: :tile, :layer, etc.
	•	In the binding block: provide params: mapping where values can be $variables or literals.

Example:

```db
provider: sqlite
path: "./data/example.sqlite.db"
namespace: "$db"

bind:
  - var: "$db.move.E"
    query: "SELECT to_tile FROM tile_edges WHERE layer = :layer AND from_tile = :tile AND dir = 'E' LIMIT 1;"
    params:
      layer: $player.pos.layer
      tile:  $player.pos.tile

### 2) Result shape rules (deterministic)
- **Single row + single column** → scalar
  e.g. `$db.move.E = "AA341-100"`
- **Single row + multiple columns** → object
  e.g. `$db.npc.merchant = { id, name, bio, tile, layer }`
- **Multiple rows** → array of objects
  e.g. `$db.poi = [ {name,tile,layer}, ... ]`
- **No rows** → `null` (scalar/object) or `[]` (array), depending on expected shape

This eliminates ambiguity and avoids “special cases” in the runtime.

---

# `interaction-demo-script.md` (DB POIs + NPC + Pickup + Talk)

Copy-paste as `interaction-demo-script.md`:

```md
---
title: "Interaction Demo (Talk / Pickup / POI)"
id: "interaction-demo"
version: "1.0.0"
runtime: "udos-md-runtime"
mode: "teletext"
stateDefaults: "preserve"
data:
  db:
    primary: "./data/example.sqlite.db"
---

# Interaction Demo (Talk / Pickup / POI)

This script demonstrates:
- Map + sprites
- POIs loaded from SQLite
- “Talk” interaction when you’re on the same tile as an NPC
- “Pickup” interaction at a POI (Garden)
- Conditional nav without loops (fixed slots with `when` guards)
- Panels with `$variables` embedded

---

## Boot

```state
$player = {
  name: "Traveller",
  hp: 10,
  coins: 0,
  has_key: false,
  pos: { tile: "AA340-100", layer: 300 },
  sprite: { ch: "@", z: 10 }
}

$sprites = [
  { id: "player", ch: "@", z: 10, pos: { tile: "AA340-100", layer: 300 } },
  { id: "npc_merchant", ch: "M", z: 5, pos: { tile: "AA341-100", layer: 300 } },
  { id: "npc_guard", ch: "G", z: 5, pos: { tile: "AA342-100", layer: 300 } }
]

$ui = {
  msg: "Walk to a character to TALK, or visit the Garden to PICKUP.",
  last: "boot"
}

$world = {
  garden_tile: "AA340-100",
  merchant_tile: "AA341-100",
  gate_tile: "AA342-100",
  market_tile: "AA343-100"
}

$inventory = {
  apple: 0,
  note: 1
}


⸻

DB bindings (NPC + POIs near you)

provider: sqlite
path: "./data/example.sqlite.db"
namespace: "$db"

bind:
  # NPC records (single-row objects)
  - var: "$db.npc.merchant"
    query: "SELECT id, name, bio, tile, layer FROM npc WHERE id='npc_merchant' LIMIT 1;"

  - var: "$db.npc.guard"
    query: "SELECT id, name, bio, tile, layer FROM npc WHERE id='npc_guard' LIMIT 1;"

  # POIs on current layer (multi-row array)
  - var: "$db.poi"
    query: "SELECT name, kind, tile, layer, note FROM poi WHERE layer = :layer ORDER BY name LIMIT 25;"
    params:
      layer: $player.pos.layer

POI fixed slots (no loops)

We project up to 5 POIs into fixed variables for conditional nav without needing iteration.

provider: sqlite
path: "./data/example.sqlite.db"
namespace: "$db"

bind:
  - var: "$db.poi0"
    query: "SELECT name, kind, tile, layer, note FROM poi WHERE layer = :layer ORDER BY name LIMIT 1 OFFSET 0;"
    params: { layer: $player.pos.layer }

  - var: "$db.poi1"
    query: "SELECT name, kind, tile, layer, note FROM poi WHERE layer = :layer ORDER BY name LIMIT 1 OFFSET 1;"
    params: { layer: $player.pos.layer }

  - var: "$db.poi2"
    query: "SELECT name, kind, tile, layer, note FROM poi WHERE layer = :layer ORDER BY name LIMIT 1 OFFSET 2;"
    params: { layer: $player.pos.layer }

  - var: "$db.poi3"
    query: "SELECT name, kind, tile, layer, note FROM poi WHERE layer = :layer ORDER BY name LIMIT 1 OFFSET 3;"
    params: { layer: $player.pos.layer }

  - var: "$db.poi4"
    query: "SELECT name, kind, tile, layer, note FROM poi WHERE layer = :layer ORDER BY name LIMIT 1 OFFSET 4;"
    params: { layer: $player.pos.layer }


⸻

HUD

[STATUS]
████████████████████████████
█ Name:  $player.name       █
█ Coins: $player.coins      █
█ Key:   $player.has_key    █
█ Tile:  $player.pos.tile   █
█ Msg:   $ui.msg            █
████████████████████████████


⸻

Map

center: $player.pos.tile
layer: $player.pos.layer
viewport: "15x9"
style: "teletext"
show:
  terrain: true
  poi: true
  sprites: true
sprites: $sprites


⸻

Movement (simple)

- label: Move West
  to: "#move-west"
- label: Move East
  to: "#move-east"
- label: Interact (Talk / Pickup)
  to: "#interact"
- label: POIs on this layer
  to: "#poi"


⸻

Move-west

```set
set $player.pos.tile "AA342-100"
set $ui.msg "Moved West."
set $ui.last "move_w"

```else
```if $player.pos.tile == 'AA342-100'
```set
set $player.pos.tile "AA341-100"
set $ui.msg "Moved West."
set $ui.last "move_w"

```else
```if $player.pos.tile == 'AA341-100'
```set
set $player.pos.tile "AA340-100"
set $ui.msg "Moved West."
set $ui.last "move_w"

```else
```if $player.pos.tile == 'AA340-100'
```set
set $player.pos.tile "AA339-100"
set $ui.msg "Moved West."
set $ui.last "move_w"

```else
```set
set $ui.msg "No more West."
set $ui.last "move_w_blocked"





```nav
- label: Back
  to: "#hud"


⸻

Move-east

```set
set $player.pos.tile "AA340-100"
set $ui.msg "Moved East."
set $ui.last "move_e"

```else
```if $player.pos.tile == 'AA340-100'
```set
set $player.pos.tile "AA341-100"
set $ui.msg "Moved East."
set $ui.last "move_e"

```else
```if $player.pos.tile == 'AA341-100'
```set
set $player.pos.tile "AA342-100"
set $ui.msg "Moved East."
set $ui.last "move_e"

```else
```if $player.pos.tile == 'AA342-100'
```if $player.has_key == true and $player.coins >= 10
```set
set $player.pos.tile "AA343-100"
dec $player.coins 10
set $ui.msg "Paid toll and entered Market."
set $ui.last "move_e_market"

```else
```set
set $ui.msg "Gate blocked: need key + 10 coins."
set $ui.last "move_e_gate_blocked"



```else
```set
set $ui.msg "No more East."
set $ui.last "move_e_blocked"





```nav
- label: Back
  to: "#hud"


⸻

Interact

[INTERACT]
Stand on:
- Garden tile to PICKUP
- Merchant tile to TALK
- Gate tile to TALK (guard)

1) Garden pickup

You rummage in the garden and find 7 coins and a key.

You are not at the garden.

```set
inc $player.coins 7
toggle $player.has_key
set $ui.msg "Picked up: +7 coins, key."
set $ui.last "pickup_garden"

### 2) Talk to Merchant (requires standing on merchant tile)

```if $player.pos.tile == $world.merchant_tile
You greet **$db.npc.merchant.name**.

$db.npc.merchant.bio

(You don’t see the merchant here.)

3) Talk to Guard at Gate

The guard says: “Key and 10 coins. No exceptions.”

(There’s no guard here.)

- label: Back
  to: "#hud"


⸻

POI

[POI LIST]
Below are up to 5 POIs from the DB on this layer.
(Shown without loops via fixed slots.)

- label: "$db.poi0.name"
  to: "#poi0"
  when: "$db.poi0.name != null"
- label: "$db.poi1.name"
  to: "#poi1"
  when: "$db.poi1.name != null"
- label: "$db.poi2.name"
  to: "#poi2"
  when: "$db.poi2.name != null"
- label: "$db.poi3.name"
  to: "#poi3"
  when: "$db.poi3.name != null"
- label: "$db.poi4.name"
  to: "#poi4"
  when: "$db.poi4.name != null"
- label: Back
  to: "#hud"


⸻

POI0

[POI]
Name: $db.poi0.name
Kind: $db.poi0.kind
Tile: $db.poi0.tile
Note: $db.poi0.note

- label: Jump to this POI (teleport)
  to: "#teleport-poi0"
- label: Back
  to: "#poi"

Teleport-poi0

set $player.pos.tile $db.poi0.tile
set $ui.msg "Teleported to POI: $db.poi0.name"
set $ui.last "teleport_poi0"

- label: Back to HUD
  to: "#hud"


⸻

POI1

[POI]
Name: $db.poi1.name
Kind: $db.poi1.kind
Tile: $db.poi1.tile
Note: $db.poi1.note

- label: Jump to this POI (teleport)
  to: "#teleport-poi1"
- label: Back
  to: "#poi"

Teleport-poi1

set $player.pos.tile $db.poi1.tile
set $ui.msg "Teleported to POI: $db.poi1.name"
set $ui.last "teleport_poi1"

- label: Back to HUD
  to: "#hud"


⸻

POI2

[POI]
Name: $db.poi2.name
Kind: $db.poi2.kind
Tile: $db.poi2.tile
Note: $db.poi2.note

- label: Jump to this POI (teleport)
  to: "#teleport-poi2"
- label: Back
  to: "#poi"

Teleport-poi2

set $player.pos.tile $db.poi2.tile
set $ui.msg "Teleported to POI: $db.poi2.name"
set $ui.last "teleport_poi2"

- label: Back to HUD
  to: "#hud"


⸻

POI3

[POI]
Name: $db.poi3.name
Kind: $db.poi3.kind
Tile: $db.poi3.tile
Note: $db.poi3.note

- label: Jump to this POI (teleport)
  to: "#teleport-poi3"
- label: Back
  to: "#poi"

Teleport-poi3

set $player.pos.tile $db.poi3.tile
set $ui.msg "Teleported to POI: $db.poi3.name"
set $ui.last "teleport_poi3"

- label: Back to HUD
  to: "#hud"


⸻

POI4

[POI]
Name: $db.poi4.name
Kind: $db.poi4.kind
Tile: $db.poi4.tile
Note: $db.poi4.note

- label: Jump to this POI (teleport)
  to: "#teleport-poi4"
- label: Back
  to: "#poi"

Teleport-poi4

set $player.pos.tile $db.poi4.tile
set $ui.msg "Teleported to POI: $db.poi4.name"
set $ui.last "teleport_poi4"

- label: Back to HUD
  to: "#hud"


⸻

HUD anchor



[STATUS]
████████████████████████████
█ Name:  $player.name       █
█ Coins: $player.coins      █
█ Key:   $player.has_key    █
█ Tile:  $player.pos.tile   █
█ Msg:   $ui.msg            █
████████████████████████████

---

### Notes (implementation expectations)

- Movement is explicit to avoid loops.
- Interaction is “stand-on-tile” logic.
- POI “dynamic nav” is achieved via **fixed slots** (`poi0..poi4`).
- Teleport is included as a clean test of `set` using DB-derived values.
- You can later add a formal `action` block, but this stays within the v0 blocks we agreed.


⸻
````
