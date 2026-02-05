# Sonic Modular Plugin — Quick Start

**Date:** 2026-02-05  
**Status:** ✅ **Migration Complete** — wizard/server.py uses modular plugin routes (v1.3.1)  
**Goal:** Get the modular plugin system running

---

## 1. Verify Installation

```bash
# Run verification script
python3 tools/verify_sonic_plugin.py

# Or run directly if executable
./tools/verify_sonic_plugin.py
```

Expected output:
```
✅ Schemas module loaded
✅ API module loaded
✅ Sync module loaded
✅ Plugin loader loaded
✅ Wizard routes loaded
✅ Wizard service loaded
✅ TUI handler loaded
✅ ALL TESTS PASSED - Plugin system ready
```

---

## 2. Rebuild Device Database

```bash
# Option A: Python API
python3 -c "
from library.sonic.sync import get_sync_service
sync = get_sync_service()
result = sync.rebuild_database()
print(f\"✅ {result['record_count']} devices loaded\")
"

# Option B: Direct SQLite
sqlite3 memory/sonic/sonic-devices.db < sonic/datasets/sonic-devices.sql
```

---

## 3. Test API Service

```bash
# Get health status
python3 -c "
from library.sonic.api import get_sonic_service
api = get_sonic_service()
print(api.health())
"

# Query devices
python3 -c "
from library.sonic.api import get_sonic_service
from library.sonic.schemas import DeviceQuery
api = get_sonic_service()
query = DeviceQuery(vendor='Raspberry', limit=5)
devices = api.query_devices(query)
print(f'Found {len(devices)} devices')
for d in devices:
    print(f'  - {d.vendor} {d.model}')
"
```

---

## 4. Test TUI Handler

```bash
# Test SONIC SYNC command
python3 -c "
from core.commands.sonic_plugin_handler import SonicPluginHandler
handler = SonicPluginHandler()
result = handler.handle('SONIC', ['sync'])
print(result)
"

# Test SONIC PLUGIN command
python3 -c "
from core.commands.sonic_plugin_handler import SonicPluginHandler
handler = SonicPluginHandler()
result = handler.handle('SONIC', ['plugin'])
print(result)
"
```

---

## 5. Start Wizard with Plugin Routes

### Active Setup (wizard/server.py v1.1.1)

```python
# wizard/server.py (✅ Updated 2026-02-05)
from wizard.routes.sonic_plugin_routes import create_sonic_plugin_routes

sonic_router = create_sonic_plugin_routes(auth_guard=self._authenticate_admin)
app.include_router(sonic_router)
```

### Start server

```bash
cd wizard
python3 server.py
```

---

## 6. Test Wizard Endpoints

```bash
# Health check
curl http://localhost:8765/api/sonic/health

# Get schema
curl http://localhost:8765/api/sonic/schema

# Query devices
curl "http://localhost:8765/api/sonic/devices?vendor=Dell&limit=5"

# Get stats
curl http://localhost:8765/api/sonic/stats

# Sync status
curl http://localhost:8765/api/sonic/sync/status

# Rebuild database (POST)
curl -X POST http://localhost:8765/api/sonic/sync/rebuild

# Export to CSV
curl -X POST http://localhost:8765/api/sonic/sync/export
```

---

## 7. Use in TUI

### Add to core/tui/ucode.py

```python
from core.commands.sonic_plugin_handler import SonicPluginHandler

# In command registry
self.handlers['SONIC'] = SonicPluginHandler()
```

### Use in TUI session

```
uDOS> SONIC SYNC
# Check database sync status

uDOS> SONIC REBUILD --force
# Rebuild device database

uDOS> SONIC EXPORT sonic-devices.csv
# Export to CSV

uDOS> SONIC PLUGIN
# Show plugin info
```

---

## 8. Troubleshooting

### Import Errors

```bash
# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Ensure repo root in path
export PYTHONPATH="/Users/fredbook/Code/uDOS:$PYTHONPATH"

# Retry verification
python3 tools/verify_sonic_plugin.py
```

### Database Not Found

```bash
# Check if SQL source exists
ls -la sonic/datasets/sonic-devices.sql

# Rebuild
python3 -c "
from library.sonic.sync import get_sync_service
sync = get_sync_service()
result = sync.rebuild_database(force=True)
print(result)
"
```

### Plugin Not Available

```bash
# Check plugin info
python3 -c "
from extensions.sonic_loader import get_sonic_loader
loader = get_sonic_loader()
print(loader.get_plugin_info())
print('Available:', loader.is_available())
"

# Check file structure
ls -la library/sonic/
```

---

## 9. Next Steps

**Once verified:**
1. Update documentation references (remove "screwdriver")
2. Archive legacy files
3. Update BINDER-SONIC-ENDPOINTS.md
4. Update WIZARD-SONIC-PLUGIN-ECOSYSTEM.md
5. Test with real device queries

**See detailed docs:**
- Migration: `docs/SONIC-MIGRATION-MODULAR.md`
- Summary: `docs/SONIC-TUI-MODULAR-SUMMARY.md`
- File index: `docs/SONIC-MODULAR-FILE-INDEX.md`

---

## Command Reference

### Python API

```python
# Load plugin
from extensions.sonic_loader import load_sonic_plugin
plugin = load_sonic_plugin()

# Get services
api = plugin['api'].get_sonic_service()
sync = plugin['sync'].get_sync_service()

# Query devices
from library.sonic.schemas import DeviceQuery, ReflashPotential
query = DeviceQuery(
    vendor="Dell",
    reflash_potential=ReflashPotential.HIGH,
    limit=10
)
devices = api.query_devices(query)

# Database sync
status = sync.get_status()
if status.needs_rebuild:
    result = sync.rebuild_database()
```

### TUI Commands

```
SONIC SYNC           # Check sync status
SONIC REBUILD        # Rebuild database
SONIC REBUILD --force # Force rebuild
SONIC EXPORT [path]  # Export to CSV
SONIC PLUGIN         # Show plugin info
```

### HTTP Endpoints

```bash
GET  /api/sonic/health
GET  /api/sonic/schema
GET  /api/sonic/devices[?filters]
GET  /api/sonic/devices/{id}
GET  /api/sonic/stats
GET  /api/sonic/sync/status
POST /api/sonic/sync/rebuild[?force=false]
POST /api/sonic/sync/export[?output_path=]
GET  /api/sonic/flash-packs
GET  /api/sonic/flash-packs/{id}
```

---

_Quick start guide — 2026-02-05_
