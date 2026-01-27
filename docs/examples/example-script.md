---
title: "Example Interactive Script"
id: "example-script"
version: "1.0.0"
runtime: "udos-md-runtime"
mode: "teletext"
stateDefaults: "preserve"
data:
  db:
    primary: "./data/example.sqlite.db"
---

# Example Script (all features)

This file demonstrates:

- `$variables` + interpolation in normal text and in code blocks
- Structured state: objects, arrays, sprites, map layers/locations
- `form`, `set`, `if/else`, `nav`
- `panel` (ASCII/teletext)
- `map` (viewport render)
- Optional sandboxed `.ts` logic (Phase 2 feature)
- External SQLite `.db` as an _extended variable source_ (read-only in v0)

---

## 0) State boot

```state
$app = { name: "uDOS", mode: "teletext", locale: "en-AU" }

$player = {
  id: "player",
  name: "Traveller",
  hp: 10,
  coins: 3,
  has_key: false,
  pos: { tile: "AA340-100", layer: 300 },
  sprite: { ch: "@", z: 10 }
}

$world = {
  tile: "AA340-100",
  layer: 300,
  layers: {
    100: { label: "World", cell_km: 83 },
    300: { label: "City",  cell_m: 93 },
    400: { label: "District", cell_m: 3 }
  }
}

$sprites = [
  { id: "player", ch: "@", z: 10, pos: { tile: "AA340-100", layer: 300 } },
  { id: "npc_merchant", ch: "M", z: 5, pos: { tile: "AA341-100", layer: 300 } },
  { id: "npc_guard", ch: "G", z: 5, pos: { tile: "AA339-100", layer: 300 } }
]

$inventory = [
  { id: "apple", label: "Apple", qty: 1 },
  { id: "note", label: "Crumpled note", qty: 1 }
]

$ui = {
  last_anchor: "#start",
  last_action: "boot",
  debug: false
}


⸻

1) External DB: extend variables (SQLite)

The runtime can optionally bind external data into $variables.
In v0, treat this as read-only and cacheable.

provider: sqlite
path: "./data/example.sqlite.db"
namespace: "$db"

# Optional: schema assumptions
# table: facts(key TEXT PRIMARY KEY, value TEXT)
# table: npc(id TEXT PRIMARY KEY, name TEXT, bio TEXT, tile TEXT, layer INT)

bind:
  - var: "$db.fact.weather"
    query: "SELECT value FROM facts WHERE key='weather' LIMIT 1;"
  - var: "$db.npc.merchant"
    query: "SELECT id, name, bio, tile, layer FROM npc WHERE id='npc_merchant' LIMIT 1;"
  - var: "$db.map.poi"
    query: "SELECT name, tile, layer FROM poi WHERE layer = 300 LIMIT 25;"

If available, you can now reference:
	•	$db.fact.weather
	•	$db.npc.merchant.name
	•	$db.map.poi[0].name

Example: Today’s DB weather snippet is: $db.fact.weather

⸻

2) Start

Start

Hello $player.name.
HP: $player.hp · Coins: $player.coins · Key: $player.has_key
Location: $player.pos.tile at Layer $player.pos.layer ($world.layers[$player.pos.layer].label)

⸻

3) Form: edit live variables

- var: $player.name
  type: text
  label: Your name
  placeholder: Traveller

- var: $player.coins
  type: number
  label: Coins
  min: 0

- var: $player.has_key
  type: toggle
  label: Do you have the key?

- var: $player.pos.layer
  type: choice
  label: Map layer
  options:
    - label: City (300)
      value: 300
    - label: District (400)
      value: 400

- var: $ui.debug
  type: toggle
  label: Debug mode


⸻

4) Panel: teletext/ASCII with $variables inside the block

[SYSTEM INFO]
████████████████████████████
█ App:   $app.name          █
█ Mode:  $app.mode          █
█ User:  $player.name       █
█ HP:    $player.hp         █
█ Coins: $player.coins      █
█ Key:   $player.has_key    █
█ Tile:  $player.pos.tile   █
█ Layer: $player.pos.layer  █
████████████████████████████


⸻

5) Conditionals: IF / ELSE (gated storyline)

You unlock the door to the Market District. The guard nods respectfully.

The Market District gate is locked. You’ll need a key and 10 coins.


⸻

6) Map: render viewport + sprites (teletext-capable)

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

7) Navigation: choice list + when gates

- label: Visit the Garden (find items)
  to: "#garden"

- label: Talk to the Merchant (DB-backed NPC bio)
  to: "#merchant"
  when: "$db.npc.merchant.name != null"

- label: Enter the Market District
  to: "#market"
  when: "$player.has_key == true and $player.coins >= 10"

- label: Debug / Inspect State
  to: "#debug"
  when: "$ui.debug == true"


⸻

Garden

You search the garden bed and find 7 coins and a shiny key.

inc $player.coins 7
toggle $player.has_key
set $ui.last_action "garden_loot"

Return to the start:

- label: Back to Start
  to: "#start"


⸻

Merchant

The merchant looks up from their ledger.

From the DB:
	•	Name: $db.npc.merchant.name
	•	Bio: $db.npc.merchant.bio
	•	Location: $db.npc.merchant.tile / $db.npc.merchant.layer

You can buy an apple for 2 coins.

Deal! You buy an apple.

You don’t have enough coins.

- label: Buy Apple (2 coins)
  to: "#buy-apple"
  when: "$player.coins >= 2"
- label: Back to Start
  to: "#start"

Buy-apple

dec $player.coins 2
set $ui.last_action "bought_apple"

(Inventory update is shown as a pattern; if arrays are supported, switch to append/increment logic.)

[INVENTORY NOTE]
You purchased an apple.
(Inventory array mutation can be enabled in Phase 1.1)

- label: Back to Start
  to: "#start"


⸻

Market

Welcome to the Market District.

You spend 10 coins to enter (a toll).

dec $player.coins 10
set $ui.last_action "market_entry"

[MARKET PASS]
████████████████████████████
█ Entry granted.            █
█ Enjoy the market.         █
████████████████████████████

- label: Back to Start
  to: "#start"


⸻

Debug

This section shows state usage patterns and (optional) .ts logic.

8.1 Show state (render-time)
	•	$player.name = $player.name
	•	$player.hp = $player.hp
	•	$player.coins = $player.coins
	•	$player.pos.tile = $player.pos.tile
	•	$world.layers[$player.pos.layer].label = $world.layers[$player.pos.layer].label

8.2 Optional sandboxed .ts block (Phase 2)

If/when you enable sandboxed TS, this block can compute derived values.
It must be capability-limited (no network/fs, only read/write state, and emit UI events).

// Phase 2 (optional): sandboxed script
// Inputs: state (read/write), emit(type, payload), now (optional)
// No imports, no network, no fs.

const coins = state.player.coins ?? 0;
state.ui.derived = state.ui.derived ?? {};
state.ui.derived.rank =
  coins >= 20 ? "Gold" :
  coins >= 10 ? "Silver" :
  coins >= 5  ? "Bronze" : "Starter";

emit("log", { message: `Derived rank set to: ${state.ui.derived.rank}` });

If sandboxing is disabled, the runtime should render a warning panel instead of executing.

[DEBUG NOTE]
Sandboxed TS blocks are optional.
If disabled, this content is treated as documentation.

- label: Back to Start
  to: "#start"


⸻

9) End marker

Thanks for testing, $player.name.

[END]
████████████████████
█ Saved state is    █
█ per-script file.  █
████████████████████

```
