# uDOS Gameplay Anchors — Dev Spec (v1.3+)

> **Goal:** containerise classic games (or their logic) as **Game Anchors** that map into the canonical uDOS **LocId** model — so gameplay can *underlay* real-life learning, tasks, travel, and beacon-gated dimensions.

This spec assumes the v1.3 Universe mapping is locked:

- `LocId := <ANCHOR>:<SPACE>:L<EffectiveLayer>-<Cell>`
- Example LocIds:  
  `EARTH:SUR:L305-DA11`  
  `EARTH:UDN:L304-FF92`  
  `GAME:SKYRIM:SUB:L402-88AF`
- Layer semantics:
  - `SUR` → surface / overworld
  - `SUB` → dungeons, interiors, instances
  - `UDN` → hidden / inverted / mirrored

(See: **v1-3 UNIVERSE.md** in this workspace.)

---

## 1) Concept: Game Anchors (first-class uDOS anchors)

A **Game Anchor** is an adapter that maps a game’s internal coordinate/state into the uDOS grid and back.

**Key rules**
- uDOS does **not** store worlds as meshes/pixels — only *relationships* and *identities* via LocId.
- Games can run in sealed sandboxes (terminal, SDL, emu, libretro, wasm, etc).
- A LocId can point to **many** realities at once (Earth SUR + Earth UDN + Game SUB, etc).

### 1.1 Anchor identity model

**AnchorId**
- `EARTH`
- `GAME:<worldId>` (e.g. `GAME:NETHACK`, `GAME:ELITE_A`, `GAME:RPG_BBS`, `GAME:CRAWLER3D`)
- `BODY:<id>`, `CATALOG:<id>`, `SKY` (future)

**Space**
- `SUR | SUB | UDN`

**EffectiveLayer**
- `L300–L899` (banded semantics, still compressed from deeper narratives)

---

## 2) Containerisation: recommended runtimes

You’ll usually want *two* sandboxes, both with the same `GameAnchor` API.

### 2.1 Terminal Sandbox (PTY)
Best for: NetHack / Hack, rpgbbs, classic text roguelikes.

**Characteristics**
- `stdin/stdout` PTY, optionally “tiles” mode if available.
- uDOS renders output as a layer view (text grid), optionally overlaying icons.

### 2.2 Framebuffer Sandbox (SDL/Libretro/Emu)
Best for: Amiga / BBC Micro / tile engines / classic GUIs.

**Characteristics**
- Exposes:
  - framebuffer (RGBA)
  - audio stream
  - input events
  - save-states
- Can be implemented via:
  - libretro core
  - headless emulator with shared memory output
  - SDL app with IPC bridge

---

## 3) TypeScript core interfaces (uDOS Wizard / dev server)

> These are written to be dead-simple and future-proof. You can implement terminal games first and add framebuffer games later without changing the core model.

```ts
// uDOS canonical addressing
export type AnchorId = "EARTH" | `GAME:${string}` | `BODY:${string}` | `CATALOG:${string}` | "SKY";
export type SpaceId = "SUR" | "SUB" | "UDN";
export type EffectiveLayer = `L${number}`; // enforce 300-899 at validation time

export type CellId = string; // e.g. "DA11" / "FF92" / "88AF" (your grid cell encoding)
export type LocId = `${AnchorId}:${SpaceId}:${EffectiveLayer}-${CellId}`;

// Used by scripts and quests to refer to positions inside an anchor
export interface AnchorCoord {
  // A coordinate in the anchor’s native coordinate system.
  // Examples:
  // - NetHack: { x, y, depth }
  // - Elite-A: { systemId, stationId }
  // - 3D crawler: { x, y, z, floorId }
  kind: string;
  data: Record<string, unknown>;
}

export interface AnchorMeta {
  id: AnchorId;
  title: string;
  version?: string;
  description?: string;
  capabilities: {
    // rendering
    terminal?: boolean;
    framebuffer?: boolean;
    tiles?: boolean;
    // state
    saveState?: boolean;
    deterministicSeed?: boolean;
    // integration
    questEvents?: boolean;
    locidReverseLookup?: boolean;
    networkAllowed?: boolean; // should default false
  };
}

export interface QuantiseOptions {
  // how aggressively to quantise (snap) to the uDOS grid
  cellSize?: number;         // or other anchor-specific scale
  layerBandBase?: number;    // e.g. 300 / 400 / 600 etc
  clampToBounds?: boolean;
}

// Maps anchor-native coords into canonical uDOS LocIds and back.
export interface AnchorTransform {
  toLocId(coord: AnchorCoord, opts?: QuantiseOptions): LocId;
  toCoord(locId: LocId): AnchorCoord | null;
}

// Live runtime “instance” of a game/anchor session.
export interface AnchorInstance {
  instanceId: string;          // uuid
  anchorId: AnchorId;          // GAME:NETHACK etc
  createdAt: string;           // ISO
  updatedAt: string;           // ISO
  meta?: Record<string, unknown>;
}

export interface InputEvent {
  ts: number;
  type: "key" | "mouse" | "gamepad" | "touch";
  data: Record<string, unknown>;
}

export interface RenderFrame {
  ts: number;
  // One of these will exist depending on runtime:
  terminal?: {
    width: number;
    height: number;
    // a minimal model: lines OR a grid; implement either first
    lines?: string[];
    grid?: string[]; // row-major; length = height; each string length = width
  };
  framebuffer?: {
    width: number;
    height: number;
    // pointer to shared memory or encoded frame; keep it abstract here
    ref: string;
    format: "RGBA8888" | "RGB565" | "INDEXED";
  };
  // optional overlay helpers (e.g., item positions → LocIds)
  overlays?: Array<{
    locId?: LocId;
    label?: string;
    icon?: string; // future: an internal asset id
    data?: Record<string, unknown>;
  }>;
}

export interface SaveStateRef {
  // storage pointer; can be file path, blob id, etc
  ref: string;
  sizeBytes?: number;
  hash?: string;
  createdAt: string;
}

export interface AnchorEvent {
  ts: number;
  anchorId: AnchorId;
  instanceId: string;
  type:
    | "MOVE"
    | "ENTER_CELL"
    | "EXIT_CELL"
    | "PICKUP"
    | "DROP"
    | "DIALOGUE"
    | "QUEST_TRIGGER"
    | "CUSTOM";
  locId?: LocId;
  coord?: AnchorCoord;
  data?: Record<string, unknown>;
}

// The engine adapter that uDOS talks to (terminal sandbox, libretro, etc).
export interface AnchorRuntime {
  meta(): Promise<AnchorMeta>;
  transform(): Promise<AnchorTransform>;

  createInstance(params?: {
    seed?: string;
    profileId?: string;     // uDOS user profile
    space?: SpaceId;        // SUR/SUB/UDN
    initialLocId?: LocId;   // spawn
  }): Promise<AnchorInstance>;

  destroyInstance(instanceId: string): Promise<void>;

  input(instanceId: string, event: InputEvent): Promise<void>;
  tick(instanceId: string, dtMs: number): Promise<void>;

  render(instanceId: string): Promise<RenderFrame>;

  // Optional: state & rewind
  saveState?(instanceId: string): Promise<SaveStateRef>;
  loadState?(instanceId: string, state: SaveStateRef): Promise<void>;

  // Optional: event stream
  pollEvents?(instanceId: string, sinceTs: number): Promise<AnchorEvent[]>;
}
```

---

## 4) SQLite schema (anchors + game instances + LocId bindings)

> This schema is intentionally “boring”: it’s stable, queryable, and works for both terminal and emulator runtimes.

```sql
PRAGMA journal_mode=WAL;

-- 4.1 Anchor definitions
CREATE TABLE IF NOT EXISTS anchors (
  anchor_id TEXT PRIMARY KEY,               -- "EARTH", "GAME:NETHACK"
  title TEXT NOT NULL,
  description TEXT,
  version TEXT,
  capabilities_json TEXT NOT NULL,           -- JSON string
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- 4.2 Runtime instances (sessions)
CREATE TABLE IF NOT EXISTS anchor_instances (
  instance_id TEXT PRIMARY KEY,             -- uuid
  anchor_id TEXT NOT NULL,
  profile_id TEXT,                          -- uDOS user id / persona
  space_id TEXT,                            -- SUR/SUB/UDN
  seed TEXT,
  meta_json TEXT,                           -- JSON
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id)
);

CREATE INDEX IF NOT EXISTS idx_anchor_instances_anchor
  ON anchor_instances(anchor_id);

-- 4.3 LocId bindings
-- This is the glue: which game coord/state is bound to which LocId.
CREATE TABLE IF NOT EXISTS locid_bindings (
  binding_id TEXT PRIMARY KEY,              -- uuid
  locid TEXT NOT NULL,                      -- canonical LocId
  anchor_id TEXT NOT NULL,
  instance_id TEXT,                         -- nullable: can be global/world-level binding
  coord_kind TEXT NOT NULL,
  coord_json TEXT NOT NULL,                 -- JSON payload of AnchorCoord.data
  label TEXT,
  tags TEXT,                                -- comma tags (simple) OR store json
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id),
  FOREIGN KEY(instance_id) REFERENCES anchor_instances(instance_id)
);

CREATE INDEX IF NOT EXISTS idx_locid_bindings_locid
  ON locid_bindings(locid);

CREATE INDEX IF NOT EXISTS idx_locid_bindings_anchor
  ON locid_bindings(anchor_id);

-- 4.4 Save states
CREATE TABLE IF NOT EXISTS anchor_savestates (
  state_id TEXT PRIMARY KEY,               -- uuid
  instance_id TEXT NOT NULL,
  anchor_id TEXT NOT NULL,
  state_ref TEXT NOT NULL,                 -- file path / blob id
  size_bytes INTEGER,
  hash TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(instance_id) REFERENCES anchor_instances(instance_id),
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id)
);

CREATE INDEX IF NOT EXISTS idx_savestates_instance
  ON anchor_savestates(instance_id);

-- 4.5 Event log (quest triggers, movement, pickups, etc)
CREATE TABLE IF NOT EXISTS anchor_events (
  event_id TEXT PRIMARY KEY,               -- uuid
  ts INTEGER NOT NULL,                     -- epoch ms
  anchor_id TEXT NOT NULL,
  instance_id TEXT NOT NULL,
  type TEXT NOT NULL,
  locid TEXT,
  coord_kind TEXT,
  coord_json TEXT,
  data_json TEXT,
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id),
  FOREIGN KEY(instance_id) REFERENCES anchor_instances(instance_id)
);

CREATE INDEX IF NOT EXISTS idx_anchor_events_instance_ts
  ON anchor_events(instance_id, ts);

CREATE INDEX IF NOT EXISTS idx_anchor_events_locid
  ON anchor_events(locid);

-- 4.6 Quest definitions (Markdown-first, DB-indexed)
CREATE TABLE IF NOT EXISTS quests (
  quest_id TEXT PRIMARY KEY,               -- slug or uuid
  title TEXT NOT NULL,
  source_uri TEXT,                         -- binder://... or file path
  frontmatter_json TEXT NOT NULL,          -- parsed YAML frontmatter as JSON
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- 4.7 Quest progress (per profile)
CREATE TABLE IF NOT EXISTS quest_progress (
  progress_id TEXT PRIMARY KEY,            -- uuid
  quest_id TEXT NOT NULL,
  profile_id TEXT NOT NULL,
  status TEXT NOT NULL,                    -- "LOCKED"|"ACTIVE"|"COMPLETE"|"FAILED"
  last_event_ts INTEGER,
  state_json TEXT,                         -- JSON: counters, flags, etc
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(quest_id) REFERENCES quests(quest_id)
);

CREATE INDEX IF NOT EXISTS idx_quest_progress_profile
  ON quest_progress(profile_id);
```

---

## 5) Quest Markdown: `filename-script.md` (example)

> This matches your existing script direction: Markdown-first, with TS runtime blocks and LocId bindings.

```md
---
title: "Key of CAPI"
quest_id: "key-of-capi"
grid_locations:
  - "EARTH:SUR:L305-DA11"
  - "EARTH:UDN:L304-FF92"
game_bindings:
  - "GAME:NETHACK:SUB:L402-88AF"
beacon_rules:
  udn_requires_verified_wizard: true
rewards:
  - unlock_file: "binder://marketing/meta-capi-checklist.md"
  - drop_object:
      locid: "EARTH:UDN:L304-FF92"
      file: "binder://loot/capi-key.md"
---

# Key of CAPI

Find the key in the dungeon, then return to the upside-down location to unlock the checklist.

```ts
// uDOS script runtime (illustrative)
export async function onEvent(ev) {
  if (ev.type === "PICKUP" && ev.data?.item === "CAPI_KEY") {
    await uDOS.quests.complete("key-of-capi");
    await uDOS.files.unlock("binder://marketing/meta-capi-checklist.md");
  }
}
```
```

---

## 6) Beacon gating (UDN + private wizard nodes)

**Policy defaults**
- `SUR`: public / offline-friendly content allowed
- `SUB`: instance/private by default
- `UDN`: **requires proximity verification** (wizard-to-wizard handshake) unless explicitly disabled

**Implementation sketch**
- LocId resolution checks:
  - Is `SpaceId === "UDN"`?
  - If yes, verify:
    - wizard trust key present AND
    - beacon proximity proof OR local “paired device” proof
- If verification fails:
  - return an “opaque” layer view (no objects, no files, no quest triggers)

---

## 7) Immediate MVP (what to build first)

1. **Anchor registry** (DB + JSON meta) + `AnchorRuntime` interface
2. **Terminal Sandbox runtime** (PTY)
3. **GAME:NETHACK** adapter:
   - `toLocId()` quantises dungeon cells into `SUB:L4xx-....`
   - optional: map dungeon depth → effective layer band within `L400–L499`
4. **Event log** (MOVE / ENTER_CELL / PICKUP)
5. **Quest parser** (frontmatter + ts runtime hook)
6. **UDN gating** (beacon-verified wizard required)

---

## 8) Notes for your specific game list

- **NetHack / Hack (Amiga port):** ideal MVP anchor. Terminal-first, then tiles overlay.
- **rpgbbs:** becomes a *social dungeon layer* with message artefacts pinned to LocIds.
- **3D crawler:** internal 3D, but canonical identity stays grid-first. (3D is a view, not the storage model.)
- **Elite-A:** becomes the spine of your space/trade layers. Systems + ports map naturally into LocIds.

---

## 9) Next: I can generate the “GAME:NETHACK” adapter stub

If you want the next artefact, I’ll output a second Markdown file with:
- `GAME:NETHACK` quantisation rules (x,y,depth → LocId)
- recommended layer bands for floors
- a minimal PTY runtime wrapper contract
- an example `nethack.script.md` quest pack
