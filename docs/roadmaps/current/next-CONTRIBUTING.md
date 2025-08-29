# Contributing to uDOS

We welcome contributions! This guide explains how to work with the repo and submit changes.

---

## 📂 Repo Structure

- `core/` — uCORE base runtime (Bash + system libs)  
- `scripts/` — uSCRIPT runtime (Python + Bash helpers)  
- `ui/` — uNETWORK (Tauri app & IPC schemas)  
- `assets/` — Fonts, palettes, themes  
- `extensions/` — Official & community extensions  
- `distro/` — Build profiles (TinyCore A/AA/B, Ubuntu, macOS, Windows)  
- `docs/` — Documentation  
- `tools/` — Dev tooling

---

## 🌳 Branching Model

- **main** — stable, always releasable  
- **next** — integration branch for features  
- **feature/*`** — for new work, branch from `next`  
- **release/*`** — temporary hardening branches  
- **hotfix/*`** — fixes branched from `main`

---

## 🚀 Build Profiles

- **A (uCORE only)** — minimal CLI, no scripting or UI  
- **AA (Runtime)** — CLI + uSCRIPT + uNETWORK (no dev toolchains)  
- **B (Dev)** — Full runtime + Rust/Node toolchains

---

## 🔧 Development Setup

- Use Ubuntu/macOS/Windows for dev.  
- TinyCore builds are scripted in `distro/scripts/`.  
- Run `make check` to lint & test.  
- Use `tools/mock-core` to simulate uCORE for UI testing.

---

## 🧪 Testing

- Unit tests live alongside each layer (`core/tests/`, `scripts/tests/`, `ui/tests/`).  
- JSON Schemas in `ui/ipc/` must validate via CI.  
- End-to-end tests boot TinyCore images in CI VMs.

---

## 📦 Submitting Changes

1. Fork the repo.  
2. Create a feature branch from `next`.  
3. Commit with clear messages (`feat(core): add registry list`).  
4. Push & open PR against `next`.  
5. Ensure CI passes.  
6. After review, merge into `next` → eventually `main`.

---

## 📜 Code Style

- **Shell:** POSIX + Bash 3 compatibility.  
- **Python:** PEP8 + type hints.  
- **Rust/Node:** follow project lints.  
- **Docs:** Markdown, ASCII diagrams preferred.

---

## 🙏 Thanks

Thanks for helping improve uDOS! Every contribution, big or small, moves the project forward.
