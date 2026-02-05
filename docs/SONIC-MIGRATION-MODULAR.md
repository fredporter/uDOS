# Sonic Screwdriver → Modular Plugin Migration

**Status:** Provisioned (2026-02-05)  
**Goal:** Replace monolithic "screwdriver" with modular plugin system + device database sync

---

## Overview

The Sonic Screwdriver system has been refactored from a monolithic implementation into a modular plugin architecture. This enables:

- **Dynamic loading** of Sonic components via extensions system
- **Clean separation** between plugin logic (library/sonic) and integration layer (wizard/extensions)
- **Device database sync** capabilities with rebuild/export/import
- **Type-safe schemas** for devices, flash packs, layouts, and payloads
- **TUI compatibility** through plugin loader

---

## New Structure

### Before (Monolithic "Screwdriver")

```
wizard/routes/sonic_routes.py       # 485 lines, hardcoded paths
wizard/services/sonic_service.py     # Lightweight wrapper
memory/sandbox/screwdriver/          # Flash packs
wizard/schemas/screwdriver_*         # Schema files
```

**Issues:**
- Hardcoded paths: `SCREWDRIVER_PACK_ROOT`, `SCREWDRIVER_SCHEMA_PATH`
- Direct imports, tight coupling
- No plugin abstraction
- No database sync capabilities

### After (Modular Plugin System)

```
library/sonic/
  schemas/__init__.py                # Type-safe data models
  api/__init__.py                    # SonicPluginService
  sync/__init__.py                   # DeviceDatabaseSync
  container.json                     # Plugin metadata

extensions/sonic_loader.py           # Dynamic plugin loader

wizard/routes/sonic_plugin_routes.py # Modular routes
wizard/services/sonic_plugin_service.py # Service wrapper

memory/sonic/
  sonic-devices.db                   # Runtime database
  flash_packs/                       # Flash pack storage
  sync.log                           # Sync operations log
```

**Benefits:**
- Plugin-based architecture
- Dynamic loading via extensions
- Database sync with rebuild/export/import
- Type-safe schemas using dataclasses
- Clean separation of concerns

---

## Key Components

### 1. Schemas (`library/sonic/schemas/`)

**Data models:**
- `Device` - Device catalog record
- `DeviceQuery` - Query parameters
- `DeviceStats` - Catalog statistics
- `FlashPackSpec` - Flash pack specification
- `LayoutSpec` - Disk layout
- `PartitionSpec` - Partition definition
- `PayloadSpec` - Payload deployment
- `WindowsSpec` - Windows deployment
- `WizardSpec` - uDOS Wizard deployment
- `SyncStatus` - Database sync status

**Enums:**
- `FormatMode` - gpt, mbr, skip, full
- `FilesystemType` - ext4, vfat, ntfs, etc.
- `PartitionRole` - boot, udos, windows, media, data
- `ReflashPotential` - high, medium, low, unknown
- `USBBootSupport` - native, uefi_only, legacy_only, mixed, none

### 2. API Service (`library/sonic/api/`)

**`SonicPluginService`:**
- `health()` - Service health check
- `get_schema()` - Load device schema
- `query_devices(query)` - Query device catalog
- `get_device(device_id)` - Get device by ID
- `get_stats()` - Catalog statistics
- `list_flash_packs()` - List flash packs
- `get_flash_pack(pack_id)` - Get flash pack

### 3. Database Sync (`library/sonic/sync/`)

**`DeviceDatabaseSync`:**
- `get_status()` - Current sync status
- `rebuild_database(force)` - Rebuild from SQL
- `export_to_csv(output_path)` - Export to CSV
- `import_from_csv(csv_path)` - Import from CSV

**Features:**
- Automatic backup before rebuild
- Timestamp tracking
- Sync log (`memory/sonic/sync.log`)
- Schema version detection

### 4. Plugin Loader (`extensions/sonic_loader.py`)

**`SonicPluginLoader`:**
- `load_schemas()` - Load schema module
- `load_api()` - Load API service
- `load_sync()` - Load sync service
- `load_all()` - Load all components
- `get_plugin_info()` - Plugin metadata
- `is_available()` - Availability check

**Usage:**
```python
from extensions.sonic_loader import load_sonic_plugin

plugin = load_sonic_plugin()
api = plugin['api'].get_sonic_service()
sync = plugin['sync'].get_sync_service()
schemas = plugin['schemas']
```

### 5. Wizard Routes (`wizard/routes/sonic_plugin_routes.py`)

**New endpoints:**
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

**Migration complete (v1.3.1):** All code now uses `create_sonic_plugin_routes()` directly. Legacy compatibility shim removed.

---

## Migration Steps

### Phase 1: Verify Plugin Structure

```bash
# Check plugin files exist
ls -la library/sonic/schemas/__init__.py
ls -la library/sonic/api/__init__.py
ls -la library/sonic/sync/__init__.py
ls -la extensions/sonic_loader.py

# Verify Python imports
python3 -c "from library.sonic.schemas import Device; print('✅ Schemas OK')"
python3 -c "from library.sonic.api import get_sonic_service; print('✅ API OK')"
python3 -c "from library.sonic.sync import get_sync_service; print('✅ Sync OK')"
python3 -c "from extensions.sonic_loader import load_sonic_plugin; print('✅ Loader OK')"
```

### Phase 2: Database Sync

```bash
# Rebuild device database from SQL
cd /path/to/uDOS
sqlite3 memory/sonic/sonic-devices.db < sonic/datasets/sonic-devices.sql

# Or use Python API
python3 -c "
from library.sonic.sync import get_sync_service
sync = get_sync_service()
result = sync.rebuild_database(force=True)
print(result)
"
```

### Phase 3: Update Wizard Server

**Active implementation (v1.1.1):**
```python
# wizard/server.py
from wizard.routes.sonic_plugin_routes import create_sonic_plugin_routes

sonic_router = create_sonic_plugin_routes(auth_guard=self._authenticate_admin)
app.include_router(sonic_router)
```

**Note:** Legacy `wizard/routes/sonic_routes.py` removed. All imports must use `sonic_plugin_routes`.

### Phase 4: Update TUI Handler

The Core TUI handler (`core/commands/sonic_handler.py`) already works with the plugin system since it invokes `sonic/core/sonic_cli.py` directly. No changes needed unless you want to add sync commands.

**Optional: Add TUI sync commands**
```python
# In sonic_handler.py
def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
    # ... existing code ...
    
    if action == "sync":
        return self._sync_status()
    if action == "rebuild":
        return self._rebuild_db()
    
    # ...

def _sync_status(self) -> Dict:
    from library.sonic.sync import get_sync_service
    sync = get_sync_service()
    status = sync.get_status()
    return {
        "status": "ok",
        "sync_status": {
            "last_sync": status.last_sync,
            "db_exists": status.db_exists,
            "record_count": status.record_count,
            "needs_rebuild": status.needs_rebuild,
        },
    }

def _rebuild_db(self) -> Dict:
    from library.sonic.sync import get_sync_service
    sync = get_sync_service()
    result = sync.rebuild_database()
    return result
```

### Phase 5: Clean Up Legacy

**After migration complete:**

```bash
# Backup legacy files
mkdir -p .archive/screwdriver-legacy
cp wizard/routes/sonic_routes.py .archive/screwdriver-legacy/
cp wizard/services/sonic_service.py .archive/screwdriver-legacy/

# Move flash packs
mkdir -p memory/sonic/flash_packs
mv memory/sandbox/screwdriver/flash_packs/* memory/sonic/flash_packs/ 2>/dev/null || true

# Update references
grep -r "screwdriver" wizard/ --include="*.py" | tee .archive/screwdriver-references.txt
```

---

## API Changes

### Device Query

**Before:**
```python
# Direct SQL with manual param building
query = "SELECT * FROM devices WHERE vendor LIKE ?"
params = [f"%{vendor}%"]
cursor.execute(query, params)
```

**After:**
```python
from library.sonic.schemas import DeviceQuery
from library.sonic.api import get_sonic_service

api = get_sonic_service()
query = DeviceQuery(vendor="Dell", reflash_potential="high", limit=50)
devices = api.query_devices(query)
```

### Database Sync

**Before:**
```bash
# Manual SQLite rebuild
sqlite3 memory/sonic/sonic-devices.db < sonic/datasets/sonic-devices.sql
```

**After:**
```python
from library.sonic.sync import get_sync_service

sync = get_sync_service()
status = sync.get_status()
if status.needs_rebuild:
    result = sync.rebuild_database()
    print(f"Rebuilt: {result['record_count']} records")
```

### Service Health

**Before:**
```python
db_exists = SONIC_DB_PATH.exists()
table_exists = (SONIC_DATASETS_PATH / "sonic-devices.table.md").exists()
return {"database_compiled": db_exists, "datasets_available": table_exists}
```

**After:**
```python
from library.sonic.api import get_sonic_service

api = get_sonic_service()
health = api.health()
# Returns: status, datasets_available, schema_available, database_compiled,
#          record_count, db_path, flash_pack_root, sonic_root
```

---

## Testing

### Unit Tests

```python
# Test plugin loader
from extensions.sonic_loader import SonicPluginLoader

loader = SonicPluginLoader()
assert loader.is_available()
info = loader.get_plugin_info()
assert info['installed'] is True

# Test schemas
from library.sonic.schemas import Device, DeviceQuery

device = Device(id="test-device", vendor="Test", model="Model")
assert device.to_dict()['vendor'] == "Test"

# Test API
from library.sonic.api import get_sonic_service

api = get_sonic_service()
health = api.health()
assert 'status' in health

# Test sync
from library.sonic.sync import get_sync_service

sync = get_sync_service()
status = sync.get_status()
assert status.db_path
```

### Integration Tests

```bash
# Start wizard with plugin routes
cd wizard
python3 server.py

# Test endpoints
curl http://localhost:8765/api/sonic/health
curl http://localhost:8765/api/sonic/devices?vendor=Raspberry
curl http://localhost:8765/api/sonic/sync/status
curl -X POST http://localhost:8765/api/sonic/sync/rebuild?force=false
```

---

## Documentation Updates

**Update these files:**
- `docs/BINDER-SONIC-ENDPOINTS.md` - Replace screwdriver references
- `docs/ARCHITECTURE-v1.3.md` - Add modular plugin architecture
- `core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md` - Update paths and examples
- `sonic/docs/integration-spec.md` - Reference new plugin system

**Search & replace:**
```bash
grep -r "screwdriver" docs/ --include="*.md"
grep -r "SCREWDRIVER_" wizard/ --include="*.py"
grep -r "memory/sandbox/screwdriver" . --include="*.py"
```

---

## Rollback Plan

If issues arise:

1. **Keep legacy routes active:**
   ```python
   # wizard/server.py
   from wizard.routes.sonic_routes import create_sonic_routes  # Legacy
   app.include_router(create_sonic_routes(auth_guard))
   ```

2. **Restore flash packs:**
   ```bash
   mv memory/sonic/flash_packs/* memory/sandbox/screwdriver/flash_packs/
   ```

3. **Revert to archived files:**
   ```bash
   cp .archive/screwdriver-legacy/sonic_routes.py wizard/routes/
   cp .archive/screwdriver-legacy/sonic_service.py wizard/services/
   ```

---

## Benefits Summary

**Before (Screwdriver Monolith):**
- ❌ Hardcoded paths
- ❌ Tight coupling
- ❌ No plugin abstraction
- ❌ Manual database rebuild
- ❌ No sync logging

**After (Modular Plugin System):**
- ✅ Dynamic plugin loading
- ✅ Type-safe schemas
- ✅ Database sync with backup
- ✅ Clean API boundaries
- ✅ TUI + Wizard integration
- ✅ Sync status tracking
- ✅ Export/import capabilities
- ✅ Extensible architecture

---

## Next Steps

1. **Test the plugin loader** - Verify all imports work
2. **Rebuild device database** - Run sync module
3. **Update wizard server** - Switch to plugin routes
4. **Update documentation** - Remove screwdriver references
5. **Add TUI sync commands** - Optional SONIC SYNC/REBUILD
6. **Archive legacy code** - Move to .archive/

---

## Questions?

- Check `library/sonic/schemas/__init__.py` for data models
- Check `library/sonic/api/__init__.py` for API methods
- Check `library/sonic/sync/__init__.py` for sync operations
- Check `extensions/sonic_loader.py` for plugin loading
- Check `wizard/routes/sonic_plugin_routes.py` for HTTP endpoints

**Structure conforms to:**
- `.github/copilot-instructions.md` - Short, direct, lean
- `docs/AGENTS.md` - Core=offline, Wizard=cloud, Extensions=transport
- Plugin boundary rules - No hardcoded paths, modular loading

---

_Migration provisioned: 2026-02-05_  
_Status: Ready for testing and deployment_
