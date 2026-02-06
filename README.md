# uDOS v1.3

Offline-first OS layer for knowledge systems, tools, and portable environments.

**Status:** v1.3.0 (released)
**Primary target:** Alpine Linux (Sonic USB)
**Also supported:** macOS, Ubuntu, Windows (dev)

**Start here:**
- **Users/Beginners:** `wiki/Start-Here.md`
- **Developers:** `docs/README.md`
- **Release manifest:** `v1.3.0-release-manifest.yml`

---

## Quick Start

```bash
python3 uDOS.py
```

Common first commands:
- `HELP`
- `STATUS`
- `WIZARD start`

**Note:** uDOS is designed as a local Obsidian companion app. We recommend using [Obsidian](https://obsidian.md) as your independent text editor and vault reader. uDOS shares your vault using an open-box format—no sync required!

---

## What Ships in v1.3

- **Core** — Deterministic Markdown → HTML runtime (offline)
- **Wizard** — LAN gateway (AI routing, plugins, sync)
- **Sonic** — Bootable USB builder
  Repo: `https://github.com/fredporter/uDOS-sonic`
- **App** — macOS Tauri editor (alpha)
- **Extensions** — Container/plugin ecosystem
- **Vault-MD** — Local docs vault (external, user-owned)

---

## Repo Layout (Public)

```
core/        TypeScript runtime + Python TUI
wizard/      API gateway + services
sonic/       Bootable USB builder (Sonic)
app/         Tauri native app (macOS)
extensions/  Transport API definitions
library/     Container definitions
wiki/        User docs
docs/        Architecture + specs
```

---

## Documentation

- `wiki/README.md` — user guides
- `docs/README.md` — architecture + specs
- `docs/DOCS-SPINE-v1.3.md` — minimal doc spine

---

## Contributing

- `CONTRIBUTORS.md` (canonical)
- `CODE_OF_CONDUCT.md`
- `docs/CONTRIBUTION-PROCESS.md`

---

## License

See `LICENSE.txt`.
