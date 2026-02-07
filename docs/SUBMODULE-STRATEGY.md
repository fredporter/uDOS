# Submodule Strategy (v1.3)

**Goal:** Separate public core from private, licensed, or experimental modules.

---

## Public (Root Repo)
- `core/` — TypeScript runtime.
- `wizard/` — gateway services.
- `extensions/` — transport API definitions.
- `library/` — container definitions.
- `docs/` — architecture + guides.
- `knowledge/` — static catalog.

---

## Private (Submodules)
- `dev/` — experimental + Goblin dev server.
- `sonic/` — bootable USB builder.
- `app/` — Tauri native app.
- `groovebox/` — music extension.

---

## Rules
- **Public repo**: everything needed for offline core usage + docs.
- **Submodules**: licensed, paid, or platform-specific modules.
- **No production dependency** on `dev/` or experimental lanes.

---

## Versioning Policy
- Version-lock Core + Wizard in release manifest.
- Submodules can ship on independent cadence.
