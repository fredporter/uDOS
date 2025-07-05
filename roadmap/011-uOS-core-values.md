# uOS Core Values and Data Model

## 🌐 Input-Output Flow (I/O Philosophy)

* **Single-process model**: uOS accepts *one* input at a time and produces *one* output. No multitasking or background threads.
* **Markdown-first**: All interactions and outputs are serialized into `.md` files — readable, searchable, and immutable unless intentionally rewritten.
* **Privacy-by-default**: No external syncing or telemetry. All computation and memory stays local unless exported manually.

## 🪜 Moves (Lifespan Progress)

Each uOS instance evolves via `moves`. These are user-earned progress markers representing:

* A completed interaction or achievement.
* A learned skill, task, or insight.
* A decision or key life event (manually or automatically registered).

Each `move` contains:

* A timestamp.
* A reference to a mission, memory, or location.
* Metadata: intent, impact, type.
* Validation hash (when uScript confirms its conditions).

## 🪧 Mission (The Future)

Missions are forward-facing intentions. Defined by:

* **Type**: learning, creation, exploration, healing, connection.
* **Scope**: personal, shared, experimental.
* **Timeline**: with optional steps/milestones.
* **Link**: each mission connects to 1+ steps, and optionally to memories (context).
* **Location**: physical or symbolic map tiles.

## 🧠 Milestone (The Past)

Milestone are reflections of meaningful past moments on the way to completing a Mission. 

## 🧭 Location Binding (Spatial Memory)

* A milestrone, mission, or move can bind to a **Map Tile**.
* Tiles represent physical locations or virtualized symbolic domains.
* Map can be ASCII-visualized and interactive.
* When a tile is active, relevant `echo`, `anchor`, and `mission` links appear.

## 🔁 Interlinking Logic

* A `move` may:

  * Create or finalize a `milestone`
  * Unlock or complete a `mission`
  * Reveal new map tiles
* A `mission` may:

  * Be auto-suggested by patterns in `memory`
  * Require location visits to complete
* A `milestone` may:

  * Trigger contextual conversations
  * Limit or enable mission types

