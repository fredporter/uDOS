# Vault (Obsidian truth store)

This folder exists to mirror the `vault/` deliverable from `docs/uDOS-v1-3.md`. The real vault lives on disk (`~/Documents/uDOS Vault` by default) and contains:

- Markdown files (`*.md`) plus linked assets (images, attachments, etc.)
- Optional indexed state (`.udos/state.db` or `05_DATA/sqlite/udos.db`) for fast queries and tasks
- Static exports under `_site/` (one folder per theme) that Wizard can serve over LAN

Treat this directory as a placeholder for the actual vault: content must remain readable without uDOS, and every change should stay deterministic (parsing/rendering/diffs/sync). Refer to the vault contract document in `docs/Vault-Contract.md` for the precise requirements.
