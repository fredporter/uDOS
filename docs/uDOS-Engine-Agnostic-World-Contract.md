# uDOS Engine‑Agnostic World Contract  
**Version:** 1.0  
**Status:** Canonical (engine‑neutral)  

---

## 0. Purpose

This contract defines the immutable boundary between **uDOS (world truth)** and **engines (views & interaction)**.

Engines are disposable.  
The world is not.

---

## 1. Core principle

> **Identity, meaning, permissions, and persistence live in uDOS.**  
> **Engines only render and emit events.**

---

## 2. Canonical world identity

### LocId (single source of truth)

```
<ANCHOR>:<SPACE>:<EFFECTIVE_LAYER>-<CELL>
```

Examples:
```
EARTH:SUR:L305-DA11
EARTH:UDN:L304-FF92
GAME:NETHACK:SUB:L402-88AF
GAME:ELITE_A:SUR:L701-CC10
```

Engines must not reinterpret LocId semantics.

---

## 3. Engine responsibilities

### Engines MAY
- Render any visual representation
- Use any coordinate system
- Animate, simulate, stream
- Maintain temporary runtime state
- Emit events

### Engines MUST NOT
- Invent LocIds
- Persist canonical world state
- Bypass access rules
- Redefine layer meaning

---

## 4. Required adapter interface (logical)

### World input (read-only)

```ts
interface WorldQuery {
  getVisibleLocIds(view): LocId[];
  getLocMeta(locId): LocMeta;
  getObjectsAt(locId): WorldObject[];
  getPermissions(locId, profileId): AccessPolicy;
}
```

### World output (events only)

```ts
type WorldEvent =
  | { type: "MOVE"; from: LocId; to: LocId }
  | { type: "ENTER"; locId: LocId }
  | { type: "EXIT"; locId: LocId }
  | { type: "INTERACT"; locId: LocId; objectId?: string }
  | { type: "QUEST_TRIGGER"; questId: string }
  | { type: "CUSTOM"; name: string; data?: unknown };
```

Engines never mutate world state directly.

---

## 5. Coordinates & transforms

Coordinates are views, not truth.

Engines must provide reversible transforms:

```ts
LocId ⇄ EngineCoord
```

If precision is lost, LocId always wins.

---

## 6. Layer semantics

| Space | Meaning |
|------|--------|
| SUR | Surface / overworld |
| SUB | Dungeons / interiors / instances |
| UDN | Hidden / inverted / beacon-gated |

Engines may style layers differently but must not merge them.

---

## 7. Objects

```ts
interface WorldObject {
  objectId: string;
  locId: LocId;
  type: "file" | "npc" | "portal" | "marker" | "custom";
  uri?: string;
}
```

Objects are owned by uDOS.  
Engines only render & interact.

---

## 8. Quests

- Quests are Markdown-first
- Engines emit events
- uDOS resolves logic, rewards, and persistence

---

## 9. Persistence rules

| Data | Owner |
|-----|------|
| LocIds | uDOS |
| Layers | uDOS |
| Quests | uDOS |
| Files | uDOS |
| Permissions | uDOS |
| Save-states | Engine (opaque) |

---

## 10. Compatibility guarantee

Any two engines obeying this contract can represent the same world without loss.

---

## 11. Design mantra

> **uDOS thinks. Engines feel.**  
> **uDOS remembers. Engines experience.**

---

End of contract.
