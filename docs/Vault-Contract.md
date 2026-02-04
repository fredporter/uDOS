# Vault Contract

This contract codifies the “vault is truth” principle from `docs/uDOS-v1-3.md` (sections 1 and 2). Any vault must obey:

1. **Content layout**
   - Markdown files (`*.md`) and assets (images, attachments) live in the vault root or nested folders.
   - The vault remains readable without uDOS installed (open-box guarantee).
   - No proprietary database may replace the Markdown source; state is derived/persisted separately.

2. **App state**
   - `.udos/` optionally holds settings, task indexes, fonts, and other uDOS state.
   - `05_DATA/sqlite/udos.db` (or `.udos/state.db`) stores deterministic indices (tasks, runs, permissions, logs).

3. **Export slots**
   - `_site/<theme>/...` holds the static HTML bundles produced by the renderer (themes described in `docs/Theme-Pack-Contract.md`).
   - `06_RUNS/` stores mission run reports; `07_LOGS/` stores logs when missions run.

4. **Contributions**
   - Contributions arrive as patch bundles (see `docs/Contributions-Contract.md`) and are applied to Markdown files.
   - Vault owners control permissioning locally; the vault must never implicitly trust WordPress or other services as truth sources.

5. **Determinism**
   - Markdown parsing, rendering, and diffing must be reproducible and testable (`docs/uDOS-v1-3.md` sections 2 and 7).
   - `core/` must provide the tools to verify checksums, ASTs, and SQLite indices for every vault.
