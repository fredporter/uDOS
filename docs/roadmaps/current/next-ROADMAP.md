# uDOS Roadmap Strategy (uCORE → uSCRIPT → uNETWORK)

This roadmap describes how the uDOS project is structured and delivered across platforms, with a layered design and clear separation of concerns.

---

## 🎯 Goals

- **Separation of concerns:** runtime “core” vs script runtime vs UI.  
- **Predictable distribution:** same repo powers macOS/Ubuntu/Windows and TinyCore A/AA/B.  
- **Assets & extensions are first-class:** stored in their own directories.  
- **Stable public interfaces:** CLI + JSON contracts between layers.

---

## 📂 Repository Layout

```
uDOS/
├─ core/                     # uCORE: base runtime (POSIX + Bash)
├─ scripts/                  # uSCRIPT runtime (Python venv, helpers)
├─ ui/                       # uNETWORK (Tauri app, binaries + schemas)
├─ assets/                   # Fonts, palettes, themes
├─ extensions/               # Official & community extensions
├─ distro/                   # Build profiles & packaging
│  ├─ profiles/              # TinyCore A/AA/B, Ubuntu, Windows, macOS
│  └─ scripts/               # build-image, pack-tcz/sce
├─ docs/                     # Architecture, distros, API
├─ tools/                    # Dev tooling
└─ VERSION                   # Single source of truth
```

---

## 🔗 Layer Contracts

- **core ⇄ scripts:** CLI tools that emit/accept JSON (jq-friendly).  
- **scripts ⇄ ui:** JSON message bus (schemas in `ui/ipc/`).  
- **assets:** managed by `UDOS_ASSETS_DIR` with manifest.json for versioning.

---

## 🌳 Branching & Release Model

- **main** — always releasable.  
- **next** — integration branch for features.  
- **release/*** — short-lived hardening branches.  
- **hotfix/*** — emergency fixes.

**Tags:** `vMAJOR.MINOR.PATCH` used across all artefacts.

---

## 📦 Build Profiles

- **A (uCORE only)** — CLI, minimal packages.  
- **AA (Runtime)** — uCORE + uSCRIPT + uNETWORK (no dev toolchains).  
- **B (Dev)** — Full runtime + dev stacks (Rust, Node, etc).

---

## 🛠 CI/CD

- **PRs:** lint, unit tests, schema validation.  
- **Nightly:** build TinyCore ISOs (A & AA) + desktop artifacts.  
- **Release:** build all installers and TinyCore ISOs/IMGs; publish manifest + docs.

---

## 📌 Migration Plan

1. Move fonts/extensions → `assets/` & `extensions/`.  
2. Replace hardcoded paths with `UDOS_ASSETS_DIR`.  
3. Bootstrap registers assets/extensions into cached index.  
4. Profiles explicitly include bundles.

---

## ✅ Developer Ergonomics

- Local dev on Ubuntu/macOS/Windows.  
- Mock core (`tools/mock-core`) for UI testing without TinyCore.  
- Contracts and adapters are the main touchpoints between layers.

---
