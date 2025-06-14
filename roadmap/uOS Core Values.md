# uOS Core Values and Data Model

## 🌐 Input-Output Flow (I/O Philosophy)

* **Single-process model**: uOS accepts *one* input at a time and produces *one* output. No multitasking or background threads.
* **Markdown-first**: All interactions and outputs are serialized into `.md` files — readable, searchable, and immutable unless intentionally rewritten.
* **Privacy-by-default**: No external syncing or telemetry. All computation and memory stays local unless exported manually.

## 🪜 Steps (Lifespan Progress)

Each uOS instance evolves via `steps`. These are user-earned progress markers representing:

* A completed interaction or achievement.
* A learned skill, task, or insight.
* A decision or key life event (manually or automatically registered).

Each `step` contains:

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

## 🧠 Memory (The Past)

Memories are reflections of meaningful past moments. They are categorized into four types:

### 1. `uMemory:direct`

* Direct log of a conversation or experience.
* Includes date, raw input/output, notes.

### 2. `uMemory:insight`

* A distilled learning from previous interactions.
* May summarize many `direct` memories.

### 3. `uMemory:anchor`

* A fixed point in space/time that is frequently referenced — e.g., "first code deployment," "hospital visit," or "graduation."
* Can be pinned to a map tile.

### 4. `uMemory:echo`

* A resurfaced or revisited memory brought back by a `step`, mission, or location.
* Echoes may trigger events, updates, or dialogues.

## 🧭 Location Binding (Spatial Memory)

* Each memory, mission, or step can bind to a **Map Tile**.
* Tiles represent physical locations or virtualized symbolic domains.
* Map can be ASCII-visualized and interactive.
* When a tile is active, relevant `echo`, `anchor`, and `mission` links appear.

## 🔁 Interlinking Logic

* A `step` may:

  * Create or finalize a `memory`
  * Unlock or complete a `mission`
  * Reveal new map tiles
* A `mission` may:

  * Be auto-suggested by patterns in `memory`
  * Require location visits to complete
* A `memory:anchor` may:

  * Trigger contextual conversations
  * Limit or enable mission types

---

> "A Wizard's life is mapped not by time, but by Steps. Every memory, every mission, every echo weaves a spell across your world."

Shall we begin with the map tiles' database + logic next?
