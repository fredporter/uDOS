# uDOS Extensions (Public) — Alpha v1.0.0

Distributable extension set for uDOS (API + Transport). Local-only tooling lives outside this tree.

## Scope and Separation

- **Public/git:** Only shipable source (API, Transport), shared docs, and orchestration scripts. No build outputs, installs, downloads, or logs live here.
- **Local/runtime:** Put logs and runtime state in `memory/logs/` or `sandbox/logs/`. Downloaded assets or vendor drops belong in `library/` (gitignored). Park retired code in [extensions/.archive/](.archive/).
- **Cloud/desktop tooling:** Lives in `wizard/extensions/` (not synced by default). VS Code extension removed from public tree; recover via git history if needed.

## Current Layout (2026-01-17)

```
extensions/
├── api/                      # REST/WebSocket API server (public)
├── transport/                # Private transport layer (MeshCore, QR, Audio, NFC, BT)
├── vscode/                   # VS Code language support (grammar + snippets)
├── docs/                     # Extension docs (public)
│   ├── PORT-REGISTRY.md
│   ├── QUICK-REFERENCE.md
│   └── SERVER-MANAGEMENT.md
├── server_manager.py         # Unified server control
└── .archive/                 # Legacy snapshots (git-tracked only)
```

## Recent Changes

- Consolidated extension docs under [docs/](docs/) and removed top-level duplicates.
- Reintroduced VS Code language support under [vscode/](vscode/) for grammar and snippets; still lightweight and build-free.
- Public `/extensions` now contains only distributable components and docs; local-only runtimes stay in Wizard or gitignored paths.
- Applied unified gitignore rules to `/library/` and `/dev/library/` to prevent cloned repos from remote syncing.

## Version Management

```bash
python -m core.version show
python -m core.version check
python -m core.version bump api patch
python -m core.version bump transport patch
```

## Transport Policy

Private transports allow commands and data: MeshCore, Bluetooth Private, NFC, QR Relay, Audio Relay. Public signal only: Bluetooth Public (no data).

## Two-Realm Model

- **Remote/public:** [api/](api/), [transport/](transport/), [docs/](docs/), [server_manager.py](server_manager.py)
- **Local/runtime (gitignored):** `memory/`, `sandbox/`, `library/` downloads, logs, caches, node modules, compiled assets
- **Archived:** [extensions/.archive/](.archive/) for retired components (use git history for the removed VS Code extension)

## References

- [../AGENTS.md](../AGENTS.md)
- [../docs/\_index.md](../docs/_index.md)
- [transport/policy.yaml](transport/policy.yaml)
- [docs/QUICK-REFERENCE.md](docs/QUICK-REFERENCE.md)

---

_Last updated: 2026-01-15_
