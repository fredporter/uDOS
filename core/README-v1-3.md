# Core / TS Engine (v1.3)

This supplement to `core/README.md` spells out how the TS core satisfies the deliverable from `docs/uDOS-v1-3.md:11`:

- `core/` houses the deterministic TS engine (parsing, rendering, SQLite state, diffing, export packaging) that powers both the local portal and the static lanes.
- Keep the renderer agnostic: it should emit HTML + metadata for the theme slots described in `docs/Theme-Pack-Contract.md` and share tokens defined in `docs/CSS-Tokens.md`.
- When ready, the renderer should export to `memory/vault/_site/<theme>/...` while logging missions, jobs, and contributions in the vault SQLite (`docs/Vault-Contract.md`, `docs/Mission-Job-Schema.md`, `docs/Contributions-Contract.md`).

This file is purely documentation for the scaffold; implementation stays inside the existing `core/src/` modules.
