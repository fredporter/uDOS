# Wizard Folder Cleanup — 2026-01-15

**Status:** ✅ Complete  
**Purpose:** Remove experimental dev features from production Wizard folder

---

## What Was Cleaned Up

### 1. Archived Files (→ `.archive/wizard-dev-2026-01-15/`)

**Services:**

- `wizard/services/dev/binder_compiler.py`
- `wizard/services/dev/database_service.py`
- `wizard/services/dev/notion_sync_service.py`
- `wizard/services/dev/runtime_executor.py`
- `wizard/services/dev/task_scheduler.py`
- `wizard/services/dev/webhook_test_client.py`

**Server:**

- `wizard/dev_server.py` — Experimental FastAPI server (port 8766)

**Folders:**

- `wizard/dev_studio/` — Empty directory

**Build Artifacts:**

- `wizard/distribution/test/build/` — Old test builds

### 2. Updated References

**wizard/launch_wizard_dev.py:**

- Removed `from wizard.dev_server import main`
- Added redirect message pointing to Goblin Dev Server

**wizard/wizard_tui.py:**

- Changed server reference from `dev_server.py` → `server.py` (production)

**wizard/README.md:**

- Added production status header
- Added Wizard vs Goblin comparison table
- Clarified production-only scope

---

## Why Cleanup Was Needed

After completing Step 1 (Goblin Dev Server architecture), the Wizard folder contained:

1. **Production services** — Device auth, plugin repo, AI routing (keep)
2. **Experimental services** — Notion sync, TS runtime, task scheduler (moved to Goblin)
3. **Dev server** — Unstable endpoints on port 8766 (replaced by Goblin on 8767)

**Problem:** Mixed production and experimental code in same folder

**Solution:** Clear separation:

- **Wizard** (`/wizard/`) = Production stable (port 8765)
- **Goblin** (`/dev/goblin/`) = Experimental unstable (port 8767)

---

## Wizard Folder Now Contains (Production Only)

### Core Server

- `server.py` — Production FastAPI server (port 8765)
- `wizard_tui.py` — Management TUI

### Production Services (`/wizard/services/`)

- `ai_gateway.py` — AI provider integration
- `cost_tracking.py` — Cost monitoring
- `device_auth.py` — Device authentication
- `gmail_relay.py` — Email forwarding
- `mesh_sync.py` — Mesh network sync
- `model_router.py` — AI routing logic
- `monitoring_manager.py` — System monitoring
- `plugin_repository.py` — Plugin management
- `quota_tracker.py` — Usage quotas
- `rate_limiter.py` — Rate limiting

### Extensions (`/wizard/extensions/`)

- `assistant/` — AI services (Gemini, Vibe CLI, Ollama)
- `groovebox/` — Music production

### Other

- `config/` — Configuration files
- `distribution/` — Package building
- `providers/` — AI provider adapters
- `schemas/` — Data schemas
- `tests/` — Unit tests
- `tools/` — Utilities
- `web/` — Web dashboard

---

## Goblin Dev Server Has (Experimental)

Located in `/dev/goblin/`:

### Core Services

- `notion_sync_service.py` — Notion webhook integration
- `runtime_executor.py` — TS Markdown runtime
- `task_scheduler.py` — Organic cron
- `binder_compiler.py` — Multi-format compilation

### Server

- `goblin_server.py` — FastAPI on port 8767
- 16 experimental endpoints (`/api/v0/*`)

### Documentation

- `README.md` — Complete architecture guide
- `QUICK-REFERENCE.md` — Quick start
- `config/goblin.example.json` — Configuration template

### Launcher

- `bin/Launch-Goblin-Dev.command` — Launch script

---

## Verification

```bash
# No dev files remain in wizard
$ find wizard -name "dev_server.py" -o -name "dev_studio" -o -path "*/services/dev"
# (no output — clean!)

# Archived files exist
$ ls .archive/wizard-dev-2026-01-15/
ARCHIVE-NOTE.md  dev/  dev_server.py  dev_studio/

# Goblin is ready
$ ls dev/goblin/
README.md  QUICK-REFERENCE.md  config/  goblin_server.py  services/
```

---

## Impact

**No breaking changes** — All functionality preserved:

| Feature         | Old Location                  | New Location                         |
| --------------- | ----------------------------- | ------------------------------------ |
| Notion sync     | `wizard/services/dev/`        | `dev/goblin/services/`               |
| TS runtime      | `wizard/services/dev/`        | `dev/goblin/services/`               |
| Task scheduler  | `wizard/services/dev/`        | `dev/goblin/services/`               |
| Binder compiler | `wizard/services/dev/`        | `dev/goblin/services/`               |
| Dev endpoints   | `wizard/dev_server.py` (8766) | `dev/goblin/goblin_server.py` (8767) |

**Wizard is now:**

- ✅ Production-only
- ✅ Stable API (`/api/v1/*`)
- ✅ No experimental code
- ✅ Clear scope and boundaries

**Goblin is now:**

- ✅ Experimental-only
- ✅ Unstable API (`/api/v0/*`)
- ✅ Localhost-only
- ✅ Safe to break and iterate

---

## References

- **Archive Note:** [.archive/wizard-dev-2026-01-15/ARCHIVE-NOTE.md](/.archive/wizard-dev-2026-01-15/ARCHIVE-NOTE.md)
- **Wizard README:** [wizard/README.md](/wizard/README.md)
- **Goblin README:** [dev/goblin/README.md](/dev/goblin/README.md)
- **AGENTS.md:** Sections 3.3.1-3.3.2
- **Step 1 Summary:** [docs/devlog/2026-01-15-step-1-complete.md](/docs/devlog/2026-01-15-step-1-complete.md)

---

_Cleanup completed: 2026-01-15_  
_Wizard folder is now production-only_  
_All experimental features moved to Goblin Dev Server_
