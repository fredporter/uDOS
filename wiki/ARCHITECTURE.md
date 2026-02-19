# uDOS Architecture

**Version:** v1.4.3
**Last Updated:** 2026-02-19
**Status:** Active

uDOS is an offline‑first, vault‑based system with optional gateway services and modular extensions.

---

## Overview

```
uDOS/
├── core/          # Offline runtime + TUI
├── wizard/        # Optional gateway (LAN/cloud)
├── sonic/         # Bootable USB entry point
├── app/           # Native UI (Tauri)
├── library/       # Container definitions
├── extensions/    # Transport API contracts
├── docs/          # Architecture + specs
├── wiki/          # Beginner-friendly docs
└── knowledge/     # Static knowledge catalog
```

---

## Core (Offline Runtime)
**Location:** `core/`

**Responsibilities**
- Markdown → state → HTML rendering
- Deterministic output
- Vault-first file access
- TUI command surface (uCODE)

**Boundaries**
- ✅ No network dependency
- ✅ Local-only by default
- ❌ No cloud services

---

## Wizard (Gateway)
**Location:** `wizard/`

**Responsibilities**
- AI routing (local-first via Ollama, optional cloud)
- Render gateway (`/api/render/*`)
- Plugin registry + update routing

**Boundaries**
- ✅ Stateless (no user data at rest)
- ✅ LAN-first
- ❌ No TUI logic

---

## Sonic (Bootable Entry)
**Location:** `sonic/`

**Responsibilities**
- USB builder
- Bootable entry point for TUI

---

## App (Tauri)
**Location:** `app/`

**Responsibilities**
- Vault picker + editor
- Local preview using Core runtime
- Optional Wizard connection

---

## Extensions + Containers
**Location:** `library/`, `extensions/`

**Responsibilities**
- Container definitions (library)
- API contracts (extensions)

---

## Versioning
- Core + Wizard release baseline is tracked in `releases/v1.4.3.yml`.
- Submodules can ship on their own cadence.

---

## Related Docs
- `docs/README.md`
- `docs/roadmap.md`
- `docs/specs/wiki_spec_obsidian.md`
