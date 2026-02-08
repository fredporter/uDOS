# Sonic → TUI Entry: Modular Plugin System

**Date:** 2026-02-05  
**Status:** Provisioned  
**Goal:** Replace screwdriver monolith with modular plugin system + device database sync

---

## What Was Built

### 1. Type-Safe Schemas
**File:** `library/sonic/schemas/__init__.py`

- Device catalog models (Device, DeviceQuery, DeviceStats)
- Flash pack specifications (FlashPackSpec, LayoutSpec, PartitionSpec)
- Deployment specs (PayloadSpec, WindowsSpec, WizardSpec)
- Sync status tracking (SyncStatus)
- Enums for format modes, filesystems, partition roles, etc.

### 2. Plugin API Service
**File:** `library/sonic/api/__init__.py`

- `SonicPluginService` - Core API interface
- Device queries with type-safe filters
- Flash pack management
- Health checks and statistics
- Auto-detection of repo paths

### 3. Database Sync Module
**File:** `library/sonic/sync/__init__.py`

- `DeviceDatabaseSync` - Sync operations
- Rebuild database from SQL source
- Export to CSV / Import from CSV
- Automatic backups before rebuild
- Sync logging to `memory/sonic/sync.log`

### 4. Plugin Loader
**File:** `extensions/sonic_loader.py`

- `SonicPluginLoader` - Dynamic loading system
- Load schemas, api, sync independently
- Plugin availability checking
- Metadata extraction from container.json

### 5. Modular Wizard Routes
**File:** `wizard/routes/sonic_plugin_routes.py`

- `create_sonic_plugin_routes()` - New modular endpoints
- Device queries with advanced filters
- Database sync endpoints (status, rebuild, export)
- Flash pack management
- Legacy compatibility redirect

### 6. Wizard Service Wrapper
**File:** `wizard/services/sonic_plugin_service.py`

- `SonicPluginService` - Wizard service layer
- Graceful degradation if plugin unavailable
- Health checking

### 7. Migration Guide
**File:** `docs/SONIC-MIGRATION-MODULAR.md`

- Complete migration documentation
- API comparison (before/after)
- Testing procedures
- Rollback plan

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Core TUI (Offline)                    │
│  core/commands/sonic_handler.py → sonic/core/sonic_cli  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────┐
│              Extensions (Plugin Loader)                  │
│  extensions/sonic_loader.py → load_sonic_plugin()       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────┐
│            Library (Modular Plugin)                      │
│  library/sonic/                                          │
│    ├── schemas/__init__.py   (Data models)              │
│    ├── api/__init__.py        (Service API)             │
│    └── sync/__init__.py       (DB sync)                 │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────┐
│              Wizard (Cloud Services)                     │
│  wizard/routes/sonic_plugin_routes.py                   │
│  wizard/services/sonic_plugin_service.py                │
└─────────────────────────────────────────────────────────┘
```

**Data Flow:**
```
sonic/datasets/sonic-devices.sql
  ↓ (rebuild)
memory/sonic/sonic-devices.db
  ↓ (query)
library/sonic/api → SonicPluginService
  ↓ (HTTP)
wizard/routes/sonic_plugin_routes → FastAPI
  ↓
TUI/GUI/External clients
```

---

## Key Features

### Type-Safe Queries
```python
from library.sonic.schemas import DeviceQuery, ReflashPotential
from library.sonic.api import get_sonic_service

api = get_sonic_service()
query = DeviceQuery(
    vendor="Raspberry Pi",
    reflash_potential=ReflashPotential.HIGH,
    usb_boot=USBBootSupport.NATIVE,
    limit=50
)
devices = api.query_devices(query)
```

### Database Sync
```python
from library.sonic.sync import get_sync_service

sync = get_sync_service()
status = sync.get_status()

if status.needs_rebuild:
    result = sync.rebuild_database()
    print(f"✅ Rebuilt: {result['record_count']} devices")
```

### Dynamic Loading
```python
from extensions.sonic_loader import load_sonic_plugin

plugin = load_sonic_plugin()
api = plugin['api'].get_sonic_service()
health = api.health()
```

### HTTP Endpoints
```bash
# Health check
GET /api/sonic/health

# Query devices
GET /api/sonic/devices?vendor=Dell&reflash_potential=high

# Sync operations
GET /api/sonic/sync/status
POST /api/sonic/sync/rebuild?force=false
POST /api/sonic/sync/export

# Flash packs
GET /api/sonic/flash-packs
GET /api/sonic/flash-packs/{pack_id}
```

---

## Benefits

### Before (Screwdriver Monolith)
- Hardcoded paths: `SCREWDRIVER_PACK_ROOT`, `SCREWDRIVER_SCHEMA_PATH`
- Direct database access with manual SQL
- No sync capabilities
- Tight coupling between wizard and sonic
- 485 lines in sonic_routes.py

### After (Modular Plugin)
- ✅ Dynamic plugin loading via extensions
- ✅ Type-safe schemas with dataclasses & enums
- ✅ Database sync with rebuild/export/import
- ✅ Clean API boundaries
- ✅ Graceful degradation if plugin unavailable
- ✅ Automatic backups before rebuild
- ✅ Sync logging and status tracking
- ✅ Path auto-detection
- ✅ Extensible architecture

---

## File Locations

### New Files
```
library/sonic/schemas/__init__.py              # Data models
library/sonic/api/__init__.py                  # API service
library/sonic/sync/__init__.py                 # DB sync
extensions/sonic_loader.py                     # Plugin loader
wizard/routes/sonic_plugin_routes.py           # Modular routes
wizard/services/sonic_plugin_service.py        # Service wrapper
docs/SONIC-MIGRATION-MODULAR.md               # Migration guide
```

### Runtime Paths (New)
```
memory/sonic/
  ├── sonic-devices.db        # Runtime database
  ├── sync.log                # Sync operations log
  └── flash_packs/            # Flash pack storage
```

### Legacy Paths (Deprecated)
```
memory/sandbox/screwdriver/   # OLD flash pack location
wizard/routes/sonic_routes.py # OLD monolithic routes
wizard/services/sonic_service.py # OLD basic service
```

---

## Next Actions

1. **Test Plugin Loader**
   ```bash
   python3 -c "from extensions.sonic_loader import load_sonic_plugin; \
               p = load_sonic_plugin(); print(p['api'].get_sonic_service().health())"
   ```

2. **Rebuild Database**
   ```bash
   python3 -c "from library.sonic.sync import get_sync_service; \
               s = get_sync_service(); print(s.rebuild_database())"
   ```

3. **Update Wizard Server**
   ```python
   # In wizard/server.py
   from wizard.routes.sonic_plugin_routes import create_sonic_plugin_routes
   app.include_router(create_sonic_plugin_routes(auth_guard))
   ```

4. **Optional: Add TUI Sync Commands**
   ```python
   # In core/commands/sonic_handler.py
   # Add: SONIC SYNC, SONIC REBUILD
   ```

5. **Update Documentation**
   - Remove "screwdriver" references from docs/
   - Update BINDER-SONIC-ENDPOINTS.md
   - Update WIZARD-SONIC-PLUGIN-ECOSYSTEM.md

6. **Archive Legacy**
   ```bash
   mkdir -p .archive/screwdriver-legacy
   mv wizard/routes/sonic_routes.py .archive/screwdriver-legacy/
   mv wizard/services/sonic_service.py .archive/screwdriver-legacy/
   ```

---

## Boundary Compliance

**Follows uDOS architecture rules:**

✅ **Core (offline TUI):**
- No cloud dependencies
- Uses sonic/core/sonic_cli.py directly
- No business logic in handler

✅ **Extensions (transport):**
- sonic_loader.py provides plugin loading
- Clean API, no cloud assumptions

✅ **Library (plugins):**
- Self-contained in library/sonic/
- No wizard imports
- Modular schemas/api/sync

✅ **Wizard (cloud services):**
- HTTP endpoints only
- Uses plugin loader from extensions
- Service wrapper for wizard integration

**Logger compliance:**
```python
from core.services.logging_manager import get_logger
logger = get_logger('sonic-plugin')
logger.info('[LOCAL] Device query executed')
```

---

## References

- **Migration Guide:** `docs/SONIC-MIGRATION-MODULAR.md`
- **Agent Rules:** `docs/AGENTS.md`
- **Architecture:** `docs/ARCHITECTURE-v1.3.md`
- **Plugin Ecosystem:** `core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md`
- **Integration Spec:** `core/sonic/docs/integration-spec.md`
- **Endpoints:** `docs/BINDER-SONIC-ENDPOINTS.md`

---

_Structure provisioned: 2026-02-05_  
_Ready for: Testing → Deployment → Legacy cleanup_
