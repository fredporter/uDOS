# uDOS Development Plan (Next 90 Days)

## Objectives

- Deliver a **cross-platform alpha** with stable CLI and minimal Tauri UI.
- Lock the **16×16 u-cell display system** (see `docs/DISPLAY-SYSTEM.md`).
- Prove the **input layer** (standard + chorded).
- Introduce the **uSCRIPT Container System** to run *any script* (bash, Python, Node, uCODE/basic).
- Curate **fonts and palettes** (see `docs/uDOS-Font-Roadmap.md`).
- Provide **internal tools** such as the **uDOS Font Editor** (`docs/uDOS-Font-Editor.md`) as reference containers/extensions.

---

## Workstreams & Milestones

### 1) Core Runtime & Process Model

Goal: predictable app lifecycle; sandboxed script execution; IPC channels.

- M1: Config precedence + env loading.
- M2: Job runner with logs + exit codes.
- M3: IPC JSONL schema between UI <→ Core.\
  **Acceptance:** `udos run demo/hello.ud` executes deterministically with logs.

---

### 2) UI/Display — 16×16 u-cell

Canonical spec: [`docs/DISPLAY-SYSTEM.md`]

- M1: Fullscreen Tauri window + system display detection.
- M2: u-cell grid engine (10/12/14 text box modes, 4× overlay).
- M3: Palette + font switch at runtime.\
  **Acceptance:** `demo/display/showcase.ud` switches fonts/palettes smoothly.

---

### 3) Fonts & Palettes

Canonical spec: [`docs/uDOS-Font-Roadmap.md`]

- M1: Finalise 8 bundled monosort fonts + pipeline to pack bitmap fonts.
- M2: Validate tput colour mapping end-to-end (macOS Terminal + Tauri).
- M3: Grayscale palette replaces “Forest Sprite”.\
  **Acceptance:** `uDATA-colours.json` + `uFONTS.json` are applied identically in CLI and UI.

---

### 4) Input System (Standard + Chorded)

Goal: unified input map; chorded “nav” layer (↑ ↓ ← →, GO, BACK).

- M1: Keymap schema + profile loader.
- M2: Repeat/hold consistency across OSes.
- M3: Pointer abstraction placeholder (future tablet/touch).\
  **Acceptance:** Switch profiles on the fly via `demo/input/navtest.ud`.

---

### 5) uSCRIPT Engine + Container System

Goal: run arbitrary scripts (bash, Python, Node, uCODE/basic) reproducibly inside isolated venvs.

- M1: uSCRIPT DSL basics (`step`, `exec`, `ask`, `render`, `store`).
- M2: Container spec v0 + Python adapter.
- M3: Node adapter + shell adapter (allowlist).
- M4: uCODE/basic interpreter MVP.
- M5: Sandboxing + resource limits.\
  **Acceptance:**
- `udos run demo/containers/py-hello.uspec` runs in a fresh venv, JSONL logs to artefacts.
- `udos run demo/basic/hello.ucode` runs in BASIC interpreter.

---

### 6) Internal Tools (via Containers/Extensions)

Reference: [`docs/uDOS-Font-Editor.md`]

- M1: Containerised **Font Editor** (bitmap font grid, inspired by 1980s Mac tools).
- M2: “Palette Switcher” extension (UI).
- M3: “Webhook Server” extension (local dev utility).\
  **Acceptance:** Internal tools run as uSCRIPT containers, no external marketplace required.

---

### 7) Packaging & Installers

- M1: Launch scripts wired (`launch-udos.sh` calls correct platform launcher).
- M2: macOS app bundle (stretch).
- M3: Windows installer + Ubuntu `.deb`.\
  **Acceptance:** One-liner install per OS producing desktop icon + CLI `udos`.

---

### 8) CI/CD & Testing

- M1: CI build + smoke test of `demo/`.
- M2: Golden screenshots for display tests.
- M3: Release pipeline → GitHub Releases.\
  **Acceptance:** PRs pass golden-image tests + demo smoke tests.

---

### 9) Documentation & Developer Experience

Docs Hub: `docs/INDEX.md` links **ARCHITECTURE**, **USER-COMMAND-MANUAL**, **DISPLAY-SYSTEM**, **Font Roadmap**, **Font Editor**.

- M1: Restructure docs hub.
- M2: “Hello u-cell” + “First uSCRIPT” tutorials.
- M3: Container spec reference + BASIC guide.\
  **Acceptance:** All docs have consistent Acorn-style ASCII aesthetic.

---

## Updated ASCII Sketch

```
+------------------ uDOS (App Shell, Tauri) -------------------+
| Input Layer | 16x16 u-cell Display (DISPLAY-SYSTEM.md)       |
| Fonts & Palettes (Font Roadmap) | Host APIs                  |
+------------------------- IPC JSONL --------------------------+
|                   Core Runtime                               |
|  Config | Job Runner | uSCRIPT VM | uSCRIPT Containers       |
|         |            |            | - Python venv            |
|         |            |            | - Node env               |
|         |            |            | - Shell (allowlist)      |
|         |            |            | - uCODE/basic VM         |
+------------------- Internal Tools / Extensions --------------+
| Font Editor (uDOS-Font-Editor.md) | Palette Switcher | Hooks |
+---------------------- Storage / Network ---------------------+
| uMEMORY | sandbox/artifacts | logs | caches | allowlists     |
+--------------------------------------------------------------+
```

