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
- `groovebox/` — music extension.
- Obsidian Companion app lives in external private pre-release repo: `fredporter/oc-app`.

---

## Rules
- **Public repo**: everything needed for offline core usage + docs.
- **Submodules**: licensed, paid, or platform-specific modules.
- **No production dependency** on `dev/` or experimental lanes.

---

## External Add-ons
- **Clone, don’t fork**: keep upstream intact for credit and future pulls.
- **Local mirrors only**: store clones locally and update from upstream.
- **Containerize + layer**: wrap external tools with uDOS UI and policies.

---

## Versioning Policy
- Version-lock Core + Wizard in release manifest.
- Submodules can ship on independent cadence.
