# Configuration (v1.3)

**Version:** v1.3.0  
**Last Updated:** 2026-02-04  
**Status:** Active

uDOS uses a unified, user‑editable markdown config. Keep it local, readable, and portable.

---

## Where the Config Lives

Common defaults:

- **TUI / dev:** `memory/config/udos.md`
- **Vault‑first:** `~/Documents/uDOS Vault/system/udos.md`

Use `PROFILE EDIT` to open the active file.

---

## Core Commands

```
PROFILE          # view current profile
PROFILE SETUP    # run setup wizard
PROFILE EDIT     # open config
PROFILE SET $VAR value
PROFILE GET $VAR
GET $VAR         # shorthand
```

> Use `HELP` for the current command surface.

---

## What’s Inside

The config file stores:

- **Profile** — name, timezone, location
- **Preferences** — theme, tips, autosave
- **Security** — auth mode, timeout
- **Project vars** — project metadata
- **Custom vars** — user‑defined fields

Keep it human‑readable and avoid secrets in plain text. Secrets belong in the secure store/keystore, not in `udos.md`.

---

## Environment Overrides

Set `UDOS_*` env vars to override config values at runtime. Example:

```bash
export UDOS_THEME=teletext
```

---

## Notes

- Treat the config as **portable** and **local‑first**.
- Avoid hardcoding versions anywhere; use manifest + version tools.

For deep reference, see `/docs` and the active config template in your vault.
