# uDOS v1.3 Architecture (Production)

**Status:** Draft (v1.3.0)
**Scope:** Core + Wizard + Sonic + App + Extensions

---

## 1) Goals
- Offline-first, deterministic core runtime.
- Vault-first storage (Obsidian-compatible).
- Optional LAN/cloud gateway (Wizard) without data-at-rest.
- Modular extensions via container contracts.

---

## 2) Core (Offline Runtime)
**Location:** `core/`

**Responsibilities**
- Parse Markdown → state → HTML.
- Deterministic output for identical inputs.
- Local-only by default; no network dependency.

**Key Interfaces**
- `core/src/types.ts` — runtime state, blocks, document model.
- `core/src/spatial/*` — anchor + grid canvas interfaces (stubs).

---

## 3) Wizard (Gateway)
**Location:** `wizard/`

**Responsibilities**
- Render gateway for LAN/cloud (stateless).
- AI routing (Ollama local-first + optional cloud).
- Plugin repository + update routing.

**Key Routes**
- `/api/render/*` — render lane.
- `/api/plugin/*` — plugin operations.
- `/api/ai/complete` — AI interface (mode presets).

---

## 4) Sonic (Bootable Entry)
**Location:** `sonic/`

**Responsibilities**
- USB builder and multi-boot installer.
- Bootable entry for TUI + minimal services.

---

## 5) App (Tauri)
**Location:** `app/`

**Responsibilities**
- Local vault picker + editor.
- Offline preview using Core runtime.
- Optional Wizard connection for AI.

---

## 6) Extensions + Containers
**Location:** `library/`

**Responsibilities**
- Container definitions for extensions.
- Contracts in `library/extensions/`.

---

## 7) Silos + Bridges
See `V1.3-FINAL-TRANSITION-PLAN.md` for the authoritative layout.

---

## 8) Versioning + Release
- Manifest: `v1.3.0-release-manifest.yml`.
- Version locks across Core + Wizard.

