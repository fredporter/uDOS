# Sonic Modular Plugin System — File Index

**Provisioned:** 2026-02-05  
**Goal:** Replace screwdriver with modular plugin system + device database sync

---

## Created Files

### Core Plugin Components

#### 1. Schemas Module
**Path:** `library/sonic/schemas/__init__.py`  
**Purpose:** Type-safe data models for devices, flash packs, layouts, payloads  
**Exports:**
- Device, DeviceQuery, DeviceStats
- FlashPackSpec, LayoutSpec, PartitionSpec
- PayloadSpec, WindowsSpec, WizardSpec
- SyncStatus
- Enums: FormatMode, FilesystemType, PartitionRole, ReflashPotential, USBBootSupport

#### 2. API Service
**Path:** `library/sonic/api/__init__.py`  
**Purpose:** Plugin service interface for device queries and flash packs  
**Exports:**
- SonicPluginService
- get_sonic_service()

**Key methods:**
- `health()` - Service status
- `get_schema()` - Device schema
- `query_devices(query)` - Type-safe device queries
- `get_device(device_id)` - Get device by ID
- `get_stats()` - Catalog statistics
- `list_flash_packs()` - List flash packs
- `get_flash_pack(pack_id)` - Get flash pack details

#### 3. Database Sync Module
**Path:** `library/sonic/sync/__init__.py`  
**Purpose:** Device database synchronization with rebuild/export/import  
**Exports:**
- DeviceDatabaseSync
- get_sync_service()

**Key methods:**
- `get_status()` - Sync status
- `rebuild_database(force)` - Rebuild from SQL
- `export_to_csv(output_path)` - Export to CSV
- `import_from_csv(csv_path)` - Import from CSV

---

### Extension Layer

#### 4. Plugin Loader
**Path:** `extensions/sonic_loader.py`  
**Purpose:** Dynamic loading of Sonic plugin components  
**Exports:**
- SonicPluginLoader
- get_sonic_loader()
- load_sonic_plugin()

**Key methods:**
- `load_schemas()` - Load schema module
- `load_api()` - Load API service
- `load_sync()` - Load sync service
- `load_all()` - Load all components
- `get_plugin_info()` - Plugin metadata
- `is_available()` - Availability check

---

### Wizard Integration

#### 5. Modular Routes
**Path:** `wizard/routes/sonic_plugin_routes.py`  
**Purpose:** FastAPI routes using modular plugin system  
**Exports:**
- create_sonic_plugin_routes()
- create_sonic_routes() (legacy compatibility)

**Endpoints:**
- `GET /api/sonic/health` - Service health
- `GET /api/sonic/schema` - Device schema
- `GET /api/sonic/devices` - Query devices
- `GET /api/sonic/devices/{id}` - Device details
- `GET /api/sonic/stats` - Catalog stats
- `GET /api/sonic/sync/status` - Sync status
- `POST /api/sonic/sync/rebuild` - Rebuild database
- `POST /api/sonic/sync/export` - Export to CSV
- `GET /api/sonic/flash-packs` - List flash packs
- `GET /api/sonic/flash-packs/{id}` - Flash pack details

#### 6. Service Wrapper
**Path:** `wizard/services/sonic_plugin_service.py`  
**Purpose:** Wizard service layer with graceful degradation  
**Exports:**
- SonicPluginService
- get_sonic_service()

---

### TUI Integration

#### 7. Plugin Handler
**Path:** `core/commands/sonic_plugin_handler.py`  
**Purpose:** Extended TUI handler with sync commands  
**Exports:**
- SonicPluginHandler

**TUI Commands:**
- `SONIC SYNC` - Check sync status
- `SONIC REBUILD [--force]` - Rebuild database
- `SONIC EXPORT [path]` - Export to CSV
- `SONIC PLUGIN` - Show plugin info

---

### Documentation

#### 8. Migration Guide
**Path:** `docs/SONIC-MIGRATION-MODULAR.md`  
**Purpose:** Complete migration from screwdriver to modular system  
**Contents:**
- Overview and structure comparison
- Component documentation
- Migration steps (5 phases)
- API changes (before/after)
- Testing procedures
- Rollback plan

#### 9. Summary Document
**Path:** `docs/SONIC-TUI-MODULAR-SUMMARY.md`  
**Purpose:** Quick reference for modular plugin system  
**Contents:**
- What was built
- Architecture diagram
- Key features with code examples
- Benefits comparison
- File locations
- Next actions
- Boundary compliance

#### 10. File Index (This File)
**Path:** `docs/SONIC-MODULAR-FILE-INDEX.md`  
**Purpose:** Index of all created files with descriptions

---

## Runtime Artifacts

### New Runtime Paths
```
memory/sonic/
  ├── sonic-devices.db        # Runtime device database
  ├── sync.log                # Sync operations log
  └── flash_packs/            # Flash pack storage
      └── {pack_id}/flash-pack.json  # Individual flash packs
```

### Flash Pack Templates
```
sonic/config/flash-packs/
  └── windows10-entertainment.json
```

### Existing Source Paths
```
sonic/datasets/
  ├── sonic-devices.sql       # Device database source
  ├── sonic-devices.schema.json # JSON schema
  ├── sonic-devices.table.md  # Markdown reference
  └── sonic-devices.csv       # CSV export/import
```

---

## Import Paths

### Plugin Components
```python
# Schemas
from library.sonic.schemas import Device, DeviceQuery, FlashPackSpec

# API
from library.sonic.api import get_sonic_service

# Sync
from library.sonic.sync import get_sync_service

# Loader
from extensions.sonic_loader import load_sonic_plugin
```

### Wizard Integration
```python
# Routes
from wizard.routes.sonic_plugin_routes import create_sonic_plugin_routes

# Service
from wizard.services.sonic_plugin_service import get_sonic_service
```

### TUI Integration
```python
# Handler
from core.commands.sonic_plugin_handler import SonicPluginHandler
```

---

## File Dependencies

```
library/sonic/schemas/__init__.py
  (no dependencies - base data models)

library/sonic/api/__init__.py
  ├── library.sonic.schemas

library/sonic/sync/__init__.py
  ├── library.sonic.schemas

extensions/sonic_loader.py
  ├── library.sonic.schemas
  ├── library.sonic.api
  └── library.sonic.sync

wizard/routes/sonic_plugin_routes.py
  ├── extensions.sonic_loader
  └── library.sonic.schemas (for type hints)

wizard/services/sonic_plugin_service.py
  └── extensions.sonic_loader

core/commands/sonic_plugin_handler.py
  ├── library.sonic.sync
  └── extensions.sonic_loader
```

---

## Testing Quick Reference

### Test Plugin Availability
```bash
python3 -c "from extensions.sonic_loader import load_sonic_plugin; \
            p = load_sonic_plugin(); print('✅ Plugin loaded')"
```

### Test API Service
```bash
python3 -c "from library.sonic.api import get_sonic_service; \
            api = get_sonic_service(); print(api.health())"
```

### Test Database Sync
```bash
python3 -c "from library.sonic.sync import get_sync_service; \
            sync = get_sync_service(); print(sync.get_status())"
```

### Test TUI Handler
```bash
python3 -c "from core.commands.sonic_plugin_handler import SonicPluginHandler; \
            h = SonicPluginHandler(); print(h.handle('SONIC', ['plugin']))"
```

### Test Wizard Routes
```bash
# Start wizard server, then:
curl http://localhost:8765/api/sonic/health
curl http://localhost:8765/api/sonic/sync/status
```

---

## Related Files (Existing)

### To Update
- `wizard/server.py` - Include plugin routes
- `core/tui/ucode.py` - Register plugin handler
- `docs/BINDER-SONIC-ENDPOINTS.md` - Update endpoint docs
- `docs/ARCHITECTURE-v1.3.md` - Add plugin architecture
- `core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md` - Update paths

### To Archive
- `wizard/routes/sonic_routes.py` → `.archive/screwdriver-legacy/`
- `wizard/services/sonic_service.py` → `.archive/screwdriver-legacy/`
- `memory/sandbox/screwdriver/` → `.archive/screwdriver-legacy/`

---

## File Statistics

**Total files created:** 10
- **3** Core plugin components (schemas, api, sync)
- **1** Extension loader
- **2** Wizard integration (routes, service)
- **1** TUI handler
- **3** Documentation files

**Lines of code (approx):**
- Schemas: ~250 lines
- API: ~330 lines
- Sync: ~380 lines
- Loader: ~180 lines
- Routes: ~240 lines
- Service: ~70 lines
- Handler: ~180 lines
- **Total plugin code:** ~1,630 lines

**Documentation:**
- Migration guide: ~450 lines
- Summary: ~300 lines
- File index: ~250 lines
- **Total docs:** ~1,000 lines

---

## Next Steps Checklist

- [ ] Test plugin loader availability
- [ ] Rebuild device database from SQL
- [ ] Update wizard/server.py to use plugin routes
- [ ] Test HTTP endpoints
- [ ] Optional: Integrate TUI sync commands
- [ ] Update documentation (remove screwdriver refs)
- [ ] Archive legacy screwdriver files
- [ ] Update BINDER-SONIC-ENDPOINTS.md
- [ ] Update WIZARD-SONIC-PLUGIN-ECOSYSTEM.md
- [ ] Update ARCHITECTURE-v1.3.md

---

## Architecture Compliance

✅ **Core (offline):** No cloud, no GUI
- TUI handler uses local plugin loader
- No wizard dependencies

✅ **Extensions (transport):** API + plugin loading
- sonic_loader provides dynamic loading
- No business logic

✅ **Library (plugins):** Self-contained modules
- No wizard imports
- Modular schemas/api/sync

✅ **Wizard (cloud services):** HTTP endpoints only
- Uses extension loader
- Service wrapper for integration

**Logger usage:**
```python
from core.services.logging_manager import get_logger
logger = get_logger('sonic-plugin')
logger.info('[LOCAL] Operation completed')
```

---

_File index last updated: 2026-02-05_
