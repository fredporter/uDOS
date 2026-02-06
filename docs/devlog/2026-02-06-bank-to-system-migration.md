# Memory/Bank to System Migration

**Date:** 2026-02-06  
**Status:** ✅ Complete  
**Impact:** High — Core path restructuring

---

## Summary

Migrated from legacy bank structure to cleaner separation:
- `memory/system/` — System templates/config (tracked in git)
- `vault-md/bank/` — User data vault (local only)
- `memory/private/` — Secrets/credentials (gitignored)

**Just completed (2026-02-06):**
- Updated core paths to use `memory/system/` and `vault-md/`, removed legacy bank references.
- Updated installer/migration scripts and `.gitignore`.
- Updated docs to remove legacy bank references or mark them as legacy.
- Moved remaining repo bank content into `memory/system/`.

---

## Migration Details

### Directories Moved

```bash
legacy bank system/          → memory/system/
legacy bank locations/       → vault-md/bank/locations/
legacy bank spatial/         → vault-md/bank/spatial/
legacy bank private/         → memory/private/
legacy bank binders/         → vault-md/bank/binders/
```

### Files Updated

#### Python Code (20+ files)
- `core/tui/fkey_handler.py` — Workspace paths
- `core/services/theme_service.py` — Theme directory
- `core/services/location_migration_service.py` — Location data paths
- `core/services/todo_service.py` — Seed path
- `core/services/config_sync_service.py` — Token path
- `core/services/user_service.py` — State directory
- `core/services/prompt_parser_service.py` — Seed path
- `core/ui/workspace_selector.py` — Workspace options
- `core/tui/ucode.py` — Admin token path
- `core/commands/setup_handler.py` — Confirmation paths
- `core/commands/shakedown_handler.py` — Directory checks
- `core/commands/destroy_handler.py` — Compost paths
- `core/commands/story_handler.py` — Story file resolution
- `core/binder/manager.py` — Binder workspace
- `core/commands/binder_handler.py` — Default binder root
- `wizard/services/secret_store.py` — Key file path
- `wizard/tools/secret_store_cli.py` — Private directory
- `wizard/tools/generate_github_secrets.py` — Temp file path
- `wizard/web/web_service.py` — Config directory
- `wizard/web/gmail_oauth_server.py` — Credentials path
- `wizard/routes/settings_unified.py` — Secret store key

#### Shell Scripts
- `bin/install.sh` — Directory creation
- `bin/migrate-v1.2-to-v1.3.sh` — Source paths
- `memory/system/startup.sh` — Init directories

#### Configuration
- `.gitignore` — Path patterns updated

#### Documentation
- `docs/decisions/ADR-0004-data-layer-architecture.md` — Architecture paths
- `docs/howto/SEED-INSTALLATION-GUIDE.md` — Legacy notice added
- `docs/OBSIDIAN-INTEGRATION.md` — Path update notice
- `docs/TUI-Vibe-Integration.md` — Legacy path notice

---

## New Structure

```
memory/
├── logs/              # Runtime logs (gitignored)
├── system/            # System templates (tracked)
│   ├── themes/
│   ├── *.md stories
│   └── *.sh scripts
├── private/           # Secrets/credentials (gitignored)
├── sandbox/           # User workspace (gitignored)
└── wizard/            # Wizard state (gitignored)

vault-md/
└── bank/
    ├── locations/     # Location data
    ├── spatial/       # Spatial filesystem
    └── binders/       # User binders
```

---

## Legacy Compatibility

**Legacy paths retired:**
- Deprecated bank directory archived to `memory/.archive/removed-bank-2026-02-06/`.
- Code now references new paths.
- Docs marked with legacy notices.

---

## Rationale

See [ADR-0004: Data Layer Architecture](../decisions/ADR-0004-data-layer-architecture.md)

**Key improvements:**
1. **Clearer separation** — System vs user data
2. **Simpler git tracking** — Only `memory/system/` tracked
3. **Better vault paradigm** — User data in `vault-md/`
4. **Aligned with contracts** — Follows Core vs Wizard boundaries

---

## Next Steps

1. ✅ Test TUI startup
2. ✅ Test Wizard initialization
3. ✅ Test binder operations
4. ⏳ Update extension APIs if needed
5. ✅ Archive legacy bank directory after verification

---

_Migration completed 2026-02-06 by GitHub Copilot_
